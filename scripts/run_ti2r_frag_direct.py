"""Exactly one authorized DIRECT invocation; no source discovery or retry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from snbi_fragmentation import ti2r_frag_direct_authority as authority

BASE_SHA = "b7bbb6a1f0d3eaa43866027762eb2ed061c3d7c6"
AUTHORITY = "configs/authority/ti2r-frag-direct.json"
DECISION = "docs/decisions/AUTHORIZATION-TI2R-FRAG-DIRECT-2026-09-18.md"
EXPOSURE = "artifacts/evidence/TI2R_FRAG_DIRECT/exposure.json"
CONFIG = "configs/registration/ti2r-frag-direct-method.json"
MANIFEST = "artifacts/metadata/ti2-pilot-manifest.json"
FROZEN_FILES = (
    "docs/protocols/TI2R_FRAG_DIRECT_PROTOCOL.md", "scripts/run_ti2r_frag_direct.py",
    "src/snbi_fragmentation/ti2r_frag_direct_authority.py",
    "src/snbi_fragmentation/ti2r_frag_direct_registration.py",
    CONFIG, EXPOSURE, MANIFEST, "pyproject.toml", "configs/authority/ti2r-frag.json",
    "src/snbi_fragmentation/ti2r_frag_authority.py", "src/snbi_fragmentation/ti2_authority.py",
    "artifacts/evidence/TI2R_FRAG/result.json",
)
PAIRS = (
    ("ESM3-to-ESM1", "ESM1", "ESM3", (0, 146, 293), (73, 219)),
    ("ESM6-to-ESM4", "ESM4", "ESM6", (0, 197, 394), (98, 295)),
)


def git(root, *arguments):
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def frozen_inputs(root):
    authority.require_active(root)
    if git(root, "status", "--porcelain"):
        raise ValueError("BLOCKED_PREFLIGHT: dirty C2")
    c2, c1 = git(root, "rev-parse", "HEAD"), git(root, "rev-parse", "HEAD^")
    if git(root, "rev-parse", "HEAD^^") != BASE_SHA:
        raise ValueError("BLOCKED_PREFLIGHT: C1/C2 base differs")
    if git(root, "log", "-1", "--format=%s") != "chore(authority): activate one-shot DIRECT mapping":
        raise ValueError("BLOCKED_PREFLIGHT: expected C2")
    if set(git(root, "diff", "--name-only", c1, c2).splitlines()) != {AUTHORITY, DECISION}:
        raise ValueError("BLOCKED_PREFLIGHT: C2 changed frozen scope")
    texts, hashes = {}, {}
    for name in FROZEN_FILES:
        text = authority.read_text_file(root, name)
        if text.encode() != subprocess.check_output(["git", "show", f"{c1}:{name}"], cwd=root):
            raise ValueError("BLOCKED_PREFLIGHT: frozen text changed")
        texts[name] = text
        hashes[name] = hashlib.sha256(text.encode()).hexdigest()
    exposure, manifest = json.loads(texts[EXPOSURE]), json.loads(texts[MANIFEST])
    if exposure["original_manifest_sha256"] != hashes[MANIFEST]:
        raise ValueError("BLOCKED_PREFLIGHT: manifest custody mismatch")
    originals = {(x["source_id"], x["frame_index"]): x for x in manifest["images"]}
    for asset in exposure["assets"]:
        original = originals[(asset["source_id"], asset["frame_index"])]
        if any(asset.get("original_role" if k == "role" else k) != v for k, v in original.items()):
            raise ValueError("BLOCKED_PREFLIGHT: modified frozen metadata")
        if asset["asset_id"] != f"{asset['source_id']}:{asset['frame_index']}":
            raise ValueError("BLOCKED_PREFLIGHT: asset identity mismatch")
    return c2, hashes, exposure, json.loads(texts[CONFIG])


def aggregate(pairs):
    if any(p.get("status") == "BLOCKED_DIMENSION_DIVERGENCE" or
           p.get("holdout", {}).get("status") == "BLOCKED_DIMENSION_DIVERGENCE" for p in pairs.values()):
        return "BLOCKED_DIMENSION_DIVERGENCE", "BLOCKED"
    passes = sum(p.get("holdout", {}).get("status") == "PASS" for p in pairs.values())
    if passes == 2:
        return "PASS", "PASS_DIRECT_RASTER_MAPPING"
    if passes == 1:
        return "PARTIAL_ONE_PAIR", "PARTIAL_ONE_PAIR"
    if any(p.get("status") == "BLOCKED_REFERENCE_STILL_INSUFFICIENT" or
           p.get("holdout", {}).get("status") == "BLOCKED_REFERENCE_STILL_INSUFFICIENT" for p in pairs.values()):
        return "BLOCKED_REFERENCE_STILL_INSUFFICIENT", "BLOCKED"
    return "BLOCKED_DIRECT_MAPPING", "BLOCKED"


def execute(session, exposure, config, science, report):
    assets = {a["asset_id"]: a for a in exposure["assets"]}
    def read_pair(reference, moving, index, role):
        frames = []
        for source in (reference, moving):
            identifier = f"{source}:{index}"
            asset = assets[identifier]
            raw = authority.read_asset(session, identifier, role=role)
            frames.append(science.prepare(raw, asset["width"], asset["height"], config))
        return tuple(frames)
    for pair, reference, moving, development_indices, holdout_indices in PAIRS:
        print(f"DIRECT development {pair}", flush=True)
        development = [read_pair(reference, moving, i, "development") for i in development_indices]
        result = science.evaluate_development(pair, development, config)
        result["development_indices"] = list(development_indices)
        report["pairs"][pair] = result
        del development
        if result["status"] == "BLOCKED_DIMENSION_DIVERGENCE":
            raise ValueError("BLOCKED_DIMENSION_DIVERGENCE")
        if result["status"] != "PASS":
            result["holdout"] = {"status": "NOT_OPENED", "reason": "DEVELOPMENT_NOT_PASSED"}
            continue
        seals = exposure["holdout_seals"]
        if not all(seals[f"{source}:{i}"]["holdout_sealed"] is True
                   for source in (reference, moving) for i in holdout_indices):
            result["holdout"] = {"status": "NOT_OPENED", "reason": "CUSTODY_NOT_PROVEN"}
            continue
        session.freeze_offset(pair, {"offset": result["offset"], "development_pass": True,
                                    "development": result})
    # Complete all candidate selection before any temporal holdout; never revisit it.
    for pair, reference, moving, _, holdout_indices in PAIRS:
        result = report["pairs"][pair]
        if result["status"] != "PASS" or "holdout" in result:
            continue
        print(f"DIRECT holdout {pair}; integer offset frozen", flush=True)
        holdout = [read_pair(reference, moving, i, "holdout") for i in holdout_indices]
        result["holdout"] = science.evaluate_holdout(pair, holdout, result["offset"], config)
        result["holdout_indices"] = list(holdout_indices)
        del holdout
        if result["holdout"]["status"] == "BLOCKED_DIMENSION_DIVERGENCE":
            raise ValueError("BLOCKED_DIMENSION_DIVERGENCE")
    report["TI2R_FRAG_DIRECT"], report["G2_FRAG"] = aggregate(report["pairs"])
    return report


def main():
    authority.require_active(ROOT)
    session = None
    report = {"TI2R_FRAG_DIRECT": "BLOCKED_DIRECT_MAPPING", "G2_FRAG": "BLOCKED", "pairs": {}}
    try:
        if len(sys.argv) != 1:
            raise ValueError("BLOCKED_SCOPE: no arguments permitted")
        c2, hashes, exposure, config = frozen_inputs(ROOT)
        from snbi_fragmentation import ti2r_frag_direct_registration as science
        session = authority.begin_session(ROOT, c2_sha=c2, frozen_hashes=hashes,
                                          assets=exposure["assets"], exposure=exposure["holdout_seals"])
        execute(session, exposure, config, science, report)
    except BaseException as exc:
        marker = str(exc).split(":", 1)[0]
        report["TI2R_FRAG_DIRECT"] = "BLOCKED_DIMENSION_DIVERGENCE" if marker == "BLOCKED_DIMENSION_DIVERGENCE" else "BLOCKED_DIRECT_MAPPING"
        report["failure_type"] = type(exc).__name__
        report["terminal_reason"] = marker if marker.startswith("BLOCKED_") and len(marker) < 80 else "BLOCKED_INTERRUPTED"
    report.update({"G2_SOLUTE": "NOT_EXECUTED", "G3": "BLOCKED_OR_PENDING_G2_COMPLETE",
                   "TI3_PLUS_AUTHORIZED": False, "invocations": 1, "authorized_assets": 20,
                   "physical_conversion": False, "new_data_or_redecoding": False,
                   "validation_kind": "INTERNAL_TEMPORAL_SAME_ACQUISITION"})
    if report["TI2R_FRAG_DIRECT"] == "PASS":
        report["G2_SPATIAL"] = "PARTIAL_PENDING_G2_SOLUTE"
    if session is not None:
        report["opened_assets"] = session.opened_assets
        session.write_result(report)
    # Full text metrics persist once in result.json; stdout avoids bulky duplication.
    print(json.dumps({k: v for k, v in report.items() if k != "pairs"}, indent=2, sort_keys=True))
    return 0 if report["TI2R_FRAG_DIRECT"] in {"PASS", "PARTIAL_ONE_PAIR"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
