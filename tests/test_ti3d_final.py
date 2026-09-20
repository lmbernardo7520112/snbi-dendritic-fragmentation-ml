"""Synthetic final-fit and prediction-first contracts; no experimental I/O."""

import copy
import hashlib
import importlib.util
import inspect
import unittest
from unittest import mock

from snbi_fragmentation import ti3d_final as final


NUMERICAL = all(importlib.util.find_spec(name) is not None
                for name in ("numpy", "scipy", "skimage", "sklearn"))


def metadata_samples():
    training, reserved = [], []
    for target, source, frame, split, positive, background in (
        (training, "ESM1", 73, "TRAIN", 16, 6),
        (training, "ESM4", 98, "TRAIN", 1, 11),
        (training, "ESM1", 219, "DEVELOPMENT", 3, 2),
        (training, "ESM4", 197, "DEVELOPMENT", 5, 6),
        (reserved, "ESM1", 293, "FINAL_TEST", 2, 1),
        (reserved, "ESM4", 295, "FINAL_TEST", 1, 2),
    ):
        acquisition = "bottom_up_anti_parallel" if source == "ESM1" else "top_down_parallel"
        for label, count in ((1, positive), (0, background)):
            for index in range(count):
                target.append({"sample_id": f"synthetic|{source}|{frame}|{label}|{index}",
                               "source_id": source, "frame_index": frame, "split": split,
                               "acquisition_id": acquisition, "baseline_label": label,
                               "context_group": f"{acquisition}|{source}|{frame}"})
    return training, reserved


def session():
    return final.FinalEvaluationSession([f"training-{i}" for i in range(50)],
                                        [f"final-{i}" for i in range(6)])


def text_writer(record):
    return hashlib.sha256(final.canonical_bytes(record)).hexdigest()


class FinalMetadataTests(unittest.TestCase):
    def test_fifty_training_six_final_counts_and_fixed_acquisition_composition(self):
        training, reserved = metadata_samples()
        before = copy.deepcopy((training, reserved))
        report = final.validate_sample_contract(training, reserved)
        self.assertEqual(report["training_sample_count"], 50)
        self.assertEqual(report["final_sample_count"], 6)
        self.assertEqual(report["training_class_counts"], {"0": 25, "1": 25})
        self.assertEqual(report["final_class_counts"], {"0": 3, "1": 3})
        self.assertEqual(report["training_composition"], final.TRAINING_COMPOSITION)
        self.assertEqual((training, reserved), before)

    def test_wrong_counts_classes_types_or_acquisition_cannot_change_training_policy(self):
        training, reserved = metadata_samples()
        cases = [(training[:-1], reserved), (training, reserved[:-1])]
        for field, value in (("baseline_label", 0), ("baseline_label", True),
                             ("acquisition_id", "top_down_parallel"), ("split", "FINAL_TEST"),
                             ("frame_index", True), ("context_group", "different")):
            changed = copy.deepcopy(training)
            changed[0][field] = value
            cases.append((changed, reserved))
        changed = copy.deepcopy(reserved)
        changed[0]["baseline_label"] = 0
        cases.append((training, changed))
        for left, right in cases:
            with self.subTest(first=left[0]), self.assertRaises(final.FinalContractError):
                final.validate_sample_contract(left, right)

    def test_duplicate_and_overlapping_ids_rejected(self):
        training, reserved = metadata_samples()
        for same_partition in (True, False):
            changed = copy.deepcopy(reserved)
            changed[0]["sample_id"] = reserved[1]["sample_id"] if same_partition else training[0]["sample_id"]
            with self.assertRaises(final.FinalContractError):
                final.validate_sample_contract(training, changed)
        with self.assertRaises(final.FinalContractError):
            final.FinalEvaluationSession([f"id{i}" for i in range(50)], [f"id{i}" for i in range(6)])

    def test_preserved_split_and_context_prevent_final_becoming_training(self):
        training, reserved = metadata_samples()
        changed = copy.deepcopy(training)
        changed[0] |= {"frame_index": 293, "split": "TRAIN"}
        with self.assertRaises(final.FinalContractError):
            final.validate_sample_contract(changed, reserved)
        changed = copy.deepcopy(training)
        changed[0]["split"] = "DEVELOPMENT"
        with self.assertRaises(final.FinalContractError):
            final.validate_sample_contract(changed, reserved)

    def test_inference_has_no_label_or_threshold_interface(self):
        self.assertEqual(list(inspect.signature(final.FinalEvaluationSession.infer).parameters),
                         ["self", "final_features", "final_ids"])
        self.assertEqual(list(inspect.signature(final.FinalEvaluationSession.fit).parameters),
                         ["self", "training_features", "training_labels"])
        self.assertEqual(final.FINAL_MODEL_PARAMETERS["n_estimators"], 100)
        self.assertEqual(final.FINAL_MODEL_PARAMETERS["random_state"], 42)
        self.assertEqual(final.FINAL_MODEL_PARAMETERS["class_weight"], None)

    def test_scoring_before_predictions_and_inference_before_fit_freeze_are_denied(self):
        evaluator = session()
        with mock.patch.object(final, "_scientific_runtime") as runtime:
            with self.assertRaises(final.FinalContractError):
                evaluator.infer(object(), evaluator.final_ids)
            with self.assertRaises(final.FinalContractError):
                evaluator.score(object(), evaluator.final_ids)
            runtime.assert_not_called()
        self.assertEqual(evaluator.counters["final_evaluations"], 0)

    def test_failed_fit_text_freeze_permanently_denies_final_inference(self):
        evaluator = session()
        evaluator.state = "FITTED"
        evaluator._fit_record = {"synthetic": "no model or pixels"}
        with self.assertRaises(final.FinalContractError):
            evaluator.freeze_fit(lambda record: "0" * 64)
        with self.assertRaises(final.FinalContractError):
            evaluator.freeze_fit(text_writer)
        with self.assertRaises(final.FinalContractError):
            evaluator.infer(object(), evaluator.final_ids)

    def test_failed_prediction_text_freeze_never_allows_scoring_or_rewrite(self):
        evaluator = session()
        evaluator.state = "PREDICTED"
        evaluator._prediction_record = {"synthetic": "no predictions"}
        with self.assertRaises(OSError):
            evaluator.freeze_predictions(mock.Mock(side_effect=OSError("exclusive writer failure")))
        with self.assertRaises(final.FinalContractError):
            evaluator.freeze_predictions(text_writer)
        with self.assertRaises(final.FinalContractError):
            evaluator.score(object(), evaluator.final_ids)


