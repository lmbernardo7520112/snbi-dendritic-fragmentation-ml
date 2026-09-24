"""Group-level fixed models on invented in-memory fixtures only."""

from copy import deepcopy
import importlib.util
import inspect
import json
from pathlib import Path
import unittest
from unittest import mock

from snbi_fragmentation import study3_models as core
from snbi_fragmentation.study2c_models import RF_DEFAULTS
from snbi_fragmentation.study3_domain import TrajectoryGroup


NUMERIC_AVAILABLE = all(importlib.util.find_spec(name) is not None
                        for name in ("numpy", "sklearn", "skimage"))


def synthetic_groups(fold=1, prefix="synthetic"):
    groups = []
    for acquisition_index, acquisition in enumerate(core.FRAME_DENOMINATORS):
        for label in (0, 1):
            group_id = f"{prefix}-{acquisition_index}-{label}"
            groups.append(TrajectoryGroup.from_rows([
                {"sample_id": f"{group_id}-{frame}", "group_id": group_id,
                 "acquisition_id": acquisition, "frame_index": frame,
                 "label": label, "tier": "GOLD" if label else "BACKGROUND",
                 "cv_fold": fold, "split": "TRAIN"}
                for frame in range(1 + acquisition_index + label)
            ]))
    return groups


class Study3ModelStaticTests(unittest.TestCase):
    def test_reference_equals_all_historical_parameter_types(self):
        contract = core.method_contract()
        self.assertTrue(core.exact(contract["rf_parameters"], RF_DEFAULTS))
        self.assertEqual(contract["rf_parameter_count"], 19)
        self.assertIsNone(contract["rf_parameters"]["n_jobs"])
        self.assertEqual(contract["rf_parameters"]["random_state"], 42)
        self.assertEqual(set(contract["classical_representations"].values()), {20, 60})
        json.dumps(contract, allow_nan=False)

    def test_method_has_fixed_logreg_and_defensive_copy(self):
        contract = core.method_contract()
        self.assertEqual({k: contract["metadata_parameters"][k]
                          for k in ("C", "penalty", "solver", "max_iter")},
                         {"C": 1.0, "penalty": "l2", "solver": "lbfgs", "max_iter": 10000})
        contract["rf_parameters"]["random_state"] = 100
        self.assertEqual(core.method_contract()["rf_parameters"]["random_state"], 42)

    def test_no_implicit_fit_callback_or_validation_prediction_labels(self):
        for fn in (core.fit_reference, core.fit_metadata):
            self.assertIs(inspect.signature(fn).parameters["on_event"].default, inspect.Parameter.empty)
        self.assertEqual(list(inspect.signature(core.predict_reference).parameters), ["model", "X"])
        self.assertEqual(list(inspect.signature(core.predict_metadata).parameters), ["model", "X"])

    def test_acquisition_majority_tie_predicts_zero_without_fit(self):
        result = core.acquisition_only(synthetic_groups(), synthetic_groups(0, "valid"), fold=0)
        self.assertEqual(result["predictions"], [0, 0, 0, 0])
        self.assertEqual(result["fit_calls"], 0)
        self.assertTrue(result["diagnostic_only"])

    def test_acquisition_prediction_uses_train_groups_not_validation_labels(self):
        groups = synthetic_groups()
        extra = synthetic_groups(prefix="extra")
        groups += [g for g in extra if g.label == 1]
        result = core.acquisition_only(groups, synthetic_groups(0, "valid"), fold=0)
        self.assertEqual(result["predictions"], [1, 1, 1, 1])

    def test_acquisition_control_rejects_fold_crossing(self):
        with self.assertRaisesRegex(core.Study3ModelError, "validation groups"):
            core.acquisition_only(synthetic_groups(0), synthetic_groups(0, "valid"), fold=0)


