"""Frozen Study4 S4-B0A matching and folds on explicitly supplied metadata.

All functions are pure and use only the standard library. Nothing opens files,
reads the real corpus, or grants authority to select real pair identities.
The default ledger cardinality guard is the frozen future 17 + 8 = 25 rule;
small synthetic examples must explicitly disable that cardinality guard.
"""

import hashlib


ACQUISITIONS = ("bottom_up_anti_parallel", "top_down_parallel")
FRAME_MAX = dict(zip(ACQUISITIONS, (293, 394)))
T = 8
FOLD_COUNT = 4
EXPECTED_BOTTOM_UP_PAIRS = 17
EXPECTED_TOP_DOWN_PAIRS = 8
EXPECTED_TOTAL_PAIRS = 25
EXPECTED_PAIR_COUNTS = dict(zip(
    ACQUISITIONS, (EXPECTED_BOTTOM_UP_PAIRS, EXPECTED_TOP_DOWN_PAIRS)))
PAIR_FIELDS = (
    "pair_id", "acquisition_id", "positive_group_id", "background_group_id",
    "shared_frames", "positive_selected_frames", "background_selected_frames",
    "fold",
)
GROUP_FIELDS = ("acquisition_id", "role", "frames")


class MatchingError(ValueError):
    """Supplied metadata or a pair ledger violates the frozen contract."""


def _require(condition, message):
    if not condition:
        raise MatchingError(message)


def _canonical_identity(value):
    return (type(value) is str and bool(value) and value == value.strip()
            and "\0" not in value
            and not any(0xD800 <= ord(character) <= 0xDFFF for character in value))


def _frames(values, acquisition=None):
    _require(type(values) in (tuple, list), "BLOCKED_INVALID_FRAME_COLLECTION")
    upper = max(FRAME_MAX.values()) if acquisition is None else FRAME_MAX[acquisition]
    _require(all(type(value) is int and 0 <= value <= upper for value in values),
             "BLOCKED_INVALID_FRAME_INDEX")
    _require(len(set(values)) == len(values), "BLOCKED_DUPLICATE_FRAME_INDEX")
    return tuple(sorted(values))


def _checked_groups(groups):
    _require(type(groups) is dict, "BLOCKED_INVALID_GROUP_COLLECTION")
    checked = {}
    for group_id, group in groups.items():
        _require(_canonical_identity(group_id), "BLOCKED_NONCANONICAL_GROUP_IDENTITY")
        _require(type(group) is dict and set(group) == set(GROUP_FIELDS),
                 "BLOCKED_GROUP_SCHEMA")
        acquisition = group["acquisition_id"]
        _require(type(acquisition) is str and acquisition in ACQUISITIONS,
                 "BLOCKED_UNKNOWN_ACQUISITION")
        _require(type(group["role"]) is str
                 and group["role"] in ("positive", "background"),
                 "BLOCKED_INVALID_GROUP_ROLE")
        checked[group_id] = {
            "acquisition_id": acquisition,
            "role": group["role"],
            "frames": _frames(group["frames"], acquisition),
        }
    return checked


