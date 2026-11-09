"""PREMIUM motion-design kit (SVG → cairosvg, 1080×1920). Two house looks from the best Claude-niche reels:

  LIGHT «бумага + точки» (как ИИмерсивный, reel DeIZGnxNoGX): светлый фон с точечной сеткой, белые/тёмные карточки
        с мягкой многослойной тенью, окна кода/терминала, курсор «ты», нумерованные шаги, пиксельный Клод-кабан.
  DARK  «редакционный тёмный» (как dino81club, reel DfML30xsNmi): почти чёрный фон, тёплое оранжевое свечение,
        моно-метка раздела сверху, фразы по центру с оранжевыми ключевыми словами, UI-карточки, штамп «БЕСПЛАТНО»,
        ряд иконок-плиток, графики, окно чата Claude, финальная карточка Telegram.

Usage (in a compose script):
    import sys; sys.path.insert(0, "reels/motion"); import mokit as M
    th = M.LIGHT  (or M.DARK)
    svg = M.frame(th, t, [M.bg(th, t), M.card(...), M.cursor(...), M.headline(th, t, t0, "Один *сканирует*", y=300)])
    M.render(frame_fn, seconds, "build/frames", fps=30)  → PNGs (multiprocess)  → ffmpeg as usual
Text with *stars* marks accent words (orange). Every element takes t0 = appear time and animates in itself
(ease-out rise + fade, ~0.35 s), so a scene is just a list of elements with start times.
"""
import math, os
from html import escape
from multiprocessing import Pool

W, H = 1080, 1920
SANS = "Inter"; MONO = "DejaVu Sans Mono"
LIGHT = dict(name="light", bg="#F2F1EC", dot="#C9C6BD", card="#FFFFFF", card2="#14161B", ink="#16181D", sub="#6B6F78",
             accent="#F26B3A", blue="#2F6BFF", green="#21C17A", red="#E5484D", line="#D8D5CC", glow=None)
DARK = dict(name="dark", bg="#0A0908", dot="#1A1816", card="#17140F", card2="#211C16", ink="#F6F1EA", sub="#8D857A",
            accent="#FF9A3C", blue="#5B8CFF", green="#3DDC84", red="#FF5A5F", line="#2B261F", glow="#FF7A1A")


# ------------------------------------------------------------------ easing / timing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x, s=1.6): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def appear(t, t0, d=0.35): return ease((t - t0) / d)
def gone(t, t1, d=0.25): return 1 - ease((t - t1) / d) if t1 is not None else 1.0


def wrap(el, t, t0, t1=None, rise=26, pop=False, cx=540, cy=960):
    """standard entrance: fade + rise (or springy pop) and soft exit"""
    a = appear(t, t0) * gone(t, t1)
    if a <= 0.001: return ""
    if pop:
        s = 0.6 + 0.4 * back((t - t0) / 0.45)
        return f'<g opacity="{a:.3f}" transform="translate({cx},{cy}) scale({s:.4f}) translate({-cx},{-cy})">{el}</g>'
    return f'<g opacity="{a:.3f}" transform="translate(0,{(1 - appear(t, t0)) * rise:.1f})">{el}</g>'


# ------------------------------------------------------------------ text helpers
_fonts = {}


def tw(text, size, weight=600, mono=False):
    from PIL import ImageFont
    f = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf" if mono else \
        {400: "Inter-Regular", 500: "Inter-Medium", 600: "Inter-SemiBold", 700: "Inter-Bold", 800: "Inter-ExtraBold", 900: "Inter-Black"}[weight]
    path = f if mono else f"/usr/share/fonts/opentype/inter/{f}.otf"
    k = (path, size)
    if k not in _fonts: _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k].getlength(text)


def rich(th, x, y, text, size, weight=700, anchor="middle", color=None, maxw=920, lh=1.18, reveal=None):
    """multi-line text; *word* = accent colour. reveal=(t, t0, per_word) types words in one by one."""
    words = text.split(); lines, cur = [], []
    for w in words:
        if cur and tw(" ".join(x.replace("*", "") for x in cur + [w]), size, weight) > maxw: lines.append(cur); cur = [w]
        else: cur.append(w)
    lines.append(cur); out = []; idx = 0
    for li, ln in enumerate(lines):
        plain = " ".join(w.replace("*", "") for w in ln); lw = tw(plain, size, weight)
        xx = x - lw / 2 if anchor == "middle" else x; yy = y + (li - (len(lines) - 1) / 2) * size * lh
        for w in ln:
            acc = "*" in w; s = w.replace("*", ""); op = 1.0
            if reveal: tt, t0, pw = reveal; op = ease((tt - t0 - idx * pw) / 0.18)
            idx += 1
            if op > 0.001:
                out.append(f'<text x="{xx:.1f}" y="{yy:.1f}" font-family="{SANS}" font-weight="{weight}" font-size="{size}" '
                           f'fill="{th["accent"] if acc else (color or th["ink"])}" opacity="{op:.3f}" dominant-baseline="middle">{escape(s)}</text>')
            xx += tw(s + " ", size, weight)
    return "".join(out)


