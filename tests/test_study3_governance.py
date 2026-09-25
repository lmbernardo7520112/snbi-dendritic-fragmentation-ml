"""Governance repair fixtures: Git identity metadata and source text only.

No real guard entrypoint, science preflight, payload, feature extraction or
model fit is invoked. Synthetic filesystem fixtures remain below the ignored
repository-local temporary root. Git history reads are limited to exact
authorized textual blobs used to certify historical and recovery custody.
"""

import ast
from copy import deepcopy
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import check_phase_scope as phase
from scripts import check_repository_data as data
from scripts import check_study3_governance as governance
from scripts import check_ti3_scope as ti3
from snbi_fragmentation import study3_execution as execution


ROOT = Path(__file__).absolute().parents[1]
BASE = "68ae723b392a41f52c07e2a8345437b169d5ea78"
MODULES = ("domain", "design", "io", "temporal_features", "cnn", "models", "metrics", "execution")
NEW_STUDY3_PYTHON = frozenset(
    ["src/snbi_fragmentation/study3_" + name + ".py" for name in MODULES]
    + ["tests/test_study3_" + name + ".py" for name in MODULES]
    + ["scripts/run_study3.py", "scripts/check_study3_governance.py", "tests/test_study3_governance.py"])
MODIFIED_GUARDS = {"scripts/check_phase_scope.py", "scripts/check_ti3_scope.py"}
RECOVERY_1_PYTHON = frozenset({"scripts/run_study3_recovery_1.py",
                             "tests/test_study3_execution_recovery_1.py"})
HISTORICAL_STUDY3_PATHS = NEW_STUDY3_PYTHON | RECOVERY_1_PYTHON
HISTORICAL_TORCH_PATHS = frozenset({"src/snbi_fragmentation/ti3c_cnn.py", "tests/test_ti3c_cnn.py",
                                  "src/snbi_fragmentation/study2c_cnn.py", "tests/test_study2c_cnn.py"})
STUDY3_TORCH_PATHS = frozenset({"src/snbi_fragmentation/study3_cnn.py", "tests/test_study3_cnn.py"})


class ScopeCompatibilityAssertions:
    """Partition explicitly declared additions before any snapshot exclusion."""

    def assert_study3_and_study4_additions(self, manifest, old_paths):
        self.assertEqual(set(manifest["domains"]), phase.DOMAIN_NAMES)
        self.assertEqual(len(NEW_STUDY3_PYTHON), 19)
        self.assertEqual(len(RECOVERY_1_PYTHON), 2)
        self.assertEqual(len(HISTORICAL_STUDY3_PATHS), 21)
        self.assertFalse(HISTORICAL_STUDY3_PATHS & old_paths)
        rows = [(domain, row) for domain, entries in manifest["domains"].items() for row in entries]
        paths = [row["path"] for _, row in rows]
        self.assertEqual(len(paths), len(set(paths)), "duplicate explicit classification")
        additions = {row["path"]: (domain, row) for domain, row in rows if row["path"] not in old_paths}
        self.assertTrue(HISTORICAL_STUDY3_PATHS <= additions.keys(), "missing historical Study3/Recovery path")
        historical, study4 = {}, {}
        for path, (domain, row) in additions.items():
            self.assertEqual(domain, "TI3_ACTIVE", path)
            self.assertEqual(row["classification"], "TI3_ACTIVE", path)
            self.assertEqual(row["state"], "TRACKED", path)
            if path in HISTORICAL_STUDY3_PATHS:
                expected_origin = "STUDY3_EXECUTION_RECOVERY_1" if path in RECOVERY_1_PYTHON else "STUDY3"
                self.assertEqual(row["origin_phase"], expected_origin, path)
                historical[path] = row
            else:
                self.assertIsInstance(row["origin_phase"], str, path)
                self.assertTrue(row["origin_phase"].startswith("STUDY4_"), path)
                self.assertIsNotNone(re.fullmatch(
                    r"(?:src/snbi_fragmentation/study4_|tests/test_study4_|scripts/(?:run|check)_study4_)"
                    r"[^/\\*?\[\]]*\.py", path), path)
                study4[path] = row
        self.assertEqual(set(historical), HISTORICAL_STUDY3_PATHS)
        return historical, study4


class CheckoutIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary_parent = ROOT / ".bootstrap-test-tmp"
        temporary_parent.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="study3-governance-", dir=temporary_parent)
        self.addCleanup(temporary.cleanup)
        self.temporary = Path(temporary.name)
        self.root = self.temporary / "checkout"
        self.root.mkdir()

    def linked(self):
        self.common = self.temporary / "canonical-git"
        self.gitdir = self.common / "worktrees" / "synthetic-study3"
        self.gitdir.mkdir(parents=True)
        (self.root / ".git").write_text("gitdir: " + str(self.gitdir) + "\n", encoding="utf-8")
        self.outputs = {"--show-toplevel": str(self.root), "--git-dir": str(self.gitdir),
                        "--git-common-dir": str(self.common)}

    def probes(self):
        def fake(command, **options):
            self.assertEqual(command[:3], ["git", "--no-optional-locks", "rev-parse"])
            self.assertEqual(options["cwd"], self.root)
            self.assertEqual(options["env"], data.SAFE_GIT_ENV)
            self.assertIs(options["check"], True)
            self.assertIs(options["capture_output"], True)
            self.assertIs(options["text"], True)
            return subprocess.CompletedProcess(command, 0, self.outputs[command[-1]] + "\n", "")
        return patch.object(phase.subprocess, "run", side_effect=fake)

    def test_standalone_directory_preserves_historical_acceptance_without_git_probes(self):
        (self.root / ".git").mkdir()
        with patch.object(phase.subprocess, "run", side_effect=AssertionError("unexpected probe")):
            self.assertEqual(phase.require_supported_checkout(self.root), "STANDALONE")
        data.require_standalone_checkout(self.root)

    def test_valid_linked_worktree_identity_accepts_exact_three_safe_git_probes(self):
        self.linked()
        with self.probes() as probes:
            self.assertEqual(phase.require_supported_checkout(self.root), "LINKED_WORKTREE")
        self.assertEqual([call.args[0][-1] for call in probes.call_args_list],
                         ["--show-toplevel", "--git-dir", "--git-common-dir"])

    def test_dotgit_symlink_is_denied_before_git_probe(self):
        target = self.temporary / "synthetic-git"
        target.mkdir()
        (self.root / ".git").symlink_to(target, target_is_directory=True)
        with patch.object(phase.subprocess, "run") as probes:
            with self.assertRaises((ValueError, OSError)):
                phase.require_supported_checkout(self.root)
        probes.assert_not_called()

    def test_malformed_gitfile_and_oversized_file_are_denied(self):
        for value in ("", "not gitdir\n", "gitdir:\n", "gitdir: x\nsecond line\n", "x" * 4097):
            (self.root / ".git").write_text(value, encoding="utf-8")
            with self.subTest(value=value[:30]), patch.object(phase.subprocess, "run") as probes:
                with self.assertRaises((ValueError, OSError)):
                    phase.require_supported_checkout(self.root)
                probes.assert_not_called()

    def test_nonexistent_gitdir_is_denied(self):
        (self.root / ".git").write_text("gitdir: " + str(self.temporary / "absent") + "\n")
        with patch.object(phase.subprocess, "run") as probes:
            with self.assertRaises((ValueError, OSError)):
                phase.require_supported_checkout(self.root)
        probes.assert_not_called()

    def test_divergent_toplevel_is_denied(self):
        self.linked()
        self.outputs["--show-toplevel"] = str(self.common)
        with self.probes(), self.assertRaises(ValueError):
            phase.require_supported_checkout(self.root)

    def test_reported_gitdir_must_equal_the_gitfile(self):
        self.linked()
        other = self.common / "worktrees" / "other"
        other.mkdir()
        self.outputs["--git-dir"] = str(other)
        with self.probes(), self.assertRaises(ValueError):
            phase.require_supported_checkout(self.root)

    def test_incompatible_common_directory_is_denied(self):
        self.linked()
        other = self.temporary / "other-common"
        other.mkdir()
        self.outputs["--git-common-dir"] = str(other)
        with self.probes(), self.assertRaises(ValueError):
            phase.require_supported_checkout(self.root)

    def test_arbitrary_gitdir_layout_is_denied_even_when_probes_agree(self):
        self.linked()
        arbitrary = self.common / "arbitrary" / "not-a-worktree"
        arbitrary.mkdir(parents=True)
        (self.root / ".git").write_text("gitdir: " + str(arbitrary) + "\n")
        self.outputs["--git-dir"] = str(arbitrary)
        with self.probes(), self.assertRaises(ValueError):
            phase.require_supported_checkout(self.root)

    def test_gitdir_symlink_indirection_is_denied(self):
        self.linked()
        alias = self.temporary / "indirection"
        alias.symlink_to(self.gitdir, target_is_directory=True)
        (self.root / ".git").write_text("gitdir: " + str(alias) + "\n")
        with self.probes(), self.assertRaises((ValueError, OSError)):
            phase.require_supported_checkout(self.root)

    def test_legacy_standalone_checker_still_rejects_linked_gitfile(self):
        self.linked()
        with self.assertRaises(ValueError):
            data.require_standalone_checkout(self.root)


class ComposedGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path("synthetic-root-never-opened")
        self.inventory = [{"path": "README.md", "git_mode": "100644", "blob_sha": "a" * 40, "stage": "0"},
                          {"path": "scripts/run_study3.py", "git_mode": "100644", "blob_sha": "b" * 40, "stage": "0"}]
        self.checkout = self.enterContext(patch.object(phase, "require_supported_checkout", return_value="LINKED_WORKTREE"))
        self.index = self.enterContext(patch.object(phase, "read_index_inventory", return_value=self.inventory))
        self.scope = self.enterContext(patch.object(phase, "audit", return_value={
            "status": "PASS", "violations": [], "experimental_content_bytes_read": 0}))

    def test_composition_pass_requires_unchanged_policy_on_every_index_entry(self):
        with patch.object(data, "audit_entries", wraps=data.audit_entries) as immutable:
            result = governance.audit(self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["audit"], "study3_governance")
        self.assertEqual(result["checkout_kind"], "LINKED_WORKTREE")
        self.assertEqual(result["data_guard_status"], "PASS")
        self.assertEqual(result["phase_scope_status"], "PASS")
        self.assertEqual(result["experimental_content_bytes_read"], 0)
        immutable.assert_called_once_with([(r["git_mode"], r["path"]) for r in self.inventory])
        self.scope.assert_called_once_with(root=self.root)

    def test_tracked_forbidden_data_blocks_before_phase_text_or_payload_open(self):
        self.inventory.append({"path": "data/derived/synthetic-payload.bin", "git_mode": "100644",
                               "blob_sha": "c" * 40, "stage": "0"})
        with patch("builtins.open", side_effect=AssertionError("payload must not open")), \
                patch("os.open", side_effect=AssertionError("payload must not open")), \
                patch.object(phase, "read_regular", side_effect=AssertionError("text must not open")):
            result = governance.audit(self.root)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["data_guard_status"], "BLOCKED")
        self.assertEqual(result["phase_scope_status"], "NOT_RUN")
        self.assertEqual(result["experimental_content_bytes_read"], 0)
        self.scope.assert_not_called()

    def test_checkout_denial_precedes_index_and_policies(self):
        self.checkout.side_effect = ValueError("synthetic invalid identity")
        result = governance.audit(self.root)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIsNone(result["checkout_kind"])
        self.index.assert_not_called()
        self.scope.assert_not_called()

    def test_phase_block_cannot_be_converted_into_governance_pass(self):
        self.scope.return_value["status"] = "BLOCKED"
        result = governance.audit(self.root)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["data_guard_status"], "PASS")
        self.assertEqual(result["phase_scope_status"], "BLOCKED")

    def test_nonzero_reported_experimental_bytes_fail_closed(self):
        self.scope.return_value["experimental_content_bytes_read"] = 1
        self.assertEqual(governance.audit(self.root)["status"], "BLOCKED")

    def test_main_prints_json_and_exit_status_from_composed_audit_only(self):
        for status, code in (("PASS", 0), ("BLOCKED", 1)):
            report = {"audit": "study3_governance", "status": status}
            with patch.object(governance, "audit", return_value=report), patch("sys.stdout", new_callable=io.StringIO) as output:
                self.assertEqual(governance.main(), code)
            self.assertEqual(json.loads(output.getvalue()), report)


def partition_fixture():
    manifest = {"schema_version": 1, "baseline_sha": phase.BASELINE_SHA,
                "domains": {"LEGACY_TI2": [], "TI3_A0_FROZEN": [], "TI3_ACTIVE": []}}
    baseline = []
    for index, path in enumerate([f"src/synthetic_legacy_{i:03}.py" for i in range(75)] + sorted(phase.A0_PATHS)):
        domain = "TI3_A0_FROZEN" if path in phase.A0_PATHS else "LEGACY_TI2"
        row = {"path": path, "git_mode": "100644", "blob_sha": f"{index:040x}", "classification": domain}
        if domain == "TI3_A0_FROZEN":
            row.update(origin_phase="TI3_A0", mutable=False)
        manifest["domains"][domain].append(row)
        baseline.append({k: row[k] for k in ("path", "git_mode", "blob_sha")})
    inventory = [dict(row, stage="0") for row in baseline]
    return manifest, inventory, baseline


