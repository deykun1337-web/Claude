"""Blender: dialog sketch «Друг занял 5000» — night room with pink neon, Ruslan v2 (pink DEYKUN cap) + Klod. Blocky 3D.
Usage: blender -b -P dolg3d.py -- plan.json outdir start end"""
import bpy, json, math, os, random, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "scene3d.py")).read()
exec(_src[:_src.index("# ------------------------------------------------------------- characters")])
ee = sc.eevee
ee.taa_render_samples = 12; ee.bloom_intensity = 0.1; ee.bloom_threshold = 0.8; ee.bloom_radius = 6.5
ee.use_ssr = False; ee.use_gtao = True; ee.gtao_distance = 0.15
sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.3
S, E = PLAN["S"], PLAN["E"]
HIDE = (0, 0, -50)


def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


# ================================================================ night room
world((0.01, 0.012, 0.03), 0.4)
wallm = mat_col("wall", "#1B1E33", 0.85); floorm = mat_tex("floor", "plank_floor", 0.35)
box("floor", 14, 12, 0.1, (0, 2, -0.05), {"other": floorm})
box("back", 14, 0.2, 6, (0, 3.2, 3), {"other": wallm})
box("left", 0.2, 10, 6, (-3.6, 0, 3), {"other": wallm}); box("right", 0.2, 10, 6, (3.6, 0, 3), {"other": wallm})
city = mat_tex("city", "city", 0.9, emit=1.3)
box("window", 2.2, 0.05, 1.8, (-1.6, 3.08, 2.1), {"front": city, "other": wallm})
frame = mat_col("frame", "#0C0D14", 0.5)
for (w, h, x, z) in ((2.4, 0.1, -1.6, 3.05), (2.4, 0.1, -1.6, 1.15), (0.1, 2.0, -2.75, 2.1), (0.1, 2.0, -0.45, 2.1), (0.06, 1.8, -1.6, 2.1)):
    box("wf", w, 0.1, h, (x, 3.02, z), {"other": frame})
pinkneon = mat_col("pinkneon", "#FF4FA8", 0.3, emit=16); violet = mat_col("violet", "#7A5CFF", 0.3, emit=12)
box("neon1", 5.5, 0.05, 0.05, (0.8, 3.06, 3.6), {"other": pinkneon})
box("neon2", 0.05, 0.05, 2.2, (3.45, 2.9, 1.6), {"other": violet})
point("pinkL", (0.8, 2.6, 3.4), 220, (1.0, 0.35, 0.7)); point("violetL", (3.2, 2.6, 1.6), 140, (0.5, 0.4, 1.0))
# shelf with glowing «Claude» starburst sign + plants + speaker
box("shelf", 1.6, 0.35, 0.05, (1.8, 2.95, 1.9), {"other": mat_col("shelfm", "#2B2F45", 0.5)})
orange = mat_col("orange", "#FF9A5A", 0.3, emit=12)
for k in range(8):
    a = k * math.pi / 4
    b = box("ray", 0.05, 0.05, 0.28, (1.3 + 0.12 * math.sin(a), 3.0, 2.35 + 0.12 * math.cos(a)), {"other": orange}); b.rotation_euler = (0, a, 0)
