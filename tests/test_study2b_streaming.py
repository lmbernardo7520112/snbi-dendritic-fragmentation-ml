"""Synthetic source custody and bounded paired pipes; never invoke FFmpeg."""

from contextlib import ExitStack
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import MappingProxyType, SimpleNamespace
import unittest
from unittest import mock

from snbi_fragmentation import study2b_streaming as streaming


def metadata(size, inode):
    return SimpleNamespace(st_dev=1, st_ino=inode, st_mode=stat.S_IFREG | 0o444,
                           st_nlink=1, st_size=size, st_mtime_ns=1, st_ctime_ns=1)


def process_fixture(running=False):
    process = mock.Mock()
    process.poll.return_value = None if running else 0
    process.returncode = 0
    process.wait.return_value = 0
    return process


def native_payloads(process, frame_bytes, count, record, timeout):
    del process, timeout
    for ordinal in range(count):
        record["native_bytes_received"] += frame_bytes
        yield bytes([ordinal % 256]) * frame_bytes
    record["decoder_exit_code"] = 0


class SyntheticAuthentication:
    """Tiny replacement specs and generated compressed bytes, no source paths."""

    def __init__(self, bad_hash=None, bad_size=None):
        self.stack = ExitStack()
        self.specs = {}
        self.payloads = []
        self.records = {}
        for index, source in enumerate(streaming.SOURCE_ORDER):
            payload = ("synthetic:" + source).encode("ascii")
            count = 3 if index < 2 else 2
            historical = (0, 2) if index < 2 else (1,)
            digest = hashlib.sha256(payload).hexdigest()
            if index == bad_hash:
                digest = "0" * 64
            self.specs[source] = streaming.SourceSpec(
                source, "/synthetic-never-opened/" + source + ".mp4",
                len(payload), digest, 4, 4, count, historical)
            self.payloads.extend((payload, b""))
            self.records[101 + index] = metadata(
                len(payload) - (index == bad_size), 1001 + index)

    def __enter__(self):
        patch = self.stack.enter_context
        patch(mock.patch.object(streaming, "SOURCES", MappingProxyType(self.specs)))
        self.open = patch(mock.patch.object(streaming, "_open_source",
                                           side_effect=[101, 102, 103, 104]))
        self.close = patch(mock.patch.object(streaming.os, "close"))
        self.seek = patch(mock.patch.object(streaming.os, "lseek"))
        self.fstat = patch(mock.patch.object(streaming.os, "fstat",
                                            side_effect=lambda fd: self.records[fd]))
        self.stat = patch(mock.patch.object(
            streaming, "_stat_source", side_effect=lambda spec:
            self.records[101 + streaming.SOURCE_ORDER.index(spec.source_id)]))
        self.read = patch(mock.patch.object(streaming.os, "read",
                                           side_effect=self.payloads))
        return self

    def __exit__(self, *args):
        return self.stack.__exit__(*args)


def consume_pairs(reader):
    for left, right in streaming.SOURCE_PAIRS:
        for first, second in zip(reader.iter_frames(left),
                                 reader.iter_frames(right), strict=True):
            if first[0] != second[0]:
                raise AssertionError("synthetic pair index mismatch")


