"""Fail-closed active authority from pyproject.toml [tool.snbi] only.

Historical decisions, environment variables and documentary PASS results are
never sources of execution permission. This revision recognizes the closed
state only: a future scientific authorization requires a new author decision
and a reviewed change, not a truthy toggle in configuration.
"""

from __future__ import annotations

import os
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
CLOSED_STATE = {
    "ti2_execution": "TERMINAL_BLOCKED_CLOSED",
    "ti2_closeout_1": "PASS",
    "current_authorized_activity": "NONE_AWAITING_AUTHOR_DECISION",
    "ti2_execution_authorized": False,
    "ti2r_authorized": False,
    "ti3_plus_authorized": False,
}
BOUNDARY_STATE = {
    "authorized_branch": "feat/ti2-registration-calibration",
    "write_boundary": "repository-only-default-sandbox",
    "pilot_image_limit": 30,
    "blocked_phases": [f"TI-{phase}" for phase in range(3, 9)],
}


class AuthorityError(ValueError):
    """Missing, ambiguous or unsupported canonical authority."""


class ScientificExecutionBlocked(RuntimeError):
    """No scientific entry point is authorized in this revision."""


def validate_governance(governance: object) -> list[str]:
    """Check exact types and values; Python truthiness is never permission."""
    if type(governance) is not dict:
        return ["canonical tool.snbi table is missing or invalid"]
    expected = {**CLOSED_STATE, **BOUNDARY_STATE}
    violations = []
    for key, value in expected.items():
        if key not in governance:
            violations.append(f"canonical authority field missing: {key}")
        elif type(governance[key]) is not type(value) or governance[key] != value:
            violations.append(f"canonical authority field unsupported: {key}")
    for key in sorted(set(governance) - set(expected)):
        violations.append(f"unknown or competing authority field: {key}")
    return violations


def load_governance(root: Path = ROOT) -> dict:
    """Read only the canonical text file; never inspect scientific locations."""
    candidate = root / "pyproject.toml"
    if root.is_symlink() or candidate.is_symlink():
        raise AuthorityError("canonical authority symlink is prohibited")
    descriptor = os.open(candidate, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        project = tomllib.load(stream)
    tool = project.get("tool")
    governance = tool.get("snbi") if type(tool) is dict else None
    violations = validate_governance(governance)
    if violations:
        raise AuthorityError("; ".join(violations))
    return governance


def audit_authority(root: Path = ROOT) -> dict:
    """A coherent closed configuration passes the audit but denies execution."""
    violations = []
    try:
        load_governance(root)
    except (OSError, UnicodeError, ValueError) as exc:
        # Do not disclose paths, source locators or arbitrary malformed values.
        violations.append(f"canonical authority unavailable or invalid: {type(exc).__name__}")
    return {
        "status": "PASS" if not violations else "BLOCKED",
        "violations": violations,
        "authority_source": "pyproject.toml [tool.snbi]",
        "ti2_execution_authorized": False,
        "ti2r_authorized": False,
        "ti3_plus_authorized": False,
        "current_authorized_activity": (
            CLOSED_STATE["current_authorized_activity"] if not violations else "BLOCKED_INVALID_AUTHORITY"
        ),
        "scientific_readiness": "BLOCKED",
        "scientific_readiness_reason": "new author decision and reviewed authorization required",
    }


def require_scientific_authority(root: Path = ROOT) -> None:
    """Deny before any source examination, external tool or scientific call."""
    report = audit_authority(root)
    if report["status"] != "PASS":
        raise ScientificExecutionBlocked("TI2_EXECUTION_BLOCKED: invalid canonical authority")
    raise ScientificExecutionBlocked("TI2_EXECUTION_BLOCKED: terminally closed; new author decision required")