def optimize_matching(edge_supports):
    """Return the exact optimal sorted edge tuple for one acquisition.

    Input maps (positive_group_id, background_group_id) to integer common-frame
    support >= 8. Acquisition membership is checked by the ledger functions.

    Successive shortest residual paths produce a minimum-cost flow of each
    attained cardinality. Augmenting until no path remains gives maximum
    cardinality, regardless of costs. For m canonically sorted edges, let
    B = 2**m and reward edge i by support*B + 2**(m-1-i). All lexicographic
    bits combined are < B, so one unit of support dominates every tie bit.
    At equal cardinality and support, the earliest edge in the symmetric
    difference determines the lexicographically smaller sorted edge list;
    its bit exceeds the sum of every later bit. Negating rewards therefore
    realizes the exact second and third objectives with arbitrary-precision
    integers. Bellman-Ford handles negative residual costs without floats.
    """
    _require(type(edge_supports) is dict, "BLOCKED_INVALID_EDGE_SUPPORTS")
    for edge, support in edge_supports.items():
        _require(type(edge) is tuple and len(edge) == 2
                 and all(_canonical_identity(identity) for identity in edge),
                 "BLOCKED_NONCANONICAL_EDGE")
        _require(type(support) is int and support >= T, "BLOCKED_INVALID_EDGE_SUPPORT")
    edges = tuple(sorted(edge_supports))
    positive_ids = sorted({edge[0] for edge in edges})
    background_ids = sorted({edge[1] for edge in edges})
    _require(not set(positive_ids).intersection(background_ids),
             "BLOCKED_INCONSISTENT_GROUP_ROLE")
    if not edges:
        return ()

    source = 0
    positive_nodes = {identity: index + 1 for index, identity in enumerate(positive_ids)}
    background_start = 1 + len(positive_ids)
    background_nodes = {identity: background_start + index
                        for index, identity in enumerate(background_ids)}
    sink = background_start + len(background_ids)
    graph = [[] for _ in range(sink + 1)]

    def add_arc(start, end, cost):
        forward = [end, len(graph[end]), 1, cost]
        reverse = [start, len(graph[start]), 0, -cost]
        graph[start].append(forward)
        graph[end].append(reverse)
        return forward

    for positive in positive_ids:
        add_arc(source, positive_nodes[positive], 0)
    for background in background_ids:
        add_arc(background_nodes[background], sink, 0)
    scale = 1 << len(edges)
    edge_arcs = {}
    for index, edge in enumerate(edges):
        tie_bit = 1 << (len(edges) - index - 1)
        reward = edge_supports[edge] * scale + tie_bit
        edge_arcs[edge] = add_arc(positive_nodes[edge[0]], background_nodes[edge[1]], -reward)

    while True:
        distances = [None] * len(graph)
        parents = [None] * len(graph)
        distances[source] = 0
        for _ in range(len(graph) - 1):
            changed = False
            for start, arcs in enumerate(graph):
                if distances[start] is None:
                    continue
                for arc_index, arc in enumerate(arcs):
                    end, _, capacity, cost = arc
                    candidate = distances[start] + cost
                    if capacity and (distances[end] is None or candidate < distances[end]):
                        distances[end] = candidate
                        parents[end] = (start, arc_index)
                        changed = True
            if not changed:
                break
        if distances[sink] is None:
            break
        node = sink
        while node != source:
            start, arc_index = parents[node]
            arc = graph[start][arc_index]
            arc[2] -= 1
            graph[node][arc[1]][2] += 1
            node = start
    return tuple(edge for edge in edges if edge_arcs[edge][2] == 0)


def nearest_integer_rank(numerator, denominator):
    """Round a nonnegative rational to nearest integer, with exact ties lower."""
    _require(type(numerator) is int and numerator >= 0
             and type(denominator) is int and denominator > 0,
             "BLOCKED_INVALID_RANK_RATIO")
    quotient, remainder = divmod(numerator, denominator)
    return quotient + int(2 * remainder > denominator)


def _select_from_shared(shared):
    _require(len(shared) >= T, "BLOCKED_INSUFFICIENT_COMMON_FRAME_SUPPORT")
    selected = tuple(shared[nearest_integer_rank(k * (len(shared) - 1), T - 1)]
                     for k in range(T))
    _require(len(set(selected)) == T, "BLOCKED_REPEATED_SELECTED_FRAME")
    return selected


def select_shared_frames(positive_frames, background_frames):
    """Select eight real common frames using the frozen integer rank rule."""
    shared = tuple(sorted(set(_frames(positive_frames)) & set(_frames(background_frames))))
    return _select_from_shared(shared)


def pair_id(acquisition_id, positive_id, background_id):
    """Hash the exact domain-separated, NUL-delimited UTF-8 pair identity."""
    _require(all(_canonical_identity(identity)
                 for identity in (acquisition_id, positive_id, background_id)),
             "BLOCKED_NONCANONICAL_PAIR_IDENTITY")
    _require(acquisition_id in ACQUISITIONS, "BLOCKED_UNKNOWN_ACQUISITION")
    _require(positive_id != background_id, "BLOCKED_GROUP_REUSE")
    canonical = (b"STUDY4_PAIR_V1\0" + acquisition_id.encode("utf-8")
                 + b"\0" + positive_id.encode("utf-8")
                 + b"\0" + background_id.encode("utf-8"))
    return "S4P_" + hashlib.sha256(canonical).hexdigest()


