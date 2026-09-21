"""Synthetic Study2-B orchestration contracts; no source, decoder or ML access."""

import ast
from collections import Counter
from contextlib import ExitStack
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from snbi_fragmentation import study2b_execution as execution
from snbi_fragmentation import study2b_streaming as streaming


HEAD = "b" * 40
FREE = SimpleNamespace(total=2**42, used=0, free=2**42)


def authority():
    return {
        "schema_version": 1, "phase": "STUDY2_B", "base_sha": execution.BASE,
        "branch": execution.BRANCH, "sources": ["ESM1", "ESM2", "ESM4", "ESM5"],
        "ml": False, "human_review": False, "scientific_runs_limit": 1,
        "patch_side": 65, "patch_radius": 32,
        "channels": ["STRUCTURAL_Y", "RELATIVE_SOLUTE_FIELD_Y"], "dtype": "uint8",
        "max_patch_cache_bytes": execution.MAX_PATCH,
        "max_temp_bytes": execution.MAX_METADATA,
        "min_free_disk_reserve_bytes": execution.MIN_FREE,
        "metadata_output_budget_bytes": execution.MAX_METADATA,
        "legacy_fixture_count": 50, "expected_input_records": 27396,
        "terminal_closes_authority": True,
        "authority_sha256": execution.digest(b"synthetic author decision"),
        "decoder_gate_authority_sha256": execution.digest(b"synthetic decoder decision"),
    }


def ci_proof():
    return {"head_sha": HEAD, "runs": [{
        "headSha": HEAD, "status": "completed", "conclusion": "success",
        "jobs": [{"name": name, "status": "completed", "conclusion": "success",
                  "steps": [{"name": "synthetic", "status": "completed", "conclusion": "success"}]}
                 for name in sorted(execution.REQUIRED_JOBS)],
    }]}


