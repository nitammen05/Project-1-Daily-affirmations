# Handoff: Daily Affirmations

Last updated 2026-11-13. Notes for whoever picks this up next (a new Claude
session or me).

## Status: working, all requirements in Spec.md met

Built 2026-11-11 in commit `deef4d1`. 61 tests pass. The server has been run
from the terminal and checked with `curl`. The user has also run it themselves,
because `affirmations.txt` and `ratings.json` now exist.

- Run: `python3 server.py` (opens http://localhost:8000; stop with Ctrl+C)
- Test: `python3 -m unittest discover -s tests -t . -v`
- Layout and file purposes: see `README.md`

## Rules to keep following (from this folder's CLAUDE.md)

- Python only, standard library only (no pip installs; pytest is not installed,
  so use `unittest`).
- Never edit or delete the original files: `Spec.md`, `Problem.md`, `CLAUDE.md`.
- Add tests for every new function, written as you go, not at the end.
- Don't ask the user how to implement things. Make reasonable decisions.
- The parent `../CLAUDE.md` still applies: tutor, explain terms, check
  understanding, and commit after changes.

## Design decisions already made (don't re-litigate)

- **No JavaScript.** The affirmation card is a separate page (`/card`) inside an
  `<iframe>`, so its form buttons reload only the card and the music keeps playing.
- **Music is generated** by `music.py` (sine-wave chords and chimes, about 32 s
  loop, about 1.4 MB WAV), created once on first run.
- **Range requests and HEAD** are supported for `/music.wav` (`apply_range` in
  `server.py`), because Safari needs them to play audio.
- **Any shown affirmation can be rated**, not only the built-in ones.
- **Personal data is git-ignored:** `affirmations.txt`, `ratings.json`,
  `calm_music.wav`. They are created at runtime.
- `App.handle()` returns `(status, content_type, bytes)` and is kept separate
  from the networking so it can be tested without a server.

## Not yet verified

- Nobody has looked at the page visually in a browser in a session (layout,
  phone width, dark backgrounds). Worth a look.
- Audio playback in Safari is untested in practice (only Range support is tested).

## Possible next steps (only if the user wants them)

- Show the top-rated affirmations, or pick highly rated ones more often.
- Let the user delete their own affirmations.
- A "today's affirmation" that stays the same all day.

## Teaching thread to pick up

- The user learned how to run the app and the tests. Three check-yourself
  questions were asked but **not answered yet**:
  1. Why doesn't clicking "Another affirmation" stop the music? (Answer: the
     iframe.)
  2. If `MAX_STARS` became 10, which test fails? (Answer:
     `test_invalid_stars`, since 6 would become valid.)
  3. What happens if you refresh the page after Ctrl+C? (Answer: the browser
     can't connect.)
  Ask one of these again to check understanding.
- Session-start routine skipped on 2026-11-11: re-fetching the course
  instructions and checking for new migrations. Do it at the start of the next
  session.

## Loose ends

- `.Rhistory` (an R history file, not from this project) is untracked in this
  folder. It was left alone. Ask the user before deleting or ignoring it.
