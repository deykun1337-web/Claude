"""Telegram channel helper for @deykun1337 (Bot API).

The bot token is read from the environment variable TG_BOT_TOKEN (set by the owner in the cloud
environment settings; it is never stored in this repo). The bot must be an admin of the channel with
rights: change info, post, edit, delete messages, invite users via link.

Usage:
  python3 reels/tg_bot.py whoami                       # check the token, show the bot
  python3 reels/tg_bot.py channel <@name|-100id>       # remember the channel (writes reels/state/tg.json)
  python3 reels/tg_bot.py setup <title> <descr.txt> <avatar.png>   # title, description, photo
  python3 reels/tg_bot.py link                         # create/print the invite link with join requests
  python3 reels/tg_bot.py approve                      # approve all pending join requests (run hourly)
  python3 reels/tg_bot.py post <file.md>               # post a guide (Telegram HTML subset)
  python3 reels/tg_bot.py clean <max_id>               # try to delete old posts 1..max_id
"""
import json, os, re, sys, time, urllib.request, urllib.parse, urllib.error, uuid

TOKEN = os.environ.get("TG_BOT_TOKEN", "")
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state", "tg.json")


def api(method, params=None, files=None):
    if not TOKEN: raise SystemExit("TG_BOT_TOKEN is not set (add it in the environment settings)")
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    if files:
        b = uuid.uuid4().hex; body = b""
        for k, v in (params or {}).items():
            body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        for k, path in files.items():
            body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{os.path.basename(path)}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()
            body += open(path, "rb").read() + b"\r\n"
        body += f"--{b}--\r\n".encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    else:
        req = urllib.request.Request(url, data=json.dumps(params or {}).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: res = json.loads(r.read())
    except urllib.error.HTTPError as e:
        res = json.loads(e.read() or b"{}")
    if not res.get("ok"): raise RuntimeError(f"{method}: {res.get('description')}")
    return res["result"]


def state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {}


def save(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True); json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)


def chat():
    c = state().get("chat_id")
    if not c: raise SystemExit("run: tg_bot.py channel <@name|-100id> first")
    return c


def md_to_html(md):
    out = []
    for ln in md.splitlines():
        ln = ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        ln = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", ln)
        if ln.startswith("# "): ln = f"<b>{ln[2:].upper()}</b>"
        elif ln.startswith("## "): ln = f"\n<b>{ln[3:]}</b>"
        elif ln.startswith("&gt; "): ln = f"<code>{ln[5:]}</code>"
        out.append(ln)
    return "\n".join(out).strip()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "whoami":
        print(json.dumps(api("getMe"), ensure_ascii=False))
    elif cmd == "channel":
        c = api("getChat", {"chat_id": sys.argv[2]})
        st = state(); st["chat_id"] = c["id"]; st["title"] = c.get("title"); save(st)
        me = api("getMe"); m = api("getChatMember", {"chat_id": c["id"], "user_id": me["id"]})
        print(json.dumps({"chat": {"id": c["id"], "title": c.get("title"), "type": c.get("type"), "username": c.get("username")},
                          "bot_rights": {k: v for k, v in m.items() if k.startswith("can_")}}, ensure_ascii=False, indent=1))
    elif cmd == "setup":
        title, descr, photo = sys.argv[2], open(sys.argv[3], encoding="utf-8").read().strip(), sys.argv[4]
        for m, p in (("setChatTitle", {"title": title}), ("setChatDescription", {"description": descr})):
            try: api(m, {"chat_id": chat(), **p}); print(m, "ok")
            except RuntimeError as e: print(e)
        try: api("setChatPhoto", {"chat_id": chat()}, {"photo": photo}); print("setChatPhoto ok")
        except RuntimeError as e: print(e)
    elif cmd == "link":
        st = state()
        if not st.get("invite"):
            r = api("createChatInviteLink", {"chat_id": chat(), "name": "instagram", "creates_join_request": True})
            st["invite"] = r["invite_link"]; save(st)
        print(st["invite"])
    elif cmd == "approve":
        st = state(); off = st.get("offset", 0); n = 0
        ups = api("getUpdates", {"offset": off, "timeout": 0, "allowed_updates": ["chat_join_request"]})
        for u in ups:
            off = u["update_id"] + 1; r = u.get("chat_join_request")
            if r and r["chat"]["id"] == st.get("chat_id"):
                try: api("approveChatJoinRequest", {"chat_id": r["chat"]["id"], "user_id": r["from"]["id"]}); n += 1
                except RuntimeError as e: print("skip", e)
        st["offset"] = off; save(st); print("approved", n)
    elif cmd == "post":
        r = api("sendMessage", {"chat_id": chat(), "text": md_to_html(open(sys.argv[2], encoding="utf-8").read())[:4000], "parse_mode": "HTML",
                                "link_preview_options": {"is_disabled": True}})
        print("posted", r["message_id"])
    elif cmd == "clean":
        mx = int(sys.argv[2]); ok = 0
        for i in range(1, mx + 1):
            try: api("deleteMessage", {"chat_id": chat(), "message_id": i}); ok += 1
            except RuntimeError: pass
            time.sleep(0.05)
        print("deleted", ok)
    else:
        print(__doc__)
