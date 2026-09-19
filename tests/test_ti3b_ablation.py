"""Synthetic TI3-B admission, paired native geometry, features and one RF fit."""

import copy
import importlib.util
import json
import math
import unittest
from unittest import mock

from snbi_fragmentation import ti3_baseline as baseline
from snbi_fragmentation import ti3b_ablation as ablation


NUMERICAL = all(importlib.util.find_spec(name) is not None
                for name in ("numpy", "scipy", "skimage", "sklearn"))


def image_metadata(source="ESM2", frame=73, split="TRAIN"):
    width, height = (1278, 1018) if source == "ESM2" else (1278, 1012)
    return {
        "source_id": source, "frame_index": frame, "split": split,
        "width": width, "height": height, "pixel_format": "yuv420p", "bit_depth": 8,
        "frame_bytes": width * height * 3 // 2,
        "acquisition_id": "bottom_up_anti_parallel" if source == "ESM2" else "top_down_parallel",
    }


def structural_sample(image, x=200, y=300, sample_id="synthetic-pair"):
    return {
        key: image[key] for key in ("frame_index", "split", "width", "height", "acquisition_id")
    } | {
        "source_id": "ESM1" if image["source_id"] == "ESM2" else "ESM4",
        "sample_id": sample_id, "center_x": x, "center_y": y,
        "patch_radius_px": 32, "patch_side_px": 65, "mapping_offset_xy": [0, 0],
        "patch_xyxy": [x - 32, y - 32, x + 33, y + 33],
    }


class InputTrap:
    def __len__(self):
        raise AssertionError("forbidden buffer inspected")

    def __getitem__(self, key):
        raise AssertionError("forbidden input indexed")

    def __array__(self, *args, **kwargs):
        raise AssertionError("forbidden input converted")


