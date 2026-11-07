"""«Стажёр бесплатно» — blocky dialogue: office guy + Клод the boar. 60 fps render."""
import math, os, sys
from multiprocessing import Pool
import cairosvg
import base
from base import tw, clamp, prog, lerp, e_out, e_in, stext, is_blink, mouth_at, FONT
from kit import e_inout
import medlib
from blocky import guy_head, guy_body, klod, coderoom, cube, Grid
from timeline import *

DEFS = medlib.DEFS.replace("</defs>", '''
<linearGradient id="gSalon" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2A1240"/><stop offset="1" stop-color="#7A2E8E"/></linearGradient>
<linearGradient id="gSalon2" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E0F33"/><stop offset="1" stop-color="#5B2A78"/></linearGradient>
<radialGradient id="gNeon" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FF7AC8" stop-opacity="0.6"/><stop offset="1" stop-color="#FF7AC8" stop-opacity="0"/></radialGradient>
<radialGradient id="gLamp" cx="0.5" cy="0.2" r="0.8"><stop offset="0" stop-color="#FFE7A8" stop-opacity="0.55"/><stop offset="1" stop-color="#FFE7A8" stop-opacity="0"/></radialGradient>
<radialGradient id="gKey" cx="0.5" cy="0.4" r="0.7"><stop offset="0" stop-color="#FFE0F0" stop-opacity="0.25"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
</defs>''')

G_EXPR = {0: "sad", 2: "neutral", 4: "sad", 6: "neutral", 8: "neutral", 10: "neutral", 12: "shock", 14: "happy", 16: "happy", 17: "shock", 19: "smug"}
K_EXPR = {1: "neutral", 3: "neutral", 5: "smug", 7: "neutral", 9: "neutral", 11: "smug", 13: "smug", 15: "neutral", 18: "happy", 20: "happy"}
CAPTION = {}
GRADE = {7: ("2", "#E53935"), 9: ("3−", "#FB8C00"), 13: ("5", "#43A047"), 18: ("5+", "#43A047")}


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


def grade_badge(t, i):
    if i not in GRADE: return ""
    g, col = GRADE[i]; t0 = VOICE_START[i] + 0.05
    p = prog(t, t0, t0 + 0.2)
    if p <= 0: return ""
    sc = lerp(2.4, 1.0, e_out(p))
    return (f'<g opacity="{clamp(p * 3):.2f}" transform="translate(820,700) rotate(-10) scale({sc:.3f})">'
            '<rect x="-115" y="-115" width="230" height="230" fill="#000" opacity="0.35" transform="translate(12,14)"/>'
            f'<rect x="-115" y="-115" width="230" height="230" fill="#FFF8E7" stroke="{col}" stroke-width="16"/>'
            + stext(0, 0, g, 140, fill=col, sw=0, shadow=False) + "</g>")


def guy_close(t, m, expr):
    blink = is_blink(t + 1.3)
    return (coderoom(t, 0) + '<rect width="1080" height="1920" fill="url(#gKey)"/>'
            + guy_body(-60, 1640, 1200, 700) + guy_head(60, 640, 1000, t, m, expr, blink))


def klod_close(t, m, expr, i):
    return (coderoom(t, 1) + '<rect width="1080" height="1920" fill="url(#gKey)"/>'
            + klod(40, 780, 1000, t, mouth=m, expr=expr, blink=is_blink(t), legs=True, glint=0.8) + grade_badge(t, i))


def wide(t, f, i, end=False):
    out = [coderoom(t, 2)]
    speaking_p = SPK[i] == "p" and VOICE_START[i] <= t <= VOICE_END[i] + 0.1
    u = 26; gx, gy = 110, 700
    out.append(cube(gx + 2 * u, gy + 28 * u, 5 * u, 12 * u, 3 * u, "#2B3F7A", -1) + cube(gx + 9 * u, gy + 28 * u, 5 * u, 12 * u, 3 * u, "#2B3F7A", -1))
    out.append(cube(gx - 2 * u, gy + 16 * u, 4 * u, 12 * u, 2 * u, "#F2F2F2", -1) + cube(gx + 14 * u, gy + 16 * u, 4 * u, 12 * u, 2 * u, "#F2F2F2", -1))
    out.append(guy_body(gx + 2 * u, gy + 16 * u, 12 * u, 12 * u))
    out.append(guy_head(gx, gy, 16 * u, t, mouth_at(f) if speaking_p else 0, "happy" if end else "neutral", is_blink(t)))
    speaking_k = SPK[i] == "n" and VOICE_START[i] <= t <= VOICE_END[i] + 0.1
    out.append(klod(600, 1060, 380, t, mouth=mouth_at(f) if speaking_k else 0, expr="happy" if end else "smug", blink=is_blink(t + 0.5), side_dir=-1))
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
    if shot == "girl" or (shot != "nik" and shot != "wide"):
        body = guy_close(t, m, G_EXPR.get(i, "neutral"))
    elif shot == "nik":
        body = klod_close(t, m, K_EXPR.get(i, "neutral"), i)
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
