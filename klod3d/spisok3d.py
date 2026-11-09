"""Blender: listicle «5 вещей, чтобы делать мультики» — night room, Ruslan v2 + Klod, a 3D prop pops up for every step.
Usage: blender -b -P spisok3d.py -- plan.json outdir start end"""
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
RX, KX = -1.25, 0.35
# Ruslan v2: pink DEYKUN cap, friendly face, white tee + gold chain, jeans, 3D nose
R_ROOT = empty("ruslan", (RX, 0.2, 0), 28)
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
K_ROOT = empty("klod", (KX, 0, 0), -12)
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

# ---------------- step props
holo_c = mat_col("holo_c", "#5AD2FF", 0.3, emit=9); holo_o = mat_col("holo_o", "#FF9A5A", 0.3, emit=10); white = mat_col("white", "#F4F6FA", 0.5, emit=0.6)
PROPS = []
p = empty("p_laptop", HIDE)
box("lbase", 0.7, 0.48, 0.04, (0, 0, 0), {"other": mat_col("lap", "#2B2E36", 0.35, metal=0.5)}, p)
scrp = empty("lscr", (0, 0.22, 0.02), 0, p); scrp.rotation_euler = (math.radians(-12), 0, 0)
box("lid", 0.7, 0.03, 0.46, (0, 0, 0.23), {"front": mat_tex("lsc", "scr_claude", 0.4, emit=1.8), "other": mat_col("lap2", "#2B2E36", 0.35, metal=0.5)}, scrp)
PROPS.append(p)
p = empty("p_cloud", HIDE)
for (x, y, z, s_) in ((0, 0, 0.1, 0.42), (-0.28, 0, 0.0, 0.3), (0.28, 0, 0.0, 0.32), (0.1, 0.05, 0.28, 0.3), (-0.15, 0.05, 0.24, 0.26)):
    box("cl", s_, s_, s_, (x, y, z), {"other": white}, p)
box("cph", 0.16, 0.03, 0.3, (0, -0.05, -0.55), {"front": mat_col("cphs", "#9AD7FF", 0.3, emit=4), "other": mat_col("cphb", "#15161A", 0.4)}, p)
for k in range(5): box("dot", 0.03, 0.03, 0.03, (0, -0.03, -0.18 - k * 0.07), {"other": holo_c}, p)
PROPS.append(p)
p = empty("p_cube", HIDE)
L = 0.5
for (x, y, z, w, d, h) in [(0, sy * L / 2, sz * L / 2, L, 0.025, 0.025) for sy in (-1, 1) for sz in (-1, 1)] + \
        [(sx * L / 2, 0, sz * L / 2, 0.025, L, 0.025) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * L / 2, sy * L / 2, 0, 0.025, 0.025, L) for sx in (-1, 1) for sy in (-1, 1)]:
    box("edge", w, d, h, (x, y, z), {"other": holo_c}, p)
box("core", 0.2, 0.2, 0.2, (0, 0, 0), {"other": holo_o}, p)
PROPS.append(p)
p = empty("p_mic", HIDE)
box("mhead", 0.22, 0.22, 0.3, (0, 0, 0.25), {"other": mat_col("grill", "#C9CED6", 0.3, metal=0.8)}, p)
box("mbody", 0.1, 0.1, 0.35, (0, 0, -0.05), {"other": mat_col("mb", "#1E2028", 0.4)}, p)
box("mring", 0.26, 0.04, 0.04, (0, 0, 0.1), {"other": holo_o}, p)
WAVE = []
for k in range(8):
    WAVE.append(box("wv", 0.05, 0.05, 0.3, (-0.6 + k * 0.17 if k < 4 else 0.0, 0, 0.25), {"other": holo_c if k % 2 else holo_o}, p))
for k, wv in enumerate(WAVE): wv.location = ((-0.62 + k * 0.08) if k < 4 else (0.38 + (k - 4) * 0.08), 0, 0.25)
PROPS.append(p)
p = empty("p_bulb", HIDE)
bulb = mat_col("bulbm", "#FFE27A", 0.3, emit=4)
box("bglass", 0.36, 0.36, 0.4, (0, 0, 0.25), {"other": bulb}, p); box("bglass2", 0.26, 0.26, 0.12, (0, 0, 0.5), {"other": bulb}, p)
box("bbase", 0.2, 0.2, 0.18, (0, 0, -0.03), {"other": mat_col("bbase", "#9AA3AE", 0.3, metal=0.8)}, p)
PROPS.append(p)
BULB_L = point("bulbL", HIDE, 0, (1.0, 0.85, 0.4))
PROP_POS = Vector((KX, -0.25, 2.05))

