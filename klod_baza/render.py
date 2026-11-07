"""«Снесла базу» — blocky dialogue: nail-salon girl + Клод the boar. 60 fps render."""
import math, os, sys
from multiprocessing import Pool
import cairosvg
import base
from base import tw, clamp, prog, lerp, e_out, e_in, stext, is_blink, mouth_at, FONT
from kit import e_inout
import medlib
from blocky import girl_head, girl_body, girl_arm, klod, salon, cube
from timeline import *

DEFS = medlib.DEFS.replace("</defs>", '''
<linearGradient id="gSalon" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2A1240"/><stop offset="1" stop-color="#7A2E8E"/></linearGradient>
<linearGradient id="gSalon2" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E0F33"/><stop offset="1" stop-color="#5B2A78"/></linearGradient>
<radialGradient id="gNeon" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FF7AC8" stop-opacity="0.6"/><stop offset="1" stop-color="#FF7AC8" stop-opacity="0"/></radialGradient>
<radialGradient id="gLamp" cx="0.5" cy="0.2" r="0.8"><stop offset="0" stop-color="#FFE7A8" stop-opacity="0.55"/><stop offset="1" stop-color="#FFE7A8" stop-opacity="0"/></radialGradient>
<radialGradient id="gKey" cx="0.5" cy="0.4" r="0.7"><stop offset="0" stop-color="#FFE0F0" stop-opacity="0.25"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
</defs>''')

G_EXPR = {0: "sad", 2: "shock", 4: "smug", 6: "angry", 8: "angry", 10: "plead", 12: "happy", 14: "panic", 16: "shock", 18: "happy", 20: "sweet"}
K_EXPR = {13: "neutral", 15: "smug", 17: "smug", 19: "happy", 21: "happy", 9: "neutral", 7: "smug"}
CAPTION = {3: "Две. «production» и «production-old-НЕ-ТРОГАТЬ».", 11: "Есть папка «backup», кис.", 21: "«production-old-НЕ-ТРОГАТЬ-2»."}


def wrap(txt, size, maxw):
    lines = [""]
    for w in txt.split():
        cand = (lines[-1] + " " + w).strip()
        if tw(cand, size) <= maxw or not lines[-1]: lines[-1] = cand
        else: lines.append(w)
    return lines


def caption(t):
    i = line_at(t)
    if t < VOICE_START[i] - 0.08 or t > VOICE_END[i] + 0.45: return ""
    txt = CAPTION.get(i, base.VOICE_TEXT[i])
    size = 60; lines = wrap(txt, size, 900)
    op = clamp((t - VOICE_START[i] + 0.08) * 10)
    return "".join(stext(540, 400 + k * size * 1.22, ln, size, fill="#fff", stroke="#000", sw=10, shadow=False, op=op).replace(FONT, "Inter Display ExtraBold")
                   for k, ln in enumerate(lines))


def girl_close(t, m, expr, hand):
    blink = is_blink(t + 1.3) and expr not in ("happy",)
    return (salon(t, 0) + '<rect width="1080" height="1920" fill="url(#gKey)"/>'
            + girl_body(-60, 1640, 1200, 700) + girl_head(60, 640, 1000, t, m, expr, blink)
            + (girl_arm(820, 1500, 62, hand) if hand > 0 else ""))


def klod_close(t, m, expr):
    return (salon(t, 1) + '<rect width="1080" height="1920" fill="url(#gKey)"/>'
            + klod(40, 780, 1000, t, mouth=m, expr=expr, blink=is_blink(t), legs=True, glint=0.8))


