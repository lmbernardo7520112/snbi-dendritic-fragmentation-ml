"""Dependency-free geometry contracts for the authorized TI-2 pilot.

Coordinates are pixel centers in native index units: the top-left center is
``(0, 0)``, x increases rightward and y increases downward. Matrices map column
vectors from a modality to its clean-radiography reference. This module does
not read images, fit parameters, decide physical orientation from appearance,
or supply scientific evidence that the caller has not measured.
"""

from collections.abc import Iterable, Mapping, Sequence
import math
from numbers import Real
from typing import Any


Matrix = tuple[tuple[float, float, float], ...]
Point = tuple[float, float]
ROI = tuple[int, int, int, int]

TRANSFORM_HIERARCHY = (
    "identity", "border_crop", "integer_translation", "subpixel_translation",
    "rigid", "similarity", "affine",
)
ESTIMATION_INDICES = {"bottom-up": (0, 146, 293), "top-down": (0, 197, 394)}
VALIDATION_INDICES = {"bottom-up": (73, 219), "top-down": (98, 295)}
UNCERTAINTY_COMPONENTS = ("scale", "registration", "temporal", "discretization", "roi")

_TOLERANCE = 1e-9


class GeometryContractError(ValueError):
    """A blocking TI-2 geometry or calibration contract was violated."""


def _finite(value: Any, name: str, *, nonnegative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise GeometryContractError(f"{name} must be a finite real number")
    result = float(value)
    if not math.isfinite(result) or (nonnegative and result < 0):
        raise GeometryContractError(f"{name} must be finite and within its domain")
    return result


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GeometryContractError(f"{name} requires explicit documentary evidence")
    return value


def _close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=_TOLERANCE, abs_tol=_TOLERANCE)


def _matrix(matrix: Sequence[Sequence[Real]]) -> Matrix:
    try:
        rows = tuple(tuple(row) for row in matrix)
    except TypeError as exc:
        raise GeometryContractError("GEO-202: matrix must be 3x3") from exc
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise GeometryContractError("GEO-202: matrix must be 3x3")
    values = tuple(tuple(_finite(item, "matrix entry") for item in row) for row in rows)
    # Reject even a small projective component, rather than silently rounding it.
    if values[2] != (0.0, 0.0, 1.0):
        raise GeometryContractError("GEO-204: only affine homogeneous matrices are permitted")
    a, b, _ = values[0]
    c, d, _ = values[1]
    determinant = a * d - b * c
    if not math.isfinite(determinant) or abs(determinant) <= 1e-12:
        raise GeometryContractError("GEO-202: matrix is singular or numerically degenerate")
    return values


def validate_transform(
    matrix: Sequence[Sequence[Real]],
    transform_class: str,
    *,
    affine_evidence: str | None = None,
) -> Matrix:
    """Validate geometry and the declared class, returning an immutable matrix.

    The positive-axis test deliberately disallows 90-degree rotations and
    greater, including a 180-degree rotation that would reverse both axes
    despite having positive determinant. It is a conservative numeric check;
    physical gravity/growth/thermal metadata still require separate evidence.
    A caller must document why simpler hierarchy levels were insufficient.
    """
    if transform_class not in TRANSFORM_HIERARCHY:
        raise GeometryContractError("GEO-204: prohibited or unknown transformation class")
    result = _matrix(matrix)
    a, b, tx = result[0]
    c, d, ty = result[1]
    if a * d - b * c <= 0 or a <= 0 or d <= 0:
        raise GeometryContractError("GEO-205: reflection or axis reversal is prohibited")
    translation = _close(a, 1) and _close(b, 0) and _close(c, 0) and _close(d, 1)
    if transform_class in TRANSFORM_HIERARCHY[:4]:
        if not translation:
            raise GeometryContractError("GEO-203: declared class cannot contain rotation, shear or scale")
        if transform_class == "identity" and not (_close(tx, 0) and _close(ty, 0)):
            raise GeometryContractError("GEO-203: identity cannot translate")
        if transform_class in ("border_crop", "integer_translation"):
            if not (_close(tx, round(tx)) and _close(ty, round(ty))):
                raise GeometryContractError("GEO-203: integer transform cannot translate subpixels")
        if transform_class == "border_crop" and (tx > 0 or ty > 0):
            raise GeometryContractError("GEO-203: border removal uses nonpositive offsets")
    elif transform_class in ("rigid", "similarity"):
        first_norm = a * a + c * c
        second_norm = b * b + d * d
        if not _close(a * b + c * d, 0) or not _close(first_norm, second_norm):
            raise GeometryContractError("GEO-203: rigid/similarity cannot shear or scale axes differently")
        if transform_class == "rigid" and not _close(first_norm, 1):
            raise GeometryContractError("GEO-203: rigid transformation cannot change scale")
    else:
        _text(affine_evidence, "GEO-203: affine geometric evidence")
    return result


