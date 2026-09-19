"""Apply the preregistered TI3 metadata planner once, with no experimental I/O."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

from snbi_fragmentation.ti3_dataset import build_manifest, validate_manifest

BASE = Path("artifacts/evidence/TI3_A_RESUME")
INPUTS = (
    "artifacts/evidence/TI3_TARGET_RESOLUTION/SITE_DEDUPLICATION.json",
    "artifacts/evidence/TI3_TARGET_RESOLUTION/WEAK_LABEL_LEDGER.json",
    "artifacts/metadata/ti2-pilot-manifest.json",
)
FROZEN_TEXT_ALLOWLIST = frozenset(INPUTS + (
    "src/snbi_fragmentation/ti3_dataset.py",
    "tests/test_ti3_dataset.py",
    "scripts/build_ti3_manifest.py",
    "configs/registration/ti2r-frag-direct-method.json",
    *(str(BASE / name) for name in (
        "authorization.md", "DATASET_SPEC.md", "SPLIT_PROTOCOL.md",
        "BACKGROUND_PROTOCOL.md", "LEAKAGE_THREAT_MODEL.md",
        "BASELINE_SPEC.md", "COURSE_ALIGNMENT.md", "CLAIM_SCOPE.md",
    )),
))


def read_text_bytes(name):
    if name not in FROZEN_TEXT_ALLOWLIST and name != str(BASE / "metadata-preflight-freeze.json"):
        raise ValueError("Path outside documentary text allowlist")
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Relative in-repository text required")
    for part in (path, *path.parents):
        if stat.S_ISLNK(part.lstat().st_mode):
            raise ValueError("Symlink prohibited")
    if path.suffix not in {".json", ".md", ".py", ".txt", ".yml"}:
        raise ValueError("Text allowlist required")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as handle:
        raw = handle.read()
    raw.decode("utf-8")
    return raw


def write_once(name, value):
    path = BASE / name
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def main():
    for path in (BASE, *BASE.parents):
        if stat.S_ISLNK(path.lstat().st_mode):
            raise ValueError("Evidence directory symlink prohibited")
    if (BASE / "results.json").exists():
        raise ValueError("Terminal evidence prohibits another application")
    freeze = json.loads(read_text_bytes(str(BASE / "metadata-preflight-freeze.json")))
    if set(freeze["text_sha256"]) != FROZEN_TEXT_ALLOWLIST:
        raise ValueError("Exact documentary freeze allowlist required")
    head = subprocess.check_output(["git", "--no-optional-locks", "rev-parse", "HEAD"], text=True).strip()
    if head != freeze["head"]:
        raise ValueError("Preflight HEAD divergence")
    checked = {}
    for name, expected in freeze["text_sha256"].items():
        raw = read_text_bytes(name)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("Frozen text divergence")
        checked[name] = raw
    if not set(INPUTS).issubset(checked):
        raise ValueError("Metadata input freeze incomplete")
    sites, ledger, pilot = [json.loads(checked[name]) for name in INPUTS]
    if len(sites) != 52 or len(ledger) != 491:
        raise ValueError("Historical target count divergence")
    if sum(row["new_supervision"] == "POSITIVE" for row in ledger) != 108:
        raise ValueError("Historical positive count divergence")
    if sum(row["new_supervision"] == "IGNORE" for row in ledger) != 383:
        raise ValueError("Historical IGNORE count divergence")
    write_once("metadata-preflight-receipt.json", {
        "scope": "DOCUMENTARY_GEOMETRY_ONLY",
        "head": head,
        "metadata_planner_invocations": 1,
        "scientific_ml_runs": 0,
        "experimental_opens": 0,
        "experimental_bytes": 0,
        "text_sha256": freeze["text_sha256"],
    })
    result = build_manifest(sites, ledger, pilot["images"])
    if result["state"] == "PASS":
        validate_manifest(result)
    write_once("metadata-preflight-result.json", result)
    print(json.dumps({
        "scope": "DOCUMENTARY_GEOMETRY_ONLY",
        "result_keys": sorted(result),
        "status": result["state"],
        "split_counts": result["split_counts"],
        "scientific_ml_runs": 0,
        "experimental_opens": 0,
        "experimental_bytes": 0,
    }, sort_keys=True))
    return 0 if result["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