def wide(t, f, i, end=False):
    out = [salon(t, 0, 0.15), '<rect x="0" y="1380" width="1080" height="540" fill="#3A1F33"/>']
    for k in range(9): out.append(f'<rect x="{k * 130 - 30}" y="1380" width="115" height="540" fill="#4A2942" opacity="0.6"/>')
    # manicure table
    out.append(cube(560, 1240, 440, 50, 120, "#F4E9F7", -1) + cube(600, 1290, 30, 230, 20, "#C9B3D6", -1) + cube(940, 1290, 30, 230, 20, "#C9B3D6", -1))
    out.append(cube(700, 1180, 150, 60, 60, "#FFFFFF", -1))
    speaking_g = SPK[i] == "g" and VOICE_START[i] <= t <= VOICE_END[i] + 0.1
    jump = abs(math.sin((t - VOICE_START[i]) * 9)) * 30 if (i == 14 and not end) else 0
    u = 26
    gx, gy = 120, 760 - jump
    out.append(cube(gx + 2 * u, gy + 16 * u + 12 * u, 5 * u, 12 * u, 3 * u, "#E8E0F0", -1) + cube(gx + 9 * u, gy + 16 * u + 12 * u, 5 * u, 12 * u, 3 * u, "#E8E0F0", -1))
    out.append(girl_body(gx + 2 * u, gy + 16 * u, 12 * u, 12 * u))
    out.append(girl_arm(gx - 2 * u, gy + 16 * u, u * 0.9, 1 if i == 14 and not end else 0) + girl_arm(gx + 14 * u, gy + 16 * u, u * 0.9, 0))
    out.append(girl_head(gx, gy, 16 * u, t, mouth_at(f) if speaking_g else 0, "panic" if (i == 14 and not end) else "happy", is_blink(t)))
    speaking_k = SPK[i] == "n" and VOICE_START[i] <= t <= VOICE_END[i] + 0.1
    out.append(klod(600, 1000, 380, t, mouth=mouth_at(f) if speaking_k else 0, expr="happy" if end else "neutral", blink=is_blink(t + 0.5), side_dir=-1))
    return "".join(out)


def frame_svg(f):
    t = f / FPS
    shot, i = shot_at(t)
    st = VOICE_START[i] - 0.08
    push = 1 + 0.07 * e_inout(clamp((t - st) / 3.2))
    sway = 6 * math.sin(t * 0.9) + 3 * math.sin(t * 2.3)
    speaking = VOICE_START[i] <= t <= VOICE_END[i] + 0.1
    m = mouth_at(f) if speaking else 0.0
    end = t > VOICE_END[-1] + 0.35
    if shot == "girl":
        body = girl_close(t, m, G_EXPR.get(i, "neutral"), prog(t, st, st + 0.4) if i in (10, 12, 18) else 0)
    elif shot == "nik":
        body = klod_close(t, m, K_EXPR.get(i, "neutral"))
    else:
        body = wide(t, f, i, end)
    cam = f'translate({sway:.1f},0) translate(540,1100) scale({push:.4f}) translate(-540,-1100)'
    fade_in = f'<rect width="1080" height="1920" fill="#000" opacity="{1 - clamp(t * 3):.2f}"/>' if t < 0.4 else ""
    fade_out = f'<rect width="1080" height="1920" fill="#000" opacity="{clamp((t - DUR + 0.7) / 0.7):.2f}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}'
            f'<rect width="{W}" height="{H}" fill="#000"/><g transform="{cam}">{body}</g>'
            f'<rect width="{W}" height="{H}" fill="url(#gVig)"/>{caption(t)}{fade_in}{fade_out}{base.WM()}</svg>')


def render(f):
    cairosvg.svg2png(bytestring=frame_svg(f).encode(), write_to=f"build/frames/{f:05d}.png")
    return f


if __name__ == "__main__":
    os.makedirs("build/frames", exist_ok=True)
    frames = [int(x) for x in sys.argv[1:]] or list(range(NFRAMES))
    with Pool(os.cpu_count()) as pool:
        for i, _ in enumerate(pool.imap_unordered(render, frames, chunksize=4)):
            if i % 500 == 0: print("frame", i, flush=True)
    print("done", len(frames))
