from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import check_repository_data as guard
from scripts.check_repository_data import audit_entries, classify_path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryDataGuardTests(unittest.TestCase):
    def test_allows_source_and_text_evidence(self):
        for path in (
            "src/snbi_fragmentation/domain.py",
            "artifacts/evidence/G1/gate-decision.json",
            "artifacts/metadata/README.md",
        ):
            with self.subTest(path=path):
                self.assertIsNone(classify_path(path))

    def test_blocks_data_paths_and_suffixes_case_insensitively(self):
        cases = (
            "data/raw/source.bin",
            "data/derived/frame.txt",
            "elsewhere/FRAME.PNG",
            "weights.Model.ONNX",
            "archive.tar.gz",
            "cache/experiment.ZARR/chunk",
            "labels/events.json",
            "frames/frame_without_suffix",
            "artifacts/evidence/G3/overlay.svg",
            "docs/AGENTS.md",
            "AGENTS.override.md",
        )
        for path in cases:
            with self.subTest(path=path):
                self.assertIsNotNone(classify_path(path))

    def test_blocks_unsafe_paths_and_symlinks(self):
        self.assertIsNotNone(classify_path("/tmp/outside.txt"))
        self.assertIsNotNone(classify_path("docs/../outside.txt"))
        self.assertIsNotNone(classify_path("README.md", mode="120000"))
        self.assertIsNotNone(classify_path("vendor", mode="160000"))
        self.assertIsNotNone(classify_path("data/raw"))

    def test_synthetic_audit_fails_closed(self):
        report = audit_entries([
            ("100644", "README.md"),
            ("100644", "data/raw/ESM1.MP4"),
        ])
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["content_bytes_read"], 0)

    @patch.object(guard, "require_standalone_checkout")
    @patch.object(guard.subprocess, "run")
    def test_git_inventory_uses_fixed_environment_and_checks_root(self, run, checkout):
        run.side_effect = [
            subprocess.CompletedProcess(
                args=[], returncode=0, stdout=f"{ROOT}\n", stderr=""
            ),
            subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout=b"100644 0000000000000000000000000000000000000000 0\tREADME.md\0",
                stderr=b"",
            ),
        ]
        self.assertEqual(guard.tracked_entries(), [("100644", "README.md")])
        checkout.assert_called_once_with(ROOT)
        self.assertEqual(run.call_count, 2)
        for call in run.call_args_list:
            self.assertEqual(call.kwargs["env"], guard.SAFE_GIT_ENV)
            self.assertNotIn("HOME", call.kwargs["env"])

    def test_gitignore_covers_fictitious_lowercase_data_names(self):
        names = "\n".join([
            "data/raw/fictitious.mp4",
            "data/derived/fictitious.png",
            "fictitious.npy",
            "fictitious.onnx",
            "fictitious.ipynb",
            "fictitious.sqlite3",
            "labels/fictitious.json",
            "cache/fictitious.zarr/chunk",
        ]) + "\n"
        if not (ROOT / ".git").is_dir():
            self.skipTest("requires the real Git checkout used by local/CI validation")
        completed = subprocess.run(
            [
                "git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                "-c", "core.excludesFile=/dev/null", "check-ignore",
                "--no-index", "--stdin",
            ],
            cwd=ROOT, input=names, capture_output=True, text=True, check=False,
            env={
                "PATH": "/usr/bin:/bin:/snap/bin",
                "LANG": "C", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0",
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
                "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
            },
        )
        self.assertEqual(completed.returncode, 0, "git check-ignore failed")
        self.assertEqual(set(completed.stdout.splitlines()), set(names.splitlines()))


if __name__ == "__main__":
    unittest.main()
