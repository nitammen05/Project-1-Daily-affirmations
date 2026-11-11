"""HTML for the affirmations webpage, built as Python strings.

The main page holds the nature scene and the music player. The affirmation
card is a separate small page shown inside an <iframe>, so clicking its
buttons reloads only the card and the music keeps playing.
"""

from html import escape

STAR_LABELS = {1: "1 star", 2: "2 stars", 3: "3 stars", 4: "4 stars", 5: "5 stars"}

COLORS = """
  --sky-top: #cfe8e4; --sky-bottom: #f6ecd9; --sun: #ffe3a3;
  --hill-far: #a9cbb0; --hill-mid: #7fae8a; --hill-near: #5b8f6a;
  --card: rgba(255, 253, 247, 0.82); --ink: #2f4a3a; --soft-ink: #5e7a68;
  --accent: #6a9c78; --accent-dark: #4e7d5c; --star: #e9b949; --star-off: #cfd8cf;
"""

MAIN_CSS = """
:root {%s}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%%; }
body {
  font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif;
  color: var(--ink);
  background: linear-gradient(var(--sky-top), var(--sky-bottom) 70%%);
  min-height: 100vh; overflow-x: hidden; position: relative;
}
.sun { position: fixed; top: 8vh; right: 12vw; width: 120px; height: 120px;
  border-radius: 50%%; background: var(--sun);
  box-shadow: 0 0 80px 40px rgba(255, 227, 163, .55);
  animation: breathe 8s ease-in-out infinite; }
@keyframes breathe { 50%% { transform: scale(1.08); } }
.hills { position: fixed; left: 0; bottom: 0; width: 100%%; height: 45vh; z-index: 0; }
.leaf { position: fixed; top: -40px; font-size: 22px; opacity: .7; z-index: 1;
  animation: fall linear infinite; }
@keyframes fall {
  0%% { transform: translate(0, 0) rotate(0deg); }
  50%% { transform: translate(60px, 55vh) rotate(180deg); }
  100%% { transform: translate(-20px, 110vh) rotate(360deg); } }
main { position: relative; z-index: 2; max-width: 640px; margin: 0 auto;
  padding: 5vh 16px 4vh; text-align: center; }
h1 { font-weight: normal; font-size: 2.3rem; margin: 0 0 .3rem; letter-spacing: .5px; }
.subtitle { color: var(--soft-ink); margin: 0 0 1.4rem; font-style: italic; }
iframe { width: 100%%; height: 560px; border: 0; background: transparent; }
.music { margin-top: .8rem; background: var(--card); border-radius: 18px;
  padding: .7rem 1rem; display: inline-flex; align-items: center; gap: .6rem;
  box-shadow: 0 6px 20px rgba(47, 74, 58, .12); flex-wrap: wrap; justify-content: center; }
.music span { color: var(--soft-ink); font-size: .95rem; }
""" % COLORS

CARD_CSS = """
:root {%s}
* { box-sizing: border-box; }
body { margin: 0; padding: 8px; background: transparent;
  font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif; color: var(--ink); }
.card { background: var(--card); border-radius: 26px; padding: 1.8rem 1.4rem;
  box-shadow: 0 10px 30px rgba(47, 74, 58, .15); backdrop-filter: blur(6px); }
.affirmation { font-size: 1.55rem; line-height: 1.45; min-height: 4.5em;
  display: flex; align-items: center; justify-content: center; margin: 0 0 1rem;
  animation: fadein 1.2s ease; }
.affirmation.placeholder { color: var(--soft-ink); font-style: italic; font-size: 1.2rem; }
@keyframes fadein { from { opacity: 0; transform: translateY(6px); } }
button, .btn { font-family: inherit; cursor: pointer; border: 0; }
.next { background: var(--accent); color: #fff; font-size: 1.1rem; padding: .8rem 1.8rem;
  border-radius: 999px; box-shadow: 0 4px 12px rgba(78, 125, 92, .35); transition: .2s; }
.next:hover { background: var(--accent-dark); transform: translateY(-1px); }
.rate { margin: 1.2rem 0 .2rem; }
.rate p { margin: 0 0 .2rem; color: var(--soft-ink); font-size: .95rem; }
.stars { display: inline-flex; flex-direction: row-reverse; }
.stars button { background: none; font-size: 2rem; color: var(--star-off);
  padding: 0 .1rem; transition: color .15s; }
.stars button.on { color: var(--star); }
.stars:hover button { color: var(--star-off); }
.stars button:hover, .stars button:hover ~ button { color: var(--star); }
.avg { color: var(--soft-ink); font-size: .9rem; min-height: 1.2em; }
.message { color: var(--accent-dark); font-style: italic; min-height: 1.3em; margin: .4rem 0; }
.message.error { color: #a5573e; }
hr { border: 0; border-top: 1px dashed #c9d6c9; margin: 1.2rem 0; }
.add label { display: block; margin-bottom: .4rem; color: var(--soft-ink); }
.add .row { display: flex; gap: .5rem; }
.add input { flex: 1; min-width: 0; font-family: inherit; font-size: 1rem; padding: .6rem .9rem;
  border: 1px solid #c9d6c9; border-radius: 999px; background: #fffdf8; color: var(--ink); }
.add input:focus { outline: 2px solid var(--accent); border-color: transparent; }
.add button { background: #e7efe4; color: var(--accent-dark); padding: .6rem 1.1rem;
  border-radius: 999px; font-size: 1rem; }
.add button:hover { background: #d8e6d3; }
""" % COLORS

