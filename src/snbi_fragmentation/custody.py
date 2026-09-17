"""Read-only source-manifest validation and SHA-256 verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterable

from .domain import Condition, EXPECTED_ESM_IDS, Modality, SourceKind, StorageKind
from .ti2_authority import require_scientific_authority

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    """Raised when the source manifest violates a TI-0 contract."""


@dataclass(frozen=True)
class VerificationResult:
    source_id: str
    status: str
    expected_sha256: str
    observed_sha256: str | None
    expected_size_bytes: int
    observed_size_bytes: int | None
    hash_scope: str
    error: str | None = None


def _hash_stream(stream: BinaryIO) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def _safe_relative(value: str, field: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ManifestError(f"{field} must be a safe relative path")
    return value


def load_manifest(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read manifest: {exc}") from exc
    validate_manifest(data)
    return data


def validate_manifest(data: dict) -> None:
    required_top = {"manifest_version", "project_id", "containers", "sources"}
    missing_top = required_top - data.keys()
    if missing_top:
        raise ManifestError(f"missing top-level fields: {sorted(missing_top)}")
    if data["manifest_version"] != "1.0.0":
        raise ManifestError("unsupported manifest_version")
    if not isinstance(data["sources"], list) or not data["sources"]:
        raise ManifestError("sources must be a non-empty list")

    containers = {}
    for item in data["containers"]:
        required = {"container_id", "filename", "sha256", "size_bytes"}
        if required - item.keys():
            raise ManifestError("container is missing required fields")
        if item["container_id"] in containers:
            raise ManifestError(f"duplicate container_id: {item['container_id']}")
        _safe_relative(item["filename"], "container filename")
        if not SHA256_RE.fullmatch(item["sha256"]):
            raise ManifestError("container sha256 must be lowercase hexadecimal")
        if not isinstance(item["size_bytes"], int) or item["size_bytes"] < 0:
            raise ManifestError("container size_bytes must be non-negative")
        containers[item["container_id"]] = item

    source_ids: set[str] = set()
    esm_ids: set[str] = set()
    for item in data["sources"]:
        required = {
            "source_id", "source_kind", "modality", "condition", "sha256",
            "size_bytes", "hash_scope", "storage", "redistribution",
        }
        missing = required - item.keys()
        if missing:
            raise ManifestError(
                f"source {item.get('source_id', '<unknown>')} missing {sorted(missing)}"
            )
        source_id = item["source_id"]
        if source_id in source_ids:
            raise ManifestError(f"duplicate source_id: {source_id}")
        source_ids.add(source_id)
        if source_id.startswith("ESM"):
            esm_ids.add(source_id)
        try:
            SourceKind(item["source_kind"])
            Modality(item["modality"])
            Condition(item["condition"])
            storage_kind = StorageKind(item["storage"]["kind"])
        except (ValueError, KeyError, TypeError) as exc:
            raise ManifestError(f"invalid enum in source {source_id}") from exc
        if not SHA256_RE.fullmatch(item["sha256"]):
            raise ManifestError(f"invalid sha256 for {source_id}")
        if not isinstance(item["size_bytes"], int) or item["size_bytes"] < 0:
            raise ManifestError(f"invalid size_bytes for {source_id}")
        storage = item["storage"]
        if storage_kind is StorageKind.FILE:
            _safe_relative(storage.get("filename", ""), "source filename")
            if item["hash_scope"] != "raw_file_bytes":
                raise ManifestError(f"file hash_scope mismatch for {source_id}")
        else:
            container_id = storage.get("container_id")
            if container_id not in containers:
                raise ManifestError(f"unknown container for {source_id}")
            _safe_relative(storage.get("member_path", ""), "archive member_path")
            if item["hash_scope"] != "uncompressed_zip_member_bytes":
                raise ManifestError(f"zip hash_scope mismatch for {source_id}")

    if esm_ids != EXPECTED_ESM_IDS:
        raise ManifestError(
            f"expected ESM1-ESM6 exactly; observed {sorted(esm_ids)}"
        )


def _verify_one(source: dict, containers: dict[str, dict], data_root: Path) -> VerificationResult:
    observed_hash: str | None = None
    observed_size: int | None = None
    try:
        storage = source["storage"]
        if storage["kind"] == StorageKind.FILE:
            path = data_root / storage["filename"]
            with path.open("rb") as stream:
                observed_hash, observed_size = _hash_stream(stream)
        else:
            container = containers[storage["container_id"]]
            archive_path = data_root / container["filename"]
            with zipfile.ZipFile(archive_path) as archive:
                with archive.open(storage["member_path"], "r") as stream:
                    observed_hash, observed_size = _hash_stream(stream)
        matches = (
            observed_hash == source["sha256"]
            and observed_size == source["size_bytes"]
        )
        return VerificationResult(
            source_id=source["source_id"],
            status="PASS" if matches else "FAIL",
            expected_sha256=source["sha256"],
            observed_sha256=observed_hash,
            expected_size_bytes=source["size_bytes"],
            observed_size_bytes=observed_size,
            hash_scope=source["hash_scope"],
            error=None if matches else "digest or byte-size mismatch",
        )
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        return VerificationResult(
            source_id=source["source_id"],
            status="FAIL",
            expected_sha256=source["sha256"],
            observed_sha256=observed_hash,
            expected_size_bytes=source["size_bytes"],
            observed_size_bytes=observed_size,
            hash_scope=source["hash_scope"],
            error=f"{type(exc).__name__}: {exc}",
        )


def _verify_container(container: dict, data_root: Path) -> VerificationResult:
    observed_hash: str | None = None
    observed_size: int | None = None
    try:
        with (data_root / container["filename"]).open("rb") as stream:
            observed_hash, observed_size = _hash_stream(stream)
        matches = (
            observed_hash == container["sha256"]
            and observed_size == container["size_bytes"]
        )
        return VerificationResult(
            source_id=container["container_id"],
            status="PASS" if matches else "FAIL",
            expected_sha256=container["sha256"],
            observed_sha256=observed_hash,
            expected_size_bytes=container["size_bytes"],
            observed_size_bytes=observed_size,
            hash_scope="raw_container_bytes",
            error=None if matches else "digest or byte-size mismatch",
        )
    except OSError as exc:
        return VerificationResult(
            source_id=container["container_id"],
            status="FAIL",
            expected_sha256=container["sha256"],
            observed_sha256=observed_hash,
            expected_size_bytes=container["size_bytes"],
            observed_size_bytes=observed_size,
            hash_scope="raw_container_bytes",
            error=f"{type(exc).__name__}: {exc}",
        )


def verify_sources(manifest: dict, data_root: Path) -> dict:
    require_scientific_authority()
    validate_manifest(manifest)
    containers = {x["container_id"]: x for x in manifest["containers"]}
    container_results = [
        _verify_container(container, data_root) for container in containers.values()
    ]
    results = [_verify_one(source, containers, data_root) for source in manifest["sources"]]
    all_results = container_results + results
    return {
        "evidence_schema_version": "1.0.0",
        "gate_id": "G0",
        "operation": "read_only_sha256_verification",
        "container_count": len(container_results),
        "source_count": len(results),
        "pass_count": sum(x.status == "PASS" for x in all_results),
        "fail_count": sum(x.status == "FAIL" for x in all_results),
        "status": "PASS" if all(x.status == "PASS" for x in all_results) else "BLOCKED",
        "container_results": [asdict(x) for x in container_results],
        "results": [asdict(x) for x in results],
    }


def _write_json(payload: dict, destination: Path | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if destination is None:
        sys.stdout.write(rendered)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate manifest contracts")
    validate.add_argument("manifest", type=Path)
    verify = subparsers.add_parser("verify", help="verify source bytes read-only")
    verify.add_argument("manifest", type=Path)
    verify.add_argument("--data-root", type=Path, required=True)
    verify.add_argument("--report", type=Path)
    return parser


def _main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        if args.command == "validate":
            _write_json({"status": "PASS", "gate_id": "G0", "source_count": len(manifest["sources"])}, None)
            return 0
        report = verify_sources(manifest, args.data_root)
        _write_json(report, args.report)
        return 0 if report["status"] == "PASS" else 1
    except ManifestError as exc:
        sys.stderr.write(f"manifest error: {exc}\n")
        return 2


def verify_main(argv: Iterable[str] | None = None) -> int:
    """Deny scientific verification before parsing a supplied path."""
    require_scientific_authority()
    return _main(argv)


def main(argv: Iterable[str] | None = None) -> int:
    """Route textual validation separately; never parse verification paths here."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and type(arguments[0]) is str and arguments[0] == "validate":
        return _main(arguments)
    return verify_main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
