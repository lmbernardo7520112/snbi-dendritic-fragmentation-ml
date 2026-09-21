"""Synthetic metadata only: bounded TRAIN design, reuse and descriptive contrasts."""

from collections import Counter
from copy import deepcopy
import hashlib
import inspect
import json
import math
import unittest
from unittest import mock

from snbi_fragmentation import study2d_design as core


def synthetic_c_split():
    """Full-count synthetic metadata; no filesystem or experimental input."""
    rows, groups, folds = [], [], {}
    class_group_index = {0: 0, 1: 0}
    for acquisition, count in zip(core.ACQUISITIONS, (24, 8)):
        for label in (0, 1):
            for index in range(count):
                gid = f"synthetic-{acquisition}-{label}-{index:02d}"
                fold = index % 4; folds[gid] = fold
                groups.append({"group_id": gid, "acquisition_id": acquisition,
                               "label": label, "split": "TRAIN", "cv_fold": fold})
                position = class_group_index[label]; class_group_index[label] += 1
                n = 120 + int(position < 18) if label else 220 + int(position < 9)
                for frame in range(n):
                    rows.append({"sample_id": f"{gid}-frame-{frame:03d}", "group_id": gid,
                                 "acquisition_id": acquisition, "frame_index": frame,
                                 "label": label, "tier": "GOLD" if label else "BACKGROUND",
                                 "split": "TRAIN", "cv_fold": fold})
    return {"status": "PASS", "samples": rows, "groups": groups, "cv_fold_by_group": folds,
            "hashes": {"cv_fold_by_group_sha256": core.json_sha(folds)}}


def synthetic_design():
    """Only tests replace the historical hash constant for their synthetic groups.

    Callers validating the returned object must use the same explicit mock of
    EXPECTED_FOLD_SHA. Production has no optional hash override or relaxed mode.
    """
    source = synthetic_c_split()
    with mock.patch.object(core, "EXPECTED_FOLD_SHA", source["hashes"]["cv_fold_by_group_sha256"]):
        return core.build_attribution_design(source)


def simple_group(n):
    return [{"sample_id": f"s{i}", "group_id": "g", "acquisition_id": core.ACQUISITIONS[0],
             "frame_index": i * 7, "label": 1, "tier": "GOLD", "split": "TRAIN"}
            for i in range(n)]


def synthetic_results(design, score=None):
    """Recorded-value fixtures only; no model, scorer or feature extraction."""
    results = {}
    for spec in design["fits"]:
        value = score(spec) if score else (0.5 + spec["K"] / 100 if spec["part"] == "A"
                                           else {"D3": 0.76, "D5": 0.78, "DALL": 0.8}[spec["density"]]
                                           if spec["part"] == "B" else 0.7)
        metrics = {"primary_gmba": value, "positive_group_macro_recall": value,
                   "negative_group_macro_specificity": value,
                   "observation": {k: value for k in ("balanced_accuracy", "accuracy", "precision", "recall", "f1")},
                   "per_acquisition": {a: {"primary_gmba": value} for a in core.ACQUISITIONS}}
        results[spec["fit_id"]] = {"fit_id": spec["fit_id"], "spec": deepcopy(spec),
                                    "fit": {"fit_calls": 1}, "metrics": metrics,
                                    "predictions": {"sample_ids": spec["validation_sample_ids"]}}
    return results


def resign(design):
    design["design_sha256"] = core.json_sha({k: v for k, v in design.items() if k != "design_sha256"})
    return design