class Study3PartitionTests(unittest.TestCase):
    def setUp(self):
        self.manifest, self.inventory, self.baseline = partition_fixture()

    def append_tracked(self, path):
        row = {"path": path, "git_mode": "100644", "blob_sha": "a" * 40,
               "classification": "TI3_ACTIVE", "state": "TRACKED", "origin_phase": "STUDY3"}
        self.inventory.append({**{k: row[k] for k in ("path", "git_mode", "blob_sha")}, "stage": "0"})
        return row

    def test_unclassified_study3_python_is_blocked(self):
        self.append_tracked("src/snbi_fragmentation/study3_domain.py")
        report = phase.audit_partition(self.manifest, self.inventory, self.baseline)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["unclassified_paths"], ["src/snbi_fragmentation/study3_domain.py"])

    def test_all_nineteen_explicit_tracked_study3_paths_pass_in_three_domains(self):
        for path in sorted(NEW_STUDY3_PYTHON):
            self.manifest["domains"]["TI3_ACTIVE"].append(self.append_tracked(path))
        result = phase.audit_partition(self.manifest, self.inventory, self.baseline)
        self.assertEqual(result["status"], "PASS", result["violations"])
        self.assertEqual(result["active_tracked_count"], 19)
        self.assertEqual(set(self.manifest["domains"]), {"LEGACY_TI2", "TI3_A0_FROZEN", "TI3_ACTIVE"})

    def test_manifest_without_study3_cannot_classify_new_tracked_paths(self):
        for path in sorted(NEW_STUDY3_PYTHON):
            self.append_tracked(path)
        report = phase.audit_partition(self.manifest, self.inventory, self.baseline)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(set(report["unclassified_paths"]), NEW_STUDY3_PYTHON)

    def test_planned_or_fourth_domain_does_not_classify_tracked_study3(self):
        row = self.append_tracked("scripts/run_study3.py")
        row["state"] = "PLANNED"
        self.manifest["domains"]["TI3_ACTIVE"].append(row)
        self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "BLOCKED")
        row["state"] = "TRACKED"
        self.manifest["domains"]["STUDY3_ACTIVE"] = []
        self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "BLOCKED")


