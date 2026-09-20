"""Explicit TI3-D admission of the fourteen authorized native buffers.

This array-only module never reads a file or grants authority. The D reader
owns receipt, phase ordering, single opens and integrity. FINAL retains its
real split; no legacy guard is bypassed by relabelling metadata. Numeric
structural support is copied unchanged from TI3-A; solutal support retains
TI3-B geometry without chroma exclusion. Every patch must pass as a batch.
"""

import math

from .ti3_baseline import _scientific_runtime
from .ti3_dataset import ACQUISITIONS, DIMENSIONS, FRAME_SPLITS, patch_xyxy, support_xyxy


STRUCTURAL_SOURCE = {"ESM1": "ESM1", "ESM2": "ESM1", "ESM4": "ESM4", "ESM5": "ESM4"}
ALLOWED_FRAMES = frozenset(
    [(source, frame) for source in ("ESM1", "ESM2") for frame in (73, 146, 219, 293)]
    + [(source, frame) for source in ("ESM4", "ESM5") for frame in (98, 197, 295)]
)


class FinalSupportError(ValueError):
    """Terminal support failure; moving or replacing any sample is forbidden."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


def _require(condition, code, message):
    if not condition:
        raise FinalSupportError(code, message)


def _metadata(image, samples):
    """Validate exact D provenance before inspecting any byte or array."""
    _require(type(image) is dict, "CONFIGURATION_DIVERGENCE", "image metadata required")
    source, frame = image.get("source_id"), image.get("frame_index")
    _require(type(source) is str and type(frame) is int and (source, frame) in ALLOWED_FRAMES,
             "FORBIDDEN_INPUT", "outside the explicit fourteen-buffer TI3-D allowlist")
    structural = STRUCTURAL_SOURCE[source]
    split = FRAME_SPLITS[(structural, frame)]
    width, height = DIMENSIONS[structural]
    acquisition = ACQUISITIONS[structural]
    _require(image.get("split") == split, "FORBIDDEN_INPUT", "original split must remain unchanged")
    _require(type(image.get("width")) is int and type(image.get("height")) is int
             and (image["width"], image["height"]) == (width, height)
             and image.get("acquisition_id") == acquisition,
             "CONFIGURATION_DIVERGENCE", "native provenance differs")
    _require(image.get("pixel_format") == "yuv420p" and type(image.get("bit_depth")) is int
             and image["bit_depth"] == 8 and type(image.get("frame_bytes")) is int
             and image["frame_bytes"] == width * height * 3 // 2,
             "NATIVE_BUFFER_MISMATCH", "native representation differs")
    _require(type(samples) is list and samples, "CONFIGURATION_DIVERGENCE", "frozen sample list required")
    support = support_xyxy(width, height)
    boxes, ids = [], set()
    for sample in samples:
        _require(type(sample) is dict, "CONFIGURATION_DIVERGENCE", "sample metadata required")
        _require(sample.get("source_id") == structural and type(sample.get("frame_index")) is int
                 and sample["frame_index"] == frame and sample.get("split") == split,
                 "FORBIDDEN_INPUT", "sample source, frame or original split differs")
        _require(sample.get("acquisition_id") == acquisition
                 and type(sample.get("width")) is int and type(sample.get("height")) is int
                 and (sample["width"], sample["height"]) == (width, height),
                 "CONFIGURATION_DIVERGENCE", "sample native provenance differs")
        sample_id = sample.get("sample_id")
        _require(type(sample_id) is str and sample_id and sample_id not in ids,
                 "CONFIGURATION_DIVERGENCE", "sample ID absent or duplicated")
        ids.add(sample_id)
        _require(all(type(sample.get(name)) is int for name in
                     ("center_x", "center_y", "patch_radius_px", "patch_side_px"))
                 and sample["patch_radius_px"] == 32 and sample["patch_side_px"] == 65,
                 "CONFIGURATION_DIVERGENCE", "exact integer 65x65 patch geometry required")
        box = patch_xyxy(sample["center_x"], sample["center_y"])
        _require(sample.get("patch_xyxy") == box and sample.get("mapping_offset_xy") == [0, 0],
                 "CONFIGURATION_DIVERGENCE", "frozen crop or identity offset differs")
        _require(support[0] <= box[0] < box[2] <= support[2]
                 and support[1] <= box[1] < box[3] <= support[3],
                 "BLOCKED_FINAL_SUPPORT" if split == "FINAL_TEST" else "SUPPORT_INVALID",
                 "whole patch lacks unchanged geometric support")
        boxes.append((sample_id, box))
    return width, height, boxes


def checked_luminance(raw, image_metadata, structural_samples):
    """Admit all original patches or fail; never certify a replacement sample."""
    width, height, boxes = _metadata(image_metadata, structural_samples)
    _require(type(raw) is bytes, "NATIVE_BUFFER_MISMATCH", "immutable native bytes required")
    count = width * height
    _require(len(raw) == count * 3 // 2, "NATIVE_BUFFER_MISMATCH", "complete native YUV420p bytes required")
    np = _scientific_runtime()
    values = np.frombuffer(raw, dtype=np.uint8)
    luminance = values[:count].reshape(height, width)
    structural = image_metadata["source_id"] in ("ESM1", "ESM4")
    if structural:
        from scipy import ndimage

        # Same numeric predicate, operators and order as TI3-A, including halo
        # and erosion. The new authority changes admissible metadata only.
        u = values[count:count + count // 4].reshape(height // 2, width // 2).astype(np.int16)
        v = values[count + count // 4:].reshape(height // 2, width // 2).astype(np.int16)
        chroma = np.maximum(np.abs(u - 128), np.abs(v - 128)) >= 20
        overlay = chroma.repeat(2, axis=0).repeat(2, axis=1)
        overlay = ndimage.maximum_filter(overlay, size=11, mode="constant", cval=0)
        mask = ~overlay
        top = max(4, math.ceil(height * 0.12))
        bottom = max(4, math.ceil(height * 0.15))
        mask[:top] = False
        mask[height - bottom:] = False
        mask[:, :4] = False
        mask[:, width - 4:] = False
        mask = ndimage.binary_erosion(mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
        for _, (x0, y0, x1, y1) in boxes:
            _require(bool(mask[y0:y1, x0:x1].all()),
                     "BLOCKED_FINAL_SUPPORT" if image_metadata["split"] == "FINAL_TEST" else "SUPPORT_INVALID",
                     "at least one unchanged patch lacks complete structural support")
    luminance.setflags(write=False)
    return luminance, {
        "status": "PASS", "sample_count": len(boxes),
        "samples_checked": [sample_id for sample_id, _ in boxes],
        "original_split": image_metadata["split"],
        "support_contract": ("STRUCTURAL_CHROMA20_HALO5_GEOMETRY_EROSION1" if structural
                             else "SOLUTAL_GEOMETRY_12PCT_15PCT_BORDER4_EROSION1_NO_CHROMA"),
    }


def extract_authorized_patch(luminance, image_metadata, structural_sample):
    """Copy the same native crop; the caller must first admit full support."""
    width, height, boxes = _metadata(image_metadata, [structural_sample])
    np = _scientific_runtime()
    _require(isinstance(luminance, np.ndarray) and luminance.dtype == np.dtype("uint8")
             and luminance.shape == (height, width),
             "NATIVE_BUFFER_MISMATCH", "unchanged native luminance required")
    _, (x0, y0, x1, y1) = boxes[0]
    return luminance[y0:y1, x0:x1].copy()