class FreshRoot(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / ".bootstrap-test-tmp"
        parent.mkdir(exist_ok=True)
        folder = tempfile.TemporaryDirectory(prefix="study2b-execution-test-", dir=parent)
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        (self.root / execution.EVIDENCE).mkdir(parents=True)
        self.disk = mock.patch.object(execution.shutil, "disk_usage", return_value=FREE).start()
        self.addCleanup(mock.patch.stopall)


class PreflightTests(FreshRoot):
    def fixture(self, mode="legacy", cfg=None):
        stack = ExitStack()
        self.addCleanup(stack.close)
        enter = stack.enter_context
        cfg = authority() if cfg is None else cfg
        paths = set(execution.CORE_PATHS + execution.TEST_PATHS + execution.PROTOCOL_PATHS + execution.INPUT_PATHS) | {
            execution.AUTHORITY, execution.EVIDENCE + "/AUTHORIZATION.md",
            execution.EVIDENCE + "/DECODER_GATE_AUTHORIZATION.md",
            execution.EVIDENCE + "/SYNTHETIC_TESTS.json",
            execution.EVIDENCE + "/LEGACY_REPRODUCTION.json",
            ".github/workflows/study2b-synthetic.yml", "configs/governance/phase-scope-v1.json",
        }
        contents = {p: ("synthetic " + p).encode() for p in paths}
        contents[execution.EVIDENCE + "/AUTHORIZATION.md"] = b"synthetic author decision"
        contents[execution.EVIDENCE + "/DECODER_GATE_AUTHORIZATION.md"] = b"synthetic decoder decision"
        contents[execution.AUTHORITY] = json.dumps(cfg).encode()
        legacy = {"status": "PASS", "legacy_fixture_pair_hash_matches": 50,
                  "implementation_hashes": {p: execution.digest(contents[p]) for p in execution.CORE_PATHS}}
        contents[execution.EVIDENCE + "/LEGACY_REPRODUCTION.json"] = json.dumps(legacy).encode()
        freeze = {"files": {p: execution.digest(b) for p, b in contents.items()}}
        contents[execution.EVIDENCE + "/METHOD_FREEZE.json"] = json.dumps(freeze).encode()
        documents = {
            execution.AUTHORITY: cfg,
            execution.EVIDENCE + "/SYNTHETIC_TESTS.json": {"status": "PASS", "skips": 0, "failures": 0, "errors": 0},
            execution.EVIDENCE + "/LEGACY_REPRODUCTION.json": legacy,
            execution.EVIDENCE + "/CI_PROOF.json": ci_proof(),
        }
        def fake_git(root, *args):
            values = {("branch", "--show-current"): execution.BRANCH,
                      ("rev-parse", "HEAD"): execution.BASE if mode == "legacy" else HEAD,
                      ("rev-parse", "HEAD^"): execution.BASE}
            return values[args]
        git = enter(mock.patch.object(execution, "git", side_effect=fake_git))
        enter(mock.patch.object(execution, "git_bytes", side_effect=lambda root, command, spec: contents[spec.split(":", 1)[1]]))
        text = enter(mock.patch.object(execution, "text_bytes", side_effect=lambda root, path: contents[path]))
        load = enter(mock.patch.object(execution, "load_json", side_effect=lambda root, path: documents[path]))
        preserved = enter(mock.patch.object(execution, "preserved_baseline", return_value=588))
        enter(mock.patch.object(execution.importlib.metadata, "version", side_effect=lambda p: {"numpy": "1.26.4", "scipy": "1.11.4"}[p]))
        source = enter(mock.patch.object(streaming, "AuthenticatedSources", side_effect=AssertionError("no experimental source")))
        return SimpleNamespace(cfg=cfg, docs=documents, contents=contents, freeze=freeze,
                               legacy=legacy, git=git, text=text, load=load, source=source, preserved=preserved)

    def test_legacy_preflight_text_only_before_receipt(self):
        f = self.fixture()
        result = execution.preflight(self.root, "legacy")
        self.assertEqual(result["head_sha"], execution.BASE)
        self.assertEqual(result["experimental_source_opens"], 0)
        self.assertFalse(result["receipt_created"])
        f.source.assert_not_called()
        self.assertFalse((self.root / execution.EVIDENCE / "LEGACY_RECEIPT.json").exists())

    def test_full_preflight_requires_frozen_text_and_eight_ci_jobs(self):
        f = self.fixture("full")
        result = execution.preflight(self.root, "full")
        self.assertEqual(result["ci_jobs"], sorted(execution.REQUIRED_JOBS))
        self.assertEqual(result["frozen_text_count"], len(f.freeze["files"]))
        f.source.assert_not_called()

    def test_terminal_and_existing_receipt_deny_before_git_or_authority_io(self):
        for filename in ("terminal-state.json", "results.json", "EXECUTION_RECEIPT.json"):
            with self.subTest(filename=filename):
                path = self.root / execution.EVIDENCE / filename
                path.write_text("{}")
                with mock.patch.object(execution, "git") as git, mock.patch.object(execution, "load_json") as load:
                    with self.assertRaises(execution.Study2Error):
                        execution.preflight(self.root, "full")
                    git.assert_not_called()
                    load.assert_not_called()
                path.unlink()

    def test_unknown_mode_denied_before_git(self):
        with mock.patch.object(execution, "git") as git:
            with self.assertRaises(execution.Study2Error):
                execution.preflight(self.root, "retry")
            git.assert_not_called()

    def test_authority_rejects_missing_unknown_and_noncanonical_types(self):
        cases = []
        missing = authority(); missing.pop("ml"); cases.append(missing)
        extra = authority(); extra["retry"] = False; cases.append(extra)
        for key, value in (("ml", 0), ("scientific_runs_limit", True), ("patch_side", 65.0),
                           ("human_review", "false"), ("sources", ["ESM1", "ESM3"])):
            wrong = authority(); wrong[key] = value; cases.append(wrong)
        for cfg in cases:
            with self.subTest(cfg=cfg):
                f = self.fixture(cfg=cfg)
                with self.assertRaises(execution.Study2Error):
                    execution.preflight(self.root, "legacy")
                f.source.assert_not_called()

    def test_authorization_digest_divergence_blocks(self):
        f = self.fixture()
        f.contents[execution.EVIDENCE + "/AUTHORIZATION.md"] += b"changed"
        with self.assertRaisesRegex(execution.Study2Error, "custody"):
            execution.preflight(self.root, "legacy")

    def test_wrong_branch_and_wrong_legacy_head_block(self):
        f = self.fixture()
        f.git.side_effect = None
        f.git.return_value = "wrong"
        with self.assertRaisesRegex(execution.Study2Error, "branch"):
            execution.preflight(self.root, "legacy")
        f.git.side_effect = lambda root, *args: execution.BRANCH if args[0] == "branch" else HEAD
        with self.assertRaisesRegex(execution.Study2Error, "precede method freeze"):
            execution.preflight(self.root, "legacy")

    def test_dependency_and_disk_reserve_checked_before_sources(self):
        f = self.fixture()
        with mock.patch.object(execution.importlib.metadata, "version", return_value="wrong"):
            with self.assertRaisesRegex(execution.Study2Error, "dependency"):
                execution.preflight(self.root, "legacy")
        self.disk.return_value = SimpleNamespace(free=execution.MIN_FREE)
        with self.assertRaisesRegex(execution.Study2Error, "disk reserve"):
            execution.preflight(self.root, "legacy")
        f.source.assert_not_called()

    def test_synthetic_failure_skips_errors_all_block(self):
        f = self.fixture()
        for key in ("skips", "failures", "errors"):
            with self.subTest(key=key):
                f.docs[execution.EVIDENCE + "/SYNTHETIC_TESTS.json"][key] = 1
                with self.assertRaisesRegex(execution.Study2Error, "synthetic"):
                    execution.preflight(self.root, "legacy")
                f.docs[execution.EVIDENCE + "/SYNTHETIC_TESTS.json"][key] = 0

    def test_modified_frozen_text_blocks_before_source(self):
        f = self.fixture("full")
        f.contents[execution.CORE_PATHS[0]] += b"changed"
        with self.assertRaisesRegex(execution.Study2Error, "frozen text differs"):
            execution.preflight(self.root, "full")
        f.source.assert_not_called()

    def test_existing_container_blocks_without_overwrite(self):
        self.fixture("full")
        path = self.root / execution.DATA / "multimodal_patches_uint8.bin"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"synthetic-existing")
        with self.assertRaisesRegex(execution.Study2Error, "output already exists"):
            execution.preflight(self.root, "full")
        self.assertEqual(path.read_bytes(), b"synthetic-existing")

    def test_failed_legacy_gate_cannot_admit_full_run(self):
        f = self.fixture("full")
        f.legacy["status"] = "BLOCKED_LEGACY_PAIR_REPRODUCTION"
        with self.assertRaisesRegex(execution.Study2Error, "legacy reproduction"):
            execution.preflight(self.root, "full")

    def test_legacy_implementation_hashes_cannot_change_before_full_run(self):
        f = self.fixture("full")
        f.legacy["implementation_hashes"][execution.CORE_PATHS[0]] = "0" * 64
        with self.assertRaisesRegex(execution.Study2Error, "implementation changed after legacy"):
            execution.preflight(self.root, "full")