box("speaker", 0.3, 0.3, 0.45, (2.2, 2.95, 2.15), {"other": mat_col("spk", "#14151C", 0.4)})
box("pot", 0.3, 0.3, 0.3, (-3.0, 2.6, 0.15), {"other": mat_col("pot", "#C65D3B", 0.6)})
rr = random.Random(5)
for k in range(5): box("leaf", 0.1, 0.1, rr.uniform(0.5, 0.9), (-3.0 + rr.uniform(-0.12, 0.12), 2.6 + rr.uniform(-0.12, 0.12), 0.6), {"other": mat_col("leaf", "#2F7A45", 0.6)}).rotation_euler = (rr.uniform(-0.4, 0.4), rr.uniform(-0.4, 0.4), 0)
box("sofa", 2.2, 0.8, 0.45, (0.4, 2.55, 0.23), {"other": mat_col("sofa", "#3B3F6B", 0.8)}); box("sofab", 2.2, 0.25, 0.7, (0.4, 2.9, 0.6), {"other": mat_col("sofa2", "#33375E", 0.8)})
rug = mat_col("rug", "#5B3A6E", 0.9)
box("rug", 3.2, 2.2, 0.01, (0.1, 0.4, 0.005), {"other": rug})
# dust motes in the light
dust = mat_col("dust", "#FFD9F0", 0.3, emit=6)
MOTES = []
for k in range(40):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rr.uniform(0.008, 0.018), location=HIDE, segments=8, ring_count=6)
    o = bpy.context.object; o.data.materials.append(dust)
    MOTES.append((o, Vector((rr.uniform(-2.2, 2.6), rr.uniform(-1.5, 2.4), rr.uniform(0.3, 3.2))), rr.uniform(0, 6)))
area("key", (-2.0, -3.6, 3.6), (0, 0.3, 1.2), 520, (1.0, 0.85, 0.9), 2.5)
area("fill", (3.0, -2.6, 2.0), (0, 0.3, 1.0), 140, (0.6, 0.7, 1.0), 3.0)
area("rim", (0.3, 2.6, 3.2), (0, 0, 1.2), 420, (1.0, 0.4, 0.75), 2.0)

# ================================================================ characters
RX, KX = -0.8, 0.8
# Ruslan v2: pink DEYKUN cap, friendly face, white tee + gold chain, jeans, 3D nose
R_ROOT = empty("ruslan", (RX, 0, 0), 22)
rface = mat_tex("rface", "r2_face_neutral_0_0", 0.55)
rside = mat_tex("rside", "r2_side"); rback = mat_tex("rback", "r2_back"); rcap = mat_tex("rcap", "r2_cap", 0.5)
tee = mat_tex("tee", "r2_tee"); teeside = mat_tex("teeside", "r2_tee_side"); rarm = mat_tex("rarm", "r2_arm"); jeans = mat_tex("jeans", "r2_jeans")
skin = mat_col("skin", "#EBC3A5", 0.55); shoe = mat_col("shoe", "#F4F4F4", 0.5)
for sx in (-0.125, 0.125):
    box("leg", 0.25, 0.25, 0.75, (sx, 0, 0.375), {"other": jeans}, R_ROOT)
    box("shoe", 0.27, 0.34, 0.1, (sx, -0.04, 0.05), {"other": shoe}, R_ROOT)
box("rbody", 0.52, 0.28, 0.76, (0, 0, 1.13), {"front": tee, "other": teeside}, R_ROOT)
HEAD = empty("head", (0, 0, 1.51), 0, R_ROOT)
box("rhead", 0.5, 0.5, 0.5, (0, 0, 0.25), {"front": rface, "back": rback, "top": rcap, "other": rside}, HEAD)
box("nose", 0.09, 0.08, 0.11, (0, -0.28, 0.2), {"other": skin}, HEAD)
pinkc = mat_col("pinkc", "#F0569A", 0.45)
box("capb", 0.54, 0.54, 0.12, (0, 0, 0.53), {"top": rcap, "other": pinkc}, HEAD)
box("brim", 0.5, 0.26, 0.04, (0, -0.36, 0.48), {"other": mat_col("brim", "#E04A8C", 0.5)}, HEAD)
logo = mat_col("logo", "#FFFFFF", 0.5)
bpy.ops.object.text_add(location=(0, -0.276, 0.535), rotation=(math.radians(90), 0, 0))
lg = bpy.context.object; lg.data.body = "DEYKUN"; lg.data.size = 0.075; lg.data.align_x = "CENTER"; lg.data.align_y = "CENTER"; lg.data.extrude = 0.004
lg.data.font = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"); lg.data.materials.append(logo); lg.parent = HEAD
ARMS = []
for sx in (-0.39, 0.39):
    sh = empty("shoulder", (sx, 0, 1.47), 0, R_ROOT)
    box("arm", 0.24, 0.26, 0.74, (0, 0, -0.35), {"other": rarm}, sh); ARMS.append(sh)
