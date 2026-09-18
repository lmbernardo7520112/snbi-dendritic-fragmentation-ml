"""Synthetic gate-document contracts; no experimental path is inspected."""

import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from snbi_fragmentation import gate_authority as gates
from snbi_fragmentation import ti2_authority as authority


ROOT = Path(__file__).resolve().parents[1]


class GateAuthorityTests(unittest.TestCase):
    def governance(self):
        return copy.deepcopy({**authority.CLOSED_STATE, **authority.BOUNDARY_STATE})

    def mirror(self):
        return {
            "authority_source": "pyproject.toml [tool.snbi]",
            "current_authorized_activity": "NONE_AWAITING_AUTHOR_DECISION",
            "ti2_execution_authorized": False,
            "ti2r_authorized": False,
            "ti3_plus_authorized": False,
            "codex_local_write_readiness": "BLOCKED_AWAITING_AUTHOR_DECISION",
        }

    def document(self, mirror=None):
        payload = self.mirror() if mirror is None else mirror
        return (
            "# Synthetic current gate\n\n"
            + gates.CURRENT_BEGIN + "\n```json\n"
            + json.dumps(payload, indent=2) + "\n```\n"
            + gates.CURRENT_END + "\n"
        )

    def test_exact_current_document_passes_without_granting_authority(self):
        self.assertEqual(gates.validate_gate_document(self.document(), self.governance()), [])

    def test_each_scientific_true_and_noncanonical_truthy_value_fails(self):
        for key in ("ti2_execution_authorized", "ti2r_authorized", "ti3_plus_authorized"):
            for value in (True, "false", "true", 0, 1, None):
                with self.subTest(key=key, value=value):
                    mirror = self.mirror()
                    mirror[key] = value
                    self.assertTrue(gates.validate_gate_document(self.document(mirror), self.governance()))

    def test_missing_or_unknown_current_keys_fail(self):
        for key in self.mirror():
            with self.subTest(missing=key):
                mirror = self.mirror()
                del mirror[key]
                self.assertTrue(gates.validate_gate_document(self.document(mirror), self.governance()))
        mirror = self.mirror()
        mirror["authorized_branch"] = "synthetic"
        self.assertTrue(gates.validate_gate_document(self.document(mirror), self.governance()))

    def test_missing_or_incorrect_canonical_bridge_fails(self):
        for value in ("", "historical decision", "pyproject.toml", None):
            with self.subTest(value=value):
                mirror = self.mirror()
                mirror["authority_source"] = value
                self.assertTrue(gates.validate_gate_document(self.document(mirror), self.governance()))

    def test_unknown_activity_and_write_readiness_fail(self):
        for key, value in (
            ("current_authorized_activity", "TI2_REGISTRATION_CALIBRATION"),
            ("codex_local_write_readiness", "AUTHORIZED_DEFAULT_SANDBOX_REPOSITORY_ONLY"),
        ):
            with self.subTest(key=key):
                mirror = self.mirror()
                mirror[key] = value
                self.assertTrue(gates.validate_gate_document(self.document(mirror), self.governance()))

    def test_current_authority_outside_historical_block_fails(self):
        for statement in (
            "TI2_EXECUTION_AUTHORIZED=true",
            "`TI2_EXECUTION_AUTHORIZED`: true",
            '"ti2r_authorized": true',
            "| ti3_plus_authorized | true |",
            "CODEX_LOCAL_WRITE_READINESS=AUTHORIZED_DEFAULT_SANDBOX_REPOSITORY_ONLY",
            "TI2_EXECUTION_AUTHORIZED=false",  # A second normative surface is ambiguous.
            "AUTHORIZED_E0_E7_FROZEN_30_IMAGE_PILOT",
            "The decision supplies the current bounded authorization.",
            "Separately authorized:",
        ):
            with self.subTest(statement=statement):
                self.assertTrue(gates.validate_gate_document(
                    self.document() + statement + "\n", self.governance(),
                ))

    def test_missing_current_block_fails(self):
        self.assertTrue(gates.validate_gate_document("# No current authority\n", self.governance()))

    def test_markdown_emphasis_cannot_hide_residual_authority(self):
        for statement in (
            "**TI2_EXECUTION_AUTHORIZED**=true",
            "__TI2_EXECUTION_AUTHORIZED__: true",
            "| **ti2r_authorized** | true |",
            "*current_authorized_activity* = TI2_REGISTRATION_CALIBRATION",
        ):
            with self.subTest(statement=statement):
                self.assertTrue(gates.validate_gate_document(
                    self.document() + statement + "\n", self.governance(),
                ))

    def test_duplicate_current_block_fails_even_inside_history(self):
        for duplicate in (
            self.document(),
            gates.HISTORICAL_BEGIN + "\n" + self.document() + gates.HISTORICAL_END,
        ):
            with self.subTest(duplicate=duplicate):
                self.assertTrue(gates.validate_gate_document(self.document() + duplicate, self.governance()))

    def test_malformed_json_fence_duplicate_keys_and_nonobject_fail(self):
        baseline = self.document()
        for malformed in (
            baseline.replace('"ti2_execution_authorized": false,', '"ti2_execution_authorized":,'),
            baseline.replace('"ti2r_authorized": false,', '"ti2r_authorized": false, "ti2r_authorized": false,'),
            baseline.replace("```json", "```text"),
            baseline.replace("```json\n", ""),
            self.document([self.mirror()]),
        ):
            with self.subTest(malformed=malformed):
                self.assertTrue(gates.validate_gate_document(malformed, self.governance()))

    def test_historical_true_is_not_treated_as_current_authority(self):
        historical = (
            gates.HISTORICAL_BEGIN + "\n"
            "## Historical consumed non-authorizing record\n"
            "TI2_EXECUTION_AUTHORIZED=true\n"
            "AUTHORIZED_E0_E7_FROZEN_30_IMAGE_PILOT\n"
            "Separately authorized: valid at the historical date only.\n"
            + gates.HISTORICAL_END + "\n"
        )
        self.assertEqual(gates.validate_gate_document(
            self.document() + historical, self.governance(),
        ), [])

    def test_unclosed_inverted_nested_or_inline_markers_fail(self):
        for malformed in (
            self.document().replace(gates.CURRENT_END, ""),
            gates.CURRENT_END + "\n" + self.document(),
            self.document() + gates.HISTORICAL_BEGIN + "\n",
            self.document() + gates.HISTORICAL_END + "\n",
            self.document() + gates.HISTORICAL_BEGIN + "\n" + gates.HISTORICAL_BEGIN
                + "\n" + gates.HISTORICAL_END + "\n" + gates.HISTORICAL_END,
            self.document().replace(gates.CURRENT_BEGIN, "inline " + gates.CURRENT_BEGIN),
            self.document() + "<!-- SNBI_HISTORICAL_NON_AUTHORIZING_BEGUN -->\n",
        ):
            with self.subTest(malformed=malformed):
                self.assertTrue(gates.validate_gate_document(malformed, self.governance()))

    def test_invalid_canonical_state_cannot_be_repaired_by_gate_text(self):
        for governance in (None, {}, {**self.governance(), "ti2_execution_authorized": True}):
            with self.subTest(governance=governance):
                self.assertTrue(gates.validate_gate_document(self.document(), governance))

    def test_audit_reads_only_the_two_allowlisted_documents(self):
        with patch.object(gates, "load_governance", return_value=self.governance()), \
                patch.object(gates, "_read_gate", return_value=self.document()) as reader:
            report = gates.audit_current_gates(ROOT)
        self.assertEqual(report, {"status": "PASS", "document_count": 2, "violations": []})
        self.assertEqual(
            [call.args[1] for call in reader.call_args_list],
            ["docs/gates/LOCAL_BOOTSTRAP.md", "docs/gates/TI2_GATE_PLAN.md"],
        )

    def test_invalid_authority_stops_before_any_gate_read(self):
        with patch.object(gates, "load_governance", side_effect=ValueError), \
                patch.object(gates, "_read_gate") as reader:
            report = gates.audit_current_gates(ROOT)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["document_count"], 0)
        reader.assert_not_called()

    def test_missing_or_unreadable_gate_fails_closed(self):
        with patch.object(gates, "load_governance", return_value=self.governance()), \
                patch.object(gates, "_read_gate", side_effect=OSError):
            report = gates.audit_current_gates(ROOT)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["document_count"], 0)
        self.assertEqual(len(report["violations"]), 2)

    def test_gate_reader_uses_no_follow_for_root_directories_and_file(self):
        with patch.object(gates.os, "open", wraps=gates.os.open) as opened:
            text = gates._read_gate(ROOT, gates.CURRENT_GATE_DOCUMENTS[0])
        self.assertTrue(text.startswith("# Gate LB0"))
        self.assertEqual(len(opened.call_args_list), 4)
        for call in opened.call_args_list:
            self.assertTrue(call.args[1] & gates.os.O_NOFOLLOW)

    def test_nonregular_gate_fails_without_content_read(self):
        with patch.object(gates.stat, "S_ISREG", return_value=False), \
                patch.object(gates.os, "fdopen", wraps=gates.os.fdopen) as opened:
            with self.assertRaisesRegex(ValueError, "regular text"):
                gates._read_gate(ROOT, gates.CURRENT_GATE_DOCUMENTS[0])
        self.assertEqual(opened.call_count, 1)

    def test_repository_current_gate_documents_are_coherent_and_closed(self):
        report = gates.audit_current_gates(ROOT)
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["document_count"], 2)


if __name__ == "__main__":
    unittest.main()
