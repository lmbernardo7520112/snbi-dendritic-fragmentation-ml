"""Pure, deterministic temporal metadata for published annotation sites.

This module has no file or image I/O. It consumes the unchanged A0 component
records and their native chromatic footprints, never luminance or solute. Site identity
is anchored to its first direct valid center and never follows a moving mean.
An ambiguous component supports a known site only if it contains that site's
complete first-direct footprint without translation. Bboxes are diagnostics,
never sufficient support. Explicitly blank chromatic frames can bound marker
appearance documentarily, never physical absence or fragmentation onset.
"""

import copy
import hashlib
import json
import math
from collections import Counter

from snbi_fragmentation.ti3_a0_annotations import AMBIGUOUS, SMALL, VALID


TOLERANCE_PX = 2.0
CHROMA_DISTANCE = 20
SOURCE_CONTRACT = {
    "ESM3": ("bottom_up_anti_parallel", 294, -2596),
    "ESM6": ("top_down_parallel", 395, -3422),
}
FRAME_STATUSES = frozenset({"PROCESSED", "DECODE_FAILED", "INTEGRITY_FAILED"})
OBSERVATION_STATUSES = frozenset({
    "DIRECT_VALID", "TEMPORAL_SUPPORTED_AMBIGUOUS",
    "PERSISTENCE_EXPECTED_UNRESOLVED", "PRE_FIRST_CONFIDENT_ANNOTATION",
    "CONFLICT", "INVALID_FRAME",
})


