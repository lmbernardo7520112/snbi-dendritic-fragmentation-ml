"""Exact elapsed and experimental times from approved textual metadata.

``physical_time`` is retained only as a deprecated alias of elapsed time. No
playback rate participates in either time calculation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, DecimalException
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


class TimeRuleError(ValueError):
    """Raised when the physical-time contract is invalid."""


_SOURCE_GROUPS = {
    "bottom-up": (("ESM1", "ESM2", "ESM3"), Decimal("-25.96")),
    "top-down": (("ESM4", "ESM5", "ESM6"), Decimal("-34.22")),
}
_SOURCE_IDS = frozenset(source for sources, _ in _SOURCE_GROUPS.values() for source in sources)


def _decimal(value) -> Decimal:
    try:
        result = Decimal(str(value))
    except (DecimalException, TypeError, ValueError) as exc:
        raise TimeRuleError("time values must be finite decimals") from exc
    if not result.is_finite():
        raise TimeRuleError("time values must be finite decimals")
    return result


def _source_offsets(data: dict) -> Mapping[str, Decimal]:
    """Build one immutable source-to-offset map from the complete config."""
    models = data.get("experimental_time_models")
    if not isinstance(models, dict) or set(models) != set(_SOURCE_GROUPS):
        raise TimeRuleError("both approved experimental time models are required")
    offsets = {}
    for condition, (expected_sources, approved_offset) in _SOURCE_GROUPS.items():
        model = models[condition]
        if not isinstance(model, dict) or not isinstance(model.get("source_ids"), list):
            raise TimeRuleError("each time model requires an explicit source ID list")
        offset = _decimal(model.get("offset_s"))
        if offset != approved_offset:
            raise TimeRuleError("experimental offset differs from the approved condition")
        for source in model["source_ids"]:
            if not isinstance(source, str) or source not in _SOURCE_IDS:
                raise TimeRuleError("unknown or missing source ID in time model")
            if source in offsets:
                raise TimeRuleError("duplicate source ID in time model")
            if source not in expected_sources:
                raise TimeRuleError("source ID assigned to the wrong experimental condition")
            offsets[source] = offset
    if set(offsets) != _SOURCE_IDS:
        raise TimeRuleError("time models must cover every ESM1–ESM6 source exactly once")
    applicability = data.get("applicability")
    if (not isinstance(applicability, list)
            or any(not isinstance(source, str) for source in applicability)
            or len(applicability) != len(_SOURCE_IDS)
            or set(applicability) != _SOURCE_IDS):
        raise TimeRuleError("time-rule applicability must cover ESM1–ESM6 exactly once")
    return MappingProxyType(offsets)


@dataclass(frozen=True)
class PhysicalTimeRule:
    delta_t_seconds: Decimal
    frame_index_origin: int
    time_origin_seconds: Decimal
    reported_fps_is_physical_time: bool
    source_offsets: Mapping[str, Decimal]

    @classmethod
    def from_mapping(cls, data: dict) -> "PhysicalTimeRule":
        if not isinstance(data, dict):
            raise TimeRuleError("time rule must be an object")
        try:
            rule = cls(
                delta_t_seconds=_decimal(data["delta_t_seconds"]),
                frame_index_origin=data["frame_index_origin"],
                time_origin_seconds=_decimal(data["time_origin_seconds"]),
                reported_fps_is_physical_time=data["reported_fps_is_physical_time"],
                source_offsets=_source_offsets(data),
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise TimeRuleError(f"invalid time rule: {exc}") from exc
        if rule.delta_t_seconds != Decimal("1.18") or _decimal(data.get("delta_t_s")) != rule.delta_t_seconds:
            raise TimeRuleError("approved frame interval must be exactly 1.18 seconds")
        if type(rule.frame_index_origin) is not int or rule.frame_index_origin != 0:
            raise TimeRuleError("TI-1 requires zero-based frame indexing")
        if rule.time_origin_seconds != Decimal("0"):
            raise TimeRuleError("elapsed time must start at zero")
        if rule.reported_fps_is_physical_time is not False:
            raise TimeRuleError("container FPS must not define physical time")
        if (data.get("time_model_status") != "DOCUMENTED_AND_RECONCILED"
                or data.get("time_zero_reference") != "solidification_front_entry_into_field_of_view"):
            raise TimeRuleError("experimental time must retain the reconciled front-entry origin")
        return rule

    def elapsed_time(self, frame_index: int) -> Decimal:
        """Return exact seconds elapsed from the first video frame."""
        if isinstance(frame_index, bool) or not isinstance(frame_index, int):
            raise TypeError("frame_index must be an integer")
        if frame_index < self.frame_index_origin:
            raise ValueError("frame_index precedes the time origin")
        return self.time_origin_seconds + (
            Decimal(frame_index - self.frame_index_origin) * self.delta_t_seconds
        )

    def experimental_time(self, source_id: str, frame_index: int) -> Decimal:
        """Return front-entry-relative time using the source's configured offset."""
        if not isinstance(source_id, str) or source_id not in self.source_offsets:
            raise TimeRuleError("source ID has no approved experimental time offset")
        return self.source_offsets[source_id] + self.elapsed_time(frame_index)

    def physical_time(self, frame_index: int) -> Decimal:
        """Deprecated elapsed-time alias; never the offset experimental time."""
        return self.elapsed_time(frame_index)

    def last_frame_time(self, frame_count: int) -> Decimal:
        if isinstance(frame_count, bool) or not isinstance(frame_count, int) or frame_count < 1:
            raise ValueError("frame_count must be a positive integer")
        return self.physical_time(frame_count - 1)

    def playback_acceleration(self, reported_fps: Decimal) -> Decimal:
        if reported_fps <= 0:
            raise ValueError("reported_fps must be positive")
        return reported_fps * self.delta_t_seconds


def load_time_rule(path: Path) -> tuple[dict, PhysicalTimeRule]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TimeRuleError(f"cannot read time rule: {exc}") from exc
    return data, PhysicalTimeRule.from_mapping(data)
