"""Synthetic native byte fixtures and pre-buffer denial; no experimental I/O."""

import importlib.util
import unittest
from unittest import mock

from snbi_fragmentation import ti3_support as support


NUMERICAL = all(importlib.util.find_spec(name) is not None
                for name in ("numpy", "scipy", "skimage", "sklearn"))


def metadata(source="ESM1", frame=73, split="TRAIN"):
    width, height = (1278, 1018) if source == "ESM1" else (1278, 1012)
    return {"source_id": source, "frame_index": frame, "split": split,
            "width": width, "height": height, "pixel_format": "yuv420p", "bit_depth": 8,
            "frame_bytes": width * height * 3 // 2,
            "acquisition_id": "bottom_up_anti_parallel" if source == "ESM1" else "top_down_parallel"}


def sample(image, x=200, y=300, sample_id="synthetic-patch"):
    return {key: image[key] for key in (
        "source_id", "frame_index", "split", "width", "height", "acquisition_id")} | {
        "sample_id": sample_id, "center_x": x, "center_y": y,
        "patch_radius_px": 32, "patch_side_px": 65,
        "patch_xyxy": [x - 32, y - 32, x + 33, y + 33]}


class BufferTrap:
    def __len__(self):
        raise AssertionError("prohibited buffer was examined")

    def __getitem__(self, key):
        raise AssertionError("prohibited buffer was indexed")


class SupportPreBufferTests(unittest.TestCase):
    def test_forbidden_source_frame_split_and_sample_deny_before_buffer_runtime(self):
        cases = []
        for source, frame, split in (("ESM1", 293, "FINAL_TEST"), ("ESM4", 295, "FINAL_TEST"),
                                     ("ESM2", 73, "TRAIN"), ("ESM3", 73, "TRAIN"),
                                     ("ESM1", 0, "TRAIN"), ("ESM1", 73, "FINAL_TEST")):
            image = metadata(source, frame, split)
            cases.append((image, [sample(image)]))
        image = metadata()
        wrong_sample = sample(image)
        wrong_sample["split"] = "FINAL_TEST"
        cases.append((image, [wrong_sample]))
        for image, samples in cases:
            with self.subTest(image=image), mock.patch.object(support, "_scientific_runtime") as runtime:
                with self.assertRaises(support.SupportContractError):
                    support.checked_native_luminance(BufferTrap(), image, samples)
                runtime.assert_not_called()

    def test_native_byte_type_count_dimensions_and_geometric_support_fail_closed(self):
        image = metadata()
        cases = [(bytearray(image["frame_bytes"]), image, [sample(image)]),
                 (b"", image, [sample(image)]),
                 (BufferTrap(), image | {"width": 1280}, [sample(image)]),
                 (BufferTrap(), image, [sample(image, x=36, y=156)])]
        for raw, image, samples in cases:
            with self.subTest(raw_type=type(raw).__name__), mock.patch.object(support, "_scientific_runtime") as runtime:
                with self.assertRaises(support.SupportContractError):
                    support.checked_native_luminance(raw, image, samples)
                runtime.assert_not_called()


@unittest.skipUnless(NUMERICAL, "optional pinned scientific dependencies unavailable")
class SupportSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.np = np

    def native_bytes(self, image, chroma=None):
        np = self.np
        width, height = image["width"], image["height"]
        luminance = (np.arange(width * height, dtype=np.uint32) % 251).astype(np.uint8).reshape(height, width)
        u = np.full((height // 2, width // 2), 128, dtype=np.uint8)
        v = u.copy()
        if chroma is not None:
            plane, x, y, value = chroma
            (u if plane == "U" else v)[y // 2, x // 2] = value
        return luminance.tobytes() + u.tobytes() + v.tobytes(), luminance

    def test_native_luminance_is_unchanged_read_only_uint8_for_both_sources(self):
        np = self.np
        for image in (metadata(), metadata("ESM4", 197, "DEVELOPMENT")):
            raw, expected = self.native_bytes(image)
            output, report = support.checked_native_luminance(raw, image, [sample(image)])
            np.testing.assert_array_equal(output, expected)
            self.assertEqual(output.dtype, np.dtype("uint8"))
            self.assertFalse(output.flags.writeable)
            self.assertTrue(np.shares_memory(output, np.frombuffer(raw, dtype=np.uint8)))
            self.assertEqual(report, {"status": "PASS", "sample_count": 1,
                                      "samples_checked": ["synthetic-patch"]})

    def test_absolute_chroma_threshold_boundary_is_19_valid_20_invalid(self):
        image = metadata()
        for plane in ("U", "V"):
            for direction in (-1, 1):
                raw, _ = self.native_bytes(image, (plane, 200, 300, 128 + direction * 19))
                support.checked_native_luminance(raw, image, [sample(image)])
                raw, _ = self.native_bytes(image, (plane, 200, 300, 128 + direction * 20))
                with self.assertRaises(support.SupportContractError) as failure:
                    support.checked_native_luminance(raw, image, [sample(image)])
                self.assertEqual(failure.exception.code, "SUPPORT_INVALID")

    def test_five_pixel_halo_and_one_pixel_erosion_block_contact(self):
        image = metadata()
        raw, _ = self.native_bytes(image, ("U", 166, 300, 148))
        # Chroma cell spans x=166,167; halo extends to 172, erosion to 173.
        support.checked_native_luminance(raw, image, [sample(image, x=206)])
        with self.assertRaises(support.SupportContractError) as failure:
            support.checked_native_luminance(raw, image, [sample(image, x=205)])
        self.assertEqual(failure.exception.code, "SUPPORT_INVALID")

    def test_complete_support_required_for_every_sample_without_salvage(self):
        image = metadata()
        raw, _ = self.native_bytes(image, ("V", 166, 300, 108))
        samples = [sample(image, x=206, sample_id="valid"), sample(image, x=205, sample_id="invalid")]
        with self.assertRaises(support.SupportContractError) as failure:
            support.checked_native_luminance(raw, image, samples)
        self.assertEqual(failure.exception.code, "SUPPORT_INVALID")
        neutral, _ = self.native_bytes(image)
        _, report = support.checked_native_luminance(neutral, image, [sample(image, x=37, y=156)])
        self.assertEqual(report["sample_count"], 1)


if __name__ == "__main__":
    unittest.main()
