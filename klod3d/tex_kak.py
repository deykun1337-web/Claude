"""Textures for the «как я делаю мультики» explainer."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont
from tex import PX, OUT
F = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
if not os.path.exists(MONO): MONO = F
w = PX(16, 16, "#B47B4B", 71, 8)
for y in range(0, 16, 4): w.p(0, y, "#8E5C34", 16, 1, 4)
for y in range(0, 16, 4): w.p((y * 5) % 16, y, "#8E5C34", 1, 4, 3)
w.save("plank_floor")
v = PX(16, 16, "#6E4A30", 72, 8)
for x in range(0, 16, 4): v.p(x, 0, "#53351F", 1, 16, 4)
v.save("plank_wall")


def screen(name, bg, lines, title=None, tcol=(217, 119, 87)):
    im = Image.new("RGB", (512, 320), bg); d = ImageDraw.Draw(im)
    if title: d.text((24, 18), title, fill=tcol, font=ImageFont.truetype(F, 44))
    f = ImageFont.truetype(MONO, 22)
    for k, (txt, col) in enumerate(lines): d.text((24, 90 + k * 34), txt, fill=col, font=f)
    im.save(os.path.join(OUT, name + ".png"))


screen("scr_claude", (18, 16, 20), [("> сделай трендовый мультик", (240, 240, 240)), ("● ищу тренды...", (217, 119, 87)), ("● пишу сценарий", (160, 160, 170)), ("● озвучка · 3D · монтаж", (160, 160, 170))], "CLAUDE CODE")
screen("scr_render", (18, 16, 20), [("blender: кадр 347 / 500", (240, 240, 240)), ("████████████░░░░  69%", (217, 119, 87)), ("eevee · 720x1280 · 24fps", (160, 160, 170))], "RENDER")
# trend graph
im = Image.new("RGB", (512, 320), (14, 20, 34)); d = ImageDraw.Draw(im)
d.text((24, 16), "ТРЕНДЫ", fill=(120, 220, 255), font=ImageFont.truetype(F, 44))
pts = [(30, 280), (110, 250), (190, 262), (270, 200), (350, 150), (430, 80), (490, 40)]
d.line(pts, fill=(61, 220, 132), width=10)
for x, y in pts: d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(255, 255, 255))
im.save(os.path.join(OUT, "scr_trend.png"))
# script page
im = Image.new("RGB", (360, 480), (246, 242, 232)); d = ImageDraw.Draw(im)
d.text((24, 20), "СЦЕНАРИЙ", fill=(30, 30, 30), font=ImageFont.truetype(F, 46))
for k in range(9): d.rectangle([24, 100 + k * 40, 24 + [300, 260, 310, 200, 290, 240, 300, 180, 270][k], 112 + k * 40], fill=(120, 120, 130))
im.save(os.path.join(OUT, "scr_script.png"))
# card «подписка»
im = Image.new("RGB", (400, 250), (217, 119, 87)); d = ImageDraw.Draw(im)
d.text((30, 30), "CLAUDE", fill=(255, 255, 255), font=ImageFont.truetype(F, 60)); d.text((30, 150), "подписка", fill=(255, 240, 230), font=ImageFont.truetype(F, 50))
im.save(os.path.join(OUT, "card_sub.png"))
# phone screen: a frame of the previous reel
src = "/home/user/Claude/zakryv/output/zakryv.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "8.8", "-i", src, "-frames:v", "1", "-vf", "scale=360:640", os.path.join(OUT, "phone_reel.png")], check=True)
print("ok")
