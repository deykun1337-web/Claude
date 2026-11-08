"""«Майкл из Техаса» — 2D cartoon short: Руслан Дейкун Кабанович + Клод the boar. 30 fps."""
import math, os, random, re, sys
from multiprocessing import Pool
import cairosvg
import base
from base import tw, fit, clamp, prog, lerp, e_out, e_in, e_back, popscale, stext, star4, mouth_at, FONT
from kit import e_inout
from chars import ruslan, mom, klod
from timeline import *

FPS30 = 30
NF = int(DUR * FPS30)
YEL, RED, GRN, OUTL = "#FFC83D", "#FF4040", "#3DDC84", "#16100F"
S = [s - 0.05 for s in VOICE_START]; E = VOICE_END
MONO = "JetBrains Mono ExtraBold"

DEFS = base.DEFS.replace("</defs>", '''
<linearGradient id="gPuff" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#D3D7DE"/><stop offset="0.5" stop-color="#8E939C"/><stop offset="1" stop-color="#5E636C"/></linearGradient>
<linearGradient id="gRoom" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B2224"/><stop offset="1" stop-color="#0D1012"/></linearGradient>
<radialGradient id="gLampR" cx="0.5" cy="0.35" r="0.7"><stop offset="0" stop-color="#FFD9A0" stop-opacity="0.28"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<radialGradient id="gDark2" cx="0.5" cy="0.45" r="0.75"><stop offset="0.45" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.8"/></radialGradient>
<linearGradient id="gMax" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE29A"/><stop offset="1" stop-color="#E8A23A"/></linearGradient>
<linearGradient id="gPaper" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4EAD8"/><stop offset="1" stop-color="#E2D3B8"/></linearGradient>
<radialGradient id="gRedRoom" cx="0.5" cy="0.5" r="0.75"><stop offset="0" stop-color="#5A1210"/><stop offset="1" stop-color="#1A0505"/></radialGradient>
</defs>''')


def wt(line, prefix):
    for w in WORDS:
        if w["line"] == line and re.sub(r"[^\w-]", "", w["w"]).lower().startswith(prefix): return w["t0"]
    return VOICE_START[line]


# ------------------------------------------------------------------ shot cues
CUES = [(0, "ui_verify"), (wt(0, "макс") - 0.05, "ui_max"), (S[1], "klod"), (S[2], "passport"), (S[3], "city"),
        (S[4], "close"), (wt(5, "майкл") - 0.05, "passport2"), (S[6], "room"), (S[7], "room_hat"), (S[8], "scan"),
        (S[9], "detect"), (S[10], "flag"), (S[11], "close_hat"), (S[13], "room_mom"), (S[14], "close_hat"), (S[15], "mom"),
        (S[16], "ui_ok"), (S[17], "party"), (S[18], "ui_block"), (S[19], "susp"), (S[20], "room_red"), (S[21], "susp"),
        (S[22], "bank"), (S[23], "susp"), (S[24], "klod_red"), (E[24] + 0.45, "end")]


def cue_at(t):
    c, t0 = CUES[0][1], 0
    for ts, name in CUES:
        if t >= ts: c, t0 = name, ts
    return c, t0


def line_now(t):
    i = 0
    for k, s in enumerate(VOICE_START):
        if t >= s - 0.05: i = k
    return i


def talking(t, spk):
    i = line_now(t)
    return SPK[i] == spk and VOICE_START[i] <= t <= VOICE_END[i] + 0.08


def mth(t, spk):
    return mouth_at(int(t * 60)) if talking(t, spk) else 0.0


def blink(t, off=0.0):
    return ((t + off) % 3.3) < 0.12


R_EXPR = {0: "neutral", 2: "shock", 4: "sad", 5: "sad", 7: "smug", 10: "angry", 11: "neutral", 12: "panic", 14: "angry", 17: "happy",
          19: "panic", 20: "cry", 21: "shock", 22: "sad", 23: "cry", 24: "cry"}


def rexpr(t):
    i = line_now(t)
    return R_EXPR.get(i, "neutral")


