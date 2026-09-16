import unittest

from snbi_fragmentation.metadata import MetadataError, parse_ffprobe


SOURCE = {"source_id": "ESM1", "condition": "bottom_up_anti_parallel", "modality": "xray_radiography"}
PAYLOAD = {
    "streams": [{"codec_type": "video", "codec_name": "h264", "width": 1278, "height": 1018,
                 "r_frame_rate": "5/1", "avg_frame_rate": "5/1", "time_base": "1/90000",
                 "start_time": "0.400000", "duration": "58.800000", "nb_frames": "294"}],
    "format": {"duration": "58.800000"},
}


class MetadataParserTests(unittest.TestCase):
    def test_parses_deterministic_fields(self):
        result = parse_ffprobe(SOURCE, PAYLOAD)
        self.assertEqual((result.width, result.height, result.frame_count), (1278, 1018, 294))
        self.assertEqual(result.reported_frame_rate_decimal, "5")
        self.assertEqual(result.probe_input_mode, "zip_member_stream_read_only")

    def test_requires_exactly_one_video_stream(self):
        with self.assertRaises(MetadataError):
            parse_ffprobe(SOURCE, {"streams": [], "format": {}})


if __name__ == "__main__":
    unittest.main()
