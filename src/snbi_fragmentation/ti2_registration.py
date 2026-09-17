"""Deterministic TI-2 correspondence measurement and frozen registration.

No file access or media decoding occurs here. Arrays supplied by the caller
are never modified. NumPy/SciPy are imported only by the optional array engine;
parameter fitting and validation use the standard library. Correspondence
thresholds and method choices must be frozen before experimental observations.
"""

from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
import math
from statistics import median
from typing import Any

from . import ti2_geometry as geometry


class RegistrationError(geometry.GeometryContractError):
    """Evidence is insufficient or registration violates a frozen contract."""


@dataclass(frozen=True)
class RegistrationConfig:
    patch_radius: int = 15
    search_radius: int = 7
    grid_rows: int = 5
    grid_cols: int = 7
    min_ncc: float = 0.60
    min_uniqueness: float = 0.08
    uniqueness_exclusion_radius: int = 2
    max_reverse_error_px: float = 0.75
    min_matches: int = 12
    min_coverage_fraction: float = 0.35
    max_coarse_translation_px: int = 48
    mutual_information_bins: int = 32

    def __post_init__(self):
        for name in ("patch_radius", "search_radius", "grid_rows", "grid_cols", "min_matches", "max_coarse_translation_px", "mutual_information_bins"):
            value = getattr(self, name)
            if type(value) is not int or value <= 0:
                raise RegistrationError(f"invalid frozen configuration: {name}")
        if self.search_radius <= self.uniqueness_exclusion_radius or self.uniqueness_exclusion_radius < 0:
            raise RegistrationError("search must include competitors beyond the excluded peak neighborhood")
        if not 0 < self.min_ncc <= 1 or not 0 < self.min_uniqueness <= 2:
            raise RegistrationError("invalid confidence threshold")
        if not 0 < self.min_coverage_fraction <= 1 or not math.isfinite(self.max_reverse_error_px) or self.max_reverse_error_px < 0:
            raise RegistrationError("invalid spatial support threshold")


DEFAULT_CONFIG = RegistrationConfig()


@dataclass(frozen=True)
class FrozenRegistration:
    condition: str
    transform_class: str
    matrix: tuple
    inverse: tuple
    estimation_indices: tuple[int, ...]
    estimation_summary_json: str
    selection_history_json: str
    config: RegistrationConfig
    estimation_aggregate_json: str = "{}"

    def as_dict(self) -> dict[str, Any]:
        import json
        return {
            "condition": self.condition, "transform_class": self.transform_class,
            "matrix": self.matrix, "inverse": self.inverse,
            "estimation_indices": self.estimation_indices,
            "estimation_metrics": json.loads(self.estimation_summary_json),
            "estimation_aggregate": json.loads(self.estimation_aggregate_json),
            "selection_history": json.loads(self.selection_history_json),
            "method_config": asdict(self.config),
            "parameter_status": "FROZEN_BEFORE_VALIDATION",
        }


def _runtime():
    try:
        import numpy as np
        from scipy import ndimage, signal
    except ImportError as exc:
        raise RegistrationError("optional numerical runtime is unavailable; no installation is attempted") from exc
    return np, ndimage, signal


def _feature(image, mask, np, ndimage):
    values = np.asarray(image)
    if values.ndim != 2 or not np.issubdtype(values.dtype, np.number) or not np.isfinite(values).all():
        raise RegistrationError("native luminance must be a finite two-dimensional numeric array")
    if mask is None:
        valid = np.ones(values.shape, dtype=bool)
    else:
        valid = np.asarray(mask)
        if valid.shape != values.shape or valid.dtype != np.bool_:
            raise RegistrationError("support mask must be boolean with the native image shape")
    safe = values.astype(np.float64, copy=True)
    safe[~valid] = 0
    # The 3x3 Sobel footprint must not touch a masked overlay or native border.
    support = ndimage.binary_erosion(valid, structure=np.ones((3, 3), dtype=bool), border_value=0)
    gradient = np.hypot(ndimage.sobel(safe, axis=1), ndimage.sobel(safe, axis=0))
    gradient[~support] = 0
    return gradient, support


