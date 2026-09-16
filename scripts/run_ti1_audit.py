"""Execute the authorized TI-1 read-only deterministic audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from snbi_fragmentation.correspondence import audit_correspondence
from snbi_fragmentation.custody import load_manifest, verify_sources
from snbi_fragmentation.metadata import ffprobe_version, metadata_as_dict, probe_zip_member
from snbi_fragmentation.timebase import load_time_rule


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("artifacts"))
    parser.add_argument("--manifest", type=Path, default=Path("configs/sources/source_manifest.json"))
    parser.add_argument("--time-rule", type=Path, default=Path("configs/time_rule.json"))
    parser.add_argument("--execution-date", default=date.today().isoformat())
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = load_manifest(args.manifest)
    custody = verify_sources(manifest, args.data_root)
    if custody["status"] != "PASS":
        raise SystemExit("G0 source verification failed; TI-1 aborted")
    containers = {x["container_id"]: x for x in manifest["containers"]}
    records, warnings = [], {}
    for source in manifest["sources"]:
        if source["source_kind"] != "video":
            continue
        storage = source["storage"]
        container = containers[storage["container_id"]]
        record, source_warnings = probe_zip_member(
            args.data_root / container["filename"], storage["member_path"], source
        )
        records.append(metadata_as_dict(record))
        warnings[source["source_id"]] = source_warnings
    records.sort(key=lambda x: x["source_id"])
    metadata_report = {
        "evidence_schema_version": "1.0.0",
        "operation": "read_only_streamed_video_metadata_probe",
        "execution_date": args.execution_date,
        "probe": {"tool": "ffprobe", "version": ffprobe_version(), "warnings": warnings},
        "records": records,
    }
    metadata_path = args.output_root / "metadata/acquisition_metadata.json"
    write_json(metadata_path, metadata_report)

    raw_rule, time_rule = load_time_rule(args.time_rule)
    time_records = []
    for record in records:
        fps = Decimal(record["reported_frame_rate_decimal"])
        time_records.append({
            "source_id": record["source_id"],
            "frame_count": record["frame_count"],
            "first_frame_physical_time_seconds": str(time_rule.physical_time(0)),
            "last_frame_physical_time_seconds": str(time_rule.last_frame_time(record["frame_count"])),
            "reported_fps": record["reported_frame_rate"],
            "playback_acceleration_factor": str(time_rule.playback_acceleration(fps)),
        })
    temporal = audit_correspondence(records)
    temporal["time_rule"] = raw_rule
    temporal["per_source_physical_time"] = time_records
    write_json(args.output_root / "evidence/G2_TEMP/temporal-correspondence-report.json", temporal)

    g1 = {
        "evidence_schema_version": "1.0.0", "gate_id": "G1", "status": "PASS",
        "mapping": [{"source_id": x["source_id"], "condition": x["condition"], "modality": x["modality"]} for x in records],
        "claim_limit": "Relative-solute videos are not interpreted as absolute Bi concentration; annotation circles are not fragment masks.",
    }
    write_json(args.output_root / "evidence/G1/modalities-report.json", g1)
    for path in [metadata_path, args.output_root / "evidence/G1/modalities-report.json", args.output_root / "evidence/G2_TEMP/temporal-correspondence-report.json"]:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksum = path.parent / "checksums.sha256"
        checksum.write_text(f"{digest}  {path.name}\n", encoding="utf-8")
    return 0 if temporal["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
