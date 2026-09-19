"""Synthetic-only checks of fixed TI3 patch extraction, LBP and RF reporting."""

import copy
import importlib.util
import json
import unittest
from unittest import mock

from snbi_fragmentation import ti3_baseline as baseline


NUMERICAL = all(importlib.util.find_spec(name) is not None
                for name in ("numpy", "scipy", "skimage", "sklearn"))


def sample(**changes):
    metadata = {
        "split": "TRAIN", "source_id": "ESM1", "width": 1278, "height": 1018,
        "center_x": 200, "center_y": 300,
        "patch_radius_px": 32, "patch_side_px": 65,
    }
    return {**metadata, **changes}


class ArrayTrap:
    def __array__(self, *args, **kwargs):
        raise AssertionError("prohibited input was accessed")

    def __getitem__(self, key):
        raise AssertionError("prohibited input was indexed")


class PatchPreImportGuardTests(unittest.TestCase):
    def assert_denied_without_runtime(self, metadata):
        with mock.patch.object(baseline, "_scientific_runtime") as runtime:
            with self.assertRaises(baseline.BaselineContractError):
                baseline.extract_patch(ArrayTrap(), metadata)
            runtime.assert_not_called()

    def test_final_test_and_unknown_splits_deny_before_runtime_and_array(self):
        for split in ("FINAL_TEST", "FINAL", "SEALED", "TRAINING", None, True):
            with self.subTest(split=split):
                self.assert_denied_without_runtime(sample(split=split))

    def test_annotation_solutal_and_unknown_sources_deny_before_array(self):
        for source in ("ESM2", "ESM3", "ESM5", "ESM6", "UNKNOWN", None, []):
            with self.subTest(source=source):
                self.assert_denied_without_runtime(sample(source_id=source))

    def test_explicit_native_integer_metadata_is_required(self):
        valid = sample()
        for key in ("width", "height", "center_x", "center_y", "patch_radius_px", "patch_side_px"):
            for value in (None, True, float(valid[key])):
                with self.subTest(key=key, value=value):
                    self.assert_denied_without_runtime(sample(**{key: value}))
        for metadata in (None, {}, sample(width=1280), sample(height=1024),
                         sample(patch_radius_px=31), sample(patch_side_px=64)):
            with self.subTest(metadata=metadata):
                self.assert_denied_without_runtime(metadata)

    def test_outside_centres_are_not_moved_or_padded(self):
        for changes in ({"center_x": 31}, {"center_y": 31},
                        {"center_x": 1246}, {"center_y": 986},
                        {"center_x": -1}, {"center_y": -100}):
            with self.subTest(changes=changes):
                self.assert_denied_without_runtime(sample(**changes))


