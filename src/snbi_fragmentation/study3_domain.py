"""Immutable Study3 identities and contracts; no I/O or experimental authority.

A positive site is not a physical event, a candidate background track is not
physical absence, and a trajectory is not an independent experiment.
"""

from dataclasses import dataclass
from enum import Enum
import math


ACQUISITIONS = ("bottom_up_anti_parallel", "top_down_parallel")
FRAME_MAX = dict(zip(ACQUISITIONS, (293, 394)))


class Study3DomainError(ValueError):
    """An identity or immutable scientific contract is invalid."""


def require(condition, message):
    if not condition:
        raise Study3DomainError(message)


class _Identity(str):
    def __new__(cls, value):
        require(isinstance(value, str) and bool(value.strip()) and value == value.strip(),
                f"nonempty canonical {cls.__name__} required")
        return str.__new__(cls, value)


class AcquisitionId(_Identity):
    def __new__(cls, value):
        require(value in ACQUISITIONS, "unknown acquisition")
        return super().__new__(cls, value)


class GroupId(_Identity):
    """Historical group identity, never a newly mined site."""


class PositiveSiteId(_Identity):
    """Weakly supervised site identity, not a physical event."""


class BackgroundTrackId(_Identity):
    """Candidate background track, not verified physical absence."""


class ObservationId(_Identity):
    """Historical row identity."""


class FrameIndex(int):
    def __new__(cls, value):
        require(type(value) in (int, FrameIndex) and value >= 0, "nonnegative integer frame required")
        return int.__new__(cls, value)


class FoldId(int):
    def __new__(cls, value):
        require(type(value) in (int, FoldId) and value in range(4), "historical fold 0..3 required")
        return int.__new__(cls, value)


class WeakLabel(str, Enum):
    GOLD = "GOLD"
    BACKGROUND = "BACKGROUND"

    @property
    def binary(self):
        return int(self is WeakLabel.GOLD)


class RepresentationKind(str, Enum):
    D1_LBP20 = "D1_LBP20"
    TRAJECTORY_MEAN_LBP20 = "TRAJECTORY_MEAN_LBP20"
    TRAJECTORY_MEDIAN_LBP20 = "TRAJECTORY_MEDIAN_LBP20"
    TRAJECTORY_Q2575_LBP60 = "TRAJECTORY_Q2575_LBP60"
    TEMPORAL_CNN1D_LBP20 = "TEMPORAL_CNN1D_LBP20"
    SPATIOTEMPORAL_CNN_SMALL = "SPATIOTEMPORAL_CNN_SMALL"
    COVERAGE_METADATA_LOGREG = "COVERAGE_METADATA_LOGREG"
    ACQUISITION_ONLY = "ACQUISITION_ONLY"


@dataclass(frozen=True)
class TrajectoryObservation:
    sample_id: ObservationId
    group_id: GroupId
    acquisition_id: AcquisitionId
    frame_index: FrameIndex
    label: int
    tier: WeakLabel
    cv_fold: FoldId
    split: str = "TRAIN"
    site_id: PositiveSiteId | None = None
    background_track_id: BackgroundTrackId | None = None

    def __post_init__(self):
        # Split and label admission precede any optional provenance handling.
        require(self.split == "TRAIN", "only historical TRAIN observations admitted")
        require(type(self.label) is int and self.label in (0, 1), "exact binary class required")
        try:
            tier = WeakLabel(self.tier)
        except (ValueError, TypeError) as exc:
            raise Study3DomainError("only GOLD/BACKGROUND weak labels admitted") from exc
        require(tier.binary == self.label, "tier/class mismatch")
        for name, constructor in (("sample_id", ObservationId), ("group_id", GroupId),
                                  ("acquisition_id", AcquisitionId), ("frame_index", FrameIndex),
                                  ("cv_fold", FoldId)):
            object.__setattr__(self, name, constructor(getattr(self, name)))
        object.__setattr__(self, "tier", tier)
        require(self.frame_index <= FRAME_MAX[self.acquisition_id], "frame outside acquisition")
        require(not (self.site_id is not None and self.background_track_id is not None),
                "positive site and background track are exclusive")
        if self.site_id is not None:
            require(self.label == 1, "background cannot claim positive site")
            object.__setattr__(self, "site_id", PositiveSiteId(self.site_id))
        if self.background_track_id is not None:
            require(self.label == 0, "positive cannot claim background track")
            object.__setattr__(self, "background_track_id", BackgroundTrackId(self.background_track_id))

    @classmethod
    def from_row(cls, row):
        require(type(row) is dict and row.get("split") == "TRAIN", "TRAIN row dictionary required")
        names = ("sample_id", "group_id", "acquisition_id", "frame_index", "label", "tier", "cv_fold")
        require(all(name in row for name in names), "incomplete historical row identity")
        return cls(**{name: row[name] for name in names}, split=row["split"],
                   site_id=row.get("site_id"), background_track_id=row.get("background_track_id"))