class CIProofTests(unittest.TestCase):
    def test_all_eight_jobs_are_required(self):
        self.assertEqual(len(execution.check_ci(ci_proof(), HEAD)), 8)

    def test_wrong_commit_missing_duplicate_extra_jobs_rejected(self):
        variants = []
        p = ci_proof(); p["head_sha"] = "x" * 40; variants.append(p)
        p = ci_proof(); p["runs"][0]["headSha"] = "x" * 40; variants.append(p)
        p = ci_proof(); p["runs"][0]["jobs"].pop(); variants.append(p)
        p = ci_proof(); p["runs"][0]["jobs"][0] = copy.deepcopy(p["runs"][0]["jobs"][1]); variants.append(p)
        p = ci_proof(); p["runs"][0]["jobs"].append(copy.deepcopy(p["runs"][0]["jobs"][0])); variants.append(p)
        for p in variants:
            with self.subTest(proof=p), self.assertRaises(execution.Study2Error):
                execution.check_ci(p, HEAD)

    def test_failed_skipped_cancelled_and_empty_steps_rejected(self):
        for conclusion in ("failure", "skipped", "cancelled", None):
            p = ci_proof(); p["runs"][0]["jobs"][0]["steps"][0]["conclusion"] = conclusion
            with self.subTest(conclusion=conclusion), self.assertRaises(execution.Study2Error):
                execution.check_ci(p, HEAD)
        p = ci_proof(); p["runs"][0]["jobs"][0]["steps"] = []
        with self.assertRaises(execution.Study2Error):
            execution.check_ci(p, HEAD)

    def test_pending_step_is_not_a_completed_green_check(self):
        p = ci_proof(); p["runs"][0]["jobs"][0]["steps"][0]["status"] = "in_progress"
        with self.assertRaises(execution.Study2Error):
            execution.check_ci(p, HEAD)


