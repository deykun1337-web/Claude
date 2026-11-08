"""«Воздухан» — trend short (2D): Руслан Дейкун Кабанович + Клод the boar. Seamless loop. 30 fps."""
import math, os, random, re, sys
from multiprocessing import Pool
import cairosvg
import base
from base import tw, fit, clamp, prog, lerp, e_out, e_in, e_back, popscale, stext, star4, mouth_at, FONT
from kit import e_inout
from chars import ruslan, klod
import lib2d
from lib2d import DEFS, room, card, brackets, box, stamp, YEL, RED, GRN, MONO
from timeline import *

FPS30 = 30
NF = int(DUR * FPS30)
S = [s - 0.05 for s in VOICE_START]; E = VOICE_END
CYAN = "#7FE3FF"


def wt(line, prefix):
    for w in WORDS:
        if w["line"] == line and re.sub(r"[^\w-]", "", w["w"]).lower().startswith(prefix): return w["t0"]
    return VOICE_START[line]


def line_now(t):
    i = 0
    for k, s in enumerate(VOICE_START):
        if t >= s - 0.05: i = k
    return i


def talking(t, spk):
    i = line_now(t)
    return SPK[i] == spk and VOICE_START[i] <= t <= VOICE_END[i] + 0.08


def mth(t, spk):
    return mouth_at(int(t * 60)) if talking(t, spk) else 0.0


lib2d.mth = mth  # room() draws Клод with this


def blink(t, off=0.0):
    return ((t + off) % 3.3) < 0.12


R_EXPR = {0: "smug", 2: "smug", 4: "neutral", 6: "angry", 8: "happy", 10: "smug"}


# ---------------------------------------------------------------- wind
WIND_KEYS = [(0, 0.0), (S[4], 0.35), (S[6], 1.0), (S[8], 0.55), (S[10], 0.15), (DUR - 0.3, 0.0)]


def wind(t):
    v = 0.0
    for k, (ts, val) in enumerate(WIND_KEYS):
        if t >= ts:
            prev = WIND_KEYS[k - 1][1] if k else 0
            v = lerp(prev, val, e_out(prog(t, ts, ts + 0.6)))
    return v


def wind_fx(t, w):
    if w < 0.02: return ""
    rr = random.Random(7); o = []
    for k in range(int(10 + 22 * w)):
        y = rr.uniform(150, 1800); sp = rr.uniform(900, 1700) * (0.5 + w); ln = rr.uniform(120, 320)
        x = (rr.uniform(0, 2000) + t * sp) % 2200 - 400
        o.append(f'<path d="M {x:.0f} {y:.0f} q {ln / 2:.0f} {-18 - 10 * math.sin(t * 6 + k):.0f} {ln:.0f} 0" stroke="#FFFFFF" stroke-width="{3 + 4 * w:.1f}" fill="none" opacity="{0.25 + 0.4 * w:.2f}" stroke-linecap="round"/>')
    for k in range(int(6 * w)):  # flying paper sheets
        x = (rr.uniform(0, 1500) + t * 900 * w) % 1500 - 200; y = rr.uniform(300, 1500) + 60 * math.sin(t * 5 + k); r = t * 400 + k * 70
        o.append(f'<rect x="{x - 40:.0f}" y="{y - 50:.0f}" width="80" height="100" fill="#F4EFE6" stroke="#9A9080" stroke-width="3" transform="rotate({r:.0f} {x:.0f} {y:.0f})"/>')
    return "".join(o)


def fan(t, cx, cy, r, w):
    if w < 0.25: return ""
    a = t * 900 * w
    blades = "".join(f'<path d="M 0 0 Q {r * 0.3:.0f} {-r * 0.9:.0f} {r * 0.05:.0f} {-r:.0f} Q {-r * 0.35:.0f} {-r * 0.8:.0f} 0 0 Z" fill="#B8C4D0" stroke="#16100F" stroke-width="6" transform="rotate({a + k * 120:.0f})"/>' for k in range(3))
    return (f'<g transform="translate({cx},{cy})" opacity="{clamp((w - 0.25) * 2):.2f}"><circle r="{r + 20}" fill="none" stroke="#5A6470" stroke-width="12"/>'
            + "".join(f'<line x1="{(r + 20) * math.cos(k * 0.52):.0f}" y1="{(r + 20) * math.sin(k * 0.52):.0f}" x2="0" y2="0" stroke="#5A6470" stroke-width="3" opacity="0.5"/>' for k in range(12))
            + blades + '<circle r="34" fill="#5A6470" stroke="#16100F" stroke-width="6"/></g>')


# ---------------------------------------------------------------- HUD: воздухан-метр
V_KEYS = [(S[3], 40), (S[4], 72), (wt(5, "девяност"), 99)]


def vval(t):
    v = 12
    for k, (ts, val) in enumerate(V_KEYS):
        if t >= ts:
            prev = V_KEYS[k - 1][1] if k else 12
            v = lerp(prev, val, e_out(prog(t, ts, ts + 0.6)))
    return int(round(v))