PHONE = empty("phone", (0, 0, 0), 0, ARMS[1])
box("ph", 0.14, 0.03, 0.26, (0, -0.15, -0.74), {"front": mat_col("phs", "#9AD7FF", 0.3, emit=4), "other": mat_col("phb", "#15161A", 0.4)}, PHONE).rotation_euler = (math.radians(65), 0, 0)

# Klod
K_ROOT = empty("klod", (KX, 0, 0), -20)
kface = mat_tex("kface", "klod_face_neutral_0_0", 0.6)
kside = mat_tex("kside", "klod_side"); ktop = mat_tex("ktop", "klod_top"); kdark = mat_tex("kdark", "klod_dark")
ksnout = mat_tex("ksnout", "klod_snout", 0.5); tusk = mat_col("tusk", "#FFF6E6", 0.3)
for lx in (-0.36, 0.36):
    for ly in (-0.22, 0.22): box("kleg", 0.17, 0.17, 0.3, (lx, ly, 0.15), {"other": kdark}, K_ROOT)
box("kbody", 1.0, 0.75, 0.75, (0, 0, 0.675), {"front": kface, "top": ktop, "other": kside}, K_ROOT)
box("snout", 0.38, 0.15, 0.19, (0, -0.445, 0.56), {"other": ksnout}, K_ROOT)
for tx in (-0.25, 0.25): box("tusk", 0.05, 0.05, 0.14, (tx, -0.4, 0.55), {"other": tusk}, K_ROOT)
for ex in (-0.39, 0.39): box("ear", 0.17, 0.1, 0.17, (ex, -0.22, 1.13), {"other": kdark}, K_ROOT)
krr = random.Random(4)
for k in range(7): box("mane", 0.07, 0.07, krr.uniform(0.06, 0.13), (-0.2 + k * 0.065, -0.05 + krr.uniform(-0.1, 0.1), 1.08), {"other": kdark}, K_ROOT)
box("cushion", 1.2, 0.95, 0.35, (KX, 0.05, 0.175), {"other": mat_col("cush", "#FF7DB4", 0.85)})
K_ROOT.location.z = 0.35

# money rain (line 6)
gold = mat_col("gold", "#F2B53A", 0.25, metal=0.9); bill = mat_col("bill", "#5FB86A", 0.6)
MONEY = []
for k in range(40):
    if k % 2:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.025, vertices=20, location=HIDE); o = bpy.context.object; o.data.materials.append(gold)
    else:
        o = box("bill", 0.3, 0.01, 0.15, HIDE, {"other": bill})
    MONEY.append((o, Vector((rr.uniform(-1.6, 1.6), rr.uniform(-1.0, 0.8))), rr.uniform(0, 1.2), rr.uniform(0, 6)))

C = bpy.data.cameras.new("cam"); C.sensor_fit = "VERTICAL"; C.sensor_height = 24; C.dof.use_dof = True
CO = bpy.data.objects.new("cam", C); bpy.context.collection.objects.link(CO); sc.camera = CO

RHEAD = Vector((RX, 0, 1.76)); KFACE = Vector((KX, -0.35, 1.0))


