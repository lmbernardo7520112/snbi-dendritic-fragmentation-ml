"""Invented matching graphs and frame indices only; never read the real corpus.

Only the named tracked contracts and matching source are read for freeze checks.
The pure APIs run with filesystem entry points blocked. No scientific runner,
real manifest, experimental payload, feature extractor, or model is invoked.
"""

import ast
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest
from unittest.mock import patch

from snbi_fragmentation import study4_matching as matching


ROOT = Path(__file__).absolute().parents[1]
BOTTOM = "bottom_up_anti_parallel"
TOP = "top_down_parallel"


def synthetic_group(role, frames=tuple(range(8)), acquisition=BOTTOM):
    return {"acquisition_id": acquisition, "role": role, "frames": tuple(frames)}


def synthetic_groups(bottom=1, top=0):
    """Disjoint invented eight-frame blocks make each intended pair unique."""
    groups = {}
    for acquisition, count in ((BOTTOM, bottom), (TOP, top)):
        for number in range(count):
            frames = tuple(range(number * 8, number * 8 + 8))
            for role in ("positive", "background"):
                group_id = f"synthetic-{acquisition}-{role}-{number:02d}"
                groups[group_id] = synthetic_group(role, frames, acquisition)
    return groups


def small_ledger(groups):
    return matching.build_pair_ledger(groups, enforce_expected_cardinality=False)


def brute_force_matching(edge_supports):
    """Independent exhaustive assignment oracle; no production solver helpers."""
    positives = sorted({positive for positive, _ in edge_supports})
    possibilities = []

    def enumerate_assignments(index, used_backgrounds, selected):
        if index == len(positives):
            edges = tuple(sorted(selected))
            possibilities.append(((-len(edges), -sum(edge_supports[e] for e in edges), edges), edges))
            return
        positive = positives[index]
        enumerate_assignments(index + 1, used_backgrounds, selected)
        for (candidate, background) in sorted(edge_supports):
            if candidate == positive and background not in used_backgrounds:
                enumerate_assignments(index + 1, used_backgrounds | {background},
                                      selected + [(positive, background)])

    enumerate_assignments(0, set(), [])
    return min(possibilities)[1]


def records_for_edges(groups, edges):
    """Assemble deliberately alternative ledgers without the matching solver."""
    records = []
    for positive, background in edges:
        acquisition = groups[positive]["acquisition_id"]
        shared = tuple(sorted(set(groups[positive]["frames"]) & set(groups[background]["frames"])))
        selected = matching.select_shared_frames(groups[positive]["frames"],
                                                 groups[background]["frames"])
        records.append({
            "pair_id": matching.pair_id(acquisition, positive, background),
            "acquisition_id": acquisition,
            "positive_group_id": positive,
            "background_group_id": background,
            "shared_frames": shared,
            "positive_selected_frames": selected,
            "background_selected_frames": selected,
        })
    return matching.assign_folds(records)


