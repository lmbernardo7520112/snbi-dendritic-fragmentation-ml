"""Synthetic runner control checks; no experimental input or media runtime."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from snbi_fragmentation import ti2_pilot, ti2_registration


REPOSITORY = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('ti2_runner_controls', REPOSITORY/'scripts/run_ti2.py')
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class ExecutionControls(unittest.TestCase):
    def setUp(self):
        temporary_root = REPOSITORY/'.bootstrap-test-tmp'
        if temporary_root.is_symlink():
            self.fail('synthetic temporary root must not be a symlink')
        temporary_root.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=temporary_root)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        root_patch = patch.object(runner, 'ROOT', self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        guard_patch = patch.object(runner, 'stage_guard')
        guard_patch.start()
        self.addCleanup(guard_patch.stop)

    def write(self, path, value):
        target = self.root/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value), encoding='utf-8')
        return hashlib.sha256(target.read_bytes()).hexdigest()

    def inputs(self, accepted=(), *, changed_runner=False):
        hashes = {}
        for moving, reference, condition in runner.PAIRS:
            key = moving + '-to-' + reference
            record = {
                'numerical_estimation_status': 'PASS' if key in accepted else 'BLOCKED',
                'condition': condition, 'transform_class': 'identity',
                'matrix': [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                'inverse': [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                'estimation_indices': [0, 146, 293] if condition == 'bottom-up' else [0, 197, 394],
                'validation_indices': [73, 219] if condition == 'bottom-up' else [98, 295],
                'estimation_metrics': {}, 'selection_history': [], 'method_config': {},
            }
            if key not in accepted:
                record.update(matrix=None, inverse=None, transform_class=None)
            path = f'configs/registration/{key}.json'
            hashes[path] = self.write(path, record)
        original = 'historical synthetic runner'
        snapshot = self.root/'artifacts/evidence/TI2/runner-at-estimation.txt'
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(original, encoding='utf-8')
        current = self.root/'scripts/run_ti2.py'
        current.parent.mkdir(parents=True, exist_ok=True)
        current.write_text('revised synthetic runner' if changed_runner else original, encoding='utf-8')
        self.write('artifacts/evidence/TI2/estimation-audit.json', {
            'frozen_registration_sha256': hashes,
            'runtime_code_sha256': {'scripts/run_ti2.py': hashlib.sha256(original.encode()).hexdigest()},
        })

    def test_all_blocked_records_never_measure_validation_pixels(self):
        self.inputs(changed_runner=True)
        with patch.object(runner, 'measure_pairs') as measure, patch('sys.stdout', new=io.StringIO()):
            runner.validate()
        measure.assert_not_called()
        report = json.loads((self.root/'artifacts/evidence/TI2/validation-audit.json').read_text())
        self.assertEqual(report['status'], 'BLOCKED')
        self.assertFalse(report['validation_pixels_accessed_for_analysis'])
        self.assertTrue(report['control_revision']['historical_runner_matches_estimation'])
        self.assertEqual(report['observations'], {})
        self.assertTrue(all(item['status'] == 'BLOCKED' for item in report['results'].values()))

    def test_mixed_status_measures_only_accepted_pair(self):
        key = 'ESM2-to-ESM1'
        self.inputs(accepted=(key,))
        measurements = {key: {73: {}, 219: {}}}
        with patch.object(runner, 'measure_pairs', return_value=(measurements, {})) as measure, \
                patch.object(ti2_registration, 'validate_registration', return_value={'status': 'PASS', 'refit_performed': False}), \
                patch('sys.stdout', new=io.StringIO()):
            runner.validate()
        measure.assert_called_once_with('validation', allowed_pair_keys=[key])

    def test_changed_method_blocks_before_any_validation_pixel_read(self):
        self.inputs(accepted=('ESM2-to-ESM1',), changed_runner=True)
        with patch.object(runner, 'measure_pairs') as measure:
            with self.assertRaisesRegex(RuntimeError, 'runtime method changed'):
                runner.validate()
        measure.assert_not_called()

    def test_measure_pairs_filters_before_loading_native_records(self):
        self.write('artifacts/metadata/ti2-pilot-manifest.json', {'images': ti2_pilot.frozen_plan()})
        key = 'ESM2-to-ESM1'
        with patch.object(ti2_pilot, 'validate_pilot_manifest'), \
                patch.object(runner, 'load_native', return_value={'Y': 'synthetic'}) as load, \
                patch.object(runner, 'registration_mask', return_value=('synthetic mask', {})), \
                patch.object(ti2_registration, 'pair_measurements', return_value={'status': 'PASS', 'matches': []}), \
                patch('sys.stdout', new=io.StringIO()):
            observations, _ = runner.measure_pairs('validation', allowed_pair_keys=[key])
        self.assertEqual(set(observations), {key})
        self.assertEqual({(call.args[0]['source_id'], call.args[0]['frame_index']) for call in load.call_args_list},
                         {('ESM1', 73), ('ESM2', 73), ('ESM1', 219), ('ESM2', 219)})

    def test_existing_validation_evidence_stops_before_measurement(self):
        self.inputs(accepted=('ESM2-to-ESM1',))
        path = 'artifacts/evidence/TI2/validation-audit.json'
        self.write(path, {'status': 'existing synthetic evidence'})
        original = (self.root/path).read_bytes()
        with patch.object(runner, 'measure_pairs') as measure:
            with self.assertRaisesRegex(RuntimeError, 'immutable evidence already exists'):
                runner.validate()
        measure.assert_not_called()
        self.assertEqual((self.root/path).read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