C = bpy.data.cameras.new("cam"); C.sensor_fit = "VERTICAL"; C.sensor_height = 24; C.dof.use_dof = True
CO = bpy.data.objects.new("cam", C); bpy.context.collection.objects.link(CO); sc.camera = CO

RHEAD = Vector((RX, 0, 1.76)); KFACE = Vector((KX, -0.35, 1.0))


def shot(F, t):
    s, bt = F["shot"], F["bt"]; p = ease(bt / 3.0)
    mid = (KFACE + PROP_POS) * 0.5
    if s == "r":   return RHEAD + Vector((0.95, -3.2 + 0.4 * p, -0.1)), RHEAD + Vector((0.12, 0, -0.3)), 36, 2.2
    if s == "rz":  return RHEAD + Vector((0.35, -2.6 + 0.6 * ease(bt / 0.25), 0.0)), RHEAD + Vector((0.0, 0, -0.08)), 40, 2.0
    if s in ("kpL", "kpR"):
        sg = 1 if s == "kpL" else -1; a = math.radians(sg * (-18 + 26 * p))
        c = Vector((KX, -0.3, 1.5)); return c + Vector((4.2 * math.sin(a), -4.2 * math.cos(a), 0.1 - 0.15 * p)), c, 30, 2.8
    if s == "k":   return KFACE + Vector((-0.9, -3.4 + 0.4 * p, 0.45)), KFACE + Vector((0, 0, -0.05)), 34, 2.2
    if s == "ring":
        a = math.radians(-25 + 50 * p); c = KFACE + Vector((0, 0, 0.2)); return c + Vector((4.6 * math.sin(a), -4.6 * math.cos(a), 0.6)), c, 28, 3.5
    if s == "two": return Vector((-0.4, -5.6 + 0.4 * p, 1.6)), Vector((-0.4, 0.0, 1.2)), 30, 4.0
    k = ease(bt / 3.0); return Vector((-0.3, -5.2 - 0.8 * k, 1.5 + 0.2 * k)), Vector((-0.3, 0.0, 1.15)), 30, 4.0


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
    K_ROOT.rotation_euler = (0, 0, math.radians(-12 + 4 * math.sin(t * 1.4)))
    for o, p0, ph in MOTES:
        o.location = (p0.x + 0.15 * math.sin(t * 0.3 + ph), p0.y + 0.1 * math.cos(t * 0.25 + ph), p0.z + 0.2 * math.sin(t * 0.2 + ph))
    st, sbt = F["step"], F["sbt"]
    for n, pr in enumerate(PROPS):
        if F["ring"] > 0:
            a = t * 0.9 + n * 2 * math.pi / 5; R = 1.35
            pr.location = (KX + R * math.cos(a), 0.1 + R * 0.6 * math.sin(a), 1.3 + 0.25 * math.sin(a * 2)); pr.scale = (0.75,) * 3
            pr.rotation_euler = (0, 0, t * 1.5 + n)
        elif n == st:
            sc_ = ease(sbt / 0.25) * (1 + 0.15 * math.sin(min(1, sbt / 0.4) * math.pi))
            pr.location = PROP_POS + Vector((0, 0, 0.06 * math.sin(t * 2.4))); pr.scale = (max(sc_, 0.001),) * 3
            pr.rotation_euler = (0, 0, math.radians(-25) + 0.6 * math.sin(t * 1.2) + (t * 1.2 if n == 2 else 0))
        else:
            pr.location = HIDE
    for k_, wv in enumerate(WAVE): wv.scale = (1, 1, 0.3 + 2.2 * F["env"] * (0.5 + 0.5 * abs(math.sin(k_ * 1.3 + t * 12))))
    BULB_L.location = PROP_POS + Vector((0, -0.3, 0.3)) if (st == 4 and F["ring"] == 0) else HIDE
    BULB_L.data.energy = 60 if st == 4 else 0
    p, q, lens, fst = shot(F, t)
    hand = Vector((math.sin(t * 1.7) * 0.012, 0, math.sin(t * 2.3) * 0.01))
    if F["shake"] > 0: hand += Vector((rnd.uniform(-1, 1), 0, rnd.uniform(-1, 1))) * 0.03 * F["shake"]
    CO.location = p + hand; look(CO, q); C.lens = lens; C.dof.aperture_fstop = fst; C.dof.focus_distance = (q - p).length
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
