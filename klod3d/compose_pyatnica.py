"""Hollywood-style finish for «Чёрная пятница»: letterbox, chrome titles, anamorphic flare, cinematic captions,
teal-orange grade + grain. Usage: python3 compose_pyatnica.py <project> <frames_dir> <plan.json> <out.mp4> [frames...]"""
import io, json, math, os, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image

proj, FR, PLANF, OUT = (os.path.abspath(a) for a in sys.argv[1:5])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from base import tw, fit, stext, clamp, prog, e_out, e_back, popscale, FONT

PLAN = json.load(open(PLANF)); FPS = PLAN["fps"]; S, E, DUR = PLAN["S"], PLAN["E"], PLAN["dur"]
CH0 = PLAN["ch0"]
GOLD = "#F2C66D"
DEFS = '''<defs>
<linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.45" stop-color="#C9D2DE"/><stop offset="0.55" stop-color="#6E7A8A"/><stop offset="1" stop-color="#E8EEF6"/></linearGradient>
<linearGradient id="goldg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF1C8"/><stop offset="0.5" stop-color="#E8B740"/><stop offset="1" stop-color="#9A6A1A"/></linearGradient>
<linearGradient id="flare" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5AB0FF" stop-opacity="0"/><stop offset="0.5" stop-color="#BFE2FF" stop-opacity="0.9"/><stop offset="1" stop-color="#5AB0FF" stop-opacity="0"/></linearGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFF4D8" stop-opacity="0.85"/><stop offset="1" stop-color="#FFB060" stop-opacity="0"/></radialGradient>
</defs>'''


def title(txt, y, size, t, t0, fill="url(#chrome)", spacing=0):
    if t < t0: return ""
    p = e_out(prog(t, t0, t0 + 0.6)); sc = 1.25 - 0.25 * p
    return (f'<g opacity="{p:.2f}" transform="translate(540,{y}) scale({sc:.3f})">'
            + stext(0, 0, txt, size, fill=fill, stroke="#0A0C10", sw=size * 0.08, shadow=True) + "</g>")


def flare(x, y, k):
    if k <= 0: return ""
    return (f'<g opacity="{k:.2f}"><rect x="-200" y="{y - 5}" width="1480" height="10" fill="url(#flare)"/>'
            f'<circle cx="{x}" cy="{y}" r="140" fill="url(#glow)"/></g>')


def overlays(F):
    t, sh, i = F["t"], F["shot"], F["line"]
    o = []
    if sh == "crane":
        o.append(title("27 НОЯБРЯ · 06:59", 520, 64, t, 0.15, fill="url(#goldg)"))
        o.append(title("ЧЁРНАЯ ПЯТНИЦА", 650, fit("ЧЁРНАЯ ПЯТНИЦА", 940, 104), t, 0.8))
        o.append(flare(540, 1060, 0.6 + 0.2 * math.sin(t * 3)))
    if sh == "charge":
        k = clamp((t - CH0) / 0.5)
        o.append(flare(540, 1000, k) + f'<rect width="1080" height="1920" fill="#FFF4D8" opacity="{0.35 * max(0, 1 - abs(t - CH0 - 0.35) * 4):.2f}"/>')
        o.append(title("ЗА СКИДКИ", 470, 110, t, CH0 + 0.2))
    if sh == "end":
        o.append(title("С ЧЁРНОЙ ПЯТНИЦЕЙ", 560, fit("С ЧЁРНОЙ ПЯТНИЦЕЙ", 940, 90), t, F["shot_t"] + 0.3))
        if t > DUR - 1.4: o.append(base.pill(540, 1260, "ОТМЕТЬ ТОГО, КТО ПОЙДЁТ ЗА СКИДКАМИ", 34, GOLD, "#0A0C10", sc=popscale(t, DUR - 1.4)))
    return "".join(o)


def captions(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            txt = " ".join(w["disp"] for w in c)
            size = min(64, fit(txt, 900, 64))
            a = clamp((t - t0) * 8)
            return stext(540, 1560, txt, size, fill="#F4F1EA", stroke="#000", sw=6, shadow=True, op=a).replace(FONT, "Inter Display Bold")
    return ""


def letterbox(t):
    h = 150 if t > 0.0 else 0
    return f'<rect width="1080" height="{h}" fill="#000"/><rect y="{1920 - h}" width="1080" height="{h}" fill="#000"/>'


def one(f):
    F = PLAN["frames"][f]; src = os.path.join(FR, f"{f:05d}.png")
    if not os.path.exists(src): return f, False
    bg = Image.open(src).convert("RGBA")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}'
           f'{overlays(F)}{letterbox(F["t"])}{captions(F["t"])}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    im = Image.alpha_composite(bg, ov)
    if F["t"] < 0.4: im = Image.blend(Image.new("RGBA", im.size, (0, 0, 0, 255)), im, F["t"] / 0.4)
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
    grade = "colorbalance=rs=-0.06:bs=0.08:rh=0.07:bh=-0.06,eq=contrast=1.08:saturation=1.1,noise=alls=4:allf=t,vignette=PI/5"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", f"scale=1080:1920:flags=lanczos,{grade},format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
