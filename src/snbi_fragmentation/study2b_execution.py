"""One-use Study2-B corpus construction; no I/O or science on import.

Only four authorized sources can be opened, after durable exclusive receipts.
Study2-A and Study1 remain immutable; no learner or feature extractor is used.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import resource
import shutil
import stat
import subprocess

BASE = "d4ef00bf1e1d84d49d4e3f2dce0d18f683598a4c"
BRANCH = "feat/study2b-dense-multimodal-corpus"
EVIDENCE = "artifacts/evidence/STUDY2_B_CORPUS"
AUTHORITY = "configs/authority/study2b.json"
A = "artifacts/evidence/STUDY2_A_ANNOTATION_MINING"
LEGACY = "artifacts/evidence/TI3_B_SOLUTAL/materialization-manifest.json"
LEGACY_IO = "artifacts/evidence/TI3_B_SOLUTAL/io-audit.json"
INPUT_MANIFEST = A + "/LOCAL_ARTIFACT_MANIFEST.json"
DATA = "data/derived/study2b"
CORE_PATHS = ("src/snbi_fragmentation/study2b_corpus.py",
              "src/snbi_fragmentation/study2b_streaming.py",
              "src/snbi_fragmentation/study2b_execution.py", "scripts/run_study2b.py")
TEST_PATHS = ("tests/test_study2b_corpus.py", "tests/test_study2b_streaming.py",
              "tests/test_study2b_execution.py")
PROTOCOL_PATHS = tuple(EVIDENCE + "/" + s for s in (
    "STUDY2_B_PROTOCOL.md", "STUDY2_B_CORPUS_SCHEMA.json",
    "STUDY2_B_BACKGROUND_CONTRACT.md", "STUDY2_B_STORAGE_CONTRACT.md",
    "STUDY2_B_CLAIM_SCOPE.md"))
INPUT_PATHS = (A + "/SITE_LEDGER.json", A + "/METRIC_SEMANTICS_RECONCILIATION.json",
               A + "/LEGACY_SITE_MAPPING.json", INPUT_MANIFEST, LEGACY, LEGACY_IO,
               "artifacts/metadata/ti2-pilot-manifest.json",
               "artifacts/evidence/TI2R_FRAG_DIRECT/ESM3-to-ESM1-freeze.json",
               "artifacts/evidence/TI2R_FRAG_DIRECT/ESM6-to-ESM4-freeze.json",
               "artifacts/evidence/TI2R_SOLUTE_HOLDOUT/repair-1/results.json")
REQUIRED_JOBS = frozenset({"deterministic-contracts", "scientific-synthetic-contracts",
    "ti3-synthetic-contracts", "ti3b-synthetic-contracts", "ti3c-synthetic-contracts",
    "ti3d-final-synthetic-contracts", "study2a-synthetic-contracts", "study2b-synthetic-contracts"})
MAX_METADATA = 268435456
MAX_PATCH = 2147483648
MIN_FREE = 53687091200
PAIR_BYTES = 8450
EXPECTED_TIERS = {"GOLD": 7941, "SILVER": 5737,
                  "UNLABELED_PRE": 8911, "UNLABELED_PERSISTENCE": 4807}
STATES = {"DIRECT_VALID": "GOLD", "TEMPORAL_SUPPORTED_AMBIGUOUS": "SILVER",
          "PRE_FIRST_CONFIDENT_ANNOTATION": "UNLABELED_PRE",
          "PERSISTENCE_EXPECTED_UNRESOLVED": "UNLABELED_PERSISTENCE"}
METRICS = {"AMBIGUOUS_COMPONENTS_TOTAL": 24246,
    "AMBIGUOUS_UNSUPPORTED_BY_KNOWN_SITE": 18670,
    "AMBIGUOUS_EXPLAINED_BY_ONE_KNOWN_SITE": 5415,
    "AMBIGUOUS_EXPLAINED_BY_MULTIPLE_KNOWN_SITES": 161,
    "SMALL_COMPONENTS_TOTAL": 292, "UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS": 18962,
    "NON_VALID_COMPONENTS_TOTAL": 24538}

class Study2Error(ValueError):
    """No failed contract grants source access or a retry."""

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

def text_bytes(root, relative):
    # Experimental/local aggregate paths are never accepted by this reader.
    if relative != "artifacts/metadata/ti2-pilot-manifest.json" and not relative.startswith(("src/", "scripts/", "tests/", "configs/", "artifacts/evidence/", ".github/")):
        raise Study2Error("text path outside allowlist")
    if PurePosixPath(relative).suffix not in {".py", ".json", ".md", ".txt", ".sha256", ".yml"}:
        raise Study2Error("not an allowed textual suffix")
    p = safe_path(root, relative)
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise Study2Error("text input must be regular")
        result = f.read()
    result.decode("utf-8", errors="strict")
    return result

def load_json(root, relative):
    return json.loads(text_bytes(root, relative))

def exclusive_json(root, relative, value):
    p = safe_path(root, relative)
    content = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    if len(content) > MAX_METADATA:
        raise Study2Error("metadata file exceeds declared budget")
    if shutil.disk_usage(root).free - len(content) < MIN_FREE:
        raise Study2Error("metadata write would consume reserved disk space")
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    directory = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return {"path": relative, "size_bytes": len(content), "sha256": digest(content)}

def git(root, *args):
    return git_bytes(root, *args).decode().strip()

def git_bytes(root, *args):
    return subprocess.run(["git", "--no-optional-locks", *args], cwd=root,
                          check=True, capture_output=True, timeout=20).stdout

def check_ci(proof, head):
    if not isinstance(proof, dict) or proof.get("head_sha") != head:
        raise Study2Error("CI proof must match exact method-freeze HEAD")
    runs = proof.get("runs")
    if not isinstance(runs, list) or not runs:
        raise Study2Error("missing CI runs")
    jobs = []
    for run in runs:
        if run.get("headSha") != head or run.get("status") != "completed" or run.get("conclusion") != "success":
            raise Study2Error("CI run incomplete or unsuccessful")
        for job in run.get("jobs", []):
            if job.get("status") != "completed" or job.get("conclusion") != "success":
                raise Study2Error("CI job incomplete or unsuccessful")
            if not job.get("steps") or any(s.get("status") != "completed" or s.get("conclusion") != "success" for s in job["steps"]):
                raise Study2Error("CI steps must all be successful")
            jobs.append(job["name"])
    if len(jobs) != len(REQUIRED_JOBS) or set(jobs) != REQUIRED_JOBS:
        raise Study2Error("all eight exact historical/new CI jobs required")
    return sorted(jobs)

def preserved_baseline(root):
    prior = set(git(root, "ls-tree", "-r", "--name-only", BASE).splitlines())
    changed = set(git(root, "diff", "--name-only", BASE, "--").splitlines())
    if (changed & prior) - {"configs/governance/phase-scope-v1.json"}:
        raise Study2Error("historical tracked content changed")
    old_scope = json.loads(git(root, "show", BASE + ":configs/governance/phase-scope-v1.json"))
    new_scope = load_json(root, "configs/governance/phase-scope-v1.json")
    if old_scope["baseline_sha"] != new_scope.get("baseline_sha") or old_scope["schema_version"] != new_scope.get("schema_version"):
        raise Study2Error("operational scope baseline changed")
    if set(old_scope["domains"]) != set(new_scope.get("domains", {})):
        raise Study2Error("operational domains changed")
    for domain, rows in old_scope["domains"].items():
        current = {r["path"]: r for r in new_scope["domains"][domain]}
        if any(not exact(row, current.get(row["path"])) for row in rows):
            raise Study2Error("historical scope entry changed")
    return len(prior)


def load_inputs(root):
    """Authenticate only the two existing JSONL metadata files, never pixels."""
    manifest = load_json(root, INPUT_MANIFEST)
    allowed = {"data/derived/study2/OBSERVATION_LEDGER.jsonl": 27396,
               "data/derived/study2/candidate-components.jsonl": 32479}
    if {r['path'] for r in manifest['artifacts']} != set(allowed):
        raise Study2Error('unexpected derived input inventory')
    loaded = {}
    for entry in manifest['artifacts']:
        name = entry['path']
        p = safe_path(root, name)
        fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as f:
            info = os.fstat(f.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size != entry['size_bytes']:
                raise Study2Error('metadata input size/type mismatch')
            content = f.read(MAX_METADATA + 1)
        if len(content) != entry['size_bytes'] or digest(content) != entry['sha256']:
            raise Study2Error('derived input custody mismatch')
        rows = [json.loads(line) for line in content.splitlines()]
        if len(rows) != allowed[name] or len(rows) != entry['record_count']:
            raise Study2Error('derived input count mismatch')
        loaded[Path(name).name] = rows
    observations = loaded['OBSERVATION_LEDGER.jsonl']
    if Counter(STATES.get(r.get('status'), 'UNKNOWN') for r in observations) != EXPECTED_TIERS:
        raise Study2Error('historical observation tiers changed')
    sites = load_json(root, A + '/SITE_LEDGER.json')
    if len(sites) != 87 or len({r['site_id'] for r in sites}) != 87:
        raise Study2Error('historical site count changed')
    reconciliation = load_json(root, A + '/METRIC_SEMANTICS_RECONCILIATION.json')
    if not exact(reconciliation['canonical_metrics'], METRICS):
        raise Study2Error('canonical metric reconciliation changed')
    return sites, observations, loaded['candidate-components.jsonl'], dict(METRICS)


def build_authenticated_plan(root):
    from .study2b_corpus import build_plan
    return build_plan(*load_inputs(root))


def preflight(root, mode):
    if mode not in {'legacy', 'full'}:
        raise Study2Error('unknown mode')
    for filename in ('terminal-state.json', 'results.json'):
        if safe_path(root, EVIDENCE + '/' + filename).exists():
            raise Study2Error('authority permanently closed')
    receipt = 'LEGACY_RECEIPT.json' if mode == 'legacy' else 'EXECUTION_RECEIPT.json'
    if safe_path(root, EVIDENCE + '/' + receipt).exists():
        raise Study2Error('invocation already consumed')
    if git(root, 'branch', '--show-current') != BRANCH:
        raise Study2Error('wrong branch')
    cfg = load_json(root, AUTHORITY)
    fixed = {'schema_version': 1, 'phase': 'STUDY2_B', 'base_sha': BASE, 'branch': BRANCH,
             'sources': ['ESM1', 'ESM2', 'ESM4', 'ESM5'], 'ml': False, 'human_review': False,
             'scientific_runs_limit': 1, 'patch_side': 65, 'patch_radius': 32,
             'channels': ['STRUCTURAL_Y', 'RELATIVE_SOLUTE_FIELD_Y'],
             'dtype': 'uint8', 'max_patch_cache_bytes': MAX_PATCH,
             'max_temp_bytes': MAX_METADATA, 'min_free_disk_reserve_bytes': MIN_FREE,
             'metadata_output_budget_bytes': MAX_METADATA,
             'legacy_fixture_count': 50, 'expected_input_records': 27396,
             'terminal_closes_authority': True}
    if set(cfg) != set(fixed) | {'authority_sha256', 'decoder_gate_authority_sha256'}:
        raise Study2Error('authority schema mismatch')
    if any(not exact(cfg.get(k), v) for k, v in fixed.items()):
        raise Study2Error('authority configuration mismatch')
    for name, key in [('AUTHORIZATION.md', 'authority_sha256'),
                      ('DECODER_GATE_AUTHORIZATION.md', 'decoder_gate_authority_sha256')]:
        if digest(text_bytes(root, EVIDENCE + '/' + name)) != cfg[key]:
            raise Study2Error('author decision custody mismatch')
    for package, pin in [('numpy', '1.26.4'), ('scipy', '1.11.4')]:
        if importlib.metadata.version(package) != pin:
            raise Study2Error('dependency divergence')
    if shutil.disk_usage(root).free < MIN_FREE + MAX_METADATA + 27396 * PAIR_BYTES:
        raise Study2Error('insufficient disk reserve for bounded corpus')
    preserved = preserved_baseline(root)
    tests = load_json(root, EVIDENCE + '/SYNTHETIC_TESTS.json')
    if tests.get('status') != 'PASS' or any(tests.get(k) != 0 for k in ('skips', 'failures', 'errors')):
        raise Study2Error('synthetic contracts not passed')
    head = git(root, 'rev-parse', 'HEAD')
    proof = {'status': 'PASS', 'mode': mode, 'head_sha': head,
             'historical_tracked_paths_preserved': preserved,
             'experimental_source_opens': 0, 'receipt_created': False,
             'free_disk_bytes': shutil.disk_usage(root).free}
    if mode == 'legacy':
        if head != BASE:
            raise Study2Error('legacy gate must precede method freeze')
        proof['implementation_hashes'] = {p: digest(text_bytes(root, p))
                                          for p in (*CORE_PATHS, AUTHORITY, *PROTOCOL_PATHS)}
    else:
        if git(root, 'rev-parse', 'HEAD^') != BASE:
            raise Study2Error('method freeze must be direct child of integration')
        freeze_path = EVIDENCE + '/METHOD_FREEZE.json'
        raw = text_bytes(root, freeze_path)
        if raw != git_bytes(root, 'show', head + ':' + freeze_path):
            raise Study2Error('freeze differs from committed bytes')
        freeze = json.loads(raw)
        required = set(CORE_PATHS + TEST_PATHS + PROTOCOL_PATHS + INPUT_PATHS) | {
            AUTHORITY, EVIDENCE + '/AUTHORIZATION.md', EVIDENCE + '/DECODER_GATE_AUTHORIZATION.md',
            EVIDENCE + '/SYNTHETIC_TESTS.json', EVIDENCE + '/LEGACY_REPRODUCTION.json',
            '.github/workflows/study2b-synthetic.yml', 'configs/governance/phase-scope-v1.json'}
        if not required <= set(freeze.get('files', {})):
            raise Study2Error('incomplete freeze')
        for path, sha in freeze['files'].items():
            content = text_bytes(root, path)
            if digest(content) != sha or content != git_bytes(root, 'show', head + ':' + path):
                raise Study2Error('frozen text differs: ' + path)
        legacy = load_json(root, EVIDENCE + '/LEGACY_REPRODUCTION.json')
        if legacy.get('status') != 'PASS' or legacy.get('legacy_fixture_pair_hash_matches') != 50:
            raise Study2Error('legacy reproduction not passed')
        for path, sha in legacy['implementation_hashes'].items():
            if digest(text_bytes(root, path)) != sha:
                raise Study2Error('implementation changed after legacy gate')
        proof['ci_jobs'] = check_ci(load_json(root, EVIDENCE + '/CI_PROOF.json'), head)
        proof['frozen_text_count'] = len(freeze['files'])
        for filename in ('multimodal_patches_uint8.bin', 'corpus-index.jsonl', 'background-pool.jsonl'):
            if safe_path(root, DATA + '/' + filename).exists():
                raise Study2Error('output already exists; no overwrite or retry')
    return proof


def arm(root, mode, proof):
    filename = 'LEGACY_RECEIPT.json' if mode == 'legacy' else 'EXECUTION_RECEIPT.json'
    return exclusive_json(root, EVIDENCE + '/' + filename, {
        'phase': 'STUDY2_B', 'mode': mode, 'created_at_utc': utc_now(), 'attempt': 1,
        'head_sha': proof['head_sha'], 'authority_sha256': digest(text_bytes(root, AUTHORITY)),
        'preflight': proof, 'sources': ['ESM1', 'ESM2', 'ESM4', 'ESM5']})


def paired_frames(reader, structural_source, solutal_source):
    if (structural_source, solutal_source) not in {('ESM1', 'ESM2'), ('ESM4', 'ESM5')}:
        raise Study2Error('cross-acquisition/source pair forbidden')
    for s, q in zip(reader.iter_frames(structural_source), reader.iter_frames(solutal_source), strict=True):
        if s[0] != q[0]:
            raise Study2Error('temporal pair mismatch')
        yield s[0], s[1], q[1], s[2], q[2]


def legacy_matches(plan, fixtures):
    """Exact canonical-coordinate overlaps; backgrounds have no site match."""
    keys = {(r['structural_source_id'], r['frame_index'], r['center_x'], r['center_y']): r
            for r in plan['records']}
    if len(keys) != len(plan['records']):
        raise Study2Error('canonical coordinate collision cannot silently merge site identities')
    return {s['sample_id']: keys[(s['structural_source_id'], s['frame_index'], s['center_x'], s['center_y'])]
            for s in fixtures if s['sample_id'].startswith('positive|')
            and (s['structural_source_id'], s['frame_index'], s['center_x'], s['center_y']) in keys}


def _run_legacy(root):
    from .study2b_corpus import legacy_patch_pair
    from .study2b_streaming import AuthenticatedSources
    proof = preflight(root, 'legacy')
    plan = build_authenticated_plan(root)
    fixtures = load_json(root, LEGACY)['samples']
    if len(fixtures) != 50 or len({s['sample_id'] for s in fixtures}) != 50:
        raise Study2Error('legacy inventory must contain exactly 50 unique pairs')
    overlaps = legacy_matches(plan, fixtures)
    native = {(r['source_id'], r['frame_index']): r['expected_sha256']
              for r in load_json(root, LEGACY_IO)['entries'] if r['opens'] == 1}
    arm(root, 'legacy', proof)
    audit, checks, frame_checks = {}, [], []
    failure = None
    try:
        with AuthenticatedSources(mode='legacy', audit=audit) as reader:
            for structural, solutal in [('ESM1', 'ESM2'), ('ESM4', 'ESM5')]:
                for frame, sraw, qraw, sh, qh in paired_frames(reader, structural, solutal):
                    if sh != native[(structural, frame)] or qh != native[(solutal, frame)]:
                        raise Study2Error('legacy native buffer hash mismatch')
                    frame_checks.append({'structural_source': structural, 'solute_source': solutal,
                                         'frame_index': frame, 'structural_sha256': sh, 'solute_sha256': qh})
                    for old in fixtures:
                        if (old['structural_source_id'], old['frame_index']) != (structural, frame):
                            continue
                        actual = legacy_patch_pair(sraw, qraw, structural, old['center_x'], old['center_y'])
                        for key in ('structural_patch_sha256', 'solutal_patch_sha256'):
                            if actual[key] != old[key]:
                                raise Study2Error('legacy patch hash mismatch: ' + old['sample_id'])
                        checks.append({'sample_id': old['sample_id'], 'status': 'PASS',
                                       'structural_patch_sha256': actual['structural_patch_sha256'],
                                       'solutal_patch_sha256': actual['solutal_patch_sha256'],
                                       'pair_sha256': actual['pair_sha256'],
                                       'canonical_corpus_overlap': old['sample_id'] in overlaps})
                    del sraw, qraw
        if len(checks) != 50 or len(frame_checks) != 5:
            raise Study2Error('legacy fixture coverage incomplete')
        for path, sha in proof['implementation_hashes'].items():
            if digest(text_bytes(root, path)) != sha:
                raise Study2Error('implementation changed during legacy gate')
    except Exception as exc:
        failure = f'{type(exc).__name__}: {exc}'
    result = {'status': 'PASS' if failure is None else 'BLOCKED_LEGACY_PAIR_REPRODUCTION',
              'legacy_fixture_pairs_expected': 50, 'legacy_fixture_pair_hash_matches': len(checks),
              'LEGACY_PATCH_PAIRS_EXPECTED': len(overlaps),
              'LEGACY_PATCH_PAIRS_MATCHED': sum(r['canonical_corpus_overlap'] for r in checks),
              'LEGACY_PATCH_PAIR_HASH_MATCHES': sum(r['canonical_corpus_overlap'] for r in checks),
              'scope': '50 unchanged compatibility fixtures; overlap counters only exact canonical site/frame/center matches; no background pixels persisted',
              'checks': checks, 'frames': frame_checks, 'failure': failure,
              'implementation_hashes': proof['implementation_hashes'],
              'scientific_study2b_runs': 0, 'ml_runs': 0, 'completed_at_utc': utc_now()}
    exclusive_json(root, EVIDENCE + '/LEGACY_IO_AUDIT.json', audit)
    exclusive_json(root, EVIDENCE + '/LEGACY_REPRODUCTION.json', result)
    if failure:
        exclusive_json(root, EVIDENCE + '/terminal-state.json', {
            'STUDY2_B': result['status'], 'STATE': 'CLOSED_BLOCKED', 'SCIENTIFIC_STUDY2B_RUNS': 0,
            'ML_RUNS': 0, 'STUDY2_C_AUTHORIZED': False,
            'CURRENT_AUTHORIZED_ACTIVITY': 'NONE_AWAITING_AUTHOR_DECISION'})
    return result


class CorpusWriter:
    """Exclusive append-only aggregate payload and two bounded JSONL ledgers."""
    FILENAMES = ('multimodal_patches_uint8.bin', 'corpus-index.jsonl', 'background-pool.jsonl')

    def __init__(self, root):
        self.root, self.files, self.hashes, self.sizes, self.counts = root, {}, {}, {}, {}
        self.closed = False
        self.metadata_bytes = 0
        for filename in self.FILENAMES:
            if safe_path(root, DATA + '/' + filename).exists():
                raise Study2Error('refuse existing aggregate')
        safe_path(root, DATA).mkdir(parents=True, exist_ok=True)
        try:
            for filename in self.FILENAMES:
                p = safe_path(root, DATA + '/' + filename)
                fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
                self.files[filename] = os.fdopen(fd, 'wb')
                self.hashes[filename] = hashlib.sha256()
                self.sizes[filename] = self.counts[filename] = 0
        except BaseException:
            self.close()
            raise

    def _write(self, filename, content, pixel=False):
        if self.closed:
            raise Study2Error('writer closed')
        projected = self.sizes[filename] + len(content)
        if pixel and projected > MAX_PATCH:
            raise Study2Error('patch cache cap exceeded')
        if not pixel and self.metadata_bytes + len(content) > MAX_METADATA:
            raise Study2Error('metadata cap exceeded')
        if shutil.disk_usage(self.root).free - len(content) < MIN_FREE:
            raise Study2Error('free disk reserve exceeded')
        if self.files[filename].write(content) != len(content):
            raise Study2Error('short aggregate write')
        self.hashes[filename].update(content)
        self.sizes[filename] = projected
        self.counts[filename] += 1
        if not pixel:
            self.metadata_bytes += len(content)

    def append_pair(self, payload):
        if type(payload) is not bytes or len(payload) != PAIR_BYTES:
            raise Study2Error('pair must be exactly two uint8 65x65 native channels')
        row = self.counts[self.FILENAMES[0]]
        self._write(self.FILENAMES[0], payload, pixel=True)
        return row

    def append_metadata(self, filename, row):
        if filename not in self.FILENAMES[1:]:
            raise Study2Error('unknown metadata output')
        content = (json.dumps(row, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode()
        self._write(filename, content)

    def close(self):
        if not self.closed:
            for f in self.files.values():
                try:
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    f.close()
            self.closed = True

    def manifest(self, complete):
        if not self.closed:
            raise Study2Error('manifest requires durable closed aggregates')
        return [{'path': DATA + '/' + name, 'size_bytes': self.sizes[name],
                 'record_count': self.counts[name], 'sha256': self.hashes[name].hexdigest(),
                 'complete': complete, 'git_status': 'LOCAL_IGNORED'} for name in self.FILENAMES]


def _run_full(root):
    from .study2b_corpus import process_frame_pair
    from .study2b_streaming import AuthenticatedSources, SOURCES
    proof = preflight(root, 'full')
    plan = build_authenticated_plan(root)
    fixtures = load_json(root, LEGACY)['samples']
    overlap = legacy_matches(plan, fixtures)
    compatibility = {(r['site_id'], r['frame_index']): old for old in fixtures
                     if old['sample_id'] in overlap for r in [overlap[old['sample_id']]]}
    arm(root, 'full', proof)
    audit, frame_hashes, index_rows = {}, [], []
    views = {name: [] for name in ('GOLD_VIEW', 'GOLD_PLUS_SILVER_VIEW', 'UNLABELED_VIEW', 'FULL_LONGITUDINAL_VIEW')}
    seen, background_tracks = set(), set()
    failure, writer, legacy_matches_count = None, None, 0
    try:
        writer = CorpusWriter(root)
        with AuthenticatedSources(mode='full', audit=audit) as reader:
            for structural, solutal in [('ESM1', 'ESM2'), ('ESM4', 'ESM5')]:
                for frame, sraw, qraw, sh, qh in paired_frames(reader, structural, solutal):
                    records = plan['records_by_frame'].get(f'{structural}:{frame}', [])
                    output = process_frame_pair(sraw, qraw, structural, frame, records,
                                                plan['exclusion_metadata'], row_start=len(views['FULL_LONGITUDINAL_VIEW']))
                    frame_hashes.append({'structural_source': structural, 'solute_source': solutal,
                                         'frame_index': frame, 'structural_frame_sha256': sh,
                                         'solute_frame_sha256': qh})
                    pairs = iter(output['pairs'])
                    for record in output['index_records']:
                        key = (record['site_id'], record['frame_index'])
                        if key in seen:
                            raise Study2Error('duplicate corpus pair')
                        record.update({'structural_source_sha256': SOURCES[structural].sha256,
                                       'solutal_source_sha256': SOURCES[solutal].sha256,
                                       'structural_frame_sha256': sh, 'solutal_frame_sha256': qh,
                                       'study2a_checkpoint': '7c192478554ea139752feaaff8cb2d44ff6747f7',
                                       'method_freeze_sha': proof['head_sha']})
                        if record['pair_status'] == 'VALID_PAIR':
                            pair = next(pairs)
                            payload = pair.tobytes(order='C')
                            row = writer.append_pair(payload)
                            if row != record['row_index'] or digest(payload) != record['pair_sha256']:
                                raise Study2Error('index/payload row or hash mismatch')
                            views['FULL_LONGITUDINAL_VIEW'].append(row)
                            tier = record['supervision_tier']
                            if tier == 'GOLD':
                                views['GOLD_VIEW'].append(row)
                            if tier in {'GOLD', 'SILVER'}:
                                views['GOLD_PLUS_SILVER_VIEW'].append(row)
                            else:
                                views['UNLABELED_VIEW'].append(row)
                            if key in compatibility:
                                old = compatibility[key]
                                if any(record[k] != old[k] for k in ('structural_patch_sha256', 'solutal_patch_sha256')):
                                    raise Study2Error('BLOCKED_LEGACY_PAIR_REPRODUCTION')
                                legacy_matches_count += 1
                        elif key in compatibility:
                            raise Study2Error('historical matched pair lost support')
                        writer.append_metadata('corpus-index.jsonl', record)
                        seen.add(key)
                        index_rows.append(record)
                    if next(pairs, None) is not None:
                        raise Study2Error('extra patch payload without metadata')
                    for background in output['background_records']:
                        background['method_freeze_sha'] = proof['head_sha']
                        writer.append_metadata('background-pool.jsonl', background)
                        background_tracks.add(background['background_track_id'])
                    del sraw, qraw, output
        if len(frame_hashes) != 689 or len(index_rows) != 27396 or legacy_matches_count != len(overlap):
            raise Study2Error('incomplete paired frame/input/legacy coverage')
    except Exception as exc:
        failure = f'{type(exc).__name__}: {exc}'
    # No source retry. Remaining input records are retained as DECODE_ERROR,
    # explicitly distinguishing unattempted records from an observed bad frame.
    if writer is not None:
        try:
            for old in plan['records']:
                key = (old['site_id'], old['frame_index'])
                if key not in seen:
                    row = dict(old, pair_status='DECODE_ERROR', row_index=None,
                               structural_patch_sha256=None, solutal_patch_sha256=None,
                               pair_sha256=None, failure_reason='NOT_ADMITTED_AFTER_TERMINAL_PIPELINE_FAILURE',
                               decode_attempted='NOT_CERTIFIED_SEE_IO_AUDIT')
                    writer.append_metadata('corpus-index.jsonl', row)
                    index_rows.append(row)
                    seen.add(key)
        finally:
            writer.close()
    return finish_full(root, proof, audit, writer, index_rows, frame_hashes,
                       views, background_tracks, failure, legacy_matches_count, len(overlap))


def finish_full(root, proof, audit, writer, rows, frames, views, background_tracks,
                failure, legacy_matches_count, legacy_expected):
    valid = [r for r in rows if r['pair_status'] == 'VALID_PAIR']
    tiers = Counter(r['supervision_tier'] for r in valid)
    input_sites, valid_sites = Counter(r['site_id'] for r in rows), Counter(r['site_id'] for r in valid)
    manifests = writer.manifest(failure is None) if writer else []
    status = 'PASS' if failure is None and len(rows) == 27396 else 'BLOCKED_PARTIAL_EXECUTION'
    coverage = lambda n, d: n / d if d else None
    metrics = {'PAIR_COVERAGE': coverage(len(valid), 27396),
        'GOLD_PAIR_COVERAGE': coverage(tiers['GOLD'], 7941),
        'SILVER_PAIR_COVERAGE': coverage(tiers['SILVER'], 5737),
        'UNLABELED_PAIR_COVERAGE': coverage(tiers['UNLABELED_PRE'] + tiers['UNLABELED_PERSISTENCE'], 13718),
        'VALID_PAIR_COUNT': len(valid), 'INVALID_PAIR_COUNT': len(rows)-len(valid),
        'VALID_SITE_COUNT': len(valid_sites),
        'SITES_WITH_COMPLETE_TRAJECTORY': sum(valid_sites[s] == n for s, n in input_sites.items()),
        'STRUCTURAL_HASH_COMPLETENESS': all(r.get('structural_patch_sha256') for r in valid),
        'SOLUTAL_HASH_COMPLETENESS': all(r.get('solutal_patch_sha256') for r in valid),
        'PAIR_HASH_COMPLETENESS': all(r.get('pair_sha256') for r in valid),
        'PROVENANCE_COMPLETENESS': all(r.get('site_id') and r.get('group_id') and r.get('structural_source_sha256') and r.get('solutal_source_sha256') for r in rows),
        'BACKGROUND_POOL_SIZE': writer.counts['background-pool.jsonl'] if writer else 0,
        'BACKGROUND_TRACK_COUNT': len(background_tracks),
        'STORAGE_BYTES': sum(r['size_bytes'] for r in manifests), 'TEMP_BYTES': 0,
        'PEAK_RSS_KIB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'PEAK_RSS_SCOPE': 'Python parent only; child decoder peak not instrumented'}
    if status == 'PASS' and not all(metrics[k] for k in ('STRUCTURAL_HASH_COMPLETENESS', 'SOLUTAL_HASH_COMPLETENESS', 'PAIR_HASH_COMPLETENESS', 'PROVENANCE_COMPLETENESS')):
        status = 'BLOCKED_PROVENANCE'
    terminal = {'STUDY2_B': status, 'STUDY2_B_METHOD': 'DENSE_MULTIMODAL_LONGITUDINAL_CORPUS',
        'SCIENTIFIC_STUDY2B_RUNS': 1, 'SITE_FRAME_INPUT_RECORDS': 27396,
        'SITE_FRAME_ACCOUNTED_RECORDS': len(rows), 'VALID_MULTIMODAL_PAIRS': len(valid),
        'GOLD_VALID_PAIRS': tiers['GOLD'], 'SILVER_VALID_PAIRS': tiers['SILVER'],
        'UNLABELED_VALID_PAIRS': tiers['UNLABELED_PRE'] + tiers['UNLABELED_PERSISTENCE'],
        'INVALID_MULTIMODAL_PAIRS': len(rows)-len(valid), 'UNIQUE_SITES_WITH_VALID_PAIRS': len(valid_sites),
        'BACKGROUND_CANDIDATES': metrics['BACKGROUND_POOL_SIZE'], 'BACKGROUND_TRACKS': len(background_tracks),
        'HUMAN_REVIEW_USED': False, 'ML_RUNS': 0, 'STATE': 'CLOSED_CONSUMED',
        'STUDY2_C_READY_FOR_AUTHOR_DECISION': status == 'PASS', 'STUDY2_C_AUTHORIZED': False,
        'MERGE_AUTHORIZED': False, 'CURRENT_AUTHORIZED_ACTIVITY': 'NONE_AWAITING_AUTHOR_DECISION'}
    audit.update({'full_scientific_runs': 1, 'ml_runs': 0, 'TEMP_PEAK_BYTES': 0,
                  'FREE_DISK_AFTER': shutil.disk_usage(root).free,
                  'CORPUS_CONTAINER_BYTES': writer.sizes[writer.FILENAMES[0]] if writer else 0,
                  'CORPUS_INDEX_BYTES': writer.sizes['corpus-index.jsonl'] if writer else 0,
                  'BACKGROUND_LEDGER_BYTES': writer.sizes['background-pool.jsonl'] if writer else 0})
    result = {'status': status, 'method_freeze_sha': proof['head_sha'], 'failure': failure,
              'terminal': terminal, 'metrics': metrics,
              'pair_status_counts': dict(Counter(r['pair_status'] for r in rows)),
              'valid_tier_counts': dict(tiers), 'input_tier_counts': dict(EXPECTED_TIERS),
              'LEGACY_PATCH_PAIRS_EXPECTED': legacy_expected,
              'LEGACY_PATCH_PAIRS_MATCHED': legacy_matches_count,
              'LEGACY_PATCH_PAIR_HASH_MATCHES': legacy_matches_count,
              'invalid_support_policy': 'Preserved exclusions; no replacement, center shift, padding or asymmetric crop'}
    container = {'format': 'HEADERLESS_C_CONTIGUOUS_UINT8', 'shape': [len(valid), 2, 65, 65],
                 'dtype': 'uint8', 'channels': ['STRUCTURAL_Y', 'RELATIVE_SOLUTE_FIELD_Y'],
                 'row_bytes': PAIR_BYTES, 'mmap_offset': 0,
                 'order': ['acquisition_id', 'frame_index', 'site_id', 'supervision_tier']}
    for name, value in [('LOCAL_ARTIFACT_MANIFEST.json', {'artifacts': manifests, 'container': container}),
                        ('FRAME_HASHES.json', frames), ('CORPUS_VIEWS.json', views),
                        ('IO_AUDIT.json', audit), ('results.json', result), ('terminal-state.json', terminal)]:
        exclusive_json(root, EVIDENCE + '/' + name, value)
    return terminal


def run(root, mode):
    receipt = EVIDENCE + ('/LEGACY_RECEIPT.json' if mode == 'legacy' else '/EXECUTION_RECEIPT.json')
    consumed_before = safe_path(root, receipt).exists()
    try:
        return _run_legacy(root) if mode == 'legacy' else _run_full(root) if mode == 'full' else preflight(root, mode)
    except Exception as exc:
        if not consumed_before and safe_path(root, receipt).exists():
            terminal = {'STUDY2_B': 'BLOCKED_POST_RECEIPT_FAILURE', 'STATE': 'CLOSED_CONSUMED',
                        'SCIENTIFIC_STUDY2B_RUNS': int(mode == 'full'), 'ML_RUNS': 0,
                        'failure': f'{type(exc).__name__}: {exc}',
                        'partial_outputs': 'PRESERVED; counters not certified beyond existing records',
                        'STUDY2_C_AUTHORIZED': False, 'CURRENT_AUTHORIZED_ACTIVITY': 'NONE_AWAITING_AUTHOR_DECISION'}
            if not safe_path(root, EVIDENCE + '/terminal-state.json').exists():
                exclusive_json(root, EVIDENCE + '/terminal-state.json', terminal)
            return terminal
        raise
