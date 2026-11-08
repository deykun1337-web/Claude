"""Per-frame plan (24 fps) for «Чёрная пятница». Usage: python3 plan_pyatnica.py <project> <out.json>"""
import json, math, os, sys
proj, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.chdir(proj); sys.path.insert(0, proj)
import base
from timeline import VOICE_START as S, VOICE_END as E, DUR, SPK
FPS = 24


def line(t): return max([k for k in range(len(S)) if t >= S[k] - 0.05] or [-1])


def lvl(t, spk):
    i = line(t)
    if i < 0 or not (SPK[i] == spk and S[i] <= t <= E[i] + 0.06): return 0
    v = base.MOUTH[min(int(t * 60), len(base.MOUTH) - 1)]
    return 0 if v < 0.22 else (1 if v < 0.6 else 2)


CH0, CH1 = E[2] + 0.1, S[3] - 0.1
SHOTS = [(0, "crane"), (S[0] - 0.05, "r_close"), (S[1] - 0.05, "k_close"), (S[2] - 0.05, "r_close"), (CH0, "charge"), (CH1, "in_wide"),
         (S[4] - 0.05, "in_k"), (S[5] - 0.05, "in_r"), (S[6] - 0.05, "in_k"), (E[6] + 0.15, "end")]
REX = {0: "angry", 1: "angry", 2: "angry", 3: "panic", 4: "shock", 5: "angry", 6: "sad"}
frames = []
for f in range(int(DUR * FPS)):
    t = f / FPS
    shot, st = [(n, ts) for ts, n in SHOTS if t >= ts][-1]
    push = min(1, (t - st) / (2.2 if shot == "crane" else 3.0)); push = push * push * (3 - 2 * push)
    i = line(t)
    charge = min(1, max(0, (t - CH0 - 0.35) / 1.3)) if CH0 <= t < CH1 else 0
    doors = min(1, max(0, (t - CH0) / 0.6)) if t >= CH0 else 0
    frames.append({"t": round(t, 3), "shot": shot, "shot_t": round(st, 3), "line": i, "push": round(push, 4),
                   "scene": "in" if shot.startswith("in") else "out",
                   "sway": [round(0.012 * math.sin(t * 0.9), 4), round(0.008 * math.sin(t * 1.3), 4)],
                   "bang": 1.0 if t < CH0 else 0.0, "charge": round(charge, 3), "doors": round(doors, 3), "solo": shot == "end",
                   "r": {"expr": REX.get(i, "angry"), "m": lvl(t, "p"), "b": 1 if (t % 3.2) < 0.12 else 0},
                   "k": {"expr": "smug" if i in (4, 6) else "neutral", "m": lvl(t, "n"), "b": 1 if ((t + 0.4) % 3.4) < 0.12 else 0}})
json.dump({"dur": DUR, "fps": FPS, "S": S, "E": E, "ch0": CH0, "ch1": CH1, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames))
