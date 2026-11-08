"""Gacha-style overlays + encode for «Уровни редкости кабанов» (claymation, animated on twos).
Usage: python3 compose_clay.py <project> <frames_dir> <plan.json> <out.mp4> [frames...]"""
import io, json, math, os, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image

proj, FR, PLANF, OUT = (os.path.abspath(a) for a in sys.argv[1:5])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from base import tw, fit, stext, clamp, prog, e_out, e_back, popscale, star4, FONT

PLAN = json.load(open(PLANF)); FPS = PLAN["fps"]; S, E, DUR = PLAN["S"], PLAN["E"], PLAN["dur"]
DROP, BANNER = PLAN["drop"], PLAN["banner"]
RCOL = ["#3BA0FF", "#B45CFF", "#FFB21F", "#FF3B5C"]
NAMES = ["RARE", "SUPER RARE", "EPIC", "MYTHIC"]
CHANCE = ["шанс 60%", "шанс 25%", "шанс 9%", "шанс 0,01%"]
WHO = ["Кабан обычный", "Кабан на массе", "Кабан-нейросеть · Клод", "Руслан ДЕЙКУН Кабанович"]
DEFS = '''<defs>
<linearGradient id="g0" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFE4FF"/><stop offset="1" stop-color="#2F86F0"/></linearGradient>
<linearGradient id="g1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F0D6FF"/><stop offset="1" stop-color="#9442F0"/></linearGradient>
<linearGradient id="g2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF4C2"/><stop offset="0.55" stop-color="#FFC233"/><stop offset="1" stop-color="#D9780F"/></linearGradient>
<linearGradient id="g3" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FF3B5C"/><stop offset="0.25" stop-color="#FFB21F"/><stop offset="0.5" stop-color="#FFF36B"/><stop offset="0.75" stop-color="#3DDC84"/><stop offset="1" stop-color="#3BA0FF"/></linearGradient>
<filter id="gl" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>'''
KEY = {"рэр": 0, "рэйр": 0, "супер": 1, "эпик": 2, "мифик": 3, "мифик...": 3}


def banner(t, i):
    t0 = BANNER[i]
    if t < t0: return ""
    sc = popscale(t, t0, 0.4)
    size = fit(NAMES[i], 900, 120 if i < 3 else 135)
    shake = 0
    if i == 3 and t < DROP[3] + 0.4: shake = 5 * math.sin(t * 60)
    nstar = i + 2 if i < 3 else 5
    stars = "".join(star4(540 + (k - (nstar - 1) / 2) * 60, 318, 24 * popscale(t, t0 + 0.15 + 0.07 * k, 0.25), "#FFE27A", rot=t * 40)
                    for k in range(nstar))
    glow = '<g filter="url(#gl)" opacity="0.8">' + stext(540, 215, NAMES[i], size, fill=RCOL[i], stroke=RCOL[i], sw=size * 0.2, shadow=False) + "</g>"
    title = stext(540, 215, NAMES[i], size, fill=f"url(#g{i})", stroke="#14101E", sw=size * 0.12)
    out = (f'<g transform="translate({540 + shake:.1f},215) scale({sc:.3f}) translate(-540,-215)">{glow}{title}</g>{stars}')
    out += base.pill(540, 1415, CHANCE[i], 36, "#14101E", "#FFFFFF", sc=popscale(t, t0 + 0.25))
    if i < 3 or t >= DROP[3] + 0.2:
        out += stext(540, 1310, WHO[i], fit(WHO[i], 940, 62), fill="#FFFFFF", stroke="#14101E", sw=10, sc=popscale(t, (DROP[i] + 0.3 if i else DROP[0] + 0.3)))
    else:
        out += stext(540, 1310, "???", 90, fill=RCOL[3], stroke="#14101E", sw=14, sc=popscale(t, t0 + 0.3), rot=4 * math.sin(t * 9))
    # sparkles orbiting the banner right after the reveal
    if t < t0 + 1.2:
        k = prog(t, t0, t0 + 1.2)
        for j in range(8):
            a = j * math.pi / 4 + k * 2.5
            out += star4(540 + math.cos(a) * (220 + 260 * k), 215 + math.sin(a) * (90 + 120 * k), 22 * (1 - k), "#FFFFFF", rot=t * 90)
    return out


