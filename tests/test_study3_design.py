"""Full-count, invented TRAIN metadata; historical identities are never read."""

from copy import deepcopy
import unittest
from unittest import mock

from snbi_fragmentation import study3_design as core
from test_study3_domain import rows_for_group


def synthetic_population():
    rows, folds = [], {}
    positions = {0: 0, 1: 0}
    for acquisition, count in zip(core.ACQUISITIONS, (24, 8)):
        for label in (0, 1):
            for index in range(count):
                gid = f"invented-{acquisition}-{label}-{index}"
                fold = index % 4
                folds[gid] = fold
                position = positions[label]
                positions[label] += 1
                n = 120 + int(position < 18) if label else 220 + int(position < 9)
                rows.extend(rows_for_group(n, gid, label, acquisition, fold))
    return rows, folds


class Study3DesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.folds = synthetic_population()
        # Only tests replace the constant. Production exposes no relaxed mode
        # or caller-supplied expected hash, including in its CLI.
        cls.patch = mock.patch.object(core, "EXPECTED_FOLD_SHA", core.json_sha(cls.folds))
        cls.patch.start()
        try:
            cls.design = core.build_study3_design(cls.rows, cls.folds)
        except BaseException:
            cls.patch.stop()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.patch.stop()

    def test_exact_population_and_28_fit_schedule(self):
        self.assertEqual(core.validate_study3_design(self.design),
                         {"status": "PASS", "rows": 10907, "groups": 64, "folds": 4, "distinct_fits": 28})
        self.assertEqual(self.design["cv_fold_by_group"], self.folds)
        self.assertEqual(len({spec["fit_id"] for spec in self.design["fits"]}), 28)
        self.assertTrue(all(type(spec["fold"]) is int for spec in self.design["fits"]))

    def test_no_group_crosses_fold_and_all_validation_groups_preserved(self):
        for spec in self.design["fits"]:
            train, valid = set(spec["training_group_ids"]), set(spec["validation_group_ids"])
            self.assertFalse(train & valid)
            self.assertEqual((len(train), len(valid)), (48, 16))
            self.assertEqual(valid, {gid for gid, fold in self.folds.items() if fold == spec["fold"]})

    def test_wrong_count_class_fold_or_split_fails_closed(self):
        for mutation in (lambda rows: rows.pop(), lambda rows: rows[0].update(split="TEST"),
                         lambda rows: rows[0].update(tier="SILVER"), lambda rows: rows[0].update(cv_fold=3),
                         lambda rows: rows[0].update(label=1, tier="GOLD")):
            rows = deepcopy(self.rows)
            mutation(rows)
            with self.assertRaises(ValueError):
                core.build_study3_design(rows, self.folds)

    def test_replacing_historical_fold_mapping_is_prohibited(self):
        folds = dict(self.folds)
        first = next(iter(folds))
        folds[first] = (folds[first] + 1) % 4
        with self.assertRaises(ValueError):
            core.build_study3_design(self.rows, folds)

    def test_resigning_tampered_schedule_does_not_bypass_contract(self):
        for mutate in (lambda d: d["fits"].append(deepcopy(d["fits"][0])),
                       lambda d: d["fits"][0]["training_group_ids"].append(d["fits"][0]["validation_group_ids"][0]),
                       lambda d: d["fits"][0].update(condition="RF_TUNED"),
                       lambda d: d["fits"][0].update(fold=False),
                       lambda d: d["contract"].update(adaptive_tuning=True)):
            design = deepcopy(self.design)
            mutate(design)
            design["design_sha256"] = core.json_sha({k: v for k, v in design.items() if k != "design_sha256"})
            with self.assertRaises(ValueError):
                core.validate_study3_design(design)

    def test_all_28_slots_consumed_and_fit_29_denied(self):
        budget = core.FitBudget(self.design["fits"])
        for spec in self.design["fits"]:
            budget.start(spec["fit_id"])
            budget.complete(spec["fit_id"])
        self.assertEqual(budget.snapshot()["distinct_fits_completed"], 28)
        with self.assertRaises(ValueError):
            budget.start(self.design["fits"][0]["fit_id"])

    def test_failed_fit_consumes_slot_without_retry_or_reordering(self):
        budget = core.FitBudget(self.design["fits"])
        first, second = [spec["fit_id"] for spec in self.design["fits"][:2]]
        with self.assertRaises(ValueError):
            budget.start(second)
        budget.start(first)
        for fit_id in (first, second):
            with self.assertRaises(ValueError):
                budget.start(fit_id)
        with self.assertRaises(ValueError):
            budget.complete(second)
        self.assertEqual(budget.snapshot()["distinct_fits_started"], 1)


if __name__ == "__main__":
    unittest.main()
