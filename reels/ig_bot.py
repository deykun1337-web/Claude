"""Keyword auto-replies for @deykun1337 via the official Instagram Graph API (graph.facebook.com, system-user token).

The access token is NOT in this repo: the session's network proxy injects it into requests to
graph.facebook.com (saved by the owner as a network secret). Needed permissions:
instagram_business_basic, instagram_business_manage_comments, instagram_business_manage_messages.

Flow (run hourly by a scheduled task):
 1. New comment with a keyword from reels/KEYWORDS.md under our recent reels
    -> private reply (DM) to the commenter: "подпишись на @deykun1337 и ответь + сюда".
 2. A person who answered in DM -> check is_user_follow_business:
    followed -> send the Telegram invite link (join requests are auto-approved by tg_bot.py approve);
    not yet  -> one reminder (max once per 12 h).
State (processed comment ids, people already served) lives in reels/state/ig.json.

Usage: python3 reels/ig_bot.py whoami | run [--dry]
"""
import json, os, random, re, sys, time, urllib.request, urllib.parse, urllib.error

API = "https://graph.facebook.com/v24.0"
IG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ig_account.json")))["ig_user_id"]
HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state", "ig.json")
DRY = "--dry" in sys.argv
OWNER = "deykun1337"
PUBLIC = ["Отправил в Директ 📩", "Лови в сообщениях 👀", "Готово, проверь Директ ✅", "Уже в Директе 🐗"]


def req(method, path, params=None, body=None):
    url = path if path.startswith("http") else f"{API}/{path}"
    if params: url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp: return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {method} {url.split('?')[0]}: {e.read().decode(errors='replace')[:400]}")


def keywords():
    kw = {}
    for ln in open(os.path.join(HERE, "KEYWORDS.md"), encoding="utf-8"):
        m = re.match(r"\|\s*([A-ZА-ЯЁ0-9]+)\s*\|", ln)
        if m and m.group(1) not in ("Слово",): kw[m.group(1)] = ln.split("|")[4].strip()
    return kw


def tg_link():
    p = os.path.join(HERE, "state", "tg.json")
    return json.load(open(p)).get("invite") if os.path.exists(p) else None


def guide_parts(word, n=950):
    """Guide text for a keyword, split into Instagram-sized DM chunks (used until the Telegram channel is ready)."""
    path = os.path.join(HERE, "guides", f"{word}.md")
    txt = open(path, encoding="utf-8").read() if os.path.exists(path) else f"Гайд {word} скоро будет 🙌"
    txt = re.sub(r"^#+ ", "", txt, flags=re.M).replace("**", "").replace("> ", "")
    parts, cur = [], ""
    for para in txt.split("\n\n"):
        if len(cur) + len(para) + 2 > n and cur: parts.append(cur.strip()); cur = ""
        cur += para + "\n\n"
    if cur.strip(): parts.append(cur.strip())
    return ["Спасибо за подписку! 🐗 Держи гайд:"] + parts[:4]


def st_load():
    return json.load(open(STATE)) if os.path.exists(STATE) else {"comments": [], "people": {}}


def st_save(st):
    if DRY: return  # a dry run must not mark comments as answered
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    st["comments"] = st["comments"][-5000:]
    json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)


def send(recipient, text):
    if DRY: print("DRY send", recipient, text[:80]); return
    req("POST", f"{IG}/messages", body={"recipient": recipient, "message": {"text": text}})


def run():
    st = st_load(); kw = keywords(); link = tg_link()
    seen = set(st["comments"]); n_c = n_l = 0
    media = req("GET", f"{IG}/media", {"fields": "id,timestamp", "limit": 15}).get("data", [])
    for m in media:
        cs = req("GET", f"{m['id']}/comments", {"fields": "id,text,username,timestamp", "limit": 50}).get("data", [])
        for c in cs:
            if c["id"] in seen or c.get("username") == OWNER: continue
            seen.add(c["id"]); st["comments"].append(c["id"])
            word = next((k for k in kw if re.search(rf"(?<!\w){k}(?!\w)", c.get("text", ""), re.I)), None)
            if not word: continue
            try:
                send({"comment_id": c["id"]}, f"Привет! 👋 Гайд «{word}» уже готов.\n"
                                              f"1) Подпишись на @{OWNER}\n2) Ответь сюда «+» — и я сразу пришлю.")
                st["people"].setdefault(c.get("username", c["id"]), {"word": word, "state": "asked", "t": time.time()}); n_c += 1
                if not DRY:  # a short public reply under the comment also lifts the reel in recommendations
                    try: req("POST", f"{c['id']}/replies", {"message": random.choice(PUBLIC)})
                    except RuntimeError as e: print("public reply failed:", e)
            except RuntimeError as e: print("private reply failed:", e)
    # DMs: people who answered after the private reply
    st_save(st)  # remember answered comments even if the DM part fails below
    conv = []
    for lim in (10, 5, 3):  # Instagram sometimes answers "reduce the amount of data" — retry smaller
        try:
            conv = req("GET", f"{IG}/conversations", {"platform": "instagram", "limit": lim, "fields": "participants,messages.limit(2){from,message,created_time}"}).get("data", []); break
        except RuntimeError as e:
            print("conversations retry:", str(e)[:120])
    for cv in conv:
        msgs = cv.get("messages", {}).get("data", [])
        if not msgs: continue
        last = msgs[0]; frm = last.get("from", {})
        if frm.get("username") == OWNER: continue
        uid, uname = frm.get("id"), frm.get("username")
        p = st["people"].get(uname)
        if not p or p["state"] == "sent": continue
        try:
            prof = req("GET", uid, {"fields": "username,is_user_follow_business"})
        except RuntimeError as e:
            print("profile failed:", e); continue
        if prof.get("is_user_follow_business"):
            if link:
                send({"id": uid}, f"Спасибо за подписку! 🐗 Вот вход в наш Telegram с гайдами и туториалами: {link}\nЗаявку одобрим автоматически.")
            else:
                for part in guide_parts(p["word"]): send({"id": uid}, part)
            p["state"] = "sent"; n_l += 1
        elif time.time() - p.get("reminded", 0) > 12 * 3600:
            send({"id": uid}, f"Пока не вижу подписку на @{OWNER} 🙈 Подпишись и снова напиши «+».")
            p["reminded"] = time.time()
    st_save(st); print(json.dumps({"private_replies": n_c, "links_sent": n_l}))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "whoami":
        print(json.dumps(req("GET", IG, {"fields": "username,followers_count,media_count"}), ensure_ascii=False))
    elif len(sys.argv) > 1 and sys.argv[1] == "run":
        run()
    else:
        print(__doc__)
