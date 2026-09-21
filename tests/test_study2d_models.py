"""Fixed RF wrapper: exactly two tiny actual synthetic fits; no source I/O."""

from copy import deepcopy
import importlib.util
import inspect
import json
import unittest
from unittest import mock

from snbi_fragmentation import study2c_models as historical
from snbi_fragmentation import study2d_models as core


NUMERIC_AVAILABLE = all(importlib.util.find_spec(n) is not None for n in ("numpy", "sklearn", "skimage"))


def synthetic_rows():
    rows = []
    for acquisition_index, acquisition in enumerate(("bottom_up_anti_parallel", "top_down_parallel")):
        for label in (0, 1):
            group = f"synthetic-{acquisition_index}-{label}"
            for frame in range(1 + 2 * acquisition_index + label):
                rows.append({"sample_id": f"{group}-{frame}", "group_id": group,
                             "acquisition_id": acquisition, "frame_index": frame,
                             "label": label, "tier": "GOLD" if label else "BACKGROUND", "split": "TRAIN"})
    return rows


class FrozenReferenceContractTests(unittest.TestCase):
    def test_all_nineteen_historical_parameters_and_types_are_identical(self):
        contract = core.method_contract()
        self.assertEqual(contract["rf_parameter_count"], 19)
        self.assertTrue(core.exact(contract["rf_parameters"], historical.RF_DEFAULTS))
        self.assertIsNone(contract["rf_parameters"]["class_weight"])
        self.assertIsNone(contract["rf_parameters"]["n_jobs"])
        self.assertEqual(contract["rf_parameters"]["n_estimators"], 100)
        self.assertEqual(contract["rf_parameters"]["random_state"], 42)

    def test_boolean_integer_coercion_and_parameter_changes_fail_closed(self):
        for key, value in (("min_samples_leaf", True), ("n_estimators", 300), ("random_state", 43)):
            changed = dict(core.RF_PARAMETERS, **{key: value})
            with mock.patch.object(core, "RF_PARAMETERS", changed), self.assertRaises(core.ReferenceModelError):
                core.method_contract()

    def test_contract_is_json_safe_defensively_copied_and_has_no_search(self):
        contract = core.method_contract(); json.dumps(contract, allow_nan=False)
        self.assertFalse(contract["hyperparameter_search"]); self.assertFalse(contract["threshold_search"])
        contract["rf_parameters"]["n_estimators"] = 1
        contract["feature_contract"]["channels"][0] = "changed"
        self.assertEqual(core.method_contract()["rf_parameters"]["n_estimators"], 100)
        self.assertEqual(core.method_contract()["feature_contract"], historical.FEATURE_CONTRACT)

    def test_group_weighting_preserves_unit_group_weight_and_equal_class_totals(self):
        weights, metadata = core.training_weights(synthetic_rows(), "GROUP_EQUAL")
        self.assertEqual(len(weights), 10)
        self.assertEqual(metadata["weight_sum_by_group"], {f"synthetic-{a}-{y}": 1.0 for a in (0, 1) for y in (0, 1)})
        self.assertEqual(metadata["weight_sum_by_class"], {"0": 2.0, "1": 2.0})
        self.assertEqual(metadata["effective_rows_per_group"]["synthetic-1-1"], 4)

    def test_observation_equal_all_ones_changes_aggregate_class_weight(self):
        weights, metadata = core.training_weights(synthetic_rows(), "OBSERVATION_EQUAL")
        self.assertEqual(weights, [1.0] * 10)
        self.assertEqual(metadata["weight_sum_by_class"], {"0": 4.0, "1": 6.0})
        self.assertEqual(metadata["weight_sum_by_group"]["synthetic-1-1"], 4.0)

    def test_dev_test_silver_unknown_tier_and_nonexact_labels_denied(self):
        mutations = [{"split": "DEVELOPMENT"}, {"split": "TEST"}, {"split": "DEV"},
                     {"tier": "SILVER", "label": 1}, {"tier": "UNLABELED_PRE_FIRST"}, {"label": False}]
        for mutation in mutations:
            rows = synthetic_rows(); rows[0].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(core.ReferenceModelError):
                core.training_weights(rows, "GROUP_EQUAL")

    def test_duplicate_ids_empty_ids_and_group_crossing_refused(self):
        for mutation in ({"sample_id": ""}, {"sample_id": "synthetic-0-1-0"},
                         {"group_id": "synthetic-0-1"}, {"acquisition_id": "unknown"}):
            rows = synthetic_rows(); rows[0].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(core.ReferenceModelError):
                core.training_weights(rows, "GROUP_EQUAL")
        rows = synthetic_rows(); rows[-1]["acquisition_id"] = "bottom_up_anti_parallel"
        with self.assertRaisesRegex(core.ReferenceModelError, "crosses"):
            core.training_weights(rows, "GROUP_EQUAL")

    def test_one_class_and_unknown_weighting_denied(self):
        with self.assertRaises(core.ReferenceModelError):
            core.training_weights([r for r in synthetic_rows() if r["label"]], "GROUP_EQUAL")
        with self.assertRaises(core.ReferenceModelError):
            core.training_weights(synthetic_rows(), "BALANCED")

    def test_prediction_has_no_labels_and_lbp_is_exact_historical_function(self):
        self.assertEqual(list(inspect.signature(core.predict_reference).parameters), ["model", "X"])
        self.assertIs(core.extract_lbp20, historical.extract_lbp20)
        source = inspect.getsource(core)
        for forbidden in ("fit_classical(", "cv_search(", "import torch", "subprocess", "open(", "read_bytes("):
            self.assertNotIn(forbidden, source)


