"""Fail closed if implementation crosses the authorized TI-0 boundary."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCKED_PATHS = (
    "src/snbi_fragmentation/acquisition.py",
    "src/snbi_fragmentation/time_map.py",
    "src/snbi_fragmentation/registration.py",
    "src/snbi_fragmentation/annotation.py",
    "src/snbi_fragmentation/dataset.py",
    "src/snbi_fragmentation/models.py",
    "src/snbi_fragmentation/evaluation.py",
)
BLOCKED_IMPORTS = ("cv2", "torch", "tensorflow", "keras", "av", "moviepy")


def audit() -> dict:
    violations: list[str] = []
    for relative in BLOCKED_PATHS:
        if (ROOT / relative).exists():
            violations.append(f"blocked path exists: {relative}")
    for path in sorted((ROOT / "src").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for name in BLOCKED_IMPORTS:
            if f"import {name}" in text or f"from {name}" in text:
                violations.append(f"blocked TI-1+ import {name} in {path.relative_to(ROOT)}")
    return {
        "authorized_phase": "TI-0",
        "blocked_phases": [f"TI-{i}" for i in range(1, 9)],
        "status": "PASS" if not violations else "BLOCKED",
        "violations": violations,
    }


def main() -> int:
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

