#!/usr/bin/env python3
"""Explicit, bounded TI-2 stages; never scans for experimental sources."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

try:
    from ti2_authority import require_scientific_authority
except ModuleNotFoundError:
    from scripts.ti2_authority import require_scientific_authority


def write_new(path, value):
    stage_guard()
    target = ROOT / path
    if target.is_symlink() or target.exists():
        raise RuntimeError('immutable evidence already exists: ' + path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as output:
        output.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def command(args):
    require_scientific_authority(ROOT)
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def stage_guard():
    require_scientific_authority(ROOT)
    if Path.cwd() != ROOT or (ROOT/'.git').is_symlink() or not (ROOT/'.git').is_dir():
        raise RuntimeError('run only at standalone repository root')
    if command(['git', 'branch', '--show-current']) != 'feat/ti2-registration-calibration':
        raise RuntimeError('incorrect branch')


def preflight(source):
    stage_guard()
    from snbi_fragmentation.custody import load_manifest
    from snbi_fragmentation.ti2_pilot import frozen_plan, verify_archive
    if (ROOT / 'data/derived/ti2-pilot').exists() or (ROOT / 'data/derived/ti2-pilot').is_symlink():
        raise RuntimeError('existing pilot: no overwrite or repeat decoding permitted')
    guards = {}
    for script in ('check_repository_data.py', 'check_local_bootstrap.py', 'check_ti2_scope.py'):
        guards[script] = json.loads(command([sys.executable, '-B', 'scripts/' + script]))
    environment = {'python': platform.python_version()}
    for package in ('numpy', 'scipy', 'Pillow'):
        environment[package] = importlib.metadata.version(package)
    for tool in ('ffmpeg', 'ffprobe'):
        environment[tool] = command([tool, '-version']).splitlines()[0]
    source_verification = verify_archive(source, load_manifest(ROOT/'configs/sources/source_manifest.json'))
    report = {'stage': 'TI2-E0', 'status': 'PASS',
              'base_commit': command(['git', 'rev-parse', 'HEAD']),
              'source_verification': source_verification, 'environment': environment,
              'guards': guards, 'plan': frozen_plan(), 'prior_pilot_destination_absent': True,
              'experimental_images_decoded_at_preflight': 0,
              'runtime_packages_preexisting_no_installation': True,
              'red_evidence': ['artifacts/evidence/TI2/red-pilot.txt',
                               'artifacts/evidence/TI2/red-geometry.txt',
                               'artifacts/evidence/TI2/red-governance.txt'],
              'boundary': 'standard sandbox; repository writes; exact supplied ZIP read-only',
              'forbidden_phases': ['TI-3', 'TI-4', 'TI-5', 'TI-6', 'TI-7', 'TI-8']}
    write_new('artifacts/evidence/TI2/preflight.json', report)
    print(json.dumps({'stage': 'TI2-E0', 'status': 'PASS', 'source': source_verification,
                      'environment': environment}, indent=2))


def pilot(source):
    stage_guard()
    from snbi_fragmentation.ti2_pilot import extract_pilot
    pre = json.loads((ROOT/'artifacts/evidence/TI2/preflight.json').read_text())
    if pre['status'] != 'PASS' or hashlib.sha256(source.encode()).hexdigest() != pre['source_verification']['source_locator_sha256']:
        raise RuntimeError('preflight/source authorization mismatch')
    report = extract_pilot(source, ROOT)
    write_new('artifacts/metadata/ti2-pilot-manifest.json', report)
    print(json.dumps({'stage': 'TI2-E1', 'status': 'PASS',
                      'image_count': report['materialized_image_count'],
                      'source_before_after_equal': report['source_verification_before'] == report['source_verification_after'],
                      'pixel_formats': {key: value['pix_fmt'] for key, value in report['source_probes'].items()}}))


def load_native(record):
    """Read only a manifest-listed, hash-authenticated native pilot image."""
    stage_guard()
    import numpy as np
    from snbi_fragmentation.ti2_pilot import frozen_plan, open_readonly
    expected = f"data/derived/ti2-pilot/{record['source_id']}-{record['frame_index']:04d}.raw"
    if record['path'] != expected or not any(
        p['source_id'] == record['source_id'] and p['frame_index'] == record['frame_index']
        for p in frozen_plan()
    ):
        raise RuntimeError('image outside frozen pilot')
    with open_readonly(ROOT/expected) as stream:
        payload = stream.read()
    if len(payload) != record['frame_bytes'] or hashlib.sha256(payload).hexdigest() != record['image_sha256']:
        raise RuntimeError('native pilot integrity mismatch')
    planes = {}
    for p in record['planes']:
        planes[p['name']] = np.frombuffer(payload, dtype=np.uint8, count=p['bytes'],
                                         offset=p['offset']).reshape(p['height'], p['width'])
    return planes


def registration_mask(record, planes):
    """Ephemeral measurement exclusion, never an annotation/event export."""
    stage_guard()
    import numpy as np
    from scipy import ndimage
    height, width = planes['Y'].shape
    valid = np.ones((height, width), dtype=bool)
    valid[:64] = False
    valid[-64:] = False
    valid[:, :64] = False
    valid[:, -64:] = False
    # Fixed metadata corner boxes audited on estimation images before fitting.
    valid[:int(height*.09), :int(width*.30)] = False
    valid[int(height*.85):, int(width*.62):] = False
    overlay = np.zeros((height, width), dtype=bool)
    if record['source_id'] in ('ESM3', 'ESM6'):
        for key in ('U', 'V'):
            if key in planes:
                chroma = planes[key]
                expanded = np.repeat(np.repeat(chroma, (height+chroma.shape[0]-1)//chroma.shape[0], axis=0),
                                     (width+chroma.shape[1]-1)//chroma.shape[1], axis=1)[:height, :width]
                overlay |= np.abs(expanded.astype(float)-128) > 12
        overlay = ndimage.binary_dilation(overlay, iterations=3)
        valid &= ~overlay
    return valid, {'measurement_rim_excluded_px': 64,
                   'metadata_exclusion_normalized_xywh': [[0, 0, .30, .09], [.62, .85, .38, .15]],
                   'colored_overlay_excluded_pixels': int(overlay.sum()),
                   'overlay_rule': 'abs(U-128)>12 or abs(V-128)>12; native chroma support; 3px dilation',
                   'overlay_purpose': 'ephemeral registration metric exclusion only; no objects or labels',
                   'metric_support_pixels': int(valid.sum())}


PAIRS = (('ESM2', 'ESM1', 'bottom-up'), ('ESM3', 'ESM1', 'bottom-up'),
         ('ESM5', 'ESM4', 'top-down'), ('ESM6', 'ESM4', 'top-down'))


def measure_pairs(role, *, allowed_pair_keys=None):
    stage_guard()
    from snbi_fragmentation.ti2_registration import pair_measurements
    from snbi_fragmentation.ti2_pilot import validate_pilot_manifest
    if role not in ('estimation', 'validation'):
        raise RuntimeError('unknown frozen pilot role')
    known_keys = {moving + '-to-' + reference for moving, reference, _ in PAIRS}
    allowed = known_keys if allowed_pair_keys is None else set(allowed_pair_keys)
    if not allowed <= known_keys:
        raise RuntimeError('unknown registration pair')
    if not allowed:
        return {}, {}
    manifest = json.loads((ROOT/'artifacts/metadata/ti2-pilot-manifest.json').read_text())
    validate_pilot_manifest(manifest)
    observations, masks = {}, {}
    for moving, reference, condition in PAIRS:
        key = moving + '-to-' + reference
        if key not in allowed:
            continue
        observations[key] = {}
        records = [r for r in manifest['images'] if r['source_id'] == moving and r['role'] == role]
        for record in records:
            i = record['frame_index']
            target = next(r for r in manifest['images'] if r['source_id'] == reference and r['frame_index'] == i)
            a, b = load_native(target), load_native(record)
            ma, sa = registration_mask(target, a)
            mb, sb = registration_mask(record, b)
            result = pair_measurements(a['Y'], b['Y'], ma, mb)
            observations[key][i] = result
            masks[key + ':' + str(i)] = {'reference': sa, 'moving': sb}
            print(json.dumps({'pair': key, 'frame_index': i, 'role': role,
                              'status': result['status'], 'matches': len(result['matches'])}), flush=True)
    return observations, masks


def estimate():
    stage_guard()
    from snbi_fragmentation.ti2_registration import fit_registration, RegistrationError
    from snbi_fragmentation.ti2_geometry import ESTIMATION_INDICES, VALIDATION_INDICES
    for moving, reference, condition in PAIRS:
        if (ROOT/f'configs/registration/{moving}-to-{reference}.json').exists():
            raise RuntimeError('frozen registration exists; no implicit refit')
    observations, masks = measure_pairs('estimation')
    hashes = {}
    for moving, reference, condition in PAIRS:
        key = moving + '-to-' + reference
        try:
            result = fit_registration(observations[key], condition).as_dict()
            result['numerical_estimation_status'] = 'PASS'
        except RegistrationError as exc:
            result = {'numerical_estimation_status': 'BLOCKED', 'reason': str(exc),
                      'matrix': None, 'inverse': None, 'transform_class': None,
                      'selection_history': getattr(exc, 'selection_history', []),
                      'parameter_status': 'NO_ADMISSIBLE_FIT'}
        result.update({'source_id': moving, 'reference_id': reference,
                       'condition': condition, 'estimation_indices': list(ESTIMATION_INDICES[condition]),
                       'validation_indices': list(VALIDATION_INDICES[condition]),
                       'convention': 'top-left pixel center=(0,0); x right; y down; column vectors; native-to-reference',
                       'physical_orientation': {'gravity_direction': 'NOT_VERIFIED',
                                                'thermal_gradient_direction': 'NOT_VERIFIED',
                                                'growth_direction': 'NOT_VERIFIED'},
                       'scope': 'numerical registration only; does not establish physical orientation or ground truth',
                       'frozen_before_validation_pixel_access': True})
        path = f'configs/registration/{key}.json'
        write_new(path, result)
        hashes[path] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    write_new('artifacts/evidence/TI2/estimation-audit.json', {
        'stage': 'TI2-E2/E3', 'observations': observations, 'measurement_exclusions': masks,
        'frozen_registration_sha256': hashes,
        'runtime_code_sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                               ('scripts/run_ti2.py', 'src/snbi_fragmentation/ti2_registration.py',
                                'src/snbi_fragmentation/ti2_geometry.py')},
        'visual_geometry_audit': {'only_estimation_images_reviewed': True,
                                 'timestamp_and_scale_bar_present': True,
                                 'annotation_overlay': 'colored; metric exclusion only',
                                 'constant_padding_removal': 'NOT_VERIFIED; dimensions alone insufficient',
                                 'physical_direction_arrows': 'NOT_VERIFIED',
                                 'author_review': 'PENDING',
                                 'diagnostic': 'data/derived/ti2-diagnostics/central-estimation.png'},
        'metadata_exclusion_extension': 'fixed normalized corner boxes from central estimation audit; before fit and validation; quantitative thresholds unchanged'})


def validate():
    stage_guard()
    from snbi_fragmentation.ti2_registration import FrozenRegistration, RegistrationConfig, validate_registration
    evidence_path = 'artifacts/evidence/TI2/validation-audit.json'
    if (ROOT/evidence_path).is_symlink() or (ROOT/evidence_path).exists():
        raise RuntimeError('immutable evidence already exists: ' + evidence_path)
    audit = json.loads((ROOT/'artifacts/evidence/TI2/estimation-audit.json').read_text())
    frozen = {}
    for moving, reference, condition in PAIRS:
        key = moving + '-to-' + reference
        path = f'configs/registration/{key}.json'
        content = (ROOT/path).read_bytes()
        if hashlib.sha256(content).hexdigest() != audit['frozen_registration_sha256'][path]:
            raise RuntimeError('REG-201 frozen parameters changed before validation')
        frozen[key] = json.loads(content)
    eligible = [key for key, record in frozen.items() if record['numerical_estimation_status'] == 'PASS']
    control_revision = None
    if eligible:
        # Any actual measurement still requires the exact frozen method.
        for path, digest in audit['runtime_code_sha256'].items():
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != digest:
                raise RuntimeError('runtime method changed between estimation and validation')
        observations, masks = measure_pairs('validation', allowed_pair_keys=eligible)
    else:
        # No transform exists to validate. Preserve the historical method and
        # emit a dependency decision without opening any reserved native plane.
        snapshot_path = 'artifacts/evidence/TI2/runner-at-estimation.txt'
        snapshot_hash = hashlib.sha256((ROOT/snapshot_path).read_bytes()).hexdigest()
        if snapshot_hash != audit['runtime_code_sha256']['scripts/run_ti2.py']:
            raise RuntimeError('historical runner snapshot differs from estimation evidence')
        control_revision = {
            'revision': 'validation-prerequisite-control-v1',
            'historical_runner_snapshot': snapshot_path,
            'historical_runner_sha256': snapshot_hash,
            'historical_runner_matches_estimation': True,
            'current_runner_sha256': hashlib.sha256((ROOT/'scripts/run_ti2.py').read_bytes()).hexdigest(),
            'scientific_method_reexecuted': False,
            'scope': 'dependency decision only; no estimation, refit or validation pixel analysis',
        }
        observations, masks = {}, {}
    results = {}
    for key, record in frozen.items():
        if record['numerical_estimation_status'] != 'PASS':
            results[key] = {'status': 'BLOCKED', 'reason': 'no admissible matrix from estimation',
                            'refit_performed': False, 'matrix': None, 'inverse': None,
                            'validation_indices': record['validation_indices'],
                            'validation_pixel_analysis_performed': False,
                            'validation_metrics': 'NOT_EVALUATED_WITHOUT_FROZEN_MATRIX'}
            continue
        parameters = FrozenRegistration(record['condition'], record['transform_class'],
                                        tuple(tuple(r) for r in record['matrix']),
                                        tuple(tuple(r) for r in record['inverse']),
                                        tuple(record['estimation_indices']),
                                        json.dumps(record['estimation_metrics']),
                                        json.dumps(record['selection_history']),
                                        RegistrationConfig(**record['method_config']))
        results[key] = validate_registration(parameters, observations[key])
    for path, digest in audit['frozen_registration_sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != digest:
            raise RuntimeError('REG-201 frozen parameters changed during validation')
    write_new(evidence_path, {
        'stage': 'TI2-E4', 'results': results, 'observations': observations,
        'status': 'PASS' if all(result['status'] == 'PASS' for result in results.values()) else 'BLOCKED',
        'validation_pixels_accessed_for_analysis': bool(eligible),
        'control_revision': control_revision,
        'measurement_exclusions': masks, 'refit_performed': False,
        'frozen_registration_sha256': audit['frozen_registration_sha256'],
        'author_visual_review': 'PENDING'})
    print(json.dumps({key: value['status'] for key, value in results.items()}))


if __name__ == '__main__':
    stage_guard()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('preflight', 'pilot', 'estimate', 'validate'))
    parser.add_argument('--source', help='exact operator-authorized external ZIP')
    args = parser.parse_args()
    if args.stage in ('estimate', 'validate'):
        {'estimate': estimate, 'validate': validate}[args.stage]()
    else:
        if not args.source:
            parser.error('--source is required for preflight/pilot')
        {'preflight': preflight, 'pilot': pilot}[args.stage](args.source)