class Study3ModelDocumentCoherenceTests(unittest.TestCase):
    """Versioned documentary contracts must describe the executable method."""

    @classmethod
    def setUpClass(cls):
        path = Path(__file__).absolute().parents[1] / "configs/study3/model-contract.json"
        cls.document = json.loads(path.read_text(encoding="utf-8"))
        cls.code = core.method_contract()

    def test_document_binds_all_nineteen_historical_rf_parameters_and_group_unit(self):
        self.assertEqual(self.document["rf_family"], "RF_REFERENCE")
        self.assertTrue(core.exact(self.document["rf_parameters"], RF_DEFAULTS))
        self.assertTrue(core.exact(self.document["rf_parameters"], self.code["rf_parameters"]))
        self.assertEqual(len(self.document["rf_parameters"]), 19)
        self.assertIs(self.document["one_vector_per_group"], True)
        self.assertEqual(self.code["training_unit"], "GROUP_TRAJECTORY")
        self.assertEqual(self.document["rf_training_weights"], "equal group contributions")
        self.assertIs(self.document["post_result_model_search"], False)
        self.assertIs(self.code["hyperparameter_search"], False)

    def test_document_binds_logistic_parameters_seed_and_train_only_scaler(self):
        document = self.document["COVERAGE_METADATA_LOGREG"]
        keys = {"C", "penalty", "solver", "max_iter", "random_state"}
        self.assertEqual(set(document["parameters"]), keys)
        self.assertTrue(core.exact(document["parameters"],
                                  {key: self.code["metadata_parameters"][key] for key in keys}))
        self.assertEqual(document["parameters"]["random_state"], self.code["seed"])
        self.assertEqual(document["scaler"], "StandardScaler fit on fold TRAIN groups only")
        self.assertEqual(self.code["scaler"], {"copy": True, "with_mean": True, "with_std": True})

    def test_document_binds_exact_four_metadata_features_and_acquisition_denominators(self):
        document = self.document["COVERAGE_METADATA_LOGREG"]
        normalized_names = ["log1p_n_rows" if name == "log1p(n_rows)" else name
                            for name in document["features"]]
        self.assertEqual(normalized_names, self.code["metadata_features"])
        self.assertEqual(len(normalized_names), 4)
        self.assertTrue(core.exact(document["frame_denominators"], self.code["metadata_frame_denominators"]))
        self.assertEqual(document["forbidden_features"],
                         ["acquisition_one_hot", "coordinates", "site_id", "track_id", "pixels", "LBP"])

    def test_document_binds_zero_fit_acquisition_majority_and_tie(self):
        document = self.document["ACQUISITION_ONLY"]
        self.assertEqual(document["fits"], self.code["acquisition_only_fit_calls"])
        self.assertEqual(document["tie_class"], self.code["acquisition_majority_tie_class"])
        self.assertEqual(document["rule"], "majority class per acquisition in fold TRAIN")
        self.assertIs(document["diagnostic_only"], True)


@unittest.skipUnless(NUMERIC_AVAILABLE, "scientific dependencies absent outside strict Study3 profile")
class Study3ModelAdmissionTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np, self.groups = np, synthetic_groups()
        self.X = np.zeros((4, 20), dtype=np.float64)

    def test_metadata_features_exactly_four_preregistered_values(self):
        X = core.coverage_metadata_features(self.groups)
        self.assertEqual(X.shape, (4, 4))
        self.np.testing.assert_array_equal(X[:, 0], self.np.log1p([1, 2, 2, 3]))
        self.np.testing.assert_array_equal(X[:, 1], [0, 0, 0, 0])
        self.np.testing.assert_array_equal(X[:, 2], [0, 1/293, 1/394, 2/394])
        self.np.testing.assert_array_equal(X[:, 3], X[:, 2])

    def test_callback_denial_precedes_rf_fit(self):
        from sklearn.ensemble import RandomForestClassifier
        with mock.patch.object(RandomForestClassifier, "fit") as fit:
            with self.assertRaisesRegex(RuntimeError, "budget denied"):
                core.fit_reference(self.X, self.groups, "D1_LBP20", fold=0,
                                   on_event=mock.Mock(side_effect=RuntimeError("budget denied")))
            fit.assert_not_called()

    def test_callback_denial_precedes_scaler_and_metadata_estimator(self):
        from sklearn.preprocessing import StandardScaler
        X = core.coverage_metadata_features(self.groups)
        with mock.patch.object(StandardScaler, "fit") as fit:
            with self.assertRaisesRegex(RuntimeError, "budget denied"):
                core.fit_metadata(X, self.groups, fold=0,
                                  on_event=mock.Mock(side_effect=RuntimeError("budget denied")))
            fit.assert_not_called()

    def test_invalid_features_or_representation_do_not_consume_fit(self):
        for X, representation in ((self.X[:, :19], "D1_LBP20"),
                                  (self.X.astype("uint8"), "D1_LBP20"),
                                  (self.np.full((4, 20), self.np.nan), "D1_LBP20"),
                                  (self.X, "RF_TUNED")):
            callback = mock.Mock()
            with self.assertRaises(core.Study3ModelError):
                core.fit_reference(X, self.groups, representation, fold=0, on_event=callback)
            callback.assert_not_called()

    def test_validation_groups_rejected_before_fit_callback(self):
        callback = mock.Mock()
        with self.assertRaisesRegex(core.Study3ModelError, "validation groups"):
            core.fit_reference(self.X, self.groups, "D1_LBP20", fold=1, on_event=callback)
        callback.assert_not_called()

    def test_missing_callback_fails_closed(self):
        with self.assertRaisesRegex(core.Study3ModelError, "mandatory"):
            core.fit_reference(self.X, self.groups, "D1_LBP20", fold=0, on_event=None)

    def test_metadata_cannot_replace_features_with_identifiers_or_pixels(self):
        X = core.coverage_metadata_features(self.groups)
        X[0, 0] += 1
        callback = mock.Mock()
        with self.assertRaisesRegex(core.Study3ModelError, "four fixed"):
            core.fit_metadata(X, self.groups, fold=0, on_event=callback)
        callback.assert_not_called()

    def test_fit_failure_has_one_start_no_retry_or_completion(self):
        from sklearn.ensemble import RandomForestClassifier
        events = []
        with mock.patch.object(RandomForestClassifier, "fit", side_effect=RuntimeError("synthetic failure")) as fit:
            with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
                core.fit_reference(self.X, self.groups, "D1_LBP20", fold=0, on_event=events.append)
            self.assertEqual(fit.call_count, 1)
        self.assertEqual([e["event"] for e in events], ["FIT_START"])