def _checked_pair_records(pairs, *, require_fold):
    _require(type(pairs) in (list, tuple), "BLOCKED_INVALID_PAIR_LEDGER")
    checked = []
    seen_ids = set()
    used_groups = set()
    full_fields = set(PAIR_FIELDS)
    base_fields = full_fields - {"fold"}
    for record in pairs:
        _require(type(record) is dict, "BLOCKED_PAIR_SCHEMA")
        fields = set(record)
        _require(fields == full_fields or (not require_fold and fields == base_fields),
                 "BLOCKED_PAIR_SCHEMA")
        acquisition = record["acquisition_id"]
        positive = record["positive_group_id"]
        background = record["background_group_id"]
        expected_id = pair_id(acquisition, positive, background)
        identifier = record["pair_id"]
        _require(type(identifier) is str and len(identifier) == 68
                 and identifier.startswith("S4P_")
                 and all(character in "0123456789abcdef" for character in identifier[4:])
                 and identifier == expected_id,
                 "BLOCKED_PAIR_ID_MISMATCH")
        _require(identifier not in seen_ids, "BLOCKED_PAIR_ID_COLLISION")
        seen_ids.add(identifier)
        _require(positive not in used_groups and background not in used_groups,
                 "BLOCKED_GROUP_REUSE")
        used_groups.update((positive, background))
        shared = _frames(record["shared_frames"], acquisition)
        _require(tuple(record["shared_frames"]) == shared, "BLOCKED_UNSORTED_SHARED_FRAMES")
        selected = _select_from_shared(shared)
        for field in ("positive_selected_frames", "background_selected_frames"):
            values = _frames(record[field], acquisition)
            _require(tuple(record[field]) == selected and values == selected,
                     "BLOCKED_SELECTED_FRAME_MISMATCH")
        item = {
            "pair_id": identifier,
            "acquisition_id": acquisition,
            "positive_group_id": positive,
            "background_group_id": background,
            "shared_frames": shared,
            "positive_selected_frames": selected,
            "background_selected_frames": selected,
        }
        if "fold" in record:
            _require(type(record["fold"]) is int and 0 <= record["fold"] < FOLD_COUNT,
                     "BLOCKED_INVALID_FOLD")
            item["fold"] = record["fold"]
        checked.append(item)
    return tuple(sorted(checked, key=lambda item: (
        item["acquisition_id"], item["positive_group_id"], item["background_group_id"])))


def assign_folds(pairs):
    """Return fresh pair records with acquisition-stratified four-fold assignment.

    A record represents both members of an indivisible pair. Historical folds
    are neither accepted as extra fields nor consulted. An existing valid fold
    field is overwritten by the frozen pair-hash round-robin rule.
    """
    checked = _checked_pair_records(pairs, require_fold=False)
    assigned = {}
    for acquisition in ACQUISITIONS:
        members = [item for item in checked if item["acquisition_id"] == acquisition]
        ordered = sorted(members, key=lambda item: (
            hashlib.sha256(b"STUDY4_FOLD_V1\0" + item["pair_id"].encode("utf-8")).hexdigest(),
            item["pair_id"]))
        for index, item in enumerate(ordered):
            assigned[item["pair_id"]] = index % FOLD_COUNT
    return tuple(dict(item, fold=assigned[item["pair_id"]]) for item in checked)


def _candidate_supports(groups, acquisition):
    positive = sorted(identity for identity, group in groups.items()
                      if group["acquisition_id"] == acquisition and group["role"] == "positive")
    background = sorted(identity for identity, group in groups.items()
                        if group["acquisition_id"] == acquisition
                        and group["role"] == "background")
    frames = {identity: frozenset(group["frames"]) for identity, group in groups.items()}
    supports = {}
    for positive_id in positive:
        for background_id in background:
            support = len(frames[positive_id] & frames[background_id])
            if support >= T:
                supports[(positive_id, background_id)] = support
    return supports


