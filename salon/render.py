"""«Удалила таблицу» — shot/reverse-shot dialogue: nail-salon girl + Никита Скуф Скуфыч. 60 fps render."""
import math, os, random, sys
from multiprocessing import Pool
import cairosvg
import base
from base import (tw, fit, clamp, prog, lerp, e_out, e_in, e_back, popscale, damp, stext, star4, boar, is_blink, mouth_at, INK, FONT)
from kit import e_inout, PINK, LIME, CYAN, YEL
import medlib
from medlib import polar, mug_svg
from timeline import *

DEFS = medlib.DEFS.replace("</defs>", '''
<linearGradient id="gSalon" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2A1240"/><stop offset="1" stop-color="#7A2E8E"/></linearGradient>
<linearGradient id="gSalon2" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E0F33"/><stop offset="1" stop-color="#5B2A78"/></linearGradient>
<radialGradient id="gNeon" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FF7AC8" stop-opacity="0.6"/><stop offset="1" stop-color="#FF7AC8" stop-opacity="0"/></radialGradient>
<linearGradient id="gHair" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7DC8A"/><stop offset="1" stop-color="#E2B95C"/></linearGradient>
<linearGradient id="gTable" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A3626"/><stop offset="1" stop-color="#3A2218"/></linearGradient>
<linearGradient id="gGarage" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2E3238"/><stop offset="1" stop-color="#4A4F57"/></linearGradient>
<radialGradient id="gLamp" cx="0.5" cy="0.2" r="0.8"><stop offset="0" stop-color="#FFE7A8" stop-opacity="0.55"/><stop offset="1" stop-color="#FFE7A8" stop-opacity="0"/></radialGradient>
</defs>''')

SKIN, LIPS, BLUE = "#FAD9C8", "#FF4F8B", "#4FA3E8"


# ---------- backgrounds (soft, out of focus) ----------
def bokeh(seed, n, cols, area=(0, 0, 1080, 1100), rmin=20, rmax=70, op=0.35, t=0):
    rr = random.Random(seed); x0, y0, x1, y1 = area
    return "".join(f'<circle cx="{rr.uniform(x0, x1) + 6 * math.sin(t + k):.0f}" cy="{rr.uniform(y0, y1):.0f}" r="{rr.uniform(rmin, rmax):.0f}" fill="{rr.choice(cols)}" opacity="{op * rr.uniform(0.4, 1):.2f}"/>' for k in range(n))


def shelves(x, y, w, rows, seed, op=0.75):
    rr = random.Random(seed); out = [f'<g opacity="{op}">']
    for r in range(rows):
        yy = y + r * 150
        out.append(f'<rect x="{x}" y="{yy + 95}" width="{w}" height="16" rx="6" fill="#F4E9F7"/>')
        for k in range(int(w / 46)):
            c = rr.choice(["#FF4F8B", "#C2185B", "#F06292", "#BA68C8", "#FF8A65", "#E91E63", "#F8BBD0", "#7E57C2"])
            bx = x + 12 + k * 46
            out.append(f'<rect x="{bx}" y="{yy + 40}" width="30" height="55" rx="8" fill="{c}"/><rect x="{bx + 8}" y="{yy + 18}" width="14" height="24" rx="3" fill="#2A1A22"/>')
    out.append("</g>")
    return "".join(out)


def salon_bg(t, side=0):
    if side == 0:  # behind the girl
        return ('<rect width="1080" height="1920" fill="url(#gSalon)"/>' + bokeh(1, 14, ["#FFD1F0", "#B388FF", "#FFF"], t=t * 0.5)
                + '<rect x="40" y="120" width="420" height="560" rx="20" fill="#120A24" opacity="0.8"/>' + bokeh(2, 18, [YEL, "#FFB74D", "#fff", CYAN], (60, 140, 440, 660), 6, 18, 0.8, t)
                + shelves(560, 180, 520, 5, 3)
                + '<circle cx="250" cy="880" r="260" fill="url(#gNeon)"/>'
                + '<path transform="translate(250,860) scale(2.2)" d="M0 30 C -60 -10 -40 -60 0 -30 C 40 -60 60 -10 0 30 Z" fill="none" stroke="#FF8AD8" stroke-width="7" opacity="0.9"/>'
                + '<text x="420" y="900" font-family="DejaVu Sans" font-style="italic" font-size="78" fill="#FFB3E6" opacity="0.9">nails</text>'
                + '<rect width="1080" height="1920" fill="#1A0A2A" opacity="0.25"/>')
    return ('<rect width="1080" height="1920" fill="url(#gSalon2)"/>' + shelves(0, 150, 470, 6, 7)
            + '<rect x="560" y="140" width="480" height="760" rx="20" fill="#0E0A1E" opacity="0.85"/>' + bokeh(5, 22, [YEL, "#FFB74D", "#fff", PINK], (580, 160, 1020, 880), 6, 20, 0.8, t)
            + '<circle cx="800" cy="200" r="300" fill="url(#gLamp)"/>' + bokeh(6, 10, ["#FFD1F0", "#B388FF"], t=t * 0.4)
            + '<rect width="1080" height="1920" fill="#1A0A2A" opacity="0.25"/>')