class TrackingError(ValueError):
    """Invalid metadata cannot silently alter a temporal record."""


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _sha(value):
    return (isinstance(value, str) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def _distance(left, right):
    return math.hypot(left[0] - right[0], left[1] - right[1])


def _contains(box, center):
    return box[0] <= center[0] < box[2] and box[1] <= center[1] < box[3]


def _bbox_distance(box, center):
    """Distance to the closed bbox envelope, diagnostic only, never a gate."""
    dx = max(box[0] - center[0], 0, center[0] - box[2])
    dy = max(box[1] - center[1], 0, center[1] - box[3])
    return math.hypot(dx, dy)


def _identity(source, frame, component, center):
    immutable = {
        "source_id": source, "first_direct_frame": frame,
        "first_direct_component_id": component,
        "canonical_center_xy_px": [float(v) for v in center],
    }
    encoded = json.dumps(immutable, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode("utf-8")
    return source + ":study2a-site:" + hashlib.sha256(encoded).hexdigest()


def _validated_components(result):
    if not isinstance(result, dict) or not isinstance(result.get("components"), list):
        raise TrackingError("processed frame requires an A0 component list")
    components = result["components"]
    ids = set()
    for item in components:
        if not isinstance(item, dict):
            raise TrackingError("each component must be a dictionary")
        cid = item.get("component_id")
        if type(cid) is not int or cid < 1 or cid in ids:
            raise TrackingError("component IDs must be distinct positive integers")
        ids.add(cid)
        classification = item.get("classification")
        if classification not in (VALID, AMBIGUOUS, SMALL):
            raise TrackingError("unrecognized A0 classification")
        bbox = item.get("bbox_xyxy")
        if (not isinstance(bbox, (list, tuple)) or len(bbox) != 4
                or not all(_number(v) for v in bbox)
                or not (bbox[0] < bbox[2] and bbox[1] < bbox[3])):
            raise TrackingError("component bbox must have finite ordered bounds")
        if not isinstance(item.get("reasons"), list):
            raise TrackingError("original A0 reasons must be retained")
        if classification == VALID:
            center = item.get("center_xy_px")
            if (not isinstance(center, (list, tuple)) or len(center) != 2
                    or not all(_number(v) for v in center)):
                raise TrackingError("valid center must contain finite coordinates")
            if item["reasons"]:
                raise TrackingError("a valid A0 component cannot carry rejection reasons")
    counts = Counter(c["classification"] for c in components)
    expected = {
        "component_count": len(components),
        "valid_circle_count": counts[VALID],
        "ambiguous_component_count": counts[AMBIGUOUS],
        "small_component_count": counts[SMALL],
    }
    for key, count in expected.items():
        if type(result.get(key)) is not int or result[key] != count:
            raise TrackingError("A0 component counts must match retained records")
    return sorted(copy.deepcopy(components), key=lambda item: item["component_id"])


def component_support_from_chroma(u, v, width, height, result):
    """Recover exactly the existing A0 threshold20/8-connected ink footprints.

    No circle fitting or alternative detection is performed. Pixel sets use
    native ``y * width + x`` coordinates and are strictly in-memory evidence.
    IDs, areas, bboxes and mask counts must exactly match the A0 result before
    any footprint can be used. Callers must never serialize these sets.
    """
    if any(type(value) is not int or value < 2 or value % 2 for value in (width, height)):
        raise TrackingError("native dimensions must be positive even integers")
    components = _validated_components(result)
    if result.get("native_width") != width or result.get("native_height") != height:
        raise TrackingError("footprint dimensions differ from the A0 result")
    import numpy as np
    from scipy import ndimage

    u, v = np.asarray(u), np.asarray(v)
    if any(p.shape != (height // 2, width // 2) or p.dtype != np.dtype("uint8") for p in (u, v)):
        raise TrackingError("native U/V must be half-resolution uint8 planes")
    distance = np.maximum(np.abs(u.astype(np.int16) - 128), np.abs(v.astype(np.int16) - 128))
    chromatic = distance >= CHROMA_DISTANCE
    mask = np.repeat(np.repeat(chromatic, 2, axis=0), 2, axis=1)
    labels, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=bool))
    if count != result["component_count"]:
        raise TrackingError("footprint component count differs from A0")
    for key, actual in (("colored_pixel_count", int(mask.sum())),
                        ("colored_chroma_sample_count", int(chromatic.sum()))):
        if type(result.get(key)) is not int or result[key] != actual:
            raise TrackingError("footprint mask counts differ from A0")
    by_id = {item["component_id"]: item for item in components}
    if set(by_id) != set(range(1, count + 1)):
        raise TrackingError("footprint IDs differ from A0 connectivity labels")
    footprints = {}
    for cid, box in enumerate(ndimage.find_objects(labels), 1):
        ys, xs = box
        yy, xx = np.nonzero(labels[box] == cid)
        item = by_id[cid]
        if item["bbox_xyxy"] != [xs.start, ys.start, xs.stop, ys.stop]:
            raise TrackingError("footprint bbox differs from A0")
        if type(item.get("area_px")) is not int or item["area_px"] != int(xx.size):
            raise TrackingError("footprint area differs from A0")
        footprints[cid] = frozenset((int(y) + ys.start) * width + int(x) + xs.start
                                   for y, x in zip(yy, xx))
    return footprints


def _validated_footprints(result, components):
    if "_component_pixels" not in result:
        return {}
    footprints = result["_component_pixels"]
    if (not isinstance(footprints, dict)
            or set(footprints) != {item["component_id"] for item in components}):
        raise TrackingError("component footprint mapping must cover exactly the current components")
    for item in components:
        footprint = footprints[item["component_id"]]
        if (not isinstance(footprint, frozenset) or not footprint
                or any(type(pixel) is not int or pixel < 0 for pixel in footprint)):
            raise TrackingError("component footprint must be a nonempty frozenset of native indices")
        if "area_px" in item and len(footprint) != item["area_px"]:
            raise TrackingError("component footprint size differs from A0 area")
    return footprints


class TemporalTracker:
    """Consume one source in exact frame order; retain only first ink footprints.

    ``expected_frames`` may be shorter than the source for synthetic fixtures.
    Production admission must independently require the full 294/395 frames.
    ``finish`` preserves partial coverage explicitly; it cannot certify a run.
    Failed frames must be submitted with no detector output. Their optional
    raw hash denotes bytes received before an integrity failure, not success.
    """

    def __init__(self, source_id, acquisition_id, expected_frames):
        if source_id not in SOURCE_CONTRACT:
            raise TrackingError("only ESM3 and ESM6 annotation metadata are admitted")
        expected_acquisition, maximum_frames, _ = SOURCE_CONTRACT[source_id]
        if acquisition_id != expected_acquisition:
            raise TrackingError("source must retain its documented acquisition")
        if type(expected_frames) is not int or not 1 <= expected_frames <= maximum_frames:
            raise TrackingError("invalid expected frame count")
        self.source_id = source_id
        self.acquisition_id = acquisition_id
        self.expected_frames = expected_frames
        self._sites = {}
        self._frames = []
        self._candidates = []
        self._observations = []
        self._links = []
        self._anchor_footprints = {}
        self._finished = False

    def _time(self, index):
        offset_cs = SOURCE_CONTRACT[self.source_id][2]
        return {"elapsed_time_s": 118 * index / 100,
                "experimental_time_s": (offset_cs + 118 * index) / 100}

    def _observation(self, site, index, status, component_ids, raw_sha256):
        return {
            "site_id": site["site_id"], "source_id": self.source_id,
            "acquisition_id": self.acquisition_id, "frame_index": index,
            **self._time(index), "status": status,
            "component_ids": list(component_ids), "raw_frame_sha256": raw_sha256,
            "canonical_center_xy_px": list(site["canonical_center_xy_px"]),
            "evidence_basis": {
                "DIRECT_VALID": "OBSERVED_VALID_COMPONENT_UNIQUE_IDENTITY",
                "TEMPORAL_SUPPORTED_AMBIGUOUS": "COMPLETE_FIRST_DIRECT_INK_FOOTPRINT_CONTAINED_IN_OBSERVED_AMBIGUOUS_COMPONENT",
                "PERSISTENCE_EXPECTED_UNRESOLVED": "CUMULATIVE_EXPECTATION_NOT_A_POSITIVE_LABEL",
                "PRE_FIRST_CONFIDENT_ANNOTATION": "RETROSPECTIVE_BEFORE_FIRST_DIRECT_NOT_ABSENCE",
                "CONFLICT": "OBSERVED_VALID_COMPONENT_IDENTITY_UNRESOLVED",
                "INVALID_FRAME": "NO_ADMISSIBLE_FRAME_EVIDENCE",
            }[status],
            "supervision": ("AUTO_SILVER_OBSERVATION"
                            if status == "TEMPORAL_SUPPORTED_AMBIGUOUS" else "NOT_ASSIGNED"),
            "physical_label": "NOT_INFERRED",
        }

    def _new_site(self, index, item, raw_sha256, footprint, dimensions):
        center = list(item["center_xy_px"])
        site_id = _identity(self.source_id, index, item["component_id"], center)
        if site_id in self._sites:
            raise TrackingError("duplicate deterministic site identity")
        blank = next((previous for previous in reversed(self._frames)
                      if previous["globally_blank_chromatic_frame"]), None)
        absence_frame = blank["frame_index"] if blank is not None else None
        footprint_hash = None
        if footprint:
            encoding = {"native_width": dimensions[0], "native_height": dimensions[1],
                        "encoding": "NATIVE_Y_TIMES_WIDTH_PLUS_X", "pixels": sorted(footprint)}
            footprint_hash = hashlib.sha256(json.dumps(encoding, sort_keys=True,
                                                       separators=(",", ":")).encode("utf-8")).hexdigest()
            self._anchor_footprints[site_id] = footprint
        site = {
            "site_id": site_id, "source_id": self.source_id,
            "acquisition_id": self.acquisition_id,
            "canonical_center_xy_px": center,
            "canonical_center_anchor": "FIRST_DIRECT_VALID_OBSERVATION",
            "first_direct_valid_frame": index,
            "first_confident_annotation_frame": index,
            "first_direct_component_id": item["component_id"],
            "first_direct_raw_frame_sha256": raw_sha256,
            "first_direct_chroma_footprint_sha256": footprint_hash,
            "first_direct_chroma_footprint_pixel_count": len(footprint) if footprint else None,
            "footprint_support_rule": "COMPLETE_FIRST_DIRECT_SUBSET_WITHOUT_TRANSLATION",
            "last_confident_marker_absence_frame": absence_frame,
            "last_confident_marker_absence_raw_sha256": blank["raw_frame_sha256"] if blank else None,
            "transition_interval": {
                "lower_frame_exclusive": absence_frame, "upper_frame_inclusive": index,
                "status": "DOCUMENTARY_BRACKET" if blank else "LEFT_BOUND_NOT_ESTABLISHED",
                "duration_s": 118 * (index - absence_frame) / 100 if blank else None,
                "semantics": "DOCUMENTARY_ANNOTATION_NOT_PHYSICAL_ONSET",
            },
            "absence_status": "EXPLICIT_GLOBALLY_BLANK_CHROMATIC_FRAME" if blank else "NOT_ESTABLISHED",
            "has_identity_conflict": False, "conflict_frames": [],
            "direct_observations": [],
            "annotation_semantics": "PUBLISHED_FRAGMENTATION_LOCATION",
        }
        self._sites[site_id] = site
        for previous in self._frames:
            status = ("PRE_FIRST_CONFIDENT_ANNOTATION"
                      if previous["frame_processing_status"] == "PROCESSED" else "INVALID_FRAME")
            self._observations.append(self._observation(
                site, previous["frame_index"], status, [], previous["raw_frame_sha256"]))
        return site_id

    def add_frame(self, frame_index, detector_result, raw_sha256, frame_status="PROCESSED"):
        if self._finished:
            raise TrackingError("finished tracker cannot accept another frame")
        if type(frame_index) is not int or frame_index != len(self._frames):
            raise TrackingError("frames must arrive exactly once in contiguous order from zero")
        if frame_index >= self.expected_frames or frame_status not in FRAME_STATUSES:
            raise TrackingError("frame is outside the declared coverage or has unknown status")
        if raw_sha256 is not None and not _sha(raw_sha256):
            raise TrackingError("raw hash must be a lowercase SHA-256 or null for failed frames")
        if frame_status == "PROCESSED":
            if not _sha(raw_sha256):
                raise TrackingError("processed frame requires provenance hash")
            components = _validated_components(detector_result)
            footprints = _validated_footprints(detector_result, components)
        else:
            if detector_result is not None:
                raise TrackingError("failed frame cannot contribute detector results")
            components = []
            footprints = {}

        frame = {
            "source_id": self.source_id, "acquisition_id": self.acquisition_id,
            "frame_index": frame_index, **self._time(frame_index),
            "frame_processing_status": frame_status, "raw_frame_sha256": raw_sha256,
            "component_count": len(components),
            "valid_circle_count": sum(c["classification"] == VALID for c in components),
            "ambiguous_component_count": sum(c["classification"] == AMBIGUOUS for c in components),
            "small_component_count": sum(c["classification"] == SMALL for c in components),
            "colored_pixel_count": detector_result.get("colored_pixel_count") if detector_result else None,
            "globally_blank_chromatic_frame": (
                frame_status == "PROCESSED" and not components
                and type(detector_result.get("colored_pixel_count")) is int
                and detector_result["colored_pixel_count"] == 0),
        }
        prior_sites = list(self._sites)
        valid = [item for item in components if item["classification"] == VALID]
        edges = {
            item["component_id"]: [sid for sid in prior_sites
                                   if _distance(item["center_xy_px"],
                                                self._sites[sid]["canonical_center_xy_px"]) <= TOLERANCE_PX]
            for item in valid
        }
        reverse = {sid: [cid for cid, candidates in edges.items() if sid in candidates]
                   for sid in prior_sites}
        unmatched = [item for item in valid if not edges[item["component_id"]]]
        birth_conflicts = {
            item["component_id"]: [other["component_id"] for other in valid
                                   if other["component_id"] != item["component_id"]
                                   and _distance(item["center_xy_px"], other["center_xy_px"]) <= TOLERANCE_PX]
            for item in unmatched
        }
        spatial_conflicts = {cid: set(neighbours) for cid, neighbours in birth_conflicts.items()}
        for cid, neighbours in birth_conflicts.items():
            for other_id in neighbours:
                spatial_conflicts.setdefault(other_id, set()).add(cid)
        assigned = {}
        conflicted_sites = set()
        candidate_conflicts = 0
        for item in components:
            cid = item["component_id"]
            item.update({"source_id": self.source_id, "acquisition_id": self.acquisition_id,
                         "frame_index": frame_index, **self._time(frame_index),
                         "raw_frame_sha256": raw_sha256,
                         "component_key": f"{self.source_id}:{frame_index}:{cid}"})
            if item["classification"] != VALID:
                continue
            candidates = edges[cid]
            if spatial_conflicts.get(cid):
                sid = None
                reason = "CONFLICT"
                conflicted_sites.update(candidates)
                candidate_conflicts += 1
            elif len(candidates) == 1 and len(reverse[candidates[0]]) == 1:
                sid = candidates[0]
                reason = "RECIPROCAL_SINGLETON_CANONICAL_MATCH"
            elif candidates:
                sid = None
                reason = "CONFLICT"
                conflicted_sites.update(candidates)
                candidate_conflicts += 1
            else:
                sid = self._new_site(frame_index, item, raw_sha256, footprints.get(cid),
                                     (detector_result.get("native_width"), detector_result.get("native_height")))
                reason = "FIRST_DIRECT_VALID_NEW_SITE"
            item.update({"temporal_classification": reason, "assigned_site_id": sid,
                         "candidate_site_ids": list(candidates),
                         "same_frame_conflicting_component_ids": sorted(spatial_conflicts.get(cid, []))})
            self._links.append({
                "component_key": item["component_key"], "source_id": self.source_id,
                "frame_index": frame_index, "component_id": cid,
                "site_id": sid, "candidate_site_ids": list(candidates), "status": reason,
                "same_frame_conflicting_component_ids": sorted(spatial_conflicts.get(cid, [])),
            })
            if sid is not None:
                assigned[sid] = cid
                self._sites[sid]["direct_observations"].append({
                    "frame_index": frame_index, "component_id": cid,
                    "component_key": item["component_key"],
                    "center_xy_px": list(item["center_xy_px"]),
                    "raw_frame_sha256": raw_sha256,
                })

        support = {sid: [] for sid in prior_sites}
        for item in components:
            if item["classification"] == VALID:
                continue
            containing = [sid for sid in prior_sites
                          if _contains(item["bbox_xyxy"], self._sites[sid]["canonical_center_xy_px"])]
            distances = {sid: _bbox_distance(item["bbox_xyxy"], self._sites[sid]["canonical_center_xy_px"])
                         for sid in prior_sites}
            minimum_distance = min(distances.values()) if distances else None
            item["known_site_bbox_proximity"] = {
                "minimum_bbox_envelope_distance_px": minimum_distance,
                "minimum_distance_site_ids": [sid for sid, distance in distances.items()
                                              if distance == minimum_distance],
                "containing_canonical_center_site_ids": containing,
                "sites_examined": len(prior_sites),
                "distance_used_for_assignment": False,
            }
            current_footprint = footprints.get(item["component_id"], frozenset())
            supported = [sid for sid in prior_sites
                         if item["classification"] == AMBIGUOUS
                         and self._anchor_footprints.get(sid)
                         and self._anchor_footprints[sid].issubset(current_footprint)]
            item["supported_site_ids"] = supported
            item["support_rule"] = "COMPLETE_FIRST_DIRECT_SUBSET_WITHOUT_TRANSLATION"
            item["current_chroma_footprint_available"] = bool(current_footprint)
            item["temporal_context"] = "ONLY_SITES_DIRECTLY_ESTABLISHED_BEFORE_THIS_FRAME"
            item["potential_additional_site_unresolved"] = True
            if not supported:
                item["temporal_classification"] = "POTENTIAL_NEW_SITE_UNRESOLVED"
            elif len(supported) == 1:
                item["temporal_classification"] = "EXPLAINED_BY_KNOWN_SITE"
            else:
                item["temporal_classification"] = "EXPLAINED_BY_MULTIPLE_KNOWN_SITES"
            item["overlap_status"] = ("OVERLAP_WITH_KNOWN_TRACKS"
                                      if supported
                                      else "NOT_ESTABLISHED")
            if item["classification"] == AMBIGUOUS:
                for sid in supported:
                    support[sid].append(item["component_id"])

        for sid, site in self._sites.items():
            if frame_status != "PROCESSED":
                status, ids = "INVALID_FRAME", []
            elif sid in conflicted_sites:
                site["has_identity_conflict"] = True
                site["conflict_frames"].append(frame_index)
                status, ids = "CONFLICT", reverse[sid]
            elif sid in assigned:
                status, ids = "DIRECT_VALID", [assigned[sid]]
            elif support.get(sid):
                status, ids = "TEMPORAL_SUPPORTED_AMBIGUOUS", support[sid]
            else:
                status, ids = "PERSISTENCE_EXPECTED_UNRESOLVED", []
            self._observations.append(self._observation(site, frame_index, status, ids, raw_sha256))
        self._candidates.extend(components)
        frame["new_sites"] = len(self._sites) - len(prior_sites)
        frame["valid_identity_conflict_components"] = candidate_conflicts
        frame["established_sites_after_frame"] = len(self._sites)
        self._frames.append(frame)

    def finish(self):
        if self._finished:
            raise TrackingError("tracker already finalized")
        self._finished = True
        observations = sorted(self._observations,
                              key=lambda row: (row["frame_index"], row["site_id"]))
        states = Counter(row["status"] for row in observations)
        sites = list(self._sites.values())
        for site in sites:
            relevant = [row for row in observations if row["site_id"] == site["site_id"]]
            site["observation_status_counts"] = dict(sorted(Counter(r["status"] for r in relevant).items()))
            site["direct_observation_count"] = len(site["direct_observations"])
            site["auto_gold_site"] = bool(site["direct_observations"]) and not site["has_identity_conflict"]
            site["site_quality"] = "AUTO_GOLD_SITE" if site["auto_gold_site"] else "CONFLICTED_SITE"
            site["source_provenance_complete"] = bool(site["first_direct_raw_frame_sha256"])
        frames_processed = sum(row["frame_processing_status"] == "PROCESSED" for row in self._frames)
        last_by_site = {}
        loss_transitions = 0
        for row in observations:
            previous = last_by_site.get(row["site_id"])
            if (row["status"] == "PERSISTENCE_EXPECTED_UNRESOLVED"
                    and previous in ("DIRECT_VALID", "TEMPORAL_SUPPORTED_AMBIGUOUS")):
                loss_transitions += 1
            last_by_site[row["site_id"]] = row["status"]
        summary = {
            "source_id": self.source_id, "acquisition_id": self.acquisition_id,
            "frames_expected": self.expected_frames, "frames_accounted": len(self._frames),
            "frames_processed": frames_processed,
            "frame_coverage_complete": frames_processed == self.expected_frames,
            "frame_accounting_complete": len(self._frames) == self.expected_frames,
            "unique_sites": len(sites),
            "unique_auto_gold_sites": sum(site["auto_gold_site"] for site in sites),
            "direct_valid_observations": states["DIRECT_VALID"],
            "valid_detector_components": sum(f["valid_circle_count"] for f in self._frames),
            "auto_silver_observations": states["TEMPORAL_SUPPORTED_AMBIGUOUS"],
            "ambiguous_observations": sum(f["ambiguous_component_count"] for f in self._frames),
            "small_components": sum(f["small_component_count"] for f in self._frames),
            "site_frame_records": len(observations),
            "pre_annotation_records": states["PRE_FIRST_CONFIDENT_ANNOTATION"],
            "persistence_expected_records": states["PERSISTENCE_EXPECTED_UNRESOLVED"],
            "conflict_records": states["CONFLICT"],
            "valid_identity_conflict_components": sum(f["valid_identity_conflict_components"] for f in self._frames),
            "invalid_frame_records": states["INVALID_FRAME"],
            "unexpected_graphical_disappearance_count": loss_transitions,
            "disappearance_count_unit": "SITE_TRANSITION_FROM_SUPPORTED_TO_UNRESOLVED",
            "candidate_records": len(self._candidates),
            "overlap_with_known_tracks_components": sum(c.get("overlap_status") == "OVERLAP_WITH_KNOWN_TRACKS" for c in self._candidates),
            "potential_new_site_unresolved_components": sum(c.get("potential_additional_site_unresolved", False) for c in self._candidates),
            "source_provenance_complete": all(site["source_provenance_complete"] for site in sites),
            "deterministic_id_completeness": len({s["site_id"] for s in sites}) == len(sites),
            "observation_status_counts": dict(sorted(states.items())),
            "temporal_delta_executed": False, "human_review_used": False,
            "hough_executed": False, "negative_labels_created": 0,
            "physical_events_inferred": 0,
        }
        if len(observations) != len(sites) * len(self._frames):
            raise TrackingError("site/frame accounting invariant failed")
        self._anchor_footprints.clear()
        return copy.deepcopy({"sites": sites, "observations": observations,
                              "candidate_components": self._candidates,
                              "frames": self._frames, "summary": summary,
                              "component_site_links": self._links})
