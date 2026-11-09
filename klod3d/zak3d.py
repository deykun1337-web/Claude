"""Blender: «Вы уже закрываетесь?» — night shawarma kiosk «У КЛОДА», rain, neon, roll shutter. Blocky 3D.
Usage: blender -b -P zak3d.py -- plan.json outdir start end"""
import bpy, json, math, os, random, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "scene3d.py")).read()
exec(_src[:_src.index("# ------------------------------------------------------------- characters")])
ee = sc.eevee
ee.taa_render_samples = 16; ee.bloom_intensity = 0.1; ee.bloom_threshold = 0.8; ee.bloom_radius = 6
ee.use_ssr = True; ee.use_ssr_refraction = False; ee.ssr_quality = 0.5; ee.ssr_thickness = 0.4
ee.use_volumetric_lights = True; ee.volumetric_tile_size = "8"; ee.volumetric_samples = 24; ee.volumetric_end = 30
sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.4
S, E, SLAM, UP, FR0, FR1 = PLAN["S"], PLAN["E"], PLAN["slam"], PLAN["up"], PLAN["fr0"], PLAN["fr1"]
FONT = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf")


def text3d(body, loc, size, mat, extrude=0.02, parent=None):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, 0))
    o = bpy.context.object; o.data.body = body; o.data.font = FONT; o.data.size = size; o.data.extrude = extrude
    o.data.bevel_depth = 0.004; o.data.align_x = "CENTER"; o.data.align_y = "CENTER"; o.data.materials.append(mat)
    if parent: o.parent = parent
    return o


def cam(name, lens, fstop):
    c = bpy.data.cameras.new(name); c.lens = lens; c.sensor_fit = "VERTICAL"; c.sensor_height = 24
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, c); bpy.context.collection.objects.link(o); return o


HIDE = (0, 0, -50)

# ================================================================ world: rainy night street
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes["Background"]; bg.inputs[0].default_value = (0.012, 0.018, 0.045, 1); bg.inputs[1].default_value = 1.0
vol = nt.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Density"].default_value = 0.018; vol.inputs["Color"].default_value = (0.7, 0.75, 0.9, 1)
nt.links.new(vol.outputs[0], nt.nodes["World Output"].inputs["Volume"])

wet = mat_tex("wet", "asphalt", 0.12)
box("street", 40, 30, 0.1, (0, 8, -0.05), {"other": wet})
puddle = mat_col("puddle", "#0B0E16", 0.02)
rr = random.Random(3)
for k in range(9):
    box("puddle", rr.uniform(0.6, 1.8), rr.uniform(0.4, 1.0), 0.012, (rr.uniform(-4, 4), rr.uniform(-4.5, -0.6), 0.006), {"other": puddle})
curb = mat_col("curb", "#55585E", 0.6)
box("curb", 40, 0.3, 0.16, (0, 3.6, 0.08), {"other": curb})
# far city: building blocks with lit windows
city = mat_tex("city", "city", 0.9, emit=1.4); dark = mat_col("dark", "#0A0C14", 0.8)
for k in range(10):
    bw = rr.uniform(2.0, 3.6); bh = rr.uniform(5, 11)
    box("bld", bw, 2.0, bh, (-11 + k * 2.6 + rr.uniform(-0.4, 0.4), rr.uniform(11, 15), bh / 2), {"front": city, "other": dark})

