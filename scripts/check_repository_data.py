"""Fail closed on tracked experimental data, binaries, and symlinks.

The audit reads Git index names only. It never opens experimental data.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PREFIXES = (
    "data/raw/",
    "data/interim/",
    "data/processed/",
    "data/derived/",
    "datasets/",
    "labels/",
    "splits/",
    "models/",
    "checkpoints/",
    "frames/",
    "runs/",
)
FORBIDDEN_SUFFIXES = frozenset({
    ".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v",
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp", ".dcm",
    ".npy", ".npz", ".h5", ".hdf5", ".zarr", ".parquet", ".feather",
    ".pkl", ".joblib", ".pt", ".pth", ".ckpt", ".onnx", ".safetensors",
    ".zip", ".7z", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".rar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".ipynb",
    ".bin", ".dat", ".mat", ".raw", ".sqlite", ".sqlite3", ".db",
})
TEXT_EVIDENCE_SUFFIXES = frozenset({".json", ".md", ".txt", ".sha256"})
TEXT_ARTIFACT_PREFIXES = ("artifacts/evidence/", "artifacts/metadata/")
ALLOWED_FILE_MODES = frozenset({"100644", "100755"})
SAFE_GIT_ENV = {
    "PATH": "/usr/bin:/bin:/snap/bin",
    "LANG": "C",
    "LC_ALL": "C",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "GIT_TERMINAL_PROMPT": "0",
}


def classify_path(path_text: str, mode: str = "100644") -> str | None:
    """Return a violation reason without accessing the referenced path."""
    normalized = path_text.replace("\\", "/")
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or ".." in path.parts:
        return "unsafe or non-relative path"
    if mode not in ALLOWED_FILE_MODES:
        return f"tracked non-regular entry is prohibited: mode {mode}"
    folded = normalized.casefold()
    filename = path.name.casefold()
    if filename == "agents.override.md":
        return "AGENTS override files are prohibited"
    if filename == "agents.md" and normalized != "AGENTS.md":
        return "nested or non-canonical AGENTS.md is prohibited"
    if any(
        folded == prefix.rstrip("/") or folded.startswith(prefix)
        for prefix in FORBIDDEN_PREFIXES
    ):
        return "tracked experimental-data path"
    forbidden_component_suffix = next(
        (
            PurePosixPath(component).suffix.casefold()
            for component in path.parts
            if PurePosixPath(component).suffix.casefold() in FORBIDDEN_SUFFIXES
        ),
        None,
    )
    if forbidden_component_suffix:
        return f"forbidden tracked suffix: {forbidden_component_suffix}"
    suffix = path.suffix.casefold()
    if folded.startswith("artifacts/"):
        if not any(folded.startswith(prefix) for prefix in TEXT_ARTIFACT_PREFIXES):
            return "artifact path is not allow-listed"
        if suffix not in TEXT_EVIDENCE_SUFFIXES:
            return "artifact is not an approved text evidence type"
    return None


def require_standalone_checkout(root: Path = ROOT) -> None:
    """Reject linked worktrees and external Git-directory indirection."""
    git_directory = root / ".git"
    if git_directory.is_symlink() or not git_directory.is_dir():
        raise ValueError("standalone in-root .git directory required")


def tracked_entries(root: Path = ROOT) -> list[tuple[str, str]]:
    require_standalone_checkout(root)
    identity = subprocess.run(
        ["git", "--no-optional-locks", "rev-parse", "--show-toplevel"],
        cwd=root, check=True, capture_output=True, text=True, env=SAFE_GIT_ENV,
        timeout=5,
    )
    if Path(identity.stdout.strip()).resolve() != root.resolve():
        raise ValueError("repository identity mismatch")
    completed = subprocess.run(
        ["git", "--no-optional-locks", "ls-files", "-s", "-z"],
        cwd=root, check=True, capture_output=True, env=SAFE_GIT_ENV, timeout=5,
    )
    entries: list[tuple[str, str]] = []
    for record in completed.stdout.decode("utf-8", errors="strict").split("\0"):
        if not record:
            continue
        metadata, path = record.split("\t", 1)
        mode = metadata.split(" ", 1)[0]
        entries.append((mode, path))
    return entries


def audit_entries(entries: list[tuple[str, str]]) -> dict:
    violations = []
    for mode, path in entries:
        reason = classify_path(path, mode)
        if reason:
            violations.append({"path": path, "mode": mode, "reason": reason})
    return {
        "audit": "tracked_repository_data_guard",
        "examined_entry_count": len(entries),
        "status": "PASS" if not violations else "BLOCKED",
        "violations": violations,
        "content_bytes_read": 0,
    }


def main() -> int:
    try:
        report = audit_entries(tracked_entries())
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError) as exc:
        report = {
            "audit": "tracked_repository_data_guard",
            "status": "BLOCKED",
            "violations": [{"reason": f"audit failure: {type(exc).__name__}"}],
            "content_bytes_read": 0,
        }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
