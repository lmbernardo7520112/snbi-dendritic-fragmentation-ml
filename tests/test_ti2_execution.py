"""Closed runner entry checks: AST and denied guard only, no scientific calls."""

import ast
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

from snbi_fragmentation import ti2_authority


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_ti2.py"


def executable_statements(body):
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        return body[1:]
    return body


class ExecutionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        specification = importlib.util.spec_from_file_location("ti2_closed_runner_controls", RUNNER)
        cls.runner = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(cls.runner)

    def first_call(self, statements):
        first = executable_statements(statements)[0]
        self.assertIsInstance(first, ast.Expr)
        self.assertIsInstance(first.value, ast.Call)
        self.assertIsInstance(first.value.func, ast.Name)
        return first.value.func.id

    def test_every_stage_and_scientific_helper_checks_authority_first(self):
        expected = {"preflight", "pilot", "estimate", "validate", "load_native", "registration_mask", "measure_pairs", "write_new"}
        definitions = {node.name: node for node in self.tree.body if isinstance(node, ast.FunctionDef)}
        self.assertEqual(set(definitions) - {"command", "stage_guard"}, expected)
        for name in sorted(expected):
            with self.subTest(entry=name):
                self.assertEqual(self.first_call(definitions[name].body), "stage_guard")
        for name in ("stage_guard", "command"):
            with self.subTest(entry=name):
                self.assertEqual(self.first_call(definitions[name].body), "require_scientific_authority")

    def test_cli_checks_authority_before_argument_or_source_parsing(self):
        blocks = [node for node in self.tree.body if isinstance(node, ast.If)]
        self.assertEqual(len(blocks), 1)
        self.assertEqual(self.first_call(blocks[0].body), "stage_guard")

    def test_runner_import_does_not_import_scientific_runtime(self):
        for statement in self.tree.body:
            if isinstance(statement, (ast.FunctionDef, ast.If)):
                continue
            for node in ast.walk(statement):
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse((node.module or "").startswith(("snbi_fragmentation", "numpy", "scipy")))
                elif isinstance(node, ast.Import):
                    self.assertFalse(any(alias.name.startswith(("snbi_fragmentation", "numpy", "scipy")) for alias in node.names))

    def test_denied_guard_never_inspects_working_directory_or_calls_a_tool(self):
        with patch.object(Path, "cwd") as current_directory, patch.object(self.runner, "command") as command:
            with self.assertRaisesRegex(ti2_authority.ScientificExecutionBlocked, "terminally closed"):
                self.runner.stage_guard()
        current_directory.assert_not_called()
        command.assert_not_called()

    def test_invalid_authority_denies_before_any_runner_tool(self):
        with patch.object(ti2_authority, "load_governance", side_effect=ValueError), patch.object(self.runner, "command") as command:
            with self.assertRaisesRegex(ti2_authority.ScientificExecutionBlocked, "invalid canonical"):
                self.runner.stage_guard()
        command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
