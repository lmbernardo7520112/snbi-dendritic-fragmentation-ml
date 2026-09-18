"""Frozen multimodal contracts exercised solely on synthetic memory."""

import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

from snbi_fragmentation import ti2r_solute_direct_registration as solute


NUMERICAL = importlib.util.find_spec("numpy") is not None and importlib.util.find_spec("scipy") is not None
CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs/registration/ti2r-solute-direct-method.json"


@unittest.skipUnless(NUMERICAL, "optional pinned NumPy/SciPy runtime unavailable")
class SoluteScientificSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        from scipy import ndimage
        cls.np, cls.ndimage = np, ndimage
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        generator = np.random.default_rng(2026091901)
        cls.images = [128 + 45 * ndimage.gaussian_filter(generator.normal(size=(512, 512)), 1.0) for _ in range(3)]

    def prepared(self, image, mask=None):
        if mask is None:
            mask = self.np.ones(image.shape, dtype=bool)
        return solute.prepare_luminance(image, mask, self.config)

    def series(self, transform=lambda image: image):
        return [(self.prepared(image), self.prepared(transform(image))) for image in self.images]

    def test_only_identity_is_admissible_and_exactly_48_spatial_controls_exist(self):
        controls = solute.spatial_controls()
        self.assertEqual(len(controls), 48)
        self.assertNotIn((0, 0), controls)
        self.assertEqual(set(controls), {(x, y) for y in range(-3, 4) for x in range(-3, 4)} - {(0, 0)})
        self.assertEqual(solute.identity_matrix(), [[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    def test_positive_identity_passes_both_modal_metrics_and_temporal_controls(self):
        result = solute.evaluate_series(self.series(), self.config)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["offset"], [0, 0])
        self.assertEqual(len(result["temporal_controls"]), 6)
        self.assertTrue(all(frame["selection"]["spatial_margin"] >= self.config["mind_spatial_margin"] for frame in result["per_frame"]))
        self.assertLessEqual(result["aggregate"]["maximum_px"], 0.02)

    def test_contrast_inversion_is_not_a_geometric_disagreement(self):
        result = solute.evaluate_series(self.series(lambda x: 256 - x), self.config)
        self.assertEqual(result["status"], "PASS", result["per_frame"])

    def test_monotonic_nonlinear_intensity_mapping_preserves_geometry(self):
        result = solute.evaluate_series(self.series(lambda x: 32 + 192 * ((x - 32) / 192) ** 2), self.config)
        self.assertEqual(result["status"], "PASS", result["per_frame"])

    def test_descriptor_is_explicit_self_similarity_and_affine_contrast_invariant(self):
        image = self.images[0][100:164, 100:164]
        a = solute.self_similarity(image, self.config)
        b = solute.self_similarity(210 - 0.6 * image, self.config)
        self.assertEqual(a.shape[0], 8)
        self.np.testing.assert_allclose(a, b, atol=1e-6)
        self.assertEqual(self.config["selection_descriptor"], "LOCAL_SELF_SIMILARITY_8_NOT_EXACT_MIND_SSC")

    def test_ngf_is_sign_invariant_and_zero_gradients_do_not_match(self):
        gx = self.np.array([2.0, 0.0])
        gy = self.np.array([1.0, 0.0])
        score = solute.ngf_values(gx, gy, -gx, -gy, 0.01, 0.01)
        self.assertGreater(score[0], 0.99)
        self.assertEqual(score[1], 0.0)

    def test_individual_identifiability_never_accepts_partner_or_scores(self):
        import inspect
        self.assertEqual(tuple(inspect.signature(solute.image_information).parameters), ("frame", "config"))
        reference = self.prepared(self.images[0])
        first = solute.image_information(reference, self.config)
        for moving in (self.prepared(self.images[1]), self.prepared(self.np.full((512, 512), 128.0))):
            result = solute.evaluate_series([(reference, moving)] * 3, self.config)
            self.assertEqual(result["per_frame"][0]["reference_information"], first)

    def test_flat_or_directionally_degenerate_images_are_nonidentifiable(self):
        yy, xx = self.np.indices((512, 512))
        for image in (self.np.full((512, 512), 128.0), 128 + 20 * self.np.sin(xx / 8)):
            info = solute.image_information(self.prepared(image), self.config)
            self.assertEqual(info["classification"], "NON_IDENTIFIABLE")

    def test_dominant_saturation_is_nonidentifiable(self):
        image = self.np.where(self.images[0] >= 128, 235.0, 16.0)
        info = solute.image_information(self.prepared(image), self.config)
        self.assertEqual(info["classification"], "NON_IDENTIFIABLE")
        self.assertTrue(all(b["saturation_fraction"] > 0.5 for b in info["blocks"]))

    def test_periodic_texture_is_not_certifiable_even_beyond_control_radius(self):
        yy, xx = self.np.indices((512, 512))
        for period in (4, 8, 10):
            image = 128 + 20 * self.np.cos(2 * self.np.pi * xx / period) + 20 * self.np.sin(2 * self.np.pi * yy / period)
            info = solute.image_information(self.prepared(image), self.config)
            self.assertEqual(info["classification"], "NON_IDENTIFIABLE", period)

    def test_two_identifiable_development_times_and_one_holdout_are_required(self):
        good = self.series()
        flat = self.prepared(self.np.full((512, 512), 128.0))
        result = solute.evaluate_series([(flat, flat), good[1], good[2]], self.config)
        self.assertEqual(result["status"], "PASS", result["per_frame"])
        self.assertEqual(result["non_identifiable_frames"], [0])
        blocked = solute.evaluate_series([(flat, flat), (flat, flat), good[2]], self.config)
        self.assertEqual(blocked["status"], "BLOCKED_MODALITY_INFORMATION_INSUFFICIENT")
        holdout = solute.evaluate_series([(flat, flat), good[2]], self.config, holdout=True)
        self.assertEqual(holdout["status"], "PASS", holdout["per_frame"])

    def test_spatially_independent_content_cannot_certify_identity(self):
        series = [(self.prepared(self.images[i]), self.prepared(self.images[(i + 1) % 3])) for i in range(3)]
        result = solute.evaluate_series(series, self.config)
        self.assertNotEqual(result["status"], "PASS")
        self.assertIsNone(result["matrix"])

    def test_known_nonzero_shifts_remain_controls_never_transformations(self):
        for offset in ((-3, -3), (-2, 1), (1, 0), (0, 3), (3, 3)):
            series = self.series(lambda x: self.np.roll(x, (offset[1], offset[0]), axis=(0, 1)))
            result = solute.evaluate_series(series, self.config)
            self.assertNotEqual(result["status"], "PASS", offset)
            self.assertIsNone(result["offset"])
            self.assertIsNone(result["matrix"])
            self.assertTrue(any(f["selection"]["best_control_offset"] != [0, 0] for f in result["per_frame"]))

    def test_identical_static_times_fail_temporal_discrimination(self):
        pair = (self.prepared(self.images[0]), self.prepared(256 - self.images[0]))
        result = solute.evaluate_series([pair] * 3, self.config)
        self.assertEqual(result["status"], "BLOCKED_IDENTITY_NOT_DISCRIMINATIVE")
        self.assertEqual(len(result["temporal_controls"]), 6)
        self.assertTrue(all(abs(c["mind_margin"]) < 1e-10 for c in result["temporal_controls"]))

    def test_all_wrong_temporal_pairs_are_reported_including_nonidentifiable_initial(self):
        series = self.series()
        flat = self.prepared(self.np.full((512, 512), 128.0))
        result = solute.evaluate_series([(flat, flat), series[1], series[2]], self.config)
        self.assertEqual({(c["reference_time"], c["moving_time"]) for c in result["temporal_controls"]}, {(i, j) for i in range(3) for j in range(3) if i != j})
        self.assertEqual(result["status"], "PASS")

    def test_partial_masks_do_not_create_alignment_features(self):
        mask = self.np.ones((512, 512), dtype=bool)
        mask[::37, ::31] = False
        pairs = [(self.prepared(image, mask), self.prepared(256 - image, mask)) for image in self.images]
        result = solute.evaluate_series(pairs, self.config)
        self.assertEqual(result["status"], "PASS", result["per_frame"])
        unrelated = [(self.prepared(self.images[i], mask), self.prepared(self.images[(i + 1) % 3], mask)) for i in range(3)]
        self.assertNotEqual(solute.evaluate_series(unrelated, self.config)["status"], "PASS")

    def test_selection_and_audit_footprints_do_not_overlap(self):
        blocks = solute.blocks((512, 512), self.config)
        selection = [b for b in blocks if b["role"] == "selection"]
        audit = [b for b in blocks if b["role"] == "audit"]
        for a in selection:
            x0, y0, x1, y1 = a["xyxy"]
            for b in audit:
                u0, v0, u1, v1 = b["xyxy"]
                self.assertTrue(x1 + 10 <= u0 or u1 + 10 <= x0 or y1 + 10 <= v0 or v1 + 10 <= y0)

    def test_audit_local_error_is_preserved_without_trimming(self):
        series = self.series()
        reference, moving = series[1]
        changed = moving.luminance.copy()
        block = next(b for b in solute.blocks(changed.shape, self.config) if b["role"] == "audit")
        x0, y0, x1, y1 = block["xyxy"]
        changed[y0-5:y1+5, x0-5:x1+5] = self.np.roll(changed[y0-5:y1+5, x0-5:x1+5], 3, axis=1)
        series[1] = reference, self.prepared(changed)
        result = solute.evaluate_series(series, self.config)
        self.assertEqual(result["status"], "BLOCKED_MULTIMODAL_METRIC_DISCORDANCE")
        record = next(b for b in result["per_frame"][1]["audit"]["blocks"] if b["id"] == block["id"])
        self.assertTrue(record["peak_at_search_boundary"])
        self.assertGreaterEqual(record["residual_px"], 2.5)
        self.assertFalse(record["discarded_for_error"])

    def test_boundary_ngf_peak_is_censored_not_a_passing_three_pixel_measurement(self):
        reference = self.prepared(self.images[0])
        moving = self.prepared(self.np.roll(self.images[0], 3, axis=1))
        result = solute.audit_pair(reference, moving, self.config)
        self.assertNotEqual(result["status"], "PASS")
        self.assertTrue(any(b["peak_at_search_boundary"] for b in result["blocks"] if b["residual_px"] is not None))

    def test_dimensions_and_pair_names_fail_closed(self):
        result = solute.evaluate_development("ESM2-to-ESM1", self.series(), self.config)
        self.assertEqual(result["status"], "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE")
        with self.assertRaises(solute.SoluteRegistrationError):
            solute.evaluate_development("ESM3-to-ESM1", self.series(), self.config)

    def test_holdout_cannot_receive_an_alternative_mapping(self):
        for offset in ([1, 0], [0.0, 0], [False, 0]):
            with self.assertRaises(solute.SoluteRegistrationError):
                solute.evaluate_holdout("ESM2-to-ESM1", self.series()[:2], offset, self.config)

    def test_failed_holdout_returns_validation_block_without_new_mapping(self):
        series = self.series(lambda image: self.np.roll(image, 1, axis=1))[:2]
        result = solute.evaluate_series(series, self.config, holdout=True)
        self.assertEqual(result["status"], "BLOCKED_INTERNAL_VALIDATION")
        self.assertIsNone(result["offset"])
        self.assertFalse(result["mapping_updated"])

    def test_chroma_is_not_misclassified_as_overlay_and_geometry_is_masked(self):
        np = self.np
        y = np.full((128, 128), 128, dtype=np.uint8)
        u = np.full((64, 64), 128, dtype=np.uint8)
        v = u.copy()
        u[30:33, 30:33] = 210
        frame = solute.prepare(y.tobytes() + u.tobytes() + v.tobytes(), 128, 128, self.config)
        self.assertTrue(frame.mask[55:70, 55:70].all())
        self.assertFalse(frame.mask[0].any())
        with self.assertRaises(solute.SoluteRegistrationError):
            solute.prepare(b"invalid", 128, 128, self.config)

    def test_pair_limits_cannot_be_replaced_by_only_frame_flags(self):
        self.assertFalse(solute.metrics_pass(solute.summary([0, 0, 0, 2.3] * 3), self.config))
        self.assertTrue(solute.metrics_pass(solute.summary([0, 0, 0, 2.3]), self.config))

    def test_native_dimensions_positive_development_and_holdout_both_pairs(self):
        generator = self.np.random.default_rng(2026091902)
        for name, shape in (("ESM2-to-ESM1", (1018, 1278)), ("ESM5-to-ESM4", (1012, 1278))):
            pairs = []
            for _ in range(3):
                image = 128 + 45 * self.ndimage.gaussian_filter(generator.normal(size=shape), 1.0)
                pairs.append((self.prepared(image), self.prepared(256 - image)))
            development = solute.evaluate_development(name, pairs, self.config)
            self.assertEqual(development["status"], "PASS", name)
            holdout = solute.evaluate_holdout(name, pairs[:2], [0, 0], self.config)
            self.assertEqual(holdout["status"], "PASS", name)
            self.assertEqual(holdout["matrix"], solute.identity_matrix())

    def test_changing_only_presentation_cannot_create_temporal_discrimination(self):
        pairs = []
        for value in (32, 128, 224):
            image = self.images[0].copy()
            image[:40] = value
            image[-40:] = 256 - value
            pairs.append((self.prepared(image), self.prepared(256 - image)))
        result = solute.evaluate_series(pairs, self.config)
        self.assertEqual(result["status"], "BLOCKED_IDENTITY_NOT_DISCRIMINATIVE")
        self.assertTrue(all(abs(control["mind_margin"]) < 1e-10 for control in result["temporal_controls"]))

    def test_insufficient_audit_coverage_retains_all_measured_residual_summaries(self):
        frame = self.prepared(self.images[0])
        for retained in (7, 0):
            information = solute.image_information(frame, self.config)
            audit_blocks = [b for b in information["blocks"] if b["role"] == "audit"]
            for index, block in enumerate(audit_blocks):
                block["qualified"] = index < retained
            result = solute._comparisons(frame, [frame], 0, information, [information], "audit", self.config, {})
            self.assertEqual(result["status"], "FAIL_SUPPORT")
            self.assertEqual(result["count"], retained)
            self.assertEqual(len([b for b in result["blocks"] if b["residual_px"] is not None]), retained)
            if retained:
                self.assertIsNotNone(result["maximum_px"])
            else:
                self.assertIsNone(result["maximum_px"])


if __name__ == "__main__":
    unittest.main()
