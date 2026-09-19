"""Development-only relative calibration of the unchanged SOLUTE V1 kernels.

This module performs no I/O. Translated feature sampling is the exact integer
pullback of a translated image, without interpolation, wrapping or padding.
It never returns an admissible experimental transformation or opens a holdout.
"""

import math

from . import ti2r_solute_direct_registration as v1


PERTURBATIONS = ((1, 0), (-1, 0), (0, 1), (0, -1),
                 (2, 0), (-2, 0), (0, 2), (0, -2),
                 (4, 0), (-4, 0), (0, 4), (0, -4),
                 (2, 2), (2, -2), (-2, 2), (-2, -2))
CORRECTIONS = tuple((x, y) for y in range(-4, 5) for x in range(-4, 5))
EXPERIMENTS = ((0, 0),) + PERTURBATIONS
PAD = 8
SAMPLING_OFFSETS = tuple(sorted({(-px-cx, -py-cy)
                                for px, py in EXPERIMENTS
                                for cx, cy in CORRECTIONS}, key=lambda p: (p[1], p[0])))
INDEX = {offset: i for i, offset in enumerate(SAMPLING_OFFSETS)}
PASS = "PASS"
BLOCKED = "BLOCKED_METHOD_NOT_DISCRIMINATIVE"


def validate_config(config):
    expected = {
        "schema": "TI2R-SOLUTE-V2-D-METHOD-1",
        "perturbations_dxdy": [list(p) for p in PERTURBATIONS],
        "correction_search_dxdy": [list(c) for c in CORRECTIONS],
        "common_support_erosion_radius_px": PAD,
        "minimum_recovery_margin": 0.005,
        "maximum_recovery_error_px": 0.5,
        "required_recoveries_per_metric_per_frame": 16,
        "dependency_versions": {"numpy": "1.26.4", "scipy": "1.11.4"},
        "absolute_identity_floors_are_gates": False,
        "identity_positive_control": [0, 0],
        "historical_absolute_floors": {"SS8": 0.9, "NGF": 0.8},
        "v1_config": "configs/registration/ti2r-solute-direct-method.json",
        "new_absolute_floors": None,
        "descriptor_implementations": "unchanged_v1",
        "ngf_eta": "original_unperturbed_individual_block_unchanged_v1",
        "coordinate_convention": "T_p_M(x)=M(x-p);corrected=T_c_T_p_M;true_c=-p",
        "correction_sampling_offset": "-perturbation-correction",
        "original_spatial_controls": "unchanged_v1_48_offsets_radius_3",
        "original_residuals": "unchanged_v1_7_by_7_ngf_peak_and_parabolic_measurement",
        "scientific_mask": "unchanged_v1_plus_required_common_translation_support",
        "holdout_access": "forbidden_all_eight_buffers",
        "outlier_rejection": False,
        "perturbations_are_experimental_replicates": False,
    }
    # Equality alone would admit bool as int and float for integer coordinates.
    import json
    if json.dumps(config, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise v1.SoluteRegistrationError("V2-D preregistered configuration changed")


def _sample(array, offset=(0, 0)):
    """Crop only supported samples from an eight-pixel-expanded feature block."""
    dx, dy = offset
    if type(dx) is not int or type(dy) is not int or max(abs(dx), abs(dy)) > PAD:
        raise v1.SoluteRegistrationError("integer pullback exceeds frozen support")
    h, w = array.shape[-2] - 2 * PAD, array.shape[-1] - 2 * PAD
    return array[..., PAD+dy:PAD+dy+h, PAD+dx:PAD+dx+w]


def _expanded_features(frame, block, role, config):
    """The V1 descriptor and eta, with only a larger supported crop extent."""
    np, _ = v1._runtime()
    x0, y0, x1, y1 = block["xyxy"]
    if x0 < PAD + 3 or y0 < PAD + 3 or x1 + PAD + 3 > frame.luminance.shape[1] or y1 + PAD + 3 > frame.luminance.shape[0]:
        raise v1.SoluteRegistrationError("frozen block cannot contain descriptor and translation footprint")
    if role == "selection":
        patch = frame.luminance[y0-PAD-3:y1+PAD+3, x0-PAD-3:x1+PAD+3]
        features = v1.self_similarity(patch, config)[:, 3:-3, 3:-3]
        eta = None
    elif role == "audit":
        # Reuse exactly the original V1 central block eta, not the expanded crop.
        eta = v1._features(frame, block, role, config)["eta"]
        gx = frame.gx[y0-PAD:y1+PAD, x0-PAD:x1+PAD]
        gy = frame.gy[y0-PAD:y1+PAD, x0-PAD:x1+PAD]
        denominator = np.sqrt(gx * gx + gy * gy + eta * eta)
        features = np.stack((gx / denominator, gy / denominator)).astype(np.float32)
    else:
        raise v1.SoluteRegistrationError("unknown frozen descriptor role")
    return {"features": features, "eta": eta}


def _recovery_record(perturbation, scores, supported, config, v2_config):
    true = (-perturbation[0], -perturbation[1])
    record = {"perturbation_dxdy": list(perturbation), "true_correction_dxdy": list(true),
              "scores": scores, "true_score": None, "correct_rank": None,
              "best_correction_dxdy": None, "best_corrections_dxdy": [], "unique_maximum": False,
              "best_competitor_score": None, "best_competitor_corrections_dxdy": [], "margin": None,
              "winning_score": None, "winner_runner_up_score": None, "winner_margin": None,
              "sampling_offsets_dxdy": [[-perturbation[0]-c[0], -perturbation[1]-c[1]] for c in CORRECTIONS],
              "recovery_error_px": None, "status": "FAIL_SUPPORT"}
    if not scores or any(score is None for score in scores):
        return record
    true_index = CORRECTIONS.index(true)
    peak = max(scores)
    tolerance = config["peak_tie_tolerance"]
    winners = [CORRECTIONS[i] for i, score in enumerate(scores) if abs(score-peak) <= tolerance]
    # Rank is competition rank under the unchanged numerical tie tolerance.
    true_score = scores[true_index]
    rank = 1 + sum(score > true_score + tolerance for score in scores)
    other_scores = [score for i, score in enumerate(scores) if i != true_index]
    second = max(other_scores)
    runners = [CORRECTIONS[i] for i, score in enumerate(scores)
               if i != true_index and abs(score-second) <= tolerance]
    unique = len(winners) == 1
    best = winners[0] if unique else None
    error = math.hypot(best[0]-true[0], best[1]-true[1]) if unique else None
    margin = true_score-second
    passed = (supported and unique and best == true and error <= v2_config["maximum_recovery_error_px"]
              and margin >= v2_config["minimum_recovery_margin"])
    record.update(true_score=true_score, correct_rank=rank, best_correction_dxdy=list(best) if best else None,
                  best_corrections_dxdy=[list(c) for c in winners], unique_maximum=unique,
                  best_competitor_score=second, best_competitor_corrections_dxdy=[list(c) for c in runners],
                  winning_score=peak, winner_runner_up_score=sorted(scores, reverse=True)[1],
                  winner_margin=peak-sorted(scores, reverse=True)[1],
                  margin=margin, recovery_error_px=error,
                  status="PASS" if passed else ("FAIL_RECOVERY" if supported else "FAIL_SUPPORT"))
    return record


def calibrate_role(reference, moving, reference_information, moving_information, role, config, v2_config):
    """All 16 primary perturbations, plus identity, on a single common support.

Sampling M(x-p-c) is exactly T_c(T_p M)(x) for integer p,c. Descriptor
translation equivariance permits computing each distinct displacement once;
the complete 17 by 81 score matrix is retained separately for every block.
No shifted raster, padded value or edge enters a score.
"""
    np, ndimage = v1._runtime()
    validate_config(v2_config)
    mask_name = "descriptor_mask" if role == "selection" else "gradient_mask"
    common = ndimage.binary_erosion(getattr(reference, mask_name) & getattr(moving, mask_name),
                                   structure=np.ones((2*PAD+1, 2*PAD+1), dtype=bool), border_value=0)
    moving_blocks = {b["id"]: b for b in moving_information["blocks"]}
    records, scored = [], []
    for block in reference_information["blocks"]:
        if block["role"] != role:
            continue
        record = {"id": block["id"], "quadrant": block["quadrant"], "xyxy": block["xyxy"],
                  "status": "UNAVAILABLE_INDIVIDUAL_INFORMATION", "valid_pixels": 0,
                  "eta_reference": None, "eta_moving": None, "score_matrix": None,
                  "discarded_for_error": False}
        records.append(record)
        if not block["qualified"] or not moving_blocks[block["id"]]["qualified"]:
            continue
        x0, y0, x1, y1 = block["xyxy"]
        mask = common[y0:y1, x0:x1]
        record["valid_pixels"] = int(mask.sum())
        if record["valid_pixels"] < config["minimum_valid_pixels_per_block"]:
            record["status"] = "UNAVAILABLE_COMMON_SUPPORT"
            continue
        a = _expanded_features(reference, block, role, config)
        b = _expanded_features(moving, block, role, config)
        ref = _sample(a["features"])
        scores = [v1._score(ref, _sample(b["features"], offset), mask, role) for offset in SAMPLING_OFFSETS]
        matrix = [[scores[INDEX[(-px-cx, -py-cy)]] for cx, cy in CORRECTIONS] for px, py in EXPERIMENTS]
        record.update(status="MEASURED", eta_reference=a["eta"], eta_moving=b["eta"], score_matrix=matrix)
        scored.append(matrix)
    available = [b for b in records if b["status"] == "MEASURED"]
    quadrants = sorted({tuple(b["quadrant"]) for b in available})
    supported = (len(available) >= config["minimum_blocks_per_role"]
                 and len(quadrants) >= config["minimum_quadrants_per_role"])
    means = np.asarray(scored).mean(axis=0).tolist() if scored else [[None] * len(CORRECTIONS) for _ in EXPERIMENTS]
    evaluations = [_recovery_record(p, scores, supported, config, v2_config) for p, scores in zip(EXPERIMENTS, means)]
    passed = sum(e["status"] == "PASS" for e in evaluations[1:])
    return {"status": "PASS" if supported and evaluations[0]["status"] == "PASS" and passed == 16 else "FAIL_RECOVERY",
            "descriptor": "SS8" if role == "selection" else "NGF", "role": role, "blocks": records,
            "available_blocks": len(available), "quadrants": [list(q) for q in quadrants],
            "common_valid_pixels": sum(b["valid_pixels"] for b in available),
            "identity_control": evaluations[0], "perturbations": evaluations[1:],
            "correct_recoveries": passed, "required_recoveries": 16, "recovery_fraction": passed / 16,
            "same_pixels_for_all_perturbations_and_corrections": True,
            "score_matrix_rows_perturbation_dxdy": [list(p) for p in EXPERIMENTS],
            "score_matrix_columns_correction_dxdy": [list(c) for c in CORRECTIONS],
            "error_based_rejections": 0}


def _relative_original(raw, role, temporal_information, config):
    """Reconsider raw V1 evidence without its uncalibrated absolute floors."""
    if raw is None:
        return {"status": "NON_IDENTIFIABLE", "unique_identity_maximum": False}
    prefix = "mind" if role == "selection" else "ngf"
    identity = raw["identity_score"]
    spatial = raw["spatial_controls"]
    eligible_temporal = [c for c in raw["temporal_controls"]
                         if temporal_information[c["moving_time"]]["classification"] == "IDENTIFIABLE"]
    supported = (raw["available_blocks"] >= config["minimum_blocks_per_role"]
                 and len(raw["quadrants"]) >= config["minimum_quadrants_per_role"])
    unique = identity is not None and len(spatial) == 48 and all(identity-c["score"] > config["peak_tie_tolerance"] for c in spatial)
    rank = None if identity is None else 1 + sum(c["score"] > identity + config["peak_tie_tolerance"] for c in spatial)
    relative = (unique and raw["spatial_margin"] >= config[f"{prefix}_spatial_margin"]
                and all(c["margin"] >= config[f"{prefix}_temporal_margin"] for c in eligible_temporal))
    geometry = True
    if role == "audit":
        measured = [b for b in raw["blocks"] if b["status"] == "MEASURED"]
        geometry = (v1.metrics_pass(raw, config)
                    and not any(b["peak_at_search_boundary"] or b["ambiguous_peak"] for b in measured))
    return {"status": "PASS" if supported and relative and geometry else "FAIL_RELATIVE_IDENTITY",
            "unique_identity_maximum": unique, "correct_rank": rank,
            "best_offset_dxdy": [0, 0] if unique else None,
            "eligible_temporal_controls": eligible_temporal,
            "nonidentifiable_temporal_controls_are_reported_not_gated": True,
            "historical_absolute_floor": config[f"{prefix}_minimum_identity_score"],
            "absolute_floor_used_as_gate": False, "coverage_pass": supported,
            "geometry_pass": geometry, "raw_v1": raw}


def evaluate_series(pairs, config, v2_config):
    """Three development times only, with the first an observability control."""
    validate_config(v2_config)
    if len(pairs) != 3:
        raise v1.SoluteRegistrationError("V2-D requires exactly three development times")
    original = v1.evaluate_series(pairs, config)
    temporal_information = [frame["moving_information"] for frame in original["per_frame"]]
    frames = []
    for index, ((reference, moving), raw) in enumerate(zip(pairs, original["per_frame"])):
        record = {"development_time": index, "classification": raw["classification"],
                  "reference_information": raw["reference_information"], "moving_information": raw["moving_information"],
                  "status": "NON_IDENTIFIABLE" if raw["classification"] == "NON_IDENTIFIABLE" else "BLOCKED_UNEXPECTED_INITIAL_IDENTIFIABILITY",
                  "original": None, "calibration": None, "metric_agreement": None}
        if index != 0:
            relative = {"SS8": _relative_original(raw["selection"], "selection", temporal_information, config),
                        "NGF": _relative_original(raw["audit"], "audit", temporal_information, config)}
            calibration = {"SS8": calibrate_role(reference, moving, raw["reference_information"], raw["moving_information"], "selection", config, v2_config),
                           "NGF": calibrate_role(reference, moving, raw["reference_information"], raw["moving_information"], "audit", config, v2_config)}
            agreement = (relative["SS8"].get("best_offset_dxdy") == relative["NGF"].get("best_offset_dxdy") == [0, 0]
                         and all(a["best_correction_dxdy"] == b["best_correction_dxdy"] == a["true_correction_dxdy"]
                                 for a, b in zip(calibration["SS8"]["perturbations"], calibration["NGF"]["perturbations"])))
            passed = (raw["classification"] == "IDENTIFIABLE" and agreement
                      and all(r["status"] == "PASS" for r in relative.values())
                      and all(r["status"] == "PASS" for r in calibration.values()))
            record.update(status="PASS" if passed else BLOCKED, original=relative, calibration=calibration, metric_agreement=agreement)
        frames.append(record)
    passed = frames[0]["classification"] == "NON_IDENTIFIABLE" and all(frame["status"] == "PASS" for frame in frames[1:])
    return {"status": PASS if passed else BLOCKED, "per_frame": frames,
            "temporal_controls": original["temporal_controls"], "original_residual_aggregate": original["aggregate"],
            "historical_v1_decision_from_unchanged_criteria": original["status"],
            "positive_development_times": [1, 2], "observability_control_time": 0,
            "mapping": None, "matrix": None, "inverse": None, "rectangle_roi": None,
            "holdout_evaluated": False, "units": "native_pixels", "physical_calibration": False,
            "experimental_unit": "acquisition_approximately_one_run_per_condition",
            "perturbations_or_tiles_are_physical_replicates": False, "p_values": None,
            "v1_scientific_files_modified": False, "absolute_floors_lowered": False}


def evaluate_development(pair_name, pairs, config, v2_config):
    validate_config(v2_config)
    if not v1._dimensions(pair_name, pairs, False):
        return {"status": "BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE", "per_frame": [], "matrix": None, "holdout_evaluated": False}
    result = evaluate_series(pairs, config, v2_config)
    indices = [0, 146, 293] if pair_name == "ESM2-to-ESM1" else [0, 197, 394]
    for frame, index in zip(result["per_frame"], indices):
        frame["source_index"] = index
    result["pair"] = pair_name
    return result
