"""Shared timeline: scene bounds, voice placement and event times (used by audio.py and render.py)."""
import json, os, re

W, H, FPS, DUR = 1080, 1920, 60, 18.0
NFRAMES = int(FPS * DUR)
BPM = 120
HERE = os.path.dirname(os.path.abspath(__file__))

_voice = json.load(open(os.path.join(HERE, "build", "voice_tight.json")))


def _clean(w):
    return re.sub(r"[^\w-]", "", w).lower()


def word_t(line, prefix):
    """Start time of the first word in `line` starting with `prefix`."""
    for w in WORDS:
        if w["line"] == line and _clean(w["w"]).startswith(prefix):
            return w["t0"]
    raise KeyError((line, prefix))


# Dialogue: lines follow each other; longer beats before punchlines.
SPK = [l.get("spk", "n") for l in _voice]
PAUSE_BEFORE = {5: 0.55, 13: 0.6, 16: 0.45, 17: 0.25, 20: 0.6}
VOICE_START = []
_t = 0.25
for _i, _l in enumerate(_voice):
    _t += PAUSE_BEFORE.get(_i, 0.32) if _i else 0
    VOICE_START.append(round(_t, 3)); _t += _l["dur"]
VOICE_END = [VOICE_START[i] + l["dur"] for i, l in enumerate(_voice)]
DUR = round(VOICE_END[-1] + 1.6, 2)
NFRAMES = int(FPS * DUR)
WORDS = []
for li, line in enumerate(_voice):
    for w in line["words"]:
        WORDS.append({"line": li, "w": w["w"], "t0": VOICE_START[li] + w["t"], "t1": VOICE_START[li] + w["t"] + w["d"]})

# Shot list: which picture is on screen for each line
SHOT = {i: ("girl" if s == "g" else "nik") for i, s in enumerate(SPK)}
SHOT.update({11: "usb", 13: "photo", 14: "wide", 15: "paper", 20: "garage"})
TRANSITIONS = []


def shot_at(t):
    i = line_at(t)
    return SHOT[i], i


def line_at(t):
    i = 0
    for k, s in enumerate(VOICE_START):
        if t >= s - 0.08: i = k
    return i


EV = {"stamp": 0}