def _phase_translation(reference, moving, reference_mask, moving_mask, np):
    height = max(reference.shape[0], moving.shape[0])
    width = max(reference.shape[1], moving.shape[1])
    arrays = []
    for feature, mask in ((reference, reference_mask), (moving, moving_mask)):
        if not mask.any() or float(feature[mask].std()) < 1e-12:
            return None
        centered = np.zeros((height, width), dtype=np.float64)
        local = (feature - feature[mask].mean()) * mask
        local *= np.hanning(feature.shape[0])[:, None] * np.hanning(feature.shape[1])[None, :]
        centered[:feature.shape[0], :feature.shape[1]] = local
        arrays.append(np.fft.rfft2(centered))
    spectrum = arrays[0] * arrays[1].conj()
    modulus = np.abs(spectrum)
    normalized = np.zeros_like(spectrum)
    np.divide(spectrum, modulus, out=normalized, where=modulus > 1e-12)
    correlation = np.fft.irfft2(normalized, s=(height, width))
    y, x = np.unravel_index(np.argmax(correlation), correlation.shape)
    dx = int(x if x <= width // 2 else x - width)
    dy = int(y if y <= height // 2 else y - height)
    return dx, dy


def _window_sums(values, side, np):
    integral = np.pad(values.cumsum(axis=0).cumsum(axis=1), ((1, 0), (1, 0)))
    return integral[side:, side:] - integral[:-side, side:] - integral[side:, :-side] + integral[:-side, :-side]


def _match_patch(template_feature, search_feature, template_mask, search_mask, template_point, expected_point, config, np, signal):
    radius, search = config.patch_radius, config.search_radius
    tx, ty = (int(round(value)) for value in template_point)
    ex, ey = (int(round(value)) for value in expected_point)
    side = 2 * radius + 1
    th, tw = template_feature.shape
    sh, sw = search_feature.shape
    if tx - radius < 0 or ty - radius < 0 or tx + radius >= tw or ty + radius >= th:
        return None, "template_outside_native_support"
    if not template_mask[ty - radius:ty + radius + 1, tx - radius:tx + radius + 1].all():
        return None, "template_masked"
    left, top = ex - radius - search, ey - radius - search
    right, bottom = ex + radius + search + 1, ey + radius + search + 1
    if left < 0 or top < 0 or right > sw or bottom > sh:
        return None, "search_outside_native_support"
    template = template_feature[ty - radius:ty + radius + 1, tx - radius:tx + radius + 1]
    template = template - template.mean()
    energy = float((template * template).sum())
    if energy < 1e-12:
        return None, "uninformative_template"
    region = search_feature[top:bottom, left:right]
    local_sum = _window_sums(region, side, np)
    local_square = _window_sums(region * region, side, np)
    variance = np.maximum(local_square - local_sum * local_sum / (side * side), 0)
    numerator = signal.fftconvolve(region, template[::-1, ::-1], mode="valid")
    denominator = np.sqrt(energy * variance)
    scores = np.full(numerator.shape, -np.inf)
    supported = _window_sums(search_mask[top:bottom, left:right].astype(np.int64), side, np) == side * side
    np.divide(numerator, denominator, out=scores, where=(denominator > 1e-12) & supported)
    py, px = (int(value) for value in np.unravel_index(np.argmax(scores), scores.shape))
    peak = float(scores[py, px])
    if not math.isfinite(peak) or peak < config.min_ncc:
        return None, "weak_ncc"
    if px in (0, scores.shape[1] - 1) or py in (0, scores.shape[0] - 1):
        return None, "unbracketed_peak"
    competitors = scores.copy()
    exclusion = config.uniqueness_exclusion_radius
    competitors[max(0, py - exclusion):py + exclusion + 1, max(0, px - exclusion):px + exclusion + 1] = -np.inf
    second = float(competitors.max())
    if not math.isfinite(second):
        return None, "no_supported_competitor"
    gap = peak - second
    if gap < config.min_uniqueness:
        return None, "ambiguous_peak"

    def quadratic(before, center, after):
        if not all(math.isfinite(float(value)) for value in (before, center, after)):
            return None
        curvature = before - 2 * center + after
        if curvature >= -1e-12:
            return None
        delta = 0.5 * (before - after) / curvature
        return float(delta) if abs(delta) <= 0.5 else None

    delta_x = quadratic(scores[py, px - 1], peak, scores[py, px + 1])
    delta_y = quadratic(scores[py - 1, px], peak, scores[py + 1, px])
    if delta_x is None or delta_y is None:
        return None, "subpixel_peak_not_supported"
    return {"point": [left + radius + px + delta_x, top + radius + py + delta_y], "ncc": min(1.0, peak), "uniqueness": gap}, None


def _mutual_information(reference, moving, reference_mask, moving_mask, shift, config, np):
    dx, dy = shift
    # Deterministic diagnostic in the integer-overlap region; never a fit score.
    x0, x1 = max(0, dx), min(reference.shape[1], moving.shape[1] + dx)
    y0, y1 = max(0, dy), min(reference.shape[0], moving.shape[0] + dy)
    if x0 >= x1 or y0 >= y1:
        return None
    a = np.asarray(reference)[y0:y1:4, x0:x1:4]
    b = np.asarray(moving)[y0 - dy:y1 - dy:4, x0 - dx:x1 - dx:4]
    valid = reference_mask[y0:y1:4, x0:x1:4] & moving_mask[y0 - dy:y1 - dy:4, x0 - dx:x1 - dx:4]
    if valid.sum() < 64 or float(a[valid].std()) < 1e-12 or float(b[valid].std()) < 1e-12:
        return None
    counts = np.histogram2d(a[valid], b[valid], bins=config.mutual_information_bins)[0]
    joint = counts / counts.sum()
    product = joint.sum(axis=1)[:, None] * joint.sum(axis=0)[None, :]
    nonzero = joint > 0
    return float((joint[nonzero] * np.log(joint[nonzero] / product[nonzero])).sum())


def _coverage(matches, shape):
    if not matches:
        return (0.0, 0.0)
    xs = [match["reference"][0] for match in matches]
    ys = [match["reference"][1] for match in matches]
    return ((max(xs) - min(xs)) / shape[1], (max(ys) - min(ys)) / shape[0])


def pair_measurements(reference_y, moving_y, reference_mask=None, moving_mask=None, *, config=None):
    """Measure independent native-center correspondences on a fixed spatial grid.

    Forward/reverse NCC, uniqueness and spatial support are checked before any
    transform is fitted. No matches are discarded based on a fitted residual.
    The returned PASS establishes measurement sufficiency only, never a gate.
    """
    config = DEFAULT_CONFIG if config is None else config
    np, ndimage, signal = _runtime()
    reference, rmask = _feature(reference_y, reference_mask, np, ndimage)
    moving, mmask = _feature(moving_y, moving_mask, np, ndimage)
    diagnostics = {
        "reference_shape_hw": list(reference.shape), "moving_shape_hw": list(moving.shape),
        "config": asdict(config), "coarse_translation_xy": None,
        "mutual_information_nats": None, "mutual_information_role": "diagnostic_only",
    }
    shift = _phase_translation(reference, moving, rmask, mmask, np)
    if shift is None or max(abs(value) for value in shift) > config.max_coarse_translation_px:
        diagnostics["reason"] = "uninformative_content_or_coarse_displacement_outside_frozen_search"
        return {"status": "BLOCKED", "matches": [], "diagnostics": diagnostics}
    diagnostics["coarse_translation_xy"] = list(shift)
    diagnostics["mutual_information_nats"] = _mutual_information(reference_y, moving_y, rmask, mmask, shift, config, np)
    margin = config.patch_radius + config.search_radius + max(abs(value) for value in shift) + 2
    height, width = reference.shape
    if min(height, width) <= 2 * margin:
        diagnostics["reason"] = "insufficient_spatial_extent"
        return {"status": "BLOCKED", "matches": [], "diagnostics": diagnostics}
    xs = np.rint(np.linspace(margin, width - margin - 1, config.grid_cols)).astype(int)
    ys = np.rint(np.linspace(margin, height - margin - 1, config.grid_rows)).astype(int)
    matches, rejections = [], Counter()
    for y in ys:
        for x in xs:
            forward, reason = _match_patch(reference, moving, rmask, mmask, (x, y), (x - shift[0], y - shift[1]), config, np, signal)
            if forward is None:
                rejections[reason] += 1
                continue
            mx, my = forward["point"]
            rounded = (round(mx), round(my))
            reverse, reason = _match_patch(moving, reference, mmask, rmask, rounded, (x, y), config, np, signal)
            if reverse is None:
                rejections["reverse_" + reason] += 1
                continue
            expected = (x + rounded[0] - mx, y + rounded[1] - my)
            reverse_error = math.hypot(reverse["point"][0] - expected[0], reverse["point"][1] - expected[1])
            if reverse_error > config.max_reverse_error_px:
                rejections["inconsistent_forward_reverse_match"] += 1
                continue
            matches.append({
                "reference": [int(x), int(y)], "moving": [mx, my],
                "ncc": min(forward["ncc"], reverse["ncc"]),
                "uniqueness": min(forward["uniqueness"], reverse["uniqueness"]),
                "reverse_error_px": reverse_error,
            })
    coverage = _coverage(matches, reference.shape)
    sufficient = len(matches) >= config.min_matches and min(coverage) >= config.min_coverage_fraction
    diagnostics.update({"accepted_count": len(matches), "candidate_count": len(xs) * len(ys), "rejections": dict(sorted(rejections.items())), "coverage_xy_fraction": list(coverage)})
    if not sufficient:
        diagnostics["reason"] = "insufficient_strong_unique_spatially_distributed_matches"
    return {"status": "PASS" if sufficient else "BLOCKED", "matches": matches, "diagnostics": diagnostics}


def _checked_matches(measurement, config):
    if measurement.get("status") != "PASS":
        raise RegistrationError("independent correspondence measurement is BLOCKED")
    matches = measurement.get("matches", [])
    if len(matches) < config.min_matches:
        raise RegistrationError("insufficient independently accepted correspondences")
    for match in matches:
        for key in ("moving", "reference"):
            if len(match[key]) != 2 or not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) for value in match[key]):
                raise RegistrationError("invalid native-center correspondence")
        for key in ("ncc", "uniqueness", "reverse_error_px"):
            if not isinstance(match.get(key), (int, float)) or not math.isfinite(match[key]):
                raise RegistrationError("missing finite confidence evidence")
        if not config.min_ncc <= match["ncc"] <= 1 or match["uniqueness"] < config.min_uniqueness or not 0 <= match["reverse_error_px"] <= config.max_reverse_error_px:
            raise RegistrationError("weak, ambiguous or nonreciprocal correspondence")
    shape = measurement.get("diagnostics", {}).get("reference_shape_hw")
    if not isinstance(shape, (list, tuple)) or len(shape) != 2 or any(type(value) is not int or value <= 0 for value in shape):
        raise RegistrationError("native support dimensions are required")
    if any(not (0 <= match["reference"][0] < shape[1] and 0 <= match["reference"][1] < shape[0]) for match in matches):
        raise RegistrationError("reference correspondence is outside native support")
    if min(_coverage(matches, shape)) < config.min_coverage_fraction:
        raise RegistrationError("correspondences lack distributed spatial support")
    return matches


