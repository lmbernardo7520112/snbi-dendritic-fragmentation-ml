"""Synthetic-only Study2-C classical fits, weights and bounded CV contracts."""

from collections import Counter
from copy import deepcopy
import importlib.util
import inspect
import json
import unittest
from unittest import mock
import warnings

from snbi_fragmentation import study2c_models as core


NUMERIC_AVAILABLE = all(importlib.util.find_spec(name) is not None
                        for name in ("numpy", "sklearn", "skimage"))
ACQUISITIONS = ("bottom_up_anti_parallel", "top_down_parallel")


def synthetic_rows(*, folds=False):
    rows, allocation = [], {}
    for acquisition_index, acquisition in enumerate(ACQUISITIONS):
        for label in (0, 1):
            for fold in range(4 if folds else 1):
                group = f"synthetic-{acquisition_index}-{label}-{fold}"
                allocation[group] = fold
                count = 1 + fold % 2 if folds else 1 + acquisition_index * 2 + label
                for observation in range(count):
                    rows.append({"row_id": f"{group}-{observation}", "group_id": group,
                                 "acquisition_id": acquisition, "label": label, "split": "TRAIN",
                                 "tier": "GOLD" if label else "BACKGROUND"})
    return rows, allocation


def synthetic_weights(rows):
    counts = Counter(row["group_id"] for row in rows)
    return [1.0 / counts[row["group_id"]] for row in rows]


class FrozenModelContractTests(unittest.TestCase):
    def test_grid_budget_and_exact_tie_order(self):
        grids = core.model_grids()
        self.assertEqual({k: len(v) for k, v in grids.items()},
                         {"LOGISTIC_REGRESSION": 3, "SVM_RBF": 9, "RF_TUNED": 8})
        self.assertEqual(4 * sum(map(len, grids.values())), 80)
        self.assertEqual(grids["LOGISTIC_REGRESSION"][0], {"C": 0.1})
        self.assertEqual(grids["SVM_RBF"][:3], [
            {"C": 0.1, "gamma": "scale"}, {"C": 0.1, "gamma": 0.01}, {"C": 0.1, "gamma": 0.1}])
        self.assertEqual(grids["RF_TUNED"][0],
                         {"n_estimators": 100, "max_depth": 8, "min_samples_leaf": 3})

    def test_configuration_freezes_all_rf_defaults(self):
        config = core.classical_configuration("RF_REFERENCE", {})
        self.assertEqual(len(config), 19)
        self.assertEqual(config["n_estimators"], 100)
        self.assertEqual(config["random_state"], 42)
        self.assertIsNone(config["class_weight"])
        self.assertIsNone(config["n_jobs"])
        self.assertEqual(config["max_features"], "sqrt")
        config["n_estimators"] = 1
        self.assertEqual(core.classical_configuration("RF_REFERENCE", {})["n_estimators"], 100)

    def test_off_grid_changes_and_type_coercion_denied(self):
        for family, params in [
            ("RF_REFERENCE", {"n_estimators": 100}), ("LOGISTIC_REGRESSION", {"C": 1}),
            ("LOGISTIC_REGRESSION", {"C": 0.1, "max_iter": 5}),
            ("SVM_RBF", {"C": 1.0, "gamma": "auto"}),
            ("RF_TUNED", {"n_estimators": 100, "max_depth": 8, "min_samples_leaf": True}),
        ]:
            with self.subTest(family=family, params=params), self.assertRaises(core.ModelContractError):
                core.classical_configuration(family, params)

    def test_method_contract_is_json_ready_and_defensively_copied(self):
        contract = core.method_contract()
        json.dumps(contract, allow_nan=False)
        self.assertEqual(contract["cv_fits_total"], 80)
        self.assertEqual(contract["cnn"]["parameter_count"], 5010)
        self.assertEqual(contract["cnn"]["epochs"], 20)
        contract["cnn"]["betas"][0] = 0
        contract["features"]["channels"][0] = "BAD"
        self.assertEqual(core.method_contract()["cnn"]["betas"], [0.9, 0.999])
        self.assertEqual(core.FEATURE_CONTRACT["channels"][0], "STRUCTURAL_Y")

    def test_prediction_interface_has_no_labels(self):
        self.assertEqual(list(inspect.signature(core.predict_classical).parameters), ["model", "X"])


