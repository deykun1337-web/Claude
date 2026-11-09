"""Reference scenes for style 10 (HUD-лайм). python3 reels/motion/demo_hud.py <outdir>"""
import sys; sys.path.insert(0, "/home/user/Claude/reels/motion"); import mokit as M, hud as H, cairosvg
OUT = sys.argv[1]; TOT = 30
def s1(t):
    return H.frame(t, TOT, [H.words(t, H.timed_words("ЭТОТ РОЛИК СОБРАН *БЕЗ* МОНТАЖЁРА", 0.0, 1.2), y=640),
                            H.strike(t, 0.6, 330, 980, "AFTER EFFECTS", 50, "монтаж · 01"), H.strike(t, 0.9, 700, 1210, "PREMIERE", 50, "монтаж · 02"),
                            H.side_icon(80, 900, "{ }", "КОД", t, 0.2), H.crosshair(900, 1450, t)], scene="ВСТУПЛЕНИЕ", shake_xy=H.shake(t, [0.6]))
def s2(t):
    body = (f'<text x="24" y="40" font-family="DejaVu Sans Mono" font-size="26" fill="#F3F3EE">{H.typed(t, 0.3, "хочу 30 секунд графики, лайм, зерно")}</text>')
    return H.frame(t, TOT, [H.words(t, H.timed_words("Я ПРОСТО *НАПИСАЛ*[ТЕКСТ] CLAUDE:", 0.0, 1.0), y=600),
                            H.chip(t, 0.8, 300, 820, "30 СЕКУНД", 1, -4), H.chip(t, 1.0, 780, 860, "ЛАЙМ", 2, 3), H.chip(t, 1.2, 330, 1330, "ЗЕРНО", 3, 2),
                            H.panel(t, 0.4, 150, 980, 780, 200, "СООБЩЕНИЕ", body)], scene="ПРОМПТ")
def s3(t):
    return H.frame(t, TOT, [H.words(t, H.timed_words("КАЖДАЯ *БУКВА* И КАЖДЫЙ *ПОВОРОТ_КАМЕРЫ* РАСПИСАНЫ *ПО_ВРЕМЕНИ*", 0.0, 1.6), y=600, size=54),
                            H.score(t, 0.6, y=960), H.side_icon(80, 900, "◆", "КЛЮЧИ", t, 0.3)], scene="ПАРТИТУРА")
def s4(t):
    return H.frame(t, TOT, [H.words(t, H.timed_words("ГОЛОС *ПОЛНОСТЬЮ*[AI] СГЕНЕРИРОВАН", 0.0, 1.0), y=600),
                            H.wave(t, 0.3, y=900), H.checklist(t, 0.9, [("ПЕРСОНАЖИ", False), ("СЛОЖНОЕ 3D", False), ("ТИТРЫ", True), ("ПЕРЕХОДЫ", True)], y=1180)], scene="ИТОГ")
for i, (fn, tt) in enumerate([(s1, 1.6), (s2, 1.9), (s3, 2.6), (s4, 2.6)]):
    cairosvg.svg2png(bytestring=fn(tt).encode(), write_to=f"{OUT}/h{i}.png")
