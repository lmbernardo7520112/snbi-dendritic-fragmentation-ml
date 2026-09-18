"""Public scientific I/O denies before inspecting synthetic path sentinels."""

import ast
from contextlib import ExitStack
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import run_ti1_audit
from scripts import ti2_authority as compatibility_authority
from snbi_fragmentation import custody, metadata, ti2_authority as authority
from snbi_fragmentation import ti2_pilot as pilot


ROOT = Path(__file__).resolve().parents[1]


class ExplodingPath:
    """A sentinel, never an operational path or an experimental source."""

    def __fspath__(self):
        raise AssertionError("path protocol touched before denial")

    def __str__(self):
        raise AssertionError("path string touched before denial")

    def __repr__(self):
        raise AssertionError("path representation touched before denial")

    def read(self, *args):
        raise AssertionError("source stream touched before denial")


class PublicIOAuthorityTests(unittest.TestCase):
    def calls(self):
        sentinel = ExplodingPath()
        return (
            (pilot.open_readonly, (sentinel,)),
            (pilot.verify_archive, (sentinel, sentinel)),
            (pilot.extract_pilot, (sentinel, sentinel)),
            (pilot.hash_stream, (sentinel,)),
            (custody.verify_sources, (sentinel, sentinel)),
            (custody.verify_main, (["verify", sentinel, "--data-root", sentinel],)),
            (metadata.probe_zip_member, (sentinel, sentinel, sentinel, sentinel)),
            (metadata.ffprobe_version, (sentinel,)),
            (run_ti1_audit.main, ()),
            (run_ti1_audit.write_json, (sentinel, sentinel)),
        )

    def deny_all(self, message):
        for function, arguments in self.calls():
            with self.subTest(api=function.__name__):
                with self.assertRaises(authority.ScientificExecutionBlocked) as caught:
                    function(*arguments)
                self.assertEqual(str(caught.exception), message)

    def test_guard_is_first_executable_statement_of_every_public_io_api(self):
        definitions = {
            "src/snbi_fragmentation/ti2_pilot.py": {
                "hash_stream", "open_readonly", "verify_archive", "extract_pilot"
            },
            "src/snbi_fragmentation/custody.py": {"verify_sources", "verify_main"},
            "src/snbi_fragmentation/metadata.py": {"probe_zip_member", "ffprobe_version"},
            "scripts/run_ti1_audit.py": {"main", "write_json"},
        }
        for relative, expected in definitions.items():
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
            for name in sorted(expected):
                with self.subTest(module=relative, api=name):
                    body = functions[name].body
                    if (isinstance(body[0], ast.Expr)
                            and isinstance(body[0].value, ast.Constant)
                            and isinstance(body[0].value.value, str)):
                        body = body[1:]
                    first = body[0]
                    self.assertIsInstance(first, ast.Expr)
                    self.assertIsInstance(first.value, ast.Call)
                    self.assertIsInstance(first.value.func, ast.Name)
                    self.assertEqual(first.value.func.id, "require_scientific_authority")
                    self.assertEqual(first.value.args, [])
                    self.assertEqual(first.value.keywords, [])

    def test_every_entry_uses_the_identical_shared_guard_and_exception(self):
        self.assertIs(compatibility_authority.require_scientific_authority,
                      authority.require_scientific_authority)
        self.assertIs(compatibility_authority.ScientificExecutionBlocked,
                      authority.ScientificExecutionBlocked)
        for module in (pilot, custody, metadata, run_ti1_audit):
            with self.subTest(module=module.__name__):
                self.assertIs(module.require_scientific_authority,
                              authority.require_scientific_authority)

    def test_actual_closed_canonical_state_denies_before_exploding_path_protocols(self):
        self.assertEqual(authority.audit_authority()["status"], "PASS")
        self.deny_all("TI2_EXECUTION_BLOCKED: terminally closed; new author decision required")

    def test_zero_downstream_calls_with_closed_canonical_loader_mock(self):
        # Isolate the one permitted canonical text read so every downstream I/O
        # primitive can be mocked and checked, including globally shared os.open.
        state = copy.deepcopy({**authority.CLOSED_STATE, **authority.BOUNDARY_STATE})
        targets = [
            (pilot.os, "open"), (pilot.os, "fdopen"), (pilot.os, "write"),
            (pilot.os, "memfd_create"), (pilot.os, "replace"), (pilot.os, "fspath"),
            (Path, "open"), (Path, "read_text"), (Path, "read_bytes"),
            (Path, "write_text"), (Path, "write_bytes"), (Path, "mkdir"),
            (Path, "resolve"), (Path, "absolute"), (Path, "exists"),
            (Path, "is_file"), (Path, "stat"),
            (pilot.zipfile, "ZipFile"),
            (pilot.subprocess, "run"), (pilot.subprocess, "Popen"),
            (tempfile, "TemporaryDirectory"), (tempfile, "NamedTemporaryFile"),
            (tempfile, "mkstemp"), (tempfile, "mkdtemp"),
            (pilot, "load_manifest"), (custody, "load_manifest"),
            (run_ti1_audit, "load_manifest"),
            (pilot, "decoder_command"), (metadata, "parse_ffprobe"),
            (custody, "build_parser"), (run_ti1_audit, "build_parser"),
        ]
        with patch.object(authority, "load_governance", return_value=state) as canonical, ExitStack() as stack:
            opened = stack.enter_context(patch("builtins.open"))
            mocks = [stack.enter_context(patch.object(owner, name)) for owner, name in targets]
            self.deny_all("TI2_EXECUTION_BLOCKED: terminally closed; new author decision required")
            self.assertEqual(canonical.call_count, len(self.calls()))
            for call in canonical.call_args_list:
                self.assertEqual(call.args, (authority.ROOT,))
            opened.assert_not_called()
            for mocked in mocks:
                mocked.assert_not_called()

    def test_missing_canonical_authority_denies_every_io_entry(self):
        with patch.object(authority.os, "open", side_effect=FileNotFoundError):
            self.deny_all("TI2_EXECUTION_BLOCKED: invalid canonical authority")

    def test_malformed_canonical_toml_denies_every_io_entry(self):
        with patch.object(authority.os, "open", return_value=-1), \
             patch.object(authority.os, "fdopen", side_effect=lambda *args: io.BytesIO(b"[tool.snbi\n")):
            self.deny_all("TI2_EXECUTION_BLOCKED: invalid canonical authority")

    def test_unknown_canonical_state_denies_every_io_entry(self):
        state = copy.deepcopy({**authority.CLOSED_STATE, **authority.BOUNDARY_STATE})
        state["current_authorized_activity"] = "UNKNOWN"
        with patch.object(authority.tomllib, "load", return_value={"tool": {"snbi": state}}):
            self.deny_all("TI2_EXECUTION_BLOCKED: invalid canonical authority")

    def test_conflicting_scientific_true_denies_every_io_entry(self):
        state = copy.deepcopy({**authority.CLOSED_STATE, **authority.BOUNDARY_STATE})
        state["ti2_execution_authorized"] = True
        with patch.object(authority.tomllib, "load", return_value={"tool": {"snbi": state}}):
            self.deny_all("TI2_EXECUTION_BLOCKED: invalid canonical authority")

    def test_verification_cli_dispatch_denies_before_parser_or_manifest(self):
        sentinel = ExplodingPath()
        with patch.object(custody, "build_parser") as parser, \
             patch.object(custody, "load_manifest") as manifest:
            for command in ("verify", "unknown", sentinel):
                with self.assertRaises(authority.ScientificExecutionBlocked):
                    custody.main([command, sentinel, "--data-root", sentinel])
        parser.assert_not_called()
        manifest.assert_not_called()

    def test_validation_cli_dispatch_retains_textual_metadata_only_path(self):
        arguments = ["validate", "synthetic-metadata.json"]
        with patch.object(custody, "_main", return_value=0) as text_validation, \
             patch.object(custody, "verify_main") as verification:
            self.assertEqual(custody.main(arguments), 0)
        text_validation.assert_called_once_with(arguments)
        verification.assert_not_called()


if __name__ == "__main__":
    unittest.main()