def invert_matrix(matrix: Sequence[Sequence[Real]]) -> Matrix:
    """Invert a nonsingular affine 3x3 matrix without a numerical dependency."""
    values = _matrix(matrix)
    a, b, tx = values[0]
    c, d, ty = values[1]
    determinant = a * d - b * c
    inverse = (
        (d / determinant, -b / determinant, (b * ty - d * tx) / determinant),
        (-c / determinant, a / determinant, (c * tx - a * ty) / determinant),
        (0.0, 0.0, 1.0),
    )
    return _matrix(inverse)


def transform_point(matrix: Sequence[Sequence[Real]], point: Sequence[Real]) -> Point:
    """Transform the ordered pair (x column, y row), with no rounding."""
    values = _matrix(matrix)
    try:
        coordinates = tuple(point)
    except TypeError as exc:
        raise GeometryContractError("GEO-201: point must contain x and y") from exc
    if len(coordinates) != 2:
        raise GeometryContractError("GEO-201: point must contain x and y")
    x, y = (_finite(value, "point coordinate") for value in coordinates)
    result = (
        values[0][0] * x + values[0][1] * y + values[0][2],
        values[1][0] * x + values[1][1] * y + values[1][2],
    )
    return tuple(_finite(value, "transformed coordinate") for value in result)


def roundtrip_error(
    matrix: Sequence[Sequence[Real]],
    inverse: Sequence[Sequence[Real]],
    points: Iterable[Sequence[Real]],
) -> float:
    """Maximum measured Euclidean error of T_inverse(T(point)), in pixels."""
    values, inverse_values = _matrix(matrix), _matrix(inverse)
    errors = []
    for point in points:
        original = tuple(point)
        returned = transform_point(inverse_values, transform_point(values, original))
        errors.append(math.hypot(returned[0] - original[0], returned[1] - original[1]))
    if not errors:
        raise GeometryContractError("REG-203: roundtrip requires at least one measured point")
    return max(errors)


def residual_statistics(residuals: Iterable[Real]) -> dict[str, float | int]:
    """Distances in pixels; quantiles interpolate at rank (n - 1) * p."""
    values = sorted(_finite(value, "residual", nonnegative=True) for value in residuals)
    if not values:
        raise GeometryContractError("REG-202: absent measurements cannot establish PASS")

    def quantile(probability: float) -> float:
        rank = (len(values) - 1) * probability
        low = math.floor(rank)
        high = math.ceil(rank)
        return values[low] + (rank - low) * (values[high] - values[low])

    return {
        "count": len(values),
        "median_px": quantile(0.5),
        "p95_px": quantile(0.95),
        "maximum_px": values[-1],
    }


def evaluate_residuals(residuals: Iterable[Real], roundtrip_max: Real) -> dict[str, Any]:
    """Apply the frozen 1/2/3/0.25 pixel limits, without tolerance relaxation."""
    result = dict(residual_statistics(residuals))
    result["roundtrip_max_px"] = _finite(roundtrip_max, "roundtrip maximum", nonnegative=True)
    limits = {"median_px": 1.0, "p95_px": 2.0, "maximum_px": 3.0, "roundtrip_max_px": 0.25}
    result["failures"] = [name for name, limit in limits.items() if result[name] > limit]
    result["status"] = "BLOCKED" if result["failures"] else "PASS"
    return result