class ExactMatchingTests(unittest.TestCase):
    def test_maximum_cardinality_precedes_any_support_advantage(self):
        graph = {("p0", "b0"): 300, ("p0", "b1"): 8, ("p1", "b0"): 8}
        self.assertEqual(matching.optimize_matching(graph), (("p0", "b1"), ("p1", "b0")))

    def test_secondary_objective_maximizes_total_support_globally(self):
        graph = {("p0", "b0"): 20, ("p0", "b1"): 19,
                 ("p1", "b0"): 19, ("p1", "b1"): 8}
        self.assertEqual(matching.optimize_matching(graph), (("p0", "b1"), ("p1", "b0")))

    def test_tertiary_objective_is_sorted_edge_list_lexicographic_minimum(self):
        graph = {(p, b): 8 for p in ("p0", "p1", "p2") for b in ("b0", "b1", "b2")}
        self.assertEqual(matching.optimize_matching(graph),
                         (("p0", "b0"), ("p1", "b1"), ("p2", "b2")))

    def test_greedy_first_available_edge_loses_a_pair(self):
        graph = {("p0", "b0"): 8, ("p0", "b1"): 8, ("p1", "b0"): 8}
        used_positive, used_background, greedy = set(), set(), []
        for positive, background in sorted(graph):
            if positive not in used_positive and background not in used_background:
                greedy.append((positive, background))
                used_positive.add(positive)
                used_background.add(background)
        self.assertEqual(len(greedy), 1)
        self.assertEqual(len(matching.optimize_matching(graph)), 2)

    def test_brute_force_equivalence_for_every_three_by_three_topology(self):
        edges = tuple(product(("p0", "p1", "p2"), ("b0", "b1", "b2")))
        for mask in range(1 << len(edges)):
            graph = {edge: 8 + ((index * 7 + mask) % 5)
                     for index, edge in enumerate(edges) if mask & (1 << index)}
            with self.subTest(mask=mask):
                self.assertEqual(matching.optimize_matching(graph), brute_force_matching(graph))

    def test_brute_force_equivalence_for_weighted_and_disconnected_graphs(self):
        edges = tuple(product(("p0", "p1"), ("b0", "b1")))
        for weights in product((0, 8, 9, 20), repeat=4):
            graph = {edge: support for edge, support in zip(edges, weights) if support}
            with self.subTest(weights=weights):
                self.assertEqual(matching.optimize_matching(graph), brute_force_matching(graph))
        rng = random.Random(407)
        for case in range(64):
            graph = {(f"p{p}", f"b{b}"): rng.randrange(8, 35)
                     for p in range(4) for b in range(4) if rng.randrange(3)}
            with self.subTest(case=case):
                self.assertEqual(matching.optimize_matching(graph), brute_force_matching(graph))

    def test_optimizer_deterministic_under_input_permutations_without_mutation(self):
        graph = {(f"p{p}", f"b{b}"): 8 + (p + b) % 3 for p in range(4) for b in range(4)}
        original = deepcopy(graph)
        expected = brute_force_matching(graph)
        items = list(graph.items())
        rng = random.Random(812)
        for _ in range(12):
            rng.shuffle(items)
            self.assertEqual(matching.optimize_matching(dict(items)), expected)
        self.assertEqual(graph, original)

    def test_no_positive_or_background_group_is_reused(self):
        graph = {(f"p{p}", f"b{b}"): 8 for p in range(4) for b in range(2)}
        selected = matching.optimize_matching(graph)
        self.assertEqual(len(selected), 2)
        self.assertEqual(len({p for p, _ in selected}), len(selected))
        self.assertEqual(len({b for _, b in selected}), len(selected))
        with self.assertRaises(matching.MatchingError):
            matching.optimize_matching({("same", "b"): 8, ("p", "same"): 8})

    def test_empty_graph_and_normal_unicode_string_order(self):
        self.assertEqual(matching.optimize_matching({}), ())
        graph = {(p, b): 8 for p in ("p-é", "p-z") for b in ("b-β", "b-a")}
        self.assertEqual(matching.optimize_matching(graph), (("p-z", "b-a"), ("p-é", "b-β")))

    def test_invalid_edge_supports_and_noncanonical_identities_block(self):
        for support in (0, 7, -1, True, 8.0, "8", None):
            with self.subTest(support=support), self.assertRaises(matching.MatchingError):
                matching.optimize_matching({("p", "b"): support})
        for identity in ("", " p", "p ", "p\0x", "p\ud800", 3, None):
            with self.subTest(identity=repr(identity)), self.assertRaises(matching.MatchingError):
                matching.optimize_matching({(identity, "b"): 8})
        for edge in (("p",), ("p", "b", "third"), ("same", "same"), "pb"):
            with self.subTest(edge=edge), self.assertRaises(matching.MatchingError):
                matching.optimize_matching({edge: 8})


