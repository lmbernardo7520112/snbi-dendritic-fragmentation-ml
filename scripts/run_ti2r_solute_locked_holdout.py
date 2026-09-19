"""Single authorized holdout invocation; frozen scientific functions stay intact.

Operational receipt, custody, counters and persistence only. There is no retry,
adaptive fallback, parameter mutation or route back to development buffers.
Importing this module does not run the gate or inspect experimental paths.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from snbi_fragmentation import ti2r_solute_v2_authority as safe

C1 = "e1a98917a20431ecc1c758f210b5e974b3533734"
HEAD = "0b820bc61e6dae3b7a98654a3b7d5cd292ca925e"
BRANCH = "feat/ti2r-solute-v2-calibration"
PHASE = "TI2R_SOLUTE_HOLDOUT"
EVIDENCE = "artifacts/evidence/" + PHASE
MANIFEST = EVIDENCE + "/frozen-manifest.json"
RECEIPT = EVIDENCE + "/receipt.json"
TERMINAL = EVIDENCE + "/terminal-state.json"
ORIGINAL_MANIFEST = "artifacts/metadata/ti2-pilot-manifest.json"
V1_CONFIG = "configs/registration/ti2r-solute-direct-method.json"
V2_CONFIG = "configs/registration/ti2r-solute-v2-method.json"
EVALUATOR = "scripts/ti2r_solute_locked_evaluator.py"
RUNNER = "scripts/run_ti2r_solute_locked_holdout.py"
OPERATIONAL_PATHS = frozenset({
    EVALUATOR, RUNNER, EVIDENCE + "/PRE_EXECUTION_AUDIT.md",
    EVIDENCE + "/authorization.md", EVIDENCE + "/verification.json",
})
OUTPUT_NAMES = ("receipt.json", "io-audit.json", "results.json", "terminal-state.json")
ALLOWED_NEW_PATHS = OPERATIONAL_PATHS | frozenset(
    EVIDENCE + "/" + name for name in OUTPUT_NAMES + (
        "frozen-manifest.json", "frozen-hashes.sha256", "execution-report.md",
        "commands.json", "post-run-hashes.sha256",
    )
)
PAIRS = (("ESM2-to-ESM1", "ESM1", "ESM2", (73, 219)),
         ("ESM5-to-ESM4", "ESM4", "ESM5", (98, 295)))
ASSET_IDS = frozenset(f"{source}:{index}" for _, reference, moving, indices in PAIRS
                      for source in (reference, moving) for index in indices)
ASSET_KEYS = frozenset({"asset_id", "source_id", "frame_index", "path", "width", "height",
                        "frame_bytes", "image_sha256", "pixel_format", "bit_depth"})


class HoldoutBlocked(ValueError):
    """A bounded operational contract failed; execution must not be retried."""


def require(condition, code):
    if not condition:
        raise HoldoutBlocked(code)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def git(root, *arguments):
    return subprocess.check_output(["git", *arguments], cwd=root)


def document(root, relative):
    raw = safe._read_regular(root, relative)
    return raw, json.loads(raw, object_pairs_hook=safe._unique_object)


def require_absent(root, relative):
    """Presence, including a symlink, blocks; never follows its target."""
    parent, name = safe._parent_fd(root, relative)
    try:
        try:
            os.stat(name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            return
        raise HoldoutBlocked("EXISTING_ATTEMPT_OR_OUTPUT_NO_RETRY")
    finally:
        os.close(parent)


def validate_git(root):
    require(git(root, "rev-parse", "HEAD").decode().strip() == HEAD, "HEAD_DIVERGENCE")
    require(git(root, "branch", "--show-current").decode().strip() == BRANCH, "BRANCH_DIVERGENCE")
    require(git(root, "rev-parse", "refs/remotes/origin/" + BRANCH).decode().strip() == HEAD,
            "TRACKING_BRANCH_DIVERGENCE")
    status = git(root, "status", "--porcelain=v1", "--untracked-files=all").decode()
    require(all(line.startswith("?? ") and line[3:] in ALLOWED_NEW_PATHS
                for line in status.splitlines()), "TRACKED_CHANGE_OR_UNANNOUNCED_PATH")
    require(not any(line.startswith("120000 ")
                    for line in git(root, "ls-files", "--stage").decode().splitlines()),
            "VERSIONED_SYMLINK")


def validate_ci(evidence):
    require(type(evidence) is dict and type(evidence.get("runs")) is list
            and len(evidence["runs"]) == 2, "BOTH_C2_CI_RUNS_REQUIRED")
    events, identifiers = set(), set()
    for run in evidence["runs"]:
        require(type(run) is dict and run.get("headSha") == HEAD
                and run.get("status") == "completed" and run.get("conclusion") == "success"
                and run.get("event") in ("push", "pull_request")
                and run["event"] not in events and type(run.get("databaseId")) is int
                and run["databaseId"] > 0 and run["databaseId"] not in identifiers,
                "CI_RUN_DIVERGENCE")
        require(run.get("url") == f"https://github.com/{safe.REPOSITORY}/actions/runs/{run['databaseId']}",
                "CI_RUN_URL_DIVERGENCE")
        events.add(run["event"])
        identifiers.add(run["databaseId"])
        jobs = run.get("jobs")
        require(type(jobs) is list and len(jobs) == 2
                and {job.get("name") for job in jobs} == {
                    "deterministic-contracts", "scientific-synthetic-contracts"}, "CI_JOBS_REQUIRED")
        for job in jobs:
            require(job.get("status") == "completed" and job.get("conclusion") == "success"
                    and type(job.get("steps")) is list and bool(job["steps"]), "CI_JOB_NOT_GREEN")
            require(all(step.get("status") == "completed" and step.get("conclusion") == "success"
                        for step in job["steps"]), "CI_STEP_NOT_GREEN")


def validate_assets(assets, original):
    require(type(assets) is list and len(assets) == 8, "EXACTLY_EIGHT_RESERVED_ASSETS_REQUIRED")
    originals = {(item["source_id"], item["frame_index"]): item for item in original["images"]}
    validated = {}
    for asset in assets:
        require(type(asset) is dict and set(asset) == ASSET_KEYS, "ASSET_SCHEMA_DIVERGENCE")
        source, index, identity = asset["source_id"], asset["frame_index"], asset["asset_id"]
        require(type(source) is str and type(index) is int and type(identity) is str
                and identity == f"{source}:{index}" and identity in ASSET_IDS
                and identity not in validated, "UNLISTED_OR_DUPLICATE_ASSET")
        expected = originals[(source, index)]
        require(all(safe._exact(asset[key], expected[key]) for key in ASSET_KEYS - {"asset_id"}),
                "ORIGINAL_MANIFEST_DIVERGENCE")
        height = 1018 if source in ("ESM1", "ESM2") else 1012
        require(asset["path"] == f"data/derived/ti2-pilot/{source}-{index:04d}.raw"
                and type(asset["width"]) is int and asset["width"] == 1278
                and type(asset["height"]) is int and asset["height"] == height
                and type(asset["frame_bytes"]) is int and asset["frame_bytes"] == 1278 * height * 3 // 2
                and asset["pixel_format"] == "yuv420p" and type(asset["bit_depth"]) is int
                and asset["bit_depth"] == 8 and type(asset["image_sha256"]) is str
                and safe.SHA256_RE.fullmatch(asset["image_sha256"]) is not None, "NATIVE_ASSET_DIVERGENCE")
        validated[identity] = dict(asset)
    require(set(validated) == ASSET_IDS, "RESERVED_ALLOWLIST_INCOMPLETE")
    return validated


def preflight(root):
    # Refuse a second invocation before inspecting any experimental path.
    for name in OUTPUT_NAMES:
        require_absent(root, EVIDENCE + "/" + name)
    validate_git(root)
    manifest_bytes, manifest = document(root, MANIFEST)
    require(manifest.get("phase") == PHASE and manifest.get("pre_holdout_gate") == "PASS"
            and manifest.get("head_sha") == HEAD and manifest.get("branch") == BRANCH,
            "PRE_HOLDOUT_GATE_NOT_PASS")
    scientific = manifest.get("scientific_hashes")
    operational = manifest.get("operational_hashes")
    require(type(scientific) is dict and set(scientific) == safe.FROZEN_TEXT_PATHS,
            "SCIENTIFIC_FREEZE_INCOMPLETE")
    require(type(operational) is dict and set(operational) == OPERATIONAL_PATHS,
            "OPERATIONAL_FREEZE_INCOMPLETE")
    texts = {}
    for relative, digest in {**scientific, **operational}.items():
        require(type(digest) is str and safe.SHA256_RE.fullmatch(digest) is not None,
                "INVALID_FROZEN_DIGEST")
        raw = safe._read_regular(root, relative)
        raw.decode("utf-8")
        require(hashlib.sha256(raw).hexdigest() == digest, "FROZEN_HASH_DIVERGENCE")
        if relative in scientific:
            require(raw == git(root, "show", f"{C1}:{relative}"), "SCIENTIFIC_C1_DIVERGENCE")
        texts[relative] = raw
    configs = {"v1": json.loads(texts[V1_CONFIG]), "v2": json.loads(texts[V2_CONFIG])}
    require(safe._exact(manifest.get("configurations"), configs), "CONFIGURATION_DIVERGENCE")
    from snbi_fragmentation import ti2r_solute_v2_calibration as v2
    v2.validate_config(configs["v2"])
    old_raw, old = document(root, safe.TERMINAL_PATH)
    require(old_raw == git(root, "show", f"{HEAD}:{safe.TERMINAL_PATH}"), "V2_TERMINAL_DIVERGENCE")
    require(old.get("state") == "CLOSED_CONSUMED"
            and old.get("TI2R_SOLUTE_V2_DEV") == "PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION"
            and old.get("HOLDOUT_SOLUTE") == "SEALED"
            and old.get("holdout_open_count") == 0 and old.get("holdout_content_bytes_read") == 0
            and set(old.get("holdout_assets", {})) == ASSET_IDS
            and all(item == {"open_count": 0, "content_bytes_read": 0}
                    for item in old["holdout_assets"].values()), "V2_NOT_CLOSED_OR_HOLDOUT_NOT_SEALED")
    assets = validate_assets(manifest.get("assets"), json.loads(texts[ORIGINAL_MANIFEST]))
    validate_ci(manifest.get("ci_evidence"))
    versions = {name: importlib.import_module(name).__version__ for name in ("numpy", "scipy")}
    require(versions == {"numpy": "1.26.4", "scipy": "1.11.4"}, "DEPENDENCY_VERSION_DIVERGENCE")
    audit = texts[EVIDENCE + "/PRE_EXECUTION_AUDIT.md"].decode()
    require("PRE_HOLDOUT_GATE=PASS" in audit and "PRE_HOLDOUT_GATE=FAIL" not in audit,
            "PRE_HOLDOUT_AUDIT_NOT_PASS")
    return manifest_bytes, manifest, assets, versions, texts[EVALUATOR]


class AccountedReader:
    """One attempted open per authorized asset; count bytes as they are read."""

    def __init__(self, root, assets):
        self.root, self.assets = root, assets
        self.records = {identity: {"asset_id": identity, "path": asset["path"],
                        "open_attempts": 0, "open_count": 0, "content_bytes_read": 0,
                        "status": "NOT_OPENED", "sha256": None}
                        for identity, asset in assets.items()}

    def read(self, identity):
        require(type(identity) is str and identity in ASSET_IDS and identity in self.assets,
                "UNAUTHORIZED_ASSET_BEFORE_PATH_ACCESS")
        record, asset = self.records[identity], self.assets[identity]
        require(record["open_attempts"] == 0, "ASSET_ALREADY_ATTEMPTED_NO_RETRY")
        record["open_attempts"] = 1
        record["status"] = "ATTEMPTED"
        descriptor = None
        digest, chunks = hashlib.sha256(), []
        try:
            parent, name = safe._parent_fd(self.root, asset["path"])
            try:
                descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
                record["open_count"] = 1
            finally:
                os.close(parent)
            info = os.fstat(descriptor)
            require(stat.S_ISREG(info.st_mode) and info.st_size == asset["frame_bytes"], "ASSET_SIZE_OR_TYPE")
            while record["content_bytes_read"] <= asset["frame_bytes"]:
                remaining = asset["frame_bytes"] + 1 - record["content_bytes_read"]
                chunk = os.read(descriptor, min(65536, remaining))
                if not chunk:
                    break
                record["content_bytes_read"] += len(chunk)
                digest.update(chunk)
                chunks.append(chunk)
            record["sha256"] = digest.hexdigest()
            require(record["content_bytes_read"] == asset["frame_bytes"]
                    and record["sha256"] == asset["image_sha256"], "ASSET_BYTES_OR_DIGEST")
            record["status"] = "AUTHENTICATED"
            return b"".join(chunks)
        except BaseException as exc:
            record["status"] = "TECHNICAL_INCIDENT"
            record["incident_type"] = type(exc).__name__
            record["sha256_of_bytes_read_before_incident"] = digest.hexdigest()
            raise
        finally:
            if descriptor is not None:
                os.close(descriptor)

    def audit(self):
        records = list(self.records.values())
        return {"phase": PHASE, "HOLDOUT_RUN_ATTEMPT": 1, "retries": 0,
                "authorized_buffers": 8, "assets": records,
                "files_opened": sum(record["open_count"] > 0 for record in records),
                "open_count": sum(record["open_count"] for record in records),
                "open_attempts": sum(record["open_attempts"] for record in records),
                "content_bytes_read": sum(record["content_bytes_read"] for record in records),
                "development_open_count": 0, "development_content_bytes_read": 0}


def evaluate(reader, configurations, adapter, report):
    from snbi_fragmentation import ti2r_solute_direct_registration as preparation
    # Authenticate and prepare exactly eight buffers before evaluating four cases.
    prepared = {}
    for _, reference, moving, indices in PAIRS:
        for index in indices:
            for source in (reference, moving):
                identity = f"{source}:{index}"
                asset = reader.assets[identity]
                raw = reader.read(identity)
                prepared[identity] = preparation.prepare(raw, asset["width"], asset["height"], configurations["v1"])
    for name, reference, moving, indices in PAIRS:
        pairs = [(prepared[f"{reference}:{index}"], prepared[f"{moving}:{index}"]) for index in indices]
        report["scientific_evaluation_started"] = True
        report["pair_evaluation_calls"] = report.get("pair_evaluation_calls", 0) + 1
        report["pairs"][name] = adapter.evaluate_holdout_pair(name, pairs, configurations["v1"], configurations["v2"])
    return all(pair["status"] == "PASS" for pair in report["pairs"].values())


def terminal_fields(outcome):
    valid = outcome in ("PASS", "FAIL")
    return {"phase": PHASE, "TI2R_SOLUTE_HOLDOUT": outcome,
            "G2_SOLUTE": outcome if valid else "NOT_CERTIFIED_OPERATIONAL_INCIDENT",
            "G2_FRAG": "PASS_DIRECT_RASTER_MAPPING", "HOLDOUT_SOLUTE": "CONSUMED",
            "STATE": "CLOSED" if outcome == "PASS" else "CLOSED_FAILED" if outcome == "FAIL" else "CLOSED_OPERATIONAL_INCIDENT",
            "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION",
            "TI2R_SOLUTE_HOLDOUT_AUTHORIZED": False, "TI2R_EXECUTION_AUTHORIZED": False,
            "TI3_PLUS_AUTHORIZED": False, "MERGE_AUTHORIZED": False,
            "SOLUTAL_PROTOCOL": "VALIDATED_ON_LOCKED_HOLDOUT" if outcome == "PASS" else "NOT_VALIDATED",
            "HOLDOUT_RUN_ATTEMPT": 1, "retries": 0}


def main():
    reader = None
    consumed = False
    report = {"phase": PHASE, "head_sha": HEAD, "branch": BRANCH, "pairs": {},
              "scientific_evaluation_started": False, "pair_evaluation_calls": 0,
              "cli_invocations": 1}
    outcome = "TECHNICAL_INCIDENT_REQUIRES_AUTHOR_DECISION"
    try:
        require(len(sys.argv) == 1, "NO_ARGUMENTS_ALLOWED")
        manifest_bytes, manifest, assets, versions, evaluator_bytes = preflight(ROOT)
        receipt = {"phase": PHASE, "timestamp_utc": timestamp(), "head_sha": HEAD, "branch": BRANCH,
                   "frozen_c1_sha": C1, "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                   "scientific_hashes": manifest["scientific_hashes"],
                   "operational_hashes": manifest["operational_hashes"],
                   "configurations": manifest["configurations"], "dependency_versions": versions,
                   "assets": manifest["assets"], "prior_exposure": manifest["prior_exposure"],
                   "ci_evidence": manifest["ci_evidence"], "HOLDOUT_RUN_ATTEMPT": 1,
                   "max_attempts": 1, "retries": 0, "files_opened": 0,
                   "open_count": 0, "content_bytes_read": 0,
                   "atomic_uniqueness": "O_EXCL_AND_FSYNC_BEFORE_EXPERIMENTAL_BYTES"}
        receipt_bytes = safe._encoded(receipt)
        safe._write_exclusive(ROOT, RECEIPT, receipt_bytes)
        consumed = True
        reader = AccountedReader(ROOT, assets)
        report.update(receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
                      manifest_sha256=receipt["manifest_sha256"], dependency_versions=versions,
                      started_at_utc=receipt["timestamp_utc"], frozen_c1_sha=C1)
        # Load only the already authenticated adapter bytes, without reopening
        # a path through an unchecked import loader or writing bytecode.
        spec = importlib.util.spec_from_loader("locked_holdout_evaluator", loader=None)
        adapter = importlib.util.module_from_spec(spec)
        exec(compile(evaluator_bytes, EVALUATOR, "exec"), adapter.__dict__)
        outcome = "PASS" if evaluate(reader, manifest["configurations"], adapter, report) else "FAIL"
    except BaseException as exc:
        report["incident"] = {"exception_type": type(exc).__name__,
                              "code": str(exc) if isinstance(exc, HoldoutBlocked) else "TECHNICAL_EXCEPTION",
                              "errno": getattr(exc, "errno", None),
                              "completed_pair_results": len(report["pairs"]),
                              "scientific_evaluation_started": report["scientific_evaluation_started"],
                              "pair_evaluation_calls": report["pair_evaluation_calls"],
                              "scientific_results_obtained": True if report["pairs"] else
                                  None if report["scientific_evaluation_started"] else False,
                              "observation_status": "COMPLETE_PAIR_RESULTS_AVAILABLE" if report["pairs"] else
                                  "UNKNOWN_PARTIAL_POSSIBLE" if report["scientific_evaluation_started"] else
                                  "NO_SCIENTIFIC_EVALUATION_STARTED",
                              "automatic_retry": False}
    if not consumed:
        print(json.dumps({"phase": PHASE, "PRE_HOLDOUT_GATE": "FAIL", "attempt_consumed": False,
                          "scientific_invocations": 0, "holdout_content_bytes_read": 0,
                          "incident": report.get("incident"), "retries": 0}, sort_keys=True), flush=True)
        return 3
    fields = terminal_fields(outcome)
    accounting = reader.audit()
    report.update(fields, io_audit=accounting, finished_at_utc=timestamp(),
                  scientific_invocations=int(report["scientific_evaluation_started"]),
                  new_data_or_redecoding=False, development_buffers_reopened=False,
                  physical_conversion=False, scientific_edits_after_holdout=False)
    terminal = dict(fields, head_sha=HEAD, branch=BRANCH,
                    receipt_sha256=report["receipt_sha256"], io_audit=accounting)
    try:
        # The immutable receipt already consumed the attempt. Close its state
        # before persisting full evidence; failure never triggers another run.
        safe._write_exclusive(ROOT, TERMINAL, safe._encoded(terminal))
        safe._write_exclusive(ROOT, EVIDENCE + "/io-audit.json", safe._encoded(accounting))
        safe._write_exclusive(ROOT, EVIDENCE + "/results.json", safe._encoded(report))
    except BaseException as exc:
        print(json.dumps({"phase": PHASE, "attempt_consumed": True, "outcome_observed": outcome,
                          "evidence_persistence_incident": type(exc).__name__, "io_audit": accounting,
                          "retries": 0}, sort_keys=True), flush=True)
        return 3
    print(json.dumps(dict(fields, head_sha=HEAD, branch=BRANCH,
                          pair_statuses={name: {"status": value["status"],
                              "cases": [{"source_index": frame["source_index"], "status": frame["status"]}
                                        for frame in value["per_frame"]]}
                              for name, value in report["pairs"].items()},
                          files_opened=accounting["files_opened"], open_count=accounting["open_count"],
                          content_bytes_read=accounting["content_bytes_read"], incident=report.get("incident")),
                     sort_keys=True), flush=True)
    return 0 if outcome == "PASS" else 2 if outcome == "FAIL" else 3


if __name__ == "__main__":
    raise SystemExit(main())
