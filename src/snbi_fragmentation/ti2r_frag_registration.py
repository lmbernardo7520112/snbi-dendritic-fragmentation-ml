"""Frozen, pure in-memory TI2R-FRAG registration; no filesystem or source I/O.

The fit uses gradient NCC outside reserved evaluation tiles and their movement
envelope. Evaluation measures phase-correlation residuals on withheld native
luminance. Its observations are never fitted or removed for their residual.
"""

from dataclasses import dataclass
from itertools import product
import math


MODEL_ORDER = ("M0_IDENTITY", "M1_TRANSLATION", "M2_RIGID", "M3_AFFINE")


class FragRegistrationError(ValueError):
    """Frozen scientific input or configuration is invalid."""


def _runtime():
    import numpy as np
    from scipy import ndimage, optimize
    return np, ndimage, optimize


@dataclass(frozen=True)
class PreparedFrame:
    luminance: object
    gradient: object
    mask: object


def prepare(raw_bytes, width, height, config):
    """Interpret already-authorized YUV420p bytes, without opening a path."""
    np, ndimage, _ = _runtime()
    if type(width) is not int or type(height) is not int or min(width, height) < 64 or width % 2 or height % 2:
        raise FragRegistrationError("even native YUV420p dimensions are required")
    count = width * height
    if len(raw_bytes) != count * 3 // 2:
        raise FragRegistrationError("native byte count mismatch")
    planes = np.frombuffer(raw_bytes, dtype=np.uint8)
    luminance = planes[:count].reshape(height, width).astype(np.float64)
    u = planes[count:count + count // 4].reshape(height // 2, width // 2).astype(np.int16)
    v = planes[count + count // 4:].reshape(height // 2, width // 2).astype(np.int16)
    chroma = np.maximum(np.abs(u - 128), np.abs(v - 128)) >= config["chroma_distance_threshold"]
    overlay = chroma.repeat(2, axis=0).repeat(2, axis=1)
    halo = int(config["overlay_halo_px"])
    if halo:
        overlay = ndimage.maximum_filter(overlay, size=2 * halo + 1, mode="constant", cval=0)
    return prepare_luminance(luminance, ~overlay, config)


def prepare_luminance(luminance, valid_mask, config):
    """Pure helper also used by synthetic fixtures; never resizes a raster."""
    np, ndimage, _ = _runtime()
    values = np.asarray(luminance, dtype=np.float64)
    mask = np.asarray(valid_mask, dtype=bool).copy()
    if values.ndim != 2 or values.shape != mask.shape or not np.isfinite(values).all():
        raise FragRegistrationError("finite native luminance and matching mask required")
    height, width = values.shape
    border = int(config["native_border_px"])
    top = max(border, math.ceil(height * config["text_top_fraction"]))
    bottom = max(border, math.ceil(height * config["text_bottom_fraction"]))
    mask[:top] = False
    mask[height - bottom:] = False
    mask[:, :border] = False
    mask[:, width - border:] = False
    # Sobel requires an additional pixel; excluded colors/text cannot leak in.
    mask = ndimage.binary_erosion(mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
    gradient = np.hypot(ndimage.sobel(values, axis=0), ndimage.sobel(values, axis=1))
    gradient[~mask] = 0.0
    values = values.copy()
    values.setflags(write=False)
    gradient.setflags(write=False)
    mask.setflags(write=False)
    return PreparedFrame(values, gradient, mask)


def evaluation_tiles(shape, config):
    height, width = shape
    side = max(config["tile_min_side_px"], min(config["tile_max_side_px"], int(min(shape) * config["tile_side_fraction"])))
    side -= side % 2
    tiles = []
    for row, fy in enumerate(config["tile_y_fractions"]):
        for column, fx in enumerate(config["tile_x_fractions"]):
            cx, cy = int(round(fx * (width - 1))), int(round(fy * (height - 1)))
            x0, y0 = cx - side // 2, cy - side // 2
            if x0 < 0 or y0 < 0 or x0 + side > width or y0 + side > height:
                raise FragRegistrationError("frozen evaluation tile exceeds native extent")
            tiles.append({"id": f"r{row}c{column}", "xyxy": (x0, y0, x0 + side, y0 + side),
                          "quadrant": (int(cx >= width / 2), int(cy >= height / 2))})
    return tiles


def fitting_region(shape, reference_shape, config):
    """Exclude evaluation coordinates plus the entire permitted motion halo."""
    np, _, _ = _runtime()
    region = np.ones(shape, dtype=bool)
    halo = config["evaluation_exclusion_halo_px"]
    if halo < math.ceil(config["max_corner_displacement_px"]) + 2:
        raise FragRegistrationError("evaluation separation does not cover motion/interpolation footprint")
    for tile in evaluation_tiles(reference_shape, config):
        x0, y0, x1, y1 = tile["xyxy"]
        region[max(0, y0 - halo):min(shape[0], y1 + halo), max(0, x0 - halo):min(shape[1], x1 + halo)] = False
    return region


def checked_matrix(matrix, shape, config):
    np, _, _ = _runtime()
    value = np.asarray(matrix, dtype=np.float64)
    if value.shape != (3, 3) or not np.isfinite(value).all() or not np.array_equal(value[2], [0, 0, 1]):
        raise FragRegistrationError("only finite affine homogeneous matrices are permitted")
    determinant = float(np.linalg.det(value[:2, :2]))
    if determinant <= 0:
        raise FragRegistrationError("reflection, axis inversion or singular transform prohibited")
    h, w = shape
    corners = np.array([[0, 0, 1], [w - 1, 0, 1], [0, h - 1, 1], [w - 1, h - 1, 1]], dtype=float)
    mapped = corners @ value.T
    if float(np.max(np.linalg.norm(mapped[:, :2] - corners[:, :2], axis=1))) > config["max_corner_displacement_px"]:
        raise FragRegistrationError("candidate exceeds frozen motion envelope")
    inverse = np.linalg.inv(value)
    error = float(np.max(np.linalg.norm((mapped @ inverse.T)[:, :2] - corners[:, :2], axis=1)))
    if error > config["roundtrip_limit_px"]:
        raise FragRegistrationError("numerical roundtrip exceeds limit")
    return value, inverse, determinant, error


def _phase_shift(reference, moving, epsilon):
    np, _, _ = _runtime()
    window = np.hanning(reference.shape[0])[:, None] * np.hanning(reference.shape[1])[None, :]
    a = (reference - reference.mean()) * window
    b = (moving - moving.mean()) * window
    spectrum = np.fft.rfft2(a) * np.fft.rfft2(b).conj()
    if not np.any(np.abs(spectrum) > epsilon):
        raise FragRegistrationError("zero spectral information")
    normal = np.zeros_like(spectrum)
    np.divide(spectrum, np.abs(spectrum), out=normal, where=np.abs(spectrum) > epsilon)
    correlation = np.fft.irfft2(normal, s=reference.shape)
    py, px = (int(v) for v in np.unravel_index(np.argmax(correlation), correlation.shape))
    offsets = []
    for axis, index in ((1, px), (0, py)):
        n = correlation.shape[axis]
        center = float(correlation[py, px])
        before = float(correlation[py, (px - 1) % n] if axis == 1 else correlation[(py - 1) % n, px])
        after = float(correlation[py, (px + 1) % n] if axis == 1 else correlation[(py + 1) % n, px])
        curvature = before - 2 * center + after
        delta = 0.5 * (before - after) / curvature if curvature < -epsilon else 0.0
        delta = max(-0.5, min(0.5, delta))
        offsets.append(float(index if index <= n // 2 else index - n) + delta)
    return offsets


def _reference_information(reference, config):
    """Premetric reference-only rejection of aperture/periodic ambiguity."""
    np, ndimage, _ = _runtime()
    gx, gy = ndimage.sobel(reference, axis=1), ndimage.sobel(reference, axis=0)
    tensor = np.array([[np.mean(gx * gx), np.mean(gx * gy)], [np.mean(gx * gy), np.mean(gy * gy)]])
    eigenvalues = np.linalg.eigvalsh(tensor)
    ratio = float(eigenvalues[0] / eigenvalues[1]) if eigenvalues[1] > 1e-12 else 0.0
    if ratio < config["minimum_reference_gradient_eigenvalue_ratio"]:
        return "reference_aperture_ambiguity"
    centered = reference - reference.mean()
    spectrum = np.fft.rfft2(centered)
    autocorrelation = np.fft.irfft2(spectrum * spectrum.conj(), s=reference.shape)
    if autocorrelation[0, 0] <= 1e-12:
        return "reference_zero_spectrum"
    yy, xx = np.indices(reference.shape)
    lag_x = np.minimum(xx, reference.shape[1] - xx)
    lag_y = np.minimum(yy, reference.shape[0] - yy)
    nonlocal_lags = np.maximum(lag_x, lag_y) >= int(min(reference.shape) * config["reference_periodicity_min_lag_fraction"])
    maximum = float(autocorrelation[nonlocal_lags].max() / autocorrelation[0, 0])
    if maximum >= config["maximum_reference_periodic_autocorrelation"]:
        return "reference_periodic_ambiguity"
    return None


def _warped(frame, matrix, reference_shape):
    np, ndimage, _ = _runtime()
    yy, xx = np.indices(reference_shape, dtype=np.float64)
    inverse = np.linalg.inv(matrix)
    mx = inverse[0, 0] * xx + inverse[0, 1] * yy + inverse[0, 2]
    my = inverse[1, 0] * xx + inverse[1, 1] * yy + inverse[1, 2]
    image = ndimage.map_coordinates(frame.luminance, [my, mx], order=1, mode="constant", cval=0, prefilter=False)
    # Erode source support for the bilinear footprint, sample mask nearest.
    safe = ndimage.binary_erosion(frame.mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
    mask = ndimage.map_coordinates(safe.astype(np.uint8), [my, mx], order=0, mode="constant", cval=0, prefilter=False).astype(bool)
    return image, mask


def _summary(residuals, roundtrip, config):
    np, _, _ = _runtime()
    if not residuals:
        return {"status": "BLOCKED_REFERENCE_INSUFFICIENT", "count": 0, "median_px": None, "p95_px": None, "maximum_px": None, "roundtrip_max_px": roundtrip}
    values = np.asarray(residuals, dtype=float)
    median, p95, maximum = float(np.median(values)), float(np.percentile(values, 95)), float(values.max())
    passed = median <= config["median_limit_px"] and p95 <= config["p95_limit_px"] and maximum <= config["maximum_limit_px"] and roundtrip <= config["roundtrip_limit_px"]
    return {"status": "PASS" if passed else "FAIL_ABSOLUTE_RESIDUAL", "count": len(residuals), "median_px": median, "p95_px": p95, "maximum_px": maximum, "roundtrip_max_px": roundtrip}


def evaluate_pair(pairs, matrix, config):
    """Independent reserved-tile residuals; never refits or trims observations."""
    np, _, _ = _runtime()
    if not pairs:
        raise FragRegistrationError("at least one frame pair is required")
    checked, inverse, determinant, roundtrip = checked_matrix(matrix, pairs[0][1].luminance.shape, config)
    pooled, frames, common = [], [], None
    for frame_number, (reference, moving) in enumerate(pairs):
        checked_matrix(checked, moving.luminance.shape, config)
        warped, supported = _warped(moving, checked, reference.luminance.shape)
        support = reference.mask & supported
        denominator = int(reference.mask.sum())
        fraction = float(support.sum() / denominator) if denominator else 0.0
        common = support.copy() if common is None else common & support
        residuals, records, quadrants = [], [], set()
        for tile in evaluation_tiles(reference.luminance.shape, config):
            x0, y0, x1, y1 = tile["xyxy"]
            local = support[y0:y1, x0:x1]
            tile_fraction = float(local.mean())
            record = {"id": tile["id"], "xyxy": list(tile["xyxy"]), "quadrant": list(tile["quadrant"]), "support_fraction": tile_fraction}
            a = reference.luminance[y0:y1, x0:x1]
            b = warped[y0:y1, x0:x1]
            texture = float(a[local].std()) if local.any() else 0.0
            moving_texture = float(b[local].std()) if local.any() else 0.0
            if tile_fraction < config["minimum_tile_support_fraction"] or texture < config["minimum_reference_std_luma"] or moving_texture < config["minimum_moving_std_luma"]:
                reason = "support" if tile_fraction < config["minimum_tile_support_fraction"] else "reference_texture" if texture < config["minimum_reference_std_luma"] else "moving_texture"
                record.update({"status": "UNAVAILABLE_PREMETRIC", "reason": reason})
            else:
                # Fully supported tiles have no shared mask holes that could
                # create artificial alignment peaks. Reference information is
                # assessed before comparing to moving content or its residual.
                reference_reason = _reference_information(a, config)
                if reference_reason is not None:
                    record.update({"status": "UNAVAILABLE_PREMETRIC", "reason": reference_reason})
                    records.append(record)
                    continue
                try:
                    shift = _phase_shift(a, b, config["phase_spectrum_epsilon"])
                except FragRegistrationError:
                    record.update({"status": "UNAVAILABLE_PREMETRIC", "reason": "zero_spectral_information"})
                    records.append(record)
                    continue
                residual = math.hypot(*shift)
                record.update({"status": "MEASURED", "residual_xy_px": shift, "residual_px": residual})
                residuals.append(residual)
                quadrants.add(tuple(tile["quadrant"]))
            records.append(record)
        metric = _summary(residuals, roundtrip, config)
        coverage = len(residuals) >= config["minimum_reference_tiles_per_frame"] and len(quadrants) >= config["minimum_quadrants_per_frame"]
        if not coverage:
            metric["status"] = "BLOCKED_REFERENCE_INSUFFICIENT"
        elif fraction < config["minimum_support_fraction"]:
            metric["status"] = "FAIL_ABSOLUTE_SUPPORT"
        metric.update({"frame_position": frame_number, "support_fraction": fraction, "valid_tiles": len(residuals), "quadrants": len(quadrants), "tiles": records})
        frames.append(metric)
        pooled.extend(residuals)
    aggregate = _summary(pooled, roundtrip, config)
    if any(frame["status"] == "BLOCKED_REFERENCE_INSUFFICIENT" for frame in frames):
        status = "BLOCKED_REFERENCE_INSUFFICIENT"
    else:
        status = "PASS" if aggregate["status"] == "PASS" and all(frame["status"] == "PASS" for frame in frames) else "FAIL_ABSOLUTE_CRITERION"
    yy, xx = np.nonzero(common)
    box = [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1] if len(xx) else None
    return {"status": status, "aggregate": aggregate, "per_frame": frames, "determinant": determinant,
            "inverse": inverse.tolist(), "common_support": {"pixel_count": int(common.sum()), "bounding_box_xyxy": box,
            "rectangle_roi": None, "bounding_box_is_fully_supported_roi": False}, "reference": "independent_reserved_luminance_phase_tiles", "refit_performed": False}


def _fit_context(pairs, config):
    np, ndimage, _ = _runtime()
    context = []
    for reference, moving in pairs:
        shape = reference.luminance.shape
        rregion = fitting_region(shape, shape, config)
        mregion = fitting_region(moving.luminance.shape, shape, config)
        stride = config["fit_sample_stride_px"]
        yy, xx = np.indices(shape)
        selected = reference.mask & rregion & (xx % stride == 0) & (yy % stride == 0)
        y, x = np.nonzero(selected)
        if len(x) < config["min_fit_samples_per_frame"]:
            raise FragRegistrationError("insufficient fitting-only native samples")
        moving_fit = ndimage.binary_erosion(moving.mask & mregion, structure=np.ones((3, 3), dtype=bool), border_value=0)
        context.append((reference, moving, x.astype(float), y.astype(float), reference.gradient[y, x], moving_fit))
    return context


def _matrix_for(model, parameters, shape):
    np, _, _ = _runtime()
    center = np.array([(shape[1] - 1) / 2, (shape[0] - 1) / 2])
    if model == "M1_TRANSLATION":
        linear, translation = np.eye(2), np.asarray(parameters)
    elif model == "M2_RIGID":
        angle = math.radians(parameters[0])
        linear = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
        translation = np.asarray(parameters[1:])
    elif model == "M3_AFFINE":
        linear = np.eye(2) + np.asarray(parameters[:4]).reshape(2, 2) / 100.0
        translation = np.asarray(parameters[4:])
    else:
        return np.eye(3)
    result = np.eye(3)
    result[:2, :2] = linear
    result[:2, 2] = center + translation - linear @ center
    return result


def _fit_model(model, pairs, config, previous):
    np, ndimage, optimize = _runtime()
    context = _fit_context(pairs, config)
    shape = pairs[0][1].luminance.shape
    limit = config["translation_bound_px"]
    if model == "M1_TRANSLATION":
        shifts = []
        for reference, moving, _, _, _, mmask in context:
            h, w = reference.luminance.shape
            a = reference.gradient * reference.mask * fitting_region((h, w), (h, w), config)
            b = np.zeros((h, w))
            hh, ww = min(h, moving.luminance.shape[0]), min(w, moving.luminance.shape[1])
            b[:hh, :ww] = (moving.gradient * mmask)[:hh, :ww]
            shifts.append(_phase_shift(a, b, config["phase_spectrum_epsilon"]))
        initial = np.clip(np.median(shifts, axis=0), -limit, limit)
        bounds = [(-limit, limit)] * 2
    elif model == "M2_RIGID":
        initial = [0.0, float(previous[0, 2]), float(previous[1, 2])]
        bounds = [(-config["rotation_bound_degrees"], config["rotation_bound_degrees"])] + [(-limit, limit)] * 2
    else:
        center = np.array([(shape[1] - 1) / 2, (shape[0] - 1) / 2])
        translation = previous[:2, 2] - center + previous[:2, :2] @ center
        initial = list(((previous[:2, :2] - np.eye(2)) * 100).ravel()) + list(translation)
        coefficient = config["affine_coefficient_bound_percent"]
        bounds = [(-coefficient, coefficient)] * 4 + [(-limit, limit)] * 2
    def objective(parameters):
        matrix = _matrix_for(model, parameters, shape)
        try:
            _, inverse, _, _ = checked_matrix(matrix, shape, config)
        except FragRegistrationError:
            return 10.0
        scores = []
        for _, moving, x, y, reference_values, mask in context:
            mx = inverse[0, 0] * x + inverse[0, 1] * y + inverse[0, 2]
            my = inverse[1, 0] * x + inverse[1, 1] * y + inverse[1, 2]
            # A one-pixel erosion keeps interpolation entirely in fit support.
            good = ndimage.map_coordinates(mask.astype(np.uint8), [my, mx], order=0, mode="constant", cval=0, prefilter=False).astype(bool)
            if int(good.sum()) < config["min_fit_samples_per_frame"]:
                return 10.0
            sampled = ndimage.map_coordinates(moving.gradient, [my, mx], order=1, mode="constant", cval=0, prefilter=False)[good]
            a = reference_values[good] - reference_values[good].mean()
            b = sampled - sampled.mean()
            energy = math.sqrt(float(np.sum(a * a)) * float(np.sum(b * b)))
            if energy <= 1e-12:
                return 10.0
            scores.append(float(np.sum(a * b)) / energy)
        return 1.0 - sum(scores) / len(scores)
    # Fixed finite initialization grids use fitting pixels exclusively. They
    # are part of one model fit, not retries or post-validation refinements.
    initial = [min(high, max(low, float(value))) for value, (low, high) in zip(initial, bounds)]
    candidates = [list(initial)]
    if model == "M1_TRANSLATION":
        grid = np.arange(-limit, limit + 0.01, config["translation_initial_grid_step_px"])
        candidates.extend(list(point) for point in product(grid, repeat=2))
        radii = [config["translation_refinement_radius_px"]] * 2
    elif model == "M2_RIGID":
        bound = config["rotation_bound_degrees"]
        for angle in np.arange(-bound, bound + 0.0001, config["rotation_initial_grid_step_degrees"]):
            candidates.extend(([float(angle), 0.0, 0.0], [float(angle), float(initial[1]), float(initial[2])]))
        radii = [config["rotation_refinement_radius_degrees"]] + [config["translation_refinement_radius_px"]] * 2
    else:
        candidates.extend(list(point) + [0.0, 0.0] for point in product(config["affine_initial_grid_percent"], repeat=4))
        radii = [config["affine_refinement_radius_percent"]] * 4 + [config["translation_refinement_radius_px"]] * 2
    initial_scores = [objective(candidate) for candidate in candidates]
    best = int(np.argmin(initial_scores))
    initial = candidates[best]
    local_bounds = [(max(low, value - radius), min(high, value + radius)) for value, radius, (low, high) in zip(initial, radii, bounds)]
    fitted = optimize.minimize(objective, initial, method=config["optimizer"], bounds=local_bounds,
        options={"maxiter": config["optimizer_max_iterations"], "maxfev": config["optimizer_max_evaluations"], "xtol": config["optimizer_xtol"], "ftol": config["optimizer_ftol"]})
    improved = float(fitted.fun) <= initial_scores[best]
    matrix = _matrix_for(model, fitted.x if improved else initial, shape)
    checked_matrix(matrix, shape, config)
    return matrix, {"objective": float(fitted.fun) if improved else initial_scores[best], "optimizer_success": bool(fitted.success), "evaluations": int(fitted.nfev), "initial_grid_evaluations": len(candidates), "refinement_retained": improved, "iterations": int(fitted.nit), "fitting_frame_count": len(pairs)}


def fit_pair(development, config):
    """Joint static hierarchy on three development times; first PASS freezes."""
    np, _, _ = _runtime()
    if len(development) != 3 or tuple(config["model_order"]) != MODEL_ORDER:
        raise FragRegistrationError("exactly three development times and frozen M0-M3 order required")
    previous, history = np.eye(3), []
    for model in MODEL_ORDER:
        optimization = {"fit_performed": False}
        try:
            if model == "M0_IDENTITY":
                matrix = np.eye(3)
            else:
                matrix, optimization = _fit_model(model, development, config, previous)
            if model != "M0_IDENTITY":
                optimization["fit_performed"] = True
            metrics = evaluate_pair(development, matrix, config)
        except FragRegistrationError as exc:
            if "insufficient fitting" in str(exc) or "zero spectral" in str(exc):
                history.append({"model": model, "status": "BLOCKED_REFERENCE_INSUFFICIENT", "reason": str(exc), "optimization": optimization})
                return {"status": "BLOCKED_REFERENCE_INSUFFICIENT", "matrix": None, "inverse": None, "selected_model": None, "models_tested": history, "development": None}
            history.append({"model": model, "status": "FAIL_ADMISSIBLE_FIT", "reason": str(exc), "optimization": optimization, "development": None})
            continue
        history.append({"model": model, "status": metrics["status"], "matrix": matrix.tolist(), "optimization": optimization, "development": metrics})
        if metrics["status"] == "PASS":
            return {"status": "PASS", "matrix": matrix.tolist(), "inverse": metrics["inverse"], "selected_model": model, "models_tested": history, "development": metrics, "parameter_status": "FROZEN_BEFORE_VALIDATION"}
        if metrics["status"] == "BLOCKED_REFERENCE_INSUFFICIENT":
            return {"status": "BLOCKED_REFERENCE_INSUFFICIENT", "matrix": None, "inverse": None, "selected_model": None, "models_tested": history, "development": metrics}
        previous = matrix
    return {"status": "BLOCKED_METHOD_HIERARCHY", "matrix": None, "inverse": None, "selected_model": None, "models_tested": history, "development": history[-1]["development"]}


def validate_pair(validation, matrix, config):
    """Exactly two sealed times, after a static candidate has been frozen."""
    if len(validation) != 2:
        raise FragRegistrationError("exactly two reserved validation times required")
    result = evaluate_pair(validation, matrix, config)
    if result["status"] == "FAIL_ABSOLUTE_CRITERION":
        result["status"] = "BLOCKED_VALIDATION"
    return result
