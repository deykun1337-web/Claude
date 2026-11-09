"""Daily stats for @deykun1337 → reels/ANALYTICS.md (read by every reel run to copy what works).
Uses insights (views, reach, saves, shares, avg watch time) when the token has instagram_manage_insights;
otherwise falls back to likes + comments. Usage: python3 reels/analytics.py"""
import datetime as dt, json, os, re, urllib.request, urllib.error, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
IG = json.load(open(os.path.join(HERE, "ig_account.json")))["ig_user_id"]
API = "https://graph.facebook.com/v21.0"


def get(path, params):
    try:
        return json.loads(urllib.request.urlopen(f"{API}/{path}?" + urllib.parse.urlencode(params), timeout=60).read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode(errors="replace")[:200]}


log = open(os.path.join(HERE, "LOG.md"), encoding="utf-8").read()
ms = get(f"{IG}/media", {"fields": "id,caption,timestamp,like_count,comments_count,permalink,media_product_type", "limit": 30}).get("data", [])
acc = get(IG, {"fields": "followers_count,media_count"})
rows, has_ins = [], None
for m in ms:
    if m.get("media_product_type") != "REELS": continue
    ins = get(f"{m['id']}/insights", {"metric": "views,reach,saved,shares,ig_reels_avg_watch_time"})
    v = {d["name"]: (d.get("values") or [{}])[0].get("value") for d in ins.get("data", [])}
    has_ins = bool(v) if has_ins is None else has_ins or bool(v)
    code = m["permalink"].rstrip("/").split("/")[-1]
    line = next((l for l in log.splitlines() if code in l), "")
    topic = line.split("|")[2].strip() if line.count("|") > 3 else (m.get("caption") or "")[:40].replace("\n", " ")
    trial = "пробный" in line and line.find(code) > line.find("пробный")
    score = (v.get("views") or 0) + 30 * ((v.get("saved") or 0) + 2 * (v.get("shares") or 0)) + 20 * (m.get("like_count") or 0) + 60 * (m.get("comments_count") or 0)
    rows.append((score, m["timestamp"][:16].replace("T", " "), topic[:45], "пробный" if trial else "основной", v.get("views"), v.get("reach"),
                 v.get("saved"), v.get("shares"), round((v.get("ig_reels_avg_watch_time") or 0) / 1000, 1) or None, m.get("like_count"), m.get("comments_count"), m["permalink"]))
rows.sort(reverse=True)
out = [f"# Аналитика @deykun1337 · {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC", "",
       f"Подписчиков: {acc.get('followers_count')} · публикаций: {acc.get('media_count')}",
       "" if has_ins else "⚠️ Нет доступа к статистике просмотров (insights): в токене не хватает разрешения instagram_manage_insights. Сейчас ранжирование по лайкам и комментариям.", "",
       "| # | дата | тема | тип | просмотры | охват | сохр. | репосты | ср. просмотр, с | лайки | комм. | ссылка |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for k, r in enumerate(rows, 1):
    out.append("| " + " | ".join(str(x if x is not None else "—") for x in (k,) + r[1:]) + " |")
out += ["", "Как использовать: 3 верхних ролика — образец формата/хука/темы для следующих; нижние 3 — не повторять их подачу."]
open(os.path.join(HERE, "ANALYTICS.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out[:12]))
