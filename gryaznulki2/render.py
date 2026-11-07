"""v2: «Никита Скуф Скуфыч» — 20 s vertical cartoon, rendered at 60 fps (blended to 30 fps for motion blur)."""
import math, os, random, sys
from multiprocessing import Pool
import cairosvg
import base
from base import (tw, fit, clamp, prog, lerp, e_out, e_in, e_back, e_bounce, popscale, damp, stext, pill,
                  burst, star4, heart, boar, shadow, is_blink, mouth_at, escape, INK, FONT)
from timeline import *

PINK, LIME, CYAN, YEL, DEEP = "#FF2E88", "#C6FF3D", "#22E4FF", "#FFD23F", "#120A22"
MONO = "JetBrains Mono ExtraBold"

DEFS = base.DEFS.replace("</defs>", '''
<radialGradient id="gGlowPink" cx="0.5" cy="0.45" r="0.7"><stop offset="0" stop-color="#FF2E88" stop-opacity="0.55"/><stop offset="1" stop-color="#FF2E88" stop-opacity="0"/></radialGradient>
<radialGradient id="gGlowCyan" cx="0.5" cy="0.5" r="0.7"><stop offset="0" stop-color="#22E4FF" stop-opacity="0.45"/><stop offset="1" stop-color="#22E4FF" stop-opacity="0"/></radialGradient>
<linearGradient id="gAlt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2B0B3F"/><stop offset="1" stop-color="#8A1260"/></linearGradient>
<linearGradient id="gWife" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5E6B7E"/><stop offset="1" stop-color="#3A4352"/></linearGradient>
<linearGradient id="gGr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF2E88"/><stop offset="1" stop-color="#7A1BD1"/></linearGradient>
<clipPath id="photo"><rect x="-150" y="-185" width="300" height="300"/></clipPath>
<clipPath id="left"><polygon points="0,0 620,0 460,1920 0,1920"/></clipPath>
<clipPath id="right"><polygon points="620,0 1080,0 1080,1920 460,1920"/></clipPath>
</defs>''')


# ---------- kinetic typography ----------
def ktext(x, y, txt, size, t, t0, fill="#fff", stagger=0.03, rot=0, anchor="middle", style="pop", sw=None, stroke=INK):
    """Per-letter animated text. Letters pop/drop in one by one from t0."""
    if t < t0: return ""
    sp = size * 0.22  # extra word spacing (strokes eat the gap)
    total = tw(txt, size) + sp * txt.count(" ")
    x0 = x - total / 2 if anchor == "middle" else x
    out = [f'<g transform="rotate({rot:.2f} {x:.1f} {y:.1f})">']
    for i, ch in enumerate(txt):
        if ch == " ": continue
        lx = x0 + tw(txt[:i], size) + sp * txt[:i].count(" ") + tw(ch, size) / 2
        p = prog(t, t0 + i * stagger, t0 + i * stagger + 0.32)
        if p <= 0: continue
        if style == "pop":
            sc = e_back(p, 2.6); dy = 0; r = (1 - e_out(p)) * -30
        else:  # drop
            sc = 1; dy = -(1 - e_bounce(p)) * size * 1.4; r = 0
        out.append(stext(lx, y + dy, ch, size, fill=fill, rot=r, sc=sc, sw=sw, stroke=stroke))
    out.append("</g>")
    return "".join(out)


def marker(x, y, w, h, t, t0, col, rot=-2):
    """Highlighter bar that swipes in from left."""
    p = e_out(prog(t, t0, t0 + 0.25))
    if p <= 0: return ""
    return f'<rect x="{x:.1f}" y="{y - h / 2:.1f}" width="{w * p:.1f}" height="{h:.1f}" rx="10" fill="{col}" transform="rotate({rot} {x} {y})"/>'


def sticker(cx, cy, txt, size, bg, fg, t, t0, rot):
    sc = popscale(t, t0, 0.3)
    if sc <= 0: return ""
    wob = rot + 3 * math.sin((t - t0) * 7)
    return pill(cx, cy, txt, size, bg, fg, sc=sc, rot=wob)


