"""Independent, single-use authority for solute raster identity certification.

Only low-level safe text/descriptor primitives are reused from the closed prior
phase. Its session and scientific authority are never reused. All three older
authorities must remain closed before this namespace can authorize any I/O.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat

from . import ti2r_frag_direct_authority as previous


SoluteAuthorityError = previous.DirectAuthorityError
SoluteIOBlocked = previous.DirectIOBlocked
_exact = previous._exact
_parts = previous._parts
_parent_fd = previous._parent_fd
_write_exclusive = previous._write_exclusive
_encoded = previous._encoded
_unique_object = previous._unique_object
_git_identity = previous._git_identity

AUTHORITY_PATH = "configs/authority/ti2r-solute-direct.json"
EVIDENCE_PATH = "artifacts/evidence/TI2R_SOLUTE_DIRECT"
RECEIPT_PATH = EVIDENCE_PATH + "/receipt.json"
BASE_SHA = "db03183e1456f67b5b663a4cb71361cad1404dcb"
BRANCH = "feat/ti2r-solute-direct-mapping"
PAIR_SOURCES = {"ESM2-to-ESM1": ("ESM2", "ESM1"), "ESM5-to-ESM4": ("ESM5", "ESM4")}
DIMENSIONS = {"ESM1": (1278, 1018), "ESM2": (1278, 1018), "ESM4": (1278, 1012), "ESM5": (1278, 1012)}
OFFSETS = {"ESM2-to-ESM1": {"x": [0], "y": [0]},
           "ESM5-to-ESM4": {"x": [0], "y": [0]}}
FRAME_INDICES = {
    "ESM1": {"development": [0, 146, 293], "holdout": [73, 219]},
    "ESM2": {"development": [0, 146, 293], "holdout": [73, 219]},
    "ESM4": {"development": [0, 197, 394], "holdout": [98, 295]},
    "ESM5": {"development": [0, 197, 394], "holdout": [98, 295]},
}
ASSET_ROLES = {f"{source}:{index}": role for source, roles in FRAME_INDICES.items()
               for role, indices in roles.items() for index in indices}
FROZEN_TEXT_PATHS = frozenset({
    "docs/protocols/TI2R_SOLUTE_DIRECT_PROTOCOL.md", "scripts/run_ti2r_solute_direct.py",
    "src/snbi_fragmentation/ti2r_solute_direct_authority.py",
    "src/snbi_fragmentation/ti2r_solute_direct_registration.py",
    "configs/registration/ti2r-solute-direct-method.json",
    "artifacts/evidence/TI2R_SOLUTE_DIRECT/exposure.json",
    "artifacts/metadata/ti2-pilot-manifest.json", "pyproject.toml",
    "configs/authority/ti2r-frag.json", "configs/authority/ti2r-frag-direct.json",
    "src/snbi_fragmentation/ti2r_frag_authority.py", "src/snbi_fragmentation/ti2r_frag_direct_authority.py",
    "src/snbi_fragmentation/ti2_authority.py", "artifacts/evidence/TI2R_FRAG_DIRECT/result.json",
})
STATES = {
    "PREPARED_INACTIVE": ("NONE_AWAITING_AUTHOR_DECISION", False),
    "ACTIVE_ONE_SHOT": ("TI2R_SOLUTE_DIRECT_ONE_SHOT", True),
    "CLOSED_CONSUMED": ("NONE_AWAITING_AUTHOR_DECISION", False),
}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
_SESSION_TOKEN = object()


def _read_regular(root, relative, *, limit=16_000_000):
    try:
        return previous._read_regular(root, relative, limit=limit)
    except (OSError, ValueError, UnicodeError, SoluteAuthorityError) as exc:
        raise SoluteIOBlocked(
            "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: frozen text unavailable or unsafe: "
            + type(exc).__name__
        ) from None


def expected_authority(state: str = "PREPARED_INACTIVE") -> dict:
    if type(state) is not str or state not in STATES:
        raise SoluteAuthorityError("unsupported TI2R-SOLUTE-DIRECT state")
    activity, active = STATES[state]
    return {
        "phase": "TI2R_SOLUTE_DIRECT", "state": state,
        "authorization_id": "TI2R-SOLUTE-DIRECT-2026-09-18",
        "base_sha": BASE_SHA, "authorized_branch": BRANCH,
        "allowed_pairs": list(PAIR_SOURCES),
        "allowed_frame_indices": json.loads(json.dumps(FRAME_INDICES)),
        "documented_dimensions": {source: list(size) for source, size in DIMENSIONS.items()},
        "allowed_offsets": json.loads(json.dumps(OFFSETS)),
        "holdout_policy": "OPEN_ONCE_AFTER_DEVELOPMENT_AND_FREEZE",
        "max_invocations": 1, "current_authorized_activity": activity,
        "ti2r_execution_authorized": active, "ti3_plus_authorized": False,
        "merge_authorized": False,
    }


def validate_authority(document: object) -> list[str]:
    if type(document) is not dict or type(document.get("state")) is not str or document["state"] not in STATES:
        return ["missing or unsupported direct authority state"]
    return [] if _exact(document, expected_authority(document["state"])) else ["direct authority differs from the exact canonical schema"]


def load_authority(root: Path) -> dict:
    """Require canonical legacy closure and consumption of the previous phase."""
    try:
        prior = previous.load_authority(root)
        if prior["state"] != "CLOSED_CONSUMED":
            raise SoluteAuthorityError("previous TI2R-FRAG-DIRECT authority must be consumed")
        document = json.loads(_read_regular(root, AUTHORITY_PATH), object_pairs_hook=_unique_object)
        violations = validate_authority(document)
        if violations:
            raise SoluteAuthorityError("; ".join(violations))
        return document
    except (OSError, ValueError, UnicodeError, SoluteAuthorityError) as exc:
        raise SoluteAuthorityError(
            "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: solute authority unavailable or invalid: "
            + type(exc).__name__
        ) from None


def require_active(root: Path) -> dict:
    authority = load_authority(root)
    if authority["state"] != "ACTIVE_ONE_SHOT":
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: direct authority is inactive or permanently consumed")
    return authority


def read_text_file(root: Path, relative: str) -> str:
    """Fixed governed text only; data paths are rejected before any open."""
    _parts(relative)
    if relative not in FROZEN_TEXT_PATHS and relative != AUTHORITY_PATH:
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: text input is not in the direct-phase frozen allowlist")
    return _read_regular(root, relative).decode("utf-8")


def _validate_assets(assets: object) -> dict:
    if type(assets) is not list or len(assets) != 20:
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: exactly 20 existing allowed assets are required")
    validated = {}
    for asset in assets:
        if type(asset) is not dict or type(asset.get("source_id")) is not str or type(asset.get("frame_index")) is not int:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: invalid asset identity")
        source, index = asset["source_id"], asset["frame_index"]
        asset_id = f"{source}:{index}"
        if asset_id not in ASSET_ROLES or asset_id in validated:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: asset is outside the exact allowlist or duplicated")
        if type(asset.get("asset_id")) is not str or asset["asset_id"] != asset_id or type(asset.get("role")) is not str or asset["role"] != ASSET_ROLES[asset_id]:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: asset identifier or role differs from the frozen allowlist")
        width, height = DIMENSIONS[source]
        if type(asset.get("width")) is not int or type(asset.get("height")) is not int or (asset["width"], asset["height"]) != (width, height):
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: documented raster dimensions differ")
        relative = f"data/derived/ti2-pilot/{source}-{index:04d}.raw"
        if type(asset.get("path")) is not str or asset["path"] != relative:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: asset path does not match its exact identity")
        if type(asset.get("frame_bytes")) is not int or asset["frame_bytes"] != width * height * 3 // 2:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: native raster byte count differs")
        if type(asset.get("pixel_format")) is not str or asset["pixel_format"] != "yuv420p" or type(asset.get("bit_depth")) is not int or asset["bit_depth"] != 8:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: native format differs")
        if type(asset.get("image_sha256")) is not str or not SHA256_RE.fullmatch(asset["image_sha256"]):
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: frozen asset digest is invalid")
        validated[asset_id] = {key: asset[key] for key in (
            "asset_id", "source_id", "frame_index", "role", "path", "width", "height",
            "frame_bytes", "image_sha256", "pixel_format", "bit_depth")}
    if set(validated) != set(ASSET_ROLES):
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: frozen direct asset set is incomplete")
    return validated


class SoluteSession:
    """A fresh receipt-bound session, independent from the consumed old phase."""

    def __init__(self, root, c2_sha, assets, exposure, receipt, *, _token=None):
        if _token is not _SESSION_TOKEN:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: direct session requires the atomic one-shot receipt")
        self.root, self.c2_sha, self.assets, self.exposure = root, c2_sha, assets, exposure
        self.receipt_sha256 = hashlib.sha256(receipt).hexdigest()
        self.opened = []
        self.attempted = set()
        self.candidates = {}
        self.content_bytes_read = 0

    def _require(self):
        require_active(self.root)
        if _git_identity(self.root) != (BRANCH, self.c2_sha):
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: direct branch or frozen C2 HEAD changed")
        raw = _read_regular(self.root, RECEIPT_PATH)
        if hashlib.sha256(raw).hexdigest() != self.receipt_sha256:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: direct invocation receipt changed")
        receipt = json.loads(raw)
        if not _exact(self.assets, receipt["allowed_assets"]) or not _exact(self.exposure, receipt["exposure_state"]):
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: asset or exposure drift from immutable receipt")

    @property
    def opened_assets(self):
        return json.loads(json.dumps(self.opened))

    def write_result(self, report):
        self._require()
        _write_exclusive(self.root, EVIDENCE_PATH + "/result.json", _encoded(report))

    def freeze_identity(self, pair, record):
        self._require()
        if type(pair) is not str or pair not in OFFSETS or pair in self.candidates:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: unknown pair or identity already frozen")
        if type(record) is not dict or record.get("development_pass") is not True:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: freeze requires complete development acceptance")
        offset = record.get("offset")
        if type(offset) is not list or len(offset) != 2 or any(type(value) is not int for value in offset):
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: offset must contain exactly two plain integers")
        if offset[0] not in OFFSETS[pair]["x"] or offset[1] not in OFFSETS[pair]["y"]:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: offset lies outside the sole authorized identity")
        if "matrix" in record:
            matrix = record["matrix"]
            expected = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            if (type(matrix) is not list or len(matrix) != 3
                    or any(type(row) is not list or len(row) != 3 for row in matrix)
                    or any(type(value) not in (int, float) or value != expected[y][x]
                           for y, row in enumerate(matrix) for x, value in enumerate(row))):
                raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: only the exact identity matrix can be frozen")
        required = {f"{source}:{index}" for source in PAIR_SOURCES[pair] for index in FRAME_INDICES[source]["development"]}
        if not required <= {item["asset_id"] for item in self.opened if item["status"] == "PASS"}:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: freeze requires all six successful development reads")
        content = _encoded({"pair": pair, "c2_sha": self.c2_sha, "record": record, "holdout_opened": False})
        _write_exclusive(self.root, EVIDENCE_PATH + f"/{pair}-freeze.json", content)
        self.candidates[pair] = json.loads(content)


def begin_session(root, *, c2_sha, frozen_hashes, assets, exposure):
    require_active(root)
    if type(c2_sha) is not str or not SHA1_RE.fullmatch(c2_sha) or c2_sha == BASE_SHA:
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: direct execution requires its exact C2 identity")
    if _git_identity(root) != (BRANCH, c2_sha):
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: direct execution branch or C2 identity mismatch")
    validated = _validate_assets(assets)
    if type(exposure) is not dict or set(exposure) != set(ASSET_ROLES):
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: exposure registry must identify the exact 20 assets")
    for asset_id, entry in exposure.items():
        if (type(entry) is not dict
                or set(entry) != {"holdout_eligible_this_phase", "evidence", "previous_exposure"}
                or type(entry["holdout_eligible_this_phase"]) is not bool):
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: exposure requires exact phase eligibility and prior-exposure fields")
        for field in ("evidence", "previous_exposure"):
            if (type(entry[field]) is not list or not entry[field]
                    or any(type(item) is not str or not item.strip() for item in entry[field])):
                raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: each asset requires affirmative evidence and explicit previous exposure")
        if entry["holdout_eligible_this_phase"] and ASSET_ROLES[asset_id] != "holdout":
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: phase holdout eligibility is restricted to holdout assets")
    if type(frozen_hashes) is not dict or set(frozen_hashes) != FROZEN_TEXT_PATHS:
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: all 14 frozen direct-phase text hashes are required")
    for relative, digest in frozen_hashes.items():
        if type(digest) is not str or not SHA256_RE.fullmatch(digest):
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: invalid frozen text digest")
        if hashlib.sha256(read_text_file(root, relative).encode("utf-8")).hexdigest() != digest:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: frozen direct-phase text hash mismatch")
    receipt = _encoded({
        "phase": "TI2R_SOLUTE_DIRECT", "authorization_id": "TI2R-SOLUTE-DIRECT-2026-09-18",
        "c2_sha": c2_sha, "frozen_hashes": frozen_hashes, "allowed_assets": validated,
        "exposure_state": exposure, "invocation_counter": 1, "max_invocations": 1,
        "no_prior_receipt_confirmed_by": "ATOMIC_O_EXCL_CREATION", "experimental_bytes_before_receipt": 0,
    })
    try:
        _write_exclusive(root, RECEIPT_PATH, receipt)
    except FileExistsError:
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: direct invocation already consumed; no retry") from None
    return SoluteSession(root, c2_sha, validated, json.loads(json.dumps(exposure)), receipt, _token=_SESSION_TOKEN)


def read_asset(session, asset_id, *, role):
    session._require()
    if type(asset_id) is not str or asset_id not in session.assets:
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: asset is outside the direct-phase allowlist")
    if type(role) is not str or role != ASSET_ROLES[asset_id]:
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: asset role does not match the frozen temporal role")
    if asset_id in session.attempted:
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: asset opening already attempted; no retry")
    if role == "holdout":
        entry = session.exposure[asset_id]
        pair = next(pair for pair, sources in PAIR_SOURCES.items() if asset_id.split(":")[0] in sources)
        if entry["holdout_eligible_this_phase"] is not True or not entry["evidence"] or pair not in session.candidates:
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: holdout requires phase eligibility and frozen approved development identity")
        freeze = json.loads(_read_regular(session.root, EVIDENCE_PATH + f"/{pair}-freeze.json"))
        if not _exact(freeze, session.candidates[pair]):
            raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: holdout candidate differs from immutable freeze")
    asset = session.assets[asset_id]
    session.attempted.add(asset_id)
    audit = {"asset_id": asset_id, "role": role, "status": "ATTEMPTED", "file_opened": False, "bytes_read": 0}
    session.opened.append(audit)
    try:
        parent, name = _parent_fd(session.root, asset["path"])
        try:
            descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            audit["file_opened"] = True
        finally:
            os.close(parent)
        with os.fdopen(descriptor, "rb") as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size != asset["frame_bytes"]:
                audit["status"] = "BLOCKED_SIZE_OR_TYPE"
                raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: pilot size or type differs")
            content = stream.read(asset["frame_bytes"] + 1)
    except OSError:
        audit["status"] = "BLOCKED_UNAVAILABLE"
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: existing pilot unavailable or unsafe") from None
    audit["bytes_read"] = len(content)
    session.content_bytes_read += len(content)
    if len(content) != asset["frame_bytes"] or hashlib.sha256(content).hexdigest() != asset["image_sha256"]:
        audit["status"] = "BLOCKED_DIGEST"
        raise SoluteIOBlocked("BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE: pilot digest differs")
    audit["status"] = "PASS"
    return content
