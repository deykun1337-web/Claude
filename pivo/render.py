"""«Почему от пива растёт живот» — educational short with Никита Скуф Скуфыч. 60 fps render, seamless loop."""
import math, os, random, sys
from multiprocessing import Pool
import cairosvg
import base
from base import (tw, fit, clamp, prog, lerp, e_out, e_in, e_back, e_bounce, popscale, damp, stext, pill,
                  burst, star4, boar, shadow, is_blink, mouth_at, INK, FONT)
from kit import (ktext, marker, sticker, halftone, floaters, ring, stripes_wipe, e_inout, PINK, LIME, CYAN, YEL, MONO)
from timeline import *

AMBER, FOAM, RED, BROWN = "#FFB020", "#FFF6DC", "#FF3B4A", "#1A0F05"

DEFS = base.DEFS.replace("</defs>", '''
<radialGradient id="gGlowAmber" cx="0.5" cy="0.45" r="0.7"><stop offset="0" stop-color="#FFB020" stop-opacity="0.5"/><stop offset="1" stop-color="#FFB020" stop-opacity="0"/></radialGradient>
<radialGradient id="gGlowGreen" cx="0.5" cy="0.5" r="0.7"><stop offset="0" stop-color="#3DFF9A" stop-opacity="0.35"/><stop offset="1" stop-color="#3DFF9A" stop-opacity="0"/></radialGradient>
<radialGradient id="gGlowRed" cx="0.5" cy="0.5" r="0.7"><stop offset="0" stop-color="#FF3B4A" stop-opacity="0.4"/><stop offset="1" stop-color="#FF3B4A" stop-opacity="0"/></radialGradient>
<linearGradient id="gBeer" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E88A00"/><stop offset="0.45" stop-color="#FFC233"/><stop offset="1" stop-color="#D97800"/></linearGradient>
<linearGradient id="gLiver" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#C2453F"/><stop offset="1" stop-color="#7E1F25"/></linearGradient>
<linearGradient id="gCard" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFDF6"/><stop offset="1" stop-color="#F3E9D2"/></linearGradient>
</defs>''')


# ---------- belly curve: big -> shrinks during "fix" -> grows back when the beer opens ----------
def belly_at(t):
    b = 1.32
    steps = [EV["menshe"], EV["zakus"], EV["shagov"], EV["belok"]]
    for k, ts in enumerate(steps):
        b -= 0.08 * e_back(prog(t, ts + 0.1, ts + 0.45), 2.2)
    b += 0.32 * e_back(prog(t, EV["open"] + 0.2, EV["open"] + 0.7), 2.0)
    return b + 0.02 * math.sin(t * 14) * (b - 1)  # jiggle


def nikita(t, f, x, y, s, **kw):
    kw.setdefault("blink", is_blink(t)); kw.setdefault("cap_dy", 0)
    return shadow(x, y, s * (0.8 + 0.25 * belly_at(t))) + boar(t, x, y, s, mouth=mouth_at(f), outfit=True, belly=belly_at(t), **kw)


# ---------- props ----------
def mug(cx, cy, s, t, rot=0.0, level=1.0):
    bub = "".join(f'<circle cx="{-60 + (k * 37) % 120}" cy="{90 - ((t * 120 + k * 41) % 170):.0f}" r="{4 + k % 3 * 2}" fill="#FFE9A8" opacity="0.8"/>' for k in range(9))
    top = -110 + 200 * (1 - level)
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f}) scale({s:.3f})">'
            '<path d="M 95 -60 q 75 0 75 70 q 0 70 -75 70" stroke="#E9F4F7" stroke-width="22" fill="none" opacity="0.9"/>'
            '<rect x="-100" y="-120" width="200" height="230" rx="22" fill="#E9F4F7" opacity="0.35" stroke="#fff" stroke-width="6"/>'
            f'<rect x="-88" y="{top:.0f}" width="176" height="{210 - (top + 110):.0f}" rx="14" fill="url(#gBeer)"/>{bub}'
            f'<g fill="{FOAM}" stroke="#E8D9B0" stroke-width="4"><circle cx="-70" cy="{top - 10:.0f}" r="34"/><circle cx="-20" cy="{top - 26:.0f}" r="40"/><circle cx="35" cy="{top - 18:.0f}" r="36"/><circle cx="78" cy="{top - 6:.0f}" r="28"/></g>'
            '<path d="M -70 -80 v 160" stroke="#fff" stroke-width="10" opacity="0.5" stroke-linecap="round"/></g>')