# ---------- the girl (own cartoon) ----------
EXPR = {0: "sad", 2: "shock", 4: "smug", 6: "angry", 8: "roll", 10: "plead", 12: "happy", 14: "panic", 16: "shock", 18: "touched", 19: "sweet"}


def girl(cx, cy, s, t, mouth=0.0, expr="neutral", hand=0.0):
    blink = is_blink(t + 1.3) and expr not in ("happy", "roll")
    o = [f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s:.3f})">']
    o.append('<path d="M -235 -70 Q -250 -320 0 -325 Q 250 -320 235 -70 L 265 360 L -265 360 Z" fill="url(#gHair)"/>')
    o.append(f'<rect x="-48" y="130" width="96" height="140" fill="#F2C4AE"/>')
    o.append('<path d="M -360 620 Q -340 290 -100 255 L 100 255 Q 340 290 360 620 Z" fill="#FF6FB1"/>')
    o.append('<path d="M -100 255 L -10 330 L -60 250 Z M 100 255 L 10 330 L 60 250 Z" fill="#FFD3E8" stroke="#E0559A" stroke-width="5"/>')
    o.append('<path d="M -42 230 Q 0 270 42 230" stroke="#E8A98F" stroke-width="6" fill="none"/>')
    for sg in (-1, 1):
        o.append(f'<ellipse cx="{sg * 150}" cy="10" rx="20" ry="32" fill="{SKIN}"/><circle cx="{sg * 154}" cy="58" r="16" fill="none" stroke="#E6B84A" stroke-width="6"/>')
    o.append(f'<ellipse cx="0" cy="0" rx="150" ry="178" fill="{SKIN}"/>')
    for sg in (-1, 1):
        o.append(f'<ellipse cx="{sg * 92}" cy="62" rx="36" ry="20" fill="#FF8FB0" opacity="0.45"/>')
    # eyes
    for sg in (-1, 1):
        ex, ey = sg * 62, -12
        look = 0
        if expr == "roll": look = -1
        if blink or expr == "happy":
            o.append(f'<g transform="translate({ex},{ey}) scale({sg},1)"><path d="M -40 2 Q 0 {-22 if expr == "happy" else 18} 40 2" stroke="#2A1A22" stroke-width="7" fill="none" stroke-linecap="round"/>'
                     '<path d="M 30 -4 l 18 -12 M 22 -10 l 12 -16 M 12 -14 l 6 -18" stroke="#2A1A22" stroke-width="5" stroke-linecap="round"/></g>')
            continue
        wide = {"shock": 1.35, "panic": 1.3, "plead": 1.15}.get(expr, 1.0)
        lid = {"smug": 0.45, "angry": 0.3, "touched": 0.2}.get(expr, 0.0)
        o.append(f'<g transform="translate({ex},{ey}) scale({sg},1)">'
                 f'<ellipse cx="0" cy="0" rx="42" ry="{30 * wide:.1f}" fill="#fff"/>'
                 f'<circle cx="2" cy="{2 + look * 12}" r="{22 * min(wide, 1.15):.1f}" fill="{BLUE}"/><circle cx="2" cy="{2 + look * 12}" r="11" fill="#0E1A2A"/>'
                 f'<circle cx="10" cy="{-6 + look * 12}" r="6" fill="#fff"/>'
                 + (f'<rect x="-46" y="{-34 * wide:.1f}" width="92" height="{60 * wide * lid:.1f}" fill="{SKIN}"/>' if lid else "")
                 + f'<path d="M -44 {-2 - 30 * wide * (1 - lid) + 30 * wide * lid * 0.9:.1f} Q 0 {-34 * wide * (1 - lid) - 10 + 60 * wide * lid * 0.6:.1f} 44 {-4 - 30 * wide * (1 - lid) + 30 * wide * lid * 0.9:.1f}" stroke="#2A1A22" stroke-width="8" fill="none" stroke-linecap="round"/>'
                 + f'<path d="M 36 {-14 - 20 * (wide - 1):.1f} l 20 -14 M 26 {-22 - 20 * (wide - 1):.1f} l 12 -18 M 14 {-26 - 20 * (wide - 1):.1f} l 6 -20" stroke="#2A1A22" stroke-width="5" stroke-linecap="round"/>'
                 + f'<path d="M -30 {30 * wide:.1f} Q 0 {38 * wide:.1f} 30 {30 * wide:.1f}" stroke="#2A1A22" stroke-width="3" fill="none" opacity="0.5"/></g>')
    # brows
    bt = {"angry": 16, "panic": -14, "shock": -18, "plead": -16, "sad": -10, "touched": -8}.get(expr, 0)
    by = -78 - (14 if expr in ("shock", "panic") else 0)
    for sg in (-1, 1):
        o.append(f'<path d="M {sg * 100} {by - 4} Q {sg * 66} {by - 18} {sg * 28} {by + bt}" stroke="#C99A4A" stroke-width="9" fill="none" stroke-linecap="round"/>')
    o.append('<path d="M -6 40 Q 0 62 12 58" stroke="#E0A58E" stroke-width="5" fill="none" stroke-linecap="round"/>')
    # lips
    m = mouth
    if m > 0.08:
        o.append(f'<ellipse cx="0" cy="112" rx="{40 + 8 * m:.1f}" ry="{8 + 24 * m:.1f}" fill="#7A1B3A" stroke="{LIPS}" stroke-width="12"/>')
        if m > 0.35: o.append(f'<rect x="-26" y="{112 - 8 - 24 * m + 6:.1f}" width="52" height="10" rx="4" fill="#fff"/>')
    else:
        if expr in ("happy", "sweet", "smug", "touched"):
            o.append(f'<path d="M -46 104 Q 0 140 46 104 Q 0 124 -46 104 Z" fill="{LIPS}" stroke="#C2185B" stroke-width="4"/>')
        elif expr in ("sad", "panic", "plead"):
            o.append(f'<path d="M -40 122 Q 0 98 40 122 Q 0 112 -40 122 Z" fill="{LIPS}" stroke="#C2185B" stroke-width="4"/>')
        else:
            o.append(f'<path d="M -42 110 Q -20 98 0 106 Q 20 98 42 110 Q 0 132 -42 110 Z" fill="{LIPS}" stroke="#C2185B" stroke-width="4"/>')
        o.append('<ellipse cx="-14" cy="108" rx="10" ry="4" fill="#fff" opacity="0.6"/>')
    # bangs & strands
    o.append('<path d="M -168 -40 Q -170 -240 0 -250 Q 175 -245 168 -30 Q 140 -150 40 -165 Q -40 -150 -100 -90 Q -140 -60 -168 -40 Z" fill="url(#gHair)"/>')
    o.append('<path d="M -40 -170 Q 30 -120 120 -150" stroke="#FFF1C2" stroke-width="10" fill="none" opacity="0.7" stroke-linecap="round"/>')
    o.append('<path d="M -165 -40 Q -195 120 -170 290 L -130 290 Q -150 120 -132 -20 Z" fill="url(#gHair)"/>')
    o.append('<path d="M 165 -40 Q 195 120 170 290 L 130 290 Q 150 120 132 -20 Z" fill="url(#gHair)"/>')
    if hand > 0:
        hy = lerp(420, 120, e_out(hand))
        o.append(f'<g transform="translate(250,{hy:.0f}) rotate(-15)"><rect x="-55" y="-10" width="110" height="200" rx="50" fill="{SKIN}" stroke="#E0A58E" stroke-width="5"/>'
                 + "".join(f'<rect x="{-50 + k * 26}" y="-90" width="22" height="95" rx="11" fill="{SKIN}" stroke="#E0A58E" stroke-width="4"/><rect x="{-48 + k * 26}" y="-112" width="18" height="38" rx="9" fill="#FF2E88"/>' for k in range(4))
                 + "</g>")
    o.append("</g>")
    return "".join(o)


