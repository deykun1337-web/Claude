"""2D overlay + encode for «Агенты»: hook title, agent labels, cards, bubbles, Zz, word-box captions, 2D UI shots.
Usage: python3 compose_agents.py <project_dir> <frames_dir> <plan.json> <out.mp4>"""
import io, json, glob, math, os, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image

proj, FR, PLANF, OUT = (os.path.abspath(a) for a in sys.argv[1:5])
CO = FR + "_c"; os.makedirs(CO, exist_ok=True)
os.chdir(proj); sys.path.insert(0, proj)
import cairosvg, base
from base import tw, fit, stext, clamp, prog, lerp, e_out, e_back, popscale, FONT
from timeline import DUR, WORDS, VOICE_START

PLAN = json.load(open(PLANF)); C = PLAN["cues"]; FPS = PLAN["fps"]
LABELS = {}
for fn in glob.glob(os.path.join(FR, "labels_*.json")):
    LABELS.update({int(k): v for k, v in json.load(open(fn)).items()})
SERIF = "DejaVu Serif"
ORANGE = "#E8833A"


def chip(x, y, txt, size=30, bg="#F4F1EA", fg="#1A1A1A", icon=""):
    w = tw(txt, size) + 40
    return (f'<g transform="translate({x:.0f},{y:.0f})"><rect x="{-w / 2:.0f}" y="-26" width="{w:.0f}" height="52" rx="26" fill="{bg}" stroke="#1A1A1A" stroke-width="3"/>'
            + stext(0, 0, txt, size, fill=fg, sw=0, shadow=False).replace(FONT, "Inter Display Bold") + "</g>")


def card(x, y, w, h, title, body, t, t0):
    p = e_out(prog(t, t0, t0 + 0.35))
    if p <= 0: return ""
    return (f'<g transform="translate({x},{y - (1 - p) * 60:.0f})" opacity="{p:.2f}"><rect width="{w}" height="{h}" rx="18" fill="#12151B" opacity="0.92" stroke="#2C313B" stroke-width="3"/>'
            '<circle cx="24" cy="22" r="6" fill="#FF5F57"/><circle cx="44" cy="22" r="6" fill="#FEBC2E"/><circle cx="64" cy="22" r="6" fill="#28C840"/>'
            + stext(24, 66, title, 36, fill="#fff", sw=0, shadow=False, anchor="start") + body + "</g>")


def bubble(x, y, txt, t, t0, dur=2.2):
    if not (t0 <= t < t0 + dur): return ""
    sc = popscale(t, t0, 0.3)
    w = tw(txt, 52) + 70
    return (f'<g transform="translate({x},{y}) scale({sc:.3f})"><rect x="{-w / 2:.0f}" y="-50" width="{w:.0f}" height="100" rx="26" fill="#fff" stroke="#1A1A1A" stroke-width="5"/>'
            '<polygon points="-20,48 20,48 0,84" fill="#fff" stroke="#1A1A1A" stroke-width="5"/><rect x="-18" y="40" width="36" height="12" fill="#fff"/>'
            + stext(0, 0, txt, 52, fill="#1A1A1A", sw=0, shadow=False) + "</g>")


def zz(x, y, t, k):
    o = ""
    for j in range(3):
        ph = ((t * 0.8 + j / 3 + k * 0.17) % 1)
        o += stext(x + 20 + ph * 50, y - 20 - ph * 110, "z", 30 + j * 10, fill="#D8E4FF", sw=6, shadow=False, op=1 - ph)
    return o


def labels(f, t):
    out = []
    for k, L in enumerate(LABELS.get(f, [])):
        x, y = L["x"] * 1080, L["y"] * 1920
        if L["lab"] and L["s"] > 0.8: out.append(chip(x, y - 30, L["lab"], 28 if L["id"] != "klod" else 26, bg="#F4F1EA" if L["id"] != "klod" else ORANGE, fg="#1A1A1A"))
        if L["sleep"]: out.append(zz(x, y + 20, t, k))
    return "".join(out)


