"""TI3-B receipt and exact paired TRAIN/DEV I/O; no array processing or fitting.

TI3-A's consumed authority is never rearmed. All FINAL records are textual
inventory only. Admission denies them before inspecting a path or filesystem.
"""

import copy
from datetime import datetime, timezone
import hashlib
import json
import os
import stat

from snbi_fragmentation.ti3_dataset import validate_manifest


BASE = "artifacts/evidence/TI3_B_SOLUTAL"
RECEIPT_PATH = BASE + "/execution-receipt.json"
TERMINAL_PATH = BASE + "/results.json"
PAIR_SOURCE = {"ESM1": "ESM2", "ESM4": "ESM5"}
STRUCTURAL_FRAMES = {
    ("ESM1", 73): "TRAIN", ("ESM1", 146): "TRAIN", ("ESM4", 98): "TRAIN",
    ("ESM1", 219): "DEVELOPMENT", ("ESM4", 197): "DEVELOPMENT",
}
ALLOWED_FRAMES = dict(STRUCTURAL_FRAMES)
ALLOWED_FRAMES.update({(PAIR_SOURCE[s], i): p for (s, i), p in STRUCTURAL_FRAMES.items()})
SEALED_FRAMES = frozenset({("ESM1", 293), ("ESM2", 293), ("ESM4", 295), ("ESM5", 295)})
DIMENSIONS = {"ESM1": (1278, 1018), "ESM2": (1278, 1018),
              "ESM4": (1278, 1012), "ESM5": (1278, 1012)}
AUTHORITY_FIELDS = {"state", "head_sha", "manifest_sha256", "inventory_sha256",
                    "method_freeze_sha256", "scientific_invocation_limit"}
_ARM_TOKEN = object()


