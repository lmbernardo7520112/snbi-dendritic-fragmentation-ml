"""Compose immutable TI2, frozen A0 and explicitly enumerated TI3 code scopes.

This is a textual custody and scope audit, never experimental authorization.
The Git baseline anchors legacy/A0 independently of the editable manifest.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
from collections import Counter
from pathlib import Path, PurePosixPath

try:
    import check_ti2_scope
    import check_ti3_scope
    from check_repository_data import SAFE_GIT_ENV, audit_entries, require_standalone_checkout
except ModuleNotFoundError:
    from scripts import check_ti2_scope, check_ti3_scope
    from scripts.check_repository_data import (
        SAFE_GIT_ENV, audit_entries, require_standalone_checkout,
    )


ROOT = Path(__file__).resolve().parents[1]
BASELINE_SHA = "41d523e038e844588ee7724e07b00f75bdf29fdc"
MANIFEST_PATH = "configs/governance/phase-scope-v1.json"
DOMAIN_NAMES = frozenset({"LEGACY_TI2", "TI3_A0_FROZEN", "TI3_ACTIVE"})
A0_PATHS = frozenset({
    "scripts/extract_ti3_a0_annotations.py",
    "scripts/inspect_ti3_a0_annotations.py",
    "src/snbi_fragmentation/ti3_a0_annotations.py",
    "tests/test_ti3_a0_annotations.py",
})


def is_relevant(path: str) -> bool:
    return path.startswith(("src/", "scripts/", "tests/")) and PurePosixPath(path).suffix.casefold() == ".py"


def git_blob_sha(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


def _safe_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return bool(parts) and not path.startswith("/") and "\\" not in path and all(
        part not in {"", ".", ".."} for part in path.split("/")
    )


def read_regular(root: Path, relative: str) -> tuple[bytes, str]:
    """Read a regular text candidate without following any in-root symlink."""
    if not _safe_path(relative):
        raise ValueError("unsafe relative path")
    parent_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        parts = PurePosixPath(relative).parts
        for component in parts[:-1]:
            next_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                              dir_fd=parent_fd)
            os.close(parent_fd)
            parent_fd = next_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                          dir_fd=parent_fd)
        try:
            metadata = os.fstat(file_fd)
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError("non-regular worktree entry")
            with os.fdopen(file_fd, "rb", closefd=False) as stream:
                content = stream.read()
            mode = "100755" if metadata.st_mode & 0o111 else "100644"
            return content, mode
        finally:
            os.close(file_fd)
    finally:
        os.close(parent_fd)


def _checkout_directory(path: Path) -> Path:
    """Validate one explicit Git identity directory without following symlinks.

    Component opens also protect relative gitdir paths containing ``..``.
    This checks directory identity only; it never lists or reads its contents.
    """
    absolute = path if path.is_absolute() else Path.cwd() / path
    directory_fd = os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in absolute.parts[1:]:
            next_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                              dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
    finally:
        os.close(directory_fd)
    # No component was a symlink; lexical normalization now equals resolution.
    return Path(os.path.abspath(absolute))


def _checkout_git_identity(root: Path, option: str) -> Path:
    """Run a raw identity query, avoiding recursion through guarded ``_git``."""
    completed = subprocess.run(
        ["git", "--no-optional-locks", "rev-parse", option], cwd=root,
        env=SAFE_GIT_ENV, check=True, capture_output=True, text=True, timeout=5,
    )
    value = completed.stdout.removesuffix("\n")
    if not value or any(character in value for character in ("\n", "\r", "\0")):
        raise ValueError("malformed Git directory identity")
    path = Path(value)
    return _checkout_directory(path if path.is_absolute() else root / path)


def require_supported_checkout(root: Path = ROOT) -> str:
    """Accept standalone or authenticated standard linked-worktree identity.

    This operational identity check grants no scientific or data-path authority.
    The immutable standalone data checker retains its original contract.
    """
    root = Path(root)
    git_entry = root / ".git"
    metadata = git_entry.lstat()
    if stat.S_ISLNK(metadata.st_mode):
        raise ValueError(".git symlink is prohibited")
    if stat.S_ISDIR(metadata.st_mode):
        require_standalone_checkout(root)
        return "STANDALONE"
    if not stat.S_ISREG(metadata.st_mode) or not 0 < metadata.st_size <= 4096:
        raise ValueError("bounded regular linked-worktree gitfile required")
    root = _checkout_directory(root)
    descriptor = os.open(root / ".git", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        opened = os.fstat(descriptor)
        if (not stat.S_ISREG(opened.st_mode) or not 0 < opened.st_size <= 4096
                or (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino)):
            raise ValueError("linked-worktree gitfile identity changed")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            content = stream.read(4097)
        if len(content) != opened.st_size or len(content) > 4096:
            raise ValueError("linked-worktree gitfile extent changed")
    finally:
        os.close(descriptor)
    match = re.fullmatch(r"gitdir: ([^\x00\r\n]+)\n?", content.decode("utf-8", errors="strict"))
    if match is None or match[1] != match[1].strip():
        raise ValueError("malformed linked-worktree gitfile")
    target = Path(match[1])
    git_directory = _checkout_directory(target if target.is_absolute() else root / target)
    if git_directory.parent.name != "worktrees":
        raise ValueError("linked gitdir must have common/worktrees/name layout")
    expected_common = _checkout_directory(git_directory.parent.parent)
    top_level = _checkout_git_identity(root, "--show-toplevel")
    reported_git = _checkout_git_identity(root, "--git-dir")
    common_directory = _checkout_git_identity(root, "--git-common-dir")
    if top_level != root:
        raise ValueError("linked-worktree top-level identity mismatch")
    if reported_git != git_directory or not reported_git.samefile(git_directory):
        raise ValueError("linked-worktree git-dir differs from gitfile")
    if common_directory != expected_common or not common_directory.samefile(expected_common):
        raise ValueError("linked-worktree common-dir layout mismatch")
    return "LINKED_WORKTREE"


def _git(root: Path, arguments: list[str]) -> bytes:
    require_supported_checkout(root)
    return subprocess.run(
        ["git", "--no-optional-locks", *arguments], cwd=root,
        env=SAFE_GIT_ENV, check=True, capture_output=True, timeout=15,
    ).stdout


def read_index_inventory(root: Path) -> list[dict]:
    records = []
    for record in _git(root, ["ls-files", "--stage", "-z"]).decode("utf-8").split("\0"):
        if not record:
            continue
        metadata, path = record.split("\t", 1)
        mode, blob_sha, stage = metadata.split(" ")
        records.append({"path": path, "git_mode": mode, "blob_sha": blob_sha,
                        "stage": stage})
    return records


def read_baseline_inventory(root: Path) -> list[dict]:
    records = []
    output = _git(root, ["ls-tree", "-r", "-z", BASELINE_SHA, "--", "src", "scripts", "tests"])
    for record in output.decode("utf-8").split("\0"):
        if not record:
            continue
        metadata, path = record.split("\t", 1)
        mode, object_type, blob_sha = metadata.split(" ")
        if is_relevant(path):
            if object_type != "blob" or mode not in {"100644", "100755"}:
                raise ValueError("baseline contains non-regular code")
            records.append({"path": path, "git_mode": mode, "blob_sha": blob_sha})
    return records


def _result(violations: list[str], **details) -> dict:
    return {"status": "BLOCKED" if violations else "PASS", "violations": violations, **details}


def audit_partition(manifest: dict, inventory: list[dict], baseline: list[dict]) -> dict:
    violations: list[str] = []
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        violations.append("unsupported scope schema")
    if manifest.get("baseline_sha") != BASELINE_SHA:
        violations.append("scope baseline does not match authorized Git commit")
    domains = manifest.get("domains")
    if not isinstance(domains, dict) or set(domains) != DOMAIN_NAMES:
        return _result([*violations, "exactly three authorized domains required"],
                       unclassified_paths=[], duplicate_classification_paths=[])
    paths: list[str] = []
    groups: dict[str, dict[str, dict]] = {}
    for domain in sorted(DOMAIN_NAMES):
        rows = domains[domain]
        groups[domain] = {}
        if not isinstance(rows, list):
            violations.append(f"domain is not an explicit entry list: {domain}")
            continue
        for row in rows:
            if not isinstance(row, dict):
                violations.append(f"invalid scope entry: {domain}")
                continue
            path = row.get("path")
            if not isinstance(path, str) or not _safe_path(path) or not is_relevant(path):
                violations.append(f"invalid relevant code path in {domain}")
                continue
            paths.append(path)
            groups[domain][path] = row
            if row.get("classification") != domain:
                violations.append(f"classification mismatch: {path}")
            if row.get("git_mode") not in {"100644", "100755"}:
                violations.append(f"invalid file mode: {path}")
            if not isinstance(row.get("blob_sha"), str) or not re.fullmatch(r"[0-9a-f]{40}", row["blob_sha"]):
                violations.append(f"invalid blob SHA: {path}")
            if domain == "TI3_A0_FROZEN" and (
                row.get("origin_phase") != "TI3_A0" or row.get("mutable") is not False
            ):
                violations.append(f"invalid frozen A0 declaration: {path}")
            if domain == "TI3_ACTIVE" and row.get("state") not in {"PLANNED", "TRACKED"}:
                violations.append(f"unknown active state: {path}")
    duplicates = sorted(path for path, count in Counter(paths).items() if count != 1)
    violations.extend(f"duplicate classification: {path}" for path in duplicates)
    relevant = {item["path"]: item for item in inventory if is_relevant(item["path"])}
    baseline_map = {item["path"]: item for item in baseline}
    if len(baseline_map) != len(baseline) or len(baseline_map) != 79:
        violations.append("authorized baseline enumeration must contain 79 unique code paths")
    if not A0_PATHS <= set(baseline_map):
        violations.append("authorized baseline is missing frozen A0 paths")
    expected_legacy = set(baseline_map) - A0_PATHS
    if set(groups["LEGACY_TI2"]) != expected_legacy:
        violations.append("legacy enumeration differs from baseline minus exact four A0 paths")
    if set(groups["TI3_A0_FROZEN"]) != A0_PATHS:
        violations.append("frozen A0 enumeration must be exactly the four authorized paths")
    for domain in ("LEGACY_TI2", "TI3_A0_FROZEN"):
        for path, row in groups[domain].items():
            anchor = baseline_map.get(path)
            if anchor is None or any(row.get(key) != anchor.get(key) for key in ("git_mode", "blob_sha")):
                violations.append(f"manifest diverges from immutable Git baseline: {path}")
    expected_tracked = set(groups["LEGACY_TI2"]) | set(groups["TI3_A0_FROZEN"])
    for path, row in groups["TI3_ACTIVE"].items():
        if row.get("state") == "TRACKED":
            expected_tracked.add(path)
        if row.get("state") == "PLANNED" and path in relevant:
            violations.append(f"PLANNED path already tracked: {path}")
        if row.get("state") == "TRACKED" and path not in relevant:
            violations.append(f"TRACKED active path absent: {path}")
    unclassified = sorted(set(relevant) - set(paths))
    missing = sorted(expected_tracked - set(relevant))
    violations.extend(f"unclassified tracked code: {path}" for path in unclassified)
    violations.extend(f"classified tracked code absent: {path}" for path in missing)
    for path in sorted(expected_tracked & set(relevant)):
        rows = [groups[domain][path] for domain in DOMAIN_NAMES if path in groups[domain]]
        if len(rows) == 1 and any(rows[0].get(key) != relevant[path].get(key)
                                 for key in ("git_mode", "blob_sha")):
            violations.append(f"tracked Git mode/blob differs from scope manifest: {path}")
    return _result(
        violations, unclassified_paths=unclassified, duplicate_classification_paths=duplicates,
        missing_paths=missing, relevant_tracked_count=len(relevant),
        legacy_file_count=len(groups["LEGACY_TI2"]),
        a0_frozen_file_count=len(groups["TI3_A0_FROZEN"]),
        active_tracked_count=sum(row.get("state") == "TRACKED" for row in groups["TI3_ACTIVE"].values()),
        active_planned_count=sum(row.get("state") == "PLANNED" for row in groups["TI3_ACTIVE"].values()),
    )


def audit_custody(root: Path, rows: list[dict]) -> dict:
    violations = []
    for row in rows:
        path = row["path"]
        try:
            content, mode = read_regular(root, path)
            content.decode("utf-8", errors="strict")
            if mode != row["git_mode"] or git_blob_sha(content) != row["blob_sha"]:
                violations.append(f"worktree mode/blob differs from frozen scope: {path}")
        except (OSError, ValueError, UnicodeError):
            violations.append(f"unavailable regular UTF-8 code: {path}")
    return _result(violations, examined_file_count=len(rows))


def audit_a0_declarations(manifest: dict, inventory: list[dict], baseline: list[dict]) -> dict:
    """Report an A0-specific block even when partition validation stops first."""
    domains = manifest.get("domains", {})
    rows = domains.get("TI3_A0_FROZEN") if isinstance(domains, dict) else None
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        return _result(["frozen A0 requires an explicit four-path declaration"])
    anchored = {row["path"]: row for row in baseline}
    indexed = {row["path"]: row for row in inventory}
    violations = []
    if len(rows) != 4 or {row.get("path") for row in rows} != A0_PATHS:
        return _result(["frozen A0 requires exactly the four authorized paths"])
    for domain in ("LEGACY_TI2", "TI3_ACTIVE"):
        other_rows = domains.get(domain, [])
        if isinstance(other_rows, list) and any(
            isinstance(row, dict) and row.get("path") in A0_PATHS for row in other_rows
        ):
            violations.append(f"frozen A0 also classified in {domain}")
    for row in rows:
        path = row["path"]
        if row.get("mutable") is not False or row.get("origin_phase") != "TI3_A0" or row.get("classification") != "TI3_A0_FROZEN":
            violations.append(f"frozen A0 declaration mismatch: {path}")
        for source in (anchored, indexed):
            if path not in source or any(source[path].get(key) != row.get(key)
                                        for key in ("git_mode", "blob_sha")):
                violations.append(f"frozen A0 baseline/index mismatch: {path}")
    return _result(violations, examined_file_count=0)


def audit_ti3_a0_frozen(root: Path, manifest: dict, inventory: list[dict], baseline: list[dict]) -> dict:
    declarations = audit_a0_declarations(manifest, inventory, baseline)
    if declarations["status"] != "PASS":
        return declarations
    return audit_custody(root, manifest["domains"]["TI3_A0_FROZEN"])


def audit(root: Path = ROOT) -> dict:
    report = {
        "audit": "composed_phase_scope", "status": "BLOCKED", "violations": [],
        "data_guard": {"status": "NOT_RUN"}, "partition": {"status": "NOT_RUN"},
        "legacy_scope": {"status": "NOT_RUN"}, "a0_frozen_scope": {"status": "NOT_RUN"},
        "ti3_scope": {"status": "NOT_RUN"}, "experimental_content_bytes_read": 0,
        "authorized_scientific_phases": [], "scientific_readiness": "BLOCKED",
        "ti2_execution_authorized": False, "ti3_plus_authorized": False,
        "merge_authorized": False,
    }
    try:
        inventory = read_index_inventory(root)
        entries = [(item["git_mode"], item["path"]) for item in inventory]
        report["data_guard"] = audit_entries(entries)
        if report["data_guard"]["status"] != "PASS":
            report["violations"].append("global tracked data guard blocked")
            return report
        if len({item["path"] for item in inventory}) != len(inventory) or any(
            item.get("stage") != "0" for item in inventory
        ):
            report["violations"].append("unmerged or duplicate Git index entry")
            return report
        content, _ = read_regular(root, MANIFEST_PATH)
        manifest = json.loads(content.decode("utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("scope manifest must be an object")
        baseline = read_baseline_inventory(root)
        report["partition"] = audit_partition(manifest, inventory, baseline)
        if report["partition"]["status"] != "PASS":
            a0_declarations = audit_a0_declarations(manifest, inventory, baseline)
            if a0_declarations["status"] != "PASS":
                report["a0_frozen_scope"] = a0_declarations
            report["violations"].extend(report["partition"]["violations"])
            return report
        legacy = manifest["domains"]["LEGACY_TI2"]
        legacy_custody = audit_custody(root, legacy)
        report["legacy_custody"] = legacy_custody
        if legacy_custody["status"] != "PASS":
            report["legacy_scope"] = legacy_custody
            report["violations"].extend(legacy_custody["violations"])
            return report
        report["legacy_scope"] = check_ti2_scope.audit(
            entries=[(row["git_mode"], row["path"]) for row in legacy],
        )
        if report["legacy_scope"]["status"] != "PASS":
            report["violations"].extend(report["legacy_scope"]["violations"])
            return report
        report["a0_frozen_scope"] = audit_ti3_a0_frozen(root, manifest, inventory, baseline)
        if report["a0_frozen_scope"]["status"] != "PASS":
            report["violations"].extend(report["a0_frozen_scope"]["violations"])
            return report
        active = [row for row in manifest["domains"]["TI3_ACTIVE"] if row["state"] == "TRACKED"]
        active_custody = audit_custody(root, active)
        report["active_custody"] = active_custody
        if active_custody["status"] != "PASS":
            report["ti3_scope"] = active_custody
            report["violations"].extend(active_custody["violations"])
            return report
        report["ti3_scope"] = check_ti3_scope.audit(
            entries=[(row["git_mode"], row["path"]) for row in active],
            root=root, manifest=manifest,
        )
        report["violations"].extend(report["ti3_scope"]["violations"])
        report["status"] = "PASS" if not report["violations"] else "BLOCKED"
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, subprocess.SubprocessError) as exc:
        report["violations"].append(f"phase scope audit unavailable: {type(exc).__name__}")
    return report


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
