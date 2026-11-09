"""Per-frame plan (24 fps) for the listicle. Usage: python3 plan_spisok.py <project> <out.json>"""
import json, os, sys
proj, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.chdir(proj); sys.path.insert(0, proj)
import base
from timeline import VOICE_START as S, VOICE_END as E, DUR, SPK
FPS = 24
STEPS = [2, 5, 6, 8, 9]


def line(t): return max([k for k in range(len(S)) if t >= S[k] - 0.05] or [0])


def lvl(t, spk):
    i = line(t)
    if not (SPK[i] == spk and S[i] <= t <= E[i] + 0.06): return 0
    v = base.MOUTH[min(int(t * 60), len(base.MOUTH) - 1)]
    return 0 if v < 0.22 else (1 if v < 0.6 else 2)


SHOTS = [(0, "r"), (S[1] - 0.1, "k"), (S[2] - 0.1, "kpL"), (S[3] - 0.08, "rz"), (S[4] - 0.1, "kpR"), (S[5] - 0.1, "kpL"), (S[6] - 0.1, "kpR"),
         (S[7] - 0.08, "r"), (S[8] - 0.1, "kpL"), (S[9] - 0.1, "kpR"), (S[10] - 0.08, "rz"), (S[11] - 0.1, "ring"), (E[11] - 0.6, "out")]
REX = {0: "think", 3: "think", 7: "think", 10: "shock", 11: "happy"}
frames = []
for f in range(int(DUR * FPS)):
    t = f / FPS
    shot, st = [(n, ts) for ts, n in SHOTS if t >= ts][-1]
    i = line(t)
    step = max([n for n, li in enumerate(STEPS) if t >= S[li] - 0.05] or [-1])
    sbt = t - (S[STEPS[step]] - 0.05) if step >= 0 else 0
    v = base.MOUTH[min(int(t * 60), len(base.MOUTH) - 1)]
    frames.append({"t": round(t, 3), "shot": shot, "bt": round(t - st, 3), "line": i, "phone": 0, "gesture": 1 if i in (0, 3, 7) else 0,
                   "jump": 0, "khop": max(0, 1 - abs(t - S[1] - 0.2) * 4) + max(0, 1 - abs(t - S[11] - 0.2) * 4), "shake": 1 if S[10] <= t < S[10] + 0.3 else 0,
                   "step": step, "sbt": round(sbt, 3), "ring": 1 if t >= S[11] - 0.1 else 0, "env": round(v if i == 8 else 0, 3),
                   "r": {"expr": REX.get(i, "happy"), "m": lvl(t, "p"), "b": 1 if (t % 3.1) < 0.12 else 0},
                   "k": {"expr": "happy" if i in (1, 11) else ("smug" if i in (4, 6) else "neutral"), "m": lvl(t, "n"), "b": 1 if ((t + 0.4) % 3.4) < 0.12 else 0}})
json.dump({"dur": DUR, "fps": FPS, "S": S, "E": E, "steps": STEPS, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames))
