"""Кабаново, серия 2 (12 новых домов): Blender frames (540×960) → 1080×1920 + overlays (captions on dark plates, comment cards, titles).
python3 kabanovo/compose.py <blender_frames_dir> <out_frames_dir>"""
import json, math, os, sys
from multiprocessing import Pool
from html import escape
from PIL import Image
sys.path.insert(0, "/home/user/Claude/reels/motion"); import mokit as M

TM = json.load(open("/home/user/Claude/kabanovo/ep2/build/timing.json")); L = TM["lines"]; TOTAL = TM["total"]
LINES = json.load(open("/home/user/Claude/kabanovo/ep2/lines.json"))
INK = "#FFFFFF"; PLATE = "#1D1712"


def phrases():
    """split each line at punctuation into phrases, time ∝ characters"""
    out = []
    for (s, d), txt in zip(L, LINES):
        parts, cur = [], ""
        for w in txt.split():
            cur = (cur + " " + w).strip()
            if w[-1] in ".,!?" and len(cur) > 14: parts.append(cur); cur = ""
        if cur: parts.append(cur)
        tot = sum(len(p) for p in parts); t = s
        for p in parts:
            dd = d * len(p) / tot; out.append((t - 0.1, t + dd + 0.25, p)); t += dd
    for i in range(len(out) - 1): out[i] = (out[i][0], min(out[i][1], out[i + 1][0]), out[i][2])
    return out


PH = phrases()


def plate_text(t, t0, t1, text, y=1590, size=44):
    a = M.appear(t, t0, 0.22) * M.gone(t, t1 - 0.2, 0.2)
    if a <= 0.01: return ""
    words = text.split(); lines, cur = [], ""
    for w in words:
        if cur and M.tw(cur + " " + w, size, 600) > 760: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    lines.append(cur); wmax = max(M.tw(l, size, 600) for l in lines) + 70; h = len(lines) * size * 1.3 + 44
    dy = (1 - M.appear(t, t0, 0.3)) * 16
    g = f'<rect x="{540 - wmax / 2:.0f}" y="{y - h / 2:.0f}" width="{wmax:.0f}" height="{h:.0f}" rx="22" fill="{PLATE}" opacity="0.86"/>'
    for i, l in enumerate(lines):
        g += (f'<text x="540" y="{y + (i - (len(lines) - 1) / 2) * size * 1.3:.0f}" text-anchor="middle" dominant-baseline="middle" '
              f'font-family="Inter" font-weight="600" font-size="{size}" fill="{INK}">{escape(l)}</text>')
    return f'<g opacity="{a:.2f}" transform="translate(0,{dy:.1f})">{g}</g>'


def comment_card(t, t0, t1, nick, text, hearts=0, h_from=None):
    a = M.appear(t, t0, 0.3) * M.gone(t, t1, 0.25)
    if a <= 0.01: return ""
    s = 0.85 + 0.15 * M.back((t - t0) / 0.45)
    n = int(hearts * M.ease((t - (h_from or t0)) / 2.2)) if hearts else 0
    liked = n > 0
    g = (M.shadow(150, 300, 780, 130, 30) + f'<rect x="150" y="300" width="780" height="130" rx="30" fill="#FFFFFF"/>'
         f'<circle cx="222" cy="365" r="36" fill="#C7652F"/><text x="222" y="367" text-anchor="middle" dominant-baseline="middle" font-family="Inter" font-size="34" font-weight="800" fill="#fff">{escape(nick[0].upper())}</text>'
         f'<text x="280" y="345" font-family="Inter" font-size="30" font-weight="700" fill="#16181D">{escape(nick)}</text>'
         f'<text x="280" y="392" font-family="Inter" font-size="30" fill="#3A3D44">{escape(text)}</text>'
         f'<path d="M868,352 c-10,-16 -34,-10 -30,8 c3,12 30,30 30,30 c0,0 27,-18 30,-30 c4,-18 -20,-24 -30,-8z" fill="{"#F2385A" if liked else "none"}" stroke="{"#F2385A" if liked else "#8A8F99"}" stroke-width="4"/>'
         + (f'<text x="868" y="420" text-anchor="middle" font-family="Inter" font-size="24" font-weight="700" fill="#8A8F99">{n}</text>' if hearts else ""))
    return f'<g opacity="{a:.2f}" transform="translate(540,365) scale({s:.3f}) translate(-540,-365)">{g}</g>'


