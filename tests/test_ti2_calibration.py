"""Synthetic, standard-library tests for printed scale-bar metrology."""

import unittest

from snbi_fragmentation import ti2_calibration as calibration


class ScaleBarTests(unittest.TestCase):
    def test_frozen_v2_rectangle_includes_visually_documented_extent(self):
        self.assertEqual(calibration.corner_rectangle(1278, 1018), (792, 865, 1252, 997))

    def test_inclusive_raster_edges_and_threshold_stability(self):
        image = [[200] * 400 for _ in range(120)]
        for y in range(80, 85):
            image[y][100:301] = [20] * 201
        result = calibration.measure_bar(image, (0, 0, 400, 120))
        self.assertEqual(result['status'], 'MEASURED')
        self.assertEqual(result['length_px'], 201)
        self.assertEqual(result['endpoints_center_x'], [100, 300])
        self.assertEqual(result['endpoints_edge_x'], [99.5, 300.5])
        self.assertGreaterEqual(result['length_uncertainty_bound_px'], 1)

    def test_no_bar_or_clipped_bar_is_unresolved(self):
        for image in ([[200] * 400 for _ in range(120)], [[0] * 400 for _ in range(120)]):
            self.assertEqual(calibration.measure_bar(image, (0, 0, 400, 120))['status'], 'UNRESOLVED')

    def test_single_dark_row_is_insufficient(self):
        image = [[200] * 400 for _ in range(120)]
        image[80][100:301] = [16] * 201
        self.assertEqual(calibration.measure_bar(image, (0, 0, 400, 120))['status'], 'UNRESOLVED')

    def test_ambiguous_parallel_long_bars_are_unresolved(self):
        image = [[200] * 400 for _ in range(120)]
        for y in (40, 41, 80, 81):
            image[y][100:301] = [16] * 201
        self.assertEqual(calibration.measure_bar(image, (0, 0, 400, 120))['status'], 'UNRESOLVED')

    def test_only_six_estimation_records_allowed(self):
        calibration.require_estimation_record({'source_id': 'ESM1', 'frame_index': 146, 'role': 'estimation'})
        for item in ({'source_id': 'ESM1', 'frame_index': 73, 'role': 'validation'}, {'source_id': 'ESM3', 'frame_index': 146, 'role': 'estimation'}):
            with self.assertRaises(ValueError):
                calibration.require_estimation_record(item)


if __name__ == '__main__':
    unittest.main()