# ---------- inserts ----------
def table_bg():
    return '<rect width="1080" height="1920" fill="url(#gTable)"/>' + "".join(f'<line x1="0" y1="{y}" x2="1080" y2="{y + 40}" stroke="#2A170F" stroke-width="5" opacity="0.6"/>' for y in range(80, 1920, 170))


def usb(t, t0):
    p = e_out(prog(t, t0 - 0.1, t0 + 0.6))
    return (table_bg() + '<circle cx="540" cy="900" r="700" fill="url(#gLamp)"/>'
            f'<g transform="translate(540,900) rotate({lerp(-25, -12, p):.1f}) scale({lerp(2.0, 2.25, p):.3f})">'
            '<rect x="-150" y="-60" width="300" height="120" rx="26" fill="#000" opacity="0.35" transform="translate(16,20)"/>'
            '<rect x="150" y="-38" width="90" height="76" rx="6" fill="#C9CED6" stroke="#6B7280" stroke-width="6"/><rect x="175" y="-18" width="20" height="14" fill="#6B7280"/><rect x="205" y="-18" width="20" height="14" fill="#6B7280"/>'
            '<rect x="-150" y="-60" width="300" height="120" rx="26" fill="#2D6CDF" stroke="#173E87" stroke-width="7"/>'
            '<rect x="-115" y="-36" width="210" height="72" rx="8" fill="#FFFDF2"/>'
            '<text x="-10" y="18" font-family="DejaVu Sans" font-style="italic" font-weight="bold" font-size="50" fill="#1B2A6B" text-anchor="middle">КОПИЯ</text>'
            '<circle cx="-128" cy="0" r="10" fill="#173E87"/></g>')


