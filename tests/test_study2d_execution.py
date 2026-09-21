"""Study2-D control-flow tests: synthetic arrays and mocked fits/I/O/Git/CI.

No real model, source decoder, historical prediction file or experimental
container is used. Fresh temporary files remain below the repository.
"""
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

from snbi_fragmentation import study2d_execution as execution

try:
    import numpy as np
except ImportError:
    np = None

HEAD = "d" * 40
RECEIPT = "a" * 64


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def synthetic_design():
    rows = [{"sample_id": f"synthetic-{i}", "group_id": f"group-{i}",
             "split": "TRAIN", "tier": "GOLD" if i % 2 else "BACKGROUND",
             "label": i % 2, "kind": "positive" if i % 2 else "background",
             "acquisition_id": "bottom_up_anti_parallel", "frame_index": i}
            for i in range(8)]
    fits = []
    for part, count in (("A", 84), ("B", 12), ("C", 4)):
        for i in range(count):
            fits.append({"fit_id": part + str(i), "part": part, "fold": i % 4,
                "K": 24, "replicate": None, "density": "D1" if part == "A" else "DALL",
                "weighting": "OBSERVATION_EQUAL" if part == "C" else "GROUP_EQUAL",
                "train_sample_ids": [r["sample_id"] for r in rows[:4]],
                "validation_sample_ids": [r["sample_id"] for r in rows[4:]]})
    return {"status": "PASS", "rows": rows, "fits": fits,
            "reuse_refs": [{"source": "A0"} for _ in range(8)]}


def successful_ci():
    jobs = [{"name": name, "status": "completed", "conclusion": "success",
             "steps": [{"status": "completed", "conclusion": "success"}]}
            for name in sorted(execution.REQUIRED_JOBS)]
    return {"head_sha": HEAD, "runs": [{"headSha": HEAD, "status": "completed",
            "conclusion": "success", "jobs": jobs}]}


def fake_module(name, **members):
    module = ModuleType(name)
    module.__dict__.update(members)
    return module


class TemporaryRoot(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / ".bootstrap-test-tmp"
        parent.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="study2d-execution-", dir=parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / execution.E).mkdir(parents=True)
        self.space = mock.patch.object(execution.shutil, "disk_usage", return_value=SimpleNamespace(free=10**12))
        self.space.start()
        self.addCleanup(self.space.stop)

    def put(self, relative, value):
        p = self.root / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(encoded(value))


