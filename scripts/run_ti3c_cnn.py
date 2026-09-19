"""Single preregistered CNN invocation; DEV opens only after ten TRAIN epochs."""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

from snbi_fragmentation.ti3_baseline import _scientific_runtime, extract_patch
from snbi_fragmentation.ti3_dataset import validate_manifest
from snbi_fragmentation.ti3_support import checked_native_luminance
from snbi_fragmentation.ti3b_ablation import checked_solutal_luminance, extract_solutal_patch
from snbi_fragmentation.ti3c_execution import (
    PAIR_SOURCE, RECEIPT_PATH, TERMINAL_PATH, arm_execution, build_inventory,
    canonical_bytes, digest_string, exact, require,
)
from snbi_fragmentation.ti3c_cnn import (
    train_fixed, evaluate_fixed, development_decision, validate_runtime, acquisition_only_diagnostic,
)


BASE = Path("artifacts/evidence/TI3_C_CNN")
PLAN = Path("artifacts/evidence/TI3_A_RESUME")
REFERENCE = Path("artifacts/evidence/TI3_B_SOLUTAL")
PILOT = Path("artifacts/metadata/ti2-pilot-manifest.json")
AUTHORITY = Path("configs/authority/ti3c-minimal-cnn.json")
CONFIG = Path("configs/ti3/minimal-cnn.json")
CHECKPOINT = "48da1af69ce48b3287f19b26bfbd24b79243d90e"
BRANCH = "feat/ti3c-minimal-multimodal-cnn"
REPOSITORY = "lmbernardo7520112/snbi-dendritic-fragmentation-ml"
REQUIRED_JOBS = ["deterministic-contracts", "scientific-synthetic-contracts",
                 "ti3-synthetic-contracts", "ti3b-synthetic-contracts", "ti3c-synthetic-contracts"]
EXPECTED_CONFIG = {
    "schema": "TI3C-MINIMAL-CNN-1", "representation": "NATIVE_Y",
    "channel_order": ["STRUCTURAL_LUMINANCE", "RELATIVE_SOLUTE_FIELD_LUMINANCE"],
    "input_shape": [2, 65, 65], "normalization": "FLOAT32_DIVIDE_255",
    "torch_version": "2.4.1+cpu", "device": "cpu", "parameter_count": 170,
    "architecture": ["Conv2d(2,8,3,padding=1,bias=True)", "ReLU()",
                     "MaxPool2d(2,stride=2)", "AdaptiveAvgPool2d((1,1))",
                     "Flatten()", "Linear(8,2,bias=True)"],
    "seeds": {"python": 42, "numpy": 42, "torch": 42, "loader_generator": 42},
    "deterministic_algorithms": True, "torch_num_threads": 1, "num_workers": 0,
    "loss": "CrossEntropyLoss()", "optimizer": "Adam", "learning_rate": 0.005,
    "weight_decay": 0.0, "epochs": 10, "batch_size": 8, "train_shuffle": True,
    "scheduler": None, "early_stopping": False, "augmentation": "NONE",
    "rf_reference_dev_balanced_accuracy": 0.75,
    "decision_rule": "CNN_GT_0_75_ELSE_MULTIMODAL_LBP_RF",
    "support_policy": "UNCHANGED_TI3B_STRUCTURAL_AND_SOLUTAL", "mapping": "IDENTITY",
    "execution_order": ["MATERIALIZE_TRAIN", "TRAIN_10_EPOCHS", "EVALUATE_TRAIN",
                        "MATERIALIZE_DEVELOPMENT", "EVALUATE_DEVELOPMENT_ONCE"],
}
EXPECTED_AUTHORITY = {
    "schema": "TI3C-ONE-SHOT-1", "state": "CONDITIONAL_ON_C1_AND_GREEN_CI",
    "repository": REPOSITORY, "branch": BRANCH, "checkpoint": CHECKPOINT,
    "scientific_invocation_limit": 1, "input_sources": ["ESM1", "ESM2", "ESM4", "ESM5"],
    "final_test_execution_authorized": False, "final_evaluation_authorized": False,
    "merge_authorized": False, "structural_baseline_rerun_authorized": False,
    "multimodal_rf_rerun_authorized": False, "cnn_authorized": True,
    "receipt_path": RECEIPT_PATH, "results_path": TERMINAL_PATH,
    "ci_jobs_required": REQUIRED_JOBS,
}


