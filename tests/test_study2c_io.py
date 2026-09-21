"""Synthetic-only Study2-C access tests; no MP4, corpus or scientific runner."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from snbi_fragmentation import study2c_io as access_io

try:
    import numpy as np
    from scipy import ndimage  # Availability only; actual fixtures are synthetic.
except ImportError:
    np = None


def checksum(payload):
    return hashlib.sha256(payload).hexdigest()


def proof(test=False):
    result = {"authorized": True, "execution_receipt_sha256": "a" * 64,
              "method_freeze_sha": "b" * 40}
    if test:
        result.update({"final_fit_durable": True, "final_fit_freeze_sha256": "c" * 64})
    return result


def selected_row(index=0, *, kind="positive", split="TRAIN", tier="GOLD",
                 source="ESM1", frame=0, x=64, y=64):
    acquisition = access_io.support.ACQUISITIONS[source]
    group = f"{acquisition}|site-{index}" if kind == "positive" else f"{acquisition}|{x}|{y}"
    return {"sample_id": f"{kind}|{group}|{frame}", "group_id": group,
            "kind": kind, "label": int(kind == "positive"), "split": split,
            "tier": tier, "acquisition_id": acquisition, "frame_index": frame,
            "structural_source_id": source,
            "solutal_source_id": {"ESM1": "ESM2", "ESM4": "ESM5"}[source],
            "center_x": x, "center_y": y,
            "patch_xyxy": [x - 32, y - 32, x + 33, y + 33],
            **({"positive_row_index": index} if kind == "positive" else {})}


class FakeNativeReader:
    """Tiny generated in-memory streams, never AuthenticatedSources or FFmpeg."""

    def __init__(self, fixture, mode, audit):
        if mode != "full":
            raise AssertionError("unexpected synthetic mode")
        self.fixture, self.audit = fixture, audit
        self.seen = []

    def __enter__(self):
        self.audit.update({"all_sources_authenticated": True,
                           "source_auth_opens": 4, "source_auth_bytes_read": 40,
                           "decoder_input_open_requests": 0,
                           "frames_emitted": 0, "native_bytes_emitted": 0})
        return self

    def __exit__(self, *args):
        self.audit["state"] = "CLOSED_COMPLETE" if args[0] is None else "CLOSED_INCOMPLETE"
        return False

    def iter_frames(self, source):
        self.seen.append(source)
        self.audit["decoder_input_open_requests"] += 1
        for index in range(2):
            if self.fixture.short_source == source and index == 1:
                return
            raw = self.fixture.native[source, index]
            self.audit["frames_emitted"] += 1
            self.audit["native_bytes_emitted"] += len(raw)
            yielded_index = index + 1 if self.fixture.shift_source == source else index
            yield yielded_index, raw, checksum(raw)


@unittest.skipIf(np is None, "NumPy/SciPy required for synthetic native fixtures")
class CorpusAccessTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1] / ".bootstrap-test-tmp"
        root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="study2c-io-", dir=root)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.allow_test = False
        self.grants = []
        self.short_source = self.shift_source = None
        self.positive_payloads = [bytes([index + 1]) * access_io.CHANNEL_BYTES
                                  + bytes([index + 51]) * access_io.CHANNEL_BYTES
                                  for index in range(4)]
        payload = b"".join(self.positive_payloads)
        path = self.root / access_io.POSITIVE_PATH
        path.parent.mkdir(parents=True)
        path.write_bytes(payload)
        self.positive_path = path
        self.native = {}
        for ordinal, source in enumerate(("ESM1", "ESM2", "ESM4", "ESM5")):
            for frame in range(2):
                self.native[source, frame] = bytes([ordinal * 30 + frame + 1]) * (128 * 128) + bytes([128]) * (128 * 128 // 2)
        frames = [{"structural_source": structural, "solute_source": solute,
                   "frame_index": frame,
                   "structural_frame_sha256": checksum(self.native[structural, frame]),
                   "solute_frame_sha256": checksum(self.native[solute, frame])}
                  for structural, solute in access_io.SOURCE_PAIRS for frame in range(2)]
        content = (json.dumps(frames) + "\n").encode()
        frame_path = self.root / access_io.FRAME_HASH_PATH
        frame_path.parent.mkdir(parents=True)
        frame_path.write_bytes(content)
        self.frame_path = frame_path
        patches = (
            mock.patch.object(access_io, "POSITIVE_BYTES", len(payload)),
            mock.patch.object(access_io, "POSITIVE_ROWS", 4),
            mock.patch.object(access_io, "POSITIVE_SHA256", checksum(payload)),
            mock.patch.object(access_io, "FRAME_HASH_SHA256", checksum(content)),
            mock.patch.object(access_io, "FRAME_COUNTS", {"ESM1": 2, "ESM4": 2}),
            mock.patch.object(access_io.support, "DIMENSIONS", {"ESM1": (128, 128), "ESM4": (128, 128)}),
            mock.patch.object(access_io, "_free_disk", return_value=10 ** 12),
            mock.patch.object(access_io, "AuthenticatedSources", side_effect=lambda mode, audit: FakeNativeReader(self, mode, audit)),
        )
        self.started = [patch.start() for patch in patches]
        for patch in patches:
            self.addCleanup(patch.stop)
        self.decoder = self.started[-1]

    def grant(self, action, phase, rows):
        self.grants.append((action, phase, len(rows)))
        return proof(test=self.allow_test)

    def positive(self, index=0, **kwargs):
        row = selected_row(index, **kwargs)
        row.update(access_io._hashes(self.positive_payloads[index]))
        return row

    def background(self, **kwargs):
        return selected_row(kind="background", tier="BACKGROUND", **kwargs)

    def reader(self):
        reader = access_io.CorpusAccess(self.root, self.grant)
        self.addCleanup(reader.close)
        return reader

    def test_constructor_inert_and_default_authority_denies_before_path(self):
        with mock.patch.object(access_io, "_directory_fd") as directory:
            reader = access_io.CorpusAccess(self.root)
            self.assertEqual(reader.audit["state"], "NOT_USED")
            with self.assertRaisesRegex(access_io.CorpusAccessError, "authorization"):
                reader.load_positive_rows([self.positive()], "TRAIN")
            with self.assertRaisesRegex(access_io.CorpusAccessError, "authorization"):
                reader.materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
            directory.assert_not_called()
            self.decoder.assert_not_called()

    def test_noncanonical_or_missing_proof_denies_before_path(self):
        for value in (True, {"authorized": 1}, {**proof(), "execution_receipt_sha256": ""},
                      {**proof(), "method_freeze_sha": "g" * 40}):
            with self.subTest(value=value), mock.patch.object(access_io, "_open_relative") as opened:
                reader = access_io.CorpusAccess(self.root, lambda *args: value)
                with self.assertRaisesRegex(access_io.CorpusAccessError, "authorization denied"):
                    reader.load_positive_rows([self.positive()], "TRAIN")
                opened.assert_not_called()

    def test_test_positive_and_background_require_durable_final_fit_before_path(self):
        reader = self.reader()
        with mock.patch.object(access_io, "_directory_fd") as directory:
            for method, rows in ((reader.load_positive_rows, [self.positive(split="TEST")]),
                                 (reader.materialize_backgrounds, [self.background(split="TEST")])):
                with self.assertRaisesRegex(access_io.CorpusAccessError, "durable final-fit"):
                    method(rows, "TEST")
            directory.assert_not_called()
        self.assertEqual(reader.audit["positive_container_auth_opens"], 0)
        self.decoder.assert_not_called()

    def test_test_silver_is_prohibited_even_with_final_fit_grant(self):
        self.allow_test = True
        reader = self.reader()
        with mock.patch.object(access_io, "_open_relative") as opened:
            with self.assertRaisesRegex(access_io.CorpusAccessError, "split/tier"):
                reader.load_positive_rows([self.positive(split="TEST", tier="SILVER")], "TEST")
            opened.assert_not_called()

    def test_positive_selected_rows_order_hashes_and_authentication_once(self):
        reader = self.reader()
        train = [self.positive(2), self.positive(0)]
        actual = reader.load_positive_rows(train, "TRAIN")
        expected = np.frombuffer(self.positive_payloads[2] + self.positive_payloads[0], dtype=np.uint8).reshape(2, 2, 65, 65)
        np.testing.assert_array_equal(actual, expected)
        dev = reader.load_positive_rows([self.positive(1, split="DEVELOPMENT")], "DEVELOPMENT")
        self.assertEqual(dev[0].tobytes(), self.positive_payloads[1])
        self.assertEqual(reader.audit["positive_container_auth_opens"], 1)
        self.assertEqual(reader.audit["positive_container_auth_bytes"], 4 * access_io.ROW_BYTES)
        self.assertEqual(reader.audit["positive_selected_rows_read"], 3)
        self.assertEqual(reader.audit["positive_selected_row_bytes"], 3 * access_io.ROW_BYTES)
        self.assertEqual(reader.audit["positive_pixels_written"], 0)
        self.decoder.assert_not_called()

    def test_all_three_positive_patch_hashes_are_checked(self):
        for key in ("structural_patch_sha256", "solutal_patch_sha256", "pair_sha256"):
            with self.subTest(key=key):
                reader = self.reader()
                row = self.positive(); row[key] = "0" * 64
                with self.assertRaisesRegex(access_io.CorpusAccessError, "canonical patch hash"):
                    reader.load_positive_rows([row], "TRAIN")
                self.assertEqual(reader.audit["positive_selected_rows_read"], 0)
                self.assertEqual(reader.audit["positive_selected_row_bytes"], access_io.ROW_BYTES)
                self.assertTrue(reader.audit["positive_container_fd_closed"])

    def test_opaque_container_hash_failure_prevents_selected_row_access(self):
        reader = self.reader()
        with mock.patch.object(access_io, "POSITIVE_SHA256", "0" * 64), \
                mock.patch.object(access_io.os, "pread") as read:
            with self.assertRaisesRegex(access_io.CorpusAccessError, "container hash"):
                reader.load_positive_rows([self.positive()], "TRAIN")
            read.assert_not_called()
        self.assertEqual(reader.audit["positive_container_auth_bytes"], 4 * access_io.ROW_BYTES)

    def test_container_size_failure_precedes_any_content_read(self):
        reader = self.reader()
        with mock.patch.object(access_io, "POSITIVE_BYTES", 1), \
                mock.patch.object(access_io.os, "read") as read:
            with self.assertRaisesRegex(access_io.CorpusAccessError, "container size"):
                reader.load_positive_rows([self.positive()], "TRAIN")
            read.assert_not_called()

    def test_positive_partial_pread_counts_every_byte_and_preserves_pair(self):
        original = access_io.os.pread
        def fragmented(descriptor, amount, offset):
            return original(descriptor, min(amount, 257), offset)
        reader = self.reader()
        with mock.patch.object(access_io.os, "pread", side_effect=fragmented):
            actual = reader.load_positive_rows([self.positive()], "TRAIN")
        self.assertEqual(actual[0].tobytes(), self.positive_payloads[0])
        self.assertEqual(reader.audit["positive_selected_row_bytes"], access_io.ROW_BYTES)

    def test_container_metadata_change_blocks_later_phase_without_reauth(self):
        reader = self.reader()
        reader.load_positive_rows([self.positive()], "TRAIN")
        self.positive_path.write_bytes(b"X" + b"".join(self.positive_payloads)[1:])
        with self.assertRaisesRegex(access_io.CorpusAccessError, "identity or metadata"):
            reader.load_positive_rows([self.positive(1, split="DEVELOPMENT")], "DEVELOPMENT")
        self.assertEqual(reader.audit["positive_container_auth_opens"], 1)
        self.assertEqual(reader.audit["positive_selected_rows_read"], 1)

    def test_symlinked_root_and_container_are_not_followed(self):
        alias = self.root / "root-alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(OSError):
            access_io.CorpusAccess(alias, self.grant).load_positive_rows([self.positive()], "TRAIN")
        saved = self.positive_path.with_name("synthetic-original.bin")
        self.positive_path.rename(saved)
        self.positive_path.symlink_to(saved.name)
        with self.assertRaises(OSError):
            self.reader().load_positive_rows([self.positive()], "TRAIN")

    def test_closed_access_does_not_reopen_container(self):
        reader = self.reader(); reader.close()
        with mock.patch.object(access_io, "_open_relative") as opened:
            with self.assertRaisesRegex(access_io.CorpusAccessError, "closed or failed"):
                reader.load_positive_rows([self.positive()], "TRAIN")
            opened.assert_not_called()

    def test_duplicate_positive_row_or_sample_is_denied_before_path(self):
        first = self.positive()
        second = deepcopy(first); second["sample_id"] += "different"; second["group_id"] += "different"
        with mock.patch.object(access_io, "_open_relative") as opened:
            with self.assertRaisesRegex(access_io.CorpusAccessError, "duplicate positive row"):
                self.reader().load_positive_rows([first, second], "TRAIN")
            opened.assert_not_called()

    def test_positive_phase_cannot_repeat_and_rows_are_reused_from_ram(self):
        reader = self.reader(); row = self.positive()
        reader.load_positive_rows([row], "TRAIN")
        with self.assertRaisesRegex(access_io.CorpusAccessError, "phase already consumed"):
            reader.load_positive_rows([self.positive(1)], "TRAIN")
        with self.assertRaisesRegex(access_io.CorpusAccessError, "reuse existing positive"):
            reader.load_positive_rows([row], "FINAL_TRAIN")
        self.assertEqual(reader.audit["positive_selected_rows_read"], 1)

    def test_train_silver_and_dev_silver_have_distinct_admissions(self):
        reader = self.reader()
        reader.load_positive_rows([self.positive(0, tier="SILVER")], "TRAIN_SILVER")
        with self.assertRaisesRegex(access_io.CorpusAccessError, "split/tier"):
            reader.load_positive_rows([self.positive(1, split="DEVELOPMENT", tier="SILVER")], "DEVELOPMENT")
        result = reader.load_positive_rows([self.positive(1, split="DEVELOPMENT", tier="SILVER")], "FINAL_TRAIN")
        self.assertEqual(result.shape, (1, 2, 65, 65))

    def test_test_positive_grant_is_logged_without_silver_access(self):
        self.allow_test = True
        reader = self.reader()
        result = reader.load_positive_rows([self.positive(split="TEST")], "TEST")
        self.assertEqual(result.shape, (1, 2, 65, 65))
        evidence = reader.audit["positive_phases"]["TEST"]["authorization"]
        self.assertTrue(evidence["final_fit_durable"])
        self.assertEqual(evidence["final_fit_freeze_sha256"], "c" * 64)

    def test_backgrounds_stream_all_native_frames_but_extract_only_selected_rows(self):
        reader = self.reader()
        rows = [self.background(source="ESM4", frame=1, split="DEVELOPMENT"),
                self.background(source="ESM1", frame=0)]
        with mock.patch.object(access_io.support, "native_luminance_and_support",
                               wraps=access_io.support.native_luminance_and_support) as support_call:
            pairs, manifest = reader.materialize_backgrounds(rows, "TRAIN_DEVELOPMENT")
        self.assertEqual(support_call.call_count, 4)
        self.assertEqual(pairs.shape, (2, 2, 65, 65))
        self.assertEqual(pairs.dtype, np.dtype("uint8"))
        self.assertTrue(np.all(pairs[0, 0] == 62)); self.assertTrue(np.all(pairs[0, 1] == 92))
        self.assertTrue(np.all(pairs[1, 0] == 1)); self.assertTrue(np.all(pairs[1, 1] == 31))
        self.assertEqual([r["sample_id"] for r in manifest["rows"]], [r["sample_id"] for r in rows])
        self.assertEqual([r["cache_row_index"] for r in manifest["rows"]], [0, 1])
        cache = manifest["artifacts"][0]
        self.assertEqual(cache["size_bytes"], 2 * access_io.ROW_BYTES)
        self.assertEqual((self.root / cache["path"]).read_bytes(), pairs.tobytes())
        self.assertEqual(cache["sha256"], checksum(pairs.tobytes()))
        ledger = (self.root / manifest["artifacts"][1]["path"]).read_bytes()
        self.assertEqual(checksum(ledger), manifest["artifacts"][1]["sha256"])
        self.assertEqual([json.loads(line)["sample_id"] for line in ledger.splitlines()], [r["sample_id"] for r in rows])
        audit = reader.audit["background_stages"]["TRAIN_DEVELOPMENT"]
        self.assertEqual(audit["streaming"]["frames_emitted"], 8)
        self.assertEqual(audit["streaming"]["decoder_input_open_requests"], 4)
        self.assertEqual(reader.audit["positive_container_auth_opens"], 0)
        self.assertEqual(reader.audit["temporary_disk_bytes"], 0)
        self.assertEqual(audit["channel_patches_written"], 4)

    def test_background_test_stage_uses_separate_cache_after_final_fit_only(self):
        reader = self.reader()
        reader.materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        self.allow_test = True
        row = self.background(source="ESM4", split="TEST")
        _, manifest = reader.materialize_backgrounds([row], "TEST")
        self.assertTrue(manifest["artifacts"][0]["path"].endswith("/cachetest.bin"))
        self.assertEqual(reader.audit["background_cache_bytes_written"], 2 * access_io.ROW_BYTES)
        self.assertEqual(self.decoder.call_count, 2)
        self.assertTrue(reader.audit["background_stages"]["TEST"]["authorization"]["final_fit_durable"])

    def test_background_stage_cannot_repeat(self):
        reader = self.reader()
        reader.materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        with self.assertRaisesRegex(access_io.CorpusAccessError, "already consumed"):
            reader.materialize_backgrounds([self.background(frame=1)], "TRAIN_DEVELOPMENT")
        self.assertEqual(self.decoder.call_count, 1)

    def test_background_caps_are_combined_across_stages_before_next_decode(self):
        reader = self.reader()
        with mock.patch.object(access_io, "MAX_CACHE_BYTES", access_io.ROW_BYTES):
            reader.materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
            self.allow_test = True
            with self.assertRaisesRegex(access_io.CorpusAccessError, "cache cap"):
                reader.materialize_backgrounds([self.background(source="ESM4", split="TEST")], "TEST")
        self.assertEqual(self.decoder.call_count, 1)

    def test_free_disk_denial_precedes_decoder(self):
        with mock.patch.object(access_io, "_free_disk", return_value=access_io.MIN_FREE_BYTES):
            with self.assertRaisesRegex(access_io.CorpusAccessError, "reserve insufficient"):
                self.reader().materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        self.decoder.assert_not_called()

    def test_changed_frame_hash_document_precedes_decoder(self):
        self.frame_path.write_bytes(self.frame_path.read_bytes() + b" ")
        with self.assertRaisesRegex(access_io.CorpusAccessError, "frame-hash custody"):
            self.reader().materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        self.decoder.assert_not_called()

    def test_changed_native_frame_hash_blocks_materialization(self):
        self.native["ESM1", 0] = b"X" + self.native["ESM1", 0][1:]
        reader = self.reader()
        with self.assertRaisesRegex(access_io.CorpusAccessError, "native frame hash"):
            reader.materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        self.assertEqual(reader.audit["background_stages"]["TRAIN_DEVELOPMENT"]["pairs_materialized"], 0)
        self.assertEqual(reader.audit["background_cache_bytes_written"], 0)

    def test_cross_temporal_pair_and_short_stream_fail_closed(self):
        self.shift_source = "ESM2"
        with self.assertRaisesRegex(access_io.CorpusAccessError, "synchronization"):
            self.reader().materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        self.shift_source = None; self.short_source = "ESM2"
        with self.assertRaises(ValueError):
            self.reader().materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")

    def test_background_full_safety_margin_is_rechecked_not_only_patch(self):
        original = access_io.support.native_luminance_and_support
        def margin_fault(raw, source, *, structural):
            y, mask = original(raw, source, structural=structural)
            writable = mask.copy()
            writable[29, 29] = False  # Outside patch [32:97], inside its margin3.
            return y, writable
        reader = self.reader()
        with mock.patch.object(access_io.support, "native_luminance_and_support", side_effect=margin_fault):
            with self.assertRaisesRegex(access_io.CorpusAccessError, "lost frozen support"):
                reader.materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        self.assertEqual(reader.audit["background_cache_bytes_written"], 0)

    def test_existing_cache_refused_before_any_decoder(self):
        path = self.root / "data/derived/study2c/cachetrain_dev.bin"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"do not replace synthetic existing cache")
        with self.assertRaisesRegex(access_io.CorpusAccessError, "existing background"):
            self.reader().materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        self.decoder.assert_not_called()
        self.assertEqual(path.read_bytes(), b"do not replace synthetic existing cache")

    def test_output_parent_symlink_is_denied_before_decode(self):
        target = self.root / "synthetic-cache-target"; target.mkdir()
        (self.root / "data/derived/study2c").symlink_to(target, target_is_directory=True)
        with self.assertRaises(OSError):
            self.reader().materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        self.decoder.assert_not_called()

    def test_crop_shift_annotation_source_and_cross_source_are_denied_before_io(self):
        cases = []
        row = self.background(); row["patch_xyxy"][0] += 1; cases.append(row)
        row = self.background(); row["structural_source_id"] = "ESM3"; cases.append(row)
        row = self.background(); row["solutal_source_id"] = "ESM5"; cases.append(row)
        row = self.background(); row["tier"] = "BACKGROUND_CANDIDATE"; cases.append(row)
        for row in cases:
            with self.subTest(row=row), mock.patch.object(access_io, "_open_relative") as opened:
                with self.assertRaises(access_io.CorpusAccessError):
                    self.reader().materialize_backgrounds([row], "TRAIN_DEVELOPMENT")
                opened.assert_not_called()
        self.decoder.assert_not_called()

    def test_background_group_cannot_cross_splits(self):
        rows = [self.background(frame=0), self.background(frame=1, split="DEVELOPMENT")]
        with self.assertRaisesRegex(access_io.CorpusAccessError, "group crosses"):
            self.reader().materialize_backgrounds(rows, "TRAIN_DEVELOPMENT")
        self.decoder.assert_not_called()

    def test_short_write_preserves_partial_counter_and_denies_retry(self):
        reader = self.reader()
        original = access_io.os.write
        def short(descriptor, content):
            return original(descriptor, content[:10])
        with mock.patch.object(access_io.os, "write", side_effect=short):
            with self.assertRaisesRegex(access_io.CorpusAccessError, "short cache write"):
                reader.materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        self.assertEqual(reader.audit["background_cache_bytes_written"], 10)
        partial = reader.audit["background_stages"]["TRAIN_DEVELOPMENT"]["artifacts"][0]
        self.assertEqual(partial["size_bytes"], 10)
        self.assertEqual(partial["sha256"], checksum(bytes([1]) * 10))
        self.assertFalse(partial["complete"])
        with self.assertRaisesRegex(access_io.CorpusAccessError, "closed or failed"):
            reader.materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")

    def test_second_output_creation_failure_preserves_first_output_identity(self):
        reader = self.reader()
        original = access_io._open_relative
        def fail_second(root, relative, *, output=False):
            if output and relative.endswith(".jsonl"):
                raise OSError("synthetic second output open failure")
            return original(root, relative, output=output)
        with mock.patch.object(access_io, "_open_relative", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "second output"):
                reader.materialize_backgrounds([self.background()], "TRAIN_DEVELOPMENT")
        partial = reader.audit["background_stages"]["TRAIN_DEVELOPMENT"]["artifacts"]
        self.assertEqual(len(partial), 1)
        self.assertTrue(partial[0]["path"].endswith("/cachetrain_dev.bin"))
        self.assertEqual(partial[0]["size_bytes"], 0)
        self.assertEqual(partial[0]["sha256"], checksum(b""))
        self.assertFalse(partial[0]["complete"])


if __name__ == "__main__":
    unittest.main()
