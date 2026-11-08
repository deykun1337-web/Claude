"""2D cartoon characters for the «Майкл из Техаса» short: Руслан Дейкун Кабанович, his mom, Клод the boar."""
import math, random
from base import star4, clamp, lerp, e_out, stext, FONT
from blocky import klod as klod_block

OUT = "#16100F"
SKIN, SKIN2 = "#EBC3A7", "#D9A588"


def _eye(ex, ey, sg, expr, blink, look):
    """One eye in head-local coords; sg=-1 left, +1 right."""
    if blink or expr == "happy":
        if expr == "happy":
            return f'<path d="M {ex - 34} {ey + 6} Q {ex} {ey - 22} {ex + 34} {ey + 6}" stroke="{OUT}" stroke-width="8" fill="none" stroke-linecap="round"/>'
        return f'<path d="M {ex - 34} {ey + 4} Q {ex} {ey + 16} {ex + 34} {ey + 4}" stroke="{OUT}" stroke-width="8" fill="none" stroke-linecap="round"/>'
    wide = {"shock": 1.35, "panic": 1.3, "cry": 1.1}.get(expr, 1.0)
    lid = {"neutral": 0.42, "sad": 0.5, "smug": 0.55, "angry": 0.35, "cry": 0.3}.get(expr, 0.15)
    ry = 34 * wide
    s = [f'<ellipse cx="{ex}" cy="{ey}" rx="44" ry="{ry:.1f}" fill="#F7F3EC" stroke="{OUT}" stroke-width="6"/>',
         f'<circle cx="{ex + look[0] * 10:.1f}" cy="{ey + 4 + look[1] * 8:.1f}" r="{17 * min(wide, 1.15):.1f}" fill="#6B4A2E"/>',
         f'<circle cx="{ex + look[0] * 10:.1f}" cy="{ey + 4 + look[1] * 8:.1f}" r="8" fill="#140C08"/>',
         f'<circle cx="{ex + look[0] * 10 + 6:.1f}" cy="{ey - 2 + look[1] * 8:.1f}" r="4.5" fill="#fff"/>']
    if lid > 0.2:  # heavy upper lid (sleepy look from the photo)
        ly = ey - ry + 2 * ry * lid
        s.append(f'<path d="M {ex - 40} {ey - ry - 2:.1f} L {ex + 40} {ey - ry - 2:.1f} L {ex + 40} {ly:.1f} Q {ex} {ly + 8:.1f} {ex - 40} {ly:.1f} Z" fill="{SKIN2}"/>')
        s.append(f'<path d="M {ex - 40} {ly:.1f} Q {ex} {ly + 8:.1f} {ex + 40} {ly:.1f}" stroke="{OUT}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    s.append(f'<path d="M {ex - 30} {ey + ry + 10:.1f} Q {ex} {ey + ry + 22:.1f} {ex + 30} {ey + ry + 10:.1f}" stroke="#8E6FA0" stroke-width="5" fill="none" opacity="0.55"/>')
    return "".join(s)


def ruslan_head(t, mouth=0.0, expr="neutral", blink=False, look=(0, 0), hat="cap", tears=0.0):
    """Head in local coords (0,0)=head centre, ~ 500px wide. Based on the user's photo:
    black trucker cap, round cheeks, heavy lids, thin moustache, cheek tattoos."""
    o = []
    # ears
    for sg in (-1, 1):
        o.append(f'<ellipse cx="{sg * 222}" cy="40" rx="40" ry="62" fill="{SKIN}" stroke="{OUT}" stroke-width="7"/>'
                 f'<path d="M {sg * 226} 20 Q {sg * 240} 40 {sg * 226} 66" stroke="{SKIN2}" stroke-width="8" fill="none"/>')
    # face: chubby round
    o.append(f'<path d="M -205 -60 Q -215 120 -150 205 Q -60 275 0 278 Q 60 275 150 205 Q 215 120 205 -60 Q 190 -190 0 -200 Q -190 -190 -205 -60 Z" fill="{SKIN}" stroke="{OUT}" stroke-width="8"/>')
    o.append('<ellipse cx="-120" cy="110" rx="62" ry="42" fill="#F2A28E" opacity="0.35"/><ellipse cx="120" cy="110" rx="62" ry="42" fill="#F2A28E" opacity="0.35"/>')
    # cheek tattoos (thin scribbles, like on the photo)
    for sg in (-1, 1):
        o.append(f'<path d="M {sg * 110} 60 q {sg * -12} 30 {sg * 6} 56 q {sg * 16} 22 {sg * -4} 52 M {sg * 140} 90 q {sg * 18} 20 {sg * 4} 46 q {sg * -14} 18 {sg * 6} 40 M {sg * 92} 130 l {sg * -18} 22 l {sg * 12} 12" '
                 f'stroke="#4A4048" stroke-width="3.5" fill="none" stroke-linecap="round" opacity="0.8"/>')
    o.append('<path d="M 90 30 q 20 -6 40 2" stroke="#4A4048" stroke-width="3" fill="none" opacity="0.7"/>')
    # brows
    bt = {"angry": 14, "sad": -12, "shock": -20, "panic": -18, "cry": -14}.get(expr, 0)
    by = -58 - (12 if expr in ("shock", "panic") else 0)
    for sg in (-1, 1):
        o.append(f'<path d="M {sg * 130} {by - 2} L {sg * 50} {by + bt}" stroke="#3A2A20" stroke-width="12" stroke-linecap="round"/>')
    for sg in (-1, 1):
        o.append(_eye(sg * 88, -8, sg, expr, blink, look))
    # nose
    o.append(f'<path d="M -10 30 Q -34 92 -14 104 Q 0 112 14 104 Q 34 92 10 30" fill="{SKIN2}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>')
    # moustache + stubble
    o.append('<path d="M -52 150 Q -26 136 0 146 Q 26 136 52 150" stroke="#3A2A20" stroke-width="6" fill="none" opacity="0.75" stroke-dasharray="6 4"/>')
    rr = random.Random(5)
    o.append("".join(f'<circle cx="{rr.uniform(-80, 80):.0f}" cy="{rr.uniform(205, 250):.0f}" r="2.4" fill="#3A2A20" opacity="0.6"/>' for _ in range(26)))
    # mouth
    if mouth > 0.12:
        ry = 8 + 34 * mouth
        o.append(f'<ellipse cx="0" cy="{178 + ry * 0.3:.1f}" rx="{38 + 10 * mouth:.1f}" ry="{ry:.1f}" fill="#4A1414" stroke="{OUT}" stroke-width="6"/>')
        o.append(f'<rect x="-26" y="{178 + ry * 0.3 - ry + 4:.1f}" width="52" height="{min(12, ry * 0.5):.1f}" rx="3" fill="#F4EEE6"/>')
    elif expr == "happy":
        o.append(f'<path d="M -64 168 Q 0 230 64 168 Q 0 190 -64 168 Z" fill="#4A1414" stroke="{OUT}" stroke-width="6"/>')
    elif expr in ("sad", "cry"):
        o.append(f'<path d="M -36 196 Q 0 172 36 196" stroke="{OUT}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    else:
        o.append(f'<path d="M -36 182 Q 0 192 36 180" stroke="{OUT}" stroke-width="7" fill="none" stroke-linecap="round"/>'
                 '<path d="M -26 192 Q 0 204 26 192" stroke="#C98478" stroke-width="5" fill="none"/>')
    if tears > 0:
        for sg in (-1, 1):
            yy = 30 + (t * 260 + (sg + 1) * 50) % 160
            o.append(f'<path d="M {sg * 96} {yy:.0f} q -12 20 0 28 q 12 -8 0 -28 Z" fill="#7CC4FF" opacity="{tears:.2f}"/>')
    # headwear
    if hat == "cap":
        o.append(f'<path d="M -212 -40 Q -215 -250 0 -262 Q 215 -250 212 -40 Q 120 -78 0 -80 Q -120 -78 -212 -40 Z" fill="#1E2128" stroke="{OUT}" stroke-width="8"/>')
        o.append('<path d="M 120 -230 Q 200 -170 206 -60" stroke="#2C3038" stroke-width="22" fill="none" opacity="0.8"/>')
        o.append('<path d="M -130 -200 Q 0 -230 130 -200" stroke="#2A2E36" stroke-width="5" fill="none"/>')
        o.append(stext(0, -168, "DEYKUN", 40, fill="#F1F1F1", sw=0, shadow=False))
        o.append(stext(0, -126, "NINETEEN 1337", 22, fill="#D9D9D9", sw=0, shadow=False))
        o.append('<ellipse cx="0" cy="-90" rx="46" ry="15" fill="#2D5BD1" stroke="#D9D9D9" stroke-width="3"/>')
        o.append(f'<path d="M -230 -52 Q -40 -110 170 -60 Q 120 -10 -60 -14 Q -190 -12 -246 -26 Z" fill="#14161B" stroke="{OUT}" stroke-width="8" stroke-linejoin="round"/>')
    else:  # cowboy hat (the «Майкл» disguise)
        o.append(f'<path d="M -330 -60 Q -250 -10 0 -18 Q 250 -10 330 -60 Q 300 -2 0 4 Q -300 -2 -330 -60 Z" fill="#6B4423" stroke="{OUT}" stroke-width="8"/>')
        o.append(f'<path d="M -170 -40 Q -180 -230 -60 -250 Q 0 -200 60 -250 Q 180 -230 170 -40 Q 0 -60 -170 -40 Z" fill="#7A4E2A" stroke="{OUT}" stroke-width="8"/>')
        o.append(f'<path d="M -168 -70 Q 0 -96 168 -70 L 166 -42 Q 0 -64 -166 -42 Z" fill="#2A1A10"/>')
        o.append(star4(0, -60, 18, "#E8B740") + star4(0, -60, 18, "#E8B740", rot=45))
    return "".join(o)


def puffer(w=1.0, arms_up=0.0):
    """Silver glossy puffer jacket (from the photo), local coords: neck at (0,0)."""
    o = []
    if arms_up > 0:
        for sg in (-1, 1):
            a = lerp(0, 1, arms_up)
            o.append(f'<path d="M {sg * 300} 120 Q {sg * 420} {lerp(260, -60, a):.0f} {sg * 400} {lerp(500, -340, a):.0f}" stroke="{OUT}" stroke-width="150" fill="none" stroke-linecap="round"/>'
                     f'<path d="M {sg * 300} 120 Q {sg * 420} {lerp(260, -60, a):.0f} {sg * 400} {lerp(500, -340, a):.0f}" stroke="url(#gPuff)" stroke-width="136" fill="none" stroke-linecap="round"/>'
                     f'<circle cx="{sg * 400}" cy="{lerp(500, -400, a):.0f}" r="52" fill="{SKIN}" stroke="{OUT}" stroke-width="7"/>')
    o.append(f'<path d="M -420 900 Q -440 260 -300 120 Q -160 30 0 40 Q 160 30 300 120 Q 440 260 420 900 Z" fill="url(#gPuff)" stroke="{OUT}" stroke-width="9"/>')
    for k in range(1, 7):  # quilting
        y = 80 + k * 115
        o.append(f'<path d="M -410 {y + 30} Q -200 {y - 20} -10 {y + 10}" stroke="#5A5E66" stroke-width="7" fill="none" opacity="0.8"/>'
                 f'<path d="M 10 {y + 10} Q 200 {y - 20} 410 {y + 30}" stroke="#5A5E66" stroke-width="7" fill="none" opacity="0.8"/>')
    for x, y, l in ((-260, 220, 120), (-200, 420, 160), (230, 300, 140), (300, 520, 110), (-320, 600, 130), (150, 640, 120)):
        o.append(f'<path d="M {x} {y} q {l * 0.4} {-l * 0.3} {l} {-l * 0.1}" stroke="#FFFFFF" stroke-width="14" fill="none" opacity="0.55" stroke-linecap="round"/>')
    # hood / collar around the neck
    o.append(f'<path d="M -230 90 Q -200 -40 -90 -50 L -60 60 Q -150 80 -180 150 Z" fill="#4E525A" stroke="{OUT}" stroke-width="7"/>'
             f'<path d="M 230 90 Q 200 -40 90 -50 L 60 60 Q 150 80 180 150 Z" fill="#4E525A" stroke="{OUT}" stroke-width="7"/>')
    o.append(f'<path d="M -70 40 L 0 120 L 70 40 Q 0 70 -70 40 Z" fill="#1A1C22"/>')
    # zipper(s)
    for zx in (-12, 30):
        o.append(f'<line x1="{zx}" y1="110" x2="{zx + 10}" y2="900" stroke="#15171C" stroke-width="10"/>')
        o.append("".join(f'<rect x="{zx - 6 + k * 0.1:.1f}" y="{120 + k * 22}" width="12" height="8" fill="#2E3138"/>' for k in range(36)))
    return "".join(o)


def ruslan(t, cx, cy, s, mouth=0.0, expr="neutral", blink=False, look=(0, 0), hat="cap", tilt=0.0, arms_up=0.0, tears=0.0):
    """Head centre at (cx, cy)."""
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s:.3f})">'
            f'<g transform="translate(0,300)">{puffer(arms_up=arms_up)}</g>'
            f'<rect x="-70" y="240" width="140" height="90" fill="{SKIN2}"/>'
            f'<g transform="rotate({tilt:.2f} 0 250) translate(0,250) scale(1.22) translate(0,-250)">{ruslan_head(t, mouth, expr, blink, look, hat, tears)}</g></g>')


