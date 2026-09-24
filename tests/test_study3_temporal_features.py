"""Invented features only; the dedicated scientific profile requires NumPy."""

import unittest

try:
    import numpy as np
except ImportError:
    np = None

from snbi_fragmentation import study3_temporal_features as core
from test_study3_domain import rows_for_group


def invented_features(rows):
    return {row["sample_id"]: np.arange(20, dtype=np.float64) + row["frame_index"] * 10
            for row in rows}


@unittest.skipUnless(np is not None, "NumPy required by the dedicated Study3 scientific synthetic profile")
class Study3TemporalFeatureTests(unittest.TestCase):
    def test_d1_lower_temporal_median_odd_even_single(self):
        for n, expected in ((1, 0), (2, 0), (5, 2), (6, 2)):
            self.assertEqual(core.select_d1(rows_for_group(n)[::-1]).frame_index, expected)

    def test_mean_and_median_summarize_all_real_rows(self):
        rows = rows_for_group(4)
        features = invented_features(rows)
        features[rows[-1]["sample_id"]] += 100
        result = core.summarize_lbp20(rows[::-1], features)
        np.testing.assert_array_equal(result["D1_LBP20"], np.arange(20) + 10)
        np.testing.assert_array_equal(result["TRAJECTORY_MEAN_LBP20"], np.arange(20) + 40)
        np.testing.assert_array_equal(result["TRAJECTORY_MEDIAN_LBP20"], np.arange(20) + 15)

    def test_q2575_linear_and_quantile_major_concatenation(self):
        rows = rows_for_group(4)
        result = core.summarize_lbp20(rows, invented_features(rows))["TRAJECTORY_Q2575_LBP60"]
        np.testing.assert_array_equal(result[:20], np.arange(20) + 7.5)
        np.testing.assert_array_equal(result[20:40], np.arange(20) + 15)
        np.testing.assert_array_equal(result[40:], np.arange(20) + 22.5)

    def test_t8_uses_real_rows_rank_targets_and_endpoints(self):
        rows = rows_for_group(10)
        result = core.select_t8(rows[::-1])
        self.assertEqual(result["selected_ranks"], [0, 1, 3, 4, 5, 6, 8, 9])
        self.assertEqual(result["selected_frame_indices"], result["selected_ranks"])
        self.assertEqual(result["rank_targets"], [k * 9 / 7 for k in range(8)])
        self.assertEqual(result["duplicate_flags"], [False] * 8)
        self.assertTrue(set(result["selected_sample_ids"]) <= {row["sample_id"] for row in rows})

    def test_exact_rational_half_tie_is_lower(self):
        # Denominator seven never yields a half tie. The shared integer rule is
        # tested directly to prevent a future floating-point rounding shortcut.
        self.assertEqual(core.nearest_rank_lower(1, 2), 0)
        self.assertEqual(core.nearest_rank_lower(3, 2), 1)
        self.assertEqual(core.nearest_rank_lower(5, 3), 2)

    def test_short_group_repeats_are_preserved_and_flagged(self):
        selection = core.select_t8(rows_for_group(2))
        self.assertEqual(selection["selected_ranks"], [0, 0, 0, 0, 1, 1, 1, 1])
        self.assertEqual(selection["duplicate_flags"], [False, True, True, True, False, True, True, True])
        single = core.select_t8(rows_for_group(1))
        self.assertEqual(single["selected_ranks"], [0] * 8)
        self.assertEqual(single["duplicate_flags"], [False] + [True] * 7)

    def test_builder_aligns_sorted_group_ids_classical_and_cnn_arrays(self):
        rows = rows_for_group(3, "z") + rows_for_group(2, "a", label=0)
        result = core.build_representations(rows[::-1], invented_features(rows))
        self.assertEqual(result["group_ids"], ["a", "z"])
        self.assertEqual(result["labels"].tolist(), [0, 1])
        self.assertEqual(result["temporal_lbp"].shape, (2, 20, 8))
        self.assertEqual(result["classical"]["TRAJECTORY_Q2575_LBP60"].shape, (2, 60))
        np.testing.assert_array_equal(result["temporal_lbp"][0, :, 0], np.arange(20))
        self.assertEqual(result["selections"], [core.select_t8(group) for group in result["groups"]])

    def test_permutation_determinism_and_no_feature_mutation(self):
        rows = rows_for_group(5)
        features = invented_features(rows)
        before = {sid: values.copy() for sid, values in features.items()}
        first = core.build_representations(rows, features)
        second = core.build_representations(rows[::-1], features)
        for name in first["classical"]:
            np.testing.assert_array_equal(first["classical"][name], second["classical"][name])
        np.testing.assert_array_equal(first["temporal_lbp"], second["temporal_lbp"])
        for sid in before:
            np.testing.assert_array_equal(before[sid], features[sid])

    def test_missing_extra_nonfinite_or_wrong_width_feature_denied(self):
        rows = rows_for_group(2)
        for mutate in (lambda f: f.pop(rows[0]["sample_id"]),
                       lambda f: f.update(extra=np.zeros(20)),
                       lambda f: f.update({rows[0]["sample_id"]: np.zeros(19)}),
                       lambda f: f.update({rows[0]["sample_id"]: np.full(20, np.nan)})):
            features = invented_features(rows)
            mutate(features)
            with self.assertRaises(ValueError):
                core.build_representations(rows, features)

    def test_nontrain_denied_before_feature_lookup(self):
        class Poison(dict):
            def __getitem__(self, key):
                raise AssertionError("feature lookup reached")
        for split in ("DEVELOPMENT", "TEST"):
            rows = rows_for_group(1)
            rows[0]["split"] = split
            with self.assertRaises(ValueError):
                core.build_representations(rows, Poison())


if __name__ == "__main__":
    unittest.main()
