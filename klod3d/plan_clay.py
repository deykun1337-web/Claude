"""Per-frame plan (24 fps) for «Уровни редкости кабанов». Usage: python3 plan_clay.py <project> <out.json>"""
import json, math, os, sys
proj, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.chdir(proj); sys.path.insert(0, proj)
import base
from timeline import VOICE_START as S, VOICE_END as E, DUR, SPK, DROP, BANNER
FPS = 24


def line(t): return max([k for k in range(len(S)) if t >= S[k] - 0.05] or [-1])


def lvl(t, spk):
    i = line(t)
    if i < 0 or not (SPK[i] == spk and S[i] <= t <= E[i] + 0.06): return 0.0
    v = base.MOUTH[min(int(t * 60), len(base.MOUTH) - 1)]
    return round(min(1.0, max(0.0, (v - 0.15) / 0.7)), 3)


frames = []
for f in range(int(DUR * FPS)):
    t = (f - f % 2) / FPS  # on twos
    chew = 0.35 * max(0, math.sin(t * 9)) if t > DROP[0] + 0.5 else 0
    frames.append({"t": round(t, 3), "line": line(t),
                   "mouth": [round(chew, 3), 0.15, lvl(t, "n") if t > DROP[2] else 0.0, lvl(t, "p")],
                   "blink": [int(((t + k * 0.9) % 3.1) < 0.1) for k in range(4)]})
json.dump({"dur": DUR, "fps": FPS, "S": S, "E": E, "drop": DROP, "banner": BANNER, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames))