class SourceSpecificationTests(unittest.TestCase):
    def test_exact_four_sources_match_authorized_documentary_contract(self):
        expected = {
            "ESM1": (3233526, "4d07ee422e97661b1ee0ae681b7617fd7971476015603f3039c20ddf8b0c5c6d", 1018, 294, (73, 146, 219)),
            "ESM2": (41487560, "4eb1762dc4ee65c3e8b1411d80812a75257b1324d539db4c3dcf6c97c1ed9a0a", 1018, 294, (73, 146, 219)),
            "ESM4": (4509283, "9e6be3e78699d3bdd16fa71d56917479d7e16f7418b857ab3925e1115df91ebe", 1012, 395, (98, 197)),
            "ESM5": (59235679, "c9054d18f330e018e82cc6bd4db2ccfbda7ac76e01326a831857a835d1feade6", 1012, 395, (98, 197)),
        }
        self.assertEqual(tuple(streaming.SOURCES), tuple(expected))
        for source, values in expected.items():
            spec = streaming.source_spec(source)
            self.assertEqual((spec.size_bytes, spec.sha256, spec.height,
                              spec.frame_count, spec.historical_indices), values)
            self.assertEqual(spec.width, 1278)
            self.assertEqual(spec.frame_bytes, 1951506 if spec.height == 1018 else 1940004)
            self.assertTrue(spec.path.endswith("/11837_2015_1646_MO" + source + "_ESM.mp4"))

    def test_construction_is_inert_and_denies_invalid_configuration(self):
        with mock.patch.object(streaming.os, "open") as opened:
            reader = streaming.AuthenticatedSources("legacy")
            self.assertEqual(reader.audit["state"], "NOT_ENTERED")
            for mode in ("training", "LEGACY", "", None, True):
                with self.assertRaisesRegex(streaming.StreamingContractError, "MODE"):
                    streaming.AuthenticatedSources(mode)
            for timeout in (0, -1, 3601, float("inf"), float("nan"), True):
                with self.assertRaisesRegex(streaming.StreamingContractError, "TIMEOUT"):
                    streaming.AuthenticatedSources("full", timeout_seconds=timeout)
            with self.assertRaisesRegex(streaming.StreamingContractError, "AUDIT"):
                streaming.AuthenticatedSources("full", {"old": 1})
            opened.assert_not_called()

    def test_annotations_and_arbitrary_paths_are_denied_before_any_touch(self):
        with mock.patch.object(streaming.os, "open") as opened, \
                mock.patch.object(streaming, "_stat_source") as examined:
            reader = streaming.AuthenticatedSources("full")
            for source in ("ESM3", "ESM6", "../ESM1", None, {},
                           streaming.SOURCES["ESM1"].path):
                with self.assertRaisesRegex(streaming.StreamingContractError, "SOURCE_NOT_AUTHORIZED"):
                    reader.iter_frames(source)
                with self.assertRaisesRegex(streaming.StreamingContractError, "SOURCE_NOT_AUTHORIZED"):
                    streaming.decoder_command(source, 99, "full")
            opened.assert_not_called()
            examined.assert_not_called()

    def test_valid_source_still_requires_authenticated_reader(self):
        with mock.patch.object(streaming, "_open_source") as opened:
            with self.assertRaisesRegex(streaming.StreamingContractError, "NOT_AUTHENTICATED"):
                streaming.AuthenticatedSources("full").iter_frames("ESM1")
            opened.assert_not_called()

    def test_legacy_commands_emit_only_historical_train_dev_indices(self):
        for source in streaming.SOURCE_ORDER:
            spec = streaming.SOURCES[source]
            cmd = streaming.decoder_command(source, 99, "legacy")
            self.assertEqual(cmd[cmd.index("-i") + 1], "/proc/self/fd/99")
            self.assertEqual(cmd[cmd.index("-vf") + 1], "select=" + "+".join(
                f"eq(n\\,{i})" for i in spec.historical_indices))
            self.assertEqual(cmd[cmd.index("-frames:v") + 1], str(len(spec.historical_indices)))
            self.assertEqual(cmd[cmd.index("-pix_fmt") + 1], "yuv420p")
            self.assertIn("-noautorotate", cmd)
            self.assertNotIn(spec.path, cmd)
            self.assertNotIn("-ss", cmd)

    def test_full_command_requires_natural_eof_and_no_resizing(self):
        cmd = streaming.decoder_command("ESM5", 17, "full")
        for flag in ("-frames:v", "-vf", "-ss", "-s"):
            self.assertNotIn(flag, cmd)
        self.assertEqual(cmd[-3:], ["-f", "rawvideo", "pipe:1"])
        for descriptor in (-1, None, True, "17"):
            with self.assertRaisesRegex(streaming.StreamingContractError, "FD_INVALID"):
                streaming.decoder_command("ESM1", descriptor, "full")