# ---------- backgrounds ----------
def halftone(t, col, op=0.18, step=54, drift=40):
    out = [f'<g fill="{col}" opacity="{op}">']
    off = (t * drift) % step
    for j in range(-1, int(1920 / step) + 2):
        for i in range(-1, int(1080 / step) + 2):
            x = i * step + (step / 2 if j % 2 else 0) - off; y = j * step + off * 0.6
            r = 4 + 9 * (0.5 + 0.5 * math.sin(x * 0.006 + y * 0.004 + t * 2))
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}"/>')
    out.append("</g>")
    return "".join(out)


def floaters(t, seed, cols, n=10):
    rr = random.Random(seed); out = []
    for k in range(n):
        x = rr.uniform(60, 1020); y0 = rr.uniform(0, 1920); sp = rr.uniform(40, 120); kind = rr.randint(0, 2)
        y = (y0 - t * sp) % 2000 - 40; c = rr.choice(cols); r = rr.uniform(18, 40); a = t * rr.uniform(40, 140)
        if kind == 0: out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="none" stroke="{c}" stroke-width="7" opacity="0.7"/>')
        elif kind == 1: out.append(star4(x, y, r, c, rot=a).replace("<polygon", '<polygon opacity="0.8"'))
        else: out.append(f'<path d="M {x - r:.0f} {y:.0f} q {r / 2:.0f} {-r:.0f} {r:.0f} 0 t {r:.0f} 0" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.7" transform="rotate({a:.0f} {x:.0f} {y:.0f})"/>')
    return "".join(out)


def bg_neon(t, base_col=DEEP, glow="gGlowPink"):
    return (f'<rect width="1080" height="1920" fill="{base_col}"/>' + halftone(t, "#fff", 0.06)
            + f'<circle cx="540" cy="900" r="{900 + 30 * base.beat(t):.0f}" fill="url(#{glow})"/>')


def checker(t, a="#1A0A2A", b="#2A0E3F", sz=120):
    out = [f'<rect width="1080" height="1920" fill="{a}"/>']
    off = (t * 60) % (2 * sz)
    for j in range(-2, 18):
        for i in range(-2, 11):
            if (i + j) % 2: out.append(f'<rect x="{i * sz + off - sz:.0f}" y="{j * sz + off * 0.5 - sz:.0f}" width="{sz}" height="{sz}" fill="{b}"/>')
    return "".join(out)


def ring(cx, cy, r, t, col, w=10, dash="40 30"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}" transform="rotate({t * 40:.1f} {cx} {cy})" opacity="0.8"/>'


# ---------- alt girl (fictional cartoon) ----------
VARIANTS = [("#141018", PINK, LIME, "#F7D9C4"), ("#3A1F6B", CYAN, "#FF7AB8", "#F3CDB6"), ("#EDEDF2", "#141018", CYAN, "#FADCC9")]


