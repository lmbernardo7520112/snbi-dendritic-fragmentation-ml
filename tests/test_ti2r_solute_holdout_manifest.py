"""Typed manifest roundtrip only: no experimental paths or scientific calls."""

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).absolute().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "locked_holdout_manifest", ROOT / "scripts/run_ti2r_solute_locked_holdout.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class TypedManifestTests(unittest.TestCase):
    def test_recursive_types_survive_actual_manifest_encoder(self):
        fixture = {"floats": [1.0, 16.0, 235.0, 2.0, 3.0], "int": 16,
                   "str": "1.0", "bool": True,
                   "nested": [{"float": 1.0, "int": 1, "bool": False}]}
        decoded = json.loads(RUNNER.encode_manifest({"phase": "fixture"}, fixture))
        self.assertTrue(RUNNER.safe._exact(decoded["configurations"], fixture))
        self.assertTrue(all(type(v) is float for v in decoded["configurations"]["floats"]))

    def test_frozen_configurations_survive_production_serialization(self):
        configs = {name: json.loads((ROOT / path).read_text()) for name, path in
                   (("v1", RUNNER.V1_CONFIG), ("v2", RUNNER.V2_CONFIG))}
        decoded = json.loads(RUNNER.encode_manifest({}, configs))["configurations"]
        self.assertTrue(RUNNER.safe._exact(decoded, configs))
        for field in ("minimum_entropy_bits", "saturation_low_y", "saturation_high_y",
                      "median_limit_px", "p95_limit_px", "maximum_limit_px"):
            with self.subTest(field=field):
                self.assertIs(type(decoded["v1"][field]), float)

    def test_exact_still_rejects_numeric_type_substitution(self):
        for value in (1.0, 16.0, 235.0, 2.0, 3.0):
            with self.subTest(value=value):
                self.assertFalse(RUNNER.safe._exact({"v": [value]}, {"v": [int(value)]}))
        self.assertFalse(RUNNER.safe._exact(True, 1))
        self.assertFalse(RUNNER.safe._exact("1", 1))


if __name__ == "__main__":
    unittest.main()