@unittest.skipUnless(NUMERIC_AVAILABLE, "optional pinned classical libraries unavailable")
class NumericModelContractTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np
        self.rows, _ = synthetic_rows()
        self.weights = synthetic_weights(self.rows)

    def test_weight_sum_is_one_per_group_despite_unequal_observation_counts(self):
        weights, metadata = core.validate_training_rows(self.rows, self.weights)
        self.assertEqual(metadata["training_rows"], 10)
        self.assertEqual(metadata["training_group_count"], 4)
        self.assertEqual(metadata["weight_sum_by_class"], {"0": 2.0, "1": 2.0})
        self.assertEqual(len(set(weights.tolist())), 4)

    def test_globally_rescaled_weights_denied(self):
        with self.assertRaisesRegex(core.ModelContractError, "not globally rescaled"):
            core.validate_training_rows(self.rows, [2 * w for w in self.weights])

    def test_test_and_unknown_splits_denied(self):
        for split in ("TEST", "DEV", None):
            rows = deepcopy(self.rows)
            rows[0]["split"] = split
            with self.subTest(split=split), self.assertRaises(core.ModelContractError):
                core.validate_training_rows(rows, self.weights)

    def test_final_training_may_include_separate_development_groups(self):
        rows = deepcopy(self.rows)
        rows[0]["split"] = "DEVELOPMENT"
        _, metadata = core.validate_training_rows(rows, self.weights)
        self.assertEqual(metadata["training_splits"], ["DEVELOPMENT", "TRAIN"])
        with self.assertRaises(core.ModelContractError):
            core.validate_training_rows(rows, self.weights, train_only=True)

    def test_silver_positive_shares_group_total_weight(self):
        rows = deepcopy(self.rows)
        rows[-1]["tier"] = "SILVER"
        _, metadata = core.validate_training_rows(rows, self.weights)
        self.assertEqual(metadata["weight_sum_by_class"], {"0": 2.0, "1": 2.0})
        self.assertEqual(metadata["training_tier_counts"]["SILVER"], 1)

    def test_unlabeled_and_negative_silver_are_not_training_targets(self):
        for index, tier in ((0, "SILVER"), (-1, "UNLABELED_PRE_FIRST"), (-1, "PERSISTENCE_EXPECTED")):
            rows = deepcopy(self.rows)
            rows[index]["tier"] = tier
            with self.subTest(tier=tier), self.assertRaises(core.ModelContractError):
                core.validate_training_rows(rows, self.weights)

    def test_group_cannot_cross_class_acquisition_or_split(self):
        for key, value in (("label", 0), ("acquisition_id", ACQUISITIONS[0]), ("split", "DEVELOPMENT")):
            rows = deepcopy(self.rows)
            rows[-1][key] = value
            if key == "label":
                rows[-1]["tier"] = "BACKGROUND"
            with self.subTest(key=key), self.assertRaisesRegex(core.ModelContractError, "group crosses"):
                core.validate_training_rows(rows, self.weights)

    def test_nonfinite_negative_or_misaligned_weights_denied(self):
        for weights in ([float("nan")] * 10, [0.0] * 10, [-1.0] * 10, self.weights[:-1]):
            with self.subTest(weights=weights[:1]), self.assertRaises(core.ModelContractError):
                core.validate_training_rows(self.rows, weights)

    def test_lbp20_preserves_channel_order_and_exact_histogram(self):
        np = self.np
        from skimage.feature import local_binary_pattern
        pairs = np.zeros((2, 2, 65, 65), dtype=np.uint8)
        pairs[0, 1] = np.arange(65 * 65, dtype=np.uint16).reshape(65, 65).astype(np.uint8)
        pairs[1] = pairs[0, ::-1]
        features = core.extract_lbp20(pairs)
        self.assertEqual(features.shape, (2, 20))
        self.assertEqual(features.dtype, np.dtype("float64"))
        constant = np.zeros(10); constant[8] = 1
        np.testing.assert_array_equal(features[0, :10], constant)
        expected, _ = np.histogram(local_binary_pattern(pairs[0, 1], P=8, R=1, method="uniform"),
                                   bins=10, range=(0, 10), density=True)
        np.testing.assert_array_equal(features[0, 10:], expected)
        np.testing.assert_array_equal(features[0, :10], features[1, 10:])
        np.testing.assert_array_equal(features[0, 10:], features[1, :10])

    def test_noncanonical_patch_shapes_or_normalized_inputs_denied(self):
        np = self.np
        for pairs in (np.zeros((1, 2, 65, 65), dtype=np.float32),
                      np.zeros((1, 65, 65, 2), dtype=np.uint8),
                      np.zeros((0, 2, 65, 65), dtype=np.uint8)):
            with self.assertRaises(core.ModelContractError):
                core.extract_lbp20(pairs)

    def test_noncanonical_features_denied_before_fit(self):
        np = self.np
        for X in (np.zeros((10, 21)), np.zeros((10, 20), dtype=np.uint8),
                  np.full((10, 20), np.nan), np.zeros((9, 20))):
            with self.assertRaises(core.ModelContractError):
                core.fit_classical("RF_REFERENCE", {}, X, self.rows, self.weights)

    def test_convergence_warning_is_terminal_without_retry(self):
        from sklearn.exceptions import ConvergenceWarning
        def nonconvergent(*args, **kwargs):
            warnings.warn("synthetic convergence refusal", ConvergenceWarning)
        with mock.patch("sklearn.pipeline.Pipeline.fit", side_effect=nonconvergent) as fit:
            with self.assertRaisesRegex(core.ModelContractError, "BLOCKED_NONCONVERGENCE"):
                core.fit_classical("LOGISTIC_REGRESSION", {"C": 0.1}, self.np.zeros((10, 20)),
                                   self.rows, self.weights)
        self.assertEqual(fit.call_count, 1)  # mocked refusal, no actual optimizer/fit


