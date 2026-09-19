"""Operational holdout adapter to the unchanged V2 C1 scientific functions.

No I/O, development data, authority activation, parameter changes or retry is
implemented here. The caller authenticates the eight reserved native buffers
and accounts for all I/O before passing two prepared pairs at a time.

V1 supplies raw evidence for two reciprocal temporal controls. Its historical
absolute-floor decision is retained but does not decide this gate. Every
reserved case receives exactly the per-positive V2 conjunction. Unlike the
development entry point, no reserved case is an initial-time exemption.
"""

from snbi_fragmentation import ti2r_solute_direct_registration as v1
from snbi_fragmentation import ti2r_solute_v2_calibration as v2


RESERVED_INDICES = {"ESM2-to-ESM1": (73, 219), "ESM5-to-ESM4": (98, 295)}


def evaluate_holdout_pair(pair_name, pairs, config, v2_config):
    """Apply the frozen V2 decision separately to both reserved pair-instants.

This adapter intentionally does not call the V2 development-only wrapper,
whose three-time shape and initial observability control are inapplicable to
the two previously reserved times. It calls its unchanged scientific functions
and preserves all raw results, including unfavorable and unidentifiable cases.
"""
    v2.validate_config(v2_config)
    if not v1._dimensions(pair_name, pairs, True):
        raise v1.SoluteRegistrationError("reserved native dimensions diverge")

    original = v1.evaluate_series(pairs, config, holdout=True)
    temporal_information = [frame["moving_information"] for frame in original["per_frame"]]
    frames = []
    for time, ((reference, moving), raw) in enumerate(zip(pairs, original["per_frame"])):
        relative = {
            "SS8": v2._relative_original(raw["selection"], "selection", temporal_information, config),
            "NGF": v2._relative_original(raw["audit"], "audit", temporal_information, config),
        }
        calibration = {
            "SS8": v2.calibrate_role(reference, moving, raw["reference_information"],
                                     raw["moving_information"], "selection", config, v2_config),
            "NGF": v2.calibrate_role(reference, moving, raw["reference_information"],
                                     raw["moving_information"], "audit", config, v2_config),
        }
        # This expression and the following conjunction are the unchanged V2
        # per-positive decision, applied to each of the two reserved cases.
        agreement = (
            relative["SS8"].get("best_offset_dxdy")
            == relative["NGF"].get("best_offset_dxdy") == [0, 0]
            and all(
                a["best_correction_dxdy"] == b["best_correction_dxdy"] == a["true_correction_dxdy"]
                for a, b in zip(calibration["SS8"]["perturbations"], calibration["NGF"]["perturbations"])
            )
        )
        criteria = {
            "both_images_individually_identifiable": raw["classification"] == "IDENTIFIABLE",
            "SS8_original_relative_gate": relative["SS8"]["status"] == "PASS",
            "NGF_original_relative_and_residual_gate": relative["NGF"]["status"] == "PASS",
            "SS8_identity_and_all_16_recoveries_gate": calibration["SS8"]["status"] == "PASS",
            "NGF_identity_and_all_16_recoveries_gate": calibration["NGF"]["status"] == "PASS",
            "metric_agreement": agreement,
        }
        frames.append({
            "holdout_time": time,
            "source_index": RESERVED_INDICES[pair_name][time],
            "classification": raw["classification"],
            "reference_information": raw["reference_information"],
            "moving_information": raw["moving_information"],
            "status": "PASS" if all(criteria.values()) else "FAIL",
            "original": relative,
            "calibration": calibration,
            "metric_agreement": agreement,
            "criteria": criteria,
            "failed_criteria": [name for name, passed in criteria.items() if not passed],
            "raw_v1_frame": raw,
            "exempt_from_gate": False,
        })

    return {
        "pair": pair_name,
        "source_indices": list(RESERVED_INDICES[pair_name]),
        "status": "PASS" if all(frame["status"] == "PASS" for frame in frames) else "FAIL",
        "per_frame": frames,
        "temporal_controls": original["temporal_controls"],
        "original_residual_aggregate": original["aggregate"],
        "historical_v1_decision_from_unchanged_criteria": original["status"],
        "historical_v1_underlying_status": original["underlying_status"],
        "historical_v1_decision_used_as_gate": False,
        "minimum_one_identifiable_holdout_tolerance_used": False,
        "all_reserved_cases_required": True,
        "holdout_evaluated": True,
        "development_buffers_used": False,
        "frozen_identity_offset": [0, 0],
        "mapping_updated": False,
        "mapping": None,
        "matrix": None,
        "inverse": None,
        "rectangle_roi": None,
        "units": "native_pixels",
        "physical_calibration": False,
        "validation_kind": "internal_temporal_same_acquisition",
        "experimental_unit": "acquisition_approximately_one_run_per_condition",
        "perturbations_or_tiles_are_physical_replicates": False,
        "p_values": None,
        "scientific_functions_modified": False,
        "absolute_floors_lowered": False,
    }
