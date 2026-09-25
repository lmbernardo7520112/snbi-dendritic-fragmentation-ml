"""Invented metadata and disposable local roots; no real corpus or ML access.

The pure auditor is exercised on generated rows. Runner tests use fresh roots
below .bootstrap-test-tmp and fake preflight proofs, never the real CLI or a
preflight against this repository. Tracked contract/source text may be read.
"""

import ast
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from snbi_fragmentation import study4_feasibility as feasibility
from scripts import run_study4_s4a_feasibility as runner


ROOT = Path(__file__).absolute().parents[1]
BOTTOM = "bottom_up_anti_parallel"
TOP = "top_down_parallel"
ACQUISITIONS = (BOTTOM, TOP)
MANIFEST_SHA = "a" * 64
HEAD = "b" * 40
METADATA_FIELDS = (
    "sample_id", "group_id", "acquisition_id", "frame_index", "label",
    "tier", "kind", "split", "cv_fold",
)


def group_rows(group, label, frames=range(8), acquisition=BOTTOM, fold=0):
    """Every identity and frame below is invented, not copied from corpus text."""
    return [{
        "sample_id": f"{group}-{frame}", "group_id": group,
        "acquisition_id": acquisition, "frame_index": frame,
        "label": label, "tier": "GOLD" if label else "BACKGROUND",
        "kind": "positive" if label else "background", "split": "TRAIN",
        "cv_fold": fold,
    } for frame in frames]


def pair_rows(frames=range(8), acquisition=BOTTOM):
    return (group_rows("synthetic-positive", 1, frames, acquisition)
            + group_rows("synthetic-background", 0, frames, acquisition))


def capacity_rows(bottom, top):
    rows = []
    for acquisition, count in ((BOTTOM, bottom), (TOP, top)):
        for number in range(count):
            rows.extend(group_rows(f"{acquisition}-p{number}", 1, acquisition=acquisition))
            rows.extend(group_rows(f"{acquisition}-b{number}", 0, acquisition=acquisition))
    return rows


def summarize(rows):
    return feasibility.summarize_feasibility(rows, MANIFEST_SHA)


