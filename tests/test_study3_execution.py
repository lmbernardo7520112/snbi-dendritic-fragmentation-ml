"""Synthetic controller/receipt contracts; real paths and fits never run."""
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from snbi_fragmentation import study3_execution as ex
from snbi_fragmentation.study3_design import FIT_CONDITIONS, FitBudget, group_trajectories
from snbi_fragmentation.study3_models import scaler_record
from snbi_fragmentation import study2d_io as historical_io

NUMPY = importlib.util.find_spec("numpy") is not None
ROOT = Path(__file__).absolute().parents[1]
HEAD = "b" * 40


class TemporaryRoot(unittest.TestCase):
    def setUp(self):
        parent = ROOT / ".bootstrap-test-tmp"
        parent.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="study3-execution-", dir=parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def put(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def result(self):
        return json.loads((self.root / ex.EVIDENCE / "results.json").read_text())


class AdmissionTests(TemporaryRoot):
    def test_recovery_gate_denies_before_git_manifest_receipt_or_reader(self):
        authority = json.loads((ROOT / ex.AUTHORITY).read_text())
        self.put(ex.AUTHORITY, authority)
        with patch.object(ex, "git") as git, patch.object(ex, "authenticate_inputs") as inputs, \
             patch.object(ex, "emit") as emitted:
            with self.assertRaisesRegex(ex.Study3ExecutionError, "grants no science"):
                ex.run(self.root)
        git.assert_not_called()
        inputs.assert_not_called()
        emitted.assert_not_called()
        self.assertFalse((self.root / ex.EVIDENCE).exists())

    def test_internal_controller_has_the_same_authority_gate(self):
        self.put(ex.AUTHORITY, json.loads((ROOT / ex.AUTHORITY).read_text()))
        with patch.object(ex, "emit") as emitted, self.assertRaises(ex.Study3ExecutionError):
            ex._execute(self.root)
        emitted.assert_not_called()

    def test_noncanonical_truthy_current_authority_denied(self):
        authority = json.loads((ROOT / ex.AUTHORITY).read_text())
        authority["scientific_execution_authorized"] = "false"
        self.put(ex.AUTHORITY, authority)
        with self.assertRaisesRegex(ex.Study3ExecutionError, "remain closed"):
            ex._current_preparation_authority(self.root)

    def test_recovery_denial_never_creates_future_grant_or_output_namespace(self):
        self.put(ex.AUTHORITY, json.loads((ROOT / ex.AUTHORITY).read_text()))
        with self.assertRaises(ex.Study3ExecutionError):
            ex._current_preparation_authority(self.root)
        self.assertFalse((self.root / ex.SCIENCE_DECISION).exists())
        self.assertFalse((self.root / ex.EVIDENCE).exists())

    def test_unknown_missing_or_retyped_preparation_fields_fail_closed(self):
        original = json.loads((ROOT / ex.AUTHORITY).read_text())
        variants = [dict(original, extra=True), dict(original, retries=False)]
        missing = deepcopy(original)
        missing.pop("scientific_execution_authorized")
        variants.append(missing)
        for value in variants:
            self.put(ex.AUTHORITY, value)
            with self.assertRaisesRegex(ex.Study3ExecutionError, "remain closed"):
                ex._current_preparation_authority(self.root)

    def test_unknown_documentary_path_denied_before_path_conversion(self):
        class Hostile:
            def __fspath__(self):
                raise AssertionError("root touched")
        for name in ("data/derived/study2c/cachetest.bin", "ESM1.mp4", "../outside.json"):
            with self.subTest(name=name), self.assertRaises(ex.Study3ExecutionError):
                ex.read_text(Hostile(), name)

    def test_science_grant_cannot_be_inferred_from_preparation_or_truthy_text(self):
        for grant in ({}, {"grant": {}}, {"grant": {"scientific_execution_authorized": "true"},
                      "author_decision_sha256": "a" * 64},
                      {"grant": {}, "author_decision_sha256": "a" * 64, "extra": True}):
            with self.subTest(grant=grant), self.assertRaises(ex.Study3ExecutionError):
                ex.validate_science_decision(grant, HEAD, {})


class ReceiptTests(TemporaryRoot):
    def test_exclusive_fsynced_receipt_and_duplicate_denial(self):
        real_fsync = ex.os.fsync
        with patch.object(ex.os, "fsync", wraps=real_fsync) as fsync:
            digest = ex.emit(self.root, ex.RECEIPT, {"synthetic": True})
        self.assertEqual(len(digest), 64)
        self.assertEqual(fsync.call_count, 2)
        before = (self.root / ex.EVIDENCE / ex.RECEIPT).read_bytes()
        with self.assertRaises(FileExistsError):
            ex.emit(self.root, ex.RECEIPT, {"overwrite": True})
        self.assertEqual((self.root / ex.EVIDENCE / ex.RECEIPT).read_bytes(), before)

    def test_unknown_output_is_denied(self):
        with self.assertRaises(ex.Study3ExecutionError):
            ex.emit(self.root, "../escape.json", {})
        self.assertFalse((self.root / ex.EVIDENCE).exists())

    def test_symlink_output_is_denied(self):
        path = self.root / ex.EVIDENCE
        path.mkdir(parents=True)
        target = self.root / "synthetic-target"
        target.write_text("unchanged")
        (path / ex.RECEIPT).symlink_to(target)
        with self.assertRaises(ex.Study3ExecutionError):
            ex.emit(self.root, ex.RECEIPT, {})
        self.assertEqual(target.read_text(), "unchanged")


def ci_fixture():
    return {"head_sha": HEAD, "runs": [{"headSha": HEAD, "status": "completed", "conclusion": "success",
        "jobs": [{"name": name, "status": "completed", "conclusion": "success",
                  "steps": [{"status": "completed", "conclusion": "success"}]}
                 for name in sorted(ex.REQUIRED_JOBS)]}],
        "study3_synthetic": {"status": "PASS", "tests": 10, "passes": 10, "skips": 0,
            "failures": 0, "errors": 0, "expected_failures": 0, "unexpected_successes": 0}}


class CIProofTests(unittest.TestCase):
    def test_all_exact_sha_jobs_and_zero_skips_required(self):
        self.assertEqual(set(ex.verify_ci(ci_fixture(), HEAD)), ex.REQUIRED_JOBS)

    def test_wrong_sha_failed_pending_missing_or_skipped_denied(self):
        mutations = [lambda p: p.update(head_sha="c" * 40),
            lambda p: p["runs"][0].update(status="in_progress"),
            lambda p: p["runs"][0].update(conclusion="failure"),
            lambda p: p["runs"][0]["jobs"].pop(),
            lambda p: p["runs"][0]["jobs"][0]["steps"][0].update(conclusion="skipped"),
            lambda p: p["study3_synthetic"].update(skips=1),
            lambda p: p["study3_synthetic"].update(skips=False)]
        for mutate in mutations:
            value = ci_fixture()
            mutate(value)
            with self.assertRaises(ex.Study3ExecutionError):
                ex.verify_ci(value, HEAD)


def controller_fixture():
    rows = []
    for fold in range(4):
        for acq in ("bottom_up_anti_parallel", "top_down_parallel"):
            for label in (0, 1):
                i = len(rows)
                payload = bytes(8450)
                hashes = {"pair_sha256": hashlib.sha256(payload).hexdigest(),
                    "structural_patch_sha256": hashlib.sha256(payload[:4225]).hexdigest(),
                    "solutal_patch_sha256": hashlib.sha256(payload[4225:]).hexdigest()}
                path = historical_io.POSITIVE if label else historical_io.BACKGROUND
                row = {"sample_id": f"synthetic-row-{i:02}", "group_id": f"synthetic-group-{i:02}",
                    "acquisition_id": acq, "split": "TRAIN", "tier": "GOLD" if label else "BACKGROUND",
                    "kind": "positive" if label else "background", "label": label,
                    "frame_index": i, "cv_fold": fold,
                    "storage": {"path": path, "row_index": i, "offset": i * 8450,
                        "shape": [2, 65, 65], "dtype": "uint8", "expected_file_bytes": historical_io.FILES[path], **hashes}}
                if label:
                    row.update(positive_row_index=i, **hashes)
                rows.append(row)
    groups = group_trajectories(rows)
    specs = [{"fit_id": f"{condition}-f{fold}", "condition": condition, "fold": fold,
              "training_group_ids": [str(g.group_id) for g in groups if g.cv_fold != fold],
              "validation_group_ids": [str(g.group_id) for g in groups if g.cv_fold == fold]}
             for condition in FIT_CONDITIONS for fold in range(4)]
    design = {"rows": rows, "group_ids": [str(g.group_id) for g in groups], "fits": specs,
        "groups": [{"group_id": str(g.group_id), "label": g.label, "acquisition_id": str(g.acquisition_id),
                    "cv_fold": int(g.cv_fold)} for g in groups],
        "population_sha256": ex.json_hash(rows)}
    proof = {"status": "PASS", "method_freeze_sha": HEAD, "head_sha": HEAD,
             "dependencies": {"fixture": "synthetic"}, "scientific_receipt_created": False}
    return proof, {"rows": rows}, design


@unittest.skipUnless(NUMPY, "NumPy required by strict Study3 dependency profile")
class ControllerTests(TemporaryRoot):
    def setUp(self):
        super().setUp()
        import numpy as np
        from snbi_fragmentation import study3_io, study3_models, study3_cnn, study2d_models
        self.proof, self.manifest, self.design = controller_fixture()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.mode = "success"
        self.calls = CounterLike()
        owner = self

        class Reader:
            def __init__(self, root, rows, grant, audit):
                owner.calls["reader"] += 1
                owner.assertTrue((root / ex.EVIDENCE / ex.RECEIPT).is_file())
                self.rows, self.grant, self.audit = rows, grant, audit

            def load(self):
                self.grant("LOAD_TRAIN_ROWS", self.rows)
                owner.calls["load"] += 1
                if owner.mode == "io_failure":
                    raise ValueError("synthetic read refusal")
                self.audit.update(rows_read=len(self.rows), rows_authenticated=len(self.rows),
                    bytes_read=len(self.rows) * 8450,
                    **dict.fromkeys([*ex.ZERO_COUNTERS, "EXPERIMENTAL_SOURCE_OPENS", "full_container_hashes"], 0))
                if owner.mode == "bad_firewall":
                    self.audit["DEV_ROWS_READ"] = 1
                return np.zeros((len(self.rows), 2, 65, 65), dtype=np.uint8)

            def close(self):
                owner.calls["close"] += 1

        def features(values):
            owner.calls["features"] += 1
            return np.zeros((len(values), 20), dtype=np.float64)

        def fit(X, groups, condition, *, fold, on_event):
            owner.calls["fit_attempt"] += 1
            if owner.mode == "before_fit":
                raise ValueError("synthetic validation before fit")
            event = {"family": "RF_REFERENCE" if condition in FIT_CONDITIONS[:4] else condition,
                     "condition": condition, "fold": fold}
            on_event({**event, "event": "FIT_START"})
            if owner.mode == "duplicate_start":
                on_event({**event, "event": "FIT_START"})
            if owner.mode == "partial_fit":
                raise ValueError("synthetic model failure")
            fitted = {"fit_calls": 1, "fold": fold, "condition": condition,
                "training_groups": [str(g.group_id) for g in groups], "training_only": True,
                "validation_used_for_training": False}
            if condition in study3_cnn.CONFIGS:
                for epoch in range(1, 31 if owner.mode != "missing_epoch" else 30):
                    on_event({**event, "event": "FIT_EPOCH_COMPLETE", "epoch": epoch,
                              "training_groups_seen": len(groups)})
                fitted.update(epochs=30, parameter_count=study3_cnn.CONFIGS[condition]["parameter_count"],
                    random_seed=42, device="cpu", threads=1, validation_evaluations_during_training=0)
            if condition in {"TEMPORAL_CNN1D_LBP20", "COVERAGE_METADATA_LOGREG"}:
                n = 20 if condition == "TEMPORAL_CNN1D_LBP20" else 4
                fitted["scaler"] = scaler_record([0.0] * n, [1.0] * n, groups)
            on_event({**event, "event": "FIT_COMPLETE"})
            if owner.mode == "bad_fit_schema":
                fitted["fit_calls"] = 2
            return object(), fitted

        def predict(model, values):
            owner.calls["predict"] += 1
            if owner.mode == "prediction_failure":
                raise ValueError("synthetic prediction failure")
            return {"predictions": [0] * len(values), "probabilities": [[1.0, 0.0]] * len(values), "classes": [0, 1]}

        self.preflight = self.stack.enter_context(patch.object(ex, "preflight",
            return_value=(self.proof, self.manifest, self.design)))
        self.stack.enter_context(patch.object(study3_io, "Study3TrainAccess", Reader))
        self.stack.enter_context(patch.object(study2d_models, "extract_lbp20", side_effect=features))
        self.stack.enter_context(patch.object(study3_models, "fit_reference", side_effect=fit))
        self.stack.enter_context(patch.object(study3_models, "fit_metadata",
            side_effect=lambda X, groups, **kwargs: fit(X, groups, "COVERAGE_METADATA_LOGREG", **kwargs)))
        self.stack.enter_context(patch.object(study3_cnn, "fit_cnn",
            side_effect=lambda kind, X, groups, **kwargs: fit(X, groups, kind, **kwargs)))
        for module, name in ((study3_models, "predict_reference"), (study3_models, "predict_metadata"),
                             (study3_cnn, "predict_cnn")):
            self.stack.enter_context(patch.object(module, name, side_effect=predict))

    def test_complete_controller_has_28_callbacks_one_read_and_one_extraction(self):
        terminal = ex.run(self.root)
        self.assertEqual(terminal["STUDY3"], "PASS", self.result()["failure"])
        self.assertEqual(terminal["DISTINCT_FITS"], 28)
        self.assertEqual([terminal[k] for k in ("RF_FITS", "CNN1D_FITS", "SPATIOTEMPORAL_CNN_FITS", "METADATA_LOGREG_FITS")], [16, 4, 4, 4])
        self.assertEqual([self.calls[k] for k in ("load", "features", "fit_attempt", "predict")], [1, 1, 28, 28])
        receipt = json.loads((self.root / ex.EVIDENCE / ex.RECEIPT).read_text())
        self.assertIs(receipt["scientific_receipt_created"], True)
        self.assertEqual(terminal["STUDY2_C_TEST_STATE"], "UNCHANGED_CONSUMED")
        self.assertFalse(terminal["retry_authorized"])
        self.assertEqual({p.name for p in (self.root / ex.EVIDENCE).iterdir()}, ex.OUTPUT_NAMES)
        hashes = (self.root / ex.EVIDENCE / "post-run-hashes.sha256").read_text()
        for name in (ex.RECEIPT, "TEMPORAL_SELECTION_LEDGER.json", "terminal-state.json"):
            value = (self.root / ex.EVIDENCE / name).read_bytes()
            self.assertIn(hashlib.sha256(value).hexdigest() + "  " + name, hashes)

    def test_preflight_failure_creates_no_receipt_or_reader(self):
        self.preflight.side_effect = ex.Study3ExecutionError("synthetic gate")
        with self.assertRaises(ex.Study3ExecutionError):
            ex.run(self.root)
        self.assertEqual(self.calls["reader"], 0)
        self.assertFalse((self.root / ex.EVIDENCE).exists())

    def test_io_failure_has_receipt_but_no_features_or_fit(self):
        self.mode = "io_failure"
        terminal = ex.run(self.root)
        self.assertEqual(terminal["STUDY3"], "BLOCKED_PARTIAL_EXECUTION")
        self.assertEqual((self.calls["features"], self.calls["fit_attempt"]), (0, 0))
        self.assertGreater(self.calls["close"], 0)

    def test_nonzero_firewall_blocks_features_and_preserves_counter(self):
        self.mode = "bad_firewall"
        terminal = ex.run(self.root)
        self.assertEqual(self.calls["features"], 0)
        self.assertEqual(terminal["DEV_ROWS_READ"], 1)

    def test_validation_failure_before_callback_is_not_a_fit(self):
        self.mode = "before_fit"
        terminal = ex.run(self.root)
        self.assertEqual(terminal["DISTINCT_FITS"], 0)
        ledger = json.loads((self.root / ex.EVIDENCE / "FIT_LEDGER.json").read_text())
        self.assertEqual(ledger["distinct_fits_started"], 0)

    def test_partial_fit_is_consumed_and_never_retried(self):
        self.mode = "partial_fit"
        terminal = ex.run(self.root)
        self.assertEqual(terminal["DISTINCT_FITS"], 0)
        ledger = json.loads((self.root / ex.EVIDENCE / "FIT_LEDGER.json").read_text())
        self.assertEqual(ledger["distinct_fits_started"], 1)
        self.assertEqual(self.calls["fit_attempt"], 1)

    def test_duplicate_start_is_denied(self):
        self.mode = "duplicate_start"
        self.assertEqual(ex.run(self.root)["DISTINCT_FITS"], 0)
        self.assertIn("duplicate", self.result()["failure"])

    def test_missing_cnn_epoch_blocks_before_completing_first_cnn(self):
        self.mode = "missing_epoch"
        self.assertEqual(ex.run(self.root)["DISTINCT_FITS"], 16)
        self.assertIn("thirty", self.result()["failure"])

    def test_prediction_failure_keeps_completed_fit_count(self):
        self.mode = "prediction_failure"
        self.assertEqual(ex.run(self.root)["DISTINCT_FITS"], 1)
        self.assertIn("prediction", self.result()["failure"])

    def test_bad_result_schema_cannot_be_pass(self):
        self.mode = "bad_fit_schema"
        self.assertEqual(ex.run(self.root)["STUDY3"], "BLOCKED_PARTIAL_EXECUTION")
        self.assertIn("provenance", self.result()["failure"])

    def test_duplicate_invocation_preserves_receipt_and_terminal(self):
        ex.run(self.root)
        paths = [self.root / ex.EVIDENCE / n for n in (ex.RECEIPT, "terminal-state.json", "results.json")]
        before = [p.read_bytes() for p in paths]
        with self.assertRaises(FileExistsError):
            ex.run(self.root)
        self.assertEqual([p.read_bytes() for p in paths], before)
        self.assertEqual(self.calls["load"], 1)

    def test_output_failure_preserves_consumed_fallback_terminal(self):
        original = ex.emit
        def fail(root, name, value):
            if name == "results.json":
                raise OSError("synthetic result write failure")
            return original(root, name, value)
        with patch.object(ex, "emit", side_effect=fail), self.assertRaises(OSError):
            ex.run(self.root)
        terminal = json.loads((self.root / ex.EVIDENCE / "terminal-state.json").read_text())
        self.assertEqual(terminal["STUDY3"], "BLOCKED_POST_RECEIPT_FAILURE")
        self.assertFalse(terminal["retry_authorized"])

    def test_final_checksum_failure_cannot_leave_success_terminal(self):
        original = ex.emit
        def fail(root, name, value):
            if name == "post-run-hashes.sha256":
                self.assertFalse((root / ex.EVIDENCE / "terminal-state.json").exists())
                raise OSError("synthetic final checksum failure")
            return original(root, name, value)
        with patch.object(ex, "emit", side_effect=fail), self.assertRaises(OSError):
            ex.run(self.root)
        terminal = json.loads((self.root / ex.EVIDENCE / "terminal-state.json").read_text())
        self.assertEqual(terminal["STUDY3"], "BLOCKED_POST_RECEIPT_FAILURE")
        self.assertFalse(terminal["retry_authorized"])


class CounterLike(dict):
    def __missing__(self, key):
        return 0


if __name__ == "__main__":
    unittest.main()