class ReceiptAndPathTests(FreshRoot):
    def test_receipt_exclusive_and_preserved_on_second_arm(self):
        proof = {"head_sha": HEAD, "status": "PASS"}
        with mock.patch.object(execution, "text_bytes", return_value=b"synthetic authority"):
            execution.arm(self.root, "full", proof)
            path = self.root / execution.EVIDENCE / "EXECUTION_RECEIPT.json"
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                execution.arm(self.root, "full", proof)
            self.assertEqual(path.read_bytes(), before)
        self.assertEqual(json.loads(before)["attempt"], 1)

    def test_relative_path_traversal_and_symlinks_rejected(self):
        for path in ("../outside", "/absolute", "src//x", "src/./x", "src/../x", "src\\x"):
            with self.subTest(path=path), self.assertRaises(execution.Study2Error):
                execution.safe_path(self.root, path)
        target = self.root / "target"; target.mkdir()
        (self.root / "link").symlink_to(target, target_is_directory=True)
        with self.assertRaises(execution.Study2Error):
            execution.safe_path(self.root, "link/file.json")

    def test_text_reader_denies_data_source_paths_before_open(self):
        with mock.patch.object(execution.os, "open") as opened:
            for name in ("data/raw/example.mp4", "data/derived/study2/file.jsonl", "artifacts/evidence/frame.raw"):
                with self.subTest(name=name), self.assertRaises(execution.Study2Error):
                    execution.text_bytes(self.root, name)
            opened.assert_not_called()

    def test_text_reader_admits_only_exact_historical_pilot_metadata_path(self):
        relative = "artifacts/metadata/ti2-pilot-manifest.json"
        target = self.root / relative
        target.parent.mkdir(parents=True)
        content = b'{"fixture":"synthetic historical pilot metadata"}\n'
        target.write_bytes(content)
        self.assertEqual(execution.text_bytes(self.root, relative), content)
        with mock.patch.object(execution.os, "open") as opened:
            for other in ("artifacts/metadata/other.json",
                          "artifacts/metadata/ti2-pilot-manifest-copy.json",
                          "artifacts/metadata/nested/ti2-pilot-manifest.json"):
                with self.subTest(path=other), self.assertRaises(execution.Study2Error):
                    execution.text_bytes(self.root, other)
            opened.assert_not_called()

    def test_exclusive_metadata_write_disk_guard_precedes_creation(self):
        self.disk.return_value = SimpleNamespace(free=execution.MIN_FREE)
        path = execution.EVIDENCE + "/only.json"
        with self.assertRaises(execution.Study2Error):
            execution.exclusive_json(self.root, path, {"synthetic": True})
        self.assertFalse((self.root / path).exists())

    def test_failed_post_receipt_run_is_consumed_and_second_run_cannot_mutate_it(self):
        def failing(root):
            execution.exclusive_json(root, execution.EVIDENCE + "/EXECUTION_RECEIPT.json", {"attempt": 1})
            raise RuntimeError("synthetic post-receipt failure")
        with mock.patch.object(execution, "_run_full", side_effect=failing):
            terminal = execution.run(self.root, "full")
        self.assertEqual(terminal["STATE"], "CLOSED_CONSUMED")
        self.assertEqual(terminal["SCIENTIFIC_STUDY2B_RUNS"], 1)
        terminal_path = self.root / execution.EVIDENCE / "terminal-state.json"
        prior = terminal_path.read_bytes()
        with self.assertRaises(execution.Study2Error):
            execution.run(self.root, "full")
        self.assertEqual(terminal_path.read_bytes(), prior)