def mom(t, cx, cy, s, mouth=0.0, angry=1.0, blink=False):
    rr = random.Random(3)
    curls = "".join(f'<circle cx="{math.cos(a) * r:.0f}" cy="{-40 + math.sin(a) * r * 0.9:.0f}" r="{rr.uniform(38, 56):.0f}" fill="#8A4A24" stroke="{OUT}" stroke-width="6"/>'
                    for a, r in ((k * 0.42 + 3.3, 225 + rr.uniform(-15, 15)) for k in range(16)) if math.sin(a) < 0.55)
    o = [f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s:.3f})">', curls,
         f'<path d="M -380 900 Q -380 330 -200 300 L 200 300 Q 380 330 380 900 Z" fill="#E58FA0" stroke="{OUT}" stroke-width="9"/>',
         f'<path d="M -120 300 L 0 380 L 120 300 L 70 290 L 0 340 L -70 290 Z" fill="#F7EFE8" stroke="{OUT}" stroke-width="6"/>',
         f'<circle cx="0" cy="420" r="20" fill="#E8B740" stroke="{OUT}" stroke-width="5"/>',
         f'<rect x="-60" y="220" width="120" height="100" fill="{SKIN2}"/>',
         f'<ellipse cx="0" cy="40" rx="200" ry="230" fill="{SKIN}" stroke="{OUT}" stroke-width="8"/>',
         '<ellipse cx="-110" cy="110" rx="50" ry="34" fill="#F28A8A" opacity="0.5"/><ellipse cx="110" cy="110" rx="50" ry="34" fill="#F28A8A" opacity="0.5"/>']
    for sg in (-1, 1):
        ex = sg * 75
        if blink:
            o.append(f'<path d="M {ex - 30} 10 Q {ex} 22 {ex + 30} 10" stroke="{OUT}" stroke-width="7" fill="none"/>')
        else:
            o.append(f'<ellipse cx="{ex}" cy="10" rx="34" ry="28" fill="#fff" stroke="{OUT}" stroke-width="6"/><circle cx="{ex}" cy="14" r="14" fill="#4A3020"/><circle cx="{ex + 4}" cy="10" r="4" fill="#fff"/>')
            o.append(f'<path d="M {ex - 36} -8 L {ex + 36} -8 L {ex + 36} {-18 + 26 * angry:.0f} Q {ex} {-6 + 26 * angry:.0f} {ex - 36} {-18 + 26 * angry:.0f} Z" fill="{SKIN2}"/>')
        o.append(f'<path d="M {sg * 120} -50 L {sg * 40} {-50 + 30 * angry:.0f}" stroke="#5A3018" stroke-width="12" stroke-linecap="round"/>')
    o.append(f'<path d="M -8 40 Q -24 90 0 96 Q 24 90 8 40" fill="{SKIN2}" stroke="{OUT}" stroke-width="5"/>')
    if mouth > 0.12:
        o.append(f'<ellipse cx="0" cy="170" rx="{34 + 10 * mouth:.1f}" ry="{8 + 30 * mouth:.1f}" fill="#4A1414" stroke="{OUT}" stroke-width="6"/>')
    else:
        o.append(f'<path d="M -34 176 Q 0 156 34 176" stroke="{OUT}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    o.append(f'<g transform="translate(300,300) rotate({-20 + 10 * math.sin(t * 9):.1f})"><rect x="-14" y="-260" width="28" height="260" rx="10" fill="#B8BCC4" stroke="{OUT}" stroke-width="6"/>'
             f'<path d="M -70 -300 Q 0 -230 70 -300 Q 0 -360 -70 -300 Z" fill="#B8BCC4" stroke="{OUT}" stroke-width="6"/><circle cx="0" cy="0" r="40" fill="{SKIN}" stroke="{OUT}" stroke-width="6"/></g>')
    o.append("</g>")
    return "".join(o)


def klod(t, x, y, w, mouth=0.0, expr="neutral", blink=False):
    """Клод the boar: red block with snout (2D blocky). (x, y) = top-left of the face."""
    return klod_block(x, y, w, t, mouth=mouth, expr=expr, blink=blink, legs=True)
