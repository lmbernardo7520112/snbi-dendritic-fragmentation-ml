"""Metrics of invented predictions, with no learned model or source access."""

import math
import unittest

from snbi_fragmentation import study3_metrics as core


class Study3MetricTests(unittest.TestCase):
    def test_gmba_uses_one_vote_per_group_and_binary_confusion(self):
        result = core.group_metrics([0, 0, 0, 1], [0, 0, 1, 1], group_ids=["a", "b", "c", "d"])
        self.assertEqual(result["confusion_matrix"], [[2, 1], [0, 1]])
        self.assertAlmostEqual(result["primary_gmba"], (2 / 3 + 1) / 2)
        self.assertEqual(result["accuracy"], 0.75)
        self.assertEqual(result["precision"], 0.5)
        self.assertEqual(result["recall"], 1)
        self.assertAlmostEqual(result["f1"], 2 / 3)

    def test_zero_positive_predictions_have_defined_precision_f1(self):
        result = core.group_metrics([0, 1], [0, 0])
        self.assertEqual((result["precision"], result["f1"], result["primary_gmba"]), (0, 0, 0.5))

    def test_per_acquisition_missing_class_is_null_not_invented_gmba(self):
        a, b = core.ACQUISITIONS
        result = core.group_metrics([0, 0, 1, 1], [0, 1, 1, 0], [a, a, b, b])
        self.assertIsNone(result["per_acquisition"][a]["primary_gmba"])
        self.assertIsNone(result["per_acquisition"][b]["specificity"])

    def test_invalid_class_missing_class_duplicates_and_count_rejected(self):
        for labels, predictions in (([0], [0]), ([0, 1], [0]), ([False, 1], [0, 1]), ([0, 1], [0, 2])):
            with self.assertRaises(ValueError):
                core.group_metrics(labels, predictions)
        with self.assertRaises(ValueError):
            core.group_metrics([0, 1], [0, 1], group_ids=["same", "same"])

    def test_positive_mixed_nonpositive_descriptors_are_fixed(self):
        for values, expected in (([0.1, 0.2, 0.3, -0.1], "CONSISTENT_POSITIVE_INTERNAL"),
                                 ([0.4, 0.1, -0.1, -0.1], "MIXED_POSITIVE_INTERNAL"),
                                 ([0, 0, 0, 0], "NON_POSITIVE_INTERNAL"),
                                 ([0.1, 0.1, 0.1, -0.4], "NON_POSITIVE_INTERNAL")):
            result = core.describe_delta(values)
            self.assertEqual(result["descriptor"], expected)
            self.assertFalse(result["significance_test"])
            self.assertEqual(sum(result[key] for key in
                             ("positive_fold_count", "zero_fold_count", "negative_fold_count")), 4)

    def test_paired_stats_population_std_and_conventional_median(self):
        result = core.describe_delta([-1, 0, 1, 2])
        self.assertEqual((result["mean"], result["median"], result["min"], result["max"]), (0.5, 0.5, -1, 2))
        self.assertAlmostEqual(result["std"], math.sqrt(1.25))
        self.assertEqual(result["std_ddof"], 0)

    def test_all_seven_contrasts_use_paired_fold_gmba(self):
        scores = {name: [0.5] * 4 for name in {n for pair in core.CONTRASTS.values() for n in pair}}
        scores["TRAJECTORY_MEDIAN_LBP20"] = [0.6, 0.7, 0.8, 0.4]
        scores["SPATIOTEMPORAL_CNN_SMALL"] = [0.7, 0.7, 0.7, 0.7]
        result = core.summarize_contrasts(scores)
        self.assertEqual(set(result), set(core.CONTRASTS))
        self.assertEqual(result["MEDIAN_MINUS_D1"]["descriptor"], "CONSISTENT_POSITIVE_INTERNAL")
        self.assertEqual(result["SPATIOTEMPORAL_MINUS_MEDIAN"]["paired_fold_deltas"],
                         [scores["SPATIOTEMPORAL_CNN_SMALL"][f] - scores["TRAJECTORY_MEDIAN_LBP20"][f]
                          for f in range(4)])
        self.assertFalse(result["MEAN_MINUS_D1"]["primary"])

    def test_contrast_contract_rejects_missing_fold_new_family_and_nan(self):
        for mutate in (lambda s: s.update(D1_LBP20=[0.5] * 3),
                       lambda s: s.update(RF_TUNED=[0.5] * 4),
                       lambda s: s.update(D1_LBP20=[float("nan")] * 4),
                       lambda s: s.pop("D1_LBP20")):
            scores = {name: [0.5] * 4 for name in {n for pair in core.CONTRASTS.values() for n in pair}}
            mutate(scores)
            with self.assertRaises(ValueError):
                core.summarize_contrasts(scores)


if __name__ == "__main__":
    unittest.main()
