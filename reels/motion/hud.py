"""HUD-ЛАЙМ — стиль 10: «моушн-дизайн кодом» (эталон @khavinkonstantin, reel DeemgE_FdTv, 1034 коммента).

Look: почти чёрный фон, HUD-рамка (уголки, моно-метки «КАДР n / N», «1080 × 1920 · 60 fps», таймкод), кольцо обратного
отсчёта справа сверху, жирный широкий шрифт Unbounded КАПСОМ, слова падают по одному под голос, ключевые слова —
в лаймовой плашке со скобками-уголками и микро-тегом, лаймовые перечёркивания, чипы, «партитура» с ромбами-ключами,
волна голоса, чек-лист ✕/✓, иконки в скобках по бокам, прицелы, лёгкая тряска камеры на ударных словах. 60 fps.

    import sys; sys.path.insert(0, "reels/motion"); import mokit as M, hud as H
    svg = H.frame(t, TOTAL, [H.bg(t), H.words(t, t0, "Я ПРОСТО *НАПИСАЛ*[ТЕКСТ] ЕМУ:", y=760), H.chip(...)], shake=H.shake(t, hits))
    M.render(lambda t: svg_of(t), TOTAL, out, fps=60)
Плашка на несколько слов: *ПО_ВРЕМЕНИ* (подчёркивание = пробел). Звуки: reels/motion/sfx.py.
Слова под голос: H.timed_words(line_text, start, dur) раздаёт словам время пропорционально длине.
"""
import math, os, random, shutil, subprocess
from html import escape
import mokit as M

HERE = os.path.dirname(os.path.abspath(__file__)); FONT_FILE = os.path.join(HERE, "fonts", "Unbounded.ttf")
_fdir = os.path.expanduser("~/.fonts")
if not os.path.exists(os.path.join(_fdir, "Unbounded.ttf")):           # make cairosvg/fontconfig see the font in fresh containers
    os.makedirs(_fdir, exist_ok=True); shutil.copy(FONT_FILE, _fdir); subprocess.run(["fc-cache", "-f"], capture_output=True)

LIME = "#D4FF2A"; INK = "#F3F3EE"; DIM = "#6E6F68"; BG = "#070707"; GRID = "#151515"; LINE = "#2A2B27"
DISP = "Unbounded"; MONO = M.MONO
_pf = {}


def tw(text, size, weight="Black"):
    from PIL import ImageFont
    k = (size, weight)
    if k not in _pf: f = ImageFont.truetype(FONT_FILE, size); f.set_variation_by_name(weight); _pf[k] = f
    return _pf[k].getlength(text)


def ease(x): return M.ease(x)
def clamp(x, a=0.0, b=1.0): return M.clamp(x, a, b)


# ---------------------------------------------------------------- background + HUD frame
def bg(t, seed=7):
    r = random.Random(seed); out = [f'<rect width="1080" height="1920" fill="{BG}"/>']
    for x in range(0, 1081, 90): out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="1920" stroke="{GRID}" stroke-width="1"/>')
    for y in range(0, 1921, 90): out.append(f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="{GRID}" stroke-width="1"/>')
    for k in range(26):    # drifting specks
        x = (r.uniform(0, 1080) + t * r.uniform(-6, 6)) % 1080; y = (r.uniform(0, 1920) - t * r.uniform(2, 10)) % 1920
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r.uniform(1, 2.4):.1f}" fill="{LIME if k % 7 == 0 else "#3A3B36"}" opacity="{0.4 + 0.4 * math.sin(t * 2 + k):.2f}"/>')
    return "".join(out)


def crosshair(x, y, t, s=14):
    a = 45 + t * 40
    return (f'<g transform="translate({x},{y}) rotate({a:.1f})" stroke="{INK}" stroke-width="2" opacity="0.7">'
            f'<line x1="{-s}" y1="0" x2="{s}" y2="0"/><line x1="0" y1="{-s}" x2="0" y2="{s}"/></g>'
            f'<circle cx="{x}" cy="{y}" r="3" fill="{LIME}"/>')