def overlays(F):
    t = F["t"]; o = []
    if t < DROP[0] + 0.1:
        a = clamp(1 - (t - DROP[0] + 0.25) / 0.3) if t > DROP[0] - 0.25 else 1
        o.append(f'<g opacity="{a:.2f}">' + stext(540, 215, "УРОВНИ РЕДКОСТИ", fit("УРОВНИ РЕДКОСТИ", 960, 110), fill="#FFFFFF", stroke="#14101E", sw=16, sc=popscale(t, 0.1))
                 + stext(540, 330, "КАБАНОВ", 110, fill="url(#g3)", stroke="#14101E", sw=18, sc=popscale(t, 0.35), rot=-3) + "</g>")
        o.append(base.pill(540, 1215, "ОТКРЫВАЕМ ПАК", 44, "#FFE27A", "#14101E", sc=popscale(t, 0.6), rot=2))
    cur = max([i for i in range(4) if t >= BANNER[i]] or [-1])
    if 0 <= cur and t < S[6] - 0.35:
        nxt = BANNER[cur + 1] if cur < 3 else S[6] - 0.35
        if t < nxt - 0.05: o.append(banner(t, cur))
    if t >= S[6] - 0.35:
        o.append(stext(540, 215, "А ТЕБЕ КАКОЙ", fit("А ТЕБЕ КАКОЙ", 960, 110), fill="#FFFFFF", stroke="#14101E", sw=16, sc=popscale(t, S[6] - 0.2))
                 + stext(540, 330, "ВЫПАЛ?", 115, fill="url(#g3)", stroke="#14101E", sw=18, sc=popscale(t, S[6] + 0.1), rot=-3)
                 + base.pill(540, 1215, "ПИШИ В КОММЕНТЫ", 46, "#FFE27A", "#14101E", sc=popscale(t, E[6] - 0.3), rot=-2))
    # white flash on the pack burst and the mythic drop
    for tf, k in ((DROP[0] - 0.05, 0.7), (DROP[3] + 0.2, 0.9)):
        if tf <= t < tf + 0.35: o.append(f'<rect width="1080" height="1920" fill="#FFFFFF" opacity="{k * (1 - (t - tf) / 0.35):.2f}"/>')
    return "".join(o)


def captions(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            words = [w["disp"] for w in c]; size = 66; gap = size * 0.3
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 940: size = int(size * 940 / total); gap = size * 0.3; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            x = 540 - total / 2; out = []; sc = 0.85 + 0.15 * e_back(prog(t, t0, t0 + 0.15))
            for w in words:
                k = re.sub(r"[^\w.]", "", w).lower().rstrip(".")
                col = RCOL[KEY[k]] if k in KEY else "#FFFFFF"
                out.append(stext(x, 1560, w, size, fill=col, stroke="#14101E", sw=11, anchor="start"))
                x += tw(w, size) + gap
            return f'<g transform="translate(540,1560) scale({sc:.3f}) translate(-540,-1560)">' + "".join(out) + "</g>"
    return ""


def one(f):
    F = PLAN["frames"][f]; src = os.path.join(FR, f"{f - f % 2:05d}.png")
    if not os.path.exists(src): return f, False
    t_real = f / FPS
    bg = Image.open(src).convert("RGBA")
    F2 = dict(F); F2["t"] = F["t"]  # overlays also on twos, like the puppets
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}'
           f'{overlays(F2)}{captions(t_real)}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    im = Image.alpha_composite(bg, ov)
    if t_real > DUR - 0.4: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), min(1, (t_real - DUR + 0.4) / 0.4))
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
    grade = "eq=contrast=1.05:saturation=1.12,noise=alls=3:allf=t,vignette=PI/6"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", f"scale=1080:1920:flags=lanczos,{grade},format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
