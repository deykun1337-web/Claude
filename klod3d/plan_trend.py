"""Per-frame plans (24 fps) for the trend shorts. Usage: python3 plan_trend.py <project_dir> <musya|telefon> <out.json>"""
import json, math, os, sys

proj, KIND, OUT = os.path.abspath(sys.argv[1]), sys.argv[2], os.path.abspath(sys.argv[3])
os.chdir(proj); sys.path.insert(0, proj)
import base
from timeline import VOICE_START as S, VOICE_END as E, DUR, SPK

FPS = 24


def lvl(t, spk):
    i = max([k for k in range(len(S)) if t >= S[k] - 0.05] or [0])
    if not (SPK[i] == spk and S[i] <= t <= E[i] + 0.06): return 0
    v = base.MOUTH[min(int(t * 60), len(base.MOUTH) - 1)]
    return 0 if v < 0.22 else (1 if v < 0.6 else 2)


def line(t):
    return max([k for k in range(len(S)) if t >= S[k] - 0.05] or [0])


def blink(t, o=0): return 1 if ((t + o) % 3.2) < 0.12 else 0


def shot_musya(t):
    i = line(t)
    if i == 0: return ("r_close", "poster") if t < E[0] + 0.1 else ("ui", "call")
    if i == 1: return ("ui", "call")
    return {2: ("r_close", ""), 3: ("swamp", "meme"), 4: ("r_close", ""), 5: ("swamp_wide", ""), 6: ("r_close", ""), 7: ("swamp", "voz")}[i]


def shot_telefon(t):
    i = line(t)
    if i in (0, 3, 5, 7): return ("k_desk", {0: "clock", 3: "", 5: "n48", 7: ""}[i])
    if i == 1: return ("k_desk", "dance") if t < E[1] + 0.15 else ("bed", "buzz")
    if i in (2, 4): return ("bed_close", "")
    return ("bed", "drop")


frames, starts, prev = [], {}, None
for f in range(int(DUR * FPS)):
    t = f / FPS
    shot, tag = (shot_musya if KIND == "musya" else shot_telefon)(t)
    key = (shot, tag, line(t))
    if key != prev: starts[key] = t; prev = key
    push = min(1, (t - starts[key]) / 3.5); push = push * push * (3 - 2 * push)
    i = line(t)
    rm, km = lvl(t, "p"), lvl(t, "n")
    if KIND == "musya":
        ex = {0: "sad", 2: "shock", 4: "shock", 6: "angry"}.get(i, "neutral")
        r = {"expr": ex, "m": rm, "b": blink(t), "pose": "stand_phone" if i >= 2 else "stand"}
        k = {"expr": "neutral", "m": 0, "b": 0, "z0": 0.82}
        kt = {"expr": "smug" if i == 7 else "neutral", "m": km if i >= 3 else 0, "b": blink(t, 0.6), "phone": 1, "raise": 0, "z0": -0.12}
        buzz = 0
    else:
        ex = "sleep" if (i in (0, 1, 6, 7) or t < S[2]) else ("shock" if i == 4 else "sad")
        r = {"expr": ex, "m": rm, "b": blink(t), "pose": "lie_phone" if i in (2, 3, 4, 5) else "lie"}
        dance = i in (1, 7)
        k = {"expr": "smug" if i in (5, 7) else ("happy" if dance else "neutral"), "m": km, "b": blink(t, 0.4), "phone": 1, "piano": 1 if dance else 0,
             "bob": 1 if dance else 0, "z0": 0.82}
        kt = {"expr": "neutral", "m": 0, "b": 0, "phone": 0, "z0": -0.12}
        buzz = 1 if (i in (0, 1) or (i == 7)) else 0
    frames.append({"t": round(t, 3), "shot": shot, "tag": tag, "line": i, "push": round(push, 4),
                   "sway": [round(0.01 * math.sin(t * 0.9), 4), round(0.006 * math.sin(t * 1.1), 4)],
                   "r": r, "k": k, "kt": kt, "buzz": buzz})
json.dump({"dur": DUR, "fps": FPS, "kind": KIND, "S": S, "E": E, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames), "3d", sum(1 for x in frames if x["shot"] != "ui"))