def bars(t, t0):
    o = ""
    vals = [0.3, 0.6, 0.45, 0.9, 0.2, 0.75, 0.5, 0.95]
    for k, v in enumerate(vals):
        h = 150 * v * e_out(prog(t, t0 + k * 0.05, t0 + k * 0.05 + 0.4))
        o += f'<rect x="{30 + k * 62}" y="{260 - h:.0f}" width="44" height="{h:.0f}" fill="{ORANGE if v > 0.7 else "#E05A4A"}"/>'
    return o


def ui_installed(t, t0):
    p = e_out(prog(t, t0, t0 + 1.2))
    return ('<rect width="1080" height="1920" fill="#07080C"/><rect x="140" y="560" width="800" height="520" rx="20" fill="#0E1016" stroke="#2C313B" stroke-width="10"/>'
            + stext(540, 780, "Claude установлен ✓".replace(" ✓", ""), 54, fill="#C9D1DC", sw=0, shadow=False)
            + f'<rect x="300" y="860" width="480" height="14" rx="7" fill="#1E222B"/><rect x="300" y="860" width="{480 * p:.0f}" height="14" rx="7" fill="{ORANGE}"/>'
            + (f'<path d="M 860 770 l 18 18 l 34 -38" stroke="#3DDC84" stroke-width="10" fill="none"/>' if p >= 1 else ""))


def email(t, t0, stop):
    txt = "Добрый д"
    n = min(len(txt), int((t - t0 - 0.6) * 4)) if t > t0 + 0.6 else 0
    cur = "|" if (t * 2) % 1 < 0.5 else ""
    o = ['<rect width="1080" height="1920" fill="#E9E7E1"/>', '<rect x="80" y="380" width="920" height="1000" rx="12" fill="#fff" stroke="#BDB8AC" stroke-width="4"/>',
         stext(130, 450, "Новое письмо", 34, fill="#8A857A", sw=0, shadow=False, anchor="start"),
         '<line x1="110" y1="490" x2="970" y2="490" stroke="#E2DED4" stroke-width="3"/>',
         f'<text x="130" y="600" font-family="{SERIF}" font-size="64" fill="#1A1A1A">{txt[:n]}{cur}</text>']
    if t >= stop:
        o.append('<rect width="1080" height="1920" fill="#C21010" opacity="0.18"/>' + bubble(540, 900, "Не лезь!", t, stop, 9) + bubble(700, 1150, "Мы сами", t, stop + 0.6, 9))
    return "".join(o)


def hook(t):
    if t > C["hook_end"]: return ""
    a = 1 - clamp((t - C["hook_end"] + 0.3) / 0.3)
    return (f'<g opacity="{a:.2f}"><g transform="translate(540,180)"><path d="M -300 -50 L 300 -50 L 270 0 L 300 50 L -300 50 L -270 0 Z" fill="#E8DCC0" stroke="#1A1A1A" stroke-width="5"/>'
            + stext(0, 0, "Скачал Клода", 54, fill="#1A1A1A", sw=0, shadow=False) + "</g>"
            + stext(80, 1180, "СКАЧАЛ КЛОДА.", 84, fill="#fff", stroke="#1A1A1A", sw=12, anchor="start")
            + stext(80, 1290, "ЧТО ДАЛЬШЕ?", 84, fill="#FFC83D", stroke="#1A1A1A", sw=12, anchor="start") + "</g>")


