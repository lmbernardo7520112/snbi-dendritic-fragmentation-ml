from __future__ import annotations

import unittest
from subprocess import CompletedProcess
from unittest.mock import patch

from scripts import check_local_environment as environment


class LocalEnvironmentTests(unittest.TestCase):
    @patch.object(environment, "read_proc_key", return_value="1")
    @patch.object(environment, "run_sanitized")
    def test_default_diagnostic_does_not_probe_sandbox(self, run, _read):
        run.return_value = {"available": True, "exit_code": 0, "summary": "ok"}
        report = environment.diagnose(probe=False)
        self.assertEqual(report["collection_status"], "COLLECTED")
        self.assertEqual(report["mutating_commands_requested"], 0)
        self.assertFalse(report["network_required"])
        self.assertEqual(report["bwrap_capability"]["status"], "NOT_RUN")
        self.assertEqual(
            report["codex_write_readiness"],
            "BLOCKED_REQUIRES_REAL_CODEX_SANDBOX_CHECK_AND_AUTHOR_DECISION",
        )
        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual(commands, list(environment.VERSION_COMMANDS.values()))
        self.assertFalse(any("/bin/true" in command for command in commands))

    @patch.object(environment, "run_sanitized")
    def test_failed_inert_probe_is_blocked(self, run):
        run.return_value = {"available": True, "exit_code": 1, "summary": "operation not permitted"}
        self.assertEqual(environment.bwrap_capability_probe()["status"], "BLOCKED")
        self.assertEqual(run.call_count, 1)

    @patch.object(environment.subprocess, "run")
    def test_command_environment_is_minimal_and_output_is_redacted(self, run):
        run.return_value = CompletedProcess(
            args=["git", "--version"], returncode=1,
            stdout="", stderr="PRIVATE_MARKER_SHOULD_NOT_LEAK",
        )
        result = environment.run_sanitized(["git", "--version"], output_policy="version")
        self.assertEqual(result["summary"], "command-failed-redacted")
        self.assertNotIn("PRIVATE_MARKER", str(result))
        self.assertEqual(run.call_args.kwargs["env"], environment.SAFE_ENV)
        self.assertNotIn("HOME", run.call_args.kwargs["env"])


if __name__ == "__main__":
    unittest.main()
