"""Deterministic physical-time rule for the approved TI-1 scope."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


class TimeRuleError(ValueError):
    """Raised when the physical-time contract is invalid."""


@dataclass(frozen=True)
class PhysicalTimeRule:
    delta_t_seconds: Decimal
    frame_index_origin: int
    time_origin_seconds: Decimal
    reported_fps_is_physical_time: bool

    @classmethod
    def from_mapping(cls, data: dict) -> "PhysicalTimeRule":
        try:
            rule = cls(
                delta_t_seconds=Decimal(str(data["delta_t_seconds"])),
                frame_index_origin=int(data["frame_index_origin"]),
                time_origin_seconds=Decimal(str(data["time_origin_seconds"])),
                reported_fps_is_physical_time=bool(data["reported_fps_is_physical_time"]),
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise TimeRuleError(f"invalid time rule: {exc}") from exc
        if rule.delta_t_seconds <= 0:
            raise TimeRuleError("delta_t_seconds must be positive")
        if rule.frame_index_origin != 0:
            raise TimeRuleError("TI-1 requires zero-based frame indexing")
        if rule.reported_fps_is_physical_time:
            raise TimeRuleError("container FPS must not define physical time")
        return rule

    def physical_time(self, frame_index: int) -> Decimal:
        if isinstance(frame_index, bool) or not isinstance(frame_index, int):
            raise TypeError("frame_index must be an integer")
        if frame_index < self.frame_index_origin:
            raise ValueError("frame_index precedes the time origin")
        return self.time_origin_seconds + (
            Decimal(frame_index - self.frame_index_origin) * self.delta_t_seconds
        )

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
