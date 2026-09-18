"""Pure-memory, frozen multimodal test of identity, never a registrator.

Selection uses explicitly defined eight-channel local self-similarity, not
an assertion of exact MIND-SSC equivalence. Disjoint audit blocks use squared
normalized gradient products. All nonzero shifts are negative controls only.
"""

from dataclasses import dataclass
import math


DIMENSIONS = {"ESM2-to-ESM1": (1018, 1278), "ESM5-to-ESM4": (1012, 1278)}
OFFSETS = tuple((x, y) for y in range(-3, 4) for x in range(-3, 4))
ZERO = OFFSETS.index((0, 0))


class SoluteRegistrationError(ValueError):
    """Input violates the frozen identity-only contract."""


def _runtime():
    import numpy as np
    from scipy import ndimage
    return np, ndimage


@dataclass(frozen=True)
class PreparedFrame:
    luminance: object
    gx: object
    gy: object
    mask: object
    descriptor_mask: object
    gradient_mask: object


def spatial_controls():
    return tuple(offset for offset in OFFSETS if offset != (0, 0))


def identity_matrix():
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def prepare(raw_bytes, width, height, config):
    """Interpret Y from an already-authorized native YUV420p memory buffer."""
    np, _ = _runtime()
    if type(width) is not int or type(height) is not int or min(width, height) < 64 or width % 2 or height % 2:
        raise SoluteRegistrationError("even native YUV420p dimensions required")
    count = width * height
    if len(raw_bytes) != count * 3 // 2:
        raise SoluteRegistrationError("native buffer size mismatch")
    luminance = np.frombuffer(raw_bytes, dtype=np.uint8, count=count).reshape(height, width).astype(float)
    # Chroma can carry solutal presentation information. No unproven claim
    # that colored pixels are overlays is made; only fixed geometry is masked.
    return prepare_luminance(luminance, np.ones((height, width), dtype=bool), config)