def validate_estimation_validation(
    condition: str,
    estimation_indices: Iterable[int],
    validation_indices: Iterable[int],
) -> None:
    """Enforce the exact frozen sample partition, without assigning ML splits."""
    if condition not in ESTIMATION_INDICES:
        raise GeometryContractError("REG-201: unknown experimental condition")
    estimate, validate = tuple(estimation_indices), tuple(validation_indices)
    if any(type(index) is not int for index in estimate + validate):
        raise GeometryContractError("REG-201: frame indices must be integers")
    if estimate != ESTIMATION_INDICES[condition] or validate != VALIDATION_INDICES[condition]:
        raise GeometryContractError("REG-201: estimation and validation must use their frozen indices")


def _mask(mask: Iterable[Iterable[bool]]) -> tuple[tuple[bool, ...], ...]:
    try:
        rows = tuple(tuple(row) for row in mask)
    except TypeError as exc:
        raise GeometryContractError("ROI-201: support mask must be rectangular boolean rows") from exc
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise GeometryContractError("ROI-201: support mask must be a nonempty rectangle")
    if any(type(value) is not bool for row in rows for value in row):
        raise GeometryContractError("ROI-201: support mask entries must be boolean")
    return rows


def _roi(roi: Sequence[int]) -> ROI:
    try:
        values = tuple(roi)
    except TypeError as exc:
        raise GeometryContractError("ROI-201: ROI must be (x, y, width, height)") from exc
    if len(values) != 4 or any(type(value) is not int for value in values):
        raise GeometryContractError("ROI-201: ROI must have four integer coordinates")
    x, y, width, height = values
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise GeometryContractError("ROI-201: ROI must have positive area and nonnegative origin")
    return values


def largest_valid_rectangle(mask: Iterable[Iterable[bool]]) -> ROI:
    """Largest all-True rectangle, O(width * height), no experimental I/O.

    Return (x, y, width, height), where x/y name the first included pixel center
    and x+width/y+height are exclusive index limits. Area ties choose the
    lexicographically smallest (y, x, width, height), making the result stable.
    """
    rows = _mask(mask)
    heights = [0] * len(rows[0])
    best: ROI | None = None
    best_key: tuple[int, int, int, int, int] | None = None
    for y, row in enumerate(rows):
        heights = [height + 1 if value else 0 for height, value in zip(heights, row)]
        stack: list[tuple[int, int]] = []
        for x, height in enumerate(heights + [0]):
            left = x
            while stack and stack[-1][1] > height:
                start, old_height = stack.pop()
                width = x - start
                top = y - old_height + 1
                key = (-width * old_height, top, start, width, old_height)
                if best_key is None or key < best_key:
                    best = (start, top, width, old_height)
                    best_key = key
                left = start
            if height and (not stack or stack[-1][1] < height):
                stack.append((left, height))
    if best is None:
        raise GeometryContractError("ROI-201: no valid rectangular support exists")
    return best


def validate_roi(roi: Sequence[int], masks: Iterable[Iterable[Iterable[bool]]]) -> ROI:
    """Require every included center to be valid in every supplied pilot mask.

    The caller supplies one canonical support mask per modality and instant;
    manifest coverage of all 15 images per condition is checked separately.
    """
    result = _roi(roi)
    x, y, width, height = result
    count = 0
    for mask in masks:
        rows = _mask(mask)
        count += 1
        if x + width > len(rows[0]) or y + height > len(rows):
            raise GeometryContractError("ROI-201: ROI extends beyond native support")
        if any(not all(row[x:x + width]) for row in rows[y:y + height]):
            raise GeometryContractError("ROI-201: ROI contains at least one unsupported pixel")
    if count == 0:
        raise GeometryContractError("ROI-201: absent support evidence cannot establish PASS")
    return result


def validate_condition_rois(rois: Mapping[str, Sequence[int]]) -> None:
    """Require a separate ROI record for each experiment, never a global ROI."""
    if not isinstance(rois, Mapping) or set(rois) != set(ESTIMATION_INDICES):
        raise GeometryContractError("ROI-202: ROI must be recorded independently for each condition")
    for roi in rois.values():
        _roi(roi)


def unresolved_scale(reason: str) -> dict[str, Any]:
    """Explicit unresolved calibration with no implicit physical conversion."""
    return {
        "scale_status": "UNRESOLVED",
        "coordinate_unit": "pixel",
        "micrometres_per_pixel": None,
        "source": None,
        "method": None,
        "uncertainty_micrometres_per_pixel": None,
        "reason": _text(reason, "CAL-202: unresolved scale reason"),
    }


