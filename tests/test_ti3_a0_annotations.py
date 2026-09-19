"""TI3-A0 graphical diagnostics exercised only on generated arrays and metadata."""

import copy
import importlib.util
import unittest

from snbi_fragmentation import ti3_a0_annotations as annotations


NUMERICAL = importlib.util.find_spec("numpy") is not None and importlib.util.find_spec("scipy") is not None
# Synthetic-fixture bounds only: these are not experimental defaults.
CONFIG = {
    "chroma_distance": 20,
    "minimum_component_pixels": 24,
    "minimum_radius": 5.0,
    "maximum_radius": 60.0,
    "maximum_axis_ratio": 1.2,
    "maximum_radial_p95": 3.0,
    "minimum_angular_coverage": 0.9,
}


def circle(component_id, x, y):
    return {"component_id": component_id, "classification": annotations.VALID, "center_xy_px": [x, y]}


def frame(index, components, source="SYNTHETIC"):
    return {"source_id": source, "frame_index": index, "components": components}


class AnnotationConfigurationTests(unittest.TestCase):
    def test_explicit_configuration_has_no_defaults(self):
        annotations.validate_config(CONFIG)
        for key in CONFIG:
            altered = dict(CONFIG)
            del altered[key]
            with self.subTest(missing=key), self.assertRaises(annotations.AnnotationDiagnosticError):
                annotations.validate_config(altered)
        with self.assertRaises(annotations.AnnotationDiagnosticError):
            annotations.validate_config({**CONFIG, "physical_scale": 1.0})

    def test_invalid_types_nonfinite_and_inconsistent_bounds_fail_closed(self):
        changes = [(key, True) for key in CONFIG] + [
            ("chroma_distance", 0), ("chroma_distance", 129), ("chroma_distance", 20.0),
            ("minimum_component_pixels", 0), ("minimum_component_pixels", 24.0),
            ("minimum_radius", 0), ("minimum_radius", 61), ("maximum_radius", -1),
            ("maximum_axis_ratio", 0.9), ("maximum_radial_p95", -1),
            ("minimum_angular_coverage", 0), ("minimum_angular_coverage", 1.01),
            ("maximum_radius", float("nan")), ("maximum_radius", float("inf")),
        ]
        for key, value in changes:
            with self.subTest(key=key, value=value), self.assertRaises(annotations.AnnotationDiagnosticError):
                annotations.validate_config({**CONFIG, key: value})


