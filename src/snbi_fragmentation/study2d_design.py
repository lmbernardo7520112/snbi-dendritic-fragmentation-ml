"""Pure TRAIN-only metadata design and descriptive Study2-D summaries.

No files, pixels, predictions from prior DEVELOPMENT/TEST, features or learners
are accessed here. The controller authenticates the historical textual input.
"""

from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
import math
import statistics


ACQUISITIONS = ("bottom_up_anti_parallel", "top_down_parallel")
EXPECTED_FOLD_SHA = "85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2"
EXPECTED_TRAIN_ROWS = {"GOLD": 3858, "BACKGROUND": 7049}
K_QUOTAS = {4: (3, 1), 8: (6, 2), 12: (9, 3), 17: (13, 4), 24: (18, 6)}
SALTS = tuple("STUDY2D_GROUP_R" + str(i) for i in range(1, 6))
DENSITIES = ("D1", "D3", "D5", "DALL")
WEIGHTINGS = ("GROUP_EQUAL", "OBSERVATION_EQUAL")
FIT_BUDGET = {"A": 84, "B": 12, "C": 4, "total_distinct": 100,
              "conceptual_conditions": 108, "reuse_references": 8}


class AttributionDesignError(ValueError):
    """Invalid metadata or a divergence from the predeclared experiment."""


def require(value, message):
    if not value:
        raise AttributionDesignError(message)


def json_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def design_contract():
    return {"historical_cv_fold_sha256": EXPECTED_FOLD_SHA,
            "allowed_split": "TRAIN", "allowed_tiers": ["GOLD", "BACKGROUND"],
            "expected_train_rows": dict(EXPECTED_TRAIN_ROWS), "groups_per_class": 32,
            "K_quotas": {str(k): dict(zip(ACQUISITIONS, quota)) for k, quota in K_QUOTAS.items()},
            "replicate_salts": list(SALTS), "class_rank_strings": ["POSITIVE", "BACKGROUND"],
            "group_ranking": "SHA256(salt|fold_id|class|acquisition|group_id); tie by group_id",
            "fold_ids": [0, 1, 2, 3], "densities": list(DENSITIES),
            "median_rule": "zero-based index (n-1)//2; lower median",
            "quantile_rule": "nearest rank q*(n-1); exact half ties choose lower index; rational arithmetic",
            "quantiles": {"D3": [[1, 4], [1, 2], [3, 4]],
                          "D5": [[0, 1], [1, 4], [1, 2], [3, 4], [1, 1]]},
            "short_group_rule": "if n<3 for D3 or n<5 for D5 use all rows; then remove duplicates",
            "row_order": "preserve relative order from original C TRAIN sample manifest",
            "weightings": list(WEIGHTINGS), "fit_budget": dict(FIT_BUDGET),
            "execution_order": "A: fold,K,replicate; B: fold,D3/D5/DALL; C: fold",
            "descriptive_std_ddof": 0, "summary_median": "conventional median; mean of two middle values if even",
            "descriptor_primary_contrasts": {"A": "K24_MINUS_K17", "B": "DALL_MINUS_D1",
                                             "C": "GROUP_EQUAL_MINUS_OBSERVATION_EQUAL"},
            "descriptor_zero_comparison": "exact numeric zero; no tolerance or significance test",
            "effect_scope": "conditional post-hoc contrasts; effects are not additive causal percentages"}