def donut(cx, cy, s, rot):
    sp = "".join(f'<rect x="{math.cos(a) * 85:.0f}" y="{math.sin(a) * 85:.0f}" width="22" height="8" rx="4" fill="{c}" transform="rotate({a * 57 + 40:.0f} {math.cos(a) * 85:.0f} {math.sin(a) * 85:.0f})"/>'
                 for a, c in zip([k * 0.71 for k in range(14)], [YEL, CYAN, "#fff", LIME] * 4))
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            '<circle r="150" fill="#D9934A" stroke="#7A4A1E" stroke-width="8"/>'
            '<path d="M -135 -20 Q -150 -140 0 -140 Q 150 -140 135 -20 Q 120 40 90 10 Q 60 60 30 20 Q 0 70 -40 25 Q -80 60 -100 15 Q -125 50 -135 -20 Z" fill="#FF7AB8" stroke="#C2457F" stroke-width="6"/>'
            '<circle r="150" fill="none"/>' + sp +
            '<circle r="48" fill="#2A160A" stroke="#7A4A1E" stroke-width="8"/></g>')


def liver(cx, cy, s, t, sweat=0.0, stress=0.0):
    sh = 4 * stress * math.sin(t * 50)
    out = [f'<g transform="translate({cx + sh:.1f},{cy:.1f}) scale({s:.3f})">',
           '<path d="M -230 -40 C -240 -150 -60 -170 60 -140 C 200 -110 260 -60 220 20 C 180 100 40 140 -60 120 C -170 100 -220 40 -230 -40 Z" fill="url(#gLiver)" stroke="#4A1015" stroke-width="10"/>',
           '<path d="M -150 -90 C -100 -120 0 -125 60 -110" stroke="#E07A6E" stroke-width="12" fill="none" opacity="0.6" stroke-linecap="round"/>']
    for ex in (-60, 40):
        out.append(f'<ellipse cx="{ex}" cy="-25" rx="30" ry="34" fill="#fff" stroke="#4A1015" stroke-width="6"/><circle cx="{ex + 6}" cy="-20" r="13" fill="#1A0A0A"/>')
        out.append(f'<path d="M {ex - 32} {-70 + 10 * stress} L {ex + 28} {-60 - 6 * stress}" stroke="#4A1015" stroke-width="10" stroke-linecap="round"/>')
    out.append(f'<path d="M -50 55 Q -10 {30 - 25 * stress:.0f} 40 55" stroke="#4A1015" stroke-width="9" fill="none" stroke-linecap="round"/>')
    if sweat > 0:
        for k, (sx, sy) in enumerate(((150, -110), (190, -40), (-200, -100))):
            yy = sy + ((t * 160 + k * 50) % 90)
            out.append(f'<path d="M {sx} {yy:.0f} q -14 22 0 30 q 14 -8 0 -30 Z" fill="{CYAN}" opacity="{sweat:.2f}"/>')
    out.append("</g>")
    return "".join(out)


def bottle(cx, cy, s, rot):
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            '<rect x="-12" y="-70" width="24" height="34" rx="6" fill="#2F8F4E"/><rect x="-14" y="-82" width="28" height="14" rx="4" fill="#E2B13C"/>'
            '<path d="M -12 -40 Q -34 -20 -34 0 L -34 70 Q -34 82 -22 82 L 22 82 Q 34 82 34 70 L 34 0 Q 34 -20 12 -40 Z" fill="#3BB066" stroke="#14532D" stroke-width="5"/>'
            '<rect x="-30" y="10" width="60" height="38" fill="#FFF6DC"/></g>')


def fat_drop(cx, cy, s):
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s:.2f})"><path d="M 0 -40 C 26 -6 34 10 34 22 A 34 34 0 0 1 -34 22 C -34 10 -26 -6 0 -40 Z" fill="#FFD86B" stroke="#B8862B" stroke-width="5"/>'
            '<circle cx="-10" cy="12" r="7" fill="#fff" opacity="0.7"/></g>')


