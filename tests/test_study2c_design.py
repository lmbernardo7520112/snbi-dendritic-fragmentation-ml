"""Synthetic, metadata-only tests of the frozen Study2-C design and metrics."""

from collections import Counter
import copy
import hashlib
import math
import unittest

from snbi_fragmentation.study2c_design import (
    ACQUISITIONS, DesignContractError, build_design, group_equal_weights,
    metric_bundle,
)


def _hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _fixtures():
    """Distinct synthetic identities/locations; no scientific source is used."""
    index, backgrounds = [], []
    row_index = 0
    for acquisition, nsites, nbackgrounds, structural, solutal, annotation in (
        (ACQUISITIONS[0], 40, 75, "ESM1", "ESM2", "ESM3"),
        (ACQUISITIONS[1], 12, 148, "ESM4", "ESM5", "ESM6"),
    ):
        for site in range(nsites):
            site_id = f"{annotation}:synthetic-site:{site:03d}"
            group_id = acquisition + "|" + site_id
            x, y = 100 + site, 200 + site
            for frame, state, tier in (
                (10, "DIRECT_VALID", "GOLD"),
                (11, "DIRECT_VALID", "GOLD"),
                (12, "TEMPORAL_SUPPORTED_AMBIGUOUS", "SILVER"),
                (13, "PRE_FIRST_CONFIDENT_ANNOTATION", "UNLABELED_PRE"),
                (14, "PERSISTENCE_EXPECTED_UNRESOLVED", "UNLABELED_PERSISTENCE"),
            ):
                identity = f"{group_id}|{frame}"
                index.append({
                    "site_id": site_id, "group_id": group_id, "pair_id": identity,
                    "acquisition_id": acquisition, "structural_source_id": structural,
                    "solutal_source_id": solutal, "frame_index": frame,
                    "center_x": x, "center_y": y,
                    "canonical_center_xy_px": [x - 0.5, y + 0.49],
                    "patch_xyxy": [x - 32, y - 32, x + 33, y + 33],
                    "pair_status": "VALID_PAIR", "observation_state": state,
                    "supervision_tier": tier, "row_index": row_index,
                    "structural_patch_sha256": _hash("structural|" + identity),
                    "solutal_patch_sha256": _hash("solutal|" + identity),
                    "pair_sha256": _hash("pair|" + identity),
                    "structural_source_sha256": _hash(structural),
                    "solutal_source_sha256": _hash(solutal),
                    "structural_frame_sha256": _hash(structural + str(frame)),
                    "solutal_frame_sha256": _hash(solutal + str(frame)),
                    "method_freeze_sha": "0" * 40,
                    "annotation_provenance": {"large_unused": [1, 2, 3]},
                })
                row_index += 1
            index.append({"site_id": site_id, "frame_index": 15,
                          "pair_status": "INVALID_BOTH"})
        for i in range(nbackgrounds):
            x, y = 32 + 65 * (i % 19), 162 + 65 * (i // 19)
            track = f"{acquisition}|{x}|{y}"
            for frame in (10, 11):
                backgrounds.append({
                    "acquisition_id": acquisition, "structural_source_id": structural,
                    "solutal_source_id": solutal, "frame_index": frame,
                    "center_x": x, "center_y": y,
                    "patch_xyxy": [x - 32, y - 32, x + 33, y + 33],
                    "background_track_id": track,
                    "hash_rank": _hash(f"STUDY2B_BACKGROUND_V1|{track}|{frame}"),
                    "status": "BACKGROUND_CANDIDATE",
                    "exclusion_status": "ALL_EXCLUSIONS_PASSED",
                    "pixels_materialized": False, "physical_absence_inferred": False,
                    "method_freeze_sha": "0" * 40,
                    "structural_support": "PASS", "solutal_support": "PASS",
                })
    return index, backgrounds


def _metric_rows(group, label, count, *, acquisition="synthetic_acquisition",
                 split="DEVELOPMENT", tier=None):
    return [{"group_id": group, "label": label, "acquisition_id": acquisition,
             "split": split, "tier": tier or ("GOLD" if label else "BACKGROUND")}
            for _ in range(count)]


class Study2CDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index, cls.backgrounds = _fixtures()
        cls.design = build_design(cls.index, cls.backgrounds)

    def test_exact_group_budgets_and_acquisition_strata(self):
        self.assertEqual(self.design["status"], "PASS")
        self.assertEqual(len(self.design["groups"]), 104)
        for split, bottom, top in (("TRAIN", 24, 8), ("DEVELOPMENT", 8, 2), ("TEST", 8, 2)):
            for label in (0, 1):
                counts = Counter(g["acquisition_id"] for g in self.design["groups"]
                                 if g["split"] == split and g["label"] == label)
                self.assertEqual(counts, {ACQUISITIONS[0]: bottom, ACQUISITIONS[1]: top})

    def test_design_is_input_order_independent_and_does_not_mutate(self):
        before = copy.deepcopy((self.index, self.backgrounds))
        reordered = build_design(list(reversed(self.index)), list(reversed(self.backgrounds)))
        self.assertEqual(self.design, reordered)
        self.assertEqual(before, (self.index, self.backgrounds))

    def test_background_ranking_is_exact_and_reserve_disjoint(self):
        expected = set()
        for acq, quota in zip(ACQUISITIONS, (40, 12)):
            tracks = {r["background_track_id"] for r in self.backgrounds if r["acquisition_id"] == acq}
            ordered = sorted(tracks, key=lambda t: (_hash(f"STUDY2C_BACKGROUND_SELECTION_V1|{acq}|{t}"), t))
            expected.update(ordered[:quota])
        self.assertEqual(expected, set(self.design["selected_background_tracks"]))
        reserve = set(self.design["unused_background_tracks"])
        self.assertFalse(expected & reserve)
        self.assertEqual(len(reserve), 171)
        self.assertEqual(len(expected | reserve), 223)

    def test_split_ranking_uses_exact_prefix_class_and_quotas(self):
        for acq, quotas in zip(ACQUISITIONS, ((24, 8, 8), (8, 2, 2))):
            for label, cls in ((1, "POSITIVE"), (0, "BACKGROUND")):
                groups = [g for g in self.design["groups"] if g["acquisition_id"] == acq and g["label"] == label]
                groups.sort(key=lambda g: (_hash(f"STUDY2C_SPLIT_V1|{acq}|{cls}|{g['group_id']}"), g["group_id"]))
                self.assertEqual([g["split"] for g in groups],
                                 [s for s, count in zip(("TRAIN", "DEVELOPMENT", "TEST"), quotas) for _ in range(count)])

    def test_background_frame_count_cannot_change_selected_tracks(self):
        shorter = [r for r in self.backgrounds if r["frame_index"] == 10]
        result = build_design(self.index, shorter)
        self.assertEqual(result["selected_background_tracks"], self.design["selected_background_tracks"])
        self.assertEqual(result["groups"], self.design["groups"])

    def test_all_selected_background_candidates_remain(self):
        rows = [r for r in self.design["samples"] if r["kind"] == "background"]
        self.assertEqual(len(rows), 104)
        self.assertEqual(set(Counter(r["group_id"] for r in rows).values()), {2})
        self.assertTrue(all(r["tier"] == "BACKGROUND" and r["label"] == 0 for r in rows))

    def test_unlabeled_and_invalid_rows_excluded_silver_retained(self):
        self.assertEqual(Counter(r["tier"] for r in self.design["samples"]),
                         {"GOLD": 104, "SILVER": 52, "BACKGROUND": 104})
        self.assertEqual(self.design["counts"]["excluded_corpus_rows"],
                         {"UNLABELED_PRE": 52, "UNLABELED_PERSISTENCE": 52, "invalid_support_or_decode": 52})
        self.assertTrue(all(r["frame_index"] <= 12 for r in self.design["samples"]))

    def test_positive_original_rows_hashes_and_pointers_preserved(self):
        originals = {r.get("pair_id"): r for r in self.index}
        for row in self.design["samples"]:
            if row["kind"] != "positive":
                continue
            original = originals[row["positive_pair_id"]]
            self.assertEqual(row["positive_row_index"], original["row_index"])
            self.assertEqual(row["study2b_provenance"]["original_row_index"], original["row_index"])
            self.assertNotIn("annotation_provenance", row)
            for key in ("pair_sha256", "structural_patch_sha256", "solutal_patch_sha256", "patch_xyxy"):
                self.assertEqual(row[key], original[key])

    def test_no_group_crosses_splits_and_sample_ids_are_unique(self):
        memberships = {}
        for row in self.design["samples"]:
            old = memberships.setdefault(row["group_id"], row["split"])
            self.assertEqual(old, row["split"])
        self.assertEqual(len(memberships), 104)
        self.assertEqual(len({r["sample_id"] for r in self.design["samples"]}), len(self.design["samples"]))

    def test_cv_train_only_four_balanced_strata_and_exact_ranking(self):
        folds = self.design["cv_fold_by_group"]
        self.assertEqual(len(folds), 64)
        for acq, expected in zip(ACQUISITIONS, (6, 2)):
            for label, cls in ((1, "POSITIVE"), (0, "BACKGROUND")):
                rows = [g for g in self.design["groups"] if g["split"] == "TRAIN"
                        and g["acquisition_id"] == acq and g["label"] == label]
                rows.sort(key=lambda g: (_hash(f"STUDY2C_CV_V1|{acq}|{cls}|{g['group_id']}"), g["group_id"]))
                self.assertEqual(Counter(folds[g["group_id"]] for g in rows), {i: expected for i in range(4)})
                self.assertEqual([folds[g["group_id"]] for g in rows], [i % 4 for i in range(len(rows))])
        self.assertTrue(all((g["group_id"] in folds) == (g["split"] == "TRAIN") for g in self.design["groups"]))
        self.assertTrue(all(("cv_fold" in r) == (r["split"] == "TRAIN") for r in self.design["samples"]))

    def test_test_memberships_are_logically_sealed_from_training_selection(self):
        rows = self.design["samples"]
        train = [r for r in rows if r["split"] == "TRAIN" and r["tier"] in {"GOLD", "BACKGROUND"}]
        for fold in range(4):
            fit = [r for r in train if r["cv_fold"] != fold]
            validation = [r for r in train if r["cv_fold"] == fold]
            self.assertFalse({r["group_id"] for r in fit} & {r["group_id"] for r in validation})
            self.assertEqual(len({r["group_id"] for r in fit}), 48)
            self.assertEqual(len({r["group_id"] for r in validation}), 16)
            self.assertFalse(any(r["split"] == "TEST" for r in fit + validation))
        self.assertEqual(self.design["TEST_STATE"], "LOGICALLY_SEALED_TEST")
        self.assertEqual(self.design["TEST_CLAIM"], "GROUP_HELD_OUT_INTERNAL_TEST")
        self.assertFalse(self.design["scientific_fits_authorized"])

    def test_insufficient_background_capacity_blocks_without_reallocation(self):
        bottom = sorted({r["background_track_id"] for r in self.backgrounds if r["acquisition_id"] == ACQUISITIONS[0]})
        limited = [r for r in self.backgrounds if r["acquisition_id"] != ACQUISITIONS[0]
                   or r["background_track_id"] in bottom[:39]]
        result = build_design(self.index, limited)
        self.assertEqual(result["status"], "BLOCKED_BACKGROUND_GROUP_CAPACITY")
        self.assertEqual(result["samples"], [])
        self.assertEqual(result["groups"], [])
        self.assertFalse(result["scientific_fits_authorized"])

    def test_positive_quota_or_goldless_group_is_rejected(self):
        first = self.index[0]["site_id"]
        for modified in ([r for r in self.index if r["site_id"] != first],
                         [r for r in self.index if not (r["site_id"] == first and r.get("supervision_tier") == "GOLD")]):
            with self.subTest(rows=len(modified)), self.assertRaises(DesignContractError):
                build_design(modified, self.backgrounds)

    def test_duplicate_corpus_or_background_identity_rejected(self):
        with self.assertRaises(DesignContractError):
            build_design(self.index + [copy.deepcopy(self.index[0])], self.backgrounds)
        with self.assertRaises(DesignContractError):
            build_design(self.index, self.backgrounds + [copy.deepcopy(self.backgrounds[0])])

    def test_invalid_positive_hash_row_index_tier_or_geometry_rejected(self):
        changes = ({"pair_sha256": "bad"}, {"row_index": True},
                   {"observation_state": "TEMPORAL_SUPPORTED_AMBIGUOUS"},
                   {"center_x": self.index[0]["center_x"] + 1},
                   {"structural_source_id": "ESM4"}, {"frame_index": -1},
                   {"pair_status": "UNKNOWN"}, {"group_id": "different"})
        for change in changes:
            with self.subTest(change=change):
                rows = copy.deepcopy(self.index); rows[0].update(change)
                with self.assertRaises(DesignContractError):
                    build_design(rows, self.backgrounds)

    def test_rounded_half_up_canonical_center_and_constant_group_required(self):
        self.assertEqual(self.design["status"], "PASS")
        rows = copy.deepcopy(self.index)
        rows[0]["canonical_center_xy_px"][0] -= 0.01
        with self.assertRaises(DesignContractError):
            build_design(rows, self.backgrounds)
        rows = copy.deepcopy(self.index)
        rows[0]["canonical_center_xy_px"][0] += 0.1
        with self.assertRaises(DesignContractError):
            build_design(rows, self.backgrounds)

    def test_background_frozen_admissibility_cannot_be_weakened(self):
        for change in ({"pixels_materialized": True}, {"physical_absence_inferred": True},
                       {"exclusion_status": "UNCHECKED"}, {"hash_rank": "bad"},
                       {"status": "NEGATIVE"}, {"solutal_source_id": "ESM5"}):
            with self.subTest(change=change):
                rows = copy.deepcopy(self.backgrounds); rows[0].update(change)
                with self.assertRaises(DesignContractError):
                    build_design(self.index, rows)


class Study2CMetricTests(unittest.TestCase):
    def test_group_weights_sum_to_one_without_frame_count_advantage(self):
        rows = _metric_rows("p", 1, 3) + _metric_rows("n", 0, 7)
        weights = group_equal_weights(rows)
        self.assertAlmostEqual(math.fsum(weights[:3]), 1)
        self.assertAlmostEqual(math.fsum(weights[3:]), 1)
        self.assertEqual(weights[:3], [1 / 3] * 3)
        self.assertEqual(weights[3:], [1 / 7] * 7)

    def test_weights_support_cv_subsets_without_hardcoded_group_count(self):
        rows = sum((_metric_rows(f"g{i}", i % 2, i + 1) for i in range(6)), [])
        weights = group_equal_weights(rows)
        for label in (0, 1):
            self.assertAlmostEqual(math.fsum(w for r, w in zip(rows, weights) if r["label"] == label), 3)

    def test_group_cannot_cross_class_acquisition_or_split(self):
        for change in ({"label": 0}, {"acquisition_id": "other"}, {"split": "TEST"}):
            with self.subTest(change=change):
                rows = _metric_rows("p", 1, 2); rows[1].update(change)
                with self.assertRaises(DesignContractError):
                    group_equal_weights(rows)

    def test_primary_gmba_is_group_macro_not_observation_balanced_accuracy(self):
        rows = _metric_rows("p-long", 1, 9) + _metric_rows("p-short", 1, 1) + _metric_rows("n", 0, 4)
        result = metric_bundle(rows, [1] * 9 + [0] + [0] * 4)
        self.assertEqual(result["primary_gmba"], 0.75)
        self.assertEqual(result["positive_group_macro_recall"], 0.5)
        self.assertEqual(result["negative_group_macro_specificity"], 1)
        self.assertEqual(result["observation"]["balanced_accuracy"], 0.95)
        self.assertEqual(result["observation"]["confusion_matrix"], [[4, 0], [1, 9]])
        self.assertEqual(result["gmba"], result["primary_gmba"])

    def test_majority_vote_tie_predicts_zero(self):
        rows = _metric_rows("p", 1, 2) + _metric_rows("n", 0, 2)
        result = metric_bundle(rows, [0, 1, 0, 1])
        self.assertEqual(result["primary_gmba"], 0.5)
        self.assertEqual(result["majority_vote_group_balanced_accuracy"], 0.5)
        self.assertTrue(all(g["majority_vote_prediction"] == 0 for g in result["group_details"]))

    def test_observation_metrics_and_confusion_have_true_rows_predicted_columns(self):
        rows = _metric_rows("p", 1, 3) + _metric_rows("n", 0, 3)
        result = metric_bundle(rows, [1, 1, 0, 0, 0, 1])["observation"]
        self.assertEqual(result["confusion_matrix"], [[2, 1], [1, 2]])
        for key in ("balanced_accuracy", "accuracy", "precision", "recall", "f1"):
            self.assertAlmostEqual(result[key], 2 / 3)
        self.assertEqual(result["class_order"], [0, 1])

    def test_all_positive_predictions_have_expected_zero_specificity(self):
        rows = _metric_rows("p", 1, 4) + _metric_rows("n", 0, 4)
        result = metric_bundle(rows, [1] * 8)
        self.assertEqual(result["primary_gmba"], 0.5)
        self.assertEqual(result["observation"]["precision"], 0.5)
        self.assertEqual(result["observation"]["recall"], 1)
        self.assertEqual(result["observation"]["specificity"], 0)

    def test_per_acquisition_gmba_and_missing_class_are_explicit(self):
        rows = (_metric_rows("pA", 1, 2, acquisition="A") + _metric_rows("nA", 0, 2, acquisition="A")
                + _metric_rows("pB", 1, 2, acquisition="B"))
        result = metric_bundle(rows, [1, 1, 0, 0, 0, 0])
        self.assertEqual(result["primary_gmba"], 0.75)
        self.assertEqual(result["per_acquisition"]["A"]["primary_gmba"], 1)
        self.assertIsNone(result["per_acquisition"]["B"]["primary_gmba"])
        self.assertIsNone(result["per_acquisition"]["B"]["observation"]["balanced_accuracy"])

    def test_silver_denied_default_and_never_test_target(self):
        for split in ("TRAIN", "DEVELOPMENT", "TEST"):
            rows = _metric_rows("p", 1, 1, split=split, tier="SILVER") + _metric_rows("n", 0, 1, split=split)
            with self.subTest(split=split), self.assertRaises(DesignContractError):
                metric_bundle(rows, [1, 0])
            if split == "TEST":
                with self.assertRaises(DesignContractError):
                    metric_bundle(rows, [1, 0], allow_training_silver=True)
            else:
                result = metric_bundle(rows, [1, 0], allow_training_silver=True)
                self.assertEqual(result["primary_gmba"], 1)
                self.assertEqual(result["metric_semantics"], "EXPLICIT_TRAINING_RESUBSTITUTION_WITH_SILVER")

    def test_unlabeled_and_tier_label_mismatch_rejected(self):
        for tier in ("UNLABELED_PRE", "UNLABELED_PERSISTENCE", "BACKGROUND", "UNKNOWN"):
            rows = _metric_rows("p", 1, 1, tier=tier) + _metric_rows("n", 0, 1)
            with self.subTest(tier=tier), self.assertRaises(DesignContractError):
                metric_bundle(rows, [1, 0])

    def test_invalid_predictions_counts_and_truth_types_rejected(self):
        rows = _metric_rows("p", 1, 1) + _metric_rows("n", 0, 1)
        for predictions in (None, [1], [1, 0, 1], [True, 0], [1.0, 0], [2, 0], ["1", 0]):
            with self.subTest(predictions=predictions), self.assertRaises(DesignContractError):
                metric_bundle(rows, predictions)
        changed = copy.deepcopy(rows); changed[0]["label"] = True
        with self.assertRaises(DesignContractError):
            metric_bundle(changed, [1, 0])

    def test_empty_and_single_class_metrics_rejected(self):
        for rows, predictions in (([], []), (_metric_rows("p", 1, 1), [1])):
            with self.subTest(rows=rows), self.assertRaises(DesignContractError):
                metric_bundle(rows, predictions)
        with self.assertRaises(DesignContractError):
            group_equal_weights([])

    def test_metric_outputs_deterministic_and_inputs_unchanged(self):
        rows = _metric_rows("p", 1, 2) + _metric_rows("n", 0, 2)
        predictions = [1, 0, 0, 0]
        before = copy.deepcopy((rows, predictions))
        first = metric_bundle(rows, predictions)
        second = metric_bundle(list(reversed(rows)), list(reversed(predictions)))
        self.assertEqual(first, second)
        self.assertEqual(before, (rows, predictions))


if __name__ == "__main__":
    unittest.main()
