"""Pixel-art textures for the blocky 3D characters (Minecraft-like), generated with PIL."""
import os, random
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "tex")
os.makedirs(OUT, exist_ok=True)
SCALE = 16


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def jitter(c, rr, k=10):
    return tuple(max(0, min(255, v + rr.randint(-k, k))) for v in c)


class PX:
    def __init__(self, w, h, base, seed=1, noise=8):
        self.w, self.h = w, h
        self.rr = random.Random(seed)
        self.img = Image.new("RGB", (w, h))
        b = hexrgb(base)
        for y in range(h):
            for x in range(w):
                self.img.putpixel((x, y), jitter(b, self.rr, noise))

    def p(self, x, y, col, w=1, h=1, noise=6):
        c = hexrgb(col)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < self.w and 0 <= yy < self.h:
                    self.img.putpixel((xx, yy), jitter(c, self.rr, noise))

    def save(self, name):
        self.img.resize((self.w * SCALE, self.h * SCALE), Image.NEAREST).save(os.path.join(OUT, name + ".png"))


EXPRS = ["neutral", "sad", "shock", "smug", "angry", "plead", "happy", "panic", "sweet"]

# ---------------- girl ----------------
G = dict(skin="#F2C9A8", hair="#F0D58C", hair2="#D9B867", lash="#3A2A2A", iris="#4AA3DF", pupil="#1F3A5A",
         lip="#E2477A", lip2="#B8325C", blush="#F59AA8", brow="#C99A4A")


def girl_face(expr, m, b):
    t = PX(16, 16, G["skin"], 3)
    for r in range(4): t.p(0, r, G["hair"], 16)
    t.p(0, 4, G["hair"], 2); t.p(6, 4, G["hair"], 4); t.p(14, 4, G["hair"], 2); t.p(3, 3, G["hair2"], 3); t.p(11, 2, G["hair2"], 3)
    for r in range(4, 16): t.p(0, r, G["hair"], 2); t.p(14, r, G["hair"], 2)
    if expr == "angry":
        t.p(3, 5, G["brow"]); t.p(4, 6, G["brow"], 2); t.p(12, 5, G["brow"]); t.p(10, 6, G["brow"], 2)
    else:
        by = 5 if expr in ("shock", "panic", "plead") else 6
        t.p(3, by, G["brow"], 3); t.p(10, by, G["brow"], 3)
    for ex in (3, 9):
        if b or expr == "happy":
            if expr == "happy": t.p(ex + 1, 8, G["lash"], 2); t.p(ex, 9, G["lash"]); t.p(ex + 3, 9, G["lash"])
            else: t.p(ex, 9, G["lash"], 4)
            continue
        t.p(ex, 7, G["lash"], 4); t.p(2 if ex == 3 else 13, 7, G["lash"])
        tall = 3 if expr in ("shock", "panic") else 2
        t.p(ex, 8, "#FFFFFF", 4, tall); t.p(ex + 1, 8, G["iris"], 2, tall); t.p(ex + 1, 8 + tall - 1, G["pupil"])
        if expr in ("smug", "angry"): t.p(ex, 8, G["lash"], 4)
    t.p(2, 10, G["blush"], 2); t.p(12, 10, G["blush"], 2); t.p(7, 10, "#E0B08E", 2)
    if m >= 1:
        t.p(6, 12, G["lip"], 4); t.p(6, 13, "#5A1A2A", 4, m); t.p(6, 13 + m, G["lip"], 4)
    elif expr in ("sad", "panic", "plead"):
        t.p(7, 12, G["lip"], 2); t.p(6, 13, G["lip"]); t.p(9, 13, G["lip"])
    elif expr in ("happy", "smug", "sweet"):
        t.p(5, 12, G["lip"]); t.p(10, 12, G["lip"]); t.p(6, 13, G["lip"], 4)
    else:
        t.p(6, 12, G["lip"], 4); t.p(6, 13, G["lip2"], 4)
    return t