HILLS_SVG = """
<svg class="hills" viewBox="0 0 1440 400" preserveAspectRatio="none" aria-hidden="true">
  <path fill="var(--hill-far)" d="M0 220 C 240 140 420 200 640 170 C 880 135 1100 210 1440 150 L1440 400 L0 400Z"/>
  <path fill="var(--hill-mid)" d="M0 280 C 300 210 520 300 780 250 C 1020 205 1200 280 1440 240 L1440 400 L0 400Z"/>
  <g fill="var(--hill-near)">
    <path d="M0 330 C 260 290 560 350 860 320 C 1120 295 1300 340 1440 320 L1440 400 L0 400Z"/>
    <polygon points="140,320 165,250 190,320"/><polygon points="170,325 200,235 230,325"/>
    <polygon points="1180,315 1210,240 1240,315"/><polygon points="1225,320 1250,262 1275,320"/>
  </g>
</svg>
"""

LEAVES = "".join(
    f'<div class="leaf" style="left:{left}%;animation-duration:{dur}s;'
    f'animation-delay:{delay}s" aria-hidden="true">{leaf}</div>'
    for left, dur, delay, leaf in [
        (8, 22, 0, "&#127807;"), (27, 28, 6, "&#127811;"), (52, 25, 12, "&#127807;"),
        (73, 30, 3, "&#127811;"), (90, 26, 15, "&#127807;"),
    ]
)


def render_main_page():
    """The full page: scene, title, the card iframe and the music player."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daily Affirmations</title>
<style>{MAIN_CSS}</style>
</head>
<body>
<div class="sun" aria-hidden="true"></div>
{HILLS_SVG}
{LEAVES}
<main>
  <h1>Daily Affirmations</h1>
  <p class="subtitle">Take a slow breath. You are growing, one day at a time.</p>
  <iframe src="/card" title="Affirmation card"></iframe>
  <div class="music">
    <span>&#127925; Calming music</span>
    <audio controls loop preload="auto" src="/music.wav">Your browser cannot play audio.</audio>
  </div>
</main>
</body>
</html>"""


def render_stars(text, selected=None):
    """Five star buttons that each submit a rating for `text`."""
    buttons = []
    # row-reverse layout: write 5..1 so they display 1..5 left to right
    for n in range(5, 0, -1):
        on = " on" if selected and n <= selected else ""
        buttons.append(
            f'<button class="star{on}" type="submit" name="stars" value="{n}" '
            f'title="{STAR_LABELS[n]}" aria-label="{STAR_LABELS[n]}">&#9733;</button>'
        )
    return (
        '<form class="rate" method="post" action="/card/rate">'
        "<p>How much did this one help?</p>"
        f'<input type="hidden" name="text" value="{escape(text, quote=True)}">'
        f'<div class="stars">{"".join(buttons)}</div></form>'
    )


def render_card(affirmation=None, average=None, message="", error=False, selected=None):
    """The small page shown inside the iframe."""
    if affirmation:
        shown = f'<p class="affirmation">{escape(affirmation)}</p>'
        prev_field = (f'<input type="hidden" name="prev" '
                      f'value="{escape(affirmation, quote=True)}">')
        button_label = "Another affirmation"
        rating = render_stars(affirmation, selected)
        avg_text = (f"Average: {average:.1f} &#9733;" if average is not None
                    else "Not rated yet")
        rating += f'<div class="avg">{avg_text}</div>'
    else:
        shown = ('<p class="affirmation placeholder">'
                 "Press the button whenever you need a kind word.</p>")
        prev_field = ""
        button_label = "Give me an affirmation"
        rating = ""
    msg_class = "message error" if error else "message"
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>{CARD_CSS}</style></head>
<body>
<div class="card">
  {shown}
  <form method="get" action="/card"><input type="hidden" name="action" value="next">
  {prev_field}
  <button class="next" type="submit">{button_label}</button></form>
  {rating}
  <div class="{msg_class}" role="status">{escape(message)}</div>
  <hr>
  <form class="add" method="post" action="/card/add">
    <label for="new">Write your own affirmation</label>
    <div class="row">
      <input id="new" name="text" maxlength="300" placeholder="I am..." required>
      <button type="submit">Add</button>
    </div>
  </form>
</div>
</body>
</html>"""