def hud(t):
    if not (S[3] <= t < S[10]): return ""
    v = vval(t); col = GRN if v < 40 else (YEL if v < 80 else RED)
    return ('<g transform="translate(150,110)"><rect width="560" height="120" rx="14" fill="#0E1116" opacity="0.88" stroke="#2C313B" stroke-width="3"/>'
            '<circle cx="28" cy="24" r="7" fill="#FF5F57"/><circle cx="50" cy="24" r="7" fill="#FEBC2E"/><circle cx="72" cy="24" r="7" fill="#28C840"/>'
            + stext(24, 66, "$ воздухан-метр", 30, fill="#C9D1DC", sw=0, shadow=False, anchor="start").replace(FONT, MONO)
            + stext(380, 66, f"{v}%", 44, fill=col, sw=0, shadow=False, anchor="start").replace(FONT, MONO)
            + f'<rect x="24" y="92" width="512" height="10" rx="5" fill="#252A33"/><rect x="24" y="92" width="{512 * v / 100:.0f}" height="10" rx="5" fill="{col}"/></g>')


# ---------------------------------------------------------------- scenes
def close(t, t0, w):
    zoom = 1 + 0.05 * prog(t, t0, t0 + 3)
    ex = R_EXPR.get(line_now(t), "neutral")
    sway = 6 * w * math.sin(t * 13)
    return (room(t, show_klod=False) + '<rect width="1080" height="1920" fill="#000" opacity="0.35"/>'
            + fan(t, 540, 760, 360, w)
            + f'<g transform="translate(540,1100) scale({zoom:.4f}) translate(-540,-1100) translate({sway:.1f},0)">'
            + ruslan(t, 540, 860, 1.05, mth(t, "p"), ex, blink(t), (0, 0), "cap", tilt=3 * math.sin(t * 1.3) + 4 * w * math.sin(t * 9)) + "</g>")


def promise_icons(t):
    o = []
    for k, (word, label, x, y, col) in enumerate((("качалк", "КАЧАЛКА", 230, 520, "#FF7A59"), ("бизнес", "БИЗНЕС", 820, 470, "#3DDC84"), ("дуба", "ДУБАЙ", 540, 330, "#FFC83D"))):
        t0 = wt(0, word)
        if t >= t0:
            o.append(lib2d.stext(x, y, label, 66, fill=col, sc=popscale(t, t0, 0.3), rot=-6 + 6 * k))
    return "".join(o)


def mondays(t, t0):
    o = ['<rect width="1080" height="1920" fill="#0B0D11"/>', stext(540, 260, "ПОНЕДЕЛЬНИКИ", 80, fill="#fff", sw=0, shadow=False)]
    n = int(round(47 * e_out(prog(t, t0, t0 + 1.4))))
    for k in range(47):
        c, r = k % 7, k // 7
        x = 120 + c * 125; y = 420 + r * 150
        o.append(f'<rect x="{x}" y="{y}" width="105" height="125" rx="12" fill="#1A1E26" stroke="#2C313B" stroke-width="3"/>'
                 + stext(x + 52, y + 40, "ПН", 30, fill="#8A93A6", sw=0, shadow=False))
        if k < n:
            o.append(f'<path d="M {x + 15} {y + 70} L {x + 90} {y + 112} M {x + 90} {y + 70} L {x + 15} {y + 112}" stroke="{RED}" stroke-width="9" stroke-linecap="round"/>')
    o.append(stext(540, 1560, f"{n}", 160, fill=YEL, sc=1 + 0.05 * math.sin(t * 8)))
    return "".join(o)


def klod_close(t, t0, w, smug=False, note=False):
    z = 1 + 0.06 * prog(t, t0, t0 + 3)
    o = ['<rect width="1080" height="1920" fill="#141010"/>', f'<g transform="translate(540,1000) scale({z:.4f}) translate(-540,-1000)">',
         '<rect x="0" y="1260" width="1080" height="660" fill="#2A1A14"/><rect x="0" y="1250" width="1080" height="30" fill="#3A2A22"/>']
    kx = 160 + 14 * w * math.sin(t * 15)
    o.append(klod(t, kx, 700, 760, mouth=mth(t, "n"), expr="smug" if smug else "neutral", blink=blink(t, 0.4)))
    if w > 0.3:  # bristles blown by the wind
        for k in range(9):
            bx = 300 + k * 55; ln = 60 + 40 * w + 15 * math.sin(t * 20 + k)
            o.append(f'<path d="M {bx} 560 q {ln * 0.6:.0f} {-20 - 10 * math.sin(t * 25 + k):.0f} {ln:.0f} 0" stroke="#7A2F20" stroke-width="16" fill="none" stroke-linecap="round"/>')
    o.append("</g>")
    if note:
        p = e_out(prog(t, t0, t0 + 0.4))
        inner = (stext(-300, -150, "Обещания Руслана", 40, fill="#fff", sw=0, shadow=False, anchor="start")
                 + "".join(stext(-300, -70 + k * 70, f"☐ {s}".replace("☐ ", "• "), 36, fill="#C9D1DC", sw=0, shadow=False, anchor="start")
                           for k, s in enumerate(("качалка", "бизнес", "Дубай", "вынести мусор (с 12 мая)"))))
        o.append(f'<g transform="translate(0,{(1 - p) * -500:.0f})">' + card(540, 360, 720, 420, inner) + "</g>")
    if smug:
        o.append(stext(820, 420, "−0 ₽ за свет", 50, fill=CYAN, sc=popscale(t, t0 + 0.3, 0.3), rot=8))
    return "".join(o)