def girl_misc():
    h = PX(16, 16, G["hair"], 4, 12)
    for k in range(10): h.p(h.rr.randint(0, 15), h.rr.randint(0, 15), G["hair2"], 1, h.rr.randint(1, 4))
    h.save("girl_hair")
    s = PX(16, 16, "#F06AAE", 5); s.p(6, 0, "#FFC2DD", 4, 2); s.p(0, 9, "#D9559A", 16); s.save("girl_shirt")
    a = PX(16, 16, "#F06AAE", 6); a.save("girl_sleeve")
    sk = PX(16, 16, G["skin"], 7); sk.save("girl_skin")
    n = PX(16, 16, G["skin"], 8); n.p(0, 0, "#FF2E88", 16, 4); n.save("girl_hand")
    l = PX(16, 16, "#E8E0F0", 9); l.p(0, 13, "#FFFFFF", 16, 3); l.save("girl_legs")


# ---------------- guy ----------------
P = dict(skin="#C98B63", hair="#5A3A22", cap="#E0559A", cap2="#B83C7A", eye="#2B3A67", stub="#A8724F", mouth="#7A3A24")


def guy_face(expr, m, b):
    t = PX(16, 16, P["skin"], 13)
    t.p(0, 0, P["cap"], 16, 3); t.p(0, 3, P["cap2"], 16)
    t.p(0, 4, P["hair"], 3); t.p(13, 4, P["hair"], 3); t.p(0, 5, P["hair"], 1, 3); t.p(15, 5, P["hair"], 1, 3)
    if expr == "angry":
        t.p(3, 6, P["hair"]); t.p(4, 7, P["hair"], 2); t.p(12, 6, P["hair"]); t.p(10, 7, P["hair"], 2)
    else:
        by = 5 if expr in ("shock", "panic") else 6
        t.p(3, by, P["hair"], 3); t.p(10, by, P["hair"], 3)
    for ex in (3, 10):
        if b: t.p(ex, 9, "#3A2418", 3); continue
        if expr == "happy": t.p(ex, 9, "#3A2418", 3); t.p(ex + 1, 8, "#3A2418"); continue
        tall = 3 if expr in ("shock", "panic") else 2
        t.p(ex, 8, "#FFFFFF", 3, tall); t.p(ex + 1, 8, P["eye"], 1, tall)
        if expr == "smug": t.p(ex, 8, P["skin"], 3)
    t.p(7, 10, "#B07650", 2, 2)
    for sx, sy in ((3, 12), (5, 14), (10, 14), (12, 12), (4, 13), (11, 13), (7, 15), (9, 15), (2, 11), (13, 11)):
        t.p(sx, sy, P["stub"])
    if m >= 1:
        t.p(6, 12, "#5A2418", 4, m); t.p(6, 12, "#EDE3D8", 4)
    elif expr in ("happy", "smug"):
        t.p(5, 12, P["mouth"]); t.p(10, 12, P["mouth"]); t.p(6, 13, P["mouth"], 4)
    else:
        t.p(6, 13, P["mouth"], 4)
    return t


def guy_misc():
    c = PX(16, 16, P["cap"], 14, 10); c.save("guy_cap")
    h = PX(16, 16, P["hair"], 15); h.p(0, 0, P["cap"], 16, 4); h.save("guy_side")
    s = PX(16, 16, "#F2F2F2", 16, 5); s.p(6, 0, P["skin"], 4, 1); s.save("guy_shirt")
    a = PX(16, 16, P["skin"], 17); a.p(0, 0, "#F2F2F2", 16, 5); a.save("guy_arm")
    l = PX(16, 16, "#2B3F7A", 18); l.p(0, 13, "#1A1A1A", 16, 3); l.save("guy_legs")


# ---------------- Клод the boar ----------------
K = dict(body="#E5684B", dark="#B84A33", eye="#111111", spark="#FFE9D6", mane="#7A2F20", snout="#F49A82", nost="#6A2418")


