"""Frozen, metadata-only TI3 patch planning. This module performs no I/O.

The support rectangle is the documentary border/text component of G2's mask,
including its one-pixel erosion. It is not a certified scientific ROI or a
reconstruction of the experimental chromatic mask. Rectangles ending in xyxy
are half-open; intersection calculations explicitly use inclusive pixel ends.
"""

import copy
import hashlib
import math


SCHEMA = "TI3-CANONICAL-PATCH-MANIFEST-1"
TARGET = "PUBLISHED_FRAGMENTATION_LOCATION_PRESENT"
SPLITS = ("TRAIN", "DEVELOPMENT", "FINAL_TEST")
FRAME_SPLITS = {
    ("ESM1", 73): "TRAIN", ("ESM1", 146): "TRAIN",
    ("ESM4", 98): "TRAIN", ("ESM1", 219): "DEVELOPMENT",
    ("ESM4", 197): "DEVELOPMENT", ("ESM1", 293): "FINAL_TEST",
    ("ESM4", 295): "FINAL_TEST",
}
SOURCE_MAP = {"ESM3": "ESM1", "ESM6": "ESM4"}
ACQUISITIONS = {
    "ESM1": "bottom_up_anti_parallel", "ESM4": "top_down_parallel",
}
DIMENSIONS = {"ESM1": (1278, 1018), "ESM4": (1278, 1012)}
PARAMETERS = {
    "patch_radius_px": 32, "patch_side_px": 65,
    "registration_guard_px": 3, "site_exclusion_radius_px": 35,
    "site_exclusion_geometry": "closed_L_infinity_square_contacts_blocked",
    "center_rounding": "floor(coordinate+0.5)", "mapping_offset_xy": [0, 0],
    "support_border_px": 4, "support_erosion_px": 1,
    "support_top_fraction": 0.12, "support_bottom_fraction": 0.15,
    "support_fraction_rounding": "ceil",
    "support_semantics": "documentary_geometry_not_certified_roi_or_chroma_mask",
    "background_seed": 42, "background_grid_stride_px": 65,
    "background_quota": "one_per_valid_positive_per_split",
    "background_order": "sha256_TI3_BACKGROUND_V1_pipe_42_source_frame_x_y",
    "background_reuse": "no_overlap_in_same_acquisition_across_all_frames",
    "positive_ignore_policy": "diagnostic_only_not_an_exclusion",
    "input_plane": "Y", "input_sources": ["ESM1", "ESM4"],
    "input_rescaling": False, "padding": False,
}


class DatasetContractError(ValueError):
    """A required metadata invariant is missing, inconsistent or unsafe."""


def _require(condition, message):
    if not condition:
        raise DatasetContractError(message)


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _point(observation):
    point = [observation.get("center_x"), observation.get("center_y")]
    _require(all(_number(v) for v in point), "finite observed center required")
    return point


def support_xyxy(width, height):
    """Fixed documentary support, including historical one-pixel erosion."""
    return [5, max(4, math.ceil(height * 0.12)) + 1,
            width - 5, height - max(4, math.ceil(height * 0.15)) - 1]


def patch_xyxy(x, y):
    return [x - 32, y - 32, x + 33, y + 33]


def _closed(box):
    return [box[0], box[1], box[2] - 1, box[3] - 1]


