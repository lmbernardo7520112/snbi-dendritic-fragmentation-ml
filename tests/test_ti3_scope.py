"""Text-only adversarial TI3 dependency boundary checks."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import check_ti2_scope, check_ti3_scope


class TI3ScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        (self.root / "scripts/active.py").write_text("import sklearn\n", encoding="utf-8")
        (self.root / "requirements-ti3-ml.txt").write_text("\n".join(check_ti3_scope.REQUIREMENTS) + "\n", encoding="utf-8")
        (self.root / "pyproject.toml").write_text("[project]\ndependencies = []\n", encoding="utf-8")
        self.manifest = {"domains": {"TI3_ACTIVE": [{"path": "scripts/active.py", "git_mode": "100644", "state": "TRACKED"}]}}
        self.entries = [("100644", "scripts/active.py")]

    def audit(self):
        return check_ti3_scope.audit(entries=self.entries, root=self.root, manifest=self.manifest)

    def test_sklearn_legacy_fails(self):
        self.assertTrue(check_ti2_scope.source_violations("import sklearn", "scripts/legacy.py"))

    def test_sklearn_active_passes(self):
        self.assertEqual(self.audit()["status"], "PASS")

    def test_torch_active_fails(self):
        (self.root / "scripts/active.py").write_text("import torch\n", encoding="utf-8")
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_all_frozen_imports_pass(self):
        self.assertFalse(check_ti3_scope.source_violations("import numpy, scipy, skimage, sklearn", "scripts/active.py"))

    def test_other_third_party_fails(self):
        self.assertTrue(check_ti3_scope.source_violations("import pandas", "scripts/active.py"))

    def test_literal_and_unresolved_dynamic_import_fail(self):
        for source in ("__import__('torch')", "importlib.import_module('keras')", "__import__(name)"):
            with self.subTest(source=source):
                self.assertTrue(check_ti3_scope.source_violations(source, "scripts/active.py"))

    def test_extra_requirement_fails(self):
        with (self.root / "requirements-ti3-ml.txt").open("a") as stream:
            stream.write("pandas==2.0.0\n")
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_changed_pin_fails(self):
        path = self.root / "requirements-ti3-ml.txt"
        path.write_text(path.read_text().replace("1.26.4", "2.0.0"), encoding="utf-8")
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_legacy_dependency_fails(self):
        (self.root / "pyproject.toml").write_text('[project]\ndependencies = ["sklearn"]\n', encoding="utf-8")
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_unlisted_path_denied_before_text(self):
        self.entries.append(("100644", "scripts/annotations.py"))
        with mock.patch.object(check_ti3_scope, "read_text", side_effect=AssertionError("must not read")):
            self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_planned_entry_cannot_be_audited_as_tracked(self):
        self.manifest["domains"]["TI3_ACTIVE"][0]["state"] = "PLANNED"
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_duplicate_inventory_fails(self):
        self.entries *= 2
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_nonregular_entry_fails_before_read(self):
        self.entries = [("120000", "scripts/active.py")]
        with mock.patch.object(check_ti3_scope, "read_text", side_effect=AssertionError("must not read")):
            self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_worktree_symlink_fails(self):
        path = self.root / "scripts/active.py"
        path.unlink()
        path.symlink_to("missing.py")
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_syntax_error_fails(self):
        self.assertTrue(check_ti3_scope.source_violations("import (", "scripts/active.py"))


if __name__ == "__main__":
    unittest.main()
