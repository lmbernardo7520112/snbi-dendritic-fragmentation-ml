"""One development-only V2-D invocation after published preregistration CI."""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from snbi_fragmentation import ti2r_solute_v2_authority as authority

BASE_SHA = "fcfc5e1445467248566e881c61929d4d3da7b1d8"
EXPOSURE = "artifacts/evidence/TI2R_SOLUTE_V2/exposure.json"
CONFIG = "configs/registration/ti2r-solute-v2-method.json"
V1_CONFIG = "configs/registration/ti2r-solute-direct-method.json"
MANIFEST = "artifacts/metadata/ti2-pilot-manifest.json"
ASSET_FIELDS = ("asset_id", "source_id", "frame_index", "role", "path", "width", "height",
                "frame_bytes", "image_sha256", "pixel_format", "bit_depth")
PAIRS = (("ESM2-to-ESM1", "ESM1", "ESM2", (0, 146, 293)),
         ("ESM5-to-ESM4", "ESM4", "ESM5", (0, 197, 394)))
HOLDOUT_IDS = tuple(f"{s}:{i}" for s, indices in
                   (("ESM1", (73, 219)), ("ESM2", (73, 219)),
                    ("ESM4", (98, 295)), ("ESM5", (98, 295))) for i in indices)
PASS = "PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION"
FAIL = "BLOCKED_METHOD_NOT_DISCRIMINATIVE"
OPERATIONAL = "BLOCKED_OPERATIONAL_REQUIRES_AUTHOR_DECISION"


def git(root, *arguments):
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def frozen_inputs(root):
    authority.require_preregistered(root)
    if git(root, "status", "--porcelain"):
        raise ValueError("BLOCKED_PREFLIGHT: dirty C1")
    c1 = git(root, "rev-parse", "HEAD")
    if git(root, "rev-parse", "HEAD^") != BASE_SHA:
        raise ValueError("BLOCKED_PREFLIGHT: C1 base differs")
    if git(root, "rev-parse", "refs/remotes/origin/feat/ti2r-solute-v2-calibration") != c1:
        raise ValueError("BLOCKED_PREFLIGHT: C1 not published")
    if git(root, "log", "-1", "--format=%s") != "feat(ti2r): preregister development-only solute V2 calibration":
        raise ValueError("BLOCKED_PREFLIGHT: expected preregistration C1")
    if any(line.startswith("120000 ") for line in git(root, "ls-files", "--stage").splitlines()):
        raise ValueError("BLOCKED_PREFLIGHT: versioned symlink")
    texts, hashes = {}, {}
    for name in sorted(authority.FROZEN_TEXT_PATHS):
        text = authority.read_text_file(root, name)
        if text.encode() != subprocess.check_output(["git", "show", f"{c1}:{name}"], cwd=root):
            raise ValueError("BLOCKED_PREFLIGHT: frozen text changed")
        texts[name] = text
        hashes[name] = hashlib.sha256(text.encode()).hexdigest()
    exposure, manifest = json.loads(texts[EXPOSURE]), json.loads(texts[MANIFEST])
    if exposure["original_manifest_sha256"] != hashes[MANIFEST]:
        raise ValueError("BLOCKED_CUSTODY: manifest differs")
    originals = {(x["source_id"], x["frame_index"]): x for x in manifest["images"]}
    for asset in exposure["assets"]:
        original = originals[(asset["source_id"], asset["frame_index"])]
        if any(asset.get("original_role" if k == "role" else k) != v for k, v in original.items()):
            raise ValueError("BLOCKED_CUSTODY: frozen metadata differs")
        if asset["asset_id"] != f"{asset['source_id']}:{asset['frame_index']}":
            raise ValueError("BLOCKED_CUSTODY: identity differs")
    versions = {name: importlib.import_module(name).__version__ for name in ("numpy", "scipy")}
    if versions != {"numpy": "1.26.4", "scipy": "1.11.4"}:
        raise ValueError("BLOCKED_RUNTIME: dependency versions differ")
    return c1, hashes, exposure, json.loads(texts[V1_CONFIG]), json.loads(texts[CONFIG]), versions


