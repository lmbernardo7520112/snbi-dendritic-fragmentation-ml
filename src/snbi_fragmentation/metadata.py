"""Read-only video metadata probing without frame extraction."""

from __future__ import annotations

import json
import re
import subprocess
import zipfile
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path

from .ti2_authority import require_scientific_authority


class MetadataError(RuntimeError):
    """Raised when a source cannot be probed deterministically."""


@dataclass(frozen=True)
class VideoMetadata:
    source_id: str
    condition: str
    modality: str
    codec_name: str
    width: int
    height: int
    reported_frame_rate: str
    reported_frame_rate_decimal: str
    time_base: str
    start_time_seconds: str
    playback_duration_seconds: str
    frame_count: int
    probe_input_mode: str = "zip_member_stream_read_only"


FFPROBE_ENTRIES = (
    "stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,"
    "time_base,start_time,duration,nb_frames:format=format_name,duration"
)


def parse_rate(value: str) -> Decimal:
    try:
        numerator, denominator = value.split("/", 1)
        result = Decimal(numerator) / Decimal(denominator)
    except (ValueError, ArithmeticError) as exc:
        raise MetadataError(f"invalid frame rate: {value}") from exc
    if result <= 0:
        raise MetadataError("frame rate must be positive")
    return result


def parse_ffprobe(source: dict, payload: dict) -> VideoMetadata:
    streams = [x for x in payload.get("streams", []) if x.get("codec_type") == "video"]
    if len(streams) != 1:
        raise MetadataError(f"{source['source_id']} must contain exactly one video stream")
    stream = streams[0]
    rate = stream.get("avg_frame_rate") or stream["r_frame_rate"]
    try:
        frame_count = int(stream["nb_frames"])
        width = int(stream["width"])
        height = int(stream["height"])
        duration = str(stream.get("duration") or payload["format"]["duration"])
        metadata = VideoMetadata(
            source_id=source["source_id"], condition=source["condition"],
            modality=source["modality"], codec_name=stream["codec_name"],
            width=width, height=height, reported_frame_rate=rate,
            reported_frame_rate_decimal=format(parse_rate(rate), "f"),
            time_base=stream["time_base"],
            start_time_seconds=str(stream["start_time"]),
            playback_duration_seconds=duration, frame_count=frame_count,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise MetadataError(f"incomplete metadata for {source.get('source_id')}: {exc}") from exc
    if min(metadata.width, metadata.height, metadata.frame_count) <= 0:
        raise MetadataError("dimensions and frame_count must be positive")
    return metadata


def ffprobe_version(executable: str = "ffprobe") -> str:
    require_scientific_authority()
    completed = subprocess.run(
        [executable, "-version"], check=True, capture_output=True, text=True
    )
    return completed.stdout.splitlines()[0]


def probe_zip_member(
    archive_path: Path, member_path: str, source: dict, executable: str = "ffprobe"
) -> tuple[VideoMetadata, list[str]]:
    require_scientific_authority()
    command = [
        executable, "-v", "warning", "-show_entries", FFPROBE_ENTRIES,
        "-of", "json", "pipe:0",
    ]
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert process.stdin is not None
    try:
        with zipfile.ZipFile(archive_path) as archive, archive.open(member_path) as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                process.stdin.write(block)
        process.stdin.close()
        assert process.stdout is not None and process.stderr is not None
        stdout = process.stdout.read()
        stderr = process.stderr.read().decode("utf-8", errors="replace")
        return_code = process.wait()
    except Exception:
        process.kill()
        process.wait()
        raise
    if return_code != 0:
        raise MetadataError(f"ffprobe failed for {source['source_id']}: {stderr.strip()}")
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise MetadataError(f"invalid ffprobe JSON for {source['source_id']}") from exc
    warnings = [
        re.sub(r"@ 0x[0-9a-fA-F]+", "@ <runtime-address>", line)
        for line in stderr.splitlines() if line.strip()
    ]
    return parse_ffprobe(source, payload), warnings


def metadata_as_dict(value: VideoMetadata) -> dict:
    return asdict(value)