def chips_bag(cx, cy, s, rot, col="#E53935", label="ЧИПСЫ"):
    zz = " ".join(f"L {-80 + k * 16} {-120 + (8 if k % 2 else 0)}" for k in range(11))
    zb = " ".join(f"L {80 - k * 16} {120 - (8 if k % 2 else 0)}" for k in range(11))
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<path d="M -80 -112 {zz} L 84 -110 Q 100 0 84 110 {zb} L -84 110 Q -100 0 -80 -112 Z" fill="{col}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
            '<ellipse cx="0" cy="10" rx="54" ry="40" fill="#FFD23F" stroke="#B8862B" stroke-width="5"/>'
            + stext(0, -60, label, 34, fill="#fff", sw=6, shadow=False) + "</g>")


def crouton(cx, cy, s, rot):
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            '<rect x="-30" y="-30" width="60" height="60" rx="10" fill="#C88A3E" stroke="#6B4116" stroke-width="5"/>'
            '<circle cx="-10" cy="-8" r="4" fill="#8A5A22"/><circle cx="12" cy="10" r="4" fill="#8A5A22"/><circle cx="8" cy="-14" r="3" fill="#8A5A22"/></g>')


def checkbox(x, y, t, t0):
    p = prog(t, t0, t0 + 0.25)
    out = f'<rect x="{x - 34}" y="{y - 34}" width="68" height="68" rx="14" fill="#fff" stroke="{INK}" stroke-width="7"/>'
    if p > 0:
        out += f'<path d="M {x - 20} {y + 2} L {x - 6} {y + 18} L {x + 26} {y - 22}" stroke="#2EB872" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="90" stroke-dashoffset="{90 * (1 - e_out(p)):.1f}"/>'
    return out


def sixpack(cx, cy, s):
    out = [f'<g transform="translate({cx},{cy}) scale({s})"><rect x="-120" y="-150" width="240" height="300" rx="60" fill="#E88A6A" stroke="#7A3520" stroke-width="8"/>']
    for r in range(3):
        for c in (-1, 1):
            out.append(f'<rect x="{c * 52 - 42}" y="{-120 + r * 85}" width="84" height="70" rx="22" fill="#F4A48C" stroke="#7A3520" stroke-width="5"/>')
    out.append("</g>")
    return "".join(out)


def bookmark(cx, cy, s, fill):
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s:.3f})"><path d="M -110 -150 h 220 v 300 l -110 -80 l -110 80 Z" fill="#000" opacity="0.35" transform="translate(14,16)"/>'
            f'<path d="M -110 -150 h 220 v 300 l -110 -80 l -110 80 Z" fill="{fill}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/></g>')


def bg(t, col=BROWN, glow="gGlowAmber"):
    return (f'<rect width="1080" height="1920" fill="{col}"/>' + halftone(t, "#fff", 0.05)
            + f'<circle cx="540" cy="900" r="{900 + 30 * base.beat(t):.0f}" fill="url(#{glow})"/>')


def grid(t, col="#0D1020", line="#1C2340"):
    out = [f'<rect width="1080" height="1920" fill="{col}"/>']
    off = (t * 30) % 60
    for k in range(-60, 1140, 60): out.append(f'<line x1="{k + off:.0f}" y1="0" x2="{k + off:.0f}" y2="1920" stroke="{line}" stroke-width="2"/>')
    for k in range(0, 1980, 60): out.append(f'<line x1="0" y1="{k - off:.0f}" x2="1080" y2="{k - off:.0f}" stroke="{line}" stroke-width="2"/>')
    return "".join(out)


