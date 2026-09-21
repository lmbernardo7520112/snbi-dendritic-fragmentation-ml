"""One authorized Study2-C benchmark, with staged group-held-out TEST admission."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path, PurePosixPath
import resource
import shutil
import stat
import subprocess
import time

BASE = "de7670bb8491d2ef01809b33aa326aa3a264324c"
BRANCH = "feat/study2c-group-aware-benchmark"
E = "artifacts/evidence/STUDY2_C_BENCHMARK"
B = "artifacts/evidence/STUDY2_B_CORPUS"
AUTH = "configs/authority/study2c.json"
DATA = "data/derived/study2c"
MIN_FREE = 53687091200
MAX_TEXT = 268435456
AUTH_SHA = "59405ea29a29039246e090e6fa5f72a580a7c183af0dbd1d324d341eb8b05450"
MODELS = ("LOGISTIC_REGRESSION", "SVM_RBF", "RF_REFERENCE", "RF_TUNED", "CNN_V2")
REQUIRED_JOBS = frozenset(("deterministic-contracts", "scientific-synthetic-contracts", "ti3-synthetic-contracts", "ti3b-synthetic-contracts", "ti3c-synthetic-contracts", "ti3d-final-synthetic-contracts", "study2a-synthetic-contracts", "study2b-synthetic-contracts", "study2c-synthetic-contracts"))
CODE = tuple("src/snbi_fragmentation/study2c_"+n+".py" for n in ("design","models","cnn","io","execution"))+("scripts/run_study2c.py",)
TESTS = tuple("tests/test_study2c_"+n+".py" for n in ("design","models","cnn","io","execution"))
PROTOCOLS = tuple(E+"/"+n for n in ("STUDY2_C_PROTOCOL.md","MODEL_CONTRACT.json","SPLIT_MANIFEST.json"))
PINS = {"numpy":"1.26.4","scipy":"1.11.4","scikit-image":"0.24.0","scikit-learn":"1.5.2","torch":"2.4.1+cpu"}
class Study2Error(ValueError):
    """Failure never permits an implicit retry or TEST access."""
def utc_now():
    return datetime.now(timezone.utc).isoformat()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def exact(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b

def safe_path(root, relative):
    parts = PurePosixPath(relative).parts
    if not parts or relative.startswith("/") or any(p in {"", ".", ".."} for p in relative.split("/")) or "\\" in relative:
        raise Study2Error("unsafe relative path")
    current = Path(root)
    if current.is_symlink():
        raise Study2Error("root symlink")
    for part in parts:
        current /= part
        if current.is_symlink():
            raise Study2Error("symlink prohibited")
    return current

def git(root, *args):
    return git_bytes(root, *args).decode().strip()

def git_bytes(root, *args):
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=root,
                          check=True, capture_output=True, timeout=20).stdout


def read_text(root, name):
    if not name.startswith(("src/", "scripts/", "tests/", "configs/", "artifacts/evidence/", ".github/")) and name not in {"requirements-ti3-ml.txt", "requirements-ti3c-cnn.txt", "constraints-ti3c-cnn.txt"}:
        raise Study2Error("text path not allowed")
    if PurePosixPath(name).suffix not in {".json", ".py", ".md", ".txt", ".yml", ".sha256"}:
        raise Study2Error("not text")
    p = safe_path(root, name)
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise Study2Error("regular text required")
        b = f.read(MAX_TEXT+1)
    if len(b) > MAX_TEXT:
        raise Study2Error("text budget")
    b.decode("utf-8", errors="strict")
    return b


def load(root, name):
    return json.loads(read_text(root, name))


def emit(root, name, value):
    p = safe_path(root, E+"/"+name)
    b = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n").encode()
    if len(b)>MAX_TEXT or shutil.disk_usage(root).free-len(b)<MIN_FREE:
        raise Study2Error("metadata or disk budget")
    fd = os.open(p, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as f:
        f.write(b); f.flush(); os.fsync(f.fileno())
    directory = os.open(p.parent, os.O_RDONLY|os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return digest(b)


def verify_ci(proof, head):
    if proof.get("head_sha") != head:
        raise Study2Error("CI wrong HEAD")
    names=[]
    for r in proof.get("runs", []):
        if r.get("headSha") != head or r.get("status") != "completed" or r.get("conclusion") != "success":
            raise Study2Error("CI run not successful")
        for j in r.get("jobs", []):
            if j.get("status") != "completed" or j.get("conclusion") != "success" or not j.get("steps"):
                raise Study2Error("CI job not successful")
            if any(s.get("status") != "completed" or s.get("conclusion") != "success" for s in j["steps"]):
                raise Study2Error("CI step not successful")
            names.append(j["name"])
    if len(names)!=len(REQUIRED_JOBS) or set(names)!=REQUIRED_JOBS:
        raise Study2Error("all nine CI jobs required")
    return names


def authority(root):
    if git(root,"branch","--show-current")!=BRANCH:
        raise Study2Error("wrong branch")
    expected={"schema_version":1,"phase":"STUDY2_C","base_sha":BASE,"branch":BRANCH,
              "authority_sha256":AUTH_SHA,"scientific_invocations_limit":1,
              "cv_fits_limit":80,"development_model_fits":5,"silver_fits":1,
              "final_fits":1,"test_evaluations":1,"human_review":False,
              "augmentation":False,"valid_support_sites":52,"background_tracks":52,
              "terminal_closes_authority":True}
    if not exact(load(root,AUTH),expected) or digest(read_text(root,E+"/AUTHORIZATION.md"))!=AUTH_SHA:
        raise Study2Error("authority divergence")
    return expected


def preserved_baseline(root):
    changed=set(git(root,"diff","--name-only",BASE,"--").splitlines())
    old=set(git(root,"ls-tree","-r","--name-only",BASE).splitlines())
    if (changed&old)-{"scripts/check_ti3_scope.py","configs/governance/phase-scope-v1.json"}:
        raise Study2Error("immutable historical file modified")
    baseline=git_bytes(root,"show",BASE+":scripts/check_ti3_scope.py")
    exact_change=baseline.replace(b'    "src/snbi_fragmentation/ti3c_cnn.py", "tests/test_ti3c_cnn.py",\n',b'    "src/snbi_fragmentation/ti3c_cnn.py", "tests/test_ti3c_cnn.py",\n    "src/snbi_fragmentation/study2c_cnn.py", "tests/test_study2c_cnn.py",\n')
    if read_text(root,"scripts/check_ti3_scope.py")!=exact_change:
        raise Study2Error("scope checker change outside narrow Torch admission")
    previous=json.loads(git_bytes(root,"show",BASE+":configs/governance/phase-scope-v1.json"))
    current=load(root,"configs/governance/phase-scope-v1.json")
    if previous["baseline_sha"]!=current.get("baseline_sha") or previous["schema_version"]!=current.get("schema_version"):
        raise Study2Error("scope anchor changed")
    for domain,rows in previous["domains"].items():
        now={r["path"]:r for r in current["domains"][domain]}
        for r in rows:
            a=dict(r); b=dict(now.get(r["path"],{}))
            if r["path"]=="scripts/check_ti3_scope.py":
                a.pop("blob_sha"); b.pop("blob_sha",None)
            if not exact(a,b):
                raise Study2Error("historical scope entry altered")
    return len(old)


def load_ledger_inputs(root):
    manifest=load(root,B+"/LOCAL_ARTIFACT_MANIFEST.json")
    names={"data/derived/study2b/corpus-index.jsonl":27396,"data/derived/study2b/background-pool.jsonl":70844}
    output={}
    for entry in manifest["artifacts"]:
        name=entry["path"]
        if name not in names:
            continue
        p=safe_path(root,name)
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,"rb") as f:
            if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
                raise Study2Error("metadata regular file required")
            b=f.read(MAX_TEXT+1)
        if len(b)!=entry["size_bytes"] or digest(b)!=entry["sha256"]:
            raise Study2Error("immutable B ledger diverged")
        rows=[json.loads(line) for line in b.splitlines()]
        if len(rows)!=names[name]:
            raise Study2Error("B ledger count changed")
        output[PurePosixPath(name).name]=rows
    if len(output)!=2:
        raise Study2Error("both B metadata ledgers required")
    return output["corpus-index.jsonl"],output["background-pool.jsonl"]


def prepare_plan(root):
    from .study2c_design import build_design
    authority(root)
    if git(root,"rev-parse","HEAD")!=BASE:
        raise Study2Error("plan must precede scientific method freeze")
    for n in ("PLAN_RECEIPT.json","SPLIT_MANIFEST.json","terminal-state.json"):
        if safe_path(root,E+"/"+n).exists():
            raise Study2Error("plan already consumed")
    tests=load(root,E+"/SYNTHETIC_TESTS.json")
    if tests.get("status")!="PASS":
        raise Study2Error("synthetic tests required before real metadata split")
    emit(root,"PLAN_RECEIPT.json",{"created_at_utc":utc_now(),"metadata_only":True,
        "design_sha256":digest(read_text(root,CODE[0])),"source_pixel_reads":0})
    design=build_design(*load_ledger_inputs(root))
    if design.get("status")!="PASS":
        emit(root,"terminal-state.json",{"STUDY2_C":"BLOCKED_BACKGROUND_GROUP_CAPACITY","detail":design,"scientific_fits":0})
        return design
    emit(root,"SPLIT_MANIFEST.json",design)
    return {"status":"PASS","counts":design["counts"],"test_state":"LOGICALLY_SEALED_TEST","source_pixel_reads":0}


def preflight(root):
    for n in ("EXECUTION_RECEIPT.json","results.json","terminal-state.json"):
        if safe_path(root,E+"/"+n).exists():
            raise Study2Error("authority consumed; no retry")
    for n in ("cachetrain_dev.bin","cachetrain_dev.jsonl","cachetest.bin","cachetest.jsonl"):
        if safe_path(root,DATA+"/"+n).exists():
            raise Study2Error("preexisting Study2-C cache; no overwrite or retry")
    authority(root)
    if shutil.disk_usage(root).free<MIN_FREE+2147483648+MAX_TEXT:
        raise Study2Error("disk reserve insufficient")
    head=git(root,"rev-parse","HEAD")
    if git(root,"rev-parse","HEAD^")!=BASE:
        raise Study2Error("method freeze must directly follow merge")
    preserved_baseline(root)
    for line in read_text(root,"constraints-ti3c-cnn.txt").decode().splitlines():
        name,version=line.split("==")
        if importlib.metadata.version(name)!=version:
            raise Study2Error("dependency pin divergence: "+name)
    raw=read_text(root,E+"/METHOD_FREEZE.json")
    if raw!=git_bytes(root,"show",head+":"+E+"/METHOD_FREEZE.json"):
        raise Study2Error("method freeze differs from committed blob")
    freeze=json.loads(raw)
    required=set(CODE+TESTS+PROTOCOLS)|{AUTH,E+"/AUTHORIZATION.md",E+"/SYNTHETIC_TESTS.json",
        ".github/workflows/study2c-synthetic.yml","scripts/check_ti3_scope.py","configs/governance/phase-scope-v1.json",
        B+"/LOCAL_ARTIFACT_MANIFEST.json",B+"/FRAME_HASHES.json","src/snbi_fragmentation/study2b_corpus.py","src/snbi_fragmentation/study2b_streaming.py"}
    if not required<=set(freeze.get("files",{})):
        raise Study2Error("incomplete freeze")
    for n,sha in freeze["files"].items():
        b=read_text(root,n)
        if digest(b)!=sha or b!=git_bytes(root,"show",head+":"+n):
            raise Study2Error("frozen bytes differ: "+n)
    tests=load(root,E+"/SYNTHETIC_TESTS.json")
    if tests.get("status")!="PASS" or any(tests.get(k)!=0 for k in ("skips","failures","errors")):
        raise Study2Error("synthetic validation not passed")
    design=load(root,E+"/SPLIT_MANIFEST.json")
    if design.get("status")!="PASS":
        raise Study2Error("metadata split gate not passed")
    jobs=verify_ci(load(root,E+"/CI_PROOF.json"),head)
    return {"status":"PASS","head_sha":head,"freeze_text_count":len(freeze["files"]),
            "ci_jobs":jobs,"source_opens":0,"receipt_created":False,"free_disk_bytes":shutil.disk_usage(root).free}


def select_samples(design, splits, regime="GOLD_ONLY"):
    if regime not in {"GOLD_ONLY","GOLD_PLUS_SILVER"}:
        raise Study2Error("unknown regime")
    tiers={"GOLD","BACKGROUND"}|({"SILVER"} if regime=="GOLD_PLUS_SILVER" else set())
    return [r for r in design["samples"] if r["split"] in splits and r["tier"] in tiers]


def choose_family(benchmarks):
    if set(benchmarks)!=set(MODELS):
        raise Study2Error("five models required")
    return max(MODELS,key=lambda f:(benchmarks[f]["development"]["primary_gmba"],
        benchmarks[f]["development"]["observation"]["balanced_accuracy"],-MODELS.index(f)))


class AccessState:
    def __init__(self,receipt_sha,head,design):
        self.stage="DEVELOPMENT"
        self.receipt_sha=receipt_sha
        self.head=head
        self.final_fit_sha=None
        self.rows={r["sample_id"]:r for r in design["samples"]}
        if len(self.rows)!=len(design["samples"]):
            raise Study2Error("duplicate frozen sample identity")

    def grant(self,action,phase,rows):
        if action not in {"LOAD_POSITIVE_ROWS","MATERIALIZE_BACKGROUNDS"}:
            raise Study2Error("unknown input action")
        if not rows or any(not exact(r,self.rows.get(r.get("sample_id"))) for r in rows):
            raise Study2Error("input rows differ from frozen split manifest")
        kind="positive" if action=="LOAD_POSITIVE_ROWS" else "background"
        if any(r["kind"]!=kind for r in rows):
            raise Study2Error("input action/sample kind mismatch")
        allowed={"DEVELOPMENT":{"TRAIN","DEVELOPMENT","TRAIN_DEVELOPMENT"},
                 "SILVER":{"TRAIN_SILVER"},"FINAL_TRAIN":{"FINAL_TRAIN"},"TEST":{"TEST"}}
        if phase not in allowed.get(self.stage,set()):
            raise Study2Error("input access denied before stage/selection/final fit")
        if phase=="TEST" and not self.final_fit_sha:
            raise Study2Error("TEST requires durable final fit")
        if phase!="TEST" and any(r.get("split")=="TEST" for r in rows):
            raise Study2Error("TEST cannot enter earlier stages")
        proof={"authorized":True,"execution_receipt_sha256":self.receipt_sha,"method_freeze_sha":self.head}
        if phase=="TEST":
            proof.update(final_fit_durable=True,final_fit_freeze_sha256=self.final_fit_sha)
        return proof


def progress(event):
    print(json.dumps({"progress":event},ensure_ascii=False,allow_nan=False),flush=True)


def _execute(root):
    proof=preflight(root)
    design=load(root,E+"/SPLIT_MANIFEST.json")
    receipt_sha=emit(root,"EXECUTION_RECEIPT.json",{"created_at_utc":utc_now(),
        "preflight":proof,"method_freeze_sha":proof["head_sha"],"attempt":1,
        "cv_fits_budget":80,"development_fits_budget":5,"silver_fits_budget":1,
        "final_fits_budget":1,"test_evaluations_budget":1})
    from .study2c_io import CorpusAccess
    from .study2c_design import group_equal_weights,metric_bundle
    from .study2c_models import extract_lbp20,fit_classical,predict_classical,cv_search
    from .study2c_cnn import fit_cnn,predict_cnn
    import numpy as np
    state=AccessState(receipt_sha,proof["head_sha"],design)
    audit={}
    counts={"scientific_invocations":1,"cv_fits_started":0,"cv_fits_completed":0,
            "development_fits_started":0,"development_fits_completed":0,
            "silver_fits_started":0,"silver_fits_completed":0,
            "final_fits_started":0,"final_fits_completed":0,
            "development_evaluations":0,"silver_development_evaluations":0,
            "test_prediction_calls":0,"test_evaluations":0,"retries":0}
    start=time.perf_counter()
    cache,features={},{}
    cache_manifests=[]
    benchmarks={}
    selected_family=regime=None
    test_state="LOGICALLY_SEALED_TEST"
    failure=None
    accessor=CorpusAccess(root,state.grant,audit)

    def receive(rows,phase,background=False):
        missing=[r for r in rows if r["sample_id"] not in cache]
        if not missing:
            return
        if background:
            array,manifest=accessor.materialize_backgrounds(missing,phase)
            cache_manifests.append(manifest)
        else:
            array=accessor.load_positive_rows(missing,phase)
        if array.dtype!=np.uint8 or array.shape!=(len(missing),2,65,65):
            raise Study2Error("I/O shape or order contract")
        for row,pair in zip(missing,array,strict=True):
            cache[row["sample_id"]]=pair

    def inputs(rows,family):
        ids=[r["sample_id"] for r in rows]
        if family=="CNN_V2":
            return np.stack([cache[i] for i in ids])
        missing=[i for i in ids if i not in features]
        if missing:
            values=extract_lbp20(np.stack([cache[i] for i in missing]))
            for i,f in zip(missing,values,strict=True):
                features[i]=f
        return np.stack([features[i] for i in ids])

    def fit(family,params,rows,purpose):
        if any(r["split"]=="TEST" for r in rows):
            raise Study2Error("TEST in fit")
        weights=group_equal_weights(rows)
        x=inputs(rows,family)
        counts[purpose+"_fits_started"]+=1
        progress({"stage":purpose,"family":family,"event":"fit_start","samples":len(rows)})
        if family=="CNN_V2":
            model,metadata=fit_cnn(x,rows,weights,progress=progress)
        else:
            model,metadata=fit_classical(family,params,x,rows,weights)
        counts[purpose+"_fits_completed"]+=1
        progress({"stage":purpose,"family":family,"event":"fit_complete"})
        return model,metadata

    def predict(model,family,rows):
        x=inputs(rows,family)
        output=predict_cnn(model,x) if family=="CNN_V2" else predict_classical(model,x)
        if len(output["predictions"])!=len(rows):
            raise Study2Error("prediction count differs")
        return output

    def prediction_record(rows,output):
        return {"sample_ids":[r["sample_id"] for r in rows],**output}

    def cv_progress(event):
        # Report actual calls emitted by the frozen classical search.
        if event.get("event")=="CV_FIT_START":
            counts["cv_fits_started"]+=1
            if counts["cv_fits_started"]>80:
                raise Study2Error("CV started budget exceeded")
        elif event.get("event")=="CV_FIT_COMPLETE":
            counts["cv_fits_completed"]+=1
            if counts["cv_fits_completed"]>counts["cv_fits_started"]:
                raise Study2Error("CV completion without fit start")
        progress(event)

    try:
        train=select_samples(design,{"TRAIN"})
        dev=select_samples(design,{"DEVELOPMENT"})
        receive([r for r in train if r["kind"]=="positive"],"TRAIN")
        receive([r for r in dev if r["kind"]=="positive"],"DEVELOPMENT")
        receive([r for r in train+dev if r["kind"]=="background"],"TRAIN_DEVELOPMENT",True)
        emit(root,"DEVELOPMENT_MATERIALIZATION.json",{"cache_manifests":cache_manifests,
            "gold_train_count":sum(r["label"]==1 for r in train),
            "gold_development_count":sum(r["label"]==1 for r in dev),"test_rows_read":0})
        frozen_parameters={}
        for family in MODELS:
            cv_report={"status":"NOT_APPLICABLE_NO_TUNING","fit_calls":0}
            params={}
            if family in {"LOGISTIC_REGRESSION","SVM_RBF","RF_TUNED"}:
                expected={"LOGISTIC_REGRESSION":12,"SVM_RBF":36,"RF_TUNED":32}[family]
                before=counts["cv_fits_completed"]
                started_before=counts["cv_fits_started"]
                params,cv_report=cv_search(family,inputs(train,family),train,
                    design["cv_fold_by_group"],progress=cv_progress)
                if cv_report["fit_calls"]!=expected or counts["cv_fits_completed"]-before!=expected or counts["cv_fits_started"]-started_before!=expected:
                    raise Study2Error("CV call budget mismatch")
                emit(root,family+"_CV.json",cv_report)
            frozen_parameters[family]=params
            model,fit_meta=fit(family,params,train,"development")
            training_output=predict(model,family,train)
            training_metrics=metric_bundle(train,training_output["predictions"])
            dev_output=predict(model,family,dev)
            counts["development_evaluations"]+=1
            dev_metrics=metric_bundle(dev,dev_output["predictions"])
            record={"chosen_parameters":params,"cv":cv_report,"fit":fit_meta,
                "train":training_metrics,"development":dev_metrics,
                "train_predictions":prediction_record(train,training_output),
                "development_predictions":prediction_record(dev,dev_output),
                "sample_counts":{"train":len(train),"development":len(dev)},
                "group_counts":{"train":len({r['group_id'] for r in train}),"development":len({r['group_id'] for r in dev})}}
            emit(root,family+"_DEVELOPMENT.json",record)
            benchmarks[family]=record
            del model
        if counts["cv_fits_completed"]!=80 or counts["development_fits_completed"]!=5:
            raise Study2Error("benchmark budget not fulfilled")
        selected_family=choose_family(benchmarks)
        emit(root,"FAMILY_SELECTION.json",{"selected_model_family":selected_family,
            "method":"DEV_GMBA_then_observation_BA_then_frozen_family_order",
            "development_scores":{f:{"gmba":v["development"]["primary_gmba"],
                "observation_ba":v["development"]["observation"]["balanced_accuracy"]} for f,v in benchmarks.items()},
            "family_selection_closed":True,"test_rows_read":0})
        state.stage="SILVER"
        silver_train=select_samples(design,{"TRAIN"},"GOLD_PLUS_SILVER")
        receive([r for r in silver_train if r["tier"]=="SILVER"],"TRAIN_SILVER")
        model,silver_fit=fit(selected_family,frozen_parameters[selected_family],silver_train,"silver")
        silver_output=predict(model,selected_family,dev)
        counts["silver_development_evaluations"]+=1
        silver_metric=metric_bundle(dev,silver_output["predictions"])
        gold_metric=benchmarks[selected_family]["development"]
        regime="GOLD_PLUS_SILVER" if silver_metric["primary_gmba"]>gold_metric["primary_gmba"] else "GOLD_ONLY"
        emit(root,"SILVER_ABLATION.json",{"family":selected_family,"fit":silver_fit,
            "gold_development_reference":gold_metric,"gold_plus_silver_development":silver_metric,
            "gold_plus_silver_predictions":prediction_record(dev,silver_output),
            "selected_supervision_regime":regime,"gold_reference_reexecuted":False,
            "additional_tuning":False,"test_rows_read":0})
        del model
        final_rows=select_samples(design,{"TRAIN","DEVELOPMENT"},regime)
        pipeline_sha=emit(root,"FINAL_PIPELINE.json",{"created_at_utc":utc_now(),
            "method_freeze_sha":proof["head_sha"],"selected_model_family":selected_family,
            "selected_supervision_regime":regime,"hyperparameters":frozen_parameters[selected_family],
            "training_ids_sha256":digest(json.dumps([r['sample_id'] for r in final_rows]).encode()),
            "sample_count":len(final_rows),"group_count":len({r['group_id'] for r in final_rows}),
            "test_state":"LOGICALLY_SEALED_TEST","selection_closed":True})
        state.stage="FINAL_TRAIN"
        if regime=="GOLD_PLUS_SILVER":
            receive([r for r in final_rows if r["tier"]=="SILVER"],"FINAL_TRAIN")
        model,final_meta=fit(selected_family,frozen_parameters[selected_family],final_rows,"final")
        state.final_fit_sha=emit(root,"FINAL_FIT_FREEZE.json",{"created_at_utc":utc_now(),
            "final_pipeline_sha256":pipeline_sha,"fit_metadata":final_meta,
            "fit_completed":True,"fit_calls":1,"test_not_admitted":True,
            "scope":"Durable fit completion/configuration record; no model binary serialization"})
        state.stage="TEST"
        test_state="CONSUMED_ACCESS_STARTED"
        test=select_samples(design,{"TEST"})
        emit(root,"TEST_ACCESS_RECEIPT.json",{"created_at_utc":utc_now(),
            "final_pipeline_sha256":pipeline_sha,"final_fit_freeze_sha256":state.final_fit_sha,
            "test_samples":len(test),"positive_groups":10,"background_groups":10})
        receive([r for r in test if r["kind"]=="positive"],"TEST")
        receive([r for r in test if r["kind"]=="background"],"TEST",True)
        counts["test_prediction_calls"]+=1
        output=predict(model,selected_family,test)
        prediction_sha=emit(root,"TEST_PREDICTIONS.json",{
            "final_fit_freeze_sha256":state.final_fit_sha,**prediction_record(test,output)})
        metrics=metric_bundle(test,output["predictions"])
        counts["test_evaluations"]+=1
        test_state="CONSUMED"
        emit(root,"TEST_METRICS.json",{"prediction_sha256":prediction_sha,"metrics":metrics,
            "samples":len(test),"group_count":len({r['group_id'] for r in test}),
            "labels":[r['label'] for r in test],"sample_ids":[r['sample_id'] for r in test]})
        del model
    except Exception as exc:
        failure=f"{type(exc).__name__}: {exc}"
    finally:
        accessor.close()
    success=failure is None and counts["cv_fits_completed"]==80 and counts["development_fits_completed"]==5 and counts["silver_fits_completed"]==1 and counts["final_fits_completed"]==1 and counts["test_evaluations"]==1
    terminal={"STUDY2_C":"PASS" if success else "BLOCKED_PARTIAL_EXECUTION",
        "STUDY2_C_METHOD":"GROUP_AWARE_MULTIMODAL_BENCHMARK","VALID_SUPPORT_SITES":52,
        "VALID_SUPPORT_SITE_DOMAIN_ONLY":True,"SELECTED_BACKGROUND_TRACKS":52,
        "TRAIN_POSITIVE_GROUPS":32,"TRAIN_BACKGROUND_GROUPS":32,"DEV_POSITIVE_GROUPS":10,
        "DEV_BACKGROUND_GROUPS":10,"TEST_POSITIVE_GROUPS":10,"TEST_BACKGROUND_GROUPS":10,
        "MODELS_EVALUATED":counts["development_evaluations"],"SELECTED_MODEL_FAMILY":selected_family,
        "SELECTED_SUPERVISION_REGIME":regime,"FINAL_STUDY2_PIPELINE":None if selected_family is None else {"family":selected_family,"supervision":regime},
        "TEST_STATE":test_state,"SCIENTIFIC_TEST_EVALUATIONS":counts["test_evaluations"],
        "HUMAN_REVIEW_USED":False,"AUGMENTATION_USED":False,"EXTERNAL_GENERALIZATION_CLAIM":False,
        "STUDY2_CLOSED":True,"STATE":"CLOSED_CONSUMED","MERGE_AUTHORIZED":False,
        "CURRENT_AUTHORIZED_ACTIVITY":"NONE_AWAITING_AUTHOR_DECISION"}
    emit(root,"IO_AUDIT.json",audit)
    emit(root,"BACKGROUND_ARTIFACTS.json",{"manifests":cache_manifests})
    emit(root,"results.json",{"status":terminal["STUDY2_C"],"failure":failure,
        "terminal":terminal,"counts":counts,"runtime_seconds":time.perf_counter()-start,
        "peak_python_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "free_disk_after":shutil.disk_usage(root).free,"method_freeze_sha":proof["head_sha"]})
    emit(root,"terminal-state.json",terminal)
    return terminal


def run(root):
    consumed=safe_path(root,E+"/EXECUTION_RECEIPT.json").exists()
    try:
        return _execute(root)
    except Exception as exc:
        if not consumed and safe_path(root,E+"/EXECUTION_RECEIPT.json").exists() and not safe_path(root,E+"/terminal-state.json").exists():
            result={"STUDY2_C":"BLOCKED_POST_RECEIPT_FAILURE","STATE":"CLOSED_CONSUMED",
                    "failure":f"{type(exc).__name__}: {exc}","retry_authorized":False,
                    "counters":"Only completed durable records certify progress",
                    "CURRENT_AUTHORIZED_ACTIVITY":"NONE_AWAITING_AUTHOR_DECISION"}
            emit(root,"terminal-state.json",result)
            return result
        raise
