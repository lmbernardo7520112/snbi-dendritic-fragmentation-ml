"""Canonical closed-authority contracts using only text and synthetic state."""

import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import ti2_authority as authority


ROOT = Path(__file__).resolve().parents[1]


class ClosedAuthorityTests(unittest.TestCase):
    def governance(self):
        return copy.deepcopy({**authority.CLOSED_STATE, **authority.BOUNDARY_STATE})

    def test_current_closed_state_is_consistent_but_never_permission(self):
        report = authority.audit_authority(ROOT)
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["current_authorized_activity"], "NONE_AWAITING_AUTHOR_DECISION")
        self.assertEqual(report["scientific_readiness"], "BLOCKED")
        for key in ("ti2_execution_authorized", "ti2r_authorized", "ti3_plus_authorized"):
            self.assertIs(report[key], False)
        with self.assertRaisesRegex(authority.ScientificExecutionBlocked, "terminally closed"):
            authority.require_scientific_authority(ROOT)

    def test_each_of_six_required_states_missing_fails_closed(self):
        for key in authority.CLOSED_STATE:
            with self.subTest(key=key):
                state = self.governance()
                del state[key]
                self.assertTrue(authority.validate_governance(state))

    def test_each_of_six_states_rejects_unknown_and_noncanonical_truthiness(self):
        for key, expected in authority.CLOSED_STATE.items():
            for value in (None, True, False, 0, 1, "true", "false", "yes", "UNKNOWN", "", [], {}):
                if type(value) is type(expected) and value == expected:
                    continue
                with self.subTest(key=key, value=value):
                    state = self.governance()
                    state[key] = value
                    self.assertTrue(authority.validate_governance(state))
                    with patch.object(authority.tomllib, "load", return_value={"tool": {"snbi": state}}):
                        report = authority.audit_authority(ROOT)
                        self.assertEqual(report["status"], "BLOCKED")
                        self.assertIs(report["ti2_execution_authorized"], False)
                        with self.assertRaisesRegex(authority.ScientificExecutionBlocked, "invalid canonical"):
                            authority.require_scientific_authority(ROOT)

    def test_competing_alias_and_unknown_fields_are_rejected(self):
        for key, value in (
            ("authorized_activity", "ti2-registration-calibration"),
            ("lifecycle_state", "TI-2-execution-authorized"),
            ("TI2_EXECUTION_AUTHORIZED", True),
            ("future_unknown_authority", True),
        ):
            with self.subTest(key=key):
                state = self.governance()
                state[key] = value
                self.assertTrue(authority.validate_governance(state))

    def test_missing_or_wrong_type_tables_fail_closed(self):
        for document in ({}, {"tool": {}}, {"tool": "unknown"}, {"tool": {"snbi": []}}):
            with self.subTest(document=document), patch.object(authority.tomllib, "load", return_value=document):
                self.assertEqual(authority.audit_authority(ROOT)["status"], "BLOCKED")

    def test_duplicate_toml_state_or_unreadable_canonical_file_fails_closed(self):
        with patch.object(authority.os, "fdopen", return_value=io.BytesIO(
            b'[tool.snbi]\nti2_execution_authorized=false\nti2_execution_authorized=true\n'
        )), patch.object(authority.os, "open", return_value=-1):
            self.assertEqual(authority.audit_authority(ROOT)["status"], "BLOCKED")
        with patch.object(authority.os, "open", side_effect=OSError):
            self.assertEqual(authority.audit_authority(ROOT)["status"], "BLOCKED")

    def test_historical_true_text_does_not_supply_or_override_authority(self):
        temporary_root = ROOT / ".bootstrap-test-tmp"
        self.assertFalse(temporary_root.is_symlink())
        temporary_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            root = Path(directory)
            old = root / "historical-authorization.md"
            old.write_text("TI2_EXECUTION_AUTHORIZED=true\nAUTHORIZED_ACTIVITY=TI2_REGISTRATION_CALIBRATION\n", encoding="utf-8")
            canonical = root / "pyproject.toml"
            canonical.write_text((ROOT / "pyproject.toml").read_text(encoding="utf-8"), encoding="utf-8")
            with patch.object(authority.os, "open", wraps=authority.os.open) as opened:
                report = authority.audit_authority(root)
                self.assertEqual(report["status"], "PASS")
                self.assertIs(report["ti2_execution_authorized"], False)
                self.assertEqual([call.args[0] for call in opened.call_args_list], [canonical])
            canonical.unlink()
            self.assertEqual(authority.audit_authority(root)["status"], "BLOCKED")

    def test_symlink_authority_is_rejected_without_opening(self):
        with patch.object(Path, "is_symlink", return_value=True), patch.object(authority.os, "open") as opened:
            self.assertEqual(authority.audit_authority(ROOT)["status"], "BLOCKED")
        opened.assert_not_called()

    def test_report_sanitizes_malformed_values_and_paths(self):
        with patch.object(authority, "load_governance", side_effect=ValueError("private locator must not leak")):
            report = authority.audit_authority(ROOT)
        self.assertNotIn("private locator", json.dumps(report))
        self.assertEqual(report["current_authorized_activity"], "BLOCKED_INVALID_AUTHORITY")


if __name__ == "__main__":
    unittest.main()