# ------------------------------------------------------------------ backgrounds
def carpet(x, y, w, h):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#7A1E22" stroke="#C9A04A" stroke-width="14"/>']
    for k in range(3):
        cy = y + h * (k + 0.5) / 3; r = min(w, h / 3) * 0.36
        for rr, col in ((r, "#1F3B6B"), (r * 0.72, "#C9A04A"), (r * 0.45, "#7A1E22"), (r * 0.2, "#E8D7B0")):
            o.append(f'<polygon points="{x + w / 2},{cy - rr} {x + w / 2 + rr * 1.3},{cy} {x + w / 2},{cy + rr} {x + w / 2 - rr * 1.3},{cy}" fill="{col}"/>')
    for k in range(0, int(w), 40): o.append(f'<rect x="{x + k + 10}" y="{y + 10}" width="14" height="14" fill="#C9A04A" opacity="0.7" transform="rotate(45 {x + k + 17} {y + 17})"/>')
    return "".join(o)


def usflag(x, y, w, h, p=1.0):
    if p <= 0: return ""
    o = [f'<g opacity="{p:.2f}">']
    for k in range(13): o.append(f'<rect x="{x}" y="{y + k * h / 13:.1f}" width="{w}" height="{h / 13 + 0.5:.1f}" fill="{"#B22234" if k % 2 == 0 else "#F2EFE8"}"/>')
    o.append(f'<rect x="{x}" y="{y}" width="{w * 0.42:.1f}" height="{h * 7 / 13:.1f}" fill="#3C3B6E"/>')
    for r in range(5):
        for c in range(6): o.append(f'<circle cx="{x + 20 + c * w * 0.42 / 6.3:.1f}" cy="{y + 22 + r * h * 7 / 13 / 5.4:.1f}" r="5" fill="#fff"/>')
    o.append("</g>")
    return "".join(o)


def room(t, flag=0.0, red=False, show_klod=True):
    o = ['<rect width="1080" height="1920" fill="url(#gRoom)"/>',
         '<rect x="0" y="0" width="1080" height="1250" fill="#22302E" opacity="0.6"/>',
         carpet(120, 260, 620, 860), usflag(120, 260, 620, 860, flag),
         '<rect x="820" y="300" width="200" height="360" fill="#2C3A38" stroke="#0E1414" stroke-width="8"/><text x="920" y="520" font-family="Inter Display Black" font-size="110" fill="#E8E2D2" text-anchor="middle" opacity="0.8">66</text>',
         '<rect x="0" y="1250" width="1080" height="670" fill="#140F0E"/>',
         # desk with laptop and Клод
         '<rect x="620" y="1280" width="460" height="40" fill="#3A2A22" stroke="#0E0A08" stroke-width="6"/><rect x="650" y="1320" width="30" height="300" fill="#2A1E18"/>',
         '<path d="M 880 1280 L 1050 1280 L 1030 1180 L 900 1180 Z" fill="#2A2F36" stroke="#0E0A08" stroke-width="5"/><rect x="905" y="1188" width="120" height="84" fill="#FF3B30" opacity="0.85"/>']
    if show_klod: o.append(klod(t, 690, 1120, 170, mouth=mth(t, "n"), blink=blink(t, 0.4)))
    o.append('<rect width="1080" height="1920" fill="url(#gLampR)"/>')
    if red: o.append('<rect width="1080" height="1920" fill="#C21010" opacity="0.32"/>')
    return "".join(o)


def city(t):
    rr = random.Random(4); o = ['<rect width="1080" height="1920" fill="#0A0D1A"/>', '<circle cx="230" cy="260" r="70" fill="#E8E2C8"/>']
    for c in range(6):
        for r in range(12):
            x = 120 + c * 150; y = 420 + r * 120
            lit = rr.random() < 0.18
            col = "#E8B740" if lit else "#151A2A"
            if c == 3 and r == 3: col = "#E8302A"
            o.append(f'<rect x="{x}" y="{y}" width="110" height="80" fill="{col}" opacity="{0.9 if lit else 1}"/>')
    return "".join(o)