def corners(x, y, w, h, l=26, col=LIME, sw=4, op=1.0):
    p = [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]
    return "".join(f'<path d="M{cx + dx * l},{cy} L{cx},{cy} L{cx},{cy + dy * l}" fill="none" stroke="{col}" stroke-width="{sw}" opacity="{op}"/>' for cx, cy, dx, dy in p)


def ring_timer(t, total, cx=965, cy=330, r=52):
    left = max(0.0, total - t); frac = left / total; circ = 2 * math.pi * r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0E0E0D" stroke="{LINE}" stroke-width="6"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LIME}" stroke-width="6" stroke-linecap="round" '
            f'stroke-dasharray="{circ * frac:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>'
            f'<text x="{cx}" y="{cy + 2}" text-anchor="middle" dominant-baseline="middle" font-family="{MONO}" font-size="26" font-weight="bold" fill="{INK}">00:{int(math.ceil(left)):02d}</text>')


def frame_hud(t, total, fps=60, scene="", band=(250, 1660)):
    """corner brackets of the content band, top/bottom mono telemetry, progress bar, timer"""
    y0, y1 = band; n = int(t * fps); N = int(total * fps)
    tc = f"{int(t // 60):02d}:{int(t % 60):02d}:{int((t % 1) * fps):02d}"
    out = [corners(28, y0, 1024, y1 - y0, 34, "#3C3D38", 3)]
    out.append(f'<text x="60" y="{y0 + 40}" font-family="{MONO}" font-size="19" fill="{DIM}">● REC {tc}</text>')
    out.append(f'<text x="540" y="{y0 + 40}" text-anchor="middle" font-family="{MONO}" font-size="19" fill="{DIM}">КАМ 1 · {scene}</text>')
    out.append(f'<text x="1020" y="{y0 + 40}" text-anchor="end" font-family="{MONO}" font-size="19" fill="{DIM}">КАДР {n} / {N}</text>')
    out.append(f'<text x="60" y="{y1 - 24}" font-family="{MONO}" font-size="19" fill="{DIM}">{scene.lower()}</text>')
    out.append(f'<text x="1020" y="{y1 - 24}" text-anchor="end" font-family="{MONO}" font-size="19" fill="{DIM}">1080 × 1920 · {fps} fps</text>')
    out.append(f'<rect x="60" y="{y1 - 60}" width="960" height="3" fill="{LINE}"/><rect x="60" y="{y1 - 60}" width="{960 * t / total:.1f}" height="3" fill="{LIME}"/>')
    out.append(ring_timer(t, total, cy=y0 + 120))
    return "".join(out)


# ---------------------------------------------------------------- kinetic typography
def timed_words(text, start, dur):
    """[(word, t0)] — words spread over the spoken line proportional to their length"""
    ws = text.split(); tot = sum(len(w.replace("*", "")) + 2 for w in ws); t = start; out = []
    for w in ws:
        out.append((w, t)); t += dur * (len(w.replace("*", "")) + 2) / tot
    return out


def _parse(w):
    """*СЛОВО*[ТЕГ]  → (word, accent, tag)"""
    tag = None
    if "[" in w and w.endswith("]"): w, tag = w[:-1].split("[", 1)
    acc = "*" in w; return w.replace("*", "").replace("_", " "), acc, tag


