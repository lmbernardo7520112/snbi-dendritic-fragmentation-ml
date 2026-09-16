"""Fail closed if the repository crosses the authorized TI-1 boundary."""

from __future__ import annotations

import json
from pathlib import Path

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
BLOCKED_ARTIFACT_SUFFIXES = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".npy", ".pt", ".pth", ".h5")


def audit() -> dict:
    violations: list[str] = []
    for relative in BLOCKED_PATHS:
        if (ROOT / relative).exists():
            violations.append(f"blocked path exists: {relative}")
    for path in sorted((ROOT / "src").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for name in BLOCKED_IMPORTS:
            if f"import {name}" in text or f"from {name}" in text:
                violations.append(f"blocked TI-2+ import {name} in {path.relative_to(ROOT)}")
    for root_name in ("data", "artifacts"):
        for path in (ROOT / root_name).rglob("*"):
            if path.is_file() and path.suffix.lower() in BLOCKED_ARTIFACT_SUFFIXES:
                violations.append(f"extracted/model artifact forbidden in TI-1: {path.relative_to(ROOT)}")
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
