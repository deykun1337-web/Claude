"""Renders every frame of the cartoon as SVG -> PNG (1080x1920, 30 fps)."""
import json, math, os, random, sys
from html import escape
from multiprocessing import Pool
import cairosvg
from PIL import ImageFont
from timeline import *

FONT = "Inter Display Black"
FONTFILE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
MOUTH = json.load(open("build/mouth.json"))
VOICE_TEXT = [l["text"] for l in json.load(open("build/voice_tight.json"))]
INK = "#2A120A"
MUD, MUD2, MUD3 = "#6B4226", "#8B5A36", "#4A2C18"
_fc = {}


# ---------- helpers ----------
def tw(text, size):
    if size not in _fc:
        _fc[size] = ImageFont.truetype(FONTFILE, size)
    return _fc[size].getlength(text)


def fit(text, maxw, maxsize):
    s = maxsize
    while s > 20 and tw(text, s) > maxw:
        s -= 2
    return s


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, a, b):
    return clamp((t - a) / (b - a))


def lerp(a, b, p):
    return a + (b - a) * p


def e_out(p):
    return 1 - (1 - p) ** 3


def e_in(p):
    return p ** 2


def e_inout(p):
    return 3 * p * p - 2 * p * p * p


def e_back(p, s=1.9):
    p -= 1
    return 1 + p * p * ((s + 1) * p + s)


def e_bounce(p):
    n, d = 7.5625, 2.75
    if p < 1 / d: return n * p * p
    if p < 2 / d: p -= 1.5 / d; return n * p * p + 0.75
    if p < 2.5 / d: p -= 2.25 / d; return n * p * p + 0.9375
    p -= 2.625 / d; return n * p * p + 0.984375


def popscale(t, t0, d=0.35):
    """0 before t0, overshoot pop to 1."""
    if t < t0: return 0.0
    return e_back(prog(t, t0, t0 + d))


def damp(t, t0, amp, freq=22, k=7):
    if t < t0: return 0.0
    dt = t - t0
    return amp * math.exp(-dt * k) * math.cos(dt * freq)


def stext(x, y, txt, size, fill="#fff", stroke=INK, sw=None, shadow=True, anchor="middle", rot=0, sc=1, op=1):
    """Bold outlined text, vertically centred on y."""
    if sc <= 0.001 or op <= 0.001: return ""
    sw = sw if sw is not None else size * 0.17
    e = escape(txt, quote=False)
    by = size * 0.36
    base = f'font-family="{FONT}" font-size="{size}" text-anchor="{anchor}"'
    g = f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.2f}) scale({sc:.3f})" opacity="{op:.3f}">'
    if shadow:
        g += f'<text x="0" y="{by + size * 0.1:.1f}" {base} fill="{stroke}" stroke="{stroke}" stroke-width="{sw:.1f}" stroke-linejoin="round">{e}</text>'
    if sw > 0:
        g += f'<text x="0" y="{by:.1f}" {base} fill="{stroke}" stroke="{stroke}" stroke-width="{sw:.1f}" stroke-linejoin="round">{e}</text>'
    g += f'<text x="0" y="{by:.1f}" {base} fill="{fill}">{e}</text></g>'
    return g


def pill(cx, cy, txt, size, bg, fg, sc=1, rot=0):
    if sc <= 0.001: return ""
    w = tw(txt, size) + size * 1.2; h = size * 1.7
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f}) scale({sc:.3f})">'
            f'<rect x="{-w / 2 + 8:.1f}" y="{-h / 2 + 12:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" fill="{INK}"/>'
            f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" fill="{bg}" stroke="{INK}" stroke-width="7"/>'
            + stext(0, 0, txt, size, fill=fg, sw=0, shadow=False) + "</g>")


def burst(cx, cy, r, n, fill, stroke=INK, seed=1, rot=0, sc=1, ry=None):
    if sc <= 0.001: return ""
    rr = random.Random(seed); ry = ry or r; pts = []
    for i in range(n * 2):
        a = math.pi * i / n
        k = 1.0 if i % 2 == 0 else rr.uniform(0.68, 0.8)
        pts.append(f"{math.cos(a) * r * k:.1f},{math.sin(a) * ry * k:.1f}")
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f}) scale({sc:.3f})">'
            f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="10" stroke-linejoin="round"/></g>')