# ================================================================ kiosk «ШАУРМА У КЛОДА»
KX = 0.7
wall = mat_tex("kwall", "kiosk_wall", 0.6); tile = mat_tex("tile", "tile_white", 0.3); roof = mat_tex("roof", "roof", 0.5)
steel = mat_col("steel", "#B9C0C8", 0.25, metal=0.8)
box("pillarL", 0.4, 0.1, 2.8, (KX - 1.05, 0.05, 1.4), {"other": wall})
box("pillarR", 0.4, 0.1, 2.8, (KX + 1.05, 0.05, 1.4), {"other": wall})
box("under", 1.7, 0.1, 0.95, (KX, 0.05, 0.475), {"other": wall})
box("over", 1.7, 0.1, 0.6, (KX, 0.05, 2.5), {"other": wall})
box("sideL", 0.1, 2.3, 2.8, (KX - 1.2, 1.15, 1.4), {"front": wall, "other": wall})
box("sideR", 0.1, 2.3, 2.8, (KX + 1.2, 1.15, 1.4), {"other": wall})
box("back", 2.5, 0.1, 2.8, (KX, 2.25, 1.4), {"other": tile})
box("roof", 2.8, 2.6, 0.14, (KX, 1.15, 2.87), {"other": roof})
box("ledge", 1.85, 0.36, 0.06, (KX, -0.17, 0.98), {"other": steel})
box("counter", 1.7, 0.55, 0.06, (KX, 0.35, 0.92), {"other": steel})
box("counterfront", 1.7, 0.05, 0.9, (KX, 0.6, 0.45), {"other": steel})
# sign + neon
box("sign", 2.7, 0.18, 0.66, (KX, -0.02, 3.27), {"other": mat_col("signb", "#14161D", 0.5)})
neo = mat_col("neo", "#FF8A1F", 0.3, emit=14); cyan = mat_col("cyan", "#38E1FF", 0.3, emit=12)
text3d("ШАУРМА", (KX, -0.13, 3.36), 0.34, neo)
text3d("У КЛОДА", (KX, -0.13, 3.1), 0.17, cyan)
point("neoL", (KX, -0.9, 3.2), 120, (1.0, 0.55, 0.15))
openm = mat_col("openm", "#3DFF7A", 0.3, emit=10); closedm = mat_col("closedm", "#FF2A3A", 0.3, emit=12)
OPEN = text3d("ОТКРЫТО", (KX, -0.02, 2.55), 0.16, openm); CLOSED = text3d("ЗАКРЫТО", (KX, -0.02, 2.55), 0.16, closedm)
# interior: lamp, clock, doner, shelves
box("lamp", 1.2, 0.3, 0.04, (KX, 1.1, 2.78), {"other": mat_col("lampm", "#FFF1D6", 0.3, emit=8)})
IN_L = area("inside", (KX, 1.0, 2.7), (KX, 0.6, 0.0), 380, (1.0, 0.82, 0.6), 1.2)
clockm = mat_col("clockm", "#FF2A3A", 0.3, emit=10)
box("clockbox", 0.62, 0.06, 0.26, (KX - 0.55, 2.18, 2.0), {"other": mat_col("clb", "#111111", 0.4)})
CLK1 = text3d("23:59", (KX - 0.55, 2.14, 2.0), 0.17, clockm); CLK2 = text3d("00:00", (KX - 0.55, 2.14, 2.0), 0.17, clockm)
DONER = empty("doner", (KX + 0.62, 1.55, 0.95))
donm = mat_tex("donm", "doner", 0.45)
for k in range(9):
    s = 0.34 - abs(k - 4) * 0.025
    b = box("dn", s, s, 0.1, (0, 0, 0.1 + k * 0.1), {"other": donm}, DONER); b.rotation_euler = (0, 0, k * 0.4)
box("spit", 0.03, 0.03, 1.25, (0, 0, 0.6), {"other": steel}, DONER)
box("heater", 0.55, 0.06, 0.9, (KX + 0.62, 1.95, 1.45), {"other": mat_col("heat", "#FF6A1F", 0.4, emit=6)})
point("heatL", (KX + 0.62, 1.7, 1.4), 60, (1.0, 0.45, 0.15))
shelf = mat_col("shelf", "#C9CED4", 0.3, metal=0.5)
box("shelf", 1.0, 0.25, 0.04, (KX - 0.45, 2.1, 1.55), {"other": shelf})
for k, c in enumerate(["#E8242C", "#FFFFFF", "#FFC21F", "#E8242C", "#3DDC84", "#FFFFFF"]):
    box("sauce", 0.1, 0.1, 0.24, (KX - 0.85 + k * 0.16, 2.1, 1.69), {"other": mat_col(f"sc{k}", c, 0.25)})