# ---------- scenes ----------
def scene_hook(t, f):
    out = [bg(t), ring(540, 1150, 500, t, AMBER, 10), floaters(t, 7, [AMBER, FOAM, PINK], 10)]
    out.append(nikita(t, f, 540, 1500, 0.95, brow=0.5 if t < EV["ne"] else -0.6, headrot=4 * math.sin(t * 2 * math.pi),
                      sq=0.03 * math.sin(t * 9)))
    out.append(mug(880, 1180 + 10 * math.sin(t * 3), 0.85, t, rot=8))
    # hook text is on screen from frame 0 (thumbnail + loop)
    out.append(marker(80, 250, 920, 150, t, -1, AMBER, rot=-2))
    out.append(stext(540, 250, "ПИВНОЙ ЖИВОТ", fit("ПИВНОЙ ЖИВОТ", 900, 128), fill="#fff", rot=-2))
    sz = fit("НЕ ИЗ-ЗА ПИВА?!", 960, 110)
    out.append(ktext(540, 420, "НЕ ИЗ-ЗА ПИВА?!", sz, t, EV["ne"], fill=RED, rot=2, stagger=0.025))
    out.append(sticker(760, 560, "НУ... ПОЧТИ", 50, FOAM, INK, t, EV["pochti"], 6))
    out.append(sticker(540, 700, "НИКИТА СКУФ СКУФЫЧ", 46, LIME, INK, t, EV["nikita"], -3))
    return "".join(out)


def scene_cal(t, f):
    out = [grid(t), f'<circle cx="540" cy="800" r="760" fill="url(#gGlowAmber)"/>']
    out.append(ktext(540, 220, "КАЛОРИИ", 130, t, 4.45, fill=AMBER))
    pm = e_back(prog(t, EV["pollitra"], EV["pollitra"] + 0.4))
    if pm > 0:
        out.append(mug(lerp(-300, 290, pm), 720, 0.95, t, rot=-6 + 4 * math.sin(t * 3)))
        out.append(stext(290, 940, "0,5 Л ПИВА", 54, fill="#fff", sc=pm))
    pd = e_back(prog(t, EV["ponchik"] - 0.25, EV["ponchik"] + 0.15))
    out.append(stext(540, 720, "≈", 140, fill=YEL, sc=popscale(t, EV["ponchik"] - 0.3)))
    if pd > 0:
        out.append(donut(lerp(1400, 800, pd), 720, 0.95, t * 40))
        out.append(stext(800, 940, "ПОНЧИК", 54, fill="#fff", sc=pd))
    if t >= EV["dvesti"]:
        n = int(round(215 * e_out(prog(t, EV["dvesti"], EV["dvesti"] + 0.8))))
        sc = popscale(t, EV["dvesti"], 0.3)
        out.append(f'<g transform="translate(540,1120) scale({sc:.3f}) rotate(-3)"><rect x="-330" y="-95" width="660" height="190" rx="30" fill="{INK}"/>'
                   f'<rect x="-340" y="-105" width="660" height="190" rx="30" fill="{AMBER}" stroke="{INK}" stroke-width="8"/>'
                   + stext(-10, -10, f"≈{n} ККАЛ", 104, fill=INK, sw=0, shadow=False).replace(FONT, MONO) + "</g>")
    out.append(nikita(t, f, 540, 1555, 0.5, brow=0.3, look=(0, -1), headrot=3 * math.sin(t * 5)))
    return "".join(out)