@unittest.skipUnless(NUMERIC_AVAILABLE, "optional pinned numeric libraries unavailable")
class ReferenceRefusalTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np; self.rows = synthetic_rows(); self.X = np.zeros((10, 20))

    def test_noncanonical_features_denied_before_fit_and_events(self):
        for X in (self.np.zeros((10, 19)), self.np.zeros((9, 20)), self.np.zeros((10, 20), dtype="uint8"),
                  self.np.full((10, 20), self.np.nan)):
            callback = mock.Mock()
            with self.assertRaises(core.ReferenceModelError):
                core.fit_reference(X, self.rows, "GROUP_EQUAL", callback)
            callback.assert_not_called()

    def test_row_denial_precedes_library_fit(self):
        from sklearn.ensemble import RandomForestClassifier
        self.rows[0]["split"] = "TEST"
        with mock.patch.object(RandomForestClassifier, "fit") as fit:
            with self.assertRaises(core.ReferenceModelError):
                core.fit_reference(self.X, self.rows, "GROUP_EQUAL")
            fit.assert_not_called()

    def test_start_callback_denial_prevents_actual_fit(self):
        from sklearn.ensemble import RandomForestClassifier
        with mock.patch.object(RandomForestClassifier, "fit") as fit:
            with self.assertRaisesRegex(RuntimeError, "synthetic stop"):
                core.fit_reference(self.X, self.rows, "GROUP_EQUAL", mock.Mock(side_effect=RuntimeError("synthetic stop")))
            fit.assert_not_called()

    def test_failed_fit_reports_started_only_without_retry(self):
        from sklearn.ensemble import RandomForestClassifier
        events = []
        with mock.patch.object(RandomForestClassifier, "fit", side_effect=RuntimeError("mock fit failure")) as fit:
            with self.assertRaisesRegex(RuntimeError, "mock fit failure"):
                core.fit_reference(self.X, self.rows, "GROUP_EQUAL", events.append)
            self.assertEqual(fit.call_count, 1)
        self.assertEqual([e["event"] for e in events], ["RF_FIT_START"])

    def test_exact_estimator_parameter_divergence_prevents_fit(self):
        from sklearn.ensemble import RandomForestClassifier
        changed = dict(core.RF_PARAMETERS, n_estimators=99)
        with mock.patch.object(RandomForestClassifier, "get_params", return_value=changed), \
                mock.patch.object(RandomForestClassifier, "fit") as fit:
            with self.assertRaises(core.ReferenceModelError):
                core.fit_reference(self.X, self.rows, "GROUP_EQUAL")
            fit.assert_not_called()

    def test_constant_synthetic_lbp_features_preserve_channel_histograms(self):
        features = core.extract_lbp20(self.np.zeros((1, 2, 65, 65), dtype="uint8"))
        expected = self.np.zeros((1, 20)); expected[0, 8] = 1; expected[0, 18] = 1
        self.np.testing.assert_array_equal(features, expected)