# roll shutter (slats roll down from the housing)
box("housing", 1.82, 0.28, 0.22, (KX, -0.1, 2.31), {"other": mat_col("hous", "#6E747C", 0.4, metal=0.6)})
slatm = mat_tex("slatm", "slat", 0.35)
SLATS = [box("slat", 1.72, 0.05, 0.1, HIDE, {"other": slatm}) for k in range(13)]
STICK = text3d("ЗАКРЫТО", (0, -0.035, 0.0), 0.15, mat_col("stk", "#E01A2A", 0.5), 0.005, SLATS[3])
STICK2 = text3d("ДАЖЕ ДЛЯ ТЕБЯ", (0, -0.035, 0.0), 0.07, mat_col("stk2", "#FFFFFF", 0.5), 0.005, SLATS[2])
# shawarma rolls appearing on the ledge during the frenzy
lav = mat_tex("lav", "lavash", 0.55)
ROLLS = []
POS = [(-0.33, 0), (-0.11, 0), (0.11, 0), (0.33, 0), (-0.22, 1), (0, 1), (0.22, 1), (-0.11, 2), (0.11, 2), (0, 3)]
for k, (x, row) in enumerate(POS):
    r = box("roll", 0.2, 0.13, 0.13, HIDE, {"other": lav}); ROLLS.append((r, (KX - 0.48 + x * 0.9, -0.2, 1.08 + row * 0.13)))
# street lamp
pole = mat_col("pole", "#2B2F36", 0.4, metal=0.6)
box("pole", 0.12, 0.12, 4.2, (-2.7, -1.6, 2.1), {"other": pole}); box("arm", 1.0, 0.1, 0.1, (-2.25, -1.6, 4.15), {"other": pole})
box("lampbox", 0.4, 0.25, 0.12, (-1.85, -1.6, 4.08), {"other": mat_col("sod", "#FFB65A", 0.3, emit=12)})
sl = bpy.data.lights.new("street", "SPOT"); sl.energy = 1400; sl.color = (1.0, 0.7, 0.4); sl.spot_size = math.radians(70); sl.spot_blend = 0.5; sl.shadow_soft_size = 0.3
slo = bpy.data.objects.new("street", sl); bpy.context.collection.objects.link(slo); slo.location = (-1.85, -1.6, 4.0); look(slo, Vector((-1.2, -0.8, 0)))
area("moon", (4.0, -5.0, 6.0), (0, 1, 1), 160, (0.55, 0.65, 1.0), 6.0)
area("rimback", (-1.0, 4.5, 3.5), (-0.5, 0, 1.2), 350, (0.4, 0.55, 1.0), 3.0)

# ================================================================ characters
# Klod the boar (inside, behind the counter, standing on a crate)
K_ROOT = empty("klod", (KX + 0.05, 0.8, 0.62), 0)
kface = mat_tex("kface", "klod_face_neutral_0_0", 0.6)
kside = mat_tex("kside", "klod_side"); ktop = mat_tex("ktop", "klod_top"); kdark = mat_tex("kdark", "klod_dark")
ksnout = mat_tex("ksnout", "klod_snout", 0.5); tusk = mat_col("tusk", "#FFF6E6", 0.3)
for lx in (-0.36, 0.36):
    for ly in (-0.22, 0.22): box("kleg", 0.17, 0.17, 0.3, (lx, ly, 0.15), {"other": kdark}, K_ROOT)
