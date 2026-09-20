"""Text-only checks of the two-path Torch exception and its CPU dependency lock."""
from pathlib import Path
import unittest
from unittest import mock

from scripts import check_ti3_scope as guard


class TI3CScopeTests(unittest.TestCase):
    def setUp(self):
        self.path = "src/snbi_fragmentation/ti3c_cnn.py"
        self.entries = [("100644", self.path)]
        self.manifest = {"domains": {"TI3_ACTIVE": [{
            "path": self.path, "git_mode": "100644", "state": "TRACKED",
        }]}}
        self.constraints = "\n".join(guard.CNN_CONSTRAINTS) + "\n"
        self.texts = {
            self.path: "import torch\nfrom torch import nn\n",
            "requirements-ti3-ml.txt": "\n".join(guard.REQUIREMENTS) + "\n",
            "requirements-ti3c-cnn.txt": "\n".join(guard.CNN_REQUIREMENTS) + "\n",
            "constraints-ti3c-cnn.txt": self.constraints,
            "pyproject.toml": "[project]\ndependencies = []\n",
        }

    def audit(self):
        def read(_root, path):
            if path not in self.texts:
                raise FileNotFoundError(path)
            return self.texts[path]
        with mock.patch.object(guard, "read_text", side_effect=read):
            return guard.audit(entries=self.entries, root=Path("synthetic"),
                               manifest=self.manifest)

    def test_exact_cnn_and_test_imports_allowed(self):
        for path in guard.TORCH_PATHS:
            with self.subTest(path=path):
                self.assertEqual(guard.source_violations("import torch\nfrom torch.nn import Conv2d", path), [])

    def test_torch_rejected_in_a_b_runner_and_unknown_paths(self):
        for path in ("src/snbi_fragmentation/ti3_baseline.py",
                     "src/snbi_fragmentation/ti3b_ablation.py",
                     "scripts/run_ti3c_cnn.py", "tests/other.py"):
            with self.subTest(path=path):
                self.assertTrue(guard.source_violations("import torch", path))

    def test_similar_paths_do_not_inherit_exception(self):
        for path in ("./" + self.path, "src/snbi_fragmentation/ti3c_other.py",
                     "src/snbi_fragmentation/TI3C_cnn.py", self.path + ".py"):
            with self.subTest(path=path):
                self.assertTrue(guard.source_violations("import torch", path))

    def test_literal_dynamic_torch_uses_same_path_boundary(self):
        for source in ("__import__('torch')", "importlib.import_module('torch.nn')"):
            self.assertFalse(guard.source_violations(source, self.path))
            self.assertTrue(guard.source_violations(source, "scripts/other.py"))

    def test_unresolved_dynamic_import_still_blocked(self):
        self.assertTrue(guard.source_violations("__import__(module)", self.path))

    def test_other_ml_families_blocked_even_in_cnn_path(self):
        for name in sorted(guard.BLOCKED_ML - {"torch"}):
            with self.subTest(name=name):
                self.assertTrue(guard.source_violations(f"import {name}", self.path))

    def test_local_module_list_cannot_grant_blocked_library(self):
        self.assertTrue(guard.source_violations("import torch", "scripts/other.py", {"torch"}))
        self.assertTrue(guard.source_violations("import torchvision", self.path, {"torchvision"}))

    def test_invalid_python_still_blocked(self):
        self.assertTrue(guard.source_violations("from torch import (", self.path))

    def test_exact_cpu_dependency_contract_passes(self):
        self.assertEqual(self.audit()["status"], "PASS")

    def test_missing_constraint_file_blocks(self):
        del self.texts["constraints-ti3c-cnn.txt"]
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_missing_requirements_file_blocks(self):
        del self.texts["requirements-ti3c-cnn.txt"]
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_unapproved_requirements_option_blocks(self):
        self.texts["requirements-ti3c-cnn.txt"] += "--extra-index-url https://example.invalid\n"
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_wrong_torch_build_or_version_blocks(self):
        for version in ("2.4.1", "2.4.1+cu121", "2.5.0+cpu"):
            with self.subTest(version=version):
                changed = self.constraints.replace("2.4.1+cpu", version)
                self.assertTrue(guard.cnn_constraint_violations(changed))

    def test_frozen_scientific_pin_change_blocks(self):
        self.texts["constraints-ti3c-cnn.txt"] = self.constraints.replace("numpy==1.26.4", "numpy==2.0.0")
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_missing_transitive_pin_blocks(self):
        self.assertTrue(guard.cnn_constraint_violations(self.constraints.replace("mpmath==1.3.0\n", "")))

    def test_unpinned_range_url_and_option_block(self):
        for extra in ("filelock>=3.0", "filelock @ https://example.invalid/wheel.whl",
                      "--index-url https://example.invalid", "# unlocked"):
            with self.subTest(extra=extra):
                self.assertTrue(guard.cnn_constraint_violations(self.constraints + extra + "\n"))

    def test_extra_framework_cuda_or_unknown_dependency_blocks(self):
        for name in ("torchvision", "torchaudio", "tensorflow", "nvidia-cuda-runtime-cu12", "pandas"):
            with self.subTest(name=name):
                self.assertTrue(guard.cnn_constraint_violations(self.constraints + name + "==1.0.0\n"))

    def test_alias_duplicate_pin_blocks(self):
        self.assertTrue(guard.cnn_constraint_violations(self.constraints + "typing_extensions==4.15.0\n"))

    def test_torch_transitive_pin_drift_blocks(self):
        changed = self.constraints.replace("setuptools==84.0.0", "setuptools==83.0.0")
        self.assertTrue(guard.cnn_constraint_violations(changed))

    def test_historical_inventory_does_not_require_cnn_files(self):
        self.entries = [("100644", "scripts/historical.py")]
        self.manifest["domains"]["TI3_ACTIVE"][0]["path"] = "scripts/historical.py"
        self.texts["scripts/historical.py"] = "import sklearn\n"
        del self.texts["requirements-ti3c-cnn.txt"], self.texts["constraints-ti3c-cnn.txt"]
        self.assertEqual(self.audit()["status"], "PASS")

    def test_planned_cnn_path_requires_dependency_contract(self):
        self.entries = []
        self.manifest["domains"]["TI3_ACTIVE"][0]["state"] = "PLANNED"
        del self.texts["constraints-ti3c-cnn.txt"]
        self.assertEqual(self.audit()["status"], "BLOCKED")

    def test_cnn_exception_does_not_admit_unlisted_inventory(self):
        self.manifest["domains"]["TI3_ACTIVE"] = []
        with mock.patch.object(guard, "read_text", side_effect=AssertionError("must not read")):
            self.assertEqual(guard.audit(entries=self.entries, manifest=self.manifest)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
