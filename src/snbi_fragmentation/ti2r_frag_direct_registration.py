"""Frozen finite integer raster comparison, using only authorized memory.

No filesystem, source, path, decoder or authority I/O occurs here. Selection
uses native Sobel vectors. Reserved audit blocks use luminance and overlap-
normalized local correlation: masks are counts/weights, never image features.
"""

from dataclasses import dataclass
import math


DIMENSIONS = {
    "ESM3-to-ESM1": ((1018, 1278), (1024, 1280)),
    "ESM6-to-ESM4": ((1012, 1278), (1012, 1280)),
}


class DirectRegistrationError(ValueError):
    """An input is outside the finite frozen scientific contract."""


def _runtime():
    import numpy as np
    from scipy import ndimage, signal
    return np, ndimage, signal


@dataclass(frozen=True)
class PreparedFrame:
    luminance: object
    gx: object
    gy: object
    mask: object


def candidates(pair_name):
    if pair_name not in DIMENSIONS:
        raise DirectRegistrationError("only the two authorized fragment pairs exist")
    reference, moving = DIMENSIONS[pair_name]
    return tuple((x, y) for y in range(moving[0] - reference[0] + 1)
                 for x in range(moving[1] - reference[1] + 1))


def mapping(offset):
    if not isinstance(offset, (list, tuple)) or len(offset) != 2 or any(type(value) is not int for value in offset):
        raise DirectRegistrationError("mapping requires exactly two integer crop coordinates")
    ox, oy = offset
    return [[1, 0, -ox], [0, 1, -oy], [0, 0, 1]], [[1, 0, ox], [0, 1, oy], [0, 0, 1]]