def klod_face(expr, m, b):
    t = PX(16, 12, K["body"], 23, 10)
    # Claude sparkle (asterisk) on the forehead
    for x, y in ((7, 0), (8, 0), (7, 1), (8, 1), (6, 1), (9, 1), (7, 2), (8, 2), (5, 0), (10, 0), (5, 2), (10, 2)):
        t.p(x, y, K["spark"], noise=3)
    for ex in (3, 11):
        if b: t.p(ex, 5, K["eye"], 2); continue
        if expr == "happy": t.p(ex, 4, K["eye"], 2); t.p(ex - 1, 5, K["eye"]); t.p(ex + 2, 5, K["eye"]); continue
        if expr == "smug": t.p(ex, 4, K["eye"], 2, 2); continue
        if expr in ("wide", "shock"): t.p(ex, 2, K["eye"], 2, 4); continue
        t.p(ex, 3, K["eye"], 2, 3)
    if m >= 1:
        t.p(6, 10, "#3A0F0A", 4, m); t.p(7, 10 + m - 1, "#FF7A8A", 2)
    elif expr in ("happy", "smug"):
        t.p(5, 9, "#3A0F0A"); t.p(10, 9, "#3A0F0A"); t.p(6, 10, "#3A0F0A", 4)
    else:
        t.p(6, 10, "#3A0F0A", 4)
    return t


def klod_misc():
    b = PX(16, 16, K["body"], 24, 10); b.save("klod_side")
    top = PX(16, 16, K["body"], 25, 10)
    for k in range(9): top.p(top.rr.randint(2, 13), top.rr.randint(0, 6), K["mane"], 1, 2)
    top.save("klod_top")
    s = PX(16, 8, K["snout"], 26, 6); s.p(4, 3, K["nost"], 2, 3); s.p(10, 3, K["nost"], 2, 3); s.save("klod_snout")
    d = PX(16, 16, K["dark"], 27, 8); d.save("klod_dark")


# ---------------- sets ----------------
def city(name, seed, w=64, h=96, warm=True):
    rr = random.Random(seed)
    img = Image.new("RGB", (w, h), (10, 8, 30))
    d = ImageDraw.Draw(img)
    for k in range(14):
        bx = rr.randint(-4, w - 4); bw = rr.randint(6, 14); bh = rr.randint(30, 90)
        d.rectangle([bx, h - bh, bx + bw, h], fill=(18 + rr.randint(0, 10), 14, 40 + rr.randint(0, 20)))
        for wy in range(h - bh + 3, h - 2, 4):
            for wx in range(bx + 1, bx + bw - 1, 3):
                if rr.random() < 0.45:
                    col = rr.choice([(255, 214, 120), (255, 190, 90), (255, 240, 200), (140, 200, 255)] if warm else [(120, 170, 255), (80, 120, 220)])
                    img.putpixel((min(w - 1, wx), wy), col)
    img.resize((w * 8, h * 8), Image.NEAREST).save(os.path.join(OUT, name + ".png"))


def code_tex():
    rr = random.Random(5)
    lines = ["git push origin main", "Approved with comments", "npm run build", "release notes", "working... 4:12",
             "Triage inbox (12 new)", "Feature request #471", "Diff: 9 files, +312 -58", "passed 128 tests", "Reading 38 files",
             "Grouping into Added / Fixed", "merge conflict resolved", "deploy: staging -> prod"]
    img = Image.new("RGB", (1024, 1024), (6, 8, 20)); d = ImageDraw.Draw(img)
    from PIL import ImageFont
    f = ImageFont.truetype("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf", 34) if os.path.exists("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf") else ImageFont.load_default()
    for y in range(10, 1024, 46):
        x = rr.randint(10, 300)
        d.text((x, y), rr.choice(lines), fill=(150, 170, 230) if rr.random() < 0.8 else (230, 230, 255), font=f)
    img.save(os.path.join(OUT, "code.png"))


def floor(name, base, line, seed):
    t = PX(32, 32, base, seed, 6)
    for y in range(0, 32, 4): t.p(0, y, line, 32)
    t.save(name)


