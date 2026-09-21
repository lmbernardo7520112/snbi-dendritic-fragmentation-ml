"""Study2-C classical representation, bounded fits and TRAIN-only group CV.

Import performs no science or I/O. The controller owns corpus access, manifests,
phase authority, receipts, fit budgets and the logical TEST seal. This module
accepts in-memory arrays only and never opens a source or writes a model/cache.
"""

from collections import Counter
from copy import deepcopy
import math
import random
import time
import warnings


SEED = 42
FAMILIES = ("LOGISTIC_REGRESSION", "SVM_RBF", "RF_REFERENCE", "RF_TUNED", "CNN_V2")
CLASSICAL_FAMILIES = FAMILIES[:-1]
FEATURE_CONTRACT = {
    "channels": ["STRUCTURAL_Y", "RELATIVE_SOLUTE_FIELD_Y"],
    "patch_shape": [2, 65, 65], "patch_dtype": "uint8",
    "lbp_points": 8, "lbp_radius": 1, "lbp_method": "uniform",
    "histogram_bins": 10, "histogram_range": [0, 10], "histogram_density": True,
    "feature_dimension": 20,
}
LR_DEFAULTS = {
    "penalty": "l2", "dual": False, "tol": 1e-4, "C": 1.0,
    "fit_intercept": True, "intercept_scaling": 1, "class_weight": None,
    "random_state": 42, "solver": "lbfgs", "max_iter": 10000,
    "multi_class": "deprecated", "verbose": 0, "warm_start": False,
    "n_jobs": None, "l1_ratio": None,
}
SVM_DEFAULTS = {
    "C": 1.0, "kernel": "rbf", "degree": 3, "gamma": "scale", "coef0": 0.0,
    "shrinking": True, "probability": False, "tol": 1e-3, "cache_size": 200,
    "class_weight": None, "verbose": False, "max_iter": -1,
    "decision_function_shape": "ovr", "break_ties": False, "random_state": 42,
}
RF_DEFAULTS = {
    "bootstrap": True, "ccp_alpha": 0.0, "class_weight": None, "criterion": "gini",
    "max_depth": None, "max_features": "sqrt", "max_leaf_nodes": None,
    "max_samples": None, "min_impurity_decrease": 0.0, "min_samples_leaf": 1,
    "min_samples_split": 2, "min_weight_fraction_leaf": 0.0,
    "monotonic_cst": None, "n_estimators": 100, "n_jobs": None,
    "oob_score": False, "random_state": 42, "verbose": 0, "warm_start": False,
}
SCALER_DEFAULTS = {"copy": True, "with_mean": True, "with_std": True}
CV_FOLDS = 4
CV_FITS = {"LOGISTIC_REGRESSION": 12, "SVM_RBF": 36, "RF_TUNED": 32}
CV_TIE_CONTRACT = {
    "LOGISTIC_REGRESSION": "C ascending: 0.1,1,10",
    "SVM_RBF": "C ascending, then declared gamma order: scale,0.01,0.1",
    "RF_TUNED": "n_estimators ascending, depth 8 before None, leaf 3 before 1",
    "score": "mean of four primary_gmba values; exact float tie, no tolerance",
    "svm_gamma_note": "Declared tie ordering; scale is data-adaptive and is not claimed universally simpler.",
}


class ModelContractError(ValueError):
    """Malformed inputs or failed convergence; no retry or alternate search."""


def require(condition, message):
    if not condition:
        raise ModelContractError(message)


def model_grids():
    """Fresh JSON-serializable grids already ordered by the frozen tie rule."""
    return {
        "LOGISTIC_REGRESSION": [{"C": c} for c in (0.1, 1.0, 10.0)],
        "SVM_RBF": [{"C": c, "gamma": gamma} for c in (0.1, 1.0, 10.0)
                    for gamma in ("scale", 0.01, 0.1)],
        "RF_TUNED": [{"n_estimators": trees, "max_depth": depth, "min_samples_leaf": leaf}
                     for trees in (100, 300) for depth in (8, None) for leaf in (3, 1)],
    }


