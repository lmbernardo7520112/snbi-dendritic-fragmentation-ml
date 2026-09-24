"""Frozen Study3 orchestration; the recovery decision grants no science.

The public entry requires a separate, explicit author decision bound to the
published method SHA and its successful CI proof. Neither document is produced
by this module. Tests use fresh synthetic roots and mocked preflight only.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import time

BASE = "68ae723b392a41f52c07e2a8345437b169d5ea78"
BRANCH = "feat/study3-temporal-site-representation"
EVIDENCE = "artifacts/evidence/STUDY3_EXECUTION"
RECEIPT = "scientific-execution-receipt.json"
AUTHORITY = "configs/study3/authority.json"
# Future author-controlled documents: absent during recovery; never generated.
SCIENCE_DECISION = "docs/study3/STUDY3_SCIENCE_AUTHORIZATION.json"
CI_PROOF = ".bootstrap-test-tmp/study3/ci-proof.json"
HANDOFF = ("/home/leonardomaximinobernardo/My_projects/snbi-dendritic-fragmentation-ml/"
           "academic-deliverable-build/HANDOFF_SNBI_DENDRITIC_FRAGMENTATION_COMPLETE.md")
HANDOFF_SHA = "71bb1bf8f346f445c87561de86329d994354412354b879959f72cb4255bef445"
CONFIG_NAMES = ("authority", "data-contract", "representation-contract", "cnn-contract",
                "model-contract", "fit-budget", "evaluation-contract")
MODULES = ("domain", "design", "io", "temporal_features", "cnn", "models", "metrics", "execution")
DOC_NAMES = ("PRE_SCIENCE_INCIDENT", "PREEXPOSURE_DESIGN_DECLARATION", "COUNCIL_DECISION",
             "MASTER_PROTOCOL", "SPECIFICATIONS", "DATA_CONTRACT", "CLAIM_SCOPE",
             "RISK_REGISTER", "FUTURE_STUDY3_EXTENSIONS")
METHOD_FILES = tuple("configs/study3/" + name + ".json" for name in CONFIG_NAMES) + \
    tuple("src/snbi_fragmentation/study3_" + name + ".py" for name in MODULES) + \
    tuple("tests/test_study3_" + name + ".py" for name in MODULES) + \
    tuple("docs/study3/" + (name if name.startswith("FUTURE_") else "STUDY3_" + name)
          + ".md" for name in DOC_NAMES) + \
    ("scripts/run_study3.py", ".github/workflows/study3-synthetic-ci.yml",
     "scripts/check_study3_governance.py", "tests/test_study3_governance.py")
MODIFIED_GOVERNANCE_FILES = ("scripts/check_phase_scope.py", "scripts/check_ti3_scope.py",
                             "configs/governance/phase-scope-v1.json")
FREEZE_FILES = METHOD_FILES + MODIFIED_GOVERNANCE_FILES
INHERITED_FILES = ("src/snbi_fragmentation/study2d_io.py",
    "src/snbi_fragmentation/study2d_models.py", "src/snbi_fragmentation/study2c_models.py",
    "src/snbi_fragmentation/study2c_cnn.py", "requirements-ti3-ml.txt",
    "requirements-ti3c-cnn.txt", "constraints-ti3c-cnn.txt")
REQUIRED_JOBS = frozenset(("deterministic-contracts", "scientific-synthetic-contracts",
    "ti3-synthetic-contracts", "ti3b-synthetic-contracts", "ti3c-synthetic-contracts",
    "ti3d-final-synthetic-contracts", "study2a-synthetic-contracts",
    "study2b-synthetic-contracts", "study2c-synthetic-contracts",
    "study2d-synthetic-contracts", "study3-synthetic-contracts"))
OUTPUT_NAMES = frozenset((RECEIPT, "execution-report.md", "results.json", "terminal-state.json",
    "CLASSICAL_TRAJECTORY_RESULTS.json", "TEMPORAL_CNN1D_RESULTS.json",
    "SPATIOTEMPORAL_CNN_RESULTS.json", "METADATA_CONTROL_RESULTS.json", "FIT_LEDGER.json",
    "GROUP_LEDGER.json", "TEMPORAL_SELECTION_LEDGER.json", "REPRESENTATION_MANIFEST.json",
    "commands.json", "environment.json", "verification.json", "post-run-hashes.sha256"))
ZERO_COUNTERS = ("DEV_ROWS_READ", "TEST_ROWS_READ", "TEST_CACHE_ROWS_READ",
                 "TEST_FEATURES_COMPUTED", "MP4_OPENS", "FFMPEG_RUNS",
                 "NEW_SITES", "NEW_LABELS", "NEW_BACKGROUNDS")
MAX_TEXT = 128 * 1024 * 1024

# Recovery is a separate operational authority; the original attempt stays
# consumed. These constants do not authorize a scientific invocation.
ORIGINAL_METHOD_FREEZE_SHA = "a3f45b645e9fb3e813a43220351c951698293963"
ATTEMPT1_EVIDENCE_CHECKPOINT_SHA = "8026b821ab113f61d759a2b265ddb567e796c408"
FAILED_RECEIPT_SHA256 = "9dae20b674064870ca2a0e2d0acc2522bf67ce29011d8ac6db709c9445e80b44"
CONSUMED_AUTHOR_DECISION_SHA256 = "068830850eff8aab4441176ea6adb04c628af4d3a7f3d57fb55fb1152a42c386"
WORKTREE_ROOT = Path("/home/leonardomaximinobernardo/My_projects/snbi-dendritic-fragmentation-ml-study3")
ORIGINAL_SOURCE_ROOT = Path("/home/leonardomaximinobernardo/My_projects/snbi-dendritic-fragmentation-ml")
RECOVERY_ID = "STUDY3_EXECUTION_RECOVERY_1"
RECOVERY_EVIDENCE = "artifacts/evidence/" + RECOVERY_ID
RECOVERY_CONTRACT_PATH = "configs/study3/execution-recovery-1-contract.json"
RECOVERY_AUTHORITY = "docs/study3/STUDY3_RECOVERY_1_SCIENCE_AUTHORIZATION.json"
RECOVERY_CI_PROOF = ".bootstrap-test-tmp/study3/recovery-1-ci-proof.json"
RECOVERY_PAYLOADS = {
    "data/derived/study2b/multimodal_patches_uint8.bin": 139425000,
    "data/derived/study2c/cachetrain_dev.bin": 73827650,
}
RECOVERY_SCIENTIFIC_FILES = tuple("src/snbi_fragmentation/study3_" + name + ".py"
    for name in MODULES if name != "execution") + tuple("configs/study3/" + name + ".json"
    for name in CONFIG_NAMES if name != "authority")
RECOVERY_NEW_FILES = (
    "docs/study3/STUDY3_EXECUTION_RECOVERY_1_DECISION.md", RECOVERY_CONTRACT_PATH,
    "scripts/run_study3_recovery_1.py", "tests/test_study3_execution_recovery_1.py",
)
RECOVERY_CHANGED_FILES = (
    "src/snbi_fragmentation/study3_execution.py", "configs/governance/phase-scope-v1.json",
    "tests/test_study3_governance.py",
)
RECOVERY_FREEZE_FILES = FREEZE_FILES + RECOVERY_NEW_FILES
ORIGINAL_ATTEMPT_NAMES = OUTPUT_NAMES - {"TEMPORAL_SELECTION_LEDGER.json"}
ORIGINAL_FAILURE = "FileNotFoundError: [Errno 2] No such file or directory: 'derived'"


class Study3ExecutionError(ValueError):
    """A blocked or consumed authority cannot justify a retry."""


def require(value, message):
    if not value:
        raise Study3ExecutionError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_hash(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode())


def exact(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(exact(a[key], b[key]) for key in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def safe_path(root, relative):
    require(type(relative) is str and relative and not relative.startswith("/")
            and "\\" not in relative and all(p not in ("", ".", "..")
            for p in relative.split("/")), "unsafe relative path")
    current = Path(root)
    require(not current.is_symlink(), "root symlink forbidden")
    for part in PurePosixPath(relative).parts:
        current /= part
        require(not current.is_symlink(), "symlink forbidden")
    return current


def read_text(root, relative):
    require(relative in RECOVERY_FREEZE_FILES + INHERITED_FILES or relative in {
        AUTHORITY, SCIENCE_DECISION, CI_PROOF,
        RECOVERY_AUTHORITY, RECOVERY_CI_PROOF, RECOVERY_EVIDENCE + "/" + RECEIPT,
        "artifacts/evidence/STUDY2_D_ATTRIBUTION/TRAIN_INPUT_MANIFEST.json",
        "artifacts/evidence/STUDY2_D_ATTRIBUTION/STUDY2_D_ATTRIBUTION_DESIGN.json",
        "artifacts/evidence/STUDY2_C_BENCHMARK/terminal-state.json"}
        or relative in {EVIDENCE + "/" + name for name in ORIGINAL_ATTEMPT_NAMES},
        "text path is outside Study3 documentary allowlist")
    path = safe_path(root, relative)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "regular text required")
        data = stream.read(MAX_TEXT + 1)
    require(len(data) <= MAX_TEXT, "text size budget exceeded")
    data.decode("utf-8", errors="strict")
    return data


def load(root, relative):
    return json.loads(read_text(root, relative))


def git_bytes(root, *args):
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=root,
                          capture_output=True, check=True, timeout=30).stdout


def git(root, *args):
    return git_bytes(root, *args).decode().strip()


def verify_ci(proof, head):
    require(type(proof) is dict and proof.get("head_sha") == head
            and type(proof.get("runs")) is list and proof["runs"], "exact-SHA CI proof required")
    names = []
    for run in proof["runs"]:
        require(run.get("headSha") == head and run.get("status") == "completed"
                and run.get("conclusion") == "success" and run.get("jobs"),
                "every applicable CI run must succeed at the method SHA")
        for job in run["jobs"]:
            require(job.get("status") == "completed" and job.get("conclusion") == "success"
                    and job.get("steps"), "CI job incomplete, failed or skipped")
            require(all(s.get("status") == "completed" and s.get("conclusion") == "success"
                        for s in job["steps"]), "CI step incomplete, failed or skipped")
            names.append(job["name"])
    require(set(names) == REQUIRED_JOBS and len(names) == len(REQUIRED_JOBS),
            "all applicable eleven jobs required exactly once")
    synthetic = proof.get("study3_synthetic", {})
    require(synthetic.get("status") == "PASS" and type(synthetic.get("tests")) is int
            and synthetic["tests"] > 0 and synthetic.get("passes") == synthetic["tests"]
            and all(type(synthetic.get(k)) is int and synthetic[k] == 0
                    for k in ("skips", "failures", "errors", "expected_failures", "unexpected_successes")),
            "dedicated Study3 CI requires positive test count and zero skips/errors")
    return sorted(names)


def validate_science_decision(decision, head, contract_hashes):
    """Frozen format for a future author grant; never synthesize this document."""
    require(type(decision) is dict and set(decision) == {"grant", "author_decision_sha256"},
            "separate exact-schema author science decision required")
    fixed = {"schema_version": 1, "decision_owner": "Leonardo Maximino Bernardo",
        "activity": "STUDY3_CNN_SINGLE_SCIENTIFIC_EXECUTION", "explicit_author_decision": True,
        "scientific_execution_authorized": True, "branch": BRANCH,
        "method_freeze_sha": head, "contracts_sha256": contract_hashes,
        "scientific_invocations": 1, "distinct_fits": 28, "retries": 0,
        "development_access": False, "test_access": False, "silver_access": False,
        "video_access": False, "payload_root": "WORKTREE_ROOT_ONLY_NO_FALLBACK"}
    require(exact(decision.get("grant"), fixed),
            "future science grant must bind exact authority, method, contracts and boundaries")
    source = decision.get("author_decision_sha256")
    require(type(source) is str and len(source) == 64 and all(c in "0123456789abcdef" for c in source),
            "future explicit author decision provenance required")
    return digest(json.dumps(decision, sort_keys=True, allow_nan=False).encode())


def _current_preparation_authority(root):
    authority = load(root, AUTHORITY)
    expected = {"schema_version": 1, "phase": "PRE_SCIENCE_FREEZE_AND_CI", "study": "STUDY3_CNN",
        "decision_owner": "Leonardo Maximino Bernardo",
        "decision": "STUDY3-CNN-PRE-SCIENCE-RECOVERY-AND-FREEZE",
        "base_sha": BASE, "branch": BRANCH, "scientific_execution_authorized": False,
        "scientific_receipt_creation_authorized": False, "experimental_binary_reads_authorized": False,
        "future_execution_requires_separate_author_decision": True,
        "scientific_invocations_limit_if_separately_authorized": 1,
        "distinct_fits_limit_if_separately_authorized": 28,
        "development_access": False, "test_access": False, "silver_access": False,
        "video_access": False, "retries": 0, "merge_authorized": False,
        "terminal_closes_authority": True,
        "metadata_exposure_class": "TEXTUAL_TRAIN_METADATA_EXPOSURE_ONLY",
        "design_changed_after_metadata_exposure": False}
    require(exact(authority, expected),
            "recovery authority must remain closed to science")
    require(safe_path(root, SCIENCE_DECISION).is_file(),
            "PRE_SCIENCE_FREEZE_AND_CI grants no science; separate author decision absent")
    return authority


def authenticate_inputs(root, contract):
    from .study3_design import build_study3_design
    from .study2d_io import validate_rows

    manifest_raw = read_text(root, contract["train_manifest"])
    design_raw = read_text(root, contract["historical_design"])
    require(digest(manifest_raw) == contract["train_manifest_sha256"]
            and digest(design_raw) == contract["historical_design_sha256"],
            "historical TRAIN text changed")
    manifest, old = json.loads(manifest_raw), json.loads(design_raw)
    rows = manifest.get("rows")
    validate_rows(rows)
    stripped = [{key: value for key, value in row.items() if key != "storage"} for row in rows]
    require(exact(stripped, old.get("rows")), "manifest identities differ from frozen historical design")
    design = build_study3_design(rows, old.get("cv_fold_by_group"))
    require(design["historical_fold_sha256"] == contract["historical_fold_sha256"],
            "historical folds changed")
    return manifest, design


def validate_freeze_inventory(changes):
    """Accept only the author-approved 36 additions and three governance edits."""
    expected = {"A\t" + name for name in METHOD_FILES} | {
        "M\t" + name for name in MODIFIED_GOVERNANCE_FILES}
    require(type(changes) is list and len(changes) == 39
            and all(type(row) is str for row in changes)
            and len(expected) == 39 and set(changes) == expected,
            "freeze requires exactly 36 added and three modified authorized paths")


def preflight(root):
    """Future execution-only preflight. Never call during the recovery phase."""
    _current_preparation_authority(root)
    for name in (RECEIPT, "terminal-state.json", "results.json"):
        require(not safe_path(root, EVIDENCE + "/" + name).exists(), "consumed; retry forbidden")
    head = git(root, "rev-parse", "HEAD")
    require(git(root, "branch", "--show-current") == BRANCH, "wrong Study3 branch")
    require(git(root, "rev-list", "--parents", "-n", "1", head).split() == [head, BASE],
            "one method-freeze child of the fixed base required")
    require(not git(root, "status", "--porcelain", "--untracked-files=no"), "tracked tree must be clean")
    changes = git(root, "diff", "--name-status", "--no-renames", BASE, head).splitlines()
    validate_freeze_inventory(changes)
    contract_hashes = {}
    for name in FREEZE_FILES + INHERITED_FILES:
        data = read_text(root, name)
        require(data == git_bytes(root, "show", head + ":" + name), "method bytes changed: " + name)
        contract_hashes[name] = digest(data)
    decision = load(root, SCIENCE_DECISION)
    decision_sha = validate_science_decision(decision, head, contract_hashes)
    terminal = load(root, "artifacts/evidence/STUDY2_C_BENCHMARK/terminal-state.json")
    require(terminal.get("STATE") == "CLOSED_CONSUMED" and terminal.get("TEST_STATE") == "CONSUMED",
            "Study2-C TEST must remain consumed")
    dependencies = {}
    for line in read_text(root, "constraints-ti3c-cnn.txt").decode().splitlines():
        name, expected = line.split("==")
        actual = importlib.metadata.version(name)
        require(actual == expected, "historical dependency pin differs: " + name)
        dependencies[name] = actual
    jobs = verify_ci(load(root, CI_PROOF), head)
    # The sole external documentary path expressly named by the author.
    require(not Path(HANDOFF).is_symlink(), "HANDOFF symlink forbidden")
    fd = os.open(HANDOFF, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "HANDOFF must be regular text")
        handoff = stream.read(MAX_TEXT + 1)
    require(len(handoff) <= MAX_TEXT and digest(handoff) == HANDOFF_SHA, "HANDOFF changed")
    manifest, design = authenticate_inputs(root, load(root, "configs/study3/data-contract.json"))
    proof = {"status": "PASS", "method_freeze_sha": head, "head_sha": head, "branch": BRANCH,
        "contracts_sha256": contract_hashes, "author_decision_sha256": decision_sha,
        "population_sha256": design["population_sha256"],
        "historical_fold_sha256": design["historical_fold_sha256"],
        "fit_budget": 28, "ci_jobs": jobs, "dependencies": dependencies,
        "scientific_receipt_created": False, "experimental_binary_reads": 0}
    return proof, manifest, design


def recovery_contract():
    """Exact operational contract; it confers no execution authority."""
    return {
        "schema_version": 1, "recovery_id": RECOVERY_ID,
        "original_method_freeze_sha": ORIGINAL_METHOD_FREEZE_SHA,
        "original_receipt_sha256": FAILED_RECEIPT_SHA256,
        "original_terminal_state": "CLOSED_CONSUMED", "original_distinct_fits": 0,
        "original_payload_reads": 0, "original_feature_extractions": 0, "original_fit_calls": 0,
        "failure_class": "PRE_PAYLOAD_OPERATIONAL_FAILURE",
        "failure_reason": "WORKTREE_LOCAL_IGNORED_PAYLOAD_NOT_PROVISIONED",
        "scientific_method_changed": False, "population_changed": False,
        "folds_changed": False, "representations_changed": False, "models_changed": False,
        "hyperparameters_changed": False, "metrics_changed": False, "fit_budget_changed": False,
        "recovery_scientific_invocations_limit": 1, "recovery_distinct_fits_limit": 28,
        "recovery_retries": 0, "DEV_ACCESS": False, "TEST_ACCESS": False,
        "SILVER_ACCESS": False, "VIDEO_ACCESS": False,
    }


def validate_recovery_contract(contract):
    require(exact(contract, recovery_contract()), "recovery operational contract differs")


def validate_original_attempt(root):
    """Authenticate only the fifteen immutable, text-only attempt-1 artifacts."""
    contents = {}
    for name in sorted(ORIGINAL_ATTEMPT_NAMES):
        relative = EVIDENCE + "/" + name
        require(safe_path(root, relative).is_file(), "original attempt evidence missing: " + name)
        contents[name] = read_text(root, relative)
        require(contents[name] == git_bytes(root, "show", ATTEMPT1_EVIDENCE_CHECKPOINT_SHA + ":" + relative),
                "original evidence changed after its checkpoint: " + name)
    require(digest(contents[RECEIPT]) == FAILED_RECEIPT_SHA256, "original receipt hash differs")
    checksum_rows = contents["post-run-hashes.sha256"].decode("utf-8").splitlines()
    listed = {}
    for row in checksum_rows:
        parts = row.split("  ")
        require(len(parts) == 2 and parts[1] not in listed, "original checksum manifest malformed")
        listed[parts[1]] = parts[0]
    require(set(listed) == ORIGINAL_ATTEMPT_NAMES - {"post-run-hashes.sha256"}
            and all(listed[name] == digest(contents[name]) for name in listed),
            "original attempt evidence checksum differs")
    receipt = json.loads(contents[RECEIPT])
    terminal = json.loads(contents["terminal-state.json"])
    results = json.loads(contents["results.json"])
    verification = json.loads(contents["verification.json"])
    ledger = json.loads(contents["FIT_LEDGER.json"])
    require(receipt.get("method_freeze_sha") == ORIGINAL_METHOD_FREEZE_SHA
            and receipt.get("scientific_receipt_created") is True
            and exact(receipt.get("attempt"), 1), "original receipt provenance differs")
    require(terminal.get("STUDY3") == "BLOCKED_PARTIAL_EXECUTION"
            and terminal.get("STATE") == "CLOSED_CONSUMED"
            and terminal.get("retry_authorized") is False
            and terminal.get("adaptive_model_search") is False
            and terminal.get("method_freeze_sha") == ORIGINAL_METHOD_FREEZE_SHA
            and terminal.get("receipt_sha256") == FAILED_RECEIPT_SHA256
            and exact(terminal.get("SCIENTIFIC_STUDY3_RUNS"), 1),
            "original attempt is not the closed consumed pre-payload failure")
    zeros = ("DISTINCT_FITS", "RF_FITS", "CNN1D_FITS", "SPATIOTEMPORAL_CNN_FITS",
             "METADATA_LOGREG_FITS", "ACQUISITION_ONLY_FITS", "FEATURE_EXTRACTIONS_STARTED",
             "FEATURE_EXTRACTIONS_COMPLETED", "LBP_ROWS", *ZERO_COUNTERS)
    require(all(exact(terminal.get(name), 0) for name in zeros),
            "original attempt has nonzero scientific/feature/fit/access counters")
    counts = results.get("counts", {})
    require(results.get("status") == "BLOCKED_PARTIAL_EXECUTION"
            and results.get("failure") == ORIGINAL_FAILURE
            and results.get("method_freeze_sha") == ORIGINAL_METHOD_FREEZE_SHA
            and results.get("receipt_sha256") == FAILED_RECEIPT_SHA256
            and exact(results.get("fits"), {}) and exact(results.get("acquisition_only"), [])
            and results.get("contrasts") is None
            and exact(counts.get("SCIENTIFIC_STUDY3_RUNS"), 1)
            and all(exact(counts.get(name), 0) for name in zeros if name != "DISTINCT_FITS"),
            "original failure reason or absence of scientific results differs")
    expected_ledger = {"fit_budget": 28, "started": [], "completed": [],
                       "distinct_fits_started": 0, "distinct_fits_completed": 0}
    require(exact(ledger, expected_ledger) and exact(verification.get("fit_ledger"), expected_ledger),
            "original attempted/completed fit ledger must be zero")
    audit = verification.get("io_audit", {})
    require(verification.get("status") == "BLOCKED_PARTIAL_EXECUTION"
            and verification.get("failure") == ORIGINAL_FAILURE
            and audit.get("state") == "FAILED_CONSUMED"
            and audit.get("all_descriptors_closed") is True
            and exact(audit.get("access_records"), [])
            and all(exact(audit.get(key), 0) for key in (
                "bytes_read", "rows_read", "rows_authenticated", "container_opens", "row_attempts",
                "DEV_ROWS_READ", "TEST_ROWS_READ", "TEST_CACHE_ROWS_READ", "TEST_FEATURES_COMPUTED",
                "FFMPEG_RUNS", "EXPERIMENTAL_SOURCE_OPENS", "full_container_hashes")),
            "original scientific payload access was not zero")
    return {"original_receipt_sha256": FAILED_RECEIPT_SHA256,
            "attempt1_evidence_checkpoint_sha": ATTEMPT1_EVIDENCE_CHECKPOINT_SHA,
            "evidence_sha256": {name: digest(value) for name, value in sorted(contents.items())},
            "original_attempt_preserved": True, "original_scientific_payload_reads": 0,
            "original_features": 0, "original_fits": 0, "original_failure": ORIGINAL_FAILURE}


def verify_original_method(root):
    """The thirteen scientific source/config files remain byte-identical."""
    hashes = {}
    for name in RECOVERY_SCIENTIFIC_FILES:
        content = read_text(root, name)
        require(content == git_bytes(root, "show", ORIGINAL_METHOD_FREEZE_SHA + ":" + name),
                "original scientific method changed: " + name)
        hashes[name] = digest(content)
    return hashes


def verify_recovery_payload_sources(source_root=None):
    """Provisioning-only metadata check; never used by scientific preflight."""
    root = ORIGINAL_SOURCE_ROOT if source_root is None else source_root
    report = []
    for relative, expected_bytes in RECOVERY_PAYLOADS.items():
        source = safe_path(root, relative).lstat()
        require(stat.S_ISREG(source.st_mode) and source.st_size == expected_bytes,
                "payload source must be regular with exact size: " + relative)
        report.append({"path": relative, "expected_bytes": expected_bytes,
                       "source_regular": True, "source_size": source.st_size, "symlink": False})
    return {"status": "PASS", "verification": "METADATA_ONLY_NO_PAYLOAD_OPEN",
            "containers": report, "scientific_application_binary_reads": 0}


def verify_recovery_payload_locations(root):
    """Worktree-only metadata; no source dependency or container content read."""
    report = []
    for relative, expected_bytes in RECOVERY_PAYLOADS.items():
        destination = safe_path(root, relative).lstat()
        require(stat.S_ISREG(destination.st_mode) and destination.st_size == expected_bytes,
                "payload destination must be regular with exact size: " + relative)
        require(destination.st_nlink == 1,
                "payload destination hardlink forbidden: " + relative)
        report.append({"path": relative, "expected_bytes": expected_bytes,
                       "destination_regular": True, "destination_size": destination.st_size,
                       "symlink": False, "hardlink": False})
    return {"status": "PASS", "verification": "METADATA_ONLY_NO_PAYLOAD_OPEN",
            "containers": report, "scientific_application_binary_reads": 0}


def recovery_science_grant(head, contract_hashes, checkpoint_sha):
    """Documentary schema for a future author grant; never writes that grant."""
    require(checkpoint_sha == ATTEMPT1_EVIDENCE_CHECKPOINT_SHA,
            "recovery must follow the fixed original evidence checkpoint")
    return {"schema_version": 1, "decision_owner": "Leonardo Maximino Bernardo",
        "activity": "STUDY3_EXECUTION_RECOVERY_1_SINGLE_SCIENTIFIC_EXECUTION",
        "recovery_id": RECOVERY_ID, "explicit_author_decision": True,
        "scientific_execution_authorized": True, "branch": BRANCH,
        "original_method_freeze_sha": ORIGINAL_METHOD_FREEZE_SHA,
        "original_receipt_sha256": FAILED_RECEIPT_SHA256,
        "attempt1_evidence_checkpoint_sha": checkpoint_sha,
        "recovery_method_freeze_sha": head, "contracts_sha256": contract_hashes,
        "scientific_invocations": 1, "distinct_fits": 28, "retries": 0,
        "development_access": False, "test_access": False, "silver_access": False,
        "video_access": False, "payload_root": "WORKTREE_ROOT_ONLY_NO_FALLBACK",
        "evidence_namespace": RECOVERY_EVIDENCE}


def validate_recovery_science_decision(decision, head, contract_hashes, checkpoint_sha):
    require(type(decision) is dict and set(decision) == {"grant", "author_decision_sha256"},
            "separate exact-schema recovery author decision required")
    require(exact(decision.get("grant"), recovery_science_grant(head, contract_hashes, checkpoint_sha)),
            "recovery science grant must bind exact new authority, freeze and boundaries")
    source = decision.get("author_decision_sha256")
    require(type(source) is str and len(source) == 64 and all(c in "0123456789abcdef" for c in source)
            and source != CONSUMED_AUTHOR_DECISION_SHA256,
            "fresh recovery author decision digest required; old authority is consumed")
    return digest(json.dumps(decision, sort_keys=True, allow_nan=False).encode())


def preflight_recovery_1(root):
    """Future recovery-only admission; current preparation grants no science."""
    require(Path(root).absolute() == WORKTREE_ROOT, "recovery requires the authorized existing worktree")
    for name in (RECEIPT, "terminal-state.json", "results.json"):
        require(not safe_path(root, RECOVERY_EVIDENCE + "/" + name).exists(),
                "recovery authority consumed; second invocation forbidden")
    require(safe_path(root, RECOVERY_AUTHORITY).is_file(), "new recovery author decision absent")
    contract = load(root, RECOVERY_CONTRACT_PATH)
    validate_recovery_contract(contract)
    head = git(root, "rev-parse", "HEAD")
    require(git(root, "branch", "--show-current") == BRANCH, "wrong recovery branch")
    require(git(root, "rev-list", "--parents", "-n", "1", head).split()
            == [head, ATTEMPT1_EVIDENCE_CHECKPOINT_SHA], "recovery freeze must follow evidence checkpoint")
    require(git(root, "rev-list", "--parents", "-n", "1", ATTEMPT1_EVIDENCE_CHECKPOINT_SHA).split()
            == [ATTEMPT1_EVIDENCE_CHECKPOINT_SHA, ORIGINAL_METHOD_FREEZE_SHA],
            "original freeze/evidence checkpoint ancestry differs")
    require(not git(root, "status", "--porcelain", "--untracked-files=no"), "tracked tree must be clean")
    changes = git(root, "diff", "--name-status", "--no-renames", ATTEMPT1_EVIDENCE_CHECKPOINT_SHA, head).splitlines()
    expected = {"A\t" + name for name in RECOVERY_NEW_FILES} | {"M\t" + name for name in RECOVERY_CHANGED_FILES}
    require(len(changes) == 7 and set(changes) == expected, "exact seven-path operational recovery freeze required")
    contract_hashes = {}
    for name in RECOVERY_FREEZE_FILES + INHERITED_FILES:
        content = read_text(root, name)
        require(content == git_bytes(root, "show", head + ":" + name), "recovery freeze bytes changed: " + name)
        contract_hashes[name] = digest(content)
    decision_sha = validate_recovery_science_decision(load(root, RECOVERY_AUTHORITY), head,
        contract_hashes, ATTEMPT1_EVIDENCE_CHECKPOINT_SHA)
    original = validate_original_attempt(root)
    method_hashes = verify_original_method(root)
    payload_locations = verify_recovery_payload_locations(root)
    terminal = load(root, "artifacts/evidence/STUDY2_C_BENCHMARK/terminal-state.json")
    require(terminal.get("STATE") == "CLOSED_CONSUMED" and terminal.get("TEST_STATE") == "CONSUMED",
            "Study2-C TEST must remain consumed")
    dependencies = {}
    for line in read_text(root, "constraints-ti3c-cnn.txt").decode().splitlines():
        name, expected_version = line.split("==")
        actual = importlib.metadata.version(name)
        require(actual == expected_version, "historical dependency pin differs: " + name)
        dependencies[name] = actual
    jobs = verify_ci(load(root, RECOVERY_CI_PROOF), head)
    require(not Path(HANDOFF).is_symlink(), "HANDOFF symlink forbidden")
    fd = os.open(HANDOFF, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "HANDOFF must be regular text")
        handoff = stream.read(MAX_TEXT + 1)
    require(len(handoff) <= MAX_TEXT and digest(handoff) == HANDOFF_SHA, "HANDOFF changed")
    manifest, design = authenticate_inputs(root, load(root, "configs/study3/data-contract.json"))
    proof = {"status": "PASS", "recovery_id": RECOVERY_ID,
        "method_freeze_sha": ORIGINAL_METHOD_FREEZE_SHA, "original_method_freeze_sha": ORIGINAL_METHOD_FREEZE_SHA,
        "recovery_method_freeze_sha": head, "head_sha": head, "branch": BRANCH,
        "original_receipt_sha256": FAILED_RECEIPT_SHA256,
        "attempt1_evidence_checkpoint_sha": ATTEMPT1_EVIDENCE_CHECKPOINT_SHA,
        "contracts_sha256": contract_hashes, "original_scientific_method_sha256": method_hashes,
        "author_decision_sha256": decision_sha, "original_attempt": original,
        "payload_locations": payload_locations, "population_sha256": design["population_sha256"],
        "historical_fold_sha256": design["historical_fold_sha256"], "fit_budget": 28,
        "ci_jobs": jobs, "dependencies": dependencies, "scientific_receipt_created": False,
        "scientific_application_binary_reads": 0, "scientific_method_changed": False}
    return proof, manifest, design


def encode_evidence(value):
    return (value if isinstance(value, str) else
            json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def emit(root, name, value):
    """Original namespace writer; existing exclusive-write API is preserved."""
    return _emit_evidence(root, EVIDENCE, name, value)


def emit_recovery_1(root, name, value):
    """Recovery writer cannot choose or overwrite the original namespace."""
    return _emit_evidence(root, RECOVERY_EVIDENCE, name, value)


def _emit_evidence(root, evidence_namespace, name, value):
    require(evidence_namespace in {EVIDENCE, RECOVERY_EVIDENCE}, "unknown evidence namespace")
    require(name in OUTPUT_NAMES, "unknown evidence output")
    directory = safe_path(root, evidence_namespace)
    directory.mkdir(parents=True, exist_ok=True)
    path = safe_path(root, evidence_namespace + "/" + name)
    data = encode_evidence(value)
    require(len(data) <= MAX_TEXT, "evidence size budget exceeded")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return digest(data)


def _check_audit(audit, rows):
    require(audit.get("rows_read") == rows and audit.get("rows_authenticated") == rows
            and audit.get("bytes_read") == rows * 8450, "directed row accounting differs")
    for key in ("DEV_ROWS_READ", "TEST_ROWS_READ", "TEST_CACHE_ROWS_READ", "TEST_FEATURES_COMPUTED",
                "FFMPEG_RUNS", "EXPERIMENTAL_SOURCE_OPENS", "full_container_hashes"):
        require(type(audit.get(key)) is int and audit[key] == 0, "I/O firewall counter differs: " + key)


def validate_results(results, design):
    from .study3_cnn import CONFIGS
    from .study3_design import CLASSICAL
    from .study3_metrics import group_metrics

    expected = [s["fit_id"] for s in design["fits"]]
    groups = {g["group_id"]: g for g in design["groups"]}
    records = results.get("fits", {})
    require(type(records) is dict and list(records) == expected and len(records) == 28,
            "exact 28 completed metric records required")
    for spec in design["fits"]:
        record = records[spec["fit_id"]]
        require(exact(record.get("spec"), spec), "recorded fit specification changed")
        fitted = record.get("fit", {})
        require(type(fitted.get("fit_calls")) is int and fitted["fit_calls"] == 1
                and exact(fitted.get("fold"), spec["fold"])
                and fitted.get("condition") == spec["condition"]
                and fitted.get("training_groups") == spec["training_group_ids"]
                and fitted.get("training_only") is True
                and fitted.get("validation_used_for_training") is False,
                "fit provenance or TRAIN-only membership differs")
        predictions = record.get("predictions", {})
        require(predictions.get("group_ids") == spec["validation_group_ids"]
                and len(predictions.get("predictions", [])) == len(spec["validation_group_ids"])
                and all(type(p) is int and p in (0, 1) for p in predictions["predictions"]),
                "one binary prediction per held-out TRAIN group required")
        score = record.get("metrics", {}).get("primary_gmba")
        require(type(score) is float and 0 <= score <= 1, "finite group GMBA required")
        validation = [groups[gid] for gid in spec["validation_group_ids"]]
        metric = group_metrics([g["label"] for g in validation], predictions["predictions"],
                               [g["acquisition_id"] for g in validation])
        require(exact(record["metrics"], metric), "metric bundle differs from its group predictions")
        if spec["condition"] in CONFIGS:
            require(type(fitted.get("epochs")) is int and fitted["epochs"] == 30
                    and fitted.get("parameter_count") == CONFIGS[spec["condition"]]["parameter_count"]
                    and fitted.get("random_seed") == 42 and fitted.get("device") == "cpu"
                    and fitted.get("threads") == 1
                    and fitted.get("validation_evaluations_during_training") == 0,
                    "CNN frozen training proof differs")
        if spec["condition"] in {"TEMPORAL_CNN1D_LBP20", "COVERAGE_METADATA_LOGREG"}:
            scaler = fitted.get("scaler", {})
            dimension = 20 if spec["condition"] == "TEMPORAL_CNN1D_LBP20" else 4
            require(scaler.get("training_only") is True
                    and scaler.get("training_group_ids") == spec["training_group_ids"]
                    and len(scaler.get("mean", [])) == len(scaler.get("std", [])) == dimension
                    and scaler.get("sha256") == json_hash({k: v for k, v in scaler.items() if k != "sha256"}),
                    "TRAIN-only scaler provenance differs")
    controls = results.get("acquisition_only", [])
    require(len(controls) == 4 and [c.get("fold") for c in controls] == [0, 1, 2, 3],
            "four ordered zero-fit acquisition controls required")
    for control in controls:
        expected_ids = [g["group_id"] for g in design["groups"] if g["cv_fold"] == control["fold"]]
        require(control.get("group_ids") == expected_ids
                and type(control.get("output", {}).get("fit_calls")) is int
                and control["output"]["fit_calls"] == 0, "acquisition control membership or fit count differs")
        metric = group_metrics([groups[gid]["label"] for gid in expected_ids],
            control["output"]["predictions"], [groups[gid]["acquisition_id"] for gid in expected_ids])
        require(exact(control.get("metrics"), metric), "acquisition diagnostic metrics differ")
    return True


def _execute(root):
    """Every controller entry obtains its own author/CI/contract preflight."""
    return _execute_authorized(root, EVIDENCE)


def _execute_authorized(root, evidence_namespace):
    """One scientific core; each closed namespace dispatch owns its preflight."""
    require(evidence_namespace in {EVIDENCE, RECOVERY_EVIDENCE}, "unknown execution namespace")
    if evidence_namespace == EVIDENCE:
        preflight_operation, writer, entrypoint = preflight, emit, "scripts/run_study3.py"
    else:
        preflight_operation, writer, entrypoint = (preflight_recovery_1, emit_recovery_1,
                                                  "scripts/run_study3_recovery_1.py")
    proof, manifest, design = preflight_operation(root)
    recovery_context = ({key: proof[key] for key in (
        "recovery_id", "original_method_freeze_sha", "recovery_method_freeze_sha",
        "original_receipt_sha256", "attempt1_evidence_checkpoint_sha")}
        if evidence_namespace == RECOVERY_EVIDENCE else {})
    # Receipt creation is before imports that perform feature/model operations,
    # accessor construction, path grants and the first experimental pread.
    receipt_sha = writer(root, RECEIPT, {**proof, "scientific_receipt_created": True, "attempt": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "receipt_precedes_experimental_payload": True})
    from .study3_design import FitBudget, CLASSICAL
    budget = FitBudget(design["fits"])
    audit, records, acquisitions, selections = {}, {}, [], []
    counts = {"SCIENTIFIC_STUDY3_RUNS": 1, "FEATURE_EXTRACTIONS_STARTED": 0,
        "FEATURE_EXTRACTIONS_COMPLETED": 0, "LBP_ROWS": 0, "RF_FITS": 0,
        "CNN1D_FITS": 0, "SPATIOTEMPORAL_CNN_FITS": 0, "METADATA_LOGREG_FITS": 0,
        "ACQUISITION_ONLY_FITS": 0, **dict.fromkeys(ZERO_COUNTERS, 0)}
    accessor, failure, summary, selection_digest = None, None, None, None
    started = time.perf_counter()
    try:
        import numpy as np
        from .study3_io import Study3TrainAccess, TrainReceiptGrant
        from .study3_temporal_features import build_representations
        from .study3_models import (fit_reference, predict_reference, coverage_metadata_features,
                                    fit_metadata, predict_metadata, acquisition_only)
        from .study3_cnn import fit_cnn, predict_cnn
        from .study3_metrics import group_metrics, summarize_contrasts
        from .study2d_models import extract_lbp20

        rows = manifest["rows"]
        grant = TrainReceiptGrant(rows, receipt_sha, proof["method_freeze_sha"])
        accessor = Study3TrainAccess(root, rows, grant=grant, audit=audit)
        pairs = accessor.load()
        _check_audit(audit, len(rows))
        require(pairs.shape == (len(rows), 2, 65, 65) and pairs.dtype == np.uint8,
                "admitted TRAIN tensor shape/type differs")
        counts["FEATURE_EXTRACTIONS_STARTED"] += 1
        features = extract_lbp20(pairs)
        counts["FEATURE_EXTRACTIONS_COMPLETED"] += 1
        counts["LBP_ROWS"] = len(rows)
        rep = build_representations(rows, {r["sample_id"]: features[i] for i, r in enumerate(rows)})
        require(rep["group_ids"] == design["group_ids"], "representation group order differs")
        selections = rep["selections"]
        # Selection is durably frozen before any fit, with no interpolation.
        selection_digest = writer(root, "TEMPORAL_SELECTION_LEDGER.json", {"selections": selections,
             "sha256": json_hash(selections), "method_freeze_sha": proof["method_freeze_sha"]})
        row_index = {r["sample_id"]: i for i, r in enumerate(rows)}
        temporal_pixels = np.stack([pairs[[row_index[s] for s in entry["selected_sample_ids"]]]
                                    for entry in selections])
        del pairs
        groups, group_ids = rep["groups"], rep["group_ids"]
        lookup = {gid: i for i, gid in enumerate(group_ids)}
        metadata = coverage_metadata_features(groups)
        scores = {condition: [] for condition in [*CLASSICAL, "TEMPORAL_CNN1D_LBP20",
                  "SPATIOTEMPORAL_CNN_SMALL", "COVERAGE_METADATA_LOGREG"]}
        for spec in design["fits"]:
            condition, fold, fit_id = spec["condition"], spec["fold"], spec["fit_id"]
            ti = [lookup[g] for g in spec["training_group_ids"]]
            vi = [lookup[g] for g in spec["validation_group_ids"]]
            training = [groups[i] for i in ti]
            validation = [groups[i] for i in vi]
            events, epochs = [], []
            family = ("RF_FITS" if condition in CLASSICAL else "CNN1D_FITS"
                      if condition == "TEMPORAL_CNN1D_LBP20" else "SPATIOTEMPORAL_CNN_FITS"
                      if condition == "SPATIOTEMPORAL_CNN_SMALL" else "METADATA_LOGREG_FITS")

            def callback(event):
                name = event.get("event")
                require(event.get("condition") == condition and exact(event.get("fold"), fold),
                        "fit event condition/fold differs")
                require(event.get("family") == ("RF_REFERENCE" if condition in CLASSICAL else condition),
                        "fit event family differs")
                if name == "FIT_START":
                    require(not events, "duplicate fit start")
                    budget.start(fit_id)
                elif name == "FIT_EPOCH_COMPLETE":
                    require(condition in {"TEMPORAL_CNN1D_LBP20", "SPATIOTEMPORAL_CNN_SMALL"}
                            and events == ["FIT_START"] and len(epochs) < 30
                            and type(event.get("epoch")) is int and event["epoch"] == len(epochs) + 1
                            and event.get("training_groups_seen") == len(training),
                            "CNN epoch order or training coverage differs")
                    epochs.append(event["epoch"])
                    return
                elif name == "FIT_COMPLETE":
                    require(events == ["FIT_START"], "fit completion order differs")
                    require(len(epochs) == (30 if condition in {
                        "TEMPORAL_CNN1D_LBP20", "SPATIOTEMPORAL_CNN_SMALL"} else 0),
                        "CNN must complete exactly thirty epochs")
                    budget.complete(fit_id)
                    counts[family] += 1
                else:
                    raise Study3ExecutionError("unknown fit callback")
                events.append(name)

            if condition in CLASSICAL:
                X = rep["classical"][condition]
                model, fit_info = fit_reference(X[ti], training, condition, fold=fold, on_event=callback)
                output = predict_reference(model, X[vi])
            elif condition in {"TEMPORAL_CNN1D_LBP20", "SPATIOTEMPORAL_CNN_SMALL"}:
                X = rep["temporal_lbp"] if condition == "TEMPORAL_CNN1D_LBP20" else temporal_pixels
                model, fit_info = fit_cnn(condition, X[ti], training, fold=fold, on_event=callback)
                output = predict_cnn(model, X[vi])
            else:
                require(condition == "COVERAGE_METADATA_LOGREG", "undeclared condition")
                model, fit_info = fit_metadata(metadata[ti], training, fold=fold, on_event=callback)
                output = predict_metadata(model, metadata[vi])
            require(events == ["FIT_START", "FIT_COMPLETE"], "actual fit callbacks incomplete")
            metrics = group_metrics([g.label for g in validation], output["predictions"],
                                    [str(g.acquisition_id) for g in validation])
            scores[condition].append(metrics["primary_gmba"])
            records[fit_id] = {"spec": spec, "fit": fit_info, "metrics": metrics,
                "predictions": {"group_ids": spec["validation_group_ids"], **output}}
            del model
        for fold in range(4):
            training = [g for g in groups if g.cv_fold != fold]
            validation = [g for g in groups if g.cv_fold == fold]
            output = acquisition_only(training, validation, fold=fold)
            acquisitions.append({"fold": fold, "group_ids": [str(g.group_id) for g in validation],
                "output": output, "metrics": group_metrics([g.label for g in validation],
                    output["predictions"], [str(g.acquisition_id) for g in validation])})
        require((counts["RF_FITS"], counts["CNN1D_FITS"], counts["SPATIOTEMPORAL_CNN_FITS"],
                 counts["METADATA_LOGREG_FITS"]) == (16, 4, 4, 4), "fit family accounting differs")
        require(budget.snapshot()["distinct_fits_completed"] == 28, "28 fits must complete")
        summary = summarize_contrasts(scores)
        validate_results({"fits": records, "acquisition_only": acquisitions}, design)
    except BaseException as exc:
        failure = type(exc).__name__ + ": " + str(exc)
    finally:
        if accessor is not None:
            accessor.close()
    for key in ZERO_COUNTERS:
        counts[key] = audit.get(key, counts[key])
    counts["MP4_OPENS"] = audit.get("EXPERIMENTAL_SOURCE_OPENS", 0)
    terminal = {"STUDY3": "PASS" if failure is None else "BLOCKED_PARTIAL_EXECUTION",
        "STATE": "CLOSED_CONSUMED", "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION",
        "method_freeze_sha": proof["method_freeze_sha"], "receipt_sha256": receipt_sha,
        "retry_authorized": False, "adaptive_model_search": False,
        "STUDY2_C_TEST_STATE": "UNCHANGED_CONSUMED", "EXTERNAL_GENERALIZATION": False,
        "DISTINCT_FITS": budget.snapshot()["distinct_fits_completed"], **counts, **recovery_context}
    results = {"status": terminal["STUDY3"], "failure": failure, "counts": counts,
        "fits": records, "acquisition_only": acquisitions, "contrasts": summary,
        "method_freeze_sha": proof["method_freeze_sha"], "receipt_sha256": receipt_sha,
        "elapsed_seconds": time.perf_counter() - started, **recovery_context}
    outputs = {
        "results.json": results,
        "FIT_LEDGER.json": budget.snapshot(),
        "GROUP_LEDGER.json": {"groups": design["groups"], "population_sha256": design["population_sha256"]},
        "REPRESENTATION_MANIFEST.json": {"classical": list(CLASSICAL), "timepoints": 8,
            "selection_sha256": json_hash(selections), "real_feature_rows": counts["LBP_ROWS"]},
        "CLASSICAL_TRAJECTORY_RESULTS.json": {k: v for k, v in records.items() if v["spec"]["condition"] in CLASSICAL},
        "TEMPORAL_CNN1D_RESULTS.json": {k: v for k, v in records.items() if v["spec"]["condition"] == "TEMPORAL_CNN1D_LBP20"},
        "SPATIOTEMPORAL_CNN_RESULTS.json": {k: v for k, v in records.items() if v["spec"]["condition"] == "SPATIOTEMPORAL_CNN_SMALL"},
        "METADATA_CONTROL_RESULTS.json": {"logreg": {k: v for k, v in records.items()
            if v["spec"]["condition"] == "COVERAGE_METADATA_LOGREG"}, "acquisition_only": acquisitions,
            "interpretation": "Descriptive confound diagnostics; never justify group/fold/model changes."},
        "commands.json": {"entrypoint": entrypoint, "invocations": 1,
            "receipt_precedes_binary_read": True},
        "environment.json": {"dependencies": proof["dependencies"], "device": "cpu", "torch_threads": 1},
        "verification.json": {"status": terminal["STUDY3"], "io_audit": audit,
            "fit_ledger": budget.snapshot(), "failure": failure},
        "execution-report.md": ("# Study3 execution\n\nStatus: " + terminal["STUDY3"] +
            ". Internal exploratory group-trajectory weak-label comparison. "
            "Performance does not determine procedural PASS. Negative results are preserved. "
            "No external, causal, onset or forecasting claim is supported.\n"),
    }
    hashes = {name: writer(root, name, value) for name, value in outputs.items()}
    hashes[RECEIPT] = receipt_sha
    if selection_digest is not None:
        hashes["TEMPORAL_SELECTION_LEDGER.json"] = selection_digest
    # Publish PASS last: any preceding output failure must leave a consumed
    # BLOCKED terminal, never PASS with an incomplete checksum manifest.
    hashes["terminal-state.json"] = digest(encode_evidence(terminal))
    writer(root, "post-run-hashes.sha256", "".join(f"{sha}  {name}\n" for name, sha in sorted(hashes.items())))
    writer(root, "terminal-state.json", terminal)
    return terminal


def run(root):
    """No preparation mode or retry; current recovery authority alone denies."""
    consumed = safe_path(root, EVIDENCE + "/" + RECEIPT).exists()
    try:
        return _execute(root)
    except BaseException as exc:
        if not consumed and safe_path(root, EVIDENCE + "/" + RECEIPT).exists() and not \
                safe_path(root, EVIDENCE + "/terminal-state.json").exists():
            emit(root, "terminal-state.json", {"STUDY3": "BLOCKED_POST_RECEIPT_FAILURE",
                 "STATE": "CLOSED_CONSUMED", "SCIENTIFIC_STUDY3_RUNS": 1,
                 "failure": type(exc).__name__ + ": " + str(exc), "retry_authorized": False,
                 "counter_scope": "Only durable evidence certifies completed work",
                 "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"})
        raise


def run_recovery_1(root):
    """Only a new recovery decision can start its separate single invocation."""
    consumed = safe_path(root, RECOVERY_EVIDENCE + "/" + RECEIPT).exists()
    try:
        return _execute_authorized(root, RECOVERY_EVIDENCE)
    except BaseException as exc:
        if not consumed and safe_path(root, RECOVERY_EVIDENCE + "/" + RECEIPT).exists() and not \
                safe_path(root, RECOVERY_EVIDENCE + "/terminal-state.json").exists():
            # Recover only provenance already durably written by this invocation.
            # An incomplete receipt never warrants guessing a new freeze SHA.
            try:
                written_receipt = load(root, RECOVERY_EVIDENCE + "/" + RECEIPT)
                recovery_head = written_receipt.get("recovery_method_freeze_sha")
            except (OSError, ValueError, TypeError, UnicodeError):
                recovery_head = None
            emit_recovery_1(root, "terminal-state.json", {
                "STUDY3": "BLOCKED_POST_RECEIPT_FAILURE", "STATE": "CLOSED_CONSUMED",
                "recovery_id": RECOVERY_ID, "SCIENTIFIC_STUDY3_RUNS": 1,
                "original_method_freeze_sha": ORIGINAL_METHOD_FREEZE_SHA,
                "recovery_method_freeze_sha": recovery_head,
                "original_receipt_sha256": FAILED_RECEIPT_SHA256,
                "attempt1_evidence_checkpoint_sha": ATTEMPT1_EVIDENCE_CHECKPOINT_SHA,
                "failure": type(exc).__name__ + ": " + str(exc), "retry_authorized": False,
                "counter_scope": "Only durable evidence certifies completed work",
                "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"})
        raise