class Study4ScopeCompatibilityTests(ScopeCompatibilityAssertions, unittest.TestCase):
    def setUp(self):
        self.manifest, self.inventory, self.baseline = partition_fixture()
        self.old_paths = {row["path"] for row in self.inventory}
        for path in sorted(HISTORICAL_STUDY3_PATHS):
            origin = "STUDY3_EXECUTION_RECOVERY_1" if path in RECOVERY_1_PYTHON else "STUDY3"
            self.append_tracked(path, origin)

    def append_tracked(self, path, origin="STUDY4_SYNTHETIC"):
        row = {"path": path, "git_mode": "100644", "blob_sha": "a" * 40,
               "classification": "TI3_ACTIVE", "state": "TRACKED", "origin_phase": origin}
        self.manifest["domains"]["TI3_ACTIVE"].append(row)
        self.inventory.append({**{key: row[key] for key in ("path", "git_mode", "blob_sha")}, "stage": "0"})
        return row

    def assert_compatible(self, manifest=None):
        return self.assert_study3_and_study4_additions(
            self.manifest if manifest is None else manifest, self.old_paths)

    def test_all_twenty_one_historical_paths_are_required_and_counted_separately(self):
        historical, study4 = self.assert_compatible()
        self.assertEqual(len(historical), 21)
        self.assertEqual(len(set(historical) & NEW_STUDY3_PYTHON), 19)
        self.assertEqual(len(set(historical) & RECOVERY_1_PYTHON), 2)
        self.assertEqual(study4, {})
        self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "PASS")

    def assert_removal_blocked(self, paths):
        for path in sorted(paths):
            manifest = deepcopy(self.manifest)
            manifest["domains"]["TI3_ACTIVE"] = [row for row in manifest["domains"]["TI3_ACTIVE"]
                                                   if row["path"] != path]
            inventory = [row for row in self.inventory if row["path"] != path]
            with self.subTest(path=path):
                # Even removing both declarations and index entries cannot erase history.
                self.assertEqual(phase.audit_partition(manifest, inventory, self.baseline)["status"], "PASS")
                with self.assertRaises(AssertionError):
                    self.assert_compatible(manifest)

    def test_removing_any_historical_study3_path_blocks(self):
        self.assert_removal_blocked(NEW_STUDY3_PYTHON)

    def test_removing_either_recovery_path_blocks(self):
        self.assert_removal_blocked(RECOVERY_1_PYTHON)

    def test_changed_historical_origin_blocks(self):
        for row in self.manifest["domains"]["TI3_ACTIVE"]:
            saved = row["origin_phase"]
            row["origin_phase"] = "STUDY2"
            with self.subTest(path=row["path"]), self.assertRaises(AssertionError):
                self.assert_compatible()
            row["origin_phase"] = saved

    def test_changed_historical_classification_blocks(self):
        for row in self.manifest["domains"]["TI3_ACTIVE"]:
            row["classification"] = "TI3_A0_FROZEN"
            with self.subTest(path=row["path"]):
                with self.assertRaises(AssertionError):
                    self.assert_compatible()
                self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "BLOCKED")
            row["classification"] = "TI3_ACTIVE"

    def test_each_explicit_study4_namespace_coexists_outside_historical_twenty_one(self):
        for path in ("src/snbi_fragmentation/study4_synthetic.py", "tests/test_study4_synthetic.py",
                     "scripts/run_study4_synthetic.py", "scripts/check_study4_synthetic.py"):
            self.append_tracked(path)
        historical, study4 = self.assert_compatible()
        self.assertEqual(len(historical), 21)
        self.assertEqual(len(study4), 4)
        self.assertFalse(set(historical) & set(study4))
        self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "PASS")

    def test_unenumerated_tracked_study4_path_is_blocked(self):
        row = self.append_tracked("src/snbi_fragmentation/study4_synthetic.py")
        self.manifest["domains"]["TI3_ACTIVE"].remove(row)
        report = phase.audit_partition(self.manifest, self.inventory, self.baseline)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["unclassified_paths"], [row["path"]])

    def test_study4_outside_exact_namespaces_is_blocked(self):
        row = self.append_tracked("src/snbi_fragmentation/study4_synthetic.py")
        for path in ("src/snbi_fragmentation/study5_synthetic.py", "scripts/arbitrary.py",
                     "src/other/study4_synthetic.py", "tests/study4_synthetic.py",
                     "scripts/study4_synthetic.py", "src/snbi_fragmentation/study4_sub/file.py",
                     "src/snbi_fragmentation/study4_sub/../escape.py",
                     "src/snbi_fragmentation/study4_*.py", "scripts/run_study4_?.py",
                     "tests/test_study4_[ab].py", "tests/test_study4_sub\\escape.py"):
            row["path"] = path
            with self.subTest(path=path), self.assertRaises(AssertionError):
                self.assert_compatible()

    def test_study4_origin_requires_exact_uppercase_prefix_and_underscore(self):
        row = self.append_tracked("tests/test_study4_synthetic.py")
        for origin in ("STUDY3", "STUDY5_A0", "STUDY4", "STUDY40_A0", "study4_A0",
                       "X_STUDY4_A0", " STUDY4_A0", "", None, True):
            row["origin_phase"] = origin
            with self.subTest(origin=origin), self.assertRaises(AssertionError):
                self.assert_compatible()

    def test_no_historical_study3_or_recovery_path_can_be_relabeled_study4(self):
        for row in self.manifest["domains"]["TI3_ACTIVE"]:
            saved = row["origin_phase"]
            row["origin_phase"] = "STUDY4_SYNTHETIC"
            with self.subTest(path=row["path"]), self.assertRaises(AssertionError):
                self.assert_compatible()
            row["origin_phase"] = saved

    def test_fourth_domain_remains_blocked(self):
        self.manifest["domains"]["STUDY4_ACTIVE"] = []
        with self.assertRaises(AssertionError):
            self.assert_compatible()
        self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "BLOCKED")

    def test_planned_cannot_mask_tracked_historical_or_study4_paths(self):
        self.append_tracked("scripts/check_study4_synthetic.py")
        for row in self.manifest["domains"]["TI3_ACTIVE"]:
            row["state"] = "PLANNED"
            with self.subTest(path=row["path"]):
                with self.assertRaises(AssertionError):
                    self.assert_compatible()
                self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "BLOCKED")
            row["state"] = "TRACKED"

    def test_mode_or_blob_divergence_stays_blocked_for_history_and_extensions(self):
        self.append_tracked("scripts/run_study4_synthetic.py")
        for row in self.manifest["domains"]["TI3_ACTIVE"]:
            for key, bad in (("git_mode", "100755"), ("blob_sha", "b" * 40)):
                saved = row[key]
                row[key] = bad
                with self.subTest(path=row["path"], field=key):
                    self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "BLOCKED")
                row[key] = saved

    def test_legacy_rewrite_cannot_be_an_extension(self):
        row = self.manifest["domains"]["LEGACY_TI2"].pop()
        row.update(classification="TI3_ACTIVE", state="TRACKED", origin_phase="STUDY4_SYNTHETIC")
        self.manifest["domains"]["TI3_ACTIVE"].append(row)
        self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "BLOCKED")

    def test_duplicate_explicit_extension_cannot_disappear_in_partition(self):
        row = self.append_tracked("tests/test_study4_synthetic.py")
        self.manifest["domains"]["TI3_ACTIVE"].append(deepcopy(row))
        with self.assertRaises(AssertionError):
            self.assert_compatible()
        self.assertEqual(phase.audit_partition(self.manifest, self.inventory, self.baseline)["status"], "BLOCKED")


