import json
import unittest
from decimal import Decimal
from pathlib import Path

from snbi_fragmentation.timebase import PhysicalTimeRule, TimeRuleError


class PhysicalTimeRuleTests(unittest.TestCase):
    def setUp(self):
        data = json.loads(Path("configs/time_rule.json").read_text(encoding="utf-8"))
        self.rule = PhysicalTimeRule.from_mapping(data)

    def test_maps_zero_based_index_to_physical_time(self):
        self.assertEqual(self.rule.physical_time(0), Decimal("0.00"))
        self.assertEqual(self.rule.physical_time(1), Decimal("1.18"))
        self.assertEqual(self.rule.physical_time(293), Decimal("345.74"))
        self.assertEqual(self.rule.physical_time(394), Decimal("464.92"))

    def test_file_fps_is_not_physical_time(self):
        self.assertFalse(self.rule.reported_fps_is_physical_time)
        self.assertEqual(self.rule.playback_acceleration(Decimal("5")), Decimal("5.90"))

    def test_rejects_invalid_indices_and_rule(self):
        for invalid in (-1, True, 1.2):
            with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                self.rule.physical_time(invalid)
        with self.assertRaises(TimeRuleError):
            PhysicalTimeRule.from_mapping({
                "delta_t_seconds": "1.18", "frame_index_origin": 0,
                "time_origin_seconds": "0", "reported_fps_is_physical_time": True,
            })


if __name__ == "__main__":
    unittest.main()
