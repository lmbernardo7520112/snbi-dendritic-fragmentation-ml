"""Synthetic, dependency-free checks of the frozen TI-2 geometry contracts."""

import math
import copy
import json
from pathlib import Path
import unittest

from snbi_fragmentation import ti2_geometry as geometry


IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


class MatrixContractTests(unittest.TestCase):
    def test_pixel_centers_use_x_column_y_row(self):
        matrix = ((1, 0, 13), (0, 1, -7), (0, 0, 1))
        self.assertEqual(geometry.transform_point(matrix, (2, 5)), (15, -2))

    def test_inverse_and_roundtrip(self):
        matrix = ((1.002, 0.01, -3.4), (-0.015, 1.003, 2.1), (0, 0, 1))
        inverse = geometry.invert_matrix(matrix)
        points = ((0, 0), (1277, 1017), (12.3, 18.7))
        self.assertLess(geometry.roundtrip_error(matrix, inverse, points), 1e-10)

    def test_invalid_matrices_are_rejected(self):
        invalid = (
            ((1, 0), (0, 1)),
            ((1, 0, 0), (0, 0, 0), (0, 0, 1)),
            ((1, 0, math.nan), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (0, 1, 0), (0.001, 0, 1)),
        )
        for matrix in invalid:
            with self.subTest(matrix=matrix):
                with self.assertRaises(geometry.GeometryContractError):
                    geometry.invert_matrix(matrix)

    def test_transform_classes_match_matrix(self):
        valid = (
            (IDENTITY, "identity"),
            (((1, 0, -1), (0, 1, -3), (0, 0, 1)), "border_crop"),
            (((1, 0, 2), (0, 1, -3), (0, 0, 1)), "integer_translation"),
            (((1, 0, 0.3), (0, 1, -3.1), (0, 0, 1)), "subpixel_translation"),
            (((0.8, -0.6, 2), (0.6, 0.8, 3), (0, 0, 1)), "rigid"),
            (((1.6, -1.2, 2), (1.2, 1.6, 3), (0, 0, 1)), "similarity"),
        )
        for matrix, transform_class in valid:
            with self.subTest(transform_class=transform_class):
                self.assertEqual(
                    geometry.validate_transform(matrix, transform_class), matrix
                )

    def test_class_cannot_hide_more_complex_transform(self):
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_transform(((1, 0, 0.3), (0, 1, 0), (0, 0, 1)), "integer_translation")
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_transform(((1.1, 0, 0), (0, 1, 0), (0, 0, 1)), "similarity")
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_transform(((1, 0, 1), (0, 1, 0), (0, 0, 1)), "identity")

    def test_affine_requires_explicit_evidence(self):
        matrix = ((1, 0.01, 0), (0, 1.01, 0), (0, 0, 1))
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_transform(matrix, "affine")
        self.assertEqual(geometry.validate_transform(matrix, "affine", affine_evidence="documented independent geometry"), matrix)

    def test_prohibited_classes_and_axis_inversions_fail_closed(self):
        for transform_class in ("projective", "non_rigid", "homography"):
            with self.subTest(transform_class=transform_class):
                with self.assertRaises(geometry.GeometryContractError):
                    geometry.validate_transform(IDENTITY, transform_class)
        for a, d in ((-1, 1), (1, -1), (-1, -1)):
            with self.assertRaises(geometry.GeometryContractError):
                geometry.validate_transform(((a, 0, 0), (0, d, 0), (0, 0, 1)), "rigid")

    def test_wrong_inverse_is_detected(self):
        matrix = ((1, 0, 0.3), (0, 1, 0), (0, 0, 1))
        self.assertGreater(geometry.roundtrip_error(matrix, IDENTITY, ((0, 0),)), 0.25)


