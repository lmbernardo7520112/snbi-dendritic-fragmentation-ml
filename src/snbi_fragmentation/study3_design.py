"""Pure Study3 schedule bound to the existing historical TRAIN identities.

This module never creates a split, reads a path, or grants execution authority.
"""

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json

from .study3_domain import (ACQUISITIONS, RepresentationKind, Study3FitSpec,
                            TrajectoryGroup, require, validate_groups)


EXPECTED_FOLD_SHA = "85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2"
EXPECTED_TRAIN_ROWS = {"GOLD": 3858, "BACKGROUND": 7049}
CLASSICAL = tuple(kind.value for kind in list(RepresentationKind)[:4])
FIT_CONDITIONS = tuple(kind.value for kind in RepresentationKind
                       if kind is not RepresentationKind.ACQUISITION_ONLY)
FIT_BUDGET = {"RF": 16, "CNN1D": 4, "SPATIOTEMPORAL_CNN": 4,
              "METADATA_LOGREG": 4, "ACQUISITION_ONLY": 0, "total_distinct": 28}


def json_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def group_trajectories(rows):
    require(isinstance(rows, (list, tuple)) and bool(rows), "explicit nonempty TRAIN rows required")
    grouped = defaultdict(list)
    for row in rows:
        require(type(row) is dict and row.get("split") == "TRAIN", "DEV/TEST denied before grouping")
        require(type(row.get("group_id")) is str and row["group_id"], "explicit group identity required")
        grouped[row["group_id"]].append(row)
    groups = [TrajectoryGroup.from_rows(grouped[gid]) for gid in sorted(grouped)]
    validate_groups(groups)
    return groups


def validate_population(rows, historical_folds):
    """Authenticate the immutable counts, identities and historical fold digest."""
    groups = group_trajectories(rows)
    require(len(groups) == 64 and Counter(group.label for group in groups) == {0: 32, 1: 32},
            "exactly 64 historical TRAIN groups (32/32) required")
    require(Counter(row["tier"] for row in rows) == EXPECTED_TRAIN_ROWS,
            "exact historical 3858 GOLD and 7049 BACKGROUND rows required")
    require(type(historical_folds) is dict and set(historical_folds) == {str(g.group_id) for g in groups}
            and json_sha(historical_folds) == EXPECTED_FOLD_SHA,
            "historical fold identities/hash differ; fold regeneration forbidden")
    for group in groups:
        fold = historical_folds[group.group_id]
        require(type(fold) is int and fold in range(4) and fold == group.cv_fold,
                "row fold differs from authenticated historical fold")
    for fold in range(4):
        strata = Counter((str(g.acquisition_id), g.label) for g in groups if g.cv_fold == fold)
        require(strata == {(a, label): count for a, count in zip(ACQUISITIONS, (6, 2))
                           for label in (0, 1)}, "historical fold acquisition/class identities differ")
    return groups


def design_contract():
    return {"population": "HISTORICAL_STUDY2C_TRAIN_ONLY", "rows": 10907,
            "rows_by_tier": dict(EXPECTED_TRAIN_ROWS), "groups": 64,
            "groups_by_class": {"0": 32, "1": 32}, "fold_ids": [0, 1, 2, 3],
            "historical_fold_sha256": EXPECTED_FOLD_SHA,
            "primary_unit": "GROUP_TRAJECTORY", "row_order": ["frame_index", "sample_id"],
            "classical_conditions": list(CLASSICAL), "fit_conditions": list(FIT_CONDITIONS),
            "fit_order": "condition in frozen list, then fold 0..3",
            "fit_budget": dict(FIT_BUDGET), "adaptive_tuning": False,
            "development_access": False, "test_access": False, "test_remains_consumed": True}


def _fit_specs(groups):
    specs = []
    for condition in FIT_CONDITIONS:
        for fold in range(4):
            spec = Study3FitSpec(f"{condition}-f{fold}", condition, fold,
                tuple(g.group_id for g in groups if g.cv_fold != fold),
                tuple(g.group_id for g in groups if g.cv_fold == fold))
            value = asdict(spec)
            value["condition"] = spec.condition.value
            value["fold"] = int(spec.fold)
            value["training_group_ids"] = [str(gid) for gid in spec.training_group_ids]
            value["validation_group_ids"] = [str(gid) for gid in spec.validation_group_ids]
            specs.append(value)
    return specs