box("kbody", 1.0, 0.75, 0.75, (0, 0, 0.675), {"front": kface, "top": ktop, "other": kside}, K_ROOT)
box("snout", 0.38, 0.15, 0.19, (0, -0.445, 0.56), {"other": ksnout}, K_ROOT)
for tx in (-0.25, 0.25): box("tusk", 0.05, 0.05, 0.14, (tx, -0.4, 0.55), {"other": tusk}, K_ROOT)
for ex in (-0.39, 0.39): box("ear", 0.17, 0.1, 0.17, (ex, -0.22, 1.13), {"other": kdark}, K_ROOT)
apron = mat_col("apron", "#F4F4F0", 0.6, emit=0.35)
box("apron", 0.82, 0.03, 0.3, (0, -0.39, 0.42), {"other": apron}, K_ROOT)
HAT = empty("hat", HIDE, 0, K_ROOT)
box("hatband", 0.5, 0.42, 0.1, (0, 0, 0.05), {"other": apron}, HAT); box("hatpuff", 0.6, 0.5, 0.22, (0, 0, 0.2), {"other": apron}, HAT)
krr = random.Random(4)
for k in range(7):
    box("mane", 0.07, 0.07, krr.uniform(0.06, 0.13), (-0.2 + k * 0.065, -0.05 + krr.uniform(-0.1, 0.1), 1.08), {"other": kdark}, K_ROOT)
box("crate", 1.1, 0.8, 0.62, (KX + 0.05, 0.8, 0.31), {"other": mat_col("crate", "#6B4A2E", 0.7)})

# Ruslan (cap, puffer jacket); arms on shoulder pivots
R_ROOT = empty("ruslan", (-4.0, -0.75, 0), 0)
rface = mat_tex("rface", "ruslan_face_neutral_0_0", 0.55)
rside = mat_tex("rside", "ruslan_side"); rcap = mat_tex("rcap", "ruslan_cap"); pf = mat_tex("pfront", "puffer_front", 0.22); ps = mat_tex("pside", "puffer_side", 0.22)
rlegs = mat_tex("rlegs", "ruslan_legs"); rarm = mat_tex("rarm", "ruslan_arm", 0.22); hand = mat_col("hand", "#E8BFA2", 0.5)
LEGS = []
for sx in (-0.125, 0.125):
    hip = empty("hip", (sx, 0, 0.75), 0, R_ROOT); box("leg", 0.25, 0.25, 0.75, (0, 0, -0.375), {"other": rlegs}, hip); LEGS.append(hip)
box("rbody", 0.56, 0.32, 0.78, (0, 0, 1.13), {"front": pf, "other": ps}, R_ROOT)
box("rhead", 0.5, 0.5, 0.5, (0, 0, 1.78), {"front": rface, "top": rcap, "other": rside}, R_ROOT)
box("rcapb", 0.53, 0.53, 0.1, (0, 0, 2.05), {"other": rcap}, R_ROOT)
box("rbrim", 0.5, 0.24, 0.035, (0, -0.35, 1.985), {"other": rcap}, R_ROOT)
ARMS = []
for sx in (-0.41, 0.41):
    sh = empty("shoulder", (sx, 0, 1.48), 0, R_ROOT)
    box("arm", 0.26, 0.28, 0.76, (0, 0, -0.36), {"bottom": hand, "other": rarm}, sh); ARMS.append(sh)
CASH = empty("cash", HIDE, 0, ARMS[1])
for k in range(3): box("bill", 0.3, 0.02, 0.15, (0.0, -0.16 - k * 0.012, -0.78 + k * 0.01), {"other": mat_col(f"bill{k}", "#5FB86A" if k % 2 else "#4A9E57", 0.6)}, CASH).rotation_euler = (0, 0, math.radians(k * 8))

# sparks / flying bits during the frenzy
SPARK = [box("spk", 0.04, 0.04, 0.04, HIDE, {"other": mat_col(f"spk{k}", "#FFC24A", 0.3, emit=20)}) for k in range(18)]
srr = random.Random(11)
SPV = [(Vector((srr.uniform(-1.2, 1.2), srr.uniform(-2.2, -0.8), srr.uniform(1.5, 3.2))), srr.uniform(0, 0.5)) for _ in SPARK]