@unittest.skipUnless(NUMERICAL, "optional NumPy/SciPy unavailable; synthetic graphical arrays not run")
class GraphicalMarkerSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.np = np

    def planes(self):
        return self.np.full((96, 128), 128, dtype="uint8"), self.np.full((96, 128), 128, dtype="uint8")

    def ring(self, plane, center=(40, 40), radius=15, value=180):
        y, x = self.np.indices(plane.shape)
        plane[self.np.abs(self.np.hypot(x-center[0], y-center[1])-radius) <= 0.8] = value

    def extract(self, u, v, config=None):
        return annotations.extract_graphical_markers(u, v, 256, 192, CONFIG if config is None else config)

    def test_circle_native_pixel_centres_and_radius_respect_twofold_chroma_expansion(self):
        u, v = self.planes()
        self.ring(u)
        result = self.extract(u, v)
        self.assertEqual(result["component_count"], 1)
        self.assertEqual(result["valid_circle_count"], 1)
        component = result["components"][0]
        self.np.testing.assert_allclose(component["center_xy_px"], [80.5, 80.5], atol=1e-10)
        self.assertAlmostEqual(component["radius_graphical_px"], 30.0, delta=0.4)
        self.assertEqual(component["enclosed_hole_count"], 1)
        self.assertEqual(component["angular_bins_total"], 36)
        self.assertEqual(component["angular_bins_occupied"], 36)
        self.assertEqual(result["colored_pixel_count"], 4*result["colored_chroma_sample_count"])
        self.assertEqual(component["semantic_label"], "UNKNOWN")
        self.assertEqual(component["physical_extent"], "NOT_INFERRED")

    def test_both_chroma_planes_and_negative_deviations_are_symmetric_without_uint_wrap(self):
        u, v = self.planes()
        self.ring(u, value=148)
        positive = self.extract(u, v)
        u, v = self.planes()
        self.ring(v, value=108)
        negative = self.extract(u, v)
        self.assertEqual(positive["components"], negative["components"])
        u, v = self.planes()
        self.ring(v, value=109)
        self.assertEqual(self.extract(u, v)["component_count"], 0)

    def test_two_disjoint_circles_remain_two_components(self):
        u, v = self.planes()
        self.ring(u, center=(30, 40))
        self.ring(v, center=(90, 40))
        result = self.extract(u, v)
        self.assertEqual(result["component_count"], 2)
        self.assertEqual(result["valid_circle_count"], 2)
        self.assertEqual(sum(c["area_px"] for c in result["components"]), result["colored_pixel_count"])

    def test_overlapping_circles_stay_one_ambiguous_component_without_hough_separation(self):
        u, v = self.planes()
        self.ring(u, center=(40, 40))
        self.ring(u, center=(55, 40))
        result = self.extract(u, v)
        self.assertEqual(result["component_count"], 1)
        self.assertEqual(result["valid_circle_count"], 0)
        component = result["components"][0]
        self.assertEqual(component["classification"], annotations.AMBIGUOUS)
        self.assertGreater(component["enclosed_hole_count"], 1)
        self.assertIn("TOPOLOGY_NOT_ONE_ENCLOSED_HOLE", component["reasons"])
        self.assertEqual(component["area_px"], result["colored_pixel_count"])

    def test_filled_blob_and_text_shape_are_retained_as_noncircular(self):
        for shape in ("filled_disk", "letter_E"):
            u, v = self.planes()
            if shape == "filled_disk":
                y, x = self.np.indices(u.shape)
                u[self.np.hypot(x-40, y-40) <= 15] = 180
            else:
                u[20:50, 20:23] = 180
                for y in (20, 33, 47):
                    u[y:y+3, 20:40] = 180
            with self.subTest(shape=shape):
                result = self.extract(u, v)
                self.assertEqual(result["component_count"], 1)
                self.assertEqual(result["ambiguous_component_count"], 1)
                self.assertEqual(result["components"][0]["enclosed_hole_count"], 0)

    def test_boundary_cut_circle_is_never_certified(self):
        u, v = self.planes()
        self.ring(u, center=(5, 40))
        component = self.extract(u, v)["components"][0]
        self.assertEqual(component["classification"], annotations.AMBIGUOUS)
        self.assertTrue(component["touches_boundary"])
        self.assertIn("TOUCHES_NATIVE_BOUNDARY", component["reasons"])

    def test_small_component_and_empty_frame_do_not_create_negative_labels(self):
        u, v = self.planes()
        empty = self.extract(u, v)
        self.assertEqual(empty["component_count"], 0)
        self.assertEqual(empty["absence_semantics"], "UNKNOWN_NOT_A_NEGATIVE_LABEL")
        u[20, 30] = 180
        result = self.extract(u, v)
        self.assertEqual(result["small_component_count"], 1)
        self.assertEqual(result["components"][0]["area_px"], 4)
        self.assertEqual(result["components"][0]["classification"], annotations.SMALL)

    def test_input_layout_and_types_are_validated_before_diagnostics(self):
        u, v = self.planes()
        invalid = [(u, v, 255, 192), (u, v, True, 192), (u, v, 256, 0),
                   (u[:-1], v, 256, 192), (u.astype(float), v, 256, 192),
                   (u.ravel(), v, 256, 192)]
        for inputs in invalid:
            with self.subTest(shapes=[getattr(x, "shape", x) for x in inputs]), self.assertRaises(annotations.AnnotationDiagnosticError):
                annotations.extract_graphical_markers(*inputs, CONFIG)


