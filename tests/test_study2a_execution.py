"""Synthetic orchestration contracts; never open sources or run a detector."""

from contextlib import ExitStack
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from snbi_fragmentation import study2a_execution as execution
from snbi_fragmentation import study2a_streaming as streaming


RAW_HASH = "a" * 64
HEAD = "b" * 40


def ci_proof():
    return {"head_sha": HEAD, "runs": [{
        "headSha": HEAD, "status": "completed", "conclusion": "success",
        "jobs": [{"name": name, "status": "completed", "conclusion": "success",
                  "steps": [{"conclusion": "success"}]}
                 for name in sorted(execution.REQUIRED_JOBS)],
    }]}


def authority():
    return {
        "schema_version": 1, "base_sha": execution.BASE, "branch": execution.BRANCH,
        "phase": "STUDY2_A_ANNOTATION_MINING", "detector": copy.deepcopy(execution.DETECTOR),
        "persistence_tolerance_px": 2.0, "sources": ["ESM3", "ESM6"],
        "expected_frames": {"ESM3": 294, "ESM6": 395}, "scientific_runs_limit": 1,
        "human_review": False, "hough": False, "patches": False, "ml": False,
        "max_temp_bytes": 268435456, "max_patch_cache_bytes": 2147483648,
        "min_free_disk_reserve_bytes": execution.MIN_FREE,
        "metadata_output_budget_bytes": execution.MAX_METADATA,
        "legacy_center_absolute_tolerance_px": 1e-9,
        "new_frames_require_frozen_commit_and_green_ci": True,
        "terminal_closes_authority": True,
        "authority_sha256": execution.digest(b"synthetic author decision"),
        "decoder_gate_authority_sha256": execution.digest(b"synthetic decoder decision"),
    }


def marker(component_id, x=50.0, y=50.0):
    return {"component_id": component_id, "classification": "VALID_GRAPHICAL_CIRCLE",
            "center_xy_px": [x, y], "bbox_xyxy": [int(x)-11, int(y)-11, int(x)+12, int(y)+12],
            "area_px": 100, "reasons": [], "semantic_label": "UNKNOWN",
            "physical_extent": "NOT_INFERRED"}


def detector_result(components=()):
    return {"component_count": len(components), "valid_circle_count": len(components),
            "ambiguous_component_count": 0, "small_component_count": 0,
            "colored_pixel_count": len(components) * 100,
            "colored_chroma_sample_count": len(components) * 25,
            "components": list(components)}


def old_sites():
    return [{"annotation_site_id": f"old-{source}-{index}", "source_id": source,
             "observation_ids": [f"{source}:0:graphic-component-{index:04d}"]}
            for source, count in (("ESM3", 38), ("ESM6", 14))
            for index in range(1, count + 1)]


