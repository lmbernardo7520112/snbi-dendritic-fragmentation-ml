"""Pure graphical-annotation diagnostics for the bounded TI3-A0 audit.

Inputs are caller-supplied native YUV420p chroma planes. This module has no I/O,
authority activation, luminance processing, physical masks, or ML labels.
A geometrically admissible circle is only a graphical candidate: its shape
cannot distinguish an annotation from a circular text glyph. Persistence is
observed only at the supplied instants and never establishes physical onset.
"""

import math


VALID = "VALID_GRAPHICAL_CIRCLE"
AMBIGUOUS = "AMBIGUOUS_OR_NONCIRCULAR"
SMALL = "SMALL_COMPONENT"
ANGULAR_BINS = 36
CONFIG_KEYS = frozenset({
    "chroma_distance", "minimum_component_pixels", "minimum_radius",
    "maximum_radius", "maximum_axis_ratio", "maximum_radial_p95",
    "minimum_angular_coverage",
})


class AnnotationDiagnosticError(ValueError):
    """Malformed input cannot produce a graphical or persistence decision."""


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_config(config):
    """Validate explicit parameters; no experimental defaults are supplied."""
    if not isinstance(config, dict) or set(config) != CONFIG_KEYS:
        raise AnnotationDiagnosticError("configuration must contain exactly the documented keys")
    if type(config["chroma_distance"]) is not int or not 1 <= config["chroma_distance"] <= 128:
        raise AnnotationDiagnosticError("chroma_distance must be an integer in [1, 128]")
    if type(config["minimum_component_pixels"]) is not int or config["minimum_component_pixels"] < 1:
        raise AnnotationDiagnosticError("minimum_component_pixels must be a positive integer")
    for key in CONFIG_KEYS - {"chroma_distance", "minimum_component_pixels"}:
        if not _number(config[key]):
            raise AnnotationDiagnosticError(f"{key} must be a finite number, excluding bool")
    if not 0 < config["minimum_radius"] <= config["maximum_radius"]:
        raise AnnotationDiagnosticError("radius bounds must be positive and ordered")
    if config["maximum_axis_ratio"] < 1 or config["maximum_radial_p95"] < 0:
        raise AnnotationDiagnosticError("axis ratio must be >=1 and radial p95 must be >=0")
    if not 0 < config["minimum_angular_coverage"] <= 1:
        raise AnnotationDiagnosticError("angular coverage must be in (0, 1]")