def scan(t, t0, w):
    return (close(t, t0, w) + brackets() + box(300, 560, 480, 560, "ВОЗДУХАН 99%" if t > wt(5, "девяност") else "АНАЛИЗ...", RED if t > wt(5, "воздух") else GRN)
            + stamp(t, wt(5, "воздух"), "ВОЗДУХАН"))


def medium_trash(t, t0, w):
    o = [room(t), '<path d="M 60 1500 Q 40 1640 120 1660 L 220 1660 Q 300 1640 280 1500 Q 230 1520 170 1515 Q 110 1520 60 1500 Z" fill="#3A414D" stroke="#0B0D10" stroke-width="7"/>',
         '<path d="M 140 1510 L 120 1450 L 170 1490 L 190 1445 L 205 1510 Z" fill="#3A414D" stroke="#0B0D10" stroke-width="6"/>',
         stext(170, 1400, "мусор (с 12 мая)", 32, fill="#C9D1DC", sw=0, shadow=False),
         ruslan(t, 520, 820, 0.62, mth(t, "p"), "happy" if line_now(t) == 8 else "neutral", blink(t), (-0.6, 0), "cap")]
    return "".join(o)


CUES = [(0, "close"), (S[1], "klod_note"), (S[2], "mondays"), (S[3], "trash"), (S[4], "close"), (S[5], "scan"), (S[6], "close"),
        (S[7], "klod_wind"), (S[8], "trash"), (S[9], "klod_smug"), (S[10], "close")]


def scene(t):
    c, t0 = CUES[0][1], 0
    for ts, name in CUES:
        if t >= ts: c, t0 = name, ts
    w = wind(t)
    if c == "close": return close(t, t0, w) + (promise_icons(t) if line_now(t) == 0 else "")
    if c == "klod_note": return klod_close(t, t0, w, note=True)
    if c == "mondays": return mondays(t, t0)
    if c == "trash": return medium_trash(t, t0, w)
    if c == "scan": return scan(t, t0, w)
    if c == "klod_wind": return klod_close(t, t0, w)
    return klod_close(t, t0, w, smug=True)


KEY_Y = {"понедельника", "качалка", "бизнес", "дубай", "сорок", "седьмой", "мусор", "воздухан", "генератор", "идей", "щетина", "кондиционер", "завтра"}


def captions(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            size = 70; gap = size * 0.3
            words = [w["disp"] for w in c]
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 960: size = int(size * 960 / total); gap = size * 0.3; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            x = 540 - total / 2; out = []
            for w in words:
                k = re.sub(r"[^\w-]", "", w).lower()
                out.append(stext(x, 1480, w, size, fill=YEL if k in KEY_Y else "#F4EFE6", stroke="#120C0A", sw=12, anchor="start"))
                x += tw(w, size) + gap
            return "".join(out)
    return ""


def compose(t):
    w = wind(t)
    dx = 10 * w * math.sin(t * 31); dy = 6 * w * math.cos(t * 27)
    return (f'<g transform="translate({dx:.1f},{dy:.1f})">{scene(t)}</g>{wind_fx(t, w)}'
            f'<rect width="1080" height="1920" fill="url(#gDark2)"/>{hud(t)}{captions(t)}')


def frame_svg(f):
    t = f / FPS30
    body = compose(t)
    if t > DUR - 0.3:  # dissolve into frame 0 for a seamless loop
        body += f'<g opacity="{e_inout(prog(t, DUR - 0.3, DUR)):.3f}">{compose(0.0)}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}'
            f'<rect width="1080" height="1920" fill="#000"/>{body}{base.WM()}</svg>')


def render(f):
    cairosvg.svg2png(bytestring=frame_svg(f).encode(), write_to=f"build/frames/{f:05d}.png")
    return f


if __name__ == "__main__":
    os.makedirs("build/frames", exist_ok=True)
    frames = [int(x) for x in sys.argv[1:]] or list(range(NF))
    with Pool(os.cpu_count()) as pool:
        for i, _ in enumerate(pool.imap_unordered(render, frames, chunksize=4)):
            if i % 300 == 0: print("frame", i, flush=True)
    print("done", len(frames))
