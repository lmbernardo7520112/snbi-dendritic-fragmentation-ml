"""V2-D scientific contracts using generated arrays only."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

from snbi_fragmentation import ti2r_solute_direct_registration as v1
from snbi_fragmentation import ti2r_solute_v2_calibration as v2


NUMERICAL = importlib.util.find_spec("numpy") is not None and importlib.util.find_spec("scipy") is not None
ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/registration/ti2r-solute-direct-method.json").read_text(encoding="utf-8"))
V2_CONFIG = json.loads((ROOT / "configs/registration/ti2r-solute-v2-method.json").read_text(encoding="utf-8"))


class SoluteV2ConfigurationTests(unittest.TestCase):
    def test_exact_preregistered_perturbations_search_and_no_new_absolute_floor(self):
        v2.validate_config(V2_CONFIG)
        self.assertEqual(len(v2.PERTURBATIONS), 16)
        self.assertEqual(len(set(v2.PERTURBATIONS)), 16)
        self.assertEqual(len(v2.CORRECTIONS), 81)
        self.assertNotIn((0, 0), v2.PERTURBATIONS)
        self.assertTrue(all((-p[0], -p[1]) in v2.CORRECTIONS for p in v2.PERTURBATIONS))
        self.assertIsNone(V2_CONFIG["new_absolute_floors"])

    def test_configuration_changes_fail_closed_including_bool_integer_confusion(self):
        for key, value in (("minimum_recovery_margin", 0.004), ("maximum_recovery_error_px", 1.0),
                           ("common_support_erosion_radius_px", 7), ("required_recoveries_per_metric_per_frame", 15),
                           ("absolute_identity_floors_are_gates", True), ("identity_positive_control", [False, 0])):
            config = copy.deepcopy(V2_CONFIG)
            config[key] = value
            with self.assertRaises(v1.SoluteRegistrationError):
                v2.validate_config(config)

    def test_relative_decision_ignores_only_historical_absolute_floor(self):
        raw = {"available_blocks": 18, "quadrants": [[0,0],[1,0],[0,1],[1,1]], "identity_score": 0.6,
               "spatial_margin": 0.01, "spatial_controls": [{"score": 0.59, "offset": list(p)} for p in v1.spatial_controls()],
               "temporal_controls": [{"moving_time": 0, "score": 0.4, "margin": 0.2}], "blocks": []}
        info = [{"classification": "IDENTIFIABLE"}]
        result = v2._relative_original(raw, "selection", info, CONFIG)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["absolute_floor_used_as_gate"])
        self.assertEqual(result["raw_v1"]["identity_score"], 0.6)
        raw["spatial_margin"] = 0.004
        self.assertNotEqual(v2._relative_original(raw, "selection", info, CONFIG)["status"], "PASS")

    def test_temporal_margin_and_four_quadrants_remain_blocking(self):
        raw = {"available_blocks": 18, "quadrants": [[0,0],[1,0],[0,1],[1,1]], "identity_score": 0.6,
               "spatial_margin": 0.01, "spatial_controls": [{"score": 0.59, "offset": list(p)} for p in v1.spatial_controls()],
               "temporal_controls": [{"moving_time": 0, "score": 0.599, "margin": 0.001}], "blocks": []}
        info = [{"classification": "IDENTIFIABLE"}]
        self.assertNotEqual(v2._relative_original(raw, "selection", info, CONFIG)["status"], "PASS")
        raw["temporal_controls"][0]["margin"] = 0.2
        raw["quadrants"].pop()
        self.assertNotEqual(v2._relative_original(raw, "selection", info, CONFIG)["status"], "PASS")

    def test_ties_wrong_inverse_low_margin_and_missing_support_never_pass(self):
        p = (4, 0)
        scores = [0.2] * 81
        correct = v2.CORRECTIONS.index((-4, 0))
        scores[correct] = 0.6
        good = v2._recovery_record(p, scores, True, CONFIG, V2_CONFIG)
        self.assertEqual(good["status"], "PASS")
        self.assertEqual(good["correct_rank"], 1)
        self.assertEqual(good["recovery_error_px"], 0.0)
        self.assertNotEqual(v2._recovery_record(p, scores, False, CONFIG, V2_CONFIG)["status"], "PASS")
        for competitor in (0.6, 0.61, 0.596):
            altered = list(scores)
            altered[0] = competitor
            record = v2._recovery_record(p, altered, True, CONFIG, V2_CONFIG)
            self.assertNotEqual(record["status"], "PASS")
            self.assertEqual(record["scores"][0], competitor)

    def test_fifteen_of_sixteen_is_not_rounded_to_passing(self):
        results = []
        for index, p in enumerate(v2.PERTURBATIONS):
            scores = [0.2] * 81
            correct = v2.CORRECTIONS.index((-p[0], -p[1]))
            scores[correct] = 0.6
            if index == 15:
                scores[(correct+1) % 81] = 0.61
            results.append(v2._recovery_record(p, scores, True, CONFIG, V2_CONFIG))
        passed = sum(r["status"] == "PASS" for r in results)
        self.assertEqual(passed, 15)
        self.assertEqual(passed / len(results), 0.9375)
        self.assertLess(passed, V2_CONFIG["required_recoveries_per_metric_per_frame"])
        self.assertEqual(results[-1]["correct_rank"], 2)
        self.assertGreater(results[-1]["recovery_error_px"], 0.5)


@unittest.skipUnless(NUMERICAL, "optional pinned NumPy/SciPy runtime unavailable")
class SoluteV2ScientificSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        from scipy import ndimage
        cls.np, cls.ndimage = np, ndimage
        rng = np.random.default_rng(2026092001)
        cls.images = [128 + 45 * ndimage.gaussian_filter(rng.normal(size=(512, 512)), 1.0) for _ in range(3)]

    def prepared(self, image, mask=None):
        return v1.prepare_luminance(image, self.np.ones(image.shape, dtype=bool) if mask is None else mask, CONFIG)

    def pair(self, index=1):
        return self.prepared(self.images[index]), self.prepared(256-self.images[index])

    def test_expanded_features_preserve_both_v1_kernels_and_individual_eta(self):
        frame, _ = self.pair()
        for role in ("selection", "audit"):
            block = next(b for b in v1.blocks(frame.luminance.shape, CONFIG) if b["role"] == role)
            old = v1._features(frame, block, role, CONFIG)
            new = v2._expanded_features(frame, block, role, CONFIG)
            self.assertEqual(old["eta"], new["eta"])
            for offset in v1.OFFSETS:
                self.np.testing.assert_allclose(v1._central(old["features"], offset), v2._sample(new["features"], offset), atol=1e-6)

    def test_integer_translation_pullback_matches_explicit_no_wrap_translation(self):
        frame, _ = self.pair()
        for role in ("selection", "audit"):
            block = next(b for b in v1.blocks(frame.luminance.shape, CONFIG) if b["role"] == role)
            expanded = v2._expanded_features(frame, block, role, CONFIG)
            source = expanded["features"]
            for p in v2.PERTURBATIONS:
                dx, dy = p
                shifted = self.np.full(source.shape, self.np.nan, dtype=source.dtype)
                height, width = source.shape[-2:]
                sx0, sx1 = max(0, -dx), min(width, width-dx)
                sy0, sy1 = max(0, -dy), min(height, height-dy)
                shifted[..., sy0+dy:sy1+dy, sx0+dx:sx1+dx] = source[..., sy0:sy1, sx0:sx1]
                self.np.testing.assert_array_equal(v2._sample(shifted), v2._sample(source, (-dx, -dy)))
                self.np.testing.assert_array_equal(v2._sample(shifted, p), v2._sample(source))

    def test_all_sixteen_inverse_shifts_and_identity_pass_both_descriptors(self):
        reference, moving = self.pair()
        ref_info, mov_info = v1.image_information(reference, CONFIG), v1.image_information(moving, CONFIG)
        for role in ("selection", "audit"):
            result = v2.calibrate_role(reference, moving, ref_info, mov_info, role, CONFIG, V2_CONFIG)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["correct_recoveries"], 16)
            self.assertEqual(result["identity_control"]["status"], "PASS")
            self.assertEqual(len(result["quadrants"]), 4)
            self.assertEqual(len(result["perturbations"]), 16)
            for p, record in zip(v2.PERTURBATIONS, result["perturbations"]):
                self.assertEqual(record["best_correction_dxdy"], [-p[0], -p[1]])
                self.assertEqual(record["correct_rank"], 1)
                self.assertEqual(record["recovery_error_px"], 0.0)
                self.assertGreaterEqual(record["margin"], 0.005)
                self.assertEqual(len(record["scores"]), 81)
            self.assertTrue(all(len(b["score_matrix"]) == 17 and all(len(row) == 81 for row in b["score_matrix"])
                                for b in result["blocks"] if b["status"] == "MEASURED"))

    def test_translated_luminance_recomputed_v1_kernels_equal_feature_pullback(self):
        frame, _ = self.pair()
        for role in ("selection", "audit"):
            block = next(b for b in v1.blocks(frame.luminance.shape, CONFIG) if b["role"] == role)
            x0, y0, x1, y1 = block["xyxy"]
            expanded = v2._expanded_features(frame, block, role, CONFIG)
            for p in v2.PERTURBATIONS:
                for correction in ((0,0), (-p[0],-p[1]), (4,4), (-4,-4)):
                    dx, dy = p[0]+correction[0], p[1]+correction[1]
                    translated = self.np.full(frame.luminance.shape, 37.0)
                    height, width = translated.shape
                    sx0, sx1 = max(0,-dx), min(width,width-dx)
                    sy0, sy1 = max(0,-dy), min(height,height-dy)
                    translated[sy0+dy:sy1+dy,sx0+dx:sx1+dx] = frame.luminance[sy0:sy1,sx0:sx1]
                    prepared = self.prepared(translated)
                    if role == "selection":
                        recomputed = v1.self_similarity(prepared.luminance[y0-3:y1+3,x0-3:x1+3], CONFIG)[:,3:-3,3:-3]
                    else:
                        gx, gy = prepared.gx[y0:y1,x0:x1], prepared.gy[y0:y1,x0:x1]
                        eta = expanded["eta"]
                        denominator = self.np.sqrt(gx*gx+gy*gy+eta*eta)
                        recomputed = self.np.stack((gx/denominator,gy/denominator)).astype(self.np.float32)
                    sampled = v2._sample(expanded["features"], (-dx,-dy))
                    self.np.testing.assert_allclose(recomputed, sampled, atol=1e-6)

    def test_unrelated_images_preserve_every_failed_perturbation_and_raw_score(self):
        reference, moving = self.prepared(self.images[1]), self.prepared(self.images[2])
        ri, mi = v1.image_information(reference, CONFIG), v1.image_information(moving, CONFIG)
        for role in ("selection", "audit"):
            result = v2.calibrate_role(reference, moving, ri, mi, role, CONFIG, V2_CONFIG)
            self.assertNotEqual(result["status"], "PASS")
            self.assertEqual(len(result["perturbations"]), 16)
            self.assertTrue(all(len(p["scores"]) == 81 for p in result["perturbations"]))
            self.assertEqual(result["error_based_rejections"], 0)

    def test_common_support_excludes_mask_holes_and_all_translation_footprints(self):
        mask = self.np.ones((512, 512), dtype=bool)
        mask[235:245, 240:250] = False
        reference = self.prepared(self.images[1], mask)
        moving = self.prepared(256-self.images[1], mask)
        ri, mi = v1.image_information(reference, CONFIG), v1.image_information(moving, CONFIG)
        for role, mask_name in (("selection", "descriptor_mask"), ("audit", "gradient_mask")):
            result = v2.calibrate_role(reference, moving, ri, mi, role, CONFIG, V2_CONFIG)
            eroded = self.ndimage.binary_erosion(getattr(reference, mask_name) & getattr(moving, mask_name),
                                               structure=self.np.ones((17,17), dtype=bool), border_value=0)
            for block in result["blocks"]:
                if block["status"] == "MEASURED":
                    x0, y0, x1, y1 = block["xyxy"]
                    self.assertEqual(block["valid_pixels"], int(eroded[y0:y1,x0:x1].sum()))
            self.assertTrue(result["same_pixels_for_all_perturbations_and_corrections"])

    def test_missing_quadrant_or_seven_blocks_blocks_recovery_without_hiding_scores(self):
        reference, moving = self.pair()
        ri, mi = v1.image_information(reference, CONFIG), v1.image_information(moving, CONFIG)
        blocks = [b for b in ri["blocks"] if b["role"] == "selection"]
        for index, block in enumerate(blocks):
            block["qualified"] = index < 7
        result = v2.calibrate_role(reference, moving, ri, mi, "selection", CONFIG, V2_CONFIG)
        self.assertEqual(result["available_blocks"], 7)
        self.assertEqual(result["status"], "FAIL_RECOVERY")
        self.assertEqual(result["correct_recoveries"], 0)
        self.assertTrue(all(p["true_score"] is not None for p in result["perturbations"]))

    def test_initial_observability_and_two_positive_frames_are_kept_separate(self):
        flat = self.prepared(self.np.full((512,512), 128.0))
        result = v2.evaluate_series([(flat, flat), self.pair(1), self.pair(2)], CONFIG, V2_CONFIG)
        self.assertEqual(result["status"], v2.PASS)
        self.assertEqual([f["status"] for f in result["per_frame"]], ["NON_IDENTIFIABLE", "PASS", "PASS"])
        self.assertIsNone(result["per_frame"][0]["calibration"])
        self.assertEqual(len(result["temporal_controls"]), 6)
        self.assertFalse(result["holdout_evaluated"])
        self.assertIsNone(result["matrix"])

    def test_a_single_failed_positive_time_cannot_be_rescued_by_other_frame(self):
        flat = self.prepared(self.np.full((512,512), 128.0))
        wrong = self.prepared(self.images[2]), self.prepared(self.images[0])
        result = v2.evaluate_series([(flat, flat), self.pair(1), wrong], CONFIG, V2_CONFIG)
        self.assertEqual(result["status"], v2.BLOCKED)
        self.assertNotEqual(result["per_frame"][2]["status"], "PASS")
        self.assertEqual(len(result["per_frame"][2]["calibration"]["SS8"]["perturbations"]), 16)

    def test_original_residuals_and_all_spatial_temporal_controls_are_unchanged(self):
        flat = self.prepared(self.np.full((512,512), 128.0))
        pairs = [(flat, flat), self.pair(1), self.pair(2)]
        original = v1.evaluate_series(pairs, CONFIG)
        with mock.patch.object(v2, "calibrate_role", return_value={"status": "FAIL_RECOVERY", "perturbations": []}):
            result = v2.evaluate_series(pairs, CONFIG, V2_CONFIG)
        self.assertEqual(result["temporal_controls"], original["temporal_controls"])
        self.assertEqual(result["original_residual_aggregate"], original["aggregate"])
        for i in (1,2):
            self.assertEqual(result["per_frame"][i]["original"]["SS8"]["raw_v1"], original["per_frame"][i]["selection"])
            self.assertEqual(result["per_frame"][i]["original"]["NGF"]["raw_v1"], original["per_frame"][i]["audit"])

    def test_dimensions_count_and_holdout_api_fail_closed(self):
        pairs = [self.pair()] * 3
        result = v2.evaluate_development("ESM2-to-ESM1", pairs, CONFIG, V2_CONFIG)
        self.assertEqual(result["status"], "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE")
        with self.assertRaises(v1.SoluteRegistrationError):
            v2.evaluate_series(pairs[:2], CONFIG, V2_CONFIG)
        with self.assertRaises(v1.SoluteRegistrationError):
            v2.evaluate_development("ESM3-to-ESM1", pairs, CONFIG, V2_CONFIG)
        self.assertFalse(hasattr(v2, "evaluate_holdout"))

    def test_sampler_rejects_unsupported_noninteger_coordinates(self):
        array = self.np.zeros((1,40,40), dtype=self.np.float32)
        for offset in ((9,0), (0,-9), (1.0,0), (True,0)):
            with self.assertRaises(v1.SoluteRegistrationError):
                v2._sample(array, offset)


if __name__ == "__main__":
    unittest.main()
