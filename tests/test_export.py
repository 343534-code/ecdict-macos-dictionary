import unittest
import xml.etree.ElementTree as ET

from scripts.export_ecdict_styled import (
    normalize_definition_punctuation,
    normalize_ipa_symbols,
    normalize_pronunciation,
    normalize_pronunciation_variants,
    render,
    render_inflections,
    render_metadata_badges,
    render_metadata_groups,
    render_rank_badges,
)


class RankBadgeTests(unittest.TestCase):
    def test_oxford_and_collins_marker(self):
        self.assertEqual(
            render_rank_badges("-K3"),
            '<span class="badges study-ranks">'
            '<span class="badge badge-rank">Oxford 3000</span>'
            '<span class="badge badge-rank">Collins 3★</span></span>',
        )

    def test_collins_only_marker(self):
        self.assertEqual(
            render_rank_badges("-5"),
            '<span class="badges study-ranks">'
            '<span class="badge badge-rank">Collins 5★</span></span>',
        )

    def test_regular_metadata_is_not_a_rank_marker(self):
        self.assertIsNone(render_rank_badges("(中高 80/60)"))

    def test_render_replaces_compact_marker(self):
        rendered = render("apple", b"`3`['aepl] `4`-K3`2`\nn. apple")
        self.assertIn("Oxford 3000", rendered)
        self.assertIn("Collins 3★", rendered)
        self.assertNotIn("-K3", rendered)
        self.assertIn('class="pronunciation"', rendered)
        self.assertIn('class="pos-group"', rendered)


class MetadataBadgeTests(unittest.TestCase):
    def test_exam_and_frequency_metadata(self):
        rendered = render_metadata_badges("(中高 80/60)")
        self.assertIn('class="badge badge-exam">中考</span>', rendered)
        self.assertIn('class="badge badge-exam">高考</span>', rendered)
        self.assertNotIn("CET4", rendered)
        self.assertIn("BNC #80", rendered)
        self.assertIn("COCA #60", rendered)

    def test_all_known_exam_markers(self):
        rendered = render_metadata_badges("(中高研四六托雅宝 2182/2057)")
        for label in (
            "中考", "高考", "考研", "CET4", "CET6", "TOEFL", "IELTS", "GRE"
        ):
            self.assertIn(label, rendered)

    def test_regular_metadata_is_not_exam_metadata(self):
        self.assertIsNone(render_metadata_badges("时态: abandoned, abandoning"))

    def test_parenthesized_dictionary_content_is_not_metadata(self):
        self.assertIsNone(render_metadata_badges("(NGC 1554/55)"))

    def test_frequency_is_secondary_text_and_exams_stay_in_footer(self):
        study, footer = render_metadata_groups("(中高 3208/3113)")
        self.assertIn('class="frequency-text"', study)
        self.assertIn("BNC #3208", study)
        self.assertIn("COCA #3113", study)
        self.assertNotIn("高频", study)
        self.assertIn("考试：", footer)
        self.assertIn("中考", footer)
        self.assertIn("高考", footer)


