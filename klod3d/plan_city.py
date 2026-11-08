"""Plan (24 fps) for «Я в Москве» chase. Usage: python3 plan_city.py <project> <out.json>"""
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


CUTS = [(0, "moscow"), (E[2] + 0.1, "piter"), (E[4] + 0.1, "village"), (E[6] + 0.1, "home")]
POP = {"moscow": S[1] - 0.2, "piter": S[3] - 0.2, "village": S[5] - 0.2, "home": -1}
frames = []
for f in range(int(DUR * FPS)):
    t = f / FPS
    loc, lt = [(n, ts) for ts, n in CUTS if t >= ts][-1], 0
    loc_name, cut_t = loc[0], loc[1]
    i = line(t)
    p = min(1, max(0, (t - POP[loc_name]) / 0.3)) if POP[loc_name] >= 0 else 1
    pop = 1 + 0.25 * math.sin(p * math.pi) if 0 < p < 1 else p
    ex = {0: "happy", 2: "shock", 4: "panic", 6: "sad"}.get(i, "shock" if i in (1, 3, 5) else "sad")
    frames.append({"t": round(t, 3), "shot": "selfie", "loc": loc_name, "cut_t": round(cut_t, 3), "line": i,
                   "shake": 0.02 if (t - cut_t) < 0.25 else 0,
                   "r": {"expr": ex, "m": lvl(t, "p"), "b": 1 if (t % 3.1) < 0.12 else 0, "hop": 0.04 * abs(math.sin(t * 9)) if i == 0 else 0},
                   "k": {"expr": "smug", "m": lvl(t, "n"), "b": 1 if ((t + 0.7) % 3.4) < 0.12 else 0, "pop": round(pop, 3)}})
json.dump({"dur": DUR, "fps": FPS, "kind": "vmoskve", "S": S, "E": E, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames))