@unittest.skipUnless(NUMERIC_AVAILABLE, "optional pinned classical libraries unavailable")
class FourSyntheticClassicalFitsTests(unittest.TestCase):
    """Exactly four actual fits shared across tests; all values are synthetic."""

    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.rows, _ = synthetic_rows()
        cls.weights = synthetic_weights(cls.rows)
        rng = np.random.default_rng(731)
        cls.X = rng.normal(size=(len(cls.rows), 20)) * 0.15
        cls.X += np.asarray([row["label"] for row in cls.rows])[:, None] * 2
        cls.results = {}
        for family in core.CLASSICAL_FAMILIES:
            params = {} if family == "RF_REFERENCE" else core.model_grids()[family][0]
            cls.results[family] = core.fit_classical(family, params, cls.X, cls.rows, cls.weights)

    def test_each_family_completes_one_frozen_fit_with_json_metadata(self):
        for family, (_, metadata) in self.results.items():
            with self.subTest(family=family):
                self.assertEqual(metadata["fit_calls"], 1)
                self.assertEqual(metadata["convergence"], "PASS")
                self.assertGreaterEqual(metadata["runtime_seconds"], 0)
                self.assertEqual(metadata["weight_sum_by_class"], {"0": 2.0, "1": 2.0})
                json.dumps(metadata, allow_nan=False)

    def test_scaler_fits_only_supplied_rows_with_group_weights(self):
        import numpy as np
        expected_mean = np.average(self.X, axis=0, weights=self.weights)
        self.assertFalse(np.allclose(expected_mean, self.X.mean(axis=0)))
        for family in ("LOGISTIC_REGRESSION", "SVM_RBF"):
            scaler = self.results[family][0].named_steps["scaler"]
            np.testing.assert_allclose(scaler.mean_, expected_mean)
            self.assertAlmostEqual(float(scaler.n_samples_seen_), 4.0)

    def test_svm_retains_signed_scores_without_probability_calibration(self):
        prediction = core.predict_classical(self.results["SVM_RBF"][0], self.X)
        self.assertIsNone(prediction["probabilities"])
        self.assertEqual(len(prediction["decision_scores"]), len(self.rows))
        self.assertEqual(prediction["predictions"], [row["label"] for row in self.rows])
        self.assertIn("NOT_PROBABILITY", prediction["score_semantics"])
        self.assertFalse(self.results["SVM_RBF"][1]["probability_calibration"])

    def test_other_classical_families_return_actual_two_class_probabilities(self):
        for family in ("LOGISTIC_REGRESSION", "RF_REFERENCE", "RF_TUNED"):
            prediction = core.predict_classical(self.results[family][0], self.X)
            self.assertIsNone(prediction["decision_scores"])
            self.assertEqual(len(prediction["probabilities"]), len(self.rows))
            self.assertTrue(all(len(p) == 2 for p in prediction["probabilities"]))
            json.dumps(prediction, allow_nan=False)