# ================================================================ cameras
C = cam("cam", 30, 2.4); sc.camera = C


def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def ruslan_state(t):
    """Position, rotation, run phase and arm poses over the story."""
    x0, x1 = -4.2, -0.95
    run = 0.0
    if t < 1.55:
        k = ease((t - 0.15) / 1.4); x = x0 + (x1 - x0) * k; run = 1 - k * k
    else:
        x = x1
    y = -0.75; rot = 28
    if t >= S[4] - 0.35:  # steps closer for the pat
        k = ease((t - S[4] + 0.35) / 0.35); x = x1 + 0.55 * k; y = -0.75 + 0.15 * k; rot = 28 + 20 * k
    armR = 0.0; armL = 0.0
    if S[2] - 0.1 <= t < S[3] - 0.5: armR = 0.55 * ease((t - S[2] + 0.1) / 0.25)  # shows the cash
    if t >= S[4] - 0.1: armR = 1.35 * ease((t - S[4] + 0.1) / 0.25)  # pat
    return x, y, rot, run, armR, armL


def shutter_at(t):
    """0 = open, 1 = closed."""
    if t < S[1]: return 0.06 + 0.06 * ease(t / S[1])
    if t < SLAM - 0.35: return 0.12 + 0.14 * ease((t - S[1]) / (SLAM - 0.35 - S[1]))
    if t < SLAM: return 0.26 + 0.74 * ((t - SLAM + 0.35) / 0.35) ** 2
    if t < UP: return 1.0
    if t < UP + 0.18: return 1.0 - ((t - UP) / 0.18)
    return 0.0


def shot_cam(F, t):
    shot, st = F["shot"], F["shot_t"]; hold = t - st; push = ease(hold / 3.0)
    rx, ry, _, _, _, _ = ruslan_state(t)
    kroot = K_ROOT.location
    if shot == "est":
        k = ease(t / 1.8)
        p = Vector((2.2 - 1.0 * k, -6.6 + 1.2 * k, 2.8 - 1.0 * k)); q = Vector((0.1, 0.2, 1.7)); lens = 26
    elif shot == "r":
        head = Vector((rx, ry, 1.75)); p = head + Vector((1.25, -3.3, -0.2)) + (Vector((0, 0.3, 0)) * push); q = head + Vector((0.3, 0, -0.3)); lens = 32
    elif shot == "k":
        face = Vector((kroot.x, kroot.y - 0.4, kroot.z + 0.7)); p = Vector((kroot.x - 0.4, -2.6 + 0.3 * push, 1.55)); q = face + Vector((0, 0, -0.05)); lens = 32
    elif shot == "fr":
        face = Vector((kroot.x, kroot.y - 0.4, kroot.z + 0.6)); p = Vector((KX - 0.7, -3.4, 1.45)); q = Vector((KX - 0.1, 0.2, 1.35)); lens = 28
    else:  # two-shot
        p = Vector((0.05, -6.3 + 0.5 * push, 1.6)); q = Vector((0.1, 0.0, 1.35)); lens = 28
    return p, q, lens


