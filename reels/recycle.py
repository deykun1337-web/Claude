"""Recycle weak old reels of @deykun1337 as uniqualized TRIAL reels, then delete the weak originals.

Rules (owner's request, 09.11.2026):
  candidate  = our REELS posted on/after 2026-11-07 (our cartoon era) OR listed in reels/recycle_allow.txt,
               older than 5 days, like_count < 10, comments < 3, not about fundraising (life_dima / сбор),
               not already recycled, not itself a recycled trial.
  delete     = original is deleted only when its trial copy is ≥72 h old AND the trial has ≥ the original's likes,
               and the original still has < 3 comments. Fundraising posts are never touched.
State: reels/state/recycle.json. Token is injected by the network proxy (graph.facebook.com, rupload.facebook.com).

Usage:
  python3 reels/recycle.py plan                       # list candidates and pending deletions (no changes)
  python3 reels/recycle.py next                       # download the best candidate → reels/state/next.mp4 + prints its caption
  python3 reels/recycle.py post <caption_trial.txt>   # uniq + publish next.mp4 as a trial reel, remember the pair
  python3 reels/recycle.py cleanup [--dry]            # delete originals whose trial already did better
"""
import datetime as dt, json, os, re, subprocess, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
IG = json.load(open(os.path.join(HERE, "ig_account.json")))["ig_user_id"]
API = "https://graph.facebook.com/v21.0"
STATE = os.path.join(HERE, "state", "recycle.json")
ALLOW = os.path.join(HERE, "recycle_allow.txt")
ERA = dt.datetime(2026, 11, 7, tzinfo=dt.timezone.utc)
BLOCK = re.compile(r"life_dima|сбор|собрать|донат|помож", re.I)


def req(method, path, params=None):
    url = f"{API}/{path}" + ("?" + urllib.parse.urlencode(params) if params else "")
    r = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp: return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {e.read().decode(errors='replace')[:300]}")


import urllib.parse


def st():
    return json.load(open(STATE)) if os.path.exists(STATE) else {"pairs": [], "deleted": []}


def save(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True); json.dump(s, open(STATE, "w"), ensure_ascii=False, indent=1)


def media():
    out, url = [], f"{IG}/media"
    params = {"fields": "id,caption,timestamp,media_product_type,like_count,comments_count,permalink,media_url,thumbnail_url", "limit": 50}
    data = req("GET", url, params)
    out += data.get("data", [])
    while data.get("paging", {}).get("next") and len(out) < 300:
        with urllib.request.urlopen(data["paging"]["next"], timeout=120) as r: data = json.loads(r.read())
        out += data.get("data", [])
    return out


def ts(m): return dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z")


def candidates(ms, s):
    allow = {l.strip() for l in open(ALLOW) if l.strip() and not l.startswith("#")} if os.path.exists(ALLOW) else set()
    used = {p["orig"] for p in s["pairs"]} | {p["trial"] for p in s["pairs"]}
    now = dt.datetime.now(dt.timezone.utc); res = []
    for m in ms:
        code = m["permalink"].rstrip("/").split("/")[-1]
        if m.get("media_product_type") != "REELS" or m["id"] in used or BLOCK.search(m.get("caption") or ""): continue
        if not (ts(m) >= ERA or code in allow): continue
        if (now - ts(m)).days < 5 or (m.get("like_count") or 0) >= 10 or (m.get("comments_count") or 0) >= 3: continue
        res.append(m)
    return sorted(res, key=lambda m: (m.get("like_count") or 0, m["timestamp"]))


def to_delete(ms, s):
    by = {m["id"]: m for m in ms}; now = dt.datetime.now(dt.timezone.utc); res = []
    for p in s["pairs"]:
        o, t = by.get(p["orig"]), by.get(p["trial"])
        if not o or not t or p.get("deleted"): continue
        if BLOCK.search(o.get("caption") or "") or (o.get("comments_count") or 0) >= 3: continue
        if (now - ts(t)).total_seconds() >= 72 * 3600 and (t.get("like_count") or 0) >= (o.get("like_count") or 0):
            res.append((p, o, t))
    return res


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    s = st()
    if cmd == "plan":
        ms = media()
        for m in candidates(ms, s): print("recycle", m["permalink"], m.get("like_count"), (m.get("caption") or "")[:50].replace("\n", " "))
        for p, o, t in to_delete(ms, s): print("delete ", o["permalink"], "→ trial", t["permalink"])
    elif cmd == "next":
        c = candidates(media(), s)
        if not c: print("no candidates"); sys.exit(0)
        m = c[0]; out = os.path.join(HERE, "state", "next.mp4")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        urllib.request.urlretrieve(m["media_url"], out)
        s["next"] = {"orig": m["id"], "permalink": m["permalink"]}; save(s)
        print(json.dumps({"orig": m["permalink"], "likes": m.get("like_count"), "caption": m.get("caption") or ""}, ensure_ascii=False))
        print("video:", out, "— watch a few frames, then write a NEW trial caption and run: recycle.py post <caption.txt>")
    elif cmd == "post":
        nx = s.get("next"); src = os.path.join(HERE, "state", "next.mp4")
        if not nx or not os.path.exists(src): raise SystemExit("run next first")
        dst = os.path.join(HERE, "state", "next_trial.mp4")
        subprocess.run([sys.executable, os.path.join(HERE, "uniq.py"), src, dst], check=True)
        out = subprocess.run([sys.executable, os.path.join(HERE, "ig_post.py"), "post", dst, sys.argv[2], "--cover-ms", "2000", "--trial"], capture_output=True, text=True)
        print(out.stdout[-400:], out.stderr[-400:])
        mm = re.search(r'"media_id": "(\d+)", "permalink": "([^"]+)"', out.stdout)
        if not mm: raise SystemExit("publish failed")
        s["pairs"].append({"orig": nx["orig"], "orig_link": nx["permalink"], "trial": mm.group(1), "trial_link": mm.group(2),
                           "t": dt.datetime.now(dt.timezone.utc).isoformat()})
        s.pop("next", None); save(s)
        for f in (src, dst): os.remove(f)
        print("recycled", nx["permalink"], "→", mm.group(2))
    elif cmd == "cleanup":
        dry = "--dry" in sys.argv
        for p, o, t in to_delete(media(), s):
            if dry: print("would delete", o["permalink"]); continue
            try:
                req("DELETE", o["id"]); p["deleted"] = True; s["deleted"].append(o["permalink"]); print("deleted", o["permalink"])
            except RuntimeError as e:
                print("delete failed (API may not allow deleting this media):", e)
        save(s)
    else:
        print(__doc__)