class FreshRoot(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / ".bootstrap-test-tmp"
        parent.mkdir(exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(prefix="study2a-execution-test-", dir=parent)
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        (self.root / execution.EVIDENCE).mkdir(parents=True)

    def read_output(self, name):
        return json.loads((self.root / execution.EVIDENCE / name).read_text())


class PreflightTests(FreshRoot):
    def fixture(self, cfg=None, proof=None):
        stack = ExitStack()
        self.addCleanup(stack.close)
        enter = stack.enter_context
        cfg = authority() if cfg is None else cfg
        source = mock.Mock(side_effect=AssertionError("source access prohibited"))
        enter(mock.patch.object(streaming, "AuthenticatedSources", source))
        text = {path: b"synthetic " + path.encode() for path in (*execution.CORE_PATHS, *execution.LEGACY_PATHS)}
        text.update({execution.A0: b"synthetic A0",
                     execution.AUTHORITY: json.dumps(cfg).encode(),
                     execution.EVIDENCE + "/AUTHORIZATION.md": b"synthetic author decision",
                     execution.EVIDENCE + "/DECODER_GATE_AUTHORIZATION.md": b"synthetic decoder decision",
                     execution.EVIDENCE + "/PROTOCOL.md": b"protocol",
                     execution.EVIDENCE + "/SYNTHETIC_TESTS.json": b"{}",
                     "configs/governance/phase-scope-v1.json": b"{}",
                     ".github/workflows/study2a-synthetic.yml": b"workflow"})
        legacy = {"status": "PASS", "processed_frames": 10,
                  "counts": {"VALID": 108, "AMBIGUOUS": 380, "SMALL": 3},
                  "implementation_hashes": {p: execution.digest(text[p]) for p in (*execution.CORE_PATHS, execution.A0, execution.AUTHORITY)}}
        text[execution.EVIDENCE + "/LEGACY_REPRODUCTION.json"] = json.dumps(legacy).encode()
        hashes = {p: execution.digest(b) for p, b in text.items()}
        text[execution.EVIDENCE + "/METHOD_FREEZE.json"] = json.dumps({"files": hashes}).encode()
        objects = {execution.AUTHORITY: cfg,
                   execution.LEGACY_PATHS[0]: {"config": execution.DETECTOR, "persistence_tolerance_px": 2.0},
                   execution.EVIDENCE + "/LEGACY_REPRODUCTION.json": legacy,
                   execution.EVIDENCE + "/CI_PROOF.json": ci_proof() if proof is None else proof}
        enter(mock.patch.object(execution, "load_json", side_effect=lambda root, path: objects[path]))
        enter(mock.patch.object(execution, "text_bytes", side_effect=lambda root, path: text[path]))
        enter(mock.patch.object(execution, "A0_SHA", execution.digest(text[execution.A0])))
        enter(mock.patch.object(execution.importlib.metadata, "version", side_effect=lambda name: {"numpy": "1.26.4", "scipy": "1.11.4"}[name]))
        enter(mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=10**12)))
        enter(mock.patch.object(execution, "preserved_baseline", return_value=542))
        def git(root, *args):
            if args == ("branch", "--show-current"):
                return execution.BRANCH
            if args == ("rev-parse", "HEAD"):
                return HEAD
            if args == ("rev-parse", "HEAD^"):
                return execution.BASE
            raise AssertionError(args)
        enter(mock.patch.object(execution, "git", side_effect=git))
        enter(mock.patch.object(execution, "git_bytes", side_effect=lambda root, command, path: text[path.split(":", 1)[1]]))
        return source, text

    def test_full_preflight_text_fixture_passes_without_source_or_receipt(self):
        source, _ = self.fixture()
        proof = execution.preflight(self.root, "full")
        self.assertEqual(proof["status"], "PASS")
        self.assertEqual(set(proof["ci_jobs"]), execution.REQUIRED_JOBS)
        self.assertEqual(proof["experimental_source_opens"], 0)
        self.assertFalse(proof["receipt_created"])
        source.assert_not_called()
        self.assertFalse((self.root / execution.EVIDENCE / "EXECUTION_RECEIPT.json").exists())

    def test_authority_type_or_limit_divergence_denies_before_source(self):
        cfg = authority()
        cfg["persistence_tolerance_px"] = 2
        source, _ = self.fixture(cfg)
        with self.assertRaisesRegex(execution.Study2Error, "configuration diverged"):
            execution.run_full(self.root)
        source.assert_not_called()

    def test_wrong_ci_head_denies_before_source(self):
        proof = ci_proof()
        proof["head_sha"] = "0" * 40
        source, _ = self.fixture(proof=proof)
        with self.assertRaisesRegex(execution.Study2Error, "exact method-freeze HEAD"):
            execution.run_full(self.root)
        source.assert_not_called()

    def test_failed_step_denies_even_when_job_and_run_claim_success(self):
        proof = ci_proof()
        proof["runs"][0]["jobs"][0]["steps"][0]["conclusion"] = "skipped"
        source, _ = self.fixture(proof=proof)
        with self.assertRaisesRegex(execution.Study2Error, "steps"):
            execution.run_full(self.root)
        source.assert_not_called()

    def test_prior_receipt_prevents_all_text_git_and_source_work(self):
        execution.exclusive_json(self.root, execution.EVIDENCE + "/EXECUTION_RECEIPT.json", {"attempt": 1})
        with mock.patch.object(execution, "git") as git, mock.patch.object(streaming, "AuthenticatedSources") as source:
            with self.assertRaisesRegex(execution.Study2Error, "already consumed"):
                execution.run_full(self.root)
            source.assert_not_called()
            git.assert_not_called()

    def test_terminal_record_prevents_legacy_reactivation(self):
        execution.exclusive_json(self.root, execution.EVIDENCE + "/terminal-state.json", {"STATE": "CLOSED"})
        with mock.patch.object(streaming, "AuthenticatedSources") as source:
            with self.assertRaisesRegex(execution.Study2Error, "already closed"):
                execution.run_legacy(self.root)
            source.assert_not_called()

    def test_missing_or_duplicate_ci_job_cannot_substitute_for_all_seven(self):
        proof = ci_proof()
        proof["runs"][0]["jobs"][-1] = proof["runs"][0]["jobs"][0]
        with self.assertRaisesRegex(execution.Study2Error, "seven"):
            execution.check_ci(proof, HEAD)


