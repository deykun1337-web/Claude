"""«5 Claude в одном чате» — style 3 (dark editorial, reels/motion/mokit.py). python3 compose.py <frames_dir>"""
import json, math, sys
sys.path.insert(0, "/home/user/Claude/reels/motion"); import mokit as M

th = M.DARK
TM = json.load(open("/home/user/Claude/subagenty/build/timing.json")); T = [s for s, d in TM["lines"]]; TOTAL = TM["total"]
END = [s + d for s, d in TM["lines"]]
AG = [("🔎", "Поиск"), ("✍️", "Сценарий"), ("🎬", "Монтаж"), ("🛡️", "Проверка"), ("🚀", "Публикация")]
SC = [0.0, T[1] - 0.12, T[2] - 0.12, T[7] - 0.12, T[8] - 0.12, T[9] - 0.12, TOTAL]   # scene boundaries


def scene_wrap(t, a, b, el):
    """scene enters with a slide from the right + fade, leaves to the left"""
    if t < a - 0.01 or t > b + 0.25: return ""
    k_in = M.ease((t - a) / 0.3) if a > 0 else 1.0; k_out = 1 - M.ease((t - b) / 0.25)
    dx = (1 - k_in) * 120 - (1 - k_out) * 120; z = 1.0 + 0.035 * M.clamp((t - a) / max(b - a, 0.1))
    return (f'<g opacity="{k_in * k_out:.3f}" transform="translate({dx:.1f},0) translate(540,960) scale({z:.4f}) translate(-540,-960)">{el}</g>')


def s_hook(t):
    out = [M.label(th, "claude code · субагенты", 170)]
    out.append(M.headline(th, t, 0.02, "Один Claude — *помощник*", y=330, size=70, t1=2.7, per_word=0.05))
    out.append(M.headline(th, t, 2.75, "Пять в одном чате — *команда*", y=330, size=70, per_word=0.06))
    split = M.ease((t - 2.6) / 0.6)
    for i in range(5):
        x = 540 + (i - 2) * 190 * split
        if i != 2 and split <= 0: continue
        s = 1.0 if i == 2 else M.back((t - 2.6 - abs(i - 2) * 0.08) / 0.45)
        if s <= 0: continue
        px = 17 - 6 * split; w = 14 * px
        out.append(f'<g transform="translate({x:.1f},980) scale({s:.3f}) translate({-w / 2:.1f},{-5.5 * px:.1f})">{M.boar(0, 0, px, t + i)}</g>')
        if split > 0.5:
            out.append(M.wrap(f'<text x="{x:.1f}" y="{1130}" text-anchor="middle" font-family="Inter" font-size="30" font-weight="700" fill="{th["sub"]}">Claude #{i + 1}</text>', t, 3.1 + i * 0.07))
    out.append(M.wrap(M.card(th, 300, 1290, 480, 120, f'<text x="240" y="70" text-anchor="middle" font-family="Inter" font-size="40" font-weight="800" fill="{th["ink"]}">1 чат · 5 агентов</text>', glow=True), t, 3.4))
    return "".join(out)


def s_what(t):
    t0 = SC[1]
    code = [[("cm", "---")], [("kw", "name: "), ("str", "scout")], [("kw", "description: "), ("tx", "ищет залетевшие рилсы")],
            [("kw", "tools: "), ("fn", "WebSearch, Read")], [("kw", "model: "), ("num", "haiku")], [("cm", "---")], [("tx", "Ты разведчик. Найди 10 рилсов,")], [("tx", "которые залетели сильнее среднего…")]]
    return (M.label(th, "что это", 170) + M.headline(th, t, t0 + 0.1, "У каждого *своя задача*, инструменты и *чистая память*", y=340, size=60)
            + M.wrap(M.window(th, 90, 640, 900, 560, ".claude/agents/scout.md", M.code(code, t, t0 + 0.6, 70, size=27, hw=900), dark=True, glow=True), t, t0 + 0.3)
            + M.wrap(M.stamp(th, 0, 0, "1 файл = 1 агент", t, t0 + 2.6, rot=-8, col=th["accent"]).replace("translate(0,0)", "translate(760,1240)"), t, t0 + 2.6))