@dataclass(frozen=True)
class TrajectoryGroup:
    group_id: GroupId
    acquisition_id: AcquisitionId
    label: int
    observations: tuple[TrajectoryObservation, ...]

    def __post_init__(self):
        object.__setattr__(self, "group_id", GroupId(self.group_id))
        object.__setattr__(self, "acquisition_id", AcquisitionId(self.acquisition_id))
        require(type(self.label) is int and self.label in (0, 1), "exact group label required")
        require(type(self.observations) is tuple and bool(self.observations)
                and all(type(row) is TrajectoryObservation for row in self.observations),
                "nonempty immutable observation tuple required")
        require(all((row.group_id, row.acquisition_id, row.label, row.split) ==
                    (self.group_id, self.acquisition_id, self.label, "TRAIN")
                    for row in self.observations), "group crosses acquisition/class/split")
        require(len({row.cv_fold for row in self.observations}) == 1, "group crosses historical fold")
        require(len({row.sample_id for row in self.observations}) == len(self.observations),
                "duplicate observation identity")
        object.__setattr__(self, "observations", tuple(sorted(
            self.observations, key=lambda row: (row.frame_index, row.sample_id))))

    @classmethod
    def from_rows(cls, rows):
        require(isinstance(rows, (list, tuple)) and bool(rows), "nonempty group rows required")
        observations = tuple(row if type(row) is TrajectoryObservation else
                             TrajectoryObservation.from_row(row) for row in rows)
        first = observations[0]
        return cls(first.group_id, first.acquisition_id, first.label, observations)

    @property
    def cv_fold(self):
        return self.observations[0].cv_fold

    @property
    def n_rows(self):
        return len(self.observations)

    @property
    def first_frame(self):
        return self.observations[0].frame_index

    @property
    def last_frame(self):
        return self.observations[-1].frame_index


def validate_groups(groups):
    """Validate an arbitrary nonempty fold subset, without granting source access."""
    require(isinstance(groups, (tuple, list)) and bool(groups)
            and all(type(group) is TrajectoryGroup for group in groups), "typed trajectory groups required")
    require(len({group.group_id for group in groups}) == len(groups), "duplicate group identity")
    ids = [row.sample_id for group in groups for row in group.observations]
    require(len(set(ids)) == len(ids), "observation crosses group")
    return groups


@dataclass(frozen=True)
class TemporalSelection:
    group_id: GroupId
    selected_sample_ids: tuple[ObservationId, ...]
    selected_frame_indices: tuple[FrameIndex, ...]
    rank_targets: tuple[float, ...]
    selected_ranks: tuple[int, ...]
    duplicate_flags: tuple[bool, ...]

    def __post_init__(self):
        GroupId(self.group_id)
        fields = (self.selected_sample_ids, self.selected_frame_indices, self.rank_targets,
                  self.selected_ranks, self.duplicate_flags)
        require(all(type(values) is tuple and len(values) == 8 for values in fields), "T must equal eight")
        for sid in self.selected_sample_ids:
            ObservationId(sid)
        for frame in self.selected_frame_indices:
            FrameIndex(frame)
        require(all(type(rank) is int and rank >= 0 for rank in self.selected_ranks), "invalid selected rank")
        require(all(type(value) in (int, float) and math.isfinite(value) and value >= 0
                    for value in self.rank_targets), "invalid rank target")
        require(all(type(flag) is bool for flag in self.duplicate_flags), "exact duplicate booleans required")
        require(self.duplicate_flags == tuple(sid in self.selected_sample_ids[:i]
                    for i, sid in enumerate(self.selected_sample_ids)), "duplicate flags differ")
        last_rank = self.rank_targets[-1]
        require(int(last_rank) == last_rank, "endpoint must be a real integer observation rank")
        last_rank = int(last_rank)
        require(self.rank_targets == tuple(k * last_rank / 7 for k in range(8)), "T8 rank targets differ")
        expected_ranks = []
        for k in range(8):
            rank, remainder = divmod(k * last_rank, 7)
            expected_ranks.append(rank + int(2 * remainder > 7))
        require(self.selected_ranks == tuple(expected_ranks), "nearest lower-tie ranks differ")
        require(tuple(sorted(self.selected_frame_indices)) == self.selected_frame_indices,
                "selected real frames must retain temporal order")
        for i in range(8):
            for j in range(i):
                same_rank = self.selected_ranks[i] == self.selected_ranks[j]
                require((self.selected_sample_ids[i] == self.selected_sample_ids[j]) == same_rank,
                        "sample identity does not bind selected real row rank")
                require(not same_rank or self.selected_frame_indices[i] == self.selected_frame_indices[j],
                        "repeated observation cannot change frame")


@dataclass(frozen=True)
class TemporalRepresentation:
    group_id: GroupId
    kind: RepresentationKind
    values: tuple[float, ...]

    def __post_init__(self):
        GroupId(self.group_id)
        kind = RepresentationKind(self.kind)
        object.__setattr__(self, "kind", kind)
        dimensions = {RepresentationKind.D1_LBP20: 20, RepresentationKind.TRAJECTORY_MEAN_LBP20: 20,
                      RepresentationKind.TRAJECTORY_MEDIAN_LBP20: 20,
                      RepresentationKind.TRAJECTORY_Q2575_LBP60: 60}
        require(kind in dimensions and type(self.values) is tuple and len(self.values) == dimensions[kind]
                and all(type(value) in (int, float) and math.isfinite(value) for value in self.values),
                "finite classical representation with frozen dimension required")


