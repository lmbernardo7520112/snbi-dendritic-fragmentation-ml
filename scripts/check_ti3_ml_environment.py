#!/usr/bin/env python3
"""Check the pinned TI3 environment using in-memory synthetic inputs only.

This operational smoke test opens no experimental source, creates no dataset,
and writes no files. Its two RandomForest fits are synthetic technical checks,
not scientific ML runs or permission to access experimental pixels.
"""

from __future__ import annotations

import hashlib
from importlib import metadata
import json
import re
import sys


REQUIRED_VERSIONS = {
    "numpy": "1.26.4",
    "scipy": "1.11.4",
    "scikit-image": "0.24.0",
    "scikit-learn": "1.5.2",
}


def _installed_versions() -> dict[str, str]:
    """Return distribution names and versions without installation paths."""
    versions: dict[str, str] = {}
    for distribution in metadata.distributions():
        raw_name = distribution.metadata.get("Name")
        if not raw_name:
            raise ValueError("Distribution name is missing")
        name = re.sub(r"[-_.]+", "-", raw_name).lower()
        if name in versions:
            raise ValueError("Duplicate distribution name")
        versions[name] = distribution.version
    return dict(sorted(versions.items()))


def main() -> int:
    report: dict[str, object] = {
        "status": "FAIL",
        "scope": "SYNTHETIC_ENVIRONMENT_SMOKE_ONLY",
        "required_versions": REQUIRED_VERSIONS,
        "checks": {},
        "counters": {
            "technical_smoke_invocations": 1,
            "synthetic_fit_calls": 0,
            "scientific_ml_runs": 0,
            "experimental_opens": 0,
            "experimental_bytes": 0,
        },
    }
    checks = report["checks"]
    counters = report["counters"]
    try:
        versions = _installed_versions()
        environment = {
            "python_version": ".".join(str(value) for value in sys.version_info[:3]),
            "package_versions": versions,
        }
        serialized_environment = json.dumps(
            environment, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
        report["environment"] = environment
        report["environment_fingerprint_sha256"] = hashlib.sha256(
            serialized_environment
        ).hexdigest()
        mismatches = {
            name: {"expected": expected, "observed": versions.get(name)}
            for name, expected in REQUIRED_VERSIONS.items()
            if versions.get(name) != expected
        }
        checks["exact_dependency_versions"] = not mismatches
        if mismatches:
            report["version_mismatches"] = mismatches
            raise ValueError("Pinned dependency versions do not match")

        import numpy as np
        import scipy
        import skimage
        import sklearn
        from skimage.feature import local_binary_pattern
        from sklearn.ensemble import RandomForestClassifier

        imported_versions = {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit-image": skimage.__version__,
            "scikit-learn": sklearn.__version__,
        }
        report["imported_versions"] = imported_versions
        checks["imported_versions_match_metadata"] = (
            imported_versions == REQUIRED_VERSIONS
        )
        if not checks["imported_versions_match_metadata"]:
            raise ValueError("Imported dependency versions do not match")

        row, column = np.indices((65, 65), dtype=np.int64)
        image = ((7 * row + 11 * column + 60 * ((row // 8) % 2)) % 256).astype(
            np.uint8
        )
        lbp = local_binary_pattern(image, P=8, R=1, method="uniform")
        histogram, _ = np.histogram(lbp, bins=10, range=(0, 10), density=True)
        checks["synthetic_image_uint8_65_by_65"] = bool(
            image.dtype == np.uint8 and image.shape == (65, 65)
        )
        checks["lbp_shape"] = bool(lbp.shape == (65, 65))
        checks["lbp_histogram_ten_finite_bins"] = bool(
            histogram.shape == (10,) and np.isfinite(histogram).all()
        )
        checks["lbp_histogram_unit_sum"] = bool(
            np.isclose(histogram.sum(), 1.0, rtol=0.0, atol=1e-12)
        )
        report["lbp"] = {
            "P": 8,
            "R": 1,
            "method": "uniform",
            "histogram_bins": 10,
            "histogram_range": [0, 10],
            "density": True,
            "histogram": histogram.tolist(),
            "image_recipe": "(7*r + 11*c + 60*((r//8)%2)) % 256",
        }

        labels = (np.arange(24, dtype=np.int64) % 2).astype(np.int64)
        feature_row = np.arange(24, dtype=np.int64)[:, None]
        feature_column = np.arange(10, dtype=np.int64)[None, :]
        features = (
            (feature_row * (feature_column + 3) + feature_column**2) % 29
        ).astype(np.float64) / 28.0 + labels[:, None] * 0.25
        checks["synthetic_rf_matrix_balanced"] = bool(
            features.shape == (24, 10)
            and np.isfinite(features).all()
            and np.array_equal(np.bincount(labels), np.array([12, 12]))
        )
        first = RandomForestClassifier(n_estimators=100, random_state=42)
        parameters = first.get_params(deep=True)
        report["random_forest"] = {
            "parameters": parameters,
            "synthetic_matrix_shape": [24, 10],
            "class_counts": [12, 12],
            "feature_recipe": "((r*(c+3)+c*c)%29)/28 + (r%2)*0.25",
            "purpose": "fit/predict/probability API and fixed-seed determinism",
            "performance_evaluation": "NOT_PERFORMED",
        }
        checks["rf_fixed_estimators_and_seed"] = bool(
            parameters["n_estimators"] == 100 and parameters["random_state"] == 42
        )
        counters["synthetic_fit_calls"] += 1
        first.fit(features, labels)
        prediction = first.predict(features)
        probability = first.predict_proba(features)
        second = RandomForestClassifier(n_estimators=100, random_state=42)
        counters["synthetic_fit_calls"] += 1
        second.fit(features, labels)
        second_prediction = second.predict(features)
        second_probability = second.predict_proba(features)
        checks["rf_output_shapes_and_classes"] = bool(
            prediction.shape == (24,)
            and probability.shape == (24, 2)
            and np.array_equal(first.classes_, np.array([0, 1]))
            and np.array_equal(second.classes_, first.classes_)
        )
        checks["rf_probabilities_finite_and_normalized"] = bool(
            np.isfinite(probability).all()
            and np.logical_and(probability >= 0.0, probability <= 1.0).all()
            and np.allclose(probability.sum(axis=1), 1.0, rtol=0.0, atol=1e-12)
        )
        checks["rf_fixed_seed_prediction_determinism"] = bool(
            np.array_equal(prediction, second_prediction)
        )
        checks["rf_fixed_seed_probability_determinism"] = bool(
            np.array_equal(probability, second_probability)
        )
        if not all(checks.values()):
            raise ValueError("Synthetic environment smoke check failed")
        report["status"] = "PASS"
    except Exception as error:
        # Do not disclose import search paths, environment variables or tracebacks.
        report["error_type"] = type(error).__name__
    print(json.dumps(report, sort_keys=True, ensure_ascii=True, allow_nan=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
