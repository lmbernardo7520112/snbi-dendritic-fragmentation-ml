"""Numerical TI-2 registration tests; runtime arrays are synthetic only."""

from dataclasses import FrozenInstanceError
import importlib.util
import math
import unittest

from snbi_fragmentation import ti2_registration as registration


def measurements(tx=0.0, ty=0.0, *, angle=0.0, scale=1.0):
    matches = []
    for y in (40, 100, 160):
        for x in (40, 100, 160, 220):
            a, b = scale * math.cos(angle), scale * math.sin(angle)
            matches.append({
                "moving": [x, y], "reference": [a * x - b * y + tx, b * x + a * y + ty],
                "ncc": 0.95, "uniqueness": 0.3, "reverse_error_px": 0.01,
            })
    return {"status": "PASS", "matches": matches, "diagnostics": {"reference_shape_hw": [200, 260]}}


class FrozenRegistrationTests(unittest.TestCase):
    def test_minimal_identity_and_integer_class(self):
        for shift, expected in ((0, "identity"), (4, "integer_translation")):
            result = registration.fit_translation({i: measurements(shift, -shift) for i in (0, 146, 293)}, "bottom-up")
            self.assertEqual(result.transform_class, expected)
            self.assertEqual(result.matrix[0][2], shift)
            self.assertEqual(result.matrix[1][2], -shift)

    def test_parameter_freeze_and_validation_never_refits(self):
        frozen = registration.fit_translation({i: measurements(3, -2) for i in (0, 146, 293)}, "bottom-up")
        with self.assertRaises(FrozenInstanceError):
            frozen.matrix = ((1, 0, 6), (0, 1, 0), (0, 0, 1))
        result = registration.validate_registration(frozen, {73: measurements(3, -2), 219: measurements(7, -2)})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(frozen.matrix[0][2], 3)
        self.assertEqual(result["per_frame"]["73"]["status"], "PASS")
        self.assertEqual(result["per_frame"]["219"]["status"], "BLOCKED")

    def test_all_three_estimation_frames_required_and_quartiles_rejected(self):
        for indices in ((0, 146), (0, 73, 293)):
            with self.assertRaises(registration.RegistrationError):
                registration.fit_translation({i: measurements() for i in indices}, "bottom-up")

    def test_weak_or_insufficient_measurements_do_not_pass(self):
        for change in ("status", "ncc", "count"):
            frames = {i: measurements() for i in (0, 146, 293)}
            if change == "status":
                frames[146]["status"] = "BLOCKED"
            elif change == "ncc":
                frames[146]["matches"][0]["ncc"] = 0.1
            else:
                frames[146]["matches"] = frames[146]["matches"][:2]
            with self.assertRaises(registration.RegistrationError):
                registration.fit_translation(frames, "bottom-up")

    def test_rigid_and_similarity_use_estimation_only_after_simpler_failure(self):
        for scale, expected in ((1.0, "rigid"), (1.04, "similarity")):
            frames = {i: measurements(4, 2, angle=0.04, scale=scale) for i in (0, 146, 293)}
            frozen = registration.fit_registration(frames, "bottom-up")
            self.assertEqual(frozen.transform_class, expected)
            heldout = {i: measurements(4, 2, angle=0.04, scale=scale) for i in (73, 219)}
            self.assertEqual(registration.validate_registration(frozen, heldout)["status"], "PASS")

    def test_time_dependent_transform_blocks_without_averaging_away_failure(self):
        frames = {0: measurements(0), 146: measurements(4), 293: measurements(8)}
        with self.assertRaises(registration.RegistrationError):
            registration.fit_translation(frames, "bottom-up")

    def test_pooled_percentile_must_pass_in_addition_to_each_frame(self):
        frames = {i: measurements(1) for i in (0, 146, 293)}
        for frame in frames.values():
            frame["matches"][-1]["reference"][0] += 2
        # Per frame: eleven 1 px and one 3 px errors, P95 = 1.9 px.
        # Pooled: thirty-three 1 px and three 3 px errors, P95 = 3 px.
        frozen = registration.fit_translation(frames, "bottom-up")
        self.assertEqual(frozen.transform_class, "integer_translation")
        record = frozen.as_dict()
        identity = record["selection_history"][0]
        self.assertTrue(all(metric["status"] == "PASS" for metric in identity["per_frame"].values()))
        self.assertEqual(identity["aggregate"]["status"], "BLOCKED")
        self.assertEqual(identity["aggregate"]["p95_px"], 3)
        self.assertEqual(record["estimation_aggregate"]["status"], "PASS")

    def test_validation_requires_exact_frozen_indices(self):
        frozen = registration.fit_translation({i: measurements() for i in (0, 197, 394)}, "top-down")
        with self.assertRaises(registration.RegistrationError):
            registration.validate_registration(frozen, {73: measurements(), 219: measurements()})