class ResidualContractTests(unittest.TestCase):
    def test_interpolated_percentile_and_threshold_boundaries(self):
        stats = geometry.residual_statistics((0, 1, 2))
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["median_px"], 1)
        self.assertAlmostEqual(stats["p95_px"], 1.9)
        self.assertEqual(stats["maximum_px"], 2)
        self.assertEqual(geometry.evaluate_residuals((0, 1, 2), 0.25)["status"], "PASS")

    def test_every_error_threshold_blocks(self):
        cases = (((1.01,), 0), ((0,) * 18 + (2.9, 3), 0), ((0,) * 99 + (3.01,), 0), ((0,), 0.251))
        for residuals, roundtrip in cases:
            with self.subTest(residuals=residuals, roundtrip=roundtrip):
                self.assertEqual(geometry.evaluate_residuals(residuals, roundtrip)["status"], "BLOCKED")

    def test_no_measurements_and_invalid_residuals_are_not_pass(self):
        for residuals in ((), (-1,), (math.nan,), (math.inf,)):
            with self.assertRaises(geometry.GeometryContractError):
                geometry.residual_statistics(residuals)

    def test_frozen_estimation_validation_indices(self):
        geometry.validate_estimation_validation("bottom-up", (0, 146, 293), (73, 219))
        geometry.validate_estimation_validation("top-down", (0, 197, 394), (98, 295))
        for estimate, validate in (((0, 73, 293), (146, 219)), ((0, 146, 293), (73, 218)), ((0, 146, 293, 73), (73, 219))):
            with self.assertRaises(geometry.GeometryContractError):
                geometry.validate_estimation_validation("bottom-up", estimate, validate)


class ROIContractTests(unittest.TestCase):
    def test_largest_rectangle_does_not_use_invalid_hole(self):
        mask = [[True] * 5 for _ in range(4)]
        mask[1][2] = False
        self.assertEqual(geometry.largest_valid_rectangle(mask), (0, 2, 5, 2))
        geometry.validate_roi((0, 2, 5, 2), (mask, mask))

    def test_empty_support_blocks(self):
        with self.assertRaises(geometry.GeometryContractError):
            geometry.largest_valid_rectangle(((False, False), (False, False)))

    def test_tie_is_deterministic(self):
        self.assertEqual(geometry.largest_valid_rectangle(((True, False, True), (True, False, True))), (0, 0, 1, 2))

    def test_histogram_rectangle_matches_exhaustive_small_masks(self):
        # Independent exhaustive oracle for every nonempty 3x3 boolean mask.
        for pattern in range(1, 1 << 9):
            mask = [[bool(pattern & (1 << (y * 3 + x))) for x in range(3)] for y in range(3)]
            candidates = []
            for y in range(3):
                for x in range(3):
                    for height in range(1, 4 - y):
                        for width in range(1, 4 - x):
                            if all(mask[row][column] for row in range(y, y + height) for column in range(x, x + width)):
                                candidates.append((-width * height, y, x, width, height))
            _, y, x, width, height = min(candidates)
            with self.subTest(pattern=pattern):
                self.assertEqual(geometry.largest_valid_rectangle(mask), (x, y, width, height))

    def test_roi_must_have_complete_support_in_every_mask(self):
        good = ((True, True), (True, True))
        bad = ((True, True), (True, False))
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_roi((0, 0, 2, 2), (good, bad))
        for roi in ((0, 0, 3, 2), (-1, 0, 1, 1), (0, 0, 0, 1), (0.1, 0, 1, 1)):
            with self.assertRaises(geometry.GeometryContractError):
                geometry.validate_roi(roi, (good,))

    def test_malformed_masks_rejected(self):
        for mask in ((), ((True,), (True, False)), ((1, 0),)):
            with self.assertRaises(geometry.GeometryContractError):
                geometry.largest_valid_rectangle(mask)

    def test_condition_rois_are_independent(self):
        geometry.validate_condition_rois({"bottom-up": (0, 0, 1278, 1018), "top-down": (0, 0, 1278, 1012)})
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_condition_rois({"global": (0, 0, 1278, 1012)})


