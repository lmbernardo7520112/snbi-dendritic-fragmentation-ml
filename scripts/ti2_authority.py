"""Compatibility facade: authority is implemented only in the package."""

from pathlib import Path
import sys

# Direct script execution does not require a local package installation.
_SOURCE_ROOT = str(Path(__file__).resolve().parents[1] / "src")
if _SOURCE_ROOT not in sys.path:
    sys.path.insert(0, _SOURCE_ROOT)

from snbi_fragmentation.ti2_authority import (
    ROOT, CLOSED_STATE, BOUNDARY_STATE, AuthorityError,
    ScientificExecutionBlocked, validate_governance, load_governance,
    audit_authority, require_scientific_authority,
)