class HistoricalComparisonTests(unittest.TestCase):
    def test_exact_legacy_frame_passes(self):
        result = detector_result([marker(1)])
        proof = execution.compare_legacy_frame(result, copy.deepcopy(result), RAW_HASH, {"image_sha256": RAW_HASH})
        self.assertEqual(proof["VALID"], 1)
        self.assertEqual(proof["maximum_valid_center_difference_px"], 0.0)

    def test_raw_hash_cannot_be_replaced_by_matching_detector_output(self):
        result = detector_result()
        with self.assertRaisesRegex(execution.Study2Error, "raw hash"):
            execution.compare_legacy_frame(result, result, "b" * 64, {"image_sha256": RAW_HASH})

    def test_component_counts_and_identity_are_immutable(self):
        baseline = detector_result([marker(1)])
        modified = copy.deepcopy(baseline)
        modified["ambiguous_component_count"] += 1
        with self.assertRaisesRegex(execution.Study2Error, "count"):
            execution.compare_legacy_frame(modified, baseline, RAW_HASH, {"image_sha256": RAW_HASH})
        modified = copy.deepcopy(baseline)
        modified["components"][0]["component_id"] = 2
        with self.assertRaisesRegex(execution.Study2Error, "identity"):
            execution.compare_legacy_frame(modified, baseline, RAW_HASH, {"image_sha256": RAW_HASH})

    def test_center_tolerance_is_numerical_only_and_nonfinite_denied(self):
        baseline = detector_result([marker(1)])
        for dx in (1e-8, float("nan"), float("inf")):
            modified = copy.deepcopy(baseline)
            modified["components"][0]["center_xy_px"][0] += dx
            with self.assertRaisesRegex(execution.Study2Error, "center"):
                execution.compare_legacy_frame(modified, baseline, RAW_HASH, {"image_sha256": RAW_HASH})

    def test_all_52_legacy_sites_map_injectively(self):
        sites = old_sites()
        links = {s["observation_ids"][0]: {"state": "DIRECT_VALID", "site_id": f"new-{i}"} for i, s in enumerate(sites)}
        result = execution.map_legacy_sites(sites, links)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["mapped"], 52)

    def test_missing_conflicting_and_many_to_one_mapping_fail_closed(self):
        sites = old_sites()
        links = {s["observation_ids"][0]: {"state": "DIRECT_VALID", "site_id": f"new-{i}"} for i, s in enumerate(sites)}
        del links[sites[0]["observation_ids"][0]]
        links[sites[1]["observation_ids"][0]]["state"] = "CONFLICT"
        links[sites[2]["observation_ids"][0]]["site_id"] = "shared"
        links[sites[3]["observation_ids"][0]]["site_id"] = "shared"
        result = execution.map_legacy_sites(sites, links)
        self.assertEqual(result["unmapped"], 4)
        self.assertEqual(result["sites"][2]["status"], "UNMAPPED_NONINJECTIVE")
        self.assertEqual(result["sites"][3]["status"], "UNMAPPED_NONINJECTIVE")


