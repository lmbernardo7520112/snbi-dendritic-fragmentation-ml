"""Synthetic equivalence of new D admission and unchanged historical support."""

import copy
import importlib.util
import unittest
from unittest import mock

from snbi_fragmentation import ti3_support as structural_legacy
from snbi_fragmentation import ti3b_ablation as solutal_legacy
from snbi_fragmentation import ti3d_support as support


NUMERICAL = all(importlib.util.find_spec(name) is not None
                for name in ("numpy", "scipy", "skimage", "sklearn"))


def metadata(source="ESM1", frame=73, split="TRAIN"):
    width, height = (1278, 1018) if source in ("ESM1", "ESM2") else (1278, 1012)
    return {"source_id": source, "frame_index": frame, "split": split,
            "width": width, "height": height, "pixel_format": "yuv420p", "bit_depth": 8,
            "frame_bytes": width * height * 3 // 2,
            "acquisition_id": "bottom_up_anti_parallel" if source in ("ESM1", "ESM2") else "top_down_parallel"}


def sample(image, x=200, y=300, sample_id="synthetic-patch"):
    return {key: image[key] for key in ("frame_index", "split", "width", "height", "acquisition_id")} | {
        "source_id": support.STRUCTURAL_SOURCE.get(image["source_id"], image["source_id"]),
        "sample_id": sample_id, "center_x": x, "center_y": y,
        "patch_radius_px": 32, "patch_side_px": 65, "mapping_offset_xy": [0, 0],
        "patch_xyxy": [x - 32, y - 32, x + 33, y + 33]}


class BufferTrap:
    def __len__(self):
        raise AssertionError("forbidden buffer inspected")

    def __getitem__(self, key):
        raise AssertionError("forbidden buffer indexed")


class FinalSupportMetadataTests(unittest.TestCase):
    def test_allowlist_is_exactly_ten_training_four_final_and_preserves_splits(self):
        self.assertEqual(len(support.ALLOWED_FRAMES), 14)
        for source, frame in sorted(support.ALLOWED_FRAMES):
            structural = support.STRUCTURAL_SOURCE[source]
            split = support.FRAME_SPLITS[(structural, frame)]
            image = metadata(source, frame, split)
            self.assertEqual(support._metadata(image, [sample(image)])[:2], (image["width"], image["height"]))
        self.assertEqual(sum(frame in (293, 295) for _, frame in support.ALLOWED_FRAMES), 4)

    def test_forbidden_or_spoofed_metadata_deny_before_any_buffer_inspection(self):
        image = metadata("ESM1", 293, "FINAL_TEST")
        cases = [(image | {"source_id": "ESM3"}, [sample(image)]),
                 (image | {"frame_index": 0}, [sample(image)]),
                 (image | {"frame_index": True}, [sample(image)]),
                 (image | {"split": "TRAIN"}, [sample(image)]),
                 (image | {"bit_depth": 8.0}, [sample(image)]),
                 (image | {"width": 1278.0}, [sample(image)]),
                 (image, [sample(image) | {"split": "TRAIN"}]),
                 (image, [sample(image) | {"mapping_offset_xy": [1, 0]}]),
                 (image, [sample(image) | {"frame_index": 219}]),
                 (image, [sample(image), sample(image)]),
                 (image, [])]
        for changed, samples in cases:
            with mock.patch.object(support, "_scientific_runtime") as runtime:
                with self.assertRaises(support.FinalSupportError):
                    support.checked_luminance(BufferTrap(), changed, samples)
                runtime.assert_not_called()

    def test_incomplete_or_mutable_native_buffer_denied_without_runtime(self):
        image = metadata("ESM2", 293, "FINAL_TEST")
        for raw in (b"", bytearray(image["frame_bytes"]), memoryview(b""), BufferTrap()):
            with mock.patch.object(support, "_scientific_runtime") as runtime:
                with self.assertRaises(support.FinalSupportError):
                    support.checked_luminance(raw, image, [sample(image)])
                runtime.assert_not_called()

    def test_single_invalid_final_sample_blocks_batch_without_moving_or_replacing(self):
        image = metadata("ESM1", 293, "FINAL_TEST")
        samples = [sample(image, sample_id="valid"), sample(image, x=36, sample_id="invalid")]
        original = copy.deepcopy(samples)
        with mock.patch.object(support, "_scientific_runtime") as runtime:
            with self.assertRaises(support.FinalSupportError) as failure:
                support.checked_luminance(BufferTrap(), image, samples)
            self.assertEqual(failure.exception.code, "BLOCKED_FINAL_SUPPORT")
            runtime.assert_not_called()
        self.assertEqual(samples, original)


