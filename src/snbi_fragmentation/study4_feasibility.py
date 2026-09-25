"""Pure Study4 S4-A feasibility calculations on explicitly supplied metadata.

This module has no filesystem or scientific-library dependency. Its matching
returns capacity only: it neither selects the S4-B cohort nor optimizes shared
frame support. Calling these functions does not grant real-corpus authority.
"""


METADATA_FIELDS = (
    "sample_id", "group_id", "acquisition_id", "frame_index", "label",
    "tier", "kind", "split", "cv_fold",
)
ACQUISITIONS = ("bottom_up_anti_parallel", "top_down_parallel")
FRAME_MAX = dict(zip(ACQUISITIONS, (293, 394)))
ACQUISITION_RESULT_FIELDS = (
    "positive_group_count", "background_group_count", "candidate_edge_count",
    "isolated_positive_group_count", "isolated_background_group_count",
    "maximum_matching_capacity",
)
RESULT_FIELDS = (
    "authenticated_row_count", "positive_row_count", "background_row_count",
    "positive_group_count", "background_group_count", "by_acquisition",
    "candidate_edge_count", "isolated_positive_group_count",
    "isolated_background_group_count", "total_maximum_matching_capacity",
    "feasibility_decision", "documentary_manifest_sha256",
    "payload_binary_reads", "feature_extractions", "fits",
)


class FeasibilityError(ValueError):
    """Supplied metadata or a feasibility result violates the frozen contract."""


def _require(condition, message):
    if not condition:
        raise FeasibilityError(message)


def _canonical_identity(value):
    return type(value) is str and bool(value) and value == value.strip()


def _sha256(value):
    return (type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value))


def project_metadata(rows):
    """Validate every supplied row and discard every non-allowlisted field.

    Storage/provenance values are never inspected, traversed, or interpreted.
    Invalid rows block the analysis rather than silently changing its population.
    Empty synthetic populations are admissible and have insufficient support.
    """
    _require(type(rows) in (list, tuple), "BLOCKED_INVALID_ROW_COLLECTION")
    projected = []
    sample_ids = set()
    for row in rows:
        _require(type(row) is dict, "BLOCKED_INVALID_METADATA_ROW")
        _require(all(field in row for field in METADATA_FIELDS),
                 "BLOCKED_INCOMPLETE_AUTHORIZED_METADATA")
        item = {field: row[field] for field in METADATA_FIELDS}
        _require(all(_canonical_identity(item[field]) for field in
                     ("sample_id", "group_id", "acquisition_id")),
                 "BLOCKED_NONCANONICAL_IDENTITY")
        _require(item["sample_id"] not in sample_ids, "BLOCKED_DUPLICATE_SAMPLE_ID")
        sample_ids.add(item["sample_id"])
        _require(type(item["split"]) is str and item["split"] == "TRAIN",
                 "BLOCKED_NON_TRAIN_ROW")
        _require(type(item["label"]) is int and item["label"] in (0, 1),
                 "BLOCKED_INVALID_LABEL")
        _require(type(item["tier"]) is str and type(item["kind"]) is str,
                 "BLOCKED_INVALID_ROW_ROLE")
        expected_role = ("GOLD", "positive") if item["label"] == 1 else (
            "BACKGROUND", "background")
        _require((item["tier"], item["kind"]) == expected_role,
                 "BLOCKED_INVALID_ROW_ROLE")
        acquisition = item["acquisition_id"]
        _require(acquisition in ACQUISITIONS, "BLOCKED_UNKNOWN_ACQUISITION")
        frame = item["frame_index"]
        _require(type(frame) is int and 0 <= frame <= FRAME_MAX[acquisition],
                 "BLOCKED_INVALID_FRAME_INDEX")
        _require(type(item["cv_fold"]) is int and item["cv_fold"] in range(4),
                 "BLOCKED_INVALID_HISTORICAL_FOLD")
        projected.append(item)
    return tuple(projected)


def group_rows(rows):
    """Return canonical group IDs mapped to ordered authorized metadata tuples."""
    groups = {}
    for row in project_metadata(rows):
        groups.setdefault(row["group_id"], []).append(row)
    result = {}
    for group_id in sorted(groups):
        observations = groups[group_id]
        first = observations[0]
        _require(all((row["acquisition_id"], row["label"]) ==
                     (first["acquisition_id"], first["label"])
                     for row in observations), "BLOCKED_INCONSISTENT_GROUP_IDENTITY")
        _require(len({row["frame_index"] for row in observations}) == len(observations),
                 "BLOCKED_AMBIGUOUS_GROUP_FRAME_IDENTITY")
        result[group_id] = tuple(sorted(
            observations, key=lambda row: (row["frame_index"], row["sample_id"])))
    return result


