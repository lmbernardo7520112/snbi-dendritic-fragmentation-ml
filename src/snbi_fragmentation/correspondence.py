"""Deterministic inter-modality correspondence checks for TI-1."""

from __future__ import annotations

from collections import defaultdict

EXPECTED_MODALITIES = {
    "xray_radiography",
    "relative_solute_field",
    "cumulative_fragmentation_annotation",
}


def audit_correspondence(records: list[dict]) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        groups[record["condition"]].append(record)
    results = []
    for condition, items in sorted(groups.items()):
        modalities = {x["modality"] for x in items}
        counts = {int(x["frame_count"]) for x in items}
        durations = {x["playback_duration_seconds"] for x in items}
        rates = {x["reported_frame_rate"] for x in items}
        complete = modalities == EXPECTED_MODALITIES and len(items) == 3
        aligned = complete and len(counts) == len(durations) == len(rates) == 1
        results.append({
            "condition": condition,
            "source_ids": sorted(x["source_id"] for x in items),
            "modalities": sorted(modalities),
            "frame_counts": sorted(counts),
            "playback_durations_seconds": sorted(durations),
            "reported_frame_rates": sorted(rates),
            "frame_index_relation": "one_to_one_zero_based" if aligned else "not_established",
            "status": "PASS" if aligned else "BLOCKED",
        })
    all_pass = len(results) == 2 and all(x["status"] == "PASS" for x in results)
    return {
        "evidence_schema_version": "1.0.0",
        "gate_id": "G2-TEMP",
        "operation": "metadata_level_inter_modality_correspondence",
        "status": "PASS" if all_pass else "BLOCKED",
        "groups": results,
        "scope_limit": (
            "Establishes index-level temporal correspondence only; it does not establish "
            "pixel registration, content equivalence, or annotation geometry."
        ),
    }
