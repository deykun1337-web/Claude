"""Export a per-frame plan (24 fps) from a dialogue project's timeline for the Blender renderer.
Usage: python3 plan.py <project_dir> <set> <human> <out.json>"""
import json, math, os, sys

proj, SET, HUMAN, OUT = sys.argv[1:5]
OUT = os.path.abspath(OUT)
os.chdir(proj); sys.path.insert(0, os.getcwd())
import base
from timeline import VOICE_START, VOICE_END, SPK, DUR, line_at, shot_at
from render import G_EXPR, K_EXPR

FPS = 24
MOUTH = base.MOUTH  # 60 fps envelope
HX = {"neutral", "sad", "shock", "smug", "angry", "plead", "happy", "panic", "sweet"}


def mlevel(t):
    v = MOUTH[min(int(t * 60), len(MOUTH) - 1)]
    return 0 if v < 0.22 else (1 if v < 0.6 else 2)


def blink(t, off):
    return 1 if ((t + off) % 3.1) < 0.12 else 0


frames = []
for f in range(int(DUR * FPS)):
    t = f / FPS
    shot, i = shot_at(t)
    speaking = VOICE_START[i] <= t <= VOICE_END[i] + 0.08
    end = t > VOICE_END[-1] + 0.35
    st = VOICE_START[i] - 0.08
    push = min(1.0, max(0.0, (t - st) / 3.0)); push = push * push * (3 - 2 * push)
    hexpr = G_EXPR.get(i, "neutral") if SPK[i] != "n" else G_EXPR.get(i - 1, "neutral") if i > 0 and SPK[i - 1] != "n" else "neutral"
    hexpr = hexpr if hexpr in HX else "neutral"
    if end: hexpr = "happy"
    kexpr = K_EXPR.get(i, "neutral") if SPK[i] == "n" else "neutral"
    kexpr = {"neutral": "neutral", "happy": "happy", "smug": "smug", "wide": "wide"}.get(kexpr, "neutral")
    if end: kexpr = "happy"
    hm = mlevel(t) if (speaking and SPK[i] != "n") else 0
    km = mlevel(t) if (speaking and SPK[i] == "n") else 0
    arm = 0.0
    if hexpr in ("plead", "panic", "happy") and SPK[i] != "n":
        arm = min(1.0, max(0.0, (t - st) / 0.35))
    hop = 0.0
    if hexpr == "panic" and speaking: hop = abs(math.sin((t - st) * 9)) * 0.05
    frames.append({"t": round(t, 3), "shot": "wide" if shot not in ("girl", "nik") else shot, "push": round(push, 4),
                   "sway": [round(0.012 * math.sin(t * 0.9) + 0.006 * math.sin(t * 2.3), 4), round(0.008 * math.sin(t * 1.1), 4)],
                   "hop": round(hop, 4),
                   "h": {"expr": hexpr, "m": hm, "b": blink(t, 1.3) if hexpr != "happy" else 0, "arm": round(arm, 3)},
                   "k": {"expr": kexpr, "m": km, "b": blink(t, 0.2) if kexpr not in ("happy",) else 0}})
json.dump({"set": SET, "human": HUMAN, "fps": FPS, "dur": DUR, "frames": frames}, open(OUT, "w"))
print("plan", OUT, len(frames))
