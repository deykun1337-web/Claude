"""Очередь ГОТОВЫХ роликов: публикация одной командой (экономит лимит Claude — запуск ничего не рендерит).

    python3 reels/queue_post.py list
    python3 reels/queue_post.py publish <am|pm>      # берёт первый ролик очереди для слота (или любой), публикует в 12:30 / 21:30

Элемент очереди — reels/queue/<slug>.json:
  {"slug": "grafika", "slot": "am", "style": 10, "word": "ГРАФИКА",
   "video_A": "grafika/output/grafika_A.mp4", "video": "grafika/output/grafika.mp4", "trial": "grafika/output/grafika_trial.mp4",
   "caption": "grafika/caption.txt", "caption_trial": "grafika/caption_trial.txt", "comment": "grafika/comment.txt",
   "tg": "grafika/tg.md", "guide": "reels/guides/ГРАФИКА.md", "keyword_row": "| ГРАФИКА | ... |", "log": "тема | стиль | длина"}
Шаги publish: строка слова в KEYWORDS.md (чтобы бот сразу отвечал) → основной рилс --at слот --comment → пробная копия --trial
(при лимите — в trial_later.txt) → гайд и ролик в Telegram → LOG.md, styles_used, удалить элемент → git commit + push.
"""
import json, os, re, subprocess, sys, time

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); Q = os.path.join(R, "reels", "queue")
SLOT = {"am": "12:30", "pm": "21:30"}


def sh(*cmd, check=False):
    p = subprocess.run(cmd, cwd=R, capture_output=True, text=True); out = (p.stdout + p.stderr).strip()
    print(f"$ {' '.join(cmd)[:120]}\n{out[-1200:]}", flush=True)
    if check and p.returncode: sys.exit(f"failed: {cmd}")
    return p.returncode, out


def items():
    os.makedirs(Q, exist_ok=True)
    return sorted([json.load(open(os.path.join(Q, f), encoding="utf-8")) for f in os.listdir(Q) if f.endswith(".json")], key=lambda x: x.get("order", 99))


def publish(slot):
    its = items()
    if not its: print("queue empty"); return 1
    it = next((x for x in its if x.get("slot") == slot), its[0])
    kw = os.path.join(R, "reels", "KEYWORDS.md"); txt = open(kw, encoding="utf-8").read()
    if f"| {it['word']} |" not in txt:
        open(kw, "w", encoding="utf-8").write(txt.rstrip("\n") + "\n" + it["keyword_row"] + "\n")
    sh("git", "add", "-A", "reels/KEYWORDS.md", "reels/guides"); sh("git", "commit", "-qm", f"Keyword {it['word']} (queued reel {it['slug']})")
    sh("git", "push", "-q", "origin", "HEAD")
    rc, out = sh("python3", "reels/ig_post.py", "post", it["video_A"], it["caption"], "--cover-ms", "700", "--at", SLOT[slot], "--comment", it["comment"])
    m = re.search(r'"permalink": "([^"]+)"', out); link = m.group(1) if m else None
    if not link: print("MAIN POST FAILED — элемент остаётся в очереди"); return 2
    rc, out = sh("python3", "reels/ig_post.py", "post", it["trial"], it["caption_trial"], "--cover-ms", "700", "--trial")
    trial = re.search(r'"permalink": "([^"]+)"', out)
    if not trial:
        open(os.path.join(R, "reels", "state", "trial_later.txt"), "a").write(it["slug"] + "\n")
    if os.environ.get("TG_BOT_TOKEN"):
        sh("python3", "reels/tg_bot.py", "post", it["guide"]); sh("python3", "reels/tg_bot.py", "video", it["video"], it["tg"])
    log = os.path.join(R, "reels", "LOG.md"); s = open(log, encoding="utf-8").read()
    row = f"| {time.strftime('%Y-%m-%d')} | {it['log']} (из очереди) | {it['word']} · {link}" + (f" · пробный {trial.group(1)}" if trial else " · пробный — trial_later") + " |\n"
    i = s.find("\n## Стили графики"); s = (s[:i].rstrip("\n") + "\n" + row + s[i:]) if i >= 0 else s + row
    open(log, "w", encoding="utf-8").write(s)
    sh("python3", "reels/style_pick.py", "log", str(it.get("style", 0)), it["slug"])
    os.remove(os.path.join(Q, f"{it['slug']}.json"))
    sh("git", "add", "-A", "reels/LOG.md", "reels/state", "reels/queue"); sh("git", "commit", "-qm", f"Published queued reel {it['slug']}")
    for k in range(4):
        if sh("git", "push", "-q", "origin", "HEAD")[0] == 0: break
        sh("git", "pull", "-q", "--rebase", "origin", "claude/trusting-cray-jkn30e"); time.sleep(2 ** k)
    print(json.dumps({"published": it["slug"], "link": link, "trial": trial.group(1) if trial else None}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "list":
        for x in items(): print(x["slug"], x.get("slot"), x["word"], x["log"])
    elif a[0] == "publish": sys.exit(publish(a[1] if len(a) > 1 else "am"))
