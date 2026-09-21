"""Synthetic-only Study2A identity, temporal states and immutable A0 fixtures."""

import copy
import importlib.util
import json
import unittest

from snbi_fragmentation import study2a_tracking as tracking
from snbi_fragmentation import ti3_a0_annotations as a0


HASH = "a" * 64
ACQUISITION = "bottom_up_anti_parallel"
NUMERICAL = (importlib.util.find_spec("numpy") is not None
             and importlib.util.find_spec("scipy") is not None)
A0_CONFIG = {
    "chroma_distance": 20, "minimum_component_pixels": 32,
    "minimum_radius": 8.0, "maximum_radius": 16.0,
    "maximum_axis_ratio": 1.2, "maximum_radial_p95": 4.0,
    "minimum_angular_coverage": 0.9,
}


def component(cid, x=50.0, y=50.0, classification=a0.VALID, box=None):
    return {
        "component_id": cid, "classification": classification,
        "center_xy_px": [x, y],
        "bbox_xyxy": list(box if box is not None else (x - 11, y - 11, x + 12, y + 12)),
        "reasons": [] if classification == a0.VALID else ["SYNTHETIC_REJECTION"],
        "semantic_label": "UNKNOWN", "physical_extent": "NOT_INFERRED",
    }


def result(*components, footprints=None, colored_pixel_count=None):
    output = {
        "component_count": len(components),
        "valid_circle_count": sum(c["classification"] == a0.VALID for c in components),
        "ambiguous_component_count": sum(c["classification"] == a0.AMBIGUOUS for c in components),
        "small_component_count": sum(c["classification"] == a0.SMALL for c in components),
        "components": list(components),
    }
    if footprints is not None:
        output["_component_pixels"] = {cid: frozenset(pixels) for cid, pixels in footprints.items()}
    if colored_pixel_count is not None:
        output["colored_pixel_count"] = colored_pixel_count
    return output


def run(*frames, source="ESM3"):
    acquisition = tracking.SOURCE_CONTRACT[source][0]
    tracker = tracking.TemporalTracker(source, acquisition, len(frames))
    for index, frame in enumerate(frames):
        tracker.add_frame(index, frame, HASH)
    return tracker.finish()


