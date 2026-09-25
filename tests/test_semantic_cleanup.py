import tempfile
import unittest
from pathlib import Path

from scripts.export_ecdict_styled import render_semantic_entry
from semantic_cleanup.prepare_requests import is_priority
from semantic_cleanup.schema import SemanticValidationError, validate_semantic_entry
from semantic_cleanup.store import SemanticStore


def release_entry():
    return {
        "schema_version": "1.0",
        "word": "release",
        "pronunciation": ["/rɪˈliːs/"],
        "senses": [
            {
                "pos": "n.",
                "sense_number": 1,
                "english_definition": "the act of making someone or something free",
                "chinese_definition": "释放；解放；解除限制；释放",
                "examples": [],
                "usage_notes": [],
            },
            {
                "pos": "n.",
                "sense_number": 2,
                "english_definition": "an official announcement or publication",
                "chinese_definition": "发布、发行",
                "examples": [],
                "usage_notes": [],
            },
            {
                "pos": "vt.",
                "sense_number": 1,
                "english_definition": "to let someone or something go free",
                "chinese_definition": "释放；放走",
                "examples": [],
                "usage_notes": [],
            },
            {
                "pos": "vt.",
                "sense_number": 2,
                "english_definition": "to make something available to the public",
                "chinese_definition": "发布；发行；推出",
                "examples": [
                    {
                        "english": "The company released a new product.",
                        "chinese": "公司发布了一款新产品。",
                    }
                ],
                "usage_notes": [],
            },
        ],
        "morphology": [
            {"label": "过去式", "form": "released"},
            {"label": "现在分词", "form": "releasing"},
            {"label": "三单", "form": "releases"},
        ],
        "exam_tags": ["CET4", "CET6", "TOEFL", "IELTS"],
        "frequency": {"bnc": 1120, "coca": 1232, "oxford_3000": True, "collins": 5},
        "provenance": {"source": "test", "model": "test"},
    }


class SemanticEntryTests(unittest.TestCase):
    def test_normalizes_glosses_and_preserves_pos_numbering(self):
        entry = validate_semantic_entry(release_entry())
        self.assertEqual(entry["senses"][0]["chinese_definition"], "释放；解放；解除限制")
        self.assertEqual(entry["senses"][1]["chinese_definition"], "发布；发行")

    def test_rejects_non_contiguous_pos_numbering(self):
        entry = release_entry()
        entry["senses"][1]["sense_number"] = 3
        with self.assertRaises(SemanticValidationError):
            validate_semantic_entry(entry)

    def test_rejects_more_than_one_example_per_entry(self):
        entry = release_entry()
        entry["senses"][0]["examples"] = [{"english": "A release happened.", "chinese": "发生了发布。"}]
        with self.assertRaises(SemanticValidationError):
            validate_semantic_entry(entry)

    def test_store_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "semantic.sqlite"
            with SemanticStore(database, writable=True) as store:
                self.assertEqual(store.upsert_many([release_entry()]), 1)
            with SemanticStore(database) as store:
                self.assertEqual(store.get("release")["word"], "release")

    def test_semantic_render_has_all_learning_layers(self):
        rendered = render_semantic_entry(validate_semantic_entry(release_entry()))
        self.assertIn("Oxford 3000", rendered)
        self.assertIn("Collins 5★", rendered)
        self.assertIn('class="sense-number">①</span>', rendered)
        self.assertIn('class="sense-number">②</span>', rendered)
        self.assertIn("The company released a new product.", rendered)
        self.assertIn("考试：", rendered)
        self.assertIn("词频：", rendered)
        self.assertIn("BNC 1120 · COCA 1232", rendered)

    def test_priority_selection_is_not_limited_to_one_word(self):
        rules = {
            "priority": {
                "include_oxford_3000": True,
                "minimum_collins_stars": 3,
                "bnc_core_max": 5000,
                "coca_core_max": 5000,
                "include_exam_tagged": True,
            }
        }
        self.assertTrue(is_priority({"frequency": {"bnc": 120}}, rules))
        self.assertTrue(is_priority({"frequency": {}, "exam_tags": ["CET4"]}, rules))
        self.assertFalse(is_priority({"frequency": {"bnc": 99999}, "exam_tags": []}, rules))


if __name__ == "__main__":
    unittest.main()