class SolutalMetadataTests(unittest.TestCase):
    def assert_denied_before_input(self, image, samples):
        with mock.patch.object(ablation, "_scientific_runtime") as runtime:
            with self.assertRaises(ablation.AblationContractError):
                ablation.checked_solutal_luminance(InputTrap(), image, samples)
            if len(samples) == 1:
                with self.assertRaises(ablation.AblationContractError):
                    ablation.extract_solutal_patch(InputTrap(), image, samples[0])
            runtime.assert_not_called()

    def test_final_structural_and_solutal_frames_deny_before_buffers_or_arrays(self):
        for source, frame in (("ESM1", 293), ("ESM4", 295), ("ESM2", 293), ("ESM5", 295)):
            image = image_metadata(source, frame, "FINAL_TEST")
            with self.subTest(source=source):
                self.assert_denied_before_input(image, [structural_sample(image)])

    def test_other_sources_frames_and_spoofed_splits_are_denied(self):
        valid = image_metadata()
        for changes in ({"source_id": "ESM1"}, {"source_id": "ESM3"},
                        {"source_id": "ESM6"}, {"source_id": None}, {"source_id": []},
                        {"frame_index": 0}, {"frame_index": 74}, {"frame_index": True},
                        {"frame_index": 73.0}, {"split": "DEVELOPMENT"},
                        {"split": "FINAL_TEST"}):
            with self.subTest(changes=changes):
                self.assert_denied_before_input(valid | changes, [structural_sample(valid)])

    def test_cross_modality_source_frame_split_or_acquisition_mismatch_denied(self):
        image = image_metadata()
        sample = structural_sample(image)
        for changes in ({"source_id": "ESM2"}, {"source_id": "ESM4"},
                        {"frame_index": 146}, {"frame_index": True},
                        {"split": "DEVELOPMENT"}, {"split": "FINAL_TEST"},
                        {"acquisition_id": "top_down_parallel"}):
            with self.subTest(changes=changes):
                self.assert_denied_before_input(image, [sample | changes])

    def test_native_representation_must_be_exact(self):
        image = image_metadata()
        for changes in ({"width": 1280}, {"width": 1278.0}, {"height": 1024},
                        {"height": 1018.0}, {"bit_depth": True}, {"bit_depth": 8.0},
                        {"pixel_format": "rgb24"}, {"frame_bytes": image["frame_bytes"] - 1},
                        {"acquisition_id": "top_down_parallel"}):
            with self.subTest(changes=changes):
                self.assert_denied_before_input(image | changes, [structural_sample(image)])

    def test_metadata_requires_unique_sample_ids_and_original_crop(self):
        image = image_metadata()
        sample = structural_sample(image)
        for changes in ({"sample_id": ""}, {"sample_id": None}, {"center_x": 200.0},
                        {"center_y": True}, {"patch_side_px": 63}, {"patch_radius_px": 31},
                        {"patch_xyxy": [168, 268, 232, 333]}, {"mapping_offset_xy": [1, 0]}):
            with self.subTest(changes=changes):
                self.assert_denied_before_input(image, [sample | changes])
        self.assert_denied_before_input(image, [sample, copy.deepcopy(sample)])
        self.assert_denied_before_input(image, [])

    def test_support_contact_failure_stops_without_moving_or_replacing_sample(self):
        image = image_metadata()
        # Historical geometry [5,124,1273,864] after the one-pixel erosion.
        for x, y in ((36, 300), (1241, 300), (200, 155), (200, 832)):
            with self.subTest(center=(x, y)), mock.patch.object(ablation, "_scientific_runtime") as runtime:
                with self.assertRaises(ablation.AblationContractError) as failure:
                    ablation.checked_solutal_luminance(InputTrap(), image, [structural_sample(image, x, y)])
                self.assertEqual(failure.exception.code, "BLOCKED_SOLUTAL_SUPPORT")
                runtime.assert_not_called()

    def test_one_invalid_patch_denies_the_entire_batch_before_buffer(self):
        image = image_metadata()
        samples = [structural_sample(image, sample_id="valid"),
                   structural_sample(image, x=36, sample_id="invalid")]
        before = copy.deepcopy(samples)
        self.assert_denied_before_input(image, samples)
        self.assertEqual(samples, before)

    def test_full_immutable_byte_count_required_before_runtime(self):
        image = image_metadata()
        for raw in (b"", bytearray(image["frame_bytes"]), memoryview(b""), InputTrap()):
            with self.subTest(kind=type(raw).__name__), mock.patch.object(ablation, "_scientific_runtime") as runtime:
                with self.assertRaises(ablation.AblationContractError):
                    ablation.checked_solutal_luminance(raw, image, [structural_sample(image)])
                runtime.assert_not_called()


class DevelopmentDecisionTests(unittest.TestCase):
    def test_strict_improvement_and_exact_tie_with_no_rounding(self):
        reference = 0.6875
        for value, expected in (
            (0.625, "STRUCTURAL_ONLY"), (reference, "STRUCTURAL_ONLY"),
            (math.nextafter(reference, 1.0), "STRUCTURAL_PLUS_RELATIVE_SOLUTE"),
            (0.75, "STRUCTURAL_PLUS_RELATIVE_SOLUTE"),
        ):
            with self.subTest(value=value):
                result = ablation.development_decision(value)
                self.assertEqual(result["structural_reference_balanced_accuracy"], reference)
                self.assertEqual(result["delta_dev_balanced_accuracy"], value - reference)
                self.assertEqual(result["dev_modality_preference"], expected)

    def test_missing_nonfinite_or_nonmetric_value_cannot_choose_modality(self):
        for value in (None, True, "0.75", float("nan"), float("inf"), -0.1, 1.1):
            with self.subTest(value=value), self.assertRaises(ablation.AblationContractError):
                ablation.development_decision(value)