def _frame_metrics(matrix, matches):
    distances = []
    for match in matches:
        x, y = geometry.transform_point(matrix, match["moving"])
        distances.append(math.hypot(x - match["reference"][0], y - match["reference"][1]))
    inverse = geometry.invert_matrix(matrix)
    roundtrip = geometry.roundtrip_error(matrix, inverse, (match["moving"] for match in matches))
    return geometry.evaluate_residuals(distances, roundtrip), distances


def _procrustes(matches, with_scale):
    count = len(matches)
    mx = sum(match["moving"][0] for match in matches) / count
    my = sum(match["moving"][1] for match in matches) / count
    rx = sum(match["reference"][0] for match in matches) / count
    ry = sum(match["reference"][1] for match in matches) / count
    dot, cross, energy = 0.0, 0.0, 0.0
    for match in matches:
        x, y = match["moving"][0] - mx, match["moving"][1] - my
        u, v = match["reference"][0] - rx, match["reference"][1] - ry
        dot += x * u + y * v
        cross += x * v - y * u
        energy += x * x + y * y
    norm = math.hypot(dot, cross)
    if energy <= 1e-12 or norm <= 1e-12:
        raise RegistrationError("independent geometry is degenerate for rigid/similarity fitting")
    scale = norm / energy if with_scale else 1.0
    a, b = scale * dot / norm, scale * cross / norm
    return ((a, -b, rx - a * mx + b * my), (b, a, ry - b * mx - a * my), (0.0, 0.0, 1.0))