def shot(F, t):
    s, bt = F["shot"], F["bt"]; p = ease(bt / 2.5)
    if s == "r":   return RHEAD + Vector((0.95, -3.2 + 0.4 * p, -0.1)), RHEAD + Vector((0.12, 0, -0.3)), 36, 2.2
    if s == "rz":  return RHEAD + Vector((0.35, -2.6 + 0.6 * ease(bt / 0.25), 0.0)), RHEAD + Vector((0.0, 0, -0.08)), 40, 2.0
    if s == "rp":  return RHEAD + Vector((1.1, -3.0 + 0.3 * p, -0.35)), RHEAD + Vector((0.2, 0, -0.4)), 34, 2.2
    if s == "k":   return KFACE + Vector((-0.9, -3.4 + 0.4 * p, 0.45)), KFACE + Vector((0, 0, -0.05)), 34, 2.2
    if s == "kl":  return KFACE + Vector((-0.6, -3.0 + 0.3 * p, -0.5)), KFACE + Vector((0, 0, 0.2)), 30, 2.2
    if s == "ko":
        a = math.radians(-30 + 40 * p); return KFACE + Vector((3.3 * math.sin(a), -3.3 * math.cos(a), 0.35)), KFACE + Vector((0, 0, -0.05)), 34, 2.2
    if s == "kr":  return KFACE + Vector((-1.1, -3.2, 0.6)), KFACE + Vector((-0.2, 0, -0.05)), 34, 2.2
    if s == "two": return Vector((0.0, -5.0 + 0.4 * p, 1.5)), Vector((0.0, 0.0, 1.2)), 30, 4.0
    k = ease(bt / 3.0); return Vector((0.0, -4.4 - 0.8 * k, 1.4 + 0.2 * k)), Vector((0.0, 0.0, 1.15)), 30, 4.0   # "out"


frames = PLAN["frames"]
for fr in range(START, min(END, len(frames))):
    F = frames[fr]; t = F["t"]; r, k = F["r"], F["k"]; rnd = random.Random(fr)
    set_tex(rface, f'r2_face_{r["expr"]}_{r["m"]}_{r["b"]}')
    set_tex(kface, f'klod_face_{k["expr"]}_{k["m"]}_{k["b"]}')
    # Ruslan body language
    talk_r = r["m"] > 0
    HEAD.rotation_euler = (math.radians(3 * math.sin(t * 2.3) + (4 if talk_r else 0) * math.sin(t * 7)), 0, math.radians(5 * math.sin(t * 1.1)))
    phone_up = F["phone"]
    ARMS[1].rotation_euler = (math.radians(-70 * phone_up - (12 * math.sin(t * 6) if talk_r and not phone_up else 0)), 0, math.radians(-15 * phone_up))
    ARMS[0].rotation_euler = (math.radians(-35 * F["gesture"] * (0.6 + 0.4 * math.sin(t * 5))), 0, math.radians(25 * F["gesture"]))
    PHONE.location = (0, 0, 0) if phone_up > 0.5 else HIDE
    R_ROOT.location.z = 0.18 * F["jump"]
    # Klod bounce
    K_ROOT.location.z = 0.35 + 0.02 * math.sin(t * 3) + (0.03 * abs(math.sin(t * 9)) if k["m"] > 0 else 0) + 0.2 * F["khop"]
    K_ROOT.rotation_euler = (0, 0, math.radians(-20 + 4 * math.sin(t * 1.4)))
    for o, p0, ph in MOTES:
        o.location = (p0.x + 0.15 * math.sin(t * 0.3 + ph), p0.y + 0.1 * math.cos(t * 0.25 + ph), p0.z + 0.2 * math.sin(t * 0.2 + ph))
    for o, xy, dl, sp in MONEY:
        u = t - (S[6] + 0.6) - dl * 0.6
        if u < 0 or u > 3.5: o.location = HIDE; continue
        z = max(0.02, 3.4 - 4.9 * u * u * 0.6)
        o.location = (xy.x, xy.y, z); o.rotation_euler = ((sp + u * 6) if z > 0.03 else 0, (sp + u * 4) if z > 0.03 else 0, sp)
    p, q, lens, fst = shot(F, t)
    hand = Vector((math.sin(t * 1.7) * 0.012, 0, math.sin(t * 2.3) * 0.01))
    if F["shake"] > 0: hand += Vector((rnd.uniform(-1, 1), 0, rnd.uniform(-1, 1))) * 0.03 * F["shake"]
    CO.location = p + hand; look(CO, q); C.lens = lens; C.dof.aperture_fstop = fst; C.dof.focus_distance = (q - p).length
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