def _git(*arguments, binary=False):
    result = subprocess.check_output(["git", "--no-optional-locks", *arguments], text=not binary)
    return result if binary else result.strip()


def _read_text(path):
    require(not path.is_absolute() and ".." not in path.parts, "TEXT_PATH_NOT_RELATIVE")
    require(path.parts[0] in {"artifacts", "src", "tests", "scripts", "configs", ".github", "docs"}
            or path.name in {"requirements-ti3-ml.txt", "requirements-ti3c-cnn.txt",
                             "constraints-ti3c-cnn.txt", "pyproject.toml", "README.md", "AGENTS.md"},
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
                and run.get("conclusion") == "success", "CI_NOT_GREEN_AT_C1")
        require(type(run.get("jobs")) is list and run["jobs"], "CI_JOBS_MISSING")
        for job in run["jobs"]:
            require(job.get("status") == "completed" and job.get("conclusion") == "success", "CI_JOB_NOT_GREEN")
            steps = job.get("steps")
            require(type(steps) is list and steps, "CI_STEPS_MISSING")
            require(all(s.get("status") == "completed" and s.get("conclusion") == "success" for s in steps),
                    "CI_STEP_NOT_GREEN")
            observed.add(job.get("name"))
    require(set(REQUIRED_JOBS).issubset(observed), "CI_REQUIRED_JOB_MISSING")


def acquisition_diagnostic(manifest):
    """Revalidate the frozen metadata-only diagnostic without experimental I/O."""
    return acquisition_only_diagnostic(manifest["samples"])


def _validate_reference(manifest, result, terminal, materialization):
    require(result.get("TI3_B") == "PASS" and exact(result.get("SCIENTIFIC_TI3B_RUNS"), 1)
            and result.get("ML_FINAL_TEST_EXECUTED") is False, "TI3B_RESULT_NOT_CLOSED_PASS")
    require(terminal.get("STATE") == "CLOSED_CONSUMED" and terminal.get("TI3_B_EXECUTION_AUTHORIZED") is False
            and all(exact(terminal.get(k), 0) for k in ("FINAL_STRUCTURAL_OPENS", "FINAL_STRUCTURAL_BYTES",
                                                       "FINAL_SOLUTAL_OPENS", "FINAL_SOLUTAL_BYTES")),
            "TI3B_AUTHORITY_NOT_CLOSED")
    dev = result["ablation"]["evaluations"]["DEVELOPMENT"]
    require(exact(dev.get("balanced_accuracy"), 0.75) and exact(dev.get("confusion_matrix"), [[4, 4], [0, 8]]),
            "MULTIMODAL_REFERENCE_DIVERGENCE")
    require(result["ablation"].get("dev_modality_preference") == "STRUCTURAL_PLUS_RELATIVE_SOLUTE",
            "FROZEN_MODALITY_DIVERGENCE")
    samples, final = materialization.get("samples"), materialization.get("final_samples")
    require(type(samples) is list and len(samples) == 50 and type(final) is list and len(final) == 6,
            "REFERENCE_SAMPLES_DIVERGENCE")
    previous = {s["sample_id"]: s for s in samples}
    sealed = {s["sample_id"]: s for s in final}
    require(len(previous) == 50 and len(sealed) == 6, "DUPLICATE_REFERENCE_SAMPLE")
    expected_order = {split: [] for split in ("TRAIN", "DEVELOPMENT")}
    for source in manifest["source_inventory"]:
        if source["split"] != "FINAL_TEST":
            expected_order[source["split"]].extend(sorted(s["sample_id"] for s in manifest["samples"]
                if (s["source_id"], s["frame_index"]) == (source["source_id"], source["frame_index"])))
    require(exact(result.get("sample_order"), expected_order), "REFERENCE_SAMPLE_ORDER_DIVERGENCE")
    for sample in manifest["samples"]:
        if sample["split"] == "FINAL_TEST":
            old = sealed.get(sample["sample_id"])
            require(old is not None and old.get("split") == "FINAL_TEST"
                    and old.get("structural_input_opened") is False and old.get("solutal_input_opened") is False
                    and all(old.get(k) is None for k in ("structural_patch_sha256", "solutal_patch_sha256", "feature_sha256")),
                    "REFERENCE_FINAL_ALREADY_MATERIALIZED")
            continue
        old = previous.get(sample["sample_id"])
        require(old is not None, "REFERENCE_SAMPLE_MISSING")
        expected = {"split": sample["split"], "structural_source_id": sample["source_id"],
                    "solutal_source_id": PAIR_SOURCE[sample["source_id"]], "frame_index": sample["frame_index"],
                    "center_x": sample["center_x"], "center_y": sample["center_y"], "patch_side_px": 65}
        require(all(exact(old.get(k), v) for k, v in expected.items()), "REFERENCE_SAMPLE_METADATA_DIVERGENCE")
        require(all(digest_string(old.get(k)) for k in ("structural_patch_sha256", "solutal_patch_sha256")),
                "REFERENCE_PATCH_CUSTODY_MISSING")
    return previous, expected_order


