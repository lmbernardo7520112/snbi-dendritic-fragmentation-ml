"""One finite graphical extraction on the ten exposed TI3-A0 DEV assets."""
import hashlib
import json
import os

from inspect_ti3_a0_annotations import (
    ALLOWLIST, EVIDENCE, now, planes, preflight, read_asset,
    read_relative, text_json, write_json,
)
from snbi_fragmentation.ti3_a0_annotations import (
    VALID, extract_graphical_markers, match_persistence, validate_config,
)


def main():
    method = text_json("artifacts/evidence/TI3_A0/extraction-method.json")
    validate_config(method["config"])
    for path, expected in method["frozen_code_sha256"].items():
        with os.fdopen(read_relative(path), "rb") as stream:
            if hashlib.sha256(stream.read()).hexdigest() != expected:
                raise ValueError("extraction code freeze divergence")
    prior = text_json("artifacts/evidence/TI3_A0/characterization-io.json")
    if prior["status"] != "COMPLETED" or prior["open_count"] != 10:
        raise ValueError("completed bounded characterization required")
    assets, audit = preflight("extraction")
    frames = []
    for row in assets:
        raw = read_asset(row, audit)
        _, u, v = planes(raw, row["width"], row["height"])
        extracted = extract_graphical_markers(u, v, row["width"], row["height"], method["config"])
        for c in extracted["components"]:
            valid = c["classification"] == VALID
            c.update({
                "annotation_id": f"{row['asset_id']}:graphic-component-{c['component_id']:04d}",
                "source_id": row["source_id"], "frame_index": row["frame_index"],
                "experimental_time_s": row["experimental_time_s"],
                "center_x": c["center_xy_px"][0] if valid else None,
                "center_y": c["center_xy_px"][1] if valid else None,
                "radius_or_extent_descriptor": {"radius_px":c["radius_graphical_px"], "scope":"GRAPHICAL_COMPONENT_ONLY_NOT_FRAGMENT_SIZE"},
                "provenance": {"native_path":row["path"], "native_sha256":row["image_sha256"], "development_only":True},
                "confidence": "NOT_A_PROBABILITY_OR_PHYSICAL_CERTIFICATION",
                "status": c["classification"], "physical_event_id": None,
            })
        frames.append(dict(extracted, asset_id=row["asset_id"], source_id=row["source_id"],
                           frame_index=row["frame_index"], experimental_time_s=row["experimental_time_s"]))
    temporal = {s: match_persistence([r for r in frames if r["source_id"] == s], method["persistence_tolerance_px"])
                for s in ALLOWLIST}
    audit["status"] = "COMPLETED"
    audit["finished_at_utc"] = now()
    write_json("extraction-io.json", audit)
    write_json("extraction-results.json", {"method":method, "frames":frames,
               "ml_runs":0, "negative_labels_created":0, "physical_events_inferred":0,
               "candidate_scope":"Graphical component records, not a certified ML dataset."}, exclusive=True)
    write_json("temporal-results.json", temporal, exclusive=True)
    write_json("io-audit.json", {"scope":"native buffer I/O for two declared DEV-only passes",
               "phases":[prior,audit], "unique_native_files":10,
               "native_open_attempts":prior["open_attempts"]+audit["open_attempts"],
               "native_open_count":prior["open_count"]+audit["open_count"],
               "native_bytes_read":prior["content_bytes_read"]+audit["content_bytes_read"],
               "new_frames_opened":0, "final_test_opened":False,
               "visual_derivatives":"Recorded separately; no new experimental frame content.",
               "ml_runs":0}, exclusive=True)
    print(json.dumps({"status":"COMPLETED", "frames":[{k:r[k] for k in ("asset_id","component_count","valid_circle_count","ambiguous_component_count","small_component_count")} for r in frames],
                      "persistence":{s:r["cumulative_status"] for s,r in temporal.items()},
                      "native_bytes_this_pass":audit["content_bytes_read"]}, indent=2))


if __name__ == "__main__":
    main()
