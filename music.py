"""Generate a calm, loopable ambient music track as a WAV file.

A WAV file is just a header plus a long list of numbers ("samples") that
describe how the speaker should move. We compute those numbers with sine
waves: soft chord "pads" plus a few gentle chime notes.
"""

import array
import math
import random
import wave
from pathlib import Path

SAMPLE_RATE = 22050          # samples per second (enough for soft music)
CHORD_SECONDS = 8.0          # how long each chord lasts
MAX_AMPLITUDE = 32767        # biggest value a 16-bit sample can hold

# A soothing progression (frequencies in Hz): Cmaj7 -> Am7 -> Fmaj7 -> G6
CHORDS = [
    [130.81, 196.00, 246.94, 329.63],
    [110.00, 164.81, 196.00, 261.63],
    [87.31, 174.61, 220.00, 329.63],
    [98.00, 146.83, 246.94, 329.63],
]
# C major pentatonic notes for the chimes (no "wrong" notes possible)
CHIME_NOTES = [523.25, 587.33, 659.25, 783.99, 880.00]


def envelope(t, length, fade):
    """Volume (0..1) at time t in a note of `length` seconds with smooth fades."""
    if t < 0 or t > length:
        return 0.0
    if t < fade:
        return math.sin(0.5 * math.pi * t / fade) ** 2
    if t > length - fade:
        return math.sin(0.5 * math.pi * (length - t) / fade) ** 2
    return 1.0


def pad_sample(chord, t, length):
    """One sample of a soft chord pad at time t (seconds into the chord)."""
    vol = envelope(t, length, fade=length * 0.35)
    total = 0.0
    for i, freq in enumerate(chord):
        wobble = 1 + 0.002 * math.sin(2 * math.pi * 0.2 * t + i)  # slow vibrato
        total += math.sin(2 * math.pi * freq * wobble * t)
    return vol * total / len(chord)


def chime_sample(freq, t):
    """One sample of a bell-like chime, t seconds after it was struck."""
    if t < 0:
        return 0.0
    decay = math.exp(-t * 1.5)
    attack = min(1.0, t / 0.01)
    return attack * decay * (math.sin(2 * math.pi * freq * t)
                             + 0.3 * math.sin(2 * math.pi * freq * 2.01 * t))


def generate_samples(seconds_per_chord=CHORD_SECONDS, sample_rate=SAMPLE_RATE, seed=7):
    """Return an array of 16-bit samples for one full loop of the track."""
    rng = random.Random(seed)
    per_chord = int(seconds_per_chord * sample_rate)
    samples = array.array("h")
    for chord in CHORDS:
        # two chimes per chord at random gentle moments
        strikes = [(rng.uniform(1.0, seconds_per_chord - 3.0), rng.choice(CHIME_NOTES))
                   for _ in range(2)]
        for n in range(per_chord):
            t = n / sample_rate
            value = 0.55 * pad_sample(chord, t, seconds_per_chord)
            for start, freq in strikes:
                if 0 <= t - start < 3.0:
                    value += 0.12 * chime_sample(freq, t - start)
            value = max(-1.0, min(1.0, value))
            samples.append(int(value * MAX_AMPLITUDE * 0.8))
    return samples


def write_wav(path, samples, sample_rate=SAMPLE_RATE):
    """Write mono 16-bit samples to a WAV file."""
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(samples.tobytes())
    return Path(path)


def ensure_music(path):
    """Create the music file only if it does not exist yet."""
    path = Path(path)
    if not path.exists():
        write_wav(path, generate_samples())
    return path


if __name__ == "__main__":
    print("Wrote", ensure_music("calm_music.wav"))