class BoundaryTests(TemporaryRoot):
    def test_exact_distinguishes_boolean_integer_and_nested_type(self):
        self.assertFalse(execution.exact(True, 1))
        self.assertFalse(execution.exact({"a": [1.0]}, {"a": [1]}))
        self.assertTrue(execution.exact({"a": [1.0, False]}, {"a": [1.0, False]}))

    def test_safe_path_rejects_traversal_and_absolute(self):
        for name in ("../x", "/tmp/x", "a//b", "a/./b", "a\\b"):
            with self.subTest(name=name), self.assertRaises(execution.Study2DError):
                execution.safe_path(self.root, name)

    def test_safe_path_rejects_symlink(self):
        (self.root / "link").symlink_to(self.root / execution.E, target_is_directory=True)
        with self.assertRaises(execution.Study2DError):
            execution.safe_path(self.root, "link/output.json")

    def test_emit_exclusive_preserves_original(self):
        expected = execution.emit(self.root, "fixture.json", {"one": 1})
        before = (self.root / execution.E / "fixture.json").read_bytes()
        self.assertEqual(expected, execution.digest(before))
        with self.assertRaises(FileExistsError):
            execution.emit(self.root, "fixture.json", {"two": 2})
        self.assertEqual(before, (self.root / execution.E / "fixture.json").read_bytes())

    def test_read_text_rejects_DEV_TEST_predictions_before_open(self):
        with mock.patch.object(execution.os, "open") as opened:
            for name in ("TEST_PREDICTIONS.json", "TEST_METRICS.json", "CNN_V2_DEVELOPMENT.json",
                         "SILVER_ABLATION.json", "results.json"):
                with self.assertRaises(execution.Study2DError):
                    execution.read_text(self.root, execution.C + "/" + name)
            opened.assert_not_called()

    def test_read_text_rejects_experimental_path_before_open(self):
        with mock.patch.object(execution.os, "open") as opened:
            with self.assertRaises(execution.Study2DError):
                execution.read_text(self.root, "data/derived/study2c/cachetest.bin")
            opened.assert_not_called()

    def test_budget_exactly_100_plus_eight_references(self):
        b = execution.expected_fit_budget()
        self.assertEqual(b["part_a_distinct_fits"] + b["part_b_additional_distinct_fits"]
                         + b["part_c_additional_distinct_fits"], 100)
        self.assertEqual(b["conceptual_fit_reuses"], 8)
        self.assertEqual(b["retries"], 0)

    def test_authority_declares_no_DEV_TEST_silver_source_or_selection(self):
        a = execution.expected_authority()
        for field in ("development_access", "test_access", "silver_access", "source_access", "model_selection"):
            self.assertIs(a[field], False)
        self.assertEqual(a["base_sha"], execution.BASE)
        self.assertEqual(a["distinct_rf_fits_limit"], 100)

    def test_ci_all_ten_exact_jobs(self):
        self.assertEqual(set(execution.verify_ci(successful_ci(), HEAD)), execution.REQUIRED_JOBS)

    def test_ci_wrong_head(self):
        with self.assertRaises(execution.Study2DError):
            execution.verify_ci(successful_ci(), "e" * 40)

    def test_ci_skipped_step_is_not_success(self):
        p = successful_ci(); p["runs"][0]["jobs"][0]["steps"][0]["conclusion"] = "skipped"
        with self.assertRaises(execution.Study2DError): execution.verify_ci(p, HEAD)

    def test_ci_pending_or_failure_blocks(self):
        for field, value in (("status", "in_progress"), ("conclusion", "failure")):
            p = successful_ci(); p["runs"][0][field] = value
            with self.subTest(field=field), self.assertRaises(execution.Study2DError):
                execution.verify_ci(p, HEAD)

    def test_ci_duplicate_or_missing_job_blocks(self):
        for mode in ("missing", "duplicate"):
            p = successful_ci()
            if mode == "missing": p["runs"][0]["jobs"].pop()
            else: p["runs"][0]["jobs"].append(deepcopy(p["runs"][0]["jobs"][0]))
            with self.subTest(mode=mode), self.assertRaises(execution.Study2DError):
                execution.verify_ci(p, HEAD)


