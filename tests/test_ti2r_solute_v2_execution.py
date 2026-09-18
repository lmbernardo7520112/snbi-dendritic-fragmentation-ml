"""V2-D orchestration contracts using only mocked in-memory buffers."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from scripts import run_ti2r_solute_v2 as runner


class SoluteV2ExecutionTests(unittest.TestCase):
    def test_real_preregistered_text_metadata_matches_authority_contract(self):
        root = Path(__file__).absolute().parents[1]
        # Only governed textual metadata, never any path contained in it.
        exposure = json.loads((root / runner.EXPOSURE).read_text())
        projected = [{k: a[k] for k in runner.ASSET_FIELDS} for a in exposure["assets"]]
        validated = runner.authority._validate_assets(projected)
        self.assertEqual(set(validated), set(runner.authority.ASSET_ROLES))
        self.assertEqual(len(validated), 12)
        self.assertEqual(set(exposure["holdout_custody"]), set(runner.HOLDOUT_IDS))
        for record in exposure["holdout_custody"].values():
            self.assertIs(record["authorized_this_phase"], False)
        self.assertTrue(callable(runner.authority.require_preregistered))

    def test_actual_science_pass_constant_integrates_with_orchestrator(self):
        from snbi_fragmentation import ti2r_solute_v2_calibration as science
        report, _, _ = self.fake([{"status": science.PASS}, {"status": science.PASS}])
        self.assertEqual(report["TI2R_SOLUTE_V2_DEV"], runner.PASS)

    def fake(self, results):
        exposure = {"assets": [{"asset_id": f"{source}:{index}", "width": 8, "height": 8}
                    for _, ref, mov, indices in runner.PAIRS for index in indices for source in (ref, mov)]}
        preparation, science, session = Mock(), Mock(), Mock()
        preparation.prepare.side_effect = lambda raw, w, h, config: (raw, w, h)
        science.evaluate_development.side_effect = results
        opened = []
        def read(session, identifier, *, role):
            self.assertEqual(role, "development")
            opened.append(identifier)
            return b"synthetic"
        report = {"pairs": {}}
        with patch.object(runner.authority, "read_asset", side_effect=read), redirect_stdout(io.StringIO()):
            runner.execute(session, exposure, {}, {}, preparation, science, report)
        return report, opened, science

    def test_exact_twelve_development_reads_and_no_holdout_on_pass(self):
        report, opened, science = self.fake([{"status": "PASS"}, {"status": "PASS"}])
        self.assertEqual(len(opened), 12)
        self.assertEqual(len(set(opened)), 12)
        self.assertFalse(set(opened) & set(runner.HOLDOUT_IDS))
        self.assertEqual(report["TI2R_SOLUTE_V2_DEV"], runner.PASS)
        self.assertEqual(report["G2_SOLUTE"], "BLOCKED_PENDING_LOCKED_HOLDOUT")
        self.assertFalse(report["TI2R_SOLUTE_HOLDOUT_AUTHORIZED"])
        science.evaluate_holdout.assert_not_called()

    def test_first_pair_failure_does_not_skip_second_pair_or_enable_retry(self):
        report, opened, science = self.fake([{"status": "FAIL"}, {"status": "PASS"}])
        self.assertEqual(len(opened), 12)
        self.assertEqual(science.evaluate_development.call_count, 2)
        self.assertEqual(report["TI2R_SOLUTE_V2_DEV"], runner.FAIL)
        self.assertEqual(report["G2_SOLUTE"], "BLOCKED_FINAL_WITH_AVAILABLE_DATA")
        self.assertEqual(report["HOLDOUT_SOLUTE"], "SEALED_NOT_NEEDED")
        self.assertTrue(report["NO_AUTOMATIC_V3"])

    def test_unknown_scientific_state_fails_closed(self):
        report, _, _ = self.fake([{"status": "UNKNOWN"}, {"status": "PASS"}])
        self.assertEqual(report["TI2R_SOLUTE_V2_DEV"], runner.FAIL)

    def test_all_terminals_preserve_fragment_and_closed_permissions(self):
        for state in (runner.PASS, runner.FAIL, runner.OPERATIONAL):
            with self.subTest(state=state):
                value = runner.terminal_fields(state)
                self.assertEqual(value["G2_FRAG"], "PASS_DIRECT_RASTER_MAPPING")
                self.assertEqual(value["CURRENT_AUTHORIZED_ACTIVITY"], "NONE_AWAITING_AUTHOR_DECISION")
                self.assertFalse(value["TI2R_SOLUTE_HOLDOUT_AUTHORIZED"])
                self.assertFalse(value["TI3_PLUS_AUTHORIZED"])
                self.assertFalse(value["MERGE_AUTHORIZED"])

    def test_frozen_input_authority_guard_precedes_git_or_text(self):
        with patch.object(runner.authority, "require_preregistered", side_effect=RuntimeError("denied")), \
             patch.object(runner, "git") as git, patch.object(runner.authority, "read_text_file") as read:
            with self.assertRaises(RuntimeError):
                runner.frozen_inputs(object())
        git.assert_not_called()
        read.assert_not_called()

    def test_dirty_c1_denies_before_scientific_text_or_runtime(self):
        with patch.object(runner.authority, "require_preregistered"), \
             patch.object(runner, "git", return_value=" M changed"), \
             patch.object(runner.authority, "read_text_file") as read, \
             patch.object(runner.importlib, "import_module") as runtime:
            with self.assertRaisesRegex(ValueError, "dirty C1"):
                runner.frozen_inputs(object())
        read.assert_not_called()
        runtime.assert_not_called()

    def test_nonpublished_c1_denies_before_pixels(self):
        with patch.object(runner.authority, "require_preregistered"), \
             patch.object(runner, "git", side_effect=["", "a" * 40, runner.BASE_SHA, "b" * 40]), \
             patch.object(runner.authority, "read_text_file") as read:
            with self.assertRaisesRegex(ValueError, "not published"):
                runner.frozen_inputs(object())
        read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
