"""Overlays + encode for the trend shorts. Usage: python3 compose_trend.py <project> <frames_dir> <plan.json> <plate.png> <out.mp4> [frames...]"""
import io, json, math, os, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image, ImageFilter

proj, FR, PLANF, PLATE, OUT = (os.path.abspath(a) for a in sys.argv[1:6])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from base import tw, fit, stext, clamp, prog, lerp, e_out, e_back, popscale, FONT
import lib2d

PLAN = json.load(open(PLANF)); FPS = PLAN["fps"]; KIND = PLAN["kind"]; S, E = PLAN["S"], PLAN["E"]; DUR = PLAN["dur"]
plate = Image.open(PLATE).convert("RGBA").filter(ImageFilter.GaussianBlur(9))
YEL, RED, GRN = "#FFC83D", "#FF4040", "#3DDC84"
KEY = {"муся", "мусю", "муся?", "болоте", "полосатый", "воздухан", "клод", "детка", "телефон", "понедельник", "сорок", "седьмой", "восьмого", "три", "перезвоню"}


def phone_icon(x, y, s=1.0, col="#fff"):
    return f'<path transform="translate({x},{y}) scale({s})" d="M -14 -18 q -8 0 -8 10 q 2 26 32 30 q 10 0 10 -8 l -2 -8 l -12 -2 l -4 6 q -12 -4 -16 -16 l 6 -4 l -2 -12 Z" fill="{col}"/>'


def cat_px(x, y, u):
    px = ["..X......X..", ".XXX....XXX.", ".XXXXXXXXXX.", "XXOXXXXXXOXX", "XXXXXPPXXXXX", "XXXXXXXXXXXX", ".XXXXXXXXXX.", "..XXXXXXXX.."]
    col = {"X": "#C98A4A", "O": "#2A2A2A", "P": "#F28AA0"}
    return "".join(f'<rect x="{x + c * u}" y="{y + r * u}" width="{u + 0.5}" height="{u + 0.5}" fill="{col[ch]}"/>' for r, row in enumerate(px) for c, ch in enumerate(row) if ch != ".")


def poster(t):
    p = e_back(prog(t, 0.05, 0.45), 1.3)
    return (f'<g transform="translate(540,{lerp(1900, 1080, p):.0f}) rotate(-4)"><rect x="-300" y="-340" width="600" height="680" fill="#000" opacity="0.4" transform="translate(14,18)"/>'
            '<rect x="-300" y="-340" width="600" height="680" fill="#F7F3E8" stroke="#2A2A2A" stroke-width="5"/>'
            + stext(0, -270, "ПРОПАЛА КОШКА", 54, fill="#E5322D", sw=0, shadow=False) + cat_px(-180, -200, 30)
            + stext(0, 110, "МУСЯ", 96, fill="#1A1A1A", sw=0, shadow=False)
            + stext(0, 190, "3 года, отзывается на «кс-кс»", 30, fill="#4A4A4A", sw=0, shadow=False)
            + stext(0, 270, "тел.: позвоните, пожалуйста", 30, fill="#4A4A4A", sw=0, shadow=False) + "</g>")


def call_ui(t, t0, accepted_at):
    acc = t >= accepted_at
    o = ['<rect width="1080" height="1920" fill="#0B0D11" opacity="0.72"/>']
    if not acc:
        for k in range(3):
            ph = ((t * 1.2 + k / 3) % 1)
            o.append(f'<circle cx="540" cy="700" r="{120 + 260 * ph:.0f}" fill="none" stroke="#3DDC84" stroke-width="6" opacity="{1 - ph:.2f}"/>')
    o.append('<circle cx="540" cy="700" r="120" fill="#2C313B"/>' + stext(540, 700, "?", 120, fill="#9AA3B2", sw=0, shadow=False))
    o.append(stext(540, 920, "Неизвестный номер", 64, fill="#fff", sw=0, shadow=False))
    o.append(stext(540, 1000, "Болото, Россия" if not acc else f"00:{int(t - accepted_at) + 1:02d}", 40, fill="#9AA3B2", sw=0, shadow=False))
    if not acc:
        sh = 6 * math.sin(t * 40)
        o.append(f'<g transform="translate({sh:.1f},0)"><circle cx="330" cy="1300" r="80" fill="#E5322D"/><circle cx="750" cy="1300" r="80" fill="#3DDC84"/></g>'
                 + phone_icon(330, 1300, 2.0) + phone_icon(750, 1300, 2.0))
    return "".join(o)