@unittest.skipUnless(NUMERICAL, "optional pinned scientific dependencies unavailable")
class FinalSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.np = np

    def features(self, count):
        np = self.np
        labels = np.array([0, 1] * (count // 2), dtype=int)
        features = np.zeros((count, 20), dtype=np.float64)
        features[np.arange(count), labels] = 1.0
        features[np.arange(count), labels + 10] = 1.0
        return features, labels

    def test_feature_dimension_and_histogram_fail_before_constructor(self):
        np = self.np
        features, labels = self.features(50)
        cases = (features[:, :10], features[:, :19], features[:49], features.astype(np.float32),
                 features / 2, np.full((50, 20), np.nan))
        for invalid in cases:
            with self.subTest(shape=invalid.shape), mock.patch("sklearn.ensemble.RandomForestClassifier") as constructor:
                with self.assertRaises(final.FinalContractError):
                    session().fit(invalid, labels)
                constructor.assert_not_called()

    def test_training_class_count_and_exact_integer_labels_fail_before_fit(self):
        np = self.np
        features, labels = self.features(50)
        altered = labels.copy()
        altered[0] = 1
        for invalid in (labels[:-1], labels.astype(bool), labels.astype(float), altered,
                        np.zeros(50, dtype=int), labels + 1):
            with mock.patch("sklearn.ensemble.RandomForestClassifier") as constructor:
                with self.assertRaises(final.FinalContractError):
                    session().fit(features, invalid)
                constructor.assert_not_called()

    def test_parameter_or_parameter_type_drift_denies_before_fit(self):
        features, labels = self.features(50)
        for change in ({"class_weight": "balanced"}, {"n_estimators": 101},
                       {"random_state": 43}, {"ccp_alpha": 0}, {"max_features": None}):
            estimator = mock.Mock()
            estimator.get_params.return_value = final.FINAL_MODEL_PARAMETERS | change
            with mock.patch("sklearn.ensemble.RandomForestClassifier", return_value=estimator):
                with self.assertRaises(final.FinalContractError):
                    session().fit(features, labels)
                estimator.fit.assert_not_called()

    def test_failed_fit_counts_once_and_prevents_retry(self):
        features, labels = self.features(50)
        estimator = mock.Mock()
        estimator.get_params.return_value = copy.deepcopy(final.FINAL_MODEL_PARAMETERS)
        estimator.fit.side_effect = ValueError("synthetic fit failure")
        evaluator = session()
        with mock.patch("sklearn.ensemble.RandomForestClassifier", return_value=estimator):
            with self.assertRaises(ValueError):
                evaluator.fit(features, labels)
            with self.assertRaises(final.FinalContractError):
                evaluator.fit(features, labels)
        estimator.fit.assert_called_once()
        self.assertEqual(evaluator.counters["final_fit_calls"], 1)

    def test_unchanged_multimodal_feature_order(self):
        from snbi_fragmentation.ti3_baseline import lbp_features
        np = self.np
        structural = (np.arange(65 * 65).reshape(65, 65) % 253).astype(np.uint8)
        solutal = np.full((65, 65), 128, dtype=np.uint8)
        features = final.multimodal_features(structural, solutal)
        self.assertEqual(features.shape, (20,))
        np.testing.assert_array_equal(features[:10], lbp_features(structural))
        np.testing.assert_array_equal(features[10:], lbp_features(solutal))

    def test_one_real_synthetic_rf_fit_prediction_first_hash_and_single_final_score(self):
        """This is the sole actual RF fit in this new core test module."""
        from sklearn.ensemble import RandomForestClassifier
        from snbi_fragmentation import ti3_baseline, ti3b_ablation
        features, labels = self.features(50)
        final_features, final_labels = self.features(6)
        estimator = RandomForestClassifier(n_estimators=100, random_state=42)
        evaluator = session()
        timeline, texts = [], []

        def writer(kind):
            def freeze(record):
                payload = final.canonical_bytes(record)
                texts.append(payload)
                timeline.append(kind)
                return hashlib.sha256(payload).hexdigest()
            return freeze

        with mock.patch("sklearn.ensemble.RandomForestClassifier", return_value=estimator) as constructor:
            with mock.patch.object(estimator, "fit", wraps=estimator.fit) as fit:
                with mock.patch.object(ti3_baseline, "evaluate_baseline", side_effect=AssertionError("old baseline")):
                    with mock.patch.object(ti3b_ablation, "evaluate_ablation", side_effect=AssertionError("old ablation")):
                        with mock.patch.dict("sys.modules", {"torch": None}):
                            record = evaluator.fit(features, labels)
                constructor.assert_called_once_with(n_estimators=100, random_state=42)
                fit.assert_called_once()
        self.assertEqual(record["parameters"], final.FINAL_MODEL_PARAMETERS)
        self.assertEqual(record["training_sample_count"], 50)
        self.assertEqual(record["descriptive_resubstitution"]["sample_count"], 50)
        original_hash = record["logical_model_sha256"]
        self.assertEqual(original_hash, final.logical_model_sha256(estimator, evaluator.training_ids))
        # Every predictive numeric field participates; no retraining is needed
        # to prove mutation sensitivity of this in-memory synthetic forest.
        threshold = estimator.estimators_[0].tree_.threshold
        previous = threshold[0]
        threshold[0] = previous + 0.125
        self.assertNotEqual(original_hash, final.logical_model_sha256(estimator, evaluator.training_ids))
        threshold[0] = previous
        self.assertEqual(original_hash, final.logical_model_sha256(estimator, evaluator.training_ids))
        with self.assertRaises(final.FinalContractError):
            evaluator.infer(final_features, evaluator.final_ids)
        evaluator.freeze_fit(writer("fit_frozen"))
        with mock.patch.object(estimator, "predict", wraps=estimator.predict) as predict:
            records = evaluator.infer(final_features, evaluator.final_ids)
            predict.assert_called_once()
        for item in records:
            self.assertEqual(set(item), {"sample_id", "predicted_label", "probability_class_0", "probability_class_1"})
        with self.assertRaises(final.FinalContractError):
            evaluator.score(final_labels, evaluator.final_ids)
        evaluator.freeze_predictions(writer("predictions_frozen"))
        with mock.patch.object(estimator, "predict", side_effect=AssertionError("scoring repeated inference")):
            result = evaluator.score(final_labels, evaluator.final_ids)
        timeline.append("scored")
        self.assertEqual(timeline, ["fit_frozen", "predictions_frozen", "scored"])
        self.assertEqual(result["prediction_record_sha256"], hashlib.sha256(texts[1]).hexdigest())
        self.assertEqual(result["confusion_matrix"], [[3, 0], [0, 3]])
        self.assertEqual(result["balanced_accuracy"], 1.0)
        self.assertFalse(result["model_selection_reopened"])
        self.assertEqual(evaluator.counters, {"final_fit_calls": 1, "final_inference_calls": 1,
                                             "final_evaluations": 1, "model_selection_runs": 0, "tuning_runs": 0})
        for operation in (lambda: evaluator.fit(features, labels),
                          lambda: evaluator.freeze_fit(text_writer),
                          lambda: evaluator.infer(final_features, evaluator.final_ids),
                          lambda: evaluator.freeze_predictions(text_writer),
                          lambda: evaluator.score(final_labels, evaluator.final_ids)):
            with self.assertRaises(final.FinalContractError):
                operation()
        self.assertNotIn("nodes", record)
        self.assertNotIn("values", record)


if __name__ == "__main__":
    unittest.main()
