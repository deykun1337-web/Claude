"""Per-frame plan (24 fps) for the blocky 3D «Майкл из Техаса», derived from the 2D version's cue sheet."""
import json, math, os, sys

proj = os.path.abspath(sys.argv[1]); OUT = os.path.abspath(sys.argv[2])
os.chdir(proj); sys.path.insert(0, proj)
import render as R

FPS = 24
UI = {"ui_verify", "ui_max", "passport", "passport2", "city", "ui_ok", "ui_block", "bank", "end"}
EXP = {"neutral", "sad", "shock", "smug", "angry", "panic", "happy", "cry"}


def lvl(v): return 0 if v < 0.22 else (1 if v < 0.6 else 2)


frames, starts, prev = [], {}, None
for f in range(int(R.DUR * FPS)):
    t = f / FPS
    c, t0 = R.cue_at(t)
    if c in UI: shot = "ui"
    elif c in ("klod", "klod_red"): shot = "k_close"
    elif c in ("close", "close_hat", "scan", "susp"): shot = "r_close"
    elif c == "mom": shot = "m_close"
    elif c == "room_mom": shot = "mom_wide"
    else: shot = "medium"
    key = (c, t0)
    if key != prev: starts[key] = t; prev = key
    push = min(1, (t - starts[key]) / 3.5); push = push * push * (3 - 2 * push)
    hat = c not in ("close", "room", "klod", "ui_verify", "ui_max", "passport", "passport2", "city")
    arms = 0.0
    if c in ("flag", "party"): arms = min(1, (t - t0) / 0.3)
    ex = R.rexpr(t); ex = ex if ex in EXP else "neutral"
    if c == "party" or (c == "flag"): ex = "happy"
    flag = 0.0
    if t >= R.S[10]: flag = min(1, (t - R.S[10]) / 0.25)
    red = c in ("susp", "room_red", "klod_red")
    frames.append({"t": round(t, 3), "cue": c, "cue_t": round(t0, 3), "shot": shot, "push": round(push, 4),
                   "sway": [round(0.01 * math.sin(t * 0.9), 4), round(0.006 * math.sin(t * 1.1), 4)],
                   "turn_cam": round(0.12 * math.sin((t - t0) * 2.2), 4) if c == "scan" else 0,
                   "r": {"expr": ex, "m": lvl(R.mth(t, "p")), "b": 1 if R.blink(t) else 0, "hat": hat, "arms": round(arms, 3),
                         "turn": round(18 * math.sin((t - t0) * 2.2), 2) if c == "scan" else 0},
                   "k": {"expr": "smug" if c == "klod_red" else "neutral", "m": lvl(R.mth(t, "n")), "b": 1 if R.blink(t, 0.4) else 0},
                   "m": {"vis": c in ("room_mom", "mom"), "m": lvl(R.mth(t, "g")), "b": 1 if R.blink(t, 1.1) else 0},
                   "flag": round(flag, 3), "red": red})
json.dump({"dur": R.DUR, "fps": FPS, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames), "3d frames", sum(1 for x in frames if x["shot"] != "ui"))
