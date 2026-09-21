"""Synthetic-only contracts for the pure dense multimodal corpus core."""

import ast
from copy import deepcopy
import hashlib
import inspect
import unittest

from snbi_fragmentation import study2b_corpus as corpus

try:
    import numpy as np
    from scipy import ndimage  # noqa: F401: explicit availability, no optional silent pass
except ImportError:
    np = None


def synthetic_site(sid="synthetic-site", source="ESM3", point=None):
    structural = corpus.SOURCE_MAP[source]
    return {"site_id": sid, "source_id": source,
            "acquisition_id": corpus.ACQUISITIONS[structural],
            "canonical_center_xy_px": point or [300.25, 400.5],
            "auto_gold_site": True, "has_identity_conflict": False,
            "source_provenance_complete": True, "source_sha256": "a" * 64}


def synthetic_observation(site, frame=0, state="DIRECT_VALID"):
    return {"site_id": site["site_id"], "source_id": site["source_id"],
            "acquisition_id": site["acquisition_id"], "frame_index": frame,
            "canonical_center_xy_px": list(site["canonical_center_xy_px"]),
            "source_sha256": site["source_sha256"], "status": state,
            "experimental_time_s": -25.96 + 1.18 * frame, "elapsed_time_s": 1.18 * frame,
            "raw_frame_sha256": "b" * 64, "component_ids": [],
            "physical_label": "NOT_INFERRED"}


def synthetic_component(cid=1, classification="AMBIGUOUS_OR_NONCIRCULAR",
                        temporal="POTENTIAL_NEW_SITE_UNRESOLVED", box=None):
    return {"source_id": "ESM3", "acquisition_id": "bottom_up_anti_parallel",
            "frame_index": 0, "component_id": cid, "bbox_xyxy": box or [500, 500, 510, 510],
            "classification": classification, "temporal_classification": temporal,
            "supported_site_ids": [], "potential_additional_site_unresolved": True}


def synthetic_metrics(components):
    values = {k: 0 for k in corpus.METRIC_NAMES}
    mapping = {"POTENTIAL_NEW_SITE_UNRESOLVED": "AMBIGUOUS_UNSUPPORTED_BY_KNOWN_SITE",
               "EXPLAINED_BY_KNOWN_SITE": "AMBIGUOUS_EXPLAINED_BY_ONE_KNOWN_SITE",
               "EXPLAINED_BY_MULTIPLE_KNOWN_SITES": "AMBIGUOUS_EXPLAINED_BY_MULTIPLE_KNOWN_SITES"}
    for comp in components:
        if comp["classification"] == "AMBIGUOUS_OR_NONCIRCULAR":
            values["AMBIGUOUS_COMPONENTS_TOTAL"] += 1
            values[mapping[comp["temporal_classification"]]] += 1
        elif comp["classification"] == "SMALL_COMPONENT":
            values["SMALL_COMPONENTS_TOTAL"] += 1
    values["NON_VALID_COMPONENTS_TOTAL"] = values["AMBIGUOUS_COMPONENTS_TOTAL"] + values["SMALL_COMPONENTS_TOTAL"]
    values["UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS"] = values["AMBIGUOUS_UNSUPPORTED_BY_KNOWN_SITE"] + values["SMALL_COMPONENTS_TOTAL"]
    return values


def synthetic_plan(sites=None, observations=None, components=None):
    sites = sites if sites is not None else [synthetic_site()]
    observations = observations if observations is not None else [synthetic_observation(s) for s in sites]
    components = components if components is not None else []
    return corpus.build_plan(sites, observations, components, synthetic_metrics(components))


