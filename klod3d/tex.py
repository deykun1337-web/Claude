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