def fit_registration(estimation_frames, condition, *, config=None, maximum_class="similarity", border_crop_evidence=None):
    """Select the simplest adequate static transform using only three frames.

    All accepted correspondences are retained. Each estimation instant and the
    pooled set must satisfy the frozen limits; neither pooled means nor small
    per-frame samples can hide a failure. Affine requires explicit evidence and
    is never silently fitted here. Returned parameters are immutable.
    """
    import json
    config = DEFAULT_CONFIG if config is None else config
    if condition not in geometry.ESTIMATION_INDICES:
        raise RegistrationError("unknown experimental condition")
    indices = geometry.ESTIMATION_INDICES[condition]
    if set(estimation_frames) != set(indices) or any(type(index) is not int for index in estimation_frames):
        raise RegistrationError("REG-201: only the exact three estimation indices may fit parameters")
    if maximum_class not in ("subpixel_translation", "rigid", "similarity"):
        raise RegistrationError("maximum fit class is outside this frozen estimator")
    by_frame = {index: _checked_matches(estimation_frames[index], config) for index in indices}
    pooled = [match for index in indices for match in by_frame[index]]
    dx = median(match["reference"][0] - match["moving"][0] for match in pooled)
    dy = median(match["reference"][1] - match["moving"][1] for match in pooled)

    def translation(x, y):
        return ((1.0, 0.0, float(x)), (0.0, 1.0, float(y)), (0.0, 0.0, 1.0))

    candidates = [("identity", translation(0, 0))]
    history = []
    if border_crop_evidence is not None:
        if not isinstance(border_crop_evidence, Mapping) or not isinstance(border_crop_evidence.get("evidence"), str) or not border_crop_evidence["evidence"].strip():
            raise RegistrationError("border crop requires an explicit independent geometric audit")
        offsets = border_crop_evidence.get("offset_xy")
        if not isinstance(offsets, (list, tuple)) or len(offsets) != 2 or any(type(value) is not int or value > 0 for value in offsets):
            raise RegistrationError("border crop requires nonpositive integer native offsets")
        candidates.append(("border_crop", translation(*offsets)))
    candidates.extend((("integer_translation", translation(round(dx), round(dy))), ("subpixel_translation", translation(dx, dy))))
    if maximum_class in ("rigid", "similarity"):
        candidates.append(("rigid", _procrustes(pooled, False)))
    if maximum_class == "similarity":
        candidates.append(("similarity", _procrustes(pooled, True)))
    for transform_class, matrix in candidates:
        if transform_class == "integer_translation" and border_crop_evidence is None:
            history.append({"class": "border_crop", "status": "NOT_EVALUATED", "reason": "no independent border/padding evidence was supplied"})
        try:
            matrix = geometry.validate_transform(matrix, transform_class)
        except geometry.GeometryContractError as exc:
            raise RegistrationError(str(exc)) from exc
        metrics = {str(index): _frame_metrics(matrix, by_frame[index])[0] for index in indices}
        aggregate = _frame_metrics(matrix, pooled)[0]
        accepted = aggregate["status"] == "PASS" and all(metric["status"] == "PASS" for metric in metrics.values())
        history.append({"class": transform_class, "status": "PASS" if accepted else "REJECTED", "per_frame": metrics, "aggregate": aggregate})
        if accepted:
            return FrozenRegistration(condition, transform_class, matrix, geometry.invert_matrix(matrix), indices, json.dumps(metrics, sort_keys=True), json.dumps(history, sort_keys=True), config, json.dumps(aggregate, sort_keys=True))
    failure = RegistrationError("no allowed static candidate satisfies all estimation-frame limits; affine is not justified by independent evidence")
    failure.selection_history = history
    raise failure