class PreservationTests(unittest.TestCase):
    def fixture(self, changes="", old=None, new=None):
        old = old or {"baseline_sha": "a" * 40, "schema_version": 1,
                      "domains": {"LEGACY": [{"path": "src/old.py", "blob_sha": "1" * 40}]}}
        new = copy.deepcopy(old) if new is None else new
        def git(root, *args):
            if args[0] == "ls-tree": return "src/old.py\nconfigs/governance/phase-scope-v1.json"
            if args[0] == "diff": return changes
            if args[0] == "show": return json.dumps(old)
            raise AssertionError(args)
        stack = ExitStack(); self.addCleanup(stack.close)
        stack.enter_context(mock.patch.object(execution, "git", side_effect=git))
        stack.enter_context(mock.patch.object(execution, "load_json", return_value=new))
        return old, new

    def test_additive_scope_entries_preserve_old_rows(self):
        old, new = self.fixture(changes="src/new.py\nconfigs/governance/phase-scope-v1.json")
        new["domains"]["LEGACY"].append({"path": "src/new.py", "blob_sha": "2" * 40})
        self.assertEqual(execution.preserved_baseline("synthetic-root"), 2)

    def test_modified_historical_code_is_blocked(self):
        self.fixture(changes="src/old.py")
        with self.assertRaisesRegex(execution.Study2Error, "historical tracked"):
            execution.preserved_baseline("synthetic-root")

    def test_changed_historical_blob_and_domain_are_blocked(self):
        old, new = self.fixture()
        new["domains"]["LEGACY"][0]["blob_sha"] = "2" * 40
        with self.assertRaisesRegex(execution.Study2Error, "scope entry"):
            execution.preserved_baseline("synthetic-root")
        new["domains"]["UNAPPROVED"] = []
        with self.assertRaisesRegex(execution.Study2Error, "domains"):
            execution.preserved_baseline("synthetic-root")


class PairingTests(unittest.TestCase):
    def reader(self, left, right):
        return SimpleNamespace(iter_frames=mock.Mock(side_effect=lambda source: iter(left if source == "ESM1" else right)))

    def test_exact_source_and_frame_pair_order(self):
        left = [(3, b"s", "sh"), (4, b"s4", "sh4")]
        right = [(3, b"q", "qh"), (4, b"q4", "qh4")]
        self.assertEqual(list(execution.paired_frames(self.reader(left, right), "ESM1", "ESM2")),
                         [(3, b"s", b"q", "sh", "qh"), (4, b"s4", b"q4", "sh4", "qh4")])

    def test_cross_source_and_annotation_sources_denied_before_reader(self):
        reader = self.reader([], [])
        for sources in (("ESM1", "ESM5"), ("ESM3", "ESM2"), ("ESM6", "ESM5"), ("ESM2", "ESM1")):
            with self.subTest(sources=sources), self.assertRaises(execution.Study2Error):
                list(execution.paired_frames(reader, *sources))
        reader.iter_frames.assert_not_called()

    def test_temporal_mismatch_and_stream_length_mismatch_block(self):
        left = [(3, b"s", "sh")]
        with self.assertRaises(execution.Study2Error):
            list(execution.paired_frames(self.reader(left, [(4, b"q", "qh")]), "ESM1", "ESM2"))
        with self.assertRaises(ValueError):
            list(execution.paired_frames(self.reader(left, []), "ESM1", "ESM2"))

    def test_legacy_overlap_requires_exact_integer_crop_and_frame(self):
        row = {"site_id": "site-1", "structural_source_id": "ESM1", "frame_index": 73, "center_x": 100, "center_y": 200}
        fixtures = [dict(row, sample_id="positive|exact"), dict(row, sample_id="positive|shifted", center_x=101),
                    dict(row, sample_id="positive|next-frame", frame_index=74), dict(row, sample_id="background|same-pixel")]
        matched = execution.legacy_matches({"records": [row]}, fixtures)
        self.assertEqual(matched, {"positive|exact": row})

    def test_duplicate_canonical_crop_cannot_silently_merge_site_identities(self):
        row = {"site_id": "site-1", "structural_source_id": "ESM1", "frame_index": 73, "center_x": 100, "center_y": 200}
        with self.assertRaisesRegex(execution.Study2Error, "coordinate collision"):
            execution.legacy_matches({"records": [row, dict(row, site_id="site-2")]}, [])