@unittest.skipUnless(NUMERICAL, "optional pinned NumPy/SciPy/scikit-image/scikit-learn unavailable")
class BaselineSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.np = np

    def test_native_uint8_patch_copies_exact_coordinates_without_mutation(self):
        np = self.np
        image = (np.arange(1018 * 1278, dtype=np.uint32) % 251).reshape(1018, 1278).astype(np.uint8)
        metadata = sample()
        before = copy.deepcopy(metadata)
        patch = baseline.extract_patch(image, metadata)
        np.testing.assert_array_equal(patch, image[268:333, 168:233])
        self.assertEqual(patch.shape, (65, 65))
        self.assertEqual(patch.dtype, np.dtype("uint8"))
        self.assertFalse(np.shares_memory(patch, image))
        self.assertEqual(metadata, before)

    def test_exact_canvas_edges_and_both_structural_dimensions(self):
        np = self.np
        for source, height in (("ESM1", 1018), ("ESM4", 1012)):
            image = np.full((height, 1278), 17, dtype=np.uint8)
            for x, y in ((32, 32), (1245, height - 33)):
                with self.subTest(source=source, centre=(x, y)):
                    patch = baseline.extract_patch(image, sample(
                        split="DEVELOPMENT", source_id=source, height=height, center_x=x, center_y=y))
                    np.testing.assert_array_equal(patch, np.full((65, 65), 17, dtype=np.uint8))

    def test_luminance_dtype_shape_and_nonarray_inputs_are_not_coerced(self):
        np = self.np
        for image in (np.zeros((1018, 1278), dtype=float),
                      np.zeros((1017, 1278), dtype=np.uint8),
                      np.zeros((1018, 1278, 1), dtype=np.uint8), ArrayTrap()):
            with self.subTest(shape=getattr(image, "shape", None)):
                with self.assertRaises(baseline.BaselineContractError):
                    baseline.extract_patch(image, sample())

    def test_dependency_version_mismatch_denies_processing(self):
        import skimage
        with mock.patch.object(skimage, "__version__", "0.0.invalid"):
            with self.assertRaises(baseline.BaselineContractError):
                baseline.lbp_features(ArrayTrap())

    def test_lbp_is_exact_library_histogram_and_deterministic_ten_features(self):
        np = self.np
        from skimage.feature import local_binary_pattern
        row, column = np.indices((65, 65))
        patch = ((row * 17 + column * 3) % 256).astype(np.uint8)
        before = patch.copy()
        actual = baseline.lbp_features(patch)
        expected, _ = np.histogram(local_binary_pattern(patch, P=8, R=1, method="uniform"),
                                   bins=10, range=(0, 10), density=True)
        np.testing.assert_array_equal(actual, expected)
        np.testing.assert_array_equal(actual, baseline.lbp_features(patch))
        np.testing.assert_array_equal(patch, before)
        self.assertEqual(actual.shape, (10,))
        self.assertAlmostEqual(float(actual.sum()), 1.0)

    def test_lbp_refuses_resizing_float_or_multichannel_conversion(self):
        np = self.np
        for patch in (np.zeros((64, 65), dtype=np.uint8), np.zeros((65, 65), dtype=float),
                      np.zeros((65, 65, 3), dtype=np.uint8), ArrayTrap()):
            with self.subTest(shape=getattr(patch, "shape", None)):
                with self.assertRaises(baseline.BaselineContractError):
                    baseline.lbp_features(patch)

    def test_confusion_metrics_use_weak_positive_one_and_explicit_order(self):
        np = self.np
        result = baseline._classification_metrics(
            np.array([0, 0, 0, 0, 1, 1]), np.array([0, 0, 0, 1, 0, 1]))
        self.assertEqual(result["confusion_matrix"], [[3, 1], [1, 1]])
        self.assertEqual((result["TN"], result["FP"], result["FN"], result["TP"]), (3, 1, 1, 1))
        self.assertEqual(result["balanced_accuracy"], 0.625)
        self.assertAlmostEqual(result["accuracy"], 4 / 6)
        for metric in ("precision", "recall", "f1"):
            self.assertEqual(result[metric], 0.5)
        absent_prediction = baseline._classification_metrics(np.array([0, 1]), np.array([0, 0]))
        for metric in ("precision", "recall", "f1"):
            self.assertEqual(absent_prediction[metric], 0.0)

    def test_bad_feature_and_label_contracts_fail_before_any_fit(self):
        np = self.np
        features = np.full((4, 10), 0.1)
        labels = np.array([0, 1, 0, 1])
        invalid_features = [features[:, :9], features[:0], features.astype(bool),
                            np.full((4, 10), np.nan), features * 2,
                            np.full((4, 10), -0.1)]
        invalid_labels = [labels[:3], labels.astype(bool), labels.astype(float),
                          np.zeros(4, dtype=int), np.array([0, 2, 0, 2])]
        with mock.patch("sklearn.ensemble.RandomForestClassifier") as constructor:
            for invalid in invalid_features:
                with self.subTest(feature_shape=invalid.shape), self.assertRaises(baseline.BaselineContractError):
                    baseline.evaluate_baseline(invalid, labels, features, labels)
            for invalid in invalid_labels:
                with self.subTest(label_shape=invalid.shape), self.assertRaises(baseline.BaselineContractError):
                    baseline.evaluate_baseline(features, labels, features, invalid)
            constructor.assert_not_called()

    def test_one_synthetic_fit_records_frozen_defaults_and_train_dev_only(self):
        np = self.np
        from sklearn.ensemble import RandomForestClassifier
        labels = np.array([0, 1] * 8)
        features = np.zeros((16, 10), dtype=float)
        features[np.arange(16), labels] = 1.0
        estimator = RandomForestClassifier(n_estimators=100, random_state=42)
        with mock.patch("sklearn.ensemble.RandomForestClassifier", return_value=estimator) as constructor:
            with mock.patch.object(estimator, "fit", wraps=estimator.fit) as fit:
                result = baseline.evaluate_baseline(features, labels, features[:4].copy(), labels[:4].copy())
                constructor.assert_called_once_with(n_estimators=100, random_state=42)
                fit.assert_called_once()
        self.assertEqual(result["parameters"], baseline.RF_PARAMETERS)
        self.assertIsNone(result["parameters"]["class_weight"])
        self.assertEqual(result["fit_calls"], 1)
        self.assertEqual(result["model_selection_runs"], 0)
        self.assertFalse(result["final_test_evaluated"])
        self.assertEqual(set(result["evaluations"]), {"TRAIN", "DEVELOPMENT"})
        self.assertEqual(result["claim"], "CONCORDANCE_WITH_PUBLISHED_LOCATION_WEAK_LABELS")
        for split, expected_n in (("TRAIN", 16), ("DEVELOPMENT", 4)):
            item = result["evaluations"][split]
            self.assertEqual(item["sample_count"], expected_n)
            self.assertEqual(sum(item[key] for key in ("TN", "FP", "FN", "TP")), expected_n)
            self.assertEqual(len(item["predicted_labels"]), expected_n)
            self.assertEqual(len(item["probabilities_class_order_0_1"]), expected_n)
        json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
