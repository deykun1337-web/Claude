"""«Этот ролик собран без монтажёра» — style 10 HUD-lime, 60 fps. python3 grafika/compose.py <frames_dir> | sfx"""
import json, sys
sys.path.insert(0, "/home/user/Claude/reels/motion"); import mokit as M, hud as H

TM = json.load(open("/home/user/Claude/grafika/build/timing.json")); T = [s for s, d in TM["lines"]]; D = [d for s, d in TM["lines"]]; TOT = TM["total"]
END = [T[i + 1] - 0.08 if i + 1 < len(T) else TOT for i in range(len(T))]
W = lambda i, txt, **k: H.words  # placeholder for readability


def tw_(i, txt): return H.timed_words(txt, T[i], D[i] * 0.9)


def scene(t):
    i = max(k for k in range(len(T)) if t >= T[k] - 0.1) if t >= T[0] - 0.1 else 0
    L = []
    if i == 0:
        L += [H.words(t, tw_(0, "ЭТОТ РОЛИК СОБРАН *БЕЗ* МОНТАЖЁРА"), y=560, t_out=END[0]),
              H.strike(t, T[0] + 1.2, 540, 900, "AFTER EFFECTS", 52, "монтаж · 01"), H.strike(t, T[0] + 1.6, 540, 1110, "PREMIERE PRO", 52, "монтаж · 02"),
              H.side_icon(80, 1300, "{ }", "КОД", t, T[0] + 0.3), H.crosshair(960, 1350, t)]
        return L, "ВСТУПЛЕНИЕ"
    if i == 1:
        body = f'<text x="24" y="40" font-family="DejaVu Sans Mono" font-size="25" fill="#F3F3EE">{H.typed(t, T[1] + 0.5, "хочу лайм, зерно, 60 fps и свой бит")}</text>'
        L += [H.words(t, tw_(1, "Я ПРОСТО *НАПИСАЛ*[ТЕКСТ] CLAUDE"), y=560, t_out=END[1]),
              H.chip(t, T[1] + 1.4, 300, 790, "СТИЛЬ", 1, -4), H.chip(t, T[1] + 1.8, 760, 820, "ЦВЕТ", 2, 3), H.chip(t, T[1] + 2.3, 520, 1320, "МУЗЫКА", 3, -2),
              H.panel(t, T[1] + 0.3, 150, 960, 780, 190, "СООБЩЕНИЕ", body)]
        return L, "ПРОМПТ"
    if i == 2:
        L += [H.words(t, tw_(2, "ОН ПИШЕТ *КОД*[</>] — КАДР ЗА КАДРОМ"), y=560, t_out=END[2]), H.score(t, T[2] + 0.4, y=900), H.side_icon(80, 900, "◆", "КЛЮЧИ", t, T[2])]
        return L, "ПАРТИТУРА"
    if i == 3:
        L += [H.words(t, tw_(3, "ГОЛОС — *НЕЙРОСЕТЬ*[AI] МУЗЫКА — *КОДОМ*"), y=560, t_out=END[3], size=58), H.wave(t, T[3] + 0.3, y=900),
              H.checklist(t, T[3] + 1.4, [("МОНТАЖЁР", False), ("СТОКИ", False), ("СВОЙ ГОЛОС", True), ("СВОЯ МУЗЫКА", True)], y=1170, size=42)]
        return L, "ЗВУК"
    if i == 4:
        L += [H.words(t, tw_(4, "КАЖДЫЙ *ЩЕЛЧОК* РАСПИСАН *ПО_ВРЕМЕНИ*"), y=560, t_out=END[4], size=58),
              H.score(t, T[4] + 0.3, y=880, rows=("слово", "щелчок", "удар", "свуш", "камера"), seed=9, label="ЗВУКИ")]
        return L, "САУНД-ДИЗАЙН"
    if i == 5:
        L += [H.words(t, tw_(5, "*2* РОЛИКА В ДЕНЬ"), y=560, t_out=END[5], size=72),
              M.wrap(f'<text x="540" y="1000" text-anchor="middle" dominant-baseline="middle" font-family="Unbounded" font-weight="900" font-size="300" fill="#D4FF2A">0 Ч</text>', t, T[5] + 1.0, pop=True, cx=540, cy=1000),
              M.wrap('<text x="540" y="1220" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="34" fill="#6E6F68">В МОНТАЖКЕ</text>', t, T[5] + 1.3)]
        return L, "ИТОГ"
    L += [H.words(t, tw_(6, "НАПИШИ *ГРАФИКА* В КОММЕНТАРИЯХ"), y=560, size=60),
          H.chip(t, T[6] + 1.6, 540, 860, "ГРАФИКА", 1, -3, size=44), H.bubble(t, T[6] + 2.4, 300, 1020, "пришлю промпт в Директ 📩".replace(" 📩", ""), w=480),
          H.side_icon(80, 1300, "✉", "ДИРЕКТ", t, T[6] + 2.4)]
    return L, "ФИНАЛ"


HITS = [T[0] + 1.25, T[1] + 1.4, T[3] + 1.4, T[5] + 1.0, T[6] + 1.6]


def frame_svg(t):
    layers, name = scene(t)
    return H.frame(t, TOT, layers, scene=name, shake_xy=H.shake(t, HITS), fps=60)


def sfx_events():
    ev = [("whoosh", s - 0.2) for s in T[1:]] + [("boom", HITS[3])]
    ev += [("strike", T[0] + 1.6), ("strike", T[0] + 2.0), ("pop", T[1] + 1.4), ("pop", T[1] + 1.8), ("pop", T[1] + 2.3), ("type", T[1] + 0.5),
           ("pop", T[6] + 1.6), ("pop", T[6] + 2.4)]
    for i in range(len(T)):
        for w, t0 in tw_(i, "x " * 6): pass
    for k in range(4): ev.append(("tick", T[3] + 1.8 + k * 0.35))
    for k in range(8): ev.append(("tick", T[2] + 0.5 + k * 0.17)); ev.append(("tick", T[4] + 0.4 + k * 0.17))
    for i, line in enumerate(["ЭТОТ РОЛИК СОБРАН *БЕЗ* МОНТАЖЁРА", "Я ПРОСТО *НАПИСАЛ*[ТЕКСТ] CLAUDE", "ОН ПИШЕТ *КОД*[</>] — КАДР ЗА КАДРОМ",
                              "ГОЛОС — *НЕЙРОСЕТЬ*[AI] МУЗЫКА — *КОДОМ*", "КАЖДЫЙ *ЩЕЛЧОК* РАСПИСАН *ПО_ВРЕМЕНИ*", "*2* РОЛИКА В ДЕНЬ", "НАПИШИ *ГРАФИКА* В КОММЕНТАРИЯХ"]):
        for w, t0 in tw_(i, line):
            if "*" in w: ev.append(("hit", t0 + 0.05))
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "sfx":
        sys.path.insert(0, "/home/user/Claude/reels/motion"); import sfx; sfx.track(sfx_events(), TOT, "/home/user/Claude/grafika/build/sfx.wav"); print("sfx ok")
    elif sys.argv[1] == "test":
        import cairosvg
        for x in sys.argv[3:]: cairosvg.svg2png(bytestring=frame_svg(float(x)).encode(), write_to=f"{sys.argv[2]}/t_{x}.png")
    else:
        print(M.render(frame_svg, TOT, sys.argv[1], fps=60))
