from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import check_ti2_scope as scope
from snbi_fragmentation import ti2_authority


ROOT = Path(__file__).resolve().parents[1]


class ScopeGuardTests(unittest.TestCase):
    def test_ti3_plus_paths_are_blocked_even_with_nested_packages(self):
        for relative in (
            "src/snbi_fragmentation/labels.py",
            "src/snbi_fragmentation/event_ledger.py",
            "src/snbi_fragmentation/dataset/build.py",
            "scripts/run_training.py",
            "src/snbi_fragmentation/CNN.py",
        ):
            with self.subTest(relative=relative):
                self.assertTrue(scope.path_violations(relative))

    def test_ti2_numerical_modules_and_runner_are_allowed(self):
        for relative in (
            "src/snbi_fragmentation/ti2_pilot.py",
            "src/snbi_fragmentation/ti2_geometry.py",
            "scripts/run_ti2.py",
        ):
            with self.subTest(relative=relative):
                self.assertEqual(scope.path_violations(relative), [])

    def test_ml_imports_are_blocked_with_aliases_and_dynamic_literals(self):
        for source in (
            "import math, torch as t",
            "from tensorflow.keras import layers",
            "importlib.import_module('sklearn.metrics')",
            "__import__('torch')",
        ):
            with self.subTest(source=source):
                self.assertTrue(scope.source_violations(source, "src/example.py"))

    def test_comments_are_not_imports_and_invalid_python_fails_closed(self):
        self.assertEqual(scope.source_violations("# import torch\nimport math\n", "src/x.py"), [])
        self.assertTrue(scope.source_violations("def broken(", "src/x.py"))

    def test_tracked_data_blocks_before_any_source_read(self):
        with patch.object(scope, "read_source") as reader:
            report = scope.audit(entries=[("100644", "data/derived/frame.png")])
        self.assertEqual(report["status"], "BLOCKED")
        reader.assert_not_called()

    def test_scope_auditor_passes_and_later_phases_remain_blocked(self):
        report = scope.audit(entries=[("100644", "README.md")])
        self.assertEqual(report["status"], "PASS", json.dumps(report))
        self.assertIsNone(report["authorized_phase"])
        self.assertEqual(report["authorized_scientific_phases"], [])
        self.assertFalse(report["ti2_execution_authorized"])
        self.assertEqual(report["current_authorized_activity"], "NONE_AWAITING_AUTHOR_DECISION")
        self.assertEqual(report["scientific_readiness"], "BLOCKED")
        self.assertEqual(report["blocked_phases"], ["TI-2", "TI-2R", *[f"TI-{n}" for n in range(3, 9)]])

    def test_invalid_canonical_authority_stops_before_source_inspection(self):
        with patch.object(ti2_authority, "load_governance", side_effect=ValueError), \
                patch.object(scope, "read_source") as reader:
            report = scope.audit(entries=[("100644", "scripts/run_ti2.py")])
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIsNone(report["authorized_phase"])
        reader.assert_not_called()

    def test_gate_contradiction_blocks_before_source_inspection(self):
        with patch.object(scope, "audit_current_gates", return_value={
            "status": "BLOCKED", "violations": ["synthetic gate contradiction"],
            "document_count": 2,
        }), patch.object(scope, "read_source") as reader:
            report = scope.audit(entries=[("100644", "scripts/run_ti2.py")])
        self.assertEqual(report["status"], "BLOCKED")
        self.assertFalse(report["ti2_execution_authorized"])
        reader.assert_not_called()


if __name__ == "__main__":
    unittest.main()
