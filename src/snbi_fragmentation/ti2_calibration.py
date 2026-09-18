"""Printed scale-bar geometry only; no file I/O or microstructure inference.

Configuration is fixed before experimental measurement. The parent runner
authenticates native planes and supplies only the six permitted estimation
records. Scientific registration and physical orientation are separate gates.
"""

from collections import Counter
from statistics import median

METHOD_CONFIG = {
    'method_version': 'native-luma-horizontal-scale-bar-v2',
    'corner_rectangle': 'x=[floor(0.62*width),floor(0.98*width)), y=[floor(0.85*height),floor(0.98*height))',
    'thresholds_inclusive': [16, 20, 24, 28, 32, 36, 40],
    'minimum_run_px': 80,
    'maximum_run_px': 500,
    'minimum_consecutive_rows': 2,
    'row_length_tolerance_px': 2,
    'minimum_successful_thresholds': 3,
    'endpoint_raster_bound_px': 1.0,
    'nominal_printed_bar_micrometres': 500.0,
    'length_convention': 'outer edges at first_center-0.5 and last_center+0.5; inclusive raster width',
}
ALLOWED_ESTIMATION_PAIRS = frozenset(
    [('ESM1', index) for index in (0, 146, 293)]
    + [('ESM4', index) for index in (0, 197, 394)]
)


def require_estimation_record(record):
    if (record.get('source_id'), record.get('frame_index')) not in ALLOWED_ESTIMATION_PAIRS or record.get('role') != 'estimation':
        raise ValueError('scale measurement restricted to the six canonical estimation images')


def corner_rectangle(width, height):
    if width < 408 or height < 148:
        raise ValueError('native image is too small for frozen corner rectangle')
    return (int(width * 0.62), int(height * 0.85), int(width * 0.98), int(height * 0.98))


def _runs(row, threshold, x0, x1):
    runs = []
    start = None
    for x in range(x0, x1 + 1):
        dark = x < x1 and int(row[x]) <= threshold
        if dark and start is None:
            start = x
        if not dark and start is not None:
            length = x - start
            if start > x0 and x < x1 and METHOD_CONFIG['minimum_run_px'] <= length <= METHOD_CONFIG['maximum_run_px']:
                runs.append((start, x - 1, length))
            start = None
    return runs


def measure_bar(plane, rectangle):
    """Measure only a fixed printed-bar corner; return unresolved on ambiguity."""
    x0, y0, x1, y1 = rectangle
    if not (0 <= y0 < y1 <= len(plane) and 0 <= x0 < x1 <= len(plane[0])):
        raise ValueError('scale rectangle outside native support')
    trials = []
    for threshold in METHOD_CONFIG['thresholds_inclusive']:
        candidates = [(y, *run) for y in range(y0, y1) for run in _runs(plane[y], threshold, x0, x1)]
        if not candidates:
            trials.append({'threshold': threshold, 'status': 'UNRESOLVED', 'reason': 'no eligible horizontal run'})
            continue
        longest = max(item[3] for item in candidates)
        close = [item for item in candidates if item[3] >= longest - METHOD_CONFIG['row_length_tolerance_px']]
        groups = []
        for item in close:
            if groups and item[0] == groups[-1][-1][0] + 1 and abs(item[1] - groups[-1][-1][1]) <= 2 and abs(item[2] - groups[-1][-1][2]) <= 2:
                groups[-1].append(item)
            else:
                groups.append([item])
        groups = [group for group in groups if len(group) >= METHOD_CONFIG['minimum_consecutive_rows']]
        if len(groups) != 1:
            trials.append({'threshold': threshold, 'status': 'UNRESOLVED', 'reason': 'no unique consecutive multi-row bar', 'candidate_groups': len(groups)})
            continue
        group = groups[0]
        counts = Counter((item[1], item[2]) for item in group)
        endpoints = sorted(counts, key=lambda pair: (-counts[pair], pair))[0]
        trials.append({
            'threshold': threshold, 'status': 'MEASURED',
            'endpoints_center_x': list(endpoints),
            'rows': [item[0] for item in group],
            'row_lengths_px': [item[3] for item in group],
            'length_px': endpoints[1] - endpoints[0] + 1,
        })
    successes = [trial for trial in trials if trial['status'] == 'MEASURED']
    result = {'rectangle_xyxy_exclusive': list(rectangle), 'threshold_trials': trials}
    if len(successes) < METHOD_CONFIG['minimum_successful_thresholds']:
        return dict(result, status='UNRESOLVED', reason='insufficient stable threshold evidence')
    endpoints = [tuple(trial['endpoints_center_x']) for trial in successes]
    endpoint_counts = Counter(endpoints)
    selected = sorted(endpoint_counts, key=lambda pair: (-endpoint_counts[pair], pair))[0]
    lengths = [length for trial in successes for length in trial['row_lengths_px']]
    length = selected[1] - selected[0] + 1
    bound = METHOD_CONFIG['endpoint_raster_bound_px'] + max(abs(value - length) for value in lengths)
    return dict(result, status='MEASURED', length_px=length,
                endpoints_center_x=list(selected), endpoints_edge_x=[selected[0] - 0.5, selected[1] + 0.5],
                center_to_center_span_px=selected[1] - selected[0],
                measured_length_range_px=[min(lengths), max(lengths)],
                length_uncertainty_bound_px=bound)


def summarize_condition(measurements):
    """Conservative raster sensitivity bound; acquisition metrology stays explicit."""
    if len(measurements) != 3 or any(item['status'] != 'MEASURED' for item in measurements):
        return {'scale_status': 'UNRESOLVED', 'coordinate_unit': 'pixel', 'reason': 'three stable estimation-frame bar measurements required'}
    lengths = [item['length_px'] for item in measurements]
    length = median(lengths)
    bound = max(item['length_uncertainty_bound_px'] + abs(item['length_px'] - length) for item in measurements)
    if length <= bound:
        return {'scale_status': 'UNRESOLVED', 'coordinate_unit': 'pixel', 'reason': 'bar extent uncertainty includes zero'}
    nominal = METHOD_CONFIG['nominal_printed_bar_micrometres']
    value = nominal / length
    interval = [nominal / (length + bound), nominal / (length - bound)]
    return {
        'scale_status': 'BAR_GEOMETRY_MEASURED',
        'nominal_printed_bar_micrometres': nominal,
        'bar_length_px': length, 'bar_length_uncertainty_bound_px': bound,
        'estimation_frame_lengths_px': lengths,
        'horizontal_micrometres_per_pixel': value,
        'horizontal_raster_uncertainty_bound_micrometres_per_pixel': max(value - interval[0], interval[1] - value),
        'horizontal_scale_interval_micrometres_per_pixel': interval,
        'uncertainty_kind': 'conservative endpoint/threshold/row/time bound; not a statistical confidence interval',
        'nominal_label_metrology_uncertainty': 'UNRESOLVED; no independent acquisition calibration supplied',
        'vertical_scale_status': 'NOT_VERIFIED; horizontal printed bar does not independently prove isotropic physical sampling',
        'applicability': 'native horizontal pixel distances of this canonical source only; no transfer to unregistered modalities',
        'full_physical_calibration_status': 'UNRESOLVED',
        'orientation_status': 'NOT_VERIFIED',
    }
