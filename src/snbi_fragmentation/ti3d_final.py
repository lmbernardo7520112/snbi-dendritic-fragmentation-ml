"""One final multimodal LBP/RF fit, then prediction-first final scoring.

No filesystem, experimental reader, model export or model selection exists
here. The runner supplies authorized arrays and durable exclusive text writers.
Every scientific stage is single-use, including an unsuccessful attempt.
"""

import copy
import hashlib
import json

from .ti3_baseline import (
    REQUIRED_VERSIONS, RF_PARAMETERS, _classification_metrics, _scientific_runtime,
)
from .ti3b_ablation import multimodal_features
from .ti3_dataset import ACQUISITIONS, FRAME_SPLITS


FINAL_MODEL_PARAMETERS = copy.deepcopy(RF_PARAMETERS)
FEATURE_DIMENSION = 20
MODEL_FAMILY = "MULTIMODAL_LBP_RF"
TRAINING_COMPOSITION = {
    "bottom_up_anti_parallel": {"POSITIVE": 19, "BACKGROUND_CANDIDATE": 8},
    "top_down_parallel": {"POSITIVE": 6, "BACKGROUND_CANDIDATE": 17},
}


class FinalContractError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


def _require(condition, code, message):
    if not condition:
        raise FinalContractError(code, message)


def canonical_bytes(value):
    """The exact bytes the runner must exclusively write and fsync."""
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _exact(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_exact(left[key], right[key]) for key in left)
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(_exact(a, b) for a, b in zip(left, right))
    return left == right


def _ids(values, size):
    _require(type(values) in (list, tuple) and len(values) == size
             and all(type(value) is str and value for value in values)
             and len(set(values)) == size,
             "SAMPLE_CONTRACT", f"exactly {size} unique ordered sample IDs required")
    return tuple(values)


def validate_sample_contract(training_samples, final_samples):
    """Validate existing metadata without reading arrays or choosing samples."""
    _require(type(training_samples) is list and len(training_samples) == 50
             and type(final_samples) is list and len(final_samples) == 6,
             "SAMPLE_CONTRACT", "exactly 50 final-training and six final samples required")
    groups = ((training_samples, ("TRAIN", "DEVELOPMENT"), 25),
              (final_samples, ("FINAL_TEST",), 3))
    for samples, allowed, positive_count in groups:
        for sample in samples:
            _require(type(sample) is dict, "SAMPLE_CONTRACT", "sample record required")
            source, frame = sample.get("source_id"), sample.get("frame_index")
            _require(type(source) is str and type(frame) is int
                     and source in ACQUISITIONS and (source, frame) in FRAME_SPLITS
                     and sample.get("split") in allowed
                     and FRAME_SPLITS[(source, frame)] == sample["split"]
                     and sample.get("acquisition_id") == ACQUISITIONS[source],
                     "SAMPLE_CONTRACT", "original source/frame/acquisition/split must agree")
            _require(type(sample.get("baseline_label")) is int and sample["baseline_label"] in (0, 1),
                     "SAMPLE_CONTRACT", "binary integer weak label required")
            _require(sample.get("context_group") == f"{sample['acquisition_id']}|{source}|{frame}",
                     "SAMPLE_CONTRACT", "original context group differs")
        _require(sum(sample["baseline_label"] for sample in samples) == positive_count,
                 "SAMPLE_CONTRACT", "frozen class counts differ")
    training_ids = _ids([sample.get("sample_id") for sample in training_samples], 50)
    final_ids = _ids([sample.get("sample_id") for sample in final_samples], 6)
    _require(not set(training_ids).intersection(final_ids), "SAMPLE_CONTRACT", "training/final ID overlap")
    _require(not {s["context_group"] for s in training_samples}.intersection(
        s["context_group"] for s in final_samples), "SAMPLE_CONTRACT", "training/final context overlap")
    _require(sum(s["split"] == "TRAIN" for s in training_samples) == 34
             and sum(s["split"] == "DEVELOPMENT" for s in training_samples) == 16,
             "SAMPLE_CONTRACT", "original 34 TRAIN and 16 DEVELOPMENT required")
    composition = {
        acquisition: {
            "POSITIVE": sum(s["acquisition_id"] == acquisition and s["baseline_label"] == 1
                            for s in training_samples),
            "BACKGROUND_CANDIDATE": sum(s["acquisition_id"] == acquisition and s["baseline_label"] == 0
                                       for s in training_samples),
        } for acquisition in TRAINING_COMPOSITION
    }
    _require(_exact(composition, TRAINING_COMPOSITION), "SAMPLE_CONTRACT", "acquisition/class composition differs")
    return {"training_sample_ids": list(training_ids), "final_sample_ids": list(final_ids),
            "training_sample_count": 50, "final_sample_count": 6,
            "training_class_counts": {"0": 25, "1": 25},
            "final_class_counts": {"0": 3, "1": 3}, "training_composition": composition}