def altgirl(cx, cy, s, v, t, tilt=0.0, wink=False):
    hair, streak, _, skin = VARIANTS[v]
    blink = is_blink(t + v * 0.9)
    g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({tilt:.2f}) scale({s:.3f})">']
    g.append(f'<path d="M -108 -40 Q -112 -140 0 -142 Q 112 -140 108 -40 L 122 150 L -122 150 Z" fill="{hair}"/>')
    g.append('<rect x="-24" y="60" width="48" height="60" fill="#E2B49A"/>')
    g.append('<path d="M -160 200 Q -150 112 -40 104 L 40 104 Q 150 112 160 200 Z" fill="#111"/>')
    g.append('<path d="M -40 104 L 0 150 L 40 104" stroke="#2A2A2A" stroke-width="5" fill="none"/>')
    g.append('<rect x="-30" y="80" width="60" height="14" rx="4" fill="#111"/>')
    for k in range(5): g.append(f'<polygon points="{-24 + k * 12},80 {-19 + k * 12},70 {-14 + k * 12},80" fill="#C9CED6"/>')
    g.append('<circle cx="0" cy="100" r="8" fill="none" stroke="#C9CED6" stroke-width="4"/>')
    for sg in (-1, 1):
        g.append(f'<ellipse cx="{sg * 72}" cy="6" rx="12" ry="19" fill="{skin}"/>')
        g.append(f'<circle cx="{sg * 75}" cy="30" r="8" fill="none" stroke="#C9CED6" stroke-width="4"/>')
    g.append(f'<ellipse cx="0" cy="0" rx="72" ry="88" fill="{skin}"/>')
    for sg in (-1, 1):
        g.append(f'<ellipse cx="{sg * 42}" cy="26" rx="16" ry="9" fill="#FF8FA8" opacity="0.5"/>')
        ex = sg * 31
        if blink or (wink and sg == 1):
            g.append(f'<g transform="translate({ex},-4) scale({sg},1)"><path d="M -20 0 Q 0 10 20 0" stroke="#141018" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M 17 -1 L 32 -10 L 22 5 Z" fill="#141018"/></g>')
        else:
            g.append(f'<g transform="translate({ex},-4) scale({sg},1)">'
                     '<path d="M -20 0 Q 0 -17 20 0 Q 0 13 -20 0 Z" fill="#fff"/>'
                     '<circle cx="1" cy="-1" r="9" fill="#4A2D63"/><circle cx="1" cy="-1" r="4.5" fill="#000"/><circle cx="4" cy="-4" r="2.5" fill="#fff"/>'
                     '<path d="M -21 0 Q 0 -19 21 -1" stroke="#141018" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
                     '<path d="M 17 -3 L 34 -13 L 22 4 Z" fill="#141018"/></g>')
        g.append(f'<path d="M {sg * 16} -30 Q {sg * 32} -38 {sg * 50} -30" stroke="#2A1A22" stroke-width="5" fill="none" stroke-linecap="round"/>')
    g.append('<circle cx="47" cy="-36" r="3.5" fill="#C9CED6"/><circle cx="53" cy="-27" r="3.5" fill="#C9CED6"/>')
    g.append('<path d="M -3 16 Q 0 28 7 25" stroke="#C99880" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    g.append('<circle cx="9" cy="27" r="5" fill="none" stroke="#C9CED6" stroke-width="3"/>')
    g.append('<path d="M -15 47 Q 0 40 15 47 Q 0 58 -15 47 Z" fill="#4E1236"/>')
    g.append('<circle cx="11" cy="54" r="5" fill="none" stroke="#C9CED6" stroke-width="3"/>')
    g.append(f'<path d="M -82 -36 Q -84 -114 0 -116 Q 84 -114 82 -36 L 64 -42 L 52 -58 L 38 -40 L 20 -56 L 2 -38 L -16 -56 L -34 -40 L -50 -58 L -64 -42 Z" fill="{hair}"/>')
    g.append(f'<path d="M -80 -40 Q -98 40 -76 128 L -54 128 Q -70 40 -62 -40 Z" fill="{streak}"/>')
    g.append(f'<path d="M 80 -40 Q 98 40 76 128 L 54 128 Q 70 40 62 -40 Z" fill="{hair}"/>')
    g.append("</g>")
    return "".join(g)


def polaroid(cx, cy, rot, sc, v, t, caption, wink=False):
    if sc <= 0.001: return ""
    bgc = VARIANTS[v][2]
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f}) scale({sc:.3f})">'
            '<rect x="-160" y="-190" width="340" height="420" rx="10" fill="#000" opacity="0.35" transform="translate(14,18)"/>'
            '<rect x="-170" y="-205" width="340" height="420" rx="10" fill="#FBFAF7"/>'
            f'<rect x="-150" y="-185" width="300" height="300" fill="{bgc}"/>'
            f'<g clip-path="url(#photo)">{altgirl(0, -10, 1.0, v, t, tilt=4 * math.sin(t * 2 + v), wink=wink)}</g>'
            f'<rect x="-150" y="-185" width="300" height="300" fill="none" stroke="#0002" stroke-width="2"/>'
            + stext(0, 165, caption, 40, fill="#2A1A22", sw=0, shadow=False)
            + '<rect x="-40" y="-222" width="80" height="34" fill="#F6E27A" opacity="0.85" transform="rotate(-6)"/></g>')