@unittest.skipUnless(NUMERIC_AVAILABLE, "optional pinned numeric libraries unavailable")
class TwoSyntheticReferenceFitsTests(unittest.TestCase):
    """Two actual 100-tree fits total, reused by all tests in this class."""

    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.rows = synthetic_rows()
        cls.X = np.random.default_rng(101).normal(size=(10, 20)) * .1
        cls.X += np.asarray([r["label"] for r in cls.rows])[:, None]
        cls.results, cls.events = {}, {}
        for weighting in ("GROUP_EQUAL", "OBSERVATION_EQUAL"):
            cls.events[weighting] = []
            cls.results[weighting] = core.fit_reference(cls.X, cls.rows, weighting, cls.events[weighting].append)

    def test_two_completed_fits_exact_parameters_and_runtime_metadata(self):
        self.assertEqual(sum(meta["fit_calls"] for _, meta in self.results.values()), 2)
        for weighting, (model, meta) in self.results.items():
            self.assertTrue(core.exact(model.get_params(deep=False), core.RF_PARAMETERS))
            self.assertEqual(len(model.estimators_), 100)
            self.assertGreaterEqual(meta["runtime_seconds"], 0)
            self.assertEqual(meta["convergence"], "PASS")
            self.assertEqual(meta["training_splits"], ["TRAIN"])
            self.assertEqual(meta["weighting"], weighting)
            json.dumps(meta, allow_nan=False)

    def test_callbacks_record_only_actual_started_and_returned_fits(self):
        for events in self.events.values():
            self.assertEqual([e["event"] for e in events], ["RF_FIT_START", "RF_FIT_COMPLETE"])
            self.assertEqual(events[0]["training_rows"], 10)
            self.assertGreaterEqual(events[1]["runtime_seconds"], 0)

    def test_predictions_are_actual_library_probabilities_without_label_input(self):
        import numpy as np
        for model, _ in self.results.values():
            result = core.predict_reference(model, self.X)
            self.assertEqual(result["predictions"], model.predict(self.X).tolist())
            np.testing.assert_array_equal(result["probabilities"], model.predict_proba(self.X))
            self.assertEqual(result["classes"], [0, 1])
            self.assertIsNone(result["decision_scores"])
            json.dumps(result, allow_nan=False)

    def test_prediction_rejects_model_parameter_mutation(self):
        model = deepcopy(self.results["GROUP_EQUAL"][0]); model.set_params(random_state=43)
        with self.assertRaises(core.ReferenceModelError):
            core.predict_reference(model, self.X)

    def test_both_weightings_use_same_features_rows_and_differ_only_in_weights(self):
        grouped = self.results["GROUP_EQUAL"][1]; observed = self.results["OBSERVATION_EQUAL"][1]
        self.assertEqual(grouped["effective_rows_per_group"], observed["effective_rows_per_group"])
        self.assertEqual(grouped["training_groups"], observed["training_groups"])
        self.assertEqual(grouped["estimator_parameters"], observed["estimator_parameters"])
        self.assertEqual(grouped["weight_sum_by_class"], {"0": 2.0, "1": 2.0})
        self.assertEqual(observed["weight_sum_by_class"], {"0": 4.0, "1": 6.0})


if __name__ == "__main__":
    unittest.main()
