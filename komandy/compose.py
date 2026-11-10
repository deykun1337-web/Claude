"""«5 команд Claude Code» — style 4 (light paper + dots), 60 fps. python3 komandy/compose.py <frames_dir> | sfx | test <dir> t…"""
import json, sys
sys.path.insert(0, "/home/user/Claude/reels/motion"); import mokit as M

th = M.LIGHT
TM = json.load(open("/home/user/Claude/komandy/build/timing.json")); T = [s for s, d in TM["lines"]]; TOT = TM["total"]
CMDS = [("/init", "Изучит проект и создаст CLAUDE.md с правилами", [("> /init", 0.0), ("Анализирую проект…", 0.8), ("✓ Создан CLAUDE.md", 1.8)]),
        ("/clear", "Новая задача — чистый чат, лимит не тает", [("> /clear", 0.0), ("✓ Контекст очищен", 0.9)]),
        ("/compact", "Сжимает длинную переписку — работаешь дальше", [("> /compact", 0.0), ("Сжимаю историю…", 0.7), ("✓ История сжата, контекст сохранён", 1.7)]),
        ("Esc Esc", "Откат к любому твоему сообщению", [("> Esc Esc  (/rewind)", 0.0), ("↩ Вернуть код и разговор к…", 0.8), ("✓ Откат выполнен", 1.9)]),
        ("Shift+Tab", "Режимы: спрашивать / править сам / план", [("> Shift+Tab", 0.0), ("режим: принимать правки", 0.6), ("режим: план", 1.4)])]


def steps_row(t, active):
    out = ""
    for k in range(5):
        x = 70 + k * 192; a = M.appear(t, T[1] - 0.2 + k * 0.08, 0.3)
        on = k == active; done = k < active
        fill = th["blue"] if on else ("#21C17A" if done else "#FFFFFF")
        out += (f'<g opacity="{a:.2f}">' + M.shadow(x, 560, 170, 90, 22, 0.8) + f'<rect x="{x}" y="560" width="170" height="90" rx="22" fill="{fill}" stroke="#00000012" stroke-width="2"/>'
                f'<text x="{x + 85}" y="607" text-anchor="middle" dominant-baseline="middle" font-family="DejaVu Sans Mono" font-size="25" font-weight="bold" fill="{"#fff" if on or done else th["ink"]}">{CMDS[k][0]}</text></g>')
    return out


def frame_svg(t):
    els = [M.bg(th, t)]
    i = max(k for k in range(len(T)) if t >= T[k] - 0.15) if t >= T[0] - 0.15 else 0
    if i == 0:
        els.append(M.wrap(M.big_number(th, 540, 900, 5, t, 0.2, size=420, color=th["accent"]), t, 0.1, pop=True, cx=540, cy=900))
        els.append(M.wrap('<text x="540" y="1180" text-anchor="middle" font-family="Inter" font-size="56" font-weight="800" fill="#16181D">команд Claude Code</text>', t, 0.6))
        els.append(M.boar(470, 1300, 10, t))
        head = M.headline(th, t, 0.02, "Жму их *каждый день*", y=330, size=72, per_word=0.06)
    elif i <= 5:
        k = i - 1; t0 = T[i] - 0.15; name, desc, lines = CMDS[k]
        els.append(steps_row(t, k))
        els.append(M.terminal(th, 110, 760, 860, 380, lines, t, t0 + 0.4, title="Claude Code"))
        els.append(M.wrap(M.card(th, 110, 1200, 860, 150, f'<text x="430" y="85" text-anchor="middle" font-family="Inter" font-size="31" font-weight="700" fill="#16181D">{desc}</text>'), t, t0 + 1.2))
        cx, cy = M.move(t, [(t0, 900, 1500), (t0 + 0.6, 260 + k * 192, 640)])
        els.append(M.cursor(th, cx, cy, "ты", click=(t - t0 - 0.6) / 0.4))
        els.append(M.boar(880, 1400, 8, t))
        head = M.headline(th, t, t0 + 0.02, f"{['Первая', 'Вторая', 'Третья', 'Четвёртая', 'Пятая'][k]}: *{name}*", y=330, size=76, per_word=0.08)
    else:
        t0 = T[6] - 0.15
        els.append(M.keyword_bar(th, 180, 760, "КОМАНДЫ", t, t0 + 0.4))
        els.append(M.wrap(M.card(th, 190, 920, 700, 420, "".join(f'<text x="50" y="{80 + j * 64}" font-family="DejaVu Sans Mono" font-size="30" fill="#16181D">{c[0]}</text>' for j, c in enumerate(CMDS))
                                 + '<text x="50" y="395" font-family="Inter" font-size="26" fill="#6B6F78">+ полная шпаргалка — в Директе</text>'), t, t0 + 1.0))
        cx, cy = M.move(t, [(t0 + 0.4, 900, 1500), (t0 + 1.4, 860, 800)])
        els.append(M.cursor(th, cx, cy, "ты", click=(t - t0 - 1.4) / 0.4))
        head = M.headline(th, t, t0 + 0.02, "Шпаргалку *пришлю* — напиши слово", y=330, size=62)
    wm = '<text x="540" y="1840" text-anchor="middle" font-family="Inter" font-size="28" font-weight="700" fill="#16181D" opacity="0.35">@deykun1337</text>'
    return M.frame(th, t, els, cam=M.camera(t, [(0, 1.06, 540, 960), (2.5, 1.0, 540, 960), (TOT, 1.03, 540, 960)]), overlay=head + wm)


def sfx_events():
    ev = [("whoosh", s - 0.25) for s in T[1:]] + [("boom", 0.25), ("pop", 0.7)]
    for i in range(1, 6):
        ev += [("pop", T[i] + 0.45), ("type", T[i] + 0.3), ("tick", T[i] + 1.2), ("tick", T[i] + 1.9)]
    ev += [("type", T[6] + 0.7), ("pop", T[6] + 1.0), ("tick", T[6] + 1.5)]
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "sfx":
        import sfx; sfx.track(sfx_events(), TOT, "/home/user/Claude/komandy/build/sfx.wav"); print("sfx ok")
    elif sys.argv[1] == "test":
        import cairosvg
        for x in sys.argv[3:]: cairosvg.svg2png(bytestring=frame_svg(float(x)).encode(), write_to=f"{sys.argv[2]}/t_{x}.png")
    else:
        print(M.render(frame_svg, TOT, sys.argv[1], fps=60))