def _preflight():
    require(not os.path.lexists(RECEIPT_PATH) and not os.path.lexists(TERMINAL_PATH), "TI3C_AUTHORITY_ALREADY_CONSUMED")
    head = _git("rev-parse", "HEAD")
    require(_git("branch", "--show-current") == BRANCH
            and _git("rev-parse", "HEAD^") == CHECKPOINT, "C1_OR_BRANCH_DIVERGENCE")
    require(_git("rev-parse", "origin/" + BRANCH) == head, "C1_LOCAL_REMOTE_REF_DIVERGENCE")
    require(not _git("diff", "--name-only") and not _git("diff", "--cached", "--name-only"), "TRACKED_WORKTREE_OR_INDEX_DIRTY")
    require(_git("remote", "get-url", "origin") == "https://github.com/" + REPOSITORY + ".git", "REPOSITORY_IDENTITY_DIVERGENCE")
    require(sys.version_info[:2] == (3, 12) and Path(sys.prefix).absolute() == Path(".venv").absolute(),
            "REPOSITORY_PYTHON312_VENV_REQUIRED")
    require(exact(json.loads(_read_text(AUTHORITY)), EXPECTED_AUTHORITY), "CANONICAL_TI3C_AUTHORITY_DIVERGENCE")
    require(exact(json.loads(_read_text(CONFIG)), EXPECTED_CONFIG), "SCIENTIFIC_CONFIGURATION_DIVERGENCE")
    freeze_bytes = _read_text(BASE / "method-freeze.json")
    require(_git("show", "HEAD:" + str(BASE / "method-freeze.json"), binary=True) == freeze_bytes,
            "FREEZE_NOT_COMMITTED_AT_C1")
    hashes = json.loads(freeze_bytes).get("text_sha256")
    required_paths = {str(AUTHORITY), str(CONFIG), str(PLAN / "dataset_manifest.json"), str(PILOT),
                      str(REFERENCE / "results.json"), str(REFERENCE / "terminal-state.json"),
                      str(REFERENCE / "materialization-manifest.json"), str(BASE / "acquisition-only-diagnostic.json"),
                      "requirements-ti3-ml.txt", "requirements-ti3c-cnn.txt", "constraints-ti3c-cnn.txt",
                      "scripts/run_ti3c_cnn.py", "src/snbi_fragmentation/ti3c_execution.py",
                      "src/snbi_fragmentation/ti3c_cnn.py", "src/snbi_fragmentation/ti3_baseline.py",
                      "src/snbi_fragmentation/ti3_dataset.py", "src/snbi_fragmentation/ti3_support.py",
                      "src/snbi_fragmentation/ti3b_ablation.py"}
    require(type(hashes) is dict and required_paths.issubset(hashes), "INCOMPLETE_SCIENTIFIC_FREEZE")
    for name, expected in hashes.items():
        raw = _read_text(Path(name))
        require(digest_string(expected) and hashlib.sha256(raw).hexdigest() == expected, "C1_FROZEN_TEXT_DIVERGENCE")
        require(_git("show", "HEAD:" + name, binary=True) == raw, "C1_FROZEN_BLOB_DIVERGENCE")
    validate_ci(json.loads(_read_text(BASE / "ci-proof.json")), head)
    manifest_bytes = _read_text(PLAN / "dataset_manifest.json")
    manifest = json.loads(manifest_bytes)
    validate_manifest(manifest)
    require(manifest["site_count"] == 52 and len(manifest["ignore_geometry"]) == 383, "TARGET_INVENTORY_DIVERGENCE")
    diagnostic = acquisition_diagnostic(manifest)
    require(exact(json.loads(_read_text(BASE / "acquisition-only-diagnostic.json")), diagnostic),
            "ACQUISITION_DIAGNOSTIC_DIVERGENCE")
    inventory = build_inventory(manifest, json.loads(_read_text(PILOT)))
    previous, expected_order = _validate_reference(
        manifest, json.loads(_read_text(REFERENCE / "results.json")),
        json.loads(_read_text(REFERENCE / "terminal-state.json")),
        json.loads(_read_text(REFERENCE / "materialization-manifest.json")),
    )
    np = _scientific_runtime()
    versions = validate_runtime()
    active = {"state": "ARMED_ONCE", "head_sha": head, "scientific_invocation_limit": 1,
              "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
              "inventory_sha256": hashlib.sha256(canonical_bytes(inventory)).hexdigest(),
              "method_freeze_sha256": hashlib.sha256(freeze_bytes).hexdigest()}
    return head, manifest, manifest_bytes, inventory, active, previous, expected_order, np, versions, diagnostic