def fit_translation(estimation_frames, condition, *, config=None, border_crop_evidence=None):
    return fit_registration(estimation_frames, condition, config=config, maximum_class="subpixel_translation", border_crop_evidence=border_crop_evidence)


def validate_registration(frozen_registration, validation_frames):
    """Measure held-out residuals without changing any frozen parameter."""
    frozen = frozen_registration
    if not isinstance(frozen, FrozenRegistration):
        raise RegistrationError("REG-201: validation requires immutable frozen parameters")
    indices = geometry.VALIDATION_INDICES[frozen.condition]
    if set(validation_frames) != set(indices) or any(type(index) is not int for index in validation_frames):
        raise RegistrationError("REG-201: validation requires the exact two reserved quartiles")
    per_frame, pooled, max_roundtrip = {}, [], 0.0
    for index in indices:
        try:
            matches = _checked_matches(validation_frames[index], frozen.config)
            metric, distances = _frame_metrics(frozen.matrix, matches)
            pooled.extend(distances)
            max_roundtrip = max(max_roundtrip, metric["roundtrip_max_px"])
            per_frame[str(index)] = metric
        except RegistrationError as exc:
            per_frame[str(index)] = {"status": "BLOCKED", "reason": str(exc), "count": 0}
    aggregate = geometry.evaluate_residuals(pooled, max_roundtrip) if pooled else {"status": "BLOCKED", "count": 0, "reason": "no valid independent validation correspondences"}
    passed = aggregate["status"] == "PASS" and all(metric["status"] == "PASS" for metric in per_frame.values())
    return {"status": "PASS" if passed else "BLOCKED", "per_frame": per_frame, "aggregate": aggregate, "matrix": frozen.matrix, "inverse": frozen.inverse, "validation_indices": list(indices), "refit_performed": False}