def star4(cx, cy, r, fill, rot=0):
    pts = []
    for i in range(8):
        a = math.pi * i / 4 + math.radians(rot); k = r if i % 2 == 0 else r * 0.32
        pts.append(f"{cx + math.cos(a) * k:.1f},{cy + math.sin(a) * k:.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'


def heart(cx, cy, s, fill, op=1):
    return (f'<path transform="translate({cx:.1f},{cy:.1f}) scale({s:.2f})" opacity="{op:.2f}" '
            f'd="M0 30 C -60 -10 -40 -60 0 -30 C 40 -60 60 -10 0 30 Z" fill="{fill}" stroke="{INK}" stroke-width="6"/>')


# ---------- the boar (Claude) ----------
MUD_BODY = [(-125, -250, 48, 36, 40), (95, -175, 58, 40, 55), (-35, -110, 42, 28, 0), (150, -300, 30, 24, 30), (-170, -170, 26, 30, 0)]
MUD_HEAD = [(-128, -455, 34, 26, 0), (118, -490, 28, 20, 0), (35, -535, 24, 15, 0), (138, -338, 22, 17, 25), (-60, -540, 18, 12, 0)]


def mud_blob(x, y, rx, ry, drip, op):
    s = f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{MUD}" opacity="{op:.2f}"/>'
    if drip:
        s += (f'<path d="M {x - 9} {y} v {drip} a 9 9 0 0 0 18 0 v {-drip} Z" fill="{MUD}" opacity="{op:.2f}"/>')
    s += f'<ellipse cx="{x - rx * 0.3:.0f}" cy="{y - ry * 0.35:.0f}" rx="{rx * 0.3:.0f}" ry="{ry * 0.2:.0f}" fill="{MUD2}" opacity="{op:.2f}"/>'
    return s


def shades(dy):
    return (f'<g transform="translate(0,{dy:.1f})" fill="#111">'
            '<rect x="-160" y="-472" width="320" height="24"/>'
            '<rect x="-145" y="-448" width="125" height="50"/><rect x="20" y="-448" width="125" height="50"/>'
            '<rect x="-20" y="-448" width="40" height="18"/>'
            '<rect x="-130" y="-398" width="95" height="16"/><rect x="35" y="-398" width="95" height="16"/>'
            '<rect x="-128" y="-440" width="18" height="18" fill="#fff"/><rect x="-108" y="-420" width="18" height="18" fill="#fff"/>'
            '<rect x="37" y="-440" width="18" height="18" fill="#fff"/><rect x="57" y="-420" width="18" height="18" fill="#fff"/></g>')


def cap(dy):
    return (f'<g transform="translate(0,{dy:.1f})">'
            '<ellipse cx="0" cy="-548" rx="172" ry="66" fill="#4B4B55" stroke="#1E1E24" stroke-width="8"/>'
            '<path d="M -120 -590 Q 0 -560 120 -590 M -60 -608 Q 0 -585 60 -608" stroke="#2C2C33" stroke-width="5" fill="none"/>'
            '<path d="M -168 -528 Q 0 -470 168 -528 L 158 -508 Q 0 -440 -158 -508 Z" fill="#33333B" stroke="#1E1E24" stroke-width="7" stroke-linejoin="round"/>'
            '<circle cx="0" cy="-610" r="12" fill="#2C2C33"/></g>')


def boar(t, x, y, s=1.0, sq=0.0, rot=0.0, mud=0.0, mouth=0.0, blink=False, look=(0, 0),
         headrot=0.0, brow=0.3, shades_dy=None, cap_dy=None, outfit=False, hearts=False):
    sx = s * (1 + 0.22 * sq); sy = s * (1 - 0.22 * sq)
    ear = 5 * math.sin(t * 6)
    p = [f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.2f}) scale({sx:.3f},{sy:.3f})">']
    for lx in (-150, 150):
        p.append(f'<rect x="{lx - 30}" y="-100" width="60" height="100" rx="26" fill="#9A4A30" stroke="#6E2E1A" stroke-width="6"/>')
    p.append('<ellipse cx="0" cy="-215" rx="215" ry="175" fill="url(#gBody)" stroke="#7A3520" stroke-width="8"/>')
    p.append('<ellipse cx="0" cy="-165" rx="125" ry="92" fill="#F3AE90" opacity="0.6"/>')
    for lx in (-80, 80):
        p.append(f'<rect x="{lx - 38}" y="-112" width="76" height="112" rx="30" fill="#C9653F" stroke="#7A3520" stroke-width="7"/>')
        p.append(f'<path d="M {lx - 37} -26 h74 v12 a14 14 0 0 1 -14 14 h-46 a14 14 0 0 1 -14 -14 Z" fill="#3B1D14"/>')
        p.append(f'<line x1="{lx}" y1="-24" x2="{lx}" y2="0" stroke="#7A3520" stroke-width="5"/>')
    if mud > 0:
        for b in MUD_BODY: p.append(mud_blob(*b, mud))
    if outfit:
        p.append('<ellipse cx="0" cy="-215" rx="215" ry="175" fill="url(#gTrack)" stroke="#121A40" stroke-width="8"/>')
        for sg in (-1, 1):
            for off in (0, 26):
                p.append(f'<path d="M {sg * (196 - off)} -300 Q {sg * (224 - off)} -205 {sg * (180 - off)} -95" stroke="#fff" stroke-width="13" fill="none" stroke-linecap="round"/>')
        p.append('<line x1="0" y1="-255" x2="0" y2="-48" stroke="#C9CEDB" stroke-width="7"/><rect x="-9" y="-200" width="18" height="34" rx="5" fill="#C9CEDB"/>')
        for k in range(15):
            u = k / 14; cx = -125 + 250 * u; cy = -262 + 75 * (1 - (2 * u - 1) ** 2)
            p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="10" fill="none" stroke="#F2C14E" stroke-width="6"/>')
        p.append('<circle cx="0" cy="-165" r="24" fill="#F2C14E" stroke="#B8862B" stroke-width="5"/><circle cx="-7" cy="-172" r="6" fill="#FFF3C4"/>')
        for lx in (-80, 80):
            p.append(f'<rect x="{lx - 38}" y="-112" width="76" height="80" rx="26" fill="#22306B" stroke="#121A40" stroke-width="7"/>')
            p.append(f'<line x1="{lx - 22}" y1="-104" x2="{lx - 22}" y2="-40" stroke="#fff" stroke-width="8"/>')
    # head
    p.append(f'<g transform="rotate({headrot:.2f} 0 -330)">')
    for sgn, a in ((-1, -ear), (1, ear)):
        p.append(f'<g transform="rotate({a:.2f} {sgn * 140} -500)">'
                 f'<path d="M {sgn * 150} -490 L {sgn * 218} -628 L {sgn * 68} -545 Z" fill="#C9653F" stroke="#7A3520" stroke-width="8" stroke-linejoin="round"/>'
                 f'<path d="M {sgn * 148} -512 L {sgn * 192} -592 L {sgn * 106} -546 Z" fill="#F4A48C"/></g>')
    p.append('<path d="M -112 -500 L -100 -588 L -70 -535 L -45 -612 L -18 -545 L 8 -625 L 32 -545 L 58 -606 L 80 -535 L 106 -580 L 118 -500 Z" fill="#5A2A1A" stroke="#3B1810" stroke-width="5" stroke-linejoin="round"/>')
    p.append('<ellipse cx="0" cy="-405" rx="178" ry="152" fill="url(#gHead)" stroke="#7A3520" stroke-width="8"/>')
    for sgn in (-1, 1):
        p.append(f'<ellipse cx="{sgn * 128}" cy="-352" rx="30" ry="18" fill="#FF7F6E" opacity="0.45"/>')
    p.append(star4(0, -505, 30, "#FFF1E0", rot=t * 40))
    p.append(star4(0, -505, 30, "#FFF1E0", rot=t * 40 + 45).replace("<polygon", '<polygon opacity="0.85"'))
    # brows
    p.append(f'<path d="M -112 -497 L -36 {-506 + 20 * brow:.1f}" stroke="#3B1D14" stroke-width="17" stroke-linecap="round"/>')
    p.append(f'<path d="M 112 -497 L 36 {-506 + 20 * brow:.1f}" stroke="#3B1D14" stroke-width="17" stroke-linecap="round"/>')
    # eyes
    for ex in (-68, 68):
        ey = -435
        if blink:
            p.append(f'<path d="M {ex - 36} {ey} Q {ex} {ey + 22} {ex + 36} {ey}" stroke="#3B1D14" stroke-width="9" fill="none" stroke-linecap="round"/>')
        elif hearts:
            p.append(f'<path transform="translate({ex},{ey}) scale(1.15)" d="M0 30 C -60 -10 -40 -60 0 -30 C 40 -60 60 -10 0 30 Z" fill="#FF2E88" stroke="#3B1D14" stroke-width="6"/>')
        else:
            px, py = ex + look[0] * 13, ey + 6 + look[1] * 13
            p.append(f'<ellipse cx="{ex}" cy="{ey}" rx="40" ry="46" fill="#fff" stroke="#3B1D14" stroke-width="6"/>')
            p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="21" fill="#24120C"/><circle cx="{px - 7:.1f}" cy="{py - 8:.1f}" r="7" fill="#fff"/>')
    # mouth
    if mouth > 0.08:
        ry = 6 + 30 * mouth
        p.append(f'<ellipse cx="0" cy="-262" rx="{40 + 6 * mouth:.1f}" ry="{ry:.1f}" fill="#3B1210" stroke="#7A3520" stroke-width="6"/>')
        if mouth > 0.3:
            p.append(f'<ellipse cx="0" cy="{-262 + ry * 0.5:.1f}" rx="24" ry="{ry * 0.35:.1f}" fill="#FF7A8A"/>')
    else:
        p.append('<path d="M -50 -276 Q 0 -240 50 -276" stroke="#3B1D14" stroke-width="9" fill="none" stroke-linecap="round"/>')
    # snout + tusks
    p.append('<ellipse cx="0" cy="-345" rx="92" ry="64" fill="#F4A48C" stroke="#A0503A" stroke-width="7"/>')
    p.append('<ellipse cx="-30" cy="-345" rx="13" ry="22" fill="#6B2A1A"/><ellipse cx="30" cy="-345" rx="13" ry="22" fill="#6B2A1A"/>')
    for sgn in (-1, 1):
        p.append(f'<path d="M {sgn * 58} -290 Q {sgn * 120} -298 {sgn * 114} -375 Q {sgn * 96} -322 {sgn * 46} -310 Z" fill="#FFF6E6" stroke="#A0503A" stroke-width="5" stroke-linejoin="round"/>')
    if mud > 0:
        for b in MUD_HEAD: p.append(mud_blob(*b, mud))
    if cap_dy is not None: p.append(cap(cap_dy))
    if shades_dy is not None: p.append(shades(shades_dy))
    p.append("</g></g>")
    return "".join(p)


