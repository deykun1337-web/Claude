"""UI overlays + encode for the explainer (karaoke captions on top, white chips, counters, prompt bar, progress bar).
Usage: python3 compose_kak.py <project> <frames_dir> <plan.json> <out.mp4> [frames...]"""
import io, json, math, os, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image

proj, FR, PLANF, OUT = (os.path.abspath(a) for a in sys.argv[1:5])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from base import tw, fit, stext, clamp, prog, e_out, e_back, popscale, FONT

PLAN = json.load(open(PLANF)); FPS = PLAN["fps"]; S, E, DUR = PLAN["S"], PLAN["E"], PLAN["dur"]
ORANGE = "#D97757"; INK = "#14161C"
DEFS = '<defs><filter id="sh" x="-20%" y="-40%" width="140%" height="180%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity="0.35"/></filter></defs>'


def chip(cx, cy, txt, size, sc=1.0, bg="#FFFFFF", fg=INK, rot=0, border=None):
    if sc <= 0.001: return ""
    w = tw(txt, size) + size * 1.1; h = size * 1.6
    bd = f' stroke="{border}" stroke-width="5"' if border else ""
    return (f'<g filter="url(#sh)" transform="translate({cx:.1f},{cy:.1f}) rotate({rot}) scale({sc:.3f})">'
            f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h * 0.28:.1f}" fill="{bg}"{bd}/>'
            + stext(0, 0, txt, size, fill=fg, sw=0, shadow=False) + "</g>")


def money(n): return "$" + f"{n:,}".replace(",", " ")


def overlays(F):
    t = F["t"]; b = F["beat"]; bt = F["bt"]; o = []
    if b == 0:
        n = int(200_000_000 * e_out(prog(t, 0.3, 2.6)))
        o.append(chip(540, 560, money(n), 64, popscale(t, 0.15)))
        o.append(chip(540, 680, "1 мультфильм Pixar", 36, popscale(t, 0.6), bg=INK, fg="#FFFFFF"))
    if b == 1:
        sc = popscale(bt, 0.3, 0.3)
        o.append(f'<g filter="url(#sh)" transform="translate(540,640) rotate(-4) scale({sc:.3f})"><path d="M-230,-110 L170,-110 L250,0 L170,110 L-230,110 Z" fill="#3DDC84"/>'
                 + stext(-20, 0, "$0", 150, fill="#FFFFFF", sw=0, shadow=False) + "</g>")
        o.append(chip(540, 820, "по одному сообщению", 40, popscale(bt, 0.9)))
    if b == 2:
        o.append(chip(540, 560, "* Claude", 52, popscale(bt, 0.4), bg=ORANGE, fg="#FFFFFF"))
    if b == 3:
        full = "сделай трендовый мультик"; n = int(len(full) * prog(bt, 0.6, 2.2)); txt = full[:n] + ("|" if (t * 3) % 1 < 0.5 else " ")
        w = 900; sc = popscale(bt, 0.2, 0.3)
        o.append(f'<g filter="url(#sh)" transform="translate(540,1290) scale({sc:.3f})"><rect x="{-w / 2}" y="-60" width="{w}" height="120" rx="34" fill="#FFFFFF"/>'
                 + stext(-w / 2 + 60, 8, "*", 70, fill=ORANGE, sw=0, shadow=False) + stext(-w / 2 + 110, 0, txt, 44, fill=INK, sw=0, shadow=False, anchor="start")
                 + f'<circle cx="{w / 2 - 60}" cy="0" r="36" fill="{ORANGE}"/>' + stext(w / 2 - 60, 0, "↑", 44, fill="#FFFFFF", sw=0, shadow=False) + "</g>")
    if b == 4:
        o.append(chip(330, 560, "тренды ↑", 44, popscale(bt, 0.3), bg="#3DDC84", fg=INK, rot=-4))
        o.append(chip(750, 640, "сценарий ✓", 44, popscale(bt, 1.0), rot=3))
    if b == 5:
        opts = ["низкий", "писклявый", "скуф"]; sel = min(2, int(bt / 0.75))
        for i, s in enumerate(opts):
            on = i == sel
            o.append(chip(230 + i * 310, 560, s, 40, popscale(bt, 0.2 + 0.15 * i), bg=ORANGE if on else "#FFFFFF", fg="#FFFFFF" if on else INK))
    if b == 6:
        o.append(chip(540, 560, "3D · Blender · 24 кадра/с", 40, popscale(bt, 0.3), bg=INK, fg="#FFFFFF"))
    if b == 7:
        p = e_out(prog(bt, 0.2, 3.2)); sc = popscale(bt, 0.1, 0.3); w = 820
        o.append(f'<g filter="url(#sh)" transform="translate(540,560) scale({sc:.3f})"><rect x="{-w / 2 - 20}" y="-70" width="{w + 40}" height="140" rx="30" fill="#FFFFFF"/>'
                 f'<rect x="{-w / 2}" y="5" width="{w}" height="34" rx="17" fill="#E9E4DA"/><rect x="{-w / 2}" y="5" width="{w * p:.0f}" height="34" rx="17" fill="{ORANGE}"/>'
                 + stext(-w / 2, -32, f"рендер: кадр {int(500 * p)} / 500", 36, fill=INK, sw=0, shadow=False, anchor="start")
                 + stext(w / 2, -32, f"{int(100 * p)}%", 36, fill=ORANGE, sw=0, shadow=False, anchor="end") + "</g>")
        if bt > 1.0: o.append(chip(250, 1250, "Руслан: чай ☕", 36, popscale(bt, 1.0), rot=-3) if False else chip(250, 1250, "Руслан пьёт чай", 36, popscale(bt, 1.0), rot=-3))
    if b == 8:
        o.append(chip(540, 540, "✓ рилс готов", 46, popscale(bt, 0.35), bg="#3DDC84", fg=INK))
    if b == 9:
        o.append(chip(300, 1180, money(200_000_000), 38, popscale(bt, 0.3), bg=INK, fg="#FFFFFF", rot=-3))
        o.append(chip(800, 1000, "1 подписка", 40, popscale(bt, 0.6), bg=ORANGE, fg="#FFFFFF", rot=3))
    if b == 10:
        o.append(chip(540, 1230, "@deykun1337", 52, popscale(bt, 0.3), bg="#FFFFFF", fg=INK))
        o.append(chip(540, 1360, "ПОДПИШИСЬ", 54, popscale(bt, 0.7) * (1 + 0.04 * math.sin(t * 8)), bg=ORANGE, fg="#FFFFFF"))
    return "".join(o)


def captions(t):
    """Karaoke captions on top: current word white, others dimmed (like the reference)."""
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            words = [w["disp"] for w in c]; size = 70; gap = size * 0.3
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 940: size = int(size * 940 / total); gap = size * 0.3; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            x = 540 - total / 2; out = []
            for w, wd in zip(words, c):
                cur = wd["t0"] - 0.05 <= t
                out.append(stext(x, 400, w, size, fill="#FFFFFF", stroke="#000000", sw=8, anchor="start", op=1.0 if cur else 0.45))
                x += tw(w, size) + gap
            return "".join(out)
    return ""


def one(f):
    F = PLAN["frames"][f]; src = os.path.join(FR, f"{f:05d}.png")
    if not os.path.exists(src): return f, False
    bg = Image.open(src).convert("RGBA")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}'
           f'{overlays(F)}{captions(F["t"])}{base.WM()}</svg>')
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
    grade = "eq=contrast=1.04:saturation=1.08,noise=alls=2:allf=t,vignette=PI/6"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", f"scale=1080:1920:flags=lanczos,{grade},format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
