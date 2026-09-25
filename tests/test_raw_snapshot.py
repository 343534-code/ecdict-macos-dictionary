import base64
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from semantic_cleanup.raw_snapshot import create_snapshot, extract_mdx, read_source, standardize, verify_snapshot


class RawSnapshotTests(unittest.TestCase):
    def test_preserves_original_fields_and_missingness(self):
        row = {"word": " Release ", "translation": "n. 释放, 发布\r\n", "phonetic": "ri'li:s",
               "frq": "1232", "bnc": "0", "custom": {"x": [1, None]}}
        entry = standardize(row, source_sha256="a" * 64, ordinal=1, version="1.0.28")
        self.assertEqual(entry["raw_fields"], row)
        self.assertEqual(entry["translation_raw"], row["translation"])
        self.assertEqual(entry["phonetic"], "ri'li:s")
        self.assertEqual(entry["frq"], "1232")
        self.assertIsNone(entry["coca"])
        self.assertEqual(entry["word"], " Release ")

    def test_snapshot_duplicate_words_have_distinct_ids_and_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.jsonl"
            source.write_text('{"word":"bank","translation":"银行"}\n{"word":"bank","translation":"河岸"}\n', encoding="utf-8")
            original = source.read_bytes()
            output = root / "snapshot"
            manifest = create_snapshot(source, output, source_format="jsonl", version="test")
            self.assertEqual(verify_snapshot(output), manifest)
            records = [json.loads(line) for line in (output / "raw_entries.jsonl").read_text().splitlines()]
            self.assertNotEqual(records[0]["entry_id"], records[1]["entry_id"])
            with self.assertRaises(FileExistsError):
                create_snapshot(source, output, source_format="jsonl", version="test")
            self.assertEqual(source.read_bytes(), original)
            with (output / "raw_entries.jsonl").open("a") as stream:
                stream.write(" ")
            with self.assertRaises(ValueError):
                verify_snapshot(output)

    def test_failure_is_not_a_completed_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "bad.jsonl"
            source.write_text('{"word":"ok"}\n{"word":null}\n')
            with self.assertRaises(ValueError):
                create_snapshot(source, root / "snapshot", source_format="jsonl", version="test")
            self.assertFalse((root / "snapshot" / "manifest.json").exists())

    def test_csv_quoted_newlines_and_unknown_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "input.csv"
            source.write_text('word,translation,extra\nrelease,"n. 释放, 发布\nvt. 释放",保留\n', encoding="utf-8")
            rows = list(read_source(source, "csv"))
            self.assertEqual(rows[0]["translation"], "n. 释放, 发布\nvt. 释放")
            self.assertEqual(rows[0]["extra"], "保留")

    def test_mdx_bytes_and_redirects_are_lossless(self):
        key, body = b"alias\xff", b"@@@LINK=target\r\n\xff"
        with patch.dict("sys.modules", {"readmdict": type("Reader", (), {"MDX": lambda path: {key: body}})}):
            row = next(iter(read_source(Path("example.mdx"), "mdx")))
        self.assertEqual(base64.b64decode(row["mdx_key_base64"]), key)
        self.assertEqual(base64.b64decode(row["mdx_body_base64"]), body)

    def test_mdx_extraction_keeps_ascii_ipa_and_gloss_punctuation(self):
        entry = extract_mdx("`1`release`3`[ri'li:s]`2`\r\nn. 释放, 发布</br>时态: released, releasing</br>`4`K5</br>(研四 1120/1232)")
        self.assertEqual(entry["phonetic"], "[ri'li:s]")
        self.assertEqual(entry["translation_raw"], "n. 释放, 发布")
        self.assertEqual(entry["pos"], ["n."])
        self.assertEqual(entry["coca"], 1232)
        self.assertNotIn("frq", entry)
        self.assertEqual(entry["collins"], 5)

    def test_bounded_sample_is_marked_as_sample(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.jsonl"
            source.write_text('{"word":"first"}\ninvalid line\n')
            manifest = create_snapshot(source, root / "sample", source_format="jsonl", version="test", limit=1)
            self.assertEqual(manifest["scope"], "sample")
            self.assertEqual(manifest["entry_count"], 1)
            self.assertEqual(verify_snapshot(root / "sample"), manifest)


if __name__ == "__main__":
    unittest.main()