class SharedFrameSelectionTests(unittest.TestCase):
    def test_exactly_eight_shared_frames_are_selected_unchanged(self):
        frames = (1, 7, 22, 50, 93, 147, 206, 293)
        self.assertEqual(matching.select_shared_frames(frames[::-1], frames), frames)

    def test_ranks_select_real_irregular_frames_without_interpolation(self):
        frames = (1, 4, 9, 15, 23, 34, 49, 68, 90, 117, 150, 190)
        selected = matching.select_shared_frames(frames + (200,), frames + (201,))
        self.assertEqual(selected, (1, 9, 15, 34, 49, 90, 117, 190))
        self.assertEqual(len(selected), 8)
        self.assertEqual(len(set(selected)), 8)
        self.assertTrue(set(selected).issubset(frames))
        self.assertTrue(all(type(frame) is int for frame in selected))

    def test_uniform_integer_ranks_include_both_endpoints(self):
        self.assertEqual(matching.select_shared_frames(tuple(range(15)), tuple(range(15))),
                         (0, 2, 4, 6, 8, 10, 12, 14))

    def test_short_common_support_blocks_without_repetition(self):
        for positive, background in ((tuple(range(7)), tuple(range(7))),
                                     (tuple(range(12)), tuple(range(5, 17)))):
            with self.subTest(positive=positive, background=background), \
                    self.assertRaises(matching.MatchingError):
                matching.select_shared_frames(positive, background)

    def test_lower_half_tie_rule_uses_exact_integer_arithmetic(self):
        # Denominator seven cannot attain an exact half; exercise the helper directly.
        for numerator, denominator, expected in ((0, 7, 0), (49, 100, 0), (50, 100, 0),
                                                 (51, 100, 1), (3, 2, 1), (5, 2, 2),
                                                 (2**60 + 1, 2, 2**59)):
            with self.subTest(numerator=numerator, denominator=denominator):
                self.assertEqual(matching.nearest_integer_rank(numerator, denominator), expected)
        for numerator, denominator in ((-1, 7), (1, 0), (True, 7), (1, True), (1.0, 7), (1, 7.0)):
            with self.subTest(numerator=numerator, denominator=denominator), \
                    self.assertRaises(matching.MatchingError):
                matching.nearest_integer_rank(numerator, denominator)

    def test_invalid_frames_are_rejected_without_coercion_or_deduplication(self):
        for invalid in (-1, 395, True, 1.0, "1", None, 0):
            frames = tuple(range(8)) + (invalid,)
            with self.subTest(invalid=invalid), self.assertRaises(matching.MatchingError):
                matching.select_shared_frames(frames, tuple(range(8)))