_HAS_ARRAYS = importlib.util.find_spec("numpy") is not None and importlib.util.find_spec("scipy") is not None


@unittest.skipUnless(_HAS_ARRAYS, "optional NumPy/SciPy runtime is absent from dependency-free CI")
class SyntheticImageMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        from scipy import ndimage
        cls.np = np
        cls.ndimage = ndimage

    def texture(self):
        rng = self.np.random.default_rng(230917)
        return self.ndimage.gaussian_filter(rng.normal(size=(240, 300)), 1.4)

    def test_native_coordinates_recover_translation_and_inverted_contrast(self):
        reference = self.texture()
        moving = -2.5 * self.ndimage.shift(reference, (3, -4), order=1, mode="constant") + 17
        result = registration.pair_measurements(reference, moving)
        self.assertEqual(result["status"], "PASS", result["diagnostics"])
        offsets = [(m["reference"][0] - m["moving"][0], m["reference"][1] - m["moving"][1]) for m in result["matches"]]
        self.assertGreaterEqual(len(offsets), 12)
        self.assertLess(max(abs(x - 4) for x, _ in offsets), 0.2)
        self.assertLess(max(abs(y + 3) for _, y in offsets), 0.2)
        self.assertEqual(result["diagnostics"]["coarse_translation_xy"], [4, -3])

    def test_subpixel_correspondences_are_not_integer_rounded(self):
        reference = self.texture()
        moving = self.ndimage.shift(reference, (0.35, -2.4), order=3, mode="constant")
        result = registration.pair_measurements(reference, moving)
        self.assertEqual(result["status"], "PASS", result["diagnostics"])
        offsets = self.np.array([[m["reference"][0] - m["moving"][0], m["reference"][1] - m["moving"][1]] for m in result["matches"]])
        self.assertTrue(self.np.all(self.np.abs(self.np.median(offsets, axis=0) - [2.4, -0.35]) < 0.12))

    def test_uniform_and_periodic_content_are_ambiguous(self):
        uniform = self.np.zeros((240, 300))
        self.assertEqual(registration.pair_measurements(uniform, uniform)["status"], "BLOCKED")
        periodic = self.np.tile(self.np.sin(self.np.arange(300) * math.pi / 3), (240, 1))
        self.assertEqual(registration.pair_measurements(periodic, periodic)["status"], "BLOCKED")

    def test_masks_exclude_overlay_and_input_arrays_are_unchanged(self):
        reference = self.texture()
        moving = reference.copy()
        moving[90:130, 80:220] = 10000
        mask = self.np.ones_like(moving, dtype=bool)
        mask[87:133, 77:223] = False
        original_reference, original_moving = reference.copy(), moving.copy()
        result = registration.pair_measurements(reference, moving, moving_mask=mask)
        self.assertEqual(result["status"], "PASS", result["diagnostics"])
        for match in result["matches"]:
            x, y = (int(round(value)) for value in match["moving"])
            self.assertTrue(mask[y - 15:y + 16, x - 15:x + 16].all())
        self.assertTrue(self.np.array_equal(reference, original_reference))
        self.assertTrue(self.np.array_equal(moving, original_moving))

    def test_mismatched_dimensions_preserve_native_coordinates(self):
        reference = self.texture()
        moving = self.np.pad(reference, ((3, 3), (1, 1)), mode="constant")
        result = registration.pair_measurements(reference, moving)
        self.assertEqual(result["status"], "PASS", result["diagnostics"])
        offsets = self.np.array([[m["reference"][0] - m["moving"][0], m["reference"][1] - m["moving"][1]] for m in result["matches"]])
        self.assertTrue(self.np.all(self.np.abs(self.np.median(offsets, axis=0) - [-1, -3]) < 0.1))


if __name__ == "__main__":
    unittest.main()