def _closed_fields():
    return {"ML_FINAL_TEST": "SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE", "ML_FINAL_TEST_EXECUTED": False,
            "FORECASTING_AUTHORIZED": False, "CAUSALITY_CLAIM_AUTHORIZED": False,
            "EXTERNAL_GENERALIZATION_CLAIM": False, "FINAL_EVALUATION_AUTHORIZED": False,
            "MERGE_AUTHORIZED": False, "TI3_C_EXECUTION_AUTHORIZED": False,
            "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"}


def materialize_split(split, manifest, inventory, reader, previous, expected_order, np, patch_records):
    require(split in ("TRAIN", "DEVELOPMENT"), "FINAL_OR_UNKNOWN_SPLIT_DENIED")
    paired = {(r["source_id"], r["frame_index"]): r for r in inventory}
    rows, labels, metadata = [], [], []
    for source in manifest["source_inventory"]:
        if source["split"] != split:
            continue
        samples = sorted([s for s in manifest["samples"] if (s["source_id"], s["frame_index"])
                          == (source["source_id"], source["frame_index"])], key=lambda s: s["sample_id"])
        require(samples and all(s["split"] == split for s in samples), "SAMPLE_SPLIT_DIVERGENCE")
        solute = paired[(PAIR_SOURCE[source["source_id"]], source["frame_index"])]
        structural_raw = reader.read_native(source)
        structural_y, structural_support = checked_native_luminance(structural_raw, source, samples)
        solutal_raw = reader.read_native(solute)
        solutal_y, solutal_support = checked_solutal_luminance(solutal_raw, solute, samples)
        for sample in samples:
            structural_patch = extract_patch(structural_y, sample)
            solutal_patch = extract_solutal_patch(solutal_y, solute, sample)
            structural_hash = hashlib.sha256(structural_patch.tobytes()).hexdigest()
            solutal_hash = hashlib.sha256(solutal_patch.tobytes()).hexdigest()
            old = previous[sample["sample_id"]]
            require(structural_hash == old["structural_patch_sha256"], "STRUCTURAL_PATCH_DIVERGENCE")
            require(solutal_hash == old["solutal_patch_sha256"], "SOLUTAL_PATCH_DIVERGENCE")
            row = np.stack((structural_patch, solutal_patch))
            rows.append(row)
            labels.append(sample["baseline_label"])
            metadata.append(sample)
            patch_records.append({"sample_id": sample["sample_id"], "split": split,
                "structural_source_id": source["source_id"], "solutal_source_id": solute["source_id"],
                "frame_index": source["frame_index"], "center_x": sample["center_x"], "center_y": sample["center_y"],
                "patch_side_px": 65, "structural_patch_sha256": structural_hash,
                "solutal_patch_sha256": solutal_hash, "ti3b_both_patch_hashes_equal": True,
                "input_shape": [2, 65, 65], "input_uint8_sha256": hashlib.sha256(row.tobytes()).hexdigest(),
                "structural_support": structural_support, "solutal_support": solutal_support})
        del structural_raw, structural_y, solutal_raw, solutal_y
    require(exact([s["sample_id"] for s in metadata], expected_order[split]), "TI3B_SAMPLE_ORDER_DIVERGENCE")
    count, positives = (34, 17) if split == "TRAIN" else (16, 8)
    require(len(rows) == count and sum(labels) == positives, "SAMPLE_OR_LABEL_COUNTS_DIVERGENCE")
    array = np.stack(rows)
    array.setflags(write=False)
    return array, np.asarray(labels, dtype=np.int64), metadata


