"""Variant B of a finished dialogue short for Instagram trial reels:
new hook title, boxed bottom captions, progress bar, tighter framing, warm grade, alternate music.
Usage: python3 compose_b.py <project_dir> <frames_dir> <out.mp4> "<HOOK LINE 1>" "<hook line 2>" """
import io, os, subprocess, sys
from multiprocessing import Pool
from PIL import Image

proj, FR, OUT = (os.path.abspath(a) for a in sys.argv[1:4])
HOOK1, HOOK2 = sys.argv[4], sys.argv[5]
CO = FR + "_b"
os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from base import tw, fit, stext, clamp, prog, e_back, popscale, FONT
from render import DEFS, CAPTION, wrap
from timeline import DUR, VOICE_START, VOICE_END, line_at

FPS = 24
ACC = "#FFD23F"


def boxed_caption(t):
    i = line_at(t)
    if t < VOICE_START[i] - 0.08 or t > VOICE_END[i] + 0.4: return ""
    txt = CAPTION.get(i, base.VOICE_TEXT[i])
    size = 50; lines = wrap(txt, size, 860)
    h = len(lines) * size * 1.25 + 50; y0 = 1500 - h / 2
    w = max(tw(l, size) for l in lines) + 70
    sc = 0.9 + 0.1 * e_back(prog(t, VOICE_START[i] - 0.08, VOICE_START[i] + 0.1))
    out = [f'<g transform="translate(540,1500) scale({sc:.3f}) translate(-540,-1500)">',
           f'<rect x="{540 - w / 2:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" rx="26" fill="#000" opacity="0.62"/>']
    for k, ln in enumerate(lines):
        out.append(stext(540, y0 + 25 + size * 0.62 + k * size * 1.25, ln, size, fill="#fff", sw=0, shadow=False).replace(FONT, "Inter Display Bold"))
    out.append("</g>")
    return "".join(out)


def hook(t):
    if t > 1.9: return ""
    a = 1 - clamp((t - 1.5) / 0.4)
    s1 = popscale(t, 0.05, 0.3); s2 = popscale(t, 0.35, 0.3)
    return (f'<g opacity="{a:.2f}"><rect width="1080" height="1920" fill="#000" opacity="0.35"/>'
            + stext(540, 820, HOOK1, fit(HOOK1, 960, 120), fill=ACC, sc=s1, rot=-3)
            + stext(540, 970, HOOK2, fit(HOOK2, 900, 56), fill="#fff", sc=s2, rot=-2) + "</g>")


def progress(t):
    p = clamp(t / DUR)
    return (f'<rect x="0" y="1900" width="1080" height="20" fill="#000" opacity="0.4"/>'
            f'<rect x="0" y="1900" width="{1080 * p:.1f}" height="20" fill="{ACC}"/>')


def one(f):
    src = os.path.join(FR, f"{f:05d}.png")
    t = f / FPS
    # tighter framing: crop 6% and scale back up
    im = Image.open(src).convert("RGB")
    W, H = im.size; cx, cy = int(W * 0.03), int(H * 0.03)
    im = im.crop((cx, cy, W - cx, H - cy)).resize((W, H), Image.LANCZOS).convert("RGBA")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}'
           f'{boxed_caption(t)}{progress(t)}{hook(t)}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    if t > DUR - 0.6: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), min(1, (t - DUR + 0.6) / 0.6))
    Image.alpha_composite(im, ov).convert("RGB").save(os.path.join(CO, f"{f:05d}.png"))
    return f


if __name__ == "__main__":
    n = int(DUR * FPS)
    with Pool(os.cpu_count()) as p:
        p.map(one, range(n), chunksize=8)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix_b.wav"),
                    "-vf", "scale=1080:1920:flags=lanczos,eq=saturation=1.12:contrast=1.04,colorbalance=rm=0.04:bm=-0.04,format=yuv420p",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