def prepare(raw_bytes, width, height, config):
    """Decode the planes of an already-authorized existing YUV buffer in memory."""
    np, ndimage, _ = _runtime()
    if type(width) is not int or type(height) is not int or min(width, height) < 64 or width % 2 or height % 2:
        raise DirectRegistrationError("even native YUV420p dimensions required")
    count = width * height
    if len(raw_bytes) != count * 3 // 2:
        raise DirectRegistrationError("native buffer length differs from frozen dimensions")
    values = np.frombuffer(raw_bytes, dtype=np.uint8)
    luminance = values[:count].reshape(height, width).astype(float)
    u = values[count:count + count // 4].reshape(height // 2, width // 2).astype(np.int16)
    v = values[count + count // 4:].reshape(height // 2, width // 2).astype(np.int16)
    chroma = np.maximum(np.abs(u - 128), np.abs(v - 128)) >= config["chroma_distance_threshold"]
    overlay = chroma.repeat(2, axis=0).repeat(2, axis=1)
    halo = config["overlay_halo_px"]
    overlay = ndimage.maximum_filter(overlay, size=2 * halo + 1, mode="constant", cval=0)
    return prepare_luminance(luminance, ~overlay, config)


def prepare_luminance(luminance, valid_mask, config):
    np, ndimage, _ = _runtime()
    values = np.asarray(luminance, dtype=float)
    mask = np.asarray(valid_mask, dtype=bool).copy()
    if values.ndim != 2 or values.shape != mask.shape or not np.isfinite(values).all():
        raise DirectRegistrationError("finite two-dimensional luminance and matching mask required")
    h, w = values.shape
    border = config["native_border_px"]
    top = max(border, math.ceil(h * config["text_top_fraction"]))
    bottom = max(border, math.ceil(h * config["text_bottom_fraction"]))
    mask[:top] = False
    mask[h - bottom:] = False
    mask[:, :border] = False
    mask[:, w - border:] = False
    mask = ndimage.binary_erosion(mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
    # Derivatives only use a native one-pixel stencil. Excluded values cannot
    # influence any retained derivative; there is no global normalization.
    gx = ndimage.sobel(values, axis=1, mode="nearest") / 8.0
    gy = ndimage.sobel(values, axis=0, mode="nearest") / 8.0
    values = values.copy()
    for array in (values, gx, gy, mask):
        array.setflags(write=False)
    return PreparedFrame(values, gx, gy, mask)


def blocks(shape, config):
    """Static half-open native rectangles; opposite roles have a 40px gap."""
    h, w = shape
    border = config["native_border_px"]
    top = max(border, math.ceil(h * config["text_top_fraction"]))
    bottom = h - max(border, math.ceil(h * config["text_bottom_fraction"]))
    rows, columns, guard = config["grid_rows"], config["grid_columns"], config["block_guard_px"]
    if guard < config["audit_lag_radius_px"] + 6 + 2:
        raise DirectRegistrationError("partition guard does not cover all candidate and audit footprints")
    result = []
    for row in range(rows):
        for column in range(columns):
            x0 = border + (w - 2 * border) * column // columns + guard
            x1 = border + (w - 2 * border) * (column + 1) // columns - guard
            y0 = top + (bottom - top) * row // rows + guard
            y1 = top + (bottom - top) * (row + 1) // rows - guard
            if x1 <= x0 or y1 <= y0:
                raise DirectRegistrationError("raster too small for frozen spatial partition")
            result.append({"id": f"r{row}c{column}", "role": "selection" if (row + column) % 2 == 0 else "audit",
                           "quadrant": [int(column >= columns / 2), int(row >= rows / 2)],
                           "xyxy": [x0, y0, x1, y1]})
    return result


def _slice(frame, block, name, offset=(0, 0)):
    x0, y0, x1, y1 = block["xyxy"]
    ox, oy = offset
    return getattr(frame, name)[y0 + oy:y1 + oy, x0 + ox:x1 + ox]


def reference_information(reference, config):
    """This function accepts no moving frame, candidate, score or residual."""
    np, _, _ = _runtime()
    records = []
    for block in blocks(reference.luminance.shape, config):
        mask = _slice(reference, block, "mask")
        count = int(mask.sum())
        standard_deviation, eigenvalue_ratio = 0.0, 0.0
        if count:
            values = _slice(reference, block, "luminance")[mask]
            gx, gy = _slice(reference, block, "gx")[mask], _slice(reference, block, "gy")[mask]
            standard_deviation = float(values.std())
            tensor = np.array([[np.mean(gx * gx), np.mean(gx * gy)], [np.mean(gx * gy), np.mean(gy * gy)]])
            eigenvalues = np.linalg.eigvalsh(tensor)
            if eigenvalues[1] > config["numerical_epsilon"]:
                eigenvalue_ratio = max(0.0, float(eigenvalues[0] / eigenvalues[1]))
        qualified = (count >= config["minimum_valid_pixels_per_block"]
                     and standard_deviation >= config["minimum_reference_std_luma"]
                     and eigenvalue_ratio >= config["minimum_reference_gradient_eigenvalue_ratio"])
        records.append(dict(block, valid_pixels=count, standard_deviation_luma=standard_deviation,
                            gradient_eigenvalue_ratio=eigenvalue_ratio, qualified=qualified))
    roles = {}
    for role in ("selection", "audit"):
        qualified = [b for b in records if b["role"] == role and b["qualified"]]
        quadrants = sorted({tuple(b["quadrant"]) for b in qualified})
        roles[role] = {"blocks": len(qualified), "quadrants": [list(q) for q in quadrants]}
    identifiable = all(r["blocks"] >= config["minimum_blocks_per_role"]
                       and len(r["quadrants"]) >= config["minimum_quadrants_per_role"] for r in roles.values())
    return {"classification": "IDENTIFIABLE" if identifiable else "NON_IDENTIFIABLE", "roles": roles, "blocks": records,
            "criterion_inputs": "reference_luminance_gradients_mask_only"}


def _vector_ncc(reference, moving, block, mask, offset, epsilon):
    np, _, _ = _runtime()
    numerator, energy_a, energy_b = 0.0, 0.0, 0.0
    for component in ("gx", "gy"):
        a = _slice(reference, block, component)[mask]
        b = _slice(moving, block, component, offset)[mask]
        a, b = a - a.mean(), b - b.mean()
        numerator += float(np.dot(a, b))
        energy_a += float(np.dot(a, a))
        energy_b += float(np.dot(b, b))
    denominator = math.sqrt(energy_a * energy_b)
    return None if denominator <= epsilon else max(-1.0, min(1.0, numerator / denominator))


def select_candidate(reference, moving, offsets, config, information=None):
    np, _, _ = _runtime()
    information = reference_information(reference, config) if information is None else information
    context, records = [], []
    for block in information["blocks"]:
        if block["role"] != "selection" or not block["qualified"]:
            continue
        common = _slice(reference, block, "mask").copy()
        for offset in offsets:
            other = _slice(moving, block, "mask", offset)
            if other.shape != common.shape:
                raise DirectRegistrationError("candidate exceeds moving extent")
            common &= other
        count = int(common.sum())
        supported = count >= config["minimum_valid_pixels_per_block"]
        records.append({"id": block["id"], "valid_pixels": count, "quadrant": block["quadrant"],
                        "status": "AVAILABLE" if supported else "UNAVAILABLE_SUPPORT"})
        if supported:
            context.append((block, common))
    quadrants = sorted({tuple(block["quadrant"]) for block, _ in context})
    candidate_scores = []
    sample_count = sum(int(mask.sum()) for _, mask in context)
    for offset in offsets:
        values = [_vector_ncc(reference, moving, block, mask, offset, config["numerical_epsilon"]) for block, mask in context]
        score = sum(values) / len(values) if values and all(v is not None for v in values) else None
        candidate_scores.append({"offset": list(offset), "score": score, "sample_count": sample_count,
                                 "block_scores": [{"id": block["id"], "score": value} for (block, _), value in zip(context, values)]})
    available = [entry for entry in candidate_scores if entry["score"] is not None]
    result = {"status": "FAIL_SELECTION_SUPPORT", "winner": None, "margin": None, "candidate_scores": candidate_scores,
              "blocks": records, "available_blocks": len(context), "quadrants": [list(q) for q in quadrants],
              "common_sample_count": sample_count, "same_samples_for_all_candidates": True}
    if len(context) < config["minimum_blocks_per_role"] or len(quadrants) < config["minimum_quadrants_per_role"]:
        return result
    if len(available) != len(offsets):
        result["status"] = "FAIL_UNDEFINED_SELECTION_SCORE"
        return result
    ordered = sorted(available, key=lambda record: (-record["score"], record["offset"][1], record["offset"][0]))
    result["winner"] = ordered[0]["offset"]
    result["margin"] = float(ordered[0]["score"] - ordered[1]["score"])
    result["status"] = "PASS" if ordered[0]["score"] >= config["minimum_selection_score"] and result["margin"] >= config["uniqueness_margin"] else "FAIL_UNIQUE_CANDIDATE"
    return result


def _residual(reference, moving, block, offset, config):
    np, _, signal = _runtime()
    x0, y0, x1, y1 = block["xyxy"]
    ox, oy = offset
    radius = config["audit_lag_radius_px"]
    a = reference.luminance[y0:y1, x0:x1]
    ma = reference.mask[y0:y1, x0:x1].astype(float)
    b = moving.luminance[y0 + oy - radius:y1 + oy + radius, x0 + ox - radius:x1 + ox + radius]
    mb = moving.mask[y0 + oy - radius:y1 + oy + radius, x0 + ox - radius:x1 + ox + radius].astype(float)
    record = {"id": block["id"], "quadrant": block["quadrant"], "area_pixels": int(a.size),
              "status": "UNAVAILABLE_SUPPORT", "valid_pixels": 0, "minimum_lag_pixels": 0,
              "residual_px": None, "sampling_residual_dxdy": None, "peak_correlation": None}
    if b.shape != (a.shape[0] + 2 * radius, a.shape[1] + 2 * radius):
        return record
    # Subtract separate deterministic image constants solely for numerical
    # stability; exact per-overlap centering below makes them mathematically
    # irrelevant. Never fill mask holes with shared image features.
    a = a - 128.0
    b = b - 128.0
    def corr(first, second):
        return signal.correlate(first, second, mode="valid", method="fft")
    n = np.rint(corr(mb, ma))
    record["valid_pixels"] = int(n[radius, radius])
    record["minimum_lag_pixels"] = int(n.min())
    if np.any(n < config["minimum_valid_pixels_per_block"]):
        return record
    sa, sb = corr(mb, a * ma), corr(b * mb, ma)
    aa, bb = corr(mb, a * a * ma), corr(b * b * mb, ma)
    ab = corr(b * mb, a * ma)
    va, vb = np.maximum(0.0, aa - sa * sa / n), np.maximum(0.0, bb - sb * sb / n)
    denominator = np.sqrt(va * vb)
    # A constant image away from 128 can leave tiny positive variance after
    # subtracting FFT sums. Scale the numerical zero tolerance to those sums;
    # this is an undefined metric, never evidence of zero displacement.
    tolerance_a = config["numerical_epsilon"] * np.maximum(1.0, np.maximum(aa, sa * sa / n))
    tolerance_b = config["numerical_epsilon"] * np.maximum(1.0, np.maximum(bb, sb * sb / n))
    if np.any(va <= tolerance_a) or np.any(vb <= tolerance_b) or np.any(denominator <= config["numerical_epsilon"]):
        record["status"] = "FAIL_UNDEFINED_CORRELATION"
        return record
    correlations = np.clip((ab - sa * sb / n) / denominator, -1.0, 1.0)
    py, px = np.unravel_index(int(np.argmax(correlations)), correlations.shape)
    peak = float(correlations[py, px])
    dx, dy = float(px - radius), float(py - radius)
    # This parabolic refinement belongs only to the residual measurement.
    # It never enters candidate generation, mapping or holdout freezing.
    for axis in (0, 1):
        center = py if axis == 0 else px
        if 0 < center < 2 * radius:
            lower = correlations[py - 1, px] if axis == 0 else correlations[py, px - 1]
            upper = correlations[py + 1, px] if axis == 0 else correlations[py, px + 1]
            divisor = float(lower - 2 * peak + upper)
            delta = 0.0 if abs(divisor) <= config["numerical_epsilon"] else max(-0.5, min(0.5, float(0.5 * (lower - upper) / divisor)))
            if axis == 0:
                dy += delta
            else:
                dx += delta
    # Near-perfect self-correlation has symmetric neighbours up to FFT error.
    dx = 0.0 if abs(dx) < 1e-10 else dx
    dy = 0.0 if abs(dy) < 1e-10 else dy
    tied = int(np.count_nonzero(np.abs(correlations - peak) <= config["audit_peak_tie_tolerance"])) > 1
    record.update(status="FAIL_AMBIGUOUS_CORRELATION" if tied else "MEASURED", residual_px=float(math.hypot(dx, dy)),
                  sampling_residual_dxdy=[dx, dy], peak_correlation=peak, peak_at_search_boundary=bool(px in (0, 2 * radius) or py in (0, 2 * radius)))
    return record


def _summary(values):
    np, _, _ = _runtime()
    return {"count": len(values), "median_px": float(np.median(values)) if values else None,
            "p95_px": float(np.percentile(values, 95)) if values else None,
            "maximum_px": float(max(values)) if values else None}


def audit_offset(reference, moving, offset, config, information=None):
    information = reference_information(reference, config) if information is None else information
    records = [_residual(reference, moving, block, offset, config) for block in information["blocks"]
               if block["role"] == "audit" and block["qualified"]]
    measured = [record for record in records if record["residual_px"] is not None]
    summary = _summary([r["residual_px"] for r in measured])
    quadrants = sorted({tuple(r["quadrant"]) for r in measured})
    status = "PASS"
    if len(measured) < config["minimum_blocks_per_role"] or len(quadrants) < config["minimum_quadrants_per_role"]:
        status = "FAIL_AUDIT_SUPPORT"
    elif any(r["status"].startswith("FAIL_") for r in records):
        status = "FAIL_AUDIT_CORRELATION"
    elif summary["median_px"] > config["median_limit_px"] or summary["p95_px"] > config["p95_limit_px"] or summary["maximum_px"] > config["maximum_limit_px"]:
        status = "FAIL_AUDIT_METRICS"
    return dict(summary, status=status, blocks=records, quadrants=[list(q) for q in quadrants],
                measured_blocks=len(measured), metric="reserved_masked_luminance_overlap_zncc",
                error_based_rejections=0, mapping_updated=False)


def evaluate_frame(reference, moving, offsets, config, frozen_offset=None):
    information = reference_information(reference, config)
    result = {"classification": information["classification"], "reference_information": information,
              "status": "NON_IDENTIFIABLE", "winner": None, "margin": None, "candidate_scores": [],
              "selection": None, "audit": None}
    if information["classification"] == "NON_IDENTIFIABLE":
        return result
    selection = select_candidate(reference, moving, offsets, config, information)
    result.update(status=selection["status"], winner=selection["winner"], margin=selection["margin"],
                  candidate_scores=selection["candidate_scores"], selection=selection)
    if selection["status"] != "PASS":
        return result
    applied_offset = selection["winner"] if frozen_offset is None else list(frozen_offset)
    audit = audit_offset(reference, moving, applied_offset, config, information)
    status = audit["status"]
    if frozen_offset is not None and selection["winner"] != list(frozen_offset):
        status = "FAIL_FROZEN_OFFSET_CONTRADICTION"
    result.update(status=status, audit=audit, applied_offset=applied_offset)
    return result


def _evaluate(pair_name, pairs, config, holdout=False, frozen_offset=None):
    offsets = candidates(pair_name)
    count = 2 if holdout else 3
    if len(pairs) != count:
        raise DirectRegistrationError("wrong number of frozen temporal observations")
    if holdout:
        mapping(frozen_offset)
        if tuple(frozen_offset) not in offsets:
            raise DirectRegistrationError("frozen offset is outside the finite authorized candidate set")
    output = {"status": "BLOCKED_DIMENSION_DIVERGENCE", "pair": pair_name, "offset": None,
              "matrix": None, "inverse": None, "per_frame": [], "aggregate": _summary([]),
              "identifiable_frames": [], "non_identifiable_frames": [], "candidates": [list(x) for x in offsets],
              "frozen_offset": list(frozen_offset) if holdout else None, "offset_changed": False,
              "validation_kind": "internal_temporal_same_acquisition" if holdout else None,
              "rectangle_roi": None, "units": "native_pixels"}
    reference_shape, moving_shape = DIMENSIONS[pair_name]
    if any(reference.luminance.shape != reference_shape or moving.luminance.shape != moving_shape for reference, moving in pairs):
        return output
    frames = [evaluate_frame(reference, moving, offsets, config, frozen_offset=frozen_offset if holdout else None)
              for reference, moving in pairs]
    identifiable = [i for i, frame in enumerate(frames) if frame["classification"] == "IDENTIFIABLE"]
    non_identifiable = [i for i, frame in enumerate(frames) if frame["classification"] == "NON_IDENTIFIABLE"]
    residuals = [block["residual_px"] for frame in frames if frame["audit"] is not None
                 for block in frame["audit"]["blocks"] if block["residual_px"] is not None]
    output.update(per_frame=frames, aggregate=_summary(residuals), identifiable_frames=identifiable,
                  non_identifiable_frames=non_identifiable, status="BLOCKED_DIRECT_MAPPING")
    minimum = config["minimum_identifiable_holdout_frames"] if holdout else config["minimum_identifiable_development_frames"]
    if len(identifiable) < minimum:
        output["status"] = "BLOCKED_REFERENCE_STILL_INSUFFICIENT"
        return output
    if any(frames[i]["status"] != "PASS" for i in identifiable):
        return output
    aggregate = output["aggregate"]
    if (aggregate["count"] == 0 or aggregate["median_px"] > config["median_limit_px"]
            or aggregate["p95_px"] > config["p95_limit_px"] or aggregate["maximum_px"] > config["maximum_limit_px"]):
        return output
    winners = {tuple(frames[i]["winner"]) for i in identifiable}
    if len(winners) != 1 or (holdout and next(iter(winners)) != tuple(frozen_offset)):
        return output
    offset = next(iter(winners))
    matrix, inverse = mapping(offset)
    output.update(status="PASS", offset=list(offset), matrix=matrix, inverse=inverse,
                  determinant=1, numerical_roundtrip_px=0, parameter_status="FROZEN_INTEGER_CROP_MAPPING")
    return output


def evaluate_development(pair_name, pairs, config):
    return _evaluate(pair_name, pairs, config)


def evaluate_holdout(pair_name, pairs, frozen_offset, config):
    """Confirm the frozen integer; never replace it with a holdout winner."""
    return _evaluate(pair_name, pairs, config, holdout=True, frozen_offset=frozen_offset)