def _enforce_counts(pairs, enforce_expected_cardinality):
    _require(type(enforce_expected_cardinality) is bool, "BLOCKED_INVALID_CARDINALITY_GUARD")
    if enforce_expected_cardinality:
        counts = {acquisition: sum(item["acquisition_id"] == acquisition for item in pairs)
                  for acquisition in ACQUISITIONS}
        _require(counts == EXPECTED_PAIR_COUNTS and len(pairs) == EXPECTED_TOTAL_PAIRS,
                 "BLOCKED_EXPECTED_CARDINALITY_DIVERGENCE")


def build_pair_ledger(groups, *, enforce_expected_cardinality=True):
    """Build exact optimal pairs solely from supplied acquisition/role/frame sets.

    No runner or corpus source is provided. Calling this function on real
    metadata requires a future explicit author decision, independent of the
    code's frozen cardinality guard.
    """
    _require(type(enforce_expected_cardinality) is bool, "BLOCKED_INVALID_CARDINALITY_GUARD")
    checked = _checked_groups(groups)
    pairs = []
    seen_ids = set()
    for acquisition in ACQUISITIONS:
        for positive, background in optimize_matching(_candidate_supports(checked, acquisition)):
            shared = tuple(sorted(set(checked[positive]["frames"])
                                  & set(checked[background]["frames"])))
            selected = _select_from_shared(shared)
            identifier = pair_id(acquisition, positive, background)
            _require(identifier not in seen_ids, "BLOCKED_PAIR_ID_COLLISION")
            seen_ids.add(identifier)
            pairs.append({
                "pair_id": identifier,
                "acquisition_id": acquisition,
                "positive_group_id": positive,
                "background_group_id": background,
                "shared_frames": shared,
                "positive_selected_frames": selected,
                "background_selected_frames": selected,
            })
    _enforce_counts(pairs, enforce_expected_cardinality)
    return assign_folds(pairs)


def validate_pair_ledger(ledger, groups, *, enforce_expected_cardinality=True):
    """Reject invalid identities, selection, objectives, cardinality, or folds.

    Complete eligible graphs are reconstructed only from the supplied in-memory
    groups. Comparing against their exact optima rejects submaximal matchings,
    support losses, and noncanonical tertiary ties. Returns None on success.
    """
    _require(type(enforce_expected_cardinality) is bool, "BLOCKED_INVALID_CARDINALITY_GUARD")
    checked_groups = _checked_groups(groups)
    checked_pairs = _checked_pair_records(ledger, require_fold=True)
    for item in checked_pairs:
        positive = item["positive_group_id"]
        background = item["background_group_id"]
        _require(positive in checked_groups and background in checked_groups,
                 "BLOCKED_UNKNOWN_PAIR_GROUP")
        positive_group = checked_groups[positive]
        background_group = checked_groups[background]
        _require(positive_group["role"] == "positive" and background_group["role"] == "background",
                 "BLOCKED_INVALID_PAIR_ROLE")
        _require(positive_group["acquisition_id"] == background_group["acquisition_id"]
                 == item["acquisition_id"], "BLOCKED_CROSS_ACQUISITION_PAIR")
        shared = tuple(sorted(set(positive_group["frames"]) & set(background_group["frames"])))
        _require(item["shared_frames"] == shared, "BLOCKED_COMMON_FRAME_SUPPORT_MISMATCH")
    _enforce_counts(checked_pairs, enforce_expected_cardinality)
    for acquisition in ACQUISITIONS:
        actual = tuple(sorted((item["positive_group_id"], item["background_group_id"])
                              for item in checked_pairs if item["acquisition_id"] == acquisition))
        expected = optimize_matching(_candidate_supports(checked_groups, acquisition))
        _require(actual == expected, "BLOCKED_NONOPTIMAL_MATCHING")
    expected_folds = {item["pair_id"]: item["fold"] for item in assign_folds(checked_pairs)}
    _require(all(item["fold"] == expected_folds[item["pair_id"]] for item in checked_pairs),
             "BLOCKED_NONCANONICAL_FOLD_ASSIGNMENT")