# ------------------------------------------------------------------ UI cards
def card(cx, cy, w, h, inner, sc=1.0):
    return (f'<g transform="translate({cx},{cy}) scale({sc:.3f})"><rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="34" fill="#16191F" stroke="#2C313B" stroke-width="4"/>{inner}</g>')


def ui_verify(t, t0):
    sc = 0.9 + 0.1 * e_out(prog(t, t0, t0 + 0.4))
    inner = ('<path d="M 0 -250 L 70 -220 L 70 -150 Q 70 -100 0 -70 Q -70 -100 -70 -150 L -70 -220 Z" fill="none" stroke="#FF3B30" stroke-width="10"/>'
             + stext(0, -160, "!", 70, fill="#FF3B30", sw=0, shadow=False)
             + stext(0, -10, "Подтвердите", 64, fill="#fff", sw=0, shadow=False) + stext(0, 70, "личность", 64, fill="#fff", sw=0, shadow=False)
             + stext(0, 150, "Нужен паспорт и селфи.", 32, fill="#9AA3B2", sw=0, shadow=False)
             + stext(0, 195, "Иначе доступ будет закрыт.", 32, fill="#9AA3B2", sw=0, shadow=False)
             + '<rect x="-260" y="250" width="520" height="90" rx="20" fill="#E5322D"/>' + stext(0, 295, "Загрузить паспорт", 40, fill="#fff", sw=0, shadow=False))
    return '<rect width="1080" height="1920" fill="#0B0D11"/>' + card(540, 860, 760, 760, inner, sc)


def ui_max(t, t0):
    sc = e_back(prog(t, t0, t0 + 0.4))
    return ('<rect width="1080" height="1920" fill="#0B0D11"/>' + f'<g transform="translate(540,860) scale({max(sc, 0.01):.3f})">'
            + stext(0, -260, "ВАШ ТАРИФ", 44, fill="#C9B07A", sw=0, shadow=False)
            + stext(0, -80, "Max", 260, fill="url(#gMax)", sw=0, shadow=False) + stext(0, 140, "20 000 ₽", 110, fill="#fff", sw=0, shadow=False)
            + stext(0, 240, "в месяц", 40, fill="#9AA3B2", sw=0, shadow=False) + "</g>")


def passport(t, t0, edited=False):
    p = e_out(prog(t, t0, t0 + 0.5))
    rows = [("Фамилия", "Дейкун"), ("Имя", "Руслан"), ("Отчество", "Кабанович"), ("Дата рождения", "когда-то"),
            ("Место рождения", "дер. Кабаново"), ("", "Российская Федерация")]
    o = ['<rect width="1080" height="1920" fill="#120F0D"/>', f'<g transform="translate(540,{lerp(1300, 900, p):.0f}) rotate({lerp(8, -3, p):.1f}) scale(1.05)">',
         '<rect x="-430" y="-520" width="860" height="1040" rx="16" fill="#000" opacity="0.45" transform="translate(18,22)"/>',
         '<rect x="-430" y="-520" width="860" height="1040" rx="16" fill="url(#gPaper)" stroke="#8A7A5A" stroke-width="5"/>',
         stext(0, -460, "ПАСПОРТ · ВЫДАН В ОБЩАГЕ", 34, fill="#8A6A4A", sw=0, shadow=False),
         '<rect x="-390" y="-400" width="300" height="380" fill="#D8CBB0" stroke="#8A7A5A" stroke-width="4"/>',
         f'<g transform="translate(-240,-220) scale(0.42)">{ruslan(t, 0, -80, 1.0, 0, "neutral", False)}</g>'.replace('<g transform="translate(0.0,-80.0)', '<g transform="translate(0,-80)'),
         '<rect x="-390" y="-400" width="300" height="380" fill="none" stroke="#8A7A5A" stroke-width="4"/>']
    for k, (lab, val) in enumerate(rows):
        y = -360 + k * 125 if k < 4 else 160 + (k - 4) * 130
        x = -50 if k < 4 else -390
        if lab: o.append(stext(x, y - 30, lab, 26, fill="#9A8A6A", sw=0, shadow=False, anchor="start"))
        o.append(stext(x, y + 12, val, 46 if k < 5 else 40, fill="#2A2018", sw=0, shadow=False, anchor="start"))
        if edited and k in (1, 4):
            pk = prog(t, t0 + 0.2 + 0.3 * (k == 4), t0 + 0.5 + 0.3 * (k == 4))
            wv = tw(val, 46)
            o.append(f'<line x1="{x}" y1="{y + 12}" x2="{x + wv * pk:.0f}" y2="{y + 6}" stroke="#2D5BD1" stroke-width="9" stroke-linecap="round"/>')
            if pk >= 1:
                o.append(f'<text x="{x + wv + 20}" y="{y + 30}" font-family="DejaVu Sans" font-style="italic" font-weight="bold" font-size="58" fill="#2D5BD1" transform="rotate(-6 {x + wv} {y})">{"Майкл" if k == 1 else "Техас"}</text>')
    o.append('<circle cx="250" cy="330" r="120" fill="none" stroke="#6A5ACD" stroke-width="8" opacity="0.5"/>' + stext(250, 330, "ОБЩЕЖИТИЕ", 30, fill="#6A5ACD", sw=0, shadow=False, rot=-15, op=0.6))
    o.append("</g>")
    return "".join(o)


