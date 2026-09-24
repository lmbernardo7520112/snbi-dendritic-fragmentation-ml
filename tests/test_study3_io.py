"""Study3 capability tests with fabricated metadata and fully mocked I/O."""
from copy import deepcopy
import hashlib
import importlib.util
import unittest
from unittest.mock import patch

from snbi_fragmentation import study2d_io as historical
from snbi_fragmentation import study3_io as io

NUMPY = importlib.util.find_spec("numpy") is not None


def synthetic_rows():
    rows = []
    for i, label in enumerate((1, 0)):
        payload = bytes([i]) * 8450
        hashes = {"pair_sha256": hashlib.sha256(payload).hexdigest(),
                  "structural_patch_sha256": hashlib.sha256(payload[:4225]).hexdigest(),
                  "solutal_patch_sha256": hashlib.sha256(payload[4225:]).hexdigest()}
        path = historical.POSITIVE if label else historical.BACKGROUND
        row = {"sample_id": f"synthetic-{i}", "group_id": f"synthetic-group-{i}",
               "acquisition_id": "bottom_up_anti_parallel", "split": "TRAIN",
               "tier": "GOLD" if label else "BACKGROUND", "kind": "positive" if label else "background",
               "label": label, "frame_index": i, "cv_fold": i,
               "storage": {"path": path, "row_index": i, "offset": i * 8450,
                    "expected_file_bytes": historical.FILES[path], "shape": [2, 65, 65],
                    "dtype": "uint8", **hashes}}
        if label:
            row.update(positive_row_index=i, **hashes)
        rows.append(row)
    return rows


class ExplodingRoot:
    def __fspath__(self):
        raise AssertionError("root touched before denial")


class Study3IOTests(unittest.TestCase):
    def test_constructor_is_inert(self):
        with patch.object(historical, "_open_file") as opened:
            io.Study3TrainAccess(ExplodingRoot(), synthetic_rows())
        opened.assert_not_called()

    def test_receipt_is_required_before_path(self):
        with patch.object(historical, "_open_file") as opened:
            with self.assertRaises(historical.TrainAccessError):
                io.Study3TrainAccess(ExplodingRoot(), synthetic_rows()).load()
        opened.assert_not_called()

    def test_receipt_digest_requires_exact_hex(self):
        for receipt, head in (("", "a" * 40), ("g" * 64, "a" * 40), ("a" * 64, "b" * 39)):
            with self.subTest(receipt=receipt), self.assertRaises(io.Study3AccessError):
                io.TrainReceiptGrant(synthetic_rows(), receipt, head)

    def test_grant_is_single_use(self):
        rows = synthetic_rows()
        grant = io.TrainReceiptGrant(rows, "a" * 64, "b" * 40)
        self.assertIs(grant("LOAD_TRAIN_ROWS", rows)["authorized"], True)
        with self.assertRaises(io.Study3AccessError):
            grant("LOAD_TRAIN_ROWS", rows)

    def test_failed_grant_is_consumed(self):
        rows = synthetic_rows()
        grant = io.TrainReceiptGrant(rows, "a" * 64, "b" * 40)
        with self.assertRaises(io.Study3AccessError):
            grant("TEST", rows)
        with self.assertRaises(io.Study3AccessError):
            grant("LOAD_TRAIN_ROWS", rows)

    def test_locator_membership_bound_before_path(self):
        rows = synthetic_rows()
        grant = io.TrainReceiptGrant(rows, "a" * 64, "b" * 40)
        changed = deepcopy(rows)
        changed[1]["storage"]["row_index"] += 1
        changed[1]["storage"]["offset"] += 8450
        with patch.object(historical, "_open_file") as opened:
            with self.assertRaises(io.Study3AccessError):
                io.Study3TrainAccess(ExplodingRoot(), changed, grant).load()
        opened.assert_not_called()

    def test_original_mutation_cannot_change_grant(self):
        rows = synthetic_rows()
        grant = io.TrainReceiptGrant(rows, "a" * 64, "b" * 40)
        rows[0]["frame_index"] += 1
        with self.assertRaises(io.Study3AccessError):
            grant("LOAD_TRAIN_ROWS", rows)

    def check_denial(self, mutate):
        rows = synthetic_rows()
        grant = io.TrainReceiptGrant(rows, "a" * 64, "b" * 40)
        mutate(rows)
        with patch.object(historical, "_open_file") as opened:
            with self.assertRaises(historical.TrainAccessError):
                io.Study3TrainAccess(ExplodingRoot(), rows, grant).load()
        opened.assert_not_called()

    def test_dev_denied_before_path(self):
        self.check_denial(lambda r: r[0].update(split="DEVELOPMENT"))

    def test_test_denied_before_path(self):
        self.check_denial(lambda r: r[0].update(split="TEST"))

    def test_silver_denied_before_path(self):
        self.check_denial(lambda r: r[0].update(tier="SILVER"))

    def test_unlabeled_denied_before_path(self):
        self.check_denial(lambda r: r[0].update(tier="UNLABELED_PRE"))

    def test_test_cache_denied_before_path(self):
        self.check_denial(lambda r: r[1]["storage"].update(path="data/derived/study2c/cachetest.bin"))

    def test_test_index_denied_before_path(self):
        self.check_denial(lambda r: r[1]["storage"].update(path="data/derived/study2c/cachetest-index.json"))

    def test_mp4_denied_before_path(self):
        self.check_denial(lambda r: r[0]["storage"].update(path="ESM1.mp4"))

    def test_unknown_path_denied_before_path(self):
        self.check_denial(lambda r: r[0]["storage"].update(path="../uncontrolled.bin"))

    def test_bool_label_denied_before_path(self):
        self.check_denial(lambda r: r[0].update(label=True))

    @unittest.skipUnless(NUMPY, "NumPy required by strict Study3 dependency profile")
    def test_delegation_uses_only_exact_offsets_and_closes(self):
        rows = synthetic_rows()
        grant = io.TrainReceiptGrant(rows, "a" * 64, "b" * 40)
        audit = {}
        reader = io.Study3TrainAccess(ExplodingRoot(), rows, grant, audit)
        def fingerprint(fd):
            return (1, fd, 33188, historical.FILES[historical.POSITIVE if fd == 10 else historical.BACKGROUND], 0, 0)
        with patch.object(historical, "_open_file", side_effect=[10, 11]), \
             patch.object(historical, "_fingerprint", side_effect=fingerprint), \
             patch.object(historical.os, "pread", side_effect=[bytes(8450), bytes([1]) * 8450]) as pread, \
             patch.object(historical.os, "close"):
            values = reader.load()
            self.assertEqual(values.shape, (2, 2, 65, 65))
            self.assertEqual([c.args for c in pread.call_args_list], [(10, 8450, 0), (11, 8450, 8450)])
            self.assertEqual(audit["rows_authenticated"], 2)
            self.assertEqual(audit["bytes_read"], 16900)
            self.assertTrue(audit["all_descriptors_closed"])
            with self.assertRaises(historical.TrainAccessError):
                reader.load()

    def test_no_decoder_bulk_read_or_memory_mapping_added(self):
        import ast
        import inspect
        tree = ast.parse(inspect.getsource(io))
        attributes = {n.func.attr for n in ast.walk(tree)
                      if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertFalse(attributes & {"read", "read_bytes", "mmap", "memmap", "Popen"})
        self.assertIs(io.TrainCorpusAccess, historical.TrainCorpusAccess)


if __name__ == "__main__":
    unittest.main()
