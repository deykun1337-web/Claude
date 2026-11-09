"""Shared motion-graphics helpers (kinetic text, backgrounds, props) reused from the v2 cartoon."""
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
