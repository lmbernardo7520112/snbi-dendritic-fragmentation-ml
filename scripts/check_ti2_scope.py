"""Audit tracked code and dependency declarations against the TI-2 boundary.

Experimental bytes and ignored directories are never inspected. This static
guard supplements the frozen-pilot runtime checks; it is not a decoder or a
proof that arbitrary Python programs cannot perform prohibited operations.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import tomllib
from pathlib import Path, PurePosixPath

try:
    from check_repository_data import audit_entries, classify_path, tracked_entries
except ModuleNotFoundError:
    from scripts.check_repository_data import audit_entries, classify_path, tracked_entries

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_COMPONENTS = frozenset({
    "annotation", "annotations", "label", "labels", "ledger", "dataset", "datasets",
    "split", "splits", "baseline", "cnn", "model", "models", "training", "train",
    "evaluation", "evaluate", "sealed",
})
BLOCKED_IMPORTS = frozenset({
    "torch", "torchvision", "tensorflow", "keras", "sklearn", "xgboost",
    "lightgbm", "catboost", "transformers", "fastai",
})


def path_violations(relative: str) -> list[str]:
    if not relative.startswith(("src/", "scripts/")):
        return []
    components = {
        word
        for part in PurePosixPath(relative).parts
        for word in re.split(r"[_\-.]+", part.casefold())
    }
    blocked = sorted(components & BLOCKED_COMPONENTS)
    return [f"TI-3+ code path prohibited: {relative} ({','.join(blocked)})"] if blocked else []


def source_violations(source: str, relative: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [f"cannot parse tracked Python source: {relative}"]
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split('.')[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split('.')[0])
        elif isinstance(node, ast.Call) and node.args:
            function = node.func
            dynamic_import = (
                isinstance(function, ast.Name) and function.id == "__import__"
            ) or (
                isinstance(function, ast.Attribute) and function.attr == "import_module"
            )
            argument = node.args[0]
            if dynamic_import and isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                imports.add(argument.value.split('.')[0])
    return [f"ML import prohibited: {name} in {relative}" for name in sorted(imports & BLOCKED_IMPORTS)]


def read_source(relative: str) -> str:
    candidate = ROOT
    for component in PurePosixPath(relative).parts:
        candidate = candidate / component
        if candidate.is_symlink():
            raise ValueError("worktree symlink prohibited")
    return candidate.read_text(encoding="utf-8")


def audit(entries: list[tuple[str, str]] | None = None) -> dict:
    violations: list[str] = []
    try:
        inventory = tracked_entries() if entries is None else entries
        data_report = audit_entries(inventory)
        violations.extend(
            f"repository guard violation: {item['path']}" for item in data_report['violations']
        )
        # Reject the whole inventory before opening any code if a data violation exists.
        if not violations:
            for mode, relative in inventory:
                violations.extend(path_violations(relative))
                if classify_path(relative, mode) or not relative.startswith(("src/", "scripts/")):
                    continue
                if PurePosixPath(relative).suffix.casefold() != ".py":
                    continue
                violations.extend(source_violations(read_source(relative), relative))
            project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
            metadata = project.get("project", {})
            if metadata.get("dependencies", []) or any(metadata.get("optional-dependencies", {}).values()):
                violations.append("TI-2 core/CI dependency declarations must remain empty")
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError) as exc:
        violations.append(f"scope audit unavailable: {type(exc).__name__}")
    return {
        "authorized_phase": "TI-2",
        "blocked_phases": [f"TI-{phase}" for phase in range(3, 9)],
        "status": "PASS" if not violations else "BLOCKED",
        "violations": violations,
        "experimental_content_bytes_read": 0,
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