def shadow(x, y, s, lift=0.0):
    k = clamp(1 - lift / 900, 0.3, 1)
    return f'<ellipse cx="{x:.1f}" cy="{y + 4:.1f}" rx="{215 * s * k:.1f}" ry="{34 * s * k:.1f}" fill="#000" opacity="{0.22 * k:.2f}"/>'


def is_blink(t):
    ph = (t + 0.7) % 2.9
    return ph < 0.1


def mouth_at(f):
    return MOUTH[min(f, len(MOUTH) - 1)]


# ---------- particles ----------
def splash_parts(t, t0, x, y, n, seed, ground):
    dt = t - t0
    if dt < 0 or dt > 1.4: return ""
    rr = random.Random(seed); out = []; g = 2600
    for i in range(n):
        ang = math.radians(rr.uniform(-165, -15)); sp = rr.uniform(700, 1700); r = rr.uniform(9, 28)
        vx, vy = math.cos(ang) * sp, math.sin(ang) * sp
        px = x + vx * dt; py = y + vy * dt + 0.5 * g * dt * dt
        if py > ground + 30: continue
        cvy = vy + g * dt; a = math.degrees(math.atan2(cvy, vx)); v = math.hypot(vx, cvy)
        st = 1 + min(v / 1600, 1.2); op = 1 - clamp((dt - 0.9) / 0.5)
        col = rr.choice([MUD, MUD2, MUD3])
        out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r * st:.1f}" ry="{r:.1f}" transform="rotate({a:.1f} {px:.1f} {py:.1f})" fill="{col}" opacity="{op:.2f}"/>')
    return "".join(out)


def dust(t, t0, x, y):
    dt = t - t0
    if dt < 0 or dt > 0.7: return ""
    out = []
    for i, sgn in enumerate((-1, -1, 1, 1)):
        k = 1 + i % 2 * 0.6
        out.append(f'<circle cx="{x + sgn * (150 + 260 * e_out(dt / 0.7) * k):.1f}" cy="{y - 20 - 40 * dt * k:.1f}" r="{30 + 50 * dt * k:.1f}" fill="#FFE8D0" opacity="{0.8 * (1 - dt / 0.7):.2f}"/>')
    return "".join(out)


def ripples(t, t0, x, y):
    out = []
    for k in range(3):
        dt = t - t0 - k * 0.25
        if 0 < dt < 1.2:
            out.append(f'<ellipse cx="{x}" cy="{y}" rx="{120 + 300 * e_out(dt / 1.2):.1f}" ry="{30 + 70 * e_out(dt / 1.2):.1f}" fill="none" stroke="{MUD2}" stroke-width="8" opacity="{1 - dt / 1.2:.2f}"/>')
    return "".join(out)


def shake(t):
    dx = dy = 0.0
    for t0, amp in ((EV["land1"], 14), (EV["splash1"], 26), (EV["stamp"], 16), (EV["hit"], 22), (EV["land2"], 24), (EV["hru"], 30)):
        if 0 <= t - t0 < 0.5:
            k = math.exp(-(t - t0) * 9) * amp
            dx += k * math.sin((t - t0) * 70); dy += k * math.cos((t - t0) * 53)
    return dx, dy