class PairIdentityAndLedgerTests(unittest.TestCase):
    def test_pair_id_matches_full_domain_separated_utf8_digest(self):
        positive, background = "synthetic-p-é", "synthetic-b-β"
        canonical = (b"STUDY4_PAIR_V1\0" + BOTTOM.encode("utf-8") + b"\0"
                     + positive.encode("utf-8") + b"\0" + background.encode("utf-8"))
        expected = "S4P_" + hashlib.sha256(canonical).hexdigest()
        self.assertEqual(matching.pair_id(BOTTOM, positive, background), expected)
        self.assertEqual(matching.pair_id(BOTTOM, positive, background), expected)
        self.assertEqual(len(expected), 68)
        self.assertRegex(expected, r"^S4P_[0-9a-f]{64}$")
        alternatives = (matching.pair_id(TOP, positive, background),
                        matching.pair_id(BOTTOM, background, positive),
                        matching.pair_id(BOTTOM, positive + "x", background))
        self.assertEqual(len(set((expected,) + alternatives)), 4)

    def test_pair_id_rejects_ambiguous_or_noncanonical_components(self):
        for identity in ("", " p", "p ", "p\0b", "p\udfff", None):
            for positive, background in ((identity, "b"), ("p", identity)):
                with self.subTest(positive=repr(positive), background=repr(background)), \
                        self.assertRaises(matching.MatchingError):
                    matching.pair_id(BOTTOM, positive, background)
        with self.assertRaises(matching.MatchingError):
            matching.pair_id("unknown-acquisition", "p", "b")

    def test_sha256_pair_identity_collision_blocks(self):
        groups = synthetic_groups(bottom=2)
        with patch.object(matching.hashlib, "sha256") as sha256:
            sha256.return_value.hexdigest.return_value = "0" * 64
            with self.assertRaises(matching.MatchingError):
                small_ledger(groups)

    def test_builder_uses_same_acquisition_and_identical_selected_frames(self):
        groups = synthetic_groups(bottom=2, top=2)
        before = deepcopy(groups)
        ledger = small_ledger(groups)
        for pair in ledger:
            positive = groups[pair["positive_group_id"]]
            background = groups[pair["background_group_id"]]
            self.assertEqual(positive["acquisition_id"], background["acquisition_id"])
            self.assertEqual(pair["acquisition_id"], positive["acquisition_id"])
            self.assertEqual(pair["positive_selected_frames"], pair["background_selected_frames"])
            self.assertEqual(len(set(pair["positive_selected_frames"])), 8)
        self.assertEqual(groups, before)
        separated = {"p": synthetic_group("positive"),
                     "b": synthetic_group("background", acquisition=TOP)}
        self.assertEqual(small_ledger(separated), ())

    def test_group_role_acquisition_and_frame_bounds_are_validated(self):
        for replacement in ({"role": "unknown"}, {"role": True},
                            {"acquisition_id": "unknown"}, {"frames": tuple(range(7)) + (294,)},
                            {"frames": tuple(range(8)) + (True,)}):
            groups = synthetic_groups()
            first = next(iter(groups))
            groups[first].update(replacement)
            with self.subTest(replacement=replacement), self.assertRaises(matching.MatchingError):
                small_ledger(groups)
        for acquisition, last_frame in ((BOTTOM, 293), (TOP, 394)):
            frames = tuple(range(7)) + (last_frame,)
            groups = {"p": synthetic_group("positive", frames, acquisition),
                      "b": synthetic_group("background", frames, acquisition)}
            with self.subTest(acquisition=acquisition):
                self.assertEqual(small_ledger(groups)[0]["shared_frames"], frames)

    def test_builder_and_validator_are_deterministic_under_group_and_frame_permutations(self):
        groups = synthetic_groups(bottom=3, top=2)
        expected = small_ledger(groups)
        permuted = {key: dict(value, frames=value["frames"][::-1])
                    for key, value in reversed(tuple(groups.items()))}
        self.assertEqual(small_ledger(permuted), expected)
        self.assertIsNone(matching.validate_pair_ledger(expected, permuted,
                                                        enforce_expected_cardinality=False))

    def test_validation_rejects_reuse_cross_acquisition_and_wrong_roles(self):
        groups = synthetic_groups(bottom=2, top=1)
        ledger = small_ledger(groups)
        with self.assertRaises(matching.MatchingError):
            matching.validate_pair_ledger(ledger + (deepcopy(ledger[0]),), groups,
                                          enforce_expected_cardinality=False)
        bottom = next(pair for pair in ledger if pair["acquisition_id"] == BOTTOM)
        top = next(pair for pair in ledger if pair["acquisition_id"] == TOP)
        for field, replacement in (("background_group_id", top["background_group_id"]),
                                   ("positive_group_id", bottom["background_group_id"]),
                                   ("acquisition_id", TOP)):
            altered = deepcopy(bottom)
            altered[field] = replacement
            if field == "positive_group_id":
                altered["background_group_id"] = bottom["positive_group_id"]
            altered["pair_id"] = matching.pair_id(altered["acquisition_id"],
                                                  altered["positive_group_id"],
                                                  altered["background_group_id"])
            with self.subTest(field=field), self.assertRaises(matching.MatchingError):
                matching.validate_pair_ledger((altered,), groups, enforce_expected_cardinality=False)

    def test_validation_rejects_corrupt_identity_shared_frames_selection_and_fold(self):
        groups = synthetic_groups()
        ledger = small_ledger(groups)
        selected = ledger[0]["positive_selected_frames"]
        replacements = (("pair_id", "S4P_" + "f" * 64),
                        ("shared_frames", selected[:-1]),
                        ("positive_selected_frames", selected[::-1]),
                        ("background_selected_frames", selected[:-1] + (selected[0],)),
                        ("positive_selected_frames", selected[:-1] + (99,)),
                        ("fold", (ledger[0]["fold"] + 1) % 4), ("fold", True))
        for field, replacement in replacements:
            altered = deepcopy(ledger)
            altered[0][field] = replacement
            with self.subTest(field=field, replacement=replacement), \
                    self.assertRaises(matching.MatchingError):
                matching.validate_pair_ledger(altered, groups, enforce_expected_cardinality=False)
        for field in ledger[0]:
            altered = deepcopy(ledger)
            del altered[0][field]
            with self.subTest(missing=field), self.assertRaises(matching.MatchingError):
                matching.validate_pair_ledger(altered, groups, enforce_expected_cardinality=False)
        altered = deepcopy(ledger)
        altered[0]["historical_fold"] = 2
        with self.assertRaises(matching.MatchingError):
            matching.validate_pair_ledger(altered, groups, enforce_expected_cardinality=False)

    def test_validation_rejects_nonoptimal_support_and_lexicographic_matching(self):
        for frames0 in (tuple(range(8)), tuple(range(12))):
            groups = {"p0": synthetic_group("positive", frames0),
                      "p1": synthetic_group("positive"),
                      "b0": synthetic_group("background", frames0),
                      "b1": synthetic_group("background")}
            nonoptimal = records_for_edges(groups, (("p0", "b1"), ("p1", "b0")))
            with self.subTest(frames0=frames0), self.assertRaises(matching.MatchingError):
                matching.validate_pair_ledger(nonoptimal, groups, enforce_expected_cardinality=False)

    def test_validator_rejects_submaximum_cardinality_even_in_small_synthetic_mode(self):
        groups = synthetic_groups(2)
        ledger = small_ledger(groups)
        with self.assertRaises(matching.MatchingError):
            matching.validate_pair_ledger(ledger[:1], groups, enforce_expected_cardinality=False)
        for invalid in (0, 1, None, "false"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(matching.MatchingError):
                    matching.build_pair_ledger(groups, enforce_expected_cardinality=invalid)
                with self.assertRaises(matching.MatchingError):
                    matching.validate_pair_ledger(ledger, groups, enforce_expected_cardinality=invalid)

    def test_default_cardinality_is_exactly_seventeen_bottom_and_eight_top(self):
        groups = synthetic_groups(17, 8)
        ledger = matching.build_pair_ledger(groups)
        self.assertEqual(len(ledger), 25)
        self.assertEqual(Counter(pair["acquisition_id"] for pair in ledger), {BOTTOM: 17, TOP: 8})
        self.assertIsNone(matching.validate_pair_ledger(ledger, groups))
        for bottom, top in ((16, 8), (17, 7), (18, 8), (16, 9), (0, 0)):
            groups = synthetic_groups(bottom, top)
            with self.subTest(bottom=bottom, top=top):
                with self.assertRaises(matching.MatchingError):
                    matching.build_pair_ledger(groups)
                with self.assertRaises(matching.MatchingError):
                    matching.validate_pair_ledger(small_ledger(groups), groups)


class PairAwareFoldTests(unittest.TestCase):
    def test_stratified_hash_order_and_pair_member_indivisibility(self):
        groups = synthetic_groups(17, 8)
        ledger = matching.build_pair_ledger(groups)
        group_folds = {}
        for acquisition in (BOTTOM, TOP):
            records = [pair for pair in ledger if pair["acquisition_id"] == acquisition]
            expected_order = sorted(records, key=lambda pair: (
                hashlib.sha256(b"STUDY4_FOLD_V1\0" + pair["pair_id"].encode("utf-8")).hexdigest(),
                pair["pair_id"]))
            for index, pair in enumerate(expected_order):
                self.assertEqual(pair["fold"], index % 4)
                for field in ("positive_group_id", "background_group_id"):
                    group = pair[field]
                    self.assertNotIn(group, group_folds)
                    group_folds[group] = pair["fold"]
                self.assertEqual(group_folds[pair["positive_group_id"]],
                                 group_folds[pair["background_group_id"]])
        self.assertEqual(len(group_folds), 50)
        self.assertEqual([sum(pair["fold"] == fold for pair in ledger) for fold in range(4)],
                         [7, 6, 6, 6])
        for acquisition, expected in ((BOTTOM, [5, 4, 4, 4]), (TOP, [2, 2, 2, 2])):
            self.assertEqual([sum(pair["fold"] == fold and pair["acquisition_id"] == acquisition
                                  for pair in ledger) for fold in range(4)], expected)
        for fold in range(4):
            roles = Counter(groups[group]["role"] for group, assigned in group_folds.items()
                            if assigned == fold)
            self.assertEqual(roles["positive"], roles["background"])

    def test_fold_assignment_is_independent_of_input_order_and_old_fold_values(self):
        ledger = small_ledger(synthetic_groups(5, 3))
        inputs = [dict(pair, fold=3) for pair in reversed(ledger)]
        before = deepcopy(inputs)
        assigned = matching.assign_folds(inputs)
        self.assertEqual(assigned, ledger)
        self.assertEqual(inputs, before)
        self.assertTrue(all(all(pair is not original for original in inputs) for pair in assigned))
        self.assertEqual(matching.assign_folds([{k: v for k, v in pair.items() if k != "fold"}
                                               for pair in inputs]), ledger)

    def test_each_acquisition_fold_sequence_restarts_at_zero(self):
        groups = synthetic_groups(5, 3)
        combined = small_ledger(groups)
        for acquisition in (BOTTOM, TOP):
            alone = small_ledger({key: value for key, value in groups.items()
                                  if value["acquisition_id"] == acquisition})
            self.assertEqual({pair["pair_id"]: pair["fold"] for pair in alone},
                             {pair["pair_id"]: pair["fold"] for pair in combined
                              if pair["acquisition_id"] == acquisition})

    def test_fold_hash_ties_are_broken_by_pair_id(self):
        ledger = small_ledger(synthetic_groups(5))
        real_sha256 = hashlib.sha256

        class SameFoldDigest:
            def hexdigest(self):
                return "0" * 64

        def synthetic_fold_hash(data):
            return SameFoldDigest() if data.startswith(b"STUDY4_FOLD_V1\0") else real_sha256(data)

        with patch.object(matching.hashlib, "sha256", side_effect=synthetic_fold_hash):
            assigned = matching.assign_folds(ledger)
        expected = {pair["pair_id"]: index % 4
                    for index, pair in enumerate(sorted(ledger, key=lambda pair: pair["pair_id"]))}
        self.assertEqual({pair["pair_id"]: pair["fold"] for pair in assigned}, expected)

    def test_fold_assignment_rejects_duplicate_pairs_and_group_reuse(self):
        ledger = small_ledger(synthetic_groups(2))
        with self.assertRaises(matching.MatchingError):
            matching.assign_folds(ledger + (dict(ledger[0]),))
        altered = deepcopy(ledger)
        altered[1]["positive_group_id"] = altered[0]["positive_group_id"]
        altered[1]["pair_id"] = matching.pair_id(altered[1]["acquisition_id"],
                                                altered[1]["positive_group_id"],
                                                altered[1]["background_group_id"])
        with self.assertRaises(matching.MatchingError):
            matching.assign_folds(altered)


class PureMatchingBoundaryTests(unittest.TestCase):
    def test_all_public_operations_use_zero_filesystem_or_payload_io(self):
        groups = synthetic_groups(17, 8)
        forbidden = AssertionError("Pure matching attempted filesystem access")
        with ExitStack() as stack:
            stack.enter_context(patch("builtins.open", side_effect=forbidden))
            for name in ("open", "read", "pread", "stat", "lstat", "listdir", "scandir", "readlink"):
                stack.enter_context(patch.object(os, name, side_effect=forbidden))
            for name in ("open", "read_text", "read_bytes", "write_text", "write_bytes",
                         "stat", "lstat", "exists", "iterdir", "glob", "rglob"):
                stack.enter_context(patch.object(Path, name, side_effect=forbidden))
            self.assertEqual(matching.optimize_matching({("p", "b"): 8}), (("p", "b"),))
            self.assertEqual(matching.nearest_integer_rank(3, 2), 1)
            self.assertEqual(matching.select_shared_frames(tuple(range(8)), tuple(range(8))),
                             tuple(range(8)))
            self.assertTrue(matching.pair_id(BOTTOM, "p", "b").startswith("S4P_"))
            ledger = matching.build_pair_ledger(groups)
            self.assertEqual(matching.assign_folds(ledger), ledger)
            self.assertIsNone(matching.validate_pair_ledger(ledger, groups))

    def test_source_has_only_stdlib_dependencies_and_no_io_or_model_calls(self):
        source = (ROOT / "src/snbi_fragmentation/study4_matching.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        banned_imports = {"os", "pathlib", "io", "subprocess", "importlib", "builtins",
                          "pickle", "shelve", "sqlite3", "marshal"}
        forbidden_calls = {"open", "read", "read_bytes", "read_text", "write", "write_bytes",
                           "write_text", "stat", "lstat", "listdir", "scandir", "glob", "rglob",
                           "fit", "predict", "fit_transform", "eval", "exec", "__import__"}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                         else [node.module or ""])
                for name in names:
                    root = name.split(".")[0]
                    self.assertIn(root, sys.stdlib_module_names)
                    self.assertNotIn(root, banned_imports)
                if isinstance(node, ast.ImportFrom):
                    self.assertEqual(node.level, 0)
            if isinstance(node, ast.Call):
                called = node.func.id if isinstance(node.func, ast.Name) else (
                    node.func.attr if isinstance(node.func, ast.Attribute) else "")
                self.assertNotIn(called, forbidden_calls)

    def test_import_and_synthetic_operation_need_no_site_packages(self):
        script = ("import sys; sys.path.insert(0, sys.argv[1]); "
                  "from snbi_fragmentation import study4_matching as m; "
                  "assert m.optimize_matching({('p', 'b'): 8}) == (('p', 'b'),); "
                  "assert not ({'numpy', 'scipy', 'pandas', 'sklearn', 'torch', 'cv2'} & set(sys.modules))")
        result = subprocess.run([sys.executable, "-B", "-S", "-c", script, str(ROOT / "src")],
                                cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


class MatchingFreezeContractTests(unittest.TestCase):
    def test_hierarchical_objectives_and_expected_cardinality_are_frozen(self):
        contract = json.loads((ROOT / "configs/study4/matching-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["lexicographic_objectives"], [
            "MAXIMIZE_MATCHED_PAIR_COUNT", "MAXIMIZE_SUM_OF_COMMON_FRAME_SUPPORT",
            "LEXICOGRAPHICALLY_MINIMUM_SORTED_EDGE_KEY_LIST"])
        self.assertEqual(contract["identity_tie_break_operational_encoding"],
                         "SORTED_(POSITIVE_GROUP_ID,BACKGROUND_GROUP_ID)_TUPLES_NORMAL_STRING_LEXICOGRAPHIC_ORDER")
        self.assertIs(contract["separate_optimization_per_acquisition"], True)
        self.assertEqual(contract["expected_pair_counts_by_acquisition"], {BOTTOM: 17, TOP: 8})
        self.assertEqual(contract["expected_total_pairs"], 25)
        self.assertEqual((matching.EXPECTED_BOTTOM_UP_PAIRS, matching.EXPECTED_TOP_DOWN_PAIRS,
                          matching.EXPECTED_TOTAL_PAIRS), (17, 8, 25))
        self.assertEqual(contract["unexpected_cardinality_outcome"], "BLOCK_AND_STOP")
        self.assertIs(contract["final_pair_identities_not_selected"], True)
        self.assertIs(contract["real_matching_executed"], False)
        self.assertNotIn("PENDING", json.dumps(contract))
        for field in ("independent_of_pixels", "independent_of_features", "independent_of_model_performance"):
            self.assertIs(contract[field], True)

    def test_frame_pair_id_and_stratified_fold_contracts_are_operational(self):
        contract = json.loads((ROOT / "configs/study4/matching-contract.json").read_text(encoding="utf-8"))
        frames = contract["frame_selection"]
        self.assertEqual((frames["min_shared_frames"], frames["timepoints"], matching.T), (8, 8, 8))
        self.assertEqual(frames["relative_positions"], [[k, 7] for k in range(8)])
        self.assertEqual(frames["exact_half_tie"], "LOWER_RANK")
        self.assertEqual(frames["rank_arithmetic"], "INTEGER_QUOTIENT_REMAINDER_NO_FLOAT")
        self.assertIs(frames["same_indices_for_both_pair_members"], True)
        for field in ("interpolation", "synthetic_frames", "short_support_repetition", "padding"):
            self.assertIs(frames[field], False)
        identity = contract["pair_id"]
        self.assertEqual((identity["algorithm"], identity["prefix"], identity["digest_hex_length"]),
                         ("SHA256", "S4P_", 64))
        self.assertIs(identity["embedded_nul_allowed"], False)
        self.assertEqual(identity["collision_outcome"], "BLOCKED")
        folds = contract["folds"]
        self.assertEqual((folds["count"], matching.FOLD_COUNT), (4, 4))
        self.assertIs(folds["pair_is_indivisible"], True)
        self.assertIs(folds["group_train_validation_overlap"], False)
        self.assertIs(folds["historical_fold_reuse"], False)
        self.assertIs(folds["automatic_historical_fold_reuse"], False)
        self.assertEqual(folds["assignment"], "SHA256_PAIR_ID_ORDER_ROUND_ROBIN_SEPARATELY_PER_ACQUISITION")
        self.assertEqual(folds["ordering"], ["fold_key", "pair_id"])
        self.assertEqual(folds["expected_pair_counts_by_acquisition"],
                         {BOTTOM: [5, 4, 4, 4], TOP: [2, 2, 2, 2]})
        self.assertEqual(folds["expected_total_pair_counts"], [7, 6, 6, 6])

    def test_freeze_authority_keeps_all_scientific_access_closed(self):
        authority = json.loads((ROOT / "configs/study4/authority.json").read_text(encoding="utf-8"))
        self.assertEqual(authority["phase"], "S4_B0A_FINAL_MATCHING_FOLD_FREEZE")
        self.assertIs(authority["future_final_matching_requires_explicit_author_decision"], True)
        for field in ("scientific_execution_authorized", "experimental_binary_reads_authorized",
                      "payload_row_reads_authorized", "experimental_metadata_analysis_authorized",
                      "feature_extraction_authorized", "matching_execution_authorized",
                      "model_fit_authorized", "receipt_creation_authorized", "development_access",
                      "test_access", "silver_access", "video_access", "study3_reopened",
                      "study3_test_reopened", "new_model_search", "new_label_mining",
                      "new_background_mining", "automatic_continuation"):
            with self.subTest(field=field):
                self.assertIs(authority[field], False)
        self.assertEqual(authority["retries"], 0)

    def test_coverage_control_remains_pending_without_model_authority(self):
        contract = json.loads((ROOT / "configs/study4/evaluation-contract.json").read_text(encoding="utf-8"))
        gate = contract["coverage_gate"]
        self.assertIsNone(gate["operational_threshold"])
        self.assertIsNone(gate["operational_statistic"])
        self.assertEqual(gate["decision_rule_status"],
                         "PENDING_AUTHOR_DELIBERATION_AND_PRE_SCIENTIFIC_EXECUTION_FREEZE")
        self.assertIs(gate["passing_does_not_automatically_authorize_visual_gate"], True)
        self.assertIs(contract["future_fit_budget"]["currently_authorizes_fits"], False)


if __name__ == "__main__":
    unittest.main()
