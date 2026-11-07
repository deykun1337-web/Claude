"""Shared timeline: scene bounds, voice placement and event times (used by audio.py and render.py)."""
import json, os, re

W, H, FPS, DUR = 1080, 1920, 60, 24.5
NFRAMES = int(FPS * DUR)
BPM = 120
HERE = os.path.dirname(os.path.abspath(__file__))

# Scenes: (start, end, name)
SCENES = [(0.0, 4.4, "hook"), (4.4, 7.6, "cal"), (7.6, 11.5, "liver"), (11.5, 14.8, "snack"),
          (14.8, 19.0, "fix"), (19.0, 22.2, "myth"), (22.2, DUR, "save")]
TRANSITIONS = [4.4, 7.6, 11.5, 14.8, 19.0, 22.2]
VOICE_START = [0.05, 2.75, 4.5, 7.75, 11.6, 14.95, 19.15, 22.35]

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
    "ne": word_t(0, "не"), "pochti": word_t(0, "почти"), "nikita": word_t(1, "никит"),
    "pollitra": word_t(2, "пол"), "dvesti": word_t(2, "двест"), "ponchik": word_t(2, "пончик"),
    "pechen": word_t(3, "печен"), "alko": word_t(3, "алког"), "zhir": word_t(3, "жир"), "zapas": word_t(3, "запас"),
    "appetit": word_t(4, "аппет"), "chips": word_t(4, "чипс"), "suhar": word_t(4, "сухар"),
    "ispravit": word_t(5, "исправ"), "menshe": word_t(5, "меньше"), "zakus": word_t(5, "закус"),
    "shagov": word_t(5, "десят"), "belok": word_t(5, "белок"),
    "press": word_t(6, "пресс"), "bespol": word_t(6, "бесполез"), "vsego": word_t(6, "всего"),
    "sohrani": word_t(7, "сохран"), "pochemu": word_t(7, "почему"),
}
EV["open"] = EV["sohrani"] + 0.9   # beer can opens, belly grows back
EV["loop"] = DUR - 0.45            # crossfade into frame 0
