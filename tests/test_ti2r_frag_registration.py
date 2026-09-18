"""Only deterministic in-memory fixtures; no experimental I/O."""

import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

from snbi_fragmentation import ti2r_frag_registration as registration


NUMERICAL = importlib.util.find_spec("numpy") is not None and importlib.util.find_spec("scipy") is not None
CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs/registration/ti2r-frag-method.json"


@unittest.skipUnless(NUMERICAL, "optional pinned NumPy/SciPy runtime unavailable")
class FragScientificSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        from scipy import ndimage
        cls.np, cls.ndimage = np, ndimage
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        cls.shape = (512, 512)
        rng = np.random.default_rng(20260918)
        cls.image = 128.0 + 45.0 * ndimage.gaussian_filter(rng.normal(size=cls.shape), 1.1)

    def prepared(self, image):
        return registration.prepare_luminance(image, self.np.ones(image.shape, dtype=bool), self.config)

    def pairs(self, matrix):
        np = self.np
        yy, xx = np.indices(self.shape, dtype=float)
        moving = self.ndimage.map_coordinates(self.image, [matrix[1, 0] * xx + matrix[1, 1] * yy + matrix[1, 2], matrix[0, 0] * xx + matrix[0, 1] * yy + matrix[0, 2]], order=1, mode="nearest", prefilter=False)
        # Distinct synthetic photometric conditions share one static geometry.
        return [(self.prepared(self.image * factor), self.prepared(moving * factor + offset)) for factor, offset in ((1.0, 0.0), (0.9, 4.0), (1.1, -3.0))]

    def test_identity_stops_before_fitting(self):
        with mock.patch.object(registration, "_fit_model", side_effect=AssertionError("identity PASS must stop")):
            result = registration.fit_pair(self.pairs(self.np.eye(3)), self.config)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["selected_model"], "M0_IDENTITY")
        self.assertEqual(len(result["models_tested"]), 1)
        self.assertEqual(result["development"]["aggregate"]["count"], 48)

    def test_translation_recovered_from_joint_development(self):
        matrix = self.np.eye(3)
        matrix[:2, 2] = [4.0, -2.0]
        result = registration.fit_pair(self.pairs(matrix), self.config)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["selected_model"], "M1_TRANSLATION")
        self.np.testing.assert_allclose(result["matrix"], matrix, atol=0.25)

    def test_rigid_recovered_without_affine(self):
        matrix = registration._matrix_for("M2_RIGID", [1.3, 0.0, 0.0], self.shape)
        result = registration.fit_pair(self.pairs(matrix), self.config)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["selected_model"], "M2_RIGID")
        self.assertEqual([m["model"] for m in result["models_tested"]], list(registration.MODEL_ORDER[:3]))

    def test_affine_recovered_after_simpler_models_fail(self):
        matrix = registration._matrix_for("M3_AFFINE", [2.2, 0.0, 0.0, -2.2, 0.0, 0.0], self.shape)
        result = registration.fit_pair(self.pairs(matrix), self.config)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["selected_model"], "M3_AFFINE")
        self.assertEqual([m["model"] for m in result["models_tested"]], list(registration.MODEL_ORDER))

    def test_overlay_chroma_and_halo_excluded(self):
        np = self.np
        size = 128
        y = np.full((size, size), 120, dtype=np.uint8)
        u = np.full((size // 2, size // 2), 128, dtype=np.uint8)
        v = u.copy()
        u[30:33, 30:33] = 210
        frame = registration.prepare(y.tobytes() + u.tobytes() + v.tobytes(), size, size, self.config)
        self.assertFalse(frame.mask[60:66, 60:66].any())
        self.assertFalse(frame.mask[55, 61])
        self.assertTrue(frame.mask[45, 45])

    def test_reflection_rejected_before_metrics(self):
        matrix = self.np.eye(3)
        matrix[0, 0] = -1
        with self.assertRaisesRegex(registration.FragRegistrationError, "reflection"):
            registration.evaluate_pair(self.pairs(self.np.eye(3)), matrix, self.config)

    def test_reserved_tiles_and_motion_halo_disjoint_from_fit(self):
        region = registration.fitting_region(self.shape, self.shape, self.config)
        for tile in registration.evaluation_tiles(self.shape, self.config):
            x0, y0, x1, y1 = tile["xyxy"]
            self.assertFalse(region[y0 - 34:y1 + 34, x0 - 34:x1 + 34].any())
        self.assertGreater(int(region.sum()), 256)

    def test_large_residuals_preserved_and_frame_failure_not_pooled_away(self):
        identity = self.pairs(self.np.eye(3))[0]
        matrix = self.np.eye(3)
        matrix[:2, 2] = [5.0, 0.0]
        shifted = self.pairs(matrix)[0]
        result = registration.evaluate_pair([identity, identity, shifted], self.np.eye(3), self.config)
        self.assertEqual(result["status"], "FAIL_ABSOLUTE_CRITERION")
        self.assertEqual(result["per_frame"][2]["valid_tiles"], 16)
        self.assertGreater(result["per_frame"][2]["maximum_px"], 3.0)
        self.assertEqual(result["aggregate"]["count"], 48)

    def test_reference_texture_failure_is_blocking(self):
        flat = self.prepared(self.np.full(self.shape, 128.0))
        result = registration.fit_pair([(flat, flat)] * 3, self.config)
        self.assertEqual(result["status"], "BLOCKED_REFERENCE_INSUFFICIENT")
        self.assertEqual(len(result["models_tested"]), 1)

    def test_constant_moving_cannot_fake_zero_residual(self):
        reference = self.prepared(self.image)
        flat = self.prepared(self.np.full(self.shape, 128.0))
        result = registration.evaluate_pair([(reference, flat)] * 3, self.np.eye(3), self.config)
        self.assertEqual(result["status"], "BLOCKED_REFERENCE_INSUFFICIENT")
        self.assertEqual(result["aggregate"]["count"], 0)

    def test_periodic_or_aperture_ambiguous_reference_blocked(self):
        yy, xx = self.np.indices(self.shape)
        for values in (128 + 20 * self.np.sin(xx * self.np.pi / 4), 128 + 20 * ((xx + yy) % 2)):
            frame = self.prepared(values)
            result = registration.evaluate_pair([(frame, frame)] * 3, self.np.eye(3), self.config)
            self.assertEqual(result["status"], "BLOCKED_REFERENCE_INSUFFICIENT")

    def test_unrelated_content_cannot_certify_identity(self):
        unrelated = 128 + 45 * self.ndimage.gaussian_filter(self.np.random.default_rng(931).normal(size=self.shape), 1.1)
        result = registration.evaluate_pair([(self.prepared(self.image), self.prepared(unrelated))] * 3, self.np.eye(3), self.config)
        self.assertEqual(result["status"], "FAIL_ABSOLUTE_CRITERION")
        self.assertEqual(result["aggregate"]["count"], 48)

    def test_mask_holes_never_become_alignment_fiducials(self):
        reference = self.prepared(self.image)
        mask = self.np.ones(self.shape, dtype=bool)
        for tile in registration.evaluation_tiles(self.shape, self.config):
            x0, y0, _, _ = tile["xyxy"]
            mask[y0 + 7, x0 + 7] = False
        moving = registration.prepare_luminance(self.image, mask, self.config)
        result = registration.evaluate_pair([(reference, moving)] * 3, self.np.eye(3), self.config)
        self.assertEqual(result["status"], "BLOCKED_REFERENCE_INSUFFICIENT")
        self.assertEqual(result["aggregate"]["count"], 0)

    def test_validation_never_fits_and_requires_two_times(self):
        pairs = self.pairs(self.np.eye(3))
        with mock.patch.object(registration, "_fit_model", side_effect=AssertionError("validation never fits")):
            result = registration.validate_pair(pairs[:2], self.np.eye(3), self.config)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["refit_performed"])
        with self.assertRaises(registration.FragRegistrationError):
            registration.validate_pair(pairs, self.np.eye(3), self.config)

    def test_exact_hierarchy_is_enforced(self):
        config = dict(self.config, model_order=list(reversed(registration.MODEL_ORDER)))
        with self.assertRaises(registration.FragRegistrationError):
            registration.fit_pair(self.pairs(self.np.eye(3)), config)

    def test_native_buffer_shape_and_motion_envelope_rejected(self):
        with self.assertRaises(registration.FragRegistrationError):
            registration.prepare(b"invalid", 128, 128, self.config)
        matrix = self.np.eye(3)
        matrix[0, 2] = 33
        with self.assertRaisesRegex(registration.FragRegistrationError, "motion envelope"):
            registration.checked_matrix(matrix, self.shape, self.config)


if __name__ == "__main__":
    unittest.main()