def terminal_fields(state):
    passed = state == PASS
    return {"TI2R_SOLUTE_V2_DEV": state, "STATE": "CLOSED_CONSUMED",
            "V2_RULE": "FROZEN", "G2_FRAG": "PASS_DIRECT_RASTER_MAPPING",
            "G2_SOLUTE": "BLOCKED_PENDING_LOCKED_HOLDOUT" if passed else
                         "BLOCKED_FINAL_WITH_AVAILABLE_DATA" if state == FAIL else "BLOCKED_PENDING_V2",
            "HOLDOUT_SOLUTE": "SEALED_NOT_NEEDED" if state == FAIL else "SEALED",
            "NO_AUTOMATIC_V3": True,
            "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION",
            "TI2R_SOLUTE_HOLDOUT_AUTHORIZED": False, "TI3_PLUS_AUTHORIZED": False,
            "MERGE_AUTHORIZED": False}


def execute(session, exposure, v1_config, v2_config, preparation, science, report):
    assets = {a["asset_id"]: a for a in exposure["assets"]}
    for pair, reference, moving, indices in PAIRS:
        print(f"V2-D development {pair}; holdout prohibited", flush=True)
        observations = []
        for index in indices:
            frames = []
            for source in (reference, moving):
                identifier = f"{source}:{index}"
                asset = assets[identifier]
                raw = authority.read_asset(session, identifier, role="development")
                frames.append(preparation.prepare(raw, asset["width"], asset["height"], v1_config))
            observations.append(tuple(frames))
        result = science.evaluate_development(pair, observations, v1_config, v2_config)
        result["development_indices"] = list(indices)
        report["pairs"][pair] = result
        del observations
    passed = len(report["pairs"]) == 2 and all(p["status"] == "PASS" for p in report["pairs"].values())
    report.update(terminal_fields(PASS if passed else FAIL))
    return report


def main():
    session = None
    report = dict(terminal_fields(OPERATIONAL), pairs={})
    try:
        authority.require_preregistered(ROOT)
        if len(sys.argv) != 1:
            raise ValueError("BLOCKED_SCOPE: no command-line arguments")
        ci_evidence = json.load(sys.stdin)
        c1, hashes, exposure, v1_config, v2_config, versions = frozen_inputs(ROOT)
        from snbi_fragmentation import ti2r_solute_direct_registration as preparation
        from snbi_fragmentation import ti2r_solute_v2_calibration as science
        session = authority.begin_session(ROOT, c1_sha=c1, frozen_hashes=hashes,
                    assets=[{k: a[k] for k in ASSET_FIELDS} for a in exposure["assets"]],
                    exposure=exposure["development_eligibility"],
                    ci_evidence=ci_evidence)
        report.update(c1_sha=c1, versions=versions)
        execute(session, exposure, v1_config, v2_config, preparation, science, report)
    except BaseException as exc:
        report.update(terminal_fields(OPERATIONAL))
        marker = str(exc).split(":", 1)[0]
        report.update(failure_type=type(exc).__name__,
                      reason=marker if marker.startswith("BLOCKED_") and len(marker) < 80 else "BLOCKED_INTERRUPTED")
    report.update(invocations=1, authorized_assets=12, holdout_open_count=0, holdout_content_bytes_read=0,
                  holdout_assets=[{"asset_id": a, "open_count": 0, "content_bytes_read": 0,
                                   "status": "NOT_OPENED_THIS_PHASE"} for a in HOLDOUT_IDS],
                  physical_conversion=False, metrological_calibration=False, new_data_or_redecoding=False,
                  experimental_unit="acquisition_approximately_one_run_per_condition",
                  perturbations_are_experimental_replicates=False)
    if session is not None:
        report["opened_assets"] = session.opened_assets
        session.finish(report)
    print(json.dumps({k: v for k, v in report.items() if k != "pairs"}, indent=2, sort_keys=True))
    return 0 if report["TI2R_SOLUTE_V2_DEV"] == PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())