class GraphicalPersistenceTests(unittest.TestCase):
    def test_monotonic_sampled_circles_have_stable_ids_without_physical_onset(self):
        frames = [frame(0, [circle(1, 10, 10)]),
                  frame(10, [circle(1, 10.2, 10), circle(2, 30, 30)]),
                  frame(20, [circle(1, 10.1, 10), circle(2, 30.1, 30), circle(3, 50, 50)])]
        result = annotations.match_persistence(frames, 1.0)
        self.assertEqual(result["cumulative_status"], "PASS_SAMPLED_GRAPHICAL_PERSISTENCE")
        self.assertEqual([t["first_observed_frame_index"] for t in result["trajectories"]], [0, 10, 20])
        self.assertEqual([len(t["observations"]) for t in result["trajectories"]], [3, 2, 1])
        self.assertTrue(all(t["physical_onset_frame_index"] is None for t in result["trajectories"]))
        self.assertTrue(all(t["event_label"] == "UNKNOWN" for t in result["trajectories"]))
        self.assertEqual(result["physical_events_inferred"], 0)

    def test_unique_matching_rejects_nearest_candidate_rescue(self):
        frames = [frame(0, [circle(1, 10, 10)]),
                  frame(10, [circle(1, 10.1, 10), circle(2, 11.0, 10)]),
                  frame(20, [circle(1, 10.1, 10), circle(2, 11.0, 10)])]
        result = annotations.match_persistence(frames, 1.0)
        self.assertEqual(result["cumulative_status"], "UNRESOLVED_GRAPHICAL_AMBIGUITY")
        first = result["transitions"][0]
        self.assertEqual(len(first["candidate_edges"]), 2)
        self.assertEqual(first["links"], [])
        self.assertEqual(first["unmatched_previous_component_ids"], [1])
        self.assertEqual(first["unmatched_current_component_ids"], [1, 2])
        self.assertTrue(all(o["track_id"] is None for o in result["observations"] if o["frame_index"] > 0))

    def test_reciprocity_prevents_two_previous_circles_claiming_one_current_circle(self):
        result = annotations.match_persistence([
            frame(0, [circle(1, 10, 10), circle(2, 11, 10)]),
            frame(10, [circle(1, 10.5, 10)]),
        ], 1.0)
        self.assertEqual(result["transitions"][0]["links"], [])
        self.assertEqual(len(result["transitions"][0]["ambiguous_edges"]), 2)

    def test_disappearance_is_retained_and_blocks_cumulative_graphics(self):
        result = annotations.match_persistence([
            frame(0, [circle(1, 10, 10), circle(2, 30, 30)]),
            frame(10, [circle(1, 10, 10)]),
        ], 1.0)
        self.assertEqual(result["cumulative_status"], "FAIL_SAMPLED_GRAPHICAL_DISAPPEARANCE")
        self.assertEqual(result["transitions"][0]["not_observed_next_sample_component_ids"], [2])
        self.assertEqual(result["negative_labels_created"], 0)

    def test_every_ambiguous_or_small_component_prevents_global_pass(self):
        for classification in (annotations.AMBIGUOUS, annotations.SMALL):
            frames = [frame(0, [circle(1, 10, 10)]),
                      frame(10, [circle(1, 10, 10), {"component_id": 2, "classification": classification}])]
            with self.subTest(classification=classification):
                result = annotations.match_persistence(frames, 0)
                self.assertEqual(result["cumulative_status"], "UNRESOLVED_GRAPHICAL_AMBIGUITY")
                self.assertEqual(len(result["transitions"][0]["links"]), 1)
                self.assertEqual(result["unresolved_components"][0]["component_id"], 2)

    def test_no_circle_or_single_instant_is_not_proof_of_cumulativity_or_negatives(self):
        for frames in ([frame(0, []), frame(10, [])], [frame(0, [circle(1, 10, 10)])]):
            result = annotations.match_persistence(frames, 1)
            self.assertEqual(result["cumulative_status"], "NOT_ASSESSABLE")
            self.assertEqual(result["negative_labels_created"], 0)
            self.assertEqual(result["cumulative_semantics"], "NOT_INFERRED_FROM_GRAPHICS")

    def test_mixed_sources_unsorted_indices_duplicates_and_invalid_centres_fail_closed(self):
        valid = [frame(0, [circle(1, 10, 10)]), frame(10, [circle(1, 10, 10)])]
        invalid = [[], [valid[1], valid[0]], [valid[0], valid[0]],
                   [valid[0], frame(10, [], "OTHER")], [frame(-1, [])], [frame(True, [])],
                   [frame(0, [circle(1, 10, 10), circle(1, 20, 20)])],
                   [frame(0, [circle(1, float("nan"), 0)])],
                   [frame(0, [{"component_id": 1, "classification": "UNKNOWN_STATUS"}])]]
        for frames in invalid:
            with self.subTest(frames=frames), self.assertRaises(annotations.AnnotationDiagnosticError):
                annotations.match_persistence(frames, 1)
        for tolerance in (True, -1, float("nan"), float("inf")):
            with self.subTest(tolerance=tolerance), self.assertRaises(annotations.AnnotationDiagnosticError):
                annotations.match_persistence(valid, tolerance)

    def test_functions_do_not_mutate_supplied_metadata(self):
        frames = [frame(0, [circle(1, 10, 10)]), frame(10, [circle(1, 10, 10)])]
        original = copy.deepcopy(frames)
        annotations.match_persistence(frames, 1)
        self.assertEqual(frames, original)


if __name__ == "__main__":
    unittest.main()
