"""Pick the visual style for the next reel so looks ALTERNATE (rules in reels/STYLES.md).

    python3 reels/style_pick.py <slot: am|pm> "<topic words>"   → prints the style id + name + kit to use
    python3 reels/style_pick.py log <style_id> <slug>          → record what was published (reels/state/styles_used.txt)

Rules: never the same style as either of the last 3 reels; each day one reel is a UI-motion style (3/4/9 — the formats
that win in the Claude niche) and one is a character style (1/2/6/7/8/5); among allowed styles prefer the topic match,
then the one unused for longest.
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); LOG = os.path.join(HERE, "state", "styles_used.txt")
STYLES = {
    1: ("Гладкий 3D", "klod3d/chars_smooth.py + quality.py + Poly Haven", "char", "скетч диалог клод решает как управлять история"),
    2: ("Пластилин стоп-моушен", "klod3d/clay3d.py", "char", "тёплая история праздник эмоции как мы делаем"),
    3: ("Тёмный редакционный", "reels/motion/mokit.py DARK", "ui", "скилл агент трейд деньги новость убил инструмент github бесплатно"),
    4: ("Светлый «бумага + точки»", "reels/motion/mokit.py LIGHT", "ui", "код установка гайд шаги разработчик плагин безопасность система"),
    5: ("Пиксельный сплит-экран", "drawn/drawn2d.py pixelate + mokit", "char", "почему у одних интервью сравнение"),
    6: ("Рисованный 2D (codil.ya)", "drawn/drawn2d.py", "char", "быт мама друг офис сериал работа"),
    7: ("HD пиксель-арт", "drawn/drawn2d.py → pixelate()", "char", "подписки деньги гаджет ночь уют"),
    8: ("Реализм Poly Haven", "klod3d/assets.py + chars_smooth + quality.py", "char", "миф правда как работает улица разбор"),
    9: ("Гибрид: 3D-герой + тёмный UI", "chars_smooth (герой за ноутбуком) + mokit DARK оверлеи", "ui", "лимит комбайн автоматизация вирал рилсы заработок"),
}


def used():
    try: return [ln.split("\t") for ln in open(LOG, encoding="utf-8").read().splitlines() if ln.strip()]
    except FileNotFoundError: return []


def pick(slot, topic):
    hist = [int(r[1]) for r in used()]; last3 = set(hist[-3:]); today = time.strftime("%Y-%m-%d")
    today_kinds = [STYLES[int(r[1])][2] for r in used() if r[0] == today]
    want = None
    if today_kinds: want = "char" if today_kinds[-1] == "ui" else "ui"
    else: want = "ui" if slot == "am" else "char"
    cands = [k for k, v in STYLES.items() if k not in last3 and v[2] == want] or [k for k in STYLES if k not in last3]
    t = topic.lower()
    def score(k):
        match = sum(w in t for w in STYLES[k][3].split())
        age = len(hist) - max([i for i, h in enumerate(hist) if h == k], default=-99)
        return (match, age)
    k = max(cands, key=score); n, kit, kind, _ = STYLES[k]
    return k, n, kit, kind


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "log":
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        open(LOG, "a", encoding="utf-8").write(f"{time.strftime('%Y-%m-%d')}\t{a[1]}\t{a[2] if len(a) > 2 else ''}\n"); print("logged")
    else:
        k, n, kit, kind = pick(a[0] if a else "am", " ".join(a[1:]))
        print(f"СТИЛЬ {k}: {n}  ({'UI-моушн' if kind == 'ui' else 'персонажи'})  → {kit}")
