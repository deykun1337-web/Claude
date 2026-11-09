"""Per-frame plan (24 fps) for the explainer. Usage: python3 plan_kak.py <project> <out.json>"""
import json, os, sys
proj, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.chdir(proj); sys.path.insert(0, proj)
import base
from timeline import VOICE_START as S, VOICE_END as E, DUR
FPS = 24
frames = []
for f in range(int(DUR * FPS)):
    t = f / FPS
    beat = max([k for k in range(len(S)) if t >= S[k] - 0.12] or [0])
    v = base.MOUTH[min(int(t * 60), len(base.MOUTH) - 1)]
    talking = any(S[k] <= t <= E[k] + 0.05 for k in range(len(S)))
    m = 0 if (not talking or v < 0.22) else (1 if v < 0.6 else 2)
    frames.append({"t": round(t, 3), "beat": beat, "bt": round(t - (S[beat] - 0.12), 3), "env": round(v if talking else 0, 3),
                   "k": {"expr": "happy" if beat in (1, 8, 10) else "neutral", "m": m, "b": 1 if ((t + 0.4) % 3.3) < 0.12 else 0}})
json.dump({"dur": DUR, "fps": FPS, "S": S, "E": E, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames))
