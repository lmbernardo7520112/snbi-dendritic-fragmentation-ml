"""Synthetic orchestration: no pilot files, no scientific CLI invocation."""

from contextlib import redirect_stdout
import io
import unittest
from unittest.mock import Mock, patch

from scripts import run_ti2r_solute_direct as runner


def fixture():
    assets, seals = [], {}
    for _, ref, mov, development, holdout in runner.PAIRS:
        for source in (ref, mov):
            for index in (*development, *holdout):
                identifier = f"{source}:{index}"
                assets.append({"asset_id": identifier, "width": 8, "height": 8})
                seals[identifier] = {"holdout_eligible_this_phase": index in holdout}
    return {"assets": assets, "holdout_eligibility": seals}


def passing():
    return {"status": "PASS", "offset": [0, 0], "per_frame": []}


class SoluteExecutionTests(unittest.TestCase):
    def run_fake(self, development=None, holdouts=None, exposure=None):
        science, session, events = Mock(), Mock(), []
        science.prepare.side_effect = lambda raw, w, h, config: (raw, w, h)
        science.evaluate_development.side_effect = development or [passing(), passing()]
        science.evaluate_holdout.side_effect = holdouts or [{"status": "PASS"}, {"status": "PASS"}]
        session.freeze_identity.side_effect = lambda pair, record: events.append(("freeze", pair))
        def read(session, identifier, *, role):
            events.append((role, identifier))
            return b"synthetic"
        report = {"pairs": {}}
        with patch.object(runner.authority, "read_asset", side_effect=read), redirect_stdout(io.StringIO()):
            runner.execute(session, exposure or fixture(), {}, science, report)
        return report, events, science

    def test_twenty_exact_assets_with_both_freezes_before_holdout(self):
        report, events, science = self.run_fake()
        self.assertEqual(report["TI2R_SOLUTE_DIRECT"], "PASS_DIRECT_MULTIMODAL_MAPPING")
        reads = [event for event in events if event[0] in {"development", "holdout"}]
        self.assertEqual(len(reads), 20)
        self.assertEqual(len(set(reads)), 20)
        first = next(i for i, event in enumerate(events) if event[0] == "holdout")
        self.assertEqual(sum(e[0] == "freeze" for e in events[:first]), 2)
        self.assertFalse(any(e[1].startswith(("ESM3:", "ESM6:")) for e in reads))
        self.assertEqual(science.evaluate_development.call_count, 2)

    def test_only_approved_pair_opens_its_four_holdout_assets(self):
        report, events, _ = self.run_fake(development=[passing(), {"status": "BLOCKED_IDENTITY_NOT_DISCRIMINATIVE"}])
        self.assertEqual(report["TI2R_SOLUTE_DIRECT"], "PARTIAL_ONE_PAIR")
        opened = [e[1] for e in events if e[0] == "holdout"]
        self.assertEqual(set(opened), {"ESM1:73", "ESM1:219", "ESM2:73", "ESM2:219"})

    def test_failed_development_never_opens_holdout(self):
        report, events, science = self.run_fake(development=[{"status": "BLOCKED_MODALITY_INFORMATION_INSUFFICIENT"}] * 2)
        self.assertEqual(report["TI2R_SOLUTE_DIRECT"], "BLOCKED_MODALITY_INFORMATION_INSUFFICIENT")
        self.assertFalse(any(e[0] == "holdout" for e in events))
        science.evaluate_holdout.assert_not_called()

    def test_absent_holdout_custody_stops_phase(self):
        exposure = fixture()
        for entry in exposure["holdout_eligibility"].values():
            entry["holdout_eligible_this_phase"] = False
        with self.assertRaisesRegex(ValueError, "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE"):
            self.run_fake(exposure=exposure)

    def test_holdout_contradiction_never_revisits_development(self):
        report, _, science = self.run_fake(holdouts=[{"status": "BLOCKED_INTERNAL_VALIDATION"}] * 2)
        self.assertEqual(report["TI2R_SOLUTE_DIRECT"], "BLOCKED_INTERNAL_VALIDATION")
        self.assertEqual(science.evaluate_development.call_count, 2)
        self.assertEqual(science.evaluate_holdout.call_count, 2)

    def test_dimensions_stop_before_second_pair_or_holdout(self):
        with self.assertRaisesRegex(ValueError, "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE"):
            self.run_fake(development=[{"status": "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE"}])
        self.assertEqual(runner.aggregate({"one": {"holdout": {"status": "PASS"}},
            "two": {"status": "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE"}})[0], "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE")

    def test_frozen_inputs_guard_before_git_or_text(self):
        with patch.object(runner.authority, "require_active", side_effect=RuntimeError("closed")), \
                patch.object(runner, "git") as git, patch.object(runner.authority, "read_text_file") as text:
            with self.assertRaises(RuntimeError):
                runner.frozen_inputs(object())
        git.assert_not_called()
        text.assert_not_called()

    def test_repository_authority_inactive_or_consumed(self):
        current = runner.authority.load_authority(runner.ROOT)
        self.assertIn(current["state"], {"PREPARED_INACTIVE", "CLOSED_CONSUMED"})
        self.assertIs(current["ti2r_execution_authorized"], False)

    def test_frozen_metadata_integrate_without_experimental_io(self):
        texts = {name: runner.authority.read_text_file(runner.ROOT, name) for name in runner.FROZEN_FILES}
        answers = {("status", "--porcelain"): "", ("rev-parse", "HEAD"): "2" * 40,
            ("rev-parse", "HEAD^"): "1" * 40, ("rev-parse", "HEAD^^"): runner.BASE_SHA,
            ("log", "-1", "--format=%s"): "chore(authority): activate one-shot SOLUTE DIRECT mapping",
            ("diff", "--name-only", "1" * 40, "2" * 40): runner.AUTHORITY + "\n" + runner.DECISION}
        with patch.object(runner.authority, "require_active"), \
                patch.object(runner, "git", side_effect=lambda root, *args: answers[args]), \
                patch.object(runner.subprocess, "check_output", side_effect=lambda args, **kw: texts[args[-1].split(":", 1)[1]].encode()), \
                patch.object(runner.authority, "read_asset") as read:
            _, hashes, exposure, _ = runner.frozen_inputs(runner.ROOT)
        self.assertEqual(set(hashes), set(runner.FROZEN_FILES))
        self.assertEqual(len(exposure["assets"]), 20)
        read.assert_not_called()

    def test_fragmentation_pass_is_never_downgraded(self):
        for state in ("PASS_DIRECT_MULTIMODAL_MAPPING", "PARTIAL_ONE_PAIR", "BLOCKED_INTERNAL_VALIDATION",
                      "BLOCKED_MODALITY_INFORMATION_INSUFFICIENT", "BLOCKED_IDENTITY_NOT_DISCRIMINATIVE",
                      "BLOCKED_MULTIMODAL_METRIC_DISCORDANCE", "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE",
                      "BLOCKED_EXECUTION_FAILURE"):
            gates = runner.terminal_gates(state)
            self.assertEqual(gates["G2_FRAG"], "PASS_DIRECT_RASTER_MAPPING")
            self.assertIs(gates["TI3_PLUS_AUTHORIZED"], False)

    def test_finite_terminal_reason_precedence(self):
        for state in ("BLOCKED_MODALITY_INFORMATION_INSUFFICIENT", "BLOCKED_IDENTITY_NOT_DISCRIMINATIVE",
                      "BLOCKED_MULTIMODAL_METRIC_DISCORDANCE"):
            self.assertEqual(runner.aggregate({"one": {"status": state}}), (state, "BLOCKED"))


if __name__ == "__main__":
    unittest.main()
