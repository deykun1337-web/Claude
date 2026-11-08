"""Blocky (voxel-style) characters and sets, drawn as SVG: girl, guy, and Клод the boar."""
import math, random
from base import star4, clamp, lerp, e_out

PX = 'shape-rendering="crispEdges"'


def shade(hex_col, k):
    """Lighten (k>0) or darken (k<0) a #rrggbb colour."""
    r, g, b = (int(hex_col[i:i + 2], 16) for i in (1, 3, 5))
    if k >= 0: r, g, b = (int(c + (255 - c) * k) for c in (r, g, b))
    else: r, g, b = (int(c * (1 + k)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def cube(x, y, w, h, d, front, side_dir=1, top=None, side=None, stroke="#00000040"):
    """Oblique cube: front face at (x,y,w,h); depth d goes up and to the side (side_dir = +1 right, -1 left)."""
    dx, dy = d * 0.55 * side_dir, -d * 0.38
    top = top or shade(front, 0.18); side = side or shade(front, -0.25)
    sx = x + w if side_dir > 0 else x
    return (f'<polygon points="{x:.1f},{y:.1f} {x + dx:.1f},{y + dy:.1f} {x + w + dx:.1f},{y + dy:.1f} {x + w:.1f},{y:.1f}" fill="{top}"/>'
            f'<polygon points="{sx:.1f},{y:.1f} {sx + dx:.1f},{y + dy:.1f} {sx + dx:.1f},{y + h + dy:.1f} {sx:.1f},{y + h:.1f}" fill="{side}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{front}"/>')


class Grid:
    """Pixel grid on a cube's front face."""

    def __init__(self, x, y, unit):
        self.x, self.y, self.u = x, y, unit
        self.out = []

    def px(self, gx, gy, col, gw=1, gh=1, op=1.0):
        u = self.u
        self.out.append(f'<rect x="{self.x + gx * u:.1f}" y="{self.y + gy * u:.1f}" width="{gw * u + 0.6:.1f}" height="{gh * u + 0.6:.1f}" fill="{col}" opacity="{op}" {PX}/>')

    def svg(self):
        return "".join(self.out)


# ---------------------------------------------------------------- girl
G_SKIN, G_HAIR, G_HAIR2, G_LASH = "#F2C9A8", "#F0D58C", "#D9B867", "#3A2A2A"
G_IRIS, G_PUPIL, G_LIP, G_LIP2, G_BLUSH = "#4AA3DF", "#1F3A5A", "#E2477A", "#B8325C", "#F59AA8"


def girl_head(x, y, size, t, mouth=0.0, expr="neutral", blink=False, side_dir=-1):
    u = size / 16
    o = [cube(x, y, size, size, size * 0.5, G_SKIN, side_dir, top=G_HAIR, side=G_HAIR2)]
    g = Grid(x, y, u)
    for r in range(4): g.px(0, r, G_HAIR, 16)
    g.px(0, 4, G_HAIR, 2); g.px(6, 4, G_HAIR, 4); g.px(14, 4, G_HAIR, 2); g.px(3, 3, G_HAIR2, 3); g.px(11, 2, G_HAIR2, 3)
    for r in range(4, 16): g.px(0, r, G_HAIR, 2); g.px(14, r, G_HAIR, 2)
    g.px(1, 6, G_HAIR2, 1, 8); g.px(14, 6, G_HAIR2, 1, 8)
    by = {"shock": 5, "panic": 5, "plead": 5}.get(expr, 6)
    if expr == "angry":
        g.px(3, 5, "#C99A4A"); g.px(4, 6, "#C99A4A", 2); g.px(12, 5, "#C99A4A"); g.px(10, 6, "#C99A4A", 2)
    else:
        g.px(3, by, "#C99A4A", 3); g.px(10, by, "#C99A4A", 3)
    for ex in (3, 9):
        if blink or expr == "happy":
            if expr == "happy":
                g.px(ex + 1, 8, G_LASH, 2); g.px(ex, 9, G_LASH); g.px(ex + 3, 9, G_LASH)
            else:
                g.px(ex, 9, G_LASH, 4)
            continue
        g.px(ex, 7, G_LASH, 4); g.px(ex - 1 if ex == 3 else ex + 4, 7, G_LASH)
        tall = 3 if expr in ("shock", "panic") else 2
        g.px(ex, 8, "#fff", 4, tall); g.px(ex + 1, 8, G_IRIS, 2, tall); g.px(ex + 1, 8 + tall - 1, G_PUPIL)
        g.px(ex + 2, 8, "#fff", 1, 1, 0.9)
        if expr in ("smug", "angry"): g.px(ex, 8, G_SKIN, 4); g.px(ex, 8, G_LASH, 4, 1, 0.9)
    g.px(2, 10, G_BLUSH, 2); g.px(12, 10, G_BLUSH, 2)
    g.px(7, 10, "#E0B08E", 2)
    if mouth > 0.25:
        g.px(6, 12, G_LIP, 4); g.px(6, 13, "#5A1A2A", 4, 1 + (mouth > 0.6)); g.px(6, 14 + (mouth > 0.6), G_LIP, 4)
    elif expr in ("sad", "panic", "plead"):
        g.px(7, 12, G_LIP, 2); g.px(6, 13, G_LIP, 1); g.px(9, 13, G_LIP, 1)
    elif expr in ("happy", "smug", "sweet", "touched"):
        g.px(5, 12, G_LIP, 1); g.px(10, 12, G_LIP, 1); g.px(6, 13, G_LIP, 4)
    else:
        g.px(6, 12, G_LIP, 4); g.px(6, 13, G_LIP2, 4)
    o.append(g.svg())
    return "".join(o)


def girl_body(x, y, w, h, side_dir=-1):
    return (cube(x, y, w, h, w * 0.35, "#F06AAE", side_dir) +
            f'<rect x="{x + w * 0.38:.1f}" y="{y:.1f}" width="{w * 0.24:.1f}" height="{h * 0.12:.1f}" fill="#FFC2DD" {PX}/>'
            f'<rect x="{x:.1f}" y="{y + h * 0.55:.1f}" width="{w:.1f}" height="{h * 0.06:.1f}" fill="#D9559A" {PX}/>')


def girl_arm(x, y, u, raised):
    """Blocky arm with pink sleeve and long pink nails."""
    yy = lerp(y + 14 * u, y, e_out(raised))
    return (cube(x, yy, 4 * u, 6 * u, 2 * u, "#F06AAE", -1) + cube(x, yy - 6 * u, 4 * u, 6 * u, 2 * u, G_SKIN, -1)
            + "".join(f'<rect x="{x + k * u:.1f}" y="{yy - 8 * u:.1f}" width="{u * 0.8:.1f}" height="{2 * u:.1f}" fill="#FF2E88" {PX}/>' for k in range(4)))


# ---------------------------------------------------------------- guy
P_SKIN, P_HAIR, P_CAP, P_CAP2 = "#C98B63", "#5A3A22", "#E0559A", "#B83C7A"


def guy_head(x, y, size, t, mouth=0.0, expr="neutral", blink=False, side_dir=-1):
    u = size / 16
    o = [cube(x, y, size, size, size * 0.5, P_SKIN, side_dir, top=P_CAP, side=P_HAIR)]
    g = Grid(x, y, u)
    g.px(0, 0, P_CAP, 16, 3); g.px(0, 3, P_CAP2, 16)
    g.px(0, 4, P_HAIR, 3); g.px(13, 4, P_HAIR, 3); g.px(0, 5, P_HAIR, 1, 3); g.px(15, 5, P_HAIR, 1, 3)
    if expr == "angry":
        g.px(3, 6, P_HAIR, 1); g.px(4, 7, P_HAIR, 2); g.px(12, 6, P_HAIR); g.px(10, 7, P_HAIR, 2)
    else:
        by = 5 if expr in ("shock", "panic") else 6
        g.px(3, by, P_HAIR, 3); g.px(10, by, P_HAIR, 3)
    for ex in (3, 10):
        if blink: g.px(ex, 9, "#3A2418", 3); continue
        tall = 3 if expr in ("shock", "panic") else 2
        g.px(ex, 8, "#fff", 3, tall); g.px(ex + 1, 8, "#2B3A67", 1, tall)
        if expr == "smug": g.px(ex, 8, P_SKIN, 3)
    g.px(7, 10, "#B07650", 2, 2)
    for sx, sy in ((3, 12), (5, 14), (10, 14), (12, 12), (4, 13), (11, 13), (7, 15), (9, 15), (2, 11), (13, 11)):
        g.px(sx, sy, "#A8724F", 1, 1, 0.8)
    if mouth > 0.25:
        g.px(6, 12, "#5A2418", 4, 1 + (mouth > 0.6)); g.px(6, 12, "#fff", 4, 1, 0.5)
    elif expr in ("happy", "smug"):
        g.px(5, 12, "#7A3A24"); g.px(10, 12, "#7A3A24"); g.px(6, 13, "#7A3A24", 4)
    else:
        g.px(6, 13, "#7A3A24", 4)
    o.append(g.svg())
    # cap brim sticking out over the face
    o.append(f'<polygon points="{x - u:.1f},{y + 4 * u:.1f} {x + 17 * u:.1f},{y + 4 * u:.1f} {x + 15 * u:.1f},{y + 5.3 * u:.1f} {x + u:.1f},{y + 5.3 * u:.1f}" fill="{P_CAP2}"/>'
             f'<rect x="{x:.1f}" y="{y + 5.3 * u:.1f}" width="{16 * u:.1f}" height="{0.7 * u:.1f}" fill="#00000030"/>')
    return "".join(o)


def guy_body(x, y, w, h, side_dir=-1):
    return (cube(x, y, w, h, w * 0.35, "#F2F2F2", side_dir) +
            f'<rect x="{x + w * 0.4:.1f}" y="{y:.1f}" width="{w * 0.2:.1f}" height="{h * 0.06:.1f}" fill="#C98B63" {PX}/>')


# ---------------------------------------------------------------- Клод the boar (salmon block like the original Клод)
K, K_TOP, K_SIDE, K_SNOUT = "#E5684B", "#F08466", "#B84A33", "#F49A82"


def klod(x, y, w, t, mouth=0.0, expr="neutral", blink=False, side_dir=1, legs=True, glint=0.0):
    """Front face w x 0.75w; origin = top-left of the front face. Legs hang below."""
    u = w / 16; h = 12 * u
    o = []
    if legs:
        for lx in (1.5, 4.5, 10.5, 13.5):
            o.append(cube(x + lx * u - u, y + h, 2.2 * u, 4 * u, 1.6 * u, K_SIDE, side_dir, top=K_SIDE, side=shade(K_SIDE, -0.25)))
    # ears and mane on top
    for ex in (1, 13):
        o.append(cube(x + ex * u + u * 0.6 * side_dir, y - 2.6 * u, 2 * u, 2.2 * u, 1.2 * u, K_SIDE, side_dir))
    o.append(cube(x, y, w, h, w * 0.55, K, side_dir, top=K_TOP, side=K_SIDE))
    for mx in (5, 7, 9, 11):
        o.append(f'<rect x="{x + mx * u + w * 0.12 * side_dir:.1f}" y="{y - w * 0.2 - 1.3 * u + (mx % 3) * 0.3 * u:.1f}" width="{u * 1.1:.1f}" height="{1.3 * u:.1f}" fill="#7A2F20" {PX}/>')
    g = Grid(x, y, u)
    # Claude sparkle on the forehead
    o_sp = star4(x + 8 * u, y + 1.6 * u, 1.3 * u, "#FFE9D6", rot=t * 50) + star4(x + 8 * u, y + 1.6 * u, 1.3 * u, "#FFE9D6", rot=t * 50 + 45)
    # eyes (black blocks like the original)
    for ex in (3, 11):
        if blink or expr == "happy":
            if expr == "happy":
                g.px(ex, 4, "#111"); g.px(ex + 1, 3, "#111"); g.px(ex + 2, 4, "#111") if False else None
                g.px(ex - 0.5, 4.5, "#111", 1, 1); g.px(ex + 1.5, 4.5, "#111", 1, 1)
            else:
                g.px(ex, 5, "#111", 2, 1)
            continue
        if expr == "smug":
            g.px(ex, 4, "#111", 2, 2)
        elif expr == "wide":
            g.px(ex - 0.3, 2.5, "#111", 2.6, 3.5)
        else:
            g.px(ex, 3, "#111", 2, 3)
        if glint > 0: g.px(ex + 1.2, 3.2, "#fff", 0.6, 0.6, glint)
    # tusks
    for tx in (3.6, 11.6):
        g.px(tx, 7.4, "#FFF6E6", 0.9, 2.2); g.px(tx + (0.5 if tx < 8 else -0.2), 6.6, "#FFF6E6", 0.7, 0.9)
    # mouth under the snout
    if mouth > 0.25:
        g.px(6, 10, "#3A0F0A", 4, 1 + (mouth > 0.6)); g.px(7, 10.6 + (mouth > 0.6) * 0.5, "#FF7A8A", 2, 0.6)
    elif expr in ("happy", "smug"):
        g.px(5.5, 10, "#3A0F0A"); g.px(9.5, 10, "#3A0F0A"); g.px(6.5, 10.6, "#3A0F0A", 3, 0.7)
    else:
        g.px(6, 10.4, "#3A0F0A", 4, 0.7)
    o.append(g.svg()); o.append(o_sp)
    # snout block sticking out
    sx, sy, sw, sh = x + 5 * u, y + 6 * u, 6 * u, 3.6 * u
    o.append(cube(sx - 0.6 * u * side_dir, sy + 0.4 * u, sw, sh, 1.8 * u, K_SNOUT, side_dir, top=shade(K_SNOUT, 0.15), side=shade(K_SNOUT, -0.2)))
    gs = Grid(sx - 0.6 * u * side_dir, sy + 0.4 * u, u)
    gs.px(1.2, 1.2, "#7A2F20", 1, 1.4); gs.px(3.8, 1.2, "#7A2F20", 1, 1.4)
    o.append(gs.svg())
    return "".join(o)


# ---------------------------------------------------------------- sets
def bokeh(seed, n, cols, area=(0, 0, 1080, 1100), rmin=20, rmax=70, op=0.35, t=0):
    rr = random.Random(seed); x0, y0, x1, y1 = area
    return "".join(f'<circle cx="{rr.uniform(x0, x1) + 6 * math.sin(t + k):.0f}" cy="{rr.uniform(y0, y1):.0f}" r="{rr.uniform(rmin, rmax):.0f}" fill="{rr.choice(cols)}" opacity="{op * rr.uniform(0.4, 1):.2f}"/>' for k in range(n))


def shelves(x, y, w, rows, seed, op=0.75):
    rr = random.Random(seed); out = [f'<g opacity="{op}">']
    for r in range(rows):
        yy = y + r * 150
        out.append(f'<rect x="{x}" y="{yy + 95}" width="{w}" height="16" fill="#F4E9F7" {PX}/>')
        for k in range(int(w / 46)):
            c = rr.choice(["#FF4F8B", "#C2185B", "#F06292", "#BA68C8", "#FF8A65", "#E91E63", "#F8BBD0", "#7E57C2"])
            bx = x + 12 + k * 46
            out.append(f'<rect x="{bx}" y="{yy + 40}" width="30" height="55" fill="{c}" {PX}/><rect x="{bx + 8}" y="{yy + 18}" width="14" height="24" fill="#2A1A22" {PX}/>')
    out.append("</g>")
    return "".join(out)


def salon(t, side=0, dim=0.3):
    if side == 0:
        s = ('<rect width="1080" height="1920" fill="url(#gSalon)"/>' + bokeh(1, 14, ["#FFD1F0", "#B388FF", "#FFF"], t=t * 0.5)
             + '<rect x="40" y="120" width="420" height="600" fill="#120A24" opacity="0.85"/>'
             + '<rect x="245" y="120" width="10" height="600" fill="#2A1A3A"/><rect x="40" y="415" width="420" height="10" fill="#2A1A3A"/>'
             + bokeh(2, 18, ["#FFE082", "#FFB74D", "#fff", "#7FDBFF"], (60, 140, 440, 700), 6, 18, 0.8, t)
             + shelves(560, 180, 520, 6, 3)
             + '<circle cx="300" cy="900" r="260" fill="url(#gNeon)"/>'
             + '<path transform="translate(230,880) scale(2.0)" d="M0 30 C -60 -10 -40 -60 0 -30 C 40 -60 60 -10 0 30 Z" fill="none" stroke="#FF8AD8" stroke-width="7"/>'
             + '<text x="380" y="910" font-family="DejaVu Sans" font-style="italic" font-size="80" fill="#FFB3E6">nails</text>')
    else:
        s = ('<rect width="1080" height="1920" fill="url(#gSalon2)"/>' + shelves(0, 150, 470, 7, 7)
             + '<rect x="560" y="140" width="480" height="780" fill="#0E0A1E" opacity="0.9"/>'
             + bokeh(5, 22, ["#FFE082", "#FFB74D", "#fff", "#FF2E88"], (580, 160, 1020, 900), 6, 20, 0.8, t)
             + '<circle cx="800" cy="200" r="300" fill="url(#gLamp)"/>' + bokeh(6, 10, ["#FFD1F0", "#B388FF"], t=t * 0.4))
    return s + f'<rect width="1080" height="1920" fill="#1A0A2A" opacity="{dim}"/>'


CODE = ["git push origin main", "Approved with comments", "npm run build", "release notes v2.4", "working... 4:12",
        "Triage inbox (12 new)", "Feature request #471", "Diff: 9 files, +312 -58", "passed ✓ 128 tests", "Reading 38 files",
        "Grouping into Added / Fixed", "merge conflict resolved", "deploy: staging → prod"]


def coderoom(t, side=0):
    rr = random.Random(11 + side); out = ['<rect width="1080" height="1920" fill="#070A18"/>']
    for k in range(60):
        x = rr.uniform(-100, 1000); y = (rr.uniform(0, 1920) - t * rr.uniform(4, 14)) % 1920
        txt = rr.choice(CODE).replace("✓", "").replace("→", "->")
        out.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="JetBrains Mono" font-size="{rr.choice([22, 26, 30])}" fill="#8FA3D9" opacity="{rr.uniform(0.12, 0.4):.2f}">{txt}</text>')
    for k in range(12):
        out.append(f'<circle cx="{rr.uniform(0, 1080):.0f}" cy="{rr.uniform(0, 1500):.0f}" r="{rr.uniform(5, 9):.0f}" fill="#E53935" opacity="{0.4 + 0.4 * abs(math.sin(t + k)):.2f}"/>')
    out.append('<rect x="0" y="1450" width="1080" height="470" fill="#0B1030"/>')
    for k in range(9): out.append(f'<rect x="{k * 130 - 20}" y="1450" width="110" height="470" fill="#121A48" opacity="0.6" {PX}/>')
    out.append('<ellipse cx="540" cy="1600" rx="520" ry="120" fill="#3D5AFE" opacity="0.18"/>')
    return "".join(out)
