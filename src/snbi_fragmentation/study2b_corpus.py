"""Pure Study2-B corpus planning and native-pair admission.

No I/O, decoding, annotation extraction, registration, learning or feature
extraction occurs here. The controller owns authority, authenticated inputs,
one-shot execution, storage and immutable output ledgers. The only array
operations implement historical support predicates and unchanged uint8 crops.
All rectangles are half-open integer pixel bounds, including safety regions.
"""

from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import math


PATCH_RADIUS = 32
PATCH_SIDE = 65
BACKGROUND_SAFETY_MARGIN = 3
DIMENSIONS = {"ESM1": (1278, 1018), "ESM4": (1278, 1012)}
FRAME_COUNTS = {"ESM1": 294, "ESM4": 395}
SOURCE_MAP = {"ESM3": "ESM1", "ESM6": "ESM4"}
SOLUTE_SOURCE = {"ESM1": "ESM2", "ESM4": "ESM5"}
ACQUISITIONS = {
    "ESM1": "bottom_up_anti_parallel", "ESM4": "top_down_parallel",
}
TIERS = {
    "DIRECT_VALID": "GOLD",
    "TEMPORAL_SUPPORTED_AMBIGUOUS": "SILVER",
    "PRE_FIRST_CONFIDENT_ANNOTATION": "UNLABELED_PRE",
    "PERSISTENCE_EXPECTED_UNRESOLVED": "UNLABELED_PERSISTENCE",
}
METRIC_NAMES = frozenset({
    "AMBIGUOUS_COMPONENTS_TOTAL", "AMBIGUOUS_UNSUPPORTED_BY_KNOWN_SITE",
    "AMBIGUOUS_EXPLAINED_BY_ONE_KNOWN_SITE",
    "AMBIGUOUS_EXPLAINED_BY_MULTIPLE_KNOWN_SITES", "SMALL_COMPONENTS_TOTAL",
    "UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS", "NON_VALID_COMPONENTS_TOTAL",
})
COMPONENT_CLASSES = frozenset({"VALID_GRAPHICAL_CIRCLE", "AMBIGUOUS_OR_NONCIRCULAR", "SMALL_COMPONENT"})
ORDER_FIELDS = ["acquisition_id", "frame_index", "site_id", "supervision_tier"]


class CorpusContractError(ValueError):
    """Metadata divergence or malformed native bytes; no fallback is allowed."""


