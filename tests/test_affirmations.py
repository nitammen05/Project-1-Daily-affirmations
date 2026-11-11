import random
import tempfile
import unittest
from pathlib import Path

import affirmations as aff


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.txt = self.dir / "affirmations.txt"
        self.ratings = self.dir / "ratings.json"

    def tearDown(self):
        self._tmp.cleanup()


class TestEnsureAndLoad(TempDirTest):
    def test_ensure_file_creates_defaults(self):
        aff.ensure_file(self.txt)
        self.assertTrue(self.txt.exists())
        self.assertEqual(aff.load_affirmations(self.txt), aff.DEFAULT_AFFIRMATIONS)

    def test_ensure_file_does_not_overwrite(self):
        self.txt.write_text("Mine only\n", encoding="utf-8")
        aff.ensure_file(self.txt)
        self.assertEqual(aff.load_affirmations(self.txt), ["Mine only"])

    def test_load_skips_blank_lines(self):
        self.txt.write_text("a\n\n   \nb\n", encoding="utf-8")
        self.assertEqual(aff.load_affirmations(self.txt), ["a", "b"])


class TestCleanText(unittest.TestCase):
    def test_collapses_whitespace_and_newlines(self):
        self.assertEqual(aff.clean_text("  I am\n  strong  "), "I am strong")

    def test_empty(self):
        self.assertEqual(aff.clean_text("   \n "), "")


class TestAddAffirmation(TempDirTest):
    def test_adds_to_file_and_cycle(self):
        self.assertTrue(aff.add_affirmation(self.txt, "I shine bright."))
        self.assertIn("I shine bright.", aff.load_affirmations(self.txt))
        self.assertTrue(self.txt.read_text(encoding="utf-8").endswith("I shine bright.\n"))

    def test_rejects_empty(self):
        self.assertFalse(aff.add_affirmation(self.txt, "   "))

    def test_rejects_duplicate(self):
        aff.add_affirmation(self.txt, "Unique one")
        self.assertFalse(aff.add_affirmation(self.txt, "Unique one"))
        self.assertEqual(aff.load_affirmations(self.txt).count("Unique one"), 1)

    def test_multiline_input_becomes_one_line(self):
        aff.add_affirmation(self.txt, "line one\nline two")
        self.assertIn("line one line two", aff.load_affirmations(self.txt))


class TestPick(unittest.TestCase):
    def test_empty_list(self):
        self.assertIsNone(aff.pick_affirmation([]))

    def test_avoids_previous(self):
        rng = random.Random(0)
        for _ in range(50):
            self.assertEqual(aff.pick_affirmation(["a", "b"], previous="a", rng=rng), "b")

    def test_single_item_still_returned(self):
        self.assertEqual(aff.pick_affirmation(["only"], previous="only"), "only")


class TestRatings(TempDirTest):
    def test_missing_file_is_empty(self):
        self.assertEqual(aff.load_ratings(self.ratings), {})

    def test_corrupt_file_is_empty(self):
        self.ratings.write_text("{not json", encoding="utf-8")
        self.assertEqual(aff.load_ratings(self.ratings), {})

    def test_rate_and_average(self):
        aff.rate_affirmation(self.ratings, "I can do hard things.", 5)
        aff.rate_affirmation(self.ratings, "I can do hard things.", 4)
        ratings = aff.load_ratings(self.ratings)
        self.assertEqual(ratings["I can do hard things."], [5, 4])
        self.assertEqual(aff.average_rating(ratings, "I can do hard things."), 4.5)

    def test_average_unrated(self):
        self.assertIsNone(aff.average_rating({}, "x"))

    def test_invalid_stars(self):
        for bad in (0, 6, -1):
            with self.assertRaises(ValueError):
                aff.rate_affirmation(self.ratings, "x", bad)
        with self.assertRaises(ValueError):
            aff.rate_affirmation(self.ratings, "x", "abc")

    def test_empty_text_rejected(self):
        with self.assertRaises(ValueError):
            aff.rate_affirmation(self.ratings, "  ", 3)


if __name__ == "__main__":
    unittest.main()