if __name__ == "__main__":
    for e in EXPRS:
        for m in (0, 1, 2):
            for b in (0, 1):
                girl_face(e, m, b).save(f"girl_face_{e}_{m}_{b}")
                guy_face(e, m, b).save(f"guy_face_{e}_{m}_{b}")
    for e in ("neutral", "happy", "smug", "wide"):
        for m in (0, 1, 2):
            for b in (0, 1):
                klod_face(e, m, b).save(f"klod_face_{e}_{m}_{b}")
    girl_misc(); guy_misc(); klod_misc()
    city("city", 1); city("city2", 2)
    code_tex()
    floor("floor_wood", "#4A2C24", "#3A2018", 31); floor("floor_blue", "#141A3A", "#0E1330", 32)
    print("textures:", len(os.listdir(OUT)))


# ---------------- Руслан (from the user's photo) ----------------
R = dict(skin="#E8BFA2", cap="#1C1F26", cap2="#2C303A", hair="#3A2A20", eye="#5A3A22", lid="#C99A80", tat="#5A505A",
         stub="#B08A74", mouth="#8A4A3E")


def ruslan_face(expr, m, b):
    t = PX(16, 16, R["skin"], 41, 6)
    t.p(0, 0, R["cap"], 16, 4, noise=4)
    t.p(4, 1, "#E8E8E8", 8, 1, noise=2)              # cap print
    t.p(6, 2, "#2D5BD1", 4, 1, noise=2)              # blue patch
    t.p(0, 4, R["cap2"], 16, noise=3)                 # brim shadow
    t.p(0, 5, R["hair"], 1, 2); t.p(15, 5, R["hair"], 1, 2)
    by = 5 if expr in ("shock",) else 6
    t.p(3, by, R["hair"], 3); t.p(10, by, R["hair"], 3)
    for ex in (3, 10):
        if b or expr == "sleep": t.p(ex, 8, "#3A2418", 3); continue
        if expr == "happy": t.p(ex, 8, "#3A2418", 3); t.p(ex + 1, 7, "#3A2418"); continue
        t.p(ex, 7, R["lid"], 3)                       # heavy upper lid
        t.p(ex, 8, "#F4EFE6", 3); t.p(ex + 1, 8, R["eye"])
        t.p(ex, 9, "#B89AA8", 3, 1, noise=3)          # under-eye
    for x, y in ((2, 10), (3, 11), (2, 12), (3, 13), (13, 10), (12, 11), (13, 12), (12, 13), (4, 12), (11, 12)):
        t.p(x, y, R["tat"], noise=4)                  # cheek tattoos
    t.p(7, 10, "#D6A88C", 2, 2)
    t.p(6, 12, R["stub"], 4, noise=4)                 # thin moustache
    for x, y in ((5, 14), (7, 15), (9, 15), (10, 14), (6, 15), (8, 14)): t.p(x, y, R["stub"])
    if m >= 1: t.p(6, 13, "#4A1414", 4, m)
    elif expr == "happy": t.p(5, 13, R["mouth"]); t.p(10, 13, R["mouth"]); t.p(6, 14, R["mouth"], 4)
    else: t.p(6, 13, R["mouth"], 4)
    return t


def ruslan_misc():
    s = PX(16, 16, R["skin"], 42); s.p(0, 0, R["cap"], 16, 5); s.save("ruslan_side")
    c = PX(16, 16, R["cap"], 43, 5); c.save("ruslan_cap")
    j = PX(16, 16, "#A8ADB6", 44, 14)
    for y in (2, 6, 10, 14): j.p(0, y, "#6E737C", 16, noise=6)
    for x, y in ((2, 4), (11, 8), (4, 12), (12, 3)): j.p(x, y, "#F2F4F7", 2, 1, noise=3)
    j.save("puffer_side")
    jf = PX(16, 16, "#A8ADB6", 45, 14)
    for y in (2, 6, 10, 14): jf.p(0, y, "#6E737C", 16, noise=6)
    jf.p(7, 0, "#16181D", 1, 16, noise=2); jf.p(8, 0, "#2A2D33", 1, 16, noise=2)
    jf.p(5, 0, "#3E424A", 6, 2, noise=3)
    for x, y in ((2, 4), (12, 8), (3, 12), (12, 3)): jf.p(x, y, "#F2F4F7", 2, 1, noise=3)
    jf.save("puffer_front")
    l = PX(16, 16, "#23252B", 46); l.p(0, 13, "#E8E8E8", 16, 3); l.save("ruslan_legs")
    a = PX(16, 16, "#A8ADB6", 47, 14); a.p(0, 12, R["skin"], 16, 4); a.save("ruslan_arm")


