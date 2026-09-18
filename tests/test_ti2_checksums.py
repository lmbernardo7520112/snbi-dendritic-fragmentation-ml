"""Checksum safety contracts use fresh textual fixtures, never scientific data."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import check_ti2_checksums as checksums


ROOT = Path(__file__).absolute().parents[1]


class TextualChecksumTests(unittest.TestCase):
    def setUp(self):
        temporary_parent = ROOT / ".bootstrap-test-tmp"
        temporary_parent.mkdir(exist_ok=True)
        if temporary_parent.is_symlink():
            self.fail("synthetic temporary parent must not be a symlink")
        temporary = tempfile.TemporaryDirectory(prefix="checksums-", dir=temporary_parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = self.root / checksums.MANIFEST
        self.manifest.parent.mkdir(parents=True)
        self.entries = [("100644", checksums.MANIFEST)]

    def text_file(self, relative="docs/evidence.txt", content=b"synthetic evidence\r\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        self.entries.append(("100644", relative))
        return f"{hashlib.sha256(content).hexdigest()}  {relative}\n"

    def verify(self, text):
        self.manifest.write_text(text, encoding="utf-8", newline="")
        return checksums.verify(self.root, entries=self.entries)

    def assert_rejected_before_member_read(self, text):
        with patch.object(checksums, "_read_regular_file", wraps=checksums._read_regular_file) as reader:
            report = self.verify(text)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["verified_count"], 0)
        self.assertTrue(report["violations"])
        self.assertEqual([call.args[1] for call in reader.call_args_list], [checksums.MANIFEST])
        return report

    def test_exact_bytes_and_deterministic_counts(self):
        text = self.text_file(content="synthetic µ\r\n".encode("utf-8"))
        first = self.verify("# textual fixtures only\n" + text)
        self.assertEqual(first, self.verify("# textual fixtures only\n" + text))
        self.assertEqual(first["status"], "PASS")
        self.assertEqual(first["listed_count"], 1)
        self.assertEqual(first["unique_count"], 1)
        self.assertEqual(first["verified_count"], 1)
        self.assertEqual(first["historical_checksum_count"], 70)
        self.assertEqual(first["violations"], [])

    def test_newline_normalization_cannot_hide_a_mismatch(self):
        self.text_file(content=b"synthetic\r\n")
        digest = hashlib.sha256(b"synthetic\n").hexdigest()
        report = self.verify(f"{digest}  docs/evidence.txt\n")
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["verified_count"], 0)
        self.assertTrue(any(item["reason"] == "SHA-256 mismatch" for item in report["violations"]))

    def test_malformed_hashes_and_entry_syntax_are_rejected(self):
        self.text_file()
        for line in ("z" * 64 + "  docs/evidence.txt", "a" * 63 + "  docs/evidence.txt",
                     "a" * 65 + "  docs/evidence.txt", "a" * 64 + " docs/evidence.txt",
                     "a" * 64 + "  "):
            with self.subTest(line=line):
                self.assert_rejected_before_member_read(line + "\n")

    def test_empty_manifest_is_not_a_vacuous_pass(self):
        self.assert_rejected_before_member_read("# no entries\n\n")

    def test_duplicates_block_all_member_reads(self):
        line = self.text_file()
        report = self.assert_rejected_before_member_read(line + line)
        self.assertEqual(report["listed_count"], 2)
        self.assertEqual(report["unique_count"], 1)

    def test_manifest_cannot_hash_itself(self):
        self.assert_rejected_before_member_read("a" * 64 + "  " + checksums.MANIFEST + "\n")

    def test_absolute_parent_dot_and_noncanonical_paths_rejected_before_open(self):
        for relative in ("/outside.txt", "../outside.txt", "docs/../../outside.txt",
                         "./README.md", "docs//evidence.txt", "C:/outside.txt",
                         "docs\\evidence.txt", "docs/../README.md", "docs/a\t.txt"):
            with self.subTest(path=relative):
                self.entries.append(("100644", relative))
                self.assert_rejected_before_member_read("a" * 64 + "  " + relative + "\n")

    def test_experimental_and_private_paths_rejected_without_stat_or_open(self):
        good = self.text_file()
        for relative in ("data/note.txt", "data/derived/frame.raw", "video.mp4", "frame.png",
                         "frame.raw", "arrays.npy", "archive.zip", "models/notes.txt",
                         "datasets/notes.json", "docs/frames/note.txt", "docs/frame.PNG/note.txt",
                         "notes.csv", ".env", ".git/config", "credentials/token.txt"):
            with self.subTest(path=relative):
                self.entries.append(("100644", relative))
                self.assert_rejected_before_member_read(good + "a" * 64 + "  " + relative + "\n")

    def test_untracked_file_is_rejected_even_when_it_exists(self):
        line = self.text_file()
        self.entries = self.entries[:1]
        self.assert_rejected_before_member_read(line)

    def test_missing_tracked_file_fails(self):
        self.entries.append(("100644", "docs/missing.txt"))
        report = self.verify("a" * 64 + "  docs/missing.txt\n")
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["verified_count"], 0)

    def test_tracked_symlink_or_submodule_mode_is_rejected_before_open(self):
        line = self.text_file()
        for mode in ("120000", "160000", "040000"):
            self.entries[-1] = (mode, "docs/evidence.txt")
            self.assert_rejected_before_member_read(line)

    def test_symlink_file_metadata_is_rejected_without_creating_links(self):
        line = self.text_file()
        real_stat = checksums.os.stat

        def synthetic_link(path, *args, **kwargs):
            if path == "evidence.txt":
                return SimpleNamespace(st_mode=stat.S_IFLNK | 0o777)
            return real_stat(path, *args, **kwargs)

        with patch.object(checksums.os, "stat", side_effect=synthetic_link), \
                patch.object(checksums.os, "open", wraps=checksums.os.open) as opener:
            report = self.verify(line)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertNotIn("evidence.txt", [call.args[0] for call in opener.call_args_list])

    def test_symlink_directory_cannot_resolve_outside_root(self):
        line = self.text_file()
        real_stat = checksums.os.stat

        def synthetic_link(path, *args, **kwargs):
            if path == "docs":
                return SimpleNamespace(st_mode=stat.S_IFLNK | 0o777)
            return real_stat(path, *args, **kwargs)

        with patch.object(checksums.os, "stat", side_effect=synthetic_link), \
                patch.object(checksums.os, "open", wraps=checksums.os.open) as opener:
            report = self.verify(line)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertNotIn("docs", [call.args[0] for call in opener.call_args_list])
        self.assertNotIn("evidence.txt", [call.args[0] for call in opener.call_args_list])

    def test_nonregular_directory_is_never_opened_as_a_file(self):
        (self.root / "directory.txt").mkdir()
        self.entries.append(("100644", "directory.txt"))
        with patch.object(checksums.os, "open", wraps=checksums.os.open) as opener:
            report = self.verify("a" * 64 + "  directory.txt\n")
        self.assertEqual(report["status"], "BLOCKED")
        self.assertNotIn("directory.txt", [call.args[0] for call in opener.call_args_list])

    def test_nonregular_fifo_metadata_is_rejected_without_creating_fifo(self):
        line = self.text_file()
        real_stat = checksums.os.stat

        def synthetic_fifo(path, *args, **kwargs):
            if path == "evidence.txt":
                return SimpleNamespace(st_mode=stat.S_IFIFO | 0o600)
            return real_stat(path, *args, **kwargs)

        with patch.object(checksums.os, "stat", side_effect=synthetic_fifo), \
                patch.object(checksums.os, "open", wraps=checksums.os.open) as opener:
            report = self.verify(line)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertNotIn("evidence.txt", [call.args[0] for call in opener.call_args_list])

    def test_manifest_itself_must_be_tracked_regular_text(self):
        for entries in ([], [("120000", checksums.MANIFEST)]):
            with patch.object(checksums, "_read_regular_file") as reader:
                report = checksums.verify(self.root, entries=entries)
            self.assertEqual(report["status"], "BLOCKED")
            reader.assert_not_called()

    def test_unmerged_duplicate_git_entries_fail_closed(self):
        with patch.object(checksums, "_read_regular_file") as reader:
            report = checksums.verify(self.root, entries=self.entries * 2)
        self.assertEqual(report["status"], "BLOCKED")
        reader.assert_not_called()

    def test_manifest_decoding_failure_is_nonzero(self):
        self.manifest.write_bytes(b"\xff")
        report = checksums.verify(self.root, entries=self.entries)
        self.assertEqual(report["status"], "BLOCKED")

    def test_cli_returns_nonzero_on_any_violation(self):
        with patch.object(checksums, "verify", return_value={"status": "BLOCKED"}), \
                patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(checksums.main(), 1)

    def test_cli_never_supplies_an_untracked_exception(self):
        with patch.object(checksums, "verify", return_value={"status": "PASS"}) as verifier, \
                patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(checksums.main(), 0)
        verifier.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
