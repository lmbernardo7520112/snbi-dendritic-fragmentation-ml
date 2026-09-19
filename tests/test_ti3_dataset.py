"""Synthetic textual fixtures only: no native files, arrays or project results."""

import copy
import unittest

from snbi_fragmentation.ti3_dataset import (
    ACQUISITIONS, DIMENSIONS, FRAME_SPLITS, SPLITS, DatasetContractError,
    build_manifest, patch_xyxy, support_xyxy, validate_manifest,
)


def pilot_fixture():
    images = []
    for source, frame in FRAME_SPLITS:
        w, h = DIMENSIONS[source]
        images.append({
            "source_id": source, "frame_index": frame, "width": w, "height": h,
            "experiment_id": ACQUISITIONS[source], "pixel_format": "yuv420p", "bit_depth": 8,
            "frame_bytes": w * h * 3 // 2, "image_sha256": "a" * 64,
            "experimental_time_s": (-25.96 if source == "ESM1" else -34.22) + 1.18 * frame,
            "path": f"data/derived/ti2-pilot/{source}-{frame:04d}.raw",
            "planes": [{"name": "Y", "offset": 0, "bytes": w * h, "width": w, "height": h},
                       {"name": "U"}, {"name": "V"}],
        })
    return images


def add_site(sites, ledger, site_id, frame, x, y, source="ESM3", later=()):
    acquisition = ACQUISITIONS["ESM1" if source == "ESM3" else "ESM4"]
    observations = []
    for index, (observation_frame, ox, oy) in enumerate([(frame, x, y)] + list(later)):
        observation_id = f"{site_id}-observation-{index}"
        observations.append({"observation_id": observation_id, "frame_index": observation_frame,
                             "center_x": ox, "center_y": oy})
        ledger.append({"observation_id": observation_id, "annotation_site_id": site_id,
                       "source_id": source, "acquisition_id": acquisition,
                       "frame_index": observation_frame, "center_x": ox, "center_y": oy,
                       "new_supervision": "POSITIVE"})
    sites.append({"annotation_site_id": site_id, "source_id": source,
                  "acquisition_id": acquisition, "observations": observations,
                  "representative": {"center_x": 1200, "center_y": 900},
                  "first_confident_observation": {
                      "observation_id": observations[0]["observation_id"], "frame_index": frame}})


def fixture():
    sites, ledger = [], []
    add_site(sites, ledger, "train-site", 73, 200, 300)
    add_site(sites, ledger, "dev-site", 219, 500, 500)
    add_site(sites, ledger, "final-site", 293, 800, 700)
    return sites, ledger, pilot_fixture()


def ignore_row(observation_id, box, source="ESM3", frame=293):
    return {"observation_id": observation_id, "source_id": source,
            "acquisition_id": ACQUISITIONS["ESM1" if source == "ESM3" else "ESM4"],
            "frame_index": frame, "new_supervision": "IGNORE", "bbox_xyxy": list(box)}


