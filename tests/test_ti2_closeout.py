"""Documentary time/scale contracts; text and Decimal only, no pixel access."""

from decimal import Decimal
import json
from pathlib import Path
import unittest

from snbi_fragmentation.timebase import load_time_rule


ROOT = Path(__file__).resolve().parents[1]
D = Decimal
REFERENCE = {
    'bottom-up': ((0, '0.00', '-25.96'), (73, '86.14', '60.18'),
                  (146, '172.28', '146.32'), (219, '258.42', '232.46'),
                  (293, '345.74', '319.78')),
    'top-down': ((0, '0.00', '-34.22'), (98, '115.64', '81.42'),
                 (197, '232.46', '198.24'), (295, '348.10', '313.88'),
                 (394, '464.92', '430.70')),
}


def document(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


class CloseoutTimeSemantics(unittest.TestCase):
    def setUp(self):
        self.rule = document('configs/time_rule.json')
        self.manifest = document('artifacts/metadata/ti2-pilot-manifest.json')

    def check_condition(self, condition):
        model = self.rule['experimental_time_models'][condition]
        for index, elapsed, experimental in REFERENCE[condition]:
            with self.subTest(condition=condition, index=index):
                calculated_elapsed = D(self.rule['delta_t_s']) * index
                self.assertEqual(calculated_elapsed, D(elapsed))
                self.assertEqual(calculated_elapsed + D(model['offset_s']), D(experimental))

    def test_bottom_up_all_five_documented_points(self):
        self.check_condition('bottom-up')

    def test_top_down_all_five_documented_points(self):
        self.check_condition('top-down')

    def test_each_source_has_one_experimental_time_model(self):
        models = self.rule['experimental_time_models']
        self.assertEqual(models['bottom-up']['source_ids'], ['ESM1', 'ESM2', 'ESM3'])
        self.assertEqual(models['top-down']['source_ids'], ['ESM4', 'ESM5', 'ESM6'])
        sources = [source for model in models.values() for source in model['source_ids']]
        self.assertEqual(len(sources), len(set(sources)))

    def test_zero_reference_and_negative_initial_experimental_time_are_explicit(self):
        self.assertEqual(self.rule['time_model_status'], 'DOCUMENTED_AND_RECONCILED')
        self.assertEqual(self.rule['time_zero_reference'], 'solidification_front_entry_into_field_of_view')
        self.assertEqual(self.rule['delta_t_s'], '1.18')
        self.assertFalse(self.rule['reported_fps_is_physical_time'])
        self.assertLess(D(self.rule['experimental_time_models']['bottom-up']['offset_s']), 0)
        self.assertLess(D(self.rule['experimental_time_models']['top-down']['offset_s']), 0)

    def test_thirty_manifest_items_have_both_exact_times(self):
        expected = {}
        for condition, rows in REFERENCE.items():
            for source in self.rule['experimental_time_models'][condition]['source_ids']:
                for index, elapsed, experimental in rows:
                    expected[(source, index)] = (D(elapsed), D(experimental))
        observed = {}
        for item in self.manifest['images']:
            key = (item['source_id'], item['frame_index'])
            self.assertNotIn(key, observed)
            observed[key] = (D(str(item['elapsed_from_first_frame_s'])), D(str(item['experimental_time_s'])))
            self.assertEqual(D(str(item['physical_time_s'])), observed[key][0])
        self.assertEqual(observed, expected)
        self.assertEqual(self.manifest['materialized_image_count'], 30)

    def test_legacy_alias_is_deprecated_without_silent_value_change(self):
        for semantics in (self.rule['legacy_field_semantics'], self.manifest['time_semantics']):
            alias = semantics['physical_time_s']
            self.assertEqual(alias['status'], 'DEPRECATED_ALIAS')
            self.assertEqual(alias['alias_of'], 'elapsed_from_first_frame_s')
            self.assertTrue(alias['values_preserved'])
        _, legacy = load_time_rule(ROOT/'configs/time_rule.json')
        self.assertEqual(legacy.physical_time(146), D('172.28'))
        self.assertEqual(legacy.physical_time(197), D('232.46'))
        self.assertEqual(legacy.time_origin_seconds, D('0.00'))

    def test_documentary_provenance_does_not_claim_new_source_retrieval(self):
        provenance = self.rule['documentary_provenance']
        self.assertEqual(provenance['doi'], '10.1007/s11837-015-1646-7')
        self.assertEqual(provenance['authority'], 'docs/decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md')
        self.assertFalse(provenance['independent_primary_text_retrieved'])


class CloseoutScaleSemantics(unittest.TestCase):
    def setUp(self):
        self.configs = [document(f'configs/calibration/{condition}.json')
                        for condition in ('bottom-up', 'top-down')]

    def test_both_axes_have_documented_nominal_pixel_size(self):
        for config in self.configs:
            nominal = config['nominal_spatial_scale']
            self.assertEqual(nominal['status'], 'DOCUMENTED')
            self.assertEqual(D(nominal['pixel_size_x_um']), D('1.40'))
            self.assertEqual(D(nominal['pixel_size_y_um']), D('1.40'))

    def test_raster_crosscheck_agrees_with_nominal_and_preserves_interval(self):
        # Published crosscheck rounded to 11 decimal places; <=1e-11 tolerance.
        tolerance = D('0.00000000001')
        for config in self.configs:
            nominal, bar = config['nominal_spatial_scale'], config['printed_bar_candidate']
            self.assertEqual(D(str(bar['nominal_printed_bar_micrometres'])), D('500'))
            self.assertEqual(bar['bar_length_px'], 357)
            exact = D('500') / D('357')
            self.assertLessEqual(abs(exact-D(nominal['raster_crosscheck_um_per_px'])), tolerance)
            lo, hi = map(lambda x: D(str(x)), bar['horizontal_scale_interval_micrometres_per_pixel'])
            self.assertLess(lo, D('1.40'))
            self.assertGreater(hi, D('1.40'))
            self.assertLessEqual(abs(lo-D('1.38888888889')), tolerance)
            self.assertLessEqual(abs(hi-D('1.41242937853')), tolerance)
            self.assertIn('not a statistical confidence interval', bar['uncertainty_kind'])

    def test_nominal_documentation_does_not_create_metrological_certificate(self):
        for config in self.configs:
            nominal = config['nominal_spatial_scale']
            self.assertEqual(nominal['metrological_uncertainty_status'], 'UNRESOLVED')
            self.assertFalse(nominal['full_metrological_uncertainty_certificate_available'])
            self.assertIsNone(config['scale']['uncertainty_micrometres_per_pixel'])

    def test_no_conversion_or_propagation_follows_from_nominal_scale(self):
        for config in self.configs:
            nominal = config['nominal_spatial_scale']
            self.assertFalse(nominal['eligible_for_coordinate_conversion'])
            self.assertFalse(nominal['propagation_to_unregistered_modalities_permitted'])
            self.assertFalse(config['printed_bar_candidate']['eligible_for_coordinate_conversion'])
            self.assertEqual(config['coordinate_unit'], 'pixel')
            self.assertEqual(config['physical_coordinate_conversions_performed'], 0)
            self.assertEqual(config['scale']['scale_status'], 'UNRESOLVED')
            self.assertIsNone(config['scale']['micrometres_per_pixel'])


if __name__ == '__main__':
    unittest.main()
