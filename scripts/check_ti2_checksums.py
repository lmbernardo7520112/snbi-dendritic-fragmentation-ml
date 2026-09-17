"""Verify exact bytes of tracked textual TI-2 evidence, without experimental IO."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

try:
    from scripts.check_repository_data import classify_path, tracked_entries
except ModuleNotFoundError:
    from check_repository_data import classify_path, tracked_entries


ROOT = Path(__file__).absolute().parents[1]
MANIFEST = "artifacts/evidence/TI2/checksums.sha256"
HISTORICAL_CHECKSUM_COUNT = 70
TEXT_SUFFIXES = frozenset({".py", ".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".sha256"})
TEXT_NAMES = frozenset({"Makefile", ".gitignore", ".gitattributes", ".editorconfig"})
FORBIDDEN_COMPONENTS = frozenset({
    "data", "dataset", "datasets", "models", "model", "checkpoints", "frames",
    "images", "videos", "raw", ".git", ".codex", ".agents", ".env",
    "credentials", "tokens", "cookies", "secrets",
})
LINE = re.compile(r"([0-9a-fA-F]{64})  (.+)")


class ChecksumError(ValueError):
    """A checksum input cannot be safely or consistently verified."""


def path_violation(relative: str) -> str | None:
    """Reject unsafe/nontextual paths lexically, before filesystem inspection."""
    if not isinstance(relative, str) or not relative:
        return "empty or non-string path"
    if any(ord(character) < 32 or ord(character) == 127 for character in relative):
        return "control character in path"
    if "\\" in relative or ":" in relative:
        return "non-POSIX or drive-qualified path"
    parts = relative.split("/")
    if relative.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        return "path must be canonical and repository-relative without dot segments"
    if any(part.casefold() in FORBIDDEN_COMPONENTS for part in parts):
        return "experimental or private path prohibited"
    reason = classify_path(relative)
    if reason:
        return reason
    path = PurePosixPath(relative)
    if path.suffix.casefold() not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
        return "path is not an approved textual file type"
    return None


def _read_regular_file(root: Path, relative: str) -> bytes:
    """Walk only below root using non-following directory descriptors.

    Every component is checked before opening it; O_NOFOLLOW also closes a
    symlink replacement race. The final descriptor must still be regular.
    Nonblocking opens prevent a race replacing a regular file with a FIFO
    from hanging this verifier. No Path.resolve() can escape through a link.
    """
    reason = path_violation(relative)
    if reason:
        raise ChecksumError(reason)
    if not root.is_absolute() or not stat.S_ISDIR(root.lstat().st_mode):
        raise ChecksumError("root must be an absolute non-symlink directory")
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        parts = relative.split("/")
        for component in parts[:-1]:
            metadata = os.stat(component, dir_fd=descriptor, follow_symlinks=False)
            if not stat.S_ISDIR(metadata.st_mode):
                raise ChecksumError("non-directory or symlink path component")
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        metadata = os.stat(parts[-1], dir_fd=descriptor, follow_symlinks=False)
        if not stat.S_ISREG(metadata.st_mode):
            raise ChecksumError("non-regular or symlink file")
        file_descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                                  dir_fd=descriptor)
        try:
            if not stat.S_ISREG(os.fstat(file_descriptor).st_mode):
                raise ChecksumError("opened descriptor is not a regular file")
            chunks = []
            while chunk := os.read(file_descriptor, 65536):
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(file_descriptor)
    finally:
        os.close(descriptor)


def verify(root: Path = ROOT, *, entries: list[tuple[str, str]] | None = None) -> dict:
    """Return deterministic counts and violations; supplied entries are test fixtures.

    The command-line entry point always obtains its names/modes from Git.
    There is deliberately no CLI override for untracked files or allowed paths.
    All manifest members pass lexical/index checks before any member is opened.
    """
    report = {
        "audit": "ti2_textual_checksums", "manifest": MANIFEST,
        "historical_checksum_count": HISTORICAL_CHECKSUM_COUNT,
        "listed_count": 0, "unique_count": 0, "verified_count": 0,
        "violations": [], "status": "BLOCKED",
    }
    violations = report["violations"]
    try:
        index_entries = tracked_entries(root) if entries is None else entries
        tracked = {}
        for mode, path in index_entries:
            if path in tracked:
                raise ChecksumError("duplicate or unmerged Git index path")
            tracked[path] = mode
        if tracked.get(MANIFEST) not in {"100644", "100755"}:
            raise ChecksumError("checksum manifest must be a tracked regular file")
        text = _read_regular_file(root, MANIFEST).decode("utf-8", errors="strict")
        members = []
        seen = set()
        for line_number, line in enumerate(text.splitlines(), 1):
            if not line or line.startswith("#"):
                continue
            report["listed_count"] += 1
            match = LINE.fullmatch(line)
            if not match:
                violations.append({"line": line_number, "reason": "malformed SHA-256 entry"})
                continue
            digest, relative = match.groups()
            reason = path_violation(relative)
            if relative in seen:
                violations.append({"line": line_number, "reason": "duplicate path"})
            seen.add(relative)
            if relative == MANIFEST:
                reason = "checksum manifest must not include itself"
            elif relative not in tracked:
                reason = reason or "path is not tracked"
            elif tracked[relative] not in {"100644", "100755"}:
                reason = reason or "tracked entry is not a regular file"
            if reason:
                # Do not echo malicious input, private paths or control characters.
                violations.append({"line": line_number, "reason": reason})
            members.append((line_number, digest.lower(), relative))
        report["unique_count"] = len(seen)
        if not report["listed_count"]:
            violations.append({"reason": "empty checksum manifest"})
        if violations:
            return report
        for line_number, digest, relative in members:
            try:
                actual = hashlib.sha256(_read_regular_file(root, relative)).hexdigest()
                if actual != digest:
                    violations.append({"line": line_number, "reason": "SHA-256 mismatch"})
                else:
                    report["verified_count"] += 1
            except (OSError, ChecksumError) as exc:
                violations.append({"line": line_number,
                                   "reason": f"safe file read rejected: {type(exc).__name__}"})
        if report["verified_count"] != report["unique_count"]:
            violations.append({"reason": "verified count differs from unique entry count"})
        if not violations and report["listed_count"] == report["unique_count"]:
            report["status"] = "PASS"
    except (OSError, UnicodeError, ValueError, subprocess.SubprocessError) as exc:
        violations.append({"reason": f"verification failure: {type(exc).__name__}"})
    return report


def main() -> int:
    report = verify()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
