# Handoff: Round 2 → Round 3 (Daily Affirmations)

Written 2026-11-13 for a fresh session starting round 3. Round 1 produced
`Problem.md` and `Spec.md`. Round 2 built the program (commits `deef4d1`
through `d012517`, plus the user's `cc01e21`).

Standing rules for every session are in `CLAUDE.md` (this folder) and
`../CLAUDE.md`. Read both first.

## Current state

- **Working.** All of `Spec.md` is implemented: a nature-themed page, an
  affirmation button, generated calming music, user-written affirmations
  appended to `affirmations.txt`, and 1–5 star ratings.
- **61 tests pass** (checked 2026-11-13).
- **Python standard library only,** so there is nothing to install. Python 3.14.2
  on macOS.
- **The user has run it themselves:** `affirmations.txt` (16 lines, so one
  user-added entry) and `ratings.json` exist.

| File | Purpose |
|---|---|
| `server.py` | entry point, HTTP server, URL routing (`App.handle`), `apply_range` |
| `affirmations.py` | read/write `affirmations.txt` and `ratings.json`, random pick, averages |
| `pages.py` | HTML/CSS as Python strings (main page and iframe card) |
| `music.py` | generates `calm_music.wav` from sine waves |
| `tests/` | one `test_*.py` per module, using `unittest` |
| `README.md` | user-facing run/test instructions |
| `decisions.md` | 40 choices made in round 2 that the spec didn't ask for |
| `HANDOFF.md` | older end-of-session notes from round 2; superseded by this file |

## How to run

```
cd ~/csc299-main/Project-1-Daily-affirmations
python3 server.py                 # opens http://localhost:8000; Ctrl+C to stop
python3 server.py --port 8001 --no-browser --data-dir /some/tmp/dir
```

## How to test

```
python3 -m unittest discover -s tests -t . -v      # all tests
python3 -m unittest tests.test_affirmations -v     # one file
```

pytest is **not** installed, so don't write pytest-only tests.

## Decisions made in round 2, and why

The full list with reasons is in `decisions.md`. The ones that shape future work:

- **No JavaScript; the card is an `<iframe>` at `/card`.** Forms reload only the
  card, so the music in the outer page keeps playing. Adding JS would remove
  the need for the iframe, but it breaks "Python only" (CLAUDE.md rule 1).
- **Routing is a pure function,** `App.handle(method, path, body)` →
  `(status, content_type, bytes)`. Tests call it directly. Keep new routes there.
- **Music is generated once** and cached in `calm_music.wav`. `/music.wav`
  supports Range and HEAD requests, because Safari needs them.
- **Ratings live in `ratings.json`, keyed by the exact affirmation text,** with
  every score kept. The txt file stays one plain affirmation per line.
- **Selection is uniform random with no immediate repeat.** Ratings don't
  affect it yet.
- **Runtime data is git-ignored:** `affirmations.txt`, `ratings.json`,
  `calm_music.wav`.
- **The server binds to `127.0.0.1` only.**

## Unresolved

- **Should ratings affect selection?** (decisions.md #25) I suggested
  weighting toward higher ratings. The user hasn't answered.
- **No one has viewed the page in a browser during a session** (layout, phone
  width). It has only been checked with `curl` and the tests.
- **Safari audio playback** is untested in practice.
- **The 300-character limit** on new affirmations is enforced only by the
  browser (`maxlength`), not the server.
- **No way to delete or edit affirmations** from the page.
- **Course session-start routine not done.** Nobody has re-fetched the
  instructor's instructions or checked for new migrations since round 2 began.
- **Learning check-ins unanswered:** (1) why the music keeps playing when the
  card reloads; (2) which test fails if `MAX_STARS` became 10; (3) what a page
  refresh does after Ctrl+C. HANDOFF.md has the answers.

## Warnings for the next session

- **The original files are protected.** CLAUDE.md rule 2 forbids editing or
  deleting `Problem.md`, `Spec.md` and `CLAUDE.md`. The user has since allowed
  standing rules to be added to `CLAUDE.md`. Ask before any other change there.
- **Never undo or amend a commit,** even to fix a mistake. Make a new commit
  instead.
- **Commit `cc01e21` doesn't match its message.** It says "Added decisions.md
  and handoff.md", but it only adds an empty `.Rhistory` (an RStudio file).
  Those two files were already in earlier commits. Leave it; mention it only if
  it's relevant.
- **`ratings.json` and `affirmations.txt` are the user's real data,** including
  entries from their own manual testing. Don't delete, reset or commit them.
  Tests must use temp directories via `--data-dir` / `App(tmpdir)`.
- **A damaged `ratings.json` is read as empty,** and the next rating
  overwrites it. Be careful when changing the ratings format: existing data
  must still load.
- **Ratings are matched by exact text.** Changing `clean_text()` could orphan
  existing ratings.
- **Port 8000 may already be in use** if an earlier server is still running.
  Use `--port`.
- **CSS in `pages.py` uses `%` formatting,** so a literal `%` must be written
  `%%`. A test checks for leftovers.