def method_contract():
    """Serializable method freeze, without importing scientific libraries."""
    from .study2c_cnn import CONFIG, ARCHITECTURE

    return {"families": list(FAMILIES), "features": deepcopy(FEATURE_CONTRACT),
            "grids": model_grids(), "cv_folds": CV_FOLDS, "cv_fits": dict(CV_FITS),
            "cv_fits_total": sum(CV_FITS.values()), "cv_tie_rules": deepcopy(CV_TIE_CONTRACT),
            "logistic_defaults": deepcopy(LR_DEFAULTS), "svm_defaults": deepcopy(SVM_DEFAULTS),
            "rf_defaults": deepcopy(RF_DEFAULTS), "scaler_defaults": deepcopy(SCALER_DEFAULTS),
            "scaler_fit_weighting": "same group-equal training weights as classifier; training rows only",
            "cnn": deepcopy(CONFIG), "cnn_architecture": deepcopy(ARCHITECTURE),
            "weighting": "1/number_of_actual_training_rows_in_group; no class weights or global rescaling",
            "model_family_tie_order": list(FAMILIES),
            "cnn_batch_weight_limit": "Minibatch-normalized SGD does not imply identical effective updates per group"}


def _typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_typed_equal(a[k], b[k]) for k in a)
    return a == b


def classical_configuration(family, params):
    """Return complete frozen parameters; admit only a listed grid override."""
    require(family in CLASSICAL_FAMILIES and type(params) is dict,
            "explicit classical family and parameter mapping required")
    if family == "RF_REFERENCE":
        require(params == {}, "RF_REFERENCE does not admit tuning")
        return deepcopy(RF_DEFAULTS)
    require(any(_typed_equal(params, option) for option in model_grids()[family]),
            "parameters must equal one frozen grid candidate, including types")
    base = LR_DEFAULTS if family == "LOGISTIC_REGRESSION" else SVM_DEFAULTS if family == "SVM_RBF" else RF_DEFAULTS
    return dict(deepcopy(base), **deepcopy(params))


def validate_training_rows(rows, weights, *, train_only=False):
    """Validate group-equal weights, supervised tiers and closed TEST access."""
    import numpy as np

    require(type(rows) is list and bool(rows), "nonempty explicit training rows required")
    allowed_splits = {"TRAIN"} if train_only else {"TRAIN", "DEVELOPMENT"}
    groups, counts = {}, Counter()
    for row in rows:
        require(type(row) is dict and row.get("split") in allowed_splits,
                "TEST or unknown split cannot participate in a fit")
        group, label, acquisition, tier = (row.get(k) for k in ("group_id", "label", "acquisition_id", "tier"))
        require(type(group) is str and bool(group) and type(label) is int and label in (0, 1)
                and acquisition in {"bottom_up_anti_parallel", "top_down_parallel"},
                "canonical group, class and acquisition required")
        require((label == 1 and tier in {"GOLD", "SILVER"}) or (label == 0 and tier == "BACKGROUND"),
                "only supervised positive tiers and BACKGROUND can train")
        identity = (label, acquisition, row["split"])
        require(group not in groups or groups[group] == identity,
                "group crosses class, acquisition or split")
        groups[group] = identity
        counts[group] += 1
    require({label for label, _, _ in groups.values()} == {0, 1}, "both classes required in training")
    values = np.asarray(weights, dtype=np.float64)
    require(values.ndim == 1 and len(values) == len(rows)
            and bool(np.isfinite(values).all()) and bool((values > 0).all()),
            "finite positive weights aligned to every training row required")
    expected = np.asarray([1.0 / counts[row["group_id"]] for row in rows], dtype=np.float64)
    require(bool(np.allclose(values, expected, rtol=1e-12, atol=1e-15)),
            "weights must be exactly prospective 1/training_rows_per_group, not globally rescaled")
    return values, {
        "training_rows": len(rows), "training_group_count": len(groups),
        "training_groups": sorted(groups),
        "group_counts_by_class": {str(label): sum(identity[0] == label for identity in groups.values())
                                  for label in (0, 1)},
        "sample_counts_by_class": {str(label): sum(row["label"] == label for row in rows) for label in (0, 1)},
        "weight_sum_by_class": {str(label): math.fsum(float(w) for row, w in zip(rows, values) if row["label"] == label)
                                for label in (0, 1)},
        "weights": "1/number_of_actual_training_rows_in_group; no class_weight or global rescaling",
        "training_tier_counts": dict(sorted(Counter(row["tier"] for row in rows).items())),
        "training_splits": sorted({row["split"] for row in rows}),
    }


def _features(X, rows=None):
    import numpy as np

    require(isinstance(X, np.ndarray) and X.ndim == 2 and X.shape[1] == 20
            and X.shape[0] > 0 and np.issubdtype(X.dtype, np.floating)
            and bool(np.isfinite(X).all()), "finite floating N by 20 frozen LBP features required")
    if rows is not None:
        require(len(X) == len(rows), "feature/row count mismatch")
    return X


