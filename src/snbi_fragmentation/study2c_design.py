"""Pure metadata design, group weights and frozen Study2-C metrics.

No filesystem, pixels, arrays, decoder, feature extractor or learner is used.
The caller authenticates the immutable Study2-B ledgers before invoking the
design. TEST membership is a logical group reservation with prior exposure.
"""

from collections import Counter, defaultdict
import hashlib
import json
import math
from numbers import Integral


ACQUISITIONS = ("bottom_up_anti_parallel", "top_down_parallel")
SPLITS = ("TRAIN", "DEVELOPMENT", "TEST")
QUOTAS = {
    "bottom_up_anti_parallel": (24, 8, 8),
    "top_down_parallel": (8, 2, 2),
}
SOURCE_PAIRS = {
    "bottom_up_anti_parallel": ("ESM1", "ESM2", 294),
    "top_down_parallel": ("ESM4", "ESM5", 395),
}
TIERS = {"DIRECT_VALID": "GOLD", "TEMPORAL_SUPPORTED_AMBIGUOUS": "SILVER",
         "PRE_FIRST_CONFIDENT_ANNOTATION": "UNLABELED_PRE",
         "PERSISTENCE_EXPECTED_UNRESOLVED": "UNLABELED_PERSISTENCE"}
PAIR_STATUSES = {"VALID_PAIR", "INVALID_STRUCTURAL_SUPPORT", "INVALID_SOLUTAL_SUPPORT",
                 "INVALID_BOTH", "DECODE_ERROR"}
INDEX_PATH = "data/derived/study2b/corpus-index.jsonl"
BACKGROUND_PATH = "data/derived/study2b/background-pool.jsonl"


class DesignContractError(ValueError):
    """Missing or inconsistent frozen metadata never grants model authority."""


def _require(value, message):
    if not value:
        raise DesignContractError(message)


