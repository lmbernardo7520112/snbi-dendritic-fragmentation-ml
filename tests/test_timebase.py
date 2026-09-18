import copy
import json
import unittest
from decimal import Decimal
from pathlib import Path

from snbi_fragmentation.timebase import PhysicalTimeRule, TimeRuleError


class PhysicalTimeRuleTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(Path("configs/time_rule.json").read_text(encoding="utf-8"))
        self.rule = PhysicalTimeRule.from_mapping(self.data)

    def test_maps_zero_based_index_to_physical_time(self):
        self.assertEqual(self.rule.physical_time(0), Decimal("0.00"))
        self.assertEqual(self.rule.physical_time(1), Decimal("1.18"))
        self.assertEqual(self.rule.physical_time(293), Decimal("345.74"))
        self.assertEqual(self.rule.physical_time(394), Decimal("464.92"))

    def test_file_fps_is_not_physical_time(self):
        self.assertFalse(self.rule.reported_fps_is_physical_time)
        self.assertEqual(self.rule.playback_acceleration(Decimal("5")), Decimal("5.90"))

    def test_rejects_invalid_indices_and_rule(self):
        for invalid in (-1, True, False, 1.2, "1", None):
            for method in (self.rule.physical_time, self.rule.elapsed_time,
                           lambda index: self.rule.experimental_time("ESM1", index)):
                with self.subTest(invalid=invalid, method=method), self.assertRaises((TypeError, ValueError)):
                    method(invalid)
        with self.assertRaises(TimeRuleError):
            PhysicalTimeRule.from_mapping({
                "delta_t_seconds": "1.18", "frame_index_origin": 0,
                "time_origin_seconds": "0", "reported_fps_is_physical_time": True,
            })

    def test_all_frozen_times_are_exact_decimals_and_legacy_alias_is_elapsed(self):
        groups = (
            (("ESM1", "ESM2", "ESM3"),
             ((0, "0.00", "-25.96"), (73, "86.14", "60.18"),
              (146, "172.28", "146.32"), (219, "258.42", "232.46"),
              (293, "345.74", "319.78"))),
            (("ESM4", "ESM5", "ESM6"),
             ((0, "0.00", "-34.22"), (98, "115.64", "81.42"),
              (197, "232.46", "198.24"), (295, "348.10", "313.88"),
              (394, "464.92", "430.70"))),
        )
        for sources, points in groups:
            for source in sources:
                for index, elapsed, experimental in points:
                    with self.subTest(source=source, index=index):
                        self.assertEqual(self.rule.elapsed_time(index), Decimal(elapsed))
                        self.assertEqual(self.rule.physical_time(index), Decimal(elapsed))
                        self.assertEqual(self.rule.experimental_time(source, index), Decimal(experimental))

    def test_source_mapping_is_complete_unique_and_immutable(self):
        self.assertEqual(dict(self.rule.source_offsets), {
            **{source: Decimal("-25.96") for source in ("ESM1", "ESM2", "ESM3")},
            **{source: Decimal("-34.22") for source in ("ESM4", "ESM5", "ESM6")},
        })
        with self.assertRaises(TypeError):
            self.rule.source_offsets["ESM1"] = Decimal("0")
        self.data["experimental_time_models"]["bottom-up"]["offset_s"] = "0"
        self.assertEqual(self.rule.experimental_time("ESM1", 0), Decimal("-25.96"))

    def test_mapping_rejects_missing_duplicate_unknown_and_swapped_sources(self):
        for source_ids in ([], ["ESM1", "ESM2"], ["ESM1", "ESM1", "ESM3"],
                           ["ESM1", "ESM2", "ESM7"], ["ESM1", "ESM2", "ESM4"],
                           ["ESM1", "ESM2", None], "ESM1", None):
            bad = copy.deepcopy(self.data)
            bad["experimental_time_models"]["bottom-up"]["source_ids"] = source_ids
            with self.subTest(sources=source_ids), self.assertRaises(TimeRuleError):
                PhysicalTimeRule.from_mapping(bad)
        bad = copy.deepcopy(self.data)
        bad["experimental_time_models"]["bottom-up"]["source_ids"][2] = "ESM4"
        bad["experimental_time_models"]["top-down"]["source_ids"][0] = "ESM3"
        with self.assertRaises(TimeRuleError):
            PhysicalTimeRule.from_mapping(bad)

    def test_mapping_rejects_incomplete_models_or_applicability(self):
        for models in ({}, {"bottom-up": self.data["experimental_time_models"]["bottom-up"]},
                       {**self.data["experimental_time_models"], "other": {}}, None):
            bad = copy.deepcopy(self.data)
            bad["experimental_time_models"] = models
            with self.subTest(models=models), self.assertRaises(TimeRuleError):
                PhysicalTimeRule.from_mapping(bad)
        for applicability in ([], ["ESM1"]*6, ["ESM1", "ESM2", "ESM3", "ESM4", "ESM5", "ESM7"], None):
            bad = copy.deepcopy(self.data)
            bad["applicability"] = applicability
            with self.subTest(applicability=applicability), self.assertRaises(TimeRuleError):
                PhysicalTimeRule.from_mapping(bad)

    def test_offsets_and_cadence_reject_nonfinite_or_unapproved_values(self):
        for offset in ("-34.22", "-25.9600000001", "NaN", "Infinity", True, None):
            bad = copy.deepcopy(self.data)
            bad["experimental_time_models"]["bottom-up"]["offset_s"] = offset
            with self.subTest(offset=offset), self.assertRaises(TimeRuleError):
                PhysicalTimeRule.from_mapping(bad)
        for key, value in (("delta_t_seconds", "NaN"), ("delta_t_seconds", "0.2"),
                           ("delta_t_s", "1.18000000001"), ("frame_index_origin", False),
                           ("frame_index_origin", 0.0), ("time_origin_seconds", "-25.96"),
                           ("reported_fps_is_physical_time", "false"),
                           ("reported_fps_is_physical_time", 0),
                           ("time_model_status", "UNKNOWN"), ("time_zero_reference", "first_frame")):
            bad = copy.deepcopy(self.data)
            bad[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(TimeRuleError):
                PhysicalTimeRule.from_mapping(bad)

    def test_unknown_source_has_no_default_offset(self):
        for source in (None, "", "ESM0", "ESM7", True, []):
            with self.subTest(source=source), self.assertRaises(TimeRuleError):
                self.rule.experimental_time(source, 0)

    def test_playback_fps_cannot_change_elapsed_or_experimental_time(self):
        for fps in (1, 5, 1000):
            data = copy.deepcopy(self.data)
            data["reported_fps"] = fps
            rule = PhysicalTimeRule.from_mapping(data)
            self.assertEqual(rule.elapsed_time(146), Decimal("172.28"))
            self.assertEqual(rule.experimental_time("ESM1", 146), Decimal("146.32"))


if __name__ == "__main__":
    unittest.main()
