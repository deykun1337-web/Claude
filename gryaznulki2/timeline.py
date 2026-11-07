"""Shared timeline: scene bounds, voice placement and event times (used by audio.py and render.py)."""
import json, os, re

W, H, FPS, DUR = 1080, 1920, 60, 20.0
NFRAMES = int(FPS * DUR)
BPM = 120
HERE = os.path.dirname(os.path.abspath(__file__))

# Scenes: (start, end, name)
SCENES = [(0.0, 3.6, "intro"), (3.6, 7.5, "alts"), (7.5, 11.3, "stat"),
          (11.3, 15.0, "versus"), (15.0, DUR, "finale")]
TRANSITIONS = [3.6, 7.5, 11.3, 15.0]
VOICE_START = [0.4, 3.8, 7.7, 11.5, 15.3]

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
    "hello": 0.4, "rise": 0.3, "claude": word_t(0, "клод"), "nikita": word_t(0, "никит"),
    "skuf": word_t(0, "скуф"), "skufych": word_t(0, "скуфыч"),
    "alts": word_t(1, "альтушк"), "eyeliner": word_t(1, "подвод"), "chains": word_t(1, "цеп"), "chaos": word_t(1, "хаос"),
    "skufs": word_t(2, "скуфы"), "choose": word_t(2, "выбира"), "gr": word_t(2, "грязнул"), "instead": word_t(2, "вместо"),
    "wife": word_t(3, "жена"), "trash": word_t(3, "вынеси"), "gr2": word_t(3, "грязнул"), "concert": word_t(3, "погнал"),
    "i": word_t(4, "я"), "pick": word_t(4, "выбрал"), "grz": word_t(4, "грязнул"), "zamesto": word_t(4, "за"),
    "zhinki": word_t(4, "жинки"), "you": word_t(4, "а"),
}
EV["cap"] = EV["skufych"] + 0.15
EV["cta"] = EV["you"] + 0.9
