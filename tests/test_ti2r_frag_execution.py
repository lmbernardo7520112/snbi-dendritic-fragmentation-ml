"""Orchestration contracts: synthetic metadata/mocks only, never pilot IO."""

from contextlib import redirect_stdout
import io
import unittest
from unittest.mock import Mock, patch

from scripts import run_ti2r_frag as runner


def fixture():
    assets, seals = [], {}
    for _, reference, moving, development, validation in runner.PAIRS:
        for source in (reference, moving):
            for index in (*development, *validation):
                identifier = f"{source}:{index}"
                assets.append({"asset_id": identifier, "width": 8, "height": 8})
                seals[identifier] = {"validation_sealed": index in validation}
    return {"assets": assets, "validation_seals": seals}


def passing():
    return {"status": "PASS", "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "selected_model": "M0", "development": {"status": "PASS"}}


class FragExecutionTests(unittest.TestCase):
    def test_published_governance_is_inactive_or_consumed(self):
        current = runner.authority.load_authority(runner.ROOT)
        self.assertIn(current["state"], {"PREPARED_INACTIVE", "CLOSED_CONSUMED"})
        self.assertIs(current["ti2r_execution_authorized"], False)

    def run_fake(self, exposure=None, fits=None, validations=None):
        session = Mock()
        events = []
        session.freeze_candidate.side_effect = lambda pair, result: events.append(("freeze", pair))
        science = Mock()
        science.prepare.side_effect = lambda raw, w, h, c: (raw, w, h)
        science.fit_pair.side_effect = fits or [passing(), passing()]
        science.validate_pair.side_effect = validations or [{"status": "PASS"}, {"status": "PASS"}]
        def read(session, identifier, *, role):
            events.append((role, identifier))
            return b"synthetic only"
        with patch.object(runner.authority, "read_asset", side_effect=read), redirect_stdout(io.StringIO()):
            result = runner.execute(session, exposure or fixture(), {}, science)
        return result, events, science

    def test_exact_twenty_assets_and_all_candidates_freeze_before_validation(self):
        result, events, science = self.run_fake()
        self.assertEqual(result["TI2R_FRAG"], "PASS")
        reads = [e for e in events if e[0] in {"development", "validation"}]
        self.assertEqual(len(reads), 20)
        self.assertEqual(len(set(reads)), 20)
        self.assertEqual(sum(e[0] == "development" for e in reads), 12)
        self.assertFalse(any("ESM2" in e[1] or "ESM5" in e[1] for e in reads))
        first_validation = next(i for i, e in enumerate(events) if e[0] == "validation")
        self.assertEqual(sum(e[0] == "freeze" for e in events[:first_validation]), 2)
        self.assertEqual(science.fit_pair.call_count, 2)
        self.assertEqual(science.validate_pair.call_count, 2)

    def test_validation_without_positive_custody_is_never_read(self):
        exposure = fixture()
        for seal in exposure["validation_seals"].values():
            seal["validation_sealed"] = False
        result, events, science = self.run_fake(exposure)
        self.assertEqual(result["TI2R_FRAG"], "PARTIAL_DEVELOPMENT_ONLY")
        self.assertFalse(any(e[0] == "validation" for e in events))
        science.validate_pair.assert_not_called()

    def test_failed_development_never_opens_quartiles(self):
        result, events, science = self.run_fake(fits=[
            {"status": "BLOCKED_REFERENCE_INSUFFICIENT"},
            {"status": "BLOCKED_METHOD_HIERARCHY"},
        ])
        self.assertEqual(result["TI2R_FRAG"], "BLOCKED_REFERENCE_INSUFFICIENT")
        self.assertFalse(any(e[0] in {"freeze", "validation"} for e in events))
        science.validate_pair.assert_not_called()

    def test_one_condition_pass_does_not_refit_failed_validation(self):
        result, events, science = self.run_fake(validations=[{"status": "PASS"}, {"status": "BLOCKED_VALIDATION"}])
        self.assertEqual(result["TI2R_FRAG"], "PARTIAL_ONE_CONDITION")
        self.assertEqual(science.fit_pair.call_count, 2)
        self.assertEqual(science.validate_pair.call_count, 2)

    def test_validation_reference_insufficiency_preserves_specific_block(self):
        result, _, _ = self.run_fake(validations=[
            {"status": "BLOCKED_REFERENCE_INSUFFICIENT"}, {"status": "BLOCKED_VALIDATION"}])
        self.assertEqual(result["TI2R_FRAG"], "BLOCKED_REFERENCE_INSUFFICIENT")

    def test_unsealed_candidate_with_other_condition_without_candidate_is_development_only(self):
        exposure = fixture()
        for key, seal in exposure["validation_seals"].items():
            if key.startswith(("ESM1:", "ESM3:")):
                seal["validation_sealed"] = False
        result, events, _ = self.run_fake(exposure, fits=[passing(), {"status": "BLOCKED_METHOD_HIERARCHY"}])
        self.assertEqual(result["TI2R_FRAG"], "PARTIAL_DEVELOPMENT_ONLY")
        self.assertFalse(any(e[0] == "validation" for e in events))

    def test_pilot_io_failure_interrupts_without_retry(self):
        with patch.object(runner.authority, "read_asset", side_effect=OSError("synthetic unavailable")) as read, redirect_stdout(io.StringIO()):
            with self.assertRaises(OSError):
                runner.execute(Mock(), fixture(), {}, Mock())
        read.assert_called_once()

    def test_frozen_preflight_checks_authority_before_git_or_text(self):
        with patch.object(runner.authority, "require_active", side_effect=RuntimeError("closed")), \
                patch.object(runner, "git") as git, \
                patch.object(runner.authority, "read_text_file") as read:
            with self.assertRaises(RuntimeError):
                runner.frozen_inputs(object())
        git.assert_not_called()
        read.assert_not_called()

    def test_frozen_manifest_registry_integrate_without_asset_io(self):
        # Real tracked/new governance text only; C2 identity is simulated.
        texts = {name: runner.authority.read_text_file(runner.ROOT, name)
                 for name in runner.FROZEN_FILES}
        responses = {
            ("status", "--porcelain"): "",
            ("rev-parse", "HEAD"): "2" * 40,
            ("rev-parse", "HEAD^"): "1" * 40,
            ("rev-parse", "HEAD^^"): runner.BASE_SHA,
            ("log", "-1", "--format=%s"): "chore(authority): activate one-shot TI2R-FRAG execution",
            ("diff", "--name-only", "1" * 40, "2" * 40): runner.AUTHORITY + "\n" + runner.DECISION,
        }
        with patch.object(runner.authority, "require_active"), \
                patch.object(runner, "git", side_effect=lambda root, *args: responses[args]), \
                patch.object(runner.subprocess, "check_output", side_effect=lambda args, **kw: texts[args[-1].split(":", 1)[1]].encode()), \
                patch.object(runner.authority, "read_asset") as experimental:
            c2, hashes, exposure, config = runner.frozen_inputs(runner.ROOT)
        self.assertEqual(c2, "2" * 40)
        self.assertEqual(len(exposure["assets"]), 20)
        self.assertEqual(set(hashes), set(runner.FROZEN_FILES))
        self.assertEqual(config["direction"], "moving_to_reference")
        experimental.assert_not_called()


if __name__ == "__main__":
    unittest.main()
