"""«Ноябрь 2026 наступил» — the polar bear meme meets Никита Скуф Скуфыч. 60 fps render, seamless loop."""
import math, os, random, sys
from multiprocessing import Pool
import cairosvg
import base
from base import (tw, fit, clamp, prog, lerp, e_out, e_in, e_back, e_bounce, popscale, damp, stext, pill,
                  burst, star4, boar, shadow, is_blink, mouth_at, INK, FONT, escape)
from kit import (ktext, marker, sticker, halftone, floaters, ring, stripes_wipe, e_inout, PINK, LIME, CYAN, YEL, MONO)
from timeline import *

ICE, NAVY, RED, FOAM = "#BFE6FF", "#0B1026", "#E53935", "#FFF6DC"
SERIF = "DejaVu Serif"

DEFS = base.DEFS.replace("</defs>", '''
<linearGradient id="gNight" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050816"/><stop offset="0.7" stop-color="#16244A"/><stop offset="1" stop-color="#2B3F6E"/></linearGradient>
<linearGradient id="gSnow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#DDEBFA"/><stop offset="1" stop-color="#9FB6D6"/></linearGradient>
<radialGradient id="gMoon" cx="0.5" cy="0.5" r="0.5"><stop offset="0.6" stop-color="#FFFBE8"/><stop offset="1" stop-color="#FFFBE8" stop-opacity="0"/></radialGradient>
<radialGradient id="gFur" cx="0.4" cy="0.3" r="0.8"><stop offset="0" stop-color="#FFFFFA"/><stop offset="0.7" stop-color="#E6EAF0"/><stop offset="1" stop-color="#B8C3D3"/></radialGradient>
<radialGradient id="gSpot" cx="0.5" cy="0.55" r="0.55"><stop offset="0" stop-color="#9FC4FF" stop-opacity="0.35"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<radialGradient id="gDark" cx="0.5" cy="0.5" r="0.7"><stop offset="0.35" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.85"/></radialGradient>
<linearGradient id="gBeer" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E88A00"/><stop offset="0.45" stop-color="#FFC233"/><stop offset="1" stop-color="#D97800"/></linearGradient>
<linearGradient id="gSofa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6E7F45"/><stop offset="1" stop-color="#4A5A2C"/></linearGradient>
<linearGradient id="gTrack2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#34449A"/><stop offset="1" stop-color="#1A2456"/></linearGradient>
</defs>''')


# ---------- night winter ----------
def snow(t, n=70, seed=3, speed=1.0, op=0.9):
    rr = random.Random(seed); out = [f'<g fill="#fff" opacity="{op}">']
    for k in range(n):
        x0 = rr.uniform(0, 1080); y0 = rr.uniform(0, 1920); sp = rr.uniform(80, 220) * speed; r = rr.uniform(3, 9)
        y = (y0 + t * sp) % 1960 - 20; x = x0 + 30 * math.sin(t * 1.3 + k)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}"/>')
    out.append("</g>")
    return "".join(out)


def night(t, ground=1380):
    rr = random.Random(9)
    stars = "".join(f'<circle cx="{rr.uniform(0, 1080):.0f}" cy="{rr.uniform(0, 900):.0f}" r="{rr.uniform(1.5, 3.5):.1f}" fill="#fff" opacity="{0.4 + 0.5 * abs(math.sin(t * 2 + k)):.2f}"/>' for k in range(45))
    return ('<rect width="1080" height="1920" fill="url(#gNight)"/>' + stars +
            '<circle cx="830" cy="330" r="150" fill="url(#gMoon)"/><circle cx="830" cy="330" r="95" fill="#FFFBE8"/>'
            '<circle cx="800" cy="310" r="18" fill="#EDE6C8"/><circle cx="855" cy="360" r="12" fill="#EDE6C8"/>'
            f'<path d="M 0 {ground} Q 270 {ground - 60} 540 {ground - 10} T 1080 {ground - 30} V 1920 H 0 Z" fill="url(#gSnow)"/>')