def _require(condition, message):
    if not condition:
        raise CorpusContractError(message)


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _sha(value):
    return (type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def patch_xyxy(x, y):
    """Exactly [y-32:y+33, x-32:x+33], represented as xyxy."""
    _require(type(x) is int and type(y) is int, "integer canonical crop center required")
    return [x - PATCH_RADIUS, y - PATCH_RADIUS, x + PATCH_RADIUS + 1,
            y + PATCH_RADIUS + 1]


def support_xyxy(width, height):
    """Historical 12%/15% bands, border four and one-pixel erosion."""
    return [5, max(4, math.ceil(height * 0.12)) + 1,
            width - 5, height - max(4, math.ceil(height * 0.15)) - 1]


def _box(value):
    _require(type(value) in (list, tuple) and len(value) == 4
             and all(type(v) is int for v in value)
             and value[0] < value[2] and value[1] < value[3],
             "nonempty half-open integer rectangle required")
    return list(value)


def _expanded(box, margin=BACKGROUND_SAFETY_MARGIN):
    return [box[0] - margin, box[1] - margin, box[2] + margin, box[3] + margin]


def _intersects(a, b):
    # Contact of documentary envelopes is also blocked, conservatively. The
    # right/bottom values remain exclusive for slicing but boundary touch does
    # not create an admissible background gap.
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def _inside(box, outer):
    return (outer[0] <= box[0] < box[2] <= outer[2]
            and outer[1] <= box[1] < box[3] <= outer[3])


def _pixel_distance(a, b):
    """Euclidean distance between closed pixel-center envelopes, zero on overlap."""
    dx = max(a[0] - (b[2] - 1), b[0] - (a[2] - 1), 0)
    dy = max(a[1] - (b[3] - 1), b[1] - (a[3] - 1), 0)
    return math.hypot(dx, dy)


def _source_frame(source, frame):
    _require(source in DIMENSIONS, "only structural ESM1/ESM4 pair keys allowed")
    _require(type(frame) is int and 0 <= frame < FRAME_COUNTS[source],
             "frame outside frozen acquisition extent")
    return f"{source}:{frame}"


def _metrics(candidates, canonical_metrics):
    _require(type(canonical_metrics) is dict and set(canonical_metrics) == METRIC_NAMES,
             "consume exactly seven reconciled metric names")
    _require(all(type(v) is int and v >= 0 for v in canonical_metrics.values()),
             "canonical counts must be nonnegative integers")
    counts = Counter()
    for component in candidates:
        classification = component.get("classification")
        _require(classification in COMPONENT_CLASSES, "unknown graphical component class")
        counts[classification] += 1
        if classification == "AMBIGUOUS_OR_NONCIRCULAR":
            temporal = component.get("temporal_classification")
            _require(temporal in {"POTENTIAL_NEW_SITE_UNRESOLVED", "EXPLAINED_BY_KNOWN_SITE",
                                  "EXPLAINED_BY_MULTIPLE_KNOWN_SITES"},
                     "unknown reconciled ambiguous population")
            counts[temporal] += 1
        elif classification == "SMALL_COMPONENT":
            _require(component.get("temporal_classification") == "POTENTIAL_NEW_SITE_UNRESOLVED",
                     "SMALL corpus semantics diverged from frozen reconciliation")
    expected = {
        "AMBIGUOUS_COMPONENTS_TOTAL": counts["AMBIGUOUS_OR_NONCIRCULAR"],
        "AMBIGUOUS_UNSUPPORTED_BY_KNOWN_SITE": counts["POTENTIAL_NEW_SITE_UNRESOLVED"],
        "AMBIGUOUS_EXPLAINED_BY_ONE_KNOWN_SITE": counts["EXPLAINED_BY_KNOWN_SITE"],
        "AMBIGUOUS_EXPLAINED_BY_MULTIPLE_KNOWN_SITES": counts["EXPLAINED_BY_MULTIPLE_KNOWN_SITES"],
        "SMALL_COMPONENTS_TOTAL": counts["SMALL_COMPONENT"],
        "UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS": counts["POTENTIAL_NEW_SITE_UNRESOLVED"] + counts["SMALL_COMPONENT"],
        "NON_VALID_COMPONENTS_TOTAL": counts["AMBIGUOUS_OR_NONCIRCULAR"] + counts["SMALL_COMPONENT"],
    }
    _require(expected == canonical_metrics, "frozen candidate populations differ from canonical metrics")


def build_plan(site_doc, observations, candidates, canonical_metrics):
    """Produce a deterministic, JSON-serializable plan from authenticated texts.

    The controller additionally enforces the production 87/27396 cardinalities
    and hashes. This pure routine validates record identities and reconciled
    populations, and never accesses an annotation source or rebuilds its labels.
    """
    _require(type(site_doc) is list and site_doc and type(observations) is list
             and observations and type(candidates) is list, "explicit frozen ledgers required")
    _metrics(candidates, canonical_metrics)
    sites, global_boxes = {}, {source: [] for source in DIMENSIONS}
    for site in site_doc:
        sid, annotation_source = site.get("site_id"), site.get("source_id")
        _require(type(sid) is str and sid and sid not in sites and annotation_source in SOURCE_MAP,
                 "site identity absent, duplicated or outside annotation mapping")
        source = SOURCE_MAP[annotation_source]
        _require(site.get("acquisition_id") == ACQUISITIONS[source]
                 and site.get("auto_gold_site") is True
                 and site.get("has_identity_conflict") is False
                 and site.get("source_provenance_complete") is True,
                 "site must preserve AUTO_GOLD and acquisition provenance")
        point = site.get("canonical_center_xy_px")
        _require(type(point) is list and len(point) == 2 and all(_finite(v) for v in point),
                 "finite frozen canonical center required")
        _require(_sha(site.get("source_sha256")), "site annotation source hash required")
        x, y = (math.floor(v + 0.5) for v in point)
        sites[sid] = {"site": site, "source": source, "center": [x, y]}
        global_boxes[source].append({"site_id": sid, "bbox_xyxy": _expanded(patch_xyxy(x, y)),
                                     "exclusion_basis": "GLOBAL_ALL_TIME_AUTO_GOLD_SITE_PATCH_PLUS_MARGIN3"})
    for boxes in global_boxes.values():
        boxes.sort(key=lambda r: r["site_id"])

    component_boxes, candidate_ids = defaultdict(list), set()
    for component in candidates:
        annotation_source = component.get("source_id")
        _require(annotation_source in SOURCE_MAP, "component source outside frozen annotation mapping")
        source, frame = SOURCE_MAP[annotation_source], component.get("frame_index")
        key = _source_frame(source, frame)
        _require(component.get("acquisition_id") == ACQUISITIONS[source], "component acquisition differs")
        cid = component.get("component_id")
        identity = (annotation_source, frame, cid)
        _require(type(cid) is int and cid >= 1 and identity not in candidate_ids,
                 "component identity absent or duplicated")
        candidate_ids.add(identity)
        bbox = _box(component.get("bbox_xyxy"))
        supported = component.get("supported_site_ids", [])
        _require(type(supported) is list and all(sid in sites and sites[sid]["source"] == source
                                                for sid in supported),
                 "component support references an unknown or different-acquisition site")
        # Includes all ambiguous/small bboxes irrespective of historical boolean,
        # plus VALID components as conservative known-site temporal footprints.
        component_boxes[key].append({
            "component_id": cid, "component_key": component.get("component_key", f"{annotation_source}:{frame}:{cid}"),
            "bbox_xyxy": bbox, "classification": component["classification"],
            "supported_site_ids": list(supported),
            "exclusion_basis": ("KNOWN_SITE_TEMPORAL_COMPONENT_FOOTPRINT" if component["classification"] == "VALID_GRAPHICAL_CIRCLE"
                                else "ALL_AMBIGUOUS_AND_SMALL_COMPONENT_BBOXES"),
        })
    for boxes in component_boxes.values():
        boxes.sort(key=lambda r: r["component_id"])

    records, record_ids, count_by_site, supervised_by_site = [], set(), Counter(), Counter()
    for obs in observations:
        sid, frame, state = obs.get("site_id"), obs.get("frame_index"), obs.get("status")
        _require(sid in sites and state in TIERS, "unknown site or observation state")
        item = sites[sid]
        site, source = item["site"], item["source"]
        _source_frame(source, frame)
        identity = (sid, frame)
        _require(identity not in record_ids, "duplicate site/frame pair")
        record_ids.add(identity)
        _require(obs.get("source_id") == site["source_id"]
                 and obs.get("acquisition_id") == ACQUISITIONS[source]
                 and obs.get("canonical_center_xy_px") == site["canonical_center_xy_px"]
                 and obs.get("source_sha256") == site["source_sha256"],
                 "observation canonical center or cross-source provenance differs")
        _require(_finite(obs.get("experimental_time_s")) and _finite(obs.get("elapsed_time_s"))
                 and _sha(obs.get("raw_frame_sha256")), "temporal and annotation-frame provenance required")
        count_by_site[sid] += 1
        supervised_by_site[sid] += state in {"DIRECT_VALID", "TEMPORAL_SUPPORTED_AMBIGUOUS"}
        x, y = item["center"]
        records.append({
            "pair_id": f"{ACQUISITIONS[source]}|{sid}|{frame}", "site_id": sid,
            "group_id": f"{ACQUISITIONS[source]}|{sid}", "acquisition_id": ACQUISITIONS[source],
            "annotation_source_id": site["source_id"], "structural_source_id": source,
            "solutal_source_id": SOLUTE_SOURCE[source], "frame_index": frame,
            "experimental_time_s": obs["experimental_time_s"], "elapsed_time_s": obs["elapsed_time_s"],
            "canonical_center_xy_px": list(site["canonical_center_xy_px"]),
            "center_x": x, "center_y": y, "patch_xyxy": patch_xyxy(x, y),
            "mapping_offset_xy": [0, 0], "patch_radius_px": PATCH_RADIUS,
            "patch_side_px": PATCH_SIDE, "observation_state": state, "supervision_tier": TIERS[state],
            "channel_order": ["STRUCTURAL_Y", "RELATIVE_SOLUTE_FIELD_Y"],
            "annotation_provenance": deepcopy(obs),
        })
    _require(set(count_by_site) == set(sites), "every frozen site requires observations")
    for record in records:
        sid = record["site_id"]
        denominator = supervised_by_site[sid]
        _require(denominator > 0, "AUTO_GOLD site requires at least one supervised observation")
        record.update({"site_observation_count": count_by_site[sid],
                       "site_supervised_observation_count": denominator,
                       "candidate_equal_site_weight": 1.0 / denominator,
                       "weight_semantics": "PROSPECTIVE_METADATA_ONLY_NOT_APPLIED"})
    records.sort(key=lambda r: tuple(r[k] for k in ORDER_FIELDS))
    by_frame = defaultdict(list)
    for record in records:
        by_frame[_source_frame(record["structural_source_id"], record["frame_index"])].append(record)
    return {"schema_version": 1, "array_order_fields": list(ORDER_FIELDS), "records": records,
            "records_by_frame": dict(by_frame),
            "exclusion_metadata": {"global_site_boxes": global_boxes,
                                   "frame_component_boxes": dict(component_boxes)},
            "input_record_count": len(records), "site_count": len(sites),
            "tier_counts": dict(sorted(Counter(r["supervision_tier"] for r in records).items())),
            "canonical_metrics": dict(canonical_metrics)}


def native_luminance_and_support(raw, structural_source, *, structural):
    """Return unchanged Y and the historical mask; no file operation occurs."""
    _require(structural_source in DIMENSIONS and type(structural) is bool,
             "explicit structural source and modality required")
    width, height = DIMENSIONS[structural_source]
    count = width * height
    _require(type(raw) is bytes and len(raw) == count * 3 // 2,
             "complete immutable native YUV420p frame required")
    import numpy as np
    from scipy import ndimage

    values = np.frombuffer(raw, dtype=np.uint8)
    luminance = values[:count].reshape(height, width)
    if structural:
        u = values[count:count + count // 4].reshape(height // 2, width // 2).astype(np.int16)
        v = values[count + count // 4:].reshape(height // 2, width // 2).astype(np.int16)
        chroma = np.maximum(np.abs(u - 128), np.abs(v - 128)) >= 20
        overlay = chroma.repeat(2, axis=0).repeat(2, axis=1)
        overlay = ndimage.maximum_filter(overlay, size=11, mode="constant", cval=0)
        mask = ~overlay
    else:
        # The relative-solute field's color is scientific display content;
        # historical solutal admission never treats its chroma as an overlay.
        mask = np.ones((height, width), dtype=bool)
    top = max(4, math.ceil(height * 0.12))
    bottom = max(4, math.ceil(height * 0.15))
    mask[:top] = False
    mask[height - bottom:] = False
    mask[:, :4] = False
    mask[:, width - 4:] = False
    mask = ndimage.binary_erosion(mask, structure=np.ones((3, 3), dtype=bool), border_value=0)
    luminance.setflags(write=False)
    mask.setflags(write=False)
    return luminance, mask


def _admitted(box, mask, width, height):
    return (_inside(box, support_xyxy(width, height))
            and bool(mask[box[1]:box[3], box[0]:box[2]].all()))


def legacy_patch_pair(structural_raw, solutal_raw, structural_source, center_x, center_y):
    """Reproduce one explicit historical crop for compatibility, without ML.

    The historical fixture may be a background; this routine does not create
    a corpus record or authorize its use as a new background. The controller
    restricts this call to the exact historical source/frame/center fixtures.
    """
    box = patch_xyxy(center_x, center_y)
    structural_y, structural_mask = native_luminance_and_support(
        structural_raw, structural_source, structural=True)
    solute_y, solute_mask = native_luminance_and_support(
        solutal_raw, structural_source, structural=False)
    width, height = DIMENSIONS[structural_source]
    _require(_admitted(box, structural_mask, width, height)
             and _admitted(box, solute_mask, width, height),
             "BLOCKED_LEGACY_PAIR_REPRODUCTION: historical crop lacks complete support")
    import numpy as np
    x0, y0, x1, y1 = box
    pair = np.stack((structural_y[y0:y1, x0:x1], solute_y[y0:y1, x0:x1]), axis=0)
    _require(pair.dtype == np.dtype("uint8") and pair.shape == (2, PATCH_SIDE, PATCH_SIDE),
             "historical crop geometry differs")
    return {"structural_patch_sha256": hashlib.sha256(pair[0].tobytes(order="C")).hexdigest(),
            "solutal_patch_sha256": hashlib.sha256(pair[1].tobytes(order="C")).hexdigest(),
            "pair_sha256": hashlib.sha256(pair.tobytes(order="C")).hexdigest()}


def background_pool_for_frame(structural_source, frame_index, structural_mask,
                              solute_mask, exclusion_metadata):
    """Metadata-only pool over every admissible fixed grid location, no quota.

    Safety support is checked on the full patch expanded by three pixels.
    Exclusion uses the global all-time union of site patches, also expanded by
    three pixels, and every per-frame candidate component envelope. The latter
    includes all VALID footprints and every AMBIGUOUS/SMALL record.
    """
    key = _source_frame(structural_source, frame_index)
    width, height = DIMENSIONS[structural_source]
    _require(type(exclusion_metadata) is dict
             and set(exclusion_metadata.get("global_site_boxes", {})) == set(DIMENSIONS)
             and type(exclusion_metadata.get("frame_component_boxes")) is dict,
             "complete explicit exclusion metadata required")
    import numpy as np
    _require(all(isinstance(m, np.ndarray) and m.dtype == np.dtype("bool")
                 and m.shape == (height, width) for m in (structural_mask, solute_mask)),
             "native modality support masks required")
    global_boxes = exclusion_metadata["global_site_boxes"][structural_source]
    frame_boxes = exclusion_metadata["frame_component_boxes"].get(key, [])
    exclusions = [_box(item.get("bbox_xyxy")) for item in global_boxes + frame_boxes]
    pool = []
    for y in range(PATCH_RADIUS, height - PATCH_RADIUS, PATCH_SIDE):
        for x in range(PATCH_RADIUS, width - PATCH_RADIUS, PATCH_SIDE):
            box = patch_xyxy(x, y)
            safety = _expanded(box)
            if (not _admitted(safety, structural_mask, width, height)
                    or not _admitted(safety, solute_mask, width, height)
                    or any(_intersects(safety, excluded) for excluded in exclusions)):
                continue
            acquisition = ACQUISITIONS[structural_source]
            track = f"{acquisition}|{x}|{y}"
            rank_text = f"STUDY2B_BACKGROUND_V1|{track}|{frame_index}"
            pool.append({
                "acquisition_id": acquisition, "structural_source_id": structural_source,
                "solutal_source_id": SOLUTE_SOURCE[structural_source], "frame_index": frame_index,
                "center_x": x, "center_y": y, "patch_xyxy": box, "safety_xyxy": safety,
                "background_track_id": track,
                "hash_rank": hashlib.sha256(rank_text.encode("utf-8")).hexdigest(),
                "status": "BACKGROUND_CANDIDATE", "exclusion_status": "ALL_EXCLUSIONS_PASSED",
                "minimum_exclusion_envelope_distance_px": min(
                    (_pixel_distance(safety, e) for e in exclusions), default=None),
                "site_exclusion_count": len(global_boxes), "frame_component_exclusion_count": len(frame_boxes),
                "structural_support": "PASS", "solutal_support": "PASS",
                "pixels_materialized": False, "physical_absence_inferred": False,
            })
    return pool


def process_frame_pair(structural_raw, solute_raw, structural_source, frame_index,
                       records, exclusion_metadata, row_start=0):
    """Account for every frozen record; return arrays only for admitted pairs.

    Returned ``pairs[k]`` maps to the unique valid index record having
    ``row_index=row_start+k``. Invalid records retain null hashes and row_index.
    Native frame source authentication and synchronized ordering are controller
    obligations; explicit record provenance is independently checked here.
    """
    _source_frame(structural_source, frame_index)
    _require(type(row_start) is int and row_start >= 0 and type(records) is list,
             "explicit nonnegative container offset and record list required")
    _require(records == sorted(records, key=lambda r: tuple(r[k] for k in ORDER_FIELDS)),
             "frame records must retain frozen deterministic order")
    ids = set()
    for record in records:
        _require(record.get("structural_source_id") == structural_source
                 and record.get("solutal_source_id") == SOLUTE_SOURCE[structural_source]
                 and record.get("acquisition_id") == ACQUISITIONS[structural_source]
                 and record.get("frame_index") == frame_index,
                 "cross-source, modality or temporal mixing denied")
        sid, pair_id = record.get("site_id"), record.get("pair_id")
        _require(type(sid) is str and pair_id == f"{ACQUISITIONS[structural_source]}|{sid}|{frame_index}"
                 and pair_id not in ids and record.get("group_id") == f"{ACQUISITIONS[structural_source]}|{sid}",
                 "duplicate pair or altered group identity")
        ids.add(pair_id)
        point = record.get("canonical_center_xy_px")
        _require(type(point) is list and len(point) == 2 and all(_finite(v) for v in point),
                 "canonical center absent")
        x, y = (math.floor(v + 0.5) for v in point)
        _require(record.get("center_x") == x and record.get("center_y") == y
                 and record.get("patch_xyxy") == patch_xyxy(x, y)
                 and record.get("mapping_offset_xy") == [0, 0]
                 and record.get("patch_radius_px") == PATCH_RADIUS
                 and record.get("patch_side_px") == PATCH_SIDE
                 and record.get("supervision_tier") == TIERS.get(record.get("observation_state")),
                 "altered canonical center, crop, tier or mapping")
    structural_y, structural_mask = native_luminance_and_support(
        structural_raw, structural_source, structural=True)
    solute_y, solute_mask = native_luminance_and_support(solute_raw, structural_source, structural=False)
    structural_frame_hash = hashlib.sha256(structural_raw).hexdigest()
    solute_frame_hash = hashlib.sha256(solute_raw).hexdigest()
    width, height = DIMENSIONS[structural_source]
    pairs, index_records = [], []
    import numpy as np
    for record in records:
        box = record["patch_xyxy"]
        structural_ok = _admitted(box, structural_mask, width, height)
        solute_ok = _admitted(box, solute_mask, width, height)
        status = ("VALID_PAIR" if structural_ok and solute_ok else
                  "INVALID_STRUCTURAL_SUPPORT" if not structural_ok and solute_ok else
                  "INVALID_SOLUTAL_SUPPORT" if structural_ok and not solute_ok else "INVALID_BOTH")
        item = deepcopy(record)
        item.update({"pair_status": status, "row_index": None,
                     "structural_patch_sha256": None, "solutal_patch_sha256": None, "pair_sha256": None,
                     "structural_frame_sha256": structural_frame_hash,
                     "solutal_frame_sha256": solute_frame_hash,
                     "structural_support": "PASS" if structural_ok else "INVALID",
                     "solutal_support": "PASS" if solute_ok else "INVALID",
                     "support_disposition": ("ADMITTED" if status == "VALID_PAIR" else
                                             f"{record['supervision_tier']}_INVALID_SUPPORT")})
        if status == "VALID_PAIR":
            x0, y0, x1, y1 = box
            pair = np.stack((structural_y[y0:y1, x0:x1], solute_y[y0:y1, x0:x1]), axis=0)
            _require(pair.dtype == np.dtype("uint8") and pair.shape == (2, PATCH_SIDE, PATCH_SIDE),
                     "native crop must be exact unchanged two-channel 65x65 uint8")
            item.update({"row_index": row_start + len(pairs),
                         "structural_patch_sha256": hashlib.sha256(pair[0].tobytes(order="C")).hexdigest(),
                         "solutal_patch_sha256": hashlib.sha256(pair[1].tobytes(order="C")).hexdigest(),
                         "pair_sha256": hashlib.sha256(pair.tobytes(order="C")).hexdigest()})
            pairs.append(pair)
        index_records.append(item)
    background = background_pool_for_frame(structural_source, frame_index, structural_mask,
                                           solute_mask, exclusion_metadata)
    return {"pairs": pairs, "index_records": index_records, "background_records": background,
            "support_summary": {"input_records": len(records), "valid_pairs": len(pairs),
                                "pair_status_counts": dict(Counter(r["pair_status"] for r in index_records)),
                                "background_candidates": len(background),
                                "structural_frame_sha256": structural_frame_hash,
                                "solutal_frame_sha256": solute_frame_hash}}


def corpus_views(index_records):
    """Four logical row-index views with no pixel duplication or learning."""
    views = {"GOLD_VIEW": [], "GOLD_PLUS_SILVER_VIEW": [], "UNLABELED_VIEW": [],
             "FULL_LONGITUDINAL_VIEW": []}
    rows, identities = set(), set()
    for record in index_records:
        pair_id = record.get("pair_id")
        _require(type(pair_id) is str and pair_id not in identities, "duplicate index pair identity")
        identities.add(pair_id)
        if record.get("pair_status") != "VALID_PAIR":
            _require(record.get("row_index") is None, "invalid pair cannot own a tensor row")
            continue
        row, tier = record.get("row_index"), record.get("supervision_tier")
        _require(type(row) is int and row >= 0 and row not in rows and tier in TIERS.values(),
                 "invalid, duplicate or untyped row mapping")
        rows.add(row)
        views["FULL_LONGITUDINAL_VIEW"].append(row)
        if tier == "GOLD":
            views["GOLD_VIEW"].append(row)
        if tier in {"GOLD", "SILVER"}:
            views["GOLD_PLUS_SILVER_VIEW"].append(row)
        else:
            views["UNLABELED_VIEW"].append(row)
    _require(rows == set(range(len(rows))), "container rows must cover zero-based contiguous positions")
    for values in views.values():
        values.sort()
    return views
