"""Single-use TI2R-FRAG authority and exact, guarded native-buffer reads.

The legacy TI-2 authority must remain canonically closed.  This namespace grants
no permission to an old scientific entry point.  Canonical text and Git identity
are examined before any experimental path or byte.  The exclusive receipt is a
durable invocation lock; an interrupted attempt cannot be resumed or retried.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess

from .ti2_authority import load_governance


AUTHORITY_PATH = "configs/authority/ti2r-frag.json"
RECEIPT_PATH = "artifacts/evidence/TI2R_FRAG/receipt.json"
BASE_SHA = "0245faf74aa15424d95d43f92e87b32a06ac987b"
BRANCH = "feat/ti2r-frag-registration"
PAIR_SOURCES = {"ESM3-to-ESM1": ("ESM3", "ESM1"), "ESM6-to-ESM4": ("ESM6", "ESM4")}
FRAME_INDICES = {
    "ESM1": {"development": [0, 146, 293], "validation": [73, 219]},
    "ESM3": {"development": [0, 146, 293], "validation": [73, 219]},
    "ESM4": {"development": [0, 197, 394], "validation": [98, 295]},
    "ESM6": {"development": [0, 197, 394], "validation": [98, 295]},
}
ASSET_ROLES = {
    f"{source}:{index}": role
    for source, roles in FRAME_INDICES.items()
    for role, indices in roles.items()
    for index in indices
}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
FROZEN_TEXT_PATHS = frozenset({
    "docs/protocols/TI2R_FRAG_PROTOCOL.md", "scripts/run_ti2r_frag.py",
    "src/snbi_fragmentation/ti2r_frag_authority.py",
    "src/snbi_fragmentation/ti2r_frag_registration.py",
    "configs/registration/ti2r-frag-method.json",
    "artifacts/evidence/TI2R_FRAG/exposure.json",
    "artifacts/metadata/ti2-pilot-manifest.json", "pyproject.toml",
})
STATES = {
    "PREPARED_INACTIVE": ("NONE_AWAITING_AUTHOR_DECISION", False),
    "ACTIVE_ONE_SHOT": ("TI2R_FRAG_ONE_SHOT", True),
    "CLOSED_CONSUMED": ("NONE_AWAITING_AUTHOR_DECISION", False),
}
_SESSION_TOKEN = object()


class FragAuthorityError(RuntimeError):
    """Canonical state or the single-use execution boundary is invalid."""


class FragIOBlocked(FragAuthorityError):
    """Experimental I/O is denied without touching its path or contents."""


def expected_authority(state: str = "PREPARED_INACTIVE") -> dict:
    if type(state) is not str or state not in STATES:
        raise FragAuthorityError("unsupported TI2R-FRAG state")
    activity, authorized = STATES[state]
    return {
        "phase": "TI2R_FRAG", "state": state,
        "authorization_id": "TI2R-FRAG-2026-09-18",
        "authorized_branch": BRANCH, "base_sha": BASE_SHA,
        "allowed_pairs": list(PAIR_SOURCES),
        "allowed_frame_indices": json.loads(json.dumps(FRAME_INDICES)),
        "max_invocations": 1, "validation_policy": "OPEN_ONCE_AFTER_FREEZE",
        "current_authorized_activity": activity,
        "ti2r_execution_authorized": authorized,
        "ti3_plus_authorized": False, "merge_authorized": False,
    }


def _exact(value: object, expected: object) -> bool:
    if type(value) is not type(expected):
        return False
    if type(expected) is dict:
        return set(value) == set(expected) and all(_exact(value[key], item) for key, item in expected.items())
    if type(expected) is list:
        return len(value) == len(expected) and all(_exact(a, b) for a, b in zip(value, expected))
    return value == expected


def validate_authority(document: object) -> list[str]:
    if type(document) is not dict or type(document.get("state")) is not str or document["state"] not in STATES:
        return ["unsupported or missing TI2R-FRAG authority"]
    if not _exact(document, expected_authority(document["state"])):
        return ["TI2R-FRAG authority must match the exact state and asset allowlist"]
    return []


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise FragAuthorityError("duplicate canonical JSON field")
        result[key] = value
    return result


def _parts(relative: object) -> tuple[str, ...]:
    if type(relative) is not str:
        raise FragIOBlocked("relative path must be a plain string")
    parts = relative.split("/")
    if not parts or any(part in ("", ".", "..") for part in parts) or "\\" in relative or "\x00" in relative:
        raise FragIOBlocked("unsafe relative path")
    return tuple(parts)


def _parent_fd(root: Path, relative: str, *, create: bool = False) -> tuple[int, str]:
    parts = _parts(relative)
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            if create:
                try:
                    os.mkdir(part, dir_fd=descriptor)
                except FileExistsError:
                    pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor, parts[-1]
    except BaseException:
        os.close(descriptor)
        raise


def _read_regular(root: Path, relative: str, *, limit: int = 16_000_000) -> bytes:
    parent, name = _parent_fd(root, relative)
    try:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    finally:
        os.close(parent)
    with os.fdopen(descriptor, "rb") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > limit:
            raise FragAuthorityError("text input is not a bounded regular file")
        content = stream.read(limit + 1)
        if len(content) > limit:
            raise FragAuthorityError("text input exceeded its bound")
        return content


def read_text_file(root: Path, relative: str) -> str:
    """Read governed repository text only; this API never accepts data paths."""
    parts = _parts(relative)
    if relative != "pyproject.toml" and (
        parts[0] not in ("docs", "scripts", "src", "configs", "artifacts")
        or (parts[0] == "artifacts" and parts[1:2] not in (("metadata",), ("evidence",)))
    ):
        raise FragIOBlocked("frozen input must be safe repository text")
    if not relative.endswith((".json", ".py", ".md", ".toml")):
        raise FragIOBlocked("frozen input must have an allowed textual format")
    return _read_regular(root, relative).decode("utf-8")


def load_authority(root: Path) -> dict:
    """Validate the dedicated namespace and reject any competing legacy grant."""
    try:
        load_governance(root)
        document = json.loads(_read_regular(root, AUTHORITY_PATH), object_pairs_hook=_unique_object)
        violations = validate_authority(document)
        if violations:
            raise FragAuthorityError("; ".join(violations))
        return document
    except (OSError, ValueError, UnicodeError) as exc:
        raise FragAuthorityError(f"canonical authority unavailable or invalid: {type(exc).__name__}") from None


def require_active(root: Path) -> dict:
    authority = load_authority(root)
    if authority["state"] != "ACTIVE_ONE_SHOT":
        raise FragIOBlocked("TI2R-FRAG is inactive or permanently consumed")
    return authority


def _git_identity(root: Path) -> tuple[str, str]:
    results = []
    for arguments in (("branch", "--show-current"), ("rev-parse", "HEAD")):
        result = subprocess.run(["git", *arguments], cwd=root, check=False, capture_output=True, text=True)
        if result.returncode:
            raise FragAuthorityError("read-only Git identity verification failed")
        results.append(result.stdout.strip())
    return tuple(results)


def _validate_assets(assets: object) -> dict:
    if type(assets) is not list or len(assets) != 20:
        raise FragIOBlocked("exactly the 20 frozen fragment assets are required")
    validated = {}
    for asset in assets:
        if type(asset) is not dict or type(asset.get("source_id")) is not str or type(asset.get("frame_index")) is not int:
            raise FragIOBlocked("invalid frozen asset identity")
        asset_id = f"{asset['source_id']}:{asset['frame_index']}"
        if asset_id not in ASSET_ROLES or asset_id in validated:
            raise FragIOBlocked("asset is outside the exact allowlist or duplicated")
        expected_path = f"data/derived/ti2-pilot/{asset['source_id']}-{asset['frame_index']:04d}.raw"
        if type(asset.get("path")) is not str or asset["path"] != expected_path:
            raise FragIOBlocked("asset path does not match its frozen identity")
        if type(asset.get("frame_bytes")) is not int or not 0 < asset["frame_bytes"] <= 32_000_000:
            raise FragIOBlocked("asset byte count is invalid")
        if type(asset.get("image_sha256")) is not str or not SHA256_RE.fullmatch(asset["image_sha256"]):
            raise FragIOBlocked("asset digest is invalid")
        validated[asset_id] = {
            "source_id": asset["source_id"], "frame_index": asset["frame_index"],
            "path": expected_path, "frame_bytes": asset["frame_bytes"],
            "image_sha256": asset["image_sha256"], "role": ASSET_ROLES[asset_id],
        }
    if set(validated) != set(ASSET_ROLES):
        raise FragIOBlocked("frozen asset allowlist is incomplete")
    return validated


def _write_exclusive(root: Path, relative: str, content: bytes) -> None:
    parent, name = _parent_fd(root, relative, create=True)
    try:
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(parent)
    finally:
        os.close(parent)


def _encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


class Session:
    """Created only by begin_session; every asset read checks durable custody."""

    def __init__(self, root: Path, c2_sha: str, assets: dict, exposure: dict, receipt: bytes, *, _token=None):
        if _token is not _SESSION_TOKEN:
            raise FragIOBlocked("session creation requires the atomic single-use receipt")
        self.root = root
        self.c2_sha = c2_sha
        self.assets = assets
        self.exposure = exposure
        self.receipt_sha256 = hashlib.sha256(receipt).hexdigest()
        self.opened = []
        self.attempted = set()
        self.content_bytes_read = 0
        self.candidates = {}

    def _require(self) -> None:
        require_active(self.root)
        if _git_identity(self.root) != (BRANCH, self.c2_sha):
            raise FragIOBlocked("execution branch or frozen C2 HEAD changed")
        receipt = _read_regular(self.root, RECEIPT_PATH)
        if hashlib.sha256(receipt).hexdigest() != self.receipt_sha256:
            raise FragIOBlocked("exclusive invocation receipt changed")
        original = json.loads(receipt)
        if not _exact(self.assets, original["allowed_assets"]) or not _exact(self.exposure, original["exposure_state"]):
            raise FragIOBlocked("session assets or exposure drifted from the immutable receipt")

    @property
    def opened_assets(self) -> list:
        return json.loads(json.dumps(self.opened))

    def write_result(self, report: dict) -> None:
        self._require()
        _write_exclusive(self.root, "artifacts/evidence/TI2R_FRAG/result.json", _encoded(report))

    def freeze_candidate(self, pair: str, record: dict) -> None:
        """Persist one development-approved matrix before any validation opening."""
        self._require()
        if type(pair) is not str or pair not in PAIR_SOURCES or pair in self.candidates:
            raise FragIOBlocked("candidate pair is unknown or already frozen")
        if type(record) is not dict or record.get("development_pass") is not True:
            raise FragIOBlocked("candidate requires positive development acceptance")
        matrix = record.get("matrix")
        if type(matrix) is not list or len(matrix) != 3 or any(type(row) is not list or len(row) != 3 for row in matrix):
            raise FragIOBlocked("candidate matrix must be 3 by 3")
        if any(type(value) not in (int, float) or not math.isfinite(value) for row in matrix for value in row):
            raise FragIOBlocked("candidate matrix must contain finite numbers")
        if (matrix[2] != [0, 0, 1] or matrix[0][0] <= 0 or matrix[1][1] <= 0
                or matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0] <= 0):
            raise FragIOBlocked("candidate reflection, inversion or projective matrix is forbidden")
        required = {f"{source}:{index}" for source in PAIR_SOURCES[pair] for index in FRAME_INDICES[source]["development"]}
        if not required <= {entry["asset_id"] for entry in self.opened if entry["status"] == "PASS"}:
            raise FragIOBlocked("candidate cannot freeze before all six development assets")
        content = _encoded({"pair": pair, "c2_sha": self.c2_sha, "record": record, "validation_opened": False})
        _write_exclusive(self.root, f"artifacts/evidence/TI2R_FRAG/{pair}-freeze.json", content)
        self.candidates[pair] = json.loads(content)


def begin_session(root: Path, *, c2_sha: str, frozen_hashes: dict, assets: list, exposure: dict) -> Session:
    """Atomically consume the one invocation before any experimental bytes."""
    require_active(root)
    if type(c2_sha) is not str or not SHA1_RE.fullmatch(c2_sha) or c2_sha == BASE_SHA:
        raise FragIOBlocked("valid C2 commit identity is required")
    if _git_identity(root) != (BRANCH, c2_sha):
        raise FragIOBlocked("execution branch or C2 HEAD does not match")
    validated = _validate_assets(assets)
    if type(exposure) is not dict or set(exposure) != set(ASSET_ROLES):
        raise FragIOBlocked("exposure registry must identify all 20 allowed assets")
    for entry in exposure.values():
        if type(entry) is not dict or type(entry.get("validation_sealed")) is not bool or type(entry.get("evidence")) is not list:
            raise FragIOBlocked("exposure registry requires explicit seal and textual evidence")
        if any(type(item) is not str or not item.strip() for item in entry["evidence"]):
            raise FragIOBlocked("exposure evidence references must be nonempty strings")
        if entry["validation_sealed"] and not entry["evidence"]:
            raise FragIOBlocked("absence of a log is not positive validation custody")
    if type(frozen_hashes) is not dict or set(frozen_hashes) != FROZEN_TEXT_PATHS:
        raise FragIOBlocked("frozen protocol, runner, config and scientific hashes are required")
    for relative, digest in frozen_hashes.items():
        if type(digest) is not str or not SHA256_RE.fullmatch(digest):
            raise FragIOBlocked("frozen text input or digest is invalid")
        if hashlib.sha256(read_text_file(root, relative).encode("utf-8")).hexdigest() != digest:
            raise FragIOBlocked("frozen text hash mismatch")
    receipt_document = {
        "phase": "TI2R_FRAG", "authorization_id": "TI2R-FRAG-2026-09-18",
        "c2_sha": c2_sha, "frozen_hashes": frozen_hashes,
        "allowed_assets": validated, "exposure_state": exposure,
        "invocation_counter": 1, "max_invocations": 1,
        "no_prior_receipt_confirmed_by": "ATOMIC_O_EXCL_CREATION",
        "experimental_bytes_before_receipt": 0,
    }
    receipt = _encoded(receipt_document)
    try:
        _write_exclusive(root, RECEIPT_PATH, receipt)
    except FileExistsError:
        raise FragIOBlocked("one invocation already consumed; retries are forbidden") from None
    return Session(root, c2_sha, validated, json.loads(json.dumps(exposure)), receipt, _token=_SESSION_TOKEN)


def read_asset(session: Session, asset_id: str, *, role: str) -> bytes:
    """Read one exact allowed buffer after all authority and custody checks."""
    session._require()
    if type(asset_id) is not str or asset_id not in session.assets:
        raise FragIOBlocked("asset is outside the exact fragment allowlist")
    if type(role) is not str or role not in ("development", "validation") or session.assets[asset_id]["role"] != role:
        raise FragIOBlocked("asset role does not match the frozen frame role")
    if asset_id in session.attempted:
        raise FragIOBlocked("asset read already attempted; no repeated opening")
    if role == "validation":
        exposure = session.exposure[asset_id]
        pair = next(pair for pair, sources in PAIR_SOURCES.items() if asset_id.split(":")[0] in sources)
        if exposure["validation_sealed"] is not True or not exposure["evidence"] or pair not in session.candidates:
            raise FragIOBlocked("validation requires positive custody and frozen development candidate")
        freeze = json.loads(_read_regular(session.root, f"artifacts/evidence/TI2R_FRAG/{pair}-freeze.json"))
        if not _exact(freeze, session.candidates[pair]):
            raise FragIOBlocked("validation candidate differs from its immutable freeze")
    asset = session.assets[asset_id]
    session.attempted.add(asset_id)
    audit = {"asset_id": asset_id, "role": role, "status": "ATTEMPTED", "bytes_read": 0}
    session.opened.append(audit)
    try:
        parent, name = _parent_fd(session.root, asset["path"])
        try:
            descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        finally:
            os.close(parent)
        with os.fdopen(descriptor, "rb") as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size != asset["frame_bytes"]:
                audit["status"] = "BLOCKED_SIZE_OR_TYPE"
                raise FragIOBlocked("BLOCKED_PILOT_UNAVAILABLE: pilot size or type differs")
            content = stream.read(asset["frame_bytes"] + 1)
    except OSError:
        audit["status"] = "BLOCKED_UNAVAILABLE"
        raise FragIOBlocked("BLOCKED_PILOT_UNAVAILABLE: existing pilot cannot be opened safely") from None
    audit["bytes_read"] = len(content)
    session.content_bytes_read += len(content)
    if len(content) != asset["frame_bytes"] or hashlib.sha256(content).hexdigest() != asset["image_sha256"]:
        audit["status"] = "BLOCKED_DIGEST"
        raise FragIOBlocked("BLOCKED_PILOT_UNAVAILABLE: pilot digest differs from frozen manifest")
    audit["status"] = "PASS"
    return content