class ExactTorchScopeTests(unittest.TestCase):
    def test_study3_cnn_module_torch_is_admitted(self):
        self.assertEqual(ti3.source_violations("import torch\n", "src/snbi_fragmentation/study3_cnn.py"), [])

    def test_study3_cnn_test_torch_is_admitted(self):
        self.assertEqual(ti3.source_violations("from torch import nn\n", "tests/test_study3_cnn.py"), [])

    def test_study3_models_torch_remains_blocked(self):
        self.assertTrue(ti3.source_violations("import torch\n", "src/snbi_fragmentation/study3_models.py"))

    def test_study3_runner_torch_remains_blocked(self):
        self.assertTrue(ti3.source_violations("import torch\n", "scripts/run_study3.py"))

    def test_four_historical_torch_paths_remain_accepted(self):
        for path in HISTORICAL_TORCH_PATHS:
            with self.subTest(path=path):
                self.assertEqual(ti3.source_violations("import torch\n", path), [])

    def test_exact_six_paths_and_seventh_path_is_denied(self):
        self.assertEqual(ti3.TORCH_PATHS, HISTORICAL_TORCH_PATHS | STUDY3_TORCH_PATHS)
        self.assertEqual(len(ti3.TORCH_PATHS), 6)
        self.assertTrue(ti3.source_violations("import torch\n", "src/snbi_fragmentation/study3_seventh.py"))

    def test_other_forbidden_frameworks_stay_blocked_even_in_cnn_paths(self):
        for name in ("torchvision", "torchaudio", "tensorflow", "keras", "transformers", "xgboost",
                     "lightgbm", "catboost", "fastai"):
            for path in STUDY3_TORCH_PATHS:
                with self.subTest(name=name, path=path):
                    self.assertTrue(ti3.source_violations("import " + name + "\n", path))


