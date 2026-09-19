"""Admission of frozen TRAIN/DEVELOPMENT patches from authorized native bytes.

The caller owns authority, receipt, single-read custody and hash verification.
This module has no I/O and does not run registration, change geometry, discard
samples, compute image statistics or export a mask. It reproduces only the
frozen chroma/border/text support exclusions necessary to admit each patch.
"""

import math

from .ti3_baseline import _scientific_runtime
from .ti3_dataset import ACQUISITIONS, DIMENSIONS, FRAME_SPLITS, patch_xyxy, support_xyxy


ALLOWED_FRAMES = frozenset({("ESM1", 73), ("ESM1", 146), ("ESM1", 219),
                            ("ESM4", 98), ("ESM4", 197)})


class SupportContractError(ValueError):
    """Any failure terminates admission; callers may not salvage other samples."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


def _require(condition, code, message):
    if not condition:
        raise SupportContractError(code, message)


def _metadata(image, samples):
    """Deny every forbidden source/frame/sample before examining the buffer."""
    _require(type(image) is dict, "CONFIGURATION_DIVERGENCE", "explicit image metadata required")
    source, frame = image.get("source_id"), image.get("frame_index")
    _require(type(source) is str and type(frame) is int,
             "FORBIDDEN_INPUT", "explicit structural source and frame required")
    key = (source, frame)
    _require(key in ALLOWED_FRAMES, "FORBIDDEN_INPUT", "input outside TRAIN/DEVELOPMENT allowlist")
    split = FRAME_SPLITS[key]
    _require(image.get("split") == split, "FORBIDDEN_INPUT", "image split differs from fixed frame split")
    width, height = DIMENSIONS[source]
    _require(type(image.get("width")) is int and type(image.get("height")) is int
             and (image["width"], image["height"]) == (width, height),
             "CONFIGURATION_DIVERGENCE", "native dimensions differ")
    _require(image.get("acquisition_id") == ACQUISITIONS[source]
             and image.get("pixel_format") == "yuv420p" and image.get("bit_depth") == 8
             and type(image.get("frame_bytes")) is int
             and image["frame_bytes"] == width * height * 3 // 2,
             "CONFIGURATION_DIVERGENCE", "native representation or acquisition differs")
    _require(type(samples) is list and samples, "CONFIGURATION_DIVERGENCE", "frozen sample list required")
    boxes, ids = [], set()
    support = support_xyxy(width, height)
    for sample in samples:
        _require(type(sample) is dict, "CONFIGURATION_DIVERGENCE", "sample metadata required")
        _require(sample.get("source_id") == source and type(sample.get("frame_index")) is int
                 and sample["frame_index"] == frame and sample.get("split") == split,
                 "FORBIDDEN_INPUT", "sample belongs to another source/frame/split")
        _require(sample.get("acquisition_id") == ACQUISITIONS[source]
                 and type(sample.get("width")) is int and type(sample.get("height")) is int
                 and (sample["width"], sample["height"]) == (width, height),
                 "CONFIGURATION_DIVERGENCE", "sample native provenance differs")
        sample_id = sample.get("sample_id")
        _require(type(sample_id) is str and sample_id and sample_id not in ids,
                 "CONFIGURATION_DIVERGENCE", "sample ID missing or duplicated")
        ids.add(sample_id)
        names = ("center_x", "center_y", "patch_radius_px", "patch_side_px")
        _require(all(type(sample.get(name)) is int for name in names)
                 and sample["patch_radius_px"] == 32 and sample["patch_side_px"] == 65,
                 "CONFIGURATION_DIVERGENCE", "fixed integer patch geometry required")
        box = patch_xyxy(sample["center_x"], sample["center_y"])
        _require(sample.get("patch_xyxy") == box, "CONFIGURATION_DIVERGENCE", "frozen crop differs")
        _require(support[0] <= box[0] < box[2] <= support[2]
                 and support[1] <= box[1] < box[3] <= support[3],
                 "SUPPORT_INVALID", "whole patch is outside frozen geometric support")
        boxes.append((sample_id, box))
    return width, height, boxes


def checked_native_luminance(raw: bytes, image_metadata, samples):
    """Return an unchanged read-only uint8 Y view only if every patch is valid.

    Chroma distance >=20, a five-pixel square halo, frozen native borders and
    text bands, and one 3x3 erosion exactly reproduce the historical support
    predicate. No gradient, transform, metric, feature or object is computed.
    """
    width, height, boxes = _metadata(image_metadata, samples)
    _require(type(raw) is bytes, "NATIVE_BUFFER_MISMATCH", "immutable native bytes required")
    count = width * height
    _require(len(raw) == count * 3 // 2, "NATIVE_BUFFER_MISMATCH", "complete native YUV420p bytes required")
    np = _scientific_runtime()
    from scipy import ndimage

    values = np.frombuffer(raw, dtype=np.uint8)
    luminance = values[:count].reshape(height, width)
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
    for sample_id, (x0, y0, x1, y1) in boxes:
        _require(bool(mask[y0:y1, x0:x1].all()), "SUPPORT_INVALID",
                 "at least one frozen patch lacks complete native support")
    luminance.setflags(write=False)
    return luminance, {"status": "PASS", "sample_count": len(boxes),
                       "samples_checked": [sample_id for sample_id, _ in boxes]}
