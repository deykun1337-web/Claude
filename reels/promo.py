"""Promo helpers for @deykun1337 reels (fast ffmpeg passes, no re-render).

  cover <in.mp4> <out.mp4> "<ХУК В 2 СТРОКИ>" [--color yellow|pink|orange]
      Burns a bold cover-title plate into the first 1.4 s (pops in, fades out) in the middle of the frame,
      so the frame at --cover-ms 700 is a designed cover (readable in the 3:4 profile grid) and the
      first second has a strong text hook. Main and trial versions get DIFFERENT hooks → A/B test.
  story <in.mp4> <out.mp4> "<СЛОВО>" [start_s]
      9-second story teaser from the reel: top plate «НОВЫЙ РИЛС», bottom plate «Смотри в профиле · пиши <СЛОВО>».

Prints the cover offset in ms to pass to ig_post.py (--cover-ms).
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
COL = {"yellow": ("#FFE27A", "#14161C"), "pink": ("#F0569A", "#FFFFFF"), "orange": ("#D97757", "#FFFFFF"), "white": ("#FFFFFF", "#14161C")}


def plate(lines, bg, fg, width=980, size=104, pad=46, radius=46):
    f = ImageFont.truetype(FONT, size)
    while max(f.getlength(l) for l in lines) > width - 2 * pad and size > 40:
        size -= 4; f = ImageFont.truetype(FONT, size)
    lh = int(size * 1.12); w = int(max(f.getlength(l) for l in lines) + 2 * pad); h = lh * len(lines) + 2 * pad - int(size * 0.12)
    im = Image.new("RGBA", (w + 24, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([12, 22, w + 12, h + 22], radius, fill=(0, 0, 0, 110))          # shadow
    d.rounded_rectangle([12, 8, w + 12, h + 8], radius, fill=bg)
    for k, l in enumerate(lines):
        d.text((12 + (w - f.getlength(l)) / 2, 8 + pad + k * lh - int(size * 0.1)), l, font=f, fill=fg)
    return im


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def cover(src, out, text, color="yellow"):
    bg, fg = COL.get(color, COL["yellow"])
    lines = [l.strip() for l in text.upper().split("|")] if "|" in text else _split(text.upper())
    p = plate(lines, bg, fg)
    tmp = tempfile.mkdtemp(); png = os.path.join(tmp, "c.png"); p.save(png)
    # pop-in scale 0.6→1 in 0.18 s, hold, fade out at 1.15–1.4 s; centred slightly above middle (grid-safe)
    flt = ("[1:v]format=rgba,scale=w='iw*min(1,0.6+t/0.45)':h=-1:eval=frame,fade=t=out:st=1.15:d=0.25:alpha=1[c];"
           "[0:v][c]overlay=x=(W-w)/2:y=H*0.63-h/2:enable='lt(t,1.4)',format=yuv420p[v]")
    ff(["-i", src, "-loop", "1", "-t", "1.5", "-i", png, "-filter_complex", flt, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264",
        "-preset", "medium", "-crf", "19", "-c:a", "copy", "-movflags", "+faststart", out])
    print(700)


def _split(t):
    w = t.split(); best = [t]
    if len(t) > 14:
        mid = len(t) / 2; acc = 0
        for i, x in enumerate(w):
            acc += len(x) + 1
            if acc >= mid: best = [" ".join(w[:i + 1]), " ".join(w[i + 1:])]; break
    return [b for b in best if b]


def story(src, out, word, start=0.0):
    tmp = tempfile.mkdtemp()
    top = plate(["НОВЫЙ РИЛС"], "#F0569A", "#FFFFFF", size=80); top.save(os.path.join(tmp, "t.png"))
    bot = plate(["Смотри в профиле", f"пиши {word.upper()} в комментах"], "#FFFFFF", "#14161C", size=64); bot.save(os.path.join(tmp, "b.png"))
    flt = ("[0:v]trim=start={s}:duration=9,setpts=PTS-STARTPTS[v0];[v0][1:v]overlay=x=(W-w)/2:y=170[v1];"
           "[v1][2:v]overlay=x=(W-w)/2:y=H-h-260,format=yuv420p[v]").format(s=start)
    ff(["-i", src, "-i", os.path.join(tmp, "t.png"), "-i", os.path.join(tmp, "b.png"), "-filter_complex", flt,
        "-af", f"atrim=start={start}:duration=9,asetpts=PTS-STARTPTS,afade=t=out:st=8.4:d=0.6", "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
    print("story", out)


if __name__ == "__main__":
    a = sys.argv
    if len(a) >= 5 and a[1] == "cover":
        cover(a[2], a[3], a[4], a[a.index("--color") + 1] if "--color" in a else "yellow")
    elif len(a) >= 5 and a[1] == "story":
        story(a[2], a[3], a[4], float(a[5]) if len(a) > 5 else 0.0)
    else:
        print(__doc__)
