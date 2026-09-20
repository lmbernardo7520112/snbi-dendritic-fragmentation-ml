"""One final RF refit, then durable prediction-first evaluation of six samples."""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

from snbi_fragmentation.ti3_baseline import _scientific_runtime, RF_PARAMETERS, REQUIRED_VERSIONS
from snbi_fragmentation.ti3_dataset import validate_manifest
from snbi_fragmentation.ti3b_ablation import multimodal_features
from snbi_fragmentation.ti3d_execution import (
    PAIR_SOURCE, RECEIPT_PATH, TERMINAL_PATH, arm_execution, build_inventory,
    canonical_bytes, digest_string, exact, require,
)
from snbi_fragmentation.ti3d_final import (
    FinalEvaluationSession, validate_sample_contract, canonical_bytes as evidence_bytes,
)
from snbi_fragmentation.ti3d_support import checked_luminance, extract_authorized_patch

BASE = Path("artifacts/evidence/TI3_D_FINAL")
PLAN = Path("artifacts/evidence/TI3_A_RESUME")
REFERENCE = Path("artifacts/evidence/TI3_B_SOLUTAL")
CNN_REFERENCE = Path("artifacts/evidence/TI3_C_CNN")
PILOT = Path("artifacts/metadata/ti2-pilot-manifest.json")
AUTHORITY = Path("configs/authority/ti3d-final.json")
CONFIG = Path("configs/ti3/final-evaluation.json")
CHECKPOINT = "a8227901506c3de6fe4a5a4bd19021be3f39b2e8"
BRANCH = "feat/ti3d-final-evaluation"
REPOSITORY = "lmbernardo7520112/snbi-dendritic-fragmentation-ml"
MANIFEST_SHA256 = "c8e82b72ff5dc51d188a764c577c11d514474b14d90aea6292c1439e776fb487"
FINAL_MANIFEST_SHA256 = "985af14d0d6a74298bbc0380767f900d264f544303e46ecd8ed4dc0eb1ab649f"
REQUIRED_JOBS = ["deterministic-contracts", "scientific-synthetic-contracts",
    "ti3-synthetic-contracts", "ti3b-synthetic-contracts", "ti3c-synthetic-contracts",
    "ti3d-final-synthetic-contracts"]
