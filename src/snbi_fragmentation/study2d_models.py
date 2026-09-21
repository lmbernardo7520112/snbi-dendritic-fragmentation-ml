"""Only RF_REFERENCE/LBP20 and two explicitly authorized TRAIN weight schemes."""

from collections import Counter
from copy import deepcopy
import math
import random
import time
import warnings

from .study2c_models import FEATURE_CONTRACT, RF_DEFAULTS, extract_lbp20, predict_classical


RF_PARAMETERS = {
    "bootstrap": True, "ccp_alpha": 0.0, "class_weight": None, "criterion": "gini",
    "max_depth": None, "max_features": "sqrt", "max_leaf_nodes": None,
    "max_samples": None, "min_impurity_decrease": 0.0, "min_samples_leaf": 1,
    "min_samples_split": 2, "min_weight_fraction_leaf": 0.0,
    "monotonic_cst": None, "n_estimators": 100, "n_jobs": None,
    "oob_score": False, "random_state": 42, "verbose": 0, "warm_start": False,
}


class ReferenceModelError(ValueError):
    """No adaptive parameter or row admission changes are permitted."""


def require(value, message):
    if not value:
        raise ReferenceModelError(message)


def exact(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def method_contract():
    require(exact(RF_PARAMETERS, RF_DEFAULTS), "historical nineteen RF parameters changed")
    return {"model": "RF_REFERENCE", "rf_parameters": deepcopy(RF_PARAMETERS),
            "rf_parameter_count": 19, "feature_contract": deepcopy(FEATURE_CONTRACT),
            "weightings": {"GROUP_EQUAL": "1/selected_training_rows_in_group", "OBSERVATION_EQUAL": "1.0"},
            "class_weight": None, "allowed_split": "TRAIN", "allowed_tiers": ["GOLD", "BACKGROUND"],
            "rf_seed_every_fit": 42, "hyperparameter_search": False, "threshold_search": False,
            "weighting_limit": "Weights describe supplied contributions; bootstrap draws need not have identical group totals. Observation weights also alter aggregate class weight."}


def training_weights(rows, weighting):
    require(type(rows) is list and rows and weighting in {"GROUP_EQUAL", "OBSERVATION_EQUAL"},
            "explicit TRAIN rows and frozen weighting required")
    identities, counts, ids = {}, Counter(), set()
    for row in rows:
        require(type(row) is dict and row.get("split") == "TRAIN", "DEV/TEST fit forbidden")
        label, tier = row.get("label"), row.get("tier")
        require(type(label) is int and (label, tier) in {(1, "GOLD"), (0, "BACKGROUND")},
                "SILVER/unlabeled/unknown supervision forbidden")
        gid, sample_id, acquisition = (row.get(k) for k in ("group_id", "sample_id", "acquisition_id"))
        require(type(gid) is str and gid and type(sample_id) is str and sample_id and sample_id not in ids
                and acquisition in {"bottom_up_anti_parallel", "top_down_parallel"}, "canonical identities required")
        require(gid not in identities or identities[gid] == (label, acquisition), "group crosses class/acquisition")
        identities[gid] = (label, acquisition); counts[gid] += 1; ids.add(sample_id)
    require({v[0] for v in identities.values()} == {0, 1}, "both classes required")
    weights = [1.0 / counts[r["group_id"]] if weighting == "GROUP_EQUAL" else 1.0 for r in rows]
    metadata = {"training_rows": len(rows), "training_group_count": len(identities),
                "training_groups": sorted(identities), "weighting": weighting,
                "effective_rows_per_group": dict(sorted(counts.items())),
                "weight_sum_by_group": {g: math.fsum(w for r, w in zip(rows, weights) if r["group_id"] == g)
                                        for g in sorted(identities)},
                "weight_sum_by_class": {str(c): math.fsum(w for r, w in zip(rows, weights) if r["label"] == c) for c in (0, 1)},
                "group_counts_by_class": {str(c): sum(v[0] == c for v in identities.values()) for c in (0, 1)},
                "sample_counts_by_class": {str(c): sum(r["label"] == c for r in rows) for c in (0, 1)},
                "training_tier_counts": dict(Counter(r["tier"] for r in rows)), "training_splits": ["TRAIN"]}
    return weights, metadata


def _features(X, count=None):
    import numpy as np

    require(isinstance(X, np.ndarray) and X.ndim == 2 and X.shape[1] == 20 and len(X) > 0
            and np.issubdtype(X.dtype, np.floating) and bool(np.isfinite(X).all()),
            "finite N by20 frozen LBP features required")
    require(count is None or len(X) == count, "feature/row count mismatch")


def fit_reference(X, rows, weighting, on_event=None):
    """Exactly one fresh RF fit; callbacks delimit the actual library call."""
    config = method_contract()["rf_parameters"]
    values, metadata = training_weights(rows, weighting)
    _features(X, len(rows))
    require(on_event is None or callable(on_event), "callback must be callable")
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier

    random.seed(42); np.random.seed(42)
    model = RandomForestClassifier(**config)
    require(exact(model.get_params(deep=False), config), "RF exact parameter/type divergence")
    labels = np.asarray([r["label"] for r in rows], dtype=np.int64)
    weights = np.asarray(values, dtype=np.float64)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        if on_event:
            on_event({"event": "RF_FIT_START", "family": "RF_REFERENCE", "training_rows": len(rows), "weighting": weighting})
        start = time.perf_counter()
        model.fit(X, labels, sample_weight=weights)
        elapsed = time.perf_counter() - start
        if on_event:
            on_event({"event": "RF_FIT_COMPLETE", "family": "RF_REFERENCE", "runtime_seconds": elapsed, "weighting": weighting})
    require(exact(model.get_params(deep=False), config), "RF parameters mutated during fit")
    metadata.update(family="RF_REFERENCE", estimator_parameters=config, fit_calls=1,
                    runtime_seconds=elapsed, input_feature_dimension=20, convergence="PASS",
                    warnings=[{"category": w.category.__name__, "message": str(w.message)} for w in caught],
                    random_seed=42, hyperparameter_search=False)
    return model, metadata


def predict_reference(model, X):
    """No labels or selection hook; preserve library class-probability semantics."""
    _features(X)
    from sklearn.ensemble import RandomForestClassifier

    require(type(model) is RandomForestClassifier and exact(model.get_params(deep=False), RF_PARAMETERS),
            "only unchanged RF_REFERENCE can predict")
    return predict_classical(model, X)
