"""Static TI3 import/dependency guard for the explicit active domain only.

This checker grants no experimental authority. It inspects text, never imports
the audited modules, and complements the compositor's blob/partition checks.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tomllib

try:
    from check_repository_data import audit_entries, classify_path
except ModuleNotFoundError:
    from scripts.check_repository_data import audit_entries, classify_path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = (
    "numpy==1.26.4", "scipy==1.11.4", "scikit-image==0.24.0",
    "scikit-learn==1.5.2",
)
ALLOWED_ML = frozenset({"numpy", "scipy", "skimage", "sklearn"})
BLOCKED_ML = frozenset({
    "torch", "torchvision", "tensorflow", "keras", "xgboost", "lightgbm",
    "catboost", "transformers", "fastai",
})


def read_text(root: Path, relative: str) -> str:
    if classify_path(relative):
        raise ValueError("unsafe text path")
    path = root
    for component in PurePosixPath(relative).parts:
        path = path / component
        if path.is_symlink():
            raise ValueError("symlink prohibited")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("regular text required")
        return stream.read().decode("utf-8")


def source_violations(source: str, relative: str, local_modules=()) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [f"cannot parse Python: {relative}"]
    imports = set()
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            dynamic = (
                isinstance(node.func, ast.Name) and node.func.id == "__import__"
            ) or (
                isinstance(node.func, ast.Attribute) and node.func.attr == "import_module"
            )
            if dynamic:
                if not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                    violations.append(f"unresolved dynamic import: {relative}")
                else:
                    imports.add(node.args[0].value.split(".")[0])
    allowed = set(sys.stdlib_module_names) | ALLOWED_ML | set(local_modules) | {"snbi_fragmentation", "scripts"}
    for name in sorted(imports):
        if name in BLOCKED_ML or name not in allowed:
            violations.append(f"unapproved import {name}: {relative}")
    return violations


def audit(*, entries, root=ROOT, manifest) -> dict:
    report = {"status": "BLOCKED", "violations": [], "examined_entry_count": len(entries), "experimental_content_bytes_read": 0}
    violations = report["violations"]
    try:
        data = audit_entries(entries)
        if data["status"] != "PASS":
            violations.append("active data guard failed")
            return report
        records = manifest["domains"]["TI3_ACTIVE"]
        expected = {item["path"]: item["git_mode"] for item in records if item["state"] == "TRACKED"}
        actual = {path: mode for mode, path in entries}
        if len(expected) != sum(item["state"] == "TRACKED" for item in records) or len(actual) != len(entries) or actual != expected:
            violations.append("active inventory differs from explicit TRACKED allowlist")
            return report
        local_modules = {PurePosixPath(item["path"]).stem for domain in manifest["domains"].values() for item in domain}
        for mode, relative in entries:
            if not relative.startswith(("src/", "scripts/", "tests/")) or PurePosixPath(relative).suffix != ".py":
                violations.append(f"active entry is not relevant Python: {relative}")
                continue
            violations.extend(source_violations(read_text(root, relative), relative, local_modules))
        requirements = read_text(root, "requirements-ti3-ml.txt").splitlines()
        if requirements != list(REQUIREMENTS):
            violations.append("TI3 requirements must contain exactly the four ordered frozen pins")
        project = tomllib.loads(read_text(root, "pyproject.toml")).get("project", {})
        if project.get("dependencies", []) or any(project.get("optional-dependencies", {}).values()):
            violations.append("legacy project dependencies must remain empty")
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        violations.append(f"TI3 text audit unavailable: {type(exc).__name__}")
    report["status"] = "PASS" if not violations else "BLOCKED"
    return report


def main() -> int:
    # The global compositor supplies the authenticated exhaustive inventory.
    try:
        import check_phase_scope
    except ModuleNotFoundError:
        from scripts import check_phase_scope
    report = check_phase_scope.audit(root=ROOT)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