def _row_groups(rows):
    require(type(rows) is list and rows, "explicit nonempty TRAIN rows required")
    groups, identities, ids, frames = defaultdict(list), {}, set(), set()
    for row in rows:
        require(type(row) is dict and row.get("split") == "TRAIN", "DEV/TEST/unknown split forbidden")
        label, tier = row.get("label"), row.get("tier")
        require(type(label) is int and (label, tier) in {(1, "GOLD"), (0, "BACKGROUND")},
                "SILVER and unlabeled rows forbidden; exact GOLD/BACKGROUND labels required")
        gid, sid, acquisition, frame = (row.get(k) for k in
                                       ("group_id", "sample_id", "acquisition_id", "frame_index"))
        require(type(gid) is str and gid and type(sid) is str and sid
                and acquisition in ACQUISITIONS and type(frame) is int and frame >= 0,
                "canonical row/group/acquisition/frame identity required")
        require(sid not in ids and (gid, frame) not in frames, "duplicate row ID or group/frame")
        identity = (acquisition, label)
        require(gid not in identities or identities[gid] == identity, "group identity crosses class/acquisition")
        identities[gid] = identity; ids.add(sid); frames.add((gid, frame)); groups[gid].append(row)
    return dict(groups), identities


def temporal_sample_ids(group_rows, density):
    """Select ranks only; lower half ties preserve the D1 median at every level."""
    groups, _ = _row_groups(group_rows)
    require(len(groups) == 1 and density in DENSITIES, "one group and frozen density required")
    ordered = sorted(group_rows, key=lambda r: (r["frame_index"], r["sample_id"]))
    n = len(ordered)
    if density == "DALL" or (density == "D3" and n < 3) or (density == "D5" and n < 5):
        indices = list(range(n))
    elif density == "D1":
        indices = [(n - 1) // 2]
    else:
        fractions = [(1, 4), (1, 2), (3, 4)] if density == "D3" else [(0, 1), (1, 4), (1, 2), (3, 4), (1, 1)]
        indices = []
        for numerator, denominator in fractions:
            rank, remainder = divmod(numerator * (n - 1), denominator)
            indices.append(rank + int(2 * remainder > denominator))
        indices = sorted(set(indices))
    return [ordered[i]["sample_id"] for i in indices]


def _rank(salt, fold, label, acquisition, group):
    class_name = "POSITIVE" if label else "BACKGROUND"
    return hashlib.sha256(f"{salt}|{fold}|{class_name}|{acquisition}|{group}".encode()).hexdigest()


def build_attribution_design(c_split):
    """Construct the sole 100-fit plan from the authenticated C manifest."""
    require(type(c_split) is dict and c_split.get("status") == "PASS", "historical C split must pass")
    folds = c_split.get("cv_fold_by_group")
    require(type(folds) is dict and json_sha(folds) == EXPECTED_FOLD_SHA
            and c_split.get("hashes", {}).get("cv_fold_by_group_sha256") == EXPECTED_FOLD_SHA,
            "historical TRAIN fold hash differs")
    require(type(c_split.get("samples")) is list and type(c_split.get("groups")) is list,
            "historical rows and groups required")
    rows = deepcopy([r for r in c_split["samples"] if r.get("split") == "TRAIN"
                     and r.get("tier") in {"GOLD", "BACKGROUND"}])
    groups, identities = _row_groups(rows)
    require(Counter(r["tier"] for r in rows) == EXPECTED_TRAIN_ROWS,
            "TRAIN GOLD3858/BACKGROUND7049 row budget differs")
    original_groups = [g for g in c_split["groups"] if g.get("split") == "TRAIN"]
    require(len(original_groups) == 64 and len(groups) == 64 and set(folds) == set(groups),
            "exact historical64 TRAIN groups required")
    require({g["group_id"] for g in original_groups} == set(groups), "TRAIN group allowlist differs")
    for group in original_groups:
        require(identities[group["group_id"]] == (group["acquisition_id"], group["label"]),
                "historical group signature differs")
    for gid, group_rows in groups.items():
        require(type(folds[gid]) is int and folds[gid] in range(4)
                and all(r.get("cv_fold") == folds[gid] for r in group_rows), "row fold differs from frozen group")
    temporal = {gid: {density: temporal_sample_ids(group_rows, density) for density in DENSITIES}
                for gid, group_rows in sorted(groups.items())}
    validation, rankings, fits = {}, {}, []
    for fold in range(4):
        validation[str(fold)] = [r["sample_id"] for r in rows if folds[r["group_id"]] == fold]
        strata = Counter(identities[g] for g in groups if folds[g] == fold)
        require(strata == Counter({(a, label): count for a, count in zip(ACQUISITIONS, (6, 2))
                                   for label in (0, 1)}), "historical validation strata differ")
        rankings[str(fold)] = {}
        for replicate, salt in enumerate(SALTS, 1):
            ranks = {}
            for acquisition in ACQUISITIONS:
                ranks[acquisition] = {}
                for label in (0, 1):
                    pool = [g for g in groups if folds[g] != fold and identities[g] == (acquisition, label)]
                    pool.sort(key=lambda gid: (_rank(salt, fold, label, acquisition, gid), gid))
                    ranks[acquisition][str(label)] = pool
            rankings[str(fold)][str(replicate)] = ranks

    def spec(part, fold, K, replicate, density, weighting, selected_groups):
        selected = set().union(*(set(temporal[g][density]) for g in selected_groups))
        selected_ids = [r["sample_id"] for r in rows if r["sample_id"] in selected]
        fit_id = (f"A-f{fold}-K{K}-r{replicate}" if replicate is not None else f"A-f{fold}-K24-all") if part == "A" else f"B-f{fold}-{density}" if part == "B" else f"C-f{fold}-OBSERVATION_EQUAL"
        return {"fit_id": fit_id, "part": part, "fold": fold, "K": K, "replicate": replicate,
                "density": density, "weighting": weighting, "training_group_ids": sorted(selected_groups),
                "train_sample_ids": selected_ids, "validation_sample_ids": validation[str(fold)],
                "training_sample_ids_sha256": json_sha(selected_ids),
                "validation_sample_ids_sha256": json_sha(validation[str(fold)]),
                "effective_rows_per_group": {g: len(temporal[g][density]) for g in sorted(selected_groups)},
                "fit_required": True}

    for fold in range(4):
        for K, quotas in K_QUOTAS.items():
            for replicate in ([None] if K == 24 else range(1, 6)):
                if K == 24:
                    selected = {g for g in groups if folds[g] != fold}
                else:
                    rank = rankings[str(fold)][str(replicate)]
                    selected = set().union(*(set(rank[a][str(label)][:quota])
                                            for a, quota in zip(ACQUISITIONS, quotas) for label in (0, 1)))
                fits.append(spec("A", fold, K, replicate, "D1", "GROUP_EQUAL", selected))
    for fold in range(4):
        pool = {g for g in groups if folds[g] != fold}
        for density in ("D3", "D5", "DALL"):
            fits.append(spec("B", fold, 24, None, density, "GROUP_EQUAL", pool))
    for fold in range(4):
        fits.append(spec("C", fold, 24, None, "DALL", "OBSERVATION_EQUAL",
                         {g for g in groups if folds[g] != fold}))
    refs = [{"part": "B", "fold": f, "K": 24, "density": "D1", "weighting": "GROUP_EQUAL",
             "reuse_id": f"B-f{f}-D1", "source_fit_id": f"A-f{f}-K24-all", "fit_required": False}
            for f in range(4)]
    refs += [{"part": "C", "fold": f, "K": 24, "density": "DALL", "weighting": "GROUP_EQUAL",
              "reuse_id": f"C-f{f}-GROUP_EQUAL", "source_fit_id": f"B-f{f}-DALL", "fit_required": False}
             for f in range(4)]
    design = {"status": "PASS", "schema_version": 1, "contract": design_contract(), "rows": rows,
              "groups": deepcopy(original_groups), "cv_fold_by_group": deepcopy(folds),
              "historical_cv_fold_sha256": EXPECTED_FOLD_SHA, "allowed_rows_sha256": json_sha(rows),
              "temporal_samples": temporal, "group_rankings": rankings,
              "validation_sample_ids_by_fold": validation, "fits": fits, "reuse_refs": refs,
              "fit_budget": dict(FIT_BUDGET), "allowed_row_count": len(rows),
              "TRAIN_ONLY": True, "SILVER_USED": False, "MODEL_SELECTION_REOPENED": False}
    design["design_sha256"] = json_sha(design)
    validate_attribution_design(design)
    return design


def validate_attribution_design(design):
    """Validate frozen membership and schedule, without rebuilding/reranking it."""
    require(type(design) is dict and design.get("status") == "PASS", "frozen design required")
    require(design.get("design_sha256") == json_sha({k: v for k, v in design.items() if k != "design_sha256"}),
            "design content hash differs")
    require(design.get("contract") == design_contract() and design.get("fit_budget") == FIT_BUDGET,
            "design method contract differs")
    rows = design.get("rows"); groups, identities = _row_groups(rows)
    require(Counter(r["tier"] for r in rows) == EXPECTED_TRAIN_ROWS and len(groups) == 64,
            "exact original TRAIN input budget differs")
    require(design.get("allowed_rows_sha256") == json_sha(rows), "allowed row hash differs")
    folds = design.get("cv_fold_by_group")
    require(type(folds) is dict and set(folds) == set(groups) and json_sha(folds) == EXPECTED_FOLD_SHA,
            "historical TRAIN fold hash differs")
    require(all(type(f) is int and f in range(4) for f in folds.values()), "invalid historical fold")
    by_id = {r["sample_id"]: r for r in rows}
    fits = design.get("fits")
    require(type(fits) is list and len(fits) == 100 and len({f.get("fit_id") for f in fits}) == 100,
            "exactly100 unique fit identifiers required")
    require(Counter(f.get("part") for f in fits) == {"A": 84, "B": 12, "C": 4}, "part fit budget differs")
    expected_ids = [f"A-f{f}-K{k}-r{r}" if k < 24 else f"A-f{f}-K24-all"
                    for f in range(4) for k in K_QUOTAS
                    for r in (range(1, 6) if k < 24 else [None])]
    expected_ids += [f"B-f{f}-{d}" for f in range(4) for d in ("D3", "D5", "DALL")]
    expected_ids += [f"C-f{f}-OBSERVATION_EQUAL" for f in range(4)]
    require([s["fit_id"] for s in fits] == expected_ids, "fit condition identifiers or exact execution order differ")
    require(design.get("TRAIN_ONLY") is True and design.get("SILVER_USED") is False
            and design.get("MODEL_SELECTION_REOPENED") is False
            and design.get("allowed_row_count") == len(rows), "terminal design boundaries differ")
    last_part = "A"
    for s in fits:
        require(s["part"] >= last_part, "A/B/C execution order differs"); last_part = s["part"]
        fold, K = s.get("fold"), s.get("K")
        require(type(fold) is int and fold in range(4) and type(K) is int and K in K_QUOTAS,
                "unknown fold/K")
        require(s.get("density") in DENSITIES and s.get("weighting") in WEIGHTINGS,
                "unknown density/weighting")
        if s["part"] == "A":
            require(s["density"] == "D1" and s["weighting"] == "GROUP_EQUAL"
                    and ((K == 24 and s["replicate"] is None) or (K < 24 and type(s["replicate"]) is int
                         and s["replicate"] in range(1, 6))), "part A differs")
        elif s["part"] == "B":
            require(K == 24 and s["density"] in {"D3", "D5", "DALL"}
                    and s["weighting"] == "GROUP_EQUAL" and s["replicate"] is None, "part B differs")
        else:
            require(K == 24 and s["density"] == "DALL" and s["weighting"] == "OBSERVATION_EQUAL"
                    and s["replicate"] is None, "part C differs")
        expected_id = ((f"A-f{fold}-K{K}-r{s['replicate']}" if K < 24 else f"A-f{fold}-K24-all")
                       if s["part"] == "A" else f"B-f{fold}-{s['density']}" if s["part"] == "B"
                       else f"C-f{fold}-OBSERVATION_EQUAL")
        require(s["fit_id"] == expected_id and s.get("fit_required") is True,
                "fit identifier does not bind its condition or fit flag")
        train_ids, validation_ids = s.get("train_sample_ids"), s.get("validation_sample_ids")
        require(type(train_ids) is list and train_ids and len(set(train_ids)) == len(train_ids)
                and set(train_ids) <= set(by_id), "training ID allowlist differs")
        expected_validation = [r["sample_id"] for r in rows if folds[r["group_id"]] == fold]
        require(validation_ids == expected_validation and validation_ids == design["validation_sample_ids_by_fold"][str(fold)],
                "validation side must contain all original GOLD/BG rows in historical held-out groups")
        require(not set(train_ids) & set(validation_ids), "train/validation row leakage")
        train_groups = {by_id[i]["group_id"] for i in train_ids}
        require(all(folds[g] != fold for g in train_groups) and sorted(train_groups) == s["training_group_ids"],
                "group leakage or group membership divergence")
        strata = Counter(identities[g] for g in train_groups)
        require(strata == Counter({(a, label): n for a, n in zip(ACQUISITIONS, K_QUOTAS[K]) for label in (0, 1)}),
                "training acquisition/class quota differs")
        expected_ids_for_density = set().union(*(set(design["temporal_samples"][g][s["density"]]) for g in train_groups))
        require(train_ids == [r["sample_id"] for r in rows if r["sample_id"] in expected_ids_for_density],
                "temporal row selection/order differs")
        require(s["training_sample_ids_sha256"] == json_sha(train_ids)
                and s["validation_sample_ids_sha256"] == json_sha(validation_ids), "fit membership hash differs")
        require(s["effective_rows_per_group"] == dict(sorted(Counter(by_id[i]["group_id"] for i in train_ids).items())),
                "effective rows per group differs")
    refs = design.get("reuse_refs")
    require(type(refs) is list and len(refs) == 8 and all(r.get("fit_required") is False for r in refs),
            "eight reuse-only references required")
    expected_refs = {(f"B-f{f}-D1", f"A-f{f}-K24-all") for f in range(4)}
    expected_refs |= {(f"C-f{f}-GROUP_EQUAL", f"B-f{f}-DALL") for f in range(4)}
    require({(r.get("reuse_id"), r.get("source_fit_id")) for r in refs} == expected_refs,
            "reuse references differ")
    return {"status": "PASS", "allowed_rows": len(rows), "TRAIN_groups": len(groups),
            "distinct_fits": len(fits), "reuse_references": len(refs), "planner_reexecuted": False}


validate_design = validate_attribution_design


def _stats(values):
    require(values and all(type(v) in (float, int) and math.isfinite(v) for v in values),
            "finite recorded scores required")
    mean = math.fsum(values) / len(values)
    return {"mean": mean, "median": statistics.median(values),
            "standard_deviation": math.sqrt(math.fsum((v - mean) ** 2 for v in values) / len(values)),
            "std_ddof": 0, "min": min(values), "max": max(values), "n_fits": len(values)}


def summarize_attribution(design, results_by_fit):
    """Describe all frozen contrasts; never rank/select a replacement pipeline."""
    validate_attribution_design(design)
    specs = {s["fit_id"]: s for s in design["fits"]}
    require(type(results_by_fit) is dict and set(results_by_fit) == set(specs), "all100 and only100 fit results required")
    for fid, result in results_by_fit.items():
        require(result.get("fit_id") == fid and result.get("spec") == specs[fid], "result/spec binding differs")
        m = result.get("metrics", {})
        require(type(m.get("primary_gmba")) in (int, float) and math.isfinite(m["primary_gmba"])
                and 0 <= m["primary_gmba"] <= 1, "invalid primary GMBA")
        require(set(m.get("per_acquisition", {})) == set(ACQUISITIONS), "both acquisition metric records required")
        for a in ACQUISITIONS:
            value = m["per_acquisition"][a].get("primary_gmba")
            require(type(value) in (float, int) and math.isfinite(value) and 0 <= value <= 1,
                    "invalid per-acquisition GMBA")

    def score(fid, acquisition=None):
        m = results_by_fit[fid]["metrics"]
        return m["primary_gmba"] if acquisition is None else m["per_acquisition"][acquisition]["primary_gmba"]

    def level(ids):
        secondary = {}
        for name in ("balanced_accuracy", "accuracy", "precision", "recall", "f1"):
            secondary["observation_" + name] = _stats([results_by_fit[i]["metrics"]["observation"][name] for i in ids])
        for name in ("positive_group_macro_recall", "negative_group_macro_specificity"):
            secondary[name] = _stats([results_by_fit[i]["metrics"][name] for i in ids])
        return {"fit_ids": ids, "global": _stats([score(i) for i in ids]),
                "per_acquisition": {a: _stats([score(i, a) for i in ids]) for a in ACQUISITIONS},
                "secondary_statistics": secondary}

    def contrast(pairs):
        output = {}
        for acquisition in (None, *ACQUISITIONS):
            records = [{"fold": specs[comparison]["fold"], "replicate": specs[comparison]["replicate"],
                        "reference_fit_id": reference, "comparison_fit_id": comparison,
                        "delta": score(reference, acquisition) - score(comparison, acquisition)}
                       for reference, comparison in pairs]
            values = [r["delta"] for r in records]; stats = _stats(values)
            stats.update(mean_paired_delta=stats["mean"], median_paired_delta=stats["median"],
                         positive_delta_count=sum(v > 0 for v in values), zero_delta_count=sum(v == 0 for v in values),
                         negative_delta_count=sum(v < 0 for v in values), paired_deltas=records,
                         n_pairs=len(values))
            output["global" if acquisition is None else acquisition] = stats
        return {"global": output.pop("global"), "per_acquisition": output}

    def descriptor(c, threshold, weighting=False):
        s = c["global"]
        if s["mean_paired_delta"] <= 0:
            return "NO_GROUP_EQUAL_BENEFIT" if weighting else "NON_POSITIVE"
        if s["positive_delta_count"] >= threshold:
            return "CONSISTENT_GROUP_EQUAL_BENEFIT" if weighting else "CONSISTENT_POSITIVE"
        return "MIXED_GROUP_EQUAL_BENEFIT" if weighting else "MIXED_POSITIVE"

    part_a = {"levels": {}, "contrasts": {}, "distinct_fits": 84}
    for K in K_QUOTAS:
        ids = [s["fit_id"] for s in design["fits"] if s["part"] == "A" and s["K"] == K]
        part_a["levels"][str(K)] = level(ids)
        if K < 24:
            pairs = [(f"A-f{f}-K24-all", f"A-f{f}-K{K}-r{r}") for f in range(4) for r in range(1, 6)]
            part_a["contrasts"][f"K24_MINUS_K{K}"] = contrast(pairs)
    part_a["descriptor"] = descriptor(part_a["contrasts"]["K24_MINUS_K17"], 15)
    part_a["descriptor_contrast"] = "K24_MINUS_K17"
    part_a["dependence_note"] = "Each fold's K24 baseline is reused for five replicate contrasts; twenty pairs are not independent experiments."
    part_b = {"levels": {}, "contrasts": {}, "conceptual_fits": 16, "new_distinct_fits": 12, "reused_results": 4}
    density_ids = {d: [f"A-f{f}-K24-all" if d == "D1" else f"B-f{f}-{d}" for f in range(4)] for d in DENSITIES}
    for d, ids in density_ids.items():
        part_b["levels"][d] = level(ids)
    for high, low in (("D3", "D1"), ("D5", "D1"), ("DALL", "D1"), ("DALL", "D5")):
        part_b["contrasts"][high + "_MINUS_" + low] = contrast(list(zip(density_ids[high], density_ids[low])))
    part_b["descriptor"] = descriptor(part_b["contrasts"]["DALL_MINUS_D1"], 3)
    part_b["descriptor_contrast"] = "DALL_MINUS_D1"
    group_ids = density_ids["DALL"]; observation_ids = [f"C-f{f}-OBSERVATION_EQUAL" for f in range(4)]
    part_c = {"levels": {"GROUP_EQUAL": level(group_ids), "OBSERVATION_EQUAL": level(observation_ids)},
              "contrast": contrast(list(zip(group_ids, observation_ids))), "new_distinct_fits": 4,
              "reused_results": 4}
    part_c["descriptor"] = descriptor(part_c["contrast"], 3, True)
    part_c["descriptor_contrast"] = "GROUP_EQUAL_MINUS_OBSERVATION_EQUAL"
    attribution = {"GROUP_DIVERSITY_DESCRIPTOR": part_a["descriptor"],
                   "GROUP_DIVERSITY_DELTA_K24_K17": part_a["contrasts"]["K24_MINUS_K17"]["global"]["mean_paired_delta"],
                   "GROUP_DIVERSITY_DELTA_K24_K4": part_a["contrasts"]["K24_MINUS_K4"]["global"]["mean_paired_delta"],
                   "TEMPORAL_DENSITY_DESCRIPTOR": part_b["descriptor"],
                   "TEMPORAL_DENSITY_DELTA_ALL_1": part_b["contrasts"]["DALL_MINUS_D1"]["global"]["mean_paired_delta"],
                   "GROUP_WEIGHTING_DESCRIPTOR": part_c["descriptor"],
                   "GROUP_WEIGHTING_DELTA": part_c["contrast"]["global"]["mean_paired_delta"],
                   "DISTINCT_RF_FITS": 100, "MODEL_SELECTION_REOPENED": False,
                   "analysis_kind": "POST_HOC_CONTROLLED_ATTRIBUTION_ANALYSIS",
                   "effects_are_additive": False, "p_values_computed": False,
                   "secondary_contrast_descriptors": "NOT_DEFINED; descriptors above apply only to their preregistered primary contrast"}
    table = [{"condition": f"K{k}/D1/GROUP_EQUAL", "changes": "training group count/diversity",
              "fixed": "RF/LBP/folds/validation/density/weighting", "mean_gmba": part_a["levels"][str(k)]["global"]["mean"]}
             for k in K_QUOTAS]
    table += [{"condition": f"K24/{d}/GROUP_EQUAL", "changes": "within-group temporal rows",
               "fixed": "RF/LBP/folds/validation/groups/total input weight per group",
               "mean_gmba": part_b["levels"][d]["global"]["mean"]} for d in ("D3", "D5", "DALL")]
    table += [{"condition": "K24/DALL/OBSERVATION_EQUAL", "changes": "row weighting",
               "fixed": "RF/LBP/folds/validation/groups/exact training rows",
               "mean_gmba": part_c["levels"]["OBSERVATION_EQUAL"]["global"]["mean"]}]
    terminal = {k: attribution[k] for k in (
        "GROUP_DIVERSITY_DESCRIPTOR", "GROUP_DIVERSITY_DELTA_K24_K17", "GROUP_DIVERSITY_DELTA_K24_K4",
        "TEMPORAL_DENSITY_DESCRIPTOR", "TEMPORAL_DENSITY_DELTA_ALL_1",
        "GROUP_WEIGHTING_DESCRIPTOR", "GROUP_WEIGHTING_DELTA")}
    markdown = "| Condição | O que muda | O que fica fixo | GMBA médio |\n| --- | --- | --- | ---: |\n"
    markdown += "\n".join(f"| {r['condition']} | {r['changes']} | {r['fixed']} | {r['mean_gmba']!r} |" for r in table) + "\n"
    return {"status": "PASS", "part_a": part_a, "part_b": part_b, "part_c": part_c,
            "attribution_summary": attribution, "narrative_bridge_table": table,
            "terminal_fields": terminal, "narrative_bridge_markdown": markdown,
            "condition_means_are_descriptive_not_independent_replicates": True,
            "model_or_pipeline_selected": False}