def ui_ok(t, t0):
    p = e_back(prog(t, t0, t0 + 0.4))
    return ('<rect width="1080" height="1920" fill="#06140D"/><circle cx="540" cy="820" r="420" fill="#1E7A4A" opacity="0.18"/>'
            + f'<g transform="translate(540,780) scale({max(p, 0.01):.3f})"><circle r="170" fill="none" stroke="{GRN}" stroke-width="18"/>'
            + f'<path d="M -80 0 L -20 60 L 90 -60" stroke="{GRN}" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'
            + stext(540, 1080, "Личность подтверждена", 54, fill="#fff", sw=0, shadow=False)
            + stext(540, 1150, "Майкл Кабанович, штат Техас", 36, fill="#8FCFAA", sw=0, shadow=False))


def ui_block(t, t0):
    p = e_back(prog(t, t0, t0 + 0.4))
    fp = "".join(f'<path d="M {-60 + k * 6} {40 - k * 4} Q 0 {-80 + k * 10} {60 - k * 6} {40 - k * 4}" stroke="#FF3B30" stroke-width="8" fill="none"/>' for k in range(7))
    return ('<rect width="1080" height="1920" fill="#140606"/>' + f'<g transform="translate(540,760) scale({max(p, 0.01) * 1.6:.3f})">{fp}</g>'
            + stext(540, 1000, "Аккаунт", 70, fill="#fff", sw=0, shadow=False) + stext(540, 1085, "заблокирован", 70, fill="#fff", sw=0, shadow=False))


def bank(t, t0):
    p = e_out(prog(t, t0, t0 + 0.4))
    inner = ('<rect x="-380" y="-130" width="60" height="60" rx="14" fill="#2C313B"/>' + stext(-300, -100, "Мой банк · вчера, 23:59", 32, fill="#9AA3B2", sw=0, shadow=False, anchor="start")
             + stext(-380, -10, "−20 000 ₽", 110, fill="#FF4D4D", sw=0, shadow=False, anchor="start")
             + stext(-380, 80, "Подписка Max", 40, fill="#fff", sw=0, shadow=False, anchor="start")
             + stext(-380, 135, "Списание: Майкл К.", 32, fill="#9AA3B2", sw=0, shadow=False, anchor="start"))
    return '<rect width="1080" height="1920" fill="#0B0D11"/>' + f'<g transform="translate(0,{(1 - p) * 300:.0f})">' + card(540, 820, 860, 380, inner) + "</g>"


# ------------------------------------------------------------------ HUD
SUSP_KEYS = [(S[6], 12), (S[7], 28), (S[8], 41), (S[9], 58), (S[10], 64), (S[12], 80), (S[13], 99), (S[16], 0)]


