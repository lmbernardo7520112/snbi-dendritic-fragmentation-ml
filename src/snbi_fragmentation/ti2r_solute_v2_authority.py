"""CI-gated, single-use V2 development authority; holdout is never admissible.

The immutable C1 configuration supplies a conditional grant. A published C1,
green push and PR CI, and an atomic receipt are all required before bytes.
The terminal tombstone closes the namespace before the result is persisted.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

from . import ti2r_solute_direct_authority as previous


V2AuthorityError = previous.SoluteAuthorityError
V2IOBlocked = previous.SoluteIOBlocked
SoluteAuthorityError = V2AuthorityError
SoluteIOBlocked = V2IOBlocked
_exact = previous._exact
_parts = previous._parts
_parent_fd = previous._parent_fd
_write_exclusive = previous._write_exclusive
_encoded = previous._encoded
_unique_object = previous._unique_object
_git_identity = previous._git_identity
_read_regular = previous._read_regular
SHA256_RE = previous.SHA256_RE
SHA1_RE = previous.SHA1_RE

REPOSITORY = "lmbernardo7520112/snbi-dendritic-fragmentation-ml"
BRANCH = "feat/ti2r-solute-v2-calibration"
BASE_SHA = "fcfc5e1445467248566e881c61929d4d3da7b1d8"
AUTHORITY_PATH = "configs/authority/ti2r-solute-v2.json"
EVIDENCE_PATH = "artifacts/evidence/TI2R_SOLUTE_V2"
RECEIPT_PATH = EVIDENCE_PATH + "/receipt.json"
TERMINAL_PATH = EVIDENCE_PATH + "/terminal-state.json"
RESULT_PATH = EVIDENCE_PATH + "/result.json"
PAIR_SOURCES = previous.PAIR_SOURCES
DIMENSIONS = previous.DIMENSIONS
FRAME_INDICES = {source: list(roles["development"])
                 for source, roles in previous.FRAME_INDICES.items()}
ASSET_ROLES = {f"{source}:{index}": "development"
               for source, indices in FRAME_INDICES.items() for index in indices}
HOLDOUT_ASSETS = frozenset(asset for asset, role in previous.ASSET_ROLES.items()
                         if role == "holdout")
FROZEN_TEXT_PATHS = frozenset({
    "docs/protocols/TI2R_SOLUTE_V2_PROTOCOL.md",
    "docs/decisions/AUTHORIZATION-TI2R-SOLUTE-V2-D-2026-09-18.md",
    "scripts/run_ti2r_solute_v2.py", "scripts/run_ti2r_solute_v2_synthetic.py",
    "src/snbi_fragmentation/ti2r_solute_v2_authority.py",
    "src/snbi_fragmentation/ti2r_solute_v2_calibration.py",
    "configs/registration/ti2r-solute-v2-method.json", AUTHORITY_PATH,
    "tests/test_ti2r_solute_v2_authority.py",
    "tests/test_ti2r_solute_v2_calibration.py",
    "tests/test_ti2r_solute_v2_execution.py",
    EVIDENCE_PATH + "/exposure.json",
    "src/snbi_fragmentation/ti2r_solute_direct_registration.py",
    "configs/registration/ti2r-solute-direct-method.json",
    "src/snbi_fragmentation/ti2r_solute_direct_authority.py",
    "configs/authority/ti2r-solute-direct.json",
    "src/snbi_fragmentation/ti2r_frag_direct_authority.py",
    "configs/authority/ti2r-frag-direct.json",
    "src/snbi_fragmentation/ti2r_frag_authority.py",
    "configs/authority/ti2r-frag.json",
    "src/snbi_fragmentation/ti2_authority.py", "pyproject.toml",
    "artifacts/metadata/ti2-pilot-manifest.json", ".github/workflows/ci.yml",
    "artifacts/evidence/TI2R_SOLUTE_DIRECT/result.json",
})
TERMINALS = {
    "PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION":
        ("BLOCKED_PENDING_LOCKED_HOLDOUT", "SEALED"),
    "BLOCKED_METHOD_NOT_DISCRIMINATIVE":
        ("BLOCKED_FINAL_WITH_AVAILABLE_DATA", "SEALED_NOT_NEEDED"),
    "BLOCKED_OPERATIONAL_REQUIRES_AUTHOR_DECISION":
        ("BLOCKED_PENDING_V2", "SEALED"),
}
_SESSION_TOKEN = object()


def _deny(message):
    raise V2IOBlocked("BLOCKED_OPERATIONAL_REQUIRES_AUTHOR_DECISION: " + message)


def expected_authority():
    return {
        "phase": "TI2R_SOLUTE_V2_DEV", "state": "PREREGISTERED_CI_GATED",
        "authorization_id": "TI2R-SOLUTE-V2-D-2026-09-18",
        "base_sha": BASE_SHA, "authorized_branch": BRANCH,
        "allowed_pairs": list(PAIR_SOURCES),
        "allowed_frame_indices": json.loads(json.dumps(FRAME_INDICES)),
        "documented_dimensions": {source: list(size) for source, size in DIMENSIONS.items()},
        "holdout_policy": "ALWAYS_DENY_ALL_EIGHT_BEFORE_PATH_ACCESS",
        "execution_policy": "ONE_INVOCATION_AFTER_PUBLISHED_C1_CI",
        "max_invocations": 1,
        "current_authorized_activity": "TI2R_SOLUTE_V2_PREREGISTERED_CI_GATED",
        "development_execution_after_c1_ci_authorized": True,
        "ti2r_execution_authorized": False,
        "ti2r_solute_holdout_authorized": False,
        "ti3_plus_authorized": False, "merge_authorized": False,
        "terminal_tombstone": TERMINAL_PATH,
    }


def validate_authority(document):
    return [] if _exact(document, expected_authority()) else ["V2 authority differs from exact C1 schema"]


def _require_no_terminal(root):
    """Presence closes authority; no parsing, symlink following or data I/O."""
    try:
        parent, name = _parent_fd(root, TERMINAL_PATH)
        try:
            os.stat(name, dir_fd=parent, follow_symlinks=False)
        finally:
            os.close(parent)
    except FileNotFoundError:
        return
    except OSError:
        _deny("terminal state cannot be safely checked")
    _deny("terminal tombstone exists; authority is permanently consumed")


def load_authority(root):
    _require_no_terminal(root)
    try:
        if previous.load_authority(root)["state"] != "CLOSED_CONSUMED":
            _deny("previous SOLUTE and all ancestor authorities must remain consumed")
        document = json.loads(_read_regular(root, AUTHORITY_PATH), object_pairs_hook=_unique_object)
        if validate_authority(document):
            _deny("invalid canonical V2 authority")
        return document
    except (OSError, ValueError, UnicodeError) as exc:
        _deny("canonical V2 authority unavailable: " + type(exc).__name__)


def require_preregistered(root):
    """Validate conditional C1 authority; this alone grants no experimental I/O."""
    return load_authority(root)


def read_text_file(root, relative):
    _parts(relative)
    if relative not in FROZEN_TEXT_PATHS:
        _deny("text input is outside the frozen V2 allowlist")
    return _read_regular(root, relative).decode("utf-8")


def _git_read(root, *arguments):
    result = subprocess.run(["git", *arguments], cwd=root, check=False,
                            capture_output=True, text=True)
    if result.returncode:
        _deny("read-only C1 Git preflight failed")
    return result.stdout.strip()


def verify_c1_git(root, c1_sha):
    if _git_identity(root) != (BRANCH, c1_sha):
        _deny("branch or C1 identity differs")
    if _git_read(root, "rev-list", "--parents", "-n", "1", "HEAD").split() != [c1_sha, BASE_SHA]:
        _deny("C1 must be the single preregistration commit above the audited merge")
    if _git_read(root, "rev-parse", "refs/remotes/origin/" + BRANCH) != c1_sha:
        _deny("published tracking branch differs from C1")
    if _git_read(root, "status", "--porcelain=v1", "--untracked-files=all"):
        _deny("C1 worktree or index is not clean")


def validate_ci_evidence(document, c1_sha):
    """Validate operator-supplied authenticated GitHub observations, never network."""
    if (type(document) is not dict
            or set(document) != {"repository", "branch", "head_sha", "published", "pull_request", "runs"}
            or document["repository"] != REPOSITORY or document["branch"] != BRANCH
            or document["head_sha"] != c1_sha or document["published"] is not True):
        _deny("missing or inconsistent published C1 evidence")
    pr = document["pull_request"]
    if (type(pr) is not dict or set(pr) != {"number", "state", "draft", "head_sha", "base_sha"}
            or type(pr["number"]) is not int or pr["number"] <= 9
            or pr["state"] != "OPEN" or pr["draft"] is not True
            or pr["head_sha"] != c1_sha or pr["base_sha"] != BASE_SHA):
        _deny("C1 requires an open Draft PR at the frozen head and base")
    runs = document["runs"]
    if type(runs) is not list or len(runs) != 2:
        _deny("both push and pull-request C1 CI evidence are required")
    ids, events = set(), set()
    for run in runs:
        if (type(run) is not dict
                or set(run) != {"databaseId", "event", "headSha", "status", "conclusion", "url", "jobs"}
                or type(run["databaseId"]) is not int or run["databaseId"] <= 0
                or run["databaseId"] in ids or run["event"] not in ("push", "pull_request")
                or run["event"] in events or run["headSha"] != c1_sha
                or run["status"] != "completed" or run["conclusion"] != "success"
                or run["url"] != f"https://github.com/{REPOSITORY}/actions/runs/{run['databaseId']}"):
            _deny("C1 CI run identity, status or conclusion differs")
        ids.add(run["databaseId"])
        events.add(run["event"])
        jobs = run["jobs"]
        if type(jobs) is not list or len(jobs) != 2:
            _deny("C1 requires both mandatory CI jobs")
        names = set()
        for job in jobs:
            if (type(job) is not dict or set(job) != {"name", "status", "conclusion", "steps"}
                    or job["name"] not in ("deterministic-contracts", "scientific-synthetic-contracts")
                    or job["name"] in names or job["status"] != "completed"
                    or job["conclusion"] != "success" or type(job["steps"]) is not list
                    or not job["steps"]):
                _deny("mandatory CI job missing, skipped or non-green")
            names.add(job["name"])
            for step in job["steps"]:
                if (type(step) is not dict or set(step) != {"name", "status", "conclusion"}
                        or type(step["name"]) is not str or not step["name"].strip()
                        or step["status"] != "completed" or step["conclusion"] != "success"):
                    _deny("CI step missing, skipped or non-green")


def _validate_assets(assets):
    if type(assets) is not list or len(assets) != 12:
        _deny("exactly twelve development assets are required")
    validated = {}
    keys = {"asset_id", "source_id", "frame_index", "role", "path", "width", "height",
            "frame_bytes", "image_sha256", "pixel_format", "bit_depth"}
    for asset in assets:
        if (type(asset) is not dict or set(asset) != keys
                or type(asset["source_id"]) is not str or type(asset["frame_index"]) is not int):
            _deny("invalid development asset identity")
        source, index = asset["source_id"], asset["frame_index"]
        identity = f"{source}:{index}"
        if identity not in ASSET_ROLES or identity in validated:
            _deny("holdout or unlisted/duplicate development asset")
        if (type(asset["asset_id"]) is not str or asset["asset_id"] != identity
                or asset["role"] != "development"
                or type(asset["path"]) is not str
                or asset["path"] != f"data/derived/ti2-pilot/{source}-{index:04d}.raw"):
            _deny("development identity, role or exact path differs")
        width, height = DIMENSIONS[source]
        if (type(asset["width"]) is not int or type(asset["height"]) is not int
                or (asset["width"], asset["height"]) != (width, height)
                or type(asset["frame_bytes"]) is not int or asset["frame_bytes"] != width * height * 3 // 2
                or asset["pixel_format"] != "yuv420p" or type(asset["bit_depth"]) is not int
                or asset["bit_depth"] != 8 or type(asset["image_sha256"]) is not str
                or not SHA256_RE.fullmatch(asset["image_sha256"])):
            _deny("native development dimensions, bytes, format or digest differ")
        validated[identity] = json.loads(json.dumps(asset))
    if set(validated) != set(ASSET_ROLES):
        _deny("development allowlist is incomplete")
    return validated


def _verify_frozen(root, hashes):
    if type(hashes) is not dict or set(hashes) != FROZEN_TEXT_PATHS:
        _deny("the complete frozen V2 text set is required")
    for relative, digest in hashes.items():
        if type(digest) is not str or not SHA256_RE.fullmatch(digest):
            _deny("invalid frozen text digest")
        if hashlib.sha256(read_text_file(root, relative).encode("utf-8")).hexdigest() != digest:
            _deny("frozen C1 text differs")


def begin_session(root, *, c1_sha, frozen_hashes, assets, exposure, ci_evidence):
    load_authority(root)
    if type(c1_sha) is not str or not SHA1_RE.fullmatch(c1_sha) or c1_sha == BASE_SHA:
        _deny("exact C1 commit identity is required")
    validate_ci_evidence(ci_evidence, c1_sha)
    verify_c1_git(root, c1_sha)
    validated = _validate_assets(assets)
    if type(exposure) is not dict or set(exposure) != set(ASSET_ROLES):
        _deny("exposure must describe exactly the twelve development assets")
    for entry in exposure.values():
        if (type(entry) is not dict
                or set(entry) != {"development_eligible_this_phase", "evidence", "previous_exposure"}
                or entry["development_eligible_this_phase"] is not True):
            _deny("explicit development eligibility and prior exposure are required")
        for field in ("evidence", "previous_exposure"):
            if (type(entry[field]) is not list or not entry[field]
                    or any(type(item) is not str or not item.strip() for item in entry[field])):
                _deny("exposure evidence must be affirmative nonempty text")
    _verify_frozen(root, frozen_hashes)
    receipt = _encoded({
        "phase": "TI2R_SOLUTE_V2_DEV", "authorization_id": "TI2R-SOLUTE-V2-D-2026-09-18",
        "c1_sha": c1_sha, "frozen_hashes": frozen_hashes, "allowed_assets": validated,
        "exposure_state": exposure, "ci_evidence": ci_evidence,
        "invocation_counter": 1, "max_invocations": 1,
        "no_prior_receipt_confirmed_by": "ATOMIC_O_EXCL_CREATION",
        "experimental_bytes_before_receipt": 0,
        "holdout_assets": sorted(HOLDOUT_ASSETS), "holdout_open_count": 0,
        "holdout_content_bytes_read": 0,
    })
    try:
        _write_exclusive(root, RECEIPT_PATH, receipt)
    except FileExistsError:
        _deny("invocation already consumed; no retry")
    return V2Session(root, c1_sha, validated, json.loads(json.dumps(exposure)), receipt,
                     _token=_SESSION_TOKEN)


class V2Session:
    def __init__(self, root, c1_sha, assets, exposure, receipt, *, _token=None):
        if _token is not _SESSION_TOKEN:
            _deny("session requires the atomic CI-gated invocation receipt")
        self.root, self.c1_sha, self.assets, self.exposure = root, c1_sha, assets, exposure
        self.receipt_sha256 = hashlib.sha256(receipt).hexdigest()
        self.opened, self.attempted = [], set()
        self.content_bytes_read = 0
        self.closed = False

    def _require(self):
        if self.closed:
            _deny("session is closed")
        load_authority(self.root)
        if _git_identity(self.root) != (BRANCH, self.c1_sha):
            _deny("branch or frozen C1 HEAD changed")
        raw = _read_regular(self.root, RECEIPT_PATH)
        if hashlib.sha256(raw).hexdigest() != self.receipt_sha256:
            _deny("immutable invocation receipt changed")
        receipt = json.loads(raw, object_pairs_hook=_unique_object)
        if not _exact(self.assets, receipt["allowed_assets"]) or not _exact(self.exposure, receipt["exposure_state"]):
            _deny("asset or exposure drift from immutable receipt")
        _verify_frozen(self.root, receipt["frozen_hashes"])

    @property
    def opened_assets(self):
        return json.loads(json.dumps(self.opened))

    def finish(self, report):
        """Consume authority before persistence, including failed result writes."""
        if self.closed:
            _deny("finish already attempted; no retry")
        self.closed = True
        valid = (type(report) is dict and type(report.get("TI2R_SOLUTE_V2_DEV")) is str
                 and report["TI2R_SOLUTE_V2_DEV"] in TERMINALS)
        if not valid:
            state = "BLOCKED_OPERATIONAL_REQUIRES_AUTHOR_DECISION"
        else:
            state = report["TI2R_SOLUTE_V2_DEV"]
        gate, seal = TERMINALS[state]
        terminal = {
            "phase": "TI2R_SOLUTE_V2_DEV", "state": "CLOSED_CONSUMED",
            "c1_sha": self.c1_sha, "receipt_sha256": self.receipt_sha256,
            "TI2R_SOLUTE_V2_DEV": state, "G2_SOLUTE": gate,
            "G2_FRAG": "PASS_DIRECT_RASTER_MAPPING", "HOLDOUT_SOLUTE": seal,
            "CURRENT_AUTHORIZED_ACTIVITY": "NONE_AWAITING_AUTHOR_DECISION",
            "TI2R_EXECUTION_AUTHORIZED": False, "TI2R_SOLUTE_HOLDOUT_AUTHORIZED": False,
            "TI3_PLUS_AUTHORIZED": False, "MERGE_AUTHORIZED": False,
            "NO_AUTOMATIC_V3": True, "invocation_counter": 1,
            "opened_assets": self.opened_assets, "content_bytes_read": self.content_bytes_read,
            "open_count": sum(item["file_opened"] for item in self.opened),
            "holdout_open_count": 0, "holdout_content_bytes_read": 0,
            "holdout_assets": {asset: {"open_count": 0, "content_bytes_read": 0}
                               for asset in sorted(HOLDOUT_ASSETS)},
        }
        if state == "PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION":
            terminal["V2_RULE"] = "FROZEN"
        _write_exclusive(self.root, TERMINAL_PATH, _encoded(terminal))
        if not valid:
            _deny("invalid result; authority closed with operational failure")
        _write_exclusive(self.root, RESULT_PATH, _encoded(report))
        return terminal


def read_asset(session, asset_id, *, role="development"):
    # Reject before invoking session logic or examining any experimental path.
    if (type(asset_id) is not str or asset_id not in ASSET_ROLES
            or type(role) is not str or role != "development"):
        _deny("all holdouts and all unlisted assets are unconditionally forbidden")
    session._require()
    if asset_id in session.attempted:
        _deny("development asset opening already attempted; no retry")
    asset = session.assets[asset_id]
    session.attempted.add(asset_id)
    audit = {"asset_id": asset_id, "role": role, "status": "ATTEMPTED",
             "file_opened": False, "bytes_read": 0}
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
                _deny("development asset type or size differs")
            content = stream.read(asset["frame_bytes"] + 1)
    except OSError:
        audit["status"] = "BLOCKED_UNAVAILABLE"
        _deny("development asset unavailable or unsafe")
    audit["bytes_read"] = len(content)
    session.content_bytes_read += len(content)
    if len(content) != asset["frame_bytes"] or hashlib.sha256(content).hexdigest() != asset["image_sha256"]:
        audit["status"] = "BLOCKED_DIGEST"
        _deny("development bytes differ from the frozen manifest")
    audit["status"] = "PASS"
    return content
