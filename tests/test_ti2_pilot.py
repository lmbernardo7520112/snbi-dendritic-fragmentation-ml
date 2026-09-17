"""Synthetic custody and allowlist contracts; never opens experimental data."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from snbi_fragmentation import ti2_pilot as pilot


class PilotJournalTests(unittest.TestCase):
    def setUp(self):
        temporary_root = Path(__file__).resolve().parents[1]/'.bootstrap-test-tmp'
        if temporary_root.is_symlink():
            self.fail('synthetic temporary root must not be a symlink')
        temporary_root.mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(dir=temporary_root)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def test_atomic_journal_failure_preserves_previous_complete_record(self):
        destination = self.root/'attempt.json'
        previous = {'status': 'DECODED_AND_VERIFIED', 'materialized_image_count': 0}
        pilot._atomic_json(destination, previous)
        original = destination.read_bytes()
        with patch.object(pilot.os, 'replace', side_effect=OSError('synthetic publication failure')):
            with self.assertRaises(OSError):
                pilot._atomic_json(destination, {'status': 'COMPLETE', 'materialized_image_count': 30})
        self.assertEqual(destination.read_bytes(), original)
        self.assertEqual(json.loads(destination.read_text()), previous)
        self.assertEqual(json.loads((self.root/'.attempt.json.tmp').read_text())['materialized_image_count'], 30)

    def test_successful_journal_updates_leave_no_pending_file(self):
        destination = self.root/'attempt.json'
        pilot._atomic_json(destination, {'materialized_image_count': 0})
        pilot._atomic_json(destination, {'materialized_image_count': 1})
        self.assertEqual(json.loads(destination.read_text()), {'materialized_image_count': 1})
        self.assertFalse((self.root/'.attempt.json.tmp').exists())

    def test_lineage_is_created_once_and_cannot_be_overwritten(self):
        destination = self.root/'lineage.json'
        lineage = {'record_kind': 'verified_prepublication_lineage', 'images': ['synthetic identity']}
        pilot._exclusive_json(destination, lineage)
        original = destination.read_bytes()
        with self.assertRaises(FileExistsError):
            pilot._exclusive_json(destination, {'images': ['replacement']})
        self.assertEqual(destination.read_bytes(), original)
        self.assertEqual(json.loads(destination.read_text()), lineage)


class PilotContracts(unittest.TestCase):
    def test_exact_thirty_unique_pairs_and_physical_time(self):
        plan = pilot.frozen_plan()
        pilot.validate_plan(plan)
        self.assertEqual(len(plan), 30)
        self.assertEqual(len({(p['source_id'], p['frame_index']) for p in plan}), 30)
        self.assertEqual(plan[-1]['physical_time_s'], 464.92)
        self.assertEqual(sum(p['role'] == 'estimation' for p in plan), 18)
        self.assertEqual(sum(p['role'] == 'validation' for p in plan), 12)

    def test_extra_missing_duplicate_and_unapproved_index_fail(self):
        plan = pilot.frozen_plan()
        changed = copy.deepcopy(plan)
        changed[0]['frame_index'] = 1
        for bad in (plan + [plan[0]], plan[:-1], [plan[0]] * 30, changed):
            with self.subTest(case=bad[:1]):
                with self.assertRaises(pilot.PilotContractError):
                    pilot.validate_plan(bad)

    def test_changed_time_condition_or_holdout_role_fails(self):
        for field, value in (('physical_time_s', 0.2), ('condition', 'other'), ('role', 'validation')):
            bad = pilot.frozen_plan()
            bad[0][field] = value
            with self.assertRaises(pilot.PilotContractError):
                pilot.validate_plan(bad)

    def test_plan_deterministic_and_independent_copies(self):
        first = pilot.frozen_plan()
        second = pilot.frozen_plan()
        self.assertEqual(first, second)
        first[0]['source_id'] = 'ESM9'
        self.assertEqual(second[0]['source_id'], 'ESM1')

    def test_hashing_does_not_change_stream_bytes(self):
        stream = io.BytesIO(b'synthetic custody fixture')
        original = stream.getvalue()
        digest, size = pilot.hash_stream(stream)
        self.assertEqual(stream.getvalue(), original)
        self.assertEqual(size, len(original))
        self.assertEqual(len(digest), 64)

    def test_readonly_flags_reject_source_symlink(self):
        with patch.object(pilot.os, 'open', side_effect=OSError('refused')) as opened:
            with self.assertRaises(OSError):
                pilot.open_readonly('synthetic.zip')
        flags = opened.call_args.args[1]
        self.assertEqual(flags & pilot.os.O_ACCMODE, pilot.os.O_RDONLY)
        self.assertTrue(flags & pilot.os.O_NOFOLLOW)

    def test_native_yuv_planes_preserve_all_channels_and_bit_depth(self):
        layout = pilot.native_layout('yuv420p', 1278, 1018)
        self.assertEqual(layout['frame_bytes'], 1278 * 1018 * 3 // 2)
        self.assertEqual(layout['channels'], 3)
        self.assertEqual(layout['bit_depth'], 8)
        self.assertEqual(len(layout['planes']), 3)
        with self.assertRaises(pilot.PilotContractError):
            pilot.native_layout('unknown', 4, 4)

    def test_decoder_filter_contains_only_frozen_indices(self):
        command = pilot.decoder_command(7, 'ESM1', 'yuv420p')
        self.assertIn('select=eq(n\\,0)+eq(n\\,73)+eq(n\\,146)+eq(n\\,219)+eq(n\\,293)', command)
        self.assertEqual(command[command.index('-frames:v') + 1], '5')
        self.assertEqual(command[command.index('-pix_fmt') + 1], 'yuv420p')
        self.assertNotIn('-y', command)
        self.assertLess(command.index('-noautorotate'), command.index('-i'))
        self.assertFalse(any(token in ' '.join(command) for token in ('scale=', 'crop=', 'eq=', 'histeq=')))

    def test_wrong_output_size_fails_before_materialization(self):
        self.assertEqual(pilot.split_native_frames(b'abcdef', 2, 3), [b'ab', b'cd', b'ef'])
        for data in (b'abcde', b'abcdefg'):
            with self.assertRaises(pilot.PilotContractError):
                pilot.split_native_frames(data, 2, 3)

    def test_source_metadata_and_lineage_required(self):
        with self.assertRaises(pilot.PilotContractError):
            pilot.validate_pilot_manifest({'images': pilot.frozen_plan()})

    def test_sealed_bytes_are_authenticated_before_decoder_access(self):
        fixture = b'non-decodable synthetic custody bytes'
        archive = unittest.mock.Mock()
        archive.open.side_effect = lambda *args: io.BytesIO(fixture)
        entry = {'sha256': '0'*64, 'size_bytes': len(fixture),
                 'storage': {'member_path': 'synthetic.mp4'}}
        with self.assertRaises(pilot.PilotContractError):
            pilot._sealed_member(archive, entry)
        entry['sha256'] = hashlib.sha256(fixture).hexdigest()
        fd = pilot._sealed_member(archive, entry)
        try:
            self.assertEqual(pilot.os.read(fd, len(fixture)), fixture)
            with self.assertRaises(OSError):
                pilot.os.write(fd, b'mutation')
        finally:
            pilot.os.close(fd)

    def test_manifest_cannot_forge_custody_or_transform_native_images(self):
        sources = pilot.load_manifest(pilot.Path(__file__).resolve().parents[1]/'configs/sources/source_manifest.json')
        by_id = {s['source_id']: s for s in sources['sources']}
        images=[]
        for plan in pilot.frozen_plan():
            source = by_id[plan['source_id']]
            width, height = pilot.DIMENSIONS[plan['source_id']]
            command = [arg.replace('/proc/self/fd/SEALED', '<sealed-memfd>') for arg in pilot.decoder_command('SEALED', plan['source_id'], 'yuv420p')]
            images.append({**plan, **pilot.native_layout('yuv420p', width, height),
                'source_sha256': source['sha256'], 'image_sha256':'a'*64,
                'path': f"data/derived/ti2-pilot/{plan['source_id']}-{plan['frame_index']:04d}.raw",
                'codec':'h264', 'decoder_method':'ffmpeg-native-select-sealed-anonymous-mp4-v1',
                'decoder_command':command,
                'lineage':{'container_sha256':sources['containers'][0]['sha256'],
                    'member_path':source['storage']['member_path'],'native_planes_unchanged':True}})
        valid={'schema_version':'1.0.0','materialized_image_count':30,'images':images}
        pilot.validate_pilot_manifest(valid, sources)
        for field, value in (('lineage','yes'),('source_sha256','0'*64),('colorspace_conversion',True),
                              ('decoder_command',['ffmpeg','-vf','crop=100:100']),('codec','invented')):
            bad=copy.deepcopy(valid)
            bad['images'][0][field]=value
            with self.assertRaises(pilot.PilotContractError):
                pilot.validate_pilot_manifest(bad,sources)


if __name__ == '__main__':
    unittest.main()