def photo(t, t0):
    p = e_back(prog(t, t0 - 0.1, t0 + 0.4), 1.4)
    fish = ('<g transform="translate(150,-10) rotate(-20)"><path d="M -150 0 Q -40 -80 120 0 Q -40 80 -150 0 Z" fill="#9FB8C8" stroke="#3E5566" stroke-width="7"/>'
            '<path d="M 110 0 L 180 -50 L 170 0 L 180 50 Z" fill="#9FB8C8" stroke="#3E5566" stroke-width="7"/><circle cx="-110" cy="-10" r="10" fill="#111"/></g>')
    return (table_bg() + '<circle cx="540" cy="900" r="700" fill="url(#gLamp)"/>'
            f'<g transform="translate(540,{lerp(1500, 900, p):.0f}) rotate({lerp(15, -5, p):.1f}) scale(1.35)">'
            '<rect x="-290" y="-330" width="580" height="680" rx="12" fill="#000" opacity="0.35" transform="translate(16,20)"/>'
            '<rect x="-300" y="-340" width="600" height="680" rx="12" fill="#FBFAF4"/>'
            '<rect x="-270" y="-310" width="540" height="520" fill="#8EC5E8"/><rect x="-270" y="40" width="540" height="170" fill="#3E7CA6"/>'
            '<circle cx="180" cy="-220" r="50" fill="#FFF3B0"/>'
            '<g transform="translate(-60,0)">' + boar(t, 0, 200, 0.62, mouth=0, outfit=True, cap_dy=0, brow=0.8, blink=False) + fish + '</g>'
            '<text x="0" y="290" font-family="DejaVu Sans" font-style="italic" font-size="44" fill="#2A1A22" text-anchor="middle">рыбалка, 2019 🐟</text></g>').replace(" 🐟", "")