# ---------- polar bear (own drawing of the meme pose: sitting, front paws straight down) ----------
def polar(cx, cy, s, t, mouth=0.0, outfit=0.0, cap_dy=None, glow=0.0, tilt=0.0, mug_p=0.0):
    out = [f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s:.3f})">']
    for sg in (-1, 1):
        out.append(f'<ellipse cx="{sg * 150}" cy="-62" rx="100" ry="64" fill="url(#gFur)" stroke="#8A97AB" stroke-width="7"/>')
        out.append(f'<ellipse cx="{sg * 205}" cy="-22" rx="50" ry="26" fill="#E6EAF0" stroke="#8A97AB" stroke-width="6"/>')
    out.append('<ellipse cx="0" cy="-270" rx="195" ry="255" fill="url(#gFur)" stroke="#8A97AB" stroke-width="8"/>')
    if outfit > 0:
        o = outfit
        out.append(f'<g opacity="{o:.2f}"><ellipse cx="0" cy="-270" rx="195" ry="255" fill="url(#gTrack2)" stroke="#121A40" stroke-width="8"/>'
                   + "".join(f'<path d="M {sg * (178 - off)} -420 Q {sg * (205 - off)} -270 {sg * (165 - off)} -100" stroke="#fff" stroke-width="13" fill="none" stroke-linecap="round"/>' for sg in (-1, 1) for off in (0, 26))
                   + '<line x1="0" y1="-470" x2="0" y2="-40" stroke="#C9CEDB" stroke-width="7"/></g>')
    # front legs
    for sg in (-1, 1):
        x = sg * 62
        out.append(f'<rect x="{x - 40}" y="-330" width="80" height="320" rx="36" fill="{"url(#gTrack2)" if outfit > 0.5 else "url(#gFur)"}" stroke="#8A97AB" stroke-width="7"/>')
        if outfit > 0.5:
            out.append(f'<line x1="{x + sg * 26}" y1="-320" x2="{x + sg * 26}" y2="-60" stroke="#fff" stroke-width="9"/>')
        out.append(f'<ellipse cx="{x}" cy="-16" rx="52" ry="26" fill="#F4F4EE" stroke="#8A97AB" stroke-width="6"/>')
        for k in (-1, 0, 1): out.append(f'<line x1="{x + k * 16}" y1="-26" x2="{x + k * 16}" y2="-6" stroke="#8A97AB" stroke-width="4"/>')
    if outfit > 0.5:
        for k in range(13):
            u = k / 12; ux = -110 + 220 * u; uy = -470 + 70 * (1 - (2 * u - 1) ** 2)
            out.append(f'<circle cx="{ux:.1f}" cy="{uy:.1f}" r="10" fill="none" stroke="#F2C14E" stroke-width="6"/>')
    # head
    out.append(f'<g transform="rotate({tilt:.2f} 0 -470)">')
    for sg in (-1, 1):
        out.append(f'<circle cx="{sg * 92}" cy="-648" r="34" fill="url(#gFur)" stroke="#8A97AB" stroke-width="7"/><circle cx="{sg * 92}" cy="-648" r="16" fill="#AEB8C8"/>')
    out.append('<ellipse cx="0" cy="-565" rx="125" ry="110" fill="url(#gFur)" stroke="#8A97AB" stroke-width="8"/>')
    out.append('<ellipse cx="0" cy="-515" rx="64" ry="48" fill="#FFFFFA" stroke="#A9B4C4" stroke-width="5"/>')
    for sg in (-1, 1):
        ex = sg * 46
        out.append(f'<circle cx="{ex}" cy="-592" r="11" fill="#0A0A10"/><circle cx="{ex + 3}" cy="-596" r="3.5" fill="#fff"/>')
        if glow > 0:
            out.append(f'<circle cx="{ex}" cy="-592" r="26" fill="#9FC4FF" opacity="{0.35 * glow:.2f}"/>')
    out.append('<ellipse cx="0" cy="-540" rx="24" ry="16" fill="#0A0A10"/><ellipse cx="-7" cy="-545" rx="7" ry="4" fill="#fff" opacity="0.6"/>')
    out.append('<path d="M 0 -524 L 0 -505" stroke="#0A0A10" stroke-width="5"/>')
    if mouth > 0.08:
        out.append(f'<ellipse cx="0" cy="-490" rx="{26 + 6 * mouth:.1f}" ry="{4 + 20 * mouth:.1f}" fill="#2A1218" stroke="#0A0A10" stroke-width="4"/>')
    else:
        out.append('<path d="M -24 -500 Q -12 -490 0 -505 Q 12 -490 24 -500" stroke="#0A0A10" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if cap_dy is not None:
        out.append(f'<g transform="translate(0,{cap_dy:.1f})"><ellipse cx="0" cy="-660" rx="130" ry="52" fill="#4B4B55" stroke="#1E1E24" stroke-width="8"/>'
                   '<path d="M -128 -642 Q 0 -596 128 -642 L 120 -626 Q 0 -572 -120 -626 Z" fill="#33333B" stroke="#1E1E24" stroke-width="7"/>'
                   '<circle cx="0" cy="-708" r="11" fill="#2C2C33"/></g>')
    out.append("</g>")
    if mug_p > 0:
        out.append(f'<g transform="translate(150,-230) scale({0.55 * e_back(mug_p):.3f}) rotate(-8)">{mug_svg(t)}</g>')
    out.append("</g>")
    return "".join(out)


def mug_svg(t, level=1.0):
    bub = "".join(f'<circle cx="{-60 + (k * 37) % 120}" cy="{90 - ((t * 120 + k * 41) % 170):.0f}" r="{4 + k % 3 * 2}" fill="#FFE9A8" opacity="0.8"/>' for k in range(8))
    return ('<path d="M 95 -60 q 75 0 75 70 q 0 70 -75 70" stroke="#E9F4F7" stroke-width="22" fill="none" opacity="0.9"/>'
            '<rect x="-100" y="-120" width="200" height="230" rx="22" fill="#E9F4F7" opacity="0.35" stroke="#fff" stroke-width="6"/>'
            f'<rect x="-88" y="-110" width="176" height="210" rx="14" fill="url(#gBeer)"/>{bub}'
            f'<g fill="{FOAM}" stroke="#E8D9B0" stroke-width="4"><circle cx="-70" cy="-120" r="34"/><circle cx="-20" cy="-136" r="40"/><circle cx="35" cy="-128" r="36"/><circle cx="78" cy="-116" r="28"/></g>')


# ---------- props ----------
def calendar(cx, cy, t):
    """Tear-off calendar: OCTOBER page rips away at EV['tear'] revealing NOVEMBER 2026."""
    out = [f'<g transform="translate({cx},{cy}) rotate(-3)">',
           '<rect x="-250" y="-290" width="500" height="580" rx="26" fill="#000" opacity="0.4" transform="translate(16,20)"/>',
           '<rect x="-250" y="-290" width="500" height="580" rx="26" fill="#FBFAF4" stroke="#2A120A" stroke-width="8"/>',
           f'<rect x="-250" y="-290" width="500" height="150" rx="26" fill="{RED}"/><rect x="-250" y="-170" width="500" height="30" fill="{RED}"/>',
           stext(0, -215, "НОЯБРЬ", 84, fill="#fff", sw=0, shadow=False),
           stext(0, 30, "2026", 190, fill="#2A120A", sw=0, shadow=False),
           stext(0, 210, "наступил", 56, fill="#9A7B66", sw=0, shadow=False)]
    for k in range(-3, 4): out.append(f'<circle cx="{k * 60}" cy="-290" r="13" fill="#555" stroke="#2A120A" stroke-width="4"/>')
    if t < EV["tear"] + 0.6:
        p = prog(t, EV["tear"], EV["tear"] + 0.6)
        dx = 900 * e_in(p); dy = -300 * p + 900 * p * p; r = 70 * e_in(p)
        out.append(f'<g transform="translate({dx:.0f},{dy:.0f}) rotate({r:.1f} 250 -290)" opacity="{1 - p * 0.3:.2f}">'
                   '<rect x="-250" y="-290" width="500" height="580" rx="26" fill="#F3EFE2" stroke="#2A120A" stroke-width="8"/>'
                   '<rect x="-250" y="-290" width="500" height="150" rx="26" fill="#6B7A8F"/><rect x="-250" y="-170" width="500" height="30" fill="#6B7A8F"/>'
                   + stext(0, -215, "ОКТЯБРЬ", 80, fill="#fff", sw=0, shadow=False)
                   + stext(0, 30, "31", 220, fill="#6B7A8F", sw=0, shadow=False) + "</g>")
    out.append("</g>")
    return "".join(out)


def phone(cx, cy, t):
    out = [f'<g transform="translate({cx},{cy}) rotate(4)">',
           '<rect x="-250" y="-460" width="500" height="920" rx="70" fill="#000" opacity="0.45" transform="translate(16,22)"/>',
           '<rect x="-250" y="-460" width="500" height="920" rx="70" fill="#111318" stroke="#3A3F4B" stroke-width="10"/>',
           '<rect x="-225" y="-420" width="450" height="840" rx="46" fill="#05060A"/>',
           '<rect x="-60" y="-445" width="120" height="26" rx="13" fill="#000"/>',
           # blurry tiny bear in the "2023 post"
           '<g opacity="0.85" transform="translate(0,-40) scale(0.42)">' + polar(0, 330, 1.0, 0, glow=1) + '</g>',
           '<rect x="-225" y="-420" width="450" height="840" rx="46" fill="url(#gDark)"/>',
           stext(-200, 250, "пост из 2023 года", 30, fill="#C9D3E6", sw=0, shadow=False, anchor="start"),
           stext(-200, 300, "это ноябрьский мем 2026,", 32, fill="#fff", sw=0, shadow=False, anchor="start"),
           stext(-200, 345, "вы пока не поймёте", 32, fill="#fff", sw=0, shadow=False, anchor="start")]
    for k, ic in enumerate(("♥", "✎", "➦")):
        out.append(f'<circle cx="185" cy="{-120 + k * 110}" r="36" fill="#fff" opacity="0.15"/>')
    out.append("</g>")
    return "".join(out).replace(FONT + '" font-size="30"', FONT + '" font-size="30"')


def sofa():
    return ('<rect x="70" y="1160" width="940" height="300" rx="70" fill="url(#gSofa)" stroke="#2C3618" stroke-width="10"/>'
            '<rect x="40" y="1380" width="1000" height="190" rx="60" fill="#5C6E36" stroke="#2C3618" stroke-width="10"/>'
            '<line x1="540" y1="1390" x2="540" y2="1560" stroke="#2C3618" stroke-width="8"/>'
            '<rect x="10" y="1260" width="130" height="320" rx="60" fill="#6E7F45" stroke="#2C3618" stroke-width="10"/>'
            '<rect x="940" y="1260" width="130" height="320" rx="60" fill="#6E7F45" stroke="#2C3618" stroke-width="10"/>'
            '<rect x="120" y="1560" width="40" height="60" fill="#2C1A10"/><rect x="920" y="1560" width="40" height="60" fill="#2C1A10"/>')


def nikita(t, f, x, y, s, **kw):
    kw.setdefault("blink", is_blink(t)); kw.setdefault("cap_dy", 0)
    return boar(t, x, y, s, mouth=nik_mouth(t, f), outfit=True, **kw)


def bear_mouth(t, f):
    on = any(VOICE_START[i] <= t <= VOICE_END[i] + 0.3 for i in (2, 5))
    return mouth_at(f) if on else 0.0


def nik_mouth(t, f):
    on = not any(VOICE_START[i] <= t <= VOICE_END[i] + 0.3 for i in (2, 5))
    return mouth_at(f) if on else 0.0


# ---------- scenes ----------
def scene_hook(t, f):
    out = [night(t), snow(t)]
    out.append(calendar(540, 640, t))
    out.append(stext(540, 230, "НОЯБРЬ 2026", fit("НОЯБРЬ 2026", 900, 120), fill=ICE, rot=-2))
    out.append(shadow(540, 1600, 0.7))
    look = (math.sin(t * 3), 0) if t > EV["medvedya"] - 0.6 else (0, -1)
    out.append(boar(t, 540, 1600, 0.7, mouth=nik_mouth(t, f), outfit=True, cap_dy=0, blink=is_blink(t), brow=-0.7, look=look,
                    headrot=4 * math.sin(t * 2.5), sq=0.03 * math.sin(t * 9)))
    out.append(sticker(800, 1080, "ГДЕ МЕДВЕДЬ?", 50, ICE, INK, t, EV["medvedya"] + 0.1, 7))
    return "".join(out)


def scene_future(t, f):
    out = ['<rect width="1080" height="1920" fill="#07060F"/>', halftone(t, CYAN, 0.08), floaters(t, 3, [CYAN, PINK], 8)]
    out.append(ktext(540, 200, "МЕМ ИЗ БУДУЩЕГО", fit("МЕМ ИЗ БУДУЩЕГО", 960, 100), t, 3.85, fill=CYAN))
    pp = e_back(prog(t, 3.85, 4.3), 1.3)
    out.append(f'<g transform="translate(0,{(1 - pp) * 1500:.0f})">{phone(540, 860, t)}</g>')
    if t >= EV["tri"]:
        yr = 2023 + int(min(3, 3 * prog(t, EV["tri"], EV["tri"] + 1.1)))
        sc = popscale(t, EV["tri"], 0.3)
        out.append(f'<g transform="translate(540,1430) scale({sc:.3f}) rotate(-3)"><rect x="-300" y="-85" width="600" height="170" rx="28" fill="{INK}"/>'
                   f'<rect x="-310" y="-95" width="600" height="170" rx="28" fill="{YEL}" stroke="{INK}" stroke-width="8"/>'
                   + stext(-10, -10, f"2023 → {yr}", 92, fill=INK, sw=0, shadow=False).replace(FONT, MONO) + "</g>")
    return "".join(out)


def scene_bear(t, f):
    z = 1 + 0.18 * e_inout(prog(t, 6.2, 9.6))
    out = [f'<g transform="translate(540,1100) scale({z:.4f}) translate(-540,-1100)">', night(t, 1450),
           '<rect width="1080" height="1920" fill="#000" opacity="0.45"/>', '<ellipse cx="540" cy="1250" rx="620" ry="760" fill="url(#gSpot)"/>']
    pin = e_out(prog(t, EV["bear_in"], EV["bear_in"] + 1.2))
    out.append(f'<g opacity="{pin:.2f}">' + polar(540, 1470, 1.05, t, mouth=bear_mouth(t, f), glow=clamp((t - 7.5) * 2),
                                                    tilt=6 * math.sin(t * 0.8)) + "</g>")
    out.append(snow(t, 90, 5, 0.6, 0.8))
    out.append("</g>")
    out.append('<rect width="1080" height="1920" fill="url(#gDark)"/>')
    # creepy text
    op = clamp((t - EV["pomni"] + 1.6) * 1.5)
    out.append(f'<g opacity="{op:.2f}"><text x="540" y="330" font-family="{SERIF}" font-size="64" fill="#E8EEF9" text-anchor="middle" letter-spacing="10">REMEMBER</text>'
               f'<text x="540" y="430" font-family="{SERIF}" font-size="64" fill="#E8EEF9" text-anchor="middle" letter-spacing="10">NOVEMBER 2026</text></g>')
    # glitch bars
    rr = random.Random(int(t * 12))
    if rr.random() < 0.25:
        for _ in range(3):
            y = rr.uniform(0, 1920)
            out.append(f'<rect x="0" y="{y:.0f}" width="1080" height="{rr.uniform(6, 30):.0f}" fill="{rr.choice([CYAN, PINK, "#fff"])}" opacity="0.25"/>')
    return "".join(out)


def scene_came(t, f):
    out = [base.bg_carpet(t), '<rect width="1080" height="1920" fill="#000" opacity="0.15"/>', sofa()]
    out.append(ktext(540, 210, "МЕДВЕДЬ ПРИШЁЛ", fit("МЕДВЕДЬ ПРИШЁЛ", 960, 104), t, EV["prishel"] - 0.1, fill=ICE))
    # bear walks in and plops on the sofa
    pw = prog(t, 9.75, EV["divan"] + 0.1)
    bx = lerp(1400, 760, e_out(pw)); by = 1480 - 40 * abs(math.sin(pw * 9)) * (1 - pw)
    sq_hit = damp(t, EV["divan"] + 0.1, 0.4)
    out.append(nikita(t, f, 300, 1480, 0.58, look=(1, 0), brow=-0.6 if t < EV["skufom"] else 0.6, headrot=3 * math.sin(t * 5)))
    outfit = e_out(prog(t, EV["skufom"], EV["skufom"] + 0.3))
    cd = lerp(-900, 0, e_bounce(prog(t, EV["skufom"] - 0.3, EV["skufom"]))) if t > EV["skufom"] - 0.3 else None
    out.append(f'<g transform="translate({bx:.1f},{by:.1f}) scale({1 + 0.15 * sq_hit:.3f},{1 - 0.15 * sq_hit:.3f}) translate({-bx:.1f},{-by:.1f})">'
               + polar(bx, by, 0.6, t, mouth=bear_mouth(t, f), outfit=outfit, cap_dy=cd, mug_p=prog(t, EV["pivo"], EV["pivo"] + 0.35)) + "</g>")
    if t > EV["pivo"]:
        out.append(sticker(880, 860, "ПШШШ", 50, FOAM, INK, t, EV["pivo"], 10))
    if t >= EV["skufom"]:
        out.append(marker(110, 400, 860, 140, t, EV["skufom"] - 0.05, PINK, rot=-2))
        out.append(ktext(540, 400, "И СТАЛ СКУФОМ", fit("И СТАЛ СКУФОМ", 840, 110), t, EV["skufom"], fill="#fff", rot=-2, style="drop"))
    return "".join(out)


def scene_skufych(t, f):
    out = [base.bg_carpet(t), '<rect width="1080" height="1920" fill="#000" opacity="0.15"/>', sofa()]
    out.append(sticker(540, 220, "НОЯБРЬ 2026", 50, ICE, INK, t, 13.62, -3))
    out.append(marker(80, 380, 920, 150, t, EV["skufych"] - 0.25, LIME, rot=-2))
    out.append(ktext(540, 380, "МЕДВЕДЬ СКУФЫЧ", fit("МЕДВЕДЬ СКУФЫЧ", 900, 112), t, EV["skufych"] - 0.2, fill=INK, rot=-2, stroke="#fff", sw=10))
    # clink: both lift mugs toward the centre
    pc = e_back(prog(t, EV["clink"] - 0.35, EV["clink"]), 1.5) if t < EV["clink"] + 0.6 else 1 - e_out(prog(t, EV["clink"] + 0.6, EV["clink"] + 1.0))
    out.append(nikita(t, f, 300, 1480, 0.58, look=(1, -0.3), brow=0.7, headrot=4 * math.sin(t * 2 * math.pi)))
    out.append(polar(760, 1480, 0.6, t, mouth=bear_mouth(t, f), outfit=1, cap_dy=0, tilt=4 * math.sin(t * 2 * math.pi)))
    mx1 = lerp(400, 500, pc); mx2 = lerp(860, 600, pc); my = lerp(1250, 1000, pc)
    out.append(f'<g transform="translate({mx1:.0f},{my:.0f}) scale(0.5) rotate({lerp(0, 25, pc):.0f})">{mug_svg(t)}</g>')
    out.append(f'<g transform="translate({mx2:.0f},{my:.0f}) scale(-0.5,0.5) rotate({lerp(0, 25, pc):.0f})">{mug_svg(t)}</g>')
    if t > EV["clink"]:
        dt = t - EV["clink"]
        for k in range(8):
            a = -math.pi / 2 + (k - 3.5) * 0.4
            out.append(f'<circle cx="{550 + math.cos(a) * 320 * dt:.0f}" cy="{880 + math.sin(a) * 420 * dt + 700 * dt * dt:.0f}" r="{16 - 5 * dt:.1f}" fill="{FOAM}" opacity="{clamp(1 - dt):.2f}"/>')
        out.append(burst(550, 860, 70, 10, YEL, seed=2, sc=popscale(t, EV["clink"], 0.2) * clamp(1.2 - dt), rot=t * 40))
    out.append(sticker(540, 610, "ОТМЕТЬ ТОГО, КТО ЖДАЛ МЕДВЕДЯ", 38, YEL, INK, t, EV["cta"], 3))
    if t >= EV["stamp"]:
        pp = prog(t, EV["stamp"], EV["stamp"] + 0.18); sc = lerp(3, 1, e_out(pp))
        out.append(f'<g opacity="{clamp(pp * 3):.2f}"><g transform="translate(540,780) rotate(-8) scale({sc:.3f})">'
                   f'<rect x="-250" y="-55" width="500" height="110" rx="18" fill="none" stroke="{RED}" stroke-width="11"/>'
                   + stext(0, 0, "ДОЖДАЛИСЬ", 70, fill=RED, sw=0, shadow=False) + "</g></g>")
    return "".join(out)


SCENE_FN = {"hook": scene_hook, "future": scene_future, "bear": scene_bear, "came": scene_came, "skufych": scene_skufych}


def subtitles(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    bear = any(VOICE_START[i] <= t <= VOICE_END[i] + 0.3 for i in (2, 5))
    hl = "#7FB2FF" if bear else PINK
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            size = 70; gap = size * 0.32
            words = [w["disp"].upper() for w in c]
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 960:
                size = int(size * 960 / total); gap = size * 0.32; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            sc = lerp(0.8, 1, e_back(prog(t, t0, t0 + 0.14)))
            cx, cy = 540, 1690
            out = [f'<g transform="translate({cx},{cy}) scale({sc:.3f}) translate({-cx},{-cy})">']
            x = cx - total / 2
            for w, wd in zip(words, c):
                ww = tw(w, size)
                if wd["t0"] - 0.03 <= t < wd["t1"] + 0.05:
                    out.append(f'<rect x="{x - 14:.1f}" y="{cy - size * 0.62:.1f}" width="{ww + 28:.1f}" height="{size * 1.24:.1f}" rx="14" fill="{hl}" transform="rotate(-2 {x + ww / 2:.1f} {cy})"/>')
                out.append(stext(x, cy, w, size, fill="#fff", anchor="start", op=1 if wd["t0"] - 0.03 <= t else 0.55))
                x += ww + gap
            out.append("</g>")
            return "".join(out)
    return ""


def punch(t):
    s = 1.0
    for T in TRANSITIONS + CUTS + [EV["tear"], EV["skufom"], EV["clink"]]:
        if 0 <= t - T < 0.35: s += 0.06 * (1 - e_out((t - T) / 0.35))
    return s


def shake(t):
    dx = dy = 0.0
    for t0, amp in ((6.2, 18), (9.6, 18), (EV["divan"] + 0.1, 12), (EV["stamp"], 14)):
        if 0 <= t - t0 < 0.5:
            k = math.exp(-(t - t0) * 9) * amp
            dx += k * math.sin((t - t0) * 70); dy += k * math.cos((t - t0) * 53)
    return dx, dy


def flash(t):
    for T in CUTS:
        if 0 <= t - T < 0.18:
            return f'<rect width="1080" height="1920" fill="#fff" opacity="{0.8 * (1 - (t - T) / 0.18):.2f}"/>'
    return ""


def compose(t, f):
    name = next((n for a, b, n in SCENES if a <= t < b), "skufych")
    dx, dy = shake(t); s = punch(t)
    return (f'<g transform="translate({dx:.1f},{dy:.1f}) translate(540,960) scale({1.03 * s:.4f}) translate(-540,-960)">{SCENE_FN[name](t, f)}</g>'
            f'<rect width="{W}" height="{H}" fill="url(#gVig)"/>{flash(t)}{stripes_wipe(t)}{subtitles(t)}')


def frame_svg(f):
    t = f / FPS
    body = compose(t, f)
    if t > EV["loop"]:
        body += f'<g opacity="{e_inout(prog(t, EV["loop"], DUR)):.3f}">{compose(0.0, 0)}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}'
            f'<rect width="{W}" height="{H}" fill="#000"/>{body}{base.WM()}</svg>')


def render(f):
    cairosvg.svg2png(bytestring=frame_svg(f).encode(), write_to=f"build/frames/{f:05d}.png")
    return f


if __name__ == "__main__":
    os.makedirs("build/frames", exist_ok=True)
    frames = [int(x) for x in sys.argv[1:]] or list(range(NFRAMES))
    with Pool(os.cpu_count()) as pool:
        for i, _ in enumerate(pool.imap_unordered(render, frames, chunksize=4)):
            if i % 300 == 0: print("frame", i, flush=True)
    print("done", len(frames))