class SyntheticDatasetContractTests(unittest.TestCase):
    def test_balanced_sealed_plan_is_deterministic_and_does_not_mutate_inputs(self):
        inputs = fixture()
        before = copy.deepcopy(inputs)
        first = build_manifest(*inputs)
        second = build_manifest(*inputs)
        self.assertEqual(first, second)
        self.assertEqual(inputs, before)
        self.assertEqual(first["state"], "PASS")
        self.assertTrue(validate_manifest(first))
        for split in SPLITS:
            self.assertEqual(first["split_counts"][split]["valid_positives"], 1)
            self.assertEqual(first["split_counts"][split]["selected_backgrounds"], 1)
        self.assertEqual(first["experimental_opens"], 0)
        self.assertEqual(first["ml_runs"], 0)

    def test_first_observation_own_coordinate_not_later_medoid(self):
        sites, ledger, images = fixture()
        sites.pop(0)
        ledger.pop(0)
        add_site(sites, ledger, "train-site", 73, 200.5, 300.49,
                 later=((146, 1100, 400),))
        result = build_manifest(sites, ledger, images)
        sample = next(s for s in result["positive_candidates"] if s["annotation_site_id"] == "train-site")
        self.assertEqual(sample["center_native_xy"], [201, 300])
        self.assertEqual(sample["published_center_xy"], [200.5, 300.49])
        self.assertEqual(sample["frame_index"], 73)
        self.assertTrue(validate_manifest(result))

    def test_documentary_support_uses_ceil_and_one_pixel_erosion(self):
        self.assertEqual(support_xyxy(1278, 1018), [5, 124, 1273, 864])
        self.assertEqual(support_xyxy(1278, 1012), [5, 123, 1273, 859])
        self.assertEqual(patch_xyxy(37, 156), [5, 124, 70, 189])

    def test_boundary_patch_is_not_padded_or_recentered(self):
        for center, expected in ((37, "VALID"), (36, "UNAVAILABLE")):
            with self.subTest(center=center):
                sites, ledger, images = fixture()
                sites[0]["observations"][0].update(center_x=center, center_y=156)
                ledger[0].update(center_x=center, center_y=156)
                result = build_manifest(sites, ledger, images)
                sample = next(s for s in result["positive_candidates"] if s["annotation_site_id"] == "train-site")
                self.assertEqual(sample["status"], expected)
                self.assertEqual(sample["center_x"], center)

    def test_cross_split_zone_boundary_contact_is_invalid_context(self):
        sites, ledger, images = fixture()
        sites[1]["observations"][0].update(center_x=267, center_y=300)
        ledger[1].update(center_x=267, center_y=300)
        result = build_manifest(sites, ledger, images)
        train = next(s for s in result["positive_candidates"] if s["annotation_site_id"] == "train-site")
        self.assertEqual(train["exclusion_reasons"], ["INVALID_CONTEXT"])
        self.assertEqual(train["conflicting_site_ids"], ["dev-site"])
        self.assertEqual(result["state"], "BLOCKED_SPLIT_SUPPORT")
        self.assertEqual(result["samples"], [])
        self.assertEqual(result["final_test_status"], "NOT_DEFINED_NOT_OPENED")
        with self.assertRaises(DatasetContractError):
            validate_manifest(result)

    def test_cross_split_zone_one_pixel_separation_is_permitted(self):
        sites, ledger, images = fixture()
        sites[1]["observations"][0].update(center_x=268, center_y=300)
        ledger[1].update(center_x=268, center_y=300)
        result = build_manifest(sites, ledger, images)
        self.assertTrue(all(p["status"] == "VALID" for p in result["positive_candidates"]))
        self.assertTrue(validate_manifest(result))

    def test_all_observed_centers_protect_other_splits(self):
        sites, ledger, images = fixture()
        sites.pop(1)
        ledger.pop(1)
        add_site(sites, ledger, "dev-site", 219, 500, 500, later=((293, 220, 300),))
        result = build_manifest(sites, ledger, images)
        train = next(s for s in result["positive_candidates"] if s["annotation_site_id"] == "train-site")
        self.assertIn("dev-site", train["conflicting_site_ids"])

    def test_same_split_sites_do_not_become_cross_split_conflicts(self):
        sites, ledger, images = fixture()
        add_site(sites, ledger, "train-neighbor", 146, 215, 310)
        result = build_manifest(sites, ledger, images)
        self.assertEqual(result["split_counts"]["TRAIN"]["valid_positives"], 2)
        self.assertEqual(result["split_counts"]["TRAIN"]["selected_backgrounds"], 2)
        self.assertTrue(validate_manifest(result))

    def test_unknown_region_is_diagnostic_not_a_positive_exclusion(self):
        sites, ledger, images = fixture()
        ledger.append(ignore_row("ambiguous-neighbor", [190, 290, 211, 311]))
        result = build_manifest(sites, ledger, images)
        positive = next(s for s in result["positive_candidates"] if s["annotation_site_id"] == "train-site")
        self.assertEqual(positive["status"], "VALID")
        self.assertEqual(positive["ignore_diagnostic_ids"], ["ambiguous-neighbor"])
        self.assertTrue(validate_manifest(result))

    def test_ignore_from_any_frame_blocks_background_and_never_becomes_negative(self):
        sites, ledger, images = fixture()
        for source in ("ESM3", "ESM6"):
            ledger.append(ignore_row(f"opaque-{source}", [0, 0, 1280, 1024], source, frame=0))
        result = build_manifest(sites, ledger, images)
        self.assertEqual(result["state"], "BLOCKED_BACKGROUND_SUPPORT")
        self.assertEqual(result["background_deficits"], {s: 1 for s in SPLITS})
        self.assertEqual(result["samples"], [])
        self.assertEqual(result["final_test_status"], "NOT_DEFINED_NOT_OPENED")
        self.assertTrue(all(p["status"] == "VALID" for p in result["positive_candidates"]))

    def test_missing_fco_observation_and_unapproved_fco_frame_fail_closed(self):
        for corruption in ("missing", "zero", "duplicate"):
            with self.subTest(corruption=corruption):
                sites, ledger, images = fixture()
                if corruption == "missing":
                    sites[0]["first_confident_observation"]["observation_id"] = "not-observed"
                elif corruption == "zero":
                    sites[0]["first_confident_observation"]["frame_index"] = 0
                    sites[0]["observations"][0]["frame_index"] = 0
                else:
                    sites[0]["observations"].append({
                        "observation_id": "duplicate-first-time", "frame_index": 73,
                        "center_x": 200, "center_y": 300})
                with self.assertRaises(DatasetContractError):
                    build_manifest(sites, ledger, images)

    def test_duplicate_site_and_missing_positive_ledger_fail_closed(self):
        for corruption in ("duplicate", "missing-positive"):
            sites, ledger, images = fixture()
            if corruption == "duplicate":
                sites.append(copy.deepcopy(sites[0]))
            else:
                ledger.pop(0)
            with self.assertRaises(DatasetContractError):
                build_manifest(sites, ledger, images)

    def test_pilot_shape_path_plane_and_source_are_exact(self):
        for field, value in (("width", 1280), ("path", "data/arbitrary.raw"),
                             ("pixel_format", "rgb24"), ("source_id", "ESM2")):
            with self.subTest(field=field):
                sites, ledger, images = fixture()
                images[0][field] = value
                with self.assertRaises(DatasetContractError):
                    build_manifest(sites, ledger, images)

    def test_guard_rejects_open_final_input_before_any_materialization(self):
        for level in ("manifest", "source", "sample"):
            result = build_manifest(*fixture())
            if level == "manifest":
                result["input_opened"] = True
            else:
                key = "source_inventory" if level == "source" else "samples"
                next(s for s in result[key] if s["split"] == "FINAL_TEST")["input_opened"] = True
            with self.assertRaises(DatasetContractError):
                validate_manifest(result)

    def test_guard_rejects_source_split_context_center_mapping_and_target_changes(self):
        changes = (("source_id", "ESM2"), ("split", "DEVELOPMENT"),
                   ("context_group_id", "different-group"), ("center_x", 201),
                   ("mapping_offset_xy", [1, 0]), ("target", "EXACT_PHYSICAL_ONSET"),
                   ("label", "PHYSICAL_NEGATIVE"), ("input_hash_if_opened", "a" * 64))
        for field, value in changes:
            with self.subTest(field=field):
                result = build_manifest(*fixture())
                positive = next(s for s in result["samples"] if s["annotation_site_id"] == "train-site")
                positive[field] = value
                with self.assertRaises(DatasetContractError):
                    validate_manifest(result)

    def test_guard_rejects_duplicated_sites_and_sample_ids(self):
        for corruption in ("site", "sample"):
            result = build_manifest(*fixture())
            if corruption == "site":
                result["site_assignments"].append(copy.deepcopy(result["site_assignments"][0]))
            else:
                result["samples"].append(copy.deepcopy(result["samples"][0]))
            with self.assertRaises(DatasetContractError):
                validate_manifest(result)

    def test_guard_rejects_false_exclusion_and_parameter_changes(self):
        for corruption in ("parameter", "exclusion", "missing-candidate"):
            result = build_manifest(*fixture())
            if corruption == "parameter":
                result["parameters"]["registration_guard_px"] = 2
            elif corruption == "exclusion":
                result["positive_candidates"][0]["status"] = "UNAVAILABLE"
            else:
                result["positive_candidates"].pop(0)
            with self.assertRaises(DatasetContractError):
                validate_manifest(result)

    def test_required_sample_schema_is_present_and_all_inputs_remain_unopened(self):
        result = build_manifest(*fixture())
        required = {"sample_id", "annotation_site_id_or_background_id", "source_id", "frame_index",
                    "experimental_time_s", "center_x", "center_y", "patch_radius_px", "patch_side_px",
                    "label", "split", "context_group_id", "provenance", "input_hash_if_opened"}
        for sample in result["samples"]:
            self.assertTrue(required.issubset(sample))
            self.assertFalse(sample["input_opened"])
            self.assertIsNone(sample["input_hash_if_opened"])


if __name__ == "__main__":
    unittest.main()
