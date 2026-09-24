"""Group-unit metrics and the seven fixed descriptive contrasts; no selection."""

import math
import statistics

from .study3_domain import ACQUISITIONS, RepresentationKind, Study3MetricBundle, require


CONTRASTS = {
    "MEDIAN_MINUS_D1": ("TRAJECTORY_MEDIAN_LBP20", "D1_LBP20"),
    "CNN1D_MINUS_D1": ("TEMPORAL_CNN1D_LBP20", "D1_LBP20"),
    "SPATIOTEMPORAL_MINUS_D1": ("SPATIOTEMPORAL_CNN_SMALL", "D1_LBP20"),
    "SPATIOTEMPORAL_MINUS_MEDIAN": ("SPATIOTEMPORAL_CNN_SMALL", "TRAJECTORY_MEDIAN_LBP20"),
    "SPATIOTEMPORAL_MINUS_CNN1D": ("SPATIOTEMPORAL_CNN_SMALL", "TEMPORAL_CNN1D_LBP20"),
    "MEAN_MINUS_D1": ("TRAJECTORY_MEAN_LBP20", "D1_LBP20"),
    "Q2575_MINUS_D1": ("TRAJECTORY_Q2575_LBP60", "D1_LBP20"),
}


def _binary_sequence(values):
    # ndarray.tolist is a conversion only; no features, probabilities or labels
    # are inferred. bool is intentionally not a valid binary class spelling.
    values = values.tolist() if hasattr(values, "tolist") else values
    require(isinstance(values, (list, tuple)) and bool(values)
            and all(type(value) is int and value in (0, 1) for value in values),
            "explicit nonempty exact binary sequence required")
    return list(values)


def _metrics(labels, predicted, require_both):
    require(not require_both or set(labels) == {0, 1}, "primary GMBA requires both group classes")
    matrix = [[sum(y == actual and p == prediction for y, p in zip(labels, predicted))
               for prediction in (0, 1)] for actual in (0, 1)]
    (tn, fp), (fn, tp) = matrix
    recall = tp / (tp + fn) if tp + fn else None
    specificity = tn / (tn + fp) if tn + fp else None
    gmba = (recall + specificity) / 2 if recall is not None and specificity is not None else None
    precision = tp / (tp + fp) if tp + fp else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    result = {"primary_metric": "GROUP_MACRO_BALANCED_ACCURACY", "primary_gmba": gmba,
              "group_macro_balanced_accuracy": gmba, "accuracy": (tp + tn) / len(labels),
              "precision": precision, "recall": recall, "specificity": specificity,
              "f1": f1, "confusion_matrix": matrix, "confusion_matrix_labels": [0, 1],
              "group_count": len(labels), "zero_division_precision_f1": 0,
              "missing_class_gmba": "null"}
    if require_both:
        Study3MetricBundle(gmba, result["accuracy"], precision, recall, specificity,
                           f1, tuple(tuple(row) for row in matrix))
    return result


def group_metrics(labels, predictions, acquisitions=None, group_ids=None):
    """Each aligned input element is exactly one group prediction."""
    labels, predictions = _binary_sequence(labels), _binary_sequence(predictions)
    require(len(labels) == len(predictions), "group prediction count mismatch")
    if group_ids is not None:
        require(isinstance(group_ids, (list, tuple)) and len(group_ids) == len(labels)
                and len(set(group_ids)) == len(group_ids)
                and all(isinstance(gid, str) and gid for gid in group_ids),
                "unique aligned group identities required")
    result = _metrics(labels, predictions, True)
    if acquisitions is not None:
        require(isinstance(acquisitions, (list, tuple)) and len(acquisitions) == len(labels)
                and all(acquisition in ACQUISITIONS for acquisition in acquisitions),
                "aligned historical acquisition identities required")
        result["per_acquisition"] = {}
        for acquisition in ACQUISITIONS:
            indices = [i for i, a in enumerate(acquisitions) if a == acquisition]
            result["per_acquisition"][acquisition] = (_metrics([labels[i] for i in indices],
                [predictions[i] for i in indices], False) if indices else None)
    return result


def descriptive_stats(values):
    require(isinstance(values, (list, tuple)) and bool(values)
            and all(type(value) in (int, float) and math.isfinite(value) for value in values),
            "finite recorded scores required")
    mean = math.fsum(values) / len(values)
    return {"mean": mean, "median": statistics.median(values),
            "std": math.sqrt(math.fsum((value - mean) ** 2 for value in values) / len(values)),
            "std_ddof": 0, "min": min(values), "max": max(values), "n": len(values)}


def describe_delta(deltas):
    require(isinstance(deltas, (list, tuple)) and len(deltas) == 4, "four paired fold deltas required")
    result = descriptive_stats(deltas)
    result.update(paired_fold_deltas=list(deltas),
                  positive_fold_count=sum(value > 0 for value in deltas),
                  zero_fold_count=sum(value == 0 for value in deltas),
                  negative_fold_count=sum(value < 0 for value in deltas))
    result["descriptor"] = ("CONSISTENT_POSITIVE_INTERNAL" if result["mean"] > 0
                            and result["positive_fold_count"] >= 3 else
                            "MIXED_POSITIVE_INTERNAL" if result["mean"] > 0 else "NON_POSITIVE_INTERNAL")
    result["significance_test"] = False
    return result


def summarize_contrasts(scores_by_condition):
    require(type(scores_by_condition) is dict, "recorded fold score mapping required")
    required = {condition for pair in CONTRASTS.values() for condition in pair}
    require(required <= set(scores_by_condition) <= {kind.value for kind in RepresentationKind},
            "all preregistered temporal conditions and no new model families required")
    scores = {}
    for condition, values in scores_by_condition.items():
        if type(values) is dict:
            require(set(values) == {0, 1, 2, 3} and all(type(key) is int for key in values),
                    "four explicitly identified integer folds required")
            values = [values[fold] for fold in range(4)]
        require(isinstance(values, (list, tuple)) and len(values) == 4, "four ordered fold scores required")
        descriptive_stats(values)
        require(all(0 <= value <= 1 for value in values), "GMBA outside [0,1]")
        scores[condition] = values
    return {name: dict(describe_delta([scores[positive][fold] - scores[reference][fold]
                                     for fold in range(4)]), positive_condition=positive,
                       reference_condition=reference, primary=name not in {"MEAN_MINUS_D1", "Q2575_MINUS_D1"})
            for name, (positive, reference) in CONTRASTS.items()}