class TemporalTrackingTests(unittest.TestCase):
    def test_persistent_circle_uses_stable_canonical_center(self):
        out = run(result(component(1)), result(component(1, 51.0)), result(component(9, 49.0)))
        self.assertEqual(len(out["sites"]), 1)
        self.assertEqual(out["sites"][0]["canonical_center_xy_px"], [50.0, 50.0])
        self.assertEqual(out["summary"]["direct_valid_observations"], 3)
        self.assertTrue(out["sites"][0]["auto_gold_site"])

    def test_new_circle_and_prefirst_are_not_physical_labels(self):
        out = run(result(), result(component(1)), result(component(1), component(2, 100)))
        self.assertEqual(len(out["sites"]), 2)
        new = out["sites"][1]
        self.assertEqual(new["first_direct_valid_frame"], 2)
        self.assertEqual(new["first_confident_annotation_frame"], 2)
        self.assertIsNone(new["last_confident_marker_absence_frame"])
        self.assertEqual(new["transition_interval"]["status"], "LEFT_BOUND_NOT_ESTABLISHED")
        rows = [r for r in out["observations"] if r["site_id"] == new["site_id"]]
        self.assertEqual([r["status"] for r in rows], ["PRE_FIRST_CONFIDENT_ANNOTATION"] * 2 + ["DIRECT_VALID"])
        self.assertTrue(all(r["physical_label"] == "NOT_INFERRED" for r in rows))

    def test_disappearance_never_propagates_positive(self):
        out = run(result(component(1)), result(), result(), result(component(1)))
        self.assertEqual([r["status"] for r in out["observations"]], [
            "DIRECT_VALID", "PERSISTENCE_EXPECTED_UNRESOLVED",
            "PERSISTENCE_EXPECTED_UNRESOLVED", "DIRECT_VALID"])
        self.assertEqual(out["summary"]["unexpected_graphical_disappearance_count"], 1)
        self.assertEqual(out["summary"]["negative_labels_created"], 0)

    def test_ambiguous_component_support_requires_existing_site(self):
        ambiguous = component(3, classification=a0.AMBIGUOUS)
        out = run(result(ambiguous, footprints={3: {100, 101, 102}}),
                  result(component(1), footprints={1: {100, 101}}),
                  result(ambiguous, footprints={3: {100, 101, 102}}))
        self.assertEqual(out["summary"]["auto_silver_observations"], 1)
        self.assertEqual(out["observations"][0]["status"], "PRE_FIRST_CONFIDENT_ANNOTATION")
        self.assertEqual(out["candidate_components"][0]["temporal_classification"], "POTENTIAL_NEW_SITE_UNRESOLVED")
        self.assertEqual(out["candidate_components"][-1]["temporal_classification"], "EXPLAINED_BY_KNOWN_SITE")

    def test_two_known_sites_in_overlap_are_preserved_without_new_site(self):
        out = run(result(component(1), component(2, 70), footprints={1: {100, 101}, 2: {200, 201}}),
                  result(component(9, classification=a0.AMBIGUOUS, box=[38, 38, 82, 62]),
                         footprints={9: {100, 101, 200, 201, 300}}))
        self.assertEqual(len(out["sites"]), 2)
        self.assertEqual(out["summary"]["auto_silver_observations"], 2)
        candidate = out["candidate_components"][-1]
        self.assertEqual(candidate["temporal_classification"], "EXPLAINED_BY_MULTIPLE_KNOWN_SITES")
        self.assertEqual(candidate["overlap_status"], "OVERLAP_WITH_KNOWN_TRACKS")
        self.assertTrue(candidate["potential_additional_site_unresolved"])
        self.assertEqual(candidate["classification"], a0.AMBIGUOUS)

    def test_small_component_never_becomes_silver_or_negative(self):
        out = run(result(component(1)), result(component(2, classification=a0.SMALL)))
        self.assertEqual(out["summary"]["auto_silver_observations"], 0)
        self.assertEqual(out["observations"][-1]["status"], "PERSISTENCE_EXPECTED_UNRESOLVED")
        self.assertEqual(out["candidate_components"][-1]["supported_site_ids"], [])
        self.assertEqual(out["summary"]["small_components"], 1)

    def test_bbox_upper_boundary_is_exclusive(self):
        out = run(result(component(1)), result(component(2, classification=a0.AMBIGUOUS,
                                                       box=[40, 40, 50, 60])))
        self.assertEqual(out["summary"]["auto_silver_observations"], 0)
        self.assertEqual(out["observations"][-1]["status"], "PERSISTENCE_EXPECTED_UNRESOLVED")

    def test_bbox_lower_boundary_alone_is_insufficient(self):
        out = run(result(component(1)), result(component(2, classification=a0.AMBIGUOUS,
                                                       box=[50, 50, 60, 60])))
        self.assertEqual(out["summary"]["auto_silver_observations"], 0)
        self.assertEqual(out["candidate_components"][-1]["known_site_bbox_proximity"]
                         ["containing_canonical_center_site_ids"], [out["sites"][0]["site_id"]])

    def test_enclosing_bbox_with_no_actual_anchor_ink_stays_unresolved(self):
        out = run(result(component(1), footprints={1: {100, 101, 102}}),
                  result(component(2, classification=a0.AMBIGUOUS, box=[0, 0, 100, 100]),
                         footprints={2: {200, 201, 202, 203}}))
        self.assertEqual(out["summary"]["auto_silver_observations"], 0)
        self.assertEqual(out["observations"][-1]["status"], "PERSISTENCE_EXPECTED_UNRESOLVED")
        candidate = out["candidate_components"][-1]
        self.assertEqual(candidate["temporal_classification"], "POTENTIAL_NEW_SITE_UNRESOLVED")
        self.assertEqual(candidate["supported_site_ids"], [])
        self.assertEqual(len(candidate["known_site_bbox_proximity"]["containing_canonical_center_site_ids"]), 1)

    def test_complete_anchor_subset_is_required_without_fractional_threshold(self):
        out = run(result(component(1), footprints={1: {100, 101, 102}}),
                  result(component(2, classification=a0.AMBIGUOUS), footprints={2: {100, 101, 103}}),
                  result(component(3, classification=a0.AMBIGUOUS), footprints={3: {100, 101, 102, 103}}))
        self.assertEqual([r["status"] for r in out["observations"]], [
            "DIRECT_VALID", "PERSISTENCE_EXPECTED_UNRESOLVED", "TEMPORAL_SUPPORTED_AMBIGUOUS"])
        self.assertEqual(out["sites"][0]["first_direct_chroma_footprint_pixel_count"], 3)
        self.assertEqual(len(out["sites"][0]["first_direct_chroma_footprint_sha256"]), 64)
        json.dumps(out, allow_nan=False)
        self.assertNotIn("_component_pixels", json.dumps(out))

    def test_footprint_anchor_never_updates_to_later_direct_ink(self):
        out = run(result(component(1), footprints={1: {100, 101}}),
                  result(component(2, 51), footprints={2: {200, 201}}),
                  result(component(3, classification=a0.AMBIGUOUS), footprints={3: {200, 201, 202}}),
                  result(component(4, classification=a0.AMBIGUOUS), footprints={4: {100, 101, 202}}))
        self.assertEqual([r["status"] for r in out["observations"]][-2:], [
            "PERSISTENCE_EXPECTED_UNRESOLVED", "TEMPORAL_SUPPORTED_AMBIGUOUS"])

    def test_first_direct_without_footprint_cannot_acquire_anchor_later(self):
        out = run(result(component(1)), result(component(2), footprints={2: {100, 101}}),
                  result(component(3, classification=a0.AMBIGUOUS), footprints={3: {100, 101, 102}}))
        self.assertEqual(out["summary"]["auto_silver_observations"], 0)
        self.assertIsNone(out["sites"][0]["first_direct_chroma_footprint_sha256"])

    def test_explicit_last_global_blank_bounds_documentary_appearance_only(self):
        out = run(result(colored_pixel_count=0), result(colored_pixel_count=0),
                  result(component(1, classification=a0.SMALL)), result(component(2)))
        site = out["sites"][0]
        self.assertEqual(site["last_confident_marker_absence_frame"], 1)
        self.assertEqual(site["last_confident_marker_absence_raw_sha256"], HASH)
        self.assertEqual(site["transition_interval"]["lower_frame_exclusive"], 1)
        self.assertEqual(site["transition_interval"]["upper_frame_inclusive"], 3)
        self.assertEqual(site["transition_interval"]["duration_s"], 2.36)
        self.assertEqual(site["transition_interval"]["status"], "DOCUMENTARY_BRACKET")
        self.assertEqual(out["summary"]["negative_labels_created"], 0)

    def test_unspecified_or_nonzero_chroma_does_not_establish_absence(self):
        for blank in (result(), result(colored_pixel_count=4), result(colored_pixel_count=False)):
            with self.subTest(blank=blank):
                out = run(blank, result(component(1)))
                self.assertIsNone(out["sites"][0]["last_confident_marker_absence_frame"])

    def test_footprint_schema_rejects_empty_incomplete_and_noninteger_maps(self):
        for footprints in ({1: set()}, {}, {1: {True}}, {1: {-1}}):
            with self.subTest(footprints=footprints), self.assertRaises(tracking.TrackingError):
                run(result(component(1), footprints=footprints))

    def test_two_pixel_inclusive_association(self):
        out = run(result(component(1)), result(component(2, 52)))
        self.assertEqual(len(out["sites"]), 1)
        self.assertEqual(out["summary"]["direct_valid_observations"], 2)

    def test_candidate_in_two_sites_is_conflict_not_nearest_rescue(self):
        out = run(result(component(1, 50), component(2, 53)), result(component(3, 51.1)))
        self.assertEqual(len(out["sites"]), 2)
        self.assertEqual(out["summary"]["conflict_records"], 2)
        self.assertEqual(out["summary"]["valid_identity_conflict_components"], 1)
        self.assertTrue(all(not s["auto_gold_site"] for s in out["sites"]))
        self.assertIsNone(out["component_site_links"][-1]["site_id"])
        self.assertEqual(len(out["component_site_links"][-1]["candidate_site_ids"]), 2)

    def test_two_components_competing_for_site_are_both_unassigned(self):
        out = run(result(component(1)), result(component(2, 49), component(3, 51)))
        self.assertEqual(out["summary"]["unique_sites"], 1)
        self.assertEqual(out["summary"]["conflict_records"], 1)
        self.assertTrue(all(r["site_id"] is None for r in out["component_site_links"][1:]))

    def test_transitive_drift_does_not_move_anchor(self):
        out = run(result(component(1, 50)), result(component(2, 51.9)), result(component(3, 53.8)))
        self.assertEqual(len(out["sites"]), 2)
        self.assertEqual(out["sites"][0]["canonical_center_xy_px"], [50, 50.0])
        self.assertEqual(out["sites"][0]["direct_observation_count"], 2)
        self.assertEqual(out["sites"][1]["first_direct_valid_frame"], 2)

    def test_nearby_same_frame_births_are_conflicts_not_two_sites(self):
        out = run(result(component(1, 50), component(2, 52)))
        self.assertEqual(out["summary"]["unique_sites"], 0)
        self.assertEqual(out["summary"]["valid_identity_conflict_components"], 2)
        self.assertEqual(out["summary"]["site_frame_records"], 0)
        self.assertTrue(all(c["temporal_classification"] == "CONFLICT" for c in out["candidate_components"]))

    def test_birth_near_matched_observation_conflicts_with_established_site(self):
        out = run(result(component(1, 50)), result(component(2, 51.9), component(3, 53.8)))
        self.assertEqual(len(out["sites"]), 1)
        self.assertEqual(out["summary"]["valid_identity_conflict_components"], 2)
        self.assertEqual(out["summary"]["conflict_records"], 1)
        self.assertFalse(out["sites"][0]["auto_gold_site"])
        self.assertEqual(out["candidate_components"][-1]["same_frame_conflicting_component_ids"], [2])

    def test_identity_conflict_permanently_excludes_auto_gold(self):
        out = run(result(component(1)), result(component(2, 49), component(3, 51)), result(component(4)))
        self.assertEqual(out["observations"][-1]["status"], "DIRECT_VALID")
        self.assertFalse(out["sites"][0]["auto_gold_site"])
        self.assertEqual(out["sites"][0]["conflict_frames"], [1])

    def test_deterministic_identity_and_order_under_component_permutation(self):
        a, b = component(9, 50), component(2, 80)
        first = run(result(a, b))
        second = run(result(b, a))
        self.assertEqual(first, second)
        self.assertEqual(len({s["site_id"] for s in first["sites"]}), 2)

    def test_source_isolation_and_experimental_time(self):
        first = run(result(component(1)), result(component(1)), source="ESM3")
        second = run(result(component(1)), result(component(1)), source="ESM6")
        self.assertNotEqual(first["sites"][0]["site_id"], second["sites"][0]["site_id"])
        self.assertEqual(first["frames"][1]["experimental_time_s"], -24.78)
        self.assertEqual(second["frames"][1]["experimental_time_s"], -33.04)
        self.assertEqual(first["frames"][1]["elapsed_time_s"], 1.18)

    def test_forbidden_sources_and_wrong_acquisition_rejected(self):
        for source in ("ESM1", "ESM2", "ESM4", "ESM5", "UNKNOWN"):
            with self.subTest(source=source), self.assertRaises(tracking.TrackingError):
                tracking.TemporalTracker(source, ACQUISITION, 1)
        with self.assertRaises(tracking.TrackingError):
            tracking.TemporalTracker("ESM3", "top_down_parallel", 1)

    def test_frame_order_duplicate_and_outside_coverage_rejected(self):
        tracker = tracking.TemporalTracker("ESM3", ACQUISITION, 1)
        for index in (1, -1, True):
            with self.subTest(index=index), self.assertRaises(tracking.TrackingError):
                tracker.add_frame(index, result(), HASH)
        tracker.add_frame(0, result(), HASH)
        for index in (0, 1):
            with self.subTest(index=index), self.assertRaises(tracking.TrackingError):
                tracker.add_frame(index, result(), HASH)

    def test_duplicate_component_ids_and_nonfinite_coordinates_rejected(self):
        for data in (result(component(1), component(1, 80)), result(component(1, float("nan"))),
                     result(component(1, True)), result(component(1, float("inf")))):
            with self.subTest(data=data), self.assertRaises(tracking.TrackingError):
                run(data)

    def test_original_component_is_unchanged_and_metadata_is_detached(self):
        original = result(component(1), component(2, 100, classification=a0.AMBIGUOUS))
        before = copy.deepcopy(original)
        out = run(original)
        self.assertEqual(original, before)
        for original_component, candidate in zip(before["components"], out["candidate_components"]):
            for key, value in original_component.items():
                self.assertEqual(candidate[key], value)
        out["candidate_components"][1]["reasons"].append("changed externally")
        self.assertEqual(original, before)

    def test_invalid_frame_accounted_before_and_after_first_valid(self):
        tracker = tracking.TemporalTracker("ESM3", ACQUISITION, 3)
        tracker.add_frame(0, None, None, "DECODE_FAILED")
        tracker.add_frame(1, result(component(1)), HASH)
        tracker.add_frame(2, None, HASH, "INTEGRITY_FAILED")
        out = tracker.finish()
        self.assertEqual([r["status"] for r in out["observations"]], ["INVALID_FRAME", "DIRECT_VALID", "INVALID_FRAME"])
        self.assertTrue(out["summary"]["frame_accounting_complete"])
        self.assertFalse(out["summary"]["frame_coverage_complete"])
        self.assertEqual(out["summary"]["frames_processed"], 1)

    def test_partial_finish_is_explicit_not_complete(self):
        tracker = tracking.TemporalTracker("ESM3", ACQUISITION, 3)
        tracker.add_frame(0, result(component(1)), HASH)
        out = tracker.finish()
        self.assertFalse(out["summary"]["frame_accounting_complete"])
        self.assertEqual(out["summary"]["frames_accounted"], 1)
        with self.assertRaises(tracking.TrackingError):
            tracker.add_frame(1, result(), HASH)
        with self.assertRaises(tracking.TrackingError):
            tracker.finish()

    def test_processed_provenance_and_counts_fail_closed(self):
        for bad_hash in (None, "", "A" * 64, "x" * 64):
            tracker = tracking.TemporalTracker("ESM3", ACQUISITION, 1)
            with self.subTest(hash=bad_hash), self.assertRaises(tracking.TrackingError):
                tracker.add_frame(0, result(), bad_hash)
        bad = result(component(1))
        bad["valid_circle_count"] = 0
        with self.assertRaises(tracking.TrackingError):
            run(bad)

    def test_failed_frame_rejects_detector_output(self):
        tracker = tracking.TemporalTracker("ESM3", ACQUISITION, 1)
        with self.assertRaises(tracking.TrackingError):
            tracker.add_frame(0, result(component(1)), HASH, "DECODE_FAILED")

    def test_no_manual_review_hough_delta_or_physical_events(self):
        out = run(result(component(1)))
        for field in ("human_review_used", "hough_executed", "temporal_delta_executed"):
            self.assertIs(out["summary"][field], False)
        self.assertEqual(out["summary"]["physical_events_inferred"], 0)
        self.assertEqual(set(tracking.OBSERVATION_STATUSES), {
            "DIRECT_VALID", "TEMPORAL_SUPPORTED_AMBIGUOUS", "PERSISTENCE_EXPECTED_UNRESOLVED",
            "PRE_FIRST_CONFIDENT_ANNOTATION", "CONFLICT", "INVALID_FRAME"})
        json.dumps(out, allow_nan=False)

    def test_every_site_has_exactly_one_record_per_accounted_frame(self):
        out = run(result(), result(component(1), footprints={1: {100, 101}}),
                  result(component(1), component(2, 90), footprints={1: {100, 101}, 2: {200, 201}}),
                  result(component(3, classification=a0.AMBIGUOUS, box=[30, 30, 110, 70]),
                         footprints={3: {100, 101, 200, 201, 300}}))
        keys = [(row["site_id"], row["frame_index"]) for row in out["observations"]]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), len(out["sites"]) * len(out["frames"]))
        self.assertEqual(out["summary"]["direct_valid_observations"], 3)
        self.assertEqual(out["summary"]["auto_silver_observations"], 2)
        self.assertEqual(out["summary"]["pre_annotation_records"], 3)


