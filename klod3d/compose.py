"""Overlay captions + watermark on the Blender frames and encode the final video.
Usage: python3 compose.py <project_dir> <frames_dir> <out.mp4>"""
import io, os, subprocess, sys
from multiprocessing import Pool
from PIL import Image

proj, FR, OUT = (os.path.abspath(a) for a in sys.argv[1:4])
CO = FR + "_c"
os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from render import caption, DEFS
from timeline import DUR

FPS = 24


def one(f):
    src = os.path.join(FR, f"{f:05d}.png")
    if not os.path.exists(src): return f, False
    t = f / FPS
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}'
           f'{caption(t)}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    im = Image.open(src).convert("RGBA")
    if t < 0.3: im = Image.blend(Image.new("RGBA", im.size, (0, 0, 0, 255)), im, t / 0.3)
    if t > DUR - 0.6: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), min(1, (t - DUR + 0.6) / 0.6))
    Image.alpha_composite(im, ov).convert("RGB").save(os.path.join(CO, f"{f:05d}.png"))
    return f, True


if __name__ == "__main__":
    n = int(DUR * FPS)
    with Pool(os.cpu_count()) as p:
        res = p.map(one, range(n), chunksize=8)
    missing = [f for f, ok in res if not ok]
    print("composed", n - len(missing), "missing", len(missing))
    if missing: sys.exit(1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
