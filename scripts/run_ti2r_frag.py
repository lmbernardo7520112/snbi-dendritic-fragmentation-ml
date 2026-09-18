"""One invocation only: frozen TI2R-FRAG recovery, never the legacy TI-2 runner."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from snbi_fragmentation import ti2r_frag_authority as authority

BASE_SHA = "0245faf74aa15424d95d43f92e87b32a06ac987b"
DECISION = "docs/decisions/AUTHORIZATION-TI2R-FRAG-2026-09-18.md"
AUTHORITY = "configs/authority/ti2r-frag.json"
EXPOSURE = "artifacts/evidence/TI2R_FRAG/exposure.json"
MANIFEST = "artifacts/metadata/ti2-pilot-manifest.json"
CONFIG = "configs/registration/ti2r-frag-method.json"
FROZEN_FILES = (
    "docs/protocols/TI2R_FRAG_PROTOCOL.md", "scripts/run_ti2r_frag.py",
    "src/snbi_fragmentation/ti2r_frag_authority.py",
    "src/snbi_fragmentation/ti2r_frag_registration.py",
    CONFIG, EXPOSURE, MANIFEST, "pyproject.toml",
)
PAIRS = (
    ("ESM3-to-ESM1", "ESM1", "ESM3", (0, 146, 293), (73, 219)),
    ("ESM6-to-ESM4", "ESM4", "ESM6", (0, 197, 394), (98, 295)),
)


def git(root, *arguments):
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def frozen_inputs(root):
    """Only governed text and Git metadata; never examines experimental paths."""
    authority.require_active(root)
    if git(root, "status", "--porcelain"):
        raise ValueError("BLOCKED_PREFLIGHT: C2 worktree/index is not clean")
    c2 = git(root, "rev-parse", "HEAD")
    c1 = git(root, "rev-parse", "HEAD^")
    if git(root, "rev-parse", "HEAD^^") != BASE_SHA:
        raise ValueError("BLOCKED_PREFLIGHT: expected exactly C1 and C2")
    if git(root, "log", "-1", "--format=%s") != "chore(authority): activate one-shot TI2R-FRAG execution":
        raise ValueError("BLOCKED_PREFLIGHT: C2 message differs")
    changed = set(git(root, "diff", "--name-only", c1, c2).splitlines())
    if changed != {AUTHORITY, DECISION}:
        raise ValueError("BLOCKED_PREFLIGHT: C2 changed other frozen files")
    hashes = {}
    texts = {}
    for relative in FROZEN_FILES:
        # This fixed list contains text only and is independent of asset input.
        data = authority.read_text_file(root, relative)
        texts[relative] = data
        hashes[relative] = hashlib.sha256(data.encode()).hexdigest()
        committed = subprocess.check_output(["git", "show", f"{c1}:{relative}"], cwd=root)
        if committed != data.encode():
            raise ValueError("BLOCKED_PREFLIGHT: frozen text differs from C1")
    exposure = json.loads(texts[EXPOSURE])
    manifest = json.loads(texts[MANIFEST])
    if exposure["original_manifest_sha256"] != hashes[MANIFEST]:
        raise ValueError("BLOCKED_PREFLIGHT: manifest custody mismatch")
    originals = {(x["source_id"], x["frame_index"]): x for x in manifest["images"]}
    for asset in exposure["assets"]:
        original = originals[(asset["source_id"], asset["frame_index"])]
        identifier = f"{asset['source_id']}:{asset['frame_index']}"
        if asset.get("asset_id") != identifier or asset.get("role") != authority.ASSET_ROLES.get(identifier):
            raise ValueError("BLOCKED_PREFLIGHT: asset role or identity differs")
        if any(asset.get("original_role" if k == "role" else k) != v for k, v in original.items()):
            raise ValueError("BLOCKED_PREFLIGHT: asset metadata changed")
    return c2, hashes, exposure, json.loads(texts[CONFIG])


def terminal_status(results, seals_available):
    """Fixed aggregation: no fitted pair is revised after seeing validation."""
    passed = sum(r.get("validation", {}).get("status") == "PASS" for r in results.values())
    if passed == 2:
        return "PASS", "PASS"
    if passed == 1:
        return "PARTIAL_ONE_CONDITION", "PARTIAL"
    candidates = any(r.get("status") == "PASS" for r in results.values())
    candidate_validation = [r.get("validation", {}) for r in results.values() if r.get("status") == "PASS"]
    if candidates and all(v.get("reason") == "CUSTODY_UNPROVEN" for v in candidate_validation):
        return "PARTIAL_DEVELOPMENT_ONLY", "NOT_VALIDATED"
    if not seals_available:
        return "BLOCKED_VALIDATION_CUSTODY", "BLOCKED"
    if candidates:
        if any(v.get("status") == "BLOCKED_REFERENCE_INSUFFICIENT" for v in candidate_validation):
            return "BLOCKED_REFERENCE_INSUFFICIENT", "BLOCKED"
        return "BLOCKED_VALIDATION", "BLOCKED"
    if any(r.get("status") == "BLOCKED_REFERENCE_INSUFFICIENT" for r in results.values()):
        return "BLOCKED_REFERENCE_INSUFFICIENT", "BLOCKED"
    return "BLOCKED_METHOD_HIERARCHY", "BLOCKED"


def execute(session, exposure, config, science):
    assets = {a["asset_id"]: a for a in exposure["assets"]}
    results = {}
    def read_pair(reference, moving, index, role):
        prepared = []
        for source in (reference, moving):
            identifier = f"{source}:{index}"
            asset = assets[identifier]
            raw = authority.read_asset(session, identifier, role=role)
            prepared.append(science.prepare(raw, asset["width"], asset["height"], config))
        return tuple(prepared)
    # Both development candidates freeze before the first conditional quartile.
    for pair, reference, moving, indices, _ in PAIRS:
        print(f"TI2R-FRAG development {pair}", flush=True)
        development = [read_pair(reference, moving, i, "development") for i in indices]
        result = science.fit_pair(development, config)
        results[pair] = result
        if result["status"] == "PASS":
            session.freeze_candidate(pair, {
                "matrix": result["matrix"], "development_pass": True,
                "selected_model": result["selected_model"],
                "development": result["development"],
            })
        del development
    usable_seals = False
    for pair, reference, moving, _, indices in PAIRS:
        result = results[pair]
        sealed = all(exposure["validation_seals"][f"{s}:{i}"]["validation_sealed"] is True
                     for s in (reference, moving) for i in indices)
        usable_seals = usable_seals or sealed
        if result["status"] != "PASS" or not sealed:
            result["validation"] = {"status": "NOT_OPENED", "reason":
                "NO_DEVELOPMENT_CANDIDATE" if result["status"] != "PASS" else "CUSTODY_UNPROVEN"}
            continue
        print(f"TI2R-FRAG validation {pair}; candidate frozen", flush=True)
        validation = [read_pair(reference, moving, i, "validation") for i in indices]
        result["validation"] = science.validate_pair(validation, result["matrix"], config)
        del validation
    state, gate = terminal_status(results, usable_seals)
    return {"TI2R_FRAG": state, "G2_FRAG": gate, "pairs": results}


def main():
    # No parsing/source argument is accepted. The first operation checks authority.
    authority.require_active(ROOT)
    session = None
    report = {"TI2R_FRAG": "BLOCKED_INTERRUPTED", "G2_FRAG": "BLOCKED", "pairs": {}}
    try:
        if len(sys.argv) != 1:
            raise ValueError("BLOCKED_SCOPE_OR_DEPENDENCY: no arguments permitted")
        c2, hashes, exposure, config = frozen_inputs(ROOT)
        from snbi_fragmentation import ti2r_frag_registration as science
        session = authority.begin_session(ROOT, c2_sha=c2, frozen_hashes=hashes,
                                          assets=exposure["assets"], exposure=exposure["validation_seals"])
        report = execute(session, exposure, config, science)
    except BaseException as exc:
        # No retry, traceback with experimental path, or fallback source.
        marker = str(exc).split(":", 1)[0]
        recognized = {"BLOCKED_PILOT_UNAVAILABLE", "BLOCKED_PREFLIGHT",
                      "BLOCKED_VALIDATION_CUSTODY", "BLOCKED_SCOPE_OR_DEPENDENCY"}
        report["TI2R_FRAG"] = marker if marker in recognized else "BLOCKED_INTERRUPTED"
        report["failure_type"] = type(exc).__name__
    report.update({"G2_SOLUTE": "NOT_EXECUTED", "TI3_PLUS_AUTHORIZED": False,
                   "physical_conversion": False, "ffmpeg_or_redecoding": False,
                   "authorized_asset_count": 20, "invocations": 1})
    if session is not None:
        report["opened_assets"] = session.opened_assets
        session.write_result(report)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False), flush=True)
    return 0 if report["TI2R_FRAG"] in {"PASS", "PARTIAL_ONE_CONDITION", "PARTIAL_DEVELOPMENT_ONLY"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