class MetadataFeasibilityTests(unittest.TestCase):
    def test_eight_shared_frames_create_one_candidate_edge(self):
        result = summarize(pair_rows())
        self.assertEqual(result["candidate_edge_count"], 1)
        self.assertEqual(result["total_maximum_matching_capacity"], 1)

    def test_seven_shared_frames_do_not_create_candidate_edge(self):
        result = summarize(pair_rows(range(7)))
        self.assertEqual(result["candidate_edge_count"], 0)
        self.assertEqual(result["total_maximum_matching_capacity"], 0)

    def test_same_acquisition_is_required_even_for_identical_frames(self):
        rows = group_rows("p", 1, acquisition=BOTTOM) + group_rows("b", 0, acquisition=TOP)
        result = summarize(rows)
        self.assertEqual(result["candidate_edge_count"], 0)
        self.assertEqual(result["isolated_positive_group_count"], 1)
        self.assertEqual(result["isolated_background_group_count"], 1)

    def test_support_counts_distinct_common_frames_not_total_group_rows(self):
        rows = group_rows("p", 1, range(12)) + group_rows("b", 0, range(5, 17))
        result = summarize(rows)
        self.assertEqual(result["authenticated_row_count"], 24)
        self.assertEqual(result["candidate_edge_count"], 0)

    def test_duplicate_valid_group_frame_is_explicitly_blocked(self):
        rows = pair_rows()
        duplicate = dict(rows[0], sample_id="different-sample-same-group-frame")
        rows.append(duplicate)
        with self.assertRaisesRegex(feasibility.FeasibilityError,
                                    "BLOCKED_AMBIGUOUS_GROUP_FRAME_IDENTITY"):
            summarize(rows)

    def test_duplicate_sample_identity_is_not_silently_deduplicated(self):
        rows = pair_rows()
        rows[1]["sample_id"] = rows[0]["sample_id"]
        with self.assertRaises(feasibility.FeasibilityError):
            summarize(rows)

    def test_inconsistent_group_acquisition_is_blocked(self):
        rows = pair_rows()
        rows[0]["acquisition_id"] = TOP
        with self.assertRaises(feasibility.FeasibilityError):
            summarize(rows)

    def test_inconsistent_group_label_is_blocked_even_when_each_row_is_valid(self):
        rows = pair_rows()
        rows[0].update(label=0, tier="BACKGROUND", kind="background")
        with self.assertRaises(feasibility.FeasibilityError):
            summarize(rows)

    def test_dev_row_is_blocked_not_filtered(self):
        rows = pair_rows()
        rows[0]["split"] = "DEV"
        with self.assertRaises(feasibility.FeasibilityError):
            summarize(rows)

    def test_test_row_is_blocked_not_filtered(self):
        rows = pair_rows()
        rows[0]["split"] = "TEST"
        with self.assertRaises(feasibility.FeasibilityError):
            summarize(rows)

    def test_silver_row_is_blocked_not_filtered(self):
        rows = pair_rows()
        rows[0]["tier"] = "SILVER"
        with self.assertRaises(feasibility.FeasibilityError):
            summarize(rows)

    def test_malformed_and_out_of_range_frames_are_blocked(self):
        for acquisition, value in ((BOTTOM, -1), (BOTTOM, 294), (TOP, 395),
                                   (BOTTOM, True), (BOTTOM, 1.0),
                                   (BOTTOM, "1"), (BOTTOM, None)):
            rows = pair_rows(acquisition=acquisition)
            rows[0]["frame_index"] = value
            with self.subTest(acquisition=acquisition, value=value), \
                    self.assertRaises(feasibility.FeasibilityError):
                summarize(rows)

    def test_frozen_frame_bounds_are_inclusive(self):
        for acquisition, maximum in ((BOTTOM, 293), (TOP, 394)):
            result = summarize(pair_rows(tuple(range(7)) + (maximum,), acquisition))
            with self.subTest(acquisition=acquisition):
                self.assertEqual(result["candidate_edge_count"], 1)

    def test_invalid_class_combinations_unknown_acquisitions_and_bool_labels_block(self):
        for replacement in ({"label": True}, {"label": 1, "tier": "BACKGROUND"},
                            {"kind": "background"}, {"acquisition_id": "third_acquisition"}):
            rows = pair_rows()
            rows[0].update(replacement)
            with self.subTest(replacement=replacement), self.assertRaises(feasibility.FeasibilityError):
                summarize(rows)

    def test_every_authorized_metadata_field_is_mandatory(self):
        for field in METADATA_FIELDS:
            rows = pair_rows()
            del rows[0][field]
            with self.subTest(field=field), self.assertRaises(feasibility.FeasibilityError):
                summarize(rows)

    def test_storage_provenance_and_payload_values_cannot_change_results(self):
        rows = pair_rows()
        decorated = deepcopy(rows)
        for index, row in enumerate(decorated):
            row.update(storage={"path": "/synthetic-never-open/payload.bin",
                                "row_index": 100000 + index, "offset": -index,
                                "sha256": "f" * 64, "dtype": "invented"},
                       provenance={"file_hash": "0" * 64}, row_index=-index,
                       offset=10000000, payload_bytes=[1, 2, 3], pixel_values=[4, 5])
        self.assertEqual(summarize(rows), summarize(decorated))

    def test_frame_sets_are_canonical_sorted_and_rows_remain_unchanged(self):
        rows = pair_rows((7, 0, 6, 1, 5, 2, 4, 3))
        before = deepcopy(rows)
        groups = feasibility.group_rows(rows)
        frame_sets = feasibility.valid_frame_sets(groups)
        self.assertEqual(set(frame_sets), {"synthetic-positive", "synthetic-background"})
        self.assertTrue(all(frames == tuple(range(8)) for frames in frame_sets.values()))
        self.assertEqual(rows, before)

    def test_graph_separates_acquisitions_and_keeps_isolated_positive_groups(self):
        rows = pair_rows(acquisition=BOTTOM) + group_rows("isolated-top-positive", 1, acquisition=TOP)
        graph = feasibility.construct_candidate_graph(feasibility.group_rows(rows))
        self.assertEqual(set(graph), set(ACQUISITIONS))
        self.assertEqual(graph[BOTTOM], {"synthetic-positive": ("synthetic-background",)})
        self.assertEqual(graph[TOP], {"isolated-top-positive": ()})

    def test_aggregates_count_rows_groups_edges_and_isolates_by_acquisition(self):
        rows = (pair_rows(acquisition=BOTTOM)
                + group_rows("isolated-positive", 1, range(20, 28), TOP)
                + group_rows("isolated-background", 0, range(40, 48), TOP))
        result = summarize(rows)
        self.assertEqual(result["authenticated_row_count"], 32)
        self.assertEqual(result["positive_row_count"], 16)
        self.assertEqual(result["background_row_count"], 16)
        self.assertEqual(result["positive_group_count"], 2)
        self.assertEqual(result["background_group_count"], 2)
        self.assertEqual(result["by_acquisition"][BOTTOM], {
            "positive_group_count": 1, "background_group_count": 1,
            "candidate_edge_count": 1, "isolated_positive_group_count": 0,
            "isolated_background_group_count": 0, "maximum_matching_capacity": 1,
        })
        self.assertEqual(result["by_acquisition"][TOP], {
            "positive_group_count": 1, "background_group_count": 1,
            "candidate_edge_count": 0, "isolated_positive_group_count": 1,
            "isolated_background_group_count": 1, "maximum_matching_capacity": 0,
        })

    def test_fifteen_total_pairs_are_insufficient(self):
        result = summarize(capacity_rows(14, 1))
        self.assertEqual(result["total_maximum_matching_capacity"], 15)
        self.assertEqual(result["feasibility_decision"], "INSUFFICIENT_COVERAGE_OVERLAP")

    def test_sixteen_pairs_and_both_acquisitions_are_sufficient(self):
        result = summarize(capacity_rows(15, 1))
        self.assertEqual(result["total_maximum_matching_capacity"], 16)
        self.assertEqual(result["feasibility_decision"], "SUFFICIENT_COMMON_SUPPORT")

    def test_sixteen_pairs_with_one_acquisition_absent_are_insufficient(self):
        for bottom, top in ((16, 0), (0, 16)):
            result = summarize(capacity_rows(bottom, top))
            with self.subTest(bottom=bottom, top=top):
                self.assertEqual(result["total_maximum_matching_capacity"], 16)
                self.assertEqual(result["feasibility_decision"], "INSUFFICIENT_COVERAGE_OVERLAP")

    def test_reordered_rows_have_identical_minimized_results(self):
        rows = capacity_rows(3, 2)
        self.assertEqual(summarize(rows), summarize(rows[::-1]))
        self.assertEqual(summarize(rows), summarize(rows[1::2] + rows[::2]))

    def test_pure_feasibility_performs_zero_payload_or_file_io(self):
        rows = pair_rows()
        with patch("builtins.open", side_effect=AssertionError("unexpected open")), \
             patch.object(Path, "open", side_effect=AssertionError("unexpected Path.open")), \
             patch.object(os, "open", side_effect=AssertionError("unexpected os.open")), \
             patch.object(os, "read", side_effect=AssertionError("unexpected os.read")), \
             patch.object(os, "pread", side_effect=AssertionError("unexpected os.pread")):
            result = summarize(rows)
        self.assertEqual(result["payload_binary_reads"], 0)
        self.assertEqual(result["feature_extractions"], 0)
        self.assertEqual(result["fits"], 0)

    def test_documentary_digest_must_be_a_sha256_not_a_source_locator(self):
        for digest in (None, "a" * 63, "g" * 64, "/synthetic/source.json"):
            with self.subTest(digest=digest), self.assertRaises(feasibility.FeasibilityError):
                feasibility.summarize_feasibility(pair_rows(), digest)


