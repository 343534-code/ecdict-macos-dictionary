import unittest

from scripts.export_ecdict_styled import render, render_rank_badges


class RankBadgeTests(unittest.TestCase):
    def test_oxford_and_collins_marker(self):
        self.assertEqual(
            render_rank_badges("-K3"),
            '<div class="badges"><span class="badge">Oxford 3000</span>'
            '<span class="badge">Collins 3★</span></div>',
        )

    def test_collins_only_marker(self):
        self.assertEqual(
            render_rank_badges("-5"),
            '<div class="badges"><span class="badge">Collins 5★</span></div>',
        )

    def test_regular_metadata_is_not_a_rank_marker(self):
        self.assertIsNone(render_rank_badges("(中高 80/60)"))

    def test_render_replaces_compact_marker(self):
        rendered = render("apple", b"`3`['aepl] `4`-K3`2`\nn. apple")
        self.assertIn("Oxford 3000", rendered)
        self.assertIn("Collins 3★", rendered)
        self.assertNotIn("-K3", rendered)
        self.assertIn('class="pronunciation"', rendered)
        self.assertIn('class="sense"', rendered)


if __name__ == "__main__":
    unittest.main()
