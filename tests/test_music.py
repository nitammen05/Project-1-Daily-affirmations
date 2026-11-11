import tempfile
import unittest
import wave
from pathlib import Path

import music


class TestEnvelope(unittest.TestCase):
    def test_silent_outside_note(self):
        self.assertEqual(music.envelope(-1, 8, 2), 0.0)
        self.assertEqual(music.envelope(9, 8, 2), 0.0)

    def test_starts_and_ends_silent(self):
        self.assertAlmostEqual(music.envelope(0, 8, 2), 0.0)
        self.assertAlmostEqual(music.envelope(8, 8, 2), 0.0)

    def test_full_volume_in_middle(self):
        self.assertEqual(music.envelope(4, 8, 2), 1.0)

    def test_stays_between_zero_and_one(self):
        for i in range(81):
            v = music.envelope(i / 10, 8, 2)
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)


class TestSamples(unittest.TestCase):
    def test_pad_in_range(self):
        for i in range(0, 8000, 37):
            v = music.pad_sample(music.CHORDS[0], i / 1000, 8.0)
            self.assertLessEqual(abs(v), 1.0)

    def test_chime_silent_before_strike_and_fades(self):
        self.assertEqual(music.chime_sample(440, -0.5), 0.0)
        self.assertLess(abs(music.chime_sample(440, 5.0)), 0.01)

    def test_generate_length_and_range(self):
        # short chords + low sample rate keep the test fast
        s = music.generate_samples(seconds_per_chord=4.0, sample_rate=2000)
        self.assertEqual(len(s), 4 * 4 * 2000)
        self.assertTrue(all(-32768 <= x <= 32767 for x in s))
        self.assertGreater(max(s), 1000)  # not silent

    def test_loop_edges_are_quiet(self):
        s = music.generate_samples(seconds_per_chord=4.0, sample_rate=2000)
        self.assertLess(abs(s[0]), 500)
        self.assertLess(abs(s[-1]), 500)


class TestFiles(unittest.TestCase):
    def test_write_and_ensure(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "m.wav"
            music.write_wav(path, music.generate_samples(4.0, 2000), sample_rate=2000)
            with wave.open(str(path)) as w:
                self.assertEqual(w.getnchannels(), 1)
                self.assertEqual(w.getframerate(), 2000)
                self.assertEqual(w.getnframes(), 32000)
            before = path.stat().st_mtime_ns
            music.ensure_music(path)  # should NOT regenerate
            self.assertEqual(path.stat().st_mtime_ns, before)


if __name__ == "__main__":
    unittest.main()