def beat(t):
    return math.exp(-((t * BPM / 60) % 1) * 6)


# ---------- backgrounds ----------
DEFS = '''<defs>
<radialGradient id="gBody" cx="0.4" cy="0.35" r="0.75"><stop offset="0" stop-color="#F2956F"/><stop offset="0.6" stop-color="#D97757"/><stop offset="1" stop-color="#B25A3B"/></radialGradient>
<radialGradient id="gHead" cx="0.42" cy="0.35" r="0.75"><stop offset="0" stop-color="#F49B76"/><stop offset="0.65" stop-color="#DB7A59"/><stop offset="1" stop-color="#B85C3E"/></radialGradient>
<radialGradient id="gIntro" cx="0.5" cy="0.45" r="0.8"><stop offset="0" stop-color="#FFB15E"/><stop offset="0.55" stop-color="#E8603C"/><stop offset="1" stop-color="#6E2238"/></radialGradient>
<linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7CCBF0"/><stop offset="1" stop-color="#D8F3FB"/></linearGradient>
<linearGradient id="gSunset" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF7A7A"/><stop offset="0.6" stop-color="#FFB86B"/><stop offset="1" stop-color="#FFE3A3"/></linearGradient>
<linearGradient id="gVapor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#12002E"/><stop offset="1" stop-color="#5B0E91"/></linearGradient>
<linearGradient id="gSun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE45E"/><stop offset="1" stop-color="#FF3FA4"/></linearGradient>
<linearGradient id="gCan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#AEB6C2"/><stop offset="0.4" stop-color="#F4F6F9"/><stop offset="1" stop-color="#8E97A5"/></linearGradient>
<linearGradient id="gTrack" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#34449A"/><stop offset="1" stop-color="#1A2456"/></linearGradient>
<radialGradient id="gVig" cx="0.5" cy="0.5" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.38"/></radialGradient>
</defs>'''


def bg_intro(t):
    cx, cy = 540, 900; out = ['<rect width="1080" height="1920" fill="url(#gIntro)"/>']
    rot = t * 18
    for i in range(14):
        a0 = math.radians(rot + i * 360 / 14); a1 = a0 + math.radians(360 / 28)
        out.append(f'<polygon points="{cx},{cy} {cx + math.cos(a0) * 2200:.0f},{cy + math.sin(a0) * 2200:.0f} {cx + math.cos(a1) * 2200:.0f},{cy + math.sin(a1) * 2200:.0f}" fill="#fff" opacity="{0.07 + 0.05 * beat(t):.3f}"/>')
    rr = random.Random(3)
    for i in range(14):
        bx = rr.uniform(40, 1040); sp = rr.uniform(120, 260); r = rr.uniform(14, 40); ph = rr.uniform(0, 3000)
        by = 2000 - ((t * sp + ph) % 2200)
        out.append(f'<circle cx="{bx + 20 * math.sin(t * 2 + i):.0f}" cy="{by:.0f}" r="{r:.0f}" fill="{MUD}" opacity="0.28"/>')
    return "".join(out)


def bg_meadow(t, sunset=False):
    out = [f'<rect width="1080" height="1920" fill="url(#{"gSunset" if sunset else "gSky"})"/>']
    if sunset:
        out.append(f'<circle cx="540" cy="1080" r="{260 + 8 * beat(t):.0f}" fill="#FFF3B0" opacity="0.85"/>')
    for i, (cx, cy, s, sp) in enumerate(((200, 330, 1.0, 30), (820, 520, 0.8, 22), (500, 760, 0.6, 40))):
        x = (cx + t * sp) % 1400 - 160
        out.append(f'<g transform="translate({x:.0f},{cy}) scale({s})" fill="#fff" opacity="0.9"><ellipse cx="0" cy="0" rx="120" ry="50"/><ellipse cx="-70" cy="10" rx="80" ry="40"/><ellipse cx="70" cy="12" rx="90" ry="38"/><ellipse cx="10" cy="-35" rx="70" ry="45"/></g>')
    out.append(f'<path d="M 0 1180 Q 270 1080 540 1170 T 1080 1150 V 1920 H 0 Z" fill="{"#E39A5B" if sunset else "#8FD16E"}"/>')
    out.append(f'<path d="M 0 1260 Q 300 1190 620 1250 T 1080 1240 V 1920 H 0 Z" fill="{"#C9783F" if sunset else "#6DB955"}"/>')
    for i in range(18):  # grass tufts
        gx = (i * 67 + 20) % 1080; gy = 1300 + (i * 131) % 520
        out.append(f'<path d="M {gx} {gy} l 10 -34 l 8 30 l 10 -26 l 6 30 Z" fill="{"#A85E2E" if sunset else "#4F9C3C"}"/>')
    return "".join(out)


def puddle_back(cx=540, cy=1430):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="400" ry="118" fill="{MUD3}"/>'
            f'<ellipse cx="{cx}" cy="{cy - 6}" rx="372" ry="100" fill="{MUD}"/>'
            f'<ellipse cx="{cx - 120}" cy="{cy - 40}" rx="120" ry="20" fill="{MUD2}" opacity="0.7"/>')


def puddle_front(t, cx=540, cy=1430):
    w = "".join(f" Q {cx - 300 + i * 100 + 50:.0f} {cy - 50 + 12 * math.sin(t * 5 + i)} {cx - 300 + (i + 1) * 100:.0f} {cy - 38:.0f}" for i in range(6))
    return (f'<path d="M {cx - 330} {cy - 30} L {cx - 300} {cy - 38}{w} L {cx + 330} {cy - 30} Q {cx} {cy + 150} {cx - 330} {cy - 30} Z" fill="{MUD}"/>'
            f'<path d="M {cx - 250} {cy + 10} Q {cx} {cy + 70} {cx + 250} {cy + 10}" stroke="{MUD2}" stroke-width="10" fill="none" opacity="0.8" stroke-linecap="round"/>')


