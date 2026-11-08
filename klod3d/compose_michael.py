"""Overlay HUD/UI/captions on the blocky 3D «Майкл из Техаса» frames and encode (also used for «Воздухан» via MODE=vozduhan).
Usage: python3 compose_michael.py <ruslan_project> <frames_dir> <plan.json> <plate.png> <portrait.png> <out.mp4>"""
import base64, glob, io, json, os, subprocess, sys
from multiprocessing import Pool
from PIL import Image, ImageFilter

proj, FR, PLANF, PLATE, PORT, OUT = (os.path.abspath(a) for a in sys.argv[1:7])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
import render as R

PLAN = json.load(open(PLANF)); FPS = PLAN["fps"]
BOXES = {}
for fn in glob.glob(os.path.join(FR, "boxes_*.json")):
    BOXES.update({int(k): v for k, v in json.load(open(fn)).items()})
plate = Image.open(PLATE).convert("RGBA").filter(ImageFilter.GaussianBlur(10))
P64 = base64.b64encode(open(PORT, "rb").read()).decode()

# passport photo: the blocky 3D portrait instead of the 2D drawing
R.ruslan = lambda *a, **k: (f'<svg x="-357" y="-428" width="714" height="904" viewBox="40 150 640 810" preserveAspectRatio="xMidYMid slice">'
                            f'<image href="data:image/png;base64,{P64}" width="720" height="1280"/></svg>')
UI_FN = {"ui_verify": R.ui_verify, "ui_max": R.ui_max, "passport": R.passport, "passport2": lambda t, t0: R.passport(t, t0, True),
         "ui_ok": R.ui_ok, "ui_block": R.ui_block, "bank": R.bank}


def ui_svg(c, t, t0):
    if c == "city": return R.city(t)
    if c == "end":
        return R.scene(t)
    s = UI_FN[c](t, t0)
    for col in ("#0B0D11", "#120F0D", "#06140D", "#140606"):
        s = s.replace(f'<rect width="1080" height="1920" fill="{col}"/>', f'<rect width="1080" height="1920" fill="{col}" opacity="0.74"/>', 1)
    return s


def bx(b):  # normalized box -> 1080x1920 coords
    return b[0] * 1080, b[1] * 1920, (b[2] - b[0]) * 1080, (b[3] - b[1]) * 1920


def overlays(f, F):
    t, c, t0 = F["t"], F["cue"], F["cue_t"]
    o = []
    B = BOXES.get(f)
    if c == "close": o.append(R.lower_third(t, R.S[4]))
    if c == "scan" and B:
        x, y, w, h = bx(B["head"])
        o.append(R.brackets() + f'<ellipse cx="{x + w / 2:.0f}" cy="{y + h / 2:.0f}" rx="{w * 0.75:.0f}" ry="{h * 0.9:.0f}" fill="none" stroke="#3DDC84" stroke-width="5" stroke-dasharray="14 12"/>'
                 + R.box(int(x), int(y), int(w), int(h), "ЛИЦО: МАЙКЛ? 41%", R.GRN)
                 + '<rect x="330" y="1300" width="420" height="64" rx="32" fill="#0E1116" opacity="0.85"/>' + R.stext(540, 1332, "Поверните голову", 34, fill="#fff", sw=0, shadow=False))
    if c == "detect" and B:
        x, y, w, h = bx(B["carpet"]); o.append(R.brackets() + R.box(int(x), int(y), int(w), int(h), "ОБЪЕКТ: КОВЁР 99%", R.RED))
    if c == "flag": o.append(R.stext(760, 420, "БАМ!", 130, fill="#fff", sc=R.popscale(t, t0, 0.25), rot=-10))
    if c == "room_mom" and B:
        x, y, w, h = bx(B["mom"]); o.append(R.box(int(x), int(y), int(w), int(h), "ВТОРОЙ ЧЕЛОВЕК", R.RED))
    if c == "susp": o.append(R.stamp(t, R.S[19] + 0.3))
    if c == "party": o.append('<rect width="1080" height="1920" fill="#1E7A4A" opacity="0.16"/>')
    return "".join(o)


def one(f):
    F = PLAN["frames"][f]; t = F["t"]
    if F["shot"] == "ui":
        bg = plate.copy(); mid = ui_svg(F["cue"], t, F["cue_t"])
    else:
        src = os.path.join(FR, f"{f:05d}.png")
        if not os.path.exists(src): return f, False
        bg = Image.open(src).convert("RGBA"); mid = overlays(f, F)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{R.DEFS}'
           f'{mid}{R.hud(t)}{R.captions(t)}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    im = Image.alpha_composite(bg, ov)
    if t > R.DUR - 0.6: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), min(1, (t - R.DUR + 0.6) / 0.6))
    im.convert("RGB").save(os.path.join(CO, f"{f:05d}.png"))
    return f, True


if __name__ == "__main__":
    frames = [int(x) for x in sys.argv[7:]] or range(len(PLAN["frames"]))
    with Pool(os.cpu_count()) as p:
        res = p.map(one, frames, chunksize=8)
    miss = [f for f, ok in res if not ok]
    print("composed", len(res) - len(miss), "missing", len(miss))
    if len(sys.argv) > 7: sys.exit(0)
    if miss: sys.exit(1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", "scale=1080:1920:flags=lanczos,noise=alls=2:allf=t,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
