"""Shared timeline: scene bounds, voice placement and event times (used by audio.py and render.py)."""
import json, os, re

W, H, FPS, DUR = 1080, 1920, 60, 18.0
NFRAMES = int(FPS * DUR)
BPM = 120
HERE = os.path.dirname(os.path.abspath(__file__))

# Scenes: (start, end, name)
SCENES = [(0.0, 3.8, "hook"), (3.8, 6.2, "future"), (6.2, 9.6, "bear"), (9.6, 13.6, "came"), (13.6, DUR, "skufych")]
TRANSITIONS = [3.8, 9.6]          # stripe wipes; the bear scene uses hard creepy cuts
CUTS = [6.2, 13.6]
VOICE_START = [0.1, 3.9, 6.9, 9.75, 11.2, 13.8, 17.0]

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
    "tear": 0.45, "medvedya": word_t(0, "медвед"), "tri": word_t(1, "три"), "budush": word_t(1, "будущ"),
    "bear_in": 6.35, "pomni": word_t(2, "помни"),
    "prishel": word_t(3, "пришёл"), "divan": word_t(4, "диван"), "pivo": word_t(4, "пиво"), "skufom": word_t(4, "скуф"),
    "skufych": word_t(5, "скуфыч"), "zapomni": word_t(6, "запомни"),
}
EV["clink"] = 15.35
EV["cta"] = 15.7
EV["stamp"] = 16.3
EV["loop"] = DUR - 0.45