def words(t, items, y=760, size=64, maxw=900, t_out=None, gray_before=None):
    """items = timed_words(...) or [(word, t0)]; each word drops in (scale 1.35→1, from above), accents get the lime box"""
    if t_out is not None and t > t_out + 0.35: return ""
    parsed = [(*_parse(w), t0) for w, t0 in items]; lines, cur, cw = [], [], 0
    for p in parsed:
        ww = tw(p[0], size) + (36 if p[1] else 0)
        if cur and cw + ww > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((p, ww)); cw += ww + size * 0.32
    lines.append(cur); out = []
    fade = 1 - ease((t - t_out) / 0.3) if t_out is not None else 1
    for li, ln in enumerate(lines):
        lw = sum(ww for _, ww in ln) + size * 0.32 * (len(ln) - 1); x = 540 - lw / 2
        yy = y + (li - (len(lines) - 1) / 2) * size * 1.45
        for (word, acc, tag, t0), ww in ln:
            k = clamp((t - t0) / 0.18)
            if k <= 0: x += ww + size * 0.32; continue
            s = 1.35 - 0.35 * ease(k); dy = -(1 - ease(k)) * 30; cx = x + ww / 2
            g = ""
            if acc:
                bw = ww; bh = size * 1.18; bx = x; by = yy - bh / 2 - 4
                wipe = ease(clamp((t - t0 - 0.05) / 0.2))
                g += (f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw * wipe:.1f}" height="{bh:.1f}" fill="{LIME}"/>'
                      + corners(bx - 12, by - 10, bw + 24, bh + 20, 18, LIME, 3, wipe))
                if tag: g += f'<text x="{bx + bw + 14:.1f}" y="{by - 14:.1f}" font-family="{MONO}" font-size="16" font-weight="bold" fill="{LIME}">{escape(tag)}</text>'
                g += f'<text x="{cx:.1f}" y="{yy:.1f}" text-anchor="middle" dominant-baseline="middle" font-family="{DISP}" font-weight="900" font-size="{size}" fill="#0A0A0A">{escape(word)}</text>'
            else:
                col = INK if not (gray_before and t0 < gray_before) else DIM
                g += f'<text x="{cx:.1f}" y="{yy:.1f}" text-anchor="middle" dominant-baseline="middle" font-family="{DISP}" font-weight="900" font-size="{size}" fill="{col}">{escape(word)}</text>'
            out.append(f'<g opacity="{k * fade:.2f}" transform="translate({cx:.1f},{yy + dy:.1f}) scale({s:.3f}) translate({-cx:.1f},{-yy:.1f})">{g}</g>')
            x += ww + size * 0.32
    return "".join(out)


def strike(t, t0, x, y, text, size=60, tag=None):
    """gray word on a dark card that gets crossed out by a lime line (SORA / SEEDANCE / AFTER EFFECTS)"""
    a = M.appear(t, t0, 0.25)
    if a <= 0: return ""
    w = tw(text, size) + 60; k = ease((t - t0 - 0.45) / 0.3)
    return (f'<g opacity="{a:.2f}"><rect x="{x - w / 2:.0f}" y="{y - size}" width="{w:.0f}" height="{size * 2}" rx="10" fill="#141413" stroke="{LINE}" stroke-width="2"/>'
            + (f'<text x="{x - w / 2:.0f}" y="{y - size - 10}" font-family="{MONO}" font-size="17" fill="{DIM}">{escape(tag)}</text>' if tag else "")
            + f'<text x="{x}" y="{y + 4}" text-anchor="middle" dominant-baseline="middle" font-family="{DISP}" font-weight="900" font-size="{size}" fill="#4A4B46">{escape(text)}</text>'
            f'<line x1="{x - w / 2 - 20:.0f}" y1="{y + 14}" x2="{x - w / 2 - 20 + (w + 40) * k:.0f}" y2="{y - 10}" stroke="{LIME}" stroke-width="7" stroke-linecap="round"/></g>')


def chip(t, t0, x, y, text, num=None, rot=-3, size=30):
    """lime pill that pops in with a spring (+ tiny «#01» label)"""
    k = M.back((t - t0) / 0.4, 2.0)
    if t < t0: return ""
    w = tw(text, size, "Bold") + 48; h = size * 1.9
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({max(0, k):.3f})">'
            + (f'<text x="{-w / 2:.0f}" y="{-h / 2 - 10:.0f}" font-family="{MONO}" font-size="17" fill="{DIM}">#{num:02d}</text>' if num else "")
            + f'<rect x="{-w / 2:.0f}" y="{-h / 2:.0f}" width="{w:.0f}" height="{h:.0f}" rx="12" fill="{LIME}"/>'
            f'<rect x="{-w / 2:.0f}" y="{h / 2 - 6:.0f}" width="{w:.0f}" height="8" rx="4" fill="#8FAE12"/>'
            f'<text x="0" y="2" text-anchor="middle" dominant-baseline="middle" font-family="{DISP}" font-weight="700" font-size="{size}" fill="#0A0A0A">{escape(text)}</text></g>')