def _sha(value):
    return (type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def _json_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def _rank(prefix, *parts):
    return hashlib.sha256("|".join((prefix, *map(str, parts))).encode("utf-8")).hexdigest()


def _location(row):
    _require(type(row) is dict, "record must be an explicit object")
    acquisition = row.get("acquisition_id")
    _require(acquisition in SOURCE_PAIRS, "unknown acquisition")
    structural, solutal, frames = SOURCE_PAIRS[acquisition]
    _require(row.get("structural_source_id") == structural
             and row.get("solutal_source_id") == solutal, "cross-source/acquisition record")
    frame = row.get("frame_index")
    _require(type(frame) is int and 0 <= frame < frames, "invalid native frame index")
    x, y = row.get("center_x"), row.get("center_y")
    _require(type(x) is int and type(y) is int, "integer canonical crop center required")
    box = [x - 32, y - 32, x + 33, y + 33]
    _require(row.get("patch_xyxy") == box
             and all(type(v) is int for v in row["patch_xyxy"]), "unchanged 65x65 crop required")
    return acquisition, structural, solutal, frame, x, y, box


def _sample_location(row):
    return {key: (list(row[key]) if key == "patch_xyxy" else row[key])
            for key in ("acquisition_id", "frame_index", "structural_source_id",
                        "solutal_source_id", "center_x", "center_y", "patch_xyxy")}


def build_design(index_records, background_records):
    """Freeze deterministic group selection/splits from authenticated text only.

    GOLD and SILVER metadata are retained in every group split, allowing only
    future authorized TRAIN augmentation with SILVER. Evaluation targets remain
    GOLD/background. Invalid and longitudinal unlabeled rows are never samples.
    Hash class strings are exactly POSITIVE and BACKGROUND. CV folds are 0..3.
    """
    _require(type(index_records) is list and type(background_records) is list,
             "explicit corpus and background record lists required")
    positive_groups, background_groups = {}, {}
    positive_rows, background_rows = [], []
    index_keys, positive_row_indices, background_keys = set(), set(), set()
    excluded = Counter()
    for row in index_records:
        _require(type(row) is dict and row.get("pair_status") in PAIR_STATUSES,
                 "unknown corpus pair status")
        sid, frame = row.get("site_id"), row.get("frame_index")
        _require(type(sid) is str and sid and type(frame) is int,
                 "site/frame identity required")
        key = (sid, frame)
        _require(key not in index_keys, "duplicate corpus site/frame")
        index_keys.add(key)
        if row["pair_status"] != "VALID_PAIR":
            excluded["invalid_support_or_decode"] += 1
            continue
        tier = row.get("supervision_tier")
        _require(tier in TIERS.values() and TIERS.get(row.get("observation_state")) == tier,
                 "observation state/tier divergence")
        if tier.startswith("UNLABELED_"):
            excluded[tier] += 1
            continue
        acquisition, structural, solutal, frame, x, y, box = _location(row)
        group_id = row.get("group_id")
        _require(group_id == acquisition + "|" + sid, "positive group identity differs")
        _require(row.get("pair_id") == group_id + "|" + str(frame), "positive pair identity differs")
        row_index = row.get("row_index")
        _require(type(row_index) is int and row_index >= 0 and row_index not in positive_row_indices,
                 "unique original positive row index required")
        positive_row_indices.add(row_index)
        _require(all(_sha(row.get(k)) for k in ("structural_patch_sha256", "solutal_patch_sha256", "pair_sha256")),
                 "original positive patch hashes required")
        center = row.get("canonical_center_xy_px")
        _require(type(center) is list and len(center) == 2
                 and all(type(v) in (float, int) and math.isfinite(v) for v in center)
                 and [math.floor(v + 0.5) for v in center] == [x, y], "canonical center/rounding differs")
        signature = (acquisition, sid, x, y, tuple(center))
        group = positive_groups.setdefault(group_id, {"signature": signature, "gold": 0, "silver": 0})
        _require(group["signature"] == signature, "positive group center/provenance changed")
        group[tier.lower()] += 1
        sample = _sample_location(row)
        sample.update({"sample_id": "positive|" + row["pair_id"], "group_id": group_id,
                       "label": 1, "tier": tier, "kind": "positive", "site_id": sid,
                       "positive_row_index": row_index, "positive_pair_id": row["pair_id"],
                       "canonical_center_xy_px": list(center),
                       "study2b_provenance": {"artifact": INDEX_PATH, "pair_id": row["pair_id"],
                                                "original_row_index": row_index}})
        for name in ("structural_patch_sha256", "solutal_patch_sha256", "pair_sha256",
                     "structural_source_sha256", "solutal_source_sha256",
                     "structural_frame_sha256", "solutal_frame_sha256", "experimental_time_s"):
            if name in row:
                sample[name] = row[name]
        if "method_freeze_sha" in row:
            sample["study2b_method_freeze_sha"] = row["method_freeze_sha"]
        positive_rows.append(sample)
    positive_counts = Counter(group["signature"][0] for group in positive_groups.values())
    _require(dict(positive_counts) == {a: sum(QUOTAS[a]) for a in ACQUISITIONS},
             "positive valid-support group distribution must remain 40/12")
    _require(all(g["gold"] > 0 for g in positive_groups.values()), "every benchmark positive group requires GOLD")
    for row in background_records:
        acquisition, structural, solutal, frame, x, y, box = _location(row)
        track = row.get("background_track_id")
        _require(track == f"{acquisition}|{x}|{y}", "background track identity differs")
        key = (track, frame)
        _require(key not in background_keys, "duplicate background track/frame")
        background_keys.add(key)
        _require(row.get("status") == "BACKGROUND_CANDIDATE"
                 and row.get("exclusion_status") == "ALL_EXCLUSIONS_PASSED"
                 and row.get("pixels_materialized") is False
                 and row.get("physical_absence_inferred") is False,
                 "background frozen admissibility/semantics differs")
        _require(_sha(row.get("hash_rank")), "background provenance rank required")
        signature = (acquisition, structural, solutal, x, y)
        _require(background_groups.setdefault(track, signature) == signature,
                 "background track location/acquisition changed")
        background_rows.append(row)
    capacity = Counter(signature[0] for signature in background_groups.values())
    if any(capacity[a] < sum(QUOTAS[a]) for a in ACQUISITIONS):
        return {"status": "BLOCKED_BACKGROUND_GROUP_CAPACITY", "groups": [], "samples": [],
                "selected_background_tracks": [], "unused_background_tracks": sorted(background_groups),
                "cv_fold_by_group": {}, "counts": {"positive_groups_by_acquisition": dict(positive_counts),
                    "background_tracks_available_by_acquisition": dict(capacity)},
                "scientific_fits_authorized": False}
    selected = set()
    for acquisition in ACQUISITIONS:
        tracks = [gid for gid, signature in background_groups.items() if signature[0] == acquisition]
        tracks.sort(key=lambda gid: (_rank("STUDY2C_BACKGROUND_SELECTION_V1", acquisition, gid), gid))
        selected.update(tracks[:sum(QUOTAS[acquisition])])
    groups, group_by_id, folds = [], {}, {}
    for acquisition in ACQUISITIONS:
        for label, class_name in ((1, "POSITIVE"), (0, "BACKGROUND")):
            candidates = ([gid for gid, group in positive_groups.items() if group["signature"][0] == acquisition]
                          if label else [gid for gid in selected if background_groups[gid][0] == acquisition])
            candidates.sort(key=lambda gid: (_rank("STUDY2C_SPLIT_V1", acquisition, class_name, gid), gid))
            start = 0
            for split, count in zip(SPLITS, QUOTAS[acquisition]):
                for gid in candidates[start:start + count]:
                    _require(gid not in group_by_id, "positive/background group identity collision")
                    group = {"group_id": gid, "label": label, "acquisition_id": acquisition, "split": split,
                             "kind": "positive" if label else "background"}
                    group_by_id[gid] = group
                    groups.append(group)
                start += count
            train = [gid for gid in candidates if group_by_id[gid]["split"] == "TRAIN"]
            train.sort(key=lambda gid: (_rank("STUDY2C_CV_V1", acquisition, class_name, gid), gid))
            for rank, gid in enumerate(train):
                folds[gid] = rank % 4
                group_by_id[gid]["cv_fold"] = rank % 4
    samples = positive_rows
    for row in background_rows:
        track = row["background_track_id"]
        if track not in selected:
            continue
        sample = _sample_location(row)
        sample.update({"sample_id": f"background|{track}|{row['frame_index']}", "group_id": track,
                       "label": 0, "tier": "BACKGROUND", "kind": "background",
                       "background_track_id": track, "background_pool_hash_rank": row["hash_rank"],
                       "study2b_provenance": {"artifact": BACKGROUND_PATH, "background_track_id": track,
                                                "frame_index": row["frame_index"]},
                       "pixels_materialized": False})
        for name in ("safety_xyxy", "exclusion_status", "minimum_exclusion_envelope_distance_px",
                     "site_exclusion_count", "frame_component_exclusion_count", "structural_support", "solutal_support"):
            if name in row:
                sample[name] = list(row[name]) if name == "safety_xyxy" else row[name]
        if "method_freeze_sha" in row:
            sample["study2b_method_freeze_sha"] = row["method_freeze_sha"]
        samples.append(sample)
    for sample in samples:
        group = group_by_id[sample["group_id"]]
        sample["split"] = group["split"]
        if group["split"] == "TRAIN":
            sample["cv_fold"] = group["cv_fold"]
    groups.sort(key=lambda row: row["group_id"])
    split_order = {name: i for i, name in enumerate(SPLITS)}
    samples.sort(key=lambda row: (split_order[row["split"]], row["acquisition_id"], row["label"],
                                  row["group_id"], row["frame_index"], row["sample_id"]))
    _require(len({row["sample_id"] for row in samples}) == len(samples), "duplicate design sample ID")
    _require(len(folds) == 64 and len(groups) == 104 and len(selected) == 52, "group budget divergence")
    counts = {"positive_groups_by_acquisition": dict(positive_counts),
              "background_tracks_available_by_acquisition": dict(capacity),
              "selected_background_tracks": len(selected), "valid_support_sites": len(positive_groups),
              "unused_background_tracks": len(background_groups) - len(selected),
              "input_corpus_records": len(index_records), "input_background_records": len(background_records),
              "excluded_corpus_rows": dict(sorted(excluded.items())), "splits": {}}
    for split in SPLITS:
        sg = [g for g in groups if g["split"] == split]
        sr = [r for r in samples if r["split"] == split]
        counts["splits"][split] = {"positive_groups": sum(g["label"] == 1 for g in sg),
            "background_groups": sum(g["label"] == 0 for g in sg), "sample_count": len(sr),
            "tier_counts": dict(sorted(Counter(r["tier"] for r in sr).items())),
            "by_acquisition": {a: {"positive_groups": sum(g["acquisition_id"] == a and g["label"] == 1 for g in sg),
                                   "background_groups": sum(g["acquisition_id"] == a and g["label"] == 0 for g in sg)}
                               for a in ACQUISITIONS}}
    return {"status": "PASS", "schema_version": 1, "groups": groups, "samples": samples,
            "selected_background_tracks": sorted(selected),
            "unused_background_tracks": sorted(set(background_groups) - selected),
            "counts": counts, "cv_fold_by_group": dict(sorted(folds.items())),
            "hashes": {"group_split_sha256": _json_sha(groups),
                       "selected_background_tracks_sha256": _json_sha(sorted(selected)),
                       "sample_manifest_sha256": _json_sha(samples), "cv_fold_by_group_sha256": _json_sha(folds)},
            "TEST_STATE": "LOGICALLY_SEALED_TEST", "TEST_CLAIM": "GROUP_HELD_OUT_INTERNAL_TEST",
            "VALID_SUPPORT_SITE_DOMAIN_ONLY": True, "AUGMENTATION_USED": False,
            "HUMAN_REVIEW_USED": False, "EXTERNAL_GENERALIZATION_CLAIM": False,
            "scientific_fits_authorized": False}


def _group_rows(rows):
    _require(type(rows) is list and rows, "nonempty explicit rows required")
    groups = {}
    for i, row in enumerate(rows):
        _require(type(row) is dict and type(row.get("group_id")) is str and row["group_id"],
                 "group identity required")
        label = row.get("label")
        _require(type(label) is int and label in (0, 1), "binary integer label required")
        gid = row["group_id"]
        signature = (label, row.get("acquisition_id"), row.get("split"))
        group = groups.setdefault(gid, {"signature": signature, "indices": []})
        _require(group["signature"] == signature, "group crosses label/acquisition/split")
        group["indices"].append(i)
    return groups


def group_equal_weights(rows):
    """Give each represented group total weight one; never fit or access pixels.

    Class totals equal the respective numbers of groups. The frozen design/CV
    supplies balanced group counts; this arithmetic helper has no hardcoded N.
    """
    groups = _group_rows(rows)
    return [1.0 / len(groups[row["group_id"]]["indices"]) for row in rows]


def _metrics(rows, predictions):
    groups = _group_rows(rows)
    labels = [row["label"] for row in rows]
    counts = Counter((truth, pred) for truth, pred in zip(labels, predictions))
    tn, fp, fn, tp = (counts[key] for key in ((0, 0), (0, 1), (1, 0), (1, 1)))
    n0, n1 = tn + fp, tp + fn
    accuracy = (tp + tn) / len(rows)
    recall = tp / n1 if n1 else None
    specificity = tn / n0 if n0 else None
    precision = tp / (tp + fp) if tp + fp else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    details, scores, majorities = [], {0: [], 1: []}, {0: [], 1: []}
    for gid in sorted(groups):
        group = groups[gid]; label, acquisition, split = group["signature"]
        predicted = [predictions[i] for i in group["indices"]]
        correct = sum(p == label for p in predicted)
        score = correct / len(predicted)
        majority = int(sum(predicted) > len(predicted) / 2)
        scores[label].append(score); majorities[label].append(int(majority == label))
        details.append({"group_id": gid, "label": label, "acquisition_id": acquisition,
                        "split": split, "observation_count": len(predicted), "correct_count": correct,
                        "positive_predictions": sum(predicted), "correct_fraction": score,
                        "site_recall": score if label else None,
                        "track_specificity": score if not label else None,
                        "majority_vote_prediction": majority})
    mean = lambda values: math.fsum(values) / len(values) if values else None
    positive, negative = mean(scores[1]), mean(scores[0])
    gmba = (positive + negative) / 2 if positive is not None and negative is not None else None
    mv_positive, mv_negative = mean(majorities[1]), mean(majorities[0])
    majority_ba = (mv_positive + mv_negative) / 2 if mv_positive is not None and mv_negative is not None else None
    return {"primary_gmba": gmba, "primary": gmba, "gmba": gmba,
            "positive_group_macro_recall": positive, "negative_group_macro_specificity": negative,
            "majority_vote_group_balanced_accuracy": majority_ba,
            "majority_vote_tie_rule": "PREDICT_CLASS_0",
            "observation": {"balanced_accuracy": (recall + specificity) / 2 if n0 and n1 else None,
                "accuracy": accuracy, "precision": precision, "recall": recall, "specificity": specificity,
                "f1": f1, "confusion_matrix": [[tn, fp], [fn, tp]],
                "tn": tn, "fp": fp, "fn": fn, "tp": tp, "class_order": [0, 1]},
            "group_details": details, "counts": {"observations": len(rows), "positive_groups": len(scores[1]),
                "background_groups": len(scores[0]), "positive_observations": n1, "background_observations": n0}}


def metric_bundle(rows, predictions, *, allow_training_silver=False):
    """Measure the frozen primary and secondary metrics from labels/predictions.

    SILVER is denied by default. The explicit flag permits resubstitution of
    fitted TRAIN or TRAIN+DEVELOPMENT SILVER, never SILVER TEST evaluation.
    Per-acquisition metrics with a missing class are null, not invented scores.
    """
    _require(type(allow_training_silver) is bool, "explicit boolean SILVER permission required")
    groups = _group_rows(rows)
    _require({g["signature"][0] for g in groups.values()} == {0, 1}, "both label classes required for primary metric")
    try:
        predicted = list(predictions)
    except TypeError as exc:
        raise DesignContractError("prediction sequence required") from exc
    _require(len(predicted) == len(rows), "prediction count differs from rows")
    _require(all(isinstance(p, Integral) and not isinstance(p, bool) and p in (0, 1) for p in predicted),
             "predictions must be binary integers")
    predicted = [int(p) for p in predicted]
    for row in rows:
        tier, split = row.get("tier"), row.get("split")
        _require(split in SPLITS and type(row.get("acquisition_id")) is str and row["acquisition_id"],
                 "explicit split and acquisition required")
        _require(tier in {"GOLD", "SILVER", "BACKGROUND"}, "unlabeled/unknown tier is not an evaluation target")
        _require(row["label"] == int(tier != "BACKGROUND"), "tier/label divergence")
        if tier == "SILVER":
            _require(allow_training_silver and split in {"TRAIN", "DEVELOPMENT"},
                     "SILVER requires explicit training resubstitution and cannot be TEST target")
    output = _metrics(rows, predicted)
    output["per_acquisition"] = {}
    for acquisition in sorted({row["acquisition_id"] for row in rows}):
        selected = [i for i, row in enumerate(rows) if row["acquisition_id"] == acquisition]
        output["per_acquisition"][acquisition] = _metrics([rows[i] for i in selected], [predicted[i] for i in selected])
    output["metric_semantics"] = "GOLD_AND_BACKGROUND_EVALUATION" if not any(r["tier"] == "SILVER" for r in rows) else "EXPLICIT_TRAINING_RESUBSTITUTION_WITH_SILVER"
    return output
