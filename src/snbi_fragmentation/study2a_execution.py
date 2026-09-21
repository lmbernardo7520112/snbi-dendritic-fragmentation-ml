"""One-use Study2A orchestration; no source access on import or preflight.

The old A0 kernel remains immutable. The new authorization controls only this
runner, and exclusive receipts consume each bounded invocation before I/O.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path, PurePosixPath
import resource
import shutil
import stat
import subprocess


BASE = "f36e43407f0e630d84f5e2d9306699b796b5ad2a"
BRANCH = "feat/study2a-dense-annotation-ledger"
EVIDENCE = "artifacts/evidence/STUDY2_A_ANNOTATION_MINING"
AUTHORITY = "configs/authority/study2a.json"
A0 = "src/snbi_fragmentation/ti3_a0_annotations.py"
A0_SHA = "89e4dd58cab51bcd4ed2c607e2abc14d11a2f44f5c5e827fa4e58917539619e7"
DETECTOR = {"chroma_distance": 20, "minimum_component_pixels": 32,
            "minimum_radius": 8.0, "maximum_radius": 16.0,
            "maximum_axis_ratio": 1.2, "maximum_radial_p95": 4.0,
            "minimum_angular_coverage": 0.9}
SOURCE_INFO = {
    "ESM3": {"width": 1280, "height": 1024, "frames": 294,
             "acquisition": "bottom_up_anti_parallel",
             "sha256": "d76a6466e50480a2116bc545a0ee2b8095cc14c54f861ecebee87de5b64e35be"},
    "ESM6": {"width": 1280, "height": 1012, "frames": 395,
             "acquisition": "top_down_parallel",
             "sha256": "5b8747758afde34fb626f3c4ffbd0b49ba6ca6f6b49bfa81b8cf9ee8459280ea"},
}
LEGACY_PATHS = (
    "artifacts/evidence/TI3_A0/extraction-method.json",
    "artifacts/evidence/TI3_A0/extraction-results.json",
    "artifacts/evidence/TI3_A0/development-manifest.json",
    "artifacts/evidence/TI3_TARGET_RESOLUTION/SITE_DEDUPLICATION.json",
)
CORE_PATHS = (
    "src/snbi_fragmentation/study2a_tracking.py",
    "src/snbi_fragmentation/study2a_streaming.py",
    "src/snbi_fragmentation/study2a_execution.py", "scripts/run_study2a.py",
)
REQUIRED_JOBS = frozenset({
    "deterministic-contracts", "scientific-synthetic-contracts",
    "ti3-synthetic-contracts", "ti3b-synthetic-contracts",
    "ti3c-synthetic-contracts", "ti3d-final-synthetic-contracts",
    "study2a-synthetic-contracts",
})
MAX_METADATA = 268435456
MIN_FREE = 53687091200


class Study2Error(ValueError):
    """A failed contract cannot arm scientific source access."""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def exact(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def safe_path(root, relative):
    parts = PurePosixPath(relative).parts
    if not parts or relative.startswith("/") or any(p in {"", ".", ".."} for p in relative.split("/")) or "\\" in relative:
        raise Study2Error("unsafe relative path")
    current = Path(root)
    if current.is_symlink():
        raise Study2Error("root symlink")
    for part in parts:
        current /= part
        if current.is_symlink():
            raise Study2Error("symlink prohibited")
    return current


def text_bytes(root, relative):
    # Experimental/local aggregate paths are never accepted by this reader.
    if not relative.startswith(("src/", "scripts/", "tests/", "configs/", "artifacts/evidence/", ".github/")):
        raise Study2Error("text path outside allowlist")
    if PurePosixPath(relative).suffix not in {".py", ".json", ".md", ".txt", ".sha256", ".yml"}:
        raise Study2Error("not an allowed textual suffix")
    p = safe_path(root, relative)
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise Study2Error("text input must be regular")
        result = f.read()
    result.decode("utf-8", errors="strict")
    return result


def load_json(root, relative):
    return json.loads(text_bytes(root, relative))


def exclusive_json(root, relative, value):
    p = safe_path(root, relative)
    content = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    if len(content) > MAX_METADATA:
        raise Study2Error("metadata file exceeds declared budget")
    if shutil.disk_usage(root).free - len(content) < MIN_FREE:
        raise Study2Error("metadata write would consume reserved disk space")
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    directory = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return {"path": relative, "size_bytes": len(content), "sha256": digest(content)}


def write_jsonl(root, relative, rows, remaining_budget):
    if relative not in {"data/derived/study2/OBSERVATION_LEDGER.jsonl", "data/derived/study2/candidate-components.jsonl"}:
        raise Study2Error("unknown local ledger output")
    p = safe_path(root, relative)
    p.parent.mkdir(parents=True, exist_ok=True)
    hasher, total, count = hashlib.sha256(), 0, 0
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as f:
        for row in rows:
            content = (json.dumps(row, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()
            if total + len(content) > remaining_budget or shutil.disk_usage(root).free - len(content) < MIN_FREE:
                raise Study2Error("metadata/free-disk budget exceeded; partial file preserved")
            f.write(content)
            hasher.update(content)
            total += len(content)
            count += 1
        f.flush()
        os.fsync(f.fileno())
    return {"path": relative, "size_bytes": total, "sha256": hasher.hexdigest(),
            "record_count": count, "git_status": "LOCAL_IGNORED", "complete": True}


def git(root, *args):
    return git_bytes(root, *args).decode().strip()


def git_bytes(root, *args):
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=root,
                          check=True, capture_output=True, timeout=20).stdout


def check_ci(proof, head):
    if not isinstance(proof, dict) or proof.get("head_sha") != head:
        raise Study2Error("CI proof must match exact method-freeze HEAD")
    runs = proof.get("runs")
    if not isinstance(runs, list) or not runs:
        raise Study2Error("missing CI runs")
    jobs = []
    for run in runs:
        if run.get("headSha") != head or run.get("status") != "completed" or run.get("conclusion") != "success":
            raise Study2Error("CI run incomplete or unsuccessful")
        for job in run.get("jobs", []):
            if job.get("status") != "completed" or job.get("conclusion") != "success":
                raise Study2Error("CI job incomplete or unsuccessful")
            if not job.get("steps") or any(s.get("conclusion") != "success" for s in job["steps"]):
                raise Study2Error("CI steps must all be successful")
            jobs.append(job["name"])
    if len(jobs) != len(REQUIRED_JOBS) or set(jobs) != REQUIRED_JOBS:
        raise Study2Error("all seven exact historical/new CI jobs required")
    return sorted(jobs)


def preserved_baseline(root):
    prior = set(git(root, "ls-tree", "-r", "--name-only", BASE).splitlines())
    changed = set(git(root, "diff", "--name-only", BASE, "--").splitlines())
    if (changed & prior) - {"configs/governance/phase-scope-v1.json"}:
        raise Study2Error("Study1 tracked content changed")
    old_scope = json.loads(git(root, "show", BASE + ":configs/governance/phase-scope-v1.json"))
    new_scope = load_json(root, "configs/governance/phase-scope-v1.json")
    if old_scope["baseline_sha"] != new_scope.get("baseline_sha") or old_scope["schema_version"] != new_scope.get("schema_version"):
        raise Study2Error("operational scope baseline changed")
    if set(old_scope["domains"]) != set(new_scope.get("domains", {})):
        raise Study2Error("operational domains changed")
    for domain, rows in old_scope["domains"].items():
        current = {r["path"]: r for r in new_scope["domains"][domain]}
        if any(not exact(row, current.get(row["path"])) for row in rows):
            raise Study2Error("historical scope entry changed")
    return len(prior)


def preflight(root, mode):
    if mode not in {"legacy", "full"}:
        raise Study2Error("unknown phase")
    for terminal in ("terminal-state.json", "results.json"):
        if safe_path(root, EVIDENCE + "/" + terminal).exists():
            raise Study2Error("authority already closed")
    receipt = "LEGACY_RECEIPT.json" if mode == "legacy" else "EXECUTION_RECEIPT.json"
    if safe_path(root, EVIDENCE + "/" + receipt).exists():
        raise Study2Error("invocation already consumed; retry prohibited")
    if git(root, "branch", "--show-current") != BRANCH:
        raise Study2Error("wrong branch")
    cfg = load_json(root, AUTHORITY)
    if cfg.get("base_sha") != BASE or cfg.get("branch") != BRANCH or cfg.get("phase") != "STUDY2_A_ANNOTATION_MINING":
        raise Study2Error("authority identity mismatch")
    if not exact(cfg.get("detector"), DETECTOR) or not exact(cfg.get("persistence_tolerance_px"), 2.0):
        raise Study2Error("frozen scientific configuration diverged")
    fixed = {"sources": ["ESM3", "ESM6"], "expected_frames": {"ESM3": 294, "ESM6": 395},
             "scientific_runs_limit": 1, "human_review": False, "hough": False,
             "patches": False, "ml": False, "max_temp_bytes": 268435456,
             "max_patch_cache_bytes": 2147483648, "min_free_disk_reserve_bytes": MIN_FREE,
             "metadata_output_budget_bytes": MAX_METADATA,
             "legacy_center_absolute_tolerance_px": 1e-9,
             "new_frames_require_frozen_commit_and_green_ci": True, "terminal_closes_authority": True}
    if any(not exact(cfg.get(k), v) for k, v in fixed.items()):
        raise Study2Error("authority limits changed")
    if not exact(cfg.get("schema_version"), 1) or set(cfg) != set(fixed) | {
            "schema_version", "base_sha", "branch", "phase", "detector",
            "persistence_tolerance_px", "authority_sha256", "decoder_gate_authority_sha256"}:
        raise Study2Error("authority schema mismatch")
    if digest(text_bytes(root, EVIDENCE + "/AUTHORIZATION.md")) != cfg.get("authority_sha256"):
        raise Study2Error("author instruction custody mismatch")
    if digest(text_bytes(root, EVIDENCE + "/DECODER_GATE_AUTHORIZATION.md")) != cfg.get("decoder_gate_authority_sha256"):
        raise Study2Error("decoder exception custody mismatch")
    if digest(text_bytes(root, A0)) != A0_SHA:
        raise Study2Error("A0 detector changed")
    old_method = load_json(root, LEGACY_PATHS[0])
    if not exact(old_method["config"], DETECTOR) or not exact(old_method["persistence_tolerance_px"], 2.0):
        raise Study2Error("A0 historical method mismatch")
    for name, version in {"numpy": "1.26.4", "scipy": "1.11.4"}.items():
        if importlib.metadata.version(name) != version:
            raise Study2Error("scientific dependency version mismatch")
    if shutil.disk_usage(root).free < MIN_FREE + MAX_METADATA:
        raise Study2Error("insufficient free-space reserve")
    preserved = preserved_baseline(root)
    head = git(root, "rev-parse", "HEAD")
    report = {"status": "PASS", "mode": mode, "head_sha": head,
              "historical_tracked_paths_preserved": preserved,
              "experimental_source_opens": 0, "experimental_bytes": 0,
              "receipt_created": False, "free_disk_bytes": shutil.disk_usage(root).free}
    if mode == "legacy":
        if head != BASE:
            raise Study2Error("legacy gate must precede method-freeze commit")
    else:
        if git(root, "rev-parse", "HEAD^") != BASE:
            raise Study2Error("method freeze must be direct child of base")
        frozen_path = EVIDENCE + "/METHOD_FREEZE.json"
        frozen_bytes = text_bytes(root, frozen_path)
        if git_bytes(root, "show", head + ":" + frozen_path) != frozen_bytes:
            raise Study2Error("method-freeze record differs from Git")
        freeze = json.loads(frozen_bytes)
        hashes = freeze.get("files", {})
        required = set(CORE_PATHS) | set(LEGACY_PATHS) | {A0, AUTHORITY,
            EVIDENCE + "/PROTOCOL.md", EVIDENCE + "/LEGACY_REPRODUCTION.json",
            EVIDENCE + "/AUTHORIZATION.md", EVIDENCE + "/DECODER_GATE_AUTHORIZATION.md",
            EVIDENCE + "/SYNTHETIC_TESTS.json", "configs/governance/phase-scope-v1.json",
            ".github/workflows/study2a-synthetic.yml"}
        if not isinstance(hashes, dict) or not required <= set(hashes):
            raise Study2Error("incomplete method freeze")
        for path, expected in hashes.items():
            content = text_bytes(root, path)
            if digest(content) != expected:
                raise Study2Error("method-freeze hash mismatch: " + path)
            if git_bytes(root, "show", head + ":" + path) != content:
                raise Study2Error("frozen file differs from committed content: " + path)
        legacy = load_json(root, EVIDENCE + "/LEGACY_REPRODUCTION.json")
        if legacy.get("status") != "PASS" or legacy.get("processed_frames") != 10 or legacy.get("counts") != {"VALID": 108, "AMBIGUOUS": 380, "SMALL": 3}:
            raise Study2Error("historical reproduction not passed")
        for path, expected in legacy["implementation_hashes"].items():
            if digest(text_bytes(root, path)) != expected:
                raise Study2Error("implementation changed after historical gate")
        report["ci_jobs"] = check_ci(load_json(root, EVIDENCE + "/CI_PROOF.json"), head)
        report["frozen_text_count"] = len(hashes)
    return report


def detect(raw, source, temporal_evidence=False):
    import numpy as np
    from snbi_fragmentation.ti3_a0_annotations import extract_graphical_markers
    w, h = SOURCE_INFO[source]["width"], SOURCE_INFO[source]["height"]
    n = w * h
    if len(raw) != n * 3 // 2:
        raise Study2Error("native frame byte count mismatch")
    native = np.frombuffer(raw, dtype=np.uint8)
    u = native[n:n+n//4].reshape(h//2, w//2)
    v = native[n+n//4:].reshape(h//2, w//2)
    result = extract_graphical_markers(u, v, w, h, dict(DETECTOR))
    if temporal_evidence:
        from snbi_fragmentation.study2a_tracking import component_support_from_chroma
        result["_component_pixels"] = component_support_from_chroma(u, v, w, h, result)
    return result


def compare_legacy_frame(actual, expected, raw_sha, asset):
    if raw_sha != asset["image_sha256"]:
        raise Study2Error("legacy raw hash mismatch")
    fields = ("component_count", "valid_circle_count", "ambiguous_component_count",
              "small_component_count", "colored_pixel_count", "colored_chroma_sample_count")
    if any(actual[k] != expected[k] for k in fields):
        raise Study2Error("legacy component/count mismatch")
    if len(actual["components"]) != len(expected["components"]):
        raise Study2Error("legacy components missing")
    error = 0.0
    for a, b in zip(actual["components"], expected["components"]):
        for k in ("component_id", "classification", "bbox_xyxy", "area_px", "reasons"):
            if not exact(a[k], b[k]):
                raise Study2Error("legacy component identity/classification mismatch")
        if a["classification"] == "VALID_GRAPHICAL_CIRCLE":
            delta = math.dist(a["center_xy_px"], b["center_xy_px"])
            if not math.isfinite(delta) or delta > 1e-9:
                raise Study2Error("legacy VALID center mismatch")
            error = max(error, delta)
    return {"raw_sha256": raw_sha, "raw_hash_match": True,
            "VALID": actual["valid_circle_count"],
            "AMBIGUOUS": actual["ambiguous_component_count"],
            "SMALL": actual["small_component_count"],
            "maximum_valid_center_difference_px": error, "status": "PASS"}


def legacy_inputs(root):
    assets = load_json(root, LEGACY_PATHS[2])["assets"]
    frames = load_json(root, LEGACY_PATHS[1])["frames"]
    return ({(a["source_id"], a["frame_index"]): a for a in assets},
            {(f["source_id"], f["frame_index"]): f for f in frames})


def arm(root, mode, proof):
    name = "LEGACY_RECEIPT.json" if mode == "legacy" else "EXECUTION_RECEIPT.json"
    record = {"phase": "STUDY2_A", "mode": mode, "created_at_utc": utc_now(),
              "head_sha": proof["head_sha"], "attempt": 1,
              "authority_sha256": digest(text_bytes(root, AUTHORITY)),
              "sources": SOURCE_INFO, "preflight": proof}
    return exclusive_json(root, EVIDENCE + "/" + name, record)


def _run_legacy(root):
    from snbi_fragmentation.study2a_streaming import AuthenticatedSources
    proof = preflight(root, "legacy")
    assets, frames = legacy_inputs(root)
    arm(root, "legacy", proof)
    audit, rows = {}, []
    status, failure = "PASS", None
    try:
        with AuthenticatedSources(mode="legacy", audit=audit) as reader:
            for source in SOURCE_INFO:
                for index, raw, raw_sha in reader.iter_frames(source):
                    actual = detect(raw, source)
                    check = compare_legacy_frame(actual, frames[(source, index)], raw_sha, assets[(source, index)])
                    rows.append({"source_id": source, "frame_index": index, **check})
                    del raw, actual
        if len(rows) != 10:
            raise Study2Error("legacy gate requires ten exact emitted frames")
    except Exception as exc:
        status, failure = "BLOCKED_LEGACY_REPRODUCTION", f"{type(exc).__name__}: {exc}"
    result = {"status": status, "processed_frames": len(rows), "frames": rows,
              "counts": {key: sum(r[key] for r in rows) for key in ("VALID", "AMBIGUOUS", "SMALL")},
              "failure": failure, "scientific_full_sequence_runs": 0,
              "internal_decoder_intermediates": "AUTHORIZED_NOT_EXPOSED_TO_DETECTOR_OR_SAVED",
              "implementation_hashes": {p: digest(text_bytes(root, p)) for p in (*CORE_PATHS, A0, AUTHORITY)},
              "completed_at_utc": utc_now()}
    if result["counts"] != {"VALID": 108, "AMBIGUOUS": 380, "SMALL": 3}:
        result["status"] = "BLOCKED_LEGACY_REPRODUCTION"
    exclusive_json(root, EVIDENCE + "/LEGACY_IO_AUDIT.json", audit)
    exclusive_json(root, EVIDENCE + "/LEGACY_REPRODUCTION.json", result)
    if result["status"] != "PASS":
        exclusive_json(root, EVIDENCE + "/terminal-state.json", {
            "STUDY2_A": "BLOCKED_LEGACY_REPRODUCTION", "STATE": "CLOSED_BLOCKED",
            "SCIENTIFIC_STUDY2A_RUNS": 0, "STUDY2_B_AUTHORIZED": False,
            "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"})
    return result


def run_legacy(root):
    already_consumed = safe_path(root, EVIDENCE + "/LEGACY_RECEIPT.json").exists()
    try:
        return _run_legacy(root)
    except Exception as exc:
        if not already_consumed and safe_path(root, EVIDENCE + "/LEGACY_RECEIPT.json").exists():
            terminal = {"STUDY2_A": "BLOCKED_POST_RECEIPT_LEGACY_FAILURE",
                        "STATE": "CLOSED_BLOCKED", "SCIENTIFIC_STUDY2A_RUNS": 0,
                        "failure": f"{type(exc).__name__}: {exc}",
                        "partial_counters": "NOT_CERTIFIED_PRESERVE_ALL_AVAILABLE_OUTPUTS",
                        "STUDY2_B_AUTHORIZED": False,
                        "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"}
            path = EVIDENCE + "/terminal-state.json"
            if not safe_path(root, path).exists():
                exclusive_json(root, path, terminal)
            return terminal
        raise


def map_legacy_sites(legacy, links):
    # Implementation-normalized links supplied by the tracker adapter below.
    mapped, rows = [], []
    for old in legacy:
        ids, unresolved = set(), []
        for observation in old["observation_ids"]:
            link = links.get(observation)
            if link is None or link.get("state") != "DIRECT_VALID" or not link.get("site_id"):
                unresolved.append(observation)
            else:
                ids.add(link["site_id"])
        status = "MAPPED" if len(ids) == 1 and not unresolved else "UNMAPPED_CONFLICT_OR_MISSING"
        row = {"legacy_site_id": old["annotation_site_id"], "source_id": old["source_id"],
               "new_site_ids": sorted(ids), "unresolved_observation_ids": unresolved, "status": status}
        rows.append(row)
        if status == "MAPPED":
            mapped.append(old["annotation_site_id"])
    counts = Counter(r["new_site_ids"][0] for r in rows if r["status"] == "MAPPED")
    # Two prior sites cannot silently collapse to one new identity.
    for row in rows:
        if row["status"] == "MAPPED" and counts[row["new_site_ids"][0]] != 1:
            row["status"] = "UNMAPPED_NONINJECTIVE"
    n = sum(r["status"] == "MAPPED" for r in rows)
    return {"expected": len(legacy), "mapped": n, "unmapped": len(legacy)-n,
            "status": "PASS" if len(legacy) == 52 and n == 52 else "BLOCKED_LEGACY_SITE_MAPPING", "sites": rows}


def _run_full(root):
    from snbi_fragmentation.study2a_streaming import AuthenticatedSources
    from snbi_fragmentation.study2a_tracking import TemporalTracker
    proof = preflight(root, "full")
    assets, historical_frames = legacy_inputs(root)
    legacy = load_json(root, LEGACY_PATHS[3])
    trackers = {s: TemporalTracker(s, p["acquisition"], p["frames"])
                for s, p in SOURCE_INFO.items()}
    # Existing output cannot be overwritten or reused as an implicit second run.
    for relative in ("data/derived/study2/OBSERVATION_LEDGER.jsonl",
                     "data/derived/study2/candidate-components.jsonl"):
        if safe_path(root, relative).exists():
            raise Study2Error("aggregate output already exists")
    arm(root, "full", proof)
    audit, historical_checks, next_index = {}, [], dict.fromkeys(SOURCE_INFO, 0)
    failure = None
    try:
        with AuthenticatedSources(mode="full", audit=audit) as reader:
            for source in SOURCE_INFO:
                for index, raw, raw_sha in reader.iter_frames(source):
                    if index != next_index[source]:
                        raise Study2Error("noncontiguous decoder output")
                    actual = detect(raw, source, temporal_evidence=True)
                    if (source, index) in assets:
                        check = compare_legacy_frame(actual, historical_frames[(source, index)],
                                                     raw_sha, assets[(source, index)])
                        historical_checks.append({"source_id": source, "frame_index": index, **check})
                    trackers[source].add_frame(index, actual, raw_sha)
                    next_index[source] += 1
                    del raw, actual
        if any(next_index[s] != p["frames"] for s, p in SOURCE_INFO.items()):
            raise Study2Error("incomplete full-sequence coverage")
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    # Account for every expected index. INVALID_FRAME is never converted to absence.
    # Remaining frames were NOT decoded/attempted; the failure reason states this.
    for source, parameters in SOURCE_INFO.items():
        for index in range(next_index[source], parameters["frames"]):
            trackers[source].add_frame(index, None, None, frame_status="INTEGRITY_FAILED")
    outputs = [tracker.finish() for tracker in trackers.values()]
    for output in outputs:
        source = output["summary"]["source_id"]
        for frame in output["frames"]:
            frame["source_sha256"] = SOURCE_INFO[source]["sha256"]
            if frame["frame_processing_status"] != "PROCESSED":
                frame["failure_reason"] = "NOT_ADMITTED_AFTER_TERMINAL_PIPELINE_FAILURE"
                frame["pipeline_failure"] = failure
                frame["processed"] = False
                frame["decode_attempted"] = "NOT_CERTIFIED_SEE_DECODER_AUDIT"
    sites = [site for output in outputs for site in output["sites"]]
    for site in sites:
        site["source_sha256"] = SOURCE_INFO[site["source_id"]]["sha256"]
        site["detector_code_sha256"] = A0_SHA
    frames = [frame for output in outputs for frame in output["frames"]]
    links = {f'{row["source_id"]}:{row["frame_index"]}:graphic-component-{row["component_id"]:04d}': {"state": "DIRECT_VALID" if row["site_id"] else "CONFLICT",
                                  "site_id": row["site_id"]}
             for output in outputs for row in output["component_site_links"]}
    mapping = map_legacy_sites(legacy, links)
    mapped_ids = {row["new_site_ids"][0] for row in mapping["sites"] if row["status"] == "MAPPED"}
    for site in sites:
        site["mapped_legacy_site"] = site["site_id"] in mapped_ids
    summaries = [o["summary"] for o in outputs]
    numeric = ("frames_expected", "frames_accounted", "frames_processed", "unique_sites",
               "unique_auto_gold_sites", "direct_valid_observations", "valid_detector_components",
               "auto_silver_observations", "ambiguous_observations", "small_components",
               "site_frame_records", "pre_annotation_records", "persistence_expected_records",
               "conflict_records", "valid_identity_conflict_components", "invalid_frame_records",
               "unexpected_graphical_disappearance_count", "candidate_records",
               "overlap_with_known_tracks_components", "potential_new_site_unresolved_components")
    summary = {key: sum(s[key] for s in summaries) for key in numeric}
    summary.update({"by_source": summaries, "n_acquisitions": 2,
                    "new_sites_relative_to_mapped_legacy": sum(not s["mapped_legacy_site"] for s in sites),
                    "new_auto_gold_sites_relative_to_mapped_legacy": sum(not s["mapped_legacy_site"] and s["auto_gold_site"] for s in sites),
                    "track_direct_observation_count_distribution": dict(sorted(Counter(s["direct_observation_count"] for s in sites).items())),
                    "first_direct_frame_distribution_by_source": {
                        source: dict(sorted(Counter(s["first_direct_valid_frame"] for s in sites if s["source_id"] == source).items())) for source in SOURCE_INFO},
                    "transition_interval_status_distribution": dict(Counter(s["transition_interval"]["status"] for s in sites)),
                    "source_provenance_completeness": all(s["source_provenance_complete"] for s in sites),
                    "deterministic_id_completeness": len({s["site_id"] for s in sites}) == len(sites),
                    "temporal_delta_executed": False, "human_review_used": False,
                    "hough_executed": False, "ml_runs": 0, "patches_created": 0,
                    "physical_events_inferred": 0, "negative_labels_created": 0,
                    "scientific_study2a_runs": 1, "retry_count": 0,
                    "legacy_site_mapping": {k: v for k, v in mapping.items() if k != "sites"},
                    "failure": failure, "historical_frame_rechecks": historical_checks})
    status = "PASS"
    if failure or summary["frames_processed"] != 689:
        status = "BLOCKED_PARTIAL_EXECUTION"
    elif mapping["status"] != "PASS":
        status = "BLOCKED_LEGACY_SITE_MAPPING"
    elif not summary["source_provenance_completeness"] or not summary["deterministic_id_completeness"]:
        status = "BLOCKED_CORPUS_INTEGRITY"
    summary["status"] = status
    aggregate = []
    try:
        remaining = MAX_METADATA
        for kind, path in (("observations", "OBSERVATION_LEDGER.jsonl"),
                           ("candidate_components", "candidate-components.jsonl")):
            rows = (dict(row, source_sha256=SOURCE_INFO[row["source_id"]]["sha256"])
                    for out in outputs for row in out[kind])
            record = write_jsonl(root, "data/derived/study2/" + path, rows, remaining)
            remaining -= record["size_bytes"]
            aggregate.append(record)
        for name, value in (("FRAME_SUMMARY.json", frames), ("SITE_LEDGER.json", sites),
                            ("LEGACY_SITE_MAPPING.json", mapping), ("CORPUS_SUMMARY.json", summary),
                            ("LOCAL_ARTIFACT_MANIFEST.json", {"artifacts": aggregate})):
            exclusive_json(root, EVIDENCE + "/" + name, value)
    except Exception as exc:
        status = "BLOCKED_OUTPUT_PRESERVATION"
        summary["status"] = status
        summary["preservation_failure"] = f"{type(exc).__name__}: {exc}"
    local_bytes = sum(safe_path(root, "data/derived/study2/" + name).stat().st_size
                      for name in ("OBSERVATION_LEDGER.jsonl", "candidate-components.jsonl")
                      if safe_path(root, "data/derived/study2/" + name).exists())
    audit.update({"scientific_study2a_runs": 1, "detector_frames_processed": summary["frames_processed"],
                  "temporary_bytes": 0, "patch_cache_bytes": 0, "peak_cache_usage_bytes": 0,
                  "peak_cache_usage_scope": "DISK_PIXEL_FILES_AND_PATCH_CACHE_ONLY; sparse first-direct footprints and ledger metadata reside in Python memory",
                  "aggregate_ledger_bytes": local_bytes,
                  "aggregate_complete": len(aggregate) == 2,
                  "candidate_records": summary["candidate_records"],
                  "python_process_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  "decoder_peak_rss": "NOT_INSTRUMENTED", "free_disk_bytes": shutil.disk_usage(root).free,
                  "storage_budget_compliance": local_bytes <= MAX_METADATA and shutil.disk_usage(root).free >= MIN_FREE})
    if not audit["storage_budget_compliance"]:
        status = "BLOCKED_STORAGE_BUDGET"
        summary["status"] = status
    exclusive_json(root, EVIDENCE + "/IO_AUDIT.json", audit)
    exclusive_json(root, EVIDENCE + "/results.json", summary)
    terminal = {"STUDY2_A": status, "STUDY2_A_METHOD": "FULL_SEQUENCE_TEMPORAL_ANNOTATION_MINING",
                "STATE": "CLOSED_CONSUMED", "SCIENTIFIC_STUDY2A_RUNS": 1,
                "ANNOTATION_FRAMES_EXPECTED": 689, "ANNOTATION_FRAMES_PROCESSED": summary["frames_processed"],
                "UNIQUE_AUTO_GOLD_SITES": summary["unique_auto_gold_sites"],
                "DIRECT_VALID_OBSERVATIONS": summary["direct_valid_observations"],
                "AUTO_SILVER_OBSERVATIONS": summary["auto_silver_observations"],
                "AMBIGUOUS_OBSERVATIONS": summary["ambiguous_observations"],
                "CONFLICT_RECORDS": summary["conflict_records"], "LEGACY_SITES_EXPECTED": 52,
                "LEGACY_SITES_MAPPED": mapping["mapped"], "HUMAN_REVIEW_USED": False,
                "HOUGH_EXECUTED": False, "ESM1_OPENS": 0, "ESM2_OPENS": 0,
                "ESM4_OPENS": 0, "ESM5_OPENS": 0, "PATCHES_CREATED": 0, "ML_RUNS": 0,
                "STUDY2_B_READY_FOR_AUTHOR_DECISION": status == "PASS", "STUDY2_B_AUTHORIZED": False,
                "MERGE_AUTHORIZED": False, "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"}
    exclusive_json(root, EVIDENCE + "/terminal-state.json", terminal)
    return terminal


def run_full(root):
    already_consumed = safe_path(root, EVIDENCE + "/EXECUTION_RECEIPT.json").exists()
    try:
        return _run_full(root)
    except Exception as exc:
        if not already_consumed and safe_path(root, EVIDENCE + "/EXECUTION_RECEIPT.json").exists():
            terminal = {"STUDY2_A": "BLOCKED_POST_RECEIPT_FAILURE",
                        "STATE": "CLOSED_CONSUMED", "SCIENTIFIC_STUDY2A_RUNS": 1,
                        "failure": f"{type(exc).__name__}: {exc}",
                        "partial_counters": "NOT_CERTIFIED_PRESERVE_ALL_AVAILABLE_OUTPUTS",
                        "STUDY2_B_AUTHORIZED": False,
                        "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION"}
            path = EVIDENCE + "/terminal-state.json"
            if not safe_path(root, path).exists():
                exclusive_json(root, path, terminal)
            return terminal
        raise