# ---------------- agents ----------------
AGENTS = {"blue": "#3E7BD6", "green": "#2FB37A", "yellow": "#F2C230", "purple": "#8E5BD0", "orange": "#F08A2C",
          "teal": "#25A6A0", "red": "#E0504A", "grey": "#6E737C", "pink": "#E46AA8"}


def agent_face(col, sleep):
    t = PX(16, 12, col, hash(col) % 100, 9)
    for ex in (4, 10):
        if sleep: t.p(ex, 6, "#111111", 2)
        else: t.p(ex, 4, "#111111", 2, 3)
    t.p(7, 9, "#111111", 2)
    return t


def agents_misc():
    for name, col in AGENTS.items():
        agent_face(col, False).save(f"agent_{name}")
        agent_face(col, True).save(f"agent_{name}_sleep")
        PX(16, 16, col, 60 + len(name), 9).save(f"agent_{name}_side")


if __name__ == "__main__":
    for e in ("neutral", "happy", "shock", "sleep"):
        for m in (0, 1, 2):
            for b in (0, 1):
                ruslan_face(e, m, b).save(f"ruslan_face_{e}_{m}_{b}")
    ruslan_misc(); agents_misc()
    city("night", 7)
    floor("floor_dark", "#4A3020", "#3A2418", 33)
    print("extra textures done")


# ---------------- «Майкл» extras ----------------
def ruslan_face2(expr, m, b):
    t = ruslan_face("neutral" if expr not in ("happy", "shock", "sleep") else expr, m, b)
    if b: return t
    if expr == "sad":
        t.p(3, 6, R["skin"], 3); t.p(10, 6, R["skin"], 3); t.p(3, 7, R["hair"], 1); t.p(4, 6, R["hair"], 2); t.p(12, 7, R["hair"]); t.p(10, 6, R["hair"], 2)
    elif expr == "angry":
        t.p(3, 6, R["skin"], 3); t.p(10, 6, R["skin"], 3); t.p(3, 5, R["hair"]); t.p(4, 6, R["hair"], 2); t.p(12, 5, R["hair"]); t.p(10, 6, R["hair"], 2)
    elif expr in ("panic", "cry"):
        for ex in (3, 10): t.p(ex, 7, "#F4EFE6", 3, 2); t.p(ex + 1, 7, R["eye"], 1, 2)
        t.p(3, 5, R["hair"], 3); t.p(10, 5, R["hair"], 3)
        if expr == "cry":
            for x in (3, 12): t.p(x, 10, "#7CC4FF", 1, 4, noise=3)
    elif expr == "smug":
        for ex in (3, 10): t.p(ex, 7, R["lid"], 3); t.p(ex, 8, R["lid"], 3); t.p(ex, 9, "#3A2418", 3)
    return t


M = dict(skin="#F0C9AC", hair="#8A4A24", hair2="#6E3A1C", lip="#C2455A")


def mom_face(angry, m, b):
    t = PX(16, 16, M["skin"], 51, 6)
    for r in range(4): t.p(0, r, M["hair"], 16, noise=14)
    for x in range(0, 16, 3): t.p(x, 4, M["hair2"], 2)
    t.p(0, 4, M["hair"], 2, 10); t.p(14, 4, M["hair"], 2, 10)
    if angry: t.p(3, 6, "#5A3018"); t.p(4, 7, "#5A3018", 2); t.p(12, 6, "#5A3018"); t.p(10, 7, "#5A3018", 2)
    else: t.p(3, 6, "#5A3018", 3); t.p(10, 6, "#5A3018", 3)
    for ex in (3, 10):
        if b: t.p(ex, 9, "#3A2418", 3); continue
        t.p(ex, 8, "#FFFFFF", 3, 2); t.p(ex + 1, 8, "#4A3020", 1, 2)
    t.p(2, 11, "#F28A8A", 2); t.p(12, 11, "#F28A8A", 2); t.p(7, 10, "#D9A588", 2)
    if m >= 1: t.p(6, 12, "#4A1414", 4, m + 1)
    else: t.p(6, 13, M["lip"], 4)
    return t


