"""Frozen, group-level Study3 models; admitted in-memory inputs only.

No source access, search, automatic retry or import-time scientific work.
The controller supplies a mandatory callback that reserves every fit before
the estimator or its scaler sees training values.
"""

from collections import Counter
from copy import deepcopy
import hashlib
import json
import random
import time
import warnings

from .study2c_models import FEATURE_CONTRACT, LR_DEFAULTS, RF_DEFAULTS, extract_lbp20
from .study2d_models import exact
from .study3_domain import validate_groups


CLASSICAL_REPRESENTATIONS = {
    "D1_LBP20": 20,
    "TRAJECTORY_MEAN_LBP20": 20,
    "TRAJECTORY_MEDIAN_LBP20": 20,
    "TRAJECTORY_Q2575_LBP60": 60,
}
RF_PARAMETERS = deepcopy(RF_DEFAULTS)
METADATA_PARAMETERS = deepcopy(LR_DEFAULTS)
METADATA_FEATURE_NAMES = (
    "log1p_n_rows", "first_frame_normalized", "last_frame_normalized",
    "temporal_span_normalized",
)
FRAME_DENOMINATORS = {"bottom_up_anti_parallel": 293, "top_down_parallel": 394}


class Study3ModelError(ValueError):
    """A frozen model/input contract failed; never retry or change the model."""


def require(condition, message):
    if not condition:
        raise Study3ModelError(message)


def method_contract():
    require(exact(RF_PARAMETERS, RF_DEFAULTS), "historical RF parameters changed")
    require(exact(METADATA_PARAMETERS, LR_DEFAULTS), "metadata logistic parameters changed")
    return {
        "rf_parameters": deepcopy(RF_PARAMETERS), "rf_parameter_count": 19,
        "feature_contract": deepcopy(FEATURE_CONTRACT),
        "classical_representations": dict(CLASSICAL_REPRESENTATIONS),
        "metadata_parameters": deepcopy(METADATA_PARAMETERS),
        "metadata_features": list(METADATA_FEATURE_NAMES),
        "metadata_frame_denominators": dict(FRAME_DENOMINATORS),
        "scaler": {"copy": True, "with_mean": True, "with_std": True},
        "training_unit": "GROUP_TRAJECTORY", "seed": 42,
        "hyperparameter_search": False, "threshold_search": False,
        "acquisition_only_fit_calls": 0, "acquisition_majority_tie_class": 0,
    }


def _training_groups(groups, fold, on_event):
    validate_groups(groups)
    require(type(fold) is int and fold in range(4), "four-fold integer required")
    require(callable(on_event), "mandatory fit-budget callback required")
    require(all(int(g.cv_fold) != fold for g in groups),
            "validation groups cannot participate in training or scaler fitting")
    require({int(g.label) for g in groups} == {0, 1}, "both training classes required")
    return {
        "fold": fold, "training_groups": [str(g.group_id) for g in groups],
        "training_group_count": len(groups), "training_splits": ["TRAIN"],
        "group_counts_by_class": {str(c): sum(int(g.label) == c for g in groups)
                                  for c in (0, 1)},
        "training_only": True, "validation_used_for_training": False,
    }


def _features(values, dimension, count=None):
    import numpy as np

    require(isinstance(values, np.ndarray) and values.ndim == 2
            and values.shape[1] == dimension and len(values) > 0
            and np.issubdtype(values.dtype, np.floating)
            and bool(np.isfinite(values).all()), "finite floating feature matrix required")
    require(count is None or len(values) == count, "feature/group alignment mismatch")


def scaler_record(mean, std, groups, *, variance=None, observations_per_group=None):
    """Canonical float64 statistics hash includes the exact training identities."""
    record = {"mean": [float(v) for v in mean], "std": [float(v) for v in std],
              "training_group_ids": [str(g.group_id) for g in groups],
              "training_only": True, "ddof": 0}
    if variance is not None:
        record["variance"] = [float(v) for v in variance]
    if observations_per_group is not None:
        record["observations_per_group"] = observations_per_group
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return {**record, "sha256": hashlib.sha256(encoded).hexdigest()}


def fit_reference(X, groups, representation, *, fold, on_event):
    """Fit one unchanged historical RF to one vector per training group."""
    config = method_contract()["rf_parameters"]
    require(representation in CLASSICAL_REPRESENTATIONS, "unknown classical representation")
    metadata = _training_groups(groups, fold, on_event)
    _features(X, CLASSICAL_REPRESENTATIONS[representation], len(groups))
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(**config)
    require(exact(model.get_params(deep=False), config), "RF parameter/type divergence")
    labels = np.asarray([int(g.label) for g in groups], dtype=np.int64)
    on_event({"event": "FIT_START", "family": "RF_REFERENCE",
              "condition": representation, "fold": fold})
    random.seed(42)
    np.random.seed(42)
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(X, labels)
    elapsed = time.perf_counter() - start
    require(exact(model.get_params(deep=False), config), "RF parameters changed during fit")
    model._study3_dimension = CLASSICAL_REPRESENTATIONS[representation]
    metadata.update(family="RF_REFERENCE", condition=representation,
                    estimator_parameters=config, input_feature_dimension=model._study3_dimension,
                    fit_calls=1, runtime_seconds=elapsed, random_seed=42,
                    convergence="PASS", weighting="ONE_VECTOR_PER_GROUP_EQUAL_WEIGHT",
                    warnings=[{"category": w.category.__name__, "message": str(w.message)} for w in caught])
    on_event({"event": "FIT_COMPLETE", "family": "RF_REFERENCE",
              "condition": representation, "fold": fold})
    return model, metadata


