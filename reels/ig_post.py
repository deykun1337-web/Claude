"""Publish a Reel to Instagram via the official Instagram Graph API (Content Publishing).

The access token is NOT in this script or in the repo: the session's network proxy injects it
into requests to graph.facebook.com / rupload.facebook.com (saved as a network secret on the environment).

Usage:
  python3 reels/ig_post.py whoami                         # check token + find the IG business account id
  python3 reels/ig_post.py post <video.mp4> <caption.txt> [--cover-ms 1500] [--trial] [--story]   # --trial = пробный рилс (только неподписчикам); --story = история (caption игнорируется)

Requirements on the account side: @deykun1337 is a Professional (Creator/Business) account linked to a
Facebook Page, and the token has instagram_basic + instagram_content_publish + pages_show_list.
"""
import json, os, sys, time
import urllib.request, urllib.parse, urllib.error

API = "https://graph.facebook.com/v24.0"
RUPLOAD = "https://rupload.facebook.com/ig-api-upload/v24.0"
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ig_account.json")


def req(method, url, params=None, data=None, headers=None, timeout=120):
    if params: url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    r = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise SystemExit(f"HTTP {e.code} {method} {url.split('?')[0]}: {body[:600]}")


def ig_user_id():
    if os.path.exists(STATE):
        return json.load(open(STATE))["ig_user_id"]
    pages = req("GET", f"{API}/me/accounts", {"fields": "name,instagram_business_account{id,username}"})
    for p in pages.get("data", []):
        ig = p.get("instagram_business_account")
        if ig:
            json.dump({"ig_user_id": ig["id"], "username": ig.get("username"), "page": p.get("name")}, open(STATE, "w"), ensure_ascii=False)
            return ig["id"]
    raise SystemExit("No Instagram business account linked to the token's Facebook Pages. " + json.dumps(pages)[:400])


def whoami():
    me = req("GET", f"{API}/me", {"fields": "id,name"})
    uid = ig_user_id()
    info = req("GET", f"{API}/{uid}", {"fields": "username,followers_count,media_count"})
    print(json.dumps({"facebook_user": me, "instagram": info}, ensure_ascii=False, indent=1))


def post(video, caption_file, cover_ms=1500, trial=False, story=False):
    uid = ig_user_id()
    caption = open(caption_file, encoding="utf-8").read().strip()
    size = os.path.getsize(video)
    # 1) container for a resumable Reel upload
    if story:
        c = req("POST", f"{API}/{uid}/media", {"media_type": "STORIES", "upload_type": "resumable"})
    else:
      if trial:  # trial reel: JSON body with a trial_params OBJECT (v23+); shown to non-followers only
        c = req("POST", f"{API}/{uid}/media", data=json.dumps({"media_type": "REELS", "upload_type": "resumable", "caption": caption,
                                                              "thumb_offset": cover_ms, "trial_params": {"graduation_strategy": "MANUAL"}}).encode(),
                headers={"Content-Type": "application/json"})
      else:
        c = req("POST", f"{API}/{uid}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": caption,
                                               "share_to_feed": "true", "thumb_offset": str(cover_ms)})
    cid = c["id"]
    print("container", cid, flush=True)
    # 2) upload the bytes
    with open(video, "rb") as fh:
        up = req("POST", f"{RUPLOAD}/{cid}", data=fh.read(), headers={"offset": "0", "file_size": str(size), "Content-Type": "application/octet-stream"}, timeout=600)
    print("upload", up, flush=True)
    # 3) wait for processing
    for _ in range(60):
        st = req("GET", f"{API}/{cid}", {"fields": "status_code,status"})
        print("status", st.get("status_code"), flush=True)
        if st.get("status_code") == "FINISHED": break
        if st.get("status_code") in ("ERROR", "EXPIRED"): raise SystemExit(f"processing failed: {st}")
        time.sleep(10)
    else:
        raise SystemExit("processing timed out")
    # 4) publish
    pub = req("POST", f"{API}/{uid}/media_publish", {"creation_id": cid})
    mid = pub["id"]
    link = req("GET", f"{API}/{mid}", {"fields": "permalink"}).get("permalink")
    print(json.dumps({"media_id": mid, "permalink": link}, ensure_ascii=False))
    return link


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "whoami": whoami()
    elif len(sys.argv) >= 4 and sys.argv[1] == "post":
        cover = int(sys.argv[sys.argv.index("--cover-ms") + 1]) if "--cover-ms" in sys.argv else 1500
        post(sys.argv[2], sys.argv[3], cover, trial="--trial" in sys.argv, story="--story" in sys.argv)
    else:
        print(__doc__)