class StreamingCustodyTests(unittest.TestCase):
    def test_all_four_hashes_finish_before_decoder_and_normal_exit_requires_eof(self):
        audit = {}
        with SyntheticAuthentication() as fixture, \
                mock.patch.object(streaming.subprocess, "Popen") as launch:
            with self.assertRaisesRegex(streaming.StreamingContractError, "NOT_EXHAUSTED"):
                with streaming.AuthenticatedSources("full", audit):
                    self.assertTrue(audit["all_sources_authenticated"])
                    self.assertEqual(audit["source_auth_opens"], 4)
                    self.assertEqual(audit["source_auth_bytes_read"], 56)
                    self.assertEqual(audit["source_auth_compressed_bytes_read"], 56)
                    launch.assert_not_called()
            self.assertEqual(fixture.close.call_args_list,
                             [mock.call(101), mock.call(102), mock.call(103), mock.call(104)])
        self.assertEqual(audit["state"], "CLOSED_INCOMPLETE")

    def test_each_bad_source_hash_prevents_every_decoder(self):
        for bad in range(4):
            with self.subTest(source=bad), SyntheticAuthentication(bad_hash=bad) as fixture, \
                    mock.patch.object(streaming.subprocess, "Popen") as launch:
                reader = streaming.AuthenticatedSources("full")
                with self.assertRaisesRegex(streaming.StreamingContractError, "HASH_MISMATCH"):
                    reader.__enter__()
                launch.assert_not_called()
                self.assertFalse(reader.audit["all_sources_authenticated"])
                self.assertEqual(reader.audit["source_auth_opens"], bad + 1)
                self.assertEqual(fixture.close.call_count, bad + 1)
                self.assertEqual(reader.audit["state"], "AUTHENTICATION_FAILED")

    def test_size_failure_denies_before_content_read(self):
        with SyntheticAuthentication(bad_size=0) as fixture:
            with self.assertRaisesRegex(streaming.StreamingContractError, "SIZE_MISMATCH"):
                streaming.AuthenticatedSources("legacy").__enter__()
            fixture.read.assert_not_called()
            fixture.close.assert_called_once_with(101)

    def test_metadata_mutation_denies_before_decoder_and_blocks_other_streams(self):
        with SyntheticAuthentication() as fixture, \
                mock.patch.object(streaming.subprocess, "Popen") as launch:
            reader = streaming.AuthenticatedSources("full").__enter__()
            try:
                fixture.records[101].st_mtime_ns += 1
                with self.assertRaisesRegex(streaming.StreamingContractError, "METADATA_CHANGED"):
                    next(reader.iter_frames("ESM1"))
                launch.assert_not_called()
                with self.assertRaisesRegex(streaming.StreamingContractError, "NOT_AUTHENTICATED"):
                    reader.iter_frames("ESM2")
            finally:
                reader.close()

    def test_paired_legacy_streams_have_exact_order_counts_fds_and_once_only(self):
        audit = {}
        processes = [process_fixture() for _ in range(4)]
        with SyntheticAuthentication() as fixture, \
                mock.patch.object(streaming.subprocess, "Popen", side_effect=processes) as launch, \
                mock.patch.object(streaming, "_native_frames", side_effect=native_payloads):
            with streaming.AuthenticatedSources("legacy", audit) as reader:
                observed = {}
                for left, right in streaming.SOURCE_PAIRS:
                    observed[left], observed[right] = [], []
                    for a, b in zip(reader.iter_frames(left), reader.iter_frames(right), strict=True):
                        observed[left].append(a[0]); observed[right].append(b[0])
                        self.assertEqual(a[0], b[0])
                        self.assertEqual(a[2], hashlib.sha256(a[1]).hexdigest())
                    with self.assertRaisesRegex(streaming.StreamingContractError, "ALREADY_CONSUMED"):
                        reader.iter_frames(left)
                for source in streaming.SOURCE_ORDER:
                    self.assertEqual(observed[source], list(streaming.SOURCES[source].historical_indices))
                self.assertEqual(launch.call_count, 4)
                self.assertEqual([c.kwargs["pass_fds"] for c in launch.call_args_list],
                                 [(101,), (102,), (103,), (104,)])
                self.assertTrue(all(c.kwargs["close_fds"] for c in launch.call_args_list))
                self.assertEqual(audit["frames_emitted"], 6)
                self.assertEqual(audit["native_bytes_emitted"], 144)
                self.assertEqual(audit["decoder_input_open_requests"], 4)
                self.assertIsNone(audit["decoder_compressed_bytes_read"])
                self.assertIsNone(audit["internal_intermediate_decode_count"])
                self.assertEqual(audit["historical_intermediate_frames_delivered"], 0)
            self.assertEqual(fixture.close.call_count, 4)
        self.assertEqual(audit["state"], "CLOSED_COMPLETE")
        self.assertTrue(audit["source_fds_closed"])

    def test_full_mode_emits_all_frames_and_all_sources_reach_eof(self):
        audit = {}
        with SyntheticAuthentication(), \
                mock.patch.object(streaming.subprocess, "Popen", side_effect=lambda *a, **k: process_fixture()), \
                mock.patch.object(streaming, "_native_frames", side_effect=native_payloads):
            with streaming.AuthenticatedSources("full", audit) as reader:
                consume_pairs(reader)
        self.assertEqual(audit["state"], "CLOSED_COMPLETE")
        self.assertEqual(audit["frames_emitted"], 10)
        self.assertEqual(audit["native_bytes_emitted"], 240)
        self.assertEqual(audit["native_bytes_received"], 240)
        self.assertEqual([audit["sources"][s]["frames_emitted"] for s in streaming.SOURCE_ORDER],
                         [3, 3, 2, 2])

    def test_cross_pair_and_third_stream_are_denied_before_launch(self):
        with SyntheticAuthentication(), mock.patch.object(streaming.subprocess, "Popen") as launch:
            reader = streaming.AuthenticatedSources("full").__enter__()
            try:
                reader.iter_frames("ESM1")
                with self.assertRaisesRegex(streaming.StreamingContractError, "CROSS_ACQUISITION"):
                    reader.iter_frames("ESM4")
                reader.iter_frames("ESM2")
                with self.assertRaisesRegex(streaming.StreamingContractError, "CONCURRENT_SOURCE_LIMIT"):
                    reader.iter_frames("ESM5")
                launch.assert_not_called()
            finally:
                reader.close()

    def test_consumer_failure_kills_both_active_decoders_without_masking_exception(self):
        audit = {}
        processes = [process_fixture(running=True), process_fixture(running=True)]
        with SyntheticAuthentication() as fixture, \
                mock.patch.object(streaming.subprocess, "Popen", side_effect=processes), \
                mock.patch.object(streaming, "_native_frames", side_effect=native_payloads):
            with self.assertRaisesRegex(RuntimeError, "controller stopped"):
                with streaming.AuthenticatedSources("full", audit) as reader:
                    left, right = reader.iter_frames("ESM1"), reader.iter_frames("ESM2")
                    next(left); next(right)
                    raise RuntimeError("controller stopped")
            self.assertEqual(fixture.close.call_count, 4)
        self.assertEqual(audit["frames_emitted"], 2)
        self.assertEqual(audit["state"], "CLOSED_INCOMPLETE")
        for process in processes:
            process.kill.assert_called_once()
            process.stdout.close.assert_called_once()
            process.stderr.close.assert_called_once()

    def test_normal_exit_after_partial_use_fails_closed(self):
        audit = {}
        with SyntheticAuthentication(), \
                mock.patch.object(streaming.subprocess, "Popen", return_value=process_fixture()), \
                mock.patch.object(streaming, "_native_frames", side_effect=native_payloads):
            with self.assertRaisesRegex(streaming.StreamingContractError, "NOT_EXHAUSTED"):
                with streaming.AuthenticatedSources("legacy", audit) as reader:
                    next(reader.iter_frames("ESM1"))
        self.assertEqual(audit["state"], "CLOSED_INCOMPLETE")
        self.assertEqual(audit["sources"]["ESM1"]["state"], "CONSUMER_STOPPED_BEFORE_EOF")

    def test_failed_stream_prevents_reserved_peer_from_launching(self):
        with SyntheticAuthentication(), \
                mock.patch.object(streaming.subprocess, "Popen", side_effect=OSError("synthetic")) as launch:
            reader = streaming.AuthenticatedSources("full").__enter__()
            left, right = reader.iter_frames("ESM1"), reader.iter_frames("ESM2")
            try:
                with self.assertRaises(OSError):
                    next(left)
                with self.assertRaisesRegex(streaming.StreamingContractError, "READER_FAILED"):
                    next(right)
                self.assertEqual(launch.call_count, 1)
                self.assertEqual(reader.audit["decoder_launch_attempts"], 1)
                self.assertEqual(reader.audit["decoder_launches"], 0)
            finally:
                reader.close()

    def test_reader_cannot_reenter_or_stream_after_close(self):
        with SyntheticAuthentication():
            reader = streaming.AuthenticatedSources("full").__enter__()
            reader.close()
            reader.close()
            with self.assertRaisesRegex(streaming.StreamingContractError, "ALREADY_USED"):
                reader.__enter__()
            with self.assertRaisesRegex(streaming.StreamingContractError, "NOT_AUTHENTICATED"):
                reader.iter_frames("ESM1")

    def test_partial_native_read_is_counted_without_claiming_an_emitted_frame(self):
        audit = {}
        def partial_native(process, size, count, record, timeout):
            del process, size, count, timeout
            record["native_bytes_received"] += 4
            raise streaming.StreamingContractError("DECODE_TRUNCATED_FRAME")
            yield  # The injected decoder remains a generator, without a frame.
        with SyntheticAuthentication(), \
                mock.patch.object(streaming.subprocess, "Popen", return_value=process_fixture()), \
                mock.patch.object(streaming, "_native_frames", side_effect=partial_native):
            with self.assertRaisesRegex(streaming.StreamingContractError, "TRUNCATED_FRAME"):
                with streaming.AuthenticatedSources("full", audit) as reader:
                    next(reader.iter_frames("ESM1"))
        self.assertEqual(audit["native_bytes_received"], 4)
        self.assertEqual(audit["native_bytes_emitted"], 0)
        self.assertEqual(audit["frames_emitted"], 0)

    def test_no_follow_walk_rejects_synthetic_symlinks(self):
        root = Path(__file__).resolve().parents[1] / ".bootstrap-test-tmp"
        root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="study2b-stream-test-", dir=root) as folder:
            base = Path(folder)
            (base / "actual").mkdir()
            (base / "alias").symlink_to("actual", target_is_directory=True)
            with self.assertRaises(OSError):
                streaming._parent_fd(str(base / "alias" / "synthetic.bin"))
            target = base / "synthetic.bin"
            target.write_bytes(b"synthetic")
            alias = base / "alias.bin"
            alias.symlink_to(target.name)
            spec = streaming.SourceSpec("ESM1", str(alias), 9, "0" * 64, 4, 4, 1, (0,))
            with mock.patch.object(streaming, "SOURCES", {"ESM1": spec}):
                with self.assertRaises(OSError):
                    streaming._open_source(spec)