def _checked_groups(groups):
    _require(type(groups) is dict, "BLOCKED_INVALID_GROUP_COLLECTION")
    rows = []
    for group_id, observations in groups.items():
        _require(_canonical_identity(group_id), "BLOCKED_NONCANONICAL_GROUP_IDENTITY")
        _require(type(observations) in (tuple, list) and bool(observations),
                 "BLOCKED_EMPTY_OR_INVALID_GROUP")
        _require(all(type(row) is dict and row.get("group_id") == group_id
                     for row in observations), "BLOCKED_INCONSISTENT_GROUP_IDENTITY")
        rows.extend(observations)
    return group_rows(rows)


def valid_frame_sets(groups):
    """Return sorted distinct valid frame indices, rejecting duplicate identities."""
    return {group_id: tuple(row["frame_index"] for row in observations)
            for group_id, observations in _checked_groups(groups).items()}


def construct_candidate_graph(groups):
    """Return a bipartite adjacency per acquisition; never select final pairs.

    Each positive group, including isolated groups, maps to its sorted eligible
    background IDs. Internal adjacency is not part of the disclosed result.
    """
    checked = _checked_groups(groups)
    frames = {group_id: frozenset(row["frame_index"] for row in observations)
              for group_id, observations in checked.items()}
    graphs = {}
    for acquisition in ACQUISITIONS:
        positive = [group_id for group_id, rows in checked.items()
                    if rows[0]["acquisition_id"] == acquisition and rows[0]["label"] == 1]
        background = [group_id for group_id, rows in checked.items()
                      if rows[0]["acquisition_id"] == acquisition and rows[0]["label"] == 0]
        graphs[acquisition] = {
            positive_id: tuple(background_id for background_id in background
                               if len(frames[positive_id] & frames[background_id]) >= 8)
            for positive_id in positive
        }
    return graphs


def maximum_matching_cardinality(adjacency):
    """Compute exact one-to-one capacity with deterministic augmenting paths.

    Sorted identities stabilize traversal only. No common-support weight or
    final-pair identity objective is applied, and no matching IDs are returned.
    The iterative search has no recursion-depth dependency.
    """
    _require(type(adjacency) is dict, "BLOCKED_INVALID_ADJACENCY")
    graph = {}
    for positive, background in adjacency.items():
        _require(_canonical_identity(positive), "BLOCKED_NONCANONICAL_GRAPH_IDENTITY")
        _require(type(background) in (list, tuple)
                 and all(_canonical_identity(value) for value in background),
                 "BLOCKED_INVALID_GRAPH_NEIGHBORS")
        _require(len(set(background)) == len(background), "BLOCKED_DUPLICATE_GRAPH_EDGE")
        graph[positive] = tuple(sorted(background))
    matched_left = {}
    matched_right = {}
    for source in sorted(graph):
        queue = [source]
        seen_left = {source}
        parent_right = {}
        free_right = None
        cursor = 0
        while cursor < len(queue) and free_right is None:
            positive = queue[cursor]
            cursor += 1
            for background in graph[positive]:
                if background in parent_right:
                    continue
                parent_right[background] = positive
                if background not in matched_right:
                    free_right = background
                    break
                owner = matched_right[background]
                if owner not in seen_left:
                    seen_left.add(owner)
                    queue.append(owner)
        while free_right is not None:
            positive = parent_right[free_right]
            old_right = matched_left.get(positive)
            matched_left[positive] = free_right
            matched_right[free_right] = positive
            free_right = old_right
    return len(matched_left)


def _decision(capacities):
    return ("SUFFICIENT_COMMON_SUPPORT" if sum(capacities) >= 16
            and all(capacity >= 1 for capacity in capacities)
            else "INSUFFICIENT_COVERAGE_OVERLAP")