EXPECTED_CONFIG = {
    "schema": "TI3D-FINAL-EVALUATION-1", "model_family": "MULTIMODAL_LBP_RF",
    "representation": "NATIVE_Y", "patch_side_px": 65,
    "feature_order": ["STRUCTURAL_LBP_10", "SOLUTAL_LBP_10"], "feature_dimension": 20,
    "lbp": {"P": 8, "R": 1, "method": "uniform", "bins": 10, "range": [0, 10], "density": True},
    "rf_parameters": RF_PARAMETERS, "prediction": "SKLEARN_PREDICT",
    "final_training_set": "TRAIN_UNION_DEVELOPMENT", "training_samples": 50,
    "training_class_counts": [25, 25], "final_samples": 6, "final_class_counts": [3, 3],
    "training_order": "TI3B_TRAIN_THEN_DEVELOPMENT",
    "final_order": "FROZEN_TRAINING_PLAN",
    "mapping": "IDENTITY", "support_policy": "UNCHANGED_TI3B_NUMERIC_PREDICATES_EXPLICIT_TI3D_ADMISSION",
    "primary_metric": "balanced_accuracy", "secondary_metrics": ["accuracy", "precision", "recall", "f1", "confusion_matrix"],
    "execution_order": ["EXCLUSIVE_RECEIPT", "MATERIALIZE_ALL_TRAINING_PATCHES", "TRAINING_FEATURES",
        "ONE_FINAL_FIT", "DURABLE_FIT_FREEZE", "FINAL_SUPPORT_ALL_PATCHES", "FINAL_FEATURES",
        "FINAL_INFERENCE_WITHOUT_LABELS", "DURABLE_PREDICTIONS", "FINAL_LABEL_ASSOCIATION_AND_SCORING"],
    "expected_training_opens": 10, "expected_training_bytes": 19469052,
    "expected_final_opens": 4, "expected_final_bytes": 7783020,
    "final_result_scope": "SMALL_INTERNAL_TEMPORAL_CONFIRMATION", "performance_pass_floor": None,
    "model_selection_reopened": False, "retry_limit": 0,
}
EXPECTED_AUTHORITY = {
    "schema": "TI3D-ONE-SHOT-1", "state": "CONDITIONAL_ON_D1_AND_GREEN_CI",
    "repository": REPOSITORY, "branch": BRANCH, "checkpoint": CHECKPOINT,
    "scientific_invocation_limit": 1, "final_fit_limit": 1, "final_evaluation_limit": 1,
    "input_sources": ["ESM1", "ESM2", "ESM4", "ESM5"],
    "final_test_execution_authorized": True, "final_only_after_fit_freeze": True,
    "merge_authorized": False, "model_selection_authorized": False,
    "cnn_authorized": False, "structural_only_fit_authorized": False,
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
    require(name in {"io-audit.json", "materialization-manifest.json", "results.json",
                     "fit-freeze.json", "predictions.json"}, "EVIDENCE_NAME_NOT_ALLOWED")
    for component in (BASE, *BASE.parents):
        require(not stat.S_ISLNK(component.lstat().st_mode), "EVIDENCE_SYMLINK_PROHIBITED")
    payload = evidence_bytes(value)
    fd = os.open(BASE / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    parent = os.open(BASE, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)
    return hashlib.sha256(payload).hexdigest()


def validate_ci(proof, head):
    require(type(proof) is dict and proof.get("head_sha") == head
            and proof.get("repository") == REPOSITORY, "CI_HEAD_OR_REPOSITORY_DIVERGENCE")
    runs = proof.get("runs")
    require(type(runs) is list and runs, "CI_PROOF_MISSING")
    observed = set()
    for run in runs:
        require(run.get("head_sha") == head and run.get("status") == "completed"
                and run.get("conclusion") == "success", "CI_NOT_GREEN_AT_D1")
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
        require(all(digest_string(old.get(k)) for k in ("structural_patch_sha256", "solutal_patch_sha256", "feature_sha256")),
                "REFERENCE_PATCH_CUSTODY_MISSING")
    return previous, expected_order



def _validate_policy(manifest, previous_order, policy, final_manifest):
    training_ids = previous_order["TRAIN"] + previous_order["DEVELOPMENT"]
    samples = {s["sample_id"]: s for s in manifest["samples"]}
    final_ids = []
    for image in manifest["source_inventory"]:
        if image["split"] == "FINAL_TEST":
            final_ids.extend(sorted(s["sample_id"] for s in manifest["samples"]
                if (s["source_id"], s["frame_index"]) == (image["source_id"], image["frame_index"])))
    require(exact(policy.get("training_order"), training_ids)
            and exact(policy.get("final_order"), final_ids), "TRAINING_OR_FINAL_ORDER_DIVERGENCE")
    require(policy.get("planning_manifest_sha256") == MANIFEST_SHA256, "POLICY_MANIFEST_DIVERGENCE")
    for ids, key in ((training_ids, "training_samples"), (final_ids, "final_samples")):
        records = policy.get(key)
        require(type(records) is list and len(records) == len(ids), "POLICY_RECORD_COUNT_DIVERGENCE")
        for identifier, record in zip(ids, records):
            require(record.get("sample_id") == identifier and all(
                exact(samples[identifier].get(k), v) for k, v in record.items()), "POLICY_SAMPLE_DIVERGENCE")
    require({s["sample_id"] for s in final_manifest["samples"]} == set(final_ids)
            and final_manifest.get("input_opened") is False, "FINAL_MANIFEST_DIVERGENCE")
    training, final = [samples[k] for k in training_ids], [samples[k] for k in final_ids]
    validate_sample_contract(training, final)
    return training, final


def _validate_cnn(result, terminal):
    require(result.get("TI3_C") == "PASS" and result.get("STATE") == "CLOSED_CONSUMED"
            and exact(result.get("SCIENTIFIC_TI3C_RUNS"), 1)
            and exact(result.get("retries"), 0) and exact(result.get("tuning_runs"), 0)
            and result.get("ML_FINAL_TEST_EXECUTED") is False, "TI3C_RESULT_DIVERGENCE")
    selection = result.get("selection", {})
    require(selection.get("model_family_selection") == "COMPLETE"
            and selection.get("final_model_family_preference") == "MULTIMODAL_LBP_RF",
            "CLOSED_MODEL_SELECTION_REQUIRED")
    require(terminal.get("STATE") == "CLOSED_CONSUMED"
            and terminal.get("TI3_C_EXECUTION_AUTHORIZED") is False
            and terminal.get("ML_FINAL_TEST_EXECUTED") is False
            and all(exact(terminal.get(k), 0) for k in ("FINAL_STRUCTURAL_OPENS", "FINAL_STRUCTURAL_BYTES",
                                                       "FINAL_SOLUTAL_OPENS", "FINAL_SOLUTAL_BYTES")),
            "TI3C_AUTHORITY_OR_FINAL_DIVERGENCE")


def _preflight():
    require(not os.path.lexists(RECEIPT_PATH) and not os.path.lexists(TERMINAL_PATH), "TI3D_AUTHORITY_ALREADY_CONSUMED")
    head = _git("rev-parse", "HEAD")
    require(_git("branch", "--show-current") == BRANCH
            and _git("rev-parse", "HEAD^") == CHECKPOINT, "D1_OR_BRANCH_DIVERGENCE")
    require(_git("rev-parse", "origin/" + BRANCH) == head, "D1_LOCAL_REMOTE_REF_DIVERGENCE")
    require(not _git("diff", "--name-only") and not _git("diff", "--cached", "--name-only"), "TRACKED_WORKTREE_OR_INDEX_DIRTY")
    require(_git("remote", "get-url", "origin") == "https://github.com/" + REPOSITORY + ".git", "REPOSITORY_IDENTITY_DIVERGENCE")
    require(sys.version_info[:2] == (3, 12) and Path(sys.prefix).absolute() == Path(".venv").absolute(),
            "REPOSITORY_PYTHON312_VENV_REQUIRED")
    require(exact(json.loads(_read_text(AUTHORITY)), EXPECTED_AUTHORITY), "CANONICAL_TI3D_AUTHORITY_DIVERGENCE")
    require(exact(json.loads(_read_text(CONFIG)), EXPECTED_CONFIG), "SCIENTIFIC_CONFIGURATION_DIVERGENCE")
    freeze_bytes = _read_text(BASE / "method-freeze.json")
    require(_git("show", "HEAD:" + str(BASE / "method-freeze.json"), binary=True) == freeze_bytes, "FREEZE_NOT_COMMITTED_AT_D1")
    hashes = json.loads(freeze_bytes).get("text_sha256")
    required_paths = {str(AUTHORITY), str(CONFIG), str(PLAN / "dataset_manifest.json"), str(PILOT),
        str(PLAN / "final-test-manifest.json"), str(BASE / "training-plan.json"),
        str(REFERENCE / "results.json"), str(REFERENCE / "terminal-state.json"),
        str(REFERENCE / "materialization-manifest.json"), str(CNN_REFERENCE / "results.json"),
        str(CNN_REFERENCE / "terminal-state.json"), "requirements-ti3-ml.txt",
        "scripts/run_ti3d_final.py", "src/snbi_fragmentation/ti3d_execution.py",
        "src/snbi_fragmentation/ti3d_final.py", "src/snbi_fragmentation/ti3d_support.py",
        "src/snbi_fragmentation/ti3_baseline.py", "src/snbi_fragmentation/ti3_dataset.py",
        "src/snbi_fragmentation/ti3_support.py", "src/snbi_fragmentation/ti3b_ablation.py"}
    require(type(hashes) is dict and required_paths.issubset(hashes), "INCOMPLETE_SCIENTIFIC_FREEZE")
    for name, expected in hashes.items():
        raw = _read_text(Path(name))
        require(digest_string(expected) and hashlib.sha256(raw).hexdigest() == expected, "D1_FROZEN_TEXT_DIVERGENCE")
        require(_git("show", "HEAD:" + name, binary=True) == raw, "D1_FROZEN_BLOB_DIVERGENCE")
    validate_ci(json.loads(_read_text(BASE / "ci-proof.json")), head)
    manifest_bytes = _read_text(PLAN / "dataset_manifest.json")
    require(hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA256, "PLANNING_MANIFEST_HASH_DIVERGENCE")
    final_bytes = _read_text(PLAN / "final-test-manifest.json")
    require(hashlib.sha256(final_bytes).hexdigest() == FINAL_MANIFEST_SHA256, "FINAL_MANIFEST_HASH_DIVERGENCE")
    manifest = json.loads(manifest_bytes)
    validate_manifest(manifest)
    require(manifest["site_count"] == 52 and len(manifest["ignore_geometry"]) == 383, "TARGET_INVENTORY_DIVERGENCE")
    inventory = build_inventory(manifest, json.loads(_read_text(PILOT)))
    reference_result = json.loads(_read_text(REFERENCE / "results.json"))
    previous, expected_order = _validate_reference(manifest, reference_result,
        json.loads(_read_text(REFERENCE / "terminal-state.json")),
        json.loads(_read_text(REFERENCE / "materialization-manifest.json")))
    require(exact(reference_result["ablation"].get("parameters"), RF_PARAMETERS), "TI3B_RF_PARAMETERS_DIVERGENCE")
    _validate_cnn(json.loads(_read_text(CNN_REFERENCE / "results.json")),
                  json.loads(_read_text(CNN_REFERENCE / "terminal-state.json")))
    training, final = _validate_policy(manifest, expected_order,
        json.loads(_read_text(BASE / "training-plan.json")), json.loads(final_bytes))
    np = _scientific_runtime()
    active = {"state": "ARMED_ONCE", "head_sha": head, "scientific_invocation_limit": 1,
              "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
              "inventory_sha256": hashlib.sha256(canonical_bytes(inventory)).hexdigest(),
              "method_freeze_sha256": hashlib.sha256(freeze_bytes).hexdigest()}
    return head, manifest, manifest_bytes, inventory, active, previous, training, final, np


def _closed_fields(consumed=False, executed=False):
    return {"ML_FINAL_TEST": "CONSUMED" if consumed else "SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE",
            "ML_FINAL_TEST_EXECUTED": executed, "MODEL_FAMILY": "MULTIMODAL_LBP_RF",
            "MODEL_SELECTION_REOPENED": False, "FORECASTING_AUTHORIZED": False,
            "CAUSALITY_CLAIM_AUTHORIZED": False, "EXTERNAL_GENERALIZATION_CLAIM": False,
            "FINAL_RESULT_SCOPE": "SMALL_INTERNAL_TEMPORAL_CONFIRMATION",
            "FINAL_EVALUATION_AUTHORIZED": False, "MERGE_AUTHORIZED": False,
            "TI3_D_EXECUTION_AUTHORIZED": False,
            "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"}


def materialize_patches(samples, inventory, reader, previous, records, is_final):
    """Check every support first; feature extraction is a separate later phase."""
    require(type(is_final) is bool and len(samples) == (6 if is_final else 50), "MATERIALIZATION_COUNT_DIVERGENCE")
    require(all((s["split"] == "FINAL_TEST") == is_final for s in samples), "MATERIALIZATION_SPLIT_DIVERGENCE")
    paired = {(r["source_id"], r["frame_index"]): r for r in inventory}
    ordered_frames = list(dict.fromkeys((s["source_id"], s["frame_index"]) for s in samples))
    patches = {}
    for key in ordered_frames:
        source = paired[key]
        selected = [s for s in samples if (s["source_id"], s["frame_index"]) == key]
        solute = paired[(PAIR_SOURCE[key[0]], key[1])]
        structural_raw = reader.read_native(source)
        structural_y, structural_support = checked_luminance(structural_raw, source, selected)
        solutal_raw = reader.read_native(solute)
        solutal_y, solutal_support = checked_luminance(solutal_raw, solute, selected)
        for sample in selected:
            structural_patch = extract_authorized_patch(structural_y, source, sample)
            solutal_patch = extract_authorized_patch(solutal_y, solute, sample)
            structural_hash = hashlib.sha256(structural_patch.tobytes()).hexdigest()
            solutal_hash = hashlib.sha256(solutal_patch.tobytes()).hexdigest()
            if not is_final:
                old = previous[sample["sample_id"]]
                require(structural_hash == old["structural_patch_sha256"], "STRUCTURAL_PATCH_DIVERGENCE")
                require(solutal_hash == old["solutal_patch_sha256"], "SOLUTAL_PATCH_DIVERGENCE")
            patches[sample["sample_id"]] = (structural_patch, solutal_patch)
            records.append({"sample_id": sample["sample_id"], "split": sample["split"],
                "structural_source_id": source["source_id"], "solutal_source_id": solute["source_id"],
                "frame_index": source["frame_index"], "center_x": sample["center_x"], "center_y": sample["center_y"],
                "patch_side_px": 65, "structural_patch_sha256": structural_hash,
                "solutal_patch_sha256": solutal_hash, "feature_dimension": 20, "feature_sha256": None,
                "structural_support": structural_support, "solutal_support": solutal_support,
                "ti3b_both_patch_hashes_equal": None if is_final else True})
        del structural_raw, structural_y, solutal_raw, solutal_y
    require(set(patches) == {s["sample_id"] for s in samples}, "MATERIALIZATION_INCOMPLETE")
    return patches


def extract_features(samples, patches, previous, records, np, is_final):
    require(len(patches) == (6 if is_final else 50)
            and set(patches) == {s["sample_id"] for s in samples}, "ALL_SUPPORT_REQUIRED_BEFORE_FEATURES")
    by_id = {r["sample_id"]: r for r in records}
    rows = []
    for sample in samples:
        identifier = sample["sample_id"]
        row = multimodal_features(*patches[identifier])
        require(row.shape == (20,), "FEATURE_DIMENSION_DIVERGENCE")
        digest = hashlib.sha256(row.tobytes()).hexdigest()
        if not is_final:
            require(digest == previous[identifier]["feature_sha256"], "TI3B_FEATURE_HASH_DIVERGENCE")
        by_id[identifier]["feature_sha256"] = digest
        by_id[identifier]["ti3b_feature_hash_equal"] = None if is_final else True
        rows.append(row)
    features = np.stack(rows)
    features.setflags(write=False)
    return features


def main():
    try:
        head, manifest, manifest_bytes, inventory, active, previous, training, final, np = _preflight()
    except Exception as error:
        if os.path.lexists(RECEIPT_PATH) or os.path.lexists(TERMINAL_PATH):
            # A denial is not a new scientific result and cannot regress a
            # previously consumed FINAL to SEALED or reset historical counters.
            print(json.dumps({"TI3_D_FINAL": "BLOCKED_AUTHORITY_ALREADY_CONSUMED",
                "error_code": getattr(error, "code", type(error).__name__),
                "PRIOR_TERMINAL_AND_COUNTERS": "PRESERVED_NOT_RECLASSIFIED",
                "SCIENTIFIC_INVOCATIONS_THIS_COMMAND": 0}, sort_keys=True))
            return 3
        result = {**_closed_fields(), "TI3_D_FINAL": "BLOCKED_PRE_EXECUTION", "STATE": "CLOSED_BLOCKED",
                  "error_type": type(error).__name__, "error_code": getattr(error, "code", type(error).__name__),
                  "SCIENTIFIC_FINAL_RUNS": 0, "SCIENTIFIC_FINAL_COMPLETED_RUNS": 0,
                  "FINAL_FIT_CALLS": 0, "FINAL_EVALUATIONS": 0,
                  "experimental_opens": 0, "experimental_bytes": 0}
        if not os.path.lexists(RECEIPT_PATH) and not os.path.lexists(TERMINAL_PATH):
            _write_once("results.json", result)
        print(json.dumps(result, sort_keys=True))
        return 3
    reader = session = None
    stage, fit_started, fit_completed, inference_started, scoring_started = "ARMING", False, False, False, False
    fit_record = final_result = None
    patch_records = []
    training_ids, final_ids = [s["sample_id"] for s in training], [s["sample_id"] for s in final]
    try:
        reader = arm_execution(Path("."), manifest_bytes, inventory, active, head)
        session = FinalEvaluationSession(training_ids, final_ids)
        stage = "MATERIALIZE_ALL_TRAINING_PATCHES"
        patches = materialize_patches(training, inventory, reader, previous, patch_records, False)
        audit = reader.report()
        require(audit["experimental_opens"] == 10 and audit["experimental_bytes"] == 19469052
                and audit["final_test_opens"] == 0, "PRE_FIT_IO_DIVERGENCE")
        stage = "TRAINING_FEATURES"
        features = extract_features(training, patches, previous, patch_records, np, False)
        del patches
        stage, fit_started = "ONE_FINAL_FIT", True
        fit_record = session.fit(features, np.asarray([s["baseline_label"] for s in training], dtype=np.int64))
        fit_completed = True
        del features
        stage = "DURABLE_FIT_FREEZE"
        fit_digest = session.freeze_fit(lambda record: _write_once("fit-freeze.json", record))
        reader.authorize_final(fit_digest)
        stage = "FINAL_SUPPORT_ALL_PATCHES"
        patches = materialize_patches(final, inventory, reader, previous, patch_records, True)
        audit = reader.report()
        require(audit["experimental_opens"] == 14 and audit["experimental_bytes"] == 27252072
                and audit["final_test_opens"] == 4 and audit["final_test_bytes"] == 7783020,
                "FINAL_IO_DIVERGENCE")
        stage = "FINAL_FEATURES"
        features = extract_features(final, patches, previous, patch_records, np, True)
        del patches
        stage, inference_started = "FINAL_INFERENCE_WITHOUT_LABELS", True
        session.infer(features, final_ids)
        del features
        stage = "DURABLE_PREDICTIONS"
        prediction_digest = session.freeze_predictions(lambda records: _write_once("predictions.json", records))
        stage, scoring_started = "FINAL_LABEL_ASSOCIATION_AND_SCORING", True
        final_result = session.score(np.asarray([s["baseline_label"] for s in final], dtype=np.int64), final_ids)
        stage = "COMPLETED"
        result = {**_closed_fields(True, True), "TI3_D_FINAL": "PASS", "STATE": "CLOSED_CONSUMED",
            "SCIENTIFIC_FINAL_RUNS": 1, "SCIENTIFIC_FINAL_COMPLETED_RUNS": 1,
            "FINAL_FIT_CALLS": 1, "FINAL_EVALUATIONS": 1, "FINAL_TRAINING_SAMPLES": 50, "FINAL_TEST_SAMPLES": 6,
            "D1": head, "fit": fit_record, "final_evaluation": final_result,
            "fit_freeze_sha256": fit_digest, "predictions_sha256": prediction_digest,
            "sample_order": {"FINAL_TRAINING": training_ids, "FINAL_TEST": final_ids},
            "dependency_versions": dict(REQUIRED_VERSIONS), "retries": 0, "tuning_runs": 0,
            "SCIENTIFIC_MODELING_COMPLETE": True, "FINAL_REPORT_READY_FOR_AUTHOR_DECISION": True}
        exit_code = 0
    except BaseException as error:
        audit = reader.report() if reader is not None else {}
        consumed = bool(audit.get("final_consumed", False))
        final_support_failure = stage == "FINAL_SUPPORT_ALL_PATCHES"
        counters = session.counters if session is not None else {"final_fit_calls": 0, "final_evaluations": 0, "final_inference_calls": 0}
        result = {**_closed_fields(consumed),
            "TI3_D_FINAL": "BLOCKED_FINAL_SUPPORT_OR_INTEGRITY" if final_support_failure else "BLOCKED",
            "STATE": "CLOSED_BLOCKED", "stage": stage, "D1": head,
            "error_type": type(error).__name__, "error_code": getattr(error, "code", type(error).__name__),
            "SCIENTIFIC_FINAL_RUNS": int(reader is not None), "SCIENTIFIC_FINAL_COMPLETED_RUNS": 0,
            "FINAL_FIT_CALLS": counters["final_fit_calls"], "FINAL_FIT_STARTED": int(fit_started), "FINAL_FIT_COMPLETED": int(fit_completed),
            "FINAL_EVALUATIONS": counters["final_evaluations"], "FINAL_EVALUATIONS_STARTED": int(scoring_started), "FINAL_EVALUATIONS_COMPLETED": int(final_result is not None),
            "FINAL_INFERENCES_STARTED": int(inference_started), "fit": fit_record,
            "FINAL_EVALUATION": "BLOCKED_FINAL_SUPPORT" if final_support_failure else "NOT_COMPLETED",
            "SCIENTIFIC_MODELING_COMPLETE": False, "FINAL_REPORT_READY_FOR_AUTHOR_DECISION": False,
            "retries": 0, "tuning_runs": 0}
        exit_code = 2
    if reader is not None:
        reader.close()
        audit = reader.report()
        counters = session.counters if session is not None else {"final_fit_calls": 0, "final_evaluations": 0, "final_inference_calls": 0}
        audit.update(final_fit_calls=counters["final_fit_calls"], final_evaluations=counters["final_evaluations"],
                     final_fit_calls_started=int(fit_started), final_fit_calls_completed=int(fit_completed),
                     final_inferences_started=int(inference_started), final_evaluations_started=int(scoring_started),
                     final_evaluations_completed=int(final_result is not None))
        _write_once("io-audit.json", audit)
        _write_once("materialization-manifest.json", {"D1": head,
            "planning_manifest_sha256": active["manifest_sha256"], "samples": patch_records,
            "patch_pairs": len(patch_records), "final_sample_ids": final_ids})
    else:
        audit = {"experimental_opens": 0, "experimental_bytes": 0, "final_test_opens": 0, "final_test_bytes": 0}
    _write_once("results.json", result)
    print(json.dumps({"TI3_D_FINAL": result["TI3_D_FINAL"], "stage": stage,
        "SCIENTIFIC_FINAL_RUNS": result["SCIENTIFIC_FINAL_RUNS"], "FINAL_FIT_CALLS": result["FINAL_FIT_CALLS"],
        "FINAL_EVALUATIONS": result["FINAL_EVALUATIONS"], "experimental_opens": audit["experimental_opens"],
        "experimental_bytes": audit["experimental_bytes"], "final_test_opens": audit["final_test_opens"],
        "final_test_bytes": audit["final_test_bytes"], "ML_FINAL_TEST": result["ML_FINAL_TEST"]}, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
