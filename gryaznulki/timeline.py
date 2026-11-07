"""Shared timeline: scene bounds, voice placement and event times (used by audio.py and render.py)."""
import json, os, re

W, H, FPS, DUR = 1080, 1920, 30, 15.0
NFRAMES = int(FPS * DUR)
BPM = 120
HERE = os.path.dirname(os.path.abspath(__file__))

# Scenes: (start, end, name)
SCENES = [(0.0, 3.0, "intro"), (3.0, 6.3, "define"), (6.3, 9.0, "zoom"),
          (9.0, 11.8, "skuf"), (11.8, DUR, "outro")]
TRANSITIONS = [3.0, 6.3, 9.0, 11.8]
VOICE_START = [0.35, 3.15, 6.45, 9.1, 12.15]

_voice = json.load(open(os.path.join(HERE, "build", "voice_tight.json")))


def _clean(w):
    return re.sub(r"[^\w-]", "", w).lower()


# All words with absolute times: dict(line, w, t0, t1)
WORDS = []
for li, line in enumerate(_voice):
    for w in line["words"]:
        WORDS.append({"line": li, "w": w["w"], "t0": VOICE_START[li] + w["t"],
                      "t1": VOICE_START[li] + w["t"] + w["d"]})
VOICE_END = [VOICE_START[i] + l["dur"] for i, l in enumerate(_voice)]


def word_t(line, prefix):
    """Start time of the first word in `line` starting with `prefix`."""
    for w in WORDS:
        if w["line"] == line and _clean(w["w"]).startswith(prefix):
            return w["t0"]
    raise KeyError((line, prefix))


EV = {
    "title1": 0.15, "title2": 0.45, "land1": 0.55,
    "splash1": 3.35, "card": 3.5, "stamp": word_t(1, "дерзк"),
    "chip_z": 6.35, "shades": 6.8, "vibe": word_t(2, "альтушк"),
    "allowed": word_t(2, "мне"),
    "chip_s": 9.05, "cap": 9.4, "shout": word_t(3, "оторв"),
    "slipper": word_t(3, "тикток"),
    "land2": 12.1, "tozhe": word_t(4, "тоже"), "hru": word_t(4, "хрю"),
}
EV["hit"] = EV["slipper"] + 0.38
EV["shades2"] = EV["tozhe"] + 0.3
EV["end"] = EV["hru"] + 0.45