def susp_val(t):
    v = 0
    for k, (ts, val) in enumerate(SUSP_KEYS):
        if t >= ts:
            prev = SUSP_KEYS[k - 1][1] if k else 0
            v = lerp(prev, val, e_out(prog(t, ts, ts + 0.5)))
    return int(round(v))


def hud(t):
    if not (S[6] <= t < S[18]): return ""
    v = susp_val(t); col = GRN if v < 40 else (YEL if v < 80 else RED)
    return ('<g transform="translate(150,110)"><rect width="560" height="120" rx="14" fill="#0E1116" opacity="0.88" stroke="#2C313B" stroke-width="3"/>'
            '<circle cx="28" cy="24" r="7" fill="#FF5F57"/><circle cx="50" cy="24" r="7" fill="#FEBC2E"/><circle cx="72" cy="24" r="7" fill="#28C840"/>'
            + stext(24, 66, "$ подозрительность", 30, fill="#C9D1DC", sw=0, shadow=False, anchor="start").replace(FONT, MONO)
            + stext(400, 66, f"{v}%", 44, fill=col, sw=0, shadow=False, anchor="start").replace(FONT, MONO)
            + f'<rect x="24" y="92" width="512" height="10" rx="5" fill="#252A33"/><rect x="24" y="92" width="{512 * v / 100:.0f}" height="10" rx="5" fill="{col}"/></g>')


def brackets(col="#E8EEF6"):
    o = []
    for x, y, dx, dy in ((70, 300, 1, 1), (1010, 300, -1, 1), (70, 1700, 1, -1), (1010, 1700, -1, -1)):
        o.append(f'<path d="M {x} {y + dy * 60} L {x} {y} L {x + dx * 60} {y}" stroke="{col}" stroke-width="6" fill="none"/>')
    return "".join(o)


def box(x, y, w, h, label, col):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{col}" stroke-width="6"/>'
            f'<rect x="{x}" y="{y - 44}" width="{tw(label, 28) + 30:.0f}" height="40" fill="{col}"/>'
            + stext(x + 15, y - 24, label, 28, fill="#0B0D11", sw=0, shadow=False, anchor="start"))


# ------------------------------------------------------------------ scenes
def close(t, t0, hat="cap", red=False, extra=""):
    zoom = 1 + 0.05 * prog(t, t0, t0 + 3)
    look = (0.6 * math.sin(t * 0.7), 0) if not talking(t, "p") else (0, 0)
    ex = rexpr(t)
    o = [room(t, flag=1.0 if t > S[10] else 0.0, show_klod=False), '<rect width="1080" height="1920" fill="#000" opacity="0.35"/>',
         f'<g transform="translate(540,1100) scale({zoom:.4f}) translate(-540,-1100)">',
         ruslan(t, 540, 860, 1.05, mth(t, "p"), ex, blink(t), look, hat, tilt=3 * math.sin(t * 1.3), tears=1.0 if ex == "cry" else 0), "</g>"]
    if red: o.append('<rect width="1080" height="1920" fill="#C21010" opacity="0.35"/>')
    o.append(extra)
    return "".join(o)


def lower_third(t, t0):
    p = e_out(prog(t, t0 + 0.2, t0 + 0.6)); q = 1 - e_in(prog(t, t0 + 3.0, t0 + 3.4))
    if p <= 0 or q <= 0: return ""
    x = lerp(-900, 60, p) - (1 - q) * 900
    return (f'<g transform="translate({x:.0f},1250)"><rect width="760" height="150" rx="20" fill="#0E1116" opacity="0.9"/><rect width="16" height="150" fill="{YEL}"/>'
            + stext(40, 52, "РУСЛАН ДЕЙКУН", 52, fill="#fff", sw=0, shadow=False, anchor="start")
            + stext(40, 112, "КАБАНОВИЧ", 52, fill=YEL, sw=0, shadow=False, anchor="start") + "</g>")


