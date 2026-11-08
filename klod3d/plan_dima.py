"""Per-frame plan (24 fps) for the fundraising short about Дима (rendered with michael3d.py's room)."""
import json, math, os, sys

proj, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.chdir(proj); sys.path.insert(0, proj)
import base
from timeline import VOICE_START as S, VOICE_END as E, DUR, SPK

FPS = 24


def line(t): return max([k for k in range(len(S)) if t >= S[k] - 0.05] or [0])


def lvl(t, spk):
    i = line(t)
    if not (SPK[i] == spk and S[i] <= t <= E[i] + 0.06): return 0
    v = base.MOUTH[min(int(t * 60), len(base.MOUTH) - 1)]
    return 0 if v < 0.22 else (1 if v < 0.6 else 2)


SHOT = {0: "r_close", 1: "k_close", 2: "r_close", 3: "k_close", 4: "r_close", 5: "k_close", 6: "medium", 7: "k_close", 8: "r_close"}
EXPR = {0: "sad", 2: "neutral", 4: "sad", 6: "happy", 8: "smug"}
frames, starts, prev = [], {}, None
for f in range(int(DUR * FPS)):
    t = f / FPS
    i = line(t); shot = SHOT[i]
    if shot != prev: starts[shot] = t; prev = shot
    push = min(1, (t - starts[shot]) / 3.5); push = push * push * (3 - 2 * push)
    frames.append({"t": round(t, 3), "line": i, "cue": "", "cue_t": 0, "shot": shot, "push": round(push, 4),
                   "sway": [round(0.01 * math.sin(t * 0.9), 4), round(0.006 * math.sin(t * 1.1), 4)],
                   "r": {"expr": EXPR.get(i, "neutral"), "m": lvl(t, "p"), "b": 1 if (t % 3.2) < 0.12 else 0, "hat": False,
                         "arms": min(1, max(0, (t - S[6]) / 0.4)) if i == 6 else 0.0, "turn": 0},
                   "k": {"expr": "neutral", "m": lvl(t, "n"), "b": 1 if ((t + 0.4) % 3.4) < 0.12 else 0},
                   "m": {"vis": False, "m": 0, "b": 0}, "flag": 0.0, "red": False})
json.dump({"dur": DUR, "fps": FPS, "S": S, "E": E, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames))