def agent_detail(i, t, t0):
    th_ = th
    if i == 0:
        inner = (M.candles(th_, 40, 120, 720, 260, t, t0 + 0.1, n=22, seed=5)
                 + f'<text x="40" y="70" font-family="DejaVu Sans Mono" font-size="24" fill="{th_["sub"]}">просмотры / средние по аккаунту</text>'
                 + (f'<text x="760" y="440" text-anchor="end" font-family="Inter" font-size="72" font-weight="900" fill="{th_["accent"]}">×12</text>' if t > t0 + 1.0 else ""))
        return M.card(th_, 140, 880, 800, 480, inner, glow=True)
    if i == 1:
        lines = ["0:00  Хук: «Пять Claude в одном чате»", "0:05  Что такое субагенты", "0:10  Пять ролей по очереди", "0:22  Итог + кодовое слово"]
        inner = f'<text x="40" y="70" font-family="DejaVu Sans Mono" font-size="24" fill="{th_["sub"]}">scenario.md</text>'
        for k, ln in enumerate(lines):
            vis = ln[:int(M.clamp((t - t0 - 0.15 - k * 0.25) * 60, 0, len(ln)))]
            inner += f'<text x="40" y="{150 + k * 72}" font-family="Inter" font-size="32" font-weight="600" fill="{th_["ink"]}">{vis}</text>'
        return M.card(th_, 140, 880, 800, 480, inner, glow=True)
    if i == 2:
        inner = f'<text x="40" y="70" font-family="DejaVu Sans Mono" font-size="24" fill="{th_["sub"]}">render · 30 fps</text>'
        for k, (lab, col) in enumerate([("видео", th_["blue"]), ("голос", th_["green"]), ("музыка", th_["accent"])]):
            f = M.ease((t - t0 - 0.1 - k * 0.12) / 1.0)
            inner += (f'<text x="40" y="{168 + k * 92}" font-family="Inter" font-size="28" font-weight="600" fill="{th_["sub"]}">{lab}</text>'
                      f'<rect x="200" y="{140 + k * 92}" width="560" height="40" rx="12" fill="{th_["line"]}"/>'
                      f'<rect x="200" y="{140 + k * 92}" width="{560 * f:.0f}" height="40" rx="12" fill="{col}"/>')
        inner += M.boar(330, 400, 6, t)
        return M.card(th_, 140, 880, 800, 480, inner, glow=True)
    if i == 3:
        checks = ["субтитры не на лице", "кодовое слово в финале", "звук без клиппинга", "длина 31 с"]
        inner = f'<text x="40" y="70" font-family="DejaVu Sans Mono" font-size="24" fill="{th_["sub"]}">check.log</text>'
        for k, c in enumerate(checks):
            a = M.appear(t, t0 + 0.1 + k * 0.22, 0.2)
            if a <= 0: continue
            inner += (f'<g opacity="{a:.2f}"><circle cx="62" cy="{150 + k * 76}" r="22" fill="{th_["green"]}"/>'
                      f'<path d="M51,{150 + k * 76} l8,8 l14,-16" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
                      f'<text x="104" y="{160 + k * 76}" font-family="Inter" font-size="32" font-weight="600" fill="{th_["ink"]}">{c}</text></g>')
        return M.card(th_, 140, 880, 800, 480, inner, glow=True)
    inner = (f'<text x="40" y="70" font-family="DejaVu Sans Mono" font-size="24" fill="{th_["sub"]}">instagram · 21:30</text>'
             + (f'<rect x="40" y="110" width="330" height="70" rx="20" fill="{th_["green"]}"/><text x="205" y="146" text-anchor="middle" dominant-baseline="middle" font-family="Inter" font-size="30" font-weight="800" fill="#0A0908">Опубликовано ✓</text>' if t > t0 + 0.3 else "")
             + (f'<rect x="40" y="215" width="560" height="74" rx="22" fill="#2A241D"/><text x="66" y="260" font-family="Inter" font-size="28" fill="{th_["ink"]}">@user: АГЕНТЫ</text>' if t > t0 + 0.8 else "")
             + (f'<rect x="200" y="315" width="560" height="74" rx="22" fill="{th_["accent"]}"/><text x="226" y="360" font-family="Inter" font-size="28" font-weight="700" fill="#fff">Отправил в Директ 📩</text>' if t > t0 + 1.4 else ""))
    return M.card(th_, 140, 880, 800, 480, inner, glow=True)


HEAD = ["Первый *ищет* залетевшие рилсы", "Второй *пишет* сценарий", "Третий *рисует* и монтирует", "Четвёртый *ловит* ошибки", "Пятый *публикует* и отвечает"]


def s_agents(t):
    i = max(k for k in range(5) if t >= T[2 + k] - 0.12); t0 = T[2 + i] - 0.12
    out = [M.label(th, f"агент {i + 1} из 5", 170), M.tiles(th, 540, 560, AG, t, SC[2], active=i, size=164, gap=18)]
    out.append(M.headline(th, t, t0 + 0.02, HEAD[i], y=380, size=62, per_word=0.05))
    a = M.appear(t, t0, 0.3)
    out.append(f'<g opacity="{a:.2f}" transform="translate(0,{(1 - a) * 40:.1f})">{agent_detail(i, t, t0)}</g>')
    return "".join(out)