# ---------- props ----------
def trash_bag(cx, cy, s, t):
    return (f'<g transform="translate({cx},{cy}) rotate({4 * math.sin(t * 5):.1f}) scale({s})">'
            '<path d="M -110 -40 Q -150 120 -60 150 L 60 150 Q 150 120 110 -40 Q 60 -20 0 -30 Q -60 -20 -110 -40 Z" fill="#1E2229" stroke="#0B0D10" stroke-width="8"/>'
            '<path d="M -30 -30 L -55 -95 L -5 -55 L 10 -100 L 30 -30 Z" fill="#1E2229" stroke="#0B0D10" stroke-width="7" stroke-linejoin="round"/>'
            '<path d="M -70 20 Q -60 90 -30 120" stroke="#3A414D" stroke-width="10" fill="none" stroke-linecap="round"/>'
            '<path d="M 60 -10 l 10 -20 M 80 0 l 18 -10 M 70 -25 l 0 -22" stroke="#9BE564" stroke-width="7" stroke-linecap="round"/></g>')


def guitar(cx, cy, s, rot):
    return (f'<g transform="translate({cx},{cy}) rotate({rot:.1f}) scale({s})">'
            '<rect x="-12" y="-230" width="24" height="200" fill="#2A1A22"/><rect x="-22" y="-262" width="44" height="40" rx="8" fill="#141018"/>'
            '<path d="M 0 -40 C -90 -50 -110 40 -60 70 C -110 120 -60 190 0 170 C 60 190 110 120 60 70 C 110 40 90 -50 0 -40 Z" fill="#FF2E88" stroke="#141018" stroke-width="8"/>'
            '<circle cx="0" cy="70" r="22" fill="#141018"/><rect x="-30" y="120" width="60" height="12" fill="#141018"/>'
            '<path d="M 70 -120 l 30 -10 l -18 28 l 30 -6" stroke="#FFD23F" stroke-width="8" fill="none" stroke-linejoin="round"/></g>')


def bubble(cx, cy, w, h, txt_lines, size, fill, fg, t, t0, tail="down"):
    sc = popscale(t, t0, 0.3)
    if sc <= 0: return ""
    tl = f'<polygon points="{-30},{h / 2 - 6} 30,{h / 2 - 6} -10,{h / 2 + 50}" fill="{fill}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>' if tail == "down" else ""
    out = [f'<g transform="translate({cx},{cy}) scale({sc:.3f}) rotate({2 * math.sin((t - t0) * 6):.2f})">',
           f'<rect x="{-w / 2 + 10}" y="{-h / 2 + 14}" width="{w}" height="{h}" rx="40" fill="{INK}"/>', tl,
           f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="40" fill="{fill}" stroke="{INK}" stroke-width="8"/>',
           f'<rect x="-28" y="{h / 2 - 12}" width="56" height="14" fill="{fill}"/>' if tail == "down" else ""]
    n = len(txt_lines)
    for k, ln in enumerate(txt_lines):
        out.append(stext(0, (k - (n - 1) / 2) * size * 1.12, ln, size, fill=fg, sw=0, shadow=False))
    out.append("</g>")
    return "".join(out)


# ---------- transitions & camera ----------
def stripes_wipe(t):
    cols = [PINK, LIME, CYAN, YEL]
    for n, T in enumerate(TRANSITIONS):
        if abs(t - T) < 0.24:
            p = (t - T + 0.24) / 0.48  # 0..1
            out = []
            for k in range(4):
                c = cols[(k + n) % 4]
                pk = clamp(p * 1.3 - k * 0.1)
                x = lerp(-1900, 1900, e_inout(pk))
                out.append(f'<polygon points="{x - 700:.0f},-100 {x + 900:.0f},-100 {x + 300:.0f},2020 {x - 1300:.0f},2020" fill="{c}"/>')
            return "".join(out)
    return ""


def e_inout(p):
    return 3 * p * p - 2 * p * p * p


def punch(t):
    s = 1.0
    for T in TRANSITIONS + [EV["instead"], EV["zhinki"], EV["you"]]:
        if 0 <= t - T < 0.35: s += 0.07 * (1 - e_out((t - T) / 0.35))
    return s


def shake(t):
    dx = dy = 0.0
    for t0, amp in ((EV["rise"] + 0.45, 14), (EV["instead"], 18), (EV["zhinki"], 22), (EV["you"], 26), (EV["cta"], 14)):
        if 0 <= t - t0 < 0.5:
            k = math.exp(-(t - t0) * 9) * amp
            dx += k * math.sin((t - t0) * 70); dy += k * math.cos((t - t0) * 53)
    return dx, dy


