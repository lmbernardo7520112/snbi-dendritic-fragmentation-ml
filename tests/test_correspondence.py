import unittest

from snbi_fragmentation.correspondence import EXPECTED_MODALITIES, audit_correspondence


def record(source_id, condition, modality, count=294, duration="58.800000"):
    return {"source_id": source_id, "condition": condition, "modality": modality,
            "frame_count": count, "playback_duration_seconds": duration,
            "reported_frame_rate": "5/1"}


class CorrespondenceTests(unittest.TestCase):
    def test_passes_two_complete_aligned_triplets(self):
        records = []
        for prefix, condition, count, duration in ((1, "bottom", 294, "58.800000"), (4, "top", 395, "79.000000")):
            for offset, modality in enumerate(sorted(EXPECTED_MODALITIES)):
                records.append(record(f"ESM{prefix + offset}", condition, modality, count, duration))
        report = audit_correspondence(records)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(all(x["frame_index_relation"] == "one_to_one_zero_based" for x in report["groups"]))

    def test_blocks_frame_count_mismatch(self):
        records = [
            record("ESM1", "bottom", "xray_radiography"),
            record("ESM2", "bottom", "relative_solute_field"),
            record("ESM3", "bottom", "cumulative_fragmentation_annotation", 293),
        ]
        self.assertEqual(audit_correspondence(records)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