class ExecutionContractError(ValueError):
    """An execution boundary violation, expressed without private paths."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(condition, code):
    if not condition:
        raise ExecutionContractError(code)


def exact(left, right):
    """Compare JSON values recursively without accepting bool/int/float coercion."""
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(exact(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(exact(a, b) for a, b in zip(left, right))
    return left == right


def digest_string(value, length=64):
    return type(value) is str and len(value) == length and all(c in "0123456789abcdef" for c in value)


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def validate_admission(record):
    """Reject FINAL/source/frame/split before querying the path field."""
    require(isinstance(record, dict), "SOURCE_METADATA_REQUIRED")
    require(record.get("split") in ("TRAIN", "DEVELOPMENT"), "FINAL_OR_UNKNOWN_SPLIT_DENIED")
    source, frame = record.get("source_id"), record.get("frame_index")
    require(type(source) is str and source in DIMENSIONS, "SOURCE_NOT_AUTHORIZED")
    require(type(frame) is int and (source, frame) in ALLOWED_FRAMES, "FRAME_NOT_AUTHORIZED")
    require(ALLOWED_FRAMES[(source, frame)] == record["split"], "FRAME_SPLIT_MISMATCH")
    require(record.get("path") == f"data/derived/ti2-pilot/{source}-{frame:04d}.raw", "NATIVE_PATH_MISMATCH")
    width, height = DIMENSIONS[source]
    expected = {"width": width, "height": height, "frame_bytes": width * height * 3 // 2,
                "bit_depth": 8, "pixel_format": "yuv420p", "plane": "Y",
                "y_plane": {"name": "Y", "offset": 0, "bytes": width * height,
                            "width": width, "height": height}}
    require(all(exact(record.get(k), v) for k, v in expected.items()), "NATIVE_LAYOUT_MISMATCH")
    require(digest_string(record.get("image_sha256")), "NATIVE_HASH_REQUIRED")
    return source, frame


def build_inventory(manifest, pilot):
    """Bind the seven original structural records to seven exact solutal peers.

    This performs textual joins only, never source metadata probing. Four FINAL
    records stay sealed; their appearance here grants no read authority.
    """
    validate_manifest(manifest)
    require(type(pilot) is dict and type(pilot.get("images")) is list, "PILOT_SCHEMA_MISMATCH")
    images = {}
    for image in pilot["images"]:
        key = (image.get("source_id"), image.get("frame_index"))
        require(key not in images, "DUPLICATE_PILOT_IMAGE")
        images[key] = image
    inventory = []
    for structural in manifest["source_inventory"]:
        source, frame = structural["source_id"], structural["frame_index"]
        require(source in PAIR_SOURCE, "STRUCTURAL_SOURCE_DIVERGENCE")
        for paired in (source, PAIR_SOURCE[source]):
            image = images.get((paired, frame))
            require(image is not None, "PAIRED_PILOT_IMAGE_MISSING")
            expected = {k: structural[k] for k in ("width", "height", "frame_bytes", "pixel_format", "bit_depth")}
            require(all(exact(image.get(k), v) for k, v in expected.items()), "PAIRED_LAYOUT_DIVERGENCE")
            require(image.get("experiment_id") == structural["acquisition_id"], "PAIRED_ACQUISITION_DIVERGENCE")
            require(type(image.get("planes")) is list and image["planes"]
                    and exact(image["planes"][0], structural["y_plane"]), "PAIRED_Y_PLANE_DIVERGENCE")
            record = copy.deepcopy(structural)
            record.update(source_id=paired, path=image["path"], image_sha256=image["image_sha256"])
            if paired == source:
                require(exact(record, structural), "STRUCTURAL_PILOT_DIVERGENCE")
            inventory.append(record)
    validate_inventory(inventory)
    return inventory


def validate_inventory(inventory):
    require(type(inventory) is list and len(inventory) == 14, "INVENTORY_SIZE_MISMATCH")
    seen = set()
    for record in inventory:
        require(type(record) is dict, "INVENTORY_RECORD_REQUIRED")
        source, frame = record.get("source_id"), record.get("frame_index")
        require(type(source) is str and type(frame) is int, "INVENTORY_ID_TYPE_MISMATCH")
        key = (source, frame)
        require(key not in seen, "DUPLICATE_INVENTORY_RECORD")
        seen.add(key)
        if key in SEALED_FRAMES:
            require(record.get("split") == "FINAL_TEST", "FINAL_SPLIT_DIVERGENCE")
        else:
            validate_admission(record)
    require(seen == set(ALLOWED_FRAMES) | set(SEALED_FRAMES), "INVENTORY_ALLOWLIST_MISMATCH")


def _parent_fd(root_fd, relative):
    parts = relative.split("/")
    require(all(p and p not in (".", "..") for p in parts), "RELATIVE_PATH_REQUIRED")
    current = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current)
            os.close(current)
            current = child
        return current, parts[-1]
    except BaseException:
        os.close(current)
        raise


def _exists(parent_fd, name):
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        return True
    except FileNotFoundError:
        return False


def arm_execution(root, manifest_bytes, inventory, authority, head):
    """Consume a new exclusive receipt after the caller's B1/CI preflight."""
    require(type(manifest_bytes) is bytes, "EXACT_MANIFEST_BYTES_REQUIRED")
    require(type(authority) is dict and set(authority) == AUTHORITY_FIELDS, "CUSTODY_SCHEMA_MISMATCH")
    require(authority.get("state") == "ARMED_ONCE", "CUSTODY_NOT_ARMED_ONCE")
    require(type(authority.get("scientific_invocation_limit")) is int
            and authority["scientific_invocation_limit"] == 1, "INVOCATION_LIMIT_MISMATCH")
    require(digest_string(head, 40) and authority.get("head_sha") == head, "B1_HEAD_MISMATCH")
    require(authority.get("manifest_sha256") == hashlib.sha256(manifest_bytes).hexdigest(), "MANIFEST_HASH_MISMATCH")
    require(digest_string(authority.get("method_freeze_sha256")), "METHOD_FREEZE_HASH_REQUIRED")
    try:
        manifest = json.loads(manifest_bytes)
        validate_manifest(manifest)
    except (ValueError, TypeError, KeyError, AttributeError):
        raise ExecutionContractError("MANIFEST_CONTRACT_FAILED") from None
    validate_inventory(inventory)
    structural = [r for r in inventory if r["source_id"] in PAIR_SOURCE]
    require(exact(structural, manifest["source_inventory"]), "STRUCTURAL_INVENTORY_DIVERGENCE")
    require(authority.get("inventory_sha256") == hashlib.sha256(canonical_bytes(inventory)).hexdigest(), "INVENTORY_HASH_MISMATCH")
    allowed = {(r["source_id"], r["frame_index"]): r for r in inventory if r["split"] != "FINAL_TEST"}
    root_fd = parent_fd = receipt_fd = None
    try:
        root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        parent_fd, name = _parent_fd(root_fd, RECEIPT_PATH)
        require(not _exists(parent_fd, TERMINAL_PATH.rsplit("/", 1)[1]), "TERMINAL_ALREADY_EXISTS")
        require(not _exists(parent_fd, name), "RECEIPT_ALREADY_EXISTS")
        receipt = {"schema": "TI3B-EXECUTION-RECEIPT-1", "state": "CONSUMED_BEFORE_NATIVE_BYTES",
                   "timestamp_utc": datetime.now(timezone.utc).isoformat(), "head_sha": head,
                   "authority": copy.deepcopy(authority), "scientific_invocation": 1,
                   "experimental_opens_at_receipt": 0, "experimental_bytes_at_receipt": 0,
                   "allowed_source_frames": [[s, f] for s, f in sorted(allowed)]}
        receipt_fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                             0o600, dir_fd=parent_fd)
        payload = memoryview(canonical_bytes(receipt) + b"\n")
        while payload:
            count = os.write(receipt_fd, payload)
            require(count > 0, "RECEIPT_WRITE_INCOMPLETE")
            payload = payload[count:]
        os.fsync(receipt_fd)
        os.close(receipt_fd)
        receipt_fd = None
        os.fsync(parent_fd)
        reader = NativeReader(_ARM_TOKEN, root_fd, inventory, allowed)
        root_fd = None
        return reader
    except OSError:
        raise ExecutionContractError("RECEIPT_OR_REPOSITORY_IO_FAILED") from None
    finally:
        for fd in (receipt_fd, parent_fd, root_fd):
            if fd is not None:
                os.close(fd)


