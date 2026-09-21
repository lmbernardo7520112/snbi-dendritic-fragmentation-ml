"""Receipt-gated Study2-C positive reads and selected-background streaming.

Construction is inert. The controller owns the frozen row manifest, CI, the
scientific receipt, and durable final-fit authorization. This module accepts no
alternative source path, crop, decoder, registration, or cache representation.
Study2-B functions are reused only for native streaming and numerical support;
no Study2-A/B runner, planner, corpus builder, or learner is called.
"""

from collections import defaultdict
from copy import deepcopy
import hashlib
import json
import os
import stat

from . import study2b_corpus as support
from .study2b_streaming import AuthenticatedSources


POSITIVE_PATH = "data/derived/study2b/multimodal_patches_uint8.bin"
POSITIVE_BYTES = 139425000
POSITIVE_ROWS = 16500
POSITIVE_SHA256 = "3957ba2480805fa108c216e500238f1b0fcf39520cfddd0d7d722d65f773b914"
FRAME_HASH_PATH = "artifacts/evidence/STUDY2_B_CORPUS/FRAME_HASHES.json"
FRAME_HASH_SHA256 = "643645280e38269bcf17854d7e4b9b4cfb63d5fb86ec10f5bdfa7641bac876c1"
FRAME_COUNTS = {"ESM1": 294, "ESM4": 395}
SOURCE_PAIRS = (("ESM1", "ESM2"), ("ESM4", "ESM5"))
ROW_BYTES = 8450
CHANNEL_BYTES = 4225
MAX_CACHE_BYTES = 2147483648
MAX_TEMP_BYTES = 268435456
MAX_METADATA_BYTES = 268435456
MIN_FREE_BYTES = 53687091200
HASH_CHUNK_BYTES = 1048576
CACHE_NAMES = {
    "TRAIN_DEVELOPMENT": ("cachetrain_dev.bin", "cachetrain_dev.jsonl"),
    "TEST": ("cachetest.bin", "cachetest.jsonl"),
}


class CorpusAccessError(ValueError):
    """A failed admission, custody, support, or storage condition; no retry."""


def _require(condition, message):
    if not condition:
        raise CorpusAccessError(message)


def _hex(value, length=64):
    return (type(value) is str and len(value) == length
            and all(c in "0123456789abcdef" for c in value))


def _digest(payload):
    return hashlib.sha256(payload).hexdigest()


