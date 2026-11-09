"""Chat-bubble overlays + encode for the dialog sketch «Друг занял 5000».
Usage: python3 compose_dolg.py <project> <frames_dir> <plan.json> <out.mp4> [frames...]"""
import io, json, math, os, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image

proj, FR, PLANF, OUT = (os.path.abspath(a) for a in sys.argv[1:5])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from base import tw, fit, stext, clamp, prog, e_out, e_back, popscale, FONT

PLAN = json.load(open(PLANF)); FPS = PLAN["fps"]; S, E, DUR = PLAN["S"], PLAN["E"], PLAN["dur"]
PINK, ORANGE, INK, GREEN = "#F0569A", "#D97757", "#14161C", "#3DDC84"
DEFS = '<defs><filter id="sh" x="-20%" y="-40%" width="140%" height="180%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity="0.4"/></filter></defs>'
KEY = {"долг", "наезд", "наезда", "пять", "тысяч", "десять", "коллектор", "вежливый", "привет"}


def wrap(txt, size, maxw):
    lines, cur = [], ""
    for w in txt.split():
        nxt = (cur + " " + w).strip()
        if tw(nxt, size) > maxw and cur: lines.append(cur); cur = w
        else: cur = nxt
    return lines + ([cur] if cur else [])


def bubble(y, txt, mine, t0, t, typed=True, struck=0.0):
    """Messenger bubble; mine = right/pink, other = left/grey. Text types in."""
    if t < t0: return ""
    sc = popscale(t, t0, 0.3)
    n = len(txt) if not typed else int(len(txt) * prog(t, t0 + 0.1, t0 + 0.1 + len(txt) * 0.028))
    size = 38; lines = wrap(txt, size, 600); shown = []
    left = n
    for ln in lines:
        shown.append(ln[:max(0, left)]); left -= len(ln) + 1
    w = max(tw(l, size) for l in lines) + 60; h = len(lines) * size * 1.3 + 40
    x = 1000 - w if mine else 80
    col = PINK if mine else "#2A2D3A"
    body = "".join(stext(x + 30, y + 20 + size * 0.65 + k * size * 1.3, l, size, fill="#FFFFFF", sw=0, shadow=False, anchor="start") for k, l in enumerate(shown))
    strike = ""
    if struck > 0:
        strike = f'<line x1="{x + 20}" y1="{y + h / 2}" x2="{x + 20 + (w - 40) * struck:.0f}" y2="{y + h / 2}" stroke="#FF3B3B" stroke-width="10" stroke-linecap="round"/>'
    ox, oy = (x + w, y) if mine else (x, y)
    return (f'<g filter="url(#sh)" transform="translate({ox},{oy}) scale({sc:.3f}) translate({-ox},{-oy})">'
            f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{h:.0f}" rx="34" fill="{col}"/>{body}{strike}'
            + (stext(x + w - 30, y + h + 22, "✓✓", 26, fill="#9AD7FF", sw=0, shadow=False, anchor="end") if mine and n >= len(txt) else "") + "</g>")


def chip(cx, cy, txt, size, sc=1.0, bg="#FFFFFF", fg=INK, rot=0):
    if sc <= 0.001: return ""
    w = tw(txt, size) + size * 1.1; h = size * 1.6
    return (f'<g filter="url(#sh)" transform="translate({cx:.1f},{cy:.1f}) rotate({rot}) scale({sc:.3f})">'
            f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h * 0.28:.1f}" fill="{bg}"/>'
            + stext(0, 0, txt, size, fill=fg, sw=0, shadow=False) + "</g>")


def chat_header(t, t0):
    sc = popscale(t, t0, 0.3)
    return (f'<g filter="url(#sh)" transform="translate(540,250) scale({sc:.3f}) translate(-540,-250)"><rect x="60" y="200" width="960" height="100" rx="30" fill="#14161C" fill-opacity="0.85"/>'
            f'<circle cx="125" cy="250" r="32" fill="#5A9BFF"/>' + stext(125, 250, "В", 34, fill="#FFFFFF", sw=0, shadow=False)
            + stext(180, 236, "Друг Вова · долг 5 000 ₽", 34, fill="#FFFFFF", sw=0, shadow=False, anchor="start")
            + stext(180, 272, "был(а) полгода назад", 24, fill="#9AA3B2", sw=0, shadow=False, anchor="start") + "</g>")