class CorpusPlanningTests(unittest.TestCase):
    def test_fixed_canonical_center_and_half_up_rounding(self):
        site = synthetic_site(point=[300.5, 400.49])
        obs = [synthetic_observation(site, i) for i in [8, 0, 6]]
        plan = synthetic_plan([site], obs)
        self.assertEqual([r["frame_index"] for r in plan["records"]], [0, 6, 8])
        self.assertEqual({tuple(r["patch_xyxy"]) for r in plan["records"]}, {(269, 368, 334, 433)})
        self.assertEqual({tuple(r["canonical_center_xy_px"]) for r in plan["records"]}, {(300.5, 400.49)})

    def test_all_four_tiers_and_weight_denominator_preserved(self):
        site = synthetic_site()
        obs = [synthetic_observation(site, i, state) for i, state in enumerate(corpus.TIERS)]
        records = synthetic_plan([site], obs)["records"]
        self.assertEqual({r["supervision_tier"] for r in records}, set(corpus.TIERS.values()))
        self.assertTrue(all(r["site_observation_count"] == 4 for r in records))
        self.assertTrue(all(r["site_supervised_observation_count"] == 2 for r in records))
        self.assertTrue(all(r["candidate_equal_site_weight"] == 0.5 for r in records))
        self.assertTrue(all(r["annotation_provenance"]["physical_label"] == "NOT_INFERRED" for r in records))

    def test_group_never_depends_on_frame_or_tier(self):
        site = synthetic_site()
        obs = [synthetic_observation(site, 0), synthetic_observation(site, 1, "TEMPORAL_SUPPORTED_AMBIGUOUS")]
        records = synthetic_plan([site], obs)["records"]
        self.assertEqual({r["group_id"] for r in records}, {"bottom_up_anti_parallel|synthetic-site"})
        self.assertEqual(len({r["pair_id"] for r in records}), 2)

    def test_duplicate_site_frame_rejected(self):
        site = synthetic_site(); obs = synthetic_observation(site)
        with self.assertRaisesRegex(corpus.CorpusContractError, "duplicate site/frame"):
            synthetic_plan([site], [obs, deepcopy(obs)])

    def test_duplicate_sites_rejected(self):
        site = synthetic_site()
        with self.assertRaises(corpus.CorpusContractError):
            synthetic_plan([site, deepcopy(site)])

    def test_unknown_tier_denied_instead_of_becoming_negative(self):
        site = synthetic_site()
        with self.assertRaisesRegex(corpus.CorpusContractError, "observation state"):
            synthetic_plan([site], [synthetic_observation(site, state="NEGATIVE")])

    def test_changed_observation_center_cannot_move_crop(self):
        site = synthetic_site(); obs = synthetic_observation(site)
        obs["canonical_center_xy_px"][0] += 1
        with self.assertRaisesRegex(corpus.CorpusContractError, "canonical center"):
            synthetic_plan([site], [obs])

    def test_cross_acquisition_observation_denied(self):
        site = synthetic_site(); obs = synthetic_observation(site)
        obs["acquisition_id"] = "top_down_parallel"
        with self.assertRaises(corpus.CorpusContractError):
            synthetic_plan([site], [obs])

    def test_canonical_metrics_required_and_old_field_refused(self):
        site = synthetic_site(); obs = synthetic_observation(site)
        metrics = synthetic_metrics([])
        metrics["potential_new_site_unresolved_components"] = 0
        with self.assertRaisesRegex(corpus.CorpusContractError, "seven reconciled"):
            corpus.build_plan([site], [obs], [], metrics)

    def test_ambiguous_population_and_small_arithmetic_checked(self):
        components = [synthetic_component(1), synthetic_component(2, temporal="EXPLAINED_BY_KNOWN_SITE"),
                      synthetic_component(3, temporal="EXPLAINED_BY_MULTIPLE_KNOWN_SITES"),
                      synthetic_component(4, classification="SMALL_COMPONENT")]
        plan = synthetic_plan(components=components)
        self.assertEqual(plan["canonical_metrics"]["NON_VALID_COMPONENTS_TOTAL"], 4)
        self.assertEqual(plan["canonical_metrics"]["UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS"], 2)
        metrics = synthetic_metrics(components); metrics["NON_VALID_COMPONENTS_TOTAL"] = 2
        site = synthetic_site()
        with self.assertRaisesRegex(corpus.CorpusContractError, "populations differ"):
            corpus.build_plan([site], [synthetic_observation(site)], components, metrics)

    def test_all_nonvalid_boxes_excluded_even_explained_or_false_boolean(self):
        components = [synthetic_component(1, temporal="EXPLAINED_BY_KNOWN_SITE"),
                      synthetic_component(2, classification="SMALL_COMPONENT")]
        for c in components:
            c["potential_additional_site_unresolved"] = False
        plan = synthetic_plan(components=components)
        self.assertEqual(len(plan["exclusion_metadata"]["frame_component_boxes"]["ESM1:0"]), 2)

    def test_valid_component_is_temporal_footprint_exclusion(self):
        c = synthetic_component(classification="VALID_GRAPHICAL_CIRCLE", temporal="RECIPROCAL_SINGLETON_CANONICAL_MATCH")
        box = synthetic_plan(components=[c])["exclusion_metadata"]["frame_component_boxes"]["ESM1:0"][0]
        self.assertEqual(box["exclusion_basis"], "KNOWN_SITE_TEMPORAL_COMPONENT_FOOTPRINT")

    def test_duplicate_components_rejected(self):
        component = synthetic_component()
        with self.assertRaisesRegex(corpus.CorpusContractError, "component identity"):
            synthetic_plan(components=[component, deepcopy(component)])

    def test_order_independent_of_ledger_input_order(self):
        a = synthetic_site("z"); b = synthetic_site("a"); c = synthetic_site("c", "ESM6")
        obs = [synthetic_observation(a, 1), synthetic_observation(c, 0), synthetic_observation(b, 0)]
        plan = synthetic_plan([a, b, c], obs)
        other = synthetic_plan([c, b, a], list(reversed(obs)))
        self.assertEqual(plan, other)
        self.assertEqual([(r["site_id"], r["frame_index"]) for r in plan["records"]], [("a", 0), ("z", 1), ("c", 0)])

    def test_missing_hash_and_nonfinite_time_rejected(self):
        site = synthetic_site()
        for field, value in [("raw_frame_sha256", ""), ("experimental_time_s", float("nan"))]:
            obs = synthetic_observation(site); obs[field] = value
            with self.assertRaises(corpus.CorpusContractError):
                synthetic_plan([site], [obs])

    def test_no_io_no_scientific_imports_or_decoder_calls(self):
        tree = ast.parse(inspect.getsource(corpus))
        forbidden = {"sklearn", "torch", "skimage", "subprocess", "os", "pathlib", "cv2"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertTrue(all(a.name.split(".")[0] not in forbidden for a in node.names))
            elif isinstance(node, ast.ImportFrom):
                self.assertNotIn((node.module or "").split(".")[0], forbidden)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"open", "eval", "exec", "compile", "__import__"})