def side_icon(x, y, glyph, label, t=0, t0=0):
    a = M.appear(t, t0, 0.3)
    if a <= 0: return ""
    return (f'<g opacity="{a:.2f}">' + corners(x - 34, y - 34, 68, 68, 14, LIME, 3)
            + f'<text x="{x}" y="{y + 2}" text-anchor="middle" dominant-baseline="middle" font-family="{MONO}" font-size="28" font-weight="bold" fill="{INK}">{escape(glyph)}</text>'
            f'<text x="{x}" y="{y + 60}" text-anchor="middle" font-family="{MONO}" font-size="16" fill="{DIM}">{escape(label)}</text></g>')


def score(t, t0, x=110, y=1000, w=860, rows=("буква", "форма", "камера", "поворот", "свет"), seed=4, label="ПАРТИТУРА"):
    """timeline 'partitura': rows with diamond keyframes popping in, running playhead"""
    r = random.Random(seed); out = [f'<text x="{x}" y="{y + len(rows) * 62 + 70}" font-family="{MONO}" font-size="18" fill="{DIM}">■ {label}</text>']
    for i, nm in enumerate(rows):
        yy = y + i * 62
        out.append(f'<text x="{x}" y="{yy + 6}" font-family="{MONO}" font-size="20" fill="{DIM}">{nm}</text>'
                   f'<line x1="{x + 130}" y1="{yy}" x2="{x + w}" y2="{yy}" stroke="{LINE}" stroke-width="2"/>')
        for k in range(r.randint(3, 6)):
            kx = x + 150 + r.uniform(0, w - 170); kt = t0 + (kx - x) / w * 1.4
            if t < kt: continue
            s = M.back((t - kt) / 0.3) * 13; filled = r.random() < 0.7
            out.append(f'<rect x="{kx - s:.1f}" y="{yy - s:.1f}" width="{2 * s:.1f}" height="{2 * s:.1f}" transform="rotate(45 {kx:.1f} {yy})" '
                       f'fill="{LIME if filled else "none"}" stroke="{LIME}" stroke-width="3"/>')
    ph = x + 130 + (w - 130) * clamp((t - t0) / 2.2)
    out.append(f'<line x1="{ph:.1f}" y1="{y - 30}" x2="{ph:.1f}" y2="{y + (len(rows) - 1) * 62 + 30}" stroke="{LIME}" stroke-width="3"/>')
    return "".join(out)


def wave(t, t0, x=110, y=1100, w=860, h=150, active=True, seed=2):
    """voice waveform bars (live while `active`)"""
    r = random.Random(seed); n = 64; bw = w / n; out = [f'<rect x="{x - 20}" y="{y - h / 2 - 40}" width="{w + 40}" height="{h + 80}" rx="14" fill="#101010" stroke="{LINE}" stroke-width="2"/>'
                                                          f'<text x="{x}" y="{y - h / 2 - 12}" font-family="{MONO}" font-size="17" fill="{DIM}">● REC · ГОЛОС</text>']
    k = clamp((t - t0) / 0.6)
    for i in range(int(n * k)):
        amp = (0.25 + 0.75 * abs(math.sin(i * 0.7 + r.random() * 3))) * (0.6 + 0.4 * math.sin(t * 9 + i) if active else 0.3)
        bh = h * amp * math.exp(-((i - n / 2) / (n / 2.2)) ** 2 * 0.8)
        out.append(f'<rect x="{x + i * bw:.1f}" y="{y - bh / 2:.1f}" width="{bw * 0.55:.1f}" height="{bh:.1f}" rx="2" fill="{LIME}"/>')
    return "".join(out)