def _fingerprint(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _parts(path, *, absolute):
    _require(type(path) is str and bool(path), "invalid path")
    _require(path.startswith("/") is absolute and "\\" not in path,
             "path is outside the fixed relative/absolute contract")
    tokens = path.split("/")[1:] if absolute else path.split("/")
    _require(all(token not in {"", ".", ".."} for token in tokens), "unsafe path component")
    return tokens


def _directory_fd(root, relative=(), *, create=False):
    """Walk each exact component with O_NOFOLLOW; never follow a symlink."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    descriptor = os.open("/", flags)
    try:
        for part in _parts(root, absolute=True):
            child = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        for part in relative:
            if create:
                try:
                    os.mkdir(part, 0o755, dir_fd=descriptor)
                except FileExistsError:
                    pass
            child = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _open_relative(root, relative, *, output=False):
    parts = _parts(relative, absolute=False)
    parent = _directory_fd(root, parts[:-1], create=output)
    try:
        flags = os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
        flags |= (os.O_WRONLY | os.O_CREAT | os.O_EXCL) if output else os.O_RDONLY
        descriptor = os.open(parts[-1], flags, 0o644, dir_fd=parent)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            os.close(descriptor)
            raise CorpusAccessError("only regular files are admitted")
        return descriptor
    finally:
        os.close(parent)


def _path_fingerprint(root, relative):
    parts = _parts(relative, absolute=False)
    parent = _directory_fd(root, parts[:-1])
    try:
        return _fingerprint(os.stat(parts[-1], dir_fd=parent, follow_symlinks=False))
    finally:
        os.close(parent)


def _free_disk(root):
    descriptor = _directory_fd(root)
    try:
        info = os.fstatvfs(descriptor)
        return info.f_bavail * info.f_frsize
    finally:
        os.close(descriptor)


def _hashes(payload):
    _require(type(payload) is bytes and len(payload) == ROW_BYTES,
             "one exact uint8 2x65x65 pair is required")
    return {"structural_patch_sha256": _digest(payload[:CHANNEL_BYTES]),
            "solutal_patch_sha256": _digest(payload[CHANNEL_BYTES:]),
            "pair_sha256": _digest(payload)}


def _validate_rows(rows, phase, kind):
    _require(type(rows) is list and rows, "explicit nonempty frozen row list required")
    allowed = {
        "TRAIN": ({"TRAIN"}, {"GOLD"}),
        "DEVELOPMENT": ({"DEVELOPMENT"}, {"GOLD"}),
        "TRAIN_SILVER": ({"TRAIN"}, {"SILVER"}),
        "FINAL_TRAIN": ({"TRAIN", "DEVELOPMENT"}, {"GOLD", "SILVER"}),
        "TEST": ({"TEST"}, {"GOLD"}),
    }
    if kind == "background":
        _require(phase in CACHE_NAMES, "background phase not authorized")
        splits = {"TRAIN", "DEVELOPMENT"} if phase == "TRAIN_DEVELOPMENT" else {"TEST"}
        tiers = {"BACKGROUND"}
    else:
        _require(phase in allowed, "positive phase not authorized")
        splits, tiers = allowed[phase]
    ids, identities, row_indices = set(), set(), set()
    groups = {}
    result = deepcopy(rows)
    for row in result:
        _require(type(row) is dict, "row must be an explicit mapping")
        _require(row.get("kind") == kind and type(row.get("label")) is int
                 and row["label"] == (1 if kind == "positive" else 0), "kind/label divergence")
        _require(row.get("split") in splits and row.get("tier") in tiers,
                 "split/tier is sealed or not allowed in this phase")
        sid, group = row.get("sample_id"), row.get("group_id")
        _require(type(sid) is str and sid and sid not in ids
                 and type(group) is str and group, "missing or duplicate sample identity")
        ids.add(sid)
        _require(group not in groups or groups[group] == row["split"], "group crosses splits")
        groups[group] = row["split"]
        source = row.get("structural_source_id")
        _require(source in FRAME_COUNTS
                 and row.get("solutal_source_id") == dict(SOURCE_PAIRS)[source]
                 and row.get("acquisition_id") == support.ACQUISITIONS[source], "source/acquisition mismatch")
        frame = row.get("frame_index")
        _require(type(frame) is int and 0 <= frame < FRAME_COUNTS[source], "frame outside frozen extent")
        x, y = row.get("center_x"), row.get("center_y")
        _require(type(x) is int and type(y) is int
                 and row.get("patch_xyxy") == support.patch_xyxy(x, y), "fixed crop/center divergence")
        identity = (group, frame)
        _require(identity not in identities, "duplicate group/frame pair")
        identities.add(identity)
        if kind == "positive":
            index = row.get("positive_row_index")
            _require(type(index) is int and 0 <= index < POSITIVE_ROWS
                     and index not in row_indices, "invalid or duplicate positive row index")
            row_indices.add(index)
            _require(all(_hex(row.get(key)) for key in
                         ("structural_patch_sha256", "solutal_patch_sha256", "pair_sha256")),
                     "all three canonical patch hashes are required")
        else:
            _require(group == f"{row['acquisition_id']}|{x}|{y}", "background track identity changed")
    return result


class CorpusAccess:
    """Inert until a controller grant; no global or historical authorization.

    ``grant(action, phase, rows)`` must return a receipt/head-bound mapping.
    For TEST it additionally attests that the final-fit freeze was written and
    fsynced. The controller checks actual freeze custody and row membership.
    Returned arrays are caller-owned, uint8, and in the supplied manifest order.
    """

    def __init__(self, root, grant=None, audit=None):
        _require(audit is None or (type(audit) is dict and not audit), "audit must be empty")
        self.root, self.grant = os.fspath(root), grant
        self.audit = {} if audit is None else audit
        self.audit.update({"state": "NOT_USED", "positive_container_auth_attempts": 0,
            "positive_container_auth_opens": 0, "positive_container_auth_bytes": 0,
            "positive_selected_row_attempts": 0, "positive_selected_rows_read": 0,
            "positive_selected_row_bytes": 0, "positive_phases": {},
            "background_stages": {}, "background_cache_bytes_written": 0,
            "background_metadata_bytes_written": 0, "temporary_disk_bytes": 0,
            "positive_pixels_written": 0, "full_frames_written": 0,
            "positive_container_auth_scope": "One opaque whole-container authentication after scientific receipt; separate from selected-row tensor access and any earlier integration custody hash.",
            "instrumentation_scope": "Application counters; not universal syscalls or decoder internals."})
        self._positive_fd = None
        self._positive_fingerprint = None
        self._used_ids = set()
        self._positive_phases = set()
        self._background_phases = set()
        self._failed = self._closed = False

    def __enter__(self):
        _require(not self._closed, "access object closed")
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()
        return False

    def close(self):
        if self._positive_fd is not None:
            os.close(self._positive_fd)
            self._positive_fd = None
        self._closed = True
        self.audit["positive_container_fd_closed"] = True
        self.audit["state"] = "CLOSED_FAILED" if self._failed else "CLOSED"

    def _authorize(self, action, phase, rows):
        # No path examination, hashing, native read or output creation precedes this call.
        _require(callable(self.grant), "controller authorization required")
        proof = self.grant(action, phase, rows)
        _require(type(proof) is dict and proof.get("authorized") is True
                 and _hex(proof.get("execution_receipt_sha256"))
                 and _hex(proof.get("method_freeze_sha"), 40), "receipt-bound authorization denied")
        if phase == "TEST":
            _require(proof.get("final_fit_durable") is True
                     and _hex(proof.get("final_fit_freeze_sha256")), "TEST requires durable final-fit freeze")
        _require(not self._closed and not self._failed, "access is closed or failed")
        keys = ("execution_receipt_sha256", "method_freeze_sha")
        if phase == "TEST":
            keys += ("final_fit_durable", "final_fit_freeze_sha256")
        return {key: proof[key] for key in keys}

    def _unchanged(self):
        _require(_fingerprint(os.fstat(self._positive_fd)) == self._positive_fingerprint
                 and _path_fingerprint(self.root, POSITIVE_PATH) == self._positive_fingerprint,
                 "positive container identity or metadata changed")

    def _authenticate_positive(self):
        if self._positive_fd is not None:
            self._unchanged()
            return
        self.audit["positive_container_auth_attempts"] += 1
        self._positive_fd = _open_relative(self.root, POSITIVE_PATH)
        self.audit["positive_container_auth_opens"] += 1
        info = os.fstat(self._positive_fd)
        _require(info.st_size == POSITIVE_BYTES == POSITIVE_ROWS * ROW_BYTES, "positive container size mismatch")
        self._positive_fingerprint = _fingerprint(info)
        checksum = hashlib.sha256()
        while True:
            chunk = os.read(self._positive_fd, HASH_CHUNK_BYTES)
            if not chunk:
                break
            self.audit["positive_container_auth_bytes"] += len(chunk)
            _require(self.audit["positive_container_auth_bytes"] <= POSITIVE_BYTES, "positive container grew during hash")
            checksum.update(chunk)
        _require(self.audit["positive_container_auth_bytes"] == POSITIVE_BYTES
                 and checksum.hexdigest() == POSITIVE_SHA256, "positive container hash mismatch")
        self._unchanged()
        self.audit["positive_container_authenticated_sha256"] = checksum.hexdigest()

    def load_positive_rows(self, rows, phase):
        proof = self._authorize("LOAD_POSITIVE_ROWS", phase, rows)
        selected = _validate_rows(rows, phase, "positive")
        _require(phase not in self._positive_phases, "positive phase already consumed")
        _require(not ({r["sample_id"] for r in selected} & self._used_ids),
                 "reuse existing positive tensors in RAM; do not reread rows")
        self._positive_phases.add(phase)
        record = {"state": "STARTED", "requested_rows": len(selected), "rows_read": 0,
                  "bytes_read": 0, "authorization": proof}
        self.audit["positive_phases"][phase] = record
        try:
            self._authenticate_positive()
            import numpy as np
            pairs = np.empty((len(selected), 2, 65, 65), dtype=np.uint8)
            for ordinal, row in enumerate(selected):
                self._unchanged()
                self.audit["positive_selected_row_attempts"] += 1
                payload = bytearray()
                while len(payload) < ROW_BYTES:
                    part = os.pread(self._positive_fd, ROW_BYTES - len(payload),
                                    row["positive_row_index"] * ROW_BYTES + len(payload))
                    self.audit["positive_selected_row_bytes"] += len(part)
                    record["bytes_read"] += len(part)
                    _require(bool(part), "positive row truncated")
                    payload.extend(part)
                raw = bytes(payload)
                _require(all(row[key] == value for key, value in _hashes(raw).items()),
                         "positive canonical patch hash mismatch")
                pairs[ordinal] = np.frombuffer(raw, dtype=np.uint8).reshape(2, 65, 65)
                self._used_ids.add(row["sample_id"])
                record["rows_read"] += 1
                self.audit["positive_selected_rows_read"] += 1
            self._unchanged()
            record["state"] = "COMPLETED"
            self.audit["state"] = "ACTIVE"
            return pairs
        except BaseException as exc:
            record["state"] = "FAILED"
            record["failure"] = f"{type(exc).__name__}: {exc}"
            self._failed = True
            self.close()
            raise

    def _frame_hashes(self):
        descriptor = _open_relative(self.root, FRAME_HASH_PATH)
        try:
            parts = []
            total = 0
            while True:
                piece = os.read(descriptor, HASH_CHUNK_BYTES)
                if not piece:
                    break
                total += len(piece)
                _require(total <= MAX_METADATA_BYTES, "frame-hash metadata exceeds cap")
                parts.append(piece)
        finally:
            os.close(descriptor)
        payload = b"".join(parts)
        _require(_digest(payload) == FRAME_HASH_SHA256, "frozen B frame-hash custody mismatch")
        expected = {}
        for row in json.loads(payload):
            source, frame = row["structural_source"], row["frame_index"]
            _require(source in FRAME_COUNTS and row["solute_source"] == dict(SOURCE_PAIRS)[source]
                     and type(frame) is int and 0 <= frame < FRAME_COUNTS[source], "invalid B frame identity")
            key = (source, frame)
            _require(key not in expected and _hex(row["structural_frame_sha256"])
                     and _hex(row["solute_frame_sha256"]), "invalid B frame-hash entry")
            expected[key] = (row["structural_frame_sha256"], row["solute_frame_sha256"])
        _require(len(expected) == sum(FRAME_COUNTS.values()), "incomplete frozen frame-hash coverage")
        return expected

    def _write_cache(self, selected, pairs, phase, record):
        names = CACHE_NAMES[phase]
        files, manifests = [], []
        record["artifacts"] = manifests
        checksums = []
        try:
            for name in names:
                relative = "data/derived/study2c/" + name
                descriptor = _open_relative(self.root, relative, output=True)
                files.append(descriptor)
                manifests.append({"path": relative, "size_bytes": 0, "record_count": 0,
                                  "sha256": _digest(b""), "complete": False, "git_status": "LOCAL_IGNORED"})
                checksums.append(hashlib.sha256())
            metadata = []
            for index, row in enumerate(selected):
                payload = pairs[index].tobytes(order="C")
                entry = {**row, **_hashes(payload), "cache_row_index": index,
                         "cache_path": manifests[0]["path"], "dtype": "uint8",
                         "shape": [2, 65, 65], "support_status": "PASS_MARGIN3"}
                line = (json.dumps(entry, sort_keys=True, separators=(",", ":"),
                                   allow_nan=False) + "\n").encode("utf-8")
                for file_index, content in enumerate((payload, line)):
                    counter = "background_cache_bytes_written" if file_index == 0 else "background_metadata_bytes_written"
                    cap = MAX_CACHE_BYTES if file_index == 0 else MAX_METADATA_BYTES
                    _require(self.audit[counter] + len(content) <= cap, "aggregate cache/metadata cap exceeded")
                    _require(_free_disk(self.root) - len(content) >= MIN_FREE_BYTES, "free-disk reserve exceeded")
                    amount = os.write(files[file_index], content)
                    self.audit[counter] += amount
                    manifests[file_index]["size_bytes"] += amount
                    checksums[file_index].update(content[:amount])
                    manifests[file_index]["sha256"] = checksums[file_index].hexdigest()
                    _require(amount == len(content), "short cache write")
                    manifests[file_index]["record_count"] += 1
                metadata.append(entry)
            for descriptor in files:
                os.fsync(descriptor)
            parent = _directory_fd(self.root, ("data", "derived", "study2c"))
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
            for index, item in enumerate(manifests):
                item.update({"sha256": checksums[index].hexdigest(), "complete": True})
            return {"artifacts": manifests, "rows": metadata,
                    "container": {"format": "HEADERLESS_C_CONTIGUOUS_UINT8",
                                  "shape": [len(selected), 2, 65, 65], "dtype": "uint8",
                                  "row_bytes": ROW_BYTES, "order": "FROZEN_SUPPLIED_ROW_ORDER"}}
        finally:
            for descriptor in files:
                os.close(descriptor)

    def _output_slots_absent(self, phase):
        for filename in CACHE_NAMES[phase]:
            try:
                _path_fingerprint(self.root, "data/derived/study2c/" + filename)
            except FileNotFoundError:
                continue
            raise CorpusAccessError("refuse existing background cache or ledger")

    def materialize_backgrounds(self, rows, phase):
        proof = self._authorize("MATERIALIZE_BACKGROUNDS", phase, rows)
        selected = _validate_rows(rows, phase, "background")
        _require(phase not in self._background_phases, "background stage already consumed")
        _require(not ({r["sample_id"] for r in selected} & self._used_ids), "background sample already materialized")
        self._background_phases.add(phase)
        record = {"state": "STARTED", "requested_rows": len(selected), "pairs_materialized": 0,
                  "authorization": proof, "streaming": {}, "temporary_disk_bytes": 0}
        self.audit["background_stages"][phase] = record
        try:
            required = len(selected) * ROW_BYTES
            _require(self.audit["background_cache_bytes_written"] + required <= MAX_CACHE_BYTES,
                     "aggregate background cache cap exceeded before decoding")
            self._output_slots_absent(phase)
            expected = self._frame_hashes()
            _require(_free_disk(self.root) - required >= MIN_FREE_BYTES,
                     "free-disk reserve insufficient before decoding")
            import numpy as np
            pairs = np.empty((len(selected), 2, 65, 65), dtype=np.uint8)
            by_frame = defaultdict(list)
            for ordinal, row in enumerate(selected):
                by_frame[(row["structural_source_id"], row["frame_index"])].append((ordinal, row))
            completed = set()
            with AuthenticatedSources(mode="full", audit=record["streaming"]) as reader:
                for structural, solutal in SOURCE_PAIRS:
                    count = 0
                    for first, second in zip(reader.iter_frames(structural), reader.iter_frames(solutal), strict=True):
                        frame, sraw, sh = first
                        qframe, qraw, qh = second
                        _require(frame == qframe == count and frame < FRAME_COUNTS[structural],
                                 "native modalities lost frozen frame synchronization")
                        _require((sh, qh) == expected[(structural, frame)]
                                 and (_digest(sraw), _digest(qraw)) == (sh, qh),
                                 "native frame hash differs from frozen Study2-B")
                        count += 1
                        requests = by_frame.get((structural, frame), ())
                        if requests:
                            sy, sm = support.native_luminance_and_support(sraw, structural, structural=True)
                            qy, qm = support.native_luminance_and_support(qraw, structural, structural=False)
                            width, height = support.DIMENSIONS[structural]
                            for ordinal, row in requests:
                                x0, y0, x1, y1 = row["patch_xyxy"]
                                safety = [x0 - 3, y0 - 3, x1 + 3, y1 + 3]
                                _require(support._admitted(safety, sm, width, height)
                                         and support._admitted(safety, qm, width, height),
                                         "selected background lost frozen support; no replacement")
                                pair = np.stack((sy[y0:y1, x0:x1], qy[y0:y1, x0:x1]), axis=0)
                                _require(pair.shape == (2, 65, 65) and pair.dtype == np.dtype("uint8"),
                                         "native patch shape/dtype mismatch; no padding or resize")
                                pairs[ordinal] = pair
                                completed.add(ordinal)
                                record["pairs_materialized"] += 1
                            del sy, sm, qy, qm, pair
                        del first, second, sraw, qraw
                    _require(count == FRAME_COUNTS[structural], "native frame count incomplete")
            _require(len(completed) == len(selected), "selected background rows missing")
            manifest = self._write_cache(selected, pairs, phase, record)
            self._used_ids.update(r["sample_id"] for r in selected)
            record.update({"state": "COMPLETED", "channel_patches_written": len(selected) * 2,
                           "cache_bytes": required, "positive_rows_redecoded": 0})
            self.audit["state"] = "ACTIVE"
            return pairs, manifest
        except BaseException as exc:
            record["state"] = "FAILED"
            record["failure"] = f"{type(exc).__name__}: {exc}"
            self._failed = True
            self.close()
            raise
