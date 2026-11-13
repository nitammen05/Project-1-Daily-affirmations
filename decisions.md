# Decisions I made that you didn't ask for

Spec.md asked for: a webpage with a comforting, nature-themed design; a button
that shows positive affirmations; calming music; a way to write your own
affirmations; 1–5 star ratings for the pre-made ones; and a txt file that holds
all affirmations, with yours added to the cycle.

Everything below was my choice. CLAUDE.md rule 6 allowed reasonable decisions.
Each entry says what I chose, why, and where to change it if you disagree.

## Technology

1. **Standard library only, no installs.** I didn't use a web framework like
   Flask. *Why:* it runs on any machine with Python and has no setup steps.
   *Cost:* the server code is a bit lower-level than Flask would be.
2. **HTML and CSS written as Python strings** in `pages.py`. *Why:* a webpage
   needs HTML, and rule 1 says Python only, so the page lives inside Python files.
3. **No JavaScript.** Buttons are ordinary HTML forms that reload the card.
   *Why:* this stays as close to "Python only" as a webpage can.
4. **The card is an `<iframe>`** (a page inside the page). *Why:* without
   JavaScript, a form reloads the whole page and restarts the music. Reloading
   only the iframe keeps the music playing.
5. **`unittest` instead of `pytest`.** *Why:* pytest isn't installed, and
   unittest comes with Python.
6. **Four modules:** `affirmations.py` (data), `music.py`, `pages.py`
   (HTML), `server.py` (web server). *Why:* each part can be read and tested on
   its own.
7. **`App.handle()` is kept separate from the networking code.** *Why:* tests
   can check every page without starting a real server.

## Running the program

8. **Port 8000** by default, changeable with `--port`.
9. **Only your own computer can connect.** The server listens on `127.0.0.1`,
   so other devices on your Wi-Fi can't reach it. *Why:* safety. Change it in
   `main()` in `server.py`.
10. **The browser opens automatically.** Turn it off with `--no-browser`.
11. **`--data-dir` option** to keep the data files somewhere else. The tests
    use it to avoid touching your real files.
12. **Quiet terminal.** I turned off the per-request log lines (`log_message`
    in `server.py`). *Cost:* there's less to look at when debugging.
13. **Range and HEAD request support** for the music file. *Why:* Safari won't
    play audio without it. (Not tested in a real Safari yet.)

## Music

14. **Python generates the music** instead of using a downloaded song. *Why:*
    it avoids copyright and outside files, and keeps everything in Python.
15. **The sound itself:** four slow chords (Cmaj7, Am7, Fmaj7, G6), 8 seconds
    each, with two soft chimes per chord. It makes a roughly 32-second loop,
    saved as a 1.4 MB WAV at 22,050 samples per second. Each chord fades in and
    out, so the loop has no click. *Why:* soft and repetitive enough to fade
    into the background.
16. **The music is built once** (`calm_music.wav`) and reused. Delete the file
    to rebuild it.
17. **No autoplay.** You press play. *Why:* browsers block sound that starts
    by itself, so autoplay wouldn't work reliably anyway.

## Look and feel

18. **The nature theme:** a dawn sky gradient, a slowly "breathing" sun, three
    layers of green hills with pine trees, and leaf emojis drifting down.
19. **Colors:** soft greens, cream and warm gold. **Font:** Georgia, a serif
    font already on your computer, so nothing is downloaded.
20. **Text on screen** is my wording: the subtitle, button labels ("Give me an
    affirmation" / "Another affirmation"), "How much did this one help?", and
    the success and error messages.
21. **The first screen** shows a gentle prompt, not an affirmation, until you
    press the button.

## Affirmations

22. **I wrote the 15 starting affirmations** (`DEFAULT_AFFIRMATIONS` in
    `affirmations.py`), several with nature images to match the theme.
23. **File format:** `affirmations.txt` has one affirmation per line, so you
    can also edit it by hand. Blank lines are ignored.
24. **File location:** the project folder. If the file already exists, it is
    never overwritten.
25. **Random choice with no repeats in a row.** Every affirmation is equally
    likely, and **ratings do not change how often one appears.**
26. **Cleanup of what you type:** extra spaces and line breaks are squeezed
    into one line, because each affirmation must fit on one line of the file.
27. **Empty and exact-duplicate entries are rejected** with a friendly message.
28. **300-character limit** on a new affirmation.
29. **No delete or edit button** in the page. You can edit the txt file
    directly.

## Ratings

30. **Ratings go in a separate file,** `ratings.json`, not the txt file.
    *Why:* the txt file stays a clean list you can read. JSON is a simple text
    format for storing data like lists and labels.
31. **Every rating is kept,** and the page shows the **average** to 1 decimal
    place. Rating the same one twice counts twice.
32. **Any affirmation can be rated,** including ones you wrote. The spec said
    "pre-made"; I extended it.
33. **Ratings are matched to the affirmation's exact text.** *Side effect:* if
    you edit an affirmation's wording in the txt file, its old ratings no
    longer show.
34. **A damaged `ratings.json` is treated as empty** so the app doesn't crash.
    *Side effect:* the next rating overwrites the damaged file, and any old
    ratings in it are lost.

## Safety and limits

35. **Your text is "escaped"** before it's shown. Characters like `<` become
    harmless text, so typed input can't break the page or inject code.
36. **Form submissions are capped at 10,000 bytes.**
37. **An invalid rating** (outside 1–5, or missing) gets an error message, with
    HTTP code 400 ("bad request").

## Git and extra files

38. **Not committed to git:** `affirmations.txt`, `ratings.json`,
    `calm_music.wav` (via `.gitignore`). *Why:* they're your personal data or
    can be rebuilt. *Side effect:* your own affirmations aren't backed up by
    git.
39. **Extra docs** you didn't ask for: `README.md` (how to run and test) and
    `HANDOFF.md` (notes for the next session). You did ask for HANDOFF.md, but
    after the fact.
40. **I committed automatically** after each change, as the parent CLAUDE.md
    says to.