frames = PLAN["frames"]
for fr in range(START, min(END, len(frames))):
    F = frames[fr]; t = F["t"]; rnd = random.Random(fr)
    r, k = F["r"], F["k"]
    set_tex(rface, f'ruslan_face_{r["expr"]}_{r["m"]}_{r["b"]}')
    set_tex(kface, f'klod_face_{k["expr"]}_{k["m"]}_{k["b"]}')
    # Ruslan
    x, y, rot, run, armR, armL = ruslan_state(t)
    R_ROOT.location = (x, y, 0.06 * abs(math.sin(t * 14)) * run); R_ROOT.rotation_euler = (0, 0, math.radians(rot))
    sw = math.sin(t * 14) * 0.7 * run
    LEGS[0].rotation_euler = (sw, 0, 0); LEGS[1].rotation_euler = (-sw, 0, 0)
    ARMS[0].rotation_euler = (-sw * 0.8 - armL, 0, 0)
    ARMS[1].rotation_euler = (sw * 0.8 - armR * 1.2, 0, math.radians(-25 * min(1, armR)) if t >= S[4] - 0.1 else 0)
    CASH.location = (0, 0, 0) if S[2] - 0.1 <= t < S[3] - 0.5 else HIDE
    # Klod: leans into the shutter, then dog-mode
    kx, ky, kz, krot = KX + 0.05, 0.8, 0.62, 0.0
    if S[1] <= t < SLAM: kz += 0.03 * math.sin(t * 8)
    if UP <= t < FR0: kz += 0.25 * math.exp(-(t - UP) * 6) * abs(math.cos((t - UP) * 20))
    if FR0 <= t < FR1:  # frenzy: blur of chopping
        krot = 22 * math.sin(t * 38); kz += 0.05 * abs(math.sin(t * 30)); kx += 0.08 * math.sin(t * 19)
    if t >= S[4] - 0.35:  # leans out of the window for the pat, wiggles like a happy dog
        kk = ease((t - S[4] + 0.35) / 0.3); ky = 0.8 - 0.55 * kk; kz += 0.12 * kk; krot = 9 * math.sin(t * 22) * kk
    K_ROOT.location = (kx, ky, kz); K_ROOT.rotation_euler = (0, 0, math.radians(krot))
    HAT.location = (0, 0, 1.06) if t >= UP else HIDE
    DONER.rotation_euler = (0, 0, t * (9 if FR0 <= t < FR1 + 0.5 else 0.8))
    # shutter
    c = shutter_at(t); H = c * 1.25
    for kk, sl in enumerate(SLATS):
        z = 2.2 - H + 0.05 + 0.1 * kk
        sl.location = (KX, -0.06, z) if z < 2.2 and c > 0.01 else HIDE
    OPEN.location = (KX, -0.02, 2.55) if (t < SLAM or t >= UP) else HIDE
    CLOSED.location = HIDE if (t < SLAM or t >= UP) else (KX, -0.02, 2.55)
    CLK1.location = (KX - 0.55, 2.14, 2.0) if t < UP else HIDE
    CLK2.location = HIDE if t < UP else (KX - 0.55, 2.14, 2.0)
    IN_L.data.energy = 380 if not (SLAM <= t < UP) else 120
    # rolls pile up
    n = 0 if t < FR0 else min(10, int((t - FR0) / ((FR1 - FR0) / 10.5)) + 1)
    for kk, (ro, pos) in enumerate(ROLLS):
        ro.location = pos if kk < n else HIDE; ro.rotation_euler = (0, 0, math.radians(8 * math.sin(kk * 2.1)))
    for (sp, (v, ph)) in zip(SPARK, SPV):
        if FR0 <= t < FR1:
            u = ((t - FR0) * 1.6 + ph) % 0.6
            sp.location = (KX + 0.62 + v.x * u, 1.4 + v.y * u, 1.3 + v.z * u - 4.9 * u * u)
        else:
            sp.location = HIDE
    # camera
    p, q, lens = shot_cam(F, t)
    if F["shot"] == "fr": p = p + Vector((rnd.uniform(-1, 1), 0, rnd.uniform(-1, 1))) * 0.03
    if SLAM <= t < SLAM + 0.25: p = p + Vector((rnd.uniform(-1, 1), 0, rnd.uniform(-1, 1))) * 0.05 * (1 - (t - SLAM) / 0.25)
    if UP + 0.15 <= t < UP + 0.4: p = p + Vector((rnd.uniform(-1, 1), 0, rnd.uniform(-1, 1))) * 0.04
    C.location = p; look(C, q); C.data.lens = lens; C.data.dof.focus_distance = (q - p).length
    C.data.dof.aperture_fstop = 4.0 if F["shot"] in ("est", "two") else 2.2
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
