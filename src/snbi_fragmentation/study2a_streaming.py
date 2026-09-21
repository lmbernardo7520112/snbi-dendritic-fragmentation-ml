"""Bounded native streaming for the two Study 2A annotation sources.

Import and construction perform no I/O. The controller must establish its
authority/receipt before entering ``AuthenticatedSources``. Both source hashes
are checked before a decoder can start. Historical mode emits only its ten
frozen fixtures; FFmpeg may internally decode intervening frames as separately
authorized, but those frames never reach Python or the annotation detector.

Counters describe this application, not universal system calls or FFmpeg's
internal compressed-byte reads. No image, patch or temporary file is written.
"""

from dataclasses import dataclass
import hashlib
import math
import os
import selectors
import stat
import subprocess
import time
from types import MappingProxyType


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    path: str
    size_bytes: int
    sha256: str
    width: int
    height: int
    frame_count: int
    historical_indices: tuple

    @property
    def frame_bytes(self):
        return self.width * self.height * 3 // 2


_DIRECTORY = (
    "/home/leonardomaximinobernardo/Downloads/trabalho_Final_IfGoiano/"
    "videos_trabalho_Final_IfGoiano"
)
SOURCES = MappingProxyType({
    "ESM3": SourceSpec(
        "ESM3", _DIRECTORY + "/11837_2015_1646_MOESM3_ESM.mp4", 3356196,
        "d76a6466e50480a2116bc545a0ee2b8095cc14c54f861ecebee87de5b64e35be",
        1280, 1024, 294, (0, 73, 146, 219, 293)),
    "ESM6": SourceSpec(
        "ESM6", _DIRECTORY + "/11837_2015_1646_MOESM6_ESM.mp4", 4353042,
        "5b8747758afde34fb626f3c4ffbd0b49ba6ca6f6b49bfa81b8cf9ee8459280ea",
        1280, 1012, 395, (0, 98, 197, 295, 394)),
})
SOURCE_ORDER = ("ESM3", "ESM6")
FFMPEG = "/usr/bin/ffmpeg"
STDERR_LIMIT_BYTES = 65536
HASH_CHUNK_BYTES = 1048576
DEFAULT_TIMEOUT_SECONDS = 3600.0