def paper(t, t0):
    p = e_out(prog(t, t0 - 0.1, t0 + 0.6))
    rows = ["Маша — 12:00 гель", "Катя — 15:00 снятие", "Оля — 18:00 френч ❤", "Лена — 19:30 наращ.", "Зина (?) — пятница"]
    out = [table_bg(), '<circle cx="540" cy="900" r="700" fill="url(#gLamp)"/>',
           f'<g transform="translate(540,1080) rotate({lerp(-8, -3, p):.1f}) scale({lerp(1.05, 1.12, p):.3f})">',
           '<rect x="-330" y="-470" width="660" height="900" rx="8" fill="#000" opacity="0.35" transform="translate(16,20)"/>',
           '<rect x="-330" y="-470" width="660" height="900" rx="8" fill="#FFFEF5"/>']
    for k in range(13): out.append(f'<line x1="-330" y1="{-380 + k * 64}" x2="330" y2="{-380 + k * 64}" stroke="#A8C8F0" stroke-width="3"/>')
    out.append('<line x1="-250" y1="-470" x2="-250" y2="430" stroke="#F28B82" stroke-width="4"/>')
    out.append('<text x="-230" y="-400" font-family="DejaVu Sans" font-style="italic" font-weight="bold" font-size="46" fill="#2B4FBF">ЗАПИСИ (ФИНАЛ)</text>')
    for k, r in enumerate(rows):
        out.append(f'<text x="-230" y="{-300 + k * 128}" font-family="DejaVu Sans" font-style="italic" font-size="42" fill="#2B4FBF">{r.replace("❤", "")}</text>')
    out.append('<circle cx="190" cy="300" r="95" fill="none" stroke="#C88A3E" stroke-width="14" opacity="0.45"/>')
    out.append("</g>")
    return "".join(out)


def garage(t, t0, f):
    z = 1 + 0.05 * prog(t, t0, DUR)
    out = [f'<g transform="translate(540,1000) scale({z:.4f}) translate(-540,-1000)">',
           '<rect width="1080" height="1920" fill="url(#gGarage)"/>',
           '<rect x="0" y="1380" width="1080" height="540" fill="#3A3D42"/><ellipse cx="300" cy="1600" rx="200" ry="40" fill="#24262A" opacity="0.7"/>']
    for k in range(4):
        out.append(f'<rect x="60" y="{260 + k * 190}" width="380" height="16" fill="#8A6A4A"/>')
        for j in range(4): out.append(f'<rect x="{80 + j * 90}" y="{200 + k * 190}" width="60" height="60" rx="6" fill="{["#C0392B", "#7F8C8D", "#2980B9", "#D35400"][(k + j) % 4]}"/>')
    out.append('<rect x="640" y="200" width="380" height="300" fill="#24262A"/><path d="M 660 230 L 990 230" stroke="#555" stroke-width="10"/>')
    for k, tl in enumerate(("M 690 280 l 0 160", "M 760 280 l 0 160", "M 840 280 l 30 160", "M 930 280 l -20 160")): out.append(f'<path d="{tl}" stroke="#9AA3AD" stroke-width="14" stroke-linecap="round"/>')
    out.append('<circle cx="540" cy="120" r="480" fill="url(#gLamp)"/><line x1="540" y1="0" x2="540" y2="80" stroke="#222" stroke-width="6"/><circle cx="540" cy="95" r="26" fill="#FFF3C4"/>')
    # stool with the paper, guarded by Медведь Скуфыч
    out.append('<rect x="210" y="1300" width="200" height="30" rx="8" fill="#7A5230"/><rect x="225" y="1330" width="20" height="200" fill="#5A3A20"/><rect x="375" y="1330" width="20" height="200" fill="#5A3A20"/>')
    out.append('<rect x="240" y="1270" width="140" height="40" rx="4" fill="#FFFEF5" transform="rotate(-6 310 1290)"/>')
    out.append(polar(690, 1640, 1.02, t, mouth=0, outfit=1, cap_dy=0, tilt=3 * math.sin(t * 2), mug_p=1))
    out.append('</g>')
    return "".join(out)


def wide(t, f, i):
    jump = abs(math.sin((t - VOICE_START[i]) * 9)) * 40
    out = [salon_bg(t, 0), '<rect x="0" y="1300" width="1080" height="620" fill="#3A1F33"/>',
           girl(330, 780 - jump, 0.66, t, mouth=mouth_at(int(t * FPS)), expr="panic", hand=1),
           '<rect x="80" y="1180" width="920" height="60" rx="16" fill="#F4E9F7"/><rect x="140" y="1240" width="40" height="300" fill="#C9B3D6"/><rect x="900" y="1240" width="40" height="300" fill="#C9B3D6"/>',
           '<rect x="420" y="1090" width="180" height="90" rx="20" fill="#fff"/><rect x="440" y="1110" width="140" height="30" rx="8" fill="#B388FF" opacity="0.7"/>']
    out.append(boar(t, 800, 1250, 0.52, mouth=0, outfit=True, cap_dy=0, brow=0.2, blink=is_blink(t), look=(-1, 0)))
    return "".join(out)