def scene_liver(t, f):
    out = [bg(t, "#170A0C", "gGlowRed"), floaters(t, 9, [RED, AMBER], 6)]
    out.append(ktext(540, 200, "ПЕЧЕНЬ", 120, t, EV["pechen"] - 0.1, fill="#FF8A80"))
    stress = clamp((t - EV["alko"]) * 2)
    out.append(liver(540, 640, 1.15, t, sweat=stress, stress=stress))
    out.append(sticker(540, 860, "ЗАНЯТО: АЛКОГОЛЬ", 46, RED, "#fff", t, EV["alko"], -3))
    for k in range(7):  # bottles queue into the liver
        t0 = EV["alko"] - 0.3 + k * 0.28
        if t > t0:
            p = prog(t, t0, t0 + 0.9)
            if p < 1:
                out.append(bottle(lerp(1150, 720, e_out(p)), 520 + 30 * math.sin(k), 0.8, -20 + 40 * p))
    # fat burning bar stuck
    if t >= EV["zhir"]:
        sc = popscale(t, EV["zhir"], 0.3)
        blink = 0.5 + 0.5 * math.sin(t * 12)
        out.append(f'<g transform="translate(540,1010) scale({sc:.3f})">'
                   f'<rect x="-400" y="-70" width="800" height="140" rx="26" fill="{INK}" opacity="0.85"/>'
                   + stext(-380, -32, "СЖИГАНИЕ ЖИРА", 34, fill="#fff", sw=0, shadow=False, anchor="start").replace(FONT, MONO)
                   + '<rect x="-380" y="5" width="640" height="38" rx="10" fill="#2A2F45"/>'
                   + f'<rect x="-380" y="5" width="40" height="38" rx="10" fill="{RED}"/>'
                   + f'<g opacity="{blink:.2f}"><rect x="300" y="-8" width="20" height="60" fill="{YEL}"/><rect x="335" y="-8" width="20" height="60" fill="{YEL}"/></g>'
                   + stext(320, -40, "ПАУЗА", 26, fill=YEL, sw=0, shadow=False).replace(FONT, MONO) + "</g>")
    # fat drops fall into the belly
    if t >= EV["zapas"] - 0.4:
        for k in range(6):
            t0 = EV["zapas"] - 0.4 + k * 0.12; p = prog(t, t0, t0 + 0.55)
            if 0 < p < 1:
                out.append(fat_drop(lerp(300 + k * 90, 540, p), lerp(1060, 1320, e_in(p)), 0.9))
    out.append(nikita(t, f, 540, 1560, 0.6, brow=-0.4, headrot=3 * math.sin(t * 5), sq=damp(t, EV["zapas"] + 0.2, 0.5)))
    if t > EV["zapas"] + 0.2:
        out.append(sticker(820, 1290, "+ В ЗАПАС", 42, YEL, INK, t, EV["zapas"] + 0.2, 8))
    return "".join(out)


def scene_snack(t, f):
    out = [bg(t, "#160A1F", "gGlowPink" if False else "gGlowAmber"), floaters(t, 11, [PINK, YEL], 6)]
    out.append(ktext(540, 210, "АППЕТИТ ×2", fit("АППЕТИТ ×2", 940, 120), t, EV["appetit"], fill=YEL, rot=-2))
    rr = random.Random(5); landed = 0
    for k in range(9):
        t0 = EV["chips"] - 0.5 + k * 0.17; p = prog(t, t0, t0 + 0.8)
        if p <= 0: continue
        x = rr.uniform(150, 930); rot = rr.uniform(-40, 40) + 300 * p
        y = lerp(-250, 1300, e_in(p))
        if p >= 1: landed += 1; continue
        out.append(chips_bag(x, y, 0.75, rot, rr.choice(["#E53935", "#1E88E5", "#43A047"])) if k % 3 != 2 else crouton(x, y, 1.4, rot))
    if t > EV["chips"] - 0.3:
        kcal = 215 + 110 * landed
        out.append(f'<g transform="translate(540,420) rotate(2)"><rect x="-260" y="-70" width="520" height="140" rx="26" fill="{RED}" stroke="{INK}" stroke-width="8"/>'
                   + stext(0, 0, f"{kcal} ККАЛ", 80, fill="#fff", sw=0, shadow=False).replace(FONT, MONO) + "</g>")
    out.append(nikita(t, f, 540, 1530, 0.78, hearts=t > EV["chips"], headrot=5 * math.sin(t * 6), sq=0.03 * math.sin(t * 9)))
    if t > EV["suhar"]:
        out.append(chips_bag(260, 1380, 0.6, -15, "#E53935"))
        out.append(crouton(830, 1420, 1.2, 20))
    return "".join(out)