def s_parallel(t):
    t0 = SC[3]; out = [M.label(th, "параллельно", 170), M.headline(th, t, t0 + 0.05, "Все пятеро работают *одновременно*", y=360, size=62)]
    for k, (emo, lab) in enumerate(AG):
        f = M.ease((t - t0 - 0.3) / (1.6 + 0.35 * k)); y = 620 + k * 150
        out.append(M.wrap(
            f'<text x="110" y="{y + 30}" font-family="Noto Color Emoji" font-size="44">{emo}</text>'
            f'<text x="190" y="{y + 30}" font-family="Inter" font-size="34" font-weight="700" fill="{th["ink"]}">{lab}</text>'
            f'<text x="970" y="{y + 30}" text-anchor="end" font-family="DejaVu Sans Mono" font-size="30" fill="{th["green"] if f >= 0.999 else th["sub"]}">{"готово" if f >= 0.999 else f"{f * 100:.0f}%"}</text>'
            f'<rect x="110" y="{y + 56}" width="860" height="22" rx="11" fill="{th["line"]}"/>'
            f'<rect x="110" y="{y + 56}" width="{860 * f:.0f}" height="22" rx="11" fill="{th["accent"]}"/>', t, t0 + 0.1 + k * 0.06))
    out.append(M.wrap(f'<text x="540" y="1460" text-anchor="middle" font-family="Inter" font-size="40" font-weight="700" fill="{th["sub"]}">а ты — только принимаешь результат</text>', t, T[7] + 1.6))
    return "".join(out)


def s_result(t):
    t0 = SC[4]
    return (M.label(th, "результат", 170) + M.headline(th, t, t0 + 0.05, "Так выходят *эти мультики*", y=360, size=66)
            + M.wrap(M.big_number(th, 540, 900, 2, t, t0 + 0.2, size=420, color=th["accent"]), t, t0 + 0.15, pop=True, cx=540, cy=900)
            + M.wrap(f'<text x="540" y="1180" text-anchor="middle" font-family="Inter" font-size="54" font-weight="800" fill="{th["ink"]}">ролика каждый день</text>', t, t0 + 0.5)
            + M.boar(477, 1290, 9, t))


def s_end(t):
    t0 = SC[5]
    out = [M.label(th, "инструкция", 170), M.headline(th, t, t0 + 0.05, "Как создать *своего агента*?", y=360, size=66),
           M.keyword_bar(th, 180, 640, "АГЕНТЫ", t, t0 + 0.6), M.tg_card(th, 280, 900, t, t0 + 1.6, btn="Подписаться")]
    cx, cy = M.move(t, [(t0 + 0.6, 1000, 1500), (t0 + 1.4, 860, 690), (t0 + 2.6, 860, 690), (t0 + 3.3, 560, 1440)])
    clk = max((t - t0 - 1.4) / 0.4 if t0 + 1.4 < t < t0 + 1.8 else 0, (t - t0 - 3.3) / 0.4 if t0 + 3.3 < t < t0 + 3.7 else 0)
    if t > t0 + 0.6: out.append(M.cursor(th, cx, cy, "ты", click=clk))
    out.append(M.wrap(f'<text x="540" y="1610" text-anchor="middle" font-family="Inter" font-size="40" font-weight="700" fill="{th["sub"]}">пришлю в Директ после подписки</text>', t, t0 + 2.2))
    return "".join(out)


SCENES = [s_hook, s_what, s_agents, s_parallel, s_result, s_end]


def frame_svg(t):
    k = max(i for i in range(6) if t >= SC[i] - 0.001) if t >= 0 else 0
    gx = {0: (540, 980), 1: (540, 900), 2: (540, 1100), 3: (540, 1000), 4: (540, 900), 5: (540, 1100)}[k]
    layers = [M.bg(th, t, glow_at=gx)]
    for i, fn in enumerate(SCENES):
        a, b = SC[i], SC[i + 1]
        if a - 0.01 <= t <= b + 0.25: layers.append(scene_wrap(t, a, b if i < 5 else 999, fn(t)))
    wm = f'<text x="540" y="1840" text-anchor="middle" font-family="Inter" font-size="28" font-weight="700" fill="#FFFFFF" opacity="0.35">@deykun1337</text>'
    return M.frame(th, t, layers, overlay=wm)


if __name__ == "__main__":
    if sys.argv[1] == "test":
        import cairosvg
        for x in sys.argv[3:]:
            cairosvg.svg2png(bytestring=frame_svg(float(x)).encode(), write_to=f"{sys.argv[2]}/t_{x}.png")
    else:
        print(M.render(frame_svg, TOTAL, sys.argv[1], fps=30))
