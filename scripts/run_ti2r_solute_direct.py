"""Exactly one authorized multimodal solute invocation; identity only, no retry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from snbi_fragmentation import ti2r_solute_direct_authority as authority

BASE_SHA = "db03183e1456f67b5b663a4cb71361cad1404dcb"
AUTHORITY = "configs/authority/ti2r-solute-direct.json"
DECISION = "docs/decisions/AUTHORIZATION-TI2R-SOLUTE-DIRECT-2026-09-18.md"
EXPOSURE = "artifacts/evidence/TI2R_SOLUTE_DIRECT/exposure.json"
CONFIG = "configs/registration/ti2r-solute-direct-method.json"
MANIFEST = "artifacts/metadata/ti2-pilot-manifest.json"
FROZEN_FILES = (
    "docs/protocols/TI2R_SOLUTE_DIRECT_PROTOCOL.md", "scripts/run_ti2r_solute_direct.py",
    "src/snbi_fragmentation/ti2r_solute_direct_authority.py",
    "src/snbi_fragmentation/ti2r_solute_direct_registration.py",
    CONFIG, EXPOSURE, MANIFEST, "pyproject.toml", "configs/authority/ti2r-frag.json",
    "configs/authority/ti2r-frag-direct.json", "src/snbi_fragmentation/ti2r_frag_authority.py",
    "src/snbi_fragmentation/ti2r_frag_direct_authority.py", "src/snbi_fragmentation/ti2_authority.py",
    "artifacts/evidence/TI2R_FRAG_DIRECT/result.json",
)
PAIRS = (
    ("ESM2-to-ESM1", "ESM1", "ESM2", (0, 146, 293), (73, 219)),
    ("ESM5-to-ESM4", "ESM4", "ESM5", (0, 197, 394), (98, 295)),
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
    if git(root, "log", "-1", "--format=%s") != "chore(authority): activate one-shot SOLUTE DIRECT mapping":
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
        raise ValueError("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: manifest custody mismatch")
    originals = {(x["source_id"], x["frame_index"]): x for x in manifest["images"]}
    for asset in exposure["assets"]:
        original = originals[(asset["source_id"], asset["frame_index"])]
        if any(asset.get("original_role" if k == "role" else k) != v for k, v in original.items()):
            raise ValueError("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: modified frozen metadata")
        if asset["asset_id"] != f"{asset['source_id']}:{asset['frame_index']}":
            raise ValueError("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: asset identity mismatch")
    return c2, hashes, exposure, json.loads(texts[CONFIG])


def aggregate(pairs):
    states = [p.get("status") for p in pairs.values()]
    states += [p.get("holdout", {}).get("status") for p in pairs.values()]
    if "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE" in states:
        return "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE", "BLOCKED"
    passes = sum(p.get("status") == "PASS" and p.get("holdout", {}).get("status") == "PASS"
                 for p in pairs.values())
    if passes == 2:
        return "PASS_DIRECT_MULTIMODAL_MAPPING", "PASS_INTERNAL_DIRECT_RASTER_IDENTITY"
    if passes == 1:
        return "PARTIAL_ONE_PAIR", "PARTIAL_ONE_PAIR"
    for status in ("BLOCKED_INTERNAL_VALIDATION", "BLOCKED_MULTIMODAL_METRIC_DISCORDANCE",
                   "BLOCKED_IDENTITY_NOT_DISCRIMINATIVE", "BLOCKED_MODALITY_INFORMATION_INSUFFICIENT"):
        if status in states:
            return status, "BLOCKED"
    return "BLOCKED_IDENTITY_NOT_DISCRIMINATIVE", "BLOCKED"


def terminal_gates(state):
    return {
        "G2_FRAG": "PASS_DIRECT_RASTER_MAPPING",
        "G2_SPATIAL": "PASS_WITHIN_SAMPLED_ACQUISITIONS" if state == "PASS_DIRECT_MULTIMODAL_MAPPING" else
                      "PARTIAL" if state == "PARTIAL_ONE_PAIR" else "PARTIAL_FRAG_ONLY",
        "G3": "PENDING_SEPARATE_DECISION",
        "TI3_PLUS_AUTHORIZED": False,
    }


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
        print(f"SOLUTE DIRECT development {pair}", flush=True)
        development = [read_pair(reference, moving, i, "development") for i in development_indices]
        result = science.evaluate_development(pair, development, config)
        result["development_indices"] = list(development_indices)
        report["pairs"][pair] = result
        del development
        if result["status"] == "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE":
            raise ValueError("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE")
        if result["status"] != "PASS":
            result["holdout"] = {"status": "NOT_OPENED", "reason": "DEVELOPMENT_NOT_PASSED"}
            continue
        seals = exposure["holdout_eligibility"]
        if not all(seals[f"{source}:{i}"]["holdout_eligible_this_phase"] is True
                   for source in (reference, moving) for i in holdout_indices):
            result["holdout"] = {"status": "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE", "reason": "CUSTODY_NOT_PROVEN"}
            raise ValueError("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE")
        session.freeze_identity(pair, {"offset": result["offset"], "development_pass": True,
                                    "development": result})
    # Complete all candidate selection before any temporal holdout; never revisit it.
    for pair, reference, moving, _, holdout_indices in PAIRS:
        result = report["pairs"][pair]
        if result["status"] != "PASS" or "holdout" in result:
            continue
        print(f"SOLUTE DIRECT holdout {pair}; integer offset frozen", flush=True)
        holdout = [read_pair(reference, moving, i, "holdout") for i in holdout_indices]
        result["holdout"] = science.evaluate_holdout(pair, holdout, result["offset"], config)
        result["holdout_indices"] = list(holdout_indices)
        del holdout
        if result["holdout"]["status"] == "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE":
            raise ValueError("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE")
    report["TI2R_SOLUTE_DIRECT"], report["G2_SOLUTE"] = aggregate(report["pairs"])
    return report


def main():
    authority.require_active(ROOT)
    session = None
    report = {"TI2R_SOLUTE_DIRECT": "BLOCKED_EXECUTION_FAILURE", "G2_SOLUTE": "BLOCKED", "pairs": {}}
    try:
        if len(sys.argv) != 1:
            raise ValueError("BLOCKED_SCOPE: no arguments permitted")
        c2, hashes, exposure, config = frozen_inputs(ROOT)
        from snbi_fragmentation import ti2r_solute_direct_registration as science
        session = authority.begin_session(ROOT, c2_sha=c2, frozen_hashes=hashes,
                                          assets=exposure["assets"], exposure=exposure["holdout_eligibility"])
        execute(session, exposure, config, science, report)
    except BaseException as exc:
        marker = str(exc).split(":", 1)[0]
        report["TI2R_SOLUTE_DIRECT"] = "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE" if marker == "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE" else "BLOCKED_EXECUTION_FAILURE"
        report["failure_type"] = type(exc).__name__
        report["terminal_reason"] = marker if marker.startswith("BLOCKED_") and len(marker) < 80 else "BLOCKED_INTERRUPTED"
    report.update(terminal_gates(report["TI2R_SOLUTE_DIRECT"]))
    report.update({"invocations": 1, "authorized_assets": 20,
                   "physical_conversion": False, "new_data_or_redecoding": False,
                   "validation_kind": "INTERNAL_TEMPORAL_SAME_ACQUISITION",
                   "allowed_transformation": "IDENTITY_ONLY",
                   "descriptor": "LOCAL_SELF_SIMILARITY_8_NOT_EXACT_MIND_SSC",
                   "intensity_claim": "RELATIVE_NORMALIZED_SOLUTE_RADIOGRAPHIC_FIELDS_ONLY"})
    if session is not None:
        report["opened_assets"] = session.opened_assets
        session.write_result(report)
    # Full text metrics persist once in result.json; stdout avoids bulky duplication.
    print(json.dumps({k: v for k, v in report.items() if k != "pairs"}, indent=2, sort_keys=True))
    return 0 if report["TI2R_SOLUTE_DIRECT"] in {"PASS_DIRECT_MULTIMODAL_MAPPING", "PARTIAL_ONE_PAIR"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
