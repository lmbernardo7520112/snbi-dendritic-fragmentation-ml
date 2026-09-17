"""Validate static local safeguards and current TI-2 authority without data access."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import json
import subprocess
import tomllib
from pathlib import Path

try:
    from check_repository_data import audit_entries, tracked_entries
except ModuleNotFoundError:  # imported as scripts.check_local_bootstrap in tests
    from scripts.check_repository_data import audit_entries, tracked_entries

ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION = ROOT / "docs/decisions/AUTHORIZATION-LB0-SDR2A-CLOSURE-PR5-MERGE-TI2-EXECUTION-2026-09-17.md"
REQUIRED_AGENT_MARKERS = (
    "TI2_EXECUTION_AUTHORIZED=true",
    "AUTHORIZED_ACTIVITY=TI2_REGISTRATION_CALIBRATION",
    "Do not follow symlinks",
    "no fallback outside the sandbox",
)
FORBIDDEN_TASK_TOKENS = (
    "runOn", "sudo", "apt", "pip", "ffmpeg", "ffprobe", "curl", "wget",
    "git push", "git merge", "git commit", "${input:",
)
EXPECTED_SETTINGS = {
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.terminal.activateEnvironment": False,
    "terminal.integrated.cwd": "${workspaceFolder}",
    "git.autofetch": False,
    "git.confirmSync": True,
    "git.enableSmartCommit": False,
    "git.allowForcePush": False,
    "files.watcherExclude": {
        "**/data/raw/**": True,
        "**/data/interim/**": True,
        "**/data/processed/**": True,
        "**/data/derived/**": True,
        "**/datasets/**": True,
        "**/labels/**": True,
        "**/splits/**": True,
        "**/models/**": True,
        "**/checkpoints/**": True,
        "**/frames/**": True,
        "**/runs/**": True,
    },
    "search.exclude": {
        "**/data/raw/**": True,
        "**/data/interim/**": True,
        "**/data/processed/**": True,
        "**/data/derived/**": True,
        "**/datasets/**": True,
        "**/labels/**": True,
        "**/splits/**": True,
        "**/models/**": True,
        "**/checkpoints/**": True,
        "**/frames/**": True,
        "**/runs/**": True,
    },
}
EXPECTED_TASKS = {
    "SNBI: repository data guard": {
        "label": "SNBI: repository data guard",
        "type": "process",
        "command": "/usr/bin/python3",
        "args": ["-B", "scripts/check_repository_data.py"],
        "options": {"cwd": "${workspaceFolder}"},
        "problemMatcher": [],
    },
    "SNBI: local environment diagnostics (read-only)": {
        "label": "SNBI: local environment diagnostics (read-only)",
        "type": "process",
        "command": "/usr/bin/python3",
        "args": ["-B", "scripts/check_local_environment.py"],
        "options": {"cwd": "${workspaceFolder}"},
        "problemMatcher": [],
    },
    "SNBI: bootstrap policy tests": {
        "label": "SNBI: bootstrap policy tests",
        "type": "process",
        "command": "/usr/bin/python3",
        "args": [
            "-B", "-m", "unittest", "-v",
            "tests/test_repository_data_guard.py",
            "tests/test_local_bootstrap.py",
            "tests/test_local_environment.py",
        ],
        "options": {
            "cwd": "${workspaceFolder}",
            "env": {"PYTHONPATH": "${workspaceFolder}/src"},
        },
        "problemMatcher": [],
    },
}


def validate_vscode(settings: dict, tasks: dict) -> list[str]:
    """Validate the exact editor allowlist without executing any task."""
    violations: list[str] = []
    if settings != EXPECTED_SETTINGS:
        violations.append("VS Code settings differ from the exact allowlist")
    expected_document = {
        "version": "2.0.0",
        "tasks": list(EXPECTED_TASKS.values()),
    }
    if tasks != expected_document:
        violations.append("VS Code task document differs from the exact allowlist")
    for directory in ("raw", "interim", "processed", "derived"):
        pattern = f"**/data/{directory}/**"
        if not settings.get("files.watcherExclude", {}).get(pattern):
            violations.append(f"watcher exclusion missing: {pattern}")
        if not settings.get("search.exclude", {}).get(pattern):
            violations.append(f"search exclusion missing: {pattern}")

    rendered_tasks = json.dumps(tasks)
    for token in FORBIDDEN_TASK_TOKENS:
        if token.casefold() in rendered_tasks.casefold():
            violations.append(f"forbidden VS Code task token: {token}")
    task_list = tasks.get("tasks", [])
    labels = {task.get("label") for task in task_list}
    if labels != set(EXPECTED_TASKS) or len(task_list) != len(EXPECTED_TASKS):
        violations.append("VS Code task allowlist mismatch")
    for task in task_list:
        label = task.get("label")
        if task.get("type") != "process":
            violations.append(f"task is not process type: {label}")
        if task.get("options", {}).get("cwd") != "${workspaceFolder}":
            violations.append(f"task cwd is not workspace root: {label}")
        if "runOptions" in task or "dependsOn" in task:
            violations.append(f"automatic or chained task is prohibited: {label}")
        expected = EXPECTED_TASKS.get(label)
        if expected and task != expected:
            violations.append(f"VS Code task differs from exact allowlist: {label}")
    return violations


def read_authorization() -> str:
    return AUTHORIZATION.read_text(encoding="utf-8")


def validate(entries: list[tuple[str, str]] | None = None) -> dict:
    violations: list[str] = []
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for marker in REQUIRED_AGENT_MARKERS:
        if marker not in agents:
            violations.append(f"AGENTS.md missing marker: {marker}")

    authorization = read_authorization()
    for marker in (
        "Decision status: APPROVED",
        "LB0_LOCAL_ACCEPTANCE: PASS",
        "SDR2A_STATUS: RESOLVED",
        "REAL_CODEX_SANDBOX: PASS_SMOKE",
        "authorized complete execution of TI2-E0 through TI2-E7",
        "only the 30 frozen lossless pilot images",
        "TI-3 through TI-8",
    ):
        if marker not in authorization:
            violations.append(f"authorization record missing marker: {marker}")

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    governance = project.get("tool", {}).get("snbi", {})
    if governance.get("authorized_activity") != "ti2-registration-calibration":
        violations.append("pyproject authorized activity mismatch")
    if governance.get("ti2_execution_authorized") is not True:
        violations.append("pyproject must record the approved TI-2 execution authority")
    if governance.get("blocked_phases") != [f"TI-{phase}" for phase in range(3, 9)]:
        violations.append("TI-3 through TI-8 must remain blocked")
    if governance.get("pilot_image_limit") != 30:
        violations.append("pilot image limit must remain exactly 30")
    if governance.get("authorized_branch") != "feat/ti2-registration-calibration":
        violations.append("dedicated TI-2 branch authorization mismatch")
    if governance.get("write_boundary") != "repository-only-default-sandbox":
        violations.append("repository-only default-sandbox write boundary mismatch")

    settings = json.loads((ROOT / ".vscode/settings.json").read_text(encoding="utf-8"))
    tasks = json.loads((ROOT / ".vscode/tasks.json").read_text(encoding="utf-8"))
    violations.extend(validate_vscode(settings, tasks))

    data_report = audit_entries(tracked_entries() if entries is None else entries)
    if data_report["status"] != "PASS":
        violations.extend(
            f"tracked-data violation: {item['path']}" for item in data_report["violations"]
        )
    return {
        "audit": "governed_local_bootstrap",
        "status": "PASS" if not violations else "BLOCKED",
        "violations": violations,
        "ti2_execution_authorized": not violations,
        "codex_write_readiness": (
            "AUTHORIZED_DEFAULT_SANDBOX_REPOSITORY_ONLY" if not violations else "BLOCKED"
        ),
        "readiness_basis": "author decision and static safeguards; not a runtime sandbox probe",
    }


def main() -> int:
    try:
        report = validate()
    except (
        OSError,
        subprocess.SubprocessError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        report = {
            "audit": "governed_local_bootstrap", "status": "BLOCKED",
            "violations": [f"validation failure: {type(exc).__name__}"],
            "ti2_execution_authorized": False,
            "codex_write_readiness": "BLOCKED",
        }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
