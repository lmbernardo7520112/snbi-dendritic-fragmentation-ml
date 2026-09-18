"""Exact TI-2 pilot allowlist, native decoding and immutable source custody.

Only the CLI accepts an operator-supplied path. No filesystem search is used.
MP4 members are held in sealed anonymous memory for seekable FFmpeg access;
compressed videos are never extracted to disk. Native raw frame planes are
lossless images whose layout is fully specified by the pilot manifest.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from decimal import Decimal, DecimalException
from pathlib import Path
import re
import subprocess
import zipfile

from .custody import load_manifest
from .timebase import load_time_rule
from .ti2_authority import require_scientific_authority


class PilotContractError(ValueError):
    """An invariant blocks decoding or publication."""


INDICES = {'bottom_up_anti_parallel': (0, 73, 146, 219, 293),
           'top_down_parallel': (0, 98, 197, 295, 394)}
MODALITIES = ('xray_radiography', 'relative_solute_field', 'cumulative_fragmentation_annotation')
DIMENSIONS = {'ESM1': (1278, 1018), 'ESM2': (1278, 1018), 'ESM3': (1280, 1024),
              'ESM4': (1278, 1012), 'ESM5': (1278, 1012), 'ESM6': (1280, 1012)}


def frozen_plan():
    """Build metadata only; ``physical_time_s`` is a deprecated elapsed alias."""
    _, time_rule = load_time_rule(Path(__file__).resolve().parents[2]/'configs/time_rule.json')
    result = []
    for number in range(1, 7):
        condition = 'bottom_up_anti_parallel' if number <= 3 else 'top_down_parallel'
        for position, index in enumerate(INDICES[condition]):
            source_id = f'ESM{number}'
            elapsed = time_rule.elapsed_time(index)
            experimental = time_rule.experimental_time(source_id, index)
            result.append({'source_id': f'ESM{number}', 'frame_index': index,
                           'condition': condition, 'experiment_id': condition,
                           'modality': MODALITIES[(number-1) % 3],
                           'elapsed_from_first_frame_s': float(elapsed),
                           'experimental_time_s': float(experimental),
                           'physical_time_s': float(elapsed),
                           'role': 'estimation' if position in (0, 2, 4) else 'validation'})
    return result


def validate_plan(plan):
    expected = frozen_plan()
    if not isinstance(plan, list) or len(plan) != len(expected):
        raise PilotContractError('exact ordered 30 source/index/time/role entries required')
    time_fields = ('elapsed_from_first_frame_s', 'experimental_time_s', 'physical_time_s')
    for actual, approved in zip(plan, expected, strict=True):
        if not isinstance(actual, dict) or set(actual) != set(approved):
            raise PilotContractError('all frozen pilot fields, including all three times, are required')
        if type(actual['frame_index']) is not int or actual['frame_index'] < 0:
            raise PilotContractError('frame_index must be a nonnegative integer, never boolean')
        for key, value in approved.items():
            if key not in time_fields:
                if actual[key] != value:
                    raise PilotContractError('source, index, condition, modality or role differs from frozen plan')
                continue
            try:
                observed = Decimal(str(actual[key]))
            except (DecimalException, TypeError, ValueError) as exc:
                raise PilotContractError('pilot times must be finite exact decimals') from exc
            if not observed.is_finite() or observed != Decimal(str(value)):
                raise PilotContractError('pilot elapsed, experimental or legacy alias time differs from exact rule')


def hash_stream(stream):
    require_scientific_authority()
    digest, size = hashlib.sha256(), 0
    for block in iter(lambda: stream.read(1024*1024), b''):
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def open_readonly(path):
    """Walk only the supplied path, rejecting symlinks at every component."""
    require_scientific_authority()
    path = Path(path)
    if '..' in path.parts:
        raise PilotContractError('parent traversal prohibited')
    parts = path.parts[1:] if path.is_absolute() else path.parts
    if not parts:
        raise PilotContractError('a regular file path is required')
    directory = os.open('/' if path.is_absolute() else '.',
                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in parts[:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        return os.fdopen(fd, 'rb')
    finally:
        os.close(directory)


def native_layout(pixel_format, width, height):
    if type(width) is not int or type(height) is not int or min(width, height) <= 0:
        raise PilotContractError('invalid dimensions')
    subsampling = {'yuv420p': (2, 2), 'yuvj420p': (2, 2), 'yuv422p': (2, 1),
                   'yuvj422p': (2, 1), 'yuv444p': (1, 1), 'yuvj444p': (1, 1)}
    if pixel_format == 'gray':
        sizes = [('Y', width, height)]
    elif pixel_format in subsampling:
        sx, sy = subsampling[pixel_format]
        sizes = [('Y', width, height), ('U', (width+sx-1)//sx, (height+sy-1)//sy),
                 ('V', (width+sx-1)//sx, (height+sy-1)//sy)]
    else:
        raise PilotContractError('BLOCKED_DEPENDENCY: unsupported native pixel format; no conversion allowed')
    planes, offset = [], 0
    for name, w, h in sizes:
        planes.append({'name': name, 'width': w, 'height': h, 'offset': offset, 'bytes': w*h})
        offset += w*h
    return {'format': 'native_planar_rawvideo', 'pixel_format': pixel_format,
            'width': width, 'height': height, 'channels': len(planes), 'bit_depth': 8,
            'planes': planes, 'frame_bytes': offset, 'lossless': True,
            'colorspace_conversion': False}


def decoder_command(fd, source_id, pixel_format):
    if source_id not in DIMENSIONS:
        raise PilotContractError('unknown source')
    indexes = [p['frame_index'] for p in frozen_plan() if p['source_id'] == source_id]
    selection = 'select=' + '+'.join(f'eq(n\\,{i})' for i in indexes)
    return ['ffmpeg', '-nostdin', '-v', 'error', '-threads', '1', '-noautorotate', '-i', f'/proc/self/fd/{fd}',
            '-map', '0:v:0', '-an', '-sn', '-dn', '-vf', selection, '-fps_mode', 'passthrough',
            '-frames:v', '5', '-pix_fmt', pixel_format, '-threads', '1', '-f', 'rawvideo', 'pipe:1']


def split_native_frames(data, frame_bytes, count=5):
    if type(frame_bytes) is not int or type(count) is not int or frame_bytes <= 0 or count <= 0 or len(data) != frame_bytes * count:
        raise PilotContractError('decoded byte count does not equal frozen pilot')
    return [data[i*frame_bytes:(i+1)*frame_bytes] for i in range(count)]


def validate_pilot_manifest(manifest, source_manifest=None):
    """Validate text, including exact times for all 30 items; never open frames."""
    if not isinstance(manifest, dict) or not isinstance(manifest.get('images'), list):
        raise PilotContractError('pilot manifest requires an images list')
    if source_manifest is None:
        source_manifest = load_manifest(Path(__file__).resolve().parents[2]/'configs/sources/source_manifest.json')
    sources = {s['source_id']: s for s in source_manifest['sources'] if s['source_id'] in DIMENSIONS}
    container_hash = source_manifest['containers'][0]['sha256']
    images = manifest.get('images', [])
    keys = tuple(frozen_plan()[0])
    if any(not isinstance(image, dict) for image in images):
        raise PilotContractError('each pilot item must be an object')
    validate_plan([{k: image[k] for k in keys if k in image} for image in images])
    if manifest.get('schema_version') != '1.0.0' or manifest.get('materialized_image_count') != 30:
        raise PilotContractError('pilot schema/count invalid')
    paths = set()
    for image in images:
        for key in ('source_sha256', 'image_sha256'):
            if not re.fullmatch('[0-9a-f]{64}', image.get(key, '')):
                raise PilotContractError('missing source/image digest')
        source = sources[image['source_id']]
        lineage = {'container_sha256': container_hash,
                   'member_path': source['storage']['member_path'],
                   'native_planes_unchanged': True}
        if image.get('source_sha256') != source['sha256'] or image.get('lineage') != lineage:
            raise PilotContractError('source identity/lineage differs from G0')
        if image.get('decoder_method') != 'ffmpeg-native-select-sealed-anonymous-mp4-v1' or image.get('codec') != 'h264':
            raise PilotContractError('unsupported codec or decoding method')
        command = decoder_command('SEALED', image['source_id'], image['pixel_format'])
        command = ['<sealed-memfd>' if arg == '/proc/self/fd/SEALED' else arg for arg in command]
        if image.get('decoder_command') != command:
            raise PilotContractError('decoder command differs from frozen no-conversion method')
        if (image.get('width'), image.get('height')) != DIMENSIONS[image['source_id']]:
            raise PilotContractError('native dimensions changed')
        layout = native_layout(image['pixel_format'], image['width'], image['height'])
        if any(image.get(k) != value for k, value in layout.items()):
            raise PilotContractError('native layout changed')
        path = image.get('path', '')
        expected = f"data/derived/ti2-pilot/{image['source_id']}-{image['frame_index']:04d}.raw"
        if path != expected or path in paths:
            raise PilotContractError('invalid or duplicate derived path')
        paths.add(path)


def verify_archive(source, source_manifest):
    require_scientific_authority()
    source = Path(source)
    if not source.is_absolute() or '..' in source.parts or source.is_relative_to(Path.cwd()):
        raise PilotContractError('source must be explicit, external and without symlinks')
    container = source_manifest['containers'][0]
    results = []
    with open_readonly(source) as stream:
        observed = hash_stream(stream)
        if observed != (container['sha256'], container['size_bytes']):
            raise PilotContractError('G0 archive identity mismatch')
        results.append({'source_id': container['container_id'], 'sha256': observed[0],
                        'size_bytes': observed[1], 'status': 'PASS'})
        stream.seek(0)
        with zipfile.ZipFile(stream, 'r') as archive:
            names = archive.namelist()
            for item in source_manifest['sources']:
                if item['source_id'] not in DIMENSIONS:
                    continue
                name = item['storage']['member_path']
                if names.count(name) != 1:
                    raise PilotContractError('missing or duplicate authorized member')
                with archive.open(name, 'r') as member:
                    observed = hash_stream(member)
                if observed != (item['sha256'], item['size_bytes']):
                    raise PilotContractError('G0 video identity mismatch')
                results.append({'source_id': item['source_id'], 'sha256': observed[0],
                                'size_bytes': observed[1], 'status': 'PASS'})
    return {'status': 'PASS', 'source_mode': 'O_RDONLY|O_NOFOLLOW', 'archive_mode': 'r',
            'source_locator_sha256': hashlib.sha256(str(source).encode()).hexdigest(),
            'results': results, 'source_documents_not_opened': True}


def _sealed_member(archive, entry):
    fd = os.memfd_create('ti2-readonly-mp4', os.MFD_ALLOW_SEALING)
    try:
        digest, size = hashlib.sha256(), 0
        with archive.open(entry['storage']['member_path'], 'r') as stream:
            for block in iter(lambda: stream.read(1024*1024), b''):
                digest.update(block)
                size += len(block)
                view = memoryview(block)
                while view:
                    view = view[os.write(fd, view):]
        if (digest.hexdigest(), size) != (entry['sha256'], entry['size_bytes']):
            raise PilotContractError('bytes supplied to decoder differ from G0')
        os.lseek(fd, 0, os.SEEK_SET)
        fcntl.fcntl(fd, fcntl.F_ADD_SEALS, fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW |
                    fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL)
        return fd
    except BaseException:
        os.close(fd)
        raise


def _sync_directory(directory):
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _exclusive_json(path, payload):
    """Persist a new text record once; an existing path is never replaced."""
    rendered = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + '\n'
    with path.open('x', encoding='utf-8') as output:
        output.write(rendered)
        output.flush()
        os.fsync(output.fileno())
    _sync_directory(path.parent)


def _atomic_json(path, payload):
    """Replace progress only after a complete same-directory record is durable.

    A failed replacement preserves the old journal and leaves its pending file
    for inspection. A leftover pending file blocks another update; it is never
    silently removed or overwritten.
    """
    if path.is_symlink():
        raise PilotContractError('journal symlink prohibited')
    pending = path.with_name(f'.{path.name}.tmp')
    _exclusive_json(pending, payload)
    os.replace(pending, path)
    _sync_directory(path.parent)


def extract_pilot(source, root):
    require_scientific_authority()
    root = Path(root).resolve()
    if root != Path.cwd() or not (root/'.git').is_dir() or (root/'.git').is_symlink():
        raise PilotContractError('standalone repository root required')
    manifest = load_manifest(root/'configs/sources/source_manifest.json')
    verification = verify_archive(source, manifest)
    destination = root/'data/derived/ti2-pilot'
    for candidate in (root/'data', root/'data/derived', destination):
        if candidate.is_symlink():
            raise PilotContractError('derived path symlink prohibited')
    if destination.exists():
        raise PilotContractError('existing pilot cannot be overwritten or decoded again')
    ignored = subprocess.run(['git', 'check-ignore', '-q', 'data/derived/ti2-pilot/ESM1-0000.raw'], cwd=root)
    if ignored.returncode != 0:
        raise PilotContractError('pilot destination must be Git-ignored')
    destination.mkdir(parents=True, exist_ok=False)
    journal_path = destination/'attempt.json'
    journal = {'status': 'STARTED', 'source_verification': verification,
               'materialized_image_count': 0, 'images': [],
               'restart_policy': 'STOP; never overwrite or automatically decode again'}
    _atomic_json(journal_path, journal)
    images, source_probes, prepared = [], {}, []
    with open_readonly(source) as source_stream, zipfile.ZipFile(source_stream, 'r') as archive:
        source_stream.seek(0)
        actual_container = hash_stream(source_stream)
        container = manifest['containers'][0]
        if actual_container != (container['sha256'], container['size_bytes']):
            raise PilotContractError('opened decoder archive differs from G0')
        for entry in manifest['sources']:
            source_id = entry['source_id']
            if source_id not in DIMENSIONS:
                continue
            fd = _sealed_member(archive, entry)
            try:
                probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                        '-show_streams', '-of', 'json', f'/proc/self/fd/{fd}'],
                                       pass_fds=(fd,), capture_output=True, check=True, timeout=60)
                stream = json.loads(probe.stdout)['streams'][0]
                width, height = stream['width'], stream['height']
                if (width, height) != DIMENSIONS[source_id]:
                    raise PilotContractError('dimensions differ from frozen TI1 metadata')
                layout = native_layout(stream['pix_fmt'], width, height)
                source_probes[source_id] = {k: stream.get(k) for k in ('codec_name','profile','pix_fmt',
                    'width','height','bits_per_raw_sample','nb_frames','color_range','color_space',
                    'color_transfer','color_primaries','chroma_location','side_data_list','tags')}
                os.lseek(fd, 0, os.SEEK_SET)
                command = decoder_command(fd, source_id, stream['pix_fmt'])
                decoded = subprocess.run(command, pass_fds=(fd,), capture_output=True, check=True, timeout=180)
                frames = split_native_frames(decoded.stdout, layout['frame_bytes'])
            finally:
                os.close(fd)
            plans = [p for p in frozen_plan() if p['source_id'] == source_id]
            for plan, frame in zip(plans, frames, strict=True):
                relative = f"data/derived/ti2-pilot/{source_id}-{plan['frame_index']:04d}.raw"
                prepared.append((relative, frame))
                images.append({**plan, **layout, 'path': relative, 'image_sha256': hashlib.sha256(frame).hexdigest(),
                               'source_sha256': entry['sha256'], 'codec': stream['codec_name'],
                               'decoder_method': 'ffmpeg-native-select-sealed-anonymous-mp4-v1',
                               'decoder_command': [arg.replace(f'/proc/self/fd/{fd}', '<sealed-memfd>') for arg in command],
                               'lineage': {'container_sha256': manifest['containers'][0]['sha256'],
                                           'member_path': entry['storage']['member_path'],
                                           'native_planes_unchanged': True}})
    post = verify_archive(source, manifest)
    if post != verification:
        raise PilotContractError('source changed during pilot')
    result = {'schema_version': '1.0.0', 'materialized_image_count': len(images),
              'native_pixel_format_preserved': True, 'source_verification_before': verification,
              'source_verification_after': post, 'source_probes': source_probes,
              'images': images, 'decoder_internal_reference_frames_allowed': True}
    validate_pilot_manifest(result)
    # This immutable snapshot survives any later progress-journal interruption.
    # Its count is zero at publication; attempt.json records actual progress.
    lineage = {**result, 'record_kind': 'verified_prepublication_lineage',
               'materialized_image_count': 0, 'planned_image_count': len(images)}
    _exclusive_json(destination/'lineage.json', lineage)
    journal.update({'status': 'DECODED_AND_VERIFIED', 'images': images,
                    'lineage_manifest': 'lineage.json'})
    _atomic_json(journal_path, journal)
    for relative, frame in prepared:
        with (root/relative).open('xb') as output:
            output.write(frame)
            output.flush()
            os.fsync(output.fileno())
        journal['materialized_image_count'] += 1
        _atomic_json(journal_path, journal)
    journal['status'] = 'COMPLETE'
    _atomic_json(journal_path, journal)
    return result