def medium(t, hat="cap", arms_up=0.0, flag=0.0, red=False, x=430, mom_in=0.0):
    o = [room(t, flag=flag, red=False)]
    if mom_in > 0:
        o.append(f'<g opacity="{mom_in:.2f}">' + '<rect x="0" y="380" width="120" height="900" fill="#3A2A20"/>' + mom(t, 60, 760, 0.42, mth(t, "g")) + "</g>")
    o.append(ruslan(t, x, 820, 0.62, mth(t, "p"), "happy" if arms_up > 0.5 else rexpr(t), blink(t), (0.5, 0), hat, arms_up=arms_up))
    if red: o.append('<rect width="1080" height="1920" fill="#C21010" opacity="0.32"/>')
    return "".join(o)


def stamp(t, t0, text="SUSPENDED"):
    p = prog(t, t0, t0 + 0.18)
    if p <= 0: return ""
    sc = lerp(3, 1, e_out(p))
    return (f'<g opacity="{clamp(p * 3):.2f}" transform="translate(540,640) rotate(-12) scale({sc:.3f})">'
            f'<rect x="-330" y="-70" width="660" height="140" rx="12" fill="none" stroke="{RED}" stroke-width="12"/>'
            + stext(0, 0, text, 96, fill=RED, sw=0, shadow=False) + "</g>")


def scene(t):
    c, t0 = cue_at(t)
    if c == "ui_verify": return ui_verify(t, t0)
    if c == "ui_max": return ui_max(t, t0)
    if c in ("klod", "klod_red"):
        red = c == "klod_red"
        z = 1 + 0.06 * prog(t, t0, t0 + 3)
        return (f'<rect width="1080" height="1920" fill="{"url(#gRedRoom)" if red else "#141010"}"/>'
                + f'<g transform="translate(540,1000) scale({z:.4f}) translate(-540,-1000)">'
                + '<rect x="0" y="1260" width="1080" height="660" fill="#2A1A14"/><rect x="0" y="1250" width="1080" height="30" fill="#3A2A22"/>'
                + klod(t, 160, 700, 760, mouth=mth(t, "n"), expr="smug" if red else "neutral", blink=blink(t, 0.4)) + "</g>"
                + ('<rect width="1080" height="1920" fill="#C21010" opacity="0.25"/>' if red else ""))
    if c == "passport": return passport(t, t0)
    if c == "passport2": return passport(t, t0, edited=True)
    if c == "city": return city(t)
    if c == "close": return close(t, t0, extra=lower_third(t, S[4]))
    if c == "room": return medium(t)
    if c == "room_hat": return medium(t, hat="cowboy")
    if c == "scan":
        rot = 10 * math.sin((t - t0) * 2.2)
        scan = (brackets() + '<ellipse cx="540" cy="860" rx="330" ry="470" fill="none" stroke="#3DDC84" stroke-width="5" stroke-dasharray="14 12" opacity="0.8"/>'
                + box(330, 620, 420, 480, "ЛИЦО: МАЙКЛ? 41%", GRN)
                + '<rect x="330" y="1390" width="420" height="64" rx="32" fill="#0E1116" opacity="0.85"/>' + stext(540, 1422, "Поверните голову", 34, fill="#fff", sw=0, shadow=False))
        return close(t, t0, hat="cowboy").replace('<g transform="translate(540,1100)', f'<g transform="rotate({rot:.2f} 540 1300) translate(540,1100)', 1) + scan
    if c == "detect":
        return medium(t, hat="cowboy") + brackets() + box(120, 260, 620, 860, "ОБЪЕКТ: КОВЁР 99%", RED)
    if c == "flag":
        p = e_out(prog(t, t0, t0 + 0.25))
        return (medium(t, hat="cowboy", arms_up=1.0, flag=p) + stext(250, 230, "БАМ!", 120, fill="#fff", sc=popscale(t, t0, 0.25), rot=-10))
    if c == "close_hat": return close(t, t0, hat="cowboy")
    if c == "room_mom":
        return medium(t, hat="cowboy", flag=1.0, mom_in=e_out(prog(t, t0, t0 + 0.3))) + box(10, 520, 200, 560, "ВТОРОЙ ЧЕЛОВЕК", RED)
    if c == "mom":
        return (room(t, flag=1.0, show_klod=False) + '<rect width="1080" height="1920" fill="#000" opacity="0.3"/>'
                + mom(t, 540, 860, 1.1, mth(t, "g"), blink=blink(t, 1.1)))
    if c == "ui_ok": return ui_ok(t, t0)
    if c == "party":
        return medium(t, hat="cowboy", arms_up=e_back(prog(t, t0, t0 + 0.4)), flag=1.0) + '<rect width="1080" height="1920" fill="#1E7A4A" opacity="0.18"/>'
    if c == "ui_block": return ui_block(t, t0)
    if c == "susp": return close(t, t0, hat="cowboy", red=True, extra=stamp(t, S[19] + 0.3))
    if c == "room_red": return medium(t, hat="cowboy", flag=1.0, red=True)
    if c == "bank": return bank(t, t0)
    # end card
    p = e_out(prog(t, t0, t0 + 0.5))
    return (city(t) + '<rect width="1080" height="1920" fill="#000" opacity="0.45"/>'
            + stext(540, 840, "РУСЛАН ДЕЙКУН", fit("РУСЛАН ДЕЙКУН", 940, 100), fill="#fff", sc=p)
            + stext(540, 960, "КАБАНОВИЧ", 100, fill=YEL, sc=p) + stext(540, 1090, "вернётся. Часть 2?", 44, fill="#C9D1DC", sw=0, shadow=False, op=p))