@unittest.skipUnless(NUMERIC_AVAILABLE, "optional pinned classical libraries unavailable")
class GroupCVRoutingTests(unittest.TestCase):
    """CV control-flow uses mock estimators; these tests perform zero ML fits."""

    def setUp(self):
        import numpy as np
        self.rows, self.allocation = synthetic_rows(folds=True)
        self.X = np.zeros((len(self.rows), 20), dtype=np.float64)
        self.X[:, 0] = np.arange(len(self.rows))

    def test_all_eighty_cv_calls_keep_whole_groups_and_recompute_weights(self):
        def fit(family, params, X, rows, weights):
            self.assertEqual(weights, synthetic_weights(rows))
            self.assertTrue(all(r["split"] == "TRAIN" for r in rows))
            self.assertEqual(len({self.allocation[r["group_id"]] for r in rows}), 3)
            return rows, {"fit_calls": 1, "training_groups": sorted({r["group_id"] for r in rows})}
        def predict(training_rows, X):
            validation_rows = [self.rows[int(index)] for index in X[:, 0]]
            self.assertFalse({r["group_id"] for r in training_rows} & {r["group_id"] for r in validation_rows})
            return {"predictions": [r["label"] for r in validation_rows]}
        with mock.patch.object(core, "fit_classical", side_effect=fit) as fitter, \
                mock.patch.object(core, "predict_classical", side_effect=predict):
            total = 0
            for family, options in core.model_grids().items():
                events = []
                selected, report = core.cv_search(family, self.X, self.rows, self.allocation, events.append)
                self.assertEqual(selected, options[0])  # exact ties use declared first candidate
                self.assertEqual(report["selected_overrides"], options[0])
                self.assertEqual(report["fit_calls"], 4 * len(options))
                self.assertEqual(len(report["candidates"]), len(options))
                self.assertEqual(len(events), 3 * report["fit_calls"])
                self.assertEqual([e["event"] for e in events[:3]],
                                 ["CV_FIT_START", "CV_FIT_COMPLETE", "CV_FOLD_COMPLETE"])
                self.assertFalse(report["refit_performed"])
                self.assertFalse(report["dev_or_test_used"])
                total += report["fit_calls"]
            self.assertEqual(total, 80)
            self.assertEqual(fitter.call_count, 80)

    def test_development_or_silver_denied_before_cv_fit(self):
        for key, value in (("split", "DEVELOPMENT"), ("tier", "SILVER")):
            rows = deepcopy(self.rows)
            for row in rows:
                if row["label"] == 1:
                    row[key] = value
            with mock.patch.object(core, "fit_classical") as fitter:
                with self.assertRaises(core.ModelContractError):
                    core.cv_search("LOGISTIC_REGRESSION", self.X, rows, self.allocation)
                fitter.assert_not_called()

    def test_incomplete_or_noninteger_fold_map_denied(self):
        for changed in (dict(list(self.allocation.items())[1:]),
                        dict(self.allocation, **{next(iter(self.allocation)): True})):
            with mock.patch.object(core, "fit_classical") as fitter:
                with self.assertRaises(core.ModelContractError):
                    core.cv_search("LOGISTIC_REGRESSION", self.X, self.rows, changed)
                fitter.assert_not_called()

    def test_feasible_acquisition_class_stratum_cannot_be_omitted(self):
        changed = dict(self.allocation)
        target = [r for r in self.rows if r["acquisition_id"] == ACQUISITIONS[0] and r["label"] == 1]
        for row in target:
            changed[row["group_id"]] = 0
        with mock.patch.object(core, "fit_classical") as fitter:
            with self.assertRaisesRegex(core.ModelContractError, "stratum"):
                core.cv_search("LOGISTIC_REGRESSION", self.X, self.rows, changed)
            fitter.assert_not_called()


if __name__ == "__main__":
    unittest.main()