def extract_graphical_markers(u, v, width, height, config):
    """Return every 8-connected chromatic component, without exporting masks.

    Chroma samples expand into their native 2x2 pixel blocks. Coordinates are
    native pixel centres with integer x/y; bboxes use exclusive upper bounds.
    Least-squares radii, radial thickness and fit errors describe drawn ink,
    not fragments, confidence intervals, registration or physical uncertainty.
    Any topology with other than one enclosed hole remains ambiguous, so
    overlapping circles are retained together rather than silently separated.
    """
    validate_config(config)
    if any(type(n) is not int or n < 2 or n % 2 for n in (width, height)):
        raise AnnotationDiagnosticError("native YUV420p dimensions must be positive even integers")
    import numpy as np
    from scipy import ndimage

    u, v = np.asarray(u), np.asarray(v)
    expected_shape = (height // 2, width // 2)
    if any(p.shape != expected_shape or p.dtype != np.dtype("uint8") for p in (u, v)):
        raise AnnotationDiagnosticError("U and V must be uint8 chroma planes at native half resolution")
    distance = np.maximum(np.abs(u.astype(np.int16) - 128), np.abs(v.astype(np.int16) - 128))
    chromatic = distance >= config["chroma_distance"]
    mask = np.repeat(np.repeat(chromatic, 2, axis=0), 2, axis=1)
    structure = np.ones((3, 3), dtype=bool)
    labels, count = ndimage.label(mask, structure=structure)
    components = []
    for component_id, box in enumerate(ndimage.find_objects(labels), 1):
        ys, xs = box
        local = labels[box] == component_id
        yy, xx = np.nonzero(local)
        x, y = xx.astype(float) + xs.start, yy.astype(float) + ys.start
        x0, y0, x1, y1 = xs.start, ys.start, xs.stop, ys.stop
        axis_ratio = max(x1-x0, y1-y0) / min(x1-x0, y1-y0)
        touches_boundary = x0 == 0 or y0 == 0 or x1 == width or y1 == height
        holes = ndimage.binary_fill_holes(local) & ~local
        _, hole_count = ndimage.label(holes, structure=structure)
        item = {
            "component_id": component_id,
            "bbox_xyxy": [x0, y0, x1, y1],
            "area_px": int(x.size),
            "center_xy_px": None,
            "radius_graphical_px": None,
            "radial_median_px": None,
            "radial_error_p95_px": None,
            "radial_thickness_p05_p95_px": None,
            "angular_bins_occupied": 0,
            "angular_bins_total": ANGULAR_BINS,
            "angular_coverage": 0.0,
            "axis_ratio": float(axis_ratio),
            "touches_boundary": bool(touches_boundary),
            "enclosed_hole_count": int(hole_count),
            "classification": AMBIGUOUS,
            "reasons": [],
            "semantic_label": "UNKNOWN",
            "physical_extent": "NOT_INFERRED",
        }
        # Centre coordinates before fitting to avoid unnecessary conditioning
        # from an arbitrary native-canvas origin.
        mx, my = float(x.mean()), float(y.mean())
        dx, dy = x-mx, y-my
        design = np.column_stack((2*dx, 2*dy, np.ones(x.size)))
        solution, _, rank, _ = np.linalg.lstsq(design, dx*dx + dy*dy, rcond=None)
        radius_squared = solution[2] + solution[0]**2 + solution[1]**2
        if rank == 3 and np.isfinite(solution).all() and radius_squared > 0:
            cx, cy = float(solution[0]+mx), float(solution[1]+my)
            radius = float(math.sqrt(radius_squared))
            radial = np.hypot(x-cx, y-cy)
            angles = (np.arctan2(y-cy, x-cx) + 2*math.pi) % (2*math.pi)
            bins = np.floor(angles * ANGULAR_BINS / (2*math.pi)).astype(int)
            occupied = int(np.unique(bins).size)
            item.update({
                "center_xy_px": [cx, cy],
                "radius_graphical_px": radius,
                "radial_median_px": float(np.median(radial)),
                "radial_error_p95_px": float(np.percentile(np.abs(radial-radius), 95)),
                "radial_thickness_p05_p95_px": float(np.percentile(radial, 95)-np.percentile(radial, 5)),
                "angular_bins_occupied": occupied,
                "angular_coverage": occupied / ANGULAR_BINS,
            })
        else:
            item["reasons"].append("DEGENERATE_CIRCLE_FIT")
        if x.size < config["minimum_component_pixels"]:
            item["reasons"].append("BELOW_MINIMUM_COMPONENT_PIXELS")
        if touches_boundary:
            item["reasons"].append("TOUCHES_NATIVE_BOUNDARY")
        if hole_count != 1:
            item["reasons"].append("TOPOLOGY_NOT_ONE_ENCLOSED_HOLE")
        if axis_ratio > config["maximum_axis_ratio"]:
            item["reasons"].append("AXIS_RATIO_EXCEEDS_LIMIT")
        if item["radius_graphical_px"] is not None:
            if not config["minimum_radius"] <= item["radius_graphical_px"] <= config["maximum_radius"]:
                item["reasons"].append("GRAPHICAL_RADIUS_OUTSIDE_LIMITS")
            if item["radial_error_p95_px"] > config["maximum_radial_p95"]:
                item["reasons"].append("RADIAL_ERROR_EXCEEDS_LIMIT")
            if item["angular_coverage"] < config["minimum_angular_coverage"]:
                item["reasons"].append("INSUFFICIENT_ANGULAR_COVERAGE")
        if x.size < config["minimum_component_pixels"]:
            item["classification"] = SMALL
        elif not item["reasons"]:
            item["classification"] = VALID
        components.append(item)
    return {
        "native_width": width,
        "native_height": height,
        "coordinate_convention": "native_integer_pixel_centres_xy_bbox_upper_exclusive",
        "chroma_expansion": "one_sample_to_native_2x2_block",
        "colored_chroma_sample_count": int(chromatic.sum()),
        "colored_pixel_count": int(mask.sum()),
        "component_count": int(count),
        "valid_circle_count": sum(c["classification"] == VALID for c in components),
        "ambiguous_component_count": sum(c["classification"] == AMBIGUOUS for c in components),
        "small_component_count": sum(c["classification"] == SMALL for c in components),
        "components": components,
        "absence_semantics": "UNKNOWN_NOT_A_NEGATIVE_LABEL",
        "semantic_validation": "NOT_PERFORMED",
    }


def _validate_frames(frames):
    if not isinstance(frames, list) or not frames:
        raise AnnotationDiagnosticError("frames must be a nonempty ordered list")
    source_id = frames[0].get("source_id") if isinstance(frames[0], dict) else None
    if not isinstance(source_id, str) or not source_id:
        raise AnnotationDiagnosticError("one explicit source_id is required")
    previous_index = -1
    for frame in frames:
        if not isinstance(frame, dict) or frame.get("source_id") != source_id:
            raise AnnotationDiagnosticError("persistence cannot mix sources")
        index = frame.get("frame_index")
        if type(index) is not int or index <= previous_index:
            raise AnnotationDiagnosticError("frame indices must be nonnegative and strictly increasing")
        previous_index = index
        components = frame.get("components")
        if not isinstance(components, list):
            raise AnnotationDiagnosticError("each frame must retain its full component list")
        ids = set()
        for component in components:
            if not isinstance(component, dict):
                raise AnnotationDiagnosticError("components must be dictionaries")
            cid = component.get("component_id")
            if type(cid) is not int or cid < 1 or cid in ids:
                raise AnnotationDiagnosticError("component_id must be unique and positive within each frame")
            ids.add(cid)
            if component.get("classification") not in (VALID, AMBIGUOUS, SMALL):
                raise AnnotationDiagnosticError("unknown component classification")
            if component["classification"] == VALID:
                center = component.get("center_xy_px")
                if not isinstance(center, (tuple, list)) or len(center) != 2 or not all(_number(n) for n in center):
                    raise AnnotationDiagnosticError("valid graphical circle requires finite native x/y")


def match_persistence(frames, tolerance_px):
    """Match only reciprocal singleton neighbours between sampled instants.

    All candidates within tolerance are retained: no nearest-neighbour rescue,
    temporal gap filling or assignment of ambiguous identity is performed.
    A new track records first observation in this sample, never first physical
    appearance. Any unresolved graphical component prevents a global PASS.
    """
    if not _number(tolerance_px) or tolerance_px < 0:
        raise AnnotationDiagnosticError("tolerance_px must be finite and nonnegative")
    _validate_frames(frames)
    source_id = frames[0]["source_id"]
    transitions, observations, tracks = [], [], {}
    observation_map = {}
    next_track = 1

    def add_observation(frame, component, track_id, reason):
        nonlocal next_track
        index, cid = frame["frame_index"], component["component_id"]
        if track_id == "NEW":
            track_id = f"{source_id}:sampled-graphic-{next_track:04d}"
            next_track += 1
            tracks[track_id] = {
                "track_id": track_id,
                "first_observed_frame_index": index,
                "physical_onset_frame_index": None,
                "event_label": "UNKNOWN",
                "observations": [],
            }
        observation = {
            "frame_index": index, "component_id": cid,
            "center_xy_px": list(component["center_xy_px"]),
            "track_id": track_id, "identity_status": reason,
            "physical_onset_frame_index": None,
        }
        observations.append(observation)
        observation_map[(index, cid)] = observation
        if track_id is not None:
            tracks[track_id]["observations"].append({"frame_index": index, "component_id": cid})

    for component in frames[0]["components"]:
        if component["classification"] == VALID:
            add_observation(frames[0], component, "NEW", "FIRST_OBSERVED_IN_SAMPLE")
    for previous, current in zip(frames, frames[1:]):
        left = [c for c in previous["components"] if c["classification"] == VALID]
        right = [c for c in current["components"] if c["classification"] == VALID]
        left_candidates = {c["component_id"]: [] for c in left}
        right_candidates = {c["component_id"]: [] for c in right}
        candidate_edges = []
        for a in left:
            for b in right:
                distance = math.hypot(*(x-y for x, y in zip(a["center_xy_px"], b["center_xy_px"])))
                if distance <= tolerance_px:
                    aid, bid = a["component_id"], b["component_id"]
                    left_candidates[aid].append(bid)
                    right_candidates[bid].append(aid)
                    candidate_edges.append({"previous_component_id": aid, "current_component_id": bid,
                                            "center_distance_px": distance})
        links = [edge for edge in candidate_edges
                 if len(left_candidates[edge["previous_component_id"]]) == 1
                 and len(right_candidates[edge["current_component_id"]]) == 1]
        linked_left = {edge["previous_component_id"] for edge in links}
        linked_right = {edge["current_component_id"] for edge in links}
        ambiguous_edges = [edge for edge in candidate_edges
                           if edge["previous_component_id"] not in linked_left]
        for component in right:
            cid = component["component_id"]
            if cid in linked_right:
                previous_id = right_candidates[cid][0]
                prior = observation_map[(previous["frame_index"], previous_id)]
                track_id = prior["track_id"]
                reason = "RECIPROCAL_UNIQUE_SAMPLED_MATCH" if track_id else "UNRESOLVED_PREVIOUS_IDENTITY"
            elif right_candidates[cid]:
                track_id, reason = None, "AMBIGUOUS_SPATIAL_MATCH"
            else:
                track_id, reason = "NEW", "FIRST_OBSERVED_IN_SAMPLE"
            add_observation(current, component, track_id, reason)
        unresolved_previous = [c["component_id"] for c in previous["components"] if c["classification"] != VALID]
        unresolved_current = [c["component_id"] for c in current["components"] if c["classification"] != VALID]
        missing = [c["component_id"] for c in left if not left_candidates[c["component_id"]]]
        transitions.append({
            "previous_frame_index": previous["frame_index"],
            "current_frame_index": current["frame_index"],
            "candidate_edges": candidate_edges,
            "links": links,
            "ambiguous_edges": ambiguous_edges,
            "unmatched_previous_component_ids": [c["component_id"] for c in left if c["component_id"] not in linked_left],
            "unmatched_current_component_ids": [c["component_id"] for c in right if c["component_id"] not in linked_right],
            "not_observed_next_sample_component_ids": missing,
            "unresolved_previous_component_ids": unresolved_previous,
            "unresolved_current_component_ids": unresolved_current,
            "graphical_persistence_status": (
                "UNRESOLVED_GRAPHICAL_AMBIGUITY" if ambiguous_edges or unresolved_previous or unresolved_current else
                "FAIL_SAMPLED_GRAPHICAL_DISAPPEARANCE" if missing else
                "PASS_SAMPLED_GRAPHICAL_PERSISTENCE" if left else "NOT_ASSESSABLE_NO_PREVIOUS_CIRCLE"
            ),
        })
    unresolved_components = [
        {"frame_index": f["frame_index"], "component_id": c["component_id"], "classification": c["classification"]}
        for f in frames for c in f["components"] if c["classification"] != VALID
    ]
    if unresolved_components or any(t["ambiguous_edges"] for t in transitions):
        status = "UNRESOLVED_GRAPHICAL_AMBIGUITY"
    elif any(t["not_observed_next_sample_component_ids"] for t in transitions):
        status = "FAIL_SAMPLED_GRAPHICAL_DISAPPEARANCE"
    elif any(t["links"] for t in transitions):
        status = "PASS_SAMPLED_GRAPHICAL_PERSISTENCE"
    else:
        status = "NOT_ASSESSABLE"
    return {
        "source_id": source_id,
        "frame_indices": [f["frame_index"] for f in frames],
        "tolerance_px": tolerance_px,
        "cumulative_status": status,
        "cumulative_semantics": "NOT_INFERRED_FROM_GRAPHICS",
        "observations": observations,
        "trajectories": list(tracks.values()),
        "transitions": transitions,
        "unresolved_components": unresolved_components,
        "negative_labels_created": 0,
        "physical_events_inferred": 0,
        "scope": "supplied_sampled_instants_only",
    }
