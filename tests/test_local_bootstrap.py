from __future__ import annotations

import copy
import io
import json
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from subprocess import CalledProcessError
from unittest.mock import patch

from scripts import check_local_bootstrap as bootstrap
from scripts.check_local_bootstrap import validate, validate_vscode

ROOT = Path(__file__).resolve().parents[1]


class LocalBootstrapTests(unittest.TestCase):
    def test_static_bootstrap_contracts_pass_with_safe_index(self):
        report = validate(entries=[("100644", "README.md")])
        self.assertEqual(report["status"], "PASS", report["violations"])
        self.assertFalse(report["ti2_execution_authorized"])
        self.assertEqual(
            report["codex_write_readiness"],
            "BLOCKED_REQUIRES_REAL_CODEX_SANDBOX_CHECK_AND_AUTHOR_DECISION",
        )

    def test_vscode_json_is_valid_and_tasks_are_not_automatic(self):
        settings = json.loads((ROOT / ".vscode/settings.json").read_text(encoding="utf-8"))
        tasks = json.loads((ROOT / ".vscode/tasks.json").read_text(encoding="utf-8"))
        self.assertIn("files.watcherExclude", settings)
        for task in tasks["tasks"]:
            self.assertEqual(task["type"], "process")
            self.assertNotIn("runOptions", task)

    def test_task_allowlist_rejects_command_substitution(self):
        settings = json.loads((ROOT / ".vscode/settings.json").read_text(encoding="utf-8"))
        tasks = json.loads((ROOT / ".vscode/tasks.json").read_text(encoding="utf-8"))
        malicious = copy.deepcopy(tasks)
        malicious["tasks"][0]["command"] = "bash"
        malicious["tasks"][0]["args"] = ["-c", "git reset --hard"]
        self.assertTrue(validate_vscode(settings, malicious))

    @patch.object(
        bootstrap,
        "tracked_entries",
        side_effect=CalledProcessError(returncode=128, cmd=["git", "ls-files"]),
    )
    def test_missing_git_index_fails_closed_without_traceback(self, _tracked):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = bootstrap.main()
        report = json.loads(output.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(report["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
