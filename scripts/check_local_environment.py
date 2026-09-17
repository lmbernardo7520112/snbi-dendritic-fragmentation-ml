"""Sanitized, read-only diagnostics for the local Codex environment."""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC_KEYS = {
    "unprivileged_userns_clone": Path("/proc/sys/kernel/unprivileged_userns_clone"),
    "max_user_namespaces": Path("/proc/sys/user/max_user_namespaces"),
    "apparmor_restrict_unprivileged_userns": Path(
        "/proc/sys/kernel/apparmor_restrict_unprivileged_userns"
    ),
}
VERSION_COMMANDS = {
    "git": ["git", "--version"],
    "bwrap": ["bwrap", "--version"],
    "unshare": ["unshare", "--version"],
    "code": ["code", "--version"],
}
SAFE_ENV = {
    "PATH": "/usr/bin:/bin:/snap/bin",
    "LANG": "C",
    "LC_ALL": "C",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "GIT_TERMINAL_PROMPT": "0",
}
VERSION_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])\d+(?:\.\d+){1,3}(?:[-+][A-Za-z0-9._-]+)?"
)


def _closed_summary(output: str, exit_code: int, policy: str) -> str:
    """Return only closed categories or a validated version token."""
    lowered = output.casefold()
    if exit_code == 0:
        if policy == "version":
            match = VERSION_PATTERN.search(output)
            return f"version:{match.group(0)}" if match else "version-unresolved"
        return "success"
    if "operation not permitted" in lowered:
        return "operation-not-permitted"
    if "permission denied" in lowered:
        return "permission-denied"
    if "not found" in lowered or "not installed" in lowered:
        return "not-found"
    return "command-failed-redacted"


def run_sanitized(
    command: list[str], *, timeout: int = 5, output_policy: str = "closed"
) -> dict:
    try:
        completed = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True,
            timeout=timeout, check=False, env=SAFE_ENV,
        )
    except FileNotFoundError:
        return {"available": False, "exit_code": None, "summary": "not-found"}
    except subprocess.TimeoutExpired:
        return {"available": True, "exit_code": None, "summary": "timeout"}
    except (OSError, UnicodeError):
        return {"available": False, "exit_code": None, "summary": "os-error-redacted"}
    output = f"{completed.stdout}\n{completed.stderr}"
    summary = _closed_summary(output, completed.returncode, output_policy)
    return {"available": True, "exit_code": completed.returncode, "summary": summary}


def read_proc_key(path: Path) -> str:
    try:
        value = path.read_text(encoding="ascii").strip()
        return value if value.isdecimal() else "unexpected-redacted"
    except FileNotFoundError:
        return "not-present"
    except OSError:
        return "unreadable"


def bwrap_capability_probe() -> dict:
    """Probe bubblewrap only; this is not a Codex sandbox readiness test."""
    command = [
        "bwrap", "--ro-bind", "/", "/", "--proc", "/proc", "--dev", "/dev",
        "--unshare-all", "--die-with-parent", "/bin/true",
    ]
    result = run_sanitized(command, output_policy="probe")
    result["status"] = "PASS" if result.get("exit_code") == 0 else "BLOCKED"
    return result


def diagnose(probe: bool = False) -> dict:
    tools = {
        name: run_sanitized(command, output_policy="version")
        for name, command in VERSION_COMMANDS.items()
    }
    python_supported = sys.version_info[:2] == (3, 12)
    required_tools_observed = all(
        tools[name].get("exit_code") == 0 for name in ("git", "bwrap")
    )
    system_name = platform.system()
    if system_name not in {"Linux", "Darwin", "Windows"}:
        system_name = "unexpected-redacted"
    release = platform.release()
    if not re.fullmatch(r"[A-Za-z0-9._+-]{1,128}", release):
        release = "unexpected-redacted"
    report = {
        "diagnostic": "local_environment_read_only",
        "collection_status": (
            "COLLECTED" if python_supported and required_tools_observed else "PARTIAL"
        ),
        "mutating_commands_requested": 0,
        "network_required": False,
        "python": {"version": platform.python_version(), "supported": python_supported},
        "os": {"system": system_name, "release": release},
        "tools": tools,
        "kernel_read_only": {name: read_proc_key(path) for name, path in PROC_KEYS.items()},
        "repository": {
            "identity_and_status": "NOT_COLLECTED_BY_THIS_DIAGNOSTIC",
            "reason": "verify separately with explicit human-reviewed Git commands",
        },
        "bwrap_capability": bwrap_capability_probe() if probe else {
            "status": "NOT_RUN",
            "reason": "requires explicit --probe-bwrap",
        },
        "codex_write_readiness": (
            "BLOCKED_REQUIRES_REAL_CODEX_SANDBOX_CHECK_AND_AUTHOR_DECISION"
        ),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--probe-bwrap",
        action="store_true",
        help="run one inert bubblewrap capability probe; does not authorize Codex writes",
    )
    args = parser.parse_args()
    report = diagnose(args.probe_bwrap)
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["collection_status"] != "COLLECTED":
        return 1
    if args.probe_bwrap and report["bwrap_capability"]["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
