import sys; sys.path.insert(0, "/home/user/Claude/reels/motion"); import mokit as M, cairosvg
OUT = sys.argv[1]; L, D = M.LIGHT, M.DARK   # usage: python3 reels/motion/demo.py <outdir>  (reference scenes for styles 3 and 4)
def light1(t):
    code = [[("kw", "app"), ("tx", ".post("), ("str", "'/login'"), ("tx", ", async (req) =>")], [("kw", "  const "), ("tx", "user = "), ("kw", "await "), ("fn", "db.query"), ("tx", "(")],
            [("str", "    `SELECT * FROM users")], [("str", "     WHERE email='${req.email}'`")], [("kw", "  const "), ("tx", "key = "), ("str", "'sk_live_9f2a…'")], [("tx", "});")]]
    L_ = [M.bg(L, t), M.wrap(M.window(L, 110, 520, 860, 470, "auth.js", M.code(code, t, 0.2, 60, hi={3: "#E5484D", 4: "#E5484D"}), dark=True), t, 0.1),
          M.wrap(M.big_number(L, 540, 1230, 162, t, 0.5, 230), t, 0.5), M.headline(L, t, 0.8, "дыр найдено *раньше*, чем это сделают хакеры", y=1420, size=54),
          M.boar(150, 1640, 10, t)]
    cx, cy = M.move(t, [(0, 900, 1500), (1.6, 700, 900)])
    return M.frame(L, t, L_, cam=M.camera(t, [(0, 1.08, 540, 980), (3, 1.0, 540, 960)]), overlay=M.cursor(L, cx, cy, "ты", click=(t - 1.6) / 0.4))
def light2(t):
    els = [M.bg(L, t)]
    for i, (dk, title) in enumerate([(False, "фича: оплата"), (True, "Rust  pay"), (False, "Вход"), (True, "тесты")]):
        x = 60 + (i % 2) * 500; y = 420 + (i // 2) * 560
        body = ""
        if i == 0: body = f'<rect x="60" y="150" width="300" height="80" rx="16" fill="#fff" stroke="#2F6BFF" stroke-width="4"/><text x="210" y="192" text-anchor="middle" dominant-baseline="middle" font-family="Inter" font-size="34" font-weight="700" fill="#16181D">Экран</text>'
        if i == 1: body = '<g transform="translate(0,90)">' + M.code([[("kw", "async fn "), ("fn", "pay"), ("tx", "(o)")], [("tx", "  api.charge(&o)")], [("tx", "  db.save(&o)")], [("num", "  ok")]], t, 0.6, 50, size=24) + "</g>"
        if i == 2: body = ''.join(f'<rect x="40" y="{130 + k * 100}" width="380" height="74" rx="16" fill="#fff" stroke="#21C17A" stroke-width="3"/><text x="64" y="{168 + k * 100}" dominant-baseline="middle" font-family="Inter" font-size="28" fill="#8A8F99">{w}</text>' for k, w in enumerate(["email", "пароль"])) + '<rect x="40" y="340" width="380" height="74" rx="37" fill="#F26B3A"/><text x="230" y="378" text-anchor="middle" dominant-baseline="middle" font-family="Inter" font-size="30" font-weight="800" fill="#fff">нет лимита</text>'
        if i == 3: body = M.ring(M.DARK, 230, 250, 80, t, 0.9, r=120)
        els.append(M.wrap(M.step(L, x, y, i + 1, title, body, dark=dk, w=460, h=500), t, 0.15 * i))
        if i in (0, 2): els.append(M.arrow(L, x + 470, y + 250, x + 530, y + 250, t, 0.15 * i + 0.4))
    els.append(M.boar(470, 1580, 10, t))
    return M.frame(L, t, els, overlay=M.headline(L, t, 0.2, "Каждая фича — *4 шага*", y=250, size=68))
def light3(t):
    els = [M.bg(L, t), M.terminal(L, 140, 640, 800, 420, ["> /plugin marketplace add deykun/kit", "✓ Marketplace added", "> /plugin install kabanchik", "✓ Installed kabanchik"], t, 0.0, [0, 0.9, 1.4, 2.3]) if False else
           M.terminal(L, 140, 640, 800, 420, [("> /plugin marketplace add deykun/kit", 0), ("✓ Marketplace added", 0.9), ("> /plugin install kabanchik", 1.2), ("✓ Installed kabanchik", 2.0)], t, 0.0),
           M.keyword_bar(L, 180, 1320, "КАБАН", t, 0.3)]
    return M.frame(L, t, els, overlay=M.headline(L, t, 0, "Ставится *одной командой*", y=420, size=66))
def dark1(t):
    els = [M.bg(D, t), M.label(D, "trader skill"), M.wrap(M.card(D, 190, 700, 700, 230, f'<text x="40" y="70" font-family="DejaVu Sans Mono" font-size="22" fill="#8D857A">github.com / … / trader-skill</text><text x="40" y="135" font-family="Inter" font-size="54" font-weight="800" fill="#F6F1EA">Trader Skill</text><text x="40" y="185" font-family="Inter" font-size="24" fill="#8D857A">5 скиллов для торговли прямо в Claude</text>', glow=True), t, 0.1),
           M.stamp(D, 790, 930, "БЕСПЛАТНО", t, 0.8)]
    return M.frame(D, t, els, overlay=M.headline(D, t, 0.2, "Теперь Claude сам *ищет* и *заключает* сделки", y=440, size=60))
def dark2(t):
    els = [M.bg(D, t, glow_at=(540, 1000)), M.label(D, "5 скиллов"), M.tiles(D, 540, 900, [("🔎", "Сканер"), ("📰", "Новости"), ("🎯", "Вход"), ("🛡️", "Риск"), ("⏳", "Время")], t, 0.1, active=int(t * 1.5) % 5, size=168, gap=20)]
    return M.frame(D, t, els, overlay=M.headline(D, t, 0.2, "Один *сканирует*, второй читает новости", y=440, size=60))
def dark3(t):
    els = [M.bg(D, t), M.label(D, "установка"), M.chat(D, 120, 560, 840, 620, [("me", "Установи этот скилл: github.com/…/trader-skill", 0.2), ("ai", "Ставлю Trader Skill… Готово, 5 скиллов подключены ✓", 0.9)], t, 0.0),
           M.tg_card(D, 280, 1240, t, 1.4)]
    return M.frame(D, t, els, overlay=M.headline(D, t, 0, "Кинь ему ссылку и *попроси установить*", y=420, size=58))
for name, fn, tt in [("l1", light1, 2.4), ("l2", light2, 2.5), ("l3", light3, 3.0), ("d1", dark1, 2.0), ("d2", dark2, 1.6), ("d3", dark3, 2.6)]:
    cairosvg.svg2png(bytestring=fn(tt).encode(), write_to=f"{OUT}/{name}.png")
