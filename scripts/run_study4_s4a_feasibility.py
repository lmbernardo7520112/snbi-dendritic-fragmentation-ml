"""Inactive S4-A0 entry for a separately authorized, single-use metadata audit.

Importing this file performs no filesystem access. The future local grant is
never generated here. All corpus bytes are authenticated before an exclusive
receipt consumes S4-A1; parsing and the pure analysis follow that receipt.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess

BASE = "817c099222fb9b19d0614112b47c17dde3da4110"
BRANCH = "feat/study4-coverage-controlled-temporal-representation"
WORKTREE = Path("/home/leonardomaximinobernardo/My_projects/snbi-dendritic-fragmentation-ml-study4")
AUTHORIZATION = "docs/study4/STUDY4_S4A_FEASIBILITY_AUTHORIZATION.json"
CI_PROOF = ".bootstrap-test-tmp/study4/s4a-ci-proof.json"
EVIDENCE = "artifacts/evidence/STUDY4_S4A_FEASIBILITY"
RECEIPT = "s4a-feasibility-receipt.json"
RESULT = "feasibility-result.json"
TERMINAL = "terminal-state.json"
SOURCE_MANIFEST = "artifacts/evidence/STUDY2_D_ATTRIBUTION/TRAIN_INPUT_MANIFEST.json"
SOURCE_SHA = "6ae3eee8e2fbe2c2e5de55eb84cb35b0ca7b561d37a8426b11125870003de531"
CONTRACT_PATHS = (
    "configs/study4/authority.json", "configs/study4/feasibility-contract.json",
    "configs/study4/matching-contract.json", "configs/study4/evaluation-contract.json",
    "configs/study3/data-contract.json",
)
FREEZE_CHANGES = {
    ".github/workflows/study4-synthetic-ci.yml": "A",
    "configs/governance/phase-scope-v1.json": "M",
    "configs/study4/authority.json": "M",
    "configs/study4/feasibility-contract.json": "M",
    "configs/study4/matching-contract.json": "M",
    "scripts/run_study4_s4a_feasibility.py": "A",
    "src/snbi_fragmentation/study4_feasibility.py": "A",
    "tests/test_study4_feasibility.py": "A",
}
SCIENTIFIC_METHOD_FILES = tuple(
    "src/snbi_fragmentation/study3_" + name + ".py"
    for name in ("domain", "design", "io", "temporal_features", "cnn", "models", "metrics")
) + tuple(
    "configs/study3/" + name + ".json"
    for name in ("data-contract", "representation-contract", "cnn-contract", "model-contract",
                 "fit-budget", "evaluation-contract")
)
REQUIRED_WORKFLOWS = {
    "deterministic-ci": {"path": ".github/workflows/ci.yml",
                         "jobs": ("deterministic-contracts", "scientific-synthetic-contracts")},
    "ti3-synthetic-ci": {"path": ".github/workflows/ti3-synthetic.yml",
                         "jobs": ("ti3-synthetic-contracts",)},
    "ti3b-synthetic-ci": {"path": ".github/workflows/ti3b-synthetic.yml",
                          "jobs": ("ti3b-synthetic-contracts",)},
    "ti3c-synthetic-ci": {"path": ".github/workflows/ti3c-synthetic.yml",
                          "jobs": ("ti3c-synthetic-contracts",)},
    "ti3d-final-synthetic-ci": {"path": ".github/workflows/ti3d-final-synthetic.yml",
                               "jobs": ("ti3d-final-synthetic-contracts",)},
    "study2a-synthetic-ci": {"path": ".github/workflows/study2a-synthetic.yml",
                             "jobs": ("study2a-synthetic-contracts",)},
    "study2b-synthetic-ci": {"path": ".github/workflows/study2b-synthetic.yml",
                             "jobs": ("study2b-synthetic-contracts",)},
    "study2c-synthetic-ci": {"path": ".github/workflows/study2c-synthetic.yml",
                             "jobs": ("study2c-synthetic-contracts",)},
    "study2d-synthetic-ci": {"path": ".github/workflows/study2d-synthetic.yml",
                             "jobs": ("study2d-synthetic-contracts",)},
    "study3-synthetic-ci": {"path": ".github/workflows/study3-synthetic-ci.yml",
                            "jobs": ("study3-synthetic-contracts",)},
    "study4-synthetic-ci": {"path": ".github/workflows/study4-synthetic-ci.yml",
                            "jobs": ("study4-synthetic-contracts",)},
}
TEXT_ALLOWLIST = frozenset(CONTRACT_PATHS) | frozenset(FREEZE_CHANGES) | frozenset(
    SCIENTIFIC_METHOD_FILES) | {AUTHORIZATION, CI_PROOF, SOURCE_MANIFEST}
MAX_TEXT_BYTES = 128 * 1024 * 1024


class S4AExecutionError(ValueError):
    """A frozen gate failed; there is no automatic repair or retry."""


def require(condition, message):
    if not condition:
        raise S4AExecutionError(message)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def exact(value, expected):
    if type(value) is not type(expected):
        return False
    if type(value) is dict:
        return value.keys() == expected.keys() and all(exact(value[k], expected[k]) for k in value)
    if type(value) is list:
        return len(value) == len(expected) and all(exact(a, b) for a, b in zip(value, expected))
    return value == expected


def hash_string(value, length=64):
    return type(value) is str and len(value) == length and all(c in "0123456789abcdef" for c in value)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load_json(content):
    def invalid_constant(_value):
        raise S4AExecutionError("non-finite JSON constant")
    return json.loads(content.decode("utf-8", errors="strict"),
                      object_pairs_hook=_unique_object, parse_constant=invalid_constant)


def _parts(relative):
    require(type(relative) is str and relative and not relative.startswith("/")
            and "\\" not in relative and all(part not in ("", ".", "..")
            for part in relative.split("/")), "unsafe relative path")
    return PurePosixPath(relative).parts


def _root_fd(root):
    root = Path(root).absolute()
    require(".." not in root.parts, "root traversal forbidden")
    return os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)


def _parent_fd(root, relative, create=False):
    parts = _parts(relative)
    fd = _root_fd(root)
    try:
        for component in parts[:-1]:
            if create:
                try:
                    os.mkdir(component, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd, parts[-1]
    except BaseException:
        os.close(fd)
        raise


def read_text(root, relative):
    """Read one literal documentary path, without following symlinks."""
    require(relative in TEXT_ALLOWLIST, "path outside documentary allowlist")
    parent, name = _parent_fd(root, relative)
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    finally:
        os.close(parent)
    with os.fdopen(fd, "rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "regular textual file required")
        content = stream.read(MAX_TEXT_BYTES + 1)
    require(len(content) <= MAX_TEXT_BYTES, "documentary size budget exceeded")
    content.decode("utf-8", errors="strict")
    return content


def _exists(root, relative):
    try:
        parent, name = _parent_fd(root, relative)
    except FileNotFoundError:
        return False
    try:
        try:
            info = os.stat(name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            return False
        require(not stat.S_ISLNK(info.st_mode), "symlink forbidden")
        return True
    finally:
        os.close(parent)


def _unconsumed(root):
    for name in (RECEIPT, RESULT, TERMINAL):
        require(not _exists(root, EVIDENCE + "/" + name), "S4-A1 already consumed; no retry")
    # Unknown evidence is also a divergence. Merely checking this namespace
    # never examines a corpus path or reads experimental content.
    if _exists(root, EVIDENCE):
        parent, name = _parent_fd(root, EVIDENCE)
        try:
            fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        finally:
            os.close(parent)
        try:
            require(not os.listdir(fd), "unexpected pre-existing S4-A1 evidence")
        finally:
            os.close(fd)


def git_bytes(root, *args):
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT") if key in os.environ}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"})
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=root,
                          env=env, capture_output=True, check=True, timeout=30).stdout


def git(root, *args):
    return git_bytes(root, *args).decode("utf-8").strip()


def authorization_grant(head, contract_hashes):
    """Describe the exact future author grant; do not create a local control."""
    require(hash_string(head, 40), "exact freeze SHA required")
    require(type(contract_hashes) is dict and set(contract_hashes) == set(CONTRACT_PATHS)
            and all(hash_string(value) for value in contract_hashes.values()),
            "exact frozen contract hashes required")
    return {
        "schema_version": 1, "study": "STUDY4", "phase": "S4_A1_METADATA_ONLY_FEASIBILITY",
        "decision_owner": "Leonardo Maximino Bernardo", "explicit_author_decision": True,
        "branch": BRANCH, "method_freeze_sha": head, "contracts_sha256": dict(contract_hashes),
        "documentary_manifest": SOURCE_MANIFEST, "documentary_manifest_sha256": SOURCE_SHA,
        "metadata_analysis_authorized": True, "feasibility_cardinality_matching_authorized": True,
        "receipt_creation_authorized": True, "metadata_analysis_invocations": 1, "retries": 0,
        "scientific_execution_authorized": False, "experimental_binary_reads_authorized": False,
        "payload_row_reads_authorized": False, "feature_extraction_authorized": False,
        "model_fit_authorized": False, "final_pair_matching_authorized": False,
        "pair_identity_disclosure_authorized": False, "development_access": False,
        "test_access": False, "silver_access": False, "video_access": False,
        "automatic_continuation": False,
    }


def validate_authorization(decision, head, contract_hashes):
    require(type(decision) is dict and set(decision) == {"grant", "author_decision_sha256"},
            "explicit S4-A1 local authorization required")
    require(exact(decision["grant"], authorization_grant(head, contract_hashes)),
            "grant must bind exact S4-A1 authority, freeze and contracts")
    require(hash_string(decision["author_decision_sha256"]), "author decision provenance required")
    return digest(canonical(decision))


def verify_ci(proof, head):
    require(type(proof) is dict and proof.get("head_sha") == head
            and type(proof.get("runs")) is list, "exact-SHA CI proof required")
    workflows = set()
    jobs = set()
    steps = 0
    for run in proof["runs"]:
        require(type(run) is dict and run.get("headSha") == head
                and run.get("status") == "completed" and run.get("conclusion") == "success",
                "every CI run must succeed at the exact freeze")
        name = run.get("name")
        require(type(name) is str and name in REQUIRED_WORKFLOWS and name not in workflows,
                "all eleven applicable workflows required exactly once")
        expected = REQUIRED_WORKFLOWS[name]
        require(run.get("path") == expected["path"] and type(run.get("jobs")) is list,
                "exact workflow path and jobs required")
        local_jobs = set()
        for job in run["jobs"]:
            require(type(job) is dict and job.get("status") == "completed"
                    and job.get("conclusion") == "success" and type(job.get("steps")) is list
                    and bool(job["steps"]), "CI job incomplete, failed or skipped")
            job_name = job.get("name")
            require(type(job_name) is str and job_name in expected["jobs"]
                    and job_name not in local_jobs and job_name not in jobs,
                    "unexpected or duplicate CI job")
            for step in job["steps"]:
                require(type(step) is dict and step.get("status") == "completed"
                        and step.get("conclusion") == "success", "CI step incomplete, failed or skipped")
                steps += 1
            local_jobs.add(job_name)
            jobs.add(job_name)
        require(local_jobs == set(expected["jobs"]), "workflow job missing")
        workflows.add(name)
    require(workflows == set(REQUIRED_WORKFLOWS) and len(jobs) == 12,
            "all eleven workflows and twelve jobs required")
    return {"job_count": len(jobs), "step_count": steps}


def preflight(root):
    """Authenticate controls and freeze custody without opening the corpus."""
    _unconsumed(root)
    require(_exists(root, AUTHORIZATION), "explicit S4-A1 local authorization required")
    decision_bytes = read_text(root, AUTHORIZATION)
    decision = load_json(decision_bytes)
    require(_exists(root, CI_PROOF), "exact-SHA CI proof required")
    ci_bytes = read_text(root, CI_PROOF)
    ci_proof = load_json(ci_bytes)
    require(Path(root).absolute() == WORKTREE, "authorized Study4 worktree required")
    head = git(root, "rev-parse", "HEAD")
    require(hash_string(head, 40) and head != BASE, "published S4-A0 freeze required")
    require(git(root, "symbolic-ref", "--short", "HEAD") == BRANCH, "exact Study4 branch required")
    require(git(root, "status", "--porcelain", "--untracked-files=no") == "", "tracked tree must be clean")
    require(git(root, "rev-list", "--parents", "-n", "1", head).split() == [head, BASE],
            "freeze must have exactly the authorized parent")
    changes = git(root, "diff", "--name-status", "--no-renames", BASE, head, "--").splitlines()
    actual = {}
    for line in changes:
        fields = line.split("\t")
        require(len(fields) == 2 and fields[1] not in actual, "invalid freeze inventory")
        actual[fields[1]] = fields[0]
    require(actual == FREEZE_CHANGES, "freeze requires exactly the authorized eight paths")
    for path in sorted(set(FREEZE_CHANGES) | set(CONTRACT_PATHS) | set(SCIENTIFIC_METHOD_FILES)):
        require(read_text(root, path) == git_bytes(root, "show", head + ":" + path),
                "local frozen documentary bytes changed")
    require(git_bytes(root, "diff", "--name-only", BASE, head, "--", *SCIENTIFIC_METHOD_FILES) == b"",
            "historical Study3 scientific method changed")
    contract_bytes = {path: read_text(root, path) for path in CONTRACT_PATHS}
    contract_hashes = {path: digest(content) for path, content in contract_bytes.items()}
    authority = load_json(contract_bytes["configs/study4/authority.json"])
    require(authority.get("phase") == "S4_A0_FEASIBILITY_AUDITOR_FREEZE"
            and authority.get("future_s4a_metadata_analysis_requires_explicit_author_decision") is True,
            "closed S4-A0 preparation authority required")
    require(all(authority.get(key) is False for key in (
        "scientific_execution_authorized", "experimental_metadata_analysis_authorized",
        "experimental_binary_reads_authorized", "payload_row_reads_authorized",
        "feature_extraction_authorized", "model_fit_authorized", "matching_execution_authorized",
        "receipt_creation_authorized", "development_access", "test_access", "silver_access",
        "video_access", "automatic_continuation")), "preparation authority cannot activate science")
    historical = load_json(contract_bytes["configs/study3/data-contract.json"])
    require(historical.get("train_manifest") == SOURCE_MANIFEST
            and historical.get("train_manifest_sha256") == SOURCE_SHA,
            "historical documentary manifest binding changed")
    semantic = validate_authorization(decision, head, contract_hashes)
    ci = verify_ci(ci_proof, head)
    return {"head_sha": head, "authorization_sha256": digest(decision_bytes),
            "authorization_semantic_digest": semantic, "ci_proof_sha256": digest(ci_bytes),
            "contracts_sha256": contract_hashes, "documentary_manifest_sha256": SOURCE_SHA,
            "ci_job_count": ci["job_count"], "ci_step_count": ci["step_count"]}


def _write_exclusive(root, name, value):
    require(name in (RECEIPT, RESULT, TERMINAL), "unapproved evidence filename")
    content = canonical(value) + b"\n"
    parent, leaf = _parent_fd(root, EVIDENCE + "/" + name, create=True)
    try:
        fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=parent)
    finally:
        os.close(parent)
    with os.fdopen(fd, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    return digest(content)


def create_receipt(root, proof):
    """An exclusive receipt consumes this metadata audit, never visual science."""
    _unconsumed(root)
    receipt = {"schema_version": 1, "study": "STUDY4", "phase": "S4_A1_METADATA_ONLY_FEASIBILITY",
               "created_at": datetime.now(timezone.utc).isoformat(), "authority_consumed": True,
               "metadata_analysis_invocations": 1, "retry_authorized": False,
               "head_sha": proof["head_sha"], "authorization_sha256": proof["authorization_sha256"],
               "authorization_semantic_digest": proof["authorization_semantic_digest"],
               "ci_proof_sha256": proof["ci_proof_sha256"], "contracts_sha256": proof["contracts_sha256"],
               "documentary_manifest_sha256": proof["documentary_manifest_sha256"],
               "payload_binary_reads": 0, "feature_extractions": 0, "fits": 0}
    _write_exclusive(root, RECEIPT, receipt)
    return receipt


def run(root):
    """One future invocation; no public option can bypass preflight."""
    proof = preflight(root)
    _unconsumed(root)
    raw = read_text(root, SOURCE_MANIFEST)
    require(digest(raw) == proof["documentary_manifest_sha256"], "documentary manifest SHA mismatch")
    create_receipt(root, proof)
    try:
        manifest = load_json(raw)
        require(type(manifest) is dict and type(manifest.get("rows")) is list,
                "documentary rows required")
        from snbi_fragmentation.study4_feasibility import summarize_feasibility, validate_result_schema
        result = summarize_feasibility(manifest["rows"], proof["documentary_manifest_sha256"])
        validate_result_schema(result)
        result_sha = _write_exclusive(root, RESULT, result)
        terminal = {"STUDY4_S4A": "PASS", "state": "CLOSED_CONSUMED", "authority_consumed": True,
                    "retry_authorized": False, "feasibility_decision": result["feasibility_decision"],
                    "result_sha256": result_sha, "visual_model_execution_allowed": False,
                    "final_pair_matching_executed": False, "pair_identities_selected": False,
                    "payload_binary_reads": 0, "feature_extractions": 0, "fits": 0,
                    "current_authorized_activity": "NONE_AWAITING_AUTHOR_DECISION"}
        _write_exclusive(root, TERMINAL, terminal)
        return terminal
    except Exception as error:
        # Preserve any partial artifacts. Diagnostics disclose the error class,
        # never a row, identifier, storage descriptor or source-derived message.
        blocked = {"STUDY4_S4A": "BLOCKED", "state": "CLOSED_CONSUMED", "authority_consumed": True,
                   "retry_authorized": False, "error_type": type(error).__name__,
                   "visual_model_execution_allowed": False, "final_pair_matching_executed": False,
                   "pair_identities_selected": False, "payload_binary_reads": 0,
                   "feature_extractions": 0, "fits": 0,
                   "current_authorized_activity": "NONE_AWAITING_AUTHOR_DECISION"}
        if not _exists(root, EVIDENCE + "/" + TERMINAL):
            _write_exclusive(root, TERMINAL, blocked)
        raise


def main():
    try:
        terminal = run(WORKTREE)
    except Exception as error:
        print(json.dumps({"STUDY4_S4A": "BLOCKED", "error_type": type(error).__name__,
                          "retry_authorized": False}, sort_keys=True))
        return 1
    print(json.dumps(terminal, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