def scene_fix(t, f):
    out = [bg(t, "#06160F", "gGlowGreen"), floaters(t, 13, [LIME, CYAN], 6)]
    out.append(ktext(540, 190, "КАК ИСПРАВИТЬ", fit("КАК ИСПРАВИТЬ", 940, 110), t, EV["ispravit"], fill=LIME))
    pc = e_back(prog(t, EV["ispravit"] + 0.1, EV["ispravit"] + 0.5), 1.4)
    if pc > 0:
        out.append(f'<g transform="translate(0,{(1 - pc) * 1400:.0f}) rotate(-1.5 540 700)">'
                   '<rect x="110" y="330" width="880" height="760" rx="40" fill="#000" opacity="0.4" transform="translate(14,18)"/>'
                   '<rect x="100" y="320" width="880" height="760" rx="40" fill="url(#gCard)" stroke="#2A120A" stroke-width="8"/>')
        items = [("menshe", "МЕНЬШЕ ПИВА"), ("zakus", "БЕЗ ЗАКУСОК"), ("shagov", "10 000 ШАГОВ"), ("belok", "БЕЛОК В ЕДЕ")]
        for k, (key, txt) in enumerate(items):
            y = 450 + k * 175
            out.append(checkbox(200, y, t, EV[key] + 0.1))
            on = t >= EV[key]
            out.append(stext(270, y, txt, 66, fill=INK if on else "#B9AE98", sw=0, shadow=False, anchor="start",
                             sc=1 + 0.08 * (1 - e_out(prog(t, EV[key], EV[key] + 0.3))) if on else 1))
        out.append("</g>")
    out.append(nikita(t, f, 540, 1545, 0.62, brow=0.6, headrot=4 * math.sin(t * 2 * math.pi), sq=0.03 * math.sin(t * 9)))
    if t > EV["belok"] + 0.3:
        out.append(sticker(820, 1290, "-ЖИВОТ", 50, LIME, INK, t, EV["belok"] + 0.3, 8))
    return "".join(out)


def scene_myth(t, f):
    out = [grid(t, "#14070A", "#2A1015"), f'<circle cx="540" cy="760" r="760" fill="url(#gGlowRed)"/>']
    out.append(sticker(540, 225, "МИФ", 80, RED, "#fff", t, 19.05, -4))
    out.append(ktext(540, 380, "КАЧАТЬ ПРЕСС", fit("КАЧАТЬ ПРЕСС", 940, 116), t, EV["press"] - 0.05, fill="#fff"))
    sp = popscale(t, EV["press"] + 0.1)
    if sp > 0:
        out.append(f'<g transform="translate(540,700) scale({sp:.3f}) translate(-540,-700)">{sixpack(540, 700, 1.0)}</g>')
    if t >= EV["bespol"]:
        p1 = prog(t, EV["bespol"], EV["bespol"] + 0.12); p2 = prog(t, EV["bespol"] + 0.12, EV["bespol"] + 0.24)
        out.append(f'<line x1="380" y1="520" x2="{380 + 320 * p1:.0f}" y2="{520 + 360 * p1:.0f}" stroke="{RED}" stroke-width="34" stroke-linecap="round"/>')
        if p2 > 0: out.append(f'<line x1="700" y1="520" x2="{700 - 320 * p2:.0f}" y2="{520 + 360 * p2:.0f}" stroke="{RED}" stroke-width="34" stroke-linecap="round"/>')
        out.append(stext(540, 960, "БЕСПОЛЕЗНО", fit("БЕСПОЛЕЗНО", 800, 96), fill=RED, sc=popscale(t, EV["bespol"] + 0.1), rot=-4))
    # whole-body fat loss: arrows around Nikita
    pv = prog(t, EV["vsego"], EV["vsego"] + 0.4)
    if pv > 0:
        for k in range(8):
            a = k * math.pi / 4 + 0.3; r0 = 300 + 60 * math.sin(t * 8 + k); cx, cy = 540, 1380
            x1, y1 = cx + math.cos(a) * r0, cy + math.sin(a) * r0 * 0.75; x2, y2 = cx + math.cos(a) * (r0 + 90), cy + math.sin(a) * (r0 + 90) * 0.75
            out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{LIME}" stroke-width="12" stroke-linecap="round" opacity="{pv:.2f}"/>'
                       f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="12" fill="{LIME}" opacity="{pv:.2f}"/>')
        out.append(sticker(540, 1120, "ЖИР УХОДИТ ВЕЗДЕ", 46, LIME, INK, t, EV["vsego"], 3))
    out.append(nikita(t, f, 540, 1535, 0.6, brow=-0.5 if t < EV["vsego"] else 0.4, headrot=4 * math.sin(t * 5)))
    return "".join(out)


