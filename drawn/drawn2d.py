"""Hand-drawn 2D style kit (in the spirit of @codil.ya: thick dark outlines, flat colours, warm sunset light,
paper grain, cosy detailed backgrounds) — with OUR heroes: Klod is ALWAYS a boar, Ruslan wears the pink DEYKUN cap.

All functions return SVG fragments on a 1080x1920 canvas.
  kitchen(t)                     — cosy kitchen at sunset (window with city, tiles, hood, shelf, lamp)
  room(t)                        — Ruslan's room (desk, monitor, posters, chair, window)
  ruslan(cx, cy, s, mouth, expr, blink, look, arm)   — drawn Ruslan v2
  klod(cx, cy, s, mouth, expr, blink, look, ear)     — drawn Klod boar (salmon, snout, tusks, Claude sparkle, ears)
  grade(svg_body)                — wraps a frame: warm light gradient, vignette; paper grain is added in PIL (paper()).
  bubble_caption(txt)            — small dark pill subtitle at the bottom (codil.ya-like)
Usage example: python3 drawn/drawn2d.py demo  → drawn/demo.png
"""
import math, random, sys
from html import escape

OUT = "#20160F"   # outline colour
LW = 7            # outline width


def P(d, fill, sw=LW, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{OUT}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def R(x, y, w, h, fill, rx=10, sw=LW):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{OUT}" stroke-width="{sw}"/>'


def C(x, y, r, fill, sw=LW):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{OUT}" stroke-width="{sw}"/>'


def E(x, y, rx, ry, fill, sw=LW, rot=0):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{OUT}" stroke-width="{sw}" transform="rotate({rot} {x} {y})"/>'


DEFS = '''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5B4B9A"/><stop offset="0.55" stop-color="#E77FA0"/><stop offset="1" stop-color="#FFC48A"/></linearGradient>
<linearGradient id="warm" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFB86B" stop-opacity="0.35"/><stop offset="0.6" stop-color="#FF7FA0" stop-opacity="0.08"/><stop offset="1" stop-color="#3A2A6A" stop-opacity="0.25"/></linearGradient>
<radialGradient id="vig" cx="0.5" cy="0.45" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#1A0F08" stop-opacity="0.55"/></radialGradient>
<radialGradient id="lamp" cx="0.5" cy="0" r="1"><stop offset="0" stop-color="#FFE3A8" stop-opacity="0.7"/><stop offset="1" stop-color="#FFE3A8" stop-opacity="0"/></radialGradient>
<linearGradient id="skinG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F6D3B8"/><stop offset="0.62" stop-color="#EBC3A5"/><stop offset="1" stop-color="#C9967A"/></linearGradient>
<linearGradient id="teeG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.6" stop-color="#EEE9E1"/><stop offset="1" stop-color="#C8C0B6"/></linearGradient>
<linearGradient id="capG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF7DB4"/><stop offset="1" stop-color="#D23F82"/></linearGradient>
<linearGradient id="jeansG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4D6EA3"/><stop offset="1" stop-color="#2F4670"/></linearGradient>
<linearGradient id="klodG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F58566"/><stop offset="0.55" stop-color="#E5684B"/><stop offset="1" stop-color="#B9472F"/></linearGradient>
<radialGradient id="snoutG" cx="0.4" cy="0.35" r="0.8"><stop offset="0" stop-color="#FFC2B0"/><stop offset="1" stop-color="#E88A72"/></radialGradient>
<radialGradient id="glowWin" cx="0.62" cy="0.3" r="0.55"><stop offset="0" stop-color="#FFB37A" stop-opacity="0.45"/><stop offset="1" stop-color="#FFB37A" stop-opacity="0"/></radialGradient>
<radialGradient id="glowMon" cx="0.3" cy="0.5" r="0.45"><stop offset="0" stop-color="#7FA8FF" stop-opacity="0.35"/><stop offset="1" stop-color="#7FA8FF" stop-opacity="0"/></radialGradient>
</defs>'''


def city_window(x, y, w, h, seed=3):
    rr = random.Random(seed); o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#sky)"/>']
    for k in range(9):
        bw = rr.randint(60, 120); bh = rr.randint(120, int(h * 0.75)); bx = x + rr.randint(-20, w - 40)
        o.append(f'<rect x="{bx}" y="{y + h - bh}" width="{bw}" height="{bh}" fill="#3B2F5E" opacity="0.9"/>')
        for wy in range(y + h - bh + 14, y + h - 10, 26):
            for wx in range(bx + 10, bx + bw - 12, 22):
                if rr.random() < 0.5: o.append(f'<rect x="{wx}" y="{wy}" width="10" height="13" fill="#FFD27A"/>')
    o.append(R(x, y, w, h, "none", 6, 10))
    o.append(f'<line x1="{x + w / 2}" y1="{y}" x2="{x + w / 2}" y2="{y + h}" stroke="{OUT}" stroke-width="9"/>')
    return "".join(o)


def kitchen(t):
    o = [f'<rect width="1080" height="1920" fill="#9FB4C9"/>']
    for gy in range(560, 1300, 70):            # tiles
        for gx in range(0, 1080, 70):
            o.append(f'<rect x="{gx + 3}" y="{gy + 3}" width="64" height="64" fill="#DCE6EE" stroke="#B9C7D4" stroke-width="3"/>')
    o.append(city_window(330, 420, 420, 520))
    o.append(P("M300,420 L780,420 L760,380 L320,380 Z", "#F3E6D8"))  # curtain rail
    for k in range(6): o.append(E(340 + k * 80, 395, 40, 22, "#FBD3DD", 5))
    o.append(R(760, 230, 260, 160, "#CFD6DD", 12)); o.append(P("M780,390 L1000,390 L960,470 L820,470 Z", "#B8C1CA"))  # hood
    o.append(R(40, 300, 240, 26, "#A9744A", 6))
    for k, c in enumerate(("#E86A4A", "#F2C14E", "#6BAF8A", "#5C7FD6")): o.append(R(60 + k * 55, 240, 38, 60, c, 8, 5))
    o.append(R(0, 1300, 1080, 620, "#7A4E35", 0, 0)); o.append(R(-10, 1290, 1100, 60, "#C99A6B", 4))  # counter
    o.append(R(80, 1200, 220, 110, "#E3E8EC", 14)); o.append(C(190, 1190, 30, "#D24C3A"))  # pot
    o.append(f'<rect width="1080" height="1920" fill="url(#lamp)" opacity="{0.55 + 0.05 * math.sin(t * 3):.2f}"/>')
    return "".join(o)


def room(t):
    o = [f'<rect width="1080" height="1920" fill="#4A5D8C"/>', city_window(620, 360, 360, 460, 7)]
    for k, (c, x) in enumerate((("#E86A4A", 80), ("#F2C14E", 260), ("#6BAF8A", 420))):
        o.append(R(x, 300 + (k % 2) * 40, 130, 170, c, 6, 6))
    o.append(R(0, 1250, 1080, 670, "#6B4A3A", 0, 0)); o.append(R(60, 1120, 640, 40, "#9C6B45", 6))  # desk
    o.append(R(140, 820, 420, 280, "#22262E", 14)); o.append(R(165, 845, 370, 230, "#3D6FD8", 6, 5))  # monitor
    for k in range(6): o.append(f'<rect x="185" y="{870 + k * 32}" width="{120 + (k * 53) % 180}" height="12" fill="#BFD3FF" opacity="0.8"/>')
    o.append(R(760, 1120, 70, 90, "#7FA36A", 10, 5)); o.append(P("M770,1120 q-30,-90 25,-120 q10,60 -10,120 M800,1120 q20,-100 60,-110 q-10,70 -45,110", "#5E9A54", 5))  # plant
    o.append(R(600, 1080, 80, 40, "#E9D9C2", 8, 5))   # mug
    o.append(f'<rect width="1080" height="1920" fill="url(#lamp)" opacity="0.4"/><rect width="1080" height="1920" fill="url(#glowWin)"/><rect width="1080" height="1920" fill="url(#glowMon)"/>')
    return "".join(o)


def eyes(x1, x2, y, r, look, blink, expr, iris="#3B2618"):
    o = []
    for x in (x1, x2):
        if blink:
            o.append(f'<path d="M{x - r},{y} Q{x},{y + r * 0.5} {x + r},{y}" fill="none" stroke="{OUT}" stroke-width="7" stroke-linecap="round"/>'); continue
        big = 1.25 if expr in ("shock", "panic") else 1
        o.append(E(x, y, r * big, r * 1.1 * big, "#FFFFFF", 6))
        o.append(C(x + look[0] * r * 0.35, y + look[1] * r * 0.3, r * 0.48, iris, 0))
        o.append(C(x + look[0] * r * 0.35 + r * 0.17, y + look[1] * r * 0.3 - r * 0.2, r * 0.15, "#FFFFFF", 0))
    return "".join(o)


def brows(x1, x2, y, w, expr):
    t = {"angry": (14, -8), "sad": (-12, 8), "shock": (-16, -16), "think": (6, -12), "smug": (2, -8)}.get(expr, (0, 0))
    o = []
    for side, x in ((-1, x1), (1, x2)):
        inner, outer = t
        a = (x - w, y + (outer if side == -1 else inner)); b = (x + w, y + (inner if side == -1 else outer))
        o.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{OUT}" stroke-width="10" stroke-linecap="round"/>')
    return "".join(o)


def mouth(x, y, m, expr, w=34):
    if m > 0.05:
        h = 12 + 34 * m; ww = w * (0.55 + 0.25 * m)
        o = E(x, y + h * 0.35, ww, h * 0.6, "#6E1E2A", 6)
        if m > 0.35: o += f'<ellipse cx="{x}" cy="{y + h * 0.65}" rx="{ww * 0.6}" ry="{h * 0.22}" fill="#E86A7A"/>'
        o += f'<rect x="{x - ww * 0.6}" y="{y + h * 0.35 - h * 0.6 + 4}" width="{ww * 1.2}" height="{max(5, h * 0.18)}" rx="3" fill="#FFFFFF" opacity="0.9"/>'
        return o
    if expr in ("happy", "smug"): return f'<path d="M{x - w},{y} Q{x},{y + 26} {x + w},{y}" fill="none" stroke="{OUT}" stroke-width="7" stroke-linecap="round"/>'
    if expr in ("sad", "angry"): return f'<path d="M{x - w},{y + 14} Q{x},{y - 8} {x + w},{y + 14}" fill="none" stroke="{OUT}" stroke-width="7" stroke-linecap="round"/>'
    return f'<line x1="{x - w * 0.7}" y1="{y + 4}" x2="{x + w * 0.7}" y2="{y + 4}" stroke="{OUT}" stroke-width="7" stroke-linecap="round"/>'


def ruslan(cx, cy, s=1.0, mouth_open=0.0, expr="neutral", blink=False, look=(0, 0), arm=0.0):
    """cx, cy = feet centre. ~ 900 px tall at s=1."""
    g = [f'<g transform="translate({cx},{cy}) scale({s})">']
    g.append(R(-110, -330, 90, 330, "#3C5A8C", 18)); g.append(R(20, -330, 90, 330, "#3C5A8C", 18))      # jeans
    g.append(E(-70, 0, 75, 28, "#F4F4F4")); g.append(E(70, 0, 75, 28, "#F4F4F4"))                      # sneakers
    g.append(P("M-170,-330 L-150,-650 Q0,-700 150,-650 L170,-330 Z", "#F7F4EE"))                     # tee
    g.append('<path d="M-60,-640 Q0,-560 60,-640" fill="none" stroke="#E2A93B" stroke-width="9" stroke-linecap="round"/>')                            # gold chain
    g.append(C(0, -575, 16, "#F2B53A", 5))
    a = math.radians(-70 * arm)
    g.append(f'<g transform="rotate({-15 - 60 * arm} 150 -630)">' + R(130, -640, 70, 300, "#F7F4EE", 30) + C(165, -330, 38, "#EBC3A5") + "</g>")
    g.append(f'<g transform="rotate(12 -150 -630)">' + R(-200, -640, 70, 300, "#F7F4EE", 30) + C(-165, -330, 38, "#EBC3A5") + "</g>")
    g.append(R(-38, -720, 76, 70, "#EBC3A5", 14))                                                       # neck
    g.append(E(0, -860, 175, 190, "#EBC3A5"))                                                           # head
    g.append(E(-170, -850, 30, 48, "#EBC3A5")); g.append(E(170, -850, 30, 48, "#EBC3A5"))             # ears
    g.append(P("M-178,-930 Q-170,-1080 0,-1085 Q170,-1080 178,-930 Z", "#F0569A"))                     # cap
    g.append(P("M-40,-940 Q100,-960 250,-925 Q120,-895 -40,-910 Z", "#E04A8C"))                        # brim
    g.append(f'<text x="-5" y="-990" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="44" fill="#FFFFFF">DEYKUN</text>')
    g.append(eyes(-70, 70, -860, 34, look, blink, expr)); g.append(brows(-70, 70, -915, 38, expr))
    g.append(E(-115, -800, 26, 16, "#F2A0A0", 0)); g.append(E(115, -800, 26, 16, "#F2A0A0", 0))      # blush
    g.append(P("M-6,-850 Q14,-800 -10,-795", "none", 7))                                               # nose
    g.append(mouth(0, -760, mouth_open, expr))
    g.append("</g>")
    return "".join(g)


def klod(cx, cy, s=1.0, mouth_open=0.0, expr="neutral", blink=False, look=(0, 0), ear=0.0):
    """Klod the boar, drawn: chunky salmon body, snout, tusks, ears, mane, Claude sparkle. cx,cy = feet centre."""
    body, dark, snout = "#E5684B", "#B84A33", "#F49A82"
    g = [f'<g transform="translate({cx},{cy}) scale({s})">']
    for x in (-150, -70, 70, 150): g.append(R(x - 28, -175, 56, 175, dark, 14))                         # legs
    g.append(P("M-230,-150 Q-250,-470 -60,-520 Q120,-560 230,-470 Q270,-300 230,-150 Z", body))      # body
    for k in range(7): g.append(P(f"M{-90 + k * 32},-515 l14,-40 l14,40", dark, 5))                     # mane
    for sx in (-1, 1): g.append(f'<g transform="rotate({sx * (10 + 18 * ear)} {sx * 150} -470)">' + P(f"M{sx * 120},-470 L{sx * 190},-560 L{sx * 205},-450 Z", dark) + "</g>")
    for k in range(8):                                                                                    # Claude sparkle
        a = k * math.pi / 4
        g.append(f'<line x1="{20 * math.cos(a)}" y1="{-430 + 20 * math.sin(a)}" x2="{48 * math.cos(a)}" y2="{-430 + 48 * math.sin(a)}" stroke="#FFE9D6" stroke-width="13" stroke-linecap="round"/>')
    g.append(eyes(-85, 85, -360, 30, look, blink, expr, "#111")); g.append(brows(-85, 85, -405, 32, expr))
    g.append(E(-150, -300, 26, 16, "#FF9AA2", 0)); g.append(E(150, -300, 26, 16, "#FF9AA2", 0))
    g.append(E(0, -265, 92, 62, snout)); g.append(E(-30, -265, 14, 20, "#6A2418", 0)); g.append(E(30, -265, 14, 20, "#6A2418", 0))
    for sx in (-1, 1): g.append(P(f"M{sx * 105},-225 q{sx * 18},-30 {sx * 4},-62", "#FFF6E6", 6))       # tusks
    g.append(mouth(0, -190, mouth_open, expr, 40))
    g.append("</g>")
    return "".join(g)


# ---------------- v2 "quality" heroes: cel shading, rim light, details (override the simple ones above) ----------------
def _shadow(d):
    return f'<path d="{d}" fill="#5A2E1E" opacity="0.18" stroke="none"/>'


def ruslan(cx, cy, s=1.0, mouth_open=0.0, expr="neutral", blink=False, look=(0, 0), arm=0.0):
    g = [f'<g transform="translate({cx},{cy}) scale({s})">']
    g.append(E(0, 8, 230, 30, "#000", 0) .replace('fill="#000"', 'fill="#000" opacity="0.25"'))                # ground shadow
    for x in (-62, 62):
        g.append(P(f"M{x - 48},-335 L{x - 44},-30 Q{x},-14 {x + 46},-30 L{x + 50},-335 Z", "url(#jeansG)"))
        g.append(f'<path d="M{x + 30},-300 L{x + 26},-60" stroke="#E8E8E8" stroke-width="7" opacity="0.8"/>')  # side stripe
        g.append(P(f"M{x - 70},-5 Q{x - 72},-40 {x - 30},-42 L{x + 50},-40 Q{x + 86},-30 {x + 80},-2 Z", "#F7F7F7"))
        g.append(f'<path d="M{x - 64},-12 L{x + 74},-12" stroke="#C9C9C9" stroke-width="6"/>')
    g.append(P("M-178,-320 L-160,-640 Q-90,-690 0,-692 Q90,-690 160,-640 L178,-320 Q0,-300 -178,-320 Z", "url(#teeG)"))
    g.append(_shadow("M70,-660 Q150,-640 160,-560 L172,-330 Q120,-322 80,-320 Q110,-480 70,-660 Z"))
    g.append('<path d="M-40,-470 Q-10,-455 20,-470 M-100,-400 Q-80,-390 -60,-400" stroke="#BDB4A8" stroke-width="5" fill="none"/>')  # folds
    for k in range(13):                                                                     # gold chain links
        a = -1.2 + k * 0.2; x = 70 * math.sin(a); y = -650 + 70 * (1 - math.cos(a)) * 1.2
        g.append(E(x, y, 9, 6, "#F2B53A", 3, rot=int(a * 57)))
    g.append(P("M-18,-555 L18,-555 L24,-520 L0,-505 L-24,-520 Z", "#F2B53A", 4))
    # arms
    g.append(f'<g transform="rotate({-12 - 75 * arm} 150 -625)">' + P("M128,-650 Q190,-650 196,-560 L190,-330 Q165,-312 140,-330 Z", "url(#teeG)")
             + C(166, -318, 40, "url(#skinG)") + "</g>")
    g.append('<g transform="rotate(10 -150 -625)">' + P("M-128,-650 Q-190,-650 -196,-560 L-190,-330 Q-165,-312 -140,-330 Z", "url(#teeG)")
             + C(-166, -318, 40, "url(#skinG)") + "</g>")
    g.append(P("M-42,-735 L42,-735 L46,-660 Q0,-645 -46,-660 Z", "url(#skinG)"))               # neck
    # head
    g.append(P("M-178,-880 Q-180,-700 -60,-668 Q0,-655 60,-668 Q180,-700 178,-880 Q170,-1010 0,-1015 Q-170,-1010 -178,-880 Z", "url(#skinG)"))
    g.append(_shadow("M100,-1000 Q178,-960 178,-880 Q180,-720 70,-672 Q150,-760 140,-880 Q140,-960 100,-1000 Z"))
    for sx in (-1, 1):
        g.append(P(f"M{sx * 170},-900 Q{sx * 222},-905 {sx * 214},-840 Q{sx * 208},-790 {sx * 172},-800 Z", "url(#skinG)"))
        g.append(f'<path d="M{sx * 188},-880 Q{sx * 205},-850 {sx * 188},-820" stroke="#B57E62" stroke-width="5" fill="none"/>')
    for k in range(5): g.append(P(f"M{-176 + k * 8},-935 l-14,{30 + k * 6} l22,-8 Z", "#4A3224", 3))  # sideburn tufts
    for k in range(5): g.append(P(f"M{176 - k * 8},-935 l14,{30 + k * 6} l-22,-8 Z", "#4A3224", 3))
    # cap
    g.append(P("M-186,-930 Q-182,-1098 0,-1105 Q182,-1098 186,-930 Q0,-955 -186,-930 Z", "url(#capG)"))
    g.append('<path d="M-150,-1040 Q-60,-1090 40,-1085" stroke="#FFC0DA" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.8"/>')  # highlight
    g.append(P("M-60,-948 Q110,-985 268,-930 Q150,-890 -60,-912 Z", "#E04A8C"))
    g.append(R(-110, -1035, 210, 60, "#FFFFFF", 14, 5))
    g.append('<text x="-5" y="-1002" text-anchor="middle" dominant-baseline="middle" font-family="Inter Display" font-weight="900" font-size="40" fill="#D23F82">DEYKUN</text>')
    # face
    g.append(eyes(-72, 72, -860, 36, look, blink, expr))
    if not blink and expr not in ("shock", "panic"):
        for x in (-72, 72): g.append(f'<path d="M{x - 40},-878 Q{x},-905 {x + 40},-878" fill="url(#skinG)" stroke="{OUT}" stroke-width="6"/>')  # upper lids
    g.append(brows(-72, 72, -925, 42, expr))
    g.append(E(-118, -795, 30, 17, "#F29A9A", 0).replace('fill="#F29A9A"', 'fill="#F29A9A" opacity="0.7"'))
    g.append(E(118, -795, 30, 17, "#F29A9A", 0).replace('fill="#F29A9A"', 'fill="#F29A9A" opacity="0.7"'))
    g.append(P("M-4,-860 Q22,-805 -14,-796 Q-24,-800 -20,-806", "none", 6))
    for k in range(18): g.append(C(-60 + (k * 23) % 120, -735 + (k * 7) % 30, 2.5, "#B88A70", 0))      # stubble
    g.append(mouth(0, -752, mouth_open, expr, 38))
    g.append('<path d="M-178,-880 Q-180,-700 -60,-668" stroke="#FFD9A8" stroke-width="6" fill="none" opacity="0.7"/>')   # warm rim light
    g.append("</g>")
    return "".join(g)


def klod(cx, cy, s=1.0, mouth_open=0.0, expr="neutral", blink=False, look=(0, 0), ear=0.0):
    dark = "#9E3B26"
    g = [f'<g transform="translate({cx},{cy}) scale({s})">']
    g.append(E(0, 6, 240, 28, "#000", 0).replace('fill="#000"', 'fill="#000" opacity="0.25"'))
    for x in (-150, -70, 70, 150):
        g.append(R(x - 30, -185, 60, 185, "#B9472F", 16)); g.append(R(x - 34, -24, 68, 26, "#5A2418", 10, 5))   # legs + hooves
    g.append(P("M-240,-150 Q-262,-480 -60,-530 Q130,-570 238,-478 Q285,-300 240,-150 Q0,-120 -240,-150 Z", "url(#klodG)"))
    g.append(_shadow("M120,-540 Q238,-478 260,-330 Q262,-200 240,-150 Q160,-136 110,-138 Q210,-300 120,-540 Z"))
    for k in range(9): g.append(P(f"M{-120 + k * 30},-528 q10,-50 22,-4", dark, 5))                       # mane tufts
    for k in range(14):                                                                                     # fur strokes
        x = -200 + (k * 67) % 380; y = -460 + (k * 41) % 260
        g.append(f'<path d="M{x},{y} q8,-10 16,0" stroke="#C8553A" stroke-width="5" fill="none"/>')
    for sx in (-1, 1):
        g.append(f'<g transform="rotate({sx * (8 + 18 * ear)} {sx * 150} -475)">' + P(f"M{sx * 118},-470 L{sx * 196},-575 L{sx * 214},-448 Z", "#C8553A")
                 + P(f"M{sx * 140},-478 L{sx * 192},-548 L{sx * 200},-468 Z", "#F49A82", 0) + "</g>")
    for k in range(8):
        a = k * math.pi / 4
        g.append(f'<line x1="{18 * math.cos(a)}" y1="{-432 + 18 * math.sin(a)}" x2="{50 * math.cos(a)}" y2="{-432 + 50 * math.sin(a)}" stroke="#FFF1E4" stroke-width="14" stroke-linecap="round"/>')
    g.append(eyes(-88, 88, -355, 32, look, blink, expr, "#141414")); g.append(brows(-88, 88, -405, 34, expr))
    g.append(E(-155, -292, 30, 17, "#FF9AA2", 0).replace('fill="#FF9AA2"', 'fill="#FF9AA2" opacity="0.7"'))
    g.append(E(155, -292, 30, 17, "#FF9AA2", 0).replace('fill="#FF9AA2"', 'fill="#FF9AA2" opacity="0.7"'))
    g.append(E(0, -262, 100, 66, "url(#snoutG)")); g.append(E(-34, -262, 15, 22, "#5A1C12", 0)); g.append(E(34, -262, 15, 22, "#5A1C12", 0))
    g.append('<path d="M-60,-300 Q-20,-318 20,-310" stroke="#FFE1D6" stroke-width="8" fill="none" opacity="0.8" stroke-linecap="round"/>')   # snout highlight
    for sx in (-1, 1): g.append(P(f"M{sx * 108},-222 q{sx * 22},-34 {sx * 4},-70 q{sx * -4},26 {sx * -16},48 Z", "#FFF6E6", 5))
    g.append(mouth(0, -185, mouth_open, expr, 44))
    g.append('<path d="M-240,-150 Q-262,-480 -60,-530" stroke="#FFD9A8" stroke-width="7" fill="none" opacity="0.6"/>')   # rim light
    g.append("</g>")
    return "".join(g)


def bubble_caption(txt, y=1700):
    w = 22 * len(txt) + 60
    return (f'<rect x="{540 - w / 2}" y="{y - 38}" width="{w}" height="76" rx="18" fill="#1B1B22" opacity="0.88"/>'
            f'<text x="540" y="{y + 2}" text-anchor="middle" dominant-baseline="middle" font-family="Inter" font-weight="600" font-size="40" fill="#FFFFFF">{escape(txt)}</text>')


def grade(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}{body}'
            f'<rect width="1080" height="1920" fill="url(#warm)"/><rect width="1080" height="1920" fill="url(#vig)"/></svg>')