@unittest.skipUnless(NUMERICAL, "optional pinned scientific dependencies unavailable")
class AblationSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.np = np

    def native_bytes(self, image, uv=(128, 128)):
        np = self.np
        width, height = image["width"], image["height"]
        y = (np.arange(width * height, dtype=np.uint32) % 251).astype(np.uint8).reshape(height, width)
        return y.tobytes() + bytes([uv[0]]) * (width * height // 4) + bytes([uv[1]]) * (width * height // 4), y

    def features(self):
        np = self.np
        labels = np.array([0, 1] * 8)
        features = np.zeros((16, 20), dtype=float)
        features[np.arange(16), labels] = 1.0
        features[np.arange(16), labels + 10] = 1.0
        return features, labels

    def test_native_y_view_and_identity_crop_equal_original_without_mutation(self):
        np = self.np
        for image in (image_metadata(), image_metadata("ESM5", 197, "DEVELOPMENT")):
            raw, expected = self.native_bytes(image)
            sample = structural_sample(image)
            original = copy.deepcopy(sample)
            y, report = ablation.checked_solutal_luminance(raw, image, [sample])
            np.testing.assert_array_equal(y, expected)
            self.assertFalse(y.flags.writeable)
            self.assertTrue(np.shares_memory(y, np.frombuffer(raw, dtype=np.uint8)))
            patch = ablation.extract_solutal_patch(y, image, sample)
            np.testing.assert_array_equal(patch, expected[268:333, 168:233])
            self.assertFalse(np.shares_memory(patch, y))
            self.assertEqual(sample, original)
            self.assertEqual(report["samples_checked"], [sample["sample_id"]])

    def test_solutal_chroma_is_never_classified_as_structural_overlay(self):
        np = self.np
        image = image_metadata()
        expected = None
        for uv in ((128, 128), (0, 255), (255, 0)):
            raw, y = self.native_bytes(image, uv=uv)
            actual, report = ablation.checked_solutal_luminance(raw, image, [structural_sample(image)])
            np.testing.assert_array_equal(actual, y)
            if expected is not None:
                np.testing.assert_array_equal(actual, expected)
            expected = actual
            self.assertEqual(report["status"], "PASS")

    def test_all_four_admissible_geometry_edges_remain_unchanged(self):
        image = image_metadata()
        raw, _ = self.native_bytes(image)
        samples = [structural_sample(image, x, y, str(i))
                   for i, (x, y) in enumerate(((37, 156), (1240, 156), (37, 831), (1240, 831)))]
        _, report = ablation.checked_solutal_luminance(raw, image, samples)
        self.assertEqual(report["sample_count"], 4)

    def test_solutal_crop_never_coerces_dtype_shape_or_rgb(self):
        np = self.np
        image = image_metadata()
        for array in (np.zeros((1018, 1278), dtype=float),
                      np.zeros((1012, 1278), dtype=np.uint8),
                      np.zeros((1018, 1278, 3), dtype=np.uint8), InputTrap()):
            with self.subTest(shape=getattr(array, "shape", None)), self.assertRaises(ablation.AblationContractError):
                ablation.extract_solutal_patch(array, image, structural_sample(image))

    def test_feature_order_is_exact_structural_then_solutal_ten_bins_each(self):
        np = self.np
        row, col = np.indices((65, 65))
        structural = ((row * 17 + col * 3) % 256).astype(np.uint8)
        solutal = np.full((65, 65), 120, dtype=np.uint8)
        originals = (structural.copy(), solutal.copy())
        features = ablation.multimodal_features(structural, solutal)
        self.assertEqual(features.shape, (20,))
        np.testing.assert_array_equal(features[:10], baseline.lbp_features(structural))
        np.testing.assert_array_equal(features[10:], baseline.lbp_features(solutal))
        self.assertAlmostEqual(float(features[:10].sum()), 1.0)
        self.assertAlmostEqual(float(features[10:].sum()), 1.0)
        self.assertAlmostEqual(float(features.sum()), 2.0)
        np.testing.assert_array_equal(structural, originals[0])
        np.testing.assert_array_equal(solutal, originals[1])

    def test_feature_patch_resize_float_or_extra_channel_is_prohibited(self):
        np = self.np
        valid = np.zeros((65, 65), dtype=np.uint8)
        for invalid in (valid[:64], valid.astype(float), valid[:, :, None], InputTrap()):
            for pair in ((invalid, valid), (valid, invalid)):
                with self.assertRaises(baseline.BaselineContractError):
                    ablation.multimodal_features(*pair)

    def test_twenty_columns_and_two_unit_histograms_required_before_fit(self):
        np = self.np
        features, labels = self.features()
        corrupted_half = features.copy()
        corrupted_half[:, 10:] *= 0.5
        negatives = features.copy()
        negatives[:, 9] = -0.1
        for invalid in (features[:, :10], features[:, :19], features[:0], features.astype(bool),
                        features / 2, corrupted_half, negatives, np.full(features.shape, np.nan)):
            with self.subTest(shape=invalid.shape), mock.patch("sklearn.ensemble.RandomForestClassifier") as constructor:
                with self.assertRaises(ablation.AblationContractError):
                    ablation.evaluate_ablation(invalid, labels, features, labels)
                constructor.assert_not_called()

    def test_misaligned_unknown_or_single_class_labels_deny_before_fit(self):
        np = self.np
        features, labels = self.features()
        for invalid in (labels[:3], labels.astype(float), labels.astype(bool),
                        np.zeros(16, dtype=int), np.array([0, 2] * 8)):
            with self.subTest(shape=invalid.shape), mock.patch("sklearn.ensemble.RandomForestClassifier") as constructor:
                with self.assertRaises(ablation.AblationContractError):
                    ablation.evaluate_ablation(features, labels, features, invalid)
                constructor.assert_not_called()

    def test_rf_parameter_drift_denies_before_fit(self):
        features, labels = self.features()
        estimator = mock.Mock()
        estimator.get_params.return_value = baseline.RF_PARAMETERS | {"class_weight": "balanced"}
        with mock.patch("sklearn.ensemble.RandomForestClassifier", return_value=estimator):
            with self.assertRaises(ablation.AblationContractError):
                ablation.evaluate_ablation(features, labels, features, labels)
        estimator.fit.assert_not_called()

    def test_exact_one_synthetic_fit_preserves_defaults_without_structural_rerun(self):
        from sklearn.ensemble import RandomForestClassifier
        features, labels = self.features()
        estimator = RandomForestClassifier(n_estimators=100, random_state=42)
        with mock.patch("sklearn.ensemble.RandomForestClassifier", return_value=estimator) as constructor:
            with mock.patch.object(estimator, "fit", wraps=estimator.fit) as fit:
                with mock.patch.object(baseline, "evaluate_baseline", side_effect=AssertionError("structural rerun")):
                    result = ablation.evaluate_ablation(features, labels, features[:4].copy(), labels[:4].copy())
                constructor.assert_called_once_with(n_estimators=100, random_state=42)
                fit.assert_called_once()
        self.assertEqual(result["parameters"], baseline.RF_PARAMETERS)
        self.assertEqual(result["feature_dimension"], 20)
        self.assertEqual(result["fit_calls"], 1)
        self.assertEqual(result["structural_baseline_fit_calls"], 0)
        self.assertEqual(result["tuning_runs"], 0)
        self.assertFalse(result["final_test_evaluated"])
        self.assertEqual(set(result["evaluations"]), {"TRAIN", "DEVELOPMENT"})
        for split, count in (("TRAIN", 16), ("DEVELOPMENT", 4)):
            result_split = result["evaluations"][split]
            self.assertEqual(result_split["sample_count"], count)
            self.assertEqual(sum(result_split[key] for key in ("TN", "FP", "FN", "TP")), count)
            self.assertEqual(len(result_split["probabilities_class_order_0_1"]), count)
        actual_ba = result["evaluations"]["DEVELOPMENT"]["balanced_accuracy"]
        self.assertEqual(result["delta_dev_balanced_accuracy"], actual_ba - 0.6875)
        self.assertEqual(result["dev_modality_preference"], "STRUCTURAL_PLUS_RELATIVE_SOLUTE")
        json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