def overlays(f, t, shot):
    o = [hook(t)]
    if shot == "room":
        o.append(labels(f, t))
        o.append(card(300, 120, 520, 300, "Продуктивность", bars(t, C["prod"]), t, C["prod"]) if C["prod"] <= t < C["prod"] + 4.5 else "")
        o.append(card(260, 120, 560, 200, "Совет агентов", stext(24, 140, "47 : 0 ✓".replace(" ✓", ""), 70, fill="#3DDC84", sw=0, shadow=False, anchor="start").replace(FONT, "JetBrains Mono ExtraBold"), t, C["council"]) if C["council"] <= t < C["council"] + 3 else "")
        o.append(card(260, 120, 560, 190, "4 агента спят", stext(24, 130, "ничего не делают", 34, fill="#9AA3B2", sw=0, shadow=False, anchor="start"), t, C["sleep"]) if C["sleep"] <= t < C["sleep"] + 4 else "")
        o.append(card(260, 120, 560, 190, "Юрист → агент", stext(24, 130, "представляет интересы спящих", 30, fill="#9AA3B2", sw=0, shadow=False, anchor="start"), t, C["law"]) if C["law"] <= t < C["law"] + 3.5 else "")
        o.append(bubble(300, 1100, "Пока!", t, C["bye"], 2.4))
        o.append(card(260, 120, 560, 190, "Требуются агенты", stext(24, 130, "опыт: 0 дней, без выходных", 30, fill="#9AA3B2", sw=0, shadow=False, anchor="start"), t, C["hire"]) if C["hire"] <= t < C["hire"] + 3.5 else "")
        o.append(bubble(760, 820, "Не лезь", t, C["nolez"], 2.0))
        o.append(bubble(700, 800, "Мы сами!", t, C["gather"], 2.5))
    if shot == "r_close" and C["mins"][0] <= t < C["mins"][2] + 1.6:
        body = "".join(stext(24 + k * 170, 140, v, 54, fill="#FFC83D", sw=0, shadow=False, anchor="start", op=1 if t >= C["mins"][k] else 0)
                       for k, v in enumerate(("8", "12", "34 мин")))
        o.append(card(250, 120, 580, 200, "Туалет-трекер", body, t, C["mins"][0]))
    if shot == "bed": o.append(zz(560, 820, t, 0) + zz(600, 780, t, 1))
    return "".join(o)


def captions(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            size = 52; gap = 16
            words = [w["disp"] for w in c]
            widths = [tw(w, size) * 1.08 + 28 for w in words]
            total = sum(widths) + gap * (len(words) - 1); x = 540 - total / 2; out = []
            for w, wd, ww in zip(words, c, widths):
                act = wd["t0"] - 0.03 <= t
                out.append(f'<rect x="{x:.0f}" y="1532" width="{ww:.0f}" height="70" rx="8" fill="#3D5468" opacity="{0.92 if act else 0.6}"/>'
                           f'<text x="{x + ww / 2:.0f}" y="1584" font-family="{SERIF}" font-weight="bold" font-size="{size}" fill="#F4F1EA" text-anchor="middle" opacity="{1 if act else 0.6}">{w}</text>')
                x += ww + gap
            return "".join(out)
    return ""


def one(f):
    F = PLAN["frames"][f]; t = F["t"]; shot = F["shot"]
    if shot == "ui_installed": bg = None; base2d = ui_installed(t, VOICE_START[2] - 0.05)
    elif shot == "email": bg = None; base2d = email(t, C["email"] - 0.05, C["email_stop"])
    else:
        src = os.path.join(FR, f"{f:05d}.png")
        if not os.path.exists(src): return f, False
        bg = Image.open(src).convert("RGBA"); base2d = ""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{base.DEFS}'
           f'{base2d}{overlays(f, t, shot)}{captions(t)}{base.WM()}</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=720, output_height=1280))).convert("RGBA")
    im = ov if bg is None else Image.alpha_composite(bg, ov)
    if t > DUR - 0.7: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), min(1, (t - DUR + 0.7) / 0.7))
    im.convert("RGB").save(os.path.join(CO, f"{f:05d}.png"))
    return f, True


if __name__ == "__main__":
    n = len(PLAN["frames"])
    with Pool(os.cpu_count()) as p:
        res = p.map(one, range(n), chunksize=8)
    miss = [f for f, ok in res if not ok]
    print("composed", n - len(miss), "missing", len(miss))
    if miss: sys.exit(1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(CO, "%05d.png"), "-i", os.path.join(proj, "build", "mix.wav"),
                    "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "9M", "-bufsize", "18M",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], check=True)
    print("ready", OUT)
