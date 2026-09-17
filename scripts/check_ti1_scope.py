"""Fail closed if the repository crosses the authorized TI-1 boundary."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

try:
    from check_repository_data import audit_entries, classify_path, tracked_entries
except ModuleNotFoundError:
    from scripts.check_repository_data import audit_entries, classify_path, tracked_entries

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_PATHS = (
    "src/snbi_fragmentation/registration.py",
    "src/snbi_fragmentation/annotation.py",
    "src/snbi_fragmentation/dataset.py",
    "src/snbi_fragmentation/splits.py",
    "src/snbi_fragmentation/baseline.py",
    "src/snbi_fragmentation/models.py",
    "src/snbi_fragmentation/training.py",
    "src/snbi_fragmentation/evaluation.py",
)
BLOCKED_IMPORTS = ("cv2", "torch", "tensorflow", "keras", "av", "moviepy")


def audit(entries: list[tuple[str, str]] | None = None) -> dict:
    violations: list[str] = []
    try:
        inventory = tracked_entries() if entries is None else entries
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError):
        inventory = []
        violations.append("Git index inventory unavailable")
    indexed_paths = {path for _mode, path in inventory}
    for relative in BLOCKED_PATHS:
        if relative in indexed_paths:
            violations.append(f"blocked path exists: {relative}")

    data_report = audit_entries(inventory)
    violations.extend(
        f"repository guard violation: {item['path']}"
        for item in data_report["violations"]
    )

    for mode, relative in inventory:
        path = Path(relative)
        if not relative.startswith("src/") or path.suffix.casefold() != ".py":
            continue
        if classify_path(relative, mode):
            continue
        candidate = ROOT / path
        if candidate.is_symlink():
            violations.append(f"worktree symlink is prohibited: {relative}")
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            violations.append(f"tracked source unreadable: {relative}")
            continue
        for name in BLOCKED_IMPORTS:
            if f"import {name}" in text or f"from {name}" in text:
                violations.append(f"blocked TI-2+ import {name} in {relative}")
    return {
        "authorized_phase": "TI-1",
        "blocked_phases": [f"TI-{i}" for i in range(2, 9)],
        "status": "PASS" if not violations else "BLOCKED",
        "violations": violations,
    }


def main() -> int:
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
