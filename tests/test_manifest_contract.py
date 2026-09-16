from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from snbi_fragmentation.custody import ManifestError, validate_manifest


ROOT = Path(__file__).resolve().parents[1]


class ManifestContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(
            (ROOT / "configs/sources/source_manifest.json").read_text(encoding="utf-8")
        )

    def test_canonical_manifest_is_valid(self) -> None:
        validate_manifest(self.manifest)

    def test_duplicate_source_id_is_rejected(self) -> None:
        broken = copy.deepcopy(self.manifest)
        broken["sources"][1]["source_id"] = "ESM1"
        with self.assertRaisesRegex(ManifestError, "duplicate source_id"):
            validate_manifest(broken)

    def test_missing_esm_is_rejected(self) -> None:
        broken = copy.deepcopy(self.manifest)
        broken["sources"] = [x for x in broken["sources"] if x["source_id"] != "ESM6"]
        with self.assertRaisesRegex(ManifestError, "expected ESM1-ESM6"):
            validate_manifest(broken)

    def test_unknown_modality_is_rejected(self) -> None:
        broken = copy.deepcopy(self.manifest)
        broken["sources"][0]["modality"] = "absolute_bismuth_concentration"
        with self.assertRaisesRegex(ManifestError, "invalid enum"):
            validate_manifest(broken)

    def test_path_traversal_is_rejected(self) -> None:
        broken = copy.deepcopy(self.manifest)
        broken["sources"][0]["storage"]["member_path"] = "../secret.mp4"
        with self.assertRaisesRegex(ManifestError, "safe relative path"):
            validate_manifest(broken)


if __name__ == "__main__":
    unittest.main()

