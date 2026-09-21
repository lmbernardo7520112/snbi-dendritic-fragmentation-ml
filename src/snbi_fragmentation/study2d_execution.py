"""One frozen TRAIN-only Study2-D attribution; no model selection or TEST path."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import resource
import shutil
import stat
import subprocess
import time

BASE = "ec97cb5041ef35d4f6c9a79b54d756d6fbee674f"
BRANCH = "feat/study2d-data-centric-bridge"
E = "artifacts/evidence/STUDY2_D_ATTRIBUTION"
C = "artifacts/evidence/STUDY2_C_BENCHMARK"
AUTH = "configs/authority/study2d.json"
AUTH_SHA = "5b28d77ffdb964d4f421bec1378e2b0e35feb70afb79225ad6fe08273fe4ab93"
METHOD_FREEZE_ORIGINAL = "21400de67d21901aeb8e5abac528689fc39169fa"
REPAIR_AUTH_SHA = "1b2b0eea52ea81c6b411f2b624abf3b8519d0d0753750a41f4334536e36bc10c"
FOLD_SHA = "85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2"
MAX_TEXT = 268435456
MIN_FREE = 53687091200
CODE = tuple("src/snbi_fragmentation/study2d_" + n + ".py" for n in
             ("design", "models", "io", "execution")) + ("scripts/run_study2d.py",)
TESTS = tuple("tests/test_study2d_" + n + ".py" for n in
              ("design", "models", "io", "execution"))
PROTOCOLS = tuple(E + "/" + n for n in (
    "STUDY2_D_PROTOCOL.md", "STUDY2_D_ATTRIBUTION_DESIGN.json",
    "STUDY2_D_FIT_BUDGET.json", "STUDY2_D_CLAIM_SCOPE.md",
    "MODEL_CONTRACT.json", "TRAIN_INPUT_MANIFEST.json"))
REQUIRED_JOBS = frozenset(("deterministic-contracts", "scientific-synthetic-contracts",
    "ti3-synthetic-contracts", "ti3b-synthetic-contracts", "ti3c-synthetic-contracts",
    "ti3d-final-synthetic-contracts", "study2a-synthetic-contracts",
    "study2b-synthetic-contracts", "study2c-synthetic-contracts",
    "study2d-synthetic-contracts"))


class Study2DError(ValueError):
    """A stopped attempt cannot authorize repair, retry or a new condition."""


def exact(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def require(condition, message):
    if not condition:
        raise Study2DError(message)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, relative):
    require(type(relative) is str and relative and not relative.startswith("/")
            and "\\" not in relative
            and all(p not in ("", ".", "..") for p in relative.split("/")),
            "unsafe relative path")
    current = Path(root)
    require(not current.is_symlink(), "root symlink")
    for part in PurePosixPath(relative).parts:
        current /= part
        require(not current.is_symlink(), "symlink prohibited")
    return current


def git_bytes(root, *args):
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=root,
                          capture_output=True, check=True, timeout=20).stdout


def git(root, *args):
    return git_bytes(root, *args).decode().strip()


def read_text(root, name):
    require(name.startswith(("src/", "scripts/", "tests/", "configs/",
            "artifacts/evidence/", ".github/")) or name in {
            "requirements-ti3-ml.txt", "requirements-ti3c-cnn.txt",
            "constraints-ti3c-cnn.txt"}, "text path outside allowlist")
    require(PurePosixPath(name).suffix in {".py", ".json", ".md", ".txt", ".yml", ".sha256"},
            "not textual evidence")
    # Historical prediction/metric bundles are unnecessary to this experiment.
    if name.startswith(C + "/"):
        require(PurePosixPath(name).name in {"SPLIT_MANIFEST.json", "BACKGROUND_ARTIFACTS.json",
                "MODEL_CONTRACT.json", "terminal-state.json", "METHOD_FREEZE.json"},
                "Study2-C DEV/TEST predictions and result bundles are prohibited")
    fd = os.open(safe_path(root, name), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "regular text required")
        data = stream.read(MAX_TEXT + 1)
    require(len(data) <= MAX_TEXT, "text budget exceeded")
    data.decode("utf-8", errors="strict")
    return data


def load(root, name):
    return json.loads(read_text(root, name))


def emit(root, name, value):
    require(PurePosixPath(name).name == name, "output must be a namespace leaf")
    data = ((json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
            if not isinstance(value, str) else value).encode("utf-8")
    require(len(data) <= MAX_TEXT and shutil.disk_usage(root).free - len(data) >= MIN_FREE,
            "text or disk budget exceeded")
    path = safe_path(root, E + "/" + name)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return digest(data)


def expected_authority():
    return {"schema_version": 1, "phase": "STUDY2_D", "base_sha": BASE, "branch": BRANCH,
            "authority_sha256": AUTH_SHA, "scientific_invocations_limit": 1,
            "distinct_rf_fits_limit": 100, "part_a_fits": 84, "part_b_new_fits": 12,
            "part_c_new_fits": 4, "model_family": "RF_REFERENCE", "features": "LBP20_MULTIMODAL",
            "train_positive_groups": 32, "train_background_groups": 32,
            "allowed_split": "TRAIN", "allowed_tiers": ["GOLD", "BACKGROUND"],
            "historical_cv_fold_sha256": FOLD_SHA, "development_access": False,
            "test_access": False, "silver_access": False, "source_access": False,
            "model_selection": False, "terminal_closes_authority": True}


def expected_fit_budget():
    return {"part_a_distinct_fits": 84, "part_b_additional_distinct_fits": 12,
            "part_c_additional_distinct_fits": 4, "total_distinct_rf_fits": 100,
            "conceptual_fit_reuses": 8, "scientific_invocations": 1,
            "retries": 0, "evaluation_split": "HISTORICAL_TRAIN_CV_VALIDATION_ONLY"}


def authority(root):
    require(git(root, "branch", "--show-current") == BRANCH, "wrong branch")
    require(exact(load(root, AUTH), expected_authority()), "authority divergence")
    require(digest(read_text(root, E + "/AUTHORIZATION.md")) == AUTH_SHA,
            "author decision hash differs")
    previous = load(root, C + "/terminal-state.json")
    require(previous.get("STUDY2_C") == "PASS" and previous.get("STUDY2_CLOSED") is True
            and previous.get("STATE") == "CLOSED_CONSUMED"
            and previous.get("TEST_STATE") == "CONSUMED", "Study2-C must remain consumed")
    return expected_authority()


def require_synthetic(root):
    tests = load(root, E + "/SYNTHETIC_TESTS.json")
    require(tests.get("status") == "PASS"
            and all(type(tests.get(k)) is int and tests[k] == 0 for k in ("skips", "errors", "failures")),
            "synthetic validation requires PASS and zero skips/errors/failures")
    return tests


def prepare_plan(root):
    """One textual TRAIN-only plan before the method commit; no experimental I/O."""
    authority(root)
    require(git(root, "rev-parse", "HEAD") == BASE, "plan must precede method freeze")
    for name in ("PLAN_RECEIPT.json", "STUDY2_D_ATTRIBUTION_DESIGN.json", "MODEL_CONTRACT.json",
                 "STUDY2_D_FIT_BUDGET.json", "EXECUTION_RECEIPT.json", "results.json", "terminal-state.json"):
        require(not safe_path(root, E + "/" + name).exists(), "metadata plan already consumed")
    require_synthetic(root)
    from .study2d_design import build_attribution_design, validate_attribution_design
    from .study2d_models import method_contract
    emit(root, "PLAN_RECEIPT.json", {"created_at_utc": utc_now(), "metadata_only": True,
         "head_sha": BASE, "design_code_sha256": digest(read_text(root, CODE[0])),
         "scientific_invocations": 0, "experimental_opens": 0})
    try:
        design = build_attribution_design(load(root, C + "/SPLIT_MANIFEST.json"))
        validate_attribution_design(design)
        emit(root, "STUDY2_D_ATTRIBUTION_DESIGN.json", design)
        emit(root, "STUDY2_D_FIT_BUDGET.json", expected_fit_budget())
        emit(root, "MODEL_CONTRACT.json", method_contract())
        return {"status": "PASS", "rows": len(design["rows"]), "distinct_fits": len(design["fits"]),
                "scientific_invocations": 0, "experimental_opens": 0}
    except Exception as exc:
        emit(root, "terminal-state.json", {"STUDY2_D": "BLOCKED_METADATA_PLAN",
             "failure": type(exc).__name__ + ": " + str(exc), "SCIENTIFIC_STUDY2D_RUNS": 0,
             "STATE": "CLOSED_BLOCKED", "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"})
        raise


def preserved_baseline(root):
    changed = set(git(root, "diff", "--name-only", BASE, "--").splitlines())
    old = set(git(root, "ls-tree", "-r", "--name-only", BASE).splitlines())
    require(not (changed & old) - {"configs/governance/phase-scope-v1.json"},
            "historical file changed outside phase-scope append")
    previous = json.loads(git_bytes(root, "show", BASE + ":configs/governance/phase-scope-v1.json"))
    current = load(root, "configs/governance/phase-scope-v1.json")
    for key in previous:
        if key != "domains":
            require(exact(previous[key], current.get(key)), "historical scope metadata changed")
    require(set(previous["domains"]) == set(current.get("domains", {})), "scope domains changed")
    for domain, entries in previous["domains"].items():
        new = current["domains"][domain]
        require(len({v["path"] for v in new}) == len(new), "duplicate scope path")
        now = {v["path"]: v for v in new}
        require(all(exact(v, now.get(v["path"])) for v in entries), "historical scope member changed")
        additions = set(now) - {v["path"] for v in entries}
        require(not additions or domain == "TI3_ACTIVE" and additions == set(CODE + TESTS),
                "phase-scope additions differ from exact Study2-D paths")
    return len(old)


def verify_ci(proof, head):
    require(proof.get("head_sha") == head, "CI HEAD differs")
    names = []
    for run in proof.get("runs", []):
        require(run.get("headSha") == head and run.get("status") == "completed"
                and run.get("conclusion") == "success", "CI run not successful at method SHA")
        for job in run.get("jobs", []):
            require(job.get("status") == "completed" and job.get("conclusion") == "success"
                    and job.get("steps"), "CI job not successful")
            require(all(s.get("status") == "completed" and s.get("conclusion") == "success"
                        for s in job["steps"]), "CI step not successful")
            names.append(job["name"])
    require(len(names) == len(REQUIRED_JOBS) and set(names) == REQUIRED_JOBS,
            "all ten CI jobs are required exactly once")
    return names


def validate_inputs(design, manifest):
    rows = design["rows"]
    require(type(manifest) is dict and type(manifest.get("rows")) is list,
            "TRAIN input manifest missing")
    stripped = [{k: v for k, v in r.items() if k != "storage"} for r in manifest["rows"]]
    require(exact(stripped, rows), "input rows differ by type/value/order from frozen design")
    require(all(type(r.get("storage")) is dict for r in manifest["rows"]), "storage map missing")
    require(len(rows) == 10907 and len({r["group_id"] for r in rows}) == 64,
            "TRAIN rows/groups differ")
    require(all(r.get("split") == "TRAIN" and
                ((r.get("label") == 1 and r.get("tier") == "GOLD") or
                 (r.get("label") == 0 and r.get("tier") == "BACKGROUND")) for r in rows),
            "non-TRAIN or forbidden supervision in input")
    require(Counter(r["label"] for r in rows) == {0: 7049, 1: 3858}, "TRAIN class counts differ")
    return rows


def verify_repair(root, head):
    """Admit only the one authorized compatibility child; preserve original science."""
    require(git(root, "rev-list", "--parents", "-n", "1", head).split()
            == [head, METHOD_FREEZE_ORIGINAL]
            and git(root, "rev-list", "--parents", "-n", "1", METHOD_FREEZE_ORIGINAL).split()
            == [METHOD_FREEZE_ORIGINAL, BASE], "exact repair ancestry required; merges or further children forbidden")
    require(git(root, "rev-parse", "HEAD^") == METHOD_FREEZE_ORIGINAL
            and git(root, "rev-parse", "HEAD^^") == BASE, "repair parent/grandparent differ")
    require(digest(read_text(root, E + "/CI_REPAIR_AUTHORIZATION.md")) == REPAIR_AUTH_SHA,
            "repair authorization hash differs")
    permitted_modifications = {"tests/test_study2d_io.py", "tests/test_study2d_execution.py",
        "src/snbi_fragmentation/study2d_execution.py", "configs/governance/phase-scope-v1.json",
        E + "/METHOD_FREEZE.json", E + "/SYNTHETIC_TESTS.json"}
    proof = load(root, E + "/CI_REPAIR_DIFF.json")
    declared = proof.get("allowed_changes", {})
    require(proof.get("parent_method_freeze_sha") == METHOD_FREEZE_ORIGINAL
            and proof.get("scientific_method_changed") is False, "repair diff declaration differs")
    actual = {}
    for line in git(root, "diff", "--name-status", "--no-renames", METHOD_FREEZE_ORIGINAL, head).splitlines():
        status, name = line.split("\t")
        require(name not in actual and (status == "M" and name in permitted_modifications
                or status == "A" and name.startswith(E + "/") and PurePosixPath(name).suffix
                in {".json", ".md", ".txt", ".sha256"}), "repair changed an unauthorized path")
        actual[name] = status
    require(exact(actual, declared) and {p for p, s in actual.items() if s == "M"}
            == permitted_modifications, "repair diff differs from exact published allowlist")
    for name in actual:
        entry = git(root, "ls-tree", head, "--", name).split()
        require(len(entry) == 4 and entry[0:2] == ["100644", "blob"], "repair mode/type changed")
    original = json.loads(git_bytes(root, "show", METHOD_FREEZE_ORIGINAL + ":" + E + "/METHOD_FREEZE.json"))
    for name, expected in original["files"].items():
        require(digest(git_bytes(root, "show", METHOD_FREEZE_ORIGINAL + ":" + name)) == expected,
                "original freeze blob differs")
        if name not in permitted_modifications:
            require(digest(read_text(root, name)) == expected
                    and digest(git_bytes(root, "show", head + ":" + name)) == expected,
                    "original scientific or historical contract changed: " + name)
    operational = load(root, E + "/METHOD_FREEZE.json")
    require(operational.get("parent_method_freeze_sha") == METHOD_FREEZE_ORIGINAL
            and operational.get("scientific_method_changed") is False, "operational freeze provenance missing")
    require({E + "/CI_REPAIR_AUTHORIZATION.md", E + "/CI_REPAIR_DIFF.json"}
            <= set(operational["files"]), "repair proofs must be frozen")
    return {"status": "PASS", "parent_method_freeze_sha": METHOD_FREEZE_ORIGINAL,
            "grandparent_sha": BASE, "original_hashes_verified": len(original["files"]),
            "repair_paths": len(actual), "scientific_method_changed": False}


def preflight(root):
    """Textual checks only. Does not construct a corpus reader or create a receipt."""
    for name in ("EXECUTION_RECEIPT.json", "FIT_RESULTS.json", "results.json", "terminal-state.json"):
        require(not safe_path(root, E + "/" + name).exists(), "authority consumed; no retry")
    authority(root)
    require(shutil.disk_usage(root).free >= MIN_FREE + MAX_TEXT, "disk reserve insufficient")
    head = git(root, "rev-parse", "HEAD")
    repair = verify_repair(root, head)
    preserved_baseline(root)
    for line in read_text(root, "constraints-ti3c-cnn.txt").decode().splitlines():
        name, version = line.split("==")
        require(importlib.metadata.version(name) == version, "dependency version changed: " + name)
    raw = read_text(root, E + "/METHOD_FREEZE.json")
    require(raw == git_bytes(root, "show", head + ":" + E + "/METHOD_FREEZE.json"),
            "method freeze differs from HEAD")
    freeze = json.loads(raw)
    required = set(CODE + TESTS + PROTOCOLS) | {AUTH, E + "/AUTHORIZATION.md",
        E + "/CACHE_CUSTODY_AUTHORIZATION.md", E + "/SYNTHETIC_TESTS.json",
        ".github/workflows/study2d-synthetic.yml", "configs/governance/phase-scope-v1.json",
        "constraints-ti3c-cnn.txt", "requirements-ti3-ml.txt", "requirements-ti3c-cnn.txt",
        "src/snbi_fragmentation/study2c_design.py", "src/snbi_fragmentation/study2c_models.py",
        C + "/SPLIT_MANIFEST.json", C + "/BACKGROUND_ARTIFACTS.json", C + "/terminal-state.json"}
    require(required <= set(freeze.get("files", {})), "incomplete method freeze")
    for name, expected_sha in freeze["files"].items():
        data = read_text(root, name)
        require(digest(data) == expected_sha and data == git_bytes(root, "show", head + ":" + name),
                "frozen bytes changed: " + name)
    require_synthetic(root)
    from .study2d_design import validate_attribution_design
    from .study2d_models import method_contract
    design = load(root, E + "/STUDY2_D_ATTRIBUTION_DESIGN.json")
    validate_attribution_design(design)
    require(exact(load(root, E + "/MODEL_CONTRACT.json"), method_contract()), "model contract differs")
    require(exact(load(root, E + "/STUDY2_D_FIT_BUDGET.json"), expected_fit_budget()), "fit budget differs")
    validate_inputs(design, load(root, E + "/TRAIN_INPUT_MANIFEST.json"))
    old = load(root, C + "/SPLIT_MANIFEST.json")
    require(old.get("hashes", {}).get("cv_fold_by_group_sha256") == FOLD_SHA,
            "historical fold hash differs")
    expected_rows = [r for r in old["samples"] if r["split"] == "TRAIN" and r["tier"] in {"GOLD", "BACKGROUND"}]
    require(exact(design["rows"], expected_rows), "TRAIN allowlist differs from Study2-C")
    jobs = verify_ci(load(root, E + "/CI_PROOF.json"), head)
    return {"status": "PASS", "head_sha": head, "freeze_text_count": len(freeze["files"]),
            "ci_jobs": jobs, "experimental_opens": 0, "receipt_created": False,
            "allowed_rows": len(expected_rows), "distinct_fits": 100, "repair": repair,
            "method_freeze_original": METHOD_FREEZE_ORIGINAL, "ci_repair_sha": head}


class TrainAccessState:
    """Single grant for exactly the materialized TRAIN manifest, before any path."""
    def __init__(self, receipt_sha, head, rows):
        self.receipt_sha, self.head = receipt_sha, head
        self.rows = json.loads(json.dumps(rows, allow_nan=False))
        self.granted = False

    def grant(self, action, rows):
        require(not self.granted and action == "LOAD_TRAIN_ROWS", "TRAIN input grant already consumed or wrong action")
        require(exact(rows, self.rows), "row membership/type/order changed")
        require(all(r.get("split") == "TRAIN" and r.get("tier") in {"GOLD", "BACKGROUND"} for r in rows),
                "DEV/TEST/SILVER cannot receive a grant")
        require(len(self.receipt_sha) == 64 and len(self.head) == 40, "durable receipt/head binding required")
        self.granted = True
        return {"authorized": True, "execution_receipt_sha256": self.receipt_sha,
                "method_freeze_sha": self.head}


def progress(event):
    print(json.dumps({"progress": event}, ensure_ascii=False, allow_nan=False), flush=True)


def _execute(root):
    proof = preflight(root)
    design = load(root, E + "/STUDY2_D_ATTRIBUTION_DESIGN.json")
    manifest = load(root, E + "/TRAIN_INPUT_MANIFEST.json")
    receipt_sha = emit(root, "EXECUTION_RECEIPT.json", {"created_at_utc": utc_now(),
        "preflight": proof, "method_freeze_sha": proof["head_sha"], "attempt": 1,
        "design_sha256": digest(read_text(root, E + "/STUDY2_D_ATTRIBUTION_DESIGN.json")),
        "input_manifest_sha256": digest(read_text(root, E + "/TRAIN_INPUT_MANIFEST.json")),
        "fit_budget": expected_fit_budget(), "DEV_AUTHORIZED": False, "TEST_AUTHORIZED": False})
    counts = {"scientific_invocations": 1, "feature_extractions_started": 0,
              "feature_extractions_completed": 0, "feature_rows": 0,
              "fits_started": 0, "fits_completed": 0, "validation_evaluations": 0,
              "part_a_fits": 0, "part_b_fits": 0, "part_c_fits": 0, "result_reuses": 0, "retries": 0}
    audit, records = {}, {}
    failure, active_fit, accessor, summary = None, None, None, None
    start = time.perf_counter()
    try:
        from .study2d_io import TrainCorpusAccess
        from .study2d_models import extract_lbp20, fit_reference, predict_reference
        from .study2d_design import summarize_attribution
        from .study2c_design import metric_bundle
        import numpy as np
        rows = design["rows"]
        state = TrainAccessState(receipt_sha, proof["head_sha"], manifest["rows"])
        accessor = TrainCorpusAccess(root, manifest["rows"], state.grant, audit)
        pairs = accessor.load()
        require(pairs.dtype == np.uint8 and pairs.shape == (len(rows), 2, 65, 65), "TRAIN tensor shape/type differs")
        for key in ("DEV_GROUPS_READ", "TEST_GROUPS_READ", "DEV_ROWS_READ", "TEST_ROWS_READ",
                    "TEST_CACHE_ROWS_READ", "TEST_FEATURES_COMPUTED", "EXPERIMENTAL_SOURCE_OPENS",
                    "FFMPEG_RUNS", "ESM1_OPENS", "ESM2_OPENS", "ESM3_OPENS", "ESM4_OPENS",
                    "ESM5_OPENS", "ESM6_OPENS"):
            require(type(audit.get(key)) is int and audit[key] == 0, "I/O firewall counter differs: " + key)
        require(audit.get("rows_read") == len(rows) and audit.get("rows_authenticated") == len(rows)
                and audit.get("bytes_read") == len(rows) * 8450, "I/O row authentication accounting differs")
        counts["feature_extractions_started"] += 1
        features = extract_lbp20(pairs)
        counts["feature_extractions_completed"] += 1
        counts["feature_rows"] = len(rows)
        require(features.shape == (len(rows), 20) and np.isfinite(features).all(), "LBP20 shape/values differ")
        del pairs
        accessor.close()
        row_index = {r["sample_id"]: i for i, r in enumerate(rows)}
        for spec in design["fits"]:
            active_fit = spec["fit_id"]
            require(active_fit not in records and counts["fits_started"] < 100, "duplicate fit or budget exceeded")
            ti = [row_index[s] for s in spec["train_sample_ids"]]
            vi = [row_index[s] for s in spec["validation_sample_ids"]]
            training, validation = [rows[i] for i in ti], [rows[i] for i in vi]
            event_counts = Counter()

            def on_event(event):
                name = event.get("event")
                require(name in {"RF_FIT_START", "RF_FIT_COMPLETE"}, "unknown fit event")
                if name == "RF_FIT_START":
                    require(not event_counts, "fit start repeated")
                    counts["fits_started"] += 1
                else:
                    require(event_counts["RF_FIT_START"] == 1 and not event_counts["RF_FIT_COMPLETE"],
                            "fit completion without unique start")
                    counts["fits_completed"] += 1
                    counts["part_" + spec["part"].lower() + "_fits"] += 1
                event_counts[name] += 1
                progress({**event, "fit_id": active_fit, "part": spec["part"], "fold": spec["fold"]})

            model, metadata = fit_reference(features[ti], training, spec["weighting"], on_event=on_event)
            require(event_counts == {"RF_FIT_START": 1, "RF_FIT_COMPLETE": 1}, "actual fit event budget differs")
            output = predict_reference(model, features[vi])
            require(len(output["predictions"]) == len(validation), "prediction count differs")
            metrics = metric_bundle(validation, output["predictions"])
            counts["validation_evaluations"] += 1
            records[active_fit] = {"fit_id": active_fit, "spec": spec, "fit": metadata,
                "predictions": {"sample_ids": spec["validation_sample_ids"], **output}, "metrics": metrics}
            progress({"event": "VALIDATION_COMPLETE", "fit_id": active_fit,
                      "primary_gmba": metrics["primary_gmba"]})
            del model
        require((counts["fits_started"], counts["fits_completed"], counts["validation_evaluations"],
                 counts["part_a_fits"], counts["part_b_fits"], counts["part_c_fits"]) == (100, 100, 100, 84, 12, 4),
                "distinct fit budget not fulfilled")
        summary = summarize_attribution(design, records)
        expected_fields = {"GROUP_DIVERSITY_DESCRIPTOR", "GROUP_DIVERSITY_DELTA_K24_K17",
            "GROUP_DIVERSITY_DELTA_K24_K4", "TEMPORAL_DENSITY_DESCRIPTOR",
            "TEMPORAL_DENSITY_DELTA_ALL_1", "GROUP_WEIGHTING_DESCRIPTOR", "GROUP_WEIGHTING_DELTA"}
        require(set(summary.get("terminal_fields", {})) == expected_fields,
                "attribution terminal fields missing")
        require(type(summary.get("narrative_bridge_markdown")) is str
                and "|" in summary["narrative_bridge_markdown"]
                and len(summary.get("narrative_bridge_table", [])) == 9,
                "nine-condition Markdown bridge table required")
        counts["result_reuses"] = len(design["reuse_refs"])
        require(counts["result_reuses"] == 8, "exactly eight result references required")
    except Exception as exc:
        failure = type(exc).__name__ + ": " + str(exc)
    finally:
        if accessor is not None:
            try:
                accessor.close()
            except Exception as exc:
                failure = failure or type(exc).__name__ + ": " + str(exc)
    emit(root, "FIT_RESULTS.json", {"method_freeze_sha": proof["head_sha"],
         "execution_receipt_sha256": receipt_sha, "results_by_fit_id": records,
         "completed_metric_records": len(records), "failure": failure})
    if failure is None:
        emit(root, "GROUP_DIVERSITY_RESULTS.json", summary["part_a"])
        emit(root, "TEMPORAL_DENSITY_RESULTS.json", summary["part_b"])
        emit(root, "GROUP_WEIGHTING_RESULTS.json", summary["part_c"])
        emit(root, "ATTRIBUTION_SUMMARY.json", summary["attribution_summary"])
        emit(root, "RESULTS_TABLES.md", summary["narrative_bridge_markdown"])
    success = failure is None
    terminal = {"STUDY2_D": "PASS" if success else "BLOCKED_PARTIAL_EXECUTION",
        "STUDY2_D_METHOD": "CONTROLLED_DATA_CENTRIC_BRIDGE_ATTRIBUTION",
        "SCIENTIFIC_STUDY2D_RUNS": 1, "RF_MODEL": "RF_REFERENCE", "FEATURES": "LBP20_MULTIMODAL",
        "TRAIN_POSITIVE_GROUPS_AVAILABLE": 32, "TRAIN_BACKGROUND_GROUPS_AVAILABLE": 32,
        "CV_FOLDS": 4, "DISTINCT_RF_FITS": counts["fits_completed"],
        "DEV_GROUPS_READ": 0, "TEST_GROUPS_READ": 0, "DEV_ROWS_READ": 0, "TEST_ROWS_READ": 0,
        "TEST_CACHE_ROWS_READ": 0, "TEST_FEATURES_COMPUTED": 0, "EXPERIMENTAL_SOURCE_OPENS": 0,
        "FFMPEG_RUNS": 0, "TEST_STATE": "UNCHANGED_CONSUMED", "NEW_MODEL_SEARCH": False,
        "MODEL_SELECTION_REOPENED": False, "STUDY2_ATTRIBUTION_ANALYSIS_COMPLETE": success,
        "SCIENTIFIC_PROGRAM_READY_FOR_FINAL_CLOSEOUT": success, "STATE": "CLOSED_CONSUMED",
        "MERGE_AUTHORIZED": False, "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"}
    terminal.update({"ESM" + str(i) + "_OPENS": 0 for i in range(1, 7)})
    # Preserve measured counters even when a firewall failure closes the run.
    # Zero is only the initial value before the reader supplies its audit.
    for key in ("DEV_GROUPS_READ", "TEST_GROUPS_READ", "DEV_ROWS_READ", "TEST_ROWS_READ",
                "TEST_CACHE_ROWS_READ", "TEST_FEATURES_COMPUTED", "EXPERIMENTAL_SOURCE_OPENS",
                "FFMPEG_RUNS", *("ESM" + str(i) + "_OPENS" for i in range(1, 7))):
        terminal[key] = audit.get(key, 0)
    if success:
        terminal.update(summary["terminal_fields"])
    emit(root, "IO_AUDIT.json", audit)
    emit(root, "results.json", {"status": terminal["STUDY2_D"], "failure": failure,
        "last_fit_id": active_fit, "counts": counts, "terminal": terminal,
        "runtime_seconds": time.perf_counter() - start,
        "peak_python_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "peak_python_rss_scope": "Python parent process only, not system-wide peak memory",
        "method_freeze_sha": proof["head_sha"]})
    emit(root, "terminal-state.json", terminal)
    return terminal


def run(root):
    """Never overwrite a terminal or receipt, including on a second invocation."""
    consumed = safe_path(root, E + "/EXECUTION_RECEIPT.json").exists()
    try:
        return _execute(root)
    except Exception as exc:
        if not consumed and safe_path(root, E + "/EXECUTION_RECEIPT.json").exists() \
                and not safe_path(root, E + "/terminal-state.json").exists():
            emit(root, "terminal-state.json", {"STUDY2_D": "BLOCKED_POST_RECEIPT_FAILURE",
                "SCIENTIFIC_STUDY2D_RUNS": 1, "STATE": "CLOSED_CONSUMED",
                "failure": type(exc).__name__ + ": " + str(exc), "retry_authorized": False,
                "counter_scope": "Only completed durable fit records certify progress",
                "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"})
        raise