def timer_pill(t, t0):
    sec = max(1, int(t - t0) + 1)
    return ('<rect x="390" y="190" width="300" height="70" rx="35" fill="#1E7A4A" opacity="0.9"/>' + phone_icon(445, 225, 0.9)
            + stext(570, 225, f"00:{sec:02d}", 38, fill="#fff", sw=0, shadow=False).replace(FONT, "JetBrains Mono ExtraBold"))


def meme_text(t, t0):
    a = clamp((t - t0) * 6)
    return (stext(540, 330, "МУСЯ, ЭТО ТЫ?", fit("МУСЯ, ЭТО ТЫ?", 980, 110), fill="#fff", stroke="#000", sw=16, shadow=False, op=a)
            + stext(540, 1640, "НЕТ, ЭТО НЕ МУСЯ", fit("НЕТ, ЭТО НЕ МУСЯ", 980, 104), fill="#fff", stroke="#000", sw=16, shadow=False, op=clamp((t - t0 - 0.5) * 6)))


def clock(t, t0):
    p = e_back(prog(t, t0, t0 + 0.4))
    return (f'<g transform="translate(540,330) scale({max(p, 0.01):.3f})"><rect x="-250" y="-100" width="500" height="200" rx="30" fill="#0B0D11" opacity="0.88" stroke="#2C313B" stroke-width="4"/>'
            + stext(0, 0, "03:00", 140, fill="#FF5A5A", sw=0, shadow=False).replace(FONT, "JetBrains Mono ExtraBold") + "</g>"
            + (stext(540, 520, "47 пропущенных", 54, fill="#fff", stroke=RED, sw=10, shadow=False) if t > t0 + 0.6 else ""))


def notif(t, t0, n=48):
    p = e_out(prog(t, t0, t0 + 0.3)); sh = 5 * math.sin(t * 50)
    return (f'<g transform="translate({sh:.1f},{(1 - p) * -200:.0f})"><rect x="90" y="150" width="900" height="150" rx="34" fill="#16191F" opacity="0.95" stroke="#2C313B" stroke-width="3"/>'
            '<rect x="120" y="180" width="90" height="90" rx="22" fill="#E5684B"/>' + phone_icon(165, 225, 1.4)
            + stext(240, 205, f"Клод 🐗 ({n})".replace(" 🐗", ""), 44, fill="#fff", sw=0, shadow=False, anchor="start")
            + stext(240, 262, "Входящий вызов…", 32, fill="#9AA3B2", sw=0, shadow=False, anchor="start") + "</g>")