def nikita(t, f, x, y, s, **kw):
    kw.setdefault("blink", is_blink(t))
    kw.setdefault("cap_dy", 0)
    return shadow(x, y, s) + boar(t, x, y, s, mouth=mouth_at(f), outfit=True, **kw)


# ---------- scenes ----------
def scene_intro(t, f):
    out = [bg_neon(t), ring(540, 1000, 470, t, CYAN), ring(540, 1000, 540, -t, PINK, 6, "10 24"), floaters(t, 1, [PINK, LIME, CYAN])]
    gx, gy = 540, 1430
    p = prog(t, EV["rise"], EV["rise"] + 0.45)
    y = lerp(2300, gy, e_out(p)); sq = damp(t, EV["rise"] + 0.45, 0.7) + 0.03 * math.sin(t * 9)
    cd = lerp(-900, 0, e_bounce(prog(t, EV["cap"] - 0.3, EV["cap"]))) if t > EV["cap"] - 0.3 else None
    out.append(nikita(t, f, gx, y, 0.98, sq=sq, brow=0.4, headrot=4 * math.sin(t * 2 * math.pi), cap_dy=cd))
    if t < EV["claude"] - 0.05:
        out.append(ktext(540, 400, "ЗДАРОВА!", fit("ЗДАРОВА!", 960, 170), t, EV["hello"], fill=YEL, rot=-4))
    else:
        out.append(sticker(540, 250, "КЛОД-КАБАН", 58, LIME, INK, t, EV["claude"], -3))
        out.append(marker(110, 420, 860, 150, t, EV["nikita"] - 0.05, PINK))
        out.append(ktext(540, 420, "НИКИТА", 150, t, EV["nikita"], fill="#fff", style="drop"))
        sz = fit("СКУФ СКУФЫЧ", 960, 120)
        out.append(ktext(540, 590, "СКУФ СКУФЫЧ", sz, t, EV["skuf"], fill=CYAN, rot=-3))
    return "".join(out)


def scene_alts(t, f):
    out = [checker(t), f'<rect width="1080" height="1920" fill="url(#gAlt)" opacity="0.75"/>', halftone(t, "#fff", 0.05),
           floaters(t, 2, [PINK, CYAN, "#fff"], 12)]
    out.append(ktext(540, 230, "ГРЯЗНУЛЬКИ", fit("ГРЯЗНУЛЬКИ", 960, 130), t, 3.65, fill=YEL, rot=-3))
    out.append(stext(540, 360, "=", 90, fill="#fff", sc=popscale(t, EV["alts"] - 0.15)))
    out.append(marker(200, 480, 680, 120, t, EV["alts"] - 0.05, PINK, rot=2))
    out.append(ktext(540, 480, "АЛЬТУШКИ", 118, t, EV["alts"], fill="#fff", rot=2))
    cards = [(-14, 260, 980, 0, "мрак"), (10, 820, 1010, 1, "хаос"), (-2, 540, 1080, 2, "вайб")]
    for k, (r, x, y, v, cap) in enumerate(cards):
        t0 = EV["alts"] + k * 0.18
        p = e_back(prog(t, t0, t0 + 0.45), 1.4)
        if t < t0: continue
        sx = lerp(x + (900 if k % 2 else -900), x, p); ry = r + 3 * math.sin(t * 2 + k)
        out.append(polaroid(sx, y, lerp(r * 3, ry, p), 0.92 if k < 2 else 1.0, v, t, cap, wink=(k == 2 and t > EV["chaos"])))
    out.append(sticker(250, 700, "#ПОДВОДКА", 44, "#111", PINK, t, EV["eyeliner"], -10))
    out.append(sticker(830, 700, "#ЦЕПИ", 48, "#C9CED6", INK, t, EV["chains"], 8))
    out.append(sticker(540, 1340, "#ХАОС_В_ГЛАЗАХ", 50, LIME, INK, t, EV["chaos"], -4))
    # Nikita peeking with heart eyes
    pk = e_back(prog(t, EV["alts"] + 0.4, EV["alts"] + 0.8))
    if pk > 0:
        out.append(f'<g transform="translate({lerp(1300, 0, pk):.0f},0)">' +
                   boar(t, 900, 1900, 0.62, rot=-18, mouth=mouth_at(f), outfit=True, cap_dy=0, hearts=True, headrot=4 * math.sin(t * 6)) + "</g>")
    return "".join(out)


