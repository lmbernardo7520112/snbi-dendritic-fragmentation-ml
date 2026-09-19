"""One frozen multimodal TRAIN/DEV invocation after B1 and complete green CI."""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

from snbi_fragmentation.ti3_baseline import RF_PARAMETERS, _scientific_runtime, extract_patch
from snbi_fragmentation.ti3_dataset import validate_manifest
from snbi_fragmentation.ti3_support import checked_native_luminance
from snbi_fragmentation.ti3b_ablation import (
    checked_solutal_luminance, evaluate_ablation, extract_solutal_patch, multimodal_features,
)
from snbi_fragmentation.ti3b_execution import (
    PAIR_SOURCE, RECEIPT_PATH, TERMINAL_PATH, arm_execution, build_inventory,
    canonical_bytes, digest_string, exact, require,
)


BASE = Path("artifacts/evidence/TI3_B_SOLUTAL")
PLAN = Path("artifacts/evidence/TI3_A_RESUME")
REFERENCE = PLAN / "c0r1-resume"
PILOT = Path("artifacts/metadata/ti2-pilot-manifest.json")
AUTHORITY = Path("configs/authority/ti3b-solutal-ablation.json")
CONFIG = Path("configs/ti3/solute-ablation.json")
CHECKPOINT = "7a205327b363f8cdbba99c5e58bf2f1e5d1253d3"
BRANCH = "feat/ti3b-solutal-ablation"
REPOSITORY = "lmbernardo7520112/snbi-dendritic-fragmentation-ml"
REQUIRED_JOBS = ["deterministic-contracts", "scientific-synthetic-contracts",
                 "ti3-synthetic-contracts", "ti3b-synthetic-contracts"]
EXPECTED_CONFIG = {
    "schema": "TI3B-SOLUTAL-ABLATION-1", "representation": "NATIVE_Y",
    "feature_order": ["STRUCTURAL_LBP_10", "SOLUTAL_LBP_10"], "feature_dimension": 20,
    "structural_reference_ba": 0.6875, "rf_parameters": RF_PARAMETERS, "patch_side": 65,
    "lbp": {"P": 8, "R": 1, "method": "uniform", "bins": 10, "range": [0, 10], "density": True},
    "decision_rule": "MULTIMODAL_GT_REFERENCE_ELSE_STRUCTURAL",
    "support_policy": "SOLUTAL_GEOMETRIC_12PCT_15PCT_BORDER4_EROSION1", "mapping": "IDENTITY",
}
EXPECTED_AUTHORITY = {
    "schema": "TI3B-ONE-SHOT-1", "state": "CONDITIONAL_ON_B1_AND_GREEN_CI",
    "repository": REPOSITORY, "branch": BRANCH, "checkpoint": CHECKPOINT,
    "scientific_invocation_limit": 1, "input_sources": ["ESM1", "ESM2", "ESM4", "ESM5"],
    "final_test_execution_authorized": False, "ti3_c_authorized": False,
    "merge_authorized": False, "structural_baseline_rerun_authorized": False,
    "cnn_authorized": False, "receipt_path": RECEIPT_PATH, "results_path": TERMINAL_PATH,
    "ci_jobs_required": REQUIRED_JOBS,
}


def _git(*arguments, binary=False):
    result = subprocess.check_output(["git", "--no-optional-locks", *arguments], text=not binary)
    return result if binary else result.strip()


def _read_text(path):
    require(not path.is_absolute() and ".." not in path.parts, "TEXT_PATH_NOT_RELATIVE")
    require(path.parts[0] in {"artifacts", "src", "tests", "scripts", "configs", ".github", "docs"}
            or path.name in {"requirements-ti3-ml.txt", "pyproject.toml", "README.md", "AGENTS.md"},
            "TEXT_PATH_NOT_ALLOWED")
    require(path.parts[0] != "artifacts" or str(path).startswith(("artifacts/evidence/", "artifacts/metadata/")),
            "TEXT_ARTIFACT_PATH_NOT_ALLOWED")
    require(path.suffix in {".py", ".json", ".md", ".txt", ".sha256", ".yml", ".toml"}, "TEXT_SUFFIX_NOT_ALLOWED")
    for component in (path, *path.parents):
        require(not stat.S_ISLNK(component.lstat().st_mode), "TEXT_SYMLINK_PROHIBITED")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as handle:
        require(stat.S_ISREG(os.fstat(handle.fileno()).st_mode), "REGULAR_TEXT_REQUIRED")
        raw = handle.read()
    raw.decode("utf-8")
    return raw