def overlays(F):
    t = F["t"]; i = F["line"]; o = []
    if t < S[1] - 0.2:
        o.append(chip(540, 560, "−5 000 ₽", 70, popscale(t, 1.6), bg="#FF3B3B", fg="#FFFFFF", rot=-4))
        o.append(chip(540, 690, "полгода тишины", 40, popscale(t, 2.4), rot=3))
    if S[1] - 0.2 <= t < S[6] - 0.1:
        o.append(chat_header(t, S[1] - 0.2))
        y = 340
        if t < S[3] - 0.1:
            o.append(bubble(y, "Привет! Вспомнил тебя сегодня, когда открыл пустой кошелёк", True, S[1] + 0.6, t, struck=prog(t, S[2] + 0.05, S[2] + 0.35)))
            if t >= S[2]: o.append(chip(540, 720, "НАЕЗД", 64, popscale(t, S[2]), bg="#FF3B3B", fg="#FFFFFF", rot=-6))
        else:
            o.append(bubble(y, "Брат, как сам? Мои 5 000 ₽ передают тебе привет", True, S[3] + 0.6, t))
            if t >= S[4] + 0.7: o.append(bubble(y + 190, "Брат, а можешь занять ещё 5?", False, S[4] + 0.75, t, typed=False))
            if t >= S[5] + 0.5: o.append(bubble(y + 330, "Конечно! Как только вернёшь первые 5 — сразу дам вторые", True, S[5] + 0.6, t))
    if S[6] - 0.1 <= t < S[8] - 0.1:
        sc = popscale(t, S[6] + 0.55, 0.3)
        o.append(f'<g filter="url(#sh)" transform="translate(540,300) scale({sc:.3f}) translate(-540,-300)"><rect x="90" y="230" width="900" height="140" rx="34" fill="#FFFFFF"/>'
                 f'<rect x="120" y="260" width="80" height="80" rx="20" fill="{GREEN}"/>' + stext(160, 300, "₽", 50, fill="#FFFFFF", sw=0, shadow=False)
                 + stext(230, 280, "Поступление от Вовы", 32, fill="#5A6070", sw=0, shadow=False, anchor="start")
                 + stext(230, 328, "+10 000 ₽", 50, fill=INK, sw=0, shadow=False, anchor="start") + "</g>")
        if t >= S[7]:
            o.append(chip(330, 560, "5 000 — долг", 44, popscale(t, S[7] + 0.1), bg=INK, fg="#FFFFFF", rot=-4))
            o.append(chip(720, 680, "5 000 — за тишину", 44, popscale(t, S[7] + 1.0), bg=ORANGE, fg="#FFFFFF", rot=3))
    if i == 8:
        o.append(chip(540, 560, "КОЛЛЕКТОР?", 70, popscale(t, S[8] + 0.2), bg="#FFE27A", fg=INK, rot=-3))
    if t >= S[9] + 1.0:
        sc = popscale(t, S[9] + 1.0, 0.35)
        o.append(f'<g filter="url(#sh)" transform="translate(540,470) scale({sc:.3f}) translate(-540,-470)"><rect x="140" y="340" width="800" height="260" rx="40" fill="{PINK}"/>'
                 + stext(540, 410, "Напиши в комментариях", 40, fill="#FFFFFF", sw=0, shadow=False)
                 + stext(540, 505, "ДОЛГ", 130, fill="#FFFFFF", stroke=INK, sw=10, shadow=False)
                 + stext(540, 572, "пришлю промпты для сложных сообщений", 30, fill="#FFE6F2", sw=0, shadow=False) + "</g>")
    return "".join(o)


def captions(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            words = [w["disp"] for w in c]; size = 66; gap = size * 0.3
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 940: size = int(size * 940 / total); gap = size * 0.3; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            x = 540 - total / 2; out = []; sc = 0.85 + 0.15 * e_back(prog(t, t0, t0 + 0.15))
            for w, wd in zip(words, c):
                k = re.sub(r"[^\w-]", "", w).lower()
                cur = wd["t0"] - 0.05 <= t
                out.append(stext(x, 1540, w, size, fill=("#FFE27A" if k in KEY else "#FFFFFF"), stroke="#000000", sw=10, anchor="start", op=1.0 if cur else 0.5))
                x += tw(w, size) + gap
            return f'<g transform="translate(540,1540) scale({sc:.3f}) translate(-540,-1540)">' + "".join(out) + "</g>"
    return ""


def one(f):
    F = PLAN["frames"][f]; src = os.path.join(FR, f"{f:05d}.png")
    if not os.path.exists(src): return f, False
    bg = Image.open(src).convert("RGBA")
    flash = ""
    if F["bt"] < 0.08 and f > 0: flash = f'<rect width="1080" height="1920" fill="#FFFFFF" opacity="{0.18 * (1 - F["bt"] / 0.08):.2f}"/>'
    if S[2] <= F["t"] < S[2] + 0.25: flash += f'<rect width="1080" height="1920" fill="#FF2040" opacity="{0.25 * (1 - (F["t"] - S[2]) / 0.25):.2f}"/>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}'
           f'{flash}{overlays(F)}{captions(F["t"])}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    im = Image.alpha_composite(bg, ov)
    if F["t"] > DUR - 0.4: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), min(1, (F["t"] - DUR + 0.4) / 0.4))
    im.convert("RGB").save(os.path.join(CO, f"{f:05d}.png"))
    return f, True


if __name__ == "__main__":
    frames = [int(x) for x in sys.argv[5:]] or range(len(PLAN["frames"]))
    with Pool(os.cpu_count()) as p:
        res = p.map(one, frames, chunksize=8)
    miss = [f for f, ok in res if not ok]
    print("composed", len(res) - len(miss), "missing", len(miss))
    if len(sys.argv) > 5: sys.exit(0)
    if miss: sys.exit(1)
    grade = "eq=contrast=1.05:saturation=1.1,noise=alls=2:allf=t,vignette=PI/5"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", f"scale=1080:1920:flags=lanczos,{grade},format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
