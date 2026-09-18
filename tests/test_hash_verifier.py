from __future__ import annotations

import hashlib
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from pathlib import Path

from snbi_fragmentation.custody import verify_sources


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fixture_manifest(
    file_bytes: bytes,
    member_bytes: bytes,
    container_sha256: str,
    container_size_bytes: int,
) -> dict:
    esm_sources = []
    for index in range(1, 7):
        content = member_bytes if index == 1 else f"esm-{index}".encode()
        esm_sources.append(
            {
                "source_id": f"ESM{index}",
                "source_kind": "video",
                "modality": "xray_radiography",
                "condition": "bottom_up_anti_parallel",
                "sha256": digest(content),
                "size_bytes": len(content),
                "hash_scope": "uncompressed_zip_member_bytes",
                "storage": {
                    "kind": "zip_member",
                    "container_id": "Z",
                    "member_path": f"ESM{index}.mp4",
                },
                "redistribution": "external_not_redistributed",
            }
        )
    return {
        "manifest_version": "1.0.0",
        "project_id": "TEST",
        "containers": [
            {
                "container_id": "Z",
                "filename": "sources.zip",
                "sha256": container_sha256,
                "size_bytes": container_size_bytes,
            }
        ],
        "sources": esm_sources
        + [
            {
                "source_id": "DOC",
                "source_kind": "document",
                "modality": "scientific_document",
                "condition": "not_applicable",
                "sha256": digest(file_bytes),
                "size_bytes": len(file_bytes),
                "hash_scope": "raw_file_bytes",
                "storage": {"kind": "file", "filename": "paper.pdf"},
                "redistribution": "external_not_redistributed",
            }
        ],
    }


class HashVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        # Only this entirely synthetic legacy fixture bypasses the closed guard.
        guard = patch('snbi_fragmentation.custody.require_scientific_authority')
        self.guard = guard.start()
        self.addCleanup(guard.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.file_bytes = b"documentary-source"
        self.member_bytes = b"video-source"
        (self.root / "paper.pdf").write_bytes(self.file_bytes)
        with zipfile.ZipFile(self.root / "sources.zip", "w") as archive:
            for index in range(1, 7):
                data = self.member_bytes if index == 1 else f"esm-{index}".encode()
                archive.writestr(f"ESM{index}.mp4", data)
        archive_bytes = (self.root / "sources.zip").read_bytes()
        self.manifest = fixture_manifest(
            self.file_bytes,
            self.member_bytes,
            digest(archive_bytes),
            len(archive_bytes),
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_known_bytes_pass(self) -> None:
        report = verify_sources(self.manifest, self.root)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["pass_count"], 8)

    def test_one_byte_change_fails_closed(self) -> None:
        (self.root / "paper.pdf").write_bytes(self.file_bytes + b"!")
        report = verify_sources(self.manifest, self.root)
        self.assertEqual(report["status"], "BLOCKED")
        failed = [x for x in report["results"] if x["source_id"] == "DOC"]
        self.assertEqual(failed[0]["status"], "FAIL")

    def test_missing_source_fails_closed(self) -> None:
        (self.root / "paper.pdf").unlink()
        report = verify_sources(self.manifest, self.root)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["fail_count"], 1)

    def test_container_change_fails_closed(self) -> None:
        with (self.root / "sources.zip").open("ab") as stream:
            stream.write(b"!")
        report = verify_sources(self.manifest, self.root)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["container_results"][0]["status"], "FAIL")

    def test_verification_does_not_change_source_bytes(self) -> None:
        before = digest((self.root / "paper.pdf").read_bytes())
        verify_sources(self.manifest, self.root)
        after = digest((self.root / "paper.pdf").read_bytes())
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
