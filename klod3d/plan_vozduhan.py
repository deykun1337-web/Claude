"""Per-frame plan (24 fps) for the blocky 3D «Воздухан», derived from the 2D version (vozduhan/render.py)."""
import json, math, os, random, sys

proj = os.path.abspath(sys.argv[1]); OUT = os.path.abspath(sys.argv[2])
os.chdir(proj); sys.path.insert(0, proj)
import render as R

FPS = 24


def lvl(v): return 0 if v < 0.22 else (1 if v < 0.6 else 2)


def cue(t):
    c, t0 = R.CUES[0][1], 0
    for ts, name in R.CUES:
        if t >= ts: c, t0 = name, ts
    return c, t0


rr = random.Random(3)
PAP = [(rr.uniform(-1.5, 2.5), rr.uniform(-1.2, 1.2), rr.uniform(0.6, 2.6), rr.uniform(0.6, 1.4)) for _ in range(8)]
frames, starts, prev = [], {}, None
for f in range(int(R.DUR * FPS)):
    t = f / FPS
    c, t0 = cue(t)
    shot = {"close": "r_close", "scan": "r_close", "klod_note": "k_close", "klod_wind": "k_close", "klod_smug": "k_close",
            "trash": "medium", "mondays": "ui"}[c]
    key = (c, t0)
    if key != prev: starts[key] = t; prev = key
    push = min(1, (t - starts[key]) / 3.5); push = push * push * (3 - 2 * push)
    w = R.wind(t)
    pp = []
    for k, (x0, y0, z0, sp) in enumerate(PAP[:int(8 * w)]):
        x = (x0 + t * 2.2 * sp * w) % 5.0 - 2.2
        pp.append([round(x, 3), round(y0 - 0.6, 3), round(z0 + 0.25 * math.sin(t * 4 + k), 3), round(t * 300 * sp % 360, 1), round(t * 170 * sp % 360, 1)])
    ex = R.R_EXPR.get(R.line_now(t), "neutral")
    frames.append({"t": round(t, 3), "cue": c, "cue_t": round(t0, 3), "shot": shot, "push": round(push, 4),
                   "sway": [round(0.01 * math.sin(t * 0.9) + 0.02 * w * math.sin(t * 13), 4), round(0.006 * math.sin(t * 1.1), 4)],
                   "r": {"expr": ex if ex in ("neutral", "smug", "angry", "happy") else "neutral", "m": lvl(R.mth(t, "p")), "b": 1 if R.blink(t) else 0,
                         "hat": False, "arms": 0.0, "turn": round(8 * w * math.sin(t * 9), 2)},
                   "k": {"expr": "smug" if c == "klod_smug" else "neutral", "m": lvl(R.mth(t, "n")), "b": 1 if R.blink(t, 0.4) else 0},
                   "m": {"vis": False, "m": 0, "b": 0}, "flag": 0.0, "red": False,
                   "wind": round(w, 3), "papers": pp, "trash": c == "trash"})
json.dump({"dur": R.DUR, "fps": FPS, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames), "3d frames", sum(1 for x in frames if x["shot"] != "ui"))
