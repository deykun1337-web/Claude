"""Viral-reel research for idea generation (reading, not scraping: a few dozen public reels by link).

Input: reel links/shortcodes in reels/IDEAS_INBOX.md (one per line, any text around is fine) + the table in REFERENCES.md.
For each new reel: public embed page → author, caption, view count; video → frame sheet (first 3 s dense + every 3 s).
Output:
  reels/viral/<code>/sheet.jpg    — look at it to read the hook, on-screen text and edit pace
  reels/viral/data.json           — all collected rows
  reels/viral/captured.tsv        — input for .claude/skills/ig-viral/swipe.py (outlier = views / account median in our corpus)
Then: python3 .claude/skills/ig-viral/swipe.py reels/viral/captured.tsv --out reels/SWIPE.md

Usage: python3 reels/viral.py            # process new links
       python3 reels/viral.py --hooks    # after you filled "hook" by hand in data.json, rebuild captured.tsv
"""
import html, json, os, re, statistics, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "viral")
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
CODE = re.compile(r"(?:instagram\.com/(?:reel|p)/)?\b([A-Za-z0-9_-]{11})\b")


def codes():
    found = []
    for name in ("IDEAS_INBOX.md", "REFERENCES.md"):
        p = os.path.join(HERE, name)
        if not os.path.exists(p): continue
        for m in re.finditer(r"instagram\.com/(?:reel|p)/([A-Za-z0-9_-]{11})|^\|\s*([A-Za-z0-9_-]{11})\s*\|", open(p, encoding="utf-8").read(), re.M):
            c = m.group(1) or m.group(2)
            if c not in found: found.append(c)
    return found


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read().decode("utf-8", "replace")


def embed(code):
    s = get(f"https://www.instagram.com/reel/{code}/embed/captioned/")
    cap = re.search(r'class="Caption">(.*?)<div class="CaptionComments', s, re.S)
    cap = html.unescape(re.sub(r"<[^>]+>", " ", cap.group(1))).strip() if cap else ""
    user = re.search(r'class="CaptionUsername"[^>]*>([^<]+)<', s) or re.search(r'"username\\":\\"([^\\]+)', s)
    user = user.group(1).strip() if user else ""
    if cap.startswith(user): cap = cap[len(user):].strip()
    views = re.search(r'video_view_count\\":(\d+)', s)
    mp4 = re.search(r'https:[^"]*?\.mp4[^"]*', s)
    mp4 = mp4.group(0).replace('\\\\\\/', '/').replace('\\/', '/').replace('\\u0026', '&').rstrip('\\') if mp4 else None
    return {"code": code, "account": "@" + user if user else "", "views": int(views.group(1)) if views else None, "caption": cap, "mp4": mp4}


def sheet(row):
    d = os.path.join(OUT, row["code"]); os.makedirs(d, exist_ok=True)
    vid = os.path.join(d, "v.mp4")
    try:
        urllib.request.urlretrieve(row["mp4"], vid)
    except Exception as e:
        row["error"] = f"video: {e}"; return
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vid]) or 0)
    row["length"] = round(dur, 1)
    ts = [0, 0.5, 1, 1.5, 2, 2.5, 3] + [t for t in range(6, int(dur), 3)]
    fr = []
    for k, t in enumerate(ts[:24]):
        f = os.path.join(d, f"f{k:02d}.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", vid, "-frames:v", "1", "-vf", "scale=180:320", f])
        if os.path.exists(f): fr.append(f)
    subprocess.run(["montage"] + fr + ["-tile", "8x3", "-geometry", "+2+2", os.path.join(d, "sheet.jpg")])
    for f in fr: os.remove(f)
    os.remove(vid)


def write_tsv(rows):
    by = {}
    for r in rows:
        if r.get("views"): by.setdefault(r["account"], []).append(r["views"])
    with open(os.path.join(OUT, "captured.tsv"), "w", encoding="utf-8") as f:
        f.write("account\tmedian\tviews\thook\n")
        for r in rows:
            if not r.get("views"): continue
            med = statistics.median(by[r["account"]]) if len(by[r["account"]]) >= 3 else ""
            hook = (r.get("hook") or r["caption"].split("\n")[0])[:160].replace("\t", " ")
            f.write(f"{r['account']}\t{med}\t{r['views']}\t{hook}\n")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); dp = os.path.join(OUT, "data.json")
    rows = json.load(open(dp)) if os.path.exists(dp) else []
    if "--hooks" not in sys.argv:
        have = {r["code"] for r in rows}
        for c in codes():
            if c in have: continue
            try:
                r = embed(c)
            except Exception as e:
                print("skip", c, e); continue
            if r["mp4"]: sheet(r)
            r.pop("mp4", None); rows.append(r); print(c, r["account"], r["views"], (r["caption"] or "")[:60].replace("\n", " "))
        json.dump(rows, open(dp, "w"), ensure_ascii=False, indent=1)
    write_tsv(rows); print("rows", len(rows), "→ reels/viral/captured.tsv")
