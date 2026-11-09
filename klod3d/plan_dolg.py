"""Per-frame plan (24 fps) for the dialog sketch «Друг занял 5000». Usage: python3 plan_dolg.py <project> <out.json>"""
import json, os, sys
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


SHOTS = [(0, "r"), (S[0] + 2.7, "k"), (S[1] - 0.1, "kl"), (S[2] - 0.08, "rz"), (S[3] - 0.1, "ko"), (S[4] - 0.1, "rp"),
         (S[5] - 0.1, "kr"), (S[6] - 0.1, "two"), (S[7] - 0.1, "k"), (S[8] - 0.1, "r"), (S[9] - 0.1, "ko"), (S[9] + 1.6, "out")]
REX = {0: "sad", 1: "think", 2: "angry", 3: "think", 4: "smug", 5: "think", 6: "shock", 7: "happy", 8: "smug", 9: "happy"}
KEX = {0: "neutral", 1: "smug", 2: "wide", 3: "smug", 4: "neutral", 5: "smug", 6: "happy", 7: "smug", 8: "wide", 9: "happy"}
frames = []
for f in range(int(DUR * FPS)):
    t = f / FPS
    shot, st = [(n, ts) for ts, n in SHOTS if t >= ts][-1]
    i = line(t)
    phone = 1 if i in (4, 5, 6) or (i == 3 and t > E[3] - 0.3) else 0
    frames.append({"t": round(t, 3), "shot": shot, "bt": round(t - st, 3), "line": i, "phone": phone,
                   "gesture": 1 if i in (0, 2, 8) else 0, "jump": max(0, 1 - abs(t - (S[6] + 0.7)) * 3) if i == 6 else 0,
                   "khop": max(0, 1 - abs(t - (S[9] + 0.2)) * 4),
                   "shake": 1 if (S[2] <= t < S[2] + 0.4) or (S[6] + 0.5 <= t < S[6] + 1.0) else 0,
                   "r": {"expr": REX[i], "m": lvl(t, "p"), "b": 1 if (t % 3.1) < 0.12 else 0},
                   "k": {"expr": KEX[i], "m": lvl(t, "n"), "b": 1 if ((t + 0.4) % 3.4) < 0.12 else 0}})
json.dump({"dur": DUR, "fps": FPS, "S": S, "E": E, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames))