def _features(np, features, size):
    _require(isinstance(features, np.ndarray) and features.shape == (size, FEATURE_DIMENSION)
             and features.dtype == np.dtype("float64") and np.isfinite(features).all()
             and not (features < 0).any() and not (features > 1).any(),
             "FEATURE_CONTRACT", f"exact finite float64 {size}-by-20 features required")
    for half in (features[:, :10], features[:, 10:]):
        _require(np.allclose(half.sum(axis=1), 1.0, rtol=0.0, atol=1e-12),
                 "FEATURE_CONTRACT", "each unchanged ten-bin histogram must sum to one")


def _labels(np, labels, size, positives):
    _require(isinstance(labels, np.ndarray) and labels.shape == (size,)
             and labels.dtype.kind in "iu" and np.isin(labels, [0, 1]).all()
             and int(labels.sum()) == positives,
             "LABEL_CONTRACT", "exact aligned binary weak-label counts required")


def logical_model_sha256(model, training_ids):
    """Digest complete fitted predictive tree state, never serialize a model.

    SHA-256 is domain separated by a canonical JSON header. Each array is
    framed by its path, little-endian dtype and shape, followed by a length
    and C-order bytes. Structured node fields are hashed individually in dtype
    field order, avoiding uninitialized struct padding. Every tree's scalar
    state, nodes, values, class and feature metadata, seed and full estimator
    parameters participate. Only this digest is returned; no arrays leave.
    """
    np = _scientific_runtime()
    digest = hashlib.sha256()

    def part(payload):
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)

    def array(path, value):
        value = np.asarray(value)
        _require(value.dtype.kind in "biuf", "MODEL_CONTRACT", "unexpected fitted-state dtype")
        value = np.ascontiguousarray(value.astype(value.dtype.newbyteorder("<"), copy=False))
        part(canonical_bytes({"path": path, "dtype": value.dtype.str, "shape": list(value.shape)}))
        part(value.tobytes(order="C"))

    part(canonical_bytes({
        "schema": "TI3D-RF-LOGICAL-STATE-SHA256-1", "model_family": MODEL_FAMILY,
        "parameters": model.get_params(deep=True), "training_sample_ids": list(training_ids),
        "versions": REQUIRED_VERSIONS, "n_features_in": int(model.n_features_in_),
        "n_outputs": int(model.n_outputs_), "estimator_count": len(model.estimators_),
    }))
    array("forest/classes", model.classes_)
    array("forest/n_classes", model.n_classes_)
    for index, estimator in enumerate(model.estimators_):
        tree = estimator.tree_
        state = tree.__getstate__()
        _require(set(state) == {"max_depth", "node_count", "nodes", "values"},
                 "MODEL_CONTRACT", "unrecognized fitted tree state")
        part(canonical_bytes({
            "tree_index": index, "parameters": estimator.get_params(deep=True),
            "max_depth": int(state["max_depth"]), "node_count": int(state["node_count"]),
            "n_features": int(tree.n_features), "n_outputs": int(tree.n_outputs),
            "estimator_n_features_in": int(estimator.n_features_in_),
            "estimator_n_outputs": int(estimator.n_outputs_),
            "node_fields": list(state["nodes"].dtype.names),
        }))
        array(f"tree/{index}/classes", estimator.classes_)
        array(f"tree/{index}/n_classes", estimator.n_classes_)
        array(f"tree/{index}/tree_n_classes", tree.n_classes)
        for field in state["nodes"].dtype.names:
            array(f"tree/{index}/nodes/{field}", state["nodes"][field])
        array(f"tree/{index}/values", state["values"])
    return digest.hexdigest()