def scene_stat(t, f):
    out = [f'<rect width="1080" height="1920" fill="#0D1020"/>']
    for k in range(0, 1080, 60): out.append(f'<line x1="{k}" y1="0" x2="{k}" y2="1920" stroke="#1C2340" stroke-width="2"/>')
    for k in range(0, 1920, 60): out.append(f'<line x1="0" y1="{k}" x2="1080" y2="{k}" stroke="#1C2340" stroke-width="2"/>')
    out.append(f'<circle cx="540" cy="760" r="700" fill="url(#gGlowCyan)"/>')
    out.append(stext(540, 175, "ИССЛЕДОВАНИЕ ДИВАНА НИКИТЫ", 30, fill="#8A93B8", sw=0, shadow=False, op=clamp((t - 7.55) * 4)).replace(FONT, MONO))
    out.append(ktext(540, 270, "СКУФЫ ВЫБИРАЮТ:", fit("СКУФЫ ВЫБИРАЮТ:", 960, 96), t, EV["skufs"] - 0.1, fill="#fff"))
    # bar chart
    base_y = 1080; maxh = 620
    bars = [(300, "ЖЕНА", 12, "url(#gWife)", "#9AA6BC"), (780, "ГРЯЗНУЛЬКА", 88, "url(#gGr)", PINK)]
    for x, lab, val, fillc, tc in bars:
        p = e_out(prog(t, EV["choose"], EV["choose"] + 0.9)) if lab == "ГРЯЗНУЛЬКА" else e_out(prog(t, EV["choose"] - 0.2, EV["choose"] + 0.4))
        h = maxh * val / 100 * p
        out.append(f'<rect x="{x - 130 + 10}" y="{base_y - h + 14:.1f}" width="260" height="{h:.1f}" rx="18" fill="#000" opacity="0.4"/>')
        out.append(f'<rect x="{x - 130}" y="{base_y - h:.1f}" width="260" height="{h:.1f}" rx="18" fill="{fillc}" stroke="{INK}" stroke-width="6"/>')
        if p > 0:
            out.append(stext(x, base_y - h - 60, f"{round(val * p)}%", 84, fill=tc).replace(FONT, MONO))
        out.append(stext(x, base_y + 55, lab, fit(lab, 400, 56), fill="#fff", sw=0, shadow=False, op=clamp((t - 7.7) * 4)))
    out.append(f'<line x1="120" y1="{base_y}" x2="960" y2="{base_y}" stroke="#8A93B8" stroke-width="6"/>')
    if t > EV["gr"] + 0.2:
        for k in range(6):
            a = k * math.pi / 3 + t * 2
            out.append(star4(780 + math.cos(a) * 190, base_y - 560 + math.sin(a) * 60, 22, YEL, rot=t * 150))
    # stamp
    if t >= EV["instead"]:
        pp = prog(t, EV["instead"], EV["instead"] + 0.18); sc = lerp(3, 1, e_out(pp))
        out.append(f'<g opacity="{clamp(pp * 3):.2f}"><g transform="translate(540,1255) rotate(-6) scale({sc:.3f})">'
                   '<rect x="-330" y="-62" width="660" height="124" rx="20" fill="none" stroke="#FF3B5C" stroke-width="12"/>'
                   + stext(0, 0, "ВМЕСТО ЖЕНЫ", 84, fill="#FF3B5C", sw=0, shadow=False) + "</g></g>")
    out.append(nikita(t, f, 540, 1700, 0.62, brow=0.6, look=(1, -0.6) if t < EV["instead"] else (0, 0), headrot=5 * math.sin(t * 2 * math.pi), sq=0.03 * math.sin(t * 9)))
    out.append(stext(540, 1880, "* данные взяты с потолка Никиты", 26, fill="#8A93B8", sw=0, shadow=False).replace(FONT, MONO))
    return "".join(out)