def bg_vapor(t):
    out = ['<rect width="1080" height="1920" fill="url(#gVapor)"/>']
    for i in range(40):
        rr = random.Random(i); sx = rr.uniform(0, 1080); sy = rr.uniform(0, 1100)
        out.append(f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="{rr.uniform(2, 5):.1f}" fill="#fff" opacity="{0.4 + 0.5 * abs(math.sin(t * 3 + i)):.2f}"/>')
    sr = 330 + 10 * beat(t)
    out.append(f'<circle cx="540" cy="1010" r="{sr:.0f}" fill="url(#gSun)"/>')
    for k in range(6):
        y = 1040 + k * 38; h = 6 + k * 4
        out.append(f'<rect x="150" y="{y}" width="780" height="{h}" fill="#3A0868"/>')
    hz = 1180
    out.append(f'<rect x="0" y="{hz}" width="1080" height="{1920 - hz}" fill="#14002F"/>')
    for i in range(-10, 11):
        out.append(f'<line x1="{540 + i * 40}" y1="{hz}" x2="{540 + i * 260}" y2="1920" stroke="#FF2BD6" stroke-width="4" opacity="0.8"/>')
    off = (t * 1.2) % 1
    for k in range(12):
        z = (k + 1 - off) / 12; y = hz + (1920 - hz) * z ** 2.2
        out.append(f'<line x1="0" y1="{y:.1f}" x2="1080" y2="{y:.1f}" stroke="#FF2BD6" stroke-width="{2 + 5 * z:.1f}" opacity="{0.4 + 0.6 * z:.2f}"/>')
    out.append(f'<line x1="0" y1="{hz}" x2="1080" y2="{hz}" stroke="#00F0FF" stroke-width="6"/>')
    return "".join(out)


def bg_carpet(t):
    out = ['<rect width="1080" height="1920" fill="#8E1B1B"/>']
    for k in range(-16, 17):
        x = k * 120
        out.append(f'<line x1="{x}" y1="0" x2="{x + 1400}" y2="1400" stroke="#5E0F14" stroke-width="12"/>')
        out.append(f'<line x1="{x + 1400}" y1="0" x2="{x}" y2="1400" stroke="#5E0F14" stroke-width="12"/>')
    for i in range(10):
        for j in range(13):
            cx2 = i * 120 + (60 if j % 2 else 0); cy2 = j * 60
            out.append(f'<rect x="{cx2 - 10}" y="{cy2 - 10}" width="20" height="20" transform="rotate(45 {cx2} {cy2})" fill="#D9A441"/>')
    for r, col in ((330, "#1F3B6B"), (260, "#D9A441"), (190, "#8E1B1B"), (120, "#F3E2C0"), (60, "#1F3B6B")):
        out.append(f'<polygon points="540,{760 - r} {540 + r},760 540,{760 + r} {540 - r},760" fill="{col}" stroke="#3B0A0A" stroke-width="6"/>')
    out.append('<rect x="40" y="40" width="1000" height="1250" fill="none" stroke="#D9A441" stroke-width="26"/>')
    out.append('<rect x="80" y="80" width="920" height="1170" fill="none" stroke="#F3E2C0" stroke-width="8" stroke-dasharray="30 18"/>')
    out.append('<rect x="0" y="1330" width="1080" height="590" fill="#8A5A3B"/>')
    for k in range(7):
        out.append(f'<line x1="0" y1="{1330 + k * 90}" x2="1080" y2="{1330 + k * 90}" stroke="#6E4429" stroke-width="6"/>')
    out.append('<rect x="0" y="1316" width="1080" height="20" fill="#5B3A24"/>')
    return "".join(out)


# ---------- props ----------
def deo_can(x, y, rot, sc=1):
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.2f}) scale({sc:.3f})">'
            '<rect x="-12" y="-222" width="24" height="22" fill="#1B4FB8"/>'
            '<rect x="-48" y="-205" width="96" height="62" rx="14" fill="#2D7FF9" stroke="#163C8C" stroke-width="6"/>'
            '<rect x="-58" y="-150" width="116" height="300" rx="20" fill="url(#gCan)" stroke="#4B5563" stroke-width="7"/>'
            '<rect x="-58" y="-70" width="116" height="110" fill="#2D7FF9"/>'
            + stext(0, -18, "72Ч", 50, fill="#fff", sw=0, shadow=False) +
            stext(0, 85, "ДЕО", 30, fill="#4B5563", sw=0, shadow=False) + '</g>')


def slipper(x, y, rot):
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.2f})">'
            '<ellipse cx="0" cy="0" rx="64" ry="142" fill="#3E6FB0" stroke="#1D3A63" stroke-width="8"/>'
            '<ellipse cx="0" cy="10" rx="46" ry="118" fill="#5B8BD0"/>'
            '<path d="M -68 -80 Q 0 -122 68 -80 L 66 -26 Q 0 -66 -66 -26 Z" fill="#F2F2F7" stroke="#1D3A63" stroke-width="7" stroke-linejoin="round"/>'
            '<path d="M -60 -62 Q 0 -98 60 -62" stroke="#E23B3B" stroke-width="9" fill="none"/></g>')


def stink(t, x, y, op):
    out = []
    for k, (ox, ph) in enumerate(((-260, 0), (250, 1.7), (-200, 3.1), (230, 4.4))):
        pts = []
        for j in range(12):
            yy = y - j * 28 - ((t * 140 + k * 60) % 120)
            xx = x + ox + 22 * math.sin(j * 0.8 + t * 6 + ph)
            pts.append(f"{xx:.1f},{yy:.1f}")
        out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#9BE564" stroke-width="13" stroke-linecap="round" stroke-linejoin="round" opacity="{op:.2f}"/>')
    return "".join(out)


def wipe(t):
    for T in TRANSITIONS:
        if T - 0.2 <= t < T:
            p = e_in(prog(t, T - 0.2, T)); cx, cy = 540, 1990
        elif T <= t < T + 0.2:
            p = 1 - e_out(prog(t, T, T + 0.2)); cx, cy = 540, -70
        else:
            continue
        r = 2150 * p
        if r < 2: return ""
        out = [f'<circle cx="{cx}" cy="{cy}" r="{r:.0f}" fill="{MUD3}"/>']
        for i in range(14):
            a = 2 * math.pi * i / 14 + T
            out.append(f'<circle cx="{cx + math.cos(a) * r * 0.97:.0f}" cy="{cy + math.sin(a) * r * 0.97:.0f}" r="{r * 0.12:.0f}" fill="{MUD3}"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.9:.0f}" fill="{MUD}"/>')
        return "".join(out)
    return ""


