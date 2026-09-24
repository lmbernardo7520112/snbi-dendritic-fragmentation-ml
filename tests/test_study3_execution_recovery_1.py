"""Synthetic recovery orchestration and frozen-text custody, never real science.

Every filesystem fixture is freshly created below .bootstrap-test-tmp. The
only repository reads are approved source/config text and its Git freeze blobs.
No test reads historical row manifests, caches, execution evidence or videos.
"""

import ast
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from snbi_fragmentation import study3_execution as ex
from scripts.check_repository_data import SAFE_GIT_ENV
from test_study3_execution import controller_fixture, ci_fixture
import test_study3_execution as original_test_fixtures


ROOT = Path(__file__).absolute().parents[1]
HEAD = "c" * 40
NUMPY = importlib.util.find_spec("numpy") is not None
ORIGINAL_FREEZE = "a3f45b645e9fb3e813a43220351c951698293963"
ORIGINAL_RECEIPT = "9dae20b674064870ca2a0e2d0acc2522bf67ce29011d8ac6db709c9445e80b44"
FROZEN_SCIENTIFIC_FILES = tuple(
    "src/snbi_fragmentation/study3_" + name + ".py" for name in
    ("domain", "design", "io", "temporal_features", "cnn", "models", "metrics")
) + tuple("configs/study3/" + name + ".json" for name in
          ("data-contract", "representation-contract", "cnn-contract", "model-contract",
           "fit-budget", "evaluation-contract"))
PAYLOADS = {"data/derived/study2b/multimodal_patches_uint8.bin": 17,
            "data/derived/study2c/cachetrain_dev.bin": 23}