class MaximumMatchingTests(unittest.TestCase):
    def test_background_group_cannot_be_reused(self):
        self.assertEqual(feasibility.maximum_matching_cardinality({"p1": ["b"], "p2": ["b"]}), 1)

    def test_positive_group_cannot_be_reused(self):
        self.assertEqual(feasibility.maximum_matching_cardinality({"p": ["b1", "b2", "b3"]}), 1)

    def test_augmenting_path_handles_greedy_counterexample(self):
        adjacency = {"p1": ["b1", "b2"], "p2": ["b1"]}
        self.assertEqual(feasibility.maximum_matching_cardinality(adjacency), 2)

    def test_maximum_cardinality_with_disconnected_components_and_isolates(self):
        adjacency = {"p1": ["b1", "b2"], "p2": ["b1"],
                     "p3": ["b3"], "p4": ["b3"], "isolated": []}
        self.assertEqual(feasibility.maximum_matching_cardinality(adjacency), 3)
        self.assertEqual(feasibility.maximum_matching_cardinality({}), 0)

    def test_cardinality_is_deterministic_under_vertex_and_neighbor_order(self):
        first = {"p1": ["b1", "b2"], "p2": ["b1"], "p3": ["b3", "b2"]}
        second = {key: first[key][::-1] for key in reversed(first)}
        self.assertEqual(feasibility.maximum_matching_cardinality(first), 3)
        self.assertEqual(feasibility.maximum_matching_cardinality(second), 3)

    def test_maximum_cardinality_matches_independent_exhaustive_small_graph_oracle(self):
        # All 512 bipartite graphs on three left and three right vertices.
        # The oracle enumerates partial injective assignments, not augmenting paths.
        left, right = ("p0", "p1", "p2"), ("b0", "b1", "b2")
        def exhaustive(adjacency, position=0, used=frozenset()):
            if position == len(left):
                return 0
            choices = [exhaustive(adjacency, position + 1, used)]
            choices.extend(1 + exhaustive(adjacency, position + 1, used | {target})
                           for target in adjacency[left[position]] if target not in used)
            return max(choices)
        for bits in range(512):
            graph = {source: [target for j, target in enumerate(right)
                              if bits & (1 << (3 * i + j))]
                     for i, source in enumerate(left)}
            with self.subTest(bits=bits):
                self.assertEqual(feasibility.maximum_matching_cardinality(graph), exhaustive(graph))