# ---------- camera & captions ----------
def wrap(txt, size, maxw):
    words = txt.split(); lines = [""]
    for w in words:
        cand = (lines[-1] + " " + w).strip()
        if tw(cand, size) <= maxw or not lines[-1]: lines[-1] = cand
        else: lines.append(w)
    return lines


def caption(t):
    i = line_at(t)
    if t < VOICE_START[i] - 0.08 or t > VOICE_END[i] + 0.45: return ""
    txt = base.VOICE_TEXT[i]
    size = 62; lines = wrap(txt, size, 920)
    op = clamp((t - VOICE_START[i] + 0.08) * 10)
    out = []
    for k, ln in enumerate(lines):
        y = 320 + k * size * 1.22
        out.append(stext(540, y, ln, size, fill="#fff", stroke="#000", sw=11, shadow=False, op=op).replace(FONT, "Inter Display ExtraBold"))
    return "".join(out)


def frame_svg(f):
    t = f / FPS
    shot, i = shot_at(t)
    st = VOICE_START[i] - 0.08
    push = 1 + 0.06 * e_inout(clamp((t - st) / 3.0))
    sway_x = 8 * math.sin(t * 0.9) + 4 * math.sin(t * 2.3); sway_y = 6 * math.sin(t * 1.1)
    speaking = VOICE_START[i] <= t <= VOICE_END[i] + 0.1
    m = mouth_at(f) if speaking else 0.0
    if shot == "girl":
        body = (f'<g transform="translate({-sway_x * 0.5:.1f},0)">{salon_bg(t, 0)}</g>'
                + girl(540 + sway_x, 1120 + sway_y, 1.55, t, mouth=m, expr=EXPR.get(i, "neutral"), hand=prog(t, st, st + 0.4) if i in (10, 14, 19) else 0))
    elif shot == "nik":
        brow = {1: 0.2, 3: 0.3, 5: 0.0, 7: 0.4, 9: 0.2, 17: 0.9}.get(i, 0.2)
        body = (f'<g transform="translate({-sway_x * 0.5:.1f},0)">{salon_bg(t, 1)}</g>'
                + boar(t, 540 + sway_x, 1880 + sway_y, 1.75, mouth=m, outfit=True, cap_dy=0, brow=brow, blink=is_blink(t), headrot=2 * math.sin(t * 1.5)))
    elif shot == "usb": body = usb(t, VOICE_START[i])
    elif shot == "photo": body = photo(t, VOICE_START[i])
    elif shot == "paper": body = paper(t, VOICE_START[i])
    elif shot == "wide": body = wide(t, f, i)
    else: body = garage(t, VOICE_START[i], f)
    cam = f'translate(540,1000) scale({push:.4f}) translate(-540,-1000)'
    fade_in = f'<rect width="1080" height="1920" fill="#000" opacity="{1 - clamp(t * 3):.2f}"/>' if t < 0.4 else ""
    fade_out = f'<rect width="1080" height="1920" fill="#000" opacity="{clamp((t - DUR + 0.6) / 0.6):.2f}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}'
            f'<rect width="{W}" height="{H}" fill="#000"/><g transform="{cam}">{body}</g>'
            f'<rect width="{W}" height="{H}" fill="url(#gVig)"/>{caption(t)}{fade_in}{fade_out}{base.WM()}</svg>')


def render(f):
    cairosvg.svg2png(bytestring=frame_svg(f).encode(), write_to=f"build/frames/{f:05d}.png")
    return f


if __name__ == "__main__":
    os.makedirs("build/frames", exist_ok=True)
    frames = [int(x) for x in sys.argv[1:]] or list(range(NFRAMES))
    with Pool(os.cpu_count()) as pool:
        for i, _ in enumerate(pool.imap_unordered(render, frames, chunksize=4)):
            if i % 500 == 0: print("frame", i, flush=True)
    print("done", len(frames))
