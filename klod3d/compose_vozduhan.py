"""Overlay HUD/UI/wind/captions on the blocky 3D «Воздухан» frames, seamless loop, encode.
Usage: python3 compose_vozduhan.py <vozduhan_project> <frames_dir> <plan.json> <plate.png> <out.mp4> [frames...]"""
import glob, io, json, os, subprocess, sys
from multiprocessing import Pool
from PIL import Image, ImageFilter

proj, FR, PLANF, PLATE, OUT = (os.path.abspath(a) for a in sys.argv[1:6])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
import render as R
import lib2d

PLAN = json.load(open(PLANF)); FPS = PLAN["fps"]
BOXES = {}
for fn in glob.glob(os.path.join(FR, "boxes_*.json")):
    BOXES.update({int(k): v for k, v in json.load(open(fn)).items()})
plate = Image.open(PLATE).convert("RGBA").filter(ImageFilter.GaussianBlur(10))


def note_card(t, t0):
    p = R.e_out(R.prog(t, t0, t0 + 0.4))
    inner = (R.stext(-300, -150, "Обещания Руслана", 40, fill="#fff", sw=0, shadow=False, anchor="start")
             + "".join(R.stext(-300, -70 + k * 70, "• " + s, 36, fill="#C9D1DC", sw=0, shadow=False, anchor="start")
                       for k, s in enumerate(("качалка", "бизнес", "Дубай", "вынести мусор (с 12 мая)"))))
    return f'<g transform="translate(0,{(1 - p) * -500:.0f})">' + lib2d.card(540, 420, 720, 420, inner) + "</g>"


def overlays(f, F):
    t, c, t0 = F["t"], F["cue"], F["cue_t"]
    o = []
    if c == "close" and R.line_now(t) == 0: o.append(R.promise_icons(t))
    if c == "klod_note": o.append(note_card(t, t0))
    if c == "klod_smug": o.append(R.stext(820, 420, "−0 ₽ за свет", 50, fill="#7FE3FF", sc=R.popscale(t, t0 + 0.3, 0.3), rot=8))
    B = BOXES.get(f)
    if c == "scan" and B:
        x, y = B["head"][0] * 1080, B["head"][1] * 1920; w, h = (B["head"][2] - B["head"][0]) * 1080, (B["head"][3] - B["head"][1]) * 1920
        hot = t > R.wt(5, "девяност")
        o.append(lib2d.brackets() + lib2d.box(int(x), int(y), int(w), int(h), "ВОЗДУХАН 99%" if hot else "АНАЛИЗ...", lib2d.RED if hot else lib2d.GRN)
                 + lib2d.stamp(t, R.wt(5, "воздух"), "ВОЗДУХАН"))
    return "".join(o)


def layer(f):
    F = PLAN["frames"][f]; t = F["t"]
    if F["shot"] == "ui":
        bg = plate.copy(); mid = R.mondays(t, F["cue_t"]).replace('<rect width="1080" height="1920" fill="#0B0D11"/>', '<rect width="1080" height="1920" fill="#0B0D11" opacity="0.75"/>', 1)
    else:
        bg = Image.open(os.path.join(FR, f"{f:05d}.png")).convert("RGBA"); mid = overlays(f, F)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{lib2d.DEFS}'
           f'{mid}{R.wind_fx(t, F["wind"])}{R.hud(t)}{R.captions(t)}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    return Image.alpha_composite(bg, ov)


FIRST = None


def one(f):
    global FIRST
    if not (PLAN["frames"][f]["shot"] == "ui" or os.path.exists(os.path.join(FR, f"{f:05d}.png"))): return f, False
    im = layer(f); t = PLAN["frames"][f]["t"]
    if t > PLAN["dur"] - 0.3:  # dissolve into frame 0 for a seamless loop
        if FIRST is None: FIRST = layer(0)
        im = Image.blend(im, FIRST, min(1, (t - PLAN["dur"] + 0.3) / 0.3))
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