def _group_metadata(groups):
    return [{"group_id": str(g.group_id), "acquisition_id": str(g.acquisition_id), "label": g.label,
             "split": "TRAIN", "cv_fold": int(g.cv_fold), "n_rows": g.n_rows,
             "sample_ids": [str(row.sample_id) for row in g.observations]} for g in groups]


def build_study3_design(train_rows, historical_folds):
    groups = validate_population(train_rows, historical_folds)
    design = {"status": "PASS", "schema_version": 1, "contract": design_contract(),
              "rows": deepcopy(train_rows), "groups": _group_metadata(groups),
              "group_ids": [str(g.group_id) for g in groups],
              "cv_fold_by_group": deepcopy(historical_folds),
              "historical_fold_sha256": EXPECTED_FOLD_SHA,
              "population_sha256": json_sha(train_rows), "fits": _fit_specs(groups),
              "fit_budget": dict(FIT_BUDGET), "TRAIN_ONLY": True}
    design["design_sha256"] = json_sha(design)
    validate_study3_design(design)
    return design


def validate_study3_design(design):
    require(type(design) is dict and design.get("status") == "PASS" and design.get("schema_version") == 1,
            "frozen Study3 design required")
    require(design.get("design_sha256") == json_sha({k: v for k, v in design.items() if k != "design_sha256"}),
            "design hash differs")
    require(json_sha(design.get("contract")) == json_sha(design_contract())
            and json_sha(design.get("fit_budget")) == json_sha(FIT_BUDGET)
            and design.get("TRAIN_ONLY") is True, "frozen method or access contract differs")
    groups = validate_population(design.get("rows"), design.get("cv_fold_by_group"))
    require(design.get("population_sha256") == json_sha(design["rows"])
            and design.get("historical_fold_sha256") == EXPECTED_FOLD_SHA, "population or fold digest differs")
    require(json_sha(design.get("groups")) == json_sha(_group_metadata(groups))
            and design.get("group_ids") == [str(g.group_id) for g in groups], "group ledger differs")
    require(json_sha(design.get("fits")) == json_sha(_fit_specs(groups)),
            "exact 28-fit schedule or fold isolation differs")
    return {"status": "PASS", "rows": 10907, "groups": 64, "folds": 4, "distinct_fits": 28}


class FitBudget:
    """Receipt-independent in-memory ledger: consume each slot before its fit.

    A failed fit remains consumed. This object grants no scientific authority;
    the controller must establish receipt and authorization before callbacks.
    """

    def __init__(self, specs):
        require(type(specs) is list and len(specs) == 28, "exactly 28 fit specifications required")
        expected = [(kind, fold, f"{kind}-f{fold}") for kind in FIT_CONDITIONS for fold in range(4)]
        require(all(type(spec) is dict and type(spec.get("fold")) is int for spec in specs),
                "exact integer fold specifications required")
        require([(spec.get("condition"), spec.get("fold"), spec.get("fit_id")) for spec in specs] == expected,
                "fit budget identities/order differ")
        self._specs = deepcopy(specs)
        self._started = []
        self._completed = []

    def start(self, fit_id):
        position = len(self._started)
        require(position < 28, "fit 29 forbidden")
        require(len(self._completed) == position, "unfinished fit consumed; retry forbidden")
        require(fit_id == self._specs[position]["fit_id"], "fit reuse, reordering or model search forbidden")
        self._started.append(fit_id)

    def complete(self, fit_id):
        require(len(self._started) == len(self._completed) + 1 and self._started[-1] == fit_id,
                "completion requires its single pending fit")
        self._completed.append(fit_id)

    def snapshot(self):
        return {"fit_budget": 28, "started": list(self._started), "completed": list(self._completed),
                "distinct_fits_started": len(self._started), "distinct_fits_completed": len(self._completed)}