def prepare_luminance(luminance, valid_mask, config):
    np, ndimage = _runtime()
    values = np.asarray(luminance, dtype=float)
    mask = np.asarray(valid_mask, dtype=bool).copy()
    if values.ndim != 2 or mask.shape != values.shape or not np.isfinite(values).all():
        raise SoluteRegistrationError("finite native luminance and matching mask required")
    h, w = values.shape
    border = config["native_border_px"]
    mask[:max(border, math.ceil(h * config["text_top_fraction"]))] = False
    mask[h - max(border, math.ceil(h * config["text_bottom_fraction"])):] = False
    mask[:, :border] = False
    mask[:, w - border:] = False
    descriptor_mask = ndimage.binary_erosion(mask, structure=np.ones((7, 7), dtype=bool), border_value=0)
    gradient_mask = ndimage.binary_erosion(mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
    gx = ndimage.sobel(values, axis=1, mode="nearest") / 8.0
    gy = ndimage.sobel(values, axis=0, mode="nearest") / 8.0
    values = values.copy()
    for array in (values, gx, gy, mask, descriptor_mask, gradient_mask):
        array.setflags(write=False)
    return PreparedFrame(values, gx, gy, mask, descriptor_mask, gradient_mask)


def blocks(shape, config):
    h, w = shape
    border, guard = config["native_border_px"], config["block_guard_px"]
    if guard < 10 or config["control_radius_px"] != 3:
        raise SoluteRegistrationError("frozen descriptor/audit footprints or control set changed")
    top = max(border, math.ceil(h * config["text_top_fraction"]))
    bottom = h - max(border, math.ceil(h * config["text_bottom_fraction"]))
    rows, columns = config["grid_rows"], config["grid_columns"]
    result = []
    for row in range(rows):
        for column in range(columns):
            x0 = border + (w - 2 * border) * column // columns + guard
            x1 = border + (w - 2 * border) * (column + 1) // columns - guard
            y0 = top + (bottom - top) * row // rows + guard
            y1 = top + (bottom - top) * (row + 1) // rows - guard
            if min(x1 - x0, y1 - y0) <= 0:
                raise SoluteRegistrationError("raster too small for frozen partition")
            result.append({"id": f"r{row}c{column}", "role": "selection" if (row + column) % 2 == 0 else "audit",
                           "xyxy": [x0, y0, x1, y1], "quadrant": [int(column >= columns / 2), int(row >= rows / 2)]})
    return result


def _individual_periodicity(gx, gy, mask, config):
    """Individual structural information test; never compares modalities."""
    np, _ = _runtime()
    maximum = 0.0
    for axis in (0, 1):
        for lag in config["individual_periodicity_lags"]:
            if lag >= gx.shape[axis]:
                continue
            left, right = [slice(None)] * 2, [slice(None)] * 2
            left[axis], right[axis] = slice(None, -lag), slice(lag, None)
            left, right = tuple(left), tuple(right)
            ax, ay, bx, by = gx[left], gy[left], gx[right], gy[right]
            denominator = (ax * ax + ay * ay) * (bx * bx + by * by)
            valid = mask[left] & mask[right] & (denominator > config["numerical_epsilon"])
            if int(valid.sum()) >= config["minimum_periodicity_pixels"]:
                coherence = float(np.mean(((ax * bx + ay * by) ** 2)[valid] / denominator[valid]))
                maximum = max(maximum, min(1.0, coherence))
    return maximum


def image_information(frame, config):
    """Classify one image using only its own structure and native masks."""
    np, _ = _runtime()
    records = []
    for block in blocks(frame.luminance.shape, config):
        x0, y0, x1, y1 = block["xyxy"]
        region = (slice(y0, y1), slice(x0, x1))
        mask = (frame.descriptor_mask if block["role"] == "selection" else frame.gradient_mask)[region]
        values = frame.luminance[region][mask]
        gx, gy = frame.gx[region][mask], frame.gy[region][mask]
        count = len(values)
        rms, ratio, entropy, saturation, periodicity = 0.0, 0.0, 0.0, 1.0, 0.0
        if count:
            tensor = np.array([[np.mean(gx * gx), np.mean(gx * gy)], [np.mean(gx * gy), np.mean(gy * gy)]])
            eig = np.linalg.eigvalsh(tensor)
            rms = math.sqrt(max(0.0, float(eig.sum())))
            ratio = max(0.0, float(eig[0] / eig[1])) if eig[1] > config["numerical_epsilon"] else 0.0
            histogram = np.histogram(values, bins=config["entropy_bins"], range=(0, 256))[0]
            probabilities = histogram[histogram > 0] / count
            entropy = float(-np.sum(probabilities * np.log2(probabilities)))
            saturation = float(np.mean((values <= config["saturation_low_y"]) | (values >= config["saturation_high_y"])))
            periodicity = _individual_periodicity(frame.gx[region], frame.gy[region], mask, config)
        qualified = (count >= config["minimum_valid_pixels_per_block"] and rms >= config["minimum_gradient_rms"]
                     and ratio >= config["minimum_gradient_eigenvalue_ratio"] and entropy >= config["minimum_entropy_bits"]
                     and saturation <= config["maximum_saturation_fraction"]
                     and periodicity < config["individual_periodicity_maximum_coherence"])
        records.append(dict(block, valid_pixels=count, gradient_rms=rms, gradient_eigenvalue_ratio=ratio,
                            entropy_bits=entropy, saturation_fraction=saturation, individual_periodicity_coherence=periodicity,
                            qualified=qualified))
    roles = {}
    for role in ("selection", "audit"):
        qualified = [b for b in records if b["role"] == role and b["qualified"]]
        quadrants = sorted({tuple(b["quadrant"]) for b in qualified})
        roles[role] = {"blocks": len(qualified), "quadrants": [list(q) for q in quadrants]}
    identifiable = all(r["blocks"] >= config["minimum_blocks_per_role"] and len(r["quadrants"]) >= config["minimum_quadrants_per_role"] for r in roles.values())
    return {"classification": "IDENTIFIABLE" if identifiable else "NON_IDENTIFIABLE", "blocks": records, "roles": roles,
            "inputs": "individual_image_only_no_partner_no_comparative_score_no_residual"}


def self_similarity(values, config):
    """Eight local patch relations; explicit multimodal descriptor definition.

    The caller retains only positions at least three pixels from this patch's
    edge. Roll/filter boundaries therefore never enter a scientific sample.
    """
    np, ndimage = _runtime()
    distance = config["self_similarity_neighbour_distance_px"]
    if distance != 2 or config["self_similarity_patch_side_px"] != 3:
        raise SoluteRegistrationError("descriptor footprint is frozen at radius three")
    distances = []
    for dy, dx in ((-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)):
        difference = values - np.roll(values, (-dy, -dx), axis=(0, 1))
        distances.append(ndimage.uniform_filter(difference * difference, size=3, mode="constant", cval=0))
    array = np.stack(distances)
    variance = np.maximum(array.mean(axis=0), config["numerical_epsilon"])
    descriptor = np.exp(-(array - array.min(axis=0)) / variance)
    return descriptor.astype(np.float32)


def ngf_values(ax, ay, bx, by, eta_a, eta_b):
    return ((ax * bx + ay * by) ** 2) / ((ax * ax + ay * ay + eta_a * eta_a) * (bx * bx + by * by + eta_b * eta_b))


def _features(frame, block, role, config):
    np, _ = _runtime()
    x0, y0, x1, y1 = block["xyxy"]
    pad = config["control_radius_px"]
    if role == "selection":
        values = frame.luminance[y0-pad-3:y1+pad+3, x0-pad-3:x1+pad+3]
        features = self_similarity(values, config)[:, 3:-3, 3:-3]
        mask = frame.descriptor_mask[y0-pad:y1+pad, x0-pad:x1+pad]
        eta = None
    else:
        gx = frame.gx[y0-pad:y1+pad, x0-pad:x1+pad]
        gy = frame.gy[y0-pad:y1+pad, x0-pad:x1+pad]
        mask = frame.gradient_mask[y0-pad:y1+pad, x0-pad:x1+pad]
        # This eta uses only this image's central audit block. Neither a
        # selection pixel nor another modality/frame contributes to it.
        core = mask[pad:-pad, pad:-pad]
        squared = gx[pad:-pad, pad:-pad] ** 2 + gy[pad:-pad, pad:-pad] ** 2
        rms = math.sqrt(float(np.mean(squared[core]))) if core.any() else 0.0
        eta = max(config["ngf_eta_floor"], config["ngf_eta_rms_fraction"] * rms)
        denominator = np.sqrt(gx * gx + gy * gy + eta * eta)
        features = np.stack((gx / denominator, gy / denominator)).astype(np.float32)
    return {"features": features, "mask": mask, "eta": eta}


def _central(array, offset=(0, 0)):
    dx, dy = offset
    h, w = array.shape[-2] - 6, array.shape[-1] - 6
    return array[..., 3 + dy:3 + dy + h, 3 + dx:3 + dx + w]


def _score(a, b, mask, role):
    np, _ = _runtime()
    av, bv = a[:, mask], b[:, mask]
    if role == "selection":
        return max(0.0, min(1.0, 1.0 - float(np.mean(np.abs(av - bv)))))
    return max(0.0, min(1.0, float(np.mean(np.sum(av * bv, axis=0) ** 2))))


def _peak_record(scores, config):
    np, _ = _runtime()
    surface = np.asarray(scores).reshape(7, 7)
    py, px = np.unravel_index(int(np.argmax(surface)), surface.shape)
    peak = float(surface[py, px])
    boundary = px in (0, 6) or py in (0, 6)
    ambiguous = int(np.count_nonzero(np.abs(surface - peak) <= config["peak_tie_tolerance"])) > 1
    dx, dy = float(px - 3), float(py - 3)
    for axis in (0, 1):
        index = py if axis == 0 else px
        if 0 < index < 6:
            lower = surface[py-1, px] if axis == 0 else surface[py, px-1]
            upper = surface[py+1, px] if axis == 0 else surface[py, px+1]
            divisor = float(lower - 2 * peak + upper)
            delta = 0.0 if abs(divisor) <= config["numerical_epsilon"] else max(-0.5, min(0.5, float(0.5 * (lower - upper) / divisor)))
            if axis == 0:
                dy += delta
            else:
                dx += delta
    return {"residual_px": math.hypot(dx, dy), "sampling_residual_dxdy": [dx, dy], "peak_at_search_boundary": boundary,
            "censored": boundary, "ambiguous_peak": ambiguous, "peak_score": peak, "discarded_for_error": False}


def _comparisons(reference, moving_frames, correct_index, information, moving_information, role, config, cache):
    np, _ = _runtime()
    def features(frame, block):
        key = (id(frame), block["id"], role)
        if key not in cache:
            cache[key] = _features(frame, block, role, config)
        return cache[key]
    records, spatial, temporal = [], [], [[] for _ in moving_frames]
    correct_blocks = {b["id"]: b for b in moving_information[correct_index]["blocks"]}
    for block in information["blocks"]:
        if block["role"] != role:
            continue
        record = {"id": block["id"], "quadrant": block["quadrant"], "valid_pixels": 0,
                  "status": "UNAVAILABLE_INDIVIDUAL_INFORMATION", "residual_px": None, "discarded_for_error": False}
        if not block["qualified"] or not correct_blocks[block["id"]]["qualified"]:
            records.append(record)
            continue
        a = features(reference, block)
        all_b = [features(frame, block) for frame in moving_frames]
        common = _central(a["mask"]).copy()
        for offset in OFFSETS:
            common &= _central(all_b[correct_index]["mask"], offset)
        for candidate in all_b:
            common &= _central(candidate["mask"])
        record["valid_pixels"] = int(common.sum())
        if record["valid_pixels"] < config["minimum_valid_pixels_per_block"]:
            record["status"] = "UNAVAILABLE_COMMON_SUPPORT"
            records.append(record)
            continue
        ref = _central(a["features"])
        scores = [_score(ref, _central(all_b[correct_index]["features"], offset), common, role) for offset in OFFSETS]
        temporal_scores = [_score(ref, _central(candidate["features"]), common, role) for candidate in all_b]
        record.update(status="MEASURED", identity_score=scores[ZERO], spatial_control_scores=[{"offset": list(o), "score": s} for o, s in zip(OFFSETS, scores) if o != (0, 0)],
                      temporal_scores=temporal_scores)
        if role == "audit":
            record.update(_peak_record(scores, config), eta_reference=a["eta"], eta_moving=all_b[correct_index]["eta"])
        records.append(record)
        spatial.append(scores)
        for index, score in enumerate(temporal_scores):
            temporal[index].append(score)
    available = [r for r in records if r["status"] == "MEASURED"]
    quadrants = sorted({tuple(r["quadrant"]) for r in available})
    result = {"status": "FAIL_SUPPORT", "blocks": records, "available_blocks": len(available),
              "quadrants": [list(q) for q in quadrants], "identity_score": None, "spatial_margin": None,
              "spatial_controls": [], "temporal_controls": [], "best_control_offset": None,
              "same_pixels_for_all_controls": True}
    if role == "audit":
        # An insufficient number of observations is still reported honestly;
        # descriptive metrics never override the blocking coverage gate.
        result.update(summary([r["residual_px"] for r in available]), error_based_rejections=0, mapping_updated=False)
    if not available:
        return result
    means = np.asarray(spatial).mean(axis=0)
    identity = float(means[ZERO])
    control_indices = [i for i in range(len(OFFSETS)) if i != ZERO]
    best_index = max(control_indices, key=lambda index: means[index])
    spatial_margin = identity - float(means[best_index])
    temporal_means = [float(np.mean(values)) for values in temporal]
    temporal_records = [{"moving_time": i, "score": score, "margin": identity - score} for i, score in enumerate(temporal_means) if i != correct_index]
    result.update(identity_score=identity, spatial_margin=spatial_margin, best_control_offset=list(OFFSETS[best_index]),
                  spatial_controls=[{"offset": list(OFFSETS[i]), "score": float(means[i]), "margin": identity-float(means[i])} for i in control_indices],
                  temporal_controls=temporal_records)
    if len(available) < config["minimum_blocks_per_role"] or len(quadrants) < config["minimum_quadrants_per_role"]:
        return result
    prefix = "mind" if role == "selection" else "ngf"
    discriminative = (spatial_margin >= config[f"{prefix}_spatial_margin"]
                      and all(r["margin"] >= config[f"{prefix}_temporal_margin"] for r in temporal_records)
                      and all(r["identity_score"] >= config[f"{prefix}_minimum_identity_score"] for r in available))
    result["status"] = "PASS" if discriminative else "FAIL_IDENTITY_DISCRIMINATION"
    if role == "audit":
        if any(r["peak_at_search_boundary"] or r["ambiguous_peak"] for r in available):
            result["status"] = "FAIL_CENSORED_OR_AMBIGUOUS_RESIDUAL"
        elif not metrics_pass(result, config):
            result["status"] = "FAIL_AUDIT_METRICS"
    return result


def summary(values):
    np, _ = _runtime()
    return {"count": len(values), "median_px": float(np.median(values)) if values else None,
            "p95_px": float(np.percentile(values, 95)) if values else None,
            "maximum_px": float(max(values)) if values else None}


def metrics_pass(metrics, config):
    return (metrics["count"] > 0 and metrics["median_px"] <= config["median_limit_px"]
            and metrics["p95_px"] <= config["p95_limit_px"] and metrics["maximum_px"] <= config["maximum_limit_px"])


def audit_pair(reference, moving, config):
    return _comparisons(reference, [moving], 0, image_information(reference, config), [image_information(moving, config)], "audit", config, {})


def evaluate_series(pairs, config, holdout=False):
    """Pure synthetic/scientific core; wrappers enforce native asset dimensions."""
    count = 2 if holdout else 3
    if len(pairs) != count:
        raise SoluteRegistrationError("wrong count of frozen temporal observations")
    information = [(image_information(reference, config), image_information(moving, config)) for reference, moving in pairs]
    moving_frames = [moving for _, moving in pairs]
    moving_information = [info[1] for info in information]
    frames, controls, cache = [], [], {}
    for index, ((reference, _), (ref_info, mov_info)) in enumerate(zip(pairs, information)):
        identifiable = ref_info["classification"] == mov_info["classification"] == "IDENTIFIABLE"
        frame = {"classification": "IDENTIFIABLE" if identifiable else "NON_IDENTIFIABLE", "reference_information": ref_info,
                 "moving_information": mov_info, "status": "NON_IDENTIFIABLE", "selection": None, "audit": None,
                 "applied_offset": [0, 0], "mapping_updated": False}
        if identifiable:
            selection = _comparisons(reference, moving_frames, index, ref_info, moving_information, "selection", config, cache)
            audit = _comparisons(reference, moving_frames, index, ref_info, moving_information, "audit", config, cache)
            if selection["status"] == "FAIL_SUPPORT" or audit["status"] == "FAIL_SUPPORT":
                status = "BLOCKED_MODALITY_INFORMATION_INSUFFICIENT"
            elif (selection["status"] == "PASS") != (audit["status"] == "PASS"):
                status = "BLOCKED_MULTIMODAL_METRIC_DISCORDANCE"
            elif selection["status"] != "PASS":
                status = "BLOCKED_IDENTITY_NOT_DISCRIMINATIVE"
            else:
                status = "PASS"
            frame.update(status=status, selection=selection, audit=audit)
        frames.append(frame)
        for other_index in range(count):
            if other_index == index:
                continue
            record = {"reference_time": index, "moving_time": other_index,
                      "reference_classification": ref_info["classification"],
                      "moving_classification": moving_information[other_index]["classification"],
                      "mind_score": None, "ngf_score": None, "mind_margin": None, "ngf_margin": None,
                      "status": "NOT_MEASURABLE_CORRECT_PAIR_NON_IDENTIFIABLE"}
            if identifiable:
                for role, prefix in (("selection", "mind"), ("audit", "ngf")):
                    entry = next((r for r in frame[role]["temporal_controls"] if r["moving_time"] == other_index), None)
                    if entry is not None:
                        record[f"{prefix}_score"] = entry["score"]
                        record[f"{prefix}_margin"] = entry["margin"]
                record["status"] = "MEASURED" if record["mind_score"] is not None and record["ngf_score"] is not None else "UNAVAILABLE_SUPPORT"
            controls.append(record)
    identifiable = [i for i, frame in enumerate(frames) if frame["classification"] == "IDENTIFIABLE"]
    residuals = [block["residual_px"] for frame in frames if frame["audit"] is not None
                 for block in frame["audit"]["blocks"] if block["residual_px"] is not None]
    aggregate = summary(residuals)
    minimum = config["minimum_identifiable_holdout_frames"] if holdout else config["minimum_identifiable_development_frames"]
    if len(identifiable) < minimum:
        status = "BLOCKED_MODALITY_INFORMATION_INSUFFICIENT"
    elif any(frames[i]["status"] == "BLOCKED_MODALITY_INFORMATION_INSUFFICIENT" for i in identifiable):
        status = "BLOCKED_MODALITY_INFORMATION_INSUFFICIENT"
    elif any(frames[i]["status"] == "BLOCKED_MULTIMODAL_METRIC_DISCORDANCE" for i in identifiable):
        status = "BLOCKED_MULTIMODAL_METRIC_DISCORDANCE"
    elif any(frames[i]["status"] != "PASS" for i in identifiable):
        status = "BLOCKED_IDENTITY_NOT_DISCRIMINATIVE"
    elif not metrics_pass(aggregate, config):
        status = "BLOCKED_MULTIMODAL_METRIC_DISCORDANCE"
    else:
        status = "PASS"
    underlying = status
    if holdout and status != "PASS":
        status = "BLOCKED_INTERNAL_VALIDATION"
    return {"status": status, "underlying_status": underlying, "offset": [0, 0] if status == "PASS" else None,
            "matrix": identity_matrix() if status == "PASS" else None, "inverse": identity_matrix() if status == "PASS" else None,
            "mapping_updated": False, "per_frame": frames, "temporal_controls": controls, "aggregate": aggregate,
            "identifiable_frames": identifiable, "non_identifiable_frames": [i for i in range(count) if i not in identifiable],
            "validation_kind": "internal_temporal_same_acquisition" if holdout else None,
            "admissible_mappings": [[0, 0]], "negative_control_count_per_identifiable_frame_per_metric": 48,
            "units": "native_pixels", "rectangle_roi": None, "numerical_identity_roundtrip_px": 0}


def _dimensions(pair_name, pairs, holdout):
    if pair_name not in DIMENSIONS:
        raise SoluteRegistrationError("only the two authorized relative-solute pairs exist")
    if len(pairs) != (2 if holdout else 3):
        raise SoluteRegistrationError("wrong frozen temporal observation count")
    return all(reference.luminance.shape == moving.luminance.shape == DIMENSIONS[pair_name] for reference, moving in pairs)


def evaluate_development(pair_name, pairs, config):
    if not _dimensions(pair_name, pairs, False):
        return {"status": "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE", "offset": None, "matrix": None, "inverse": None, "per_frame": []}
    result = evaluate_series(pairs, config)
    result["pair"] = pair_name
    return result


def evaluate_holdout(pair_name, pairs, frozen_offset, config):
    if not isinstance(frozen_offset, (list, tuple)) or len(frozen_offset) != 2 or any(type(x) is not int for x in frozen_offset) or list(frozen_offset) != [0, 0]:
        raise SoluteRegistrationError("holdout accepts only the previously frozen exact integer identity")
    if not _dimensions(pair_name, pairs, True):
        return {"status": "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE", "offset": None, "matrix": None, "inverse": None, "per_frame": []}
    result = evaluate_series(pairs, config, holdout=True)
    result.update(pair=pair_name, frozen_offset=[0, 0])
    return result
