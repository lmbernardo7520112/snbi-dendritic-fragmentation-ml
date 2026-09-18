"""Deterministic synthetic fixtures only; no experimental path or source I/O."""

import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

from snbi_fragmentation import ti2r_frag_direct_registration as direct


NUMERICAL = importlib.util.find_spec("numpy") is not None and importlib.util.find_spec("scipy") is not None
CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs/registration/ti2r-frag-direct-method.json"


@unittest.skipUnless(NUMERICAL, "optional pinned NumPy/SciPy runtime unavailable")
class DirectScientificSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        from scipy import ndimage
        cls.np, cls.ndimage = np, ndimage
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        rng = np.random.default_rng(2026091802)
        cls.image = 128.0 + 45.0 * ndimage.gaussian_filter(rng.normal(size=(512, 512)), 1.0)
        cls.native_image = 128.0 + 45.0 * ndimage.gaussian_filter(rng.normal(size=(1018, 1278)), 1.0)

    def prepared(self, image, mask=None):
        if mask is None:
            mask = self.np.ones(image.shape, dtype=bool)
        return direct.prepare_luminance(image, mask, self.config)

    def pair(self, offset=(0, 0), image=None, extra=(6, 2), mask=None):
        image = self.image if image is None else image
        ox, oy = offset
        moving = self.np.pad(image, ((oy, extra[0] - oy), (ox, extra[1] - ox)), mode="edge")
        return self.prepared(image), self.prepared(moving, mask)

    def native_pair(self, offset=(0, 0), pair_name="ESM3-to-ESM1"):
        if pair_name == "ESM3-to-ESM1":
            return self.pair(offset, self.native_image)
        return self.pair(offset, self.native_image[:1012], extra=(0, 2))

    def test_exact_candidate_sets_and_direction(self):
        self.assertEqual(len(direct.candidates("ESM3-to-ESM1")), 21)
        self.assertEqual(len(direct.candidates("ESM6-to-ESM4")), 3)
        self.assertIn((0, 0), direct.candidates("ESM3-to-ESM1"))
        matrix, inverse = direct.mapping((2, 6))
        self.assertEqual(matrix, [[1, 0, -2], [0, 1, -6], [0, 0, 1]])
        self.np.testing.assert_array_equal(self.np.asarray(matrix) @ inverse, self.np.eye(3))

    def test_all_twenty_four_offsets_uniquely_recovered(self):
        for name, extra in (("ESM3-to-ESM1", (6, 2)), ("ESM6-to-ESM4", (0, 2))):
            for offset in direct.candidates(name):
                reference, moving = self.pair(offset, extra=extra)
                result = direct.select_candidate(reference, moving, direct.candidates(name), self.config)
                self.assertEqual(result["status"], "PASS", (name, offset, result))
                self.assertEqual(result["winner"], list(offset))
                self.assertGreaterEqual(result["margin"], self.config["uniqueness_margin"])

    def test_native_dimensions_and_unknown_pairs_fail_closed(self):
        pair = self.pair()
        result = direct.evaluate_development("ESM3-to-ESM1", [pair] * 3, self.config)
        self.assertEqual(result["status"], "BLOCKED_DIMENSION_DIVERGENCE")
        with self.assertRaises(direct.DirectRegistrationError):
            direct.candidates("ESM2-to-ESM1")

    def test_native_identity_static_mapping_certifies_development(self):
        result = direct.evaluate_development("ESM3-to-ESM1", [self.native_pair()] * 3, self.config)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["offset"], [0, 0])
        self.assertEqual(result["identifiable_frames"], [0, 1, 2])
        self.assertLessEqual(result["aggregate"]["maximum_px"], 0.01)

    def test_native_nonzero_offsets_pass_both_pairs(self):
        for name, offset in (("ESM3-to-ESM1", (2, 6)), ("ESM6-to-ESM4", (2, 0))):
            result = direct.evaluate_development(name, [self.native_pair(offset, name)] * 3, self.config)
            self.assertEqual(result["status"], "PASS", name)
            self.assertEqual(result["offset"], list(offset))

    def test_partial_masks_are_accepted_without_full_tile_or_global_fraction(self):
        reference, moving = self.pair((1, 3))
        mask = self.np.ones(moving.luminance.shape, dtype=bool)
        mask[::11, ::9] = False
        moving = self.prepared(moving.luminance, mask)
        result = direct.evaluate_frame(reference, moving, direct.candidates("ESM3-to-ESM1"), self.config)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["winner"], [1, 3])
        self.assertTrue(any(block["valid_pixels"] < block["area_pixels"] for block in result["audit"]["blocks"]))

    def test_identifiability_depends_exclusively_on_reference(self):
        reference, moving = self.pair()
        flat = self.prepared(self.np.full(moving.luminance.shape, 128.0))
        bad_mask = self.prepared(moving.luminance, self.np.zeros(moving.luminance.shape, dtype=bool))
        outputs = [direct.evaluate_frame(reference, m, direct.candidates("ESM3-to-ESM1"), self.config) for m in (moving, flat, bad_mask)]
        self.assertTrue(all(item["classification"] == "IDENTIFIABLE" for item in outputs))
        self.assertEqual(outputs[0]["reference_information"], outputs[1]["reference_information"])
        self.assertEqual(outputs[1]["reference_information"], outputs[2]["reference_information"])
        self.assertEqual(outputs[0]["status"], "PASS")
        self.assertNotEqual(outputs[1]["status"], "PASS")
        self.assertNotEqual(outputs[2]["status"], "PASS")

    def test_nonidentifiable_initial_allows_two_informative_development_times(self):
        flat = self.pair(image=self.np.full(self.native_image.shape, 128.0))
        good = self.native_pair()
        result = direct.evaluate_development("ESM3-to-ESM1", [flat, good, good], self.config)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["non_identifiable_frames"], [0])
        self.assertIsNone(result["per_frame"][0]["winner"])

    def test_only_one_informative_development_time_is_insufficient(self):
        flat = self.pair(image=self.np.full(self.native_image.shape, 128.0))
        result = direct.evaluate_development("ESM3-to-ESM1", [flat, flat, self.native_pair()], self.config)
        self.assertEqual(result["status"], "BLOCKED_REFERENCE_STILL_INSUFFICIENT")
        self.assertIsNone(result["offset"])

    def test_flat_or_aperture_reference_is_nonidentifiable(self):
        yy, xx = self.np.indices(self.image.shape)
        for values in (self.np.full(self.image.shape, 128.0), 128 + 20 * self.np.sin(xx / 8)):
            reference, moving = self.pair(image=values)
            result = direct.evaluate_frame(reference, moving, direct.candidates("ESM3-to-ESM1"), self.config)
            self.assertEqual(result["classification"], "NON_IDENTIFIABLE")
            self.assertNotEqual(result["status"], "PASS")

    def test_periodic_reference_cannot_produce_unique_mapping(self):
        yy, xx = self.np.indices(self.image.shape)
        periodic = 128 + 20 * self.np.cos(self.np.pi * xx) + 20 * self.np.cos(self.np.pi * yy / 2)
        reference, moving = self.pair(image=periodic)
        result = direct.evaluate_frame(reference, moving, direct.candidates("ESM3-to-ESM1"), self.config)
        self.assertNotEqual(result["status"], "PASS")

    def test_period_larger_than_candidate_set_has_ambiguous_audit(self):
        yy, xx = self.np.indices(self.image.shape)
        periodic = 128 + 20 * self.np.cos(2 * self.np.pi * xx / 8) + 20 * self.np.sin(2 * self.np.pi * yy / 10)
        reference, moving = self.pair(image=periodic)
        selection = direct.select_candidate(reference, moving, direct.candidates("ESM3-to-ESM1"), self.config)
        self.assertEqual(selection["status"], "PASS")
        audit = direct.audit_offset(reference, moving, (0, 0), self.config)
        self.assertEqual(audit["status"], "FAIL_AUDIT_CORRELATION")
        self.assertTrue(any(block["status"] == "FAIL_AMBIGUOUS_CORRELATION" for block in audit["blocks"]))

    def test_unrelated_images_and_shared_mask_cannot_fake_identity(self):
        reference, moving = self.pair()
        unrelated = 128 + 45 * self.ndimage.gaussian_filter(self.np.random.default_rng(7721).normal(size=moving.luminance.shape), 1)
        mask = self.np.ones(reference.luminance.shape, dtype=bool)
        mask[::13, ::7] = False
        moving_mask = self.np.ones(moving.luminance.shape, dtype=bool)
        moving_mask[:512, :512] = mask
        reference = self.prepared(reference.luminance, mask)
        moving = self.prepared(unrelated, moving_mask)
        result = direct.evaluate_frame(reference, moving, direct.candidates("ESM3-to-ESM1"), self.config)
        self.assertEqual(result["classification"], "IDENTIFIABLE")
        self.assertNotEqual(result["status"], "PASS")
        audit = direct.audit_offset(reference, moving, (0, 0), self.config)
        self.assertNotEqual(audit["status"], "PASS")
        self.assertTrue(audit["maximum_px"] is None or audit["maximum_px"] > 3)

    def test_same_candidate_pixels_and_audit_are_disjoint(self):
        reference, moving = self.pair()
        result = direct.select_candidate(reference, moving, direct.candidates("ESM3-to-ESM1"), self.config)
        self.assertEqual(len({entry["sample_count"] for entry in result["candidate_scores"]}), 1)
        blocks = direct.blocks(reference.luminance.shape, self.config)
        selection = [b for b in blocks if b["role"] == "selection"]
        audit = [b for b in blocks if b["role"] == "audit"]
        envelope = self.config["audit_lag_radius_px"] + 6 + 1
        for first in selection:
            a, b, c, d = first["xyxy"]
            for second in audit:
                x, y, z, w = second["xyxy"]
                self.assertTrue(c + envelope <= x or z + envelope <= a or d + envelope <= y or w + envelope <= b)

    def test_high_audit_residual_is_preserved_and_blocks_frame(self):
        reference, moving = self.pair()
        changed = moving.luminance.copy()
        block = next(b for b in direct.blocks(reference.luminance.shape, self.config) if b["role"] == "audit")
        x0, y0, x1, y1 = block["xyxy"]
        pad = self.config["audit_lag_radius_px"]
        changed[y0-pad:y1+pad, x0-pad:x1+pad] = self.np.roll(changed[y0-pad:y1+pad, x0-pad:x1+pad], 5, axis=1)
        result = direct.evaluate_frame(reference, self.prepared(changed), direct.candidates("ESM3-to-ESM1"), self.config)
        self.assertEqual(result["winner"], [0, 0])
        self.assertNotEqual(result["status"], "PASS")
        self.assertGreater(result["audit"]["maximum_px"], 3)
        record = next(b for b in result["audit"]["blocks"] if b["id"] == block["id"])
        self.assertGreater(record["residual_px"], 3)

    def test_mask_holes_do_not_shift_the_measured_audit_residual(self):
        reference, moving = self.pair()
        shifted = self.np.roll(moving.luminance, 5, axis=1)
        mask = self.np.ones(shifted.shape, dtype=bool)
        mask[::17, ::11] = False
        moving = self.prepared(shifted, mask)
        audit = direct.audit_offset(reference, moving, (0, 0), self.config)
        self.assertEqual(audit["status"], "FAIL_AUDIT_METRICS")
        self.assertGreater(audit["median_px"], 4.5)
        self.assertLess(audit["median_px"], 5.5)

    def test_nonzero_constant_audit_patch_is_explicitly_undefined(self):
        reference, moving = self.pair()
        block = next(b for b in direct.blocks(reference.luminance.shape, self.config) if b["role"] == "audit")
        x0, y0, x1, y1 = block["xyxy"]
        pad = self.config["audit_lag_radius_px"]
        for constant in (64.0, 100.0, 200.0):
            changed = moving.luminance.copy()
            changed[y0-pad:y1+pad, x0-pad:x1+pad] = constant
            result = direct.evaluate_frame(reference, self.prepared(changed), direct.candidates("ESM3-to-ESM1"), self.config)
            self.assertEqual(result["classification"], "IDENTIFIABLE")
            self.assertEqual(result["winner"], [0, 0])
            self.assertEqual(result["status"], "FAIL_AUDIT_CORRELATION")
            record = next(b for b in result["audit"]["blocks"] if b["id"] == block["id"])
            self.assertEqual(record["status"], "FAIL_UNDEFINED_CORRELATION")
            self.assertIsNone(record["residual_px"])

    def test_temporal_disagreement_is_not_averaged_away(self):
        result = direct.evaluate_development("ESM3-to-ESM1", [self.native_pair(), self.native_pair(), self.native_pair((1, 0))], self.config)
        self.assertEqual(result["status"], "BLOCKED_DIRECT_MAPPING")
        self.assertIsNone(result["offset"])

    def test_holdout_confirms_frozen_offset_without_refitting(self):
        pair = self.native_pair((2, 6))
        result = direct.evaluate_holdout("ESM3-to-ESM1", [pair, pair], [2, 6], self.config)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["offset"], [2, 6])
        self.assertFalse(result["offset_changed"])

    def test_holdout_different_winner_does_not_change_offset(self):
        result = direct.evaluate_holdout("ESM3-to-ESM1", [self.native_pair((1, 0))] * 2, [0, 0], self.config)
        self.assertEqual(result["status"], "BLOCKED_DIRECT_MAPPING")
        self.assertEqual(result["frozen_offset"], [0, 0])
        self.assertIsNone(result["offset"])

    def test_holdout_audit_always_applies_frozen_offset_even_when_contradicted(self):
        with mock.patch.object(direct, "audit_offset", wraps=direct.audit_offset) as audit:
            result = direct.evaluate_holdout("ESM3-to-ESM1", [self.native_pair((1, 0))] * 2, [0, 0], self.config)
        self.assertEqual(result["status"], "BLOCKED_DIRECT_MAPPING")
        self.assertEqual(audit.call_count, 2)
        self.assertTrue(all(call.args[2] == [0, 0] for call in audit.call_args_list))
        self.assertTrue(all(frame["applied_offset"] == [0, 0] for frame in result["per_frame"]))

    def test_pair_aggregate_limits_cannot_be_bypassed_by_frame_pass_flags(self):
        frame = {"classification": "IDENTIFIABLE", "status": "PASS", "winner": [0, 0],
                 "audit": {"blocks": [{"residual_px": 0.0}, {"residual_px": 2.1}]}}
        # Each two-point frame has interpolated P95=1.995; their pooled P95
        # is 2.1, demonstrating why the pair-level gate must also be checked.
        with mock.patch.object(direct, "evaluate_frame", return_value=frame):
            result = direct.evaluate_development("ESM3-to-ESM1", [self.native_pair()] * 3, self.config)
        self.assertEqual(result["status"], "BLOCKED_DIRECT_MAPPING")
        self.assertGreater(result["aggregate"]["p95_px"], self.config["p95_limit_px"])

    def test_holdout_requires_at_least_one_informative_time(self):
        flat = self.pair(image=self.np.full(self.native_image.shape, 128.0))
        passed = direct.evaluate_holdout("ESM3-to-ESM1", [flat, self.native_pair()], [0, 0], self.config)
        blocked = direct.evaluate_holdout("ESM3-to-ESM1", [flat, flat], [0, 0], self.config)
        self.assertEqual(passed["status"], "PASS")
        self.assertEqual(blocked["status"], "BLOCKED_REFERENCE_STILL_INSUFFICIENT")

    def test_noninteger_or_outside_finite_offset_is_rejected(self):
        for offset in ([0.5, 0], [-1, 0], [3, 0], [True, 0]):
            with self.assertRaises(direct.DirectRegistrationError):
                direct.evaluate_holdout("ESM3-to-ESM1", [self.native_pair()] * 2, offset, self.config)

    def test_chroma_halo_text_and_border_exclusion(self):
        np = self.np
        y = np.full((128, 128), 120, dtype=np.uint8)
        u = np.full((64, 64), 128, dtype=np.uint8)
        v = u.copy()
        u[30:33, 30:33] = 210
        frame = direct.prepare(y.tobytes() + u.tobytes() + v.tobytes(), 128, 128, self.config)
        self.assertFalse(frame.mask[60:66, 60:66].any())
        self.assertFalse(frame.mask[55, 61])
        self.assertFalse(frame.mask[0].any())
        self.assertTrue(frame.mask[45, 45])
        with self.assertRaises(direct.DirectRegistrationError):
            direct.prepare(b"invalid", 128, 128, self.config)

    def test_audit_subpixel_estimate_never_changes_integer_mapping(self):
        reference, moving = self.pair()
        shifted = self.ndimage.shift(moving.luminance, (0, 3.4), order=1, mode="nearest", prefilter=False)
        audit = direct.audit_offset(reference, self.prepared(shifted), (0, 0), self.config)
        self.assertGreater(audit["median_px"], 3)
        self.assertEqual(audit["status"], "FAIL_AUDIT_METRICS")
        matrix, _ = direct.mapping((0, 0))
        self.assertEqual(matrix, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])


if __name__ == "__main__":
    unittest.main()