def scene_versus(t, f):
    out = []
    # left: wife (grey, sad), right: gryaznulka (neon)
    lt = 1 if t >= EV["wife"] - 0.1 else 0
    out.append(f'<g clip-path="url(#left)"><rect width="1080" height="1920" fill="url(#gWife)"/>{halftone(t, "#fff", 0.05)}</g>')
    out.append(f'<g clip-path="url(#right)"><rect width="1080" height="1920" fill="url(#gAlt)"/>{halftone(t, PINK, 0.12)}{floaters(t, 4, [PINK, CYAN, LIME], 6)}</g>')
    out.append('<polygon points="600,0 640,0 480,1920 440,1920" fill="#fff"/>')
    vs = popscale(t, 11.4, 0.4)
    out.append(burst(540, 760, 110, 12, YEL, seed=3, sc=vs, rot=t * 30))
    out.append(stext(540, 760, "VS", 92, fill=INK, sw=0, shadow=False, sc=vs))
    out.append(ktext(280, 230, "ЖЕНА", 104, t, EV["wife"], fill="#E6EBF2", rot=-3))
    out.append(ktext(790, 230, "ГРЯЗНУЛЬКА", fit("ГРЯЗНУЛЬКА", 480, 90), t, EV["gr2"], fill=PINK, rot=3))
    if t >= EV["wife"]:
        out.append(f'<g transform="translate(0,{(1 - e_back(prog(t, EV["wife"], EV["wife"] + 0.4))) * 600:.0f})">' + trash_bag(270, 600, 1.15, t) + "</g>")
    out.append(bubble(270, 930, 420, 210, ["ВЫНЕСИ", "МУСОР"], 62, "#E6EBF2", "#3A4352", t, EV["trash"]))
    if t >= EV["gr2"]:
        p = e_back(prog(t, EV["gr2"], EV["gr2"] + 0.4))
        out.append(polaroid(810, lerp(-500, 590, p), 6 + 3 * math.sin(t * 3), 0.88, 0, t, "погнали", wink=t > EV["concert"]))
    if t >= EV["concert"]:
        out.append(guitar(1000, 470, 0.55, -25 + 6 * math.sin(t * 8)))
    out.append(bubble(810, 950, 440, 210, ["ПОГНАЛИ", "НА КОНЦЕРТ!"], 56, LIME, INK, t, EV["concert"]))
    look = (-1, 0) if t < EV["gr2"] else (1, 0)
    out.append(nikita(t, f, 540, 1520, 0.72, look=look, brow=-0.6 if t < EV["gr2"] else 0.7,
                      hearts=t > EV["concert"], headrot=(-8 if t < EV["gr2"] else 8) + 3 * math.sin(t * 6), sq=0.03 * math.sin(t * 9)))
    return "".join(out)


def scene_finale(t, f):
    out = [bg_neon(t, "#16051F"), ring(540, 1250, 520, t, PINK, 12), ring(540, 1250, 600, -t * 0.7, LIME, 6, "8 22"),
           floaters(t, 5, [PINK, LIME, CYAN, YEL], 14)]
    out.append(nikita(t, f, 540, 1560, 0.82, brow=0.8, hearts=t > EV["you"] + 0.1, headrot=5 * math.sin(t * 2 * math.pi),
                      sq=damp(t, EV["zhinki"], 0.5) + 0.03 * math.sin(t * 9), shades_dy=0 if t > EV["pick"] else None))
    if t < EV["you"] - 0.05:
        out.append(ktext(540, 230, "Я БЫ ВЫБРАЛ", fit("Я БЫ ВЫБРАЛ", 940, 100), t, EV["i"], fill="#fff", stagger=0.025))
        out.append(marker(70, 400, 940, 170, t, EV["grz"] - 0.05, PINK, rot=-3))
        out.append(ktext(540, 400, "ГРЯЗНУЛЕК", fit("ГРЯЗНУЛЕК", 920, 160), t, EV["grz"], fill="#fff", rot=-3, style="drop"))
        out.append(ktext(540, 580, "ЗА МЕСТО ЖИНКИ*", fit("ЗА МЕСТО ЖИНКИ*", 960, 104), t, EV["zamesto"], fill=LIME, rot=2))
        out.append(stext(540, 700, "*жинка, это шутка, положи скалку", 30, fill="#C9B6D6", sw=0, shadow=False, op=clamp((t - EV["zhinki"] - 0.3) * 4)))
    else:
        sc = popscale(t, EV["you"], 0.35) * (1 + 0.05 * base.beat(t))
        out.append(burst(540, 450, 380, 16, YEL, seed=21, sc=sc, rot=t * 15))
        out.append(stext(540, 450, "А ТЫ?", 200, fill=PINK, sc=sc, rot=-5))
        if t >= EV["cta"]:
            out.append(sticker(540, 760, "ПИШИ В КОММЕНТЫ", 58, LIME, INK, t, EV["cta"], 3))
            out.append(stext(540, 1000, "— НИКИТА СКУФ СКУФЫЧ", 46, fill="#fff", sc=popscale(t, EV["cta"] + 0.3), rot=-2))
            bob = 18 * math.sin((t - EV["cta"]) * 8)
            out.append(f'<path d="M 540 {860 + bob:.0f} l -40 0 l 40 70 l 40 -70 Z" fill="#fff" stroke="{INK}" stroke-width="7" stroke-linejoin="round" opacity="{clamp((t - EV["cta"]) * 4):.2f}"/>')
    return "".join(out)