# ------------------------------------------------------------------ backgrounds
def bg(th, t, glow_at=(540, 820), glow_r=760, drift=True):
    dx = (t * 6) % 36 if drift else 0
    g = (f'<pattern id="dots" width="36" height="36" patternUnits="userSpaceOnUse" patternTransform="translate({dx:.1f},0)">'
         f'<circle cx="18" cy="18" r="{2.0 if th["name"] == "light" else 1.4}" fill="{th["dot"]}"/></pattern>')
    out = f'<defs>{g}</defs><rect width="{W}" height="{H}" fill="{th["bg"]}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>'
    if th["glow"]:
        br = 0.85 + 0.15 * math.sin(t * 1.3)
        out += (f'<defs><radialGradient id="glow" cx="{glow_at[0]}" cy="{glow_at[1]}" r="{glow_r * br:.0f}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" stop-color="{th["glow"]}" stop-opacity="0.30"/><stop offset="0.45" stop-color="{th["glow"]}" stop-opacity="0.08"/>'
                f'<stop offset="1" stop-color="{th["glow"]}" stop-opacity="0"/></radialGradient></defs><rect width="{W}" height="{H}" fill="url(#glow)"/>')
    # vignette
    out += ('<defs><radialGradient id="vig" cx="540" cy="960" r="1150" gradientUnits="userSpaceOnUse"><stop offset="0.55" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="{0.10 if th["name"] == "light" else 0.55}"/></radialGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
    return out


def shadow(x, y, w, h, r, strength=1.0, dy=18, glow=None):
    """soft shadow made of 10 expanding translucent rounded rects (cairosvg has no blur)"""
    out = []
    for k in range(10, 0, -1):
        e = k * 3.2
        col = glow or "#000"; op = (0.018 if not glow else 0.03) * strength
        out.append(f'<rect x="{x - e:.1f}" y="{y - e + dy * (0 if glow else 1):.1f}" width="{w + 2 * e:.1f}" height="{h + 2 * e:.1f}" rx="{r + e:.1f}" fill="{col}" opacity="{op:.3f}"/>')
    return "".join(out)


# ------------------------------------------------------------------ building blocks
def card(th, x, y, w, h, inner="", dark=False, r=34, stroke=None, glow=False):
    fill = th["card2"] if dark else th["card"]
    st = stroke or (th["line"] if th["name"] == "dark" else ("#00000010" if not dark else "#FFFFFF12"))
    return (shadow(x, y, w, h, r, 1.2 if th["name"] == "light" else 2.0, glow=th["glow"] if glow and th["glow"] else None)
            + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{st}" stroke-width="2"/>'
            + f'<g transform="translate({x},{y})">{inner}</g>')


def window(th, x, y, w, h, title="", body="", dark=True, glow=False):
    """macOS-like window: traffic lights + title bar"""
    tc = "#8D857A" if dark else "#6B6F78"
    bar = ''.join(f'<circle cx="{34 + i * 26}" cy="34" r="8.5" fill="{c}"/>' for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")))
    bar += f'<text x="{122}" y="35" font-family="{SANS}" font-size="22" font-weight="600" fill="{tc}" dominant-baseline="middle">{escape(title)}</text>'
    bar += f'<rect x="0" y="66" width="{w}" height="1.5" fill="{"#FFFFFF14" if dark else "#00000012"}"/>'
    return card(th, x, y, w, h, bar + f'<g transform="translate(0,68)">{body}</g>', dark=dark, r=26, glow=glow)


SYN = {"kw": "#FF7AB6", "fn": "#7AB8FF", "str": "#9BE38B", "num": "#FFB86B", "cm": "#6F7785", "tx": "#E8E6E3"}


def code(lines, t=None, t0=0.0, cps=40, size=25, hi=None, x=32, y=36, lh=1.6, hw=860):
    """lines = [[(kind, text), ...], ...]; typed out at cps chars/s when t is given; hi = {line_idx: colour} highlight bar"""
    out = []; shown = 1e9 if t is None else max(0, (t - t0) * cps); n = 0
    for i, ln in enumerate(lines):
        yy = y + i * size * lh
        if hi and i in hi and shown > n: out.append(f'<rect x="0" y="{yy - size * 0.95:.1f}" width="{hw}" height="{size * 1.45:.1f}" fill="{hi[i]}" opacity="0.28"/>')
        xx = x
        for kind, txt in ln:
            vis = txt[:int(clamp(shown - n, 0, len(txt)))]; n += len(txt)
            if vis: out.append(f'<text x="{xx:.1f}" y="{yy:.1f}" font-family="{MONO}" font-size="{size}" fill="{SYN.get(kind, kind)}" xml:space="preserve">{escape(vis)}</text>')
            xx += tw(txt, size, mono=True)
        n += 1
    if t is not None and shown < n and int(t * 2.2) % 2 == 0:   # blinking caret
        out.append(f'<rect x="{x}" y="{y + (len(lines)) * size * lh - size:.0f}" width="3" height="{size}" fill="#E8E6E3" opacity="0"/>')
    return "".join(out)


def terminal(th, x, y, w, h, cmds, t, t0, title="Claude Code"):
    """cmds = [("> /plugin install x", 0.0), ("✓ Installed", 1.2)]: each line appears/typed at its own offset"""
    body = []
    for i, (txt, dt) in enumerate(cmds):
        if t < t0 + dt: break
        k = int(clamp((t - t0 - dt) * 45, 0, len(txt))) if txt.startswith(">") else len(txt)
        col = th["green"] if txt.startswith("✓") else ("#E8E6E3" if txt.startswith(">") else "#9C958A")
        body.append(f'<text x="34" y="{56 + i * 44}" font-family="{MONO}" font-size="25" fill="{col}" xml:space="preserve">{escape(txt[:k])}</text>')
    return window(th, x, y, w, h, title, "".join(body), dark=True, glow=True)


def cursor(th, x, y, label="ты", click=0.0):
    """arrow pointer with a small orange name tag; click=0..1 draws a ripple"""
    rip = f'<circle cx="{x}" cy="{y}" r="{10 + 40 * click:.1f}" fill="none" stroke="{th["accent"]}" stroke-width="4" opacity="{(1 - click) * 0.8:.2f}"/>' if 0 < click < 1 else ""
    arrow = (f'<path d="M{x},{y} l0,52 l13,-12 l11,24 l10,-5 l-11,-23 l18,-1 z" fill="#FFFFFF" stroke="#16181D" stroke-width="3.5" stroke-linejoin="round"/>')
    tag = (f'<rect x="{x + 30}" y="{y + 50}" width="{tw(label, 22, 700) + 26:.0f}" height="36" rx="10" fill="{th["accent"]}"/>'
           f'<text x="{x + 43}" y="{y + 69}" font-family="{SANS}" font-size="22" font-weight="700" fill="#fff" dominant-baseline="middle">{escape(label)}</text>')
    return rip + arrow + tag


def move(t, path):
    """piecewise eased motion: path = [(t, x, y), ...] → (x, y)"""
    if t <= path[0][0]: return path[0][1:]
    for (a, x0, y0), (b, x1, y1) in zip(path, path[1:]):
        if t <= b: k = ease((t - a) / (b - a)); return (x0 + (x1 - x0) * k, y0 + (y1 - y0) * k)
    return path[-1][1:]


def step(th, x, y, n, title, body="", dark=False, w=300, h=400):
    """numbered step card (blue number chip, mono title)"""
    ink = "#F6F1EA" if dark else th["ink"]
    inner = (f'<rect x="26" y="26" width="52" height="52" rx="12" fill="{th["blue"]}"/>'
             f'<text x="52" y="53" text-anchor="middle" dominant-baseline="middle" font-family="{SANS}" font-size="30" font-weight="800" fill="#fff">{n}</text>'
             f'<text x="96" y="53" dominant-baseline="middle" font-family="{MONO}" font-size="25" fill="{th["blue"] if not dark else "#9DB8FF"}">{escape(title)}</text>' + body)
    grid = ""
    if not dark:   # faint blueprint grid inside light cards
        grid = "".join(f'<line x1="{gx}" y1="12" x2="{gx}" y2="{h - 12}" stroke="#E9ECF3" stroke-width="1.5"/>' for gx in range(30, w - 10, 30))
        grid += "".join(f'<line x1="12" y1="{gy}" x2="{w - 12}" y2="{gy}" stroke="#E9ECF3" stroke-width="1.5"/>' for gy in range(30, h - 10, 30))
    return card(th, x, y, w, h, grid + inner, dark=dark, r=30)


def big_number(th, x, y, value, t, t0, size=260, suffix="", d=0.9, color=None):
    v = int(round(value * ease((t - t0) / d)))
    s = f"{v:,}".replace(",", " ") + suffix
    return (f'<text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle" font-family="{SANS}" font-weight="900" '
            f'font-size="{size}" fill="{color or th["ink"]}" letter-spacing="-6">{s}</text>')


def stamp(th, x, y, text="БЕСПЛАТНО", t=1, t0=0, rot=-12, col=None):
    k = back((t - t0) / 0.4, 2.2); s = 1.8 - 0.8 * k if t >= t0 else 0
    if s <= 0: return ""
    col = col or th["green"]; w = tw(text, 34, 900) + 40
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({s:.3f})" opacity="{clamp((t - t0) / 0.12):.2f}">'
            f'<rect x="{-w / 2}" y="-30" width="{w}" height="60" rx="8" fill="none" stroke="{col}" stroke-width="5"/>'
            f'<text x="0" y="2" text-anchor="middle" dominant-baseline="middle" font-family="{SANS}" font-size="34" font-weight="900" fill="{col}">{escape(text)}</text></g>')


def tiles(th, cx, y, items, t, t0, active=None, size=150, gap=26):
    """row of icon tiles: items = [("🔎", "Сканер"), ...]; active = index glowing"""
    n = len(items); x0 = cx - (n * size + (n - 1) * gap) / 2; out = []
    for i, (emo, lab) in enumerate(items):
        a = appear(t, t0 + i * 0.08); x = x0 + i * (size + gap)
        if a <= 0: continue
        on = active == i
        inner = (f'<text x="{size / 2}" y="{size * 0.42}" text-anchor="middle" dominant-baseline="middle" font-family="Noto Color Emoji" font-size="{size * 0.36:.0f}">{emo}</text>'
                 f'<text x="{size / 2}" y="{size * 0.8}" text-anchor="middle" font-family="{SANS}" font-size="{size * 0.13:.0f}" font-weight="600" fill="{th["sub"]}">{escape(lab)}</text>')
        el = card(th, x, y, size, size, inner, dark=th["name"] == "dark", r=28, stroke=th["accent"] if on else None, glow=on)
        out.append(f'<g opacity="{a:.2f}" transform="translate(0,{(1 - a) * 30:.1f})">{el}</g>')
    return "".join(out)


def ring(th, cx, cy, pct, t, t0, r=150, label="покрытие", d=1.2):
    p = pct * ease((t - t0) / d); circ = 2 * math.pi * r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{th["line"]}" stroke-width="34"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{th["green"]}" stroke-width="34" stroke-linecap="round" '
            f'stroke-dasharray="{circ * p / 100:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>'
            f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" dominant-baseline="middle" font-family="{SANS}" font-size="{r * 0.55:.0f}" font-weight="900" fill="{th["ink"] if th["name"] == "dark" else "#fff"}">{p:.0f}%</text>'
            f'<text x="{cx}" y="{cy + r * 0.38:.0f}" text-anchor="middle" font-family="{SANS}" font-size="{r * 0.15:.0f}" fill="{th["sub"]}">{escape(label)}</text>')