class CorpusWriterTests(FreshRoot):
    def writer(self):
        writer = execution.CorpusWriter(self.root)
        self.addCleanup(writer.close)
        return writer

    def test_two_uint8_channels_index_mapping_and_durable_hashes(self):
        writer = self.writer()
        a = bytes([5]) * 4225 + bytes([9]) * 4225
        b = bytes([17]) * 8450
        self.assertEqual(writer.append_pair(a), 0)
        self.assertEqual(writer.append_pair(b), 1)
        writer.append_metadata("corpus-index.jsonl", {"row_index": 0, "pair_sha256": execution.digest(a)})
        writer.append_metadata("corpus-index.jsonl", {"row_index": 1, "pair_sha256": execution.digest(b)})
        writer.append_metadata("background-pool.jsonl", {"background_track_id": "synthetic|10|20"})
        with self.assertRaises(execution.Study2Error): writer.manifest(True)
        writer.close()
        manifest = writer.manifest(True)
        for item in manifest:
            content = (self.root / item["path"]).read_bytes()
            self.assertEqual(item["sha256"], hashlib.sha256(content).hexdigest())
            self.assertEqual(item["size_bytes"], len(content))
        self.assertEqual(manifest[0]["record_count"], 2)
        self.assertEqual(manifest[0]["size_bytes"], 16900)
        self.assertEqual((self.root / manifest[0]["path"]).read_bytes(), a + b)
        self.assertEqual(manifest[1]["record_count"], 2)
        self.assertEqual(manifest[2]["record_count"], 1)

    def test_pair_payload_rejects_float_sized_or_mutable_bytes(self):
        writer = self.writer()
        for payload in (bytes(8450 * 4), bytes(8449), bytearray(8450), "x" * 8450):
            with self.subTest(type=type(payload).__name__), self.assertRaises(execution.Study2Error):
                writer.append_pair(payload)
        self.assertEqual(writer.counts[writer.FILENAMES[0]], 0)

    def test_patch_cap_and_free_reserve_deny_before_writing(self):
        writer = self.writer()
        with mock.patch.object(execution, "MAX_PATCH", 8449):
            with self.assertRaisesRegex(execution.Study2Error, "patch cache"):
                writer.append_pair(bytes(8450))
        self.disk.return_value = SimpleNamespace(free=execution.MIN_FREE + 8449)
        with self.assertRaisesRegex(execution.Study2Error, "free disk"):
            writer.append_pair(bytes(8450))
        self.assertEqual(writer.sizes[writer.FILENAMES[0]], 0)

    def test_metadata_combined_cap_and_filename_allowlist(self):
        writer = self.writer()
        writer.append_metadata("corpus-index.jsonl", {"a": 1})
        with mock.patch.object(execution, "MAX_METADATA", writer.metadata_bytes):
            with self.assertRaisesRegex(execution.Study2Error, "metadata cap"):
                writer.append_metadata("background-pool.jsonl", {"b": 2})
        with self.assertRaises(execution.Study2Error):
            writer.append_metadata("unexpected.jsonl", {})

    def test_existing_aggregate_is_never_overwritten(self):
        writer = self.writer(); writer.append_pair(bytes([3]) * 8450); writer.close()
        prior = (self.root / execution.DATA / writer.FILENAMES[0]).read_bytes()
        with self.assertRaises(execution.Study2Error): execution.CorpusWriter(self.root)
        self.assertEqual((self.root / execution.DATA / writer.FILENAMES[0]).read_bytes(), prior)

    def test_closed_writer_cannot_append_and_partial_manifest_is_explicit(self):
        writer = self.writer(); writer.close()
        with self.assertRaises(execution.Study2Error): writer.append_pair(bytes(8450))
        self.assertTrue(all(row["complete"] is False for row in writer.manifest(False)))