@dataclass(frozen=True)
class Study3FitSpec:
    fit_id: str
    condition: RepresentationKind
    fold: FoldId
    training_group_ids: tuple[GroupId, ...]
    validation_group_ids: tuple[GroupId, ...]

    def __post_init__(self):
        kind = RepresentationKind(self.condition)
        object.__setattr__(self, "condition", kind)
        object.__setattr__(self, "fold", FoldId(self.fold))
        require(kind is not RepresentationKind.ACQUISITION_ONLY, "acquisition control has no fit")
        require(self.fit_id == f"{kind.value}-f{self.fold}", "fit identity does not bind condition/fold")
        for values in (self.training_group_ids, self.validation_group_ids):
            require(type(values) is tuple and bool(values) and len(set(values)) == len(values),
                    "nonempty unique immutable fold identities required")
            for gid in values:
                GroupId(gid)
        require(not set(self.training_group_ids) & set(self.validation_group_ids), "group crosses fold side")


@dataclass(frozen=True)
class Study3MetricBundle:
    group_macro_balanced_accuracy: float
    accuracy: float
    precision: float
    recall: float
    specificity: float
    f1: float
    confusion_matrix: tuple[tuple[int, int], tuple[int, int]]

    def __post_init__(self):
        for value in (self.group_macro_balanced_accuracy, self.accuracy, self.precision,
                      self.recall, self.specificity, self.f1):
            require(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1,
                    "finite metrics in [0,1] required")
        matrix = self.confusion_matrix
        require(type(matrix) is tuple and len(matrix) == 2 and all(type(row) is tuple and len(row) == 2
                and all(type(value) is int and value >= 0 for value in row) for row in matrix),
                "integer binary confusion matrix required")
        require(sum(sum(row) for row in matrix) > 0, "empty metric population")
        (tn, fp), (fn, tp) = matrix
        require(tn + fp > 0 and fn + tp > 0, "primary metric bundle requires both group classes")
        recall = tp / (tp + fn)
        specificity = tn / (tn + fp)
        expected = ((recall + specificity) / 2, (tp + tn) / (tn + fp + fn + tp),
                    tp / (tp + fp) if tp + fp else 0.0, recall, specificity,
                    2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
        observed = (self.group_macro_balanced_accuracy, self.accuracy, self.precision,
                    self.recall, self.specificity, self.f1)
        require(observed == expected, "reported metrics must match group confusion matrix")


@dataclass(frozen=True)
class Study3Result:
    condition: RepresentationKind
    fold: FoldId
    group_ids: tuple[GroupId, ...]
    predictions: tuple[int, ...]
    metrics: Study3MetricBundle

    def __post_init__(self):
        object.__setattr__(self, "condition", RepresentationKind(self.condition))
        object.__setattr__(self, "fold", FoldId(self.fold))
        require(type(self.group_ids) is tuple and self.group_ids and len(set(self.group_ids)) == len(self.group_ids),
                "one prediction per unique group required")
        require(type(self.predictions) is tuple and len(self.predictions) == len(self.group_ids)
                and all(type(value) is int and value in (0, 1) for value in self.predictions),
                "exact binary predictions aligned to groups required")
        require(type(self.metrics) is Study3MetricBundle
                and sum(sum(row) for row in self.metrics.confusion_matrix) == len(self.group_ids),
                "metric count differs from prediction count")
        for prediction in (0, 1):
            require(sum(row[prediction] for row in self.metrics.confusion_matrix) ==
                    self.predictions.count(prediction), "prediction counts differ from confusion matrix")


@dataclass(frozen=True)
class Study3TerminalState:
    status: str
    scientific_runs: int
    distinct_fits: int
    dev_rows_read: int = 0
    test_rows_read: int = 0
    video_opens: int = 0
    retry_count: int = 0
    current_authorized_activity: str = "NONE_AWAITING_AUTHOR_DECISION"

    def __post_init__(self):
        require(self.status in {"PASS", "BLOCKED", "PRE_SCIENCE_FROZEN"}, "unknown terminal status")
        require(type(self.scientific_runs) is int and self.scientific_runs in (0, 1)
                and type(self.distinct_fits) is int and 0 <= self.distinct_fits <= 28, "invalid execution counters")
        require(all(type(value) is int and value == 0 for value in
                    (self.dev_rows_read, self.test_rows_read, self.video_opens, self.retry_count)),
                "forbidden access or retry cannot pass terminal contract")
        require(self.current_authorized_activity == "NONE_AWAITING_AUTHOR_DECISION", "terminal scope must close")
        require(self.scientific_runs != 0 or self.distinct_fits == 0, "fits require an execution invocation")
        if self.status == "PASS":
            require((self.scientific_runs, self.distinct_fits) == (1, 28), "PASS requires exactly 28 completed fits")
        if self.status == "PRE_SCIENCE_FROZEN":
            require((self.scientific_runs, self.distinct_fits) == (0, 0), "pre-science terminal cannot contain fits")