class CalibrationContractTests(unittest.TestCase):
    def test_unresolved_scale_stays_in_pixels(self):
        record = geometry.unresolved_scale("No sufficient primary source was provided.")
        geometry.validate_scale(record)
        self.assertEqual(record["scale_status"], "UNRESOLVED")
        self.assertEqual(record["coordinate_unit"], "pixel")
        self.assertIsNone(record["micrometres_per_pixel"])
        with self.assertRaises(geometry.GeometryContractError):
            geometry.to_physical_length(12, record)

    def test_physical_scale_requires_source_and_uncertainty(self):
        record = {"scale_status": "RESOLVED", "coordinate_unit": "micrometre", "micrometres_per_pixel": 4.2, "source": "primary acquisition record; document SHA-256 and section", "method": "original acquisition metadata", "uncertainty_micrometres_per_pixel": 0.1, "applicability": "both axes in canonical frame"}
        geometry.validate_scale(record)
        self.assertAlmostEqual(geometry.to_physical_length(1.25, record), 5.25)
        for key in ("source", "method", "uncertainty_micrometres_per_pixel", "applicability"):
            bad = dict(record)
            bad.pop(key)
            with self.assertRaises(geometry.GeometryContractError):
                geometry.validate_scale(bad)

    def test_unresolved_physical_units_and_hidden_conversion_fail_closed(self):
        record = geometry.unresolved_scale("unresolved")
        record["coordinate_unit"] = "micrometre"
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_scale(record)
        record = geometry.unresolved_scale("unresolved")
        record["micrometres_per_pixel"] = 4.2
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_scale(record)

    def test_uncertainty_budget_requires_each_explicit_status(self):
        budget = {name: {"status": "UNRESOLVED", "reason": "not yet measured"} for name in geometry.UNCERTAINTY_COMPONENTS}
        geometry.validate_uncertainty_budget(budget)
        budget.pop("roi")
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_uncertainty_budget(budget)

    def modelled_budget(self):
        budget = {name: {"status": "UNRESOLVED", "reason": "no empirical evidence"}
                  for name in geometry.UNCERTAINTY_COMPONENTS}
        budget["discretization"] = {
            "status": "MODELLED", "evidence_kind": "ANALYTICAL_ASSUMPTION",
            "value": 1 / math.sqrt(12), "unit": "pixel",
            "method": "standard deviation of a uniform quantization distribution",
            "provenance": "analytical_model",
            "analytical_assumption": "uniform per-axis quantization error in [-0.5,+0.5] pixel",
        }
        return budget

    def test_analytical_discretization_is_valid_as_modelled(self):
        geometry.validate_uncertainty_budget(self.modelled_budget())

    def test_modelled_requires_each_evidence_field(self):
        for key in ("value", "unit", "method", "provenance", "analytical_assumption", "evidence_kind"):
            with self.subTest(missing=key):
                budget = self.modelled_budget()
                del budget["discretization"][key]
                with self.assertRaises(geometry.GeometryContractError):
                    geometry.validate_uncertainty_budget(budget)

    def test_modelled_rejects_nonfinite_negative_boolean_and_empty_evidence(self):
        for value in (math.nan, math.inf, -1, True, "0.288675"):
            budget = self.modelled_budget()
            budget["discretization"]["value"] = value
            with self.subTest(value=value), self.assertRaises(geometry.GeometryContractError):
                geometry.validate_uncertainty_budget(budget)
        for key in ("unit", "method", "provenance", "analytical_assumption", "evidence_kind"):
            budget = self.modelled_budget()
            budget["discretization"][key] = ""
            with self.subTest(key=key), self.assertRaises(geometry.GeometryContractError):
                geometry.validate_uncertainty_budget(budget)

    def test_analytical_model_cannot_be_relabelled_measured(self):
        budget = self.modelled_budget()
        budget["discretization"]["status"] = "MEASURED"
        with self.assertRaises(geometry.GeometryContractError):
            geometry.validate_uncertainty_budget(budget)

    def test_empirical_measurement_remains_a_distinct_supported_status(self):
        budget = self.modelled_budget()
        budget["registration"] = {
            "status": "MEASURED", "value": 0.5, "unit": "pixel",
            "method": "independent empirical residual measurement",
            "evidence_kind": "EMPIRICAL_MEASUREMENT", "provenance": "synthetic test fixture",
        }
        geometry.validate_uncertainty_budget(budget)

    def test_current_text_records_keep_unresolved_metrology_and_zero_conversions(self):
        root = Path(__file__).resolve().parents[1]
        for condition in ("bottom-up", "top-down"):
            record = json.loads((root / f"configs/calibration/{condition}.json").read_text())
            before = copy.deepcopy(record)
            geometry.validate_uncertainty_budget(record["uncertainty_budget"])
            component = record["uncertainty_budget"]["discretization"]
            self.assertEqual(component["status"], "MODELLED")
            self.assertEqual(component["evidence_kind"], "ANALYTICAL_ASSUMPTION")
            self.assertEqual(component["value"], 0.2886751345948129)
            self.assertEqual(record["nominal_spatial_scale"]["metrological_uncertainty_status"], "UNRESOLVED")
            self.assertEqual(record["scale"]["scale_status"], "UNRESOLVED")
            self.assertEqual(record["coordinate_unit"], "pixel")
            self.assertEqual(record["physical_coordinate_conversions_performed"], 0)
            self.assertEqual(record, before)


if __name__ == "__main__":
    unittest.main()