class FailureAccountingTests(FreshRoot):
    def test_source_failure_preserves_every_unattempted_record_without_retry(self):
        records = [{"site_id": "site-1", "frame_index": i, "supervision_tier": "UNLABELED_PRE"} for i in range(3)]
        plan = {"records": records, "records_by_frame": {}, "exclusion_metadata": {}}
        reader = mock.MagicMock()
        reader.__enter__.side_effect = RuntimeError("synthetic source admission failure")
        with mock.patch.object(execution, "preflight", return_value={"head_sha": HEAD}), \
             mock.patch.object(execution, "build_authenticated_plan", return_value=plan), \
             mock.patch.object(execution, "load_json", return_value={"samples": []}), \
             mock.patch.object(execution, "legacy_matches", return_value={}), \
             mock.patch.object(execution, "arm") as arm, \
             mock.patch.object(streaming, "AuthenticatedSources", return_value=reader) as source, \
             mock.patch.object(execution, "finish_full", side_effect=lambda *args: args) as finish:
            args = execution._run_full(self.root)
        arm.assert_called_once()
        source.assert_called_once()
        finish.assert_called_once()
        rows = args[4]
        self.assertEqual(len(rows), 3)
        self.assertEqual(Counter(r["pair_status"] for r in rows), {"DECODE_ERROR": 3})
        self.assertTrue(all(r["row_index"] is None and r["pair_sha256"] is None for r in rows))
        self.assertTrue(all(r["failure_reason"] == "NOT_ADMITTED_AFTER_TERMINAL_PIPELINE_FAILURE" for r in rows))
        self.assertIn("synthetic source admission failure", args[8])
        self.assertEqual(args[3].sizes[args[3].FILENAMES[0]], 0)
        self.assertEqual(args[3].counts["corpus-index.jsonl"], 3)


class StaticBoundaryTests(unittest.TestCase):
    def test_study2b_imports_exclude_training_and_feature_modules(self):
        root = Path(__file__).resolve().parents[1]
        forbidden = {"sklearn", "torch", "tensorflow", "skimage", "cv2"}
        forbidden_calls = {"fit", "fit_transform", "train", "local_binary_pattern", "RandomForestClassifier", "SVC"}
        for relative in execution.CORE_PATHS:
            tree = ast.parse((root / relative).read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for item in node.names:
                        self.assertNotIn(item.name.split(".")[0], forbidden, relative)
                elif isinstance(node, ast.ImportFrom):
                    self.assertNotIn((node.module or "").split(".")[0], forbidden, relative)
                elif isinstance(node, ast.Call):
                    name = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id if isinstance(node.func, ast.Name) else ""
                    self.assertNotIn(name, forbidden_calls, relative)

    def test_source_registry_excludes_annotation_streams(self):
        self.assertEqual(set(streaming.SOURCES), {"ESM1", "ESM2", "ESM4", "ESM5"})
        with mock.patch.object(streaming.os, "open") as opened:
            for source in ("ESM3", "ESM6"):
                with self.assertRaises(streaming.StreamingContractError): streaming.source_spec(source)
            opened.assert_not_called()


if __name__ == "__main__":
    unittest.main()
