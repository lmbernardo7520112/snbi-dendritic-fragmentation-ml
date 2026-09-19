"""TI3 execution guards exercised only in fresh temporary synthetic trees."""

import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from snbi_fragmentation import ti3_execution as execution
from snbi_fragmentation.ti3_dataset import build_manifest
from test_ti3_dataset import fixture


HEAD = "1" * 40


class MetadataTrap(dict):
    def get(self, key, default=None):
        if key == "path":
            raise AssertionError("forbidden source path was examined")
        return super().get(key, default)


class AdmissionBeforeIOTests(unittest.TestCase):
    def test_forbidden_split_source_and_frame_deny_before_path_or_filesystem(self):
        cases = [
            {"split": "FINAL_TEST", "source_id": "ESM1", "frame_index": 293},
            {"split": "FINAL_TEST", "source_id": "ESM4", "frame_index": 295},
        ]
        cases.extend({"split": "TRAIN", "source_id": source, "frame_index": 73}
                     for source in ("ESM2", "ESM3", "ESM5", "ESM6"))
        cases.extend((
            {"split": "TRAIN", "source_id": "ESM1", "frame_index": 0},
            {"split": "TRAIN", "source_id": "ESM1", "frame_index": 293},
            {"split": "TRAIN", "source_id": "ESM1", "frame_index": True},
            {"split": "TRAIN", "source_id": "ESM4", "frame_index": 197},
        ))
        with mock.patch.object(execution.os, "open") as opened, mock.patch.object(execution.os, "stat") as stated:
            for case in cases:
                with self.subTest(case=case), self.assertRaises(execution.ExecutionContractError):
                    execution.validate_admission(MetadataTrap(case))
            opened.assert_not_called()
            stated.assert_not_called()


class NativeExecutionSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inputs = fixture()
        cls.payloads = {}
        for image in inputs[2]:
            payload = bytes([17 if image["source_id"] == "ESM1" else 29]) * image["frame_bytes"]
            cls.payloads[(image["source_id"], image["frame_index"])] = payload
            image["image_sha256"] = hashlib.sha256(payload).hexdigest()
        cls.manifest = build_manifest(*inputs)
        cls.serialized = json.dumps(cls.manifest, sort_keys=True, allow_nan=False).encode("utf-8")
        cls.authority = {
            "state": "ARMED_ONCE", "head_sha": HEAD,
            "manifest_sha256": hashlib.sha256(cls.serialized).hexdigest(),
            "source_inventory_sha256": execution.source_inventory_sha256(cls.manifest),
            "scientific_invocation_limit": 1,
        }

    def setUp(self):
        local_parent = Path(".bootstrap-test-tmp/ti3-preflight-recovery")
        if local_parent.is_dir():
            self.temporary = tempfile.TemporaryDirectory(prefix="ti3-io-", dir=local_parent)
        elif os.environ.get("CI") == "true":
            self.temporary = tempfile.TemporaryDirectory(prefix="ti3-io-ci-")
        else:
            self.fail("authorized local synthetic temporary root is unavailable")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).absolute()
        (self.root / "data/derived/ti2-pilot").mkdir(parents=True)
        (self.root / execution.RECEIPT_PATH).parent.mkdir(parents=True)
        self.record = copy.deepcopy(next(row for row in self.manifest["source_inventory"]
                                         if (row["source_id"], row["frame_index"]) == ("ESM1", 73)))

    def arm(self, authority=None, current_head=HEAD):
        reader = execution.arm_execution(str(self.root), self.serialized,
                                         self.authority if authority is None else authority,
                                         current_head=current_head)
        self.addCleanup(reader.close)
        return reader

    def write_source(self, payload=None, record=None):
        record = self.record if record is None else record
        payload = self.payloads[(record["source_id"], record["frame_index"])] if payload is None else payload
        (self.root / record["path"]).write_bytes(payload)

    def test_receipt_fsync_precedes_native_open_and_each_buffer_opens_once(self):
        self.write_source()
        original_open, original_fsync = os.open, os.fsync
        fsync_count = 0

        def synced(fd):
            nonlocal fsync_count
            fsync_count += 1
            return original_fsync(fd)

        def opened(path, flags, *args, **kwargs):
            if path == "ESM1-0073.raw":
                self.assertGreaterEqual(fsync_count, 2)
                self.assertTrue((self.root / execution.RECEIPT_PATH).is_file())
                self.assertTrue(flags & os.O_NOFOLLOW)
                self.assertFalse(flags & os.O_WRONLY)
            return original_open(path, flags, *args, **kwargs)

        with mock.patch.object(execution.os, "open", side_effect=opened), mock.patch.object(execution.os, "fsync", side_effect=synced):
            reader = self.arm()
            returned = reader.read_native(self.record)
        self.assertEqual(returned, self.payloads[("ESM1", 73)])
        report = reader.report()
        self.assertEqual(report["experimental_opens"], 1)
        self.assertEqual(report["experimental_bytes"], self.record["frame_bytes"])
        self.assertEqual(report["final_test_opens"], 0)
        self.assertTrue(next(e for e in report["entries"] if e["frame_index"] == 73)["verified"])
        with mock.patch.object(execution.os, "open") as opened:
            with self.assertRaises(execution.ExecutionContractError):
                reader.read_native(self.record)
            opened.assert_not_called()

    def test_second_arm_existing_receipt_or_terminal_cannot_reactivate(self):
        self.arm()
        with self.assertRaisesRegex(execution.ExecutionContractError, "RECEIPT_ALREADY_EXISTS"):
            self.arm()
        (self.root / execution.TERMINAL_PATH).write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(execution.ExecutionContractError, "TERMINAL_ALREADY_EXISTS"):
            self.arm()

    def test_custody_divergence_denies_before_filesystem(self):
        for key, value in (("head_sha", "2" * 40), ("manifest_sha256", "b" * 64),
                           ("source_inventory_sha256", "c" * 64), ("state", "CLOSED"),
                           ("scientific_invocation_limit", True)):
            authority = {**self.authority, key: value}
            with self.subTest(key=key), mock.patch.object(execution.os, "open") as opened:
                with self.assertRaises(execution.ExecutionContractError):
                    self.arm(authority)
                opened.assert_not_called()
        self.assertFalse((self.root / execution.RECEIPT_PATH).exists())

    def test_manifest_byte_change_denies_before_receipt(self):
        with mock.patch.object(execution.os, "open") as opened:
            with self.assertRaisesRegex(execution.ExecutionContractError, "MANIFEST_HASH_MISMATCH"):
                execution.arm_execution(str(self.root), self.serialized + b"\n", self.authority,
                                        current_head=HEAD)
            opened.assert_not_called()

    def test_final_test_and_source_metadata_mutation_cannot_open_or_stat(self):
        reader = self.arm()
        final = next(row for row in self.manifest["source_inventory"] if row["split"] == "FINAL_TEST")
        altered = {**self.record, "image_sha256": "b" * 64}
        for record in (final, altered, {**self.record, "path": "data/arbitrary.raw"}):
            with self.subTest(record=record["source_id"]), mock.patch.object(execution.os, "open") as opened:
                with mock.patch.object(execution.os, "stat") as stated:
                    with self.assertRaises(execution.ExecutionContractError):
                        reader.read_native(record)
                    opened.assert_not_called()
                    stated.assert_not_called()
        self.assertEqual(reader.report()["experimental_opens"], 0)

    def test_hash_mismatch_keeps_full_actual_counts_and_closes_further_reads(self):
        self.write_source(b"X" * self.record["frame_bytes"])
        reader = self.arm()
        with self.assertRaisesRegex(execution.ExecutionContractError, "NATIVE_HASH_MISMATCH"):
            reader.read_native(self.record)
        report = reader.report()
        self.assertTrue(report["failed"])
        self.assertEqual(report["experimental_opens"], 1)
        self.assertEqual(report["experimental_bytes"], self.record["frame_bytes"])
        other = next(row for row in self.manifest["source_inventory"]
                     if row["source_id"] == "ESM4" and row["frame_index"] == 98)
        with mock.patch.object(execution.os, "open") as opened:
            with self.assertRaises(execution.ExecutionContractError):
                reader.read_native(other)
            opened.assert_not_called()

    def test_truncated_read_counts_only_actual_bytes_without_retry(self):
        self.write_source(b"synthetic-short")
        reader = self.arm()
        with self.assertRaisesRegex(execution.ExecutionContractError, "NATIVE_BYTE_COUNT_MISMATCH"):
            reader.read_native(self.record)
        self.assertEqual(reader.report()["experimental_bytes"], len(b"synthetic-short"))
        self.assertEqual(reader.report()["experimental_opens"], 1)

    def test_extra_byte_is_bounded_counted_and_rejected(self):
        self.write_source(self.payloads[("ESM1", 73)] + b"extra-disallowed-bytes")
        reader = self.arm()
        with self.assertRaisesRegex(execution.ExecutionContractError, "NATIVE_BYTE_COUNT_MISMATCH"):
            reader.read_native(self.record)
        self.assertEqual(reader.report()["experimental_bytes"], self.record["frame_bytes"] + 1)

    def test_read_error_preserves_partial_byte_count(self):
        self.write_source()
        reader = self.arm()
        actual_read = os.read
        calls = 0

        def interrupted(fd, size):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("synthetic failure without a real path")
            return actual_read(fd, min(size, 19))

        with mock.patch.object(execution.os, "read", side_effect=interrupted):
            with self.assertRaisesRegex(execution.ExecutionContractError, "NATIVE_IO_FAILED"):
                reader.read_native(self.record)
        self.assertEqual(reader.report()["experimental_opens"], 1)
        self.assertEqual(reader.report()["experimental_bytes"], 19)
        self.assertTrue(reader.report()["failed"])

    def test_leaf_symlink_is_never_followed(self):
        target = self.root / "synthetic-target"
        target.write_bytes(b"not an experimental file")
        (self.root / self.record["path"]).symlink_to(target)
        reader = self.arm()
        with self.assertRaises(execution.ExecutionContractError):
            reader.read_native(self.record)
        self.assertEqual(reader.report()["experimental_opens"], 0)
        self.assertEqual(reader.report()["experimental_bytes"], 0)

    def test_parent_symlink_is_never_followed(self):
        native_parent = self.root / "data/derived/ti2-pilot"
        native_parent.rmdir()
        synthetic_parent = self.root / "synthetic-directory"
        synthetic_parent.mkdir()
        native_parent.symlink_to(synthetic_parent, target_is_directory=True)
        reader = self.arm()
        with self.assertRaises(execution.ExecutionContractError):
            reader.read_native(self.record)
        self.assertEqual(reader.report()["source_open_attempts"], 0)
        self.assertEqual(reader.report()["experimental_opens"], 0)
        self.assertEqual(reader.report()["experimental_bytes"], 0)

    def test_report_is_a_copy_and_close_does_not_reopen_sources(self):
        reader = self.arm()
        report = reader.report()
        report["entries"][0]["opens"] = 900
        self.assertEqual(reader.report()["experimental_opens"], 0)
        reader.close()
        with mock.patch.object(execution.os, "open") as opened:
            with self.assertRaises(execution.ExecutionContractError):
                reader.read_native(self.record)
            opened.assert_not_called()


if __name__ == "__main__":
    unittest.main()