class TemporalSamplingTests(unittest.TestCase):
    def test_lower_median_odd_even_and_order_independence(self):
        for n, index in ((1, 0), (2, 0), (5, 2), (6, 2)):
            self.assertEqual(core.temporal_sample_ids(list(reversed(simple_group(n))), "D1"), [f"s{index}"])

    def test_quantile_half_ties_choose_lower_with_no_duplicate_rows(self):
        self.assertEqual(core.temporal_sample_ids(simple_group(3), "D3"), ["s0", "s1"])
        self.assertEqual(core.temporal_sample_ids(simple_group(4), "D3"), ["s1", "s2"])
        self.assertEqual(core.temporal_sample_ids(simple_group(7), "D5"), ["s0", "s1", "s3", "s4", "s6"])

    def test_short_groups_use_all_available_without_padding(self):
        self.assertEqual(core.temporal_sample_ids(simple_group(2), "D3"), ["s0", "s1"])
        self.assertEqual(core.temporal_sample_ids(simple_group(4), "D5"), ["s0", "s1", "s2", "s3"])

    def test_densities_are_nested_and_endpoints_are_fixed(self):
        for n in range(1, 31):
            levels = {d: core.temporal_sample_ids(simple_group(n), d) for d in core.DENSITIES}
            self.assertLessEqual(set(levels["D1"]), set(levels["D3"]))
            self.assertLessEqual(set(levels["D3"]), set(levels["D5"]))
            self.assertLessEqual(set(levels["D5"]), set(levels["DALL"]))
            self.assertIn("s0", levels["D5"]); self.assertIn(f"s{n-1}", levels["D5"])

    def test_temporal_selector_rejects_crossing_duplicates_and_nontrain(self):
        for mutation in (lambda r: r[0].update(split="TEST"), lambda r: r[0].update(split="DEVELOPMENT"),
                         lambda r: r[0].update(tier="SILVER"), lambda r: r[0].update(label=True),
                         lambda r: r[0].update(group_id="other"), lambda r: r[0].update(frame_index=7),
                         lambda r: r[0].update(sample_id="s1")):
            rows = simple_group(2); mutation(rows)
            with self.assertRaises(core.AttributionDesignError):
                core.temporal_sample_ids(rows, "D1")


class FrozenAttributionDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = synthetic_c_split()
        cls.patch = mock.patch.object(core, "EXPECTED_FOLD_SHA", cls.source["hashes"]["cv_fold_by_group_sha256"])
        cls.patch.start()
        try:
            cls.design = core.build_attribution_design(cls.source)
        except Exception:
            cls.patch.stop(); raise
        cls.results = synthetic_results(cls.design)
        cls.summary = core.summarize_attribution(cls.design, cls.results)

    @classmethod
    def tearDownClass(cls):
        cls.patch.stop()

    def test_exact_train_rows_groups_folds_and_json_contract(self):
        d = self.design
        self.assertEqual(Counter(r["tier"] for r in d["rows"]), {"GOLD": 3858, "BACKGROUND": 7049})
        self.assertEqual(len({r["group_id"] for r in d["rows"]}), 64)
        self.assertEqual(d["cv_fold_by_group"], self.source["cv_fold_by_group"])
        self.assertEqual(core.validate_attribution_design(d)["allowed_rows"], 10907)
        json.dumps(d, allow_nan=False)

    def test_only_original_train_gold_and_background_enter_despite_other_metadata(self):
        source = deepcopy(self.source)
        for split, tier in (("DEVELOPMENT", "GOLD"), ("TEST", "BACKGROUND"), ("TRAIN", "SILVER")):
            source["samples"].append(dict(source["samples"][0], sample_id=f"excluded-{split}-{tier}",
                                           split=split, tier=tier))
        d = core.build_attribution_design(source)
        self.assertEqual(d, self.design)

    def test_hash_count_and_group_identity_fail_closed(self):
        for mutation in (lambda d: d["hashes"].update(cv_fold_by_group_sha256="0" * 64),
                         lambda d: d["samples"].pop(),
                         lambda d: d["groups"].pop(),
                         lambda d: d["groups"][0].update(label=1),
                         lambda d: d["samples"][0].update(cv_fold=3)):
            source = deepcopy(self.source); mutation(source)
            with self.assertRaises(core.AttributionDesignError):
                core.build_attribution_design(source)

    def test_exact_fit_budget_and_reuse_are_separate(self):
        d = self.design
        self.assertEqual(Counter(s["part"] for s in d["fits"]), {"A": 84, "B": 12, "C": 4})
        self.assertEqual(len(d["fits"]), 100); self.assertEqual(len(d["reuse_refs"]), 8)
        self.assertFalse(any(r["fit_required"] for r in d["reuse_refs"]))
        self.assertEqual(d["fit_budget"]["conceptual_conditions"], 108)
        self.assertEqual([s["fit_id"] for s in d["fits"]][20:22], ["A-f0-K24-all", "A-f1-K4-r1"])

    def test_group_quotas_and_validation_never_change_within_fold(self):
        rows = {r["sample_id"]: r for r in self.design["rows"]}
        folds = self.design["cv_fold_by_group"]
        for spec in self.design["fits"]:
            training_groups = {rows[s]["group_id"] for s in spec["train_sample_ids"]}
            validation_groups = {rows[s]["group_id"] for s in spec["validation_sample_ids"]}
            self.assertEqual(len(validation_groups), 16)
            self.assertFalse(training_groups & validation_groups)
            self.assertTrue(all(folds[g] == spec["fold"] for g in validation_groups))
            signatures = {rows[s]["group_id"]: (rows[s]["acquisition_id"], rows[s]["label"])
                          for s in spec["train_sample_ids"]}
            expected = {(a, y): n for a, n in zip(core.ACQUISITIONS, core.K_QUOTAS[spec["K"]]) for y in (0, 1)}
            self.assertEqual(Counter(signatures.values()), expected)
            self.assertEqual(spec["validation_sample_ids"], self.design["validation_sample_ids_by_fold"][str(spec["fold"])])

    def test_replicate_salts_hash_formula_and_nested_subsets(self):
        fits = {s["fit_id"]: s for s in self.design["fits"]}
        for fold in range(4):
            for rep, salt in enumerate(core.SALTS, 1):
                previous = set()
                for k in (4, 8, 12, 17):
                    current = set(fits[f"A-f{fold}-K{k}-r{rep}"]["training_group_ids"])
                    self.assertLess(previous, current); previous = current
                self.assertLess(previous, set(fits[f"A-f{fold}-K24-all"]["training_group_ids"]))
                rank = self.design["group_rankings"][str(fold)][str(rep)][core.ACQUISITIONS[0]]["1"]
                expected = sorted(rank, key=lambda g: (hashlib.sha256(
                    f"{salt}|{fold}|POSITIVE|{core.ACQUISITIONS[0]}|{g}".encode()).hexdigest(), g))
                self.assertEqual(rank, expected)

    def test_part_a_exactly_one_row_per_selected_group(self):
        for spec in self.design["fits"][:84]:
            self.assertEqual(len(spec["train_sample_ids"]), 2 * spec["K"])
            self.assertEqual(set(spec["effective_rows_per_group"].values()), {1})

    def test_density_and_weighting_comparisons_have_identical_groups_and_full_rows(self):
        fits = {s["fit_id"]: s for s in self.design["fits"]}
        for fold in range(4):
            group = fits[f"A-f{fold}-K24-all"]["training_group_ids"]
            for density in ("D3", "D5", "DALL"):
                self.assertEqual(fits[f"B-f{fold}-{density}"]["training_group_ids"], group)
            self.assertEqual(fits[f"B-f{fold}-DALL"]["train_sample_ids"],
                             fits[f"C-f{fold}-OBSERVATION_EQUAL"]["train_sample_ids"])

    def test_validator_does_not_rebuild_or_read_science(self):
        with mock.patch.object(core, "build_attribution_design", side_effect=AssertionError("planner repeated")), \
                mock.patch.object(core, "_rank", side_effect=AssertionError("reranking")):
            self.assertEqual(core.validate_attribution_design(self.design)["status"], "PASS")
        source = inspect.getsource(core)
        for prohibited in ("import numpy", "import sklearn", "import torch", "subprocess", "open(", "read_bytes("):
            self.assertNotIn(prohibited, source)

    def test_tampered_hash_binding_order_and_reuse_refused(self):
        mutations = [lambda d: d["fits"].reverse(),
                     lambda d: d["fits"][0].update(fold=1),
                     lambda d: d["fits"][0].update(replicate=2),
                     lambda d: d["fits"][0].update(fit_required=False),
                     lambda d: d["reuse_refs"][0].update(source_fit_id="A-f1-K24-all"),
                     lambda d: d.update(SILVER_USED=True)]
        for mutation in mutations:
            d = deepcopy(self.design); mutation(d); resign(d)
            with self.assertRaises(core.AttributionDesignError):
                core.validate_attribution_design(d)

    def test_result_binding_and_exact_fit_count_required(self):
        bad = dict(self.results); bad.pop(next(iter(bad)))
        with self.assertRaises(core.AttributionDesignError):
            core.summarize_attribution(self.design, bad)
        bad = dict(self.results); key = next(iter(bad)); bad[key] = dict(bad[key], fit_id="wrong")
        with self.assertRaises(core.AttributionDesignError):
            core.summarize_attribution(self.design, bad)

    def test_summary_primary_contrasts_and_reused_pair_counts(self):
        s = self.summary
        self.assertEqual(s["part_a"]["levels"]["24"]["global"]["n_fits"], 4)
        self.assertEqual(s["part_a"]["levels"]["17"]["global"]["n_fits"], 20)
        c = s["part_a"]["contrasts"]["K24_MINUS_K17"]["global"]
        self.assertEqual(c["n_pairs"], 20); self.assertEqual(c["positive_delta_count"], 20)
        self.assertAlmostEqual(c["mean_paired_delta"], .07)
        self.assertEqual(s["part_a"]["descriptor"], "CONSISTENT_POSITIVE")
        self.assertEqual(s["part_b"]["descriptor"], "CONSISTENT_POSITIVE")
        self.assertEqual(s["part_c"]["descriptor"], "CONSISTENT_GROUP_EQUAL_BENEFIT")
        self.assertEqual(s["part_c"]["contrast"]["global"]["n_pairs"], 4)
        self.assertAlmostEqual(s["terminal_fields"]["GROUP_WEIGHTING_DELTA"], .1)
        self.assertEqual(len(s["narrative_bridge_table"]), 9)
        self.assertIn("K17/D1/GROUP_EQUAL", s["narrative_bridge_markdown"])

    def test_per_acquisition_statistics_secondary_metrics_and_descriptive_limits(self):
        s = self.summary
        self.assertEqual(set(s["part_b"]["levels"]["D5"]["per_acquisition"]), set(core.ACQUISITIONS))
        self.assertIn("observation_accuracy", s["part_a"]["levels"]["4"]["secondary_statistics"])
        self.assertFalse(s["attribution_summary"]["effects_are_additive"])
        self.assertFalse(s["attribution_summary"]["p_values_computed"])
        self.assertFalse(s["model_or_pipeline_selected"])

    def test_descriptors_apply_exact_preregistered_thresholds(self):
        def mixed(spec):
            if spec["part"] == "A":
                return .8 if spec["K"] == 24 else (.5 if spec["replicate"] <= 3 else .81)
            if spec["part"] == "B":
                return .9 if spec["fold"] < 2 else .79
            return .6 if spec["fold"] < 2 else .8
        summary = core.summarize_attribution(self.design, synthetic_results(self.design, mixed))
        self.assertEqual(summary["part_a"]["descriptor"], "MIXED_POSITIVE")
        self.assertEqual(summary["part_b"]["descriptor"], "MIXED_POSITIVE")
        self.assertEqual(summary["part_c"]["descriptor"], "MIXED_GROUP_EQUAL_BENEFIT")
        summary = core.summarize_attribution(self.design, synthetic_results(self.design, lambda s: .5))
        self.assertEqual(summary["part_a"]["descriptor"], "NON_POSITIVE")
        self.assertEqual(summary["part_b"]["descriptor"], "NON_POSITIVE")
        self.assertEqual(summary["part_c"]["descriptor"], "NO_GROUP_EQUAL_BENEFIT")

    def test_descriptive_standard_deviation_ddof_zero_and_summary_median(self):
        result = core._stats([.1, .3])
        self.assertAlmostEqual(result["mean"], .2); self.assertAlmostEqual(result["median"], .2)
        self.assertAlmostEqual(result["standard_deviation"], .1)
        self.assertEqual(result["std_ddof"], 0)
        with self.assertRaises(core.AttributionDesignError):
            core._stats([math.nan])


if __name__ == "__main__":
    unittest.main()