def _intersects(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def _inside(box, support):
    return (support[0] <= box[0] < box[2] <= support[2]
            and support[1] <= box[1] < box[3] <= support[3])


def _site_zone(point):
    return [point[0] - 35, point[1] - 35, point[0] + 35, point[1] + 35]


def _ignore_zone(box):
    return [box[0] - 3, box[1] - 3, box[2] + 2, box[3] + 2]


def _site_conflicts(box, acquisition, assignments, incompatible_split=None):
    result = []
    for site in assignments:
        if site["acquisition_id"] != acquisition:
            continue
        if incompatible_split is not None and site["split"] == incompatible_split:
            continue
        if any(_intersects(_closed(box), _site_zone(o["center_xy"]))
               for o in site["observations"]):
            result.append(site["annotation_site_id"])
    return sorted(result)


def _ignore_conflicts(box, acquisition, ignores):
    return sorted(item["observation_id"] for item in ignores
                  if item["acquisition_id"] == acquisition
                  and _intersects(_closed(box), _ignore_zone(item["bbox_xyxy"])))


def _inventory(pilot_images):
    _require(type(pilot_images) is list, "pilot images must be a list")
    indexed = {}
    for image in pilot_images:
        key = (image.get("source_id"), image.get("frame_index"))
        _require(key not in indexed, "duplicate pilot source/frame")
        indexed[key] = image
    inventory = []
    for source, frame in FRAME_SPLITS:
        _require((source, frame) in indexed, "required structural pilot metadata missing")
        image = indexed[(source, frame)]
        width, height = DIMENSIONS[source]
        _require(type(image.get("frame_index")) is int, "integer pilot frame required")
        _require((image.get("width"), image.get("height")) == (width, height),
                 "native structural dimensions differ")
        _require(image.get("experiment_id") == ACQUISITIONS[source],
                 "pilot acquisition mismatch")
        _require(image.get("pixel_format") == "yuv420p" and image.get("bit_depth") == 8,
                 "native eight-bit YUV420p required")
        _require(image.get("frame_bytes") == width * height * 3 // 2,
                 "native byte count mismatch")
        _require(_number(image.get("experimental_time_s")), "documented experimental time required")
        _require(image.get("path") == f"data/derived/ti2-pilot/{source}-{frame:04d}.raw",
                 "pilot path not the exact native allowlist path")
        digest = image.get("image_sha256", "")
        _require(type(digest) is str and len(digest) == 64
                 and all(c in "0123456789abcdef" for c in digest), "invalid known pilot hash")
        planes = image.get("planes", [])
        _require(len(planes) == 3 and planes[0] == {
            "name": "Y", "offset": 0, "bytes": width * height,
            "width": width, "height": height}, "native Y plane metadata mismatch")
        inventory.append({
            "source_id": source, "frame_index": frame,
            "acquisition_id": ACQUISITIONS[source], "split": FRAME_SPLITS[(source, frame)],
            "context_group": f"{ACQUISITIONS[source]}|{source}|{frame}",
            "width": width, "height": height, "path": image["path"],
            "image_sha256": digest, "frame_bytes": image["frame_bytes"],
            "experimental_time_s": image["experimental_time_s"],
            "pixel_format": "yuv420p", "bit_depth": 8, "plane": "Y",
            "y_plane": copy.deepcopy(planes[0]), "support_xyxy": support_xyxy(width, height),
            "input_opened": False,
        })
    return inventory


def _assign_sites(sites, ledger):
    _require(type(sites) is list and type(ledger) is list, "site and ledger lists required")
    assignments, observation_lookup, site_ids = [], {}, set()
    for site in sites:
        site_id = site.get("annotation_site_id")
        _require(type(site_id) is str and site_id and site_id not in site_ids,
                 "site ID missing or duplicated")
        site_ids.add(site_id)
        annotation_source = site.get("source_id")
        _require(annotation_source in SOURCE_MAP, "unsupported annotation source")
        source = SOURCE_MAP[annotation_source]
        acquisition = ACQUISITIONS[source]
        _require(site.get("acquisition_id") == acquisition, "site acquisition mismatch")
        observations = site.get("observations", [])
        _require(type(observations) is list and observations, "site observations required")
        fco = site.get("first_confident_observation", {})
        matches = [o for o in observations if o.get("observation_id") == fco.get("observation_id")]
        _require(len(matches) == 1, "FCO must name exactly one observed center")
        first = matches[0]
        _require(all(type(o.get("frame_index")) is int for o in observations),
                 "integer observation frames required")
        frame = first["frame_index"]
        _require(fco.get("frame_index") == frame
                 and frame == min(o["frame_index"] for o in observations), "FCO frame mismatch")
        _require(sum(o["frame_index"] == frame for o in observations) == 1,
                 "ambiguous first observation")
        _require((source, frame) in FRAME_SPLITS, "FCO outside the fixed split frames")
        points = []
        for observation in observations:
            observation_id = observation.get("observation_id")
            _require(type(observation_id) is str and observation_id
                     and observation_id not in observation_lookup, "duplicate observation ID")
            point = _point(observation)
            observation_lookup[observation_id] = (site_id, annotation_source,
                                                  acquisition, observation["frame_index"], point)
            points.append({"observation_id": observation_id,
                           "frame_index": observation["frame_index"], "center_xy": point})
        assignments.append({
            "annotation_site_id": site_id, "annotation_source_id": annotation_source,
            "source_id": source, "acquisition_id": acquisition,
            "split": FRAME_SPLITS[(source, frame)], "frame_index": frame,
            "first_observation_id": first["observation_id"],
            "published_center_xy": _point(first), "observations": points,
        })
    seen, positive_ids, ignores = set(), set(), []
    for row in ledger:
        observation_id = row.get("observation_id")
        _require(type(observation_id) is str and observation_id and observation_id not in seen,
                 "duplicate or missing ledger observation")
        seen.add(observation_id)
        annotation_source = row.get("source_id")
        _require(annotation_source in SOURCE_MAP, "unsupported ledger source")
        acquisition = ACQUISITIONS[SOURCE_MAP[annotation_source]]
        _require(row.get("acquisition_id") == acquisition, "ledger acquisition mismatch")
        supervision = row.get("new_supervision")
        if supervision == "POSITIVE":
            _require(observation_id in observation_lookup, "positive missing from site ledger")
            expected = observation_lookup[observation_id]
            _require((row.get("annotation_site_id"), annotation_source, acquisition,
                      row.get("frame_index"), _point(row)) == expected,
                     "positive/site provenance mismatch")
            positive_ids.add(observation_id)
        else:
            _require(supervision == "IGNORE", "unapproved supervision class")
            box = row.get("bbox_xyxy")
            _require(type(box) is list and len(box) == 4 and all(_number(v) for v in box)
                     and box[0] < box[2] and box[1] < box[3], "invalid IGNORE bounds")
            ignores.append({"observation_id": observation_id, "acquisition_id": acquisition,
                            "frame_index": row.get("frame_index"), "bbox_xyxy": list(box)})
    _require(positive_ids == set(observation_lookup), "site observation absent from positive ledger")
    return sorted(assignments, key=lambda s: s["annotation_site_id"]), ignores


def _sample(image, x, y, sample_id, site=None):
    result = {key: copy.deepcopy(image[key]) for key in (
        "source_id", "frame_index", "acquisition_id", "split", "context_group",
        "path", "image_sha256", "frame_bytes", "width", "height", "plane", "experimental_time_s")}
    result.update({
        "sample_id": sample_id, "annotation_site_id": None if site is None else site["annotation_site_id"],
        "annotation_site_id_or_background_id": sample_id if site is None else site["annotation_site_id"],
        "observation_id": None if site is None else site["first_observation_id"],
        "annotation_source_id": None if site is None else site["annotation_source_id"],
        "published_center_xy": None if site is None else list(site["published_center_xy"]),
        "center_native_xy": [x, y], "center_x": x, "center_y": y,
        "patch_radius_px": 32, "patch_side_px": 65, "patch_xyxy": patch_xyxy(x, y),
        "target": TARGET, "weak_label": "BACKGROUND_CANDIDATE" if site is None else "POSITIVE",
        "label": "BACKGROUND_CANDIDATE" if site is None else "POSITIVE",
        "baseline_label": 0 if site is None else 1, "input_opened": False,
        "input_hash_if_opened": None, "context_group_id": image["context_group"],
        "provenance": {"native_path": image["path"], "known_native_sha256": image["image_sha256"],
                       "native_source_id": image["source_id"], "frame_index": image["frame_index"],
                       "input_role": "structural_luminance",
                       "annotation_source_id": None if site is None else site["annotation_source_id"],
                       "observation_id": None if site is None else site["first_observation_id"]},
        "mapping_offset_xy": [0, 0], "physical_fragment_absence_claim": False,
    })
    return result


def build_manifest(sites, ledger, pilot_images):
    """Plan once from frozen textual metadata; never access a source or pixels."""
    inventory = _inventory(pilot_images)
    images = {(i["source_id"], i["frame_index"]): i for i in inventory}
    assignments, ignores = _assign_sites(sites, ledger)
    positives, exclusions = [], []
    for site in assignments:
        image = images[(site["source_id"], site["frame_index"])]
        x, y = [math.floor(v + 0.5) for v in site["published_center_xy"]]
        candidate = _sample(image, x, y, f"positive|{site['annotation_site_id']}", site)
        conflicts = _site_conflicts(candidate["patch_xyxy"], site["acquisition_id"],
                                    assignments, site["split"])
        reasons = []
        if not _inside(candidate["patch_xyxy"], image["support_xyxy"]):
            reasons.append("UNAVAILABLE")
        if conflicts:
            reasons.append("INVALID_CONTEXT")
        candidate.update({"status": "VALID" if not reasons else reasons[0],
                          "exclusion_reasons": reasons, "conflicting_site_ids": conflicts,
                          "ignore_diagnostic_ids": _ignore_conflicts(
                              candidate["patch_xyxy"], site["acquisition_id"], ignores)})
        positives.append(candidate)
        if reasons:
            exclusions.append(copy.deepcopy(candidate))
    split_counts = {}
    available_backgrounds = {split: [] for split in SPLITS}
    for image in inventory:
        support = image["support_xyxy"]
        for y in range(support[1] + 32, support[3] - 32, 65):
            for x in range(support[0] + 32, support[2] - 32, 65):
                sample_id = f"background|{image['source_id']}|{image['frame_index']}|{x}|{y}"
                candidate = _sample(image, x, y, sample_id)
                sites_hit = _site_conflicts(candidate["patch_xyxy"], image["acquisition_id"], assignments)
                ignores_hit = _ignore_conflicts(candidate["patch_xyxy"], image["acquisition_id"], ignores)
                if sites_hit or ignores_hit:
                    candidate.update({"exclusion_reasons": (["POSITIVE_SAFETY"] if sites_hit else [])
                                      + (["IGNORE_SAFETY"] if ignores_hit else []),
                                      "conflicting_site_ids": sites_hit,
                                      "conflicting_ignore_ids": ignores_hit})
                    exclusions.append(candidate)
                    continue
                rank_text = f"TI3_BACKGROUND_V1|42|{image['source_id']}|{image['frame_index']}|{x}|{y}"
                candidate["selection_rank_sha256"] = hashlib.sha256(rank_text.encode("ascii")).hexdigest()
                candidate["selection_rank_text"] = rank_text
                available_backgrounds[image["split"]].append(candidate)
    selected, deficits = [], {}
    for split in SPLITS:
        split_positives = [p for p in positives if p["split"] == split]
        valid = [p for p in split_positives if p["status"] == "VALID"]
        candidates = sorted(available_backgrounds[split], key=lambda s: (
            s["selection_rank_sha256"], s["selection_rank_text"]))
        chosen = []
        for candidate in candidates:
            if len(chosen) == len(valid):
                break
            overlap = [s["sample_id"] for s in selected + chosen
                       if s["acquisition_id"] == candidate["acquisition_id"]
                       and _intersects(_closed(s["patch_xyxy"]), _closed(candidate["patch_xyxy"]))]
            if overlap:
                exclusions.append({**candidate, "exclusion_reasons": ["BACKGROUND_SPATIAL_REUSE"],
                                   "conflicting_sample_ids": sorted(overlap)})
            else:
                chosen.append(candidate)
        selected.extend(chosen)
        deficits[split] = len(valid) - len(chosen)
        split_counts[split] = {
            "positive_candidates": len(split_positives), "valid_positives": len(valid),
            "excluded_positives": len(split_positives) - len(valid),
            "geometrically_available_backgrounds": len(candidates), "selected_backgrounds": len(chosen),
            "background_deficit": deficits[split],
            "backgrounds_by_frame": {f"{i['source_id']}:{i['frame_index']}":
                sum(s["source_id"] == i["source_id"] and s["frame_index"] == i["frame_index"] for s in chosen)
                for i in inventory if i["split"] == split},
        }
    if any(c["valid_positives"] == 0 for c in split_counts.values()):
        state = "BLOCKED_SPLIT_SUPPORT"
    elif any(deficits.values()):
        state = "BLOCKED_BACKGROUND_SUPPORT"
    else:
        state = "PASS"
    samples = ([copy.deepcopy(p) for p in positives if p["status"] == "VALID"]
               + copy.deepcopy(selected)) if state == "PASS" else []
    for split in SPLITS:
        split_counts[split]["materializable_samples"] = sum(s["split"] == split for s in samples)
    return {
        "schema": SCHEMA, "state": state, "target": TARGET,
        "parameters": copy.deepcopy(PARAMETERS), "metadata_only": True, "input_opened": False,
        "final_test_status": ("SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE" if state == "PASS"
                              else "NOT_DEFINED_NOT_OPENED"),
        "site_assignments": assignments, "ignore_geometry": ignores,
        "source_inventory": inventory, "positive_candidates": positives,
        "provisional_backgrounds": selected, "samples": samples, "exclusions": exclusions,
        "site_count": len(assignments), "split_counts": split_counts,
        "background_deficits": deficits, "ml_runs": 0, "experimental_opens": 0,
    }


def validate_manifest(manifest):
    """Fail closed without rebuilding selection, reading sources or using pixels."""
    _require(manifest.get("schema") == SCHEMA and manifest.get("target") == TARGET,
             "manifest identity mismatch")
    _require(manifest.get("parameters") == PARAMETERS, "frozen parameters differ")
    _require(manifest.get("state") == "PASS", "blocked plan cannot arm materialization")
    _require(manifest.get("metadata_only") is True and manifest.get("input_opened") is False
             and manifest.get("experimental_opens") == 0 and manifest.get("ml_runs") == 0,
             "pre-execution manifest must remain unopened")
    _require(manifest.get("final_test_status") == "SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE",
             "final-test seal or exposure declaration missing")
    inventory = manifest.get("source_inventory", [])
    sources = {}
    for image in inventory:
        key = (image.get("source_id"), image.get("frame_index"))
        _require(key in FRAME_SPLITS and key not in sources, "invalid or duplicate source/frame")
        source, frame = key
        w, h = DIMENSIONS[source]
        _require(image.get("split") == FRAME_SPLITS[key]
                 and image.get("acquisition_id") == ACQUISITIONS[source], "source split/acquisition mismatch")
        _require(image.get("width") == w and image.get("height") == h
                 and image.get("support_xyxy") == support_xyxy(w, h), "source bounds mismatch")
        _require(image.get("input_opened") is False, "source was opened before execution gate")
        _require(image.get("path") == f"data/derived/ti2-pilot/{source}-{frame:04d}.raw"
                 and image.get("frame_bytes") == w * h * 3 // 2, "source lineage mismatch")
        _require(image.get("plane") == "Y" and image.get("pixel_format") == "yuv420p"
                 and image.get("bit_depth") == 8, "source representation mismatch")
        sources[key] = image
    _require(set(sources) == set(FRAME_SPLITS), "incomplete source inventory")
    assignments = manifest.get("site_assignments", [])
    site_map = {}
    for site in assignments:
        site_id = site.get("annotation_site_id")
        _require(site_id not in site_map and type(site_id) is str, "duplicate site group")
        key = (site.get("source_id"), site.get("frame_index"))
        _require(key in FRAME_SPLITS and site.get("split") == FRAME_SPLITS[key], "site split mismatch")
        _require(SOURCE_MAP.get(site.get("annotation_source_id")) == key[0]
                 and site.get("acquisition_id") == ACQUISITIONS[key[0]], "site mapping mismatch")
        observation = [o for o in site.get("observations", [])
                       if o.get("observation_id") == site.get("first_observation_id")]
        _require(len(observation) == 1 and observation[0].get("frame_index") == key[1]
                 and observation[0].get("center_xy") == site.get("published_center_xy"), "site FCO mismatch")
        _require(key[1] == min(o["frame_index"] for o in site["observations"]), "FCO not earliest observation")
        site_map[site_id] = site
    _require(manifest.get("site_count") == len(site_map), "site count mismatch")
    samples = manifest.get("samples", [])
    _require(type(samples) is list and samples, "materializable samples missing")
    seen_samples, seen_sites, contexts, backgrounds = set(), set(), {}, []
    counts = {s: [0, 0] for s in SPLITS}
    for sample in samples:
        sample_id = sample.get("sample_id")
        _require(type(sample_id) is str and sample_id not in seen_samples, "duplicate sample")
        seen_samples.add(sample_id)
        key = (sample.get("source_id"), sample.get("frame_index"))
        _require(key in sources, "sample source outside exact structural allowlist")
        image = sources[key]
        for field in ("acquisition_id", "split", "context_group", "path", "image_sha256",
                      "frame_bytes", "width", "height", "plane", "experimental_time_s"):
            _require(sample.get(field) == image[field], "sample/source provenance mismatch")
        split = sample["split"]
        expected_context = f"{image['acquisition_id']}|{key[0]}|{key[1]}"
        _require(sample["context_group"] == expected_context, "context group mismatch")
        _require(sample.get("context_group_id") == expected_context, "canonical context group mismatch")
        _require(contexts.setdefault(expected_context, split) == split, "context crosses partitions")
        _require(sample.get("input_opened") is False, "sample opened before execution gate")
        _require(sample.get("input_hash_if_opened") is None, "unopened input cannot have observed hash")
        _require(sample.get("mapping_offset_xy") == [0, 0] and sample.get("target") == TARGET,
                 "sample mapping or target changed")
        center = sample.get("center_native_xy", [])
        _require(len(center) == 2 and all(type(v) is int for v in center), "integer pixel center required")
        _require(sample.get("center_x") == center[0] and sample.get("center_y") == center[1]
                 and type(sample.get("center_x")) is int and type(sample.get("center_y")) is int
                 and sample.get("patch_radius_px") == 32 and sample.get("patch_side_px") == 65,
                 "sample center or fixed patch contract mismatch")
        box = patch_xyxy(*center)
        _require(sample.get("patch_xyxy") == box and _inside(box, image["support_xyxy"]),
                 "patch support or size mismatch")
        site_id = sample.get("annotation_site_id")
        _require(sample.get("label") == sample.get("weak_label"), "canonical label mismatch")
        _require(sample.get("annotation_site_id_or_background_id") == (site_id or sample_id),
                 "canonical site/background identifier mismatch")
        provenance = sample.get("provenance", {})
        _require(provenance.get("native_path") == image["path"]
                 and provenance.get("known_native_sha256") == image["image_sha256"]
                 and provenance.get("native_source_id") == key[0]
                 and provenance.get("frame_index") == key[1]
                 and provenance.get("input_role") == "structural_luminance",
                 "canonical provenance mismatch")
        if sample.get("weak_label") == "POSITIVE":
            _require(sample.get("baseline_label") == 1 and site_id in site_map
                     and site_id not in seen_sites, "positive site repeated or invalid")
            seen_sites.add(site_id)
            site = site_map[site_id]
            _require(site["split"] == split and (site["source_id"], site["frame_index"]) == key,
                     "positive site crosses split or context")
            _require(sample.get("observation_id") == site["first_observation_id"]
                     and sample.get("published_center_xy") == site["published_center_xy"]
                     and center == [math.floor(v + 0.5) for v in site["published_center_xy"]],
                     "positive no longer uses its own FCO coordinate")
            _require(not _site_conflicts(box, image["acquisition_id"], assignments, split),
                     "positive has incompatible site context")
            counts[split][0] += 1
        else:
            _require(sample.get("weak_label") == "BACKGROUND_CANDIDATE"
                     and sample.get("baseline_label") == 0 and site_id is None,
                     "unapproved background supervision")
            _require(not _site_conflicts(box, image["acquisition_id"], assignments)
                     and not _ignore_conflicts(box, image["acquisition_id"], manifest["ignore_geometry"]),
                     "background intersects positive or IGNORE safety")
            _require(all(b["acquisition_id"] != image["acquisition_id"]
                         or not _intersects(_closed(box), _closed(b["patch_xyxy"])) for b in backgrounds),
                     "background spatial support reused")
            backgrounds.append(sample)
            counts[split][1] += 1
    candidates = manifest["positive_candidates"]
    candidate_sites = [p["annotation_site_id"] for p in candidates]
    _require(len(candidate_sites) == len(set(candidate_sites))
             and set(candidate_sites) == set(site_map), "incomplete canonical candidate inventory")
    valid_candidates = set()
    for candidate in candidates:
        site = site_map[candidate["annotation_site_id"]]
        image = sources[(site["source_id"], site["frame_index"])]
        center = [math.floor(v + 0.5) for v in site["published_center_xy"]]
        box = patch_xyxy(*center)
        conflicts = _site_conflicts(box, site["acquisition_id"], assignments, site["split"])
        reasons = ([] if _inside(box, image["support_xyxy"]) else ["UNAVAILABLE"])
        reasons += ["INVALID_CONTEXT"] if conflicts else []
        _require(candidate.get("exclusion_reasons") == reasons
                 and candidate.get("conflicting_site_ids") == conflicts
                 and candidate.get("status") == (reasons[0] if reasons else "VALID"),
                 "canonical candidate exclusions were altered")
        if not reasons:
            valid_candidates.add(site["annotation_site_id"])
    _require(seen_sites == valid_candidates, "valid canonical positive omitted or invented")
    for split in SPLITS:
        p, b = counts[split]
        recorded = manifest["split_counts"][split]
        _require(p > 0 and p == b and recorded["valid_positives"] == p
                 and recorded["selected_backgrounds"] == b
                 and recorded["materializable_samples"] == p + b
                 and manifest["background_deficits"][split] == 0, "split support or balance mismatch")
    return True
