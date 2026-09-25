import json
from pathlib import Path
import tempfile
import unittest

from semantic_cleanup.pipeline_v2 import collect, metadata, prepare
from semantic_cleanup.raw_snapshot import create_snapshot, encode


class PipelineV2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / "source.jsonl"
        rows = [
            {"word": "release", "translation": "n. 释放；发布", "phonetic": "ri'li:s",
             "bnc": "1120", "frq": "1232", "tag": "cet4 cet6", "exchange": "p:released/i:releasing"},
            {"word": "bank", "translation": "银行；河岸", "oxford": "1"},
            {"word": "release", "translation": "vt. 释放；发行", "bnc": "1121"},
        ]
        source.write_text("\n".join(encode(r) for r in rows) + "\n", encoding="utf-8")
        self.snapshot = self.root / "snapshot"
        create_snapshot(source, self.snapshot, source_format="jsonl", version="local-test")
        self.bundle = self.root / "requests"
        prepare(self.snapshot, self.bundle, limit=2)
        self.requests = [json.loads(line) for line in (self.bundle / "requests.jsonl").read_text().splitlines()]

    def response(self, index=0):
        request = self.requests[index]
        example = Path(__file__).resolve().parents[1] / "semantic_cleanup" / "examples-v2" / (request["locked_fields"]["word"] + ".json")
        entry = json.loads(example.read_text())
        for sense in entry["senses"]:
            sense["source_entry_ids"] = [r["entry_id"] for r in request["raw_records"]]
        return {"custom_id": request["custom_id"], "output": {"senses": entry["senses"]}}

    def collect_lines(self, lines):
        source = self.root / "responses.jsonl"
        source.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return collect(self.snapshot, self.bundle, source, self.root / "results",
                       generator="offline-fixture-not-model-call", generator_version="1")

    def test_end_to_end_candidates_remain_unapproved_and_metadata_is_locked(self):
        result = self.collect_lines([encode(self.response(0)), encode(self.response(1))])
        self.assertEqual(result["needs_review"], 2)
        self.assertEqual(result["rejected"], 0)
        self.assertEqual(result["missing_responses"], [])
        self.assertEqual(result["production_eligible"], 0)
        row = json.loads((self.root / "results" / "review.jsonl").read_text().splitlines()[0])
        self.assertEqual(row["candidate"]["frequency"]["frq"], 1232)
        self.assertIsNone(row["candidate"]["frequency"]["coca"])
        self.assertTrue(row["assessment"]["raw_source_verified"])
        self.assertIn("duplicate_record_metadata_conflict_first_record_retained", row["assessment"]["review_reasons"])

    def test_nonadjacent_duplicate_words_grouped_in_one_request(self):
        self.assertEqual(len(self.requests), 2)
        self.assertEqual(len(self.requests[0]["raw_records"]), 2)
        self.assertNotEqual(self.requests[0]["custom_id"], self.requests[1]["custom_id"])

    def test_deterministic_request_ids(self):
        target = self.root / "second"
        prepare(self.snapshot, target, limit=2)
        self.assertEqual((self.bundle / "requests.jsonl").read_bytes(), (target / "requests.jsonl").read_bytes())

    def test_bad_line_does_not_drop_later_valid_response(self):
        result = self.collect_lines(["not json", encode(self.response())])
        self.assertEqual(result["rejected"], 1)
        self.assertEqual(result["needs_review"], 1)
        self.assertEqual(len(result["missing_responses"]), 1)

    def test_duplicate_and_unknown_response_ids_rejected(self):
        valid = self.response()
        unknown = self.response(1)
        unknown["custom_id"] = "unknown"
        result = self.collect_lines([encode(valid), encode(valid), encode(unknown)])
        self.assertEqual(result["rejected"], 2)
        self.assertEqual(result["needs_review"], 1)

    def test_model_cannot_supply_frequency_or_provenance(self):
        row = self.response()
        row["output"]["frequency"] = {"bnc": 1}
        result = self.collect_lines([encode(row)])
        self.assertEqual(result["rejected"], 1)
        self.assertEqual(result["needs_review"], 0)

    def test_wrong_sense_source_rejected(self):
        row = self.response()
        row["output"]["senses"][0]["source_entry_ids"] = ["f" * 64 + ":99"]
        self.assertEqual(self.collect_lines([encode(row)])["rejected"], 1)

    def test_tampered_request_bundle_rejected_before_outputs(self):
        with (self.bundle / "requests.jsonl").open("a") as stream:
            stream.write(" ")
        with self.assertRaises(ValueError):
            self.collect_lines([encode(self.response())])
        self.assertFalse((self.root / "results").exists())

    def test_limit_missing_words_and_existing_output(self):
        with self.assertRaises(ValueError):
            prepare(self.snapshot, self.root / "bad", limit=5001)
        with self.assertRaises(ValueError):
            prepare(self.snapshot, self.root / "missing", words=["absent"])
        with self.assertRaises(FileExistsError):
            prepare(self.snapshot, self.bundle, limit=2)

    def test_safe_metadata_conversion_and_no_region_inference(self):
        fixed, notes = metadata({"word": "x", "tags": "中高 cet4", "exchange": "时态: foo, bar",
                                "phonetic": "gə'rɑ:ʒ; 'gærɑ:ʒ", "bnc": "0", "frq": "50"})
        self.assertEqual(fixed["exam_tags"], ["中考", "高考", "CET4"])
        self.assertEqual(fixed["morphology"], [])
        self.assertIn("exchange_requires_review", notes)
        self.assertIsNone(fixed["frequency"]["bnc"])
        self.assertIsNone(fixed["frequency"]["coca"])
        self.assertEqual([p["region"] for p in fixed["pronunciation"]], ["unspecified", "unspecified"])
        self.assertEqual(fixed["pronunciation"][0]["ipa"], "/gəˈrɑːʒ/")


if __name__ == "__main__":
    unittest.main()