class GrantTests(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_design()["rows"]
        self.state = execution.TrainAccessState(RECEIPT, HEAD, self.rows)

    def test_exact_grant_once(self):
        grant = self.state.grant("LOAD_TRAIN_ROWS", deepcopy(self.rows))
        self.assertEqual(grant, {"authorized": True, "execution_receipt_sha256": RECEIPT,
                                 "method_freeze_sha": HEAD})
        with self.assertRaises(execution.Study2DError): self.state.grant("LOAD_TRAIN_ROWS", self.rows)

    def test_unknown_action_denied(self):
        with self.assertRaises(execution.Study2DError): self.state.grant("LOAD_TEST_ROWS", self.rows)

    def test_reordered_or_omitted_row_denied(self):
        for rows in (list(reversed(self.rows)), self.rows[:-1]):
            with self.assertRaises(execution.Study2DError): self.state.grant("LOAD_TRAIN_ROWS", rows)

    def test_modified_row_type_denied(self):
        rows = deepcopy(self.rows); rows[0]["frame_index"] = float(rows[0]["frame_index"])
        with self.assertRaises(execution.Study2DError): self.state.grant("LOAD_TRAIN_ROWS", rows)

    def test_snapshot_does_not_follow_mutation(self):
        self.rows[0]["split"] = "TEST"
        with self.assertRaises(execution.Study2DError): self.state.grant("LOAD_TRAIN_ROWS", self.rows)

    def test_DEV_TEST_silver_rejected_even_if_constructor_receives_it(self):
        for key,value in (("split","DEVELOPMENT"),("split","TEST"),("tier","SILVER")):
            rows=deepcopy(self.rows); rows[0][key]=value
            state=execution.TrainAccessState(RECEIPT,HEAD,rows)
            with self.subTest(key=key,value=value),self.assertRaises(execution.Study2DError):
                state.grant("LOAD_TRAIN_ROWS",rows)


@unittest.skipIf(np is None, "optional NumPy unavailable; CI requires these synthetic orchestration tests")
class RunTests(TemporaryRoot):
    def setUp(self):
        super().setUp()
        self.design=synthetic_design()
        self.manifest={"rows":[{**r,"storage":{"synthetic":True}} for r in self.design["rows"]]}
        self.put(execution.E+"/STUDY2_D_ATTRIBUTION_DESIGN.json",self.design)
        self.put(execution.E+"/TRAIN_INPUT_MANIFEST.json",self.manifest)
        self.calls=CounterFixture()
        self.mode=None
        owner=self
        class Reader:
            def __init__(self,root,rows,grant,audit):
                owner.calls.readers+=1
                self.rows,self.grant,self.audit=rows,grant,audit
                owner.calls.receipt_at_reader=(root/execution.E/"EXECUTION_RECEIPT.json").exists()
            def load(self):
                owner.calls.loads+=1
                self.grant("LOAD_TRAIN_ROWS",self.rows)
                if owner.mode=="io_failure": raise ValueError("synthetic IO failure")
                keys=("DEV_GROUPS_READ","TEST_GROUPS_READ","DEV_ROWS_READ","TEST_ROWS_READ",
                      "TEST_CACHE_ROWS_READ","TEST_FEATURES_COMPUTED","EXPERIMENTAL_SOURCE_OPENS",
                      "FFMPEG_RUNS","ESM1_OPENS","ESM2_OPENS","ESM3_OPENS","ESM4_OPENS","ESM5_OPENS","ESM6_OPENS")
                self.audit.update({k:0 for k in keys})
                self.audit.update(rows_read=len(self.rows),rows_authenticated=len(self.rows),bytes_read=len(self.rows)*8450)
                if owner.mode=="bad_firewall":self.audit['DEV_ROWS_READ']=1
                return np.zeros((len(self.rows),2,65,65),dtype=np.uint8)
            def close(self):owner.calls.closes+=1
        def features(pairs):
            self.calls.features+=1
            if self.mode=="feature_failure":raise ValueError("synthetic feature failure")
            return np.zeros((len(pairs),20),dtype=np.float64)
        def fit(x,rows,weighting,on_event=None):
            self.calls.fits+=1
            if self.mode=="before_fit_failure":raise ValueError("synthetic admission failure")
            on_event({"event":"RF_FIT_START"})
            if self.mode=="duplicate_start":on_event({"event":"RF_FIT_START"})
            if self.mode=="partial_fit_failure":raise ValueError("synthetic fit failure")
            on_event({"event":"RF_FIT_COMPLETE"})
            return object(),{"fit_calls":1,"weighting":weighting}
        def predict(model,x):
            self.calls.predictions+=1
            if self.mode=="prediction_failure":raise ValueError("synthetic prediction failure")
            return {"predictions":[0]*len(x),"probabilities":[[1.0,0.0]]*len(x),"classes":[0,1]}
        def metric(rows,predictions):
            self.calls.metrics+=1
            return {"primary_gmba":0.5,"per_acquisition":{},"observation":{"balanced_accuracy":0.5}}
        def summary(design,records):
            self.calls.summaries+=1
            self.assertEqual(list(records),[s['fit_id'] for s in design['fits']])
            if self.mode=="summary_failure":raise ValueError("synthetic aggregation failure")
            fields={"GROUP_DIVERSITY_DESCRIPTOR":"NON_POSITIVE","GROUP_DIVERSITY_DELTA_K24_K17":0.0,
                    "GROUP_DIVERSITY_DELTA_K24_K4":0.0,"TEMPORAL_DENSITY_DESCRIPTOR":"NON_POSITIVE",
                    "TEMPORAL_DENSITY_DELTA_ALL_1":0.0,"GROUP_WEIGHTING_DESCRIPTOR":"NO_GROUP_EQUAL_BENEFIT",
                    "GROUP_WEIGHTING_DELTA":0.0}
            return {"part_a":{"fits":84},"part_b":{"additional_fits":12},"part_c":{"additional_fits":4},
                    "attribution_summary":{"terminal_fields":fields},"terminal_fields":fields,
                    "narrative_bridge_table":[{"condition":"synthetic"} for _ in range(9)],
                    "narrative_bridge_markdown":"| Condição | GMBA |\n| --- | ---: |\n| synthetic | 0.5 |\n"}
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        modules={
            'snbi_fragmentation.study2d_io':fake_module('study2d_io',TrainCorpusAccess=Reader),
            'snbi_fragmentation.study2d_models':fake_module('study2d_models',extract_lbp20=features,fit_reference=fit,predict_reference=predict),
            'snbi_fragmentation.study2d_design':fake_module('study2d_design',summarize_attribution=summary),
            'snbi_fragmentation.study2c_design':fake_module('study2c_design',metric_bundle=metric)}
        self.stack.enter_context(mock.patch.dict(sys.modules,modules))
        self.preflight=self.stack.enter_context(mock.patch.object(execution,'preflight',return_value={'status':'PASS','head_sha':HEAD}))
        self.stack.enter_context(mock.patch.object(execution,'progress'))

    def result(self):return json.loads((self.root/execution.E/'results.json').read_text())

    def test_complete_100_fits_order_and_eight_reuses(self):
        terminal=execution.run(self.root);r=self.result()
        self.assertEqual(terminal['STUDY2_D'],'PASS')
        self.assertTrue(self.calls.receipt_at_reader)
        self.assertEqual((self.calls.loads,self.calls.features,self.calls.fits,self.calls.predictions,self.calls.metrics),(1,1,100,100,100))
        self.assertEqual((r['counts']['part_a_fits'],r['counts']['part_b_fits'],r['counts']['part_c_fits'],r['counts']['result_reuses']),(84,12,4,8))
        self.assertEqual(r['counts']['scientific_invocations'],1)
        self.assertEqual(terminal['TEST_STATE'],'UNCHANGED_CONSUMED')
        self.assertFalse(terminal['MODEL_SELECTION_REOPENED'])
        self.assertEqual(terminal['GROUP_DIVERSITY_DESCRIPTOR'],'NON_POSITIVE')
        self.assertEqual(terminal['TEMPORAL_DENSITY_DELTA_ALL_1'],0.0)
        self.assertEqual(terminal['GROUP_WEIGHTING_DESCRIPTOR'],'NO_GROUP_EQUAL_BENEFIT')
        for name in ['GROUP_DIVERSITY_RESULTS.json','TEMPORAL_DENSITY_RESULTS.json','GROUP_WEIGHTING_RESULTS.json','ATTRIBUTION_SUMMARY.json','RESULTS_TABLES.md']:
            self.assertTrue((self.root/execution.E/name).exists())

    def test_preflight_failure_reads_nothing_and_creates_no_receipt(self):
        self.preflight.side_effect=execution.Study2DError('synthetic preflight failure')
        with self.assertRaises(execution.Study2DError):execution.run(self.root)
        self.assertEqual(self.calls.readers,0)
        self.assertFalse((self.root/execution.E/'EXECUTION_RECEIPT.json').exists())

    def test_io_failure_closes_consumed_before_features_or_fits(self):
        self.mode='io_failure';t=execution.run(self.root)
        self.assertEqual(t['STUDY2_D'],'BLOCKED_PARTIAL_EXECUTION')
        self.assertEqual((self.calls.features,self.calls.fits),(0,0))
        self.assertGreaterEqual(self.calls.closes,1)

    def test_firewall_nonzero_denies_before_features(self):
        self.mode='bad_firewall';terminal=execution.run(self.root)
        self.assertEqual(self.calls.features,0)
        self.assertIn('firewall',self.result()['failure'])
        self.assertEqual(terminal['DEV_ROWS_READ'],1)

    def test_feature_failure_is_not_fit(self):
        self.mode='feature_failure';execution.run(self.root);c=self.result()['counts']
        self.assertEqual((c['feature_extractions_started'],c['feature_extractions_completed'],c['fits_started']),(1,0,0))

    def test_validation_before_fit_does_not_increment_actual_fit(self):
        self.mode='before_fit_failure';execution.run(self.root);c=self.result()['counts']
        self.assertEqual((c['fits_started'],c['fits_completed']),(0,0))

    def test_partial_fit_preserves_one_started_zero_completed(self):
        self.mode='partial_fit_failure';execution.run(self.root);c=self.result()['counts']
        self.assertEqual((c['fits_started'],c['fits_completed'],c['validation_evaluations']),(1,0,0))

    def test_duplicate_fit_start_is_rejected(self):
        self.mode='duplicate_start';execution.run(self.root);c=self.result()['counts']
        self.assertEqual((c['fits_started'],c['fits_completed']),(1,0))

    def test_prediction_failure_keeps_completed_fit_counter(self):
        self.mode='prediction_failure';execution.run(self.root);c=self.result()['counts']
        self.assertEqual((c['fits_started'],c['fits_completed'],c['validation_evaluations']),(1,1,0))

    def test_summary_failure_does_not_erase_100_completed_fits(self):
        self.mode='summary_failure';execution.run(self.root);c=self.result()['counts']
        self.assertEqual(c['fits_completed'],100)
        self.assertEqual(self.result()['status'],'BLOCKED_PARTIAL_EXECUTION')

    def test_duplicate_fit_spec_never_refits(self):
        self.design['fits'][1]=deepcopy(self.design['fits'][0]);self.put(execution.E+'/STUDY2_D_ATTRIBUTION_DESIGN.json',self.design)
        execution.run(self.root)
        self.assertEqual(self.calls.fits,1)
        self.assertIn('duplicate',self.result()['failure'])

    def test_101st_fit_denied(self):
        extra=deepcopy(self.design['fits'][-1]);extra['fit_id']='unexpected101';self.design['fits'].append(extra)
        self.put(execution.E+'/STUDY2_D_ATTRIBUTION_DESIGN.json',self.design)
        execution.run(self.root)
        self.assertEqual(self.calls.fits,100)
        self.assertEqual(self.result()['status'],'BLOCKED_PARTIAL_EXECUTION')

    def test_missing_reuse_reference_blocks_without_extra_fit(self):
        self.design['reuse_refs'].pop();self.put(execution.E+'/STUDY2_D_ATTRIBUTION_DESIGN.json',self.design)
        execution.run(self.root)
        self.assertEqual(self.calls.fits,100)
        self.assertEqual(self.result()['status'],'BLOCKED_PARTIAL_EXECUTION')

    def test_retry_keeps_existing_terminal_and_receipt(self):
        execution.run(self.root)
        paths=[self.root/execution.E/name for name in ['EXECUTION_RECEIPT.json','terminal-state.json','results.json']]
        before=[p.read_bytes() for p in paths]
        self.preflight.side_effect=execution.Study2DError('already consumed')
        with self.assertRaises(execution.Study2DError):execution.run(self.root)
        self.assertEqual(before,[p.read_bytes() for p in paths])
        self.assertEqual(self.calls.fits,100)

    def test_results_emit_failure_closes_with_fallback_terminal(self):
        original=execution.emit
        def fail(root,name,value):
            if name=='FIT_RESULTS.json':raise OSError('synthetic evidence failure')
            return original(root,name,value)
        with mock.patch.object(execution,'emit',side_effect=fail),self.assertRaises(OSError):
            execution.run(self.root)
        terminal=json.loads((self.root/execution.E/'terminal-state.json').read_text())
        self.assertEqual(terminal['STUDY2_D'],'BLOCKED_POST_RECEIPT_FAILURE')
        self.assertIs(terminal['retry_authorized'],False)


class CounterFixture:
    def __init__(self):
        for name in ('readers','loads','features','fits','predictions','metrics','closes','summaries'):
            setattr(self,name,0)
        self.receipt_at_reader=False


class PreflightTests(TemporaryRoot):
    def fixture(self):
        design=synthetic_design();contract={'fixture':'synthetic'}
        required=set(execution.CODE+execution.TESTS+execution.PROTOCOLS)|{
            execution.AUTH,execution.E+'/AUTHORIZATION.md',execution.E+'/CACHE_CUSTODY_AUTHORIZATION.md',
            execution.E+'/SYNTHETIC_TESTS.json','.github/workflows/study2d-synthetic.yml',
            'configs/governance/phase-scope-v1.json','constraints-ti3c-cnn.txt','requirements-ti3-ml.txt',
            'requirements-ti3c-cnn.txt','src/snbi_fragmentation/study2c_design.py',
            'src/snbi_fragmentation/study2c_models.py',execution.C+'/SPLIT_MANIFEST.json',
            execution.C+'/BACKGROUND_ARTIFACTS.json',execution.C+'/terminal-state.json'}
        blobs={name:b'{}\n' for name in required}
        blobs['constraints-ti3c-cnn.txt']=b'numpy==1.26.4\n'
        blobs[execution.E+'/SYNTHETIC_TESTS.json']=encoded({'status':'PASS','skips':0,'errors':0,'failures':0})
        blobs[execution.E+'/STUDY2_D_ATTRIBUTION_DESIGN.json']=encoded(design)
        blobs[execution.E+'/STUDY2_D_FIT_BUDGET.json']=encoded(execution.expected_fit_budget())
        blobs[execution.E+'/MODEL_CONTRACT.json']=encoded(contract)
        blobs[execution.E+'/TRAIN_INPUT_MANIFEST.json']=encoded({'rows':[{**r,'storage':{}} for r in design['rows']]})
        blobs[execution.C+'/SPLIT_MANIFEST.json']=encoded({'hashes':{'cv_fold_by_group_sha256':execution.FOLD_SHA},'samples':design['rows']})
        freeze={'files':{n:execution.digest(b) for n,b in blobs.items()}}
        blobs[execution.E+'/METHOD_FREEZE.json']=encoded(freeze)
        blobs[execution.E+'/CI_PROOF.json']=encoded(successful_ci())
        def git(root,*args):return execution.BASE if args==('rev-parse','HEAD^') else HEAD
        def git_bytes(root,*args):return blobs[args[1].split(':',1)[1]]
        stack=ExitStack();self.addCleanup(stack.close)
        stack.enter_context(mock.patch.object(execution,'authority'))
        stack.enter_context(mock.patch.object(execution,'preserved_baseline'))
        stack.enter_context(mock.patch.object(execution,'read_text',side_effect=lambda root,n:blobs[n]))
        stack.enter_context(mock.patch.object(execution,'git',side_effect=git))
        stack.enter_context(mock.patch.object(execution,'git_bytes',side_effect=git_bytes))
        stack.enter_context(mock.patch.object(execution.importlib.metadata,'version',return_value='1.26.4'))
        stack.enter_context(mock.patch.object(execution,'validate_inputs'))
        stack.enter_context(mock.patch.dict(sys.modules,{
            'snbi_fragmentation.study2d_design':fake_module('design',validate_attribution_design=lambda d:{'status':'PASS'}),
            'snbi_fragmentation.study2d_models':fake_module('models',method_contract=lambda:contract)}))
        return blobs

    def test_preflight_uses_text_and_creates_no_receipt(self):
        self.fixture();r=execution.preflight(self.root)
        self.assertEqual(r['status'],'PASS')
        self.assertFalse(r['receipt_created'])
        self.assertEqual(r['experimental_opens'],0)
        self.assertFalse((self.root/execution.E/'EXECUTION_RECEIPT.json').exists())

    def test_frozen_byte_divergence_blocks(self):
        blobs=self.fixture();blobs[execution.CODE[0]]=b'changed\n'
        with self.assertRaisesRegex(execution.Study2DError,'frozen bytes'):
            execution.preflight(self.root)

    def test_preexisting_receipt_blocks_before_authority(self):
        self.put(execution.E+'/EXECUTION_RECEIPT.json',{'old':True})
        with mock.patch.object(execution,'authority') as authority,self.assertRaises(execution.Study2DError):
            execution.preflight(self.root)
        authority.assert_not_called()

    def test_existing_terminal_blocks_before_authority(self):
        self.put(execution.E+'/terminal-state.json',{'STATE':'CLOSED_CONSUMED'})
        with mock.patch.object(execution,'authority') as authority,self.assertRaises(execution.Study2DError):
            execution.preflight(self.root)
        authority.assert_not_called()


if __name__=='__main__':
    unittest.main()