def misc_michael():
    h = PX(16, 16, M["hair"], 52, 16); h.save("mom_hair")
    bl = PX(16, 16, "#E58FA0", 53, 8); bl.p(5, 0, "#F7EFE8", 6, 3); bl.p(7, 5, "#E8B740", 2, 2); bl.save("mom_blouse")
    sk = PX(16, 16, "#5A4A6A", 54); sk.save("mom_skirt")
    # carpet: ornament
    c = PX(32, 44, "#7A1E22", 55, 8)
    for y in range(44): c.p(0, y, "#C9A04A", 2, noise=4); c.p(30, y, "#C9A04A", 2, noise=4)
    c.p(0, 0, "#C9A04A", 32, 2, noise=4); c.p(0, 42, "#C9A04A", 32, 2, noise=4)
    for cy in (9, 22, 35):
        for r, col in ((6, "#1F3B6B"), (4, "#C9A04A"), (2, "#E8D7B0")):
            for dy in range(-r, r + 1):
                w = r - abs(dy); c.p(16 - w * 2, cy + dy, col, w * 4 + 1, noise=4)
    for k in range(4, 30, 4): c.p(k, 4, "#C9A04A", 2, 2); c.p(k, 39, "#C9A04A", 2, 2)
    c.save("carpet")
    f = PX(38, 26, "#F2EFE8", 56, 4)
    for k in range(13):
        if k % 2 == 0: f.p(0, k * 2, "#B22234", 38, 2, noise=6)
    f.p(0, 0, "#3C3B6E", 16, 14, noise=6)
    for r in range(4):
        for cc in range(5): f.p(1 + cc * 3, 1 + r * 3, "#FFFFFF")
    f.save("usflag")
    hat = PX(16, 16, "#7A4E2A", 57, 10); hat.p(0, 11, "#2A1A10", 16, 3); hat.p(7, 11, "#E8B740", 2, 2); hat.save("hat")
    s66 = PX(16, 24, "#2C3A38", 58, 6)
    for x, y in ((3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (4, 6), (5, 6), (4, 9), (5, 9), (6, 10), (6, 11), (4, 12), (5, 12),
                 (9, 6), (9, 7), (9, 8), (9, 9), (9, 10), (9, 11), (9, 12), (10, 6), (11, 6), (10, 9), (11, 9), (12, 10), (12, 11), (10, 12), (11, 12)):
        s66.p(x, y, "#E8E2D2", noise=3)
    s66.save("sign66")
    lap = PX(16, 10, "#FF3B30", 59, 10); lap.p(2, 2, "#FFFFFF", 12, 1); lap.p(2, 4, "#FFC8C0", 9, 1); lap.save("laptop_red")


if __name__ == "__main__":
    for e in ("neutral", "sad", "shock", "smug", "angry", "panic", "happy", "cry", "sleep"):
        for m in (0, 1, 2):
            for b in (0, 1):
                ruslan_face2(e, m, b).save(f"ruslan_face_{e}_{m}_{b}")
    for a in (0, 1):
        for m in (0, 1, 2):
            for b in (0, 1):
                mom_face(a, m, b).save(f"mom_face_{a}_{m}_{b}")
    misc_michael()
    print("michael textures done")


def ruslan_face_hat(expr, m, b):
    """Same face without the printed cap (for the cowboy-hat shots)."""
    t = ruslan_face2(expr, m, b)
    t.p(0, 0, R["hair"], 16, 3, noise=8); t.p(0, 3, R["skin"], 16, 2, noise=6); t.p(0, 3, R["hair"], 2, 3); t.p(14, 3, R["hair"], 2, 3)
    return t


if __name__ == "__main__":
    for e in ("neutral", "sad", "shock", "smug", "angry", "panic", "happy", "cry", "sleep"):
        for m in (0, 1, 2):
            for b in (0, 1):
                ruslan_face_hat(e, m, b).save(f"ruslan_face_hat_{e}_{m}_{b}")
    print("hat faces done")