def label(th, text, y=150):
    """small mono section tag at the top (dark editorial look)"""
    return (f'<text x="540" y="{y}" text-anchor="middle" font-family="{MONO}" font-size="24" letter-spacing="6" '
            f'fill="{th["sub"]}">{escape(text.upper())}</text>')


def headline(th, t, t0, text, y=330, size=64, t1=None, weight=800, per_word=0.07):
    """phrase that writes itself word by word; *accent* words in orange"""
    if t < t0 or (t1 is not None and t > t1 + 0.3): return ""
    return f'<g opacity="{gone(t, t1):.3f}">' + rich(th, 540, y, text, size, weight, reveal=(t, t0, per_word)) + "</g>"


def chat(th, x, y, w, h, msgs, t, t0, title="Claude"):
    """chat window: msgs = [("me"|"ai", text, dt)], AI shows typing dots before its reply"""
    body = []; yy = 40
    for who, txt, dt in msgs:
        if t < t0 + dt: break
        me = who == "me"; fs = 26
        lines = []; cur = ""
        for wd in txt.split():
            if cur and tw(cur + " " + wd, fs, 500) > w * 0.62: lines.append(cur); cur = wd
            else: cur = (cur + " " + wd).strip()
        lines.append(cur); bw = max(tw(l, fs, 500) for l in lines) + 44; bh = len(lines) * fs * 1.35 + 30
        bx = w - bw - 26 if me else 26
        typing = (not me) and t < t0 + dt + 0.7
        a = appear(t, t0 + dt, 0.25)
        fill = th["accent"] if me else ("#2A241D" if th["name"] == "dark" else "#EEF0F4")
        col = "#fff" if me else th["ink"]
        if typing:
            dots = "".join(f'<circle cx="{bx + 30 + i * 22}" cy="{yy + 30}" r="7" fill="{th["sub"]}" opacity="{0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 9 - i)):.2f}"/>' for i in range(3))
            body.append(f'<rect x="{bx}" y="{yy}" width="96" height="60" rx="22" fill="{fill}"/>' + dots); yy += 80
            break
        g = f'<rect x="{bx}" y="{yy}" width="{bw}" height="{bh}" rx="24" fill="{fill}"/>'
        g += "".join(f'<text x="{bx + 22}" y="{yy + 22 + (i + 0.75) * fs * 1.35 - 6:.0f}" font-family="{SANS}" font-size="{fs}" font-weight="500" fill="{col}">{escape(l)}</text>' for i, l in enumerate(lines))
        body.append(f'<g opacity="{a:.2f}" transform="translate(0,{(1 - a) * 16:.0f})">{g}</g>'); yy += bh + 18
    return window(th, x, y, w, h, title, "".join(body), dark=th["name"] == "dark")