@unittest.skipIf(np is None, "NumPy and SciPy required for synthetic native-support contracts")
class CorpusNativeSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        width, height = corpus.DIMENSIONS["ESM1"]
        n = width * height
        cls.y_s = (np.arange(n, dtype=np.uint32) % 251).astype(np.uint8).reshape(height, width)
        cls.y_r = (250 - cls.y_s).astype(np.uint8)
        cls.s = cls.y_s.tobytes() + bytes([128]) * (n // 2)
        cls.r = cls.y_r.tobytes() + bytes([200]) * (n // 2)

    def result(self, plan=None, raw=None, row_start=0, frame=0):
        plan = plan or synthetic_plan()
        return corpus.process_frame_pair(self.s if raw is None else raw, self.r, "ESM1", frame,
                                         plan["records_by_frame"].get(f"ESM1:{frame}", []),
                                         plan["exclusion_metadata"], row_start)

    def test_exact_65_square_paired_channel_order_and_hashes(self):
        result = self.result(row_start=9)
        pair, index = result["pairs"][0], result["index_records"][0]
        self.assertEqual(pair.shape, (2, 65, 65)); self.assertEqual(pair.dtype, np.dtype("uint8"))
        x0, y0, x1, y1 = index["patch_xyxy"]
        np.testing.assert_array_equal(pair[0], self.y_s[y0:y1, x0:x1])
        np.testing.assert_array_equal(pair[1], self.y_r[y0:y1, x0:x1])
        self.assertEqual(index["row_index"], 9)
        self.assertEqual(index["pair_sha256"], hashlib.sha256(pair.tobytes()).hexdigest())
        self.assertEqual(index["structural_patch_sha256"], hashlib.sha256(pair[0].tobytes()).hexdigest())
        self.assertEqual(index["solutal_patch_sha256"], hashlib.sha256(pair[1].tobytes()).hexdigest())

    def test_solutal_chroma_is_not_an_overlay(self):
        result = self.result()
        self.assertEqual(result["index_records"][0]["pair_status"], "VALID_PAIR")
        self.assertTrue(np.all(np.frombuffer(self.r, dtype=np.uint8)[self.y_r.size:] == 200))

    def test_structural_chroma_twenty_and_halo_fail_closed(self):
        width, height = corpus.DIMENSIONS["ESM1"]; n = width * height
        raw = bytearray(self.s)
        raw[n + (401 // 2) * (width // 2) + (300 // 2)] = 148
        result = self.result(raw=bytes(raw))
        self.assertEqual(result["pairs"], [])
        item = result["index_records"][0]
        self.assertEqual(item["pair_status"], "INVALID_STRUCTURAL_SUPPORT")
        self.assertEqual(item["support_disposition"], "GOLD_INVALID_SUPPORT")
        self.assertIsNone(item["row_index"]); self.assertIsNone(item["pair_sha256"])

    def test_chroma_nineteen_preserves_support(self):
        width, _ = corpus.DIMENSIONS["ESM1"]; n = self.y_s.size
        raw = bytearray(self.s); raw[n + (401 // 2) * (width // 2) + (300 // 2)] = 147
        self.assertEqual(self.result(raw=bytes(raw))["index_records"][0]["pair_status"], "VALID_PAIR")

    def test_out_of_raster_accounted_invalid_both_without_padding(self):
        plan = synthetic_plan([synthetic_site(point=[1280.0, 1000.0])])
        result = self.result(plan)
        self.assertEqual(result["pairs"], [])
        self.assertEqual(len(result["index_records"]), 1)
        record = result["index_records"][0]
        self.assertEqual(record["pair_status"], "INVALID_BOTH")
        self.assertEqual(record["center_x"], 1280)
        self.assertEqual(record["patch_xyxy"], [1248, 968, 1313, 1033])

    def test_top_band_and_erosion_admission_exact(self):
        top = corpus.support_xyxy(*corpus.DIMENSIONS["ESM1"])[1]
        bad = synthetic_plan([synthetic_site(point=[300, top + 31])])
        good = synthetic_plan([synthetic_site(point=[300, top + 32])])
        self.assertEqual(self.result(bad)["index_records"][0]["pair_status"], "INVALID_BOTH")
        self.assertEqual(self.result(good)["index_records"][0]["pair_status"], "VALID_PAIR")

    def test_incomplete_bytes_denied_without_salvage(self):
        with self.assertRaisesRegex(corpus.CorpusContractError, "complete immutable"):
            self.result(raw=self.s[:-1])

    def test_cross_source_and_temporal_mix_denied_before_bytes(self):
        for key, value in [("solutal_source_id", "ESM5"), ("structural_source_id", "ESM4"), ("frame_index", 1)]:
            plan = synthetic_plan(); plan["records"][0][key] = value
            with self.assertRaisesRegex(corpus.CorpusContractError, "mixing"):
                self.result(plan, raw=b"not inspected")

    def test_annotation_source_cannot_enter_native_path(self):
        with self.assertRaises(corpus.CorpusContractError):
            corpus.process_frame_pair(b"", b"", "ESM3", 0, [], {}, 0)
        with self.assertRaises(corpus.CorpusContractError):
            corpus.native_luminance_and_support(b"", "ESM6", structural=True)

    def test_changed_integer_crop_or_mapping_denied(self):
        for key, value in [("center_x", 301), ("mapping_offset_xy", [1, 0]), ("patch_side_px", 64)]:
            plan = synthetic_plan(); plan["records"][0][key] = value
            with self.assertRaisesRegex(corpus.CorpusContractError, "altered canonical"):
                self.result(plan, raw=b"not inspected")

    def test_legacy_hashes_identical_to_new_core_for_same_crop(self):
        item = self.result()["index_records"][0]
        hashes = corpus.legacy_patch_pair(self.s, self.r, "ESM1", item["center_x"], item["center_y"])
        self.assertEqual(hashes["structural_patch_sha256"], item["structural_patch_sha256"])
        self.assertEqual(hashes["solutal_patch_sha256"], item["solutal_patch_sha256"])
        self.assertEqual(hashes["pair_sha256"], item["pair_sha256"])

    def test_legacy_invalid_crop_denies_not_moves(self):
        with self.assertRaisesRegex(corpus.CorpusContractError, "BLOCKED_LEGACY_PAIR_REPRODUCTION"):
            corpus.legacy_patch_pair(self.s, self.r, "ESM1", 5, 5)

    def test_future_positive_exclusion_before_first_annotation(self):
        site = synthetic_site(point=[357, 422])
        observations = [synthetic_observation(site, 0, "PRE_FIRST_CONFIDENT_ANNOTATION"),
                        synthetic_observation(site, 8)]
        result = self.result(synthetic_plan([site], observations))
        pool = result["background_records"]
        self.assertTrue(pool)
        self.assertNotIn((357, 422), {(r["center_x"], r["center_y"]) for r in pool})
        zone = [322, 387, 393, 458]
        self.assertTrue(all(not corpus._intersects(r["safety_xyxy"], zone) for r in pool))

    def test_ambiguous_and_small_boxes_exclude_pool_positions(self):
        targets = [(747, 487), (942, 617)]
        components = [synthetic_component(1, box=[745, 485, 749, 489]),
                      synthetic_component(2, classification="SMALL_COMPONENT", box=[940, 615, 944, 619])]
        pool = self.result(synthetic_plan(components=components))["background_records"]
        positions = {(r["center_x"], r["center_y"]) for r in pool}
        self.assertTrue(positions)
        self.assertTrue(all(point not in positions for point in targets))

    def test_background_track_immutable_across_frames_rank_frame_specific(self):
        site = synthetic_site(); obs = [synthetic_observation(site, i) for i in [0, 1]]
        plan = synthetic_plan([site], obs)
        a = self.result(plan, frame=0)["background_records"]
        b = self.result(plan, frame=1)["background_records"]
        self.assertEqual([r["background_track_id"] for r in a], [r["background_track_id"] for r in b])
        self.assertNotEqual(a[0]["hash_rank"], b[0]["hash_rank"])
        self.assertTrue(all(r["pixels_materialized"] is False for r in a + b))
        self.assertTrue(all(r["physical_absence_inferred"] is False for r in a + b))

    def test_background_safety_support_and_boundary_contact(self):
        self.assertTrue(corpus._intersects([0, 0, 10, 10], [10, 0, 20, 10]))
        self.assertFalse(corpus._intersects([0, 0, 10, 10], [11, 0, 20, 10]))
        pool = self.result()["background_records"]
        support = corpus.support_xyxy(*corpus.DIMENSIONS["ESM1"])
        self.assertTrue(all(corpus._inside(r["safety_xyxy"], support) for r in pool))

    def test_background_pool_deterministic_and_not_balanced_to_sites(self):
        a, b = self.result(), self.result()
        self.assertEqual(a["background_records"], b["background_records"])
        self.assertGreater(len(a["background_records"]), 1)

    def test_view_rows_partition_without_pixel_duplication(self):
        site = synthetic_site()
        obs = [synthetic_observation(site, i, state) for i, state in enumerate(corpus.TIERS)]
        plan = synthetic_plan([site], obs); records = []
        for i in range(4):
            records.extend(self.result(plan, frame=i, row_start=i)["index_records"])
        views = corpus.corpus_views(records)
        self.assertEqual(views, {"GOLD_VIEW": [0], "GOLD_PLUS_SILVER_VIEW": [0, 1],
                                 "UNLABELED_VIEW": [2, 3], "FULL_LONGITUDINAL_VIEW": [0, 1, 2, 3]})

    def test_views_reject_duplicate_and_gapped_rows(self):
        item = self.result()["index_records"][0]
        with self.assertRaises(corpus.CorpusContractError):
            corpus.corpus_views([item, deepcopy(item)])
        item["row_index"] = 1
        with self.assertRaisesRegex(corpus.CorpusContractError, "contiguous"):
            corpus.corpus_views([item])


if __name__ == "__main__":
    unittest.main()