def paper(img, seed=1, amount=10):
    """Paper grain + slight colour jitter (PIL Image in, out)."""
    import numpy as np
    from PIL import Image
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    rng = np.random.default_rng(seed); n = rng.normal(0, amount, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))


def pixelate(img, factor=6, colors=80):
    """HD pixel-art look (like @tony.shev.ai): downscale, limit palette, upscale with hard pixels."""
    from PIL import Image
    w, h = img.size
    small = img.convert("RGB").resize((w // factor, h // factor), Image.LANCZOS)
    small = small.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    return small.resize((w, h), Image.NEAREST)


def chat_pill(txt, x=1040, y=180, accent="#E8806A", avatar="К"):
    """Salmon chat-message pill with a tiny avatar (dialog captions at the top, as in the pixel-art references)."""
    w = 24 * len(txt) + 120
    return (f'<rect x="{x - w}" y="{y - 40}" width="{w}" height="80" rx="20" fill="{accent}" stroke="{OUT}" stroke-width="4"/>'
            f'<rect x="{x - w + 14}" y="{y - 22}" width="44" height="44" rx="10" fill="#FFFFFF"/>'
            f'<text x="{x - w + 36}" y="{y + 2}" text-anchor="middle" dominant-baseline="middle" font-family="Inter Display" font-weight="900" font-size="28" fill="{accent}">{escape(avatar)}</text>'
            f'<text x="{x - w + 74}" y="{y + 2}" dominant-baseline="middle" font-family="Inter" font-weight="600" font-size="38" fill="#FFFFFF">{escape(txt)}</text>')


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "pixel":
    import io, cairosvg
    from PIL import Image
    body = (room(0) + ruslan(420, 2350, 1.75, 0.55, "angry", look=(1, 0), arm=0.1) + klod(900, 1830, 0.75, 0.0, "smug", look=(-1, 0))
            + chat_pill("Опять списали 20 долларов!", avatar="Р", accent="#D9606A"))
    img = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=grade(body).encode())))
    pixelate(img).save("drawn/demo_pixel.png"); print("drawn/demo_pixel.png")

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "demo":
    import io, cairosvg
    from PIL import Image
    body = kitchen(0) + klod(820, 1640, 0.9, 0.0, "smug", look=(-1, 0)) + ruslan(330, 1720, 0.95, 0.6, "shock", look=(1, 0), arm=0.0) + bubble_caption("Клод, а где мои пельмени?!")
    img = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=grade(body).encode())))
    paper(img).save("drawn/demo.png"); print("drawn/demo.png")