class LayoutTests(unittest.TestCase):
    def test_native_summary_keeps_each_pos_and_full_text_is_lossless(self):
        rendered = render('release', 'n. 释放, 发泄\nvt. 释放, 解除\nn. 发布\n[计] 版本, 发布\n`4`(研 1120/1232)'.encode())
        root = ET.fromstring('<root xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">' + rendered + '</root>')
        complete = ''.join(root.itertext())
        self.assertIn('②发布', complete)
        self.assertIn('[计算机] 版本；发布', complete)
        self.assertIn('BNC #1120', complete)
        priority = '{http://www.apple.com/DTDs/DictionaryService-1.0.rng}priority'
        for parent in root.iter():
            for child in list(parent):
                if child.get(priority) == '2':
                    parent.remove(child)
        summary = ''.join(root.itertext())
        self.assertIn('n.①释放；发泄', summary)
        self.assertIn('vt.释放；解除', summary)
        self.assertIn('②发布', summary)
        self.assertIn('BNC', summary)
        self.assertNotIn('d:priority=', rendered)
        self.assertLess(rendered.index('>vt.</span>'), rendered.index('>②</span>'))
        self.assertIn('class="pos-group pos-continuation"', rendered)

    def test_header_keeps_learning_value_with_headword(self):
        rendered = render(
            "two",
            "`3`[tu:] `4`-5`2`\nnum. two\n`4`(中高 80/60)".encode(),
        )
        self.assertTrue(rendered.startswith('<div class="entry-header"><h1>two</h1>'))
        header_end = rendered.index("</div>")
        self.assertLess(rendered.index('class="pronunciation"'), header_end)
        self.assertIn('class="badges study-ranks"', rendered[:header_end])
        self.assertGreater(rendered.index('class="frequency-text"'), header_end)

    def test_part_of_speech_and_definition_have_separate_columns(self):
        rendered = render("two", "num. 二, 二个".encode())
        self.assertIn('class="pos-group"', rendered)
        self.assertIn('<span class="pos">num.</span>', rendered)
        self.assertIn('<span class="definition">二；二个</span>', rendered)

    def test_long_part_of_speech_is_recognized(self):
        rendered = render("hello", "interj. 喂, 你好".encode())
        self.assertIn('<span class="pos">interj.</span>', rendered)

    def test_chinese_enumeration_uses_ideographic_comma(self):
        self.assertEqual(
            normalize_definition_punctuation("车库, 汽车修理厂, 机库"),
            "车库；汽车修理厂；机库",
        )
        self.assertEqual(
            normalize_definition_punctuation("HTTP, 网络协议"),
            "HTTP, 网络协议",
        )

    def test_legacy_phonetic_symbols_are_safely_normalized(self):
        normalized = normalize_pronunciation("[gә'rɑ:ʒ]")
        self.assertEqual(normalized, "/gəˈrɑːʒ/")
        self.assertNotIn("'", normalized)
        self.assertNotIn(":", normalized)
        self.assertEqual(
            normalize_pronunciation("[gә'rɑ:ʒ. 'gærɑ:ʒ]"),
            "/gəˈrɑːʒ/  /ˈgærɑːʒ/",
        )
        self.assertEqual(
            normalize_pronunciation_variants("[gә'rɑ:ʒ. 'gærɑ:ʒ]"),
            ["/gəˈrɑːʒ/", "/ˈgærɑːʒ/"],
        )
        self.assertEqual(normalize_ipa_symbols("ri'li:s"), "rɪˈliːs")

    def test_two_pronunciations_are_labelled_british_and_american(self):
        rendered = render("garage", "`3`[gә'rɑ:ʒ. 'gærɑ:ʒ]\nn. 车库".encode())
        self.assertIn('<span class="pronunciation-label">英</span>', rendered)
        self.assertIn('<span class="ipa">/gəˈrɑːʒ/</span>', rendered)
        self.assertIn('<span class="pronunciation-label">美</span>', rendered)
        self.assertIn('<span class="ipa">/ˈgærɑːʒ/</span>', rendered)

    def test_render_moves_metadata_after_core_definitions(self):
        rendered = render(
            "garage",
            "`3`[gә'rɑ:ʒ] `4`-K2`2`\nn. 车库, 汽车修理厂, 机库\n"
            "`4`(高研四六雅 3208/3113)".encode(),
        )
        core_start = rendered.index('class="core-senses')
        self.assertGreater(rendered.index("BNC #3208"), core_start)
        self.assertGreater(rendered.index("考试："), core_start)
        self.assertIn("车库；汽车修理厂；机库", rendered)
        self.assertIn("/gəˈrɑːʒ/", rendered)
        self.assertIn('class="pronunciation-variant"', rendered)
        self.assertIn('class="core-senses core-senses-divided"', rendered)

    def test_missing_optional_fields_do_not_leave_empty_sections(self):
        rendered = render("garage door opener", "n. 车库门开启装置".encode())
        self.assertIn('<h1>garage door opener</h1>', rendered)
        self.assertNotIn('class="pronunciation"', rendered)
        self.assertNotIn('class="inflections"', rendered)
        self.assertNotIn('class="exam-outline"', rendered)
        self.assertIn('class="core-senses"', rendered)
        self.assertNotIn('core-senses-divided', rendered)

    def test_long_definition_remains_inside_definition_column(self):
        definition = "描述一种在复杂上下文中需要自动换行但仍应保持右侧对齐的专业概念"
        rendered = render("incomprehensibility", f"n. {definition}".encode())
        self.assertIn('<span class="pos">n.</span>', rendered)
        self.assertIn(f'<span class="definition">{definition}</span>', rendered)

    def test_repeated_part_of_speech_is_merged_and_numbered(self):
        rendered = render(
            "release",
            "n. 释放, 发泄\nvt. 释放, 解除\nn. 发布".encode(),
        )
        self.assertEqual(rendered.count('<span class="pos">n.</span>'), 1)
        self.assertEqual(rendered.count('<span class="pos">vt.</span>'), 1)
        self.assertIn('<span class="sense-number">①</span>', rendered)
        self.assertIn('<span class="sense-number">②</span>', rendered)
        self.assertIn("释放；发泄", rendered)
        self.assertIn("发布", rendered)

    def test_computing_subject_label_is_expanded(self):
        rendered = render("release", "[计] 版本, 发布".encode())
        self.assertIn("[计算机] 版本；发布", rendered)
        self.assertNotIn("[计]", rendered)


class InflectionTests(unittest.TestCase):
    def test_regular_verb_uses_combined_past_label(self):
        rendered = render_inflections("时态: abandoned, abandoning, abandons")
        self.assertIn("过去式 / 过去分词", rendered)
        for form in ("abandoned", "abandoning", "abandons"):
            self.assertIn(
                f'<a class="inflection" href="x-dictionary:d:{form}">', rendered
            )
            self.assertIn(f'<span class="inflection-word">{form}</span>', rendered)

    def test_irregular_verb_uses_four_precise_labels(self):
        rendered = render_inflections("时态: took, taken, taking, takes")
        for label in ("过去式", "过去分词", "现在分词", "第三人称单数"):
            self.assertIn(label, rendered)
        for form in ("took", "taken", "taking", "takes"):
            self.assertIn(
                f'<a class="inflection" href="x-dictionary:d:{form}">', rendered
            )
            self.assertIn(f'<span class="inflection-word">{form}</span>', rendered)

    def test_non_inflection_metadata_is_ignored(self):
        self.assertIsNone(render_inflections("级别: A1"))

    def test_render_replaces_raw_tense_line(self):
        rendered = render("take", "`4`时态: took, taken, taking, takes".encode())
        self.assertIn('class="inflections"', rendered)
        self.assertNotIn("时态:", rendered)


if __name__ == "__main__":
    unittest.main()