@unittest.skipUnless(NUMERIC_AVAILABLE, "scientific dependencies absent outside strict Study3 profile")
class ThreeActualSyntheticStudy3FitsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.groups, cls.events, cls.fits = synthetic_groups(), {}, {}
        cls.inputs = {"D1_LBP20": np.random.default_rng(81).normal(size=(4, 20)),
                      "TRAJECTORY_Q2575_LBP60": np.random.default_rng(82).normal(size=(4, 60))}
        for name, values in cls.inputs.items():
            cls.events[name] = []
            cls.fits[name] = core.fit_reference(values, cls.groups, name, fold=0,
                                                on_event=cls.events[name].append)
        cls.metadata_X = core.coverage_metadata_features(cls.groups)
        cls.metadata_events = []
        cls.metadata_model, cls.metadata_report = core.fit_metadata(
            cls.metadata_X, cls.groups, fold=0, on_event=cls.metadata_events.append)

    def test_two_rf_fits_preserve_parameters_dimensions_and_callback_counts(self):
        for name, (model, report) in self.fits.items():
            self.assertTrue(core.exact(model.get_params(deep=False), RF_DEFAULTS))
            self.assertEqual(len(model.estimators_), 100)
            self.assertEqual(report["input_feature_dimension"], self.inputs[name].shape[1])
            self.assertEqual(report["fit_calls"], 1)
            self.assertEqual([e["event"] for e in self.events[name]], ["FIT_START", "FIT_COMPLETE"])
            json.dumps(report, allow_nan=False)

    def test_rf_predictions_are_real_library_outputs_for_twenty_and_sixty_features(self):
        import numpy as np
        for name, (model, _) in self.fits.items():
            result = core.predict_reference(model, self.inputs[name])
            self.assertEqual(result["predictions"], model.predict(self.inputs[name]).tolist())
            np.testing.assert_array_equal(result["probabilities"], model.predict_proba(self.inputs[name]))

    def test_rf_parameter_mutation_prevents_prediction(self):
        model = deepcopy(self.fits["D1_LBP20"][0])
        model.set_params(random_state=43)
        with self.assertRaises(core.Study3ModelError):
            core.predict_reference(model, self.inputs["D1_LBP20"])

    def test_metadata_scaler_uses_training_only_and_validation_cannot_change_it(self):
        import numpy as np
        report = self.metadata_report
        np.testing.assert_array_equal(report["scaler"]["mean"], self.metadata_X.mean(axis=0))
        self.assertEqual(report["scaler"]["training_group_ids"], [str(g.group_id) for g in self.groups])
        original = deepcopy(report["scaler"])
        predicted = core.predict_metadata(self.metadata_model, np.full((2, 4), 1e5, dtype=float))
        self.assertEqual(report["scaler"], original)
        self.assertEqual(len(predicted["predictions"]), 2)
        self.assertEqual(len(original["sha256"]), 64)

    def test_metadata_one_pipeline_fit_reports_no_validation(self):
        self.assertEqual([e["event"] for e in self.metadata_events], ["FIT_START", "FIT_COMPLETE"])
        self.assertEqual(self.metadata_report["fit_calls"], 1)
        self.assertFalse(self.metadata_report["validation_used_for_training"])
        self.assertEqual(self.metadata_report["convergence"], "PASS")
        json.dumps(self.metadata_report, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
