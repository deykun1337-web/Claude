"""Overlays + encode for the fundraising short about Дима.
Facts from the family's public profile @life_dima2025 (screenshot, 08.11.2026): goal 230 000 000 ₽, collected 159 087 583 ₽.
No payment details are shown on purpose: viewers are sent to the official profile only.
Usage: python3 compose_dima.py <project> <frames_dir> <plan.json> <out.mp4> [frames...]"""
import io, json, os, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image

proj, FR, PLANF, OUT = (os.path.abspath(a) for a in sys.argv[1:5])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from base import tw, fit, stext, clamp, prog, e_out, e_back, popscale, FONT
import lib2d

PLAN = json.load(open(PLANF)); FPS = PLAN["fps"]; S, E, DUR = PLAN["S"], PLAN["E"], PLAN["dur"]
GOAL, GOT = 230_000_000, 159_087_583
LEFT = GOAL - GOT
YEL, GRN, RED = "#FFC83D", "#3DDC84", "#FF4040"
MONO = "JetBrains Mono ExtraBold"
KEY = {"диме", "двенадцать", "дюшенна", "двести", "тридцать", "миллионов", "семьдесят", "семидесяти", "двадцать", "пять", "репост", "очередь", "сбор"}


def fmt(n): return f"{n:,}".replace(",", " ")


def progress_card(t, t0):
    p = e_out(prog(t, t0, t0 + 1.2)); got = int(GOT * p)
    w = 640 * GOT / GOAL * p
    return lib2d.card(540, 420, 820, 330,
                      stext(-370, -110, "Сбор для Димы", 40, fill="#fff", sw=0, shadow=False, anchor="start")
                      + stext(-370, -30, f"{fmt(got)} ₽", 64, fill=GRN, sw=0, shadow=False, anchor="start").replace(FONT, MONO)
                      + stext(-370, 30, f"из {fmt(GOAL)} ₽", 34, fill="#9AA3B2", sw=0, shadow=False, anchor="start")
                      + f'<rect x="-370" y="70" width="640" height="24" rx="12" fill="#252A33"/><rect x="-370" y="70" width="{w:.0f}" height="24" rx="12" fill="{GRN}"/>'
                      + stext(300, 82, f"{int(69 * p)}%", 30, fill="#fff", sw=0, shadow=False, anchor="start")
                      + stext(-370, 130, "по данным профиля @life_dima2025 на 08.11.2026", 22, fill="#6E7788", sw=0, shadow=False, anchor="start"))


def calc_card(t, t0):
    p = e_back(prog(t, t0, t0 + 0.4))
    return (f'<g transform="translate(540,430) scale({max(p, 0.01):.3f})">'
            + lib2d.card(0, 0, 820, 300,
                         stext(-370, -90, "Осталось собрать", 38, fill="#fff", sw=0, shadow=False, anchor="start")
                         + stext(-370, -20, f"≈ {fmt(LEFT)} ₽", 54, fill=YEL, sw=0, shadow=False, anchor="start").replace(FONT, MONO)
                         + stext(-370, 60, "÷ 25 ₽  ≈  2,8 млн человек", 46, fill=GRN, sw=0, shadow=False, anchor="start").replace(FONT, MONO))
            + "</g>")


def sent_chips(t, t0):
    return (lib2d.pill(540, 300, "✓ 25 ₽ отправлено".replace("✓ ", ""), 54, GRN, "#0B0D11", sc=popscale(t, t0 + 0.6), rot=-3)
            + lib2d.pill(540, 450, "РЕПОСТ СДЕЛАН", 54, YEL, "#0B0D11", sc=popscale(t, t0 + 1.4), rot=3))


def profile_card(t, t0):
    p = e_out(prog(t, t0, t0 + 0.4))
    return (f'<g transform="translate(0,{(1 - p) * -400:.0f})">'
            + lib2d.card(540, 430, 860, 380,
                         '<circle cx="-330" cy="-90" r="56" fill="#E1306C"/><circle cx="-330" cy="-90" r="46" fill="#16191F"/>'
                         + stext(-250, -110, "@life_dima2025", 52, fill="#fff", sw=0, shadow=False, anchor="start")
                         + stext(-250, -55, "Хрипченко Дима · Таганрог", 30, fill="#9AA3B2", sw=0, shadow=False, anchor="start")
                         + stext(-380, 40, "Ссылка на сбор — в шапке профиля", 38, fill=YEL, sw=0, shadow=False, anchor="start")
                         + stext(-380, 110, "Реквизиты проверяйте только там.", 32, fill="#FF8A8A", sw=0, shadow=False, anchor="start")
                         + stext(-380, 150, "Не переводите по ссылкам из комментариев.", 26, fill="#9AA3B2", sw=0, shadow=False, anchor="start"))
            + "</g>")


def overlays(F):
    t, i = F["t"], F["line"]
    o = []
    if i == 0 and t < E[0] + 0.2: o.append(stext(540, 330, "ДИМЕ НУЖНО 71 МЛН ₽", fit("ДИМЕ НУЖНО 71 МЛН ₽", 960, 100), fill=YEL, stroke="#1A1A1A", sw=14, rot=-2, sc=popscale(t, 0.05)))
    if i == 3: o.append(progress_card(t, S[3]))
    if i == 5: o.append(calc_card(t, S[5]))
    if i == 6: o.append(sent_chips(t, S[6]))
    if i == 7: o.append(profile_card(t, S[7]))
    if i == 8:
        o.append(stext(540, 360, "ТВОЯ ОЧЕРЕДЬ", fit("ТВОЯ ОЧЕРЕДЬ", 960, 130), fill=YEL, stroke="#1A1A1A", sw=14, rot=-3, sc=popscale(t, S[8]))
                 + lib2d.pill(540, 540, "@life_dima2025", 56, "#fff", "#0B0D11", sc=popscale(t, S[8] + 0.3)))
    return "".join(o)


def captions(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            size = 68; gap = size * 0.3
            words = [w["disp"].replace("лайф Дима двадцать двадцать пять", "@life_dima2025") for w in c]
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 960: size = int(size * 960 / total); gap = size * 0.3; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            x = 540 - total / 2; out = []
            for w in words:
                k = re.sub(r"[^\w-]", "", w).lower()
                out.append(stext(x, 1480, w, size, fill=YEL if k in KEY else "#F4EFE6", stroke="#120C0A", sw=12, anchor="start"))
                x += tw(w, size) + gap
            return "".join(out)
    return ""


def one(f):
    F = PLAN["frames"][f]; src = os.path.join(FR, f"{f:05d}.png")
    if not os.path.exists(src): return f, False
    bg = Image.open(src).convert("RGBA")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{lib2d.DEFS}'
           f'{overlays(F)}{captions(F["t"])}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    im = Image.alpha_composite(bg, ov)
    if F["t"] > DUR - 0.5: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), min(1, (F["t"] - DUR + 0.5) / 0.5))
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
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", "scale=1080:1920:flags=lanczos,noise=alls=2:allf=t,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