# ---------- subtitles ----------
def with_punct(li, ws):
    text = VOICE_TEXT[li]; pos = 0
    for w in ws:
        i = text.find(w["w"], pos)
        if i < 0: w["disp"] = w["w"]; continue
        j = i + len(w["w"])
        while j < len(text) and text[j] in ",.!?:»…": j += 1
        w["disp"] = text[i:j].replace("»", ""); pos = j
    return ws


def chunks():
    res = []
    for li in range(len(VOICE_START)):
        ws = with_punct(li, [dict(w) for w in WORDS if w["line"] == li]); cur = []
        for w in ws:
            cur.append(w)
            txt = " ".join(x["disp"] for x in cur)
            if len(cur) >= 3 or len(txt) > 15 or w["disp"][-1:] in ",.!?:":
                if len(cur) > 1 and len(cur[-1]["disp"]) <= 3 and cur[-1]["disp"][-1:].isalpha():
                    res.append(cur[:-1]); cur = [cur[-1]]
                else:
                    res.append(cur); cur = []
        if cur: res.append(cur)
    out = []
    for i, c in enumerate(res):
        t0 = c[0]["t0"] - 0.05
        nxt = res[i + 1][0]["t0"] - 0.05 if i + 1 < len(res) and res[i + 1][0]["line"] == c[0]["line"] else c[-1]["t1"] + 0.3
        if i + 1 < len(res): nxt = min(nxt, res[i + 1][0]["t0"] - 0.05)
        out.append((t0, nxt, c))
    return out


CHUNKS = None


def subtitles(t):
    global CHUNKS
    if CHUNKS is None: CHUNKS = chunks()
    for t0, t1, c in CHUNKS:
        if t0 <= t < t1:
            size = 74
            words = [w["disp"].upper() for w in c]
            gap = lambda sz: sz * 0.32
            total = sum(tw(w, size) for w in words) + gap(size) * (len(words) - 1)
            if total > 960:
                size = int(size * 960 / total); total = sum(tw(w, size) for w in words) + gap(size) * (len(words) - 1)
            sc = lerp(0.75, 1, e_back(prog(t, t0, t0 + 0.16)))
            cx, cy = 540, 1640
            out = [f'<g transform="translate({cx},{cy}) scale({sc:.3f}) translate({-cx},{-cy})">']
            x = cx - total / 2
            for w, wd in zip(words, c):
                active = wd["t0"] - 0.03 <= t
                col = "#FFD23F" if active and t < wd["t1"] + 0.05 else ("#FFFFFF" if active else "#FFFFFF")
                op = 1 if active else 0.55
                out.append(stext(x, cy, w, size, fill=col, anchor="start", op=op))
                x += tw(w, size) + gap(size)
            out.append("</g>")
            return "".join(out)
    return ""


# ---------- scenes ----------
def scene_intro(t, f):
    out = [bg_intro(t)]
    s1 = popscale(t, EV["title1"]); s2 = popscale(t, EV["title2"])
    wob = 2 * math.sin(t * 4)
    sz = fit("ГРЯЗНУЛЬКИ?", 960, 150)
    title = (stext(540, 300, "КТО ТАКИЕ", 104, sc=s1 * (1 + 0.03 * beat(t)), rot=wob * 0.5)
             + stext(540, 455, "ГРЯЗНУЛЬКИ?", sz, fill="#FFD23F", sc=s2 * (1 + 0.04 * beat(t)), rot=-4 + wob))
    gx, gy = 540, 1400
    if t < 0.2:
        return "".join(out) + title
    if t < EV["land1"]:
        p = e_in(prog(t, 0.2, EV["land1"])); y = lerp(-300, gy, p); sq = -0.35
    elif t < 2.7:
        y = gy; sq = damp(t, EV["land1"], 0.9) + 0.03 * math.sin(t * 9)
    else:
        p = prog(t, 2.7, 3.0)
        sq = 0.45 * math.sin(min(p * 2, 1) * math.pi / 2) if p < 0.5 else -0.4
        y = gy - (0 if p < 0.5 else 900 * e_in((p - 0.5) * 2))
    out.append(shadow(gx, gy, 0.95, gy - y))
    out.append(dust(t, EV["land1"], gx, gy))
    out.append(boar(t, gx, y, 0.95, sq=sq, mouth=mouth_at(f), blink=is_blink(t), brow=0.35,
                    headrot=3 * math.sin(t * math.pi * 2)))
    return "".join(out) + title


