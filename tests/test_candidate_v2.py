import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator

from semantic_cleanup.candidate_v2 import SCHEMA, assess_candidate, validate_candidate
from semantic_cleanup.raw_snapshot import create_snapshot, verify_snapshot
from semantic_cleanup.schema import SemanticValidationError
from semantic_cleanup.store import SemanticStore


EXAMPLES = Path(__file__).resolve().parents[1] / "semantic_cleanup" / "examples-v2"


def sample(word="release"):
    return json.loads((EXAMPLES / f"{word}.json").read_text(encoding="utf-8"))


class CandidateV2Tests(unittest.TestCase):
    def test_schema_and_examples_are_valid_and_not_production_approved(self):
        Draft202012Validator.check_schema(SCHEMA)
        for word in ("release", "bank", "break"):
            with self.subTest(word=word):
                entry = sample(word)
                self.assertEqual(validate_candidate(entry), entry)
                report = assess_candidate(entry)
                self.assertFalse(report["production_eligible"])
                self.assertIn("design_example_not_production_data", report["review_reasons"])

    def test_confidence_is_required_finite_numeric_and_bounded(self):
        for value in (None, True, "0.9", -0.1, 1.1, float("nan"), float("inf")):
            with self.subTest(value=value):
                entry = sample()
                entry["senses"][0]["confidence"] = value
                with self.assertRaises(SemanticValidationError):
                    validate_candidate(entry)
        entry = sample()
        del entry["senses"][0]["confidence"]
        with self.assertRaises(SemanticValidationError):
            validate_candidate(entry)

    def test_more_than_five_total_senses_go_to_review_without_truncation(self):
        entry = sample()
        for index in (3, 4):
            extra = dict(entry["senses"][0], sense_id=f"extra-{index}", sense_number=index,
                         english_definition=f"a distinct meaning number {index}")
            entry["senses"].append(extra)
        result = assess_candidate(entry)
        self.assertIn("more_than_five_senses", result["review_reasons"])
        self.assertEqual(len(validate_candidate(entry)["senses"]), 6)

    def test_all_pos_require_contiguous_integer_numbering(self):
        for value in (0, 2, True, 1.0):
            entry = sample()
            entry["senses"][2]["sense_number"] = value
            with self.subTest(value=value), self.assertRaises(SemanticValidationError):
                validate_candidate(entry)

    def test_overlong_or_multiple_sentence_english_rejected(self):
        for definition in (" ".join(["word"] * 16), "To go free. To publish something."):
            entry = sample()
            entry["senses"][0]["english_definition"] = definition
            with self.assertRaises(SemanticValidationError):
                validate_candidate(entry)

    def test_duplicate_glosses_and_invalid_separators_rejected(self):
        for text in ("释放；释放", "释放、发布", "释放;发布", "释放；", "English only"):
            entry = sample()
            entry["senses"][0]["chinese_definition"] = text
            with self.subTest(text=text), self.assertRaises(SemanticValidationError):
                validate_candidate(entry)

    def test_unrelated_bank_and_break_senses_remain_separate(self):
        self.assertEqual([s["chinese_definition"] for s in validate_candidate(sample("bank"))["senses"]],
                         ["银行", "河岸"])
        self.assertEqual(len(validate_candidate(sample("break"))["senses"]), 3)

    def test_duplicate_english_and_ids_rejected(self):
        for key in ("sense_id", "english_definition"):
            entry = sample()
            entry["senses"][1][key] = entry["senses"][0][key]
            with self.assertRaises(SemanticValidationError):
                validate_candidate(entry)

    def test_bilingual_example_pairs_and_entry_budget(self):
        entry = sample()
        entry["senses"][0]["examples"] = entry["senses"][3]["examples"]
        with self.assertRaises(SemanticValidationError):
            validate_candidate(entry)
        entry = sample()
        del entry["senses"][3]["examples"][0]["chinese"]
        with self.assertRaises(SemanticValidationError):
            validate_candidate(entry)

    def test_frequency_missingness_and_invalid_types(self):
        self.assertIsNone(validate_candidate(sample())["frequency"]["frq"])
        for value in (-1, 0, True, "100"):
            entry = sample()
            entry["frequency"]["bnc"] = value
            with self.subTest(value=value), self.assertRaises(SemanticValidationError):
                validate_candidate(entry)

    def test_bad_provenance_refs_and_model_claimed_approval_rejected(self):
        entry = sample()
        entry["senses"][0]["source_entry_ids"] = ["a" * 64 + ":1"]
        with self.assertRaises(SemanticValidationError):
            validate_candidate(entry)
        entry = sample()
        entry["review_status"] = "approved"
        with self.assertRaises(SemanticValidationError):
            validate_candidate(entry)

    def test_low_confidence_and_high_confidence_both_need_independent_review(self):
        entry = sample()
        entry["senses"][0]["confidence"] = 0.4
        self.assertIn("low_self_reported_confidence", assess_candidate(entry)["review_reasons"])
        for sense in entry["senses"]:
            sense["confidence"] = 1.0
        self.assertFalse(assess_candidate(entry)["production_eligible"])

    def test_raw_source_binding_to_phase1_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "raw.jsonl"
            source.write_text('{"word":"release","translation":"释放"}\n')
            manifest = create_snapshot(source, root / "snapshot", source_format="jsonl", version="test")
            verify_snapshot(root / "snapshot")
            row = json.loads((root / "snapshot" / "raw_entries.jsonl").read_text())
            entry = sample()
            entry["provenance"].update(source_sha256=manifest["source_sha256"],
                                       raw_entry_ids=[row["entry_id"]], ecdict_version="test")
            for sense in entry["senses"]:
                sense["source_entry_ids"] = [row["entry_id"]]
            report = assess_candidate(entry, raw_entries={row["entry_id"]: row})
            self.assertTrue(report["raw_source_verified"])
            self.assertFalse(report["production_eligible"])
            entry["word"] = "bank"
            with self.assertRaises(SemanticValidationError):
                assess_candidate(entry, raw_entries={row["entry_id"]: row})

    def test_v2_cannot_enter_legacy_store(self):
        with tempfile.TemporaryDirectory() as folder:
            with SemanticStore(Path(folder) / "semantic.sqlite", writable=True) as store:
                with self.assertRaises(SemanticValidationError):
                    store.upsert_many([sample()])
                self.assertIsNone(store.get("release"))


if __name__ == "__main__":
    unittest.main()
