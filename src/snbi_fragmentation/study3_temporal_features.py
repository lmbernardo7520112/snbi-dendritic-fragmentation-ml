"""Fixed temporal reductions of already admitted, in-memory TRAIN features.

No cache access or LBP extraction occurs here. Selection always references a
real historical observation; repeats never interpolate or fabricate pixels.
"""

from dataclasses import asdict

from .study3_design import CLASSICAL, group_trajectories
from .study3_domain import TemporalSelection, TrajectoryGroup, require


def nearest_rank_lower(numerator, denominator):
    require(type(numerator) is int and numerator >= 0 and type(denominator) is int and denominator > 0,
            "nonnegative rational rank required")
    rank, remainder = divmod(numerator, denominator)
    return rank + int(2 * remainder > denominator)


def _group(group_or_rows):
    return group_or_rows if type(group_or_rows) is TrajectoryGroup else TrajectoryGroup.from_rows(group_or_rows)


def select_d1(group_or_rows):
    group = _group(group_or_rows)
    return group.observations[(group.n_rows - 1) // 2]


def select_t8(group_or_rows):
    group = _group(group_or_rows)
    n = group.n_rows
    ranks = tuple(nearest_rank_lower(k * (n - 1), 7) for k in range(8))
    selected = tuple(group.observations[rank] for rank in ranks)
    ids = tuple(row.sample_id for row in selected)
    selection = TemporalSelection(group.group_id, ids, tuple(row.frame_index for row in selected),
                                  tuple(k * (n - 1) / 7 for k in range(8)), ranks,
                                  tuple(sid in ids[:i] for i, sid in enumerate(ids)))
    # JSON-safe lists make the exact ledger directly persistable.
    return {name: list(value) if isinstance(value, tuple) else value
            for name, value in asdict(selection).items()}


def summarize_lbp20(group_or_rows, lbp_by_sample_id):
    import numpy as np

    group = _group(group_or_rows)
    require(type(lbp_by_sample_id) is dict, "explicit sample-keyed features required")
    features = []
    for row in group.observations:
        require(row.sample_id in lbp_by_sample_id, "missing admitted observation feature")
        value = lbp_by_sample_id[row.sample_id]
        require(isinstance(value, np.ndarray) and value.shape == (20,)
                and np.issubdtype(value.dtype, np.floating) and bool(np.isfinite(value).all()),
                "finite 20-dimensional floating LBP required")
        features.append(value)
    values = np.asarray(features, dtype=np.float64)
    return {"D1_LBP20": values[(len(values) - 1) // 2].copy(),
            "TRAJECTORY_MEAN_LBP20": np.mean(values, axis=0),
            "TRAJECTORY_MEDIAN_LBP20": np.median(values, axis=0),
            "TRAJECTORY_Q2575_LBP60": np.quantile(values, [0.25, 0.50, 0.75], axis=0,
                                                  method="linear").reshape(60)}


def build_representations(rows, lbp_by_sample_id):
    import numpy as np

    groups = group_trajectories(rows)
    require(type(lbp_by_sample_id) is dict and set(lbp_by_sample_id) ==
            {row.sample_id for group in groups for row in group.observations},
            "features must match admitted TRAIN observations exactly")
    classical = {name: [] for name in CLASSICAL}
    selections, temporal = [], []
    for group in groups:
        summaries = summarize_lbp20(group, lbp_by_sample_id)
        for name in CLASSICAL:
            classical[name].append(summaries[name])
        selected = select_t8(group)
        selections.append(selected)
        temporal.append(np.stack([lbp_by_sample_id[sid] for sid in selected["selected_sample_ids"]], axis=1))
    return {"group_ids": [str(g.group_id) for g in groups], "groups": groups,
            "labels": np.asarray([g.label for g in groups], dtype=np.int64),
            "acquisitions": [str(g.acquisition_id) for g in groups],
            "classical": {name: np.asarray(values, dtype=np.float64) for name, values in classical.items()},
            "temporal_lbp": np.asarray(temporal, dtype=np.float64), "selections": selections}
