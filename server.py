"""Daily Affirmations web app. Run it from a terminal:

    python3 server.py

then open http://localhost:8000 (it opens automatically by default).
Uses only Python's standard library.
"""

import argparse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import affirmations as aff
import music
import pages

HERE = Path(__file__).resolve().parent


class App:
    """Decides what to send back for each request. Kept separate from the
    networking code so it is easy to test."""

    def __init__(self, data_dir=HERE):
        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        self.affirmations_file = aff.ensure_file(data_dir / "affirmations.txt")
        self.ratings_file = data_dir / "ratings.json"
        self.music_file = data_dir / "calm_music.wav"

    def card_for(self, text, message="", error=False, selected=None):
        ratings = aff.load_ratings(self.ratings_file)
        avg = aff.average_rating(ratings, text) if text else None
        return pages.render_card(text, avg, message, error, selected)

    def handle(self, method, raw_path, body=b""):
        """Return (status_code, content_type, body_bytes)."""
        url = urlparse(raw_path)
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        form = {k: v[0] for k, v in parse_qs(body.decode("utf-8", "replace")).items()}
        html = "text/html; charset=utf-8"

        if method == "GET" and url.path == "/":
            return 200, html, pages.render_main_page().encode()

        if method == "GET" and url.path == "/card":
            if query.get("action") == "next":
                text = aff.pick_affirmation(aff.load_affirmations(self.affirmations_file),
                                            previous=query.get("prev"))
                return 200, html, self.card_for(text).encode()
            return 200, html, self.card_for(None).encode()

        if method == "POST" and url.path == "/card/rate":
            text = aff.clean_text(form.get("text", ""))
            try:
                aff.rate_affirmation(self.ratings_file, text, form.get("stars", ""))
                stars = int(form["stars"])
                msg = "Thank you! Your rating was saved."
                return 200, html, self.card_for(text, msg, selected=stars).encode()
            except (ValueError, KeyError):
                return 400, html, self.card_for(text or None, "Please pick 1 to 5 stars.",
                                                error=True).encode()

        if method == "POST" and url.path == "/card/add":
            text = aff.clean_text(form.get("text", ""))
            if aff.add_affirmation(self.affirmations_file, text):
                msg = "Added! It is now part of your daily cycle."
                return 200, html, self.card_for(text, msg).encode()
            msg = "That one is already in your list." if text else "Please write something first."
            return 200, html, self.card_for(text or None, msg, error=True).encode()

        if method == "GET" and url.path == "/music.wav":
            music.ensure_music(self.music_file)
            return 200, "audio/wav", self.music_file.read_bytes()

        return 404, "text/plain; charset=utf-8", b"Not found"


def apply_range(payload, range_header):
    """Handle a 'Range: bytes=start-end' request (Safari needs this for audio).

    Returns (status, payload_slice, extra_headers).
    """
    total = len(payload)
    headers = {"Accept-Ranges": "bytes"}
    if not range_header or not range_header.startswith("bytes="):
        return 200, payload, headers
    try:
        start_s, end_s = range_header[len("bytes="):].split(",")[0].split("-")
        if start_s == "":                    # "bytes=-500" means the last 500 bytes
            start, end = max(0, total - int(end_s)), total - 1
        else:
            start = int(start_s)
            end = min(int(end_s), total - 1) if end_s else total - 1
    except ValueError:
        return 200, payload, headers
    if start >= total or start > end:
        headers["Content-Range"] = f"bytes */{total}"
        return 416, b"", headers
    headers["Content-Range"] = f"bytes {start}-{end}/{total}"
    return 206, payload[start:end + 1], headers


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, method, body=b"", head_only=False):
            status, ctype, payload = app.handle(method, self.path, body)
            extra = {}
            if status == 200 and ctype == "audio/wav":
                status, payload, extra = apply_range(payload, self.headers.get("Range"))
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(payload)))
            for key, value in extra.items():
                self.send_header(key, value)
            self.end_headers()
            if not head_only:
                self.wfile.write(payload)

        def do_GET(self):
            self._send("GET")

        def do_HEAD(self):
            self._send("GET", head_only=True)

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            self._send("POST", self.rfile.read(min(length, 10_000)))

        def log_message(self, fmt, *args):  # keep the terminal quiet
            pass

    return Handler


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Daily affirmations webpage")
    parser.add_argument("--port", type=int, default=8000, help="port to serve on (default 8000)")
    parser.add_argument("--data-dir", default=str(HERE),
                        help="folder for affirmations.txt, ratings.json and the music")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    app = App(args.data_dir)
    print("Preparing calming music...")
    music.ensure_music(app.music_file)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(app))
    url = f"http://localhost:{args.port}"
    print(f"Daily Affirmations is running at {url}")
    print("Press Ctrl+C to stop.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGoodbye. Be kind to yourself today.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
