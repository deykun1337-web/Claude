"""Shared overlay kit for compose_*.py (SVG strings, 1080x1920 canvas).

calm_captions(t, chunks)   — DEFAULT subtitles: white Inter SemiBold, 46 px, ≤ 2 short lines, soft shadow, no outline,
                             upper third (y≈470) so they never sit on faces/mouths (style of @manohin_nocode).
                             `chunks` = base.chunks(); pass cold_until=<s> to keep the first seconds clean (cold open).
endcard(t, t0, next_ep, word, what, question) — final screen: «В следующей серии: …», big KEYWORD plate, question to comments.
chip(cx, cy, txt, size, sc, bg, fg, rot)      — white/colour plate with drop shadow.
DEFS                                          — put once into <svg> (shadow filters).
"""
import math
from html import escape
from PIL import ImageFont

FONT_FILE = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
BOLD_FILE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
_f = {}
DEFS = ('<defs><filter id="ksh" x="-20%" y="-60%" width="140%" height="220%"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000" flood-opacity="0.75"/></filter>'
        '<filter id="kpl" x="-20%" y="-40%" width="140%" height="180%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity="0.4"/></filter></defs>')


def tw(text, size, file=FONT_FILE):
    k = (file, size)
    if k not in _f: _f[k] = ImageFont.truetype(file, size)
    return _f[k].getlength(text)


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))


def _wrap(words, size, maxw=900):
    lines, cur = [], ""
    for w in words:
        nxt = (cur + " " + w).strip()
        if tw(nxt, size) > maxw and cur: lines.append(cur); cur = w
        else: cur = nxt
    return lines + ([cur] if cur else [])


def calm_captions(t, chunks, y=470, size=46, cold_until=0.0):
    if t < cold_until: return ""
    for t0, t1, c in chunks:
        if t0 <= t < t1:
            lines = _wrap([w["disp"] for w in c], size)[:2]
            a = clamp((t - t0) / 0.08) * clamp((t1 - t) / 0.08)
            out = []
            for k, ln in enumerate(lines):
                yy = y + (k - (len(lines) - 1) / 2) * size * 1.25
                out.append(f'<text x="540" y="{yy:.0f}" text-anchor="middle" dominant-baseline="middle" font-family="Inter" font-weight="600" '
                           f'font-size="{size}" fill="#FFFFFF" filter="url(#ksh)">{escape(ln)}</text>')
            return f'<g opacity="{a:.2f}">' + "".join(out) + "</g>"
    return ""


def chip(cx, cy, txt, size, sc=1.0, bg="#FFFFFF", fg="#14161C", rot=0, bold=True):
    if sc <= 0.001: return ""
    f = BOLD_FILE if bold else FONT_FILE
    w = tw(txt, size, f) + size * 1.1; h = size * 1.6
    fam = 'font-family="Inter Display" font-weight="900"' if bold else 'font-family="Inter" font-weight="600"'
    return (f'<g filter="url(#kpl)" transform="translate({cx:.1f},{cy:.1f}) rotate({rot}) scale({sc:.3f})">'
            f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h * 0.28:.1f}" fill="{bg}"/>'
            f'<text x="0" y="0" text-anchor="middle" dominant-baseline="central" {fam} font-size="{size}" fill="{fg}">{escape(txt)}</text></g>')


def pop(t, t0, d=0.35):
    if t < t0: return 0.0
    p = clamp((t - t0) / d) - 1
    return 1 + p * p * (2.9 * p + 1.9)


def endcard(t, t0, next_ep, word, what, question, accent="#F0569A"):
    """Last ~3 s: next episode teaser (series), keyword plate (mandatory CTA), question that starts comments."""
    if t < t0: return ""
    o = [f'<rect width="1080" height="1920" fill="#000" opacity="{0.45 * clamp((t - t0) / 0.3):.2f}"/>']
    if next_ep: o.append(chip(540, 520, f"В следующей серии: {next_ep}", 40, pop(t, t0), bg="#FFFFFF", fg="#14161C"))
    sc = pop(t, t0 + 0.25)
    if sc > 0:
        o.append(f'<g filter="url(#kpl)" transform="translate(540,860) scale({sc:.3f})"><rect x="-400" y="-150" width="800" height="300" rx="44" fill="{accent}"/>'
                 f'<text x="0" y="-78" text-anchor="middle" dominant-baseline="central" font-family="Inter" font-weight="600" font-size="40" fill="#FFFFFF">Напиши в комментариях</text>'
                 f'<text x="0" y="18" text-anchor="middle" dominant-baseline="central" font-family="Inter Display" font-weight="900" font-size="128" fill="#FFFFFF">{escape(word)}</text>'
                 f'<text x="0" y="104" text-anchor="middle" dominant-baseline="central" font-family="Inter" font-weight="600" font-size="32" fill="#FFE6F2">{escape(what)}</text></g>')
    if question: o.append(chip(540, 1180, question, 42, pop(t, t0 + 0.6), bg="#14161C", fg="#FFFFFF", bold=False))
    return "".join(o)
