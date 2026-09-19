"""Adversarial scope fixtures are text in memory; no experimental I/O."""

from __future__ import annotations

import copy
import json
import unittest
from unittest.mock import patch

from scripts import check_phase_scope as scope


class PhaseScopeTests(unittest.TestCase):
    def setUp(self):
        self.content = {}
        self.baseline = []
        self.manifest = {
            "schema_version": 1, "baseline_sha": scope.BASELINE_SHA,
            "domains": {"LEGACY_TI2": [], "TI3_A0_FROZEN": [], "TI3_ACTIVE": []},
        }
        for index in range(75):
            path = f"src/legacy_module_{index:03d}.py"
            row = self.row(path, f"# synthetic legacy {index}\n".encode(), "LEGACY_TI2")
            self.manifest["domains"]["LEGACY_TI2"].append(row)
            self.baseline.append(self.git_record(row))
        for path in sorted(scope.A0_PATHS):
            row = self.row(path, f"# synthetic frozen {path}\n".encode(), "TI3_A0_FROZEN")
            row.update(origin_phase="TI3_A0", mutable=False)
            self.manifest["domains"]["TI3_A0_FROZEN"].append(row)
            self.baseline.append(self.git_record(row))
        self.active_path = "src/snbi_fragmentation/ti3_baseline.py"
        active = self.row(self.active_path, b"import sklearn\n", "TI3_ACTIVE")
        active["state"] = "TRACKED"
        self.manifest["domains"]["TI3_ACTIVE"].append(active)
        self.inventory = [dict(row, stage="0") for row in self.baseline]
        self.inventory.append(dict(self.git_record(active), stage="0"))
        self.reader = self.enterContext(patch.object(scope, "read_regular", side_effect=self.read))
        self.enterContext(patch.object(scope, "read_index_inventory", side_effect=lambda root: self.inventory))
        self.baseline_reader = self.enterContext(patch.object(
            scope, "read_baseline_inventory", side_effect=lambda root: self.baseline,
        ))
        self.legacy = self.enterContext(patch.object(scope.check_ti2_scope, "audit", return_value={
            "status": "PASS", "violations": [],
        }))
        self.active = self.enterContext(patch.object(scope.check_ti3_scope, "audit", return_value={
            "status": "PASS", "violations": [],
        }))

    def row(self, path, content, domain):
        self.content[path] = (content, "100644")
        return {"path": path, "git_mode": "100644", "blob_sha": scope.git_blob_sha(content),
                "classification": domain}

    @staticmethod
    def git_record(row):
        return {key: row[key] for key in ("path", "git_mode", "blob_sha")}

    def read(self, root, path):
        if path == scope.MANIFEST_PATH:
            return json.dumps(self.manifest).encode(), "100644"
        if path not in self.content:
            raise FileNotFoundError(path)
        return self.content[path]

    def audit(self):
        return scope.audit()

    def assert_blocked(self, report):
        self.assertEqual(report["status"], "BLOCKED", json.dumps(report))
        self.assertTrue(report["violations"])
        self.assertEqual(report["experimental_content_bytes_read"], 0)

    def test_exact_partition_passes_and_dispatches_disjoint_domains(self):
        report = self.audit()
        self.assertEqual(report["status"], "PASS", json.dumps(report))
        self.assertEqual(report["partition"]["legacy_file_count"], 75)
        self.assertEqual(report["partition"]["a0_frozen_file_count"], 4)
        self.assertEqual(report["partition"]["unclassified_paths"], [])
        self.assertEqual(report["partition"]["duplicate_classification_paths"], [])
        legacy_entries = self.legacy.call_args.kwargs["entries"]
        self.assertEqual(len(legacy_entries), 75)
        self.assertTrue(all(path not in scope.A0_PATHS for _, path in legacy_entries))
        self.assertEqual(self.active.call_args.kwargs["entries"], [("100644", self.active_path)])
        self.assertEqual(report["authorized_scientific_phases"], [])
        self.assertFalse(report["ti3_plus_authorized"])
        self.assertFalse(report["merge_authorized"])
        self.assertEqual(report["scientific_readiness"], "BLOCKED")

    def test_a_one_byte_a0_change_blocks_before_active_audit(self):
        path = sorted(scope.A0_PATHS)[0]
        original, mode = self.content[path]
        self.content[path] = (original + b"#", mode)
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["a0_frozen_scope"]["status"], "BLOCKED")
        self.active.assert_not_called()

    def test_b_renamed_a0_blocks(self):
        path = sorted(scope.A0_PATHS)[0]
        new_path = "scripts/renamed_a0.py"
        self.inventory = [dict(row, path=new_path) if row["path"] == path else row for row in self.inventory]
        self.content[new_path] = self.content.pop(path)
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["a0_frozen_scope"]["status"], "BLOCKED")
        self.legacy.assert_not_called()

    def test_c_fifth_a0_declaration_blocks(self):
        row = self.row("scripts/fifth_a0.py", b"# fifth\n", "TI3_A0_FROZEN")
        row.update(origin_phase="TI3_A0", mutable=False)
        self.manifest["domains"]["TI3_A0_FROZEN"].append(row)
        self.inventory.append(dict(self.git_record(row), stage="0"))
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["a0_frozen_scope"]["status"], "BLOCKED")

    def test_d_a0_also_in_legacy_blocks(self):
        row = copy.deepcopy(self.manifest["domains"]["TI3_A0_FROZEN"][0])
        row["classification"] = "LEGACY_TI2"
        self.manifest["domains"]["LEGACY_TI2"].append(row)
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["partition"]["duplicate_classification_paths"], [row["path"]])
        self.assertEqual(report["a0_frozen_scope"]["status"], "BLOCKED")

    def test_e_unclassified_path_blocks(self):
        row = self.row("src/unclassified.py", b"# ordinary code\n", "TI3_ACTIVE")
        self.inventory.append(dict(self.git_record(row), stage="0"))
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["partition"]["unclassified_paths"], [row["path"]])

    def test_f_active_also_in_legacy_blocks(self):
        row = copy.deepcopy(self.manifest["domains"]["TI3_ACTIVE"][0])
        row["classification"] = "LEGACY_TI2"
        self.manifest["domains"]["LEGACY_TI2"].append(row)
        self.assert_blocked(self.audit())

    def test_j_unknown_annotations_is_not_silently_classified(self):
        row = self.row("scripts/new_annotations.py", b"# no imports\n", "TI3_ACTIVE")
        self.inventory.append(dict(self.git_record(row), stage="0"))
        self.assert_blocked(self.audit())
        self.legacy.assert_not_called()

    def test_k_data_guard_blocks_before_manifest_or_any_source_read(self):
        self.inventory.append({"path": "data/derived/example.raw", "git_mode": "100644",
                               "blob_sha": "0" * 40, "stage": "0"})
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["data_guard"]["status"], "BLOCKED")
        self.reader.assert_not_called()
        self.baseline_reader.assert_not_called()

    def test_l_tracked_symlink_blocks_without_open(self):
        self.inventory[0]["git_mode"] = "120000"
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["data_guard"]["status"], "BLOCKED")
        self.reader.assert_not_called()

    def test_worktree_symlink_refusal_propagates_as_custody_block(self):
        original = self.read
        path = sorted(scope.A0_PATHS)[0]
        self.reader.side_effect = lambda root, relative: (
            (_ for _ in ()).throw(OSError("synthetic O_NOFOLLOW refusal"))
            if relative == path else original(root, relative)
        )
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["a0_frozen_scope"]["status"], "BLOCKED")

    def test_a0_worktree_manifest_and_index_coedit_cannot_replace_git_anchor(self):
        row = self.manifest["domains"]["TI3_A0_FROZEN"][0]
        replacement = b"# altered A0 all mutable copies\n"
        self.content[row["path"]] = (replacement, "100644")
        row["blob_sha"] = scope.git_blob_sha(replacement)
        for item in self.inventory:
            if item["path"] == row["path"]:
                item["blob_sha"] = row["blob_sha"]
        report = self.audit()
        self.assert_blocked(report)
        self.assertTrue(any("immutable Git baseline" in violation for violation in report["violations"]))

    def test_legacy_worktree_manifest_and_index_coedit_cannot_replace_git_anchor(self):
        row = self.manifest["domains"]["LEGACY_TI2"][0]
        replacement = b"import sklearn\n"
        self.content[row["path"]] = (replacement, "100644")
        row["blob_sha"] = scope.git_blob_sha(replacement)
        for item in self.inventory:
            if item["path"] == row["path"]:
                item["blob_sha"] = row["blob_sha"]
        self.assert_blocked(self.audit())
        self.legacy.assert_not_called()

    def test_legacy_worktree_byte_change_blocks_before_legacy_checker(self):
        path = self.manifest["domains"]["LEGACY_TI2"][0]["path"]
        self.content[path] = (b"# changed\n", "100644")
        self.assert_blocked(self.audit())
        self.legacy.assert_not_called()

    def test_missing_legacy_path_blocks_partition(self):
        path = self.manifest["domains"]["LEGACY_TI2"][0]["path"]
        self.inventory = [row for row in self.inventory if row["path"] != path]
        self.assert_blocked(self.audit())

    def test_missing_a0_path_blocks_partition(self):
        path = sorted(scope.A0_PATHS)[0]
        self.inventory = [row for row in self.inventory if row["path"] != path]
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["a0_frozen_scope"]["status"], "BLOCKED")

    def test_planned_absent_from_index_is_not_read_or_dispatched(self):
        self.manifest["domains"]["TI3_ACTIVE"][0]["state"] = "PLANNED"
        self.inventory = [row for row in self.inventory if row["path"] != self.active_path]
        self.content[self.active_path] = (b"# ignored local draft\n", "100644")
        report = self.audit()
        self.assertEqual(report["status"], "PASS", json.dumps(report))
        self.assertEqual(self.active.call_args.kwargs["entries"], [])
        self.assertNotIn(self.active_path, [call.args[1] for call in self.reader.call_args_list])

    def test_planned_but_tracked_is_inconsistent(self):
        self.manifest["domains"]["TI3_ACTIVE"][0]["state"] = "PLANNED"
        self.assert_blocked(self.audit())

    def test_tracked_but_absent_active_is_inconsistent(self):
        self.inventory = [row for row in self.inventory if row["path"] != self.active_path]
        self.assert_blocked(self.audit())

    def test_duplicate_index_or_unmerged_stage_is_blocking(self):
        self.inventory[0]["stage"] = "2"
        self.assert_blocked(self.audit())
        self.reader.assert_not_called()

    def test_changed_baseline_id_is_rejected(self):
        self.manifest["baseline_sha"] = "0" * 40
        self.assert_blocked(self.audit())

    def test_fourth_domain_is_rejected(self):
        self.manifest["domains"]["EXEMPT"] = []
        self.assert_blocked(self.audit())

    def test_mode_change_blocks(self):
        path = sorted(scope.A0_PATHS)[0]
        content, _ = self.content[path]
        self.content[path] = (content, "100755")
        self.assert_blocked(self.audit())

    def test_case_variant_python_is_relevant_and_unclassified(self):
        self.inventory.append({"path": "scripts/unclassified.PY", "git_mode": "100644",
                               "blob_sha": "0" * 40, "stage": "0"})
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["partition"]["unclassified_paths"], ["scripts/unclassified.PY"])

    def test_legacy_checker_failure_propagates_without_active_dispatch(self):
        self.legacy.return_value = {"status": "BLOCKED", "violations": ["synthetic legacy violation"]}
        report = self.audit()
        self.assert_blocked(report)
        self.assertEqual(report["legacy_scope"]["status"], "BLOCKED")
        self.active.assert_not_called()

    def test_active_checker_failure_propagates(self):
        self.active.return_value = {"status": "BLOCKED", "violations": ["synthetic prohibited import"]}
        self.assert_blocked(self.audit())


if __name__ == "__main__":
    unittest.main()