def checked_pairs(pairs):
    import numpy as np

    require(isinstance(pairs, np.ndarray) and pairs.dtype == np.dtype("uint8")
            and pairs.ndim == 4 and pairs.shape[1:] == (2, 65, 65) and len(pairs) > 0,
            "nonempty native uint8 N by 2 by 65 by 65 pairs required")
    return pairs


def extract_lbp20(pairs):
    """Compute exactly ten uniform-LBP histogram bins per native Y modality."""
    checked_pairs(pairs)
    import numpy as np
    from skimage.feature import local_binary_pattern

    result = np.empty((len(pairs), 20), dtype=np.float64)
    for row_index, pair in enumerate(pairs):
        for channel in (0, 1):
            lbp = local_binary_pattern(pair[channel], P=8, R=1, method="uniform")
            hist, _ = np.histogram(lbp, bins=10, range=(0, 10), density=True)
            result[row_index, channel * 10:(channel + 1) * 10] = hist
    require(bool(np.isfinite(result).all()), "nonfinite frozen feature representation")
    return result


def fit_classical(family, params, X, rows, weights):
    """One fit of a frozen classical pipeline; no search, evaluation or I/O."""
    configuration = classical_configuration(family, params)
    _features(X, rows)
    values, group_metadata = validate_training_rows(rows, weights)
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    random.seed(SEED)
    np.random.seed(SEED)
    labels = np.asarray([row["label"] for row in rows], dtype=np.int64)
    if family in {"LOGISTIC_REGRESSION", "SVM_RBF"}:
        estimator = LogisticRegression(**configuration) if family == "LOGISTIC_REGRESSION" else SVC(**configuration)
        model = Pipeline([("scaler", StandardScaler(**SCALER_DEFAULTS)), ("classifier", estimator)])
        fit_options = {"scaler__sample_weight": values, "classifier__sample_weight": values}
    else:
        estimator = RandomForestClassifier(**configuration)
        model = estimator
        fit_options = {"sample_weight": values}
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(X, labels, **fit_options)
    elapsed = time.perf_counter() - start
    convergence = [str(w.message) for w in caught if issubclass(w.category, ConvergenceWarning)]
    require(not convergence, "BLOCKED_NONCONVERGENCE: " + " | ".join(convergence))
    if family == "SVM_RBF":
        require(estimator.fit_status_ == 0, "BLOCKED_NONCONVERGENCE: SVC fit_status")
    metadata = {
        "family": family, "chosen_grid_parameters": deepcopy(params),
        "estimator_parameters": estimator.get_params(deep=False),
        "scaler_parameters": deepcopy(SCALER_DEFAULTS) if family in {"LOGISTIC_REGRESSION", "SVM_RBF"} else None,
        "weighted_scaler": family in {"LOGISTIC_REGRESSION", "SVM_RBF"},
        "fit_calls": 1, "runtime_seconds": elapsed, "convergence": "PASS",
        "warnings": [{"category": w.category.__name__, "message": str(w.message)} for w in caught],
        "random_seed": SEED, "input_feature_dimension": 20, **group_metadata,
    }
    if hasattr(estimator, "n_iter_"):
        metadata["iterations"] = np.asarray(estimator.n_iter_).tolist()
    if family == "SVM_RBF":
        metadata["fitted_gamma"] = float(estimator._gamma)
        metadata["probability_calibration"] = False
    return model, metadata


def predict_classical(model, X):
    """Predict without labels; retain actual library probabilities or scores."""
    _features(X)
    import numpy as np

    predictions = np.asarray(model.predict(X))
    require(predictions.shape == (len(X),) and bool(np.isin(predictions, [0, 1]).all()),
            "binary predictions required")
    result = {"predictions": [int(v) for v in predictions], "probabilities": None,
              "decision_scores": None, "classes": [0, 1]}
    require(list(model.classes_) == [0, 1], "class probability/score order differs")
    if hasattr(model, "predict_proba"):
        probabilities = np.asarray(model.predict_proba(X))
        require(probabilities.shape == (len(X), 2) and bool(np.isfinite(probabilities).all())
                and bool((probabilities >= 0).all()) and bool((probabilities <= 1).all())
                and bool(np.allclose(probabilities.sum(axis=1), 1.0)), "invalid actual probabilities")
        result["probabilities"] = probabilities.tolist()
        result["score_semantics"] = "LIBRARY_CLASS_PROBABILITIES"
    elif hasattr(model, "decision_function"):
        scores = np.asarray(model.decision_function(X))
        require(scores.shape == (len(X),) and bool(np.isfinite(scores).all()), "invalid binary decision scores")
        result["decision_scores"] = scores.tolist()
        result["score_semantics"] = "SVC_SIGNED_DECISION_FUNCTION_NOT_PROBABILITY"
    else:
        raise ModelContractError("model lacks declared probability or decision-score interface")
    return result