def _prediction(model, X):
    import numpy as np

    require(list(model.classes_) == [0, 1], "binary class ordering changed")
    predicted, probabilities = np.asarray(model.predict(X)), np.asarray(model.predict_proba(X))
    require(predicted.shape == (len(X),) and bool(np.isin(predicted, [0, 1]).all())
            and probabilities.shape == (len(X), 2) and bool(np.isfinite(probabilities).all())
            and bool((probabilities >= 0).all()) and bool((probabilities <= 1).all())
            and bool(np.allclose(probabilities.sum(axis=1), 1)), "invalid classifier output")
    return {"predictions": predicted.tolist(), "probabilities": probabilities.tolist(),
            "classes": [0, 1], "decision_scores": None,
            "score_semantics": "LIBRARY_CLASS_PROBABILITIES"}


def predict_reference(model, X):
    from sklearn.ensemble import RandomForestClassifier

    require(type(model) is RandomForestClassifier
            and exact(model.get_params(deep=False), method_contract()["rf_parameters"]),
            "unchanged historical RF required")
    _features(X, getattr(model, "_study3_dimension", None))
    return _prediction(model, X)


def coverage_metadata_features(groups):
    """Four fixed coverage features; acquisition determines only frame units."""
    validate_groups(groups)
    import numpy as np

    return np.asarray([
        [np.log1p(g.n_rows), g.first_frame / FRAME_DENOMINATORS[str(g.acquisition_id)],
         g.last_frame / FRAME_DENOMINATORS[str(g.acquisition_id)],
         (g.last_frame - g.first_frame) / FRAME_DENOMINATORS[str(g.acquisition_id)]]
        for g in groups
    ], dtype=np.float64)


def fit_metadata(X, groups, *, fold, on_event):
    """One scaler+logistic pipeline fit, entirely within the training fold."""
    config = method_contract()["metadata_parameters"]
    metadata = _training_groups(groups, fold, on_event)
    _features(X, 4, len(groups))
    import numpy as np
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    require(bool(np.array_equal(X, coverage_metadata_features(groups))),
            "metadata matrix differs from the four fixed coverage features")
    estimator = LogisticRegression(**config)
    require(exact(estimator.get_params(deep=False), config), "logistic parameter/type divergence")
    model = Pipeline([("scaler", StandardScaler()), ("classifier", estimator)])
    on_event({"event": "FIT_START", "family": "COVERAGE_METADATA_LOGREG",
              "condition": "COVERAGE_METADATA_LOGREG", "fold": fold})
    random.seed(42)
    np.random.seed(42)
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(X, np.asarray([int(g.label) for g in groups], dtype=np.int64))
    elapsed = time.perf_counter() - start
    require(not any(issubclass(w.category, ConvergenceWarning) for w in caught),
            "BLOCKED_NONCONVERGENCE; no retry permitted")
    scaler = model.named_steps["scaler"]
    metadata.update(family="COVERAGE_METADATA_LOGREG", condition="COVERAGE_METADATA_LOGREG",
                    fit_calls=1, runtime_seconds=elapsed, estimator_parameters=config,
                    input_feature_dimension=4, feature_names=list(METADATA_FEATURE_NAMES),
                    random_seed=42, convergence="PASS", iterations=estimator.n_iter_.tolist(),
                    scaler=scaler_record(scaler.mean_, scaler.scale_, groups, variance=scaler.var_),
                    warnings=[{"category": w.category.__name__, "message": str(w.message)} for w in caught])
    on_event({"event": "FIT_COMPLETE", "family": "COVERAGE_METADATA_LOGREG",
              "condition": "COVERAGE_METADATA_LOGREG", "fold": fold})
    return model, metadata


def predict_metadata(model, X):
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    _features(X, 4)
    require(type(model) is Pipeline and list(model.named_steps) == ["scaler", "classifier"]
            and type(model.named_steps["scaler"]) is StandardScaler
            and type(model.named_steps["classifier"]) is LogisticRegression
            and exact(model.named_steps["classifier"].get_params(deep=False), METADATA_PARAMETERS),
            "unchanged coverage metadata pipeline required")
    return _prediction(model, X)


def acquisition_only(train_groups, validation_groups, *, fold):
    """Training-fold acquisition majority diagnostic; no estimator or fitting."""
    _training_groups(train_groups, fold, lambda event: None)
    validate_groups(validation_groups)
    require(all(int(g.cv_fold) == fold for g in validation_groups), "wrong validation fold")
    require(not {g.group_id for g in train_groups} & {g.group_id for g in validation_groups},
            "group crosses fold sides")
    counts = {acq: Counter(int(g.label) for g in train_groups if str(g.acquisition_id) == acq)
              for acq in FRAME_DENOMINATORS}
    require(all(counts.values()), "each validation acquisition requires training support")
    majority = {acq: int(counts[acq][1] > counts[acq][0]) for acq in counts}
    return {"predictions": [majority[str(g.acquisition_id)] for g in validation_groups],
            "classes": [0, 1], "probabilities": None, "decision_scores": None,
            "fit_calls": 0, "diagnostic_only": True, "tie_class": 0,
            "majority_by_acquisition": majority,
            "training_counts": {acq: {str(c): counts[acq][c] for c in (0, 1)} for acq in counts}}