class HistoricalRepairCustodyTests(ScopeCompatibilityAssertions, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def base_text(path):
            return subprocess.run(["git", "--no-optional-locks", "show", BASE + ":" + path],
                cwd=ROOT, env=data.SAFE_GIT_ENV, check=True, capture_output=True, timeout=15).stdout
        cls.old_manifest = json.loads(base_text(phase.MANIFEST_PATH))
        cls.new_manifest = json.loads(phase.read_regular(ROOT, phase.MANIFEST_PATH)[0])
        cls.old_ti3_source = base_text("scripts/check_ti3_scope.py").decode("utf-8")

    def test_historical_manifest_rows_preserve_every_field_except_two_authorized_blob_hashes(self):
        self.assertEqual(self.old_manifest["baseline_sha"], "41d523e038e844588ee7724e07b00f75bdf29fdc")
        self.assertEqual(self.new_manifest["baseline_sha"], self.old_manifest["baseline_sha"])
        self.assertEqual(set(self.new_manifest["domains"]), set(self.old_manifest["domains"]))
        new_rows = {row["path"]: row for rows in self.new_manifest["domains"].values() for row in rows}
        for domain, rows in self.old_manifest["domains"].items():
            for old in rows:
                current = deepcopy(new_rows[old["path"]])
                if old["path"] in MODIFIED_GUARDS:
                    current["blob_sha"] = old["blob_sha"]
                with self.subTest(path=old["path"], domain=domain):
                    self.assertEqual(current, old)

    def test_manifest_preserves_twenty_one_historical_paths_and_separate_study4_extensions(self):
        old_paths = {row["path"] for rows in self.old_manifest["domains"].values() for row in rows}
        historical, study4 = self.assert_study3_and_study4_additions(self.new_manifest, old_paths)
        for row in [*historical.values(), *study4.values()]:
            with self.subTest(path=row["path"]):
                content, mode = phase.read_regular(ROOT, row["path"])
                self.assertEqual(row["git_mode"], mode)
                self.assertEqual(row["blob_sha"], phase.git_blob_sha(content))

    def test_immutable_data_guard_blob_and_torch_scope_only_change_are_preserved(self):
        content, _ = phase.read_regular(ROOT, "scripts/check_repository_data.py")
        self.assertEqual(phase.git_blob_sha(content), "9e39878e5bf18df0e05d6388c26745b7c11a4414")
        current, _ = phase.read_regular(ROOT, "scripts/check_ti3_scope.py")
        def without_torch_paths(source):
            tree = ast.parse(source)
            tree.body = [node for node in tree.body if not (isinstance(node, ast.Assign)
                         and any(isinstance(target, ast.Name) and target.id == "TORCH_PATHS"
                                 for target in node.targets))]
            return ast.dump(tree, include_attributes=False)
        self.assertEqual(without_torch_paths(current.decode("utf-8")), without_torch_paths(self.old_ti3_source))
        self.assertEqual(len(ti3.CNN_CONSTRAINTS), 22)

    def test_recovery_manifest_preserves_frozen_rows_except_two_authorized_blobs(self):
        frozen = json.loads(subprocess.run(
            ["git", "--no-optional-locks", "show",
             "a3f45b645e9fb3e813a43220351c951698293963:" + phase.MANIFEST_PATH],
            cwd=ROOT, env=data.SAFE_GIT_ENV, check=True, capture_output=True, timeout=15).stdout)
        current = deepcopy(self.new_manifest)
        mutable_blobs = {"src/snbi_fragmentation/study3_execution.py",
                         "tests/test_study3_governance.py"}
        old_paths = {row["path"] for rows in self.old_manifest["domains"].values() for row in rows}
        _, study4 = self.assert_study3_and_study4_additions(current, old_paths)
        excluded_additions = RECOVERY_1_PYTHON | set(study4)
        current["domains"]["TI3_ACTIVE"] = [row for row in current["domains"]["TI3_ACTIVE"]
                                               if row["path"] not in excluded_additions]
        frozen_rows = {row["path"]: row for rows in frozen["domains"].values() for row in rows}
        for rows in current["domains"].values():
            for row in rows:
                if row["path"] in mutable_blobs:
                    row["blob_sha"] = frozen_rows[row["path"]]["blob_sha"]
        self.assertEqual(current, frozen)


class ExactFreezeInventoryTests(unittest.TestCase):
    def setUp(self):
        self.changes = (["A\t" + path for path in execution.METHOD_FILES]
                        + ["M\t" + path for path in execution.MODIFIED_GOVERNANCE_FILES])

    def test_exact_thirty_six_additions_three_modifications_are_admitted(self):
        self.assertEqual(len(execution.METHOD_FILES), 36)
        self.assertEqual(set(execution.MODIFIED_GOVERNANCE_FILES), MODIFIED_GUARDS | {phase.MANIFEST_PATH})
        self.assertEqual(len(set(execution.FREEZE_FILES)), 39)
        execution.validate_freeze_inventory(self.changes)

    def test_fortieth_missing_duplicate_or_wrong_status_is_denied(self):
        variants = [self.changes + ["A\tscripts/unauthorized.py"], self.changes[:-1],
                    self.changes[:-1] + [self.changes[0]],
                    ["M\t" + execution.METHOD_FILES[0], *self.changes[1:]]]
        for changed in variants:
            with self.subTest(size=len(changed)), self.assertRaises(execution.Study3ExecutionError):
                execution.validate_freeze_inventory(changed)


if __name__ == "__main__":
    unittest.main()
