"""Storage logic for daily affirmations.

Affirmations live in a plain text file, one per line.
Star ratings (1-5) live in a small JSON file next to it.
"""

import json
import random
from pathlib import Path

DEFAULT_AFFIRMATIONS = [
    "I am worthy of good things, just as I am.",
    "I trust myself to handle whatever today brings.",
    "My confidence grows a little every single day.",
    "I am allowed to take up space.",
    "Like a tree, I grow strong roots and reach for the light.",
    "I am proud of how far I have come.",
    "My voice matters and my ideas have value.",
    "I can do hard things.",
    "I deserve kindness, especially from myself.",
    "Every breath I take fills me with calm and courage.",
    "I am learning, and learning takes courage.",
    "Mistakes help me grow; they do not define me.",
    "I bring something unique to the world.",
    "Like the river, I keep moving forward.",
    "I believe in myself, and that is enough to begin.",
]

MIN_STARS = 1
MAX_STARS = 5


def ensure_file(path):
    """Create the affirmations file with the defaults if it does not exist."""
    path = Path(path)
    if not path.exists():
        path.write_text("\n".join(DEFAULT_AFFIRMATIONS) + "\n", encoding="utf-8")
    return path


def load_affirmations(path):
    """Return the list of affirmations in the file (blank lines skipped)."""
    path = ensure_file(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def clean_text(text):
    """Turn user input into a single tidy line, or '' if there is nothing."""
    return " ".join(str(text).split())


def add_affirmation(path, text):
    """Append a user-written affirmation. Returns True if it was added.

    Empty text and exact duplicates are ignored.
    """
    text = clean_text(text)
    if not text:
        return False
    existing = load_affirmations(path)
    if text in existing:
        return False
    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    return True


def pick_affirmation(affirmations, previous=None, rng=random):
    """Choose a random affirmation, avoiding repeating `previous` if possible."""
    if not affirmations:
        return None
    choices = [a for a in affirmations if a != previous] or affirmations
    return rng.choice(choices)


def load_ratings(path):
    """Return the ratings dict {affirmation: [stars, ...]}; {} if missing/broken."""
    path = Path(path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def rate_affirmation(path, text, stars):
    """Record a 1-5 star rating for an affirmation. Raises ValueError if invalid."""
    stars = int(stars)
    if not MIN_STARS <= stars <= MAX_STARS:
        raise ValueError(f"stars must be between {MIN_STARS} and {MAX_STARS}")
    text = clean_text(text)
    if not text:
        raise ValueError("cannot rate an empty affirmation")
    ratings = load_ratings(path)
    ratings.setdefault(text, []).append(stars)
    Path(path).write_text(json.dumps(ratings, indent=2), encoding="utf-8")
    return ratings[text]


def average_rating(ratings, text):
    """Average stars for `text`, rounded to 1 decimal, or None if unrated."""
    scores = ratings.get(text, [])
    if not scores:
        return None
    return round(sum(scores) / len(scores), 1)