class FullRunTests(FreshRoot):
    def fixture(self, failure_after=None, fail_output=False):
        stack = ExitStack()
        self.addCleanup(stack.close)
        enter = stack.enter_context
        root = self.root
        class Reader:
            def __init__(self, mode, audit):
                self.audit = audit
                self.audit.update({"mode": mode, "source_auth_opens": 0, "synthetic_only": True})
                # The exclusive receipt must already be durable before reader construction.
                if not (root / execution.EVIDENCE / "EXECUTION_RECEIPT.json").exists():
                    raise AssertionError("reader constructed before receipt")
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.audit["closed"] = True
            def iter_frames(self, source):
                for index in range(execution.SOURCE_INFO[source]["frames"]):
                    if source == "ESM3" and failure_after is not None and index == failure_after:
                        raise RuntimeError("synthetic decode failure")
                    yield index, index.to_bytes(2, "big"), RAW_HASH
        enter(mock.patch.object(streaming, "AuthenticatedSources", Reader))
        enter(mock.patch.object(execution, "preflight", return_value={"head_sha": HEAD, "status": "PASS"}))
        enter(mock.patch.object(execution, "legacy_inputs", return_value=({}, {})))
        enter(mock.patch.object(execution, "load_json", return_value=old_sites()))
        enter(mock.patch.object(execution, "text_bytes", return_value=b"synthetic authority"))
        enter(mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=10**12)))
        def detected(raw, source, temporal_evidence=False):
            if int.from_bytes(raw, "big") != 0:
                return detector_result()
            count = 38 if source == "ESM3" else 14
            return detector_result([marker(i, 50 + (i % 10) * 60, 50 + (i // 10) * 60) for i in range(1, count + 1)])
        detector = enter(mock.patch.object(execution, "detect", side_effect=detected))
        def aggregate(root, path, rows, remaining):
            count = sum(1 for _ in rows)
            return {"path": path, "size_bytes": count, "record_count": count, "complete": True}
        if fail_output:
            aggregate = mock.Mock(side_effect=execution.Study2Error("synthetic output budget exceeded"))
        enter(mock.patch.object(execution, "write_jsonl", side_effect=aggregate))
        return detector

    def test_full_mocked_689_frames_accounts_every_index_and_maps52(self):
        detector = self.fixture()
        terminal = execution.run_full(self.root)
        self.assertEqual(terminal["STUDY2_A"], "PASS")
        self.assertEqual(terminal["ANNOTATION_FRAMES_PROCESSED"], 689)
        self.assertEqual(terminal["LEGACY_SITES_MAPPED"], 52)
        self.assertEqual(detector.call_count, 689)
        frames = self.read_output("FRAME_SUMMARY.json")
        self.assertEqual(len(frames), 689)
        self.assertTrue(all(f["frame_processing_status"] == "PROCESSED" for f in frames))
        self.assertFalse(terminal["STUDY2_B_AUTHORIZED"])
        self.assertEqual(terminal["STATE"], "CLOSED_CONSUMED")

    def test_source_failure_closes_and_accounts_unprocessed689_remainder(self):
        detector = self.fixture(failure_after=2)
        terminal = execution.run_full(self.root)
        self.assertEqual(terminal["STUDY2_A"], "BLOCKED_PARTIAL_EXECUTION")
        self.assertEqual(detector.call_count, 2)
        self.assertEqual(terminal["ANNOTATION_FRAMES_PROCESSED"], 2)
        frames = self.read_output("FRAME_SUMMARY.json")
        self.assertEqual(len(frames), 689)
        failed = [f for f in frames if f["frame_processing_status"] != "PROCESSED"]
        self.assertEqual(len(failed), 687)
        self.assertTrue(all(f["processed"] is False for f in failed))
        self.assertTrue(all("NOT_ADMITTED" in f["failure_reason"] for f in failed))
        self.assertTrue(self.read_output("IO_AUDIT.json")["closed"])
        self.assertEqual(terminal["STATE"], "CLOSED_CONSUMED")

    def test_output_budget_failure_still_closes_authority(self):
        self.fixture(fail_output=True)
        terminal = execution.run_full(self.root)
        self.assertEqual(terminal["STUDY2_A"], "BLOCKED_OUTPUT_PRESERVATION")
        self.assertEqual(terminal["STATE"], "CLOSED_CONSUMED")
        self.assertIn("preservation_failure", self.read_output("results.json"))
        self.assertFalse(terminal["STUDY2_B_READY_FOR_AUTHOR_DECISION"])

    def test_exclusive_receipt_denies_retry_even_if_preflight_is_mocked(self):
        self.fixture(failure_after=0)
        execution.run_full(self.root)
        before = (self.root / execution.EVIDENCE / "EXECUTION_RECEIPT.json").read_bytes()
        with mock.patch.object(streaming, "AuthenticatedSources") as source:
            with self.assertRaises(FileExistsError):
                execution.run_full(self.root)
            source.assert_not_called()
        self.assertEqual(before, (self.root / execution.EVIDENCE / "EXECUTION_RECEIPT.json").read_bytes())

    def test_jsonl_budget_failure_preserves_partial_file_without_overwrite(self):
        path = "data/derived/study2/OBSERVATION_LEDGER.jsonl"
        with mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=10**12)):
            with self.assertRaisesRegex(execution.Study2Error, "budget"):
                execution.write_jsonl(self.root, path, [{"x": 1}, {"long": "x" * 100}], 30)
        self.assertEqual((self.root / path).read_bytes(), b'{"x":1}\n')
        with self.assertRaises(FileExistsError):
            execution.write_jsonl(self.root, path, [], 30)

    def test_full_storage_budget_violation_cannot_return_pass(self):
        self.fixture()
        original_stat = Path.stat
        def write_small_fixture(root, relative, rows, remaining):
            path = Path(root) / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"{}\n")
            return {"path": relative, "size_bytes": 3, "record_count": 1, "complete": True}
        def measured_oversize(path, *args, **kwargs):
            observed = original_stat(path, *args, **kwargs)
            if path.name == "OBSERVATION_LEDGER.jsonl":
                # Simulate an oversized measured artifact without allocating or
                # creating a large file. Existence checks still use real paths.
                return SimpleNamespace(st_size=execution.MAX_METADATA + 1,
                                       st_mode=observed.st_mode)
            return observed
        with mock.patch.object(execution, "write_jsonl", side_effect=write_small_fixture), \
                mock.patch.object(Path, "stat", measured_oversize):
            terminal = execution.run_full(self.root)
        self.assertEqual(terminal["STUDY2_A"], "BLOCKED_STORAGE_BUDGET")
        self.assertFalse(self.read_output("IO_AUDIT.json")["storage_budget_compliance"])
        self.assertEqual(self.read_output("results.json")["status"], "BLOCKED_STORAGE_BUDGET")
        self.assertFalse(terminal["STUDY2_B_READY_FOR_AUTHOR_DECISION"])


class OutputBoundaryTests(FreshRoot):
    def test_exclusive_json_reserves_space_for_imminent_content(self):
        relative = execution.EVIDENCE + "/synthetic-output.json"
        value = {"synthetic": True}
        size = len((json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode())
        with mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=execution.MIN_FREE + size - 1)):
            with self.assertRaisesRegex(execution.Study2Error, "reserved disk"):
                execution.exclusive_json(self.root, relative, value)
        self.assertFalse((self.root / relative).exists())
        with mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=execution.MIN_FREE + size)):
            record = execution.exclusive_json(self.root, relative, value)
        self.assertEqual(record["size_bytes"], size)

    def test_jsonl_reserves_space_for_next_record_before_writing_it(self):
        relative = "data/derived/study2/OBSERVATION_LEDGER.jsonl"
        content = b'{"x":1}\n'
        with mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=execution.MIN_FREE + len(content) - 1)):
            with self.assertRaisesRegex(execution.Study2Error, "free-disk budget"):
                execution.write_jsonl(self.root, relative, [{"x": 1}], 100)
        self.assertEqual((self.root / relative).read_bytes(), b"")

    def test_legacy_post_receipt_output_failure_closes_without_reclassifying_as_preflight(self):
        original_writer = execution.exclusive_json
        reader = mock.MagicMock()
        reader.__enter__.return_value.iter_frames.side_effect = lambda source: iter(())
        def fail_audit(root, relative, value):
            if relative.endswith("/LEGACY_IO_AUDIT.json"):
                raise OSError("synthetic post-receipt output failure")
            return original_writer(root, relative, value)
        with mock.patch.object(execution, "preflight", return_value={"head_sha": execution.BASE}), \
                mock.patch.object(execution, "legacy_inputs", return_value=({}, {})), \
                mock.patch.object(execution, "text_bytes", return_value=b"synthetic text"), \
                mock.patch.object(streaming, "AuthenticatedSources", return_value=reader), \
                mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=10**12)), \
                mock.patch.object(execution, "exclusive_json", side_effect=fail_audit):
            terminal = execution.run_legacy(self.root)
        self.assertTrue((self.root / execution.EVIDENCE / "LEGACY_RECEIPT.json").exists())
        self.assertEqual(terminal["STUDY2_A"], "BLOCKED_POST_RECEIPT_LEGACY_FAILURE")
        self.assertEqual(terminal["STATE"], "CLOSED_BLOCKED")
        self.assertEqual(terminal["SCIENTIFIC_STUDY2A_RUNS"], 0)
        self.assertEqual(self.read_output("terminal-state.json"), terminal)


if __name__ == "__main__":
    unittest.main()
