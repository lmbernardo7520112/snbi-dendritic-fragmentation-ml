"""Fixed TI3 structural LBP/RF operations on caller-supplied arrays only.

This module has no source reader, filesystem writes, network, receipt or retry.
The caller must enforce the frozen manifest and single authorized invocation.
Metrics describe agreement with published-location weak labels, not physical
fragmentation recall, onset, forecasting, causality or external generalization.
"""


PATCH_RADIUS_PX = 32
PATCH_SIDE_PX = 65
NATIVE_DIMENSIONS = {"ESM1": (1278, 1018), "ESM4": (1278, 1012)}
REQUIRED_VERSIONS = {
    "numpy": "1.26.4", "scipy": "1.11.4",
    "scikit-image": "0.24.0", "scikit-learn": "1.5.2",
}
RF_PARAMETERS = {
    "bootstrap": True,
    "ccp_alpha": 0.0,
    "class_weight": None,
    "criterion": "gini",
    "max_depth": None,
    "max_features": "sqrt",
    "max_leaf_nodes": None,
    "max_samples": None,
    "min_impurity_decrease": 0.0,
    "min_samples_leaf": 1,
    "min_samples_split": 2,
    "min_weight_fraction_leaf": 0.0,
    "monotonic_cst": None,
    "n_estimators": 100,
    "n_jobs": None,
    "oob_score": False,
    "random_state": 42,
    "verbose": 0,
    "warm_start": False,
}


class BaselineContractError(ValueError):
    """Inputs cannot be processed under the frozen baseline contract."""


def _scientific_runtime():
    """Import only the exact approved implementations; no fallback exists."""
    import numpy as np
    import scipy
    import skimage
    import sklearn

    versions = {
        "numpy": np.__version__, "scipy": scipy.__version__,
        "scikit-image": skimage.__version__, "scikit-learn": sklearn.__version__,
    }
    if versions != REQUIRED_VERSIONS:
        raise BaselineContractError("TI3 pinned scientific versions do not match")
    return np


def _patch_metadata(sample):
    # These checks precede both runtime imports and all access to the array.
    if not isinstance(sample, dict):
        raise BaselineContractError("explicit sample metadata is required")
    if sample.get("split") not in ("TRAIN", "DEVELOPMENT"):
        raise BaselineContractError("FINAL_TEST and unknown splits are prohibited")
    source = sample.get("source_id")
    if not isinstance(source, str) or source not in NATIVE_DIMENSIONS:
        raise BaselineContractError("only structural ESM1 and ESM4 inputs are permitted")
    names = ("width", "height", "center_x", "center_y", "patch_radius_px", "patch_side_px")
    if any(type(sample.get(name)) is not int for name in names):
        raise BaselineContractError("dimensions, centres and patch geometry must be explicit integers")
    width, height = sample["width"], sample["height"]
    if (width, height) != NATIVE_DIMENSIONS[source]:
        raise BaselineContractError("source dimensions differ from the native contract")
    if sample["patch_radius_px"] != PATCH_RADIUS_PX or sample["patch_side_px"] != PATCH_SIDE_PX:
        raise BaselineContractError("patch geometry must remain radius 32 and side 65")
    x, y = sample["center_x"], sample["center_y"]
    box = (x - PATCH_RADIUS_PX, y - PATCH_RADIUS_PX,
           x + PATCH_RADIUS_PX + 1, y + PATCH_RADIUS_PX + 1)
    if box[0] < 0 or box[1] < 0 or box[2] > width or box[3] > height:
        raise BaselineContractError("complete native patch support is required; padding is prohibited")
    return width, height, box


def extract_patch(luma, sample):
    """Copy exactly 65x65 native uint8 values around the frozen integer centre.

    The caller validates all non-canvas support and cross-split exclusions in
    the metadata manifest before reading any input. No centre is adjusted here.
    """
    width, height, (x0, y0, x1, y1) = _patch_metadata(sample)
    np = _scientific_runtime()
    if not isinstance(luma, np.ndarray) or luma.dtype != np.dtype("uint8"):
        raise BaselineContractError("native luminance must already be a uint8 ndarray")
    if luma.shape != (height, width):
        raise BaselineContractError("luminance shape must match the native source dimensions")
    return luma[y0:y1, x0:x1].copy()


def lbp_features(patch):
    """Use scikit-image uniform P=8/R=1 and its ten-bin density histogram."""
    np = _scientific_runtime()
    if (not isinstance(patch, np.ndarray) or patch.dtype != np.dtype("uint8")
            or patch.shape != (PATCH_SIDE_PX, PATCH_SIDE_PX)):
        raise BaselineContractError("LBP requires an unchanged 65x65 uint8 patch")
    from skimage.feature import local_binary_pattern

    lbp = local_binary_pattern(patch, P=8, R=1, method="uniform")
    features, _ = np.histogram(lbp, bins=10, range=(0, 10), density=True)
    if features.shape != (10,) or not np.isfinite(features).all():
        raise BaselineContractError("LBP must produce ten finite features")
    if not np.isclose(features.sum(), 1.0, rtol=0.0, atol=1e-12):
        raise BaselineContractError("LBP histogram must have unit density sum")
    return features