def overlays(F):
    t, tag, i = F["t"], F.get("tag", ""), F["line"]
    o = []
    if KIND == "musya":
        if tag == "poster": o.append(stext(540, 330, "МУСЯ ПРОПАЛА", fit("МУСЯ ПРОПАЛА", 960, 120), fill=YEL, stroke="#1A1A1A", sw=14, rot=-3) + poster(t))
        if tag == "call": o.append(call_ui(t, E[0], S[1] - 0.2))
        if F["shot"] == "r_close" and i >= 2: o.append(timer_pill(t, S[1] - 0.2))
        if tag == "meme": o.append(meme_text(t, S[3]))
        if tag == "voz": o.append(lib2d.stamp(t, S[7] + 1.2, "ВОЗДУХАН"))
        if t > DUR - 1.3: o.append(lib2d.pill(540, 1180, "ОТМЕТЬ ТОГО, КТО ИЩЕТ МУСЮ", 40, YEL, "#1A1A1A", sc=popscale(t, DUR - 1.3)))
    elif KIND == "obidelsya":
        if tag == "hook": o.append(stext(540, 330, "КЛОД ОБИДЕЛСЯ", fit("КЛОД ОБИДЕЛСЯ", 960, 120), fill=YEL, stroke="#1A1A1A", sw=14, rot=-3))
        if tag == "47":
            o.append(lib2d.card(540, 420, 760, 260, stext(-330, -60, "Запросы к другой нейронке", 38, fill="#fff", sw=0, shadow=False, anchor="start")
                                + stext(-330, 40, "47", 110, fill=RED, sw=0, shadow=False, anchor="start").replace(FONT, "JetBrains Mono ExtraBold")))
        if tag == "ignor" and t > S[5] + 0.9:
            p = e_back(prog(t, S[5] + 0.9, S[5] + 1.3))
            o.append(f'<g transform="translate(540,400) scale({max(p, 0.01):.3f})"><rect x="-380" y="-150" width="760" height="300" rx="30" fill="#0E1116" opacity="0.92" stroke="{YEL}" stroke-width="5"/>'
                     + stext(0, -80, "ВАШ ТАРИФ", 36, fill="#C9B07A", sw=0, shadow=False) + stext(0, 0, "ИГНОР", 110, fill=YEL, sw=0, shadow=False)
                     + stext(0, 90, "20 000 ₽ / мес", 40, fill="#fff", sw=0, shadow=False) + "</g>")
        if t > DUR - 1.3: o.append(lib2d.pill(540, 1180, "ОТМЕТЬ ТОГО, КТО ИЗМЕНЯЕТ НЕЙРОНКЕ", 36, YEL, "#1A1A1A", sc=popscale(t, DUR - 1.3)))
    elif KIND == "vmoskve":
        name = {"moscow": "Москва", "piter": "Санкт-Петербург", "village": "д. Кабаново", "home": "Дом"}[F["loc"]]
        sc = popscale(t, F["cut_t"], 0.3)
        w = tw(name, 44) + 110
        o.append(f'<g transform="translate(540,230) scale({sc:.3f})"><rect x="{-w / 2:.0f}" y="-40" width="{w:.0f}" height="80" rx="40" fill="#0E1116" opacity="0.85"/>'
                 f'<path transform="translate({-w / 2 + 50:.0f},0)" d="M 0 22 C -22 -2 -18 -26 0 -26 C 18 -26 22 -2 0 22 Z" fill="{RED}"/><circle cx="{-w / 2 + 50:.0f}" cy="-10" r="7" fill="#fff"/>'
                 + stext(-w / 2 + 80, 0, name, 44, fill="#fff", sw=0, shadow=False, anchor="start") + "</g>")
        if F["line"] == 0: o.append(stext(540, 400, "Я В МОСКВЕ!", fit("Я В МОСКВЕ!", 960, 120), fill=YEL, stroke="#1A1A1A", sw=14, rot=-3, sc=popscale(t, 0.05)))
    else:
        if tag == "clock": o.append(clock(t, S[0]))
        if tag == "buzz": o.append(notif(t, E[1]))
        if tag == "n48": o.append(lib2d.pill(540, 360, "ПОНЕДЕЛЬНИК №48", 64, YEL, "#1A1A1A", sc=popscale(t, S[5] + 0.3), rot=-3))
        if tag == "dance":
            for k in range(4):
                ph = (t * 0.9 + k / 4) % 1
                o.append(stext(250 + k * 190, 900 - ph * 400, "♪", 80, fill=YEL, sw=8, op=1 - ph))
    return "".join(o)


def captions(t, tag):
    if tag == "meme": return ""
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
                out.append(stext(x, 1480, w, size, fill=YEL if k in KEY else "#F4EFE6", stroke="#120C0A", sw=12, anchor="start"))
                x += tw(w, size) + gap
            return "".join(out)
    return ""


def layer(f):
    F = PLAN["frames"][f]
    bg = plate.copy() if F["shot"] == "ui" else Image.open(os.path.join(FR, f"{f:05d}.png")).convert("RGBA")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{lib2d.DEFS}'
           f'{overlays(F)}{captions(F["t"], F.get("tag", ""))}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    return Image.alpha_composite(bg, ov)


FIRST = None


def one(f):
    global FIRST
    F = PLAN["frames"][f]
    if F["shot"] != "ui" and not os.path.exists(os.path.join(FR, f"{f:05d}.png")): return f, False
    im = layer(f); t = F["t"]
    if KIND in ("telefon", "vmoskve") and t > DUR - 0.3:
        if FIRST is None: FIRST = layer(0)
        im = Image.blend(im, FIRST, min(1, (t - DUR + 0.3) / 0.3))
    if KIND in ("musya", "obidelsya") and t > DUR - 0.5:
        im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), min(1, (t - DUR + 0.5) / 0.5))
    im.convert("RGB").save(os.path.join(CO, f"{f:05d}.png"))
    return f, True


if __name__ == "__main__":
    frames = [int(x) for x in sys.argv[6:]] or range(len(PLAN["frames"]))
    with Pool(os.cpu_count()) as p:
        res = p.map(one, frames, chunksize=8)
    miss = [f for f, ok in res if not ok]
    print("composed", len(res) - len(miss), "missing", len(miss))
    if len(sys.argv) > 6: sys.exit(0)
    if miss: sys.exit(1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", "scale=1080:1920:flags=lanczos,noise=alls=2:allf=t,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