class NativeReader:
    """At most one read per admitted native buffer; failures poison the reader."""

    def __init__(self, token, root_fd, inventory, allowed):
        require(token is _ARM_TOKEN, "EXCLUSIVE_RECEIPT_REQUIRED")
        self._root_fd, self._allowed = root_fd, copy.deepcopy(allowed)
        self._failed = self._closed = False
        self._attempted = set()
        self._entries = {(r["source_id"], r["frame_index"]): {
            "source_id": r["source_id"], "frame_index": r["frame_index"], "split": r["split"],
            "expected_bytes": r["frame_bytes"], "expected_sha256": r["image_sha256"],
            "status": "NOT_OPENED", "open_attempts": 0, "opens": 0, "bytes_read": 0,
            "bytes_read_sha256": None, "verified": False} for r in inventory}

    def read_native(self, record):
        key = validate_admission(record)
        require(not self._closed and not self._failed, "READER_CLOSED_OR_FAILED")
        require(key not in self._attempted, "SOURCE_ALREADY_ATTEMPTED")
        expected = self._allowed.get(key)
        require(expected is not None and exact(record, expected), "FROZEN_SOURCE_METADATA_MISMATCH")
        self._attempted.add(key)
        entry = self._entries[key]
        entry["status"] = "ATTEMPTED"
        parent_fd = source_fd = None
        digest, chunks = hashlib.sha256(), []
        try:
            terminal_parent, terminal_name = _parent_fd(self._root_fd, TERMINAL_PATH)
            try:
                require(not _exists(terminal_parent, terminal_name), "TERMINAL_ALREADY_EXISTS")
            finally:
                os.close(terminal_parent)
            parent_fd, name = _parent_fd(self._root_fd, expected["path"])
            entry["open_attempts"] += 1
            source_fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=parent_fd)
            entry["opens"] += 1
            metadata = os.fstat(source_fd)
            require(stat.S_ISREG(metadata.st_mode), "NATIVE_SOURCE_NOT_REGULAR")
            limit = expected["frame_bytes"]
            require(metadata.st_size == limit, "NATIVE_BYTE_COUNT_MISMATCH")
            while entry["bytes_read"] < limit:
                chunk = os.read(source_fd, min(1024 * 1024, limit - entry["bytes_read"]))
                if not chunk:
                    break
                entry["bytes_read"] += len(chunk)
                digest.update(chunk)
                chunks.append(chunk)
            require(entry["bytes_read"] == limit and os.fstat(source_fd).st_size == limit, "NATIVE_BYTE_COUNT_MISMATCH")
            require(digest.hexdigest() == expected["image_sha256"], "NATIVE_HASH_MISMATCH")
            entry.update(verified=True, status="READ_ONCE_VERIFIED")
            return b"".join(chunks)
        except (ExecutionContractError, OSError) as error:
            self._failed = True
            entry.update(status="FAILED", error_code=getattr(error, "code", "NATIVE_IO_FAILED"))
            raise ExecutionContractError(entry["error_code"]) from None
        finally:
            if entry["opens"]:
                entry["bytes_read_sha256"] = digest.hexdigest()
            for fd in (source_fd, parent_fd):
                if fd is not None:
                    os.close(fd)

    def report(self):
        entries = [copy.deepcopy(self._entries[k]) for k in sorted(self._entries)]
        def count(field, predicate):
            return sum(r[field] for r in entries if predicate(r))
        result = {"schema": "TI3B-NATIVE-IO-AUDIT-1", "receipt_invocations": 1,
                  "source_open_attempts": count("open_attempts", lambda r: True),
                  "experimental_opens": count("opens", lambda r: True),
                  "experimental_bytes": count("bytes_read", lambda r: True),
                  "failed": self._failed, "closed": self._closed, "entries": entries}
        for name, sources in (("structural", {"ESM1", "ESM4"}), ("solutal", {"ESM2", "ESM5"})):
            predicate = lambda r: r["source_id"] in sources
            final = lambda r: r["source_id"] in sources and r["split"] == "FINAL_TEST"
            result[name + "_opens"] = count("opens", predicate)
            result[name + "_bytes"] = count("bytes_read", predicate)
            result["final_" + name + "_opens"] = count("opens", final)
            result["final_" + name + "_bytes"] = count("bytes_read", final)
        result["final_test_opens"] = count("opens", lambda r: r["split"] == "FINAL_TEST")
        result["final_test_bytes"] = count("bytes_read", lambda r: r["split"] == "FINAL_TEST")
        return result

    def close(self):
        if not self._closed:
            os.close(self._root_fd)
            self._closed = True