def _validate_learning_inputs(np, features, labels, split):
    if (not isinstance(features, np.ndarray) or features.ndim != 2
            or features.shape[0] == 0 or features.shape[1] != 10
            or features.dtype.kind not in "fiu"):
        raise BaselineContractError(f"{split} requires a nonempty numeric N-by-10 matrix")
    if (not np.isfinite(features).all() or (features < 0).any() or (features > 1).any()
            or not np.allclose(features.sum(axis=1), 1.0, rtol=0.0, atol=1e-12)):
        raise BaselineContractError(f"{split} features must be finite unit-sum LBP histograms")
    if (not isinstance(labels, np.ndarray) or labels.ndim != 1
            or labels.shape[0] != features.shape[0] or labels.dtype.kind not in "iu"
            or not np.array_equal(np.unique(labels), np.array([0, 1]))):
        raise BaselineContractError(f"{split} requires aligned integer weak labels in both classes 0 and 1")


def _classification_metrics(labels, prediction):
    from sklearn.metrics import (
        accuracy_score, balanced_accuracy_score, confusion_matrix,
        f1_score, precision_score, recall_score,
    )

    tn, fp, fn, tp = (int(value) for value in confusion_matrix(labels, prediction, labels=[0, 1]).ravel())
    return {
        "balanced_accuracy": float(balanced_accuracy_score(labels, prediction)),
        "accuracy": float(accuracy_score(labels, prediction)),
        "precision": float(precision_score(labels, prediction, pos_label=1, zero_division=0)),
        "recall": float(recall_score(labels, prediction, pos_label=1, zero_division=0)),
        "f1": float(f1_score(labels, prediction, pos_label=1, zero_division=0)),
        "confusion_matrix": [[tn, fp], [fn, tp]],
        "confusion_order": "rows=true, columns=predicted; labels=[0,1]",
        "TN": tn, "FP": fp, "FN": fn, "TP": tp,
        "sample_count": int(len(labels)),
    }


def evaluate_baseline(train_features, train_labels, dev_features, dev_labels):
    """Fit once on TRAIN and report TRAIN/DEVELOPMENT agreement without selection.

    The function does not persist a model or call a runner. Its fit counter is
    per invocation; preventing a second scientific invocation belongs to the
    caller's exclusive receipt and authority checks. Zero-division precision,
    recall and F1 return zero under this preregistered reporting convention.
    """
    np = _scientific_runtime()
    _validate_learning_inputs(np, train_features, train_labels, "TRAIN")
    _validate_learning_inputs(np, dev_features, dev_labels, "DEVELOPMENT")
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    parameters = model.get_params(deep=True)
    if parameters != RF_PARAMETERS:
        raise BaselineContractError("RandomForest pinned defaults do not match the frozen contract")
    model.fit(train_features, train_labels)
    evaluations = {}
    for split, features, labels in (
        ("TRAIN", train_features, train_labels), ("DEVELOPMENT", dev_features, dev_labels),
    ):
        prediction = model.predict(features)
        probability = model.predict_proba(features)
        if (not np.array_equal(model.classes_, np.array([0, 1]))
                or prediction.shape != labels.shape or probability.shape != (len(labels), 2)
                or not np.isfinite(probability).all()
                or (probability < 0).any() or (probability > 1).any()
                or not np.allclose(probability.sum(axis=1), 1.0, rtol=0.0, atol=1e-12)):
            raise BaselineContractError("RandomForest prediction/probability contract failed")
        evaluations[split] = {
            **_classification_metrics(labels, prediction),
            "true_labels": labels.tolist(), "predicted_labels": prediction.tolist(),
            "probabilities_class_order_0_1": probability.tolist(),
        }
    return {
        "status": "COMPLETED_WITHOUT_MODEL_SELECTION",
        "claim": "CONCORDANCE_WITH_PUBLISHED_LOCATION_WEAK_LABELS",
        "positive_semantics": "PUBLISHED_FRAGMENTATION_LOCATION_PRESENT",
        "background_semantics": "BACKGROUND_CANDIDATE_NOT_PHYSICAL_ABSENCE",
        "primary_metric": "balanced_accuracy",
        "class_order": [0, 1], "parameters": parameters,
        "dependency_versions": dict(REQUIRED_VERSIONS),
        "fit_calls": 1, "model_selection_runs": 0, "evaluations": evaluations,
        "final_test_evaluated": False,
    }
