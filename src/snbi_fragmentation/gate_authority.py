"""Parse the explicit current gate documents without inspecting scientific data.

Only the canonical TOML supplies authority. Gate blocks are exact documentary
mirrors; a coherent closed mirror never grants execution permission. Historical
text is excluded only inside the explicit, non-nested historical delimiters.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat

from .ti2_authority import ROOT, load_governance, validate_governance


CURRENT_GATE_DOCUMENTS = (
    "docs/gates/LOCAL_BOOTSTRAP.md",
    "docs/gates/TI2_GATE_PLAN.md",
)
CURRENT_BEGIN = "<!-- SNBI_CURRENT_AUTHORITY_BEGIN -->"
CURRENT_END = "<!-- SNBI_CURRENT_AUTHORITY_END -->"
HISTORICAL_BEGIN = "<!-- SNBI_HISTORICAL_NON_AUTHORIZING_BEGIN -->"
HISTORICAL_END = "<!-- SNBI_HISTORICAL_NON_AUTHORIZING_END -->"
MARKERS = (CURRENT_BEGIN, CURRENT_END, HISTORICAL_BEGIN, HISTORICAL_END)

# A single normative surface is required. Even a coherent extra assignment
# belongs in the current JSON or a delimited historical record, not prose.
AUTHORITY_FIELDS = (
    "authority_source", "current_authorized_activity", "ti2_execution",
    "ti2_closeout_1", "ti2_execution_authorized", "ti2r_authorized",
    "ti3_plus_authorized", "codex_local_write_readiness", "codex_write_readiness",
    "merge_authorized", "authorized_branch", "pilot_image_limit",
    "authorized_activity", "lifecycle_state", "blocked_phases", "write_boundary",
    "ti3_to_ti8_authorized", "ti2_execution_status", "ti2_formal_closure",
)
RESIDUAL_ASSIGNMENT = re.compile(
    r"(?<![A-Za-z0-9_])[*_]*(?:" + "|".join(AUTHORITY_FIELDS)
    + r")(?![A-Za-z0-9])[\"'`*_]*\s*(?:[:=]|\|)",
    re.IGNORECASE,
)
RESIDUAL_AUTHORIZATION = re.compile(
    r"AUTHORIZED_E0_E7|AUTHORIZED_DEFAULT_SANDBOX_REPOSITORY_ONLY|"
    r"supplies\s+the\s+current\s+bounded\s+authorization|Separately\s+authorized",
    re.IGNORECASE,
)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    document = {}
    for key, value in pairs:
        if key in document:
            raise ValueError("duplicate normative key")
        document[key] = value
    return document


def _current_mirror(governance: dict) -> dict:
    return {
        "authority_source": "pyproject.toml [tool.snbi]",
        "current_authorized_activity": governance["current_authorized_activity"],
        "ti2_execution_authorized": governance["ti2_execution_authorized"],
        "ti2r_authorized": governance["ti2r_authorized"],
        "ti3_plus_authorized": governance["ti3_plus_authorized"],
        "codex_local_write_readiness": governance["codex_local_write_readiness"],
    }


def validate_gate_document(text: str, governance: object) -> list[str]:
    """Validate one exact closed mirror and reject residual active authority."""
    if validate_governance(governance):
        return ["canonical authority is missing, invalid or conflicting"]
    if type(text) is not str:
        return ["gate document must be text"]

    violations = []
    current_lines = []
    outside_lines = []
    state = None
    current_begins = 0
    current_ends = 0
    for line in text.splitlines():
        token = line.strip()
        if "SNBI_CURRENT_AUTHORITY" in line or "SNBI_HISTORICAL_NON_AUTHORIZING" in line:
            if token not in MARKERS:
                violations.append("gate delimiter is malformed or not standalone")
                continue
            if token == CURRENT_BEGIN:
                current_begins += 1
                if state is not None:
                    violations.append("gate delimiters cannot be nested")
                else:
                    state = "current"
            elif token == HISTORICAL_BEGIN:
                if state is not None:
                    violations.append("gate delimiters cannot be nested")
                else:
                    state = "historical"
            elif token == CURRENT_END:
                current_ends += 1
                if state != "current":
                    violations.append("current gate delimiter is unmatched")
                else:
                    state = None
            elif token == HISTORICAL_END:
                if state != "historical":
                    violations.append("historical gate delimiter is unmatched")
                else:
                    state = None
        elif state == "current":
            current_lines.append(line)
        elif state is None:
            outside_lines.append(line)
    if state is not None:
        violations.append("gate delimiter is unclosed")
    if current_begins != 1 or current_ends != 1:
        violations.append("exactly one current authority block is required")

    outside = "\n".join(outside_lines)
    if RESIDUAL_ASSIGNMENT.search(outside) or RESIDUAL_AUTHORIZATION.search(outside):
        violations.append("authority declaration outside current or historical block")
    if violations:
        return violations

    payload = "\n".join(current_lines).strip().splitlines()
    if len(payload) < 3 or payload[0] != "```json" or payload[-1] != "```":
        return ["current authority block must contain exactly one JSON fence"]
    try:
        current = json.loads("\n".join(payload[1:-1]), object_pairs_hook=_unique_object)
    except (ValueError, TypeError):
        return ["current authority JSON is malformed or contains duplicate keys"]
    expected = _current_mirror(governance)
    if type(current) is not dict or set(current) != set(expected):
        return ["current authority JSON keys differ from the canonical mirror"]
    for key, value in expected.items():
        if type(current[key]) is not type(value) or current[key] != value:
            violations.append(f"current authority field differs from canonical state: {key}")
    return violations


def _read_gate(root: Path, relative: str) -> str:
    """Read one allowlisted regular text file without following any symlink."""
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        components = relative.split("/")
        for component in components[:-1]:
            next_descriptor = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = next_descriptor
        file_descriptor = os.open(
            components[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
            dir_fd=descriptor,
        )
        with os.fdopen(file_descriptor, "r", encoding="utf-8") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("current gate must be a regular text file")
            return stream.read()
    finally:
        os.close(descriptor)


def audit_current_gates(root: Path = ROOT) -> dict:
    """Audit only the explicit two-file gate allowlist against canonical state."""
    violations = []
    document_count = 0
    try:
        governance = load_governance(root)
    except (OSError, UnicodeError, ValueError):
        return {
            "status": "BLOCKED", "document_count": 0,
            "violations": ["canonical authority unavailable or invalid"],
        }
    for relative in CURRENT_GATE_DOCUMENTS:
        try:
            text = _read_gate(root, relative)
            document_count += 1
            violations.extend(
                f"{relative}: {violation}"
                for violation in validate_gate_document(text, governance)
            )
        except (OSError, UnicodeError, ValueError):
            violations.append(f"{relative}: current gate text unavailable or invalid")
    return {
        "status": "PASS" if not violations else "BLOCKED",
        "document_count": document_count,
        "violations": violations,
    }