@unittest.skipUnless(NUMERICAL, "optional NumPy/SciPy unavailable; pure synthetic A0 fixtures only")
class FrozenA0SyntheticTests(unittest.TestCase):
    def extract(self, centers, with_support=False):
        import numpy as np
        u = np.full((64, 96), 128, dtype="uint8")
        v = np.full(u.shape, 128, dtype="uint8")
        yy, xx = np.indices(u.shape)
        for cx, cy in centers:
            u[np.abs(np.hypot(xx - cx, yy - cy) - 5.5) <= 0.9] = 180
        detector = a0.extract_graphical_markers(u, v, 192, 128, A0_CONFIG)
        if with_support:
            detector["_component_pixels"] = tracking.component_support_from_chroma(u, v, 192, 128, detector)
        return detector

    def test_isolated_circle_with_frozen_detector_becomes_one_direct_site(self):
        detector = self.extract([(25, 25)])
        self.assertEqual(detector["valid_circle_count"], 1)
        out = run(detector)
        self.assertEqual(out["summary"]["unique_auto_gold_sites"], 1)
        self.assertEqual(out["summary"]["direct_valid_observations"], 1)

    def test_two_circles_with_frozen_detector_become_two_sites(self):
        detector = self.extract([(25, 25), (65, 25)])
        self.assertEqual(detector["valid_circle_count"], 2)
        out = run(detector)
        self.assertEqual(out["summary"]["unique_auto_gold_sites"], 2)
        self.assertEqual(out["summary"]["direct_valid_observations"], 2)

    def test_actual_synthetic_ink_overlap_supports_complete_anchor(self):
        isolated = self.extract([(25, 25)], with_support=True)
        overlap = self.extract([(25, 25), (31, 25)], with_support=True)
        self.assertEqual(isolated["valid_circle_count"], 1)
        self.assertEqual(overlap["ambiguous_component_count"], 1)
        self.assertTrue(isolated["_component_pixels"][1].issubset(overlap["_component_pixels"][1]))
        out = run(isolated, overlap)
        self.assertEqual(out["summary"]["auto_silver_observations"], 1)
        self.assertEqual(out["sites"][0]["first_direct_chroma_footprint_pixel_count"],
                         isolated["components"][0]["area_px"])
        self.assertNotIn("_component_pixels", json.dumps(out))

    def test_helper_checks_counts_areas_boxes_and_native_shape_against_a0(self):
        import numpy as np
        u = np.full((64, 96), 128, dtype="uint8")
        v = np.full(u.shape, 128, dtype="uint8")
        u[20:23, 20:23] = 180
        original = a0.extract_graphical_markers(u, v, 192, 128, A0_CONFIG)
        good = tracking.component_support_from_chroma(u, v, 192, 128, original)
        self.assertEqual(len(good[1]), 36)
        cases = []
        bad = copy.deepcopy(original)
        bad["components"][0]["area_px"] += 1
        cases.append(bad)
        bad = copy.deepcopy(original)
        bad["components"][0]["bbox_xyxy"][0] += 1
        cases.append(bad)
        bad = copy.deepcopy(original)
        bad["colored_pixel_count"] += 1
        cases.append(bad)
        bad = copy.deepcopy(original)
        bad["native_width"] = 194
        cases.append(bad)
        for bad in cases:
            with self.subTest(bad=bad), self.assertRaises(tracking.TrackingError):
                tracking.component_support_from_chroma(u, v, 192, 128, bad)

    def test_explicit_blank_from_immutable_detector_provides_lower_bound(self):
        out = run(self.extract([], with_support=True), self.extract([(25, 25)], with_support=True))
        self.assertEqual(out["sites"][0]["last_confident_marker_absence_frame"], 0)
        self.assertEqual(out["sites"][0]["transition_interval"]["duration_s"], 1.18)


if __name__ == "__main__":
    unittest.main()