@unittest.skipUnless(NUMERICAL, "optional pinned scientific dependencies unavailable")
class FinalSupportSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.np = np

    def native_bytes(self, image, chroma=None, uv=(128, 128)):
        np = self.np
        width, height = image["width"], image["height"]
        y = (np.arange(width * height, dtype=np.uint32) % 251).astype(np.uint8).reshape(height, width)
        u = np.full((height // 2, width // 2), uv[0], dtype=np.uint8)
        v = np.full((height // 2, width // 2), uv[1], dtype=np.uint8)
        if chroma is not None:
            plane, x, row, value = chroma
            (u if plane == "U" else v)[row // 2, x // 2] = value
        return y.tobytes() + u.tobytes() + v.tobytes(), y

    def test_all_four_final_sources_return_original_luminance_and_exact_patch(self):
        np = self.np
        for source, frame in (("ESM1", 293), ("ESM2", 293), ("ESM4", 295), ("ESM5", 295)):
            image = metadata(source, frame, "FINAL_TEST")
            raw, expected = self.native_bytes(image)
            original_sample = sample(image)
            y, report = support.checked_luminance(raw, image, [original_sample])
            np.testing.assert_array_equal(y, expected)
            self.assertFalse(y.flags.writeable)
            self.assertTrue(np.shares_memory(y, np.frombuffer(raw, dtype=np.uint8)))
            self.assertEqual(report["original_split"], "FINAL_TEST")
            patch = support.extract_authorized_patch(y, image, original_sample)
            np.testing.assert_array_equal(patch, expected[268:333, 168:233])
            self.assertEqual(patch.shape, (65, 65))
            self.assertFalse(np.shares_memory(patch, y))
            self.assertEqual(original_sample["split"], "FINAL_TEST")

    def test_structural_predicate_matches_legacy_threshold_halo_and_erosion(self):
        np = self.np
        image = metadata()
        configurations = (
            (None, 200, True), (("U", 200, 300, 147), 200, True),
            (("U", 200, 300, 148), 200, False), (("V", 200, 300, 109), 200, True),
            (("V", 200, 300, 108), 200, False),
            (("U", 166, 300, 148), 206, True), (("U", 166, 300, 148), 205, False),
        )
        for chroma, x, expected_pass in configurations:
            raw, _ = self.native_bytes(image, chroma)
            samples = [sample(image, x=x)]
            if expected_pass:
                old, _ = structural_legacy.checked_native_luminance(raw, image, samples)
                new, _ = support.checked_luminance(raw, image, samples)
                np.testing.assert_array_equal(old, new)
            else:
                with self.assertRaises(structural_legacy.SupportContractError):
                    structural_legacy.checked_native_luminance(raw, image, samples)
                with self.assertRaises(support.FinalSupportError):
                    support.checked_luminance(raw, image, samples)

    def test_final_chroma_failure_is_terminal_and_never_salvages_other_patch(self):
        image = metadata("ESM4", 295, "FINAL_TEST")
        raw, _ = self.native_bytes(image, ("V", 166, 300, 108))
        samples = [sample(image, x=206, sample_id="valid"), sample(image, x=205, sample_id="invalid")]
        before = copy.deepcopy(samples)
        with self.assertRaises(support.FinalSupportError) as failure:
            support.checked_luminance(raw, image, samples)
        self.assertEqual(failure.exception.code, "BLOCKED_FINAL_SUPPORT")
        self.assertEqual(samples, before)

    def test_solutal_geometry_matches_legacy_and_never_excludes_color_field(self):
        np = self.np
        image = metadata("ESM2", 73, "TRAIN")
        for uv in ((128, 128), (0, 255), (255, 0)):
            raw, _ = self.native_bytes(image, uv=uv)
            samples = [sample(image, x=37, y=156)]
            old, old_report = solutal_legacy.checked_solutal_luminance(raw, image, samples)
            new, new_report = support.checked_luminance(raw, image, samples)
            np.testing.assert_array_equal(old, new)
            self.assertEqual(new_report["support_contract"], old_report["support_contract"])
            np.testing.assert_array_equal(
                solutal_legacy.extract_solutal_patch(old, image, samples[0]),
                support.extract_authorized_patch(new, image, samples[0]))
        for x, y in ((36, 300), (1241, 300), (200, 155), (200, 832)):
            with self.assertRaises(solutal_legacy.AblationContractError):
                solutal_legacy.checked_solutal_luminance(raw, image, [sample(image, x, y)])
            with self.assertRaises(support.FinalSupportError):
                support.checked_luminance(raw, image, [sample(image, x, y)])

    def test_final_patch_type_shape_and_geometry_cannot_be_changed(self):
        np = self.np
        image = metadata("ESM1", 293, "FINAL_TEST")
        for array in (np.zeros((1018, 1278), dtype=float), np.zeros((1012, 1278), dtype=np.uint8),
                      np.zeros((1018, 1278, 3), dtype=np.uint8), BufferTrap()):
            with self.assertRaises(support.FinalSupportError):
                support.extract_authorized_patch(array, image, sample(image))
        raw, _ = self.native_bytes(image)
        y, _ = support.checked_luminance(raw, image, [sample(image)])
        for changes in ({"patch_side_px": 63}, {"center_x": 200.0},
                        {"patch_xyxy": [168, 268, 233, 332]}, {"mapping_offset_xy": [0, 1]}):
            with self.assertRaises(support.FinalSupportError):
                support.extract_authorized_patch(y, image, sample(image) | changes)


if __name__ == "__main__":
    unittest.main()