def validate_scale(record: Mapping[str, Any]) -> None:
    """Validate units and explicit provenance; never infer a physical scale."""
    if not isinstance(record, Mapping):
        raise GeometryContractError("CAL-201: calibration must be a record")
    status = record.get("scale_status")
    if status == "UNRESOLVED":
        if record.get("coordinate_unit") != "pixel" or record.get("micrometres_per_pixel") is not None:
            raise GeometryContractError("CAL-202: unresolved scale must remain in pixels")
        if record.get("uncertainty_micrometres_per_pixel") is not None:
            raise GeometryContractError("CAL-202: unresolved scale cannot claim a physical uncertainty")
        _text(record.get("reason"), "CAL-202: unresolved scale reason")
    elif status == "RESOLVED":
        if record.get("coordinate_unit") != "micrometre":
            raise GeometryContractError("CAL-201: resolved physical unit must be explicit")
        scale = _finite(record.get("micrometres_per_pixel"), "CAL-201: physical scale")
        if scale <= 0:
            raise GeometryContractError("CAL-201: physical scale must be positive")
        for key in ("source", "method", "applicability"):
            _text(record.get(key), f"CAL-201: {key}")
        _finite(record.get("uncertainty_micrometres_per_pixel"), "UNC-201: scale uncertainty", nonnegative=True)
    else:
        raise GeometryContractError("CAL-201: scale status must be RESOLVED or UNRESOLVED")


def to_physical_length(length_pixels: Real, scale: Mapping[str, Any]) -> float:
    """Convert a length only with validated scale evidence, without rounding."""
    validate_scale(scale)
    if scale["scale_status"] != "RESOLVED":
        raise GeometryContractError("CAL-202: physical conversion is blocked while scale is unresolved")
    length = _finite(length_pixels, "length in pixels", nonnegative=True)
    return _finite(length * scale["micrometres_per_pixel"], "physical length", nonnegative=True)


def validate_uncertainty_budget(budget: Mapping[str, Mapping[str, Any]]) -> None:
    """Require each uncertainty contribution to carry a value or explicit status.

    This validates completeness, not scientific adequacy. An unresolved budget
    must remain visible to the gate decision; it does not establish G3 PASS.
    """
    if not isinstance(budget, Mapping) or any(name not in budget for name in UNCERTAINTY_COMPONENTS):
        raise GeometryContractError("UNC-201: uncertainty budget is incomplete")
    for name in UNCERTAINTY_COMPONENTS:
        item = budget[name]
        if not isinstance(item, Mapping):
            raise GeometryContractError(f"UNC-201: invalid {name} uncertainty entry")
        status = item.get("status")
        if status in ("MEASURED", "MODELLED"):
            _finite(item.get("value"), f"UNC-201: {name} uncertainty", nonnegative=True)
            _text(item.get("unit"), f"UNC-201: {name} unit")
            _text(item.get("method"), f"UNC-201: {name} method")
            if status == "MODELLED":
                if item.get("evidence_kind") != "ANALYTICAL_ASSUMPTION":
                    raise GeometryContractError("UNC-201: modelled contribution needs an analytical assumption")
                _text(item.get("provenance"), f"UNC-201: {name} provenance")
                _text(item.get("analytical_assumption"), f"UNC-201: {name} analytical assumption")
            else:
                if item.get("evidence_kind") != "EMPIRICAL_MEASUREMENT":
                    raise GeometryContractError("UNC-201: measured contribution needs empirical measurement evidence")
                provenance = _text(item.get("provenance"), f"UNC-201: {name} empirical provenance")
                if (provenance.strip().casefold() in ("analytical_model", "analytical_assumption")
                        or "analytical_assumption" in item):
                    raise GeometryContractError("UNC-201: an analytical assumption is MODELLED, not MEASURED")
        elif status in ("UNRESOLVED", "NOT_APPLICABLE"):
            _text(item.get("reason"), f"UNC-201: {name} {status} justification")
        else:
            raise GeometryContractError(f"UNC-201: missing or unknown {name} uncertainty status")