# pixel Klod-boar mascot (12×10), like the pixel crab in the reference — our hero, always a boar
BOAR = ["..dd......dd..",
        "..dsd....dsd..",
        "..sssssssssss.",
        ".sssssssssssss",
        ".ssWkssssWkss.",
        "sssssssssssss.",
        "sssPPPPPPPsss.",
        "sstPpPPPpPtss.",
        "sstPPPPPPPtss.",
        ".sssssssssss..",
        "..dd.dd.dd.dd."]
PAL = {"s": "#E5684B", "d": "#A9442E", "W": "#FFFFFF", "k": "#151515", "P": "#F49A82", "p": "#7A2A1E", "t": "#FFF6E6"}


def boar(x, y, px=9, t=0.0, bob=True):
    oy = (math.sin(t * 6) * 2 if bob else 0); out = []
    for r, row in enumerate(BOAR):
        for c, ch in enumerate(row):
            if ch in PAL: out.append(f'<rect x="{x + c * px}" y="{y + r * px + oy:.1f}" width="{px}" height="{px}" fill="{PAL[ch]}"/>')
    return "".join(out)


def arrow(th, x1, y1, x2, y2, t, t0, col=None, w=8):
    k = ease((t - t0) / 0.4); xe, ye = x1 + (x2 - x1) * k, y1 + (y2 - y1) * k
    if k <= 0: return ""
    ang = math.atan2(ye - y1, xe - x1); hl = 26
    p1 = (xe - hl * math.cos(ang - 0.5), ye - hl * math.sin(ang - 0.5)); p2 = (xe - hl * math.cos(ang + 0.5), ye - hl * math.sin(ang + 0.5))
    c = col or th["blue"]
    return (f'<line x1="{x1}" y1="{y1}" x2="{xe:.1f}" y2="{ye:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{xe:.1f},{ye:.1f} L{p2[0]:.1f},{p2[1]:.1f}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def candles(th, x, y, w, h, t, t0, n=26, seed=3):
    import random
    r = random.Random(seed); v = 0.5; out = []; k = clamp((t - t0) / 1.2)
    for i in range(int(n * k)):
        o = v; v = clamp(v + r.uniform(-0.12, 0.13), 0.08, 0.92); hi_, lo_ = max(o, v) + r.uniform(0, 0.06), min(o, v) - r.uniform(0, 0.06)
        cx = x + i * w / n; col = th["green"] if v >= o else th["red"]; yy = lambda q: y + h * (1 - q)
        out.append(f'<line x1="{cx + w / n / 2 - 3:.1f}" y1="{yy(hi_):.1f}" x2="{cx + w / n / 2 - 3:.1f}" y2="{yy(lo_):.1f}" stroke="{col}" stroke-width="3"/>'
                   f'<rect x="{cx + 2:.1f}" y="{yy(max(o, v)):.1f}" width="{w / n - 10:.1f}" height="{max(4, h * abs(v - o)):.1f}" rx="2" fill="{col}"/>')
    return "".join(out)


def tg_card(th, x, y, t, t0, channel="ДЕЙКУН × Claude", subs="Гайды и промпты каждый день", btn="Подписаться"):
    """phone-like Telegram channel card + button (end screen CTA)"""
    w, h = 520, 640
    inner = (f'<circle cx="80" cy="90" r="44" fill="{th["accent"]}"/>' + f'<g transform="translate(36,52)">{boar(0, 0, 7, t)}</g>'
             f'<text x="146" y="82" font-family="{SANS}" font-size="30" font-weight="800" fill="{th["ink"] if th["name"] == "dark" else "#16181D"}">{escape(channel)}</text>'
             f'<text x="146" y="118" font-family="{SANS}" font-size="22" fill="{th["sub"]}">{escape(subs)}</text>'
             + "".join(f'<rect x="36" y="{170 + i * 92}" width="{448 - i * 60}" height="68" rx="18" fill="{"#2A241D" if th["name"] == "dark" else "#EEF0F4"}"/>' for i in range(3))
             + f'<rect x="36" y="{h - 120}" width="448" height="84" rx="22" fill="#2AABEE"/>'
             f'<text x="260" y="{h - 76}" text-anchor="middle" dominant-baseline="middle" font-family="{SANS}" font-size="32" font-weight="800" fill="#fff">{escape(btn)}</text>')
    return wrap(card(th, x, y, w, h, inner, dark=th["name"] == "dark", r=44), t, t0, pop=True, cx=x + w / 2, cy=y + h / 2)


def keyword_bar(th, x, y, word, t, t0):
    """comment input with the keyword typed in + send button (CTA «напиши СЛОВО»)"""
    k = int(clamp((t - t0 - 0.3) * 8, 0, len(word))); w = 720
    inner = (f'<circle cx="46" cy="46" r="28" fill="{th["accent"]}"/><text x="46" y="47" text-anchor="middle" dominant-baseline="middle" font-family="{SANS}" font-size="20" font-weight="800" fill="#fff">ты</text>'
             f'<text x="94" y="48" dominant-baseline="middle" font-family="{SANS}" font-size="34" font-weight="700" fill="{th["ink"] if th["name"] == "dark" else "#16181D"}">{escape(word[:k])}</text>'
             f'<circle cx="{w - 48}" cy="46" r="30" fill="{th["blue"]}"/><path d="M{w - 60},{46} l24,-10 l-8,24 l-4,-10 z" fill="#fff"/>')
    return wrap(card(th, x, y, w, 92, inner, dark=th["name"] == "dark", r=46), t, t0)


# ------------------------------------------------------------------ camera + frame + render
def camera(t, keys):
    """keys = [(t, zoom, cx, cy)] eased → transform string (slow push-ins / pans between scenes)"""
    z, cx, cy = keys[0][1:]
    for (a, z0, x0, y0), (b, z1, x1, y1) in zip(keys, keys[1:]):
        if a <= t <= b: k = ease((t - a) / (b - a)); z, cx, cy = z0 + (z1 - z0) * k, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k; break
        if t > b: z, cx, cy = z1, x1, y1
    return f'translate(540,960) scale({z:.4f}) translate({-cx:.1f},{-cy:.1f})'


def frame(th, t, layers, cam=None, overlay=""):
    """cam = camera() transform for the world layers; overlay is drawn on top without camera (captions, labels)"""
    world = "".join(layers)
    if cam: world = f'<g transform="{cam}">{world}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{world}{overlay}</svg>'


def _one(args):
    fn, i, fps, out = args
    import cairosvg
    p = os.path.join(out, f"{i:05d}.png")
    cairosvg.svg2png(bytestring=fn(i / fps).encode(), write_to=p)
    return p


def render(fn, seconds, out, fps=30, procs=None):
    os.makedirs(out, exist_ok=True); n = int(seconds * fps)
    with Pool(procs or os.cpu_count()) as p: p.map(_one, [(fn, i, fps, out) for i in range(n)], chunksize=6)
    return n
