from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScopeGuardTests(unittest.TestCase):
    def test_ti2_plus_modules_are_absent(self) -> None:
        blocked = [
            "registration", "annotation", "dataset", "splits", "baseline",
            "models", "training", "evaluation",
        ]
        for module in blocked:
            self.assertFalse((ROOT / f"src/snbi_fragmentation/{module}.py").exists())

    def test_ml_frameworks_are_not_declared(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        for package in ("torch", "tensorflow", "keras", "opencv", "moviepy"):
            self.assertNotIn(package, pyproject.lower())

    def test_scope_auditor_passes(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "scope_audit", ROOT / "scripts/check_ti1_scope.py"
        )
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        self.assertEqual(module.audit(entries=[("100644", "README.md")])["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