def scene_define(t, f):
    out = [bg_meadow(t), puddle_back()]
    gx, gy = 540, 1430
    out.append(ripples(t, EV["splash1"], gx, gy - 10))
    if t < EV["splash1"]:
        p = prog(t, 3.0, EV["splash1"])
        x = lerp(160, gx, p); y = lerp(380, gy, e_in(p)); rot = lerp(-35, 0, p); sq = -0.35; mud = 0
    else:
        x, y, rot = gx, gy, 0; sq = damp(t, EV["splash1"], 1.0) + 0.03 * math.sin(t * 9)
        mud = e_out(prog(t, EV["splash1"], EV["splash1"] + 0.15))
    look = (0, -1) if 3.6 < t < 4.4 else (0, 0)
    brow = 1.0 if t > EV["stamp"] else 0.3
    out.append(boar(t, x, y, 0.95, sq=sq, rot=rot, mud=mud, mouth=mouth_at(f), blink=is_blink(t), look=look, brow=brow))
    out.append(puddle_front(t))
    out.append(splash_parts(t, EV["splash1"], gx, gy - 60, 48, 11, gy + 80))
    # dictionary card
    if t >= EV["card"]:
        p = e_back(prog(t, EV["card"], EV["card"] + 0.4)); cy = lerp(-420, 175, p)
        out.append(f'<g transform="translate(90,{cy:.1f}) rotate(-2)">'
                   '<rect x="12" y="16" width="900" height="420" rx="36" fill="#2A120A"/>'
                   '<rect x="0" y="0" width="900" height="420" rx="36" fill="#FFF8EC" stroke="#2A120A" stroke-width="8"/>')
        out.append(stext(450, 95, "ГРЯЗНУЛЬКА", fit("ГРЯЗНУЛЬКА", 800, 120), fill="#6B4226", sw=0, shadow=False))
        out.append(stext(450, 180, "сленг, мем осени 2026", 40, fill="#9A7B66", sw=0, shadow=False))
        out.append(f'<line x1="70" y1="225" x2="830" y2="225" stroke="#E5D3BE" stroke-width="5"/>')
        out.append(stext(450, 285, "= BADDIE по-русски:", 54, fill="#2A120A", sw=0, shadow=False))
        out.append(stext(450, 360, "дерзкая, уверенная, хаос", 50, fill="#2A120A", sw=0, shadow=False))
        out.append("</g>")
        if t >= EV["stamp"]:
            p = prog(t, EV["stamp"], EV["stamp"] + 0.18); sc = lerp(3.0, 1.0, e_out(p)); op = clamp(p * 3)
            out.append(f'<g opacity="{op:.2f}">' + burst(860, 690, 105, 12, "#FF3B3B", seed=5, rot=-14, sc=sc)
                       + stext(860, 690, "BADDIE", 44, fill="#fff", rot=-14, sc=sc, sw=9) + "</g>")
    return "".join(out)


def scene_zoom(t, f):
    out = [bg_vapor(t)]
    gx, gy = 540, 1420
    for k in range(10):  # floating alt-girl sparkles & hearts
        rr = random.Random(k); px = rr.choice([rr.uniform(90, 330), rr.uniform(750, 990)]); sp = rr.uniform(90, 160)
        py = 1250 - ((t - 6.3) * sp + rr.uniform(0, 500)) % 700
        if k % 2: out.append(heart(px, py, 0.55, "#FF5CC8", op=0.9))
        else: out.append(star4(px, py, 30, "#00F0FF", rot=t * 120 + k * 20))
    out.append(shadow(gx, gy, 0.92))
    sd = lerp(-900, 0, e_bounce(prog(t, EV["shades"] - 0.35, EV["shades"]))) if t > EV["shades"] - 0.35 else None
    out.append(boar(t, gx, gy, 0.92, sq=0.04 * math.sin(t * 4 * math.pi), mud=1, mouth=mouth_at(f), blink=False if sd is not None else is_blink(t),
                    headrot=6 * math.sin(t * 2 * math.pi), brow=0.6, shades_dy=sd))
    out.append(pill(540, 230, "ДЛЯ ЗУМЕРОВ", 64, "#00F0FF", INK, sc=popscale(t, EV["chip_z"]), rot=-3))
    sv = popscale(t, EV["vibe"])
    out.append(stext(540, 420, "АЛЬТУШКА", fit("АЛЬТУШКА", 900, 130), fill="#FF5CC8", sc=sv, rot=2 + math.sin(t * 5)))
    if t >= EV["allowed"]:
        sc = popscale(t, EV["allowed"], 0.3); rot = -8 + 2 * math.sin(t * 6)
        out.append(burst(820, 750, 240, 14, "#00F0FF", seed=17, sc=sc, rot=rot, ry=175))
        out.append(stext(820, 712, "МНЕ ВСЁ", 52, fill=INK, sw=0, shadow=False, sc=sc, rot=rot))
        out.append(stext(820, 785, "МОЖНО", 64, fill="#FF2BD6", sw=0, shadow=False, sc=sc, rot=rot))
    return "".join(out)


def scene_skuf(t, f):
    out = [bg_carpet(t)]
    gx, gy = 610, 1440
    out.append(shadow(gx, gy, 0.92))
    cd = lerp(-900, 0, e_bounce(prog(t, EV["cap"] - 0.35, EV["cap"]))) if t > EV["cap"] - 0.35 else None
    hr = damp(t, EV["hit"], 26, freq=18, k=4) if t > EV["hit"] else 2 * math.sin(t * 3)
    brow = -0.8 if t > EV["hit"] else 0.2
    look = (-1, -0.3) if EV["shout"] < t < EV["hit"] else (0, 0)
    out.append(boar(t, gx, gy, 0.92, sq=0.03 * math.sin(t * 9), mud=1, mouth=mouth_at(f), blink=is_blink(t),
                    headrot=hr, brow=brow, cap_dy=cd, look=look))
    out.append(pill(540, 240, "ДЛЯ СКУФОВ", 64, "#F2C14E", INK, sc=popscale(t, EV["chip_s"]), rot=3))
    if t >= EV["shout"]:
        sc = popscale(t, EV["shout"], 0.3); jx = 6 * math.sin(t * 60); jy = 5 * math.cos(t * 47)
        out.append(f'<g transform="translate({jx:.1f},{jy:.1f})">')
        out.append(f'<polygon points="60,560 -40,700 180,620" fill="#fff" stroke="{INK}" stroke-width="10" stroke-linejoin="round" opacity="{min(sc, 1):.2f}"/>')
        out.append(burst(470, 570, 440, 16, "#fff", seed=9, sc=sc, ry=210))
        out.append(stext(470, 510, "НУ И", 84, fill="#E23B3B", sc=sc, sw=0, shadow=False))
        out.append(stext(470, 610, "ОТОРВА!", fit("ОТОРВА!", 640, 120), fill="#E23B3B", sc=sc, sw=0, shadow=False))
        out.append(stext(470, 700, "— соседка, 1998 г.", 38, fill="#6B5B52", sc=sc, sw=0, shadow=False))
        out.append("</g>")
    if t >= EV["slipper"]:
        th = EV["hit"]
        if t < th:
            p = prog(t, EV["slipper"], th); x = lerp(-150, 560, p); y = lerp(760, 1000, p) - 160 * math.sin(math.pi * p); rot = 900 * p
        else:
            dt = t - th; x = 560 - 500 * dt; y = 1000 - 700 * dt + 2400 * dt * dt; rot = 900 - 600 * dt
        out.append(slipper(x, y, rot))
        if t > th:
            dt = t - th
            out.append(burst(820, 860, 120, 10, "#FFD23F", seed=4, sc=popscale(t, th, 0.2) * clamp(1.5 - dt), rot=8))
            out.append(stext(820, 860, "БАМ!", 60, fill=INK, sw=0, shadow=False, sc=popscale(t, th, 0.2) * clamp(1.5 - dt), rot=8))
            for k in range(4):
                a = t * 7 + k * math.pi / 2
                out.append(star4(gx + math.cos(a) * 190, gy - 600 + math.sin(a) * 50, 26, "#FFD23F", rot=t * 200))
    return "".join(out)


