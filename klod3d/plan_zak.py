"""Per-frame plan (24 fps) for «Вы уже закрываетесь?». Usage: python3 plan_zak.py <project> <out.json>"""
import json, os, sys
proj, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.chdir(proj); sys.path.insert(0, proj)
import base
from timeline import VOICE_START as S, VOICE_END as E, DUR, SPK, SLAM, UP, FR0, FR1
FPS = 24


def line(t): return max([k for k in range(len(S)) if t >= S[k] - 0.05] or [-1])


def lvl(t, spk):
    i = line(t)
    if i < 0 or not (SPK[i] == spk and S[i] <= t <= E[i] + 0.06): return 0
    v = base.MOUTH[min(int(t * 60), len(base.MOUTH) - 1)]
    return 0 if v < 0.22 else (1 if v < 0.6 else 2)


SHOTS = [(0, "est"), (S[0] - 0.08, "r"), (S[1] - 0.08, "k"), (E[1] + 0.02, "two"), (S[2] - 0.08, "r"), (S[3] - 0.55, "k"),
         (FR0, "fr"), (S[4] - 0.3, "two")]
frames = []
for f in range(int(DUR * FPS)):
    t = f / FPS
    shot, st = [(n, ts) for ts, n in SHOTS if t >= ts][-1]
    i = line(t)
    rex = "panic" if t < S[1] else ("shock" if t < S[2] else ("smug" if t < S[4] - 0.3 else "happy"))
    if FR0 <= t < S[4] - 0.3: rex = "shock"
    kex = "smug" if t < SLAM else ("wide" if t < FR0 else "happy")
    km = lvl(t, "n")
    if t >= S[4]: km = 2  # tongue out, happy dog
    frames.append({"t": round(t, 3), "shot": shot, "shot_t": round(st, 3), "line": i,
                   "r": {"expr": rex, "m": lvl(t, "p"), "b": 1 if (t % 3.1) < 0.12 else 0},
                   "k": {"expr": kex, "m": km, "b": 1 if ((t + 0.5) % 3.3) < 0.12 and t < FR0 else 0}})
json.dump({"dur": DUR, "fps": FPS, "S": S, "E": E, "slam": SLAM, "up": UP, "fr0": FR0, "fr1": FR1, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames))