def checklist(t, t0, items, x=200, y=1000, size=46):
    """[(text, ok)] — ✕ items fade to gray, ✓ items light up (lime box)"""
    out = []
    for i, (txt, ok) in enumerate(items):
        ti = t0 + i * 0.35; a = M.appear(t, ti, 0.25)
        if a <= 0: continue
        yy = y + i * size * 1.5; done = t > ti + 0.4
        col = INK if ok or not done else "#55564F"
        out.append(f'<g opacity="{a:.2f}"><text x="{x - 60}" y="{yy}" font-family="{MONO}" font-size="18" fill="{DIM}">{i + 1:02d}</text>'
                   f'<text x="{x}" y="{yy}" dominant-baseline="middle" font-family="{DISP}" font-weight="900" font-size="{size}" fill="{col}">{escape(txt)}</text>')
        bx = x + 640
        if done and ok:
            out.append(f'<rect x="{bx}" y="{yy - 24}" width="48" height="48" rx="8" fill="{LIME}"/><path d="M{bx + 11},{yy} l10,10 l17,-20" fill="none" stroke="#0A0A0A" stroke-width="6" stroke-linecap="round"/>')
        elif done:
            out.append(f'<rect x="{bx}" y="{yy - 24}" width="48" height="48" rx="8" fill="none" stroke="#55564F" stroke-width="3"/><path d="M{bx + 14},{yy - 10} l20,20 M{bx + 34},{yy - 10} l-20,20" stroke="#8A8B85" stroke-width="5"/>')
        out.append("</g>")
    return "".join(out)


def panel(t, t0, x, y, w, h, title="", body=""):
    """dark UI panel (chat / editor / render progress) with mono title"""
    a = M.appear(t, t0, 0.3)
    if a <= 0: return ""
    return (f'<g opacity="{a:.2f}" transform="translate(0,{(1 - a) * 24:.1f})"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#111110" stroke="{LINE}" stroke-width="2"/>'
            f'<text x="{x + 22}" y="{y + 34}" font-family="{MONO}" font-size="18" fill="{DIM}">■ {escape(title)}</text><g transform="translate({x},{y + 50})">{body}</g></g>')


def bubble(t, t0, x, y, text, w=440, size=26, me=True):
    a = M.appear(t, t0, 0.25)
    if a <= 0: return ""
    lines, cur = [], ""
    for wd in text.split():
        if cur and M.tw(cur + " " + wd, size, 600) > w - 40: lines.append(cur); cur = wd
        else: cur = (cur + " " + wd).strip()
    lines.append(cur); h = len(lines) * size * 1.35 + 28
    fill, col = (LIME, "#0A0A0A") if me else ("#1C1C1A", INK)
    return (f'<g opacity="{a:.2f}"><rect x="{x}" y="{y}" width="{w}" height="{h:.0f}" rx="16" fill="{fill}"/>'
            + "".join(f'<text x="{x + 20}" y="{y + 20 + (i + 0.8) * size * 1.35 - 6:.0f}" font-family="Inter" font-weight="600" font-size="{size}" fill="{col}">{escape(l)}</text>' for i, l in enumerate(lines)) + "</g>")


def typed(t, t0, text, cps=28):
    return text[:int(clamp((t - t0) * cps, 0, len(text)))]


def shake(t, hits, amp=7):
    """tiny camera shake right after stressed words: hits = [t, ...]"""
    dx = dy = 0.0
    for h in hits:
        k = t - h
        if 0 <= k < 0.25: e = math.exp(-k * 18) * amp; dx += e * math.sin(k * 90); dy += e * math.cos(k * 70)
    return dx, dy


def frame(t, total, layers, scene="", shake_xy=(0, 0), fps=60, zoom=1.0):
    dx, dy = shake_xy
    world = f'<g transform="translate({dx:.1f},{dy:.1f}) translate(540,960) scale({zoom:.4f}) translate(-540,-960)">{"".join(layers)}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920">{bg(t)}{world}{frame_hud(t, total, fps, scene)}</svg>'
