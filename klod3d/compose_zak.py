"""Overlays + encode for «Вы уже закрываетесь?» (rain, sketch captions, ГАВ stamp, shawarma counter).
Usage: python3 compose_zak.py <project> <frames_dir> <plan.json> <out.mp4> [frames...]"""
import io, json, math, os, random, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image

proj, FR, PLANF, OUT = (os.path.abspath(a) for a in sys.argv[1:5])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from base import tw, fit, stext, clamp, prog, e_out, e_back, popscale, FONT

PLAN = json.load(open(PLANF)); FPS = PLAN["fps"]; S, E, DUR = PLAN["S"], PLAN["E"], PLAN["dur"]
SLAM, UP, FR0, FR1 = PLAN["slam"], PLAN["up"], PLAN["fr0"], PLAN["fr1"]
YEL = "#FFD23F"
KEY = {"закрываетесь", "собаки", "десять", "шаурмы", "двойное", "мясо", "наличкой", "гав", "мальчик"}
RR = random.Random(5)
DROPS = [(RR.uniform(-200, 1200), RR.uniform(0, 1920), RR.uniform(60, 130), RR.uniform(0.15, 0.4)) for _ in range(70)]


def rain(t):
    out = []
    for x, y, L, a in DROPS:
        yy = (y + t * 2600) % 2100 - 100; xx = x - (yy * 0.18)
        out.append(f'<line x1="{xx:.0f}" y1="{yy:.0f}" x2="{xx - L * 0.18:.0f}" y2="{yy + L:.0f}" stroke="#CFE3FF" stroke-width="3" stroke-opacity="{a:.2f}"/>')
    return "".join(out)


def overlays(F):
    t = F["t"]; o = []
    if t < S[0] - 0.1:
        o.append(base.pill(540, 1170, "23:59", 60, "#FF2A3A", "#FFFFFF", sc=popscale(t, 0.1), rot=-3))
        o.append(stext(540, 1310, "ЗА МИНУТУ ДО ЗАКРЫТИЯ", fit("ЗА МИНУТУ ДО ЗАКРЫТИЯ", 960, 84), fill="#FFFFFF", stroke="#0A0A10", sw=13, sc=popscale(t, 0.35)))
    if UP <= t < UP + 0.9:
        sc = popscale(t, UP + 0.02, 0.25); a = clamp(1 - (t - UP - 0.6) / 0.3)
        lines = "".join(f'<line x1="{540 + math.cos(k * 0.52) * 260:.0f}" y1="{330 + math.sin(k * 0.52) * 160:.0f}" x2="{540 + math.cos(k * 0.52) * 620:.0f}" y2="{330 + math.sin(k * 0.52) * 420:.0f}" stroke="#FFFFFF" stroke-width="9" stroke-opacity="0.75"/>' for k in range(12))
        o.append(f'<g opacity="{a:.2f}">{lines}' + stext(540, 330, "ГАВ!", 210, fill=YEL, stroke="#0A0A10", sw=26, rot=-8, sc=sc) + "</g>")
    if FR0 <= t < S[4] - 0.3:
        n = min(10, int((t - FR0) / ((FR1 - FR0) / 10.5)) + 1)
        o.append(stext(540, 330, f"×{n}", 170, fill=YEL, stroke="#0A0A10", sw=20, rot=-4, sc=0.9 + 0.25 * max(0, 1 - ((t - FR0) % ((FR1 - FR0) / 10.5)) * 8)))
        o.append(base.pill(540, 480, "ДВОЙНОЕ МЯСО", 48, "#FFFFFF", "#0A0A10", sc=popscale(t, FR0 + 0.2), rot=3))
    if t > E[4] + 0.25:
        o.append(base.pill(540, 360, "ОТМЕТЬ ТОГО, КТО ВСЕГДА", 40, YEL, "#0A0A10", sc=popscale(t, E[4] + 0.25), rot=-2)
                 + base.pill(540, 450, "ПРИХОДИТ ЗА МИНУТУ ДО ЗАКРЫТИЯ", 40, YEL, "#0A0A10", sc=popscale(t, E[4] + 0.4), rot=2))
    if SLAM <= t < SLAM + 0.15: o.append(f'<rect width="1080" height="1920" fill="#FFFFFF" opacity="{0.35 * (1 - (t - SLAM) / 0.15):.2f}"/>')
    return "".join(o)


def captions(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            words = [w["disp"].upper() for w in c]; size = 74; gap = size * 0.3
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 960: size = int(size * 960 / total); gap = size * 0.3; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            x = 540 - total / 2; out = []; sc = 0.8 + 0.2 * e_back(prog(t, t0, t0 + 0.15))
            for w in words:
                k = re.sub(r"[^\w-]", "", w).lower()
                out.append(stext(x, 1500, w, size, fill=YEL if k in KEY else "#FFFFFF", stroke="#0A0A10", sw=13, anchor="start"))
                x += tw(w, size) + gap
            return f'<g transform="translate(540,1500) scale({sc:.3f}) translate(-540,-1500)">' + "".join(out) + "</g>"
    return ""


def one(f):
    F = PLAN["frames"][f]; src = os.path.join(FR, f"{f:05d}.png")
    if not os.path.exists(src): return f, False
    bg = Image.open(src).convert("RGBA")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">'
           f'{rain(F["t"])}{overlays(F)}{captions(F["t"])}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    im = Image.alpha_composite(bg, ov)
    if F["t"] < 0.3: im = Image.blend(Image.new("RGBA", im.size, (0, 0, 0, 255)), im, F["t"] / 0.3)
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
    grade = "colorbalance=rs=-0.04:bs=0.06:rh=0.06:bh=-0.04,eq=contrast=1.06:saturation=1.1,noise=alls=3:allf=t,vignette=PI/5"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", f"scale=1080:1920:flags=lanczos,{grade},format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