class MinimalResultAndContractTests(unittest.TestCase):
    def test_result_schema_contains_no_pair_identities(self):
        result = summarize(pair_rows())
        feasibility.validate_result_schema(result)
        encoded = json.dumps(result, sort_keys=True)
        self.assertNotIn("synthetic-positive", encoded)
        self.assertNotIn("synthetic-background", encoded)
        self.assertNotIn("selected_frames", encoded)
        altered = deepcopy(result)
        altered["matched_pair_identities"] = [["p", "b"]]
        with self.assertRaises(feasibility.FeasibilityError):
            feasibility.validate_result_schema(altered)

    def test_result_schema_contains_no_edge_list_or_candidate_group_ids(self):
        result = summarize(pair_rows())
        for key in ("edge_list", "candidate_group_ids", "selected_frames"):
            altered = deepcopy(result)
            altered[key] = []
            with self.subTest(key=key), self.assertRaises(feasibility.FeasibilityError):
                feasibility.validate_result_schema(altered)
        nested = deepcopy(result)
        nested["by_acquisition"][BOTTOM]["edges"] = []
        with self.assertRaises(feasibility.FeasibilityError):
            feasibility.validate_result_schema(nested)

    def test_result_schema_preserves_exact_documentary_digest_and_zero_counters(self):
        result = summarize(pair_rows())
        self.assertEqual(result["documentary_manifest_sha256"], MANIFEST_SHA)
        for field in ("payload_binary_reads", "feature_extractions", "fits"):
            for value in (1, True):
                altered = deepcopy(result)
                altered[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(feasibility.FeasibilityError):
                    feasibility.validate_result_schema(altered)

    def test_result_schema_rejects_inconsistent_aggregate_and_decision(self):
        result = summarize(pair_rows())
        for field, value in (("authenticated_row_count", 15),
                             ("total_maximum_matching_capacity", 2),
                             ("feasibility_decision", "SUFFICIENT_COMMON_SUPPORT")):
            altered = deepcopy(result)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(feasibility.FeasibilityError):
                feasibility.validate_result_schema(altered)

    def test_frozen_contract_matches_metadata_frame_bounds_and_decision(self):
        contract = json.loads((ROOT / "configs/study4/feasibility-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["operational_metadata_allowlist"], list(METADATA_FIELDS))
        self.assertEqual(contract["valid_frame_definition"], {
            "type": "INTEGER_NOT_BOOL", "minimum": 0,
            "maximum_inclusive_by_acquisition": {BOTTOM: 293, TOP: 394},
            "source": "src/snbi_fragmentation/study3_domain.py:FRAME_MAX",
        })
        self.assertEqual(contract["decision_rule"]["total_max_matched_pairs_min"], 16)
        self.assertEqual(contract["decision_rule"]["maximum_matching_capacity_min_by_acquisition"],
                         {BOTTOM: 1, TOP: 1})

    def test_module_has_only_stdlib_imports_and_runs_without_site_packages(self):
        source = (ROOT / "src/snbi_fragmentation/study4_feasibility.py").read_text(encoding="utf-8")
        imports = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertTrue(imports <= set(sys.stdlib_module_names) | {"__future__"}, imports)
        command = [sys.executable, "-B", "-S", "-c",
                   "from snbi_fragmentation.study4_feasibility import maximum_matching_cardinality; "
                   "assert maximum_matching_cardinality({'p': ('b',)}) == 1"]
        completed = subprocess.run(command, cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")},
                                   capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)


class SyntheticRunnerRoot(unittest.TestCase):
    def setUp(self):
        parent = ROOT / ".bootstrap-test-tmp"
        parent.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="study4-feasibility-", dir=parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def put(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        content = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True).encode("utf-8")
        path.write_bytes(content)
        return content

    def proof(self, content=b"invented-manifest"):
        return {
            "head_sha": HEAD, "authorization_sha256": "b" * 64,
            "authorization_semantic_digest": "c" * 64, "ci_proof_sha256": "d" * 64,
            "contracts_sha256": {path: "e" * 64 for path in runner.CONTRACT_PATHS},
            "documentary_manifest_sha256": hashlib.sha256(content).hexdigest(),
            "ci_job_count": 12, "ci_step_count": 12,
        }

    def ci_proof(self):
        return {"head_sha": HEAD, "runs": [
            {"headSha": HEAD, "name": name, "path": details["path"],
             "status": "completed", "conclusion": "success", "jobs": [
                 {"name": job, "status": "completed", "conclusion": "success", "steps": [
                     {"name": "synthetic", "status": "completed", "conclusion": "success"}]}
                 for job in details["jobs"]]}
            for name, details in runner.REQUIRED_WORKFLOWS.items()
        ]}


class FutureAuthorizationTests(SyntheticRunnerRoot):
    def test_future_runner_blocks_without_explicit_local_authorization(self):
        with patch.object(runner, "read_text", wraps=runner.read_text) as reads:
            with self.assertRaises((OSError, runner.S4AExecutionError)):
                runner.preflight(self.root)
        self.assertNotIn(runner.SOURCE_MANIFEST, [call.args[1] for call in reads.call_args_list])
        self.assertFalse((self.root / runner.EVIDENCE).exists())

    def test_future_runner_blocks_without_ci_proof_before_manifest_access(self):
        hashes = {path: "e" * 64 for path in runner.CONTRACT_PATHS}
        self.put(runner.AUTHORIZATION, {"grant": runner.authorization_grant(HEAD, hashes),
                                       "author_decision_sha256": "f" * 64})
        with patch.object(runner, "read_text", wraps=runner.read_text) as reads:
            with self.assertRaises((OSError, runner.S4AExecutionError)):
                runner.preflight(self.root)
        self.assertNotIn(runner.SOURCE_MANIFEST, [call.args[1] for call in reads.call_args_list])
        self.assertFalse((self.root / runner.EVIDENCE).exists())

    def test_exact_sha_ci_proof_is_required(self):
        proof = self.ci_proof()
        valid = runner.verify_ci(proof, HEAD)
        self.assertEqual(valid["job_count"], 12)
        self.assertEqual(valid["step_count"], 12)
        proof["head_sha"] = "f" * 40
        with self.assertRaises(runner.S4AExecutionError):
            runner.verify_ci(proof, HEAD)

    def test_ci_rejects_wrong_run_sha_missing_workflow_and_unsuccessful_step(self):
        wrong_sha = self.ci_proof()
        wrong_sha["runs"][0]["headSha"] = "f" * 40
        missing = self.ci_proof()
        missing["runs"].pop()
        skipped = self.ci_proof()
        skipped["runs"][0]["jobs"][0]["steps"][0]["conclusion"] = "skipped"
        for proof in (wrong_sha, missing, skipped):
            with self.subTest(proof=proof), self.assertRaises(runner.S4AExecutionError):
                runner.verify_ci(proof, HEAD)

    def test_authorization_is_bound_to_exact_head_and_contract_hashes(self):
        hashes = {path: "e" * 64 for path in runner.CONTRACT_PATHS}
        decision = {"grant": runner.authorization_grant(HEAD, hashes), "author_decision_sha256": "f" * 64}
        digest = runner.validate_authorization(decision, HEAD, hashes)
        self.assertRegex(digest, r"^[a-f0-9]{64}$")
        with self.assertRaises(runner.S4AExecutionError):
            runner.validate_authorization(decision, "a" * 40, hashes)
        altered_hashes = dict(hashes)
        altered_hashes[next(iter(altered_hashes))] = "0" * 64
        with self.assertRaises(runner.S4AExecutionError):
            runner.validate_authorization(decision, HEAD, altered_hashes)
        altered = deepcopy(decision)
        altered["grant"]["extra_authority"] = True
        with self.assertRaises(runner.S4AExecutionError):
            runner.validate_authorization(altered, HEAD, hashes)

    def test_second_future_receipt_creation_is_denied_and_first_is_preserved(self):
        proof = self.proof()
        runner.create_receipt(self.root, proof)
        path = self.root / runner.EVIDENCE / runner.RECEIPT
        before = path.read_bytes()
        with self.assertRaises((OSError, runner.S4AExecutionError)):
            runner.create_receipt(self.root, proof)
        self.assertEqual(path.read_bytes(), before)

    def test_existing_receipt_blocks_second_invocation_before_manifest_read(self):
        runner.create_receipt(self.root, self.proof())
        path = self.root / runner.EVIDENCE / runner.RECEIPT
        before = path.read_bytes()
        with patch.object(runner, "read_text", side_effect=AssertionError("read after consumed")):
            with self.assertRaises(runner.S4AExecutionError):
                runner.run(self.root)
        self.assertEqual(path.read_bytes(), before)

    def test_authorization_symlink_is_denied_without_following_it(self):
        target = self.root / "invented-control-target.json"
        target.write_text("{}", encoding="utf-8")
        control = self.root / runner.AUTHORIZATION
        control.parent.mkdir(parents=True, exist_ok=True)
        control.symlink_to(target)
        with self.assertRaises((OSError, runner.S4AExecutionError)):
            runner.preflight(self.root)
        self.assertFalse((self.root / runner.EVIDENCE).exists())


class FutureInvocationTests(SyntheticRunnerRoot):
    def test_synthetic_run_authenticates_bytes_then_consumes_receipt_before_analysis(self):
        rows = pair_rows()
        for row in rows:
            row["storage"] = {"path": "/synthetic-never-open/payload.bin", "offset": 42}
        content = self.put(runner.SOURCE_MANIFEST, {"rows": rows})
        proof = self.proof(content)
        events = []
        original_reader = runner.read_text
        original_create = runner.create_receipt
        original_summary = feasibility.summarize_feasibility
        def read(root, relative):
            events.append(("read", relative))
            return original_reader(root, relative)
        def receipt(root, supplied):
            events.append(("receipt", None))
            self.assertEqual(supplied["documentary_manifest_sha256"], hashlib.sha256(content).hexdigest())
            return original_create(root, supplied)
        def analyze(supplied_rows, digest):
            events.append(("analyze", None))
            self.assertTrue((self.root / runner.EVIDENCE / runner.RECEIPT).is_file())
            return original_summary(supplied_rows, digest)
        with patch.object(runner, "preflight", return_value=proof) as preflight, \
             patch.object(runner, "read_text", side_effect=read), \
             patch.object(runner, "create_receipt", side_effect=receipt), \
             patch.object(feasibility, "summarize_feasibility", side_effect=analyze):
            terminal = runner.run(self.root)
        preflight.assert_called_once_with(self.root)
        self.assertEqual(events, [("read", runner.SOURCE_MANIFEST), ("receipt", None), ("analyze", None)])
        self.assertEqual(terminal["STUDY4_S4A"], "PASS")
        self.assertEqual(terminal["state"], "CLOSED_CONSUMED")
        self.assertIs(terminal["authority_consumed"], True)
        self.assertIs(terminal["retry_authorized"], False)
        self.assertIs(terminal["visual_model_execution_allowed"], False)
        self.assertIs(terminal["final_pair_matching_executed"], False)
        self.assertIs(terminal["pair_identities_selected"], False)
        result_path = self.root / runner.EVIDENCE / runner.RESULT
        result = json.loads(result_path.read_text(encoding="utf-8"))
        feasibility.validate_result_schema(result)
        self.assertEqual(terminal["result_sha256"], hashlib.sha256(result_path.read_bytes()).hexdigest())
        self.assertEqual(set(path.name for path in (self.root / runner.EVIDENCE).iterdir()),
                         {runner.RECEIPT, runner.RESULT, runner.TERMINAL})
        for field in ("payload_binary_reads", "feature_extractions", "fits"):
            self.assertEqual(terminal[field], 0)
            self.assertEqual(result[field], 0)

    def test_wrong_documentary_digest_blocks_before_receipt_or_analysis(self):
        self.put(runner.SOURCE_MANIFEST, {"rows": pair_rows()})
        with patch.object(runner, "preflight", return_value=self.proof(b"different invented bytes")), \
             patch.object(feasibility, "summarize_feasibility", side_effect=AssertionError("analysis reached")), \
             self.assertRaises(runner.S4AExecutionError):
            runner.run(self.root)
        self.assertFalse((self.root / runner.EVIDENCE / runner.RECEIPT).exists())

    def test_failure_after_receipt_preserves_blocked_terminal_without_retry(self):
        content = self.put(runner.SOURCE_MANIFEST, {"rows": pair_rows()})
        with patch.object(runner, "preflight", return_value=self.proof(content)), \
             patch.object(feasibility, "summarize_feasibility", side_effect=feasibility.FeasibilityError("invented failure")), \
             self.assertRaises(feasibility.FeasibilityError):
            runner.run(self.root)
        receipt_path = self.root / runner.EVIDENCE / runner.RECEIPT
        terminal_path = self.root / runner.EVIDENCE / runner.TERMINAL
        receipt_before = receipt_path.read_bytes()
        terminal_before = terminal_path.read_bytes()
        terminal = json.loads(terminal_before)
        self.assertEqual(terminal["STUDY4_S4A"], "BLOCKED")
        self.assertEqual(terminal["state"], "CLOSED_CONSUMED")
        self.assertIs(terminal["authority_consumed"], True)
        self.assertIs(terminal["retry_authorized"], False)
        self.assertFalse((self.root / runner.EVIDENCE / runner.RESULT).exists())
        with patch.object(runner, "read_text", side_effect=AssertionError("read after failure")), \
             self.assertRaises(runner.S4AExecutionError):
            runner.run(self.root)
        self.assertEqual(receipt_path.read_bytes(), receipt_before)
        self.assertEqual(terminal_path.read_bytes(), terminal_before)

    def test_authenticated_malformed_json_consumes_receipt_and_blocks(self):
        content = self.put(runner.SOURCE_MANIFEST, b"not valid invented JSON")
        with patch.object(runner, "preflight", return_value=self.proof(content)), \
             self.assertRaises(ValueError):
            runner.run(self.root)
        self.assertTrue((self.root / runner.EVIDENCE / runner.RECEIPT).is_file())
        terminal = json.loads((self.root / runner.EVIDENCE / runner.TERMINAL).read_text(encoding="utf-8"))
        self.assertEqual(terminal["STUDY4_S4A"], "BLOCKED")
        self.assertIs(terminal["retry_authorized"], False)

    def test_manifest_symlink_is_denied_before_receipt(self):
        target = self.root / "invented-manifest-target.json"
        content = json.dumps({"rows": pair_rows()}).encode("utf-8")
        target.write_bytes(content)
        source = self.root / runner.SOURCE_MANIFEST
        source.parent.mkdir(parents=True, exist_ok=True)
        source.symlink_to(target)
        with patch.object(runner, "preflight", return_value=self.proof(content)), \
             self.assertRaises((OSError, runner.S4AExecutionError)):
            runner.run(self.root)
        self.assertFalse((self.root / runner.EVIDENCE / runner.RECEIPT).exists())

    def test_documentary_reader_denies_storage_path_before_any_file_open(self):
        with patch.object(os, "open", side_effect=AssertionError("unauthorized path reached filesystem")), \
             self.assertRaises(runner.S4AExecutionError):
            runner.read_text(self.root, "data/derived/invented.bin")


if __name__ == "__main__":
    unittest.main()