def cv_search(family, X, rows, fold_by_group, progress=None):
    """Evaluate each fixed candidate in four frozen TRAIN group folds once.

    Winning candidate is selected using mean primary GMBA exclusively. A tie
    retains the earlier candidate in the preregistered complexity order. The
    return value does not include a refit model; the controller separately owns
    the one subsequent full-TRAIN scientific development fit.
    """
    from .study2c_design import group_equal_weights, metric_bundle

    require(family in model_grids(), "RF_REFERENCE/CNN do not enter classical hyperparameter CV")
    _features(X, rows)
    validate_training_rows(rows, group_equal_weights(rows), train_only=True)
    require(all(row["tier"] in {"GOLD", "BACKGROUND"} for row in rows), "initial CV cannot consume SILVER")
    groups = {row["group_id"] for row in rows}
    require(type(fold_by_group) is dict and set(fold_by_group) == groups
            and all(type(fold) is int and fold in range(4) for fold in fold_by_group.values())
            and set(fold_by_group.values()) == set(range(4)), "four complete frozen group folds required")
    require(progress is None or callable(progress), "progress must be callable or absent")
    strata = {group: (next(row for row in rows if row["group_id"] == group)["acquisition_id"],
                      next(row for row in rows if row["group_id"] == group)["label"]) for group in groups}
    counts = Counter(strata.values())
    for fold in range(4):
        present = {strata[g] for g in groups if fold_by_group[g] == fold}
        require(all(count < 4 or stratum in present for stratum, count in counts.items()),
                "fold omitted an acquisition/class stratum despite feasible group capacity")
    options, reports, fit_calls = model_grids()[family], [], 0
    for candidate_index, params in enumerate(options):
        folds = []
        for fold in range(4):
            train_indices = [i for i, row in enumerate(rows) if fold_by_group[row["group_id"]] != fold]
            valid_indices = [i for i, row in enumerate(rows) if fold_by_group[row["group_id"]] == fold]
            train_rows = [rows[i] for i in train_indices]
            valid_rows = [rows[i] for i in valid_indices]
            require(train_rows and valid_rows and {r["label"] for r in valid_rows} == {0, 1},
                    "each CV training/validation fold requires nonempty classes")
            if progress:
                progress({"event": "CV_FIT_START", "family": family,
                          "candidate_index": candidate_index, "fold": fold, "fit_ordinal": fit_calls + 1})
            model, fit_metadata = fit_classical(family, params, X[train_indices], train_rows,
                                                group_equal_weights(train_rows))
            fit_calls += 1
            if progress:
                progress({"event": "CV_FIT_COMPLETE", "family": family,
                          "candidate_index": candidate_index, "fold": fold,
                          "fit_ordinal": fit_calls})
            predicted = predict_classical(model, X[valid_indices])
            metrics = metric_bundle(valid_rows, predicted["predictions"])
            score = metrics["primary_gmba"]
            require(type(score) in (float, int) and math.isfinite(score) and 0 <= score <= 1,
                    "invalid CV primary GMBA")
            folds.append({"fold": fold, "primary_gmba": float(score),
                          "validation_groups": sorted({r["group_id"] for r in valid_rows}),
                          "validation_rows": len(valid_rows), "fit": fit_metadata})
            if progress:
                progress({"event": "CV_FOLD_COMPLETE", "family": family,
                          "candidate_index": candidate_index, "fold": fold, "fit_ordinal": fit_calls,
                          "primary_gmba": float(score)})
            del model
        reports.append({"candidate_index": candidate_index, "parameters": deepcopy(params),
                        "folds": folds, "mean_primary_gmba": math.fsum(f["primary_gmba"] for f in folds) / 4})
    require(fit_calls == CV_FITS[family], "CV fit budget differs from frozen grid")
    best = max(range(len(reports)), key=lambda i: reports[i]["mean_primary_gmba"])
    selected = deepcopy(options[best])
    return selected, {"family": family, "fold_count": 4, "fit_calls": fit_calls,
                      "candidate_count": len(options), "candidates": reports,
                      "selected_candidate_index": best, "selected_parameters": selected,
                      "selected_overrides": deepcopy(selected),
                      "selected_mean_primary_gmba": reports[best]["mean_primary_gmba"],
                      "primary_metric": "GROUP_MACRO_BALANCED_ACCURACY",
                      "tie_rule": CV_TIE_CONTRACT[family], "dev_or_test_used": False,
                      "refit_performed": False}