class NativePipeTests(unittest.TestCase):
    """Real pipes carry tiny generated bytes from Python; never FFmpeg."""

    def run_pipe(self, code, count=2, timeout=2.0):
        record = {"native_bytes_received": 0, "decoder_stderr_bytes": 0,
                  "decoder_exit_code": None}
        process = subprocess.Popen([sys.executable, "-B", "-c", code],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, bufsize=0)
        try:
            frames = list(streaming._native_frames(process, 4, count, record, timeout))
            return frames, record
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()
            self.last_record = record

    def test_fragmented_frames_and_large_stderr_are_bounded(self):
        frames, record = self.run_pipe("import os; os.write(2,b'e'*200000); os.write(1,b'abc'); os.write(1,b'defgh')")
        self.assertEqual(frames, [b"abcd", b"efgh"])
        self.assertEqual(record["native_bytes_received"], 8)
        self.assertEqual(record["decoder_stderr_bytes"], 200000)
        self.assertEqual(len(record["decoder_stderr"]), streaming.STDERR_LIMIT_BYTES)
        self.assertTrue(record["decoder_stderr_truncated"])

    def test_partial_frame_fails(self):
        with self.assertRaisesRegex(streaming.StreamingContractError, "TRUNCATED_FRAME"):
            self.run_pipe("import os; os.write(1,b'abcdef')")
        self.assertEqual(self.last_record["trailing_partial_bytes"], 2)

    def test_missing_frame_fails(self):
        with self.assertRaisesRegex(streaming.StreamingContractError, "FRAME_COUNT_MISMATCH"):
            self.run_pipe("import os; os.write(1,b'abcd')")

    def test_extra_frame_fails_before_extra_delivery(self):
        with self.assertRaisesRegex(streaming.StreamingContractError, "FRAME_COUNT_EXCEEDED"):
            self.run_pipe("import os; os.write(1,b'abcdefghijkl')")
        self.assertEqual(self.last_record["native_bytes_received"], 12)

    def test_nonzero_exit_fails_even_after_expected_bytes(self):
        with self.assertRaisesRegex(streaming.StreamingContractError, "EXIT_FAILURE"):
            self.run_pipe("import os; os.write(1,b'abcdefgh'); raise SystemExit(3)")
        self.assertEqual(self.last_record["decoder_exit_code"], 3)

    def test_idle_decoder_times_out(self):
        with self.assertRaisesRegex(streaming.StreamingContractError, "DECODER_TIMEOUT"):
            self.run_pipe("import time; time.sleep(5)", timeout=0.05)


if __name__ == "__main__":
    unittest.main()