def tplate(y, text, size, weight=800, op=0.86):
    w = M.tw(text, size, weight) + 64; h = size * 1.45
    return (f'<rect x="{540 - w / 2:.0f}" y="{y - h / 2:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{h * 0.3:.0f}" fill="{PLATE}" opacity="{op}"/>'
            f'<text x="540" y="{y:.0f}" text-anchor="middle" dominant-baseline="middle" font-family="Inter" font-size="{size}" font-weight="{weight}" fill="#FFFFFF">{escape(text)}</text>')


NICKS = ["grisha_pills", "enchantleses", "svinieushi", "ayunalexx", "dr.twikibot", "why253777",
         "d_mar1k", "scarmaks.s", "1knnv.1", "tholeenwakeup", "serloopsky", "anton_life_ai"]


def title(t):
    out = ""
    a = M.gone(t, L[1][0] - 0.5, 0.4)          # hook, visible from frame 0
    if a > 0.01:
        n = min(12, int(max(0, t - 0.7) / 0.22) + (1 if t > 0.7 else 0))
        out += f'<g opacity="{a:.2f}">' + tplate(250, "КАБАНОВО · ДЕНЬ 2", 78, 900) + tplate(372, "+12 ДОМОВ", 64, 900) + "</g>"
    t5 = L[5][0]; b = M.appear(t, t5 + 0.1, 0.5)
    if b > 0.01:
        rows = "".join(f'<text x="{300 if i % 2 == 0 else 780}" y="{330 + (i // 2) * 52}" text-anchor="middle" font-family="Inter" font-size="34" font-weight="700" fill="#FFFFFF">@{n}</text>'
                       for i, n in enumerate(NICKS))
        out += (f'<g opacity="{b:.2f}">' + tplate(200, "Жители Кабаново", 60, 900)
                + f'<rect x="80" y="280" width="920" height="{52 * 6 + 30}" rx="28" fill="{PLATE}" opacity="0.86"/>' + rows + "</g>")
        out += M.keyword_bar(M.LIGHT, 180, 680, "КАБАНОВО", t, t5 + 1.2)
    return out


def overlay(t):
    parts = [title(t)]
    parts += [plate_text(t, a, b, p) for a, b, p in PH if a - 0.05 <= t <= b + 0.3]
    parts.append(comment_card(t, L[1][0] + 0.2, L[2][0] - 0.1, "grisha_pills", "КАБАНОВО хочу быть в домике!!!"))
    parts.append(comment_card(t, L[2][0], L[3][0] - 0.1, "anton_life_ai", "Кабаново)"))
    parts.append(comment_card(t, L[4][0] + 0.4, L[5][0] - 0.1, "твой_ник", "Хочу …? (пиши желание)", hearts=0))
    parts.append('<text x="540" y="1840" text-anchor="middle" font-family="Inter" font-size="28" font-weight="700" fill="#FFFFFF" opacity="0.45">@deykun1337</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920">{"".join(parts)}</svg>'


def one(args):
    import cairosvg, io
    i, src, dst = args; t = i / 30
    base = Image.open(f"{src}/{i:05d}.png").convert("RGBA").resize((1080, 1920), Image.LANCZOS)
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=overlay(t).encode()))).convert("RGBA")
    Image.alpha_composite(base, ov).convert("RGB").save(f"{dst}/{i:05d}.png")


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
    if len(sys.argv) > 3:     # test frames
        for x in sys.argv[3:]: one((int(x), src, dst))
    else:
        n = len([f for f in os.listdir(src) if f.endswith(".png")])
        with Pool(4) as p: p.map(one, [(i, src, dst) for i in range(n)], chunksize=8)
        print(n)
