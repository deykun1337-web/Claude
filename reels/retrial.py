"""Re-release old weak reels as uniqualized TRIAL reels with a keyword endcard.
Usage: python3 reels/retrial.py <slug> [--dry]   (slugs and texts in ITEMS below)
Pipeline: append 2.6 s endcard (frozen last frame + «Напиши КАБАН») → uniq.py → cover hook → ig_post.py --trial."""
import io, json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "klod3d"))
import cairosvg, ui_kit as U
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TMP = os.path.join(ROOT, "reels", "state", "retrial"); os.makedirs(TMP, exist_ok=True)
WORD, WHAT = "КАБАН", "пришлю гайд, как делать такие мультики"
TAGS = "#нейросети #claude #ии #мультики #юмор"
ITEMS = {
 "agenty":   ("agenty/output/agenty.mp4", "КЛОД НАНЯЛ|АГЕНТОВ", "Нейросеть наняла себе команду агентов. Что могло пойти не так? 🐗🤖"),
 "medved":   ("medved/output/medved_2026.mp4", "МЕДВЕДЬ|ИЗ 2026", "Тот самый медведь из ноября 2026 — теперь в мультике 🐻❄️"),
 "musya":    ("musya/output/musya.mp4", "МУСЯ,|ЭТО ТЫ?", "Муся, это ты? Нейросеть сняла мультик по мему 🐸"),
 "obidelsya":("obidelsya/output/obidelsya.mp4", "ТЫ ЧЁ,|ОБИДЕЛСЯ?", "Когда кабан обиделся, а ты не понял за что 🐗"),
 "pivo":     ("pivo/output/pivnoy_zhivot.mp4", "ПОЧЕМУ РАСТЁТ|ПИВНОЙ ЖИВОТ", "Почему от пива растёт живот — объясняет кабан Клод за 25 секунд 🍺"),
 "pyatnica": ("pyatnica/output/pyatnica.mp4", "ЧЁРНАЯ ПЯТНИЦА|06:59", "Армия скелетов штурмует ТЦ в Чёрную пятницу. Финал неожиданный 💀"),
 "redkost":  ("redkost/output/redkost.mp4", "УРОВНИ РЕДКОСТИ|КАБАНОВ", "Rare, Epic, Mythic — какой кабан выпал тебе? 🐗✨"),
 "maikl":    ("ruslan/output/maikl_3d.mp4", "МАЙКЛ|ИЗ ТЕХАСА", "Руслан стал Майклом из Техаса. Кабан Клод в шоке 🤠"),
 "telefon":  ("telefon/output/telefon.mp4", "ВОЗЬМИ ТЕЛЕФОН,|ДЕТКА", "Возьми телефон, детка — версия с кабаном 📞🐗"),
 "vmoskve":  ("vmoskve/output/vmoskve.mp4", "Я В МОСКВЕ", "Я в Москве. А кабан где? 🏙️🐗"),
 "vozduhan": ("vozduhan/output/vozduhan_3d.mp4", "ВОЗДУХАН", "Воздухан. Кабан Клод объясняет, что это такое 💨"),
 "zakryv":   ("zakryv/output/zakryv.mp4", "ВЫ УЖЕ|ЗАКРЫВАЕТЕСЬ?", "— Вы уже закрываетесь? — Мы же не собаки. — Десять шаурмы. — ГАВ! 🐶🌯"),
}


def run(cmd): subprocess.run(cmd, check=True, cwd=ROOT)


def endcard_png(path):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920">{U.DEFS}'
           + U.endcard(9.0, 0.0, "", WORD, WHAT, "А тебе какой мультик снять?") + "</svg>")
    Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).save(path)


if __name__ == "__main__":
    slug = sys.argv[1]; src, hook, cap = ITEMS[slug]
    card = os.path.join(TMP, "endcard.png"); endcard_png(card)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(ROOT, src)]))
    a = os.path.join(TMP, f"{slug}_end.mp4")
    flt = (f"[0:v]scale=1080:1920,tpad=stop_mode=clone:stop_duration=2.6[v0];[1:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1[c];"
           f"[v0][c]overlay=0:0:enable='gte(t,{d:.2f})':eof_action=repeat,format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-loop", "1", "-t", f"{d + 2.6:.2f}", "-i", card, "-filter_complex", flt,
         "-af", "apad=pad_dur=2.6", "-map", "[v]", "-map", "0:a", "-t", f"{d + 2.6:.2f}", "-c:v", "libx264", "-crf", "19", "-c:a", "aac", a])
    u = os.path.join(TMP, f"{slug}_u.mp4"); run([sys.executable, "reels/uniq.py", a, u])
    out = os.path.join(ROOT, os.path.dirname(src), f"{slug}_retrial.mp4")
    subprocess.run([sys.executable, "reels/promo.py", "cover", u, out, hook, "--color", "pink"], check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
    capf = os.path.join(TMP, f"{slug}.txt")
    open(capf, "w", encoding="utf-8").write(f"{cap}\nЭтот мультик целиком сделала нейросеть Claude.\n\nНапиши {WORD} в комментариях — {WHAT} 👇\n\n{TAGS}\n")
    for f in (a, u): os.remove(f)
    if "--dry" in sys.argv: print("ready", out); sys.exit()
    r = subprocess.run([sys.executable, "reels/ig_post.py", "post", out, capf, "--cover-ms", "700", "--trial"], cwd=ROOT, capture_output=True, text=True)
    print(slug, (r.stdout.strip().splitlines() or [""])[-1], r.stderr[-200:])
