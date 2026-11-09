"""Серия «Кабаново — деревня подписчиков»: учёт жителей, ников, желаний и план следующей серии.

    python3 reels/village.py register <N> <media_id>       # после публикации серии N
    python3 reels/village.py collect                      # собрать комментарии со всех серий → жители и желания
    python3 reels/village.py plan <N> [max_houses]        # план серии N → kabanovo/ep<N>.json + reels/village/REPORT.md

Кто получает дом (честно и только реальные ники):
  1) написал КАБАНОВО (или свой ник) под серией и ПОДПИСАН — подписку подтверждает бот ig_bot.py (state "sent" в
     reels/state/ig.json, через is_user_follow_business после ответа «+» в Директ);
  2) остальные комментаторы — в очередь «ждут подписку» (дом появится, как только бот подтвердит подписку).
Ник на доме = username комментатора (не текст из комментария — так никто не впишет чужой или оскорбительный ник).
Желание серии = комментарий с наибольшим числом лайков, прошедший фильтр (без мата, ссылок, политики, упоминаний людей).
Instagram API не отдаёт список новых подписчиков целиком — поэтому «кто подписался» считаем по комментаторам серии
(подтверждённые ботом) + прирост followers_count между сериями.
"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ig_bot import req, IG, OWNER

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "village"); os.makedirs(D, exist_ok=True)
ST = os.path.join(D, "state.json"); IGST = os.path.join(HERE, "state", "ig.json")
WORD = "КАБАНОВО"
BAD = re.compile(r"(http|www\.|t\.me|@\w|хуй|хуе|пизд|бля|ебa|ебат|ёб|сук[аи]|муда|гандон|пидор|шлюх|нацист|войн|сво\b|путин|зеленск|политик|наркот|оруж)", re.I)


def load():
    try: return json.load(open(ST, encoding="utf-8"))
    except FileNotFoundError: return {"episodes": [], "residents": {}, "wishes": [], "built": [], "followers": {}}


def save(s): json.dump(s, open(ST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def confirmed():
    try: ppl = json.load(open(IGST, encoding="utf-8")).get("people", {})
    except FileNotFoundError: return set()
    return {u for u, p in ppl.items() if p.get("state") == "sent"}


def collect():
    s = load(); fol = confirmed()
    for ep in s["episodes"]:
        url, page = f"{ep['media_id']}/comments", {"fields": "id,text,username,like_count,timestamp", "limit": 50}
        while url:
            r = req("GET", url, page); page = None
            for c in r.get("data", []):
                u = c.get("username")
                if not u or u == OWNER: continue
                txt = (c.get("text") or "").strip(); likes = c.get("like_count", 0)
                res = s["residents"].setdefault(u, {"ep": ep["n"], "t": c.get("timestamp"), "likes": 0, "house": None})
                res["likes"] = max(res["likes"], likes)
                body = re.sub(rf"(?i){WORD}", "", txt).strip(" .,!-—:")
                if len(body) >= 6 and not BAD.search(body):
                    w = next((w for w in s["wishes"] if w["id"] == c["id"]), None)
                    if w: w["likes"] = likes
                    else: s["wishes"].append({"id": c["id"], "text": body[:80], "likes": likes, "user": u, "ep": ep["n"], "done": False})
            url = r.get("paging", {}).get("next")
    for u, r in s["residents"].items(): r["follows"] = u in fol
    try: s["followers"][time.strftime("%Y-%m-%d %H:%M")] = req("GET", IG, {"fields": "followers_count"}).get("followers_count")
    except RuntimeError: pass
    save(s); print(json.dumps({"residents": len(s["residents"]), "confirmed": sum(r["follows"] for r in s["residents"].values()),
                                "wishes": len(s["wishes"])}, ensure_ascii=False))


def plan(n, max_houses=24):
    s = load(); built = [r for r in s["residents"].values() if r.get("house") is not None]
    wait = [(u, r) for u, r in s["residents"].items() if r.get("house") is None and r.get("follows")]
    wait.sort(key=lambda x: (-x[1]["likes"], x[1]["t"] or ""))
    slot = len(built); new = []
    for u, r in wait[:max_houses]:
        r["house"] = slot; r["built_ep"] = n; slot += 1; new.append(u)
    open_w = [w for w in s["wishes"] if not w["done"]]; wish = max(open_w, key=lambda w: w["likes"], default=None)
    if wish: wish["done"] = True; wish["ep"] = n; s["built"].append({"ep": n, "wish": wish["text"], "by": wish["user"], "likes": wish["likes"]})
    houses = sorted([{"nick": u, "slot": r["house"], "new": u in new} for u, r in s["residents"].items() if r.get("house") is not None], key=lambda h: h["slot"])
    ep = {"timing": f"/home/user/Claude/kabanovo/build_ep{n}/timing.json", "houses": houses, "ghosts": max(6, 14 - len(houses) // 3),
          "new": new, "wish": wish, "episode": n}
    json.dump(ep, open(os.path.join(HERE, "..", "kabanovo", f"ep{n}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pend = [u for u, r in s["residents"].items() if r.get("house") is None and not r.get("follows")]
    fl = list(s["followers"].items())
    rep = [f"# Кабаново — отчёт к серии {n} ({time.strftime('%Y-%m-%d')})", "",
           f"- Жителей с домом: **{len(houses)}** (новых в этой серии: {len(new)})",
           f"- Ждут подтверждения подписки (написали, но бот ещё не подтвердил): {len(pend)}",
           f"- Подписчики аккаунта: {fl[0][1] if fl else '?'} → {fl[-1][1] if fl else '?'} ({fl[0][0] if fl else ''} → {fl[-1][0] if fl else ''})", "",
           "## Новые дома", *(f"- @{u}" for u in new), "", "## Ждут подписку (напомнить в серии: «подпишись — и дом твой»)", *(f"- @{u}" for u in pend[:40]), "",
           "## Желание серии", f"- {wish['text']} — {wish['likes']} ❤ от @{wish['user']}" if wish else "- пока нет", "",
           "## Топ-10 желаний в очереди", *(f"- {w['text']} — {w['likes']} ❤" for w in sorted([w for w in s['wishes'] if not w['done']], key=lambda w: -w['likes'])[:10])]
    open(os.path.join(D, "REPORT.md"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
    save(s); print("\n".join(rep))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "register":
        s = load(); s["episodes"].append({"n": int(a[1]), "media_id": a[2], "date": time.strftime("%Y-%m-%d")}); save(s); print("ok")
    elif a[0] == "collect": collect()
    elif a[0] == "plan": plan(int(a[1]), int(a[2]) if len(a) > 2 else 24)