def scene_outro(t, f):
    out = [bg_meadow(t, sunset=True), puddle_back()]
    gx, gy = 540, 1430
    out.append(ripples(t, EV["land2"], gx, gy - 10)); out.append(ripples(t, EV["hru"], gx, gy - 10))
    if t < EV["land2"]:
        p = prog(t, 11.8, EV["land2"]); y = lerp(300, gy, e_in(p)); sq = -0.35
    else:
        y = gy; sq = damp(t, EV["land2"], 0.9) + damp(t, EV["hru"], 0.7) + 0.03 * math.sin(t * 9)
    sd = lerp(-900, 0, e_bounce(prog(t, EV["shades2"] - 0.3, EV["shades2"]))) if t > EV["shades2"] - 0.3 else None
    for k in range(6):  # hearts
        st = EV["land2"] + 0.3 + k * 0.4
        if t > st:
            dt = t - st; hx = gx + (-1) ** k * (160 + 40 * k) + 25 * math.sin(dt * 4)
            out.append(heart(hx, gy - 500 - 260 * dt, 0.9 + 0.1 * k % 3, "#FF5C8A", op=clamp(2 - dt)))
    out.append(boar(t, gx, y, 0.95, sq=sq, mud=1, mouth=mouth_at(f), blink=is_blink(t) and sd is None, brow=0.5,
                    headrot=4 * math.sin(t * 2 * math.pi), shades_dy=sd))
    out.append(puddle_front(t))
    out.append(splash_parts(t, EV["land2"], gx, gy - 60, 44, 21, gy + 80))
    out.append(splash_parts(t, EV["hru"], gx, gy - 60, 30, 31, gy + 80))
    if EV["tozhe"] <= t < EV["hru"]:
        sc = popscale(t, EV["tozhe"])
        out.append(stext(540, 330, "Я ТОЖЕ", 110, sc=sc, rot=-3))
        out.append(stext(540, 470, "ГРЯЗНУЛЬКА", fit("ГРЯЗНУЛЬКА", 940, 130), fill="#FFD23F", sc=sc, rot=-3))
    if EV["hru"] <= t < EV["end"] + 0.2:
        sc = popscale(t, EV["hru"], 0.3) * (1 - e_in(prog(t, EV["end"], EV["end"] + 0.2)))
        out.append(burst(540, 420, 330, 14, "#FFD23F", seed=12, sc=sc, rot=t * 20))
        out.append(stext(540, 420, "ХРЮ!", 190, fill="#FF5C8A", sc=sc, rot=-6))
    if t >= EV["end"]:
        s1 = popscale(t, EV["end"]); s2 = popscale(t, EV["end"] + 0.15)
        pulse = 1 + 0.05 * math.sin((t - EV["end"]) * 10)
        out.append(stext(540, 300, "ПОДПИШИСЬ,", fit("ПОДПИШИСЬ,", 900, 120), sc=s1, rot=-3))
        out.append(pill(540, 480, "ГРЯЗНУЛЬКА!", 86, "#FF3B5C", "#fff", sc=s2 * pulse, rot=2))
    return "".join(out)


SCENE_FN = {"intro": scene_intro, "define": scene_define, "zoom": scene_zoom, "skuf": scene_skuf, "outro": scene_outro}


HANDLE = "@deykun1337"


def watermark():
    size = 40; w = tw(HANDLE, size); x0 = 540 - (w + 62) / 2; y = 110
    icon = (f'<g transform="translate({x0:.1f},{y - 25})" fill="none" stroke="#fff" stroke-width="5">'
            '<rect x="2" y="2" width="46" height="46" rx="14"/><circle cx="25" cy="25" r="11"/>'
            '<circle cx="37.5" cy="12.5" r="2.5" fill="#fff" stroke="none"/></g>')
    shadow_icon = icon.replace(f'translate({x0:.1f},{y - 25})', f'translate({x0 + 3:.1f},{y - 22})').replace('#fff', '#000')
    return (f'<g opacity="0.85"><g opacity="0.45">{shadow_icon}</g>{icon}'
            + stext(x0 + 62, y, HANDLE, size, fill="#fff", stroke="#000", sw=7, shadow=False, anchor="start") + "</g>")


WATERMARK = None


def WM():
    global WATERMARK
    if WATERMARK is None: WATERMARK = watermark()
    return WATERMARK


def frame_svg(f):
    t = f / FPS
    name = next(n for a, b, n in SCENES if a <= t < b) if t < DUR else "outro"
    dx, dy = shake(t)
    body = SCENE_FN[name](t, f)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}'
            f'<rect width="{W}" height="{H}" fill="#000"/>'
            f'<g transform="translate({dx:.1f},{dy:.1f}) translate(540,960) scale(1.03) translate(-540,-960)">{body}</g>'
            f'<rect width="{W}" height="{H}" fill="url(#gVig)"/>'
            f'{wipe(t)}{subtitles(t)}{WM()}</svg>')


def render(f):
    cairosvg.svg2png(bytestring=frame_svg(f).encode(), write_to=f"build/frames/{f:04d}.png")
    return f


if __name__ == "__main__":
    os.makedirs("build/frames", exist_ok=True)
    frames = [int(x) for x in sys.argv[1:]] or list(range(NFRAMES))
    with Pool(os.cpu_count()) as pool:
        for i, _ in enumerate(pool.imap_unordered(render, frames, chunksize=4)):
            if i % 50 == 0: print("frame", i, flush=True)
    print("done", len(frames))