def summarize_feasibility(rows, documentary_manifest_sha256):
    """Summarize supplied metadata; byte authentication belongs to the caller."""
    _require(_sha256(documentary_manifest_sha256), "BLOCKED_INVALID_DOCUMENTARY_SHA256")
    groups = group_rows(rows)
    graphs = construct_candidate_graph(groups)
    by_acquisition = {}
    for acquisition in ACQUISITIONS:
        graph = graphs[acquisition]
        background_ids = {group_id for group_id, observations in groups.items()
                          if observations[0]["acquisition_id"] == acquisition
                          and observations[0]["label"] == 0}
        connected_background = {background_id for neighbors in graph.values()
                                for background_id in neighbors}
        by_acquisition[acquisition] = {
            "positive_group_count": len(graph),
            "background_group_count": len(background_ids),
            "candidate_edge_count": sum(len(neighbors) for neighbors in graph.values()),
            "isolated_positive_group_count": sum(not neighbors for neighbors in graph.values()),
            "isolated_background_group_count": len(background_ids - connected_background),
            "maximum_matching_capacity": maximum_matching_cardinality(graph),
        }
    positive_rows = sum(len(observations) for observations in groups.values()
                        if observations[0]["label"] == 1)
    background_rows = sum(len(observations) for observations in groups.values()
                          if observations[0]["label"] == 0)
    result = {
        "authenticated_row_count": positive_rows + background_rows,
        "positive_row_count": positive_rows,
        "background_row_count": background_rows,
        "by_acquisition": by_acquisition,
    }
    for field in ACQUISITION_RESULT_FIELDS[:-1]:
        result[field] = sum(item[field] for item in by_acquisition.values())
    capacities = [by_acquisition[acquisition]["maximum_matching_capacity"]
                  for acquisition in ACQUISITIONS]
    result.update({
        "total_maximum_matching_capacity": sum(capacities),
        "feasibility_decision": _decision(capacities),
        "documentary_manifest_sha256": documentary_manifest_sha256,
        "payload_binary_reads": 0,
        "feature_extractions": 0,
        "fits": 0,
    })
    validate_result_schema(result)
    return result


def validate_result_schema(result):
    """Reject additional disclosure, mistyped counts, or contradictory totals."""
    _require(type(result) is dict and set(result) == set(RESULT_FIELDS),
             "BLOCKED_RESULT_SCHEMA")
    non_count = {"by_acquisition", "feasibility_decision", "documentary_manifest_sha256"}
    for field in set(RESULT_FIELDS) - non_count:
        _require(type(result[field]) is int and result[field] >= 0,
                 "BLOCKED_RESULT_COUNTER")
    _require(_sha256(result["documentary_manifest_sha256"]), "BLOCKED_INVALID_DOCUMENTARY_SHA256")
    _require(all(result[field] == 0 for field in
                 ("payload_binary_reads", "feature_extractions", "fits")),
             "BLOCKED_NONZERO_SCIENTIFIC_COUNTER")
    _require(result["authenticated_row_count"] ==
             result["positive_row_count"] + result["background_row_count"],
             "BLOCKED_RESULT_ROW_TOTAL")
    _require(result["positive_row_count"] >= result["positive_group_count"]
             and result["background_row_count"] >= result["background_group_count"],
             "BLOCKED_RESULT_ROW_GROUP_COUNTS")
    by_acquisition = result["by_acquisition"]
    _require(type(by_acquisition) is dict and set(by_acquisition) == set(ACQUISITIONS),
             "BLOCKED_RESULT_ACQUISITIONS")
    capacities = []
    for acquisition in ACQUISITIONS:
        item = by_acquisition[acquisition]
        _require(type(item) is dict and set(item) == set(ACQUISITION_RESULT_FIELDS),
                 "BLOCKED_RESULT_ACQUISITION_SCHEMA")
        _require(all(type(value) is int and value >= 0 for value in item.values()),
                 "BLOCKED_RESULT_COUNTER")
        positive = item["positive_group_count"]
        background = item["background_group_count"]
        isolated_positive = item["isolated_positive_group_count"]
        isolated_background = item["isolated_background_group_count"]
        edges = item["candidate_edge_count"]
        capacity = item["maximum_matching_capacity"]
        _require(isolated_positive <= positive and isolated_background <= background,
                 "BLOCKED_RESULT_ISOLATED_COUNTS")
        active_positive = positive - isolated_positive
        active_background = background - isolated_background
        _require(max(active_positive, active_background) <= edges
                 <= active_positive * active_background,
                 "BLOCKED_RESULT_EDGE_COUNTS")
        _require(capacity <= min(active_positive, active_background)
                 and ((edges == 0 and capacity == 0) or (edges > 0 and capacity > 0)),
                 "BLOCKED_RESULT_MATCHING_CAPACITY")
        capacities.append(capacity)
    for field in ACQUISITION_RESULT_FIELDS[:-1]:
        _require(result[field] == sum(item[field] for item in by_acquisition.values()),
                 "BLOCKED_RESULT_ACQUISITION_TOTAL")
    _require(result["total_maximum_matching_capacity"] == sum(capacities),
             "BLOCKED_RESULT_MATCHING_TOTAL")
    _require(type(result["feasibility_decision"]) is str
             and result["feasibility_decision"] == _decision(capacities),
             "BLOCKED_RESULT_DECISION")