class SyntheticRecoveryRoot(unittest.TestCase):
    def setUp(self):
        parent = ROOT / ".bootstrap-test-tmp"
        parent.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="study3-recovery1-", dir=parent)
        self.addCleanup(temporary.cleanup)
        self.temporary = Path(temporary.name)
        self.root = self.temporary / "worktree"
        self.root.mkdir()
        self.source = self.temporary / "original"
        self.source.mkdir()

    def put(self, relative, value, root=None):
        path = (self.root if root is None else root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        content = value if isinstance(value, bytes) else ex.encode_evidence(value)
        path.write_bytes(content)
        return content


class RecoveryContractTests(unittest.TestCase):
    def test_contract_binds_consumed_attempt_and_fixed_new_authority(self):
        contract = ex.recovery_contract()
        ex.validate_recovery_contract(contract)
        self.assertEqual(contract["recovery_id"], "STUDY3_EXECUTION_RECOVERY_1")
        self.assertEqual(contract["original_method_freeze_sha"], ORIGINAL_FREEZE)
        self.assertEqual(contract["original_receipt_sha256"], ORIGINAL_RECEIPT)
        self.assertEqual(contract["original_terminal_state"], "CLOSED_CONSUMED")
        self.assertEqual(contract["failure_reason"], "WORKTREE_LOCAL_IGNORED_PAYLOAD_NOT_PROVISIONED")
        self.assertEqual(contract["recovery_scientific_invocations_limit"], 1)
        self.assertEqual(contract["recovery_distinct_fits_limit"], 28)
        self.assertEqual(contract["recovery_retries"], 0)
        for field in ("scientific_method_changed", "population_changed", "folds_changed",
                      "representations_changed", "models_changed", "hyperparameters_changed",
                      "metrics_changed", "fit_budget_changed", "DEV_ACCESS", "TEST_ACCESS",
                      "SILVER_ACCESS", "VIDEO_ACCESS"):
            self.assertIs(contract[field], False)

    def test_contract_rejects_new_methods_retry_truthy_aliases_and_unknown_keys(self):
        mutations = (lambda c: c.update(recovery_retries=1),
                     lambda c: c.update(recovery_distinct_fits_limit=29),
                     lambda c: c.update(scientific_method_changed=True),
                     lambda c: c.update(original_payload_reads=False),
                     lambda c: c.update(extra="unauthorized"),
                     lambda c: c.pop("original_receipt_sha256"))
        for mutation in mutations:
            contract = ex.recovery_contract()
            mutation(contract)
            with self.subTest(contract=contract), self.assertRaises(ex.Study3ExecutionError):
                ex.validate_recovery_contract(contract)

    def test_contract_rejects_development_access(self):
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_recovery_contract(dict(ex.recovery_contract(), DEV_ACCESS=True))

    def test_contract_rejects_test_access(self):
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_recovery_contract(dict(ex.recovery_contract(), TEST_ACCESS=True))

    def test_contract_rejects_silver_access(self):
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_recovery_contract(dict(ex.recovery_contract(), SILVER_ACCESS=True))

    def test_contract_rejects_video_access(self):
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_recovery_contract(dict(ex.recovery_contract(), VIDEO_ACCESS=True))


class RecoveryPayloadMetadataTests(SyntheticRecoveryRoot):
    def setUp(self):
        super().setUp()
        self.enterContext(patch.object(ex, "ORIGINAL_SOURCE_ROOT", str(self.source)))
        self.enterContext(patch.object(ex, "RECOVERY_PAYLOADS", dict(PAYLOADS)))
        for relative, size in PAYLOADS.items():
            self.put(relative, b"s" * size, root=self.source)
            self.put(relative, b"d" * size)

    def test_locations_use_only_metadata_without_binary_read_or_hash(self):
        with patch("builtins.open", side_effect=AssertionError("payload opened")), \
             patch.object(Path, "open", side_effect=AssertionError("payload opened")), \
             patch.object(os, "read", side_effect=AssertionError("payload read")), \
             patch.object(os, "pread", side_effect=AssertionError("payload pread")), \
             patch.object(ex, "digest", side_effect=AssertionError("payload hashed")):
            report = ex.verify_recovery_payload_locations(self.root)
        self.assertIsInstance(report, dict)

    def test_source_missing_blocks_without_fallback(self):
        (self.source / next(iter(PAYLOADS))).unlink()
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.verify_recovery_payload_sources(self.source)

    def test_destination_missing_blocks_even_with_available_source(self):
        (self.root / next(iter(PAYLOADS))).unlink()
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.verify_recovery_payload_locations(self.root)

    def test_destination_symlink_is_rejected(self):
        relative = next(iter(PAYLOADS))
        destination = self.root / relative
        destination.unlink()
        destination.symlink_to(self.source / relative)
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.verify_recovery_payload_locations(self.root)

    def test_source_symlink_is_rejected(self):
        relative = next(iter(PAYLOADS))
        source = self.source / relative
        source.unlink()
        source.symlink_to(self.root / relative)
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.verify_recovery_payload_sources(self.source)

    def test_destination_size_is_exact(self):
        self.put(next(iter(PAYLOADS)), b"wrong-size")
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.verify_recovery_payload_locations(self.root)

    def test_source_size_is_exact(self):
        self.put(next(iter(PAYLOADS)), b"wrong-size", root=self.source)
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.verify_recovery_payload_sources(self.source)

    def test_runtime_destinations_do_not_depend_on_original_repository(self):
        with patch.object(ex, "ORIGINAL_SOURCE_ROOT", self.temporary / "absent-original"):
            self.assertEqual(ex.verify_recovery_payload_locations(self.root)["status"], "PASS")

    def test_source_destination_hardlink_is_rejected(self):
        relative = next(iter(PAYLOADS))
        destination = self.root / relative
        destination.unlink()
        os.link(self.source / relative, destination)
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.verify_recovery_payload_locations(self.root)

    def test_parent_directory_symlink_cannot_escape_worktree(self):
        relative = next(iter(PAYLOADS))
        directory = (self.root / relative).parent
        (self.root / relative).unlink()
        directory.rmdir()
        directory.symlink_to((self.source / relative).parent, target_is_directory=True)
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.verify_recovery_payload_locations(self.root)

    def test_nonregular_destination_is_rejected(self):
        destination = self.root / next(iter(PAYLOADS))
        destination.unlink()
        destination.mkdir()
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.verify_recovery_payload_locations(self.root)


class RecoveryReceiptTests(SyntheticRecoveryRoot):
    def test_recovery_receipt_is_exclusive_fsynced_and_separate(self):
        original = self.put(ex.EVIDENCE + "/" + ex.RECEIPT, {"original": "preserve"})
        with patch.object(ex.os, "fsync", wraps=ex.os.fsync) as sync:
            ex.emit_recovery_1(self.root, ex.RECEIPT, {"recovery": "synthetic"})
        self.assertEqual(sync.call_count, 2)
        path = self.root / ex.RECOVERY_EVIDENCE / ex.RECEIPT
        before = path.read_bytes()
        with self.assertRaises(FileExistsError):
            ex.emit_recovery_1(self.root, ex.RECEIPT, {"overwrite": True})
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual((self.root / ex.EVIDENCE / ex.RECEIPT).read_bytes(), original)

    def test_recovery_writer_cannot_escape_to_original_namespace(self):
        for name in ("../STUDY3_EXECUTION/" + ex.RECEIPT, "../../original.json", "/absolute.json"):
            with self.subTest(name=name), self.assertRaises(ex.Study3ExecutionError):
                ex.emit_recovery_1(self.root, name, {})
        self.assertFalse((self.root / ex.EVIDENCE).exists())

    def test_original_run_remains_consumed_and_never_uses_recovery_authority(self):
        self.put(ex.AUTHORITY, json.loads((ROOT / ex.AUTHORITY).read_text()))
        self.put(ex.SCIENCE_DECISION, {})
        original = self.put(ex.EVIDENCE + "/" + ex.RECEIPT, {"original": "consumed"})
        with patch.object(ex, "git", side_effect=AssertionError("Git reached after consumed")), \
             patch.object(ex, "emit_recovery_1", side_effect=AssertionError("recovery writer reached")), \
             self.assertRaisesRegex(ex.Study3ExecutionError, "consumed"):
            ex.run(self.root)
        self.assertEqual((self.root / ex.EVIDENCE / ex.RECEIPT).read_bytes(), original)
        self.assertFalse((self.root / ex.RECOVERY_EVIDENCE).exists())


class OriginalAttemptEvidenceTests(SyntheticRecoveryRoot):
    """Generated consumed-attempt evidence; no real attempt files are read."""

    def setUp(self):
        super().setUp()
        self.failure = "FileNotFoundError: [Errno 2] No such file or directory: 'derived'"
        self.counts = {"SCIENTIFIC_STUDY3_RUNS": 1, "FEATURE_EXTRACTIONS_STARTED": 0,
            "FEATURE_EXTRACTIONS_COMPLETED": 0, "LBP_ROWS": 0, "RF_FITS": 0,
            "CNN1D_FITS": 0, "SPATIOTEMPORAL_CNN_FITS": 0, "METADATA_LOGREG_FITS": 0,
            "ACQUISITION_ONLY_FITS": 0, **dict.fromkeys(ex.ZERO_COUNTERS, 0)}
        self.ledger = {"fit_budget": 28, "started": [], "completed": [],
                       "distinct_fits_started": 0, "distinct_fits_completed": 0}
        self.documents = {name: {} for name in ex.OUTPUT_NAMES
                          if name not in {"TEMPORAL_SELECTION_LEDGER.json", "post-run-hashes.sha256"}}
        self.documents[ex.RECEIPT] = {"attempt": 1, "scientific_receipt_created": True,
            "method_freeze_sha": ORIGINAL_FREEZE, "head_sha": ORIGINAL_FREEZE,
            "receipt_precedes_experimental_payload": True}
        self.receipt_sha = hashlib.sha256(ex.encode_evidence(self.documents[ex.RECEIPT])).hexdigest()
        self.documents["terminal-state.json"] = {"STUDY3": "BLOCKED_PARTIAL_EXECUTION",
            "STATE": "CLOSED_CONSUMED", "retry_authorized": False, "adaptive_model_search": False,
            "DISTINCT_FITS": 0, "method_freeze_sha": ORIGINAL_FREEZE,
            "receipt_sha256": self.receipt_sha, **self.counts}
        self.documents["results.json"] = {"status": "BLOCKED_PARTIAL_EXECUTION",
            "failure": self.failure, "counts": deepcopy(self.counts), "fits": {},
            "acquisition_only": [], "contrasts": None, "method_freeze_sha": ORIGINAL_FREEZE,
            "receipt_sha256": self.receipt_sha}
        self.documents["FIT_LEDGER.json"] = deepcopy(self.ledger)
        audit_names = ("bytes_read", "rows_read", "rows_authenticated", "container_opens", "row_attempts",
                       "DEV_GROUPS_READ", "TEST_GROUPS_READ", "TRAIN_GOLD_ROWS_READ", "TRAIN_BG_ROWS_READ",
                       "TEST_CACHE_ROWS_READ", "TEST_FEATURES_COMPUTED", "EXPERIMENTAL_SOURCE_OPENS",
                       "full_container_hashes", "pixels_written", "FFMPEG_RUNS", "DEV_ROWS_READ",
                       "TEST_ROWS_READ", "ESM1_OPENS", "ESM2_OPENS", "ESM3_OPENS", "ESM4_OPENS",
                       "ESM5_OPENS", "ESM6_OPENS")
        self.documents["verification.json"] = {"status": "BLOCKED_PARTIAL_EXECUTION",
            "failure": self.failure, "fit_ledger": deepcopy(self.ledger),
            "io_audit": {**dict.fromkeys(audit_names, 0), "state": "FAILED_CONSUMED",
                         "all_descriptors_closed": True, "access_records": []}}
        self.documents["execution-report.md"] = "Synthetic consumed attempt fixture.\n"
        self.refresh_fixture()
        self.enterContext(patch.object(ex, "FAILED_RECEIPT_SHA256", self.receipt_sha))
        self.git_mock = self.enterContext(patch.object(ex, "git_bytes", side_effect=self.committed_fixture))

    def refresh_fixture(self):
        self.blobs = {}
        for name, value in self.documents.items():
            relative = ex.EVIDENCE + "/" + name
            self.blobs[relative] = self.put(relative, value)
        entries = []
        for name in sorted(self.documents):
            content = self.blobs[ex.EVIDENCE + "/" + name]
            entries.append(hashlib.sha256(content).hexdigest() + "  " + name + "\n")
        relative = ex.EVIDENCE + "/post-run-hashes.sha256"
        self.blobs[relative] = self.put(relative, "".join(entries))

    def committed_fixture(self, root, *arguments):
        self.assertEqual(root, self.root)
        self.assertEqual(arguments[0], "show")
        revision, relative = arguments[1].split(":", 1)
        self.assertEqual(revision, ex.ATTEMPT1_EVIDENCE_CHECKPOINT_SHA)
        return self.blobs[relative]

    def test_original_pre_payload_failure_is_admissible_without_science(self):
        self.assertIsInstance(ex.validate_original_attempt(self.root), dict)
        self.assertEqual(len(self.blobs), 15)

    def test_original_receipt_is_required(self):
        (self.root / ex.EVIDENCE / ex.RECEIPT).unlink()
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.validate_original_attempt(self.root)

    def test_original_receipt_digest_is_exact(self):
        with patch.object(ex, "FAILED_RECEIPT_SHA256", "f" * 64), self.assertRaises(ex.Study3ExecutionError):
            ex.validate_original_attempt(self.root)

    def test_original_terminal_is_required(self):
        (self.root / ex.EVIDENCE / "terminal-state.json").unlink()
        with self.assertRaises((OSError, ex.Study3ExecutionError)):
            ex.validate_original_attempt(self.root)

    def test_original_terminal_must_remain_closed(self):
        self.documents["terminal-state.json"]["STATE"] = "ACTIVE"
        self.refresh_fixture()
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_original_attempt(self.root)

    def test_original_nonzero_fit_blocks_recovery(self):
        self.documents["terminal-state.json"]["DISTINCT_FITS"] = 1
        self.refresh_fixture()
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_original_attempt(self.root)

    def test_original_nonzero_binary_read_blocks_recovery(self):
        self.documents["verification.json"]["io_audit"]["bytes_read"] = 1
        self.refresh_fixture()
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_original_attempt(self.root)

    def test_original_nonzero_feature_extraction_blocks_recovery(self):
        self.documents["terminal-state.json"]["FEATURE_EXTRACTIONS_STARTED"] = 1
        self.refresh_fixture()
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_original_attempt(self.root)

    def test_original_missing_payload_cause_cannot_be_replaced_by_model_failure(self):
        self.documents["results.json"]["failure"] = "ValueError: synthetic CNN failure"
        self.documents["verification.json"]["failure"] = "ValueError: synthetic CNN failure"
        self.refresh_fixture()
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_original_attempt(self.root)

    def test_original_committed_evidence_cannot_be_rewritten_and_resigned(self):
        original = dict(self.blobs)
        self.documents["execution-report.md"] = "Changed synthetic history.\n"
        self.refresh_fixture()
        self.git_mock.side_effect = lambda root, *args: original[args[1].split(":", 1)[1]]
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_original_attempt(self.root)

    def test_original_checksum_manifest_must_cover_every_preserved_artifact(self):
        relative = ex.EVIDENCE + "/post-run-hashes.sha256"
        content = self.blobs[relative].decode().splitlines(keepends=True)
        self.blobs[relative] = self.put(relative, "".join(content[:-1]))
        with self.assertRaises(ex.Study3ExecutionError):
            ex.validate_original_attempt(self.root)


class RecoveryPreflightTests(SyntheticRecoveryRoot):
    """Real admission logic against generated text and mocked Git custody."""

    def setUp(self):
        super().setUp()
        self.enterContext(patch.object(ex, "WORKTREE_ROOT", self.root))
        self.enterContext(patch.object(ex, "RECOVERY_PAYLOADS", dict(PAYLOADS)))
        for relative, size in PAYLOADS.items():
            self.put(relative, b"s" * size)
        self.proof, self.manifest, self.design = controller_fixture()
        self.design["historical_fold_sha256"] = "a" * 64
        self.blobs = {path: b"synthetic frozen text\n"
                      for path in ex.RECOVERY_FREEZE_FILES + ex.INHERITED_FILES}
        self.blobs[ex.RECOVERY_CONTRACT_PATH] = ex.encode_evidence(ex.recovery_contract())
        self.blobs["configs/study3/data-contract.json"] = ex.encode_evidence({"fixture": "synthetic"})
        self.blobs["constraints-ti3c-cnn.txt"] = b"synthetic-package==1\n"
        self.contract_hashes = {path: ex.digest(value) for path, value in self.blobs.items()}
        decision = {"grant": ex.recovery_science_grant(HEAD, self.contract_hashes,
                    ex.ATTEMPT1_EVIDENCE_CHECKPOINT_SHA), "author_decision_sha256": "e" * 64}
        self.blobs[ex.RECOVERY_AUTHORITY] = self.put(ex.RECOVERY_AUTHORITY, decision)
        proof = ci_fixture()
        proof["head_sha"] = HEAD
        for run in proof["runs"]:
            run["headSha"] = HEAD
        self.blobs[ex.RECOVERY_CI_PROOF] = ex.encode_evidence(proof)
        self.blobs["artifacts/evidence/STUDY2_C_BENCHMARK/terminal-state.json"] = ex.encode_evidence(
            {"STATE": "CLOSED_CONSUMED", "TEST_STATE": "CONSUMED"})
        handoff = self.put("synthetic-handoff.md", "Generated handoff fixture.\n")
        self.enterContext(patch.object(ex, "HANDOFF", str(self.root / "synthetic-handoff.md")))
        self.enterContext(patch.object(ex, "HANDOFF_SHA", ex.digest(handoff)))
        self.enterContext(patch.object(ex, "read_text", side_effect=lambda root, path: self.blobs[path]))
        self.git_mock = self.enterContext(patch.object(ex, "git", side_effect=self.git_fixture))
        self.enterContext(patch.object(ex, "git_bytes", side_effect=self.git_blob))
        self.enterContext(patch.object(ex.importlib.metadata, "version", return_value="1"))
        self.original = self.enterContext(patch.object(ex, "validate_original_attempt",
            return_value={"original_attempt_preserved": True, "original_fits": 0}))
        self.method = self.enterContext(patch.object(ex, "verify_original_method",
            return_value={path: "a" * 64 for path in FROZEN_SCIENTIFIC_FILES}))
        self.inputs = self.enterContext(patch.object(ex, "authenticate_inputs",
            return_value=(self.manifest, self.design)))

    def git_fixture(self, root, *arguments):
        self.assertEqual(root, self.root)
        if arguments == ("rev-parse", "HEAD"):
            return HEAD
        if arguments == ("branch", "--show-current"):
            return ex.BRANCH
        if arguments == ("rev-list", "--parents", "-n", "1", HEAD):
            return HEAD + " " + ex.ATTEMPT1_EVIDENCE_CHECKPOINT_SHA
        if arguments == ("rev-list", "--parents", "-n", "1", ex.ATTEMPT1_EVIDENCE_CHECKPOINT_SHA):
            return ex.ATTEMPT1_EVIDENCE_CHECKPOINT_SHA + " " + ORIGINAL_FREEZE
        if arguments == ("status", "--porcelain", "--untracked-files=no"):
            return ""
        if arguments[:3] == ("diff", "--name-status", "--no-renames"):
            return "\n".join(["A\t" + name for name in ex.RECOVERY_NEW_FILES]
                             + ["M\t" + name for name in ex.RECOVERY_CHANGED_FILES])
        raise AssertionError("Unexpected synthetic Git request: " + str(arguments))

    def git_blob(self, root, *arguments):
        self.assertEqual(root, self.root)
        self.assertEqual(arguments[0], "show")
        revision, relative = arguments[1].split(":", 1)
        self.assertEqual(revision, HEAD)
        return self.blobs[relative]

    def test_successful_synthetic_preflight_returns_bound_proof_without_receipt(self):
        proof, manifest, design = ex.preflight_recovery_1(self.root)
        self.assertEqual(proof["status"], "PASS")
        self.assertEqual(proof["method_freeze_sha"], ORIGINAL_FREEZE)
        self.assertEqual(proof["recovery_method_freeze_sha"], HEAD)
        self.assertFalse(proof["scientific_receipt_created"])
        self.assertEqual(proof["payload_locations"]["status"], "PASS")
        self.assertIs(manifest, self.manifest)
        self.assertIs(design, self.design)
        self.assertFalse((self.root / ex.RECOVERY_EVIDENCE).exists())

    def test_existing_recovery_receipt_blocks_before_git_or_original_evidence(self):
        self.put(ex.RECOVERY_EVIDENCE + "/" + ex.RECEIPT, {})
        with self.assertRaisesRegex(ex.Study3ExecutionError, "consumed"):
            ex.preflight_recovery_1(self.root)
        self.git_mock.assert_not_called()
        self.original.assert_not_called()

    def test_existing_recovery_results_blocks_before_git(self):
        self.put(ex.RECOVERY_EVIDENCE + "/results.json", {})
        with self.assertRaisesRegex(ex.Study3ExecutionError, "consumed"):
            ex.preflight_recovery_1(self.root)
        self.git_mock.assert_not_called()

    def test_existing_recovery_terminal_blocks_before_git(self):
        self.put(ex.RECOVERY_EVIDENCE + "/terminal-state.json", {})
        with self.assertRaisesRegex(ex.Study3ExecutionError, "consumed"):
            ex.preflight_recovery_1(self.root)
        self.git_mock.assert_not_called()

    def test_missing_new_author_decision_cannot_reuse_old_local_authority(self):
        (self.root / ex.RECOVERY_AUTHORITY).unlink()
        self.put(ex.SCIENCE_DECISION, {"grant": "consumed original"})
        with self.assertRaisesRegex(ex.Study3ExecutionError, "new recovery author decision absent"):
            ex.preflight_recovery_1(self.root)
        self.git_mock.assert_not_called()

    def test_payload_location_failure_precedes_recovery_receipt_and_reader(self):
        from snbi_fragmentation import study3_io
        (self.root / next(iter(PAYLOADS))).unlink()
        with patch.object(ex, "emit_recovery_1") as writer, \
             patch.object(study3_io, "Study3TrainAccess") as reader:
            with self.assertRaises((OSError, ex.Study3ExecutionError)):
                ex.run_recovery_1(self.root)
        writer.assert_not_called()
        reader.assert_not_called()
        self.inputs.assert_not_called()
        self.assertFalse((self.root / ex.RECOVERY_EVIDENCE).exists())

    def test_exact_new_sha_ci_proof_is_required(self):
        proof = json.loads(self.blobs[ex.RECOVERY_CI_PROOF])
        proof["head_sha"] = ORIGINAL_FREEZE
        self.blobs[ex.RECOVERY_CI_PROOF] = ex.encode_evidence(proof)
        with self.assertRaisesRegex(ex.Study3ExecutionError, "exact-SHA CI"):
            ex.preflight_recovery_1(self.root)

    def test_original_test_state_must_remain_consumed(self):
        self.blobs["artifacts/evidence/STUDY2_C_BENCHMARK/terminal-state.json"] = ex.encode_evidence(
            {"STATE": "CLOSED_CONSUMED", "TEST_STATE": "AVAILABLE"})
        with self.assertRaisesRegex(ex.Study3ExecutionError, "TEST must remain consumed"):
            ex.preflight_recovery_1(self.root)


class RecoveryScienceDecisionTests(unittest.TestCase):
    def decision(self):
        return {"grant": ex.recovery_science_grant(HEAD, {}, ex.ATTEMPT1_EVIDENCE_CHECKPOINT_SHA),
                "author_decision_sha256": "e" * 64}

    def validate(self, decision):
        return ex.validate_recovery_science_decision(decision, HEAD, {}, ex.ATTEMPT1_EVIDENCE_CHECKPOINT_SHA)

    def test_future_schema_requires_fresh_provenance_bound_to_new_freeze(self):
        self.assertEqual(len(self.validate(self.decision())), 64)

    def test_consumed_original_author_digest_is_not_reusable(self):
        decision = self.decision()
        decision["author_decision_sha256"] = ex.CONSUMED_AUTHOR_DECISION_SHA256
        with self.assertRaises(ex.Study3ExecutionError):
            self.validate(decision)

    def test_recovery_cannot_grant_forbidden_access_or_change_budget(self):
        for field, value in (("development_access", True), ("test_access", True), ("silver_access", True),
                             ("video_access", True), ("distinct_fits", 29), ("retries", 1),
                             ("recovery_method_freeze_sha", ORIGINAL_FREEZE),
                             ("scientific_execution_authorized", "true")):
            decision = self.decision()
            decision["grant"][field] = value
            with self.subTest(field=field), self.assertRaises(ex.Study3ExecutionError):
                self.validate(decision)


class FrozenScientificMethodTests(unittest.TestCase):
    """Compare approved code/config text with the immutable method Git blob."""

    @classmethod
    def setUpClass(cls):
        cls.frozen = {}
        names = FROZEN_SCIENTIFIC_FILES + ("src/snbi_fragmentation/study3_execution.py",)
        for name in names:
            cls.frozen[name] = subprocess.run(
                ["git", "--no-optional-locks", "show", ORIGINAL_FREEZE + ":" + name],
                cwd=ROOT, env=SAFE_GIT_ENV, check=True, capture_output=True, timeout=30).stdout
        cls.old_tree = ast.parse(cls.frozen["src/snbi_fragmentation/study3_execution.py"])
        cls.current_tree = ast.parse((ROOT / "src/snbi_fragmentation/study3_execution.py").read_text())

    @staticmethod
    def function(tree, name):
        return next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)

    def test_exact_thirteen_scientific_files_are_byte_identical_to_original_freeze(self):
        self.assertEqual(set(ex.RECOVERY_SCIENTIFIC_FILES), set(FROZEN_SCIENTIFIC_FILES))
        self.assertEqual(len(FROZEN_SCIENTIFIC_FILES), 13)
        for name in FROZEN_SCIENTIFIC_FILES:
            with self.subTest(path=name):
                self.assertFalse((ROOT / name).is_symlink())
                self.assertEqual((ROOT / name).read_bytes(), self.frozen[name])

    def test_original_preflight_run_and_scientific_result_validation_are_unchanged_ast(self):
        for name in ("preflight", "run", "_check_audit", "validate_results"):
            with self.subTest(function=name):
                self.assertEqual(ast.dump(self.function(self.old_tree, name), include_attributes=False),
                                 ast.dump(self.function(self.current_tree, name), include_attributes=False))

    def test_shared_scientific_body_matches_original_ast_except_evidence_writer_name(self):
        old = self.function(self.old_tree, "_execute")
        current = self.function(self.current_tree, "_execute_authorized")
        old_science = deepcopy(next(node for node in old.body if isinstance(node, ast.Try)))
        new_science = deepcopy(next(node for node in current.body if isinstance(node, ast.Try)))

        class EvidenceWriterName(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id in {"emit", "writer"}:
                    node.id = "BOUND_EVIDENCE_WRITER"
                return node

        normalizer = EvidenceWriterName()
        self.assertEqual(ast.dump(normalizer.visit(old_science), include_attributes=False),
                         ast.dump(normalizer.visit(new_science), include_attributes=False))

    def test_frozen_fit_conditions_population_folds_and_budget_are_identical(self):
        from snbi_fragmentation import study3_design
        from test_study3_design import synthetic_population
        rows, folds = synthetic_population()
        with patch.object(study3_design, "EXPECTED_FOLD_SHA", study3_design.json_sha(folds)):
            design = study3_design.build_study3_design(rows, folds)
        contract = json.loads(self.frozen["configs/study3/fit-budget.json"])
        data = json.loads(self.frozen["configs/study3/data-contract.json"])
        self.assertEqual(len(rows), data["rows"])
        self.assertEqual(len(design["groups"]), data["total_groups"])
        self.assertEqual(design["cv_fold_by_group"], folds)
        self.assertEqual(design["rows"], rows)
        self.assertEqual([(s["condition"], s["fold"]) for s in design["fits"]],
                         [(condition, fold) for condition in contract["order"]
                          for fold in contract["fold_order"]])
        self.assertEqual(len(design["fits"]), 28)
        self.assertEqual(contract["TOTAL_DISTINCT_FITS"], 28)

    def test_frozen_cnn_architecture_params_hyperparameters_rf_and_t8_are_unchanged(self):
        from snbi_fragmentation import study3_cnn, study3_models
        cnn = json.loads(self.frozen["configs/study3/cnn-contract.json"])
        model = json.loads(self.frozen["configs/study3/model-contract.json"])
        representation = json.loads(self.frozen["configs/study3/representation-contract.json"])
        for name, expected in (("TEMPORAL_CNN1D_LBP20", 5122), ("SPATIOTEMPORAL_CNN_SMALL", 2138)):
            self.assertEqual(cnn[name]["parameters"], expected)
            self.assertEqual(study3_cnn.CONFIGS[name]["parameter_count"], expected)
            self.assertEqual(study3_cnn.CONFIGS[name]["batch_size"], cnn[name]["batch_size"])
            self.assertEqual(study3_cnn.CONFIGS[name]["input_shape"], cnn[name]["input_shape"])
        for key in ("seed", "epochs", "learning_rate"):
            self.assertEqual(study3_cnn.TRAINING[key], cnn[key])
        self.assertEqual(study3_cnn.TRAINING["seed"], 42)
        self.assertEqual(study3_cnn.TRAINING["epochs"], 30)
        self.assertTrue(ex.exact(study3_models.RF_PARAMETERS, model["rf_parameters"]))
        self.assertEqual(representation["timepoints"], 8)
        self.assertEqual(representation["representations"]["TRAJECTORY_Q2575_LBP60"]["method"], "linear")

    def test_frozen_gmba_contrasts_and_descriptors_are_unchanged(self):
        from snbi_fragmentation import study3_metrics
        evaluation = json.loads(self.frozen["configs/study3/evaluation-contract.json"])
        self.assertEqual(evaluation["primary_metric"], "GROUP_MACRO_BALANCED_ACCURACY")
        self.assertEqual(set(study3_metrics.CONTRASTS),
                         set(evaluation["primary_contrasts"] + evaluation["secondary_contrasts"]))
        self.assertEqual(len(study3_metrics.CONTRASTS), 7)
        self.assertFalse(evaluation["p_values"])
        self.assertEqual(study3_metrics.describe_delta([0, 0, 0, 0])["descriptor"], "NON_POSITIVE_INTERNAL")

    def test_modified_scientific_text_is_rejected_by_recovery_admission(self):
        with patch.object(ex, "read_text", return_value=b"changed synthetic method"), \
             patch.object(ex, "git_bytes", return_value=b"frozen synthetic method"), \
             self.assertRaisesRegex(ex.Study3ExecutionError, "scientific method changed"):
            ex.verify_original_method(Path("synthetic-unused-root"))


class RecoverySharedCoreDispatchTests(SyntheticRecoveryRoot):
    def test_both_public_entries_use_the_same_core_with_only_closed_namespace_dispatch(self):
        marker = object()
        with patch.object(ex, "_execute_authorized", return_value=marker) as shared:
            self.assertIs(ex._execute(self.root), marker)
            self.assertIs(ex.run_recovery_1(self.root), marker)
        self.assertEqual([call.args for call in shared.call_args_list],
                         [(self.root, ex.EVIDENCE), (self.root, ex.RECOVERY_EVIDENCE)])

    def test_unknown_namespace_denied_before_preflight_or_writer(self):
        with patch.object(ex, "preflight") as original, patch.object(ex, "preflight_recovery_1") as recovery, \
             patch.object(ex, "emit_recovery_1") as writer:
            with self.assertRaises(ex.Study3ExecutionError):
                ex._execute_authorized(self.root, "artifacts/evidence/UNAUTHORIZED_RETRY")
        original.assert_not_called()
        recovery.assert_not_called()
        writer.assert_not_called()

    def test_core_has_no_caller_supplied_proof_or_authority_bypass(self):
        import inspect
        self.assertEqual(list(inspect.signature(ex._execute_authorized).parameters), ["root", "evidence_namespace"])

    def test_twenty_ninth_fit_is_denied_with_same_frozen_schedule(self):
        from snbi_fragmentation.study3_design import FitBudget
        _, _, design = controller_fixture()
        budget = FitBudget(design["fits"])
        for spec in design["fits"]:
            budget.start(spec["fit_id"])
            budget.complete(spec["fit_id"])
        with self.assertRaisesRegex(ValueError, "29"):
            budget.start("UNAUTHORIZED_FIT_29")
        self.assertEqual(budget.snapshot()["distinct_fits_completed"], 28)

    def test_recovery_runner_references_only_its_new_entrypoint(self):
        tree = ast.parse((ROOT / "scripts/run_study3_recovery_1.py").read_text())
        calls = [node.func.id for node in ast.walk(tree)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
        self.assertIn("run_recovery_1", calls)
        self.assertNotIn("run", calls)


@unittest.skipUnless(NUMPY, "NumPy required by the strict Study3 scientific dependency profile")
class RecoveryControllerTests(unittest.TestCase):
    """Reuse original synthetic model callbacks; no actual model is fitted."""

    def setUp(self):
        self.fixture = original_test_fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.calls = self.fixture.calls
        self.original_bytes = {}
        for name in ex.ORIGINAL_ATTEMPT_NAMES:
            relative = ex.EVIDENCE + "/" + name
            self.fixture.put(relative, {"preserve_original_synthetic_artifact": name})
            self.original_bytes[name] = (self.root / relative).read_bytes()
        proof = self.fixture.proof
        proof.update(recovery_id=ex.RECOVERY_ID, method_freeze_sha=ORIGINAL_FREEZE,
                     original_method_freeze_sha=ORIGINAL_FREEZE, recovery_method_freeze_sha=HEAD,
                     original_receipt_sha256=ORIGINAL_RECEIPT, head_sha=HEAD,
                     attempt1_evidence_checkpoint_sha=ex.ATTEMPT1_EVIDENCE_CHECKPOINT_SHA)

        def synthetic_preflight(root):
            self.assertEqual(root, self.root)
            if (root / ex.RECOVERY_EVIDENCE / ex.RECEIPT).exists():
                raise ex.Study3ExecutionError("synthetic recovery authority consumed")
            return proof, self.fixture.manifest, self.fixture.design

        self.enterContext(patch.object(ex, "preflight_recovery_1", side_effect=synthetic_preflight))
        from snbi_fragmentation import study3_io
        original_reader = study3_io.Study3TrainAccess
        owner = self

        class RecoveryReader(original_reader):
            def __init__(self, root, *args, **kwargs):
                owner.assertTrue((root / ex.RECOVERY_EVIDENCE / ex.RECEIPT).is_file())
                super().__init__(root, *args, **kwargs)

        self.enterContext(patch.object(study3_io, "Study3TrainAccess", RecoveryReader))

    def result(self):
        return json.loads((self.root / ex.RECOVERY_EVIDENCE / "results.json").read_text())

    def test_recovery_completes_exact_same_28_conditions_once_in_separate_namespace(self):
        terminal = ex.run_recovery_1(self.root)
        self.assertEqual(terminal["STUDY3"], "PASS", self.result()["failure"])
        self.assertEqual(terminal["DISTINCT_FITS"], 28)
        self.assertEqual([terminal[name] for name in
                          ("RF_FITS", "CNN1D_FITS", "SPATIOTEMPORAL_CNN_FITS", "METADATA_LOGREG_FITS")],
                         [16, 4, 4, 4])
        self.assertEqual(list(self.result()["fits"]), [spec["fit_id"] for spec in self.fixture.design["fits"]])
        self.assertEqual([self.calls[name] for name in ("load", "features", "fit_attempt")], [1, 1, 28])
        self.assertFalse(terminal["retry_authorized"])
        for name, content in self.original_bytes.items():
            self.assertEqual((self.root / ex.EVIDENCE / name).read_bytes(), content)

    def test_second_recovery_invocation_is_denied_and_all_existing_evidence_is_preserved(self):
        ex.run_recovery_1(self.root)
        paths = [self.root / ex.RECOVERY_EVIDENCE / name for name in ex.OUTPUT_NAMES]
        before = [path.read_bytes() for path in paths]
        with self.assertRaisesRegex(ex.Study3ExecutionError, "consumed"):
            ex.run_recovery_1(self.root)
        self.assertEqual([path.read_bytes() for path in paths], before)
        self.assertEqual(self.calls["load"], 1)
        self.assertEqual(self.calls["fit_attempt"], 28)

    def test_recovery_partial_fit_is_consumed_without_changing_original_evidence(self):
        self.fixture.mode = "partial_fit"
        terminal = ex.run_recovery_1(self.root)
        self.assertEqual(terminal["STUDY3"], "BLOCKED_PARTIAL_EXECUTION")
        self.assertEqual(terminal["DISTINCT_FITS"], 0)
        self.assertEqual(self.calls["fit_attempt"], 1)
        ledger = json.loads((self.root / ex.RECOVERY_EVIDENCE / "FIT_LEDGER.json").read_text())
        self.assertEqual(ledger["distinct_fits_started"], 1)
        for name, content in self.original_bytes.items():
            self.assertEqual((self.root / ex.EVIDENCE / name).read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
