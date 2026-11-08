"""Per-frame plan (24 fps) for «Агенты»: shots, Руслан, Клод and the growing crowd of agents."""
import json, math, os, re, sys

proj = os.path.abspath(sys.argv[1]); OUT = os.path.abspath(sys.argv[2])
os.chdir(proj); sys.path.insert(0, proj)
import base
from timeline import VOICE_START as S, VOICE_END as E, WORDS, DUR

FPS = 24


def wt(line, prefix):
    for w in WORDS:
        if w["line"] == line and re.sub(r"[^\w-]", "", w["w"]).lower().startswith(prefix): return w["t0"]
    return S[line]


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, a, b): return clamp((t - a) / (b - a))
def back(p, s=1.8):
    p -= 1; return 1 + p * p * ((s + 1) * p + s)


# id, colour, label, appear time, x, y, scale
A = [("mail", "blue", "почта", wt(4, "почт"), -0.9, -0.2, 1), ("call", "green", "звонки", wt(4, "звонк"), 0.05, -0.55, 1),
     ("wthr", "yellow", "погода", wt(4, "погод"), 0.95, -0.15, 1), ("fight", "purple", "разборки", wt(6, "разбор"), 0.0, 0.35, 1),
     ("track", "orange", "трекер", wt(7, "туалет"), 1.55, -0.85, 1), ("ctrl", "red", "контроль", wt(10, "ищет"), -1.55, -0.85, 1),
     ("law", "grey", "юрист", wt(11, "юрист"), -0.55, -1.15, 1), ("new1", "teal", "по найму", wt(13, "двоих"), 1.15, 0.65, 1),
     ("new2", "pink", "по найму", wt(13, "двоих") + 0.25, 1.65, 0.45, 1)]
SUB_T = wt(9, "свой")
for k, (aid, col, _, _, x, y, _) in enumerate(list(A[:5])):
    A.append((f"sub_{aid}", col, "", SUB_T + k * 0.15, x + 0.38, y - 0.2, 0.55))
SLEEPERS = {"call", "sub_mail", "sub_wthr", "fight"}
SLEEP_T = wt(10, "нашёл")
LEAVER, LEAVE_T, LEAVE_END = "wthr", S[12], S[12] + 2.6
DOOR = (-3.3, -0.4)
GATHER_T = S[15]


def shot_at(t):
    if t < S[2] - 0.05: return "r_close"
    if t < S[3] - 0.05: return "ui_installed"
    if t < wt(3, "агент") - 0.05: return "r_close"
    if t < S[5] - 0.05: return "room"
    if t < S[6] - 0.05: return "r_close"
    if t < S[8] - 0.05: return "room"
    if t < S[9] - 0.05: return "r_close"
    if t < S[14] - 0.05: return "room"
    if t < S[15] - 0.05: return "email"
    if t < S[16] - 0.05: return "room"
    if t < wt(16, "агент") - 0.05: return "r_close"
    if t < S[17] - 0.05: return "k_close"
    return "bed"


def mouth(t):
    v = base.MOUTH[min(int(t * 60), len(base.MOUTH) - 1)]
    return 0 if v < 0.22 else (1 if v < 0.6 else 2)


frames, starts = [], {}
prev = None
for f in range(int(DUR * FPS)):
    t = f / FPS
    shot = shot_at(t)
    if shot != prev: starts[shot] = t; prev = shot
    st = starts[shot]
    push = clamp((t - st) / 3.5); push = push * push * (3 - 2 * push)
    speaking = any(S[i] <= t <= E[i] + 0.06 for i in range(len(S)))
    m = mouth(t) if speaking else 0
    ag = []
    for aid, col, lab, t0, x, y, sc in A:
        if t < t0: continue
        s = sc * clamp(back(prog(t, t0, t0 + 0.35)), 0, 1.3)
        z = abs(math.sin((t + hash(aid) % 7) * 6)) * 0.06 * sc
        sleep = aid in SLEEPERS and t >= SLEEP_T
        rot = 0.0
        if sleep: z = 0; rot = 12
        ax, ay = x, y
        if aid == LEAVER and t >= LEAVE_T:
            p = prog(t, LEAVE_T + 0.4, LEAVE_END)
            ax, ay = x + (DOOR[0] - x) * p, y + (DOOR[1] - y) * p
            rot = math.degrees(math.atan2(DOOR[1] - y, DOOR[0] - x)) + 90
            if t > LEAVE_END: continue
        if t >= GATHER_T and not sleep and aid != LEAVER:  # crowd the desk: «не лезь»
            p = clamp((t - GATHER_T) / 0.8)
            ax, ay = ax + (1.6 + 0.35 * math.cos(hash(aid) % 10) - ax) * p, ay + (0.9 + 0.3 * math.sin(hash(aid) % 10) - ay) * p
        ag.append({"id": aid, "col": col, "lab": lab if t < SLEEP_T or not sleep else lab, "s": round(s, 3), "x": round(ax, 3), "y": round(ay, 3),
                   "z": round(z, 3), "rot": round(rot, 1), "sleep": sleep})
    frames.append({"t": round(t, 3), "shot": shot, "push": round(push, 4),
                   "sway": [round(0.01 * math.sin(t * 0.9), 4), round(0.006 * math.sin(t * 1.1), 4)],
                   "r": {"m": m if shot == "r_close" else 0, "b": 1 if (t % 3.2) < 0.12 else 0, "pose": "lie" if shot == "bed" else "stand"},
                   "k": {"m": m if shot == "k_close" else 0, "b": 1 if ((t + 1.1) % 3.4) < 0.12 else 0, "cap": shot == "k_close"},
                   "agents": ag})
json.dump({"dur": DUR, "fps": FPS, "frames": frames,
           "cues": {"hook_end": S[1], "prod": wt(7, "продуктив"), "mins": [wt(8, "восем"), wt(8, "двенад"), wt(8, "тридц")],
                    "council": wt(9, "решил"), "sleep": SLEEP_T, "law": wt(11, "юрист"), "bye": LEAVE_T + 0.3, "hire": wt(13, "двоих"),
                    "nolez": wt(13, "лез"), "email": S[14], "email_stop": S[15], "gather": GATHER_T, "reveal": wt(16, "агент"),
                    "need": wt(3, "агент")}}, open(OUT, "w"))
print("plan", OUT, len(frames))