def scene_save(t, f):
    out = [bg(t), ring(540, 1150, 500, t, AMBER, 10), floaters(t, 7, [AMBER, FOAM, PINK], 10)]
    sb = popscale(t, EV["sohrani"], 0.35)
    if sb > 0:
        bob = 10 * math.sin(t * 6)
        out.append(bookmark(540, 450 + bob, sb * 1.3, YEL))
        out.append(stext(540, 410 + bob, "СОХРАНИ", 50, fill=INK, sw=0, shadow=False, sc=sb))
    # Nikita cracks a beer: psst + foam, belly grows back
    out.append(nikita(t, f, 540, 1500, 0.95, brow=0.8, headrot=4 * math.sin(t * 2 * math.pi), sq=damp(t, EV["open"] + 0.3, 0.5)))
    if t > EV["open"] - 0.6:
        pm = e_back(prog(t, EV["open"] - 0.6, EV["open"] - 0.2))
        out.append(mug(lerp(1250, 880, pm), 1180, 0.85, t, rot=8))
        if t > EV["open"]:
            dt = t - EV["open"]
            for k in range(7):
                a = -math.pi / 2 + (k - 3) * 0.35
                out.append(f'<circle cx="{880 + math.cos(a) * 300 * dt:.0f}" cy="{1060 + math.sin(a) * 500 * dt + 600 * dt * dt:.0f}" r="{18 - 4 * dt:.1f}" fill="{FOAM}" opacity="{clamp(1 - dt):.2f}"/>')
            out.append(sticker(820, 900, "ПШШШ", 54, FOAM, INK, t, EV["open"], 10))
    return "".join(out)


SCENE_FN = {"hook": scene_hook, "cal": scene_cal, "liver": scene_liver, "snack": scene_snack,
            "fix": scene_fix, "myth": scene_myth, "save": scene_save}


def subtitles(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            size = 70; gap = size * 0.32
            words = [w["disp"].upper() for w in c]
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 960:
                size = int(size * 960 / total); gap = size * 0.32; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            sc = lerp(0.8, 1, e_back(prog(t, t0, t0 + 0.14)))
            cx, cy = 540, 1675
            out = [f'<g transform="translate({cx},{cy}) scale({sc:.3f}) translate({-cx},{-cy})">']
            x = cx - total / 2
            for w, wd in zip(words, c):
                ww = tw(w, size)
                if wd["t0"] - 0.03 <= t < wd["t1"] + 0.05:
                    out.append(f'<rect x="{x - 14:.1f}" y="{cy - size * 0.62:.1f}" width="{ww + 28:.1f}" height="{size * 1.24:.1f}" rx="14" fill="{AMBER}" transform="rotate(-2 {x + ww / 2:.1f} {cy})"/>')
                out.append(stext(x, cy, w, size, fill="#fff", anchor="start", op=1 if wd["t0"] - 0.03 <= t else 0.55))
                x += ww + gap
            out.append("</g>")
            return "".join(out)
    return ""


def punch(t):
    s = 1.0
    for T in TRANSITIONS + [EV["ne"], EV["bespol"], EV["open"]]:
        if 0 <= t - T < 0.35: s += 0.06 * (1 - e_out((t - T) / 0.35))
    return s


def shake(t):
    dx = dy = 0.0
    for t0, amp in ((EV["ne"], 16), (EV["zapas"] + 0.2, 12), (EV["bespol"], 20), (EV["open"], 14)):
        if 0 <= t - t0 < 0.5:
            k = math.exp(-(t - t0) * 9) * amp
            dx += k * math.sin((t - t0) * 70); dy += k * math.cos((t - t0) * 53)
    return dx, dy


def compose(t, f):
    name = next((n for a, b, n in SCENES if a <= t < b), "save")
    dx, dy = shake(t); s = punch(t)
    return (f'<g transform="translate({dx:.1f},{dy:.1f}) translate(540,960) scale({1.03 * s:.4f}) translate(-540,-960)">{SCENE_FN[name](t, f)}</g>'
            f'<rect width="{W}" height="{H}" fill="url(#gVig)"/>{stripes_wipe(t)}{subtitles(t)}')


def frame_svg(f):
    t = f / FPS
    body = compose(t, f)
    if t > EV["loop"]:  # seamless loop: dissolve into frame 0
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
