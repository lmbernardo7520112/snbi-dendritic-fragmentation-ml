"""Compose the unchanged tracked-data policy and three-domain phase audit.

Checkout identity may be standalone or an authenticated linked worktree.
Only index names and governed source/configuration text are examined; this
composition grants no scientific, data, DEV/TEST or publication authority.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

try:
    import check_phase_scope as phase_scope
    import check_repository_data as repository_data
except ModuleNotFoundError:
    from scripts import check_phase_scope as phase_scope
    from scripts import check_repository_data as repository_data


ROOT = Path(__file__).resolve().parents[1]


def audit(root: Path = ROOT) -> dict:
    """Require the immutable data policy before inspecting phase-scoped text."""
    report = {
        "audit": "study3_governance", "checkout_kind": None,
        "data_guard_status": "NOT_RUN", "phase_scope_status": "NOT_RUN",
        "experimental_content_bytes_read": 0, "status": "BLOCKED", "violations": [],
    }
    try:
        kind = phase_scope.require_supported_checkout(root)
        if kind not in {"STANDALONE", "LINKED_WORKTREE"}:
            raise ValueError("unsupported checkout identity")
        report["checkout_kind"] = kind
        inventory = phase_scope.read_index_inventory(root)
        entries = [(entry["git_mode"], entry["path"]) for entry in inventory]
        data = repository_data.audit_entries(entries)
        report["data_guard"] = data
        report["data_guard_status"] = data["status"]
        if data["status"] != "PASS" or data.get("content_bytes_read") != 0:
            report["violations"].append("immutable tracked-data policy blocked")
            return report
        phase = phase_scope.audit(root=root)
        report["phase_scope"] = phase
        report["phase_scope_status"] = phase["status"]
        if phase["status"] != "PASS" or phase.get("experimental_content_bytes_read") != 0:
            report["violations"].append("composed phase scope blocked")
            return report
        report["status"] = "PASS"
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, subprocess.SubprocessError) as exc:
        report["violations"].append("governance audit unavailable: " + type(exc).__name__)
    return report


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