def _write_once(name, value):
    require(name in {"io-audit.json", "materialization-manifest.json", "results.json"}, "EVIDENCE_NAME_NOT_ALLOWED")
    for component in (BASE, *BASE.parents):
        require(not stat.S_ISLNK(component.lstat().st_mode), "EVIDENCE_SYMLINK_PROHIBITED")
    fd = os.open(BASE / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def validate_ci(proof, head):
    require(type(proof) is dict and proof.get("head_sha") == head
            and proof.get("repository") == REPOSITORY, "CI_HEAD_OR_REPOSITORY_DIVERGENCE")
    runs = proof.get("runs")
    require(type(runs) is list and runs, "CI_PROOF_MISSING")
    observed = set()
    for run in runs:
        require(run.get("head_sha") == head and run.get("status") == "completed"
                and run.get("conclusion") == "success", "CI_NOT_GREEN_AT_B1")
        require(type(run.get("jobs")) is list and run["jobs"], "CI_JOBS_MISSING")
        for job in run["jobs"]:
            require(job.get("status") == "completed" and job.get("conclusion") == "success", "CI_JOB_NOT_GREEN")
            steps = job.get("steps")
            require(type(steps) is list and steps, "CI_STEPS_MISSING")
            require(all(s.get("status") == "completed" and s.get("conclusion") == "success" for s in steps),
                    "CI_STEP_NOT_GREEN")
            observed.add(job.get("name"))
    require(set(REQUIRED_JOBS).issubset(observed), "CI_REQUIRED_JOB_MISSING")


def _validate_reference(manifest, result, terminal, materialization):
    require(result.get("TI3_A") == "PASS" and result.get("SCIENTIFIC_ML_RUNS") == 1
            and result.get("ML_FINAL_TEST_EXECUTED") is False, "TI3A_RESULT_NOT_CLOSED_PASS")
    require(terminal.get("STATE") == "CLOSED_CONSUMED" and terminal.get("TI3_A_EXECUTION_AUTHORIZED") is False
            and terminal.get("FINAL_TEST_OPENS") == 0 and terminal.get("FINAL_TEST_BYTES") == 0,
            "TI3A_AUTHORITY_NOT_CLOSED")
    dev = result["baseline"]["evaluations"]["DEVELOPMENT"]
    require(dev.get("balanced_accuracy") == 0.6875 and dev.get("confusion_matrix") == [[3, 5], [0, 8]],
            "STRUCTURAL_REFERENCE_DIVERGENCE")
    require(exact(result["baseline"]["parameters"], RF_PARAMETERS), "STRUCTURAL_RF_CONTRACT_DIVERGENCE")
    samples = materialization.get("samples")
    require(type(samples) is list and len(samples) == len(manifest["samples"]), "REFERENCE_SAMPLES_DIVERGENCE")
    previous = {s["sample_id"]: s for s in samples}
    require(len(previous) == len(samples), "DUPLICATE_REFERENCE_SAMPLE")
    for sample in manifest["samples"]:
        old = previous.get(sample["sample_id"])
        require(old is not None, "REFERENCE_SAMPLE_MISSING")
        # TI3-A adds factual execution fields; every original field stays fixed.
        require(all(exact(old.get(k), v) for k, v in sample.items()
                    if k not in {"input_opened", "input_hash_if_opened"}),
                "REFERENCE_SAMPLE_METADATA_DIVERGENCE")
        if sample["split"] == "FINAL_TEST":
            require(old.get("input_opened") is False and old.get("patch_sha256") is None
                    and old.get("input_hash_if_opened") is None,
                    "REFERENCE_FINAL_ALREADY_MATERIALIZED")
        else:
            require(old.get("input_opened") is True and old.get("native_integrity_verified") is True
                    and old.get("input_hash_if_opened") == sample["image_sha256"]
                    and digest_string(old.get("patch_sha256")), "REFERENCE_PATCH_CUSTODY_MISSING")
    return previous, result["sample_order"]


def _preflight():
    # Only new execution/evidence metadata is probed; never a source or FINAL.
    require(not os.path.lexists(RECEIPT_PATH) and not os.path.lexists(TERMINAL_PATH), "TI3B_AUTHORITY_ALREADY_CONSUMED")
    head = _git("rev-parse", "HEAD")
    require(_git("branch", "--show-current") == BRANCH
            and _git("rev-parse", "HEAD^") == CHECKPOINT, "B1_OR_BRANCH_DIVERGENCE")
    require(_git("rev-parse", "origin/" + BRANCH) == head, "B1_LOCAL_REMOTE_REF_DIVERGENCE")
    require(not _git("diff", "--name-only") and not _git("diff", "--cached", "--name-only"), "TRACKED_WORKTREE_OR_INDEX_DIRTY")
    require(_git("remote", "get-url", "origin") == "https://github.com/" + REPOSITORY + ".git", "REPOSITORY_IDENTITY_DIVERGENCE")
    require(sys.version_info[:2] == (3, 12) and Path(sys.prefix).absolute() == Path(".venv").absolute(),
            "REPOSITORY_PYTHON312_VENV_REQUIRED")
    require(exact(json.loads(_read_text(AUTHORITY)), EXPECTED_AUTHORITY), "CANONICAL_TI3B_AUTHORITY_DIVERGENCE")
    require(exact(json.loads(_read_text(CONFIG)), EXPECTED_CONFIG), "SCIENTIFIC_CONFIGURATION_DIVERGENCE")
    freeze_bytes = _read_text(BASE / "method-freeze.json")
    require(_git("show", "HEAD:" + str(BASE / "method-freeze.json"), binary=True) == freeze_bytes,
            "FREEZE_NOT_COMMITTED_AT_B1")
    freeze = json.loads(freeze_bytes)
    hashes = freeze.get("text_sha256")
    required_paths = {str(AUTHORITY), str(CONFIG), str(PLAN / "dataset_manifest.json"), str(PILOT),
                      str(REFERENCE / "results.json"), str(REFERENCE / "terminal-state.json"),
                      str(REFERENCE / "materialization-manifest.json"),
                      "scripts/run_ti3b_ablation.py", "src/snbi_fragmentation/ti3b_execution.py",
                      "src/snbi_fragmentation/ti3b_ablation.py", "src/snbi_fragmentation/ti3_baseline.py",
                      "src/snbi_fragmentation/ti3_dataset.py", "src/snbi_fragmentation/ti3_support.py"}
    require(type(hashes) is dict and required_paths.issubset(hashes), "INCOMPLETE_SCIENTIFIC_FREEZE")
    for name, expected in hashes.items():
        raw = _read_text(Path(name))
        require(digest_string(expected) and hashlib.sha256(raw).hexdigest() == expected, "B1_FROZEN_TEXT_DIVERGENCE")
        require(_git("show", "HEAD:" + name, binary=True) == raw, "B1_FROZEN_BLOB_DIVERGENCE")
    validate_ci(json.loads(_read_text(BASE / "ci-proof.json")), head)
    manifest_bytes = _read_text(PLAN / "dataset_manifest.json")
    manifest = json.loads(manifest_bytes)
    validate_manifest(manifest)
    require(manifest["site_count"] == 52 and len(manifest["ignore_geometry"]) == 383, "TARGET_INVENTORY_DIVERGENCE")
    inventory = build_inventory(manifest, json.loads(_read_text(PILOT)))
    previous, expected_order = _validate_reference(
        manifest, json.loads(_read_text(REFERENCE / "results.json")),
        json.loads(_read_text(REFERENCE / "terminal-state.json")),
        json.loads(_read_text(REFERENCE / "materialization-manifest.json")),
    )
    np = _scientific_runtime()
    active = {"state": "ARMED_ONCE", "head_sha": head, "scientific_invocation_limit": 1,
              "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
              "inventory_sha256": hashlib.sha256(canonical_bytes(inventory)).hexdigest(),
              "method_freeze_sha256": hashlib.sha256(freeze_bytes).hexdigest()}
    return head, manifest, manifest_bytes, inventory, active, previous, expected_order, np


def _closed_fields():
    return {"ML_FINAL_TEST": "SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE", "ML_FINAL_TEST_EXECUTED": False,
            "FORECASTING_AUTHORIZED": False, "CAUSALITY_CLAIM_AUTHORIZED": False,
            "EXTERNAL_GENERALIZATION_CLAIM": False, "TI3_C_AUTHORIZED": False,
            "MERGE_AUTHORIZED": False, "TI3_B_EXECUTION_AUTHORIZED": False,
            "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"}


def main():
    try:
        head, manifest, manifest_bytes, inventory, active, previous, expected_order, np = _preflight()
    except Exception as error:
        result = {**_closed_fields(), "TI3_B": "BLOCKED_PRE_EXECUTION", "STATE": "CLOSED_BLOCKED",
                  "error_type": type(error).__name__, "error_code": getattr(error, "code", type(error).__name__),
                  "SCIENTIFIC_TI3B_RUNS": 0, "experimental_opens": 0, "experimental_bytes": 0}
        if not os.path.lexists(RECEIPT_PATH) and not os.path.lexists(TERMINAL_PATH):
            _write_once("results.json", result)
        print(json.dumps(result, sort_keys=True))
        return 3
    reader, outcome = None, None
    stage, call_started = "ARMING", False
    patch_records = []
    rows, labels, sample_ids = ({"TRAIN": [], "DEVELOPMENT": []} for _ in range(3))
    try:
        reader = arm_execution(Path("."), manifest_bytes, inventory, active, head)
        stage = "INPUT_AUTHENTICATION_AND_SUPPORT"
        paired_records = {(r["source_id"], r["frame_index"]): r for r in inventory}
        for source in manifest["source_inventory"]:
            if source["split"] == "FINAL_TEST":
                continue
            samples = sorted([s for s in manifest["samples"] if (s["source_id"], s["frame_index"])
                              == (source["source_id"], source["frame_index"])], key=lambda s: s["sample_id"])
            require(samples and all(s["split"] == source["split"] for s in samples), "SAMPLE_SPLIT_DIVERGENCE")
            solute = paired_records[(PAIR_SOURCE[source["source_id"]], source["frame_index"])]
            structural_raw = reader.read_native(source)
            structural_y, structural_support = checked_native_luminance(structural_raw, source, samples)
            solutal_raw = reader.read_native(solute)
            solutal_y, solutal_support = checked_solutal_luminance(solutal_raw, solute, samples)
            for sample in samples:
                structural_patch = extract_patch(structural_y, sample)
                structural_hash = hashlib.sha256(structural_patch.tobytes()).hexdigest()
                require(structural_hash == previous[sample["sample_id"]]["patch_sha256"], "STRUCTURAL_PATCH_DIVERGENCE")
                solutal_patch = extract_solutal_patch(solutal_y, solute, sample)
                feature = multimodal_features(structural_patch, solutal_patch)
                split = sample["split"]
                rows[split].append(feature)
                labels[split].append(sample["baseline_label"])
                sample_ids[split].append(sample["sample_id"])
                patch_records.append({"sample_id": sample["sample_id"], "split": split,
                    "structural_source_id": source["source_id"], "solutal_source_id": solute["source_id"],
                    "frame_index": source["frame_index"], "center_x": sample["center_x"], "center_y": sample["center_y"],
                    "patch_side_px": 65, "structural_patch_sha256": structural_hash,
                    "structural_reference_patch_equal": True,
                    "solutal_patch_sha256": hashlib.sha256(solutal_patch.tobytes()).hexdigest(),
                    "feature_dimension": 20, "feature_sha256": hashlib.sha256(feature.tobytes()).hexdigest(),
                    "structural_support": structural_support, "solutal_support": solutal_support})
            del structural_raw, structural_y, solutal_raw, solutal_y
        require(exact(sample_ids, expected_order), "TI3A_SAMPLE_ORDER_DIVERGENCE")
        require(len(rows["TRAIN"]) == 34 and len(rows["DEVELOPMENT"]) == 16
                and sum(labels["TRAIN"]) == 17 and sum(labels["DEVELOPMENT"]) == 8, "SAMPLE_OR_LABEL_COUNTS_DIVERGENCE")
        audit = reader.report()
        require(audit["experimental_opens"] == 10 and audit["experimental_bytes"] == 19469052
                and audit["final_test_opens"] == 0 and audit["final_test_bytes"] == 0, "PRE_FIT_IO_DIVERGENCE")
        stage, call_started = "SINGLE_MULTIMODAL_CALL", True
        outcome = evaluate_ablation(np.asarray(rows["TRAIN"]), np.asarray(labels["TRAIN"], dtype=np.int64),
                                    np.asarray(rows["DEVELOPMENT"]), np.asarray(labels["DEVELOPMENT"], dtype=np.int64))
        stage = "COMPLETED"
        result = {**_closed_fields(), "TI3_B": "PASS", "SOLUTAL_ABLATION": "COMPLETED",
                  "STATE": "CLOSED_CONSUMED", "SCIENTIFIC_TI3B_RUNS": 1,
                  "TI3_C_READY_FOR_AUTHOR_DECISION": True, "B1": head,
                  "ablation": outcome, "sample_order": sample_ids}
        exit_code = 0
    except BaseException as error:
        result = {**_closed_fields(), "TI3_B": "BLOCKED", "STATE": "CLOSED_BLOCKED", "stage": stage,
                  "error_type": type(error).__name__, "error_code": getattr(error, "code", type(error).__name__),
                  "SCIENTIFIC_TI3B_RUNS": 0, "scientific_calls_started": int(call_started),
                  "fit_calls_if_failure_inside_ablation": "NOT_VERIFIED" if call_started else 0,
                  "TI3_C_READY_FOR_AUTHOR_DECISION": False, "B1": head}
        exit_code = 2
    if reader is None:
        # Exclusive receipt failures never overwrite already-existing evidence.
        if not os.path.lexists(TERMINAL_PATH):
            _write_once("results.json", result)
        print(json.dumps(result, sort_keys=True))
        return exit_code
    reader.close()
    audit = reader.report()
    audit.update(scientific_calls_started=int(call_started), successful_scientific_calls=int(outcome is not None))
    _write_once("io-audit.json", audit)
    materialization = {"B1": head, "planning_manifest_sha256": active["manifest_sha256"],
                       "samples": patch_records, "patch_pairs": len(patch_records),
                       "final_samples": [{"sample_id": s["sample_id"], "split": "FINAL_TEST",
                           "structural_input_opened": False, "solutal_input_opened": False,
                           "structural_patch_sha256": None, "solutal_patch_sha256": None,
                           "feature_sha256": None} for s in manifest["samples"] if s["split"] == "FINAL_TEST"]}
    _write_once("materialization-manifest.json", materialization)
    _write_once("results.json", result)
    print(json.dumps({"TI3_B": result["TI3_B"], "stage": stage,
                      "SCIENTIFIC_TI3B_RUNS": result["SCIENTIFIC_TI3B_RUNS"], "patch_pairs": len(patch_records),
                      "experimental_opens": audit["experimental_opens"], "experimental_bytes": audit["experimental_bytes"],
                      "final_test_opens": audit["final_test_opens"]}, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