# ------------------------------------------------------------------ captions
KEY_Y = {"паспорт", "макс", "кабаново", "майкл", "техас", "ковёр", "флаг", "пельмени", "америка", "списали", "столе", "стол", "руслан", "руслана", "сам"}
KEY_R = {"блин", "гет", "аут", "ху", "мэм"}


def captions(t):
    if base.CHUNKS is None: base.CHUNKS = base.chunks()
    for t0, t1, c in base.CHUNKS:
        if t0 <= t < t1:
            size = 70; gap = size * 0.3
            words = [w["disp"] for w in c]
            total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            if total > 960: size = int(size * 960 / total); gap = size * 0.3; total = sum(tw(w, size) for w in words) + gap * (len(words) - 1)
            x = 540 - total / 2; out = []
            for w in words:
                k = re.sub(r"[^\w-]", "", w).lower()
                col = YEL if k in KEY_Y else (RED if k in KEY_R else "#F4EFE6")
                out.append(stext(x, 1480, w, size, fill=col, stroke="#120C0A", sw=12, anchor="start"))
                x += tw(w, size) + gap
            return "".join(out)
    return ""


def shake(t):
    for t0, amp in ((S[10], 22), (S[19] + 0.3, 16), (S[15], 10)):
        if 0 <= t - t0 < 0.45:
            k = math.exp(-(t - t0) * 9) * amp
            return k * math.sin((t - t0) * 70), k * math.cos((t - t0) * 53)
    return 0, 0


def frame_svg(f):
    t = f / FPS30
    dx, dy = shake(t)
    fade = f'<rect width="1080" height="1920" fill="#000" opacity="{clamp((t - DUR + 0.6) / 0.6):.2f}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}'
            f'<rect width="1080" height="1920" fill="#000"/><g transform="translate({dx:.1f},{dy:.1f})">{scene(t)}</g>'
            f'<rect width="1080" height="1920" fill="url(#gDark2)"/>{hud(t)}{captions(t)}{fade}{base.WM()}</svg>')


def render(f):
    cairosvg.svg2png(bytestring=frame_svg(f).encode(), write_to=f"build/frames/{f:05d}.png")
    return f


if __name__ == "__main__":
    os.makedirs("build/frames", exist_ok=True)
    frames = [int(x) for x in sys.argv[1:]] or list(range(NF))
    with Pool(os.cpu_count()) as pool:
        for i, _ in enumerate(pool.imap_unordered(render, frames, chunksize=4)):
            if i % 300 == 0: print("frame", i, flush=True)
    print("done", len(frames))
