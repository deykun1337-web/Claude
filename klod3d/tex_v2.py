"""High-res expressive faces (256 px) for Ruslan v2 and Klod: brows, eyelids, gaze, 5 mouth visemes.
Names: v2r_<expr>_<vis>_<blink>_<gaze>.png and v2k_<expr>_<vis>_<blink>_<gaze>.png
  expr  : neutral happy smug shock sad angry think panic
  vis   : 0 closed · 1 E/И (wide-narrow) · 2 A (open) · 3 O/У (round) · 4 M/Б/П (pressed)
  blink : 0 open · 1 closed
  gaze  : l c r (look left / centre / right)
Run: python3 klod3d/tex_v2.py  (≈480 files, ~20 s)"""
import os
from PIL import Image, ImageDraw, ImageFilter
from tex import OUT

S = 256
EXPRS = ["neutral", "happy", "smug", "shock", "sad", "angry", "think", "panic"]
GAZE = {"l": -1, "c": 0, "r": 1}


def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def brows(d, expr, y, xs, col, w=46, th=11):
    # (left_inner_dy, left_outer_dy) per expression; right is mirrored
    tilt = {"angry": (14, -6), "sad": (-12, 6), "shock": (-14, -14), "panic": (-10, -16), "think": (6, -10), "smug": (0, -6), "happy": (-6, -6)}.get(expr, (0, 0))
    for side, x in zip((-1, 1), xs):
        inner, outer = tilt if side == -1 else (tilt[0], tilt[1])
        x0, x1 = (x - w // 2, x + w // 2)
        yi, yo = y + inner, y + outer
        pts = [(x0, yo if side == -1 else yi), (x1, yi if side == -1 else yo)]
        if expr == "think" and side == 1: pts = [(x0, y - 14), (x1, y - 4)]
        d.line(pts, fill=col, width=th)


def eye(d, cx, cy, gaze, blink, expr, white=(250, 248, 244), iris=(92, 58, 34), lid=None, rw=26, rh=22):
    if blink or expr == "happy":
        if expr == "happy" and not blink:  # smiling eyes ^ ^
            d.arc([cx - rw, cy - rh + 6, cx + rw, cy + rh + 6], 200, 340, fill=(40, 26, 20), width=7)
        else:
            d.line([cx - rw, cy + 2, cx + rw, cy + 2], fill=(40, 26, 20), width=7)
        return
    big = 1.25 if expr in ("shock", "panic") else 1.0
    d.ellipse([cx - rw * big, cy - rh * big, cx + rw * big, cy + rh * big], fill=white)
    gx = cx + gaze * rw * 0.45
    ir = 15 * (0.85 if expr in ("shock", "panic") else 1)
    d.ellipse([gx - ir, cy - ir, gx + ir, cy + ir], fill=iris)
    d.ellipse([gx - ir * 0.5, cy - ir * 0.5, gx + ir * 0.5, cy + ir * 0.5], fill=(18, 12, 10))
    d.ellipse([gx + ir * 0.15, cy - ir * 0.7, gx + ir * 0.6, cy - ir * 0.25], fill=(255, 255, 255))
    if expr in ("smug", "angry") and lid:  # heavy upper lid
        d.rectangle([cx - rw - 2, cy - rh - 2, cx + rw + 2, cy - rh * 0.15], fill=lid)
    if expr == "sad" and lid:
        d.polygon([(cx - rw, cy - rh), (cx + rw, cy - rh), (cx + rw, cy - rh * 0.6), (cx - rw, cy - rh * 0.2)], fill=lid)


def mouth(d, cx, cy, vis, expr, dark=(70, 20, 20), lip=(150, 70, 60), tongue=(232, 106, 122), teeth=(250, 246, 240), w=52):
    if vis == 0:
        if expr in ("happy", "smug"):
            d.arc([cx - w, cy - 34, cx + w, cy + 14], 20, 160, fill=dark, width=8)
        elif expr in ("sad",):
            d.arc([cx - w * 0.8, cy, cx + w * 0.8, cy + 40], 200, 340, fill=dark, width=8)
        elif expr in ("shock", "panic"):
            d.ellipse([cx - 14, cy - 12, cx + 14, cy + 16], fill=dark)
        else:
            d.line([cx - w * 0.7, cy, cx + w * 0.7, cy], fill=dark, width=8)
        return
    if vis == 4:
        d.line([cx - w * 0.6, cy, cx + w * 0.6, cy], fill=lip, width=12); return
    box = {1: (w * 0.95, 13), 2: (w * 0.75, 30), 3: (w * 0.4, 26)}[vis]
    bx, by = box
    d.ellipse([cx - bx, cy - by, cx + bx, cy + by], fill=dark)
    if vis in (1, 2): d.rectangle([cx - bx * 0.7, cy - by, cx + bx * 0.7, cy - by + max(5, by * 0.35)], fill=teeth)
    if vis == 2: d.ellipse([cx - bx * 0.55, cy + by * 0.1, cx + bx * 0.55, cy + by * 0.95], fill=tongue)


def ruslan(expr, vis, blink, gz):
    skin, skin2 = rgb("#EBC3A5"), rgb("#D9A98A")
    im = Image.new("RGB", (S, S), skin); d = ImageDraw.Draw(im)
    d.ellipse([-40, 150, 296, 330], fill=tuple(int(c * 0.96) for c in skin))            # soft lower shading
    d.rectangle([0, 0, S, 58], fill=rgb("#F0569A")); d.rectangle([0, 58, S, 70], fill=rgb("#B8336E"))  # cap band + brim shadow
    d.rectangle([66, 18, 190, 34], fill=(255, 255, 255))                                  # DEYKUN print band
    d.rectangle([0, 70, 14, 118], fill=rgb("#4A3224")); d.rectangle([242, 70, 256, 118], fill=rgb("#4A3224"))  # hair
    brows(d, expr, 92, (78, 178), rgb("#4A3224"))
    for x in (78, 178): eye(d, x, 122, GAZE[gz], blink, expr, lid=skin2)
    for x in (52, 204): d.ellipse([x - 20, 150, x + 20, 170], fill=(242, 169, 160))      # blush
    for k in range(26):                                                                    # light stubble
        x = 80 + (k * 37) % 96; y = 200 + (k * 13) % 40
        d.ellipse([x, y, x + 3, y + 3], fill=rgb("#CFA184"))
    mouth(d, 128, 196, vis, expr)
    return im


def klod(expr, vis, blink, gz):
    body, dark = rgb("#E5684B"), rgb("#B84A33")
    im = Image.new("RGB", (S, S), body); d = ImageDraw.Draw(im)
    for k in range(60):                                                                    # clay-ish speckle
        x = (k * 53) % S; y = (k * 97) % S; d.ellipse([x, y, x + 4, y + 4], fill=tuple(min(255, c + 10) for c in body))
    # Claude sparkle on the forehead
    import math
    for k in range(8):
        a = k * math.pi / 4
        d.line([128 + 8 * math.cos(a), 34 + 8 * math.sin(a), 128 + 24 * math.cos(a), 34 + 24 * math.sin(a)], fill=rgb("#FFE9D6"), width=9)
    brows(d, expr, 72, (70, 186), rgb("#5A2418"), w=42, th=10)
    for x in (70, 186):
        if blink or expr == "happy":
            eye(d, x, 104, 0, blink, expr)
        else:
            big = 1.3 if expr in ("shock", "panic") else 1.0
            gx = x + GAZE[gz] * 9
            d.rounded_rectangle([gx - 16 * big, 104 - 22 * big, gx + 16 * big, 104 + 22 * big], 9, fill=(17, 17, 17))
            d.ellipse([gx + 2, 88, gx + 11, 97], fill=(255, 255, 255))
            if expr in ("smug", "angry"): d.rectangle([x - 22, 78, x + 22, 92], fill=body)
            if expr == "sad": d.polygon([(x - 22, 80), (x + 22, 80), (x + 22, 86), (x - 22, 98)], fill=body)
    mouth(d, 128, 214, vis, expr, dark=(58, 15, 10), lip=dark, w=46)
    return im


if __name__ == "__main__":
    n = 0
    for e in EXPRS:
        for v in range(5):
            for b in (0, 1):
                for g in GAZE:
                    ruslan(e, v, b, g).save(os.path.join(OUT, f"v2r_{e}_{v}_{b}_{g}.png"))
                    klod(e, v, b, g).save(os.path.join(OUT, f"v2k_{e}_{v}_{b}_{g}.png")); n += 2
    print("faces", n)