class StreamingContractError(RuntimeError):
    """A bounded source, integrity or decoding failure, with a stable code."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _require(condition, code):
    if not condition:
        raise StreamingContractError(code)


def source_spec(source_id):
    """Reject IDs before examining any filesystem path."""
    _require(type(source_id) is str and source_id in SOURCES,
             "SOURCE_NOT_AUTHORIZED")
    return SOURCES[source_id]


def _mode(mode):
    _require(type(mode) is str and mode in ("legacy", "full"),
             "DECODER_MODE_NOT_AUTHORIZED")


def _parent_fd(path):
    """Traverse exact directory components using no-follow directory FDs."""
    _require(path.startswith("/") and ".." not in path.split("/"),
             "SOURCE_PATH_INVALID")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    descriptor = os.open("/", flags)
    try:
        for component in path.split("/")[1:-1]:
            _require(bool(component) and component != ".", "SOURCE_PATH_INVALID")
            child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _open_source(spec):
    _require(spec is source_spec(spec.source_id), "SOURCE_SPEC_NOT_CANONICAL")
    parent = _parent_fd(spec.path)
    try:
        return os.open(spec.path.rsplit("/", 1)[1],
                       os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                       dir_fd=parent)
    finally:
        os.close(parent)


def _stat_source(spec):
    parent = _parent_fd(spec.path)
    try:
        return os.stat(spec.path.rsplit("/", 1)[1], dir_fd=parent,
                       follow_symlinks=False)
    finally:
        os.close(parent)


def _fingerprint(value):
    # atime is deliberately excluded: an authorized read may update it.
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _unchanged(spec, descriptor, original):
    _require(_fingerprint(os.fstat(descriptor)) == original,
             "SOURCE_METADATA_CHANGED")
    _require(_fingerprint(_stat_source(spec)) == original,
             "SOURCE_PATH_IDENTITY_CHANGED")


def decoder_command(source_id, descriptor, mode):
    """Return fixed native-output arguments; no shell or source-path reopen."""
    spec = source_spec(source_id)
    _mode(mode)
    _require(type(descriptor) is int and descriptor >= 0, "SOURCE_FD_INVALID")
    command = [FFMPEG, "-nostdin", "-v", "error", "-threads", "1",
               "-noautorotate", "-i", f"/proc/self/fd/{descriptor}",
               "-map", "0:v:0", "-an", "-sn", "-dn"]
    if mode == "legacy":
        expression = "+".join(f"eq(n\\,{index})" for index in spec.historical_indices)
        command += ["-vf", "select=" + expression]
    command += ["-fps_mode", "passthrough"]
    if mode == "legacy":
        command += ["-frames:v", str(len(spec.historical_indices))]
    command += ["-pix_fmt", "yuv420p", "-threads", "1", "-f", "rawvideo", "pipe:1"]
    return command


def _native_frames(process, frame_bytes, expected_count, record, timeout_seconds):
    """Drain both pipes concurrently; bound one assembled frame and stderr.

    The deadline covers the subprocess lifetime, including consumer processing
    time between yields. Extra full frames and partial trailing frames fail.
    """
    selector = selectors.DefaultSelector()
    assembled = bytearray()
    stderr = bytearray()
    count = 0
    deadline = time.monotonic() + timeout_seconds
    try:
        for stream, name in ((process.stdout, "stdout"), (process.stderr, "stderr")):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map():
            remaining = deadline - time.monotonic()
            _require(remaining > 0, "DECODER_TIMEOUT")
            events = selector.select(min(remaining, 1.0))
            for key, _ in events:
                maximum = 65536 if key.data == "stderr" else min(65536, frame_bytes - len(assembled))
                try:
                    chunk = os.read(key.fileobj.fileno(), maximum)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                if key.data == "stderr":
                    record["decoder_stderr_bytes"] += len(chunk)
                    stderr.extend(chunk[:max(0, STDERR_LIMIT_BYTES - len(stderr))])
                    continue
                record["native_bytes_received"] += len(chunk)
                assembled.extend(chunk)
                if len(assembled) == frame_bytes:
                    _require(count < expected_count, "DECODE_FRAME_COUNT_EXCEEDED")
                    frame = bytes(assembled)
                    assembled.clear()
                    count += 1
                    yield frame
                    del frame
        remaining = deadline - time.monotonic()
        _require(remaining > 0, "DECODER_TIMEOUT")
        try:
            exit_code = process.wait(timeout=min(remaining, 5.0))
        except subprocess.TimeoutExpired as exc:
            raise StreamingContractError("DECODER_TIMEOUT") from exc
        record["decoder_exit_code"] = exit_code
        _require(exit_code == 0, "DECODER_EXIT_FAILURE")
        _require(not assembled, "DECODE_TRUNCATED_FRAME")
        _require(count == expected_count, "DECODE_FRAME_COUNT_MISMATCH")
    finally:
        record["trailing_partial_bytes"] = len(assembled)
        record["decoder_stderr"] = stderr.decode("utf-8", errors="replace")
        record["decoder_stderr_truncated"] = record["decoder_stderr_bytes"] > len(stderr)
        selector.close()


class AuthenticatedSources:
    """Authenticate both sources, retain their FDs and consume each once.

    No user-supplied paths, dimensions, hashes or frame indices are accepted.
    Source authorization and decoder opens are separate counters. The decoder
    opens a seekable inherited FD through procfs, never the source pathname.
    """

    def __init__(self, mode, audit=None, timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
        _mode(mode)
        _require(type(timeout_seconds) in (int, float)
                 and math.isfinite(timeout_seconds) and 0 < timeout_seconds <= 3600,
                 "DECODER_TIMEOUT_INVALID")
        _require(audit is None or (type(audit) is dict and not audit),
                 "AUDIT_MUST_BE_EMPTY_MAPPING")
        self.mode = mode
        self.timeout_seconds = float(timeout_seconds)
        self.audit = {} if audit is None else audit
        self.audit.update({
            "mode": mode, "state": "NOT_ENTERED", "sources": {},
            "source_auth_attempts": 0, "source_auth_opens": 0,
            "source_auth_bytes_read": 0, "decoder_launch_attempts": 0,
            "decoder_launches": 0, "frames_emitted": 0,
            "decoder_input_open_requests": 0,
            "both_sources_authenticated": False,
            "native_bytes_emitted": 0, "source_path_reopens_by_python": 0,
            "resident_application_frame_window": 3,
            "frame_window_note": "Conservative three native payloads: mutable assembly, immutable copy and prior consumer frame; detector memory excluded.",
            "decoder_compressed_bytes_read": None,
            "internal_intermediate_decode_count": None,
            "historical_intermediate_frames_delivered": 0 if mode == "legacy" else None,
            "instrumentation_scope": "Application counters, not universal syscalls or decoder internal reads.",
            "frames_written": 0, "patches_written": 0, "temporary_bytes_written": 0,
        })
        self._fds = {}
        self._fingerprints = {}
        self._consumed = set()
        self._active = None
        self._entered = False
        self._closed = False
        self._failed = False

    def __enter__(self):
        _require(not self._entered and not self._closed, "SOURCE_READER_ALREADY_USED")
        self._entered = True
        self.audit["state"] = "AUTHENTICATING"
        try:
            for source_id in SOURCE_ORDER:
                spec = source_spec(source_id)
                record = {
                    "source_id": source_id, "source_path": spec.path,
                    "expected_source_bytes": spec.size_bytes,
                    "expected_sha256": spec.sha256, "actual_sha256": None,
                    "auth_bytes_read": 0, "state": "AUTHENTICATING",
                    "frames_emitted": 0, "native_bytes_emitted": 0,
                    "native_bytes_received": 0, "decoder_stderr_bytes": 0,
                    "decoder_exit_code": None, "frame_sha256": [],
                }
                self.audit["sources"][source_id] = record
                self.audit["source_auth_attempts"] += 1
                descriptor = _open_source(spec)
                self._fds[source_id] = descriptor
                self.audit["source_auth_opens"] += 1
                metadata = os.fstat(descriptor)
                _require(stat.S_ISREG(metadata.st_mode), "SOURCE_NOT_REGULAR")
                _require(metadata.st_size == spec.size_bytes, "SOURCE_SIZE_MISMATCH")
                original = _fingerprint(metadata)
                self._fingerprints[source_id] = original
                digest = hashlib.sha256()
                while True:
                    chunk = os.read(descriptor, HASH_CHUNK_BYTES)
                    if not chunk:
                        break
                    record["auth_bytes_read"] += len(chunk)
                    self.audit["source_auth_bytes_read"] += len(chunk)
                    _require(record["auth_bytes_read"] <= spec.size_bytes,
                             "SOURCE_SIZE_CHANGED_DURING_HASH")
                    digest.update(chunk)
                record["actual_sha256"] = digest.hexdigest()
                _require(record["auth_bytes_read"] == spec.size_bytes, "SOURCE_SIZE_MISMATCH")
                _require(record["actual_sha256"] == spec.sha256, "SOURCE_HASH_MISMATCH")
                _unchanged(spec, descriptor, original)
                os.lseek(descriptor, 0, os.SEEK_SET)
                record["state"] = "AUTHENTICATED_NOT_DECODED"
            self.audit["both_sources_authenticated"] = True
            self.audit["state"] = "AUTHENTICATED"
            return self
        except BaseException as exc:
            record["state"] = "AUTHENTICATION_FAILED"
            record["failure"] = getattr(exc, "code", type(exc).__name__)
            self.audit["state"] = "AUTHENTICATION_FAILED"
            self.audit["failure"] = getattr(exc, "code", type(exc).__name__)
            self.close()
            raise

    def iter_frames(self, source_id):
        spec = source_spec(source_id)
        _require(self._entered and not self._closed
                 and not self._failed
                 and self.audit.get("both_sources_authenticated") is True,
                 "SOURCE_READER_NOT_AUTHENTICATED")
        _require(source_id not in self._consumed, "SOURCE_STREAM_ALREADY_CONSUMED")
        _require(self._active is None, "CONCURRENT_SOURCE_STREAM_DENIED")
        self._consumed.add(source_id)
        self.audit["sources"][source_id]["state"] = "RESERVED_NOT_STARTED"
        self._active = self._stream(spec)
        return self._active

    def _stream(self, spec):
        record = self.audit["sources"][spec.source_id]
        descriptor = self._fds[spec.source_id]
        process = None
        native = None
        completed = False
        try:
            _unchanged(spec, descriptor, self._fingerprints[spec.source_id])
            os.lseek(descriptor, 0, os.SEEK_SET)
            command = decoder_command(spec.source_id, descriptor, self.mode)
            record["decoder_command"] = command
            self.audit["decoder_launch_attempts"] += 1
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       pass_fds=(descriptor,), close_fds=True, bufsize=0)
            self.audit["decoder_launches"] += 1
            self.audit["decoder_input_open_requests"] += 1
            record["state"] = "DECODING"
            indices = (spec.historical_indices if self.mode == "legacy"
                       else range(spec.frame_count))
            native = _native_frames(process, spec.frame_bytes, len(indices),
                                    record, self.timeout_seconds)
            for ordinal, raw in enumerate(native):
                index = indices[ordinal]
                digest = hashlib.sha256(raw).hexdigest()
                record["frames_emitted"] += 1
                record["native_bytes_emitted"] += len(raw)
                record["frame_sha256"].append({"frame_index": index, "sha256": digest})
                self.audit["frames_emitted"] += 1
                self.audit["native_bytes_emitted"] += len(raw)
                yield index, raw, digest
                del raw
            _unchanged(spec, descriptor, self._fingerprints[spec.source_id])
            record["metadata_unchanged_after_decode"] = True
            record["state"] = "COMPLETED"
            completed = True
        except GeneratorExit:
            self._failed = True
            record["state"] = "CONSUMER_STOPPED_BEFORE_EOF"
            raise
        except BaseException as exc:
            self._failed = True
            record["state"] = "FAILED"
            record["failure"] = getattr(exc, "code", type(exc).__name__)
            self.audit["failure"] = record["failure"]
            raise
        finally:
            if native is not None:
                native.close()
            if process is not None:
                if process.poll() is None:
                    try:
                        process.kill()
                    except ProcessLookupError:
                        pass
                try:
                    process.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    record["cleanup_failure"] = "DECODER_KILL_WAIT_TIMEOUT"
                record["decoder_exit_code"] = process.returncode
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        stream.close()
            if not completed:
                self.audit["state"] = "DECODE_INCOMPLETE"
            self._active = None

    def close(self):
        if self._closed:
            return
        if self._active is not None:
            self._active.close()
            self._active = None
        for descriptor in self._fds.values():
            os.close(descriptor)
        self._fds.clear()
        self._closed = True
        self.audit["source_fds_closed"] = True
        if self.audit.get("both_sources_authenticated") is True:
            complete = all(self.audit["sources"][s]["state"] == "COMPLETED"
                           for s in SOURCE_ORDER)
            self.audit["state"] = "CLOSED_COMPLETE" if complete else "CLOSED_INCOMPLETE"

    def __exit__(self, exception_type, exception, traceback):
        self.close()
        return False
