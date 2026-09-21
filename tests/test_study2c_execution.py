"""Study2-C orchestration contracts with synthetic metadata and mocked ML/I/O.

These tests run no classifier, CNN, native decoder, historical ledger reader,
Git command, remote CI, or experimental pixel access. Array fixtures are tiny
constant synthetic uint8 values created inside each test.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

from snbi_fragmentation import study2c_execution as execution

try:
    import numpy as np
except ImportError:
    np = None


HEAD = "d" * 40


def encoded(value):
    return (json.dumps(value, sort_keys=True) + "\n").encode()


def synthetic_design():
    samples = []
    for split in ("TRAIN", "DEVELOPMENT", "TEST"):
        for kind, tier, label in (("positive", "GOLD", 1),
                                  ("background", "BACKGROUND", 0),
                                  ("positive", "SILVER", 1)):
            number = len(samples) + 1
            samples.append({"sample_id": f"synthetic-{number}",
                "group_id": f"{split}|{kind}", "split": split, "kind": kind,
                "tier": tier, "label": label, "acquisition_id": "synthetic_acquisition",
                "frame_index": number, "fixture_value": number})
    return {"status": "PASS", "samples": samples,
            "counts": {"fixture_rows": len(samples)},
            "cv_fold_by_group": {"TRAIN|positive": 0, "TRAIN|background": 1}}


def successful_ci():
    jobs = [{"name": name, "status": "completed", "conclusion": "success",
             "steps": [{"name": "synthetic step", "status": "completed", "conclusion": "success"}]}
            for name in sorted(execution.REQUIRED_JOBS)]
    return {"head_sha": HEAD, "runs": [{"headSha": HEAD, "status": "completed",
                                        "conclusion": "success", "jobs": jobs}]}


def family_records(primary=0.5, secondary=0.5):
    return {name: {"development": {"primary_gmba": primary,
            "observation": {"balanced_accuracy": secondary}}} for name in execution.MODELS}


class PureExecutionContracts(unittest.TestCase):
    def test_exact_equality_preserves_nested_types(self):
        self.assertTrue(execution.exact({"x": [1, 2.0, False, None]}, {"x": [1, 2.0, False, None]}))
        self.assertFalse(execution.exact({"x": [1.0]}, {"x": [1]}))
        self.assertFalse(execution.exact({"x": True}, {"x": 1}))
        self.assertFalse(execution.exact({"x": 1}, {"x": 1, "extra": 0}))

    def test_ci_requires_all_nine_jobs_and_all_success_steps(self):
        self.assertEqual(set(execution.verify_ci(successful_ci(), HEAD)), execution.REQUIRED_JOBS)

    def test_ci_denies_wrong_head_at_proof_and_run(self):
        for field in ("proof", "run"):
            proof = successful_ci()
            if field == "proof": proof["head_sha"] = "e" * 40
            else: proof["runs"][0]["headSha"] = "e" * 40
            with self.subTest(field=field), self.assertRaises(execution.Study2Error):
                execution.verify_ci(proof, HEAD)

    def test_ci_denies_pending_failure_cancelled_and_skipped_at_every_level(self):
        for level in ("run", "job", "step"):
            for status, conclusion in (("in_progress", None), ("completed", "failure"),
                                       ("completed", "cancelled"), ("completed", "skipped")):
                proof = successful_ci()
                node = proof["runs"][0]
                if level in {"job", "step"}: node = node["jobs"][0]
                if level == "step": node = node["steps"][0]
                node.update(status=status, conclusion=conclusion)
                with self.subTest(level=level, status=status, conclusion=conclusion), self.assertRaises(execution.Study2Error):
                    execution.verify_ci(proof, HEAD)

    def test_ci_denies_missing_duplicate_unknown_jobs_and_empty_steps(self):
        for mutation in ("missing", "duplicate", "unknown", "empty_steps", "no_runs"):
            proof = successful_ci(); jobs = proof["runs"][0]["jobs"]
            if mutation == "missing": jobs.pop()
            elif mutation == "duplicate": jobs[-1] = deepcopy(jobs[0])
            elif mutation == "unknown": jobs[-1]["name"] = "unapproved-substitute"
            elif mutation == "empty_steps": jobs[-1]["steps"] = []
            else: proof["runs"] = []
            with self.subTest(mutation=mutation), self.assertRaises(execution.Study2Error):
                execution.verify_ci(proof, HEAD)

    def test_family_selection_primary_metric_precedes_secondary(self):
        records = family_records()
        records["SVM_RBF"]["development"]["primary_gmba"] = 0.7
        records["RF_REFERENCE"]["development"]["observation"]["balanced_accuracy"] = 1.0
        self.assertEqual(execution.choose_family(records), "SVM_RBF")

    def test_family_primary_tie_uses_observation_ba_then_exact_simplicity_order(self):
        records = family_records()
        records["RF_TUNED"]["development"]["observation"]["balanced_accuracy"] = 0.7
        self.assertEqual(execution.choose_family(records), "RF_TUNED")
        self.assertEqual(execution.choose_family(family_records()), "LOGISTIC_REGRESSION")
        for first in range(len(execution.MODELS)):
            records = family_records(primary=0.1)
            for name in execution.MODELS[first:]:
                records[name]["development"]["primary_gmba"] = 0.9
            self.assertEqual(execution.choose_family(records), execution.MODELS[first])

    def test_family_selection_rejects_incomplete_model_set(self):
        records = family_records(); records.pop("CNN_V2")
        with self.assertRaisesRegex(execution.Study2Error, "five models"):
            execution.choose_family(records)

    def test_samples_gold_default_and_silver_regime_preserve_order(self):
        design = synthetic_design()
        gold = execution.select_samples(design, {"TRAIN", "DEVELOPMENT"})
        self.assertEqual([r["fixture_value"] for r in gold], [1, 2, 4, 5])
        silver = execution.select_samples(design, {"TRAIN"}, "GOLD_PLUS_SILVER")
        self.assertEqual([r["fixture_value"] for r in silver], [1, 2, 3])
        self.assertTrue(all(r["tier"] != "SILVER" for r in execution.select_samples(design, {"TEST"})))
        with self.assertRaisesRegex(execution.Study2Error, "unknown regime"):
            execution.select_samples(design, {"TRAIN"}, "ALL_TIERS")

    def test_access_state_denies_unknown_action_or_changed_row(self):
        design = synthetic_design()
        state = execution.AccessState("a" * 64, HEAD, design)
        row = deepcopy(design["samples"][0])
        for key, value in (("sample_id", "unknown"), ("label", True), ("frame_index", 1.0),
                           ("split", "TEST"), ("tier", "SILVER")):
            changed = dict(row, **{key: value})
            with self.subTest(key=key), self.assertRaisesRegex(execution.Study2Error, "frozen split"):
                state.grant("LOAD_POSITIVE_ROWS", "TRAIN", [changed])
        with self.assertRaisesRegex(execution.Study2Error, "unknown input action"):
            state.grant("OPEN_EVERYTHING", "TRAIN", [row])
        with self.assertRaisesRegex(execution.Study2Error, "kind mismatch"):
            state.grant("MATERIALIZE_BACKGROUNDS", "TRAIN", [row])

    def test_access_state_denies_empty_rows_and_duplicate_manifest_identity(self):
        design = synthetic_design()
        state = execution.AccessState("a" * 64, HEAD, design)
        with self.assertRaises(execution.Study2Error):
            state.grant("LOAD_POSITIVE_ROWS", "TRAIN", [])
        design["samples"].append(deepcopy(design["samples"][0]))
        with self.assertRaisesRegex(execution.Study2Error, "duplicate"):
            execution.AccessState("a" * 64, HEAD, design)

    def test_access_stage_order_and_test_durable_proof(self):
        design = synthetic_design(); state = execution.AccessState("a" * 64, HEAD, design)
        rows = design["samples"]
        self.assertTrue(state.grant("LOAD_POSITIVE_ROWS", "TRAIN", [rows[0]])["authorized"])
        for phase, row in (("TRAIN_SILVER", rows[2]), ("FINAL_TRAIN", rows[5]), ("TEST", rows[6])):
            with self.subTest(phase=phase), self.assertRaises(execution.Study2Error):
                state.grant("LOAD_POSITIVE_ROWS", phase, [row])
        with self.assertRaisesRegex(execution.Study2Error, "TEST cannot"):
            state.grant("LOAD_POSITIVE_ROWS", "TRAIN", [rows[6]])
        state.stage = "SILVER"
        self.assertTrue(state.grant("LOAD_POSITIVE_ROWS", "TRAIN_SILVER", [rows[2]])["authorized"])
        state.stage = "FINAL_TRAIN"
        self.assertTrue(state.grant("LOAD_POSITIVE_ROWS", "FINAL_TRAIN", [rows[5]])["authorized"])
        state.stage = "TEST"
        with self.assertRaisesRegex(execution.Study2Error, "durable final fit"):
            state.grant("LOAD_POSITIVE_ROWS", "TEST", [rows[6]])
        state.final_fit_sha = "c" * 64
        proof = state.grant("LOAD_POSITIVE_ROWS", "TEST", [rows[6]])
        self.assertTrue(proof["final_fit_durable"])
        self.assertEqual(proof["final_fit_freeze_sha256"], "c" * 64)


class TemporaryExecutionCase(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / ".bootstrap-test-tmp"
        parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="study2c-controller-", dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / execution.E).mkdir(parents=True)
        patcher = mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=10 ** 12))
        patcher.start(); self.addCleanup(patcher.stop)

    def json_file(self, name):
        return json.loads((self.root / execution.E / name).read_text())

    def write(self, name, payload):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


class FilesystemAndPreflightTests(TemporaryExecutionCase):
    def test_emit_is_exclusive_and_flushes_durable_file_and_directory(self):
        with mock.patch.object(execution.os, "fsync", wraps=execution.os.fsync) as sync:
            result = execution.emit(self.root, "synthetic.json", {"value": 2})
            self.assertEqual(sync.call_count, 2)
        raw = (self.root / execution.E / "synthetic.json").read_bytes()
        self.assertEqual(result, hashlib.sha256(raw).hexdigest())
        with self.assertRaises(FileExistsError):
            execution.emit(self.root, "synthetic.json", {"value": 3})
        self.assertEqual(self.json_file("synthetic.json"), {"value": 2})

    def test_emit_denies_nonfinite_json_disk_budget_and_symlinks(self):
        with self.assertRaises(ValueError):
            execution.emit(self.root, "nan.json", {"value": float("nan")})
        with mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=execution.MIN_FREE)):
            with self.assertRaisesRegex(execution.Study2Error, "disk budget"):
                execution.emit(self.root, "small.json", {})
        (self.root / execution.E / "alias.json").symlink_to("absent.json")
        with self.assertRaisesRegex(execution.Study2Error, "symlink"):
            execution.emit(self.root, "alias.json", {})

    def test_text_reader_rejects_experimental_and_unsafe_paths_before_open(self):
        with mock.patch.object(execution.os, "open") as opened:
            for path in ("data/derived/study2b/corpus-index.jsonl", "data/video.mp4", "../outside.json",
                         "/absolute.json", "src/../outside.json", "src/binary.bin"):
                with self.subTest(path=path), self.assertRaises(execution.Study2Error):
                    execution.read_text(self.root, path)
            opened.assert_not_called()

    def preflight_fixture(self):
        required = set(execution.CODE + execution.TESTS + execution.PROTOCOLS) | {
            execution.AUTH, execution.E + "/AUTHORIZATION.md", execution.E + "/SYNTHETIC_TESTS.json",
            ".github/workflows/study2c-synthetic.yml", "scripts/check_ti3_scope.py",
            "configs/governance/phase-scope-v1.json", execution.B + "/LOCAL_ARTIFACT_MANIFEST.json",
            execution.B + "/FRAME_HASHES.json", "src/snbi_fragmentation/study2b_corpus.py",
            "src/snbi_fragmentation/study2b_streaming.py"}
        documents = {path: b"synthetic text\n" for path in required}
        documents[execution.E + "/SYNTHETIC_TESTS.json"] = encoded({"status": "PASS", "skips": 0, "failures": 0, "errors": 0})
        documents[execution.E + "/SPLIT_MANIFEST.json"] = encoded({"status": "PASS"})
        documents["constraints-ti3c-cnn.txt"] = b"synthetic-dependency==frozen-version\n"
        documents[execution.E + "/CI_PROOF.json"] = encoded(successful_ci())
        documents[execution.E + "/METHOD_FREEZE.json"] = encoded({"files": {path: execution.digest(documents[path]) for path in required}})
        committed = dict(documents)
        def git(root, *args):
            self.assertEqual(root, self.root)
            return execution.BASE if args == ("rev-parse", "HEAD^") else HEAD
        def show(root, *args):
            self.assertEqual(args[0], "show")
            return committed[args[1].split(":", 1)[1]]
        patches = [mock.patch.object(execution, "authority", return_value={}),
                   mock.patch.object(execution, "preserved_baseline", return_value=1),
                   mock.patch.object(execution, "git", side_effect=git),
                   mock.patch.object(execution, "git_bytes", side_effect=show),
                   mock.patch.object(execution, "read_text", side_effect=lambda root, name: documents[name]),
                   mock.patch.object(execution.importlib.metadata, "version", return_value="frozen-version")]
        for patch in patches:
            patch.start(); self.addCleanup(patch.stop)
        return documents, committed

    def test_preflight_checks_exact_committed_freeze_without_receipt_or_source(self):
        documents, _ = self.preflight_fixture()
        result = execution.preflight(self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["head_sha"], HEAD)
        self.assertFalse(result["receipt_created"])
        self.assertEqual(result["source_opens"], 0)
        self.assertEqual(len(result["ci_jobs"]), 9)
        self.assertFalse((self.root / execution.E / "EXECUTION_RECEIPT.json").exists())

    def test_preflight_denies_each_existing_consumption_artifact_first(self):
        for name in ("EXECUTION_RECEIPT.json", "results.json", "terminal-state.json"):
            with self.subTest(name=name), mock.patch.object(execution, "authority") as authority:
                marker = self.root / execution.E / name
                marker.write_text("{}")
                try:
                    with self.assertRaisesRegex(execution.Study2Error, "consumed"):
                        execution.preflight(self.root)
                    authority.assert_not_called()
                finally:
                    marker.unlink()

    def test_preflight_denies_wrong_parent_before_scientific_inputs(self):
        self.preflight_fixture()
        with mock.patch.object(execution, "git", return_value=HEAD):
            with self.assertRaisesRegex(execution.Study2Error, "directly follow"):
                execution.preflight(self.root)

    def test_preflight_denies_changed_scientific_text(self):
        documents, _ = self.preflight_fixture()
        documents[execution.CODE[0]] += b"changed"
        with self.assertRaisesRegex(execution.Study2Error, "frozen bytes"):
            execution.preflight(self.root)

    def test_preflight_denies_changed_freeze_blob(self):
        documents, _ = self.preflight_fixture()
        documents[execution.E + "/METHOD_FREEZE.json"] += b" "
        with self.assertRaisesRegex(execution.Study2Error, "committed blob"):
            execution.preflight(self.root)

    def test_preflight_denies_missing_frozen_path(self):
        documents, committed = self.preflight_fixture()
        name = execution.E + "/METHOD_FREEZE.json"
        freeze = json.loads(documents[name]); freeze["files"].pop(execution.CODE[0])
        documents[name] = committed[name] = encoded(freeze)
        with self.assertRaisesRegex(execution.Study2Error, "incomplete freeze"):
            execution.preflight(self.root)

    def test_preflight_denies_dependency_divergence(self):
        self.preflight_fixture()
        with mock.patch.object(execution.importlib.metadata, "version", return_value="different-version"):
            with self.assertRaisesRegex(execution.Study2Error, "dependency pin"):
                execution.preflight(self.root)


@unittest.skipIf(np is None, "NumPy required for generated orchestration fixtures")
class MockedWorkflowTests(TemporaryExecutionCase):
    """Complete controller paths; every fit, score, feature and input is mocked."""

    def setUp(self):
        super().setUp()
        self.design = synthetic_design()
        self.write(execution.E + "/SPLIT_MANIFEST.json", encoded(self.design))
        self.events = []
        self.fail = None
        self.silver_delta = 0.0
        self.winner = "RF_REFERENCE"
        self.last_prediction = None
        self.closed = False
        self.access_calls = []
        self.fit_calls = []
        self.feature_ids = []
        self.cv_calls = []
        self.scores = {family: 0.5 for family in execution.MODELS}
        self.scores[self.winner] = 0.75
        fixture = self
        class FakeAccess:
            def __init__(self, root, grant, audit):
                if fixture.fail == "access_constructor":
                    raise RuntimeError("synthetic constructor failure")
                self.grant = grant
                audit["fixture_only_no_real_sources"] = True
            def receive(self, rows, phase, background):
                action = "MATERIALIZE_BACKGROUNDS" if background else "LOAD_POSITIVE_ROWS"
                grant = self.grant(action, phase, rows)
                fixture.access_calls.append((action, phase, [r["sample_id"] for r in rows]))
                fixture.events.append(("access", phase, background))
                if phase == "TEST":
                    fixture.assertTrue((fixture.root / execution.E / "FINAL_FIT_FREEZE.json").exists())
                    fixture.assertTrue((fixture.root / execution.E / "TEST_ACCESS_RECEIPT.json").exists())
                    fixture.assertTrue(grant["final_fit_durable"])
                    if fixture.fail == "test_materialization":
                        raise RuntimeError("synthetic TEST materialization failure")
                if fixture.fail == "input_shape":
                    return np.zeros((len(rows), 1, 65, 65), dtype=np.uint8)
                return np.stack([np.full((2, 65, 65), r["fixture_value"], dtype=np.uint8) for r in rows])
            def load_positive_rows(self, rows, phase):
                return self.receive(rows, phase, False)
            def materialize_backgrounds(self, rows, phase):
                return self.receive(rows, phase, True), {"fixture_phase": phase, "artifacts": []}
            def close(self):
                fixture.closed = True
        io_module = ModuleType("snbi_fragmentation.study2c_io"); io_module.CorpusAccess = FakeAccess
        design_module = ModuleType("snbi_fragmentation.study2c_design")
        design_module.group_equal_weights = lambda rows: [1.0] * len(rows)
        design_module.metric_bundle = self.metric
        models = ModuleType("snbi_fragmentation.study2c_models")
        models.extract_lbp20 = self.features
        models.fit_classical = self.fit
        models.predict_classical = self.predict
        models.cv_search = self.cv
        cnn = ModuleType("snbi_fragmentation.study2c_cnn")
        cnn.fit_cnn = lambda x, rows, weights, progress=None: self.fit("CNN_V2", {}, x, rows, weights)
        cnn.predict_cnn = self.predict
        patches = [mock.patch.dict(sys.modules, {module.__name__: module for module in (io_module, design_module, models, cnn)}),
                   mock.patch.object(execution, "preflight", side_effect=self.preflight),
                   mock.patch.object(execution, "progress", side_effect=lambda event: self.events.append(("progress", deepcopy(event))))]
        for patch in patches:
            patch.start(); self.addCleanup(patch.stop)

    def preflight(self, root):
        if self.fail == "preflight":
            raise execution.Study2Error("synthetic preflight denial")
        if (root / execution.E / "EXECUTION_RECEIPT.json").exists():
            raise execution.Study2Error("authority consumed; no retry")
        return {"status": "PASS", "head_sha": HEAD, "source_opens": 0, "receipt_created": False}

    def features(self, pairs):
        ids = pairs[:, 0, 0, 0].tolist()
        self.feature_ids.extend(ids)
        return np.repeat(pairs[:, 0, 0, 0, None], 20, axis=1).astype(float)

    def fit(self, family, params, x, rows, weights):
        self.assertTrue(all(r["split"] != "TEST" for r in rows))
        self.assertEqual(len(x), len(rows)); self.assertEqual(len(weights), len(rows))
        purpose = "final" if (self.root / execution.E / "FINAL_PIPELINE.json").exists() else (
            "silver" if (self.root / execution.E / "FAMILY_SELECTION.json").exists() else "development")
        self.events.append(("fit", purpose, family))
        self.fit_calls.append({"family": family, "purpose": purpose, "rows": deepcopy(rows), "params": deepcopy(params)})
        if self.fail == "development_fit" and purpose == "development":
            raise RuntimeError("synthetic fit failure")
        if self.fail == "final_fit" and purpose == "final":
            raise RuntimeError("synthetic final fit failure")
        return {"family": family, "purpose": purpose}, {"fit_calls": 1, "fixture_only": True}

    def predict(self, model, x):
        self.last_prediction = dict(model)
        self.events.append(("predict", model["purpose"], model["family"]))
        count = len(x)
        if self.fail == "test_prediction_length" and model["purpose"] == "final":
            count -= 1
        return {"predictions": [1] * count, "probabilities": [[0.25, 0.75]] * count,
                "decision_scores": None, "classes": [0, 1]}

    def metric(self, rows, predictions):
        self.assertEqual(len(rows), len(predictions))
        split = rows[0]["split"]
        model = self.last_prediction
        self.events.append(("metric", split, model["purpose"], model["family"]))
        if split == "TEST":
            self.assertTrue((self.root / execution.E / "TEST_PREDICTIONS.json").exists())
            if self.fail == "test_score":
                raise RuntimeError("synthetic TEST scoring failure")
        score = self.scores[model["family"]]
        if model["purpose"] == "silver": score += self.silver_delta
        return {"primary_gmba": score, "observation": {"balanced_accuracy": score}}

    def cv(self, family, x, rows, groups, progress):
        self.cv_calls.append(family)
        self.assertTrue(all(r["split"] == "TRAIN" and r["tier"] in {"GOLD", "BACKGROUND"} for r in rows))
        count = {"LOGISTIC_REGRESSION": 12, "SVM_RBF": 36, "RF_TUNED": 32}[family]
        if self.fail == "cv_before_start":
            raise RuntimeError("synthetic pre-fit CV failure")
        for ordinal in range(1, count + 1):
            event = {"family": family, "fit_ordinal": ordinal, "candidate_index": (ordinal-1)//4, "fold": (ordinal-1)%4}
            if self.fail != "cv_complete_without_start":
                progress({**event, "event": "CV_FIT_START"})
            if self.fail == "cv_after_start":
                raise RuntimeError("synthetic CV fit failure")
            progress({**event, "event": "CV_FIT_COMPLETE"})
            if self.fail == "cv_after_complete":
                raise RuntimeError("synthetic CV scoring failure")
            progress({**event, "event": "CV_FOLD_COMPLETE", "primary_gmba": 0.5})
        report_count = count - 1 if self.fail == "cv_wrong_report" else count
        return {"fixture_choice": family}, {"fit_calls": report_count, "fixture_only": True}

    def execute(self):
        return execution.run(self.root)

    def counts(self):
        return self.json_file("results.json")["counts"]

    def test_full_mocked_flow_has_exact_budgets_prediction_first_and_gold_tie(self):
        terminal = self.execute()
        self.assertEqual(terminal["STUDY2_C"], "PASS")
        self.assertEqual(terminal["SELECTED_MODEL_FAMILY"], "RF_REFERENCE")
        self.assertEqual(terminal["SELECTED_SUPERVISION_REGIME"], "GOLD_ONLY")
        self.assertEqual(terminal["TEST_STATE"], "CONSUMED")
        counts = self.counts()
        for key, expected in {"scientific_invocations": 1, "cv_fits_started": 80,
            "cv_fits_completed": 80, "development_fits_started": 5, "development_fits_completed": 5,
            "silver_fits_started": 1, "silver_fits_completed": 1, "final_fits_started": 1,
            "final_fits_completed": 1, "development_evaluations": 5, "silver_development_evaluations": 1,
            "test_prediction_calls": 1, "test_evaluations": 1, "retries": 0}.items():
            self.assertEqual(counts[key], expected, key)
        self.assertEqual(self.cv_calls, ["LOGISTIC_REGRESSION", "SVM_RBF", "RF_TUNED"])
        self.assertEqual(len(self.fit_calls), 7)
        self.assertTrue(self.closed)
        self.assertEqual(len(self.feature_ids), len(set(self.feature_ids)))
        self.assertEqual([call[1] for call in self.access_calls],
                         ["TRAIN", "DEVELOPMENT", "TRAIN_DEVELOPMENT", "TRAIN_SILVER", "TEST", "TEST"])
        self.assertTrue(all(r["tier"] != "SILVER" for r in self.fit_calls[-1]["rows"]))
        self.assertNotIn("labels", self.json_file("TEST_PREDICTIONS.json"))
        self.assertIn("labels", self.json_file("TEST_METRICS.json"))

    def test_silver_strict_improvement_loads_dev_silver_only_for_final_fit(self):
        self.silver_delta = 0.05
        terminal = self.execute()
        self.assertEqual(terminal["SELECTED_SUPERVISION_REGIME"], "GOLD_PLUS_SILVER")
        final_call = next(call for call in self.access_calls if call[1] == "FINAL_TRAIN")
        self.assertEqual(final_call[2], [self.design["samples"][5]["sample_id"]])
        final_fit = self.fit_calls[-1]
        self.assertEqual(len(final_fit["rows"]), 6)
        self.assertTrue(all(r["split"] != "TEST" for r in final_fit["rows"]))
        reads = [sid for _, _, ids in self.access_calls for sid in ids]
        self.assertNotIn(self.design["samples"][8]["sample_id"], reads)
        self.assertEqual(len(reads), len(set(reads)))

    def test_silver_inferiority_keeps_gold_and_does_not_retry_reference(self):
        self.silver_delta = -0.1
        terminal = self.execute()
        self.assertEqual(terminal["SELECTED_SUPERVISION_REGIME"], "GOLD_ONLY")
        self.assertEqual(sum(f["purpose"] == "silver" for f in self.fit_calls), 1)
        self.assertFalse(self.json_file("SILVER_ABLATION.json")["gold_reference_reexecuted"])

    def test_cnn_selection_uses_same_frozen_final_and_silver_protocol_without_classical_research(self):
        self.scores = {family: 0.5 for family in execution.MODELS}; self.scores["CNN_V2"] = 0.8
        terminal = self.execute()
        self.assertEqual(terminal["SELECTED_MODEL_FAMILY"], "CNN_V2")
        self.assertEqual([f["family"] for f in self.fit_calls[-2:]], ["CNN_V2", "CNN_V2"])
        self.assertEqual(self.counts()["cv_fits_completed"], 80)

    def test_receipt_exclusivity_blocks_second_invocation_before_any_more_access(self):
        self.execute(); previous = deepcopy(self.access_calls)
        with self.assertRaisesRegex(execution.Study2Error, "consumed"):
            self.execute()
        self.assertEqual(self.access_calls, previous)
        self.assertEqual(self.counts()["scientific_invocations"], 1)

    def test_failed_preflight_creates_no_receipt_or_accessor(self):
        self.fail = "preflight"
        with self.assertRaisesRegex(execution.Study2Error, "preflight denial"):
            self.execute()
        self.assertFalse((self.root / execution.E / "EXECUTION_RECEIPT.json").exists())
        self.assertEqual(self.access_calls, [])
        self.assertEqual(self.fit_calls, [])

    def test_constructor_failure_after_receipt_has_closed_fallback_evidence(self):
        self.fail = "access_constructor"
        terminal = self.execute()
        self.assertEqual(terminal["STUDY2_C"], "BLOCKED_POST_RECEIPT_FAILURE")
        self.assertEqual(terminal["STATE"], "CLOSED_CONSUMED")
        self.assertFalse(terminal["retry_authorized"])
        self.assertEqual(self.fit_calls, [])

    def test_shape_divergence_stops_before_any_fit_or_test(self):
        self.fail = "input_shape"
        terminal = self.execute()
        self.assertEqual(terminal["STUDY2_C"], "BLOCKED_PARTIAL_EXECUTION")
        self.assertEqual(self.counts()["development_fits_started"], 0)
        self.assertEqual(terminal["TEST_STATE"], "LOGICALLY_SEALED_TEST")

    def test_cv_failure_before_actual_fit_reports_zero_started(self):
        self.fail = "cv_before_start"; self.execute()
        self.assertEqual(self.counts()["cv_fits_started"], 0)
        self.assertEqual(self.counts()["cv_fits_completed"], 0)
        self.assertEqual(self.counts()["development_fits_started"], 0)

    def test_cv_partial_fit_reports_one_started_zero_completed(self):
        self.fail = "cv_after_start"; self.execute()
        self.assertEqual(self.counts()["cv_fits_started"], 1)
        self.assertEqual(self.counts()["cv_fits_completed"], 0)
        self.assertEqual(self.counts()["test_evaluations"], 0)

    def test_cv_scoring_failure_preserves_successful_fit_count(self):
        self.fail = "cv_after_complete"; self.execute()
        self.assertEqual(self.counts()["cv_fits_started"], 1)
        self.assertEqual(self.counts()["cv_fits_completed"], 1)
        self.assertEqual(self.counts()["development_fits_started"], 0)

    def test_cv_wrong_report_stops_before_development_fit(self):
        self.fail = "cv_wrong_report"; terminal = self.execute()
        self.assertEqual(terminal["STUDY2_C"], "BLOCKED_PARTIAL_EXECUTION")
        self.assertEqual(self.counts()["cv_fits_completed"], 12)
        self.assertEqual(self.counts()["development_fits_started"], 0)

    def test_cv_complete_without_start_is_not_accepted_as_success(self):
        self.fail = "cv_complete_without_start"; terminal = self.execute()
        self.assertEqual(terminal["STUDY2_C"], "BLOCKED_PARTIAL_EXECUTION")
        self.assertEqual(self.counts()["development_fits_started"], 0)

    def test_development_fit_failure_preserves_started_and_blocks_test(self):
        self.fail = "development_fit"; terminal = self.execute()
        self.assertEqual(self.counts()["development_fits_started"], 1)
        self.assertEqual(self.counts()["development_fits_completed"], 0)
        self.assertEqual(terminal["TEST_STATE"], "LOGICALLY_SEALED_TEST")
        self.assertTrue(all(phase != "TEST" for _, phase, _ in self.access_calls))

    def test_final_fit_failure_keeps_test_sealed_and_has_no_fit_freeze(self):
        self.fail = "final_fit"; terminal = self.execute()
        self.assertEqual(self.counts()["final_fits_started"], 1)
        self.assertEqual(self.counts()["final_fits_completed"], 0)
        self.assertEqual(terminal["TEST_STATE"], "LOGICALLY_SEALED_TEST")
        self.assertFalse((self.root / execution.E / "FINAL_FIT_FREEZE.json").exists())
        self.assertTrue(all(phase != "TEST" for _, phase, _ in self.access_calls))

    def test_failed_durable_fit_record_blocks_test_even_after_completed_fit(self):
        original = execution.emit
        def fail_fit_freeze(root, name, value):
            if name == "FINAL_FIT_FREEZE.json":
                raise OSError("synthetic fit-freeze write failure")
            return original(root, name, value)
        with mock.patch.object(execution, "emit", side_effect=fail_fit_freeze):
            terminal = self.execute()
        self.assertEqual(self.counts()["final_fits_completed"], 1)
        self.assertEqual(terminal["TEST_STATE"], "LOGICALLY_SEALED_TEST")
        self.assertTrue(all(phase != "TEST" for _, phase, _ in self.access_calls))

    def test_test_input_failure_remains_consumed_without_evaluation(self):
        self.fail = "test_materialization"; terminal = self.execute()
        self.assertEqual(terminal["TEST_STATE"], "CONSUMED_ACCESS_STARTED")
        self.assertEqual(self.counts()["test_evaluations"], 0)
        self.assertTrue((self.root / execution.E / "TEST_ACCESS_RECEIPT.json").exists())

    def test_test_prediction_count_failure_has_one_attempt_and_zero_score(self):
        self.fail = "test_prediction_length"; self.execute()
        self.assertEqual(self.counts()["test_prediction_calls"], 1)
        self.assertEqual(self.counts()["test_evaluations"], 0)
        self.assertFalse((self.root / execution.E / "TEST_PREDICTIONS.json").exists())

    def test_test_score_failure_preserves_prediction_first_record_and_no_retry(self):
        self.fail = "test_score"; terminal = self.execute()
        self.assertEqual(self.counts()["test_prediction_calls"], 1)
        self.assertEqual(self.counts()["test_evaluations"], 0)
        self.assertTrue((self.root / execution.E / "TEST_PREDICTIONS.json").exists())
        self.assertFalse((self.root / execution.E / "TEST_METRICS.json").exists())
        self.assertEqual(terminal["TEST_STATE"], "CONSUMED_ACCESS_STARTED")


if __name__ == "__main__":
    unittest.main()