def _predictions(np, model, features, size):
    predicted = model.predict(features)
    probability = model.predict_proba(features)
    _require(np.array_equal(model.classes_, np.array([0, 1]))
             and predicted.shape == (size,) and np.isin(predicted, [0, 1]).all()
             and probability.shape == (size, 2) and np.isfinite(probability).all()
             and not (probability < 0).any() and not (probability > 1).any()
             and np.allclose(probability.sum(axis=1), 1.0, rtol=0.0, atol=1e-12),
             "MODEL_CONTRACT", "RF predict/probability contract differs")
    return predicted, probability


class FinalEvaluationSession:
    """In-memory single-fit state machine; durable receipt remains runner-owned."""

    def __init__(self, training_ids, final_ids):
        self.training_ids = _ids(training_ids, 50)
        self.final_ids = _ids(final_ids, 6)
        _require(not set(self.training_ids).intersection(self.final_ids),
                 "SAMPLE_CONTRACT", "training/final IDs overlap")
        self.state = "CREATED"
        self._fit_calls = self._inference_calls = self._evaluations = 0
        self._fit_record = self._prediction_record = self._final_result = None
        self._model = None
        self.fit_record_sha256 = self.predictions_sha256 = None

    @property
    def counters(self):
        return {"final_fit_calls": self._fit_calls, "final_inference_calls": self._inference_calls,
                "final_evaluations": self._evaluations, "model_selection_runs": 0, "tuning_runs": 0}

    @property
    def fit_record(self):
        return copy.deepcopy(self._fit_record)

    @property
    def prediction_records(self):
        return copy.deepcopy(None if self._prediction_record is None else self._prediction_record["predictions"])

    @property
    def final_result(self):
        return copy.deepcopy(self._final_result)

    def _enter(self, required, entered):
        _require(self.state == required, "SINGLE_USE_ORDER", f"requires {required}; current {self.state}")
        self.state = entered

    def fit(self, training_features, training_labels):
        self._enter("CREATED", "FIT_STARTED")
        np = _scientific_runtime()
        _features(np, training_features, 50)
        _labels(np, training_labels, 50, 25)
        from sklearn.ensemble import RandomForestClassifier

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        parameters = model.get_params(deep=True)
        _require(_exact(parameters, FINAL_MODEL_PARAMETERS), "MODEL_CONTRACT", "RF parameters differ from TI3-B")
        self._fit_calls += 1
        model.fit(training_features, training_labels)
        self._model = model
        logical_hash = logical_model_sha256(model, self.training_ids)
        prediction, probability = _predictions(np, model, training_features, 50)
        self._fit_record = {
            "schema": "TI3D-FINAL-FIT-1", "model_family": MODEL_FAMILY,
            "final_fit_calls": 1, "parameters": parameters, "feature_dimension": 20,
            "feature_order": ["STRUCTURAL_LBP_10", "SOLUTAL_LBP_10"],
            "training_sample_ids": list(self.training_ids), "training_sample_count": 50,
            "training_class_counts": {"0": 25, "1": 25},
            "training_composition": copy.deepcopy(TRAINING_COMPOSITION),
            "logical_model_sha256": logical_hash,
            "logical_hash_schema": "TI3D-RF-LOGICAL-STATE-SHA256-1",
            "dependency_versions": dict(REQUIRED_VERSIONS), "model_selection_reopened": False,
            "descriptive_resubstitution": {
                **_classification_metrics(training_labels, prediction),
                "true_labels": training_labels.tolist(), "predicted_labels": prediction.tolist(),
                "probabilities_class_order_0_1": probability.tolist(),
                "scope": "RESUBSTITUTION_ONLY_NO_DECISION_NO_GENERALIZATION_ESTIMATE",
            },
        }
        self.state = "FITTED"
        return self.fit_record

    def freeze_fit(self, write_once):
        self._enter("FITTED", "FIT_FREEZING")
        record = self.fit_record
        expected = hashlib.sha256(canonical_bytes(record)).hexdigest()
        observed = write_once(record)
        _require(type(observed) is str and observed == expected,
                 "FREEZE_FAILED", "fit record writer did not confirm exact durable text")
        self.fit_record_sha256 = observed
        self.state = "FIT_FROZEN"
        return observed

    def infer(self, final_features, final_ids):
        """No true labels enter this interface or sklearn prediction methods."""
        self._enter("FIT_FROZEN", "INFERENCE_STARTED")
        _require(_ids(final_ids, 6) == self.final_ids, "SAMPLE_CONTRACT", "final inference order differs")
        np = _scientific_runtime()
        _features(np, final_features, 6)
        _require(logical_model_sha256(self._model, self.training_ids) == self._fit_record["logical_model_sha256"],
                 "MODEL_CONTRACT", "fitted model changed after freeze")
        self._inference_calls += 1
        prediction, probability = _predictions(np, self._model, final_features, 6)
        records = [{"sample_id": sample_id, "predicted_label": int(label),
                    "probability_class_0": float(probs[0]), "probability_class_1": float(probs[1])}
                   for sample_id, label, probs in zip(self.final_ids, prediction, probability)]
        self._prediction_record = {
            "schema": "TI3D-PREDICTIONS-FIRST-1", "evaluation": "PREDICTION_FIRST_FINAL_EVALUATION",
            "fit_record_sha256": self.fit_record_sha256,
            "logical_model_sha256": self._fit_record["logical_model_sha256"],
            "predictions": records,
        }
        self.state = "PREDICTED"
        return self.prediction_records

    def freeze_predictions(self, write_once):
        self._enter("PREDICTED", "PREDICTION_FREEZING")
        record = copy.deepcopy(self._prediction_record)
        expected = hashlib.sha256(canonical_bytes(record)).hexdigest()
        observed = write_once(record)
        _require(type(observed) is str and observed == expected,
                 "FREEZE_FAILED", "prediction writer did not confirm exact durable text")
        self.predictions_sha256 = observed
        self.state = "PREDICTIONS_FROZEN"
        return observed

    def score(self, final_labels, final_ids):
        self._enter("PREDICTIONS_FROZEN", "SCORING_STARTED")
        _require(_ids(final_ids, 6) == self.final_ids, "SAMPLE_CONTRACT", "final scoring order differs")
        np = _scientific_runtime()
        _labels(np, final_labels, 6, 3)
        self._evaluations += 1
        records = self._prediction_record["predictions"]
        prediction = np.asarray([record["predicted_label"] for record in records], dtype=int)
        self._final_result = {
            **_classification_metrics(final_labels, prediction),
            "sample_ids": list(self.final_ids), "true_labels": final_labels.tolist(),
            "predicted_labels": prediction.tolist(),
            "probabilities_class_order_0_1": [[r["probability_class_0"], r["probability_class_1"]] for r in records],
            "prediction_record_sha256": self.predictions_sha256,
            "evaluation": "PREDICTION_FIRST_FINAL_EVALUATION",
            "result_scope": "SMALL_INTERNAL_TEMPORAL_CONFIRMATION", "primary_metric": "balanced_accuracy",
            "positive_semantics": "PUBLISHED_FRAGMENTATION_LOCATION_PRESENT",
            "background_semantics": "BACKGROUND_CANDIDATE_NOT_PHYSICAL_ABSENCE",
            "model_selection_reopened": False,
        }
        self.state = "SCORED"
        return self.final_result