def main():
    try:
        head, manifest, manifest_bytes, inventory, active, previous, order, np, versions, diagnostic = _preflight()
    except Exception as error:
        result = {**_closed_fields(), "TI3_C": "BLOCKED_PRE_EXECUTION", "STATE": "CLOSED_BLOCKED",
                  "error_type": type(error).__name__, "error_code": getattr(error, "code", type(error).__name__),
                  "SCIENTIFIC_TI3C_RUNS": 0, "SCIENTIFIC_TI3C_COMPLETED_RUNS": 0,
                  "experimental_opens": 0, "experimental_bytes": 0}
        if not os.path.lexists(RECEIPT_PATH) and not os.path.lexists(TERMINAL_PATH):
            _write_once("results.json", result)
        print(json.dumps(result, sort_keys=True))
        return 3
    reader, training, train_eval, dev_eval = None, None, None, None
    stage, train_started, dev_started = "ARMING", False, False
    patch_records = []
    try:
        reader = arm_execution(Path("."), manifest_bytes, inventory, active, head)
        stage = "MATERIALIZE_TRAIN"
        train_x, train_y, train_samples = materialize_split("TRAIN", manifest, inventory, reader, previous, order, np, patch_records)
        audit = reader.report()
        require(audit["experimental_opens"] == 6 and audit["experimental_bytes"] == 11686032
                and all(r["opens"] == 0 for r in audit["entries"] if r["split"] != "TRAIN"), "PRE_TRAIN_IO_DIVERGENCE")
        stage, train_started = "TRAIN_10_EPOCHS", True
        model, training = train_fixed(train_x, train_y, train_samples)
        stage = "EVALUATE_TRAIN"
        train_eval = evaluate_fixed(model, train_x, train_y, train_samples, "TRAIN")
        del train_x, train_y
        stage = "MATERIALIZE_DEVELOPMENT_AFTER_TRAIN"
        dev_x, dev_y, dev_samples = materialize_split("DEVELOPMENT", manifest, inventory, reader, previous, order, np, patch_records)
        audit = reader.report()
        require(audit["experimental_opens"] == 10 and audit["experimental_bytes"] == 19469052
                and audit["final_test_opens"] == 0 and audit["final_test_bytes"] == 0, "PRE_DEV_IO_DIVERGENCE")
        stage, dev_started = "EVALUATE_DEVELOPMENT_ONCE", True
        dev_eval = evaluate_fixed(model, dev_x, dev_y, dev_samples, "DEVELOPMENT")
        selection = development_decision(dev_eval["balanced_accuracy"])
        stage = "COMPLETED"
        result = {**_closed_fields(), "TI3_C": "PASS", "STATE": "CLOSED_CONSUMED", "SCIENTIFIC_TI3C_RUNS": 1,
                  "SCIENTIFIC_TI3C_COMPLETED_RUNS": 1,
                  "MODEL_FAMILY_SELECTION": "COMPLETE", "FINAL_EVALUATION_READY_FOR_AUTHOR_DECISION": True,
                  "C1_CNN": head, "training": training, "evaluations": {"TRAIN": train_eval, "DEVELOPMENT": dev_eval},
                  "selection": selection, "sample_order": order, "environment": versions,
                  "acquisition_only_diagnostic": diagnostic,
                  "possible_overfit": train_eval["balanced_accuracy"] == 1.0 and dev_eval["balanced_accuracy"] < 1.0,
                  "training_calls": 1, "development_evaluations": 1, "retries": 0, "tuning_runs": 0}
        exit_code = 0
    except BaseException as error:
        result = {**_closed_fields(), "TI3_C": "BLOCKED", "STATE": "CLOSED_BLOCKED", "stage": stage,
                  "error_type": type(error).__name__, "error_code": getattr(error, "code", type(error).__name__),
                  "SCIENTIFIC_TI3C_RUNS": int(reader is not None), "SCIENTIFIC_TI3C_COMPLETED_RUNS": 0,
                  "training_calls_started": int(train_started),
                  "development_evaluations_started": int(dev_started), "training": training,
                  "completed_train_evaluation": train_eval, "completed_development_evaluation": dev_eval,
                  "FINAL_EVALUATION_READY_FOR_AUTHOR_DECISION": False, "C1_CNN": head}
        exit_code = 2
    if reader is None:
        if not os.path.lexists(TERMINAL_PATH):
            _write_once("results.json", result)
        print(json.dumps(result, sort_keys=True))
        return exit_code
    reader.close()
    audit = reader.report()
    audit.update(training_calls_started=int(train_started), training_calls_completed=int(training is not None),
                 development_evaluations_started=int(dev_started), development_evaluations_completed=int(dev_eval is not None))
    _write_once("io-audit.json", audit)
    materialization = {"C1_CNN": head, "planning_manifest_sha256": active["manifest_sha256"],
                       "samples": patch_records, "patch_pairs": len(patch_records),
                       "final_samples": [{"sample_id": s["sample_id"], "split": "FINAL_TEST",
                           "structural_input_opened": False, "solutal_input_opened": False,
                           "structural_patch_sha256": None, "solutal_patch_sha256": None,
                           "input_uint8_sha256": None} for s in manifest["samples"] if s["split"] == "FINAL_TEST"]}
    _write_once("materialization-manifest.json", materialization)
    _write_once("results.json", result)
    print(json.dumps({"TI3_C": result["TI3_C"], "stage": stage,
                      "SCIENTIFIC_TI3C_RUNS": result["SCIENTIFIC_TI3C_RUNS"], "patch_pairs": len(patch_records),
                      "experimental_opens": audit["experimental_opens"], "experimental_bytes": audit["experimental_bytes"],
                      "final_test_opens": audit["final_test_opens"]}, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
