import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode

import affirmations as aff
import music
import server


class AppTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.app = server.App(self.dir)

    def tearDown(self):
        self._tmp.cleanup()

    def post(self, path, **fields):
        return self.app.handle("POST", path, urlencode(fields).encode())


class TestApp(AppTest):
    def test_creates_txt_file_on_start(self):
        self.assertTrue((self.dir / "affirmations.txt").exists())

    def test_main_page(self):
        status, ctype, body = self.app.handle("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn(b"Daily Affirmations", body)

    def test_card_placeholder(self):
        status, _, body = self.app.handle("GET", "/card")
        self.assertEqual(status, 200)
        self.assertIn(b"Give me an affirmation", body)

    def test_next_gives_an_affirmation_from_file(self):
        _, _, body = self.app.handle("GET", "/card?action=next")
        text = body.decode()
        self.assertTrue(any(a.replace("'", "&#x27;") in text
                            for a in aff.DEFAULT_AFFIRMATIONS))

    def test_add_then_it_appears_in_cycle(self):
        status, _, body = self.post("/card/add", text="I am a calm, steady river.")
        self.assertEqual(status, 200)
        self.assertIn(b"Added!", body)
        lines = (self.dir / "affirmations.txt").read_text(encoding="utf-8").splitlines()
        self.assertIn("I am a calm, steady river.", lines)

    def test_user_affirmation_is_served_by_next(self):
        (self.dir / "affirmations.txt").write_text("Only mine\n", encoding="utf-8")
        _, _, body = self.app.handle("GET", "/card?action=next")
        self.assertIn(b"Only mine", body)

    def test_add_empty_and_duplicate(self):
        _, _, body = self.post("/card/add", text="  ")
        self.assertIn(b"Please write something first.", body)
        self.post("/card/add", text="Twice")
        _, _, body = self.post("/card/add", text="Twice")
        self.assertIn(b"already in your list", body)

    def test_rate(self):
        status, _, body = self.post("/card/rate", text="I can do hard things.", stars="5")
        self.assertEqual(status, 200)
        self.assertIn(b"Average: 5.0", body)
        ratings = aff.load_ratings(self.dir / "ratings.json")
        self.assertEqual(ratings["I can do hard things."], [5])

    def test_rate_invalid(self):
        status, _, body = self.post("/card/rate", text="x", stars="9")
        self.assertEqual(status, 400)
        self.assertIn(b"Please pick 1 to 5 stars.", body)
        status, _, _ = self.post("/card/rate", text="x")
        self.assertEqual(status, 400)

    def test_not_found(self):
        self.assertEqual(self.app.handle("GET", "/nope")[0], 404)

    def test_music_served(self):
        # pre-create a tiny file so the test does not build the full track
        music.write_wav(self.app.music_file, music.generate_samples(1.0, 1000), 1000)
        status, ctype, body = self.app.handle("GET", "/music.wav")
        self.assertEqual(status, 200)
        self.assertEqual(ctype, "audio/wav")
        self.assertTrue(body.startswith(b"RIFF"))


class TestRealServer(AppTest):
    """Start the real HTTP server on a free port and talk to it."""

    def setUp(self):
        super().setUp()
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(self.app))
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        super().tearDown()

    def test_get_and_post_over_http(self):
        with urllib.request.urlopen(self.base + "/") as r:
            self.assertEqual(r.status, 200)
        data = urlencode({"text": "Sent over HTTP"}).encode()
        with urllib.request.urlopen(self.base + "/card/add", data=data) as r:
            self.assertIn(b"Added!", r.read())
        self.assertIn("Sent over HTTP", aff.load_affirmations(self.dir / "affirmations.txt"))


class TestApplyRange(unittest.TestCase):
    DATA = bytes(range(10))

    def test_no_range_returns_everything(self):
        status, body, headers = server.apply_range(self.DATA, None)
        self.assertEqual((status, body), (200, self.DATA))
        self.assertEqual(headers["Accept-Ranges"], "bytes")

    def test_start_and_end(self):
        status, body, headers = server.apply_range(self.DATA, "bytes=0-1")
        self.assertEqual((status, body), (206, b"\x00\x01"))
        self.assertEqual(headers["Content-Range"], "bytes 0-1/10")

    def test_open_ended(self):
        self.assertEqual(server.apply_range(self.DATA, "bytes=7-")[1], b"\x07\x08\x09")

    def test_suffix(self):
        self.assertEqual(server.apply_range(self.DATA, "bytes=-2")[1], b"\x08\x09")

    def test_end_past_file_is_clamped(self):
        self.assertEqual(server.apply_range(self.DATA, "bytes=8-99")[1], b"\x08\x09")

    def test_unsatisfiable(self):
        status, body, headers = server.apply_range(self.DATA, "bytes=50-60")
        self.assertEqual((status, body), (416, b""))
        self.assertEqual(headers["Content-Range"], "bytes */10")

    def test_garbage_ignored(self):
        self.assertEqual(server.apply_range(self.DATA, "bytes=a-b")[0], 200)


class TestRealServerMusic(TestRealServer):
    def test_range_and_head(self):
        music.write_wav(self.app.music_file, music.generate_samples(1.0, 1000), 1000)
        req = urllib.request.Request(self.base + "/music.wav", headers={"Range": "bytes=0-1"})
        with urllib.request.urlopen(req) as r:
            self.assertEqual(r.status, 206)
            self.assertEqual(r.read(), b"RI")
        req = urllib.request.Request(self.base + "/music.wav", method="HEAD")
        with urllib.request.urlopen(req) as r:
            self.assertEqual(r.status, 200)
            self.assertEqual(r.read(), b"")


class TestArgs(unittest.TestCase):
    def test_defaults(self):
        args = server.parse_args([])
        self.assertEqual(args.port, 8000)
        self.assertFalse(args.no_browser)

    def test_custom(self):
        args = server.parse_args(["--port", "9000", "--no-browser"])
        self.assertEqual(args.port, 9000)
        self.assertTrue(args.no_browser)


if __name__ == "__main__":
    unittest.main()