SCENE_FN = {"intro": scene_intro, "alts": scene_alts, "stat": scene_stat, "versus": scene_versus, "finale": scene_finale}


def subtitles(t):
    if t >= 15.0: return ""  # finale uses big kinetic text instead
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            size = 72; gap = size * 0.32
            words = [w["disp"].upper() for w in c]
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 960:
                size = int(size * 960 / total); gap = size * 0.32; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            sc = lerp(0.8, 1, e_back(prog(t, t0, t0 + 0.14)))
            cx, cy = 540, 1650
            out = [f'<g transform="translate({cx},{cy}) scale({sc:.3f}) translate({-cx},{-cy})">']
            x = cx - total / 2
            for w, wd in zip(words, c):
                ww = tw(w, size)
                if wd["t0"] - 0.03 <= t < wd["t1"] + 0.05:
                    out.append(f'<rect x="{x - 14:.1f}" y="{cy - size * 0.62:.1f}" width="{ww + 28:.1f}" height="{size * 1.24:.1f}" rx="14" fill="{PINK}" transform="rotate(-2 {x + ww / 2:.1f} {cy})"/>')
                out.append(stext(x, cy, w, size, fill="#fff", anchor="start", op=1 if wd["t0"] - 0.03 <= t else 0.55))
                x += ww + gap
            out.append("</g>")
            return "".join(out)
    return ""


def nametag(t):
    t0 = EV["skufych"] + 0.5
    if t < t0: return ""
    sc = popscale(t, t0, 0.35) * (1 + 0.03 * base.beat(t))
    return pill(540, 1790, "НИКИТА СКУФ СКУФЫЧ", 42, LIME, INK, sc=sc, rot=-2)


def frame_svg(f):
    t = f / FPS
    name = next((n for a, b, n in SCENES if a <= t < b), "finale")
    dx, dy = shake(t); s = punch(t)
    body = SCENE_FN[name](t, f)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}'
            f'<rect width="{W}" height="{H}" fill="#000"/>'
            f'<g transform="translate({dx:.1f},{dy:.1f}) translate(540,960) scale({1.03 * s:.4f}) translate(-540,-960)">{body}</g>'
            f'<rect width="{W}" height="{H}" fill="url(#gVig)"/>'
            f'{stripes_wipe(t)}{subtitles(t)}{nametag(t)}{base.WM()}</svg>')


def render(f):
    cairosvg.svg2png(bytestring=frame_svg(f).encode(), write_to=f"build/frames/{f:05d}.png")
    return f


if __name__ == "__main__":
    os.makedirs("build/frames", exist_ok=True)
    frames = [int(x) for x in sys.argv[1:]] or list(range(NFRAMES))
    with Pool(os.cpu_count()) as pool:
        for i, _ in enumerate(pool.imap_unordered(render, frames, chunksize=4)):
            if i % 200 == 0: print("frame", i, flush=True)
    print("done", len(frames))
