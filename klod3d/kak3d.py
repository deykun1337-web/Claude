"""Blender: explainer «как нейросеть делает мультик» — warm wooden studio, holograms, Klod the boar narrates. Blocky 3D.
Usage: blender -b -P kak3d.py -- plan.json outdir start end"""
import bpy, json, math, os, random, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "scene3d.py")).read()
exec(_src[:_src.index("# ------------------------------------------------------------- characters")])
ee = sc.eevee
ee.taa_render_samples = 12; ee.bloom_intensity = 0.09; ee.bloom_threshold = 0.85; ee.bloom_radius = 6
ee.use_ssr = False
sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.25
S, E = PLAN["S"], PLAN["E"]
HIDE = (0, 0, -50)


def cam(name, lens, fstop):
    c = bpy.data.cameras.new(name); c.lens = lens; c.sensor_fit = "VERTICAL"; c.sensor_height = 24
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, c); bpy.context.collection.objects.link(o); return o


def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def torus(name, mat, R, r):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=64, minor_segments=10, location=HIDE)
    o = bpy.context.object; o.data.materials.append(mat); return o


def cylinder(name, mat, r, h, loc=HIDE, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=loc)
    o = bpy.context.object; o.data.materials.append(mat); return o


# ================================================================ room: warm wooden studio
world((0.05, 0.035, 0.03), 0.5)
floor = mat_tex("floor", "plank_floor", 0.45); wallm = mat_tex("wallm", "plank_wall", 0.7)
box("floor", 14, 12, 0.1, (0, 2, -0.05), {"other": floor})
box("backwall", 14, 0.2, 6, (0, 4.2, 3), {"other": wallm})
box("sidewall", 0.2, 10, 6, (-4.5, 0, 3), {"other": wallm})
rr = random.Random(7)
# cork board with notes + string lights on the wall
box("cork", 1.6, 0.05, 1.0, (2.2, 4.08, 2.4), {"other": mat_col("cork", "#B98B55", 0.8)})
for k in range(7):
    box("note", 0.28, 0.02, 0.28, (1.65 + (k % 4) * 0.36, 4.05, 2.6 - (k // 4) * 0.42), {"other": mat_col(f"note{k}", rr.choice(["#FFE27A", "#FFFFFF", "#9AD7FF", "#FFB3C7"]), 0.6)}).rotation_euler = (0, rr.uniform(-0.2, 0.2), 0)
bulb = mat_col("bulb", "#FFC870", 0.4, emit=14)
for k in range(26):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(-3.6 + k * 0.3, 4.05, 3.7 - 0.18 * abs(math.sin(k * 0.45))))
    bpy.context.object.data.materials.append(bulb)
# a plant + bookshelf for depth
box("pot", 0.35, 0.35, 0.35, (-2.6, 3.4, 0.175), {"other": mat_col("pot", "#C65D3B", 0.6)})
for k in range(6):
    box("leaf", 0.12, 0.12, rr.uniform(0.4, 0.8), (-2.6 + rr.uniform(-0.15, 0.15), 3.4 + rr.uniform(-0.15, 0.15), 0.6), {"other": mat_col("leaf", "#3E8E4A", 0.6)}).rotation_euler = (rr.uniform(-0.4, 0.4), rr.uniform(-0.4, 0.4), 0)
shelfm = mat_col("shelfm", "#5A3A24", 0.6)
box("bshelf", 1.4, 0.4, 2.2, (-3.6, 3.7, 1.1), {"other": shelfm})
for r_ in range(4):
    for k in range(8):
        box("book", 0.12, 0.3, rr.uniform(0.28, 0.42), (-4.2 + k * 0.16, 3.6, 0.25 + r_ * 0.52), {"other": mat_col("bk", rr.choice(["#D97757", "#3B6EA8", "#E8C547", "#6BAA75", "#8E5CA8"]), 0.6)})
# lights: warm key, soft fill, cool rim + practical window glow
area("key", (-2.5, -3.5, 4.0), (0, 0.5, 0.8), 650, (1.0, 0.82, 0.62), 3.0)
area("fill", (3.5, -2.5, 2.0), (0, 0.5, 0.8), 180, (0.9, 0.85, 1.0), 3.0)
area("rim", (0.5, 3.5, 3.0), (0, 0, 0.8), 380, (1.0, 0.7, 0.45), 2.5)
point("practical", (2.2, 3.4, 3.3), 60, (1.0, 0.75, 0.45))

# ================================================================ desk + PC
DESK = (1.75, 0.9)
deskm = mat_col("desk", "#7A5236", 0.55)
box("desk", 1.6, 0.8, 0.06, (DESK[0], DESK[1], 0.78), {"other": deskm})
for lx in (-0.72, 0.72):
    for ly in (-0.32, 0.32): box("dleg", 0.06, 0.06, 0.78, (DESK[0] + lx, DESK[1] + ly, 0.39), {"other": deskm})
scrm = mat_tex("scrm", "scr_claude", 0.4, emit=1.6)
PCSCREEN = box("monitor", 0.95, 0.05, 0.6, (DESK[0], DESK[1] + 0.2, 1.25), {"front": scrm, "other": mat_col("mon", "#1A1A1E", 0.4)})
box("stand", 0.08, 0.08, 0.2, (DESK[0], DESK[1] + 0.25, 0.9), {"other": mat_col("mon2", "#1A1A1E", 0.4)})
box("kbd", 0.6, 0.2, 0.03, (DESK[0], DESK[1] - 0.15, 0.825), {"other": mat_col("kbd", "#2A2A30", 0.5)})
box("mug0", 0.1, 0.1, 0.12, (DESK[0] + 0.6, DESK[1] - 0.1, 0.87), {"other": mat_col("mugc", "#F4EFE6", 0.4)})

# ================================================================ characters
K_ROOT = empty("klod", (0, 0, 0), 0)
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
for k in range(7):
    box("mane", 0.07, 0.07, krr.uniform(0.06, 0.13), (-0.2 + k * 0.065, -0.05 + krr.uniform(-0.1, 0.1), 1.08), {"other": kdark}, K_ROOT)

R_ROOT = empty("ruslan", HIDE, 0)
rface = mat_tex("rface", "ruslan_face_happy_0_0", 0.55)
rside = mat_tex("rside", "ruslan_side"); rcap = mat_tex("rcap", "ruslan_cap"); rshirt = mat_col("rshirt", "#A8ADB6", 0.7)
rlegs = mat_tex("rlegs", "ruslan_legs"); hand = mat_col("hand", "#E8BFA2", 0.5)
HIPS = []
for sx in (-0.125, 0.125):
    hip = empty("hip", (sx, 0, 0.75), 0, R_ROOT); box("leg", 0.25, 0.25, 0.75, (0, 0, -0.375), {"other": rlegs}, hip); HIPS.append(hip)
box("rbody", 0.5, 0.28, 0.76, (0, 0, 1.13), {"other": rshirt}, R_ROOT)
box("rhead", 0.5, 0.5, 0.5, (0, 0, 1.76), {"front": rface, "top": rcap, "other": rside}, R_ROOT)
box("rcapb", 0.53, 0.53, 0.1, (0, 0, 2.03), {"other": rcap}, R_ROOT)
box("rbrim", 0.5, 0.24, 0.035, (0, -0.35, 1.965), {"other": rcap}, R_ROOT)
ARMS = []
for sx in (-0.37, 0.37):
    sh = empty("shoulder", (sx, 0, 1.47), 0, R_ROOT)
    box("arm", 0.24, 0.26, 0.74, (0, 0, -0.35), {"bottom": hand, "other": rshirt}, sh); ARMS.append(sh)
PH = empty("rphone", HIDE, 0, ARMS[1])
box("rph", 0.16, 0.03, 0.28, (-0.05, -0.12, -0.78), {"front": mat_col("rphs", "#9AD7FF", 0.3, emit=3), "other": mat_col("rphb", "#15161A", 0.4)}, PH).rotation_euler = (math.radians(70), 0, 0)
MUG = empty("mug", HIDE, 0, ARMS[1])
box("mugb", 0.13, 0.13, 0.15, (0, -0.1, -0.72), {"other": mat_col("mug", "#D97757", 0.4)}, MUG)
chair = mat_col("chair", "#2B2F38", 0.5)
CHAIR = empty("chair", HIDE, 0)
box("seat", 0.55, 0.55, 0.08, (0, 0, 0.5), {"other": chair}, CHAIR); box("back", 0.55, 0.08, 0.6, (0, 0.27, 0.85), {"other": chair}, CHAIR)
box("cpost", 0.06, 0.06, 0.45, (0, 0, 0.25), {"other": chair}, CHAIR)
BEAN = box("beanbag", 1.0, 0.9, 0.45, HIDE, {"other": mat_col("bean", "#3B6EA8", 0.8)})

# ================================================================ props per beat
gold = mat_col("gold", "#F2B53A", 0.25, metal=0.9)
COINS = []
for k in range(46):
    c = cylinder("coin", gold, 0.11, 0.03)
    COINS.append((c, Vector((rr.uniform(-1.3, 1.3), rr.uniform(-1.6, 0.6), 0.0)), rr.uniform(0, 2.4), rr.uniform(0, 6)))
holo_o = mat_col("holo_o", "#FF9A5A", 0.3, emit=10); holo_w = mat_col("holo_w", "#FFFFFF", 0.3, emit=12); holo_c = mat_col("holo_c", "#5AD2FF", 0.3, emit=9)
RINGS = [torus("ring0", holo_o, 0.55, 0.025), torus("ring1", holo_c, 0.42, 0.02), torus("ring2", holo_o, 0.68, 0.015)]
CORE = empty("core", HIDE)
for k in range(8):
    a = k * math.pi / 4
    b = box("ray", 0.07, 0.07, 0.3, (0.13 * math.sin(a), 0, 0.13 * math.cos(a)), {"other": holo_w}, CORE); b.rotation_euler = (0, a, 0)
PAD = cylinder("pad", mat_col("pad", "#1A1C22", 0.4), 0.6, 0.12, HIDE, 48)
PADRING = torus("padring", holo_c, 0.6, 0.03)
# floating holo screens
SCR = []
for k, tx in enumerate(["scr_trend", "scr_script", "scr_trend", "scr_script", "scr_claude"]):
    m = mat_tex(f"hs{k}", tx, 0.4, emit=2.2)
    dims = (0.8, 0.03, 0.5) if "script" not in tx else (0.45, 0.03, 0.6)
    SCR.append(box("hscr", *dims, HIDE, {"front": m, "back": m, "other": holo_c}))
PAPERS = [box("paper", 0.3, 0.01, 0.4, HIDE, {"front": mat_tex("pp", "scr_script", 0.6), "other": mat_col("ppw", "#F6F2E8", 0.6)}) for _ in range(8)]
# sound wave bars
BARS = [box("bar", 0.08, 0.08, 1.0, HIDE, {"other": holo_o if k % 2 else holo_c}) for k in range(17)]
# block-building mini world
BLOCKS = []
mini_cols = ["#E9DCC0", "#E9DCC0", "#D97757", "#3E8E4A", "#3B6EA8", "#2A2B30", "#FF8A1F"]
layout = []
for x in range(-2, 3):
    for z in range(3): layout.append(((x * 0.2, 0, z * 0.2 + 0.1), 0 if z < 2 else 1))
for x in range(-2, 3): layout.append(((x * 0.2, 0, 0.7), 5))
for k in range(5): layout.append(((-0.8, 0, 0.1 + k * 0.2), 3 if k > 2 else 6))
for k in range(3): layout.append(((0.75, 0.1, 0.1 + k * 0.2), 4))
layout += [((-0.2, -0.1, 0.9), 6), ((0.2, -0.1, 0.9), 6), ((0, -0.1, 0.9), 6)]
for k, (pos, ci) in enumerate(layout):
    b = box("blk", 0.19, 0.19, 0.19, HIDE, {"other": mat_col(f"blk{k}", mini_cols[ci], 0.5, emit=1.5 if ci == 6 else 0)})
    BLOCKS.append((b, Vector(pos), Vector((rr.uniform(-2.5, 2.5), rr.uniform(-2, 1), rr.uniform(1.5, 3.5))), k * 0.035))
# phone
PHONE = empty("phone", HIDE)
box("phbody", 0.62, 0.06, 1.15, (0, 0, 0), {"other": mat_col("ph", "#15161A", 0.3, metal=0.4)}, PHONE)
box("phscr", 0.56, 0.01, 1.04, (0, -0.035, 0), {"front": mat_tex("phs", "phone_reel", 0.3, emit=1.4), "other": mat_col("ph2", "#000000", 0.3)}, PHONE)
# balance scale
SCALE = empty("scale", HIDE)
wood = mat_col("swood", "#5A3A24", 0.5)
box("spost", 0.1, 0.1, 1.4, (0, 0, 0.7), {"other": wood}, SCALE); box("sbase", 0.6, 0.4, 0.08, (0, 0, 0.04), {"other": wood}, SCALE)
BEAM = empty("beam", (0, 0, 1.4), 0, SCALE)
box("beamb", 1.8, 0.06, 0.06, (0, 0, 0), {"other": gold}, BEAM)
PANS = []
for sx in (-0.85, 0.85):
    pv = empty("panpiv", (sx, 0, 0), 0, BEAM)
    box("string", 0.015, 0.015, 0.5, (0, 0, -0.25), {"other": mat_col("str", "#333333", 0.6)}, pv)
    p = cylinder("pan", gold, 0.32, 0.04); p.parent = pv; p.location = (0, 0, -0.52)
    PANS.append(pv)
for k in range(14):
    c = cylinder("pcoin", gold, 0.09, 0.03); c.parent = PANS[0]; c.location = (rr.uniform(-0.18, 0.18), rr.uniform(-0.18, 0.18), -0.48 + (k // 5) * 0.03)
card = box("card", 0.4, 0.02, 0.25, (0, 0, -0.38), {"front": mat_tex("cardm", "card_sub", 0.4, emit=0.6), "other": mat_col("cardb", "#D97757", 0.4)}, PANS[1])
# confetti for the end
CONF = [box("conf", 0.06, 0.06, 0.02, HIDE, {"other": mat_col(f"cf{k}", ["#D97757", "#FFE27A", "#5AD2FF", "#FFFFFF", "#3DDC84"][k % 5], 0.4, emit=2)}) for k in range(40)]
CONFV = [(Vector((rr.uniform(-2, 2), rr.uniform(-1.5, 0.5), rr.uniform(2.5, 4))), rr.uniform(0, 1.5)) for _ in CONF]

C = cam("cam", 32, 2.8); sc.camera = C


def klod_pose(beat, bt, t):
    """Klod position/rotation per beat."""
    if beat in (3,): return (0.35, 1.0, 0, -35)
    if beat in (9,): return (1.1, 0.6, 0, -15)
    if beat in (7,): return (0.95, 0.45, 0, -40)
    if beat in (8,): return (0.25, 0.55, 0, -10)
    if beat in (10,): return (0.45, 0.0, 0, 0)
    return (0.0, 0.0, 0, 0)


def shot(beat, bt, t):
    if beat == 0: k = ease(bt / 3.0); return Vector((0.9 - 0.3 * k, -4.4 + 0.9 * k, 0.75 + 0.25 * k)), Vector((0, 0, 0.95)), 30
    if beat == 1: k = ease(bt / 3.0); return Vector((-1.2, -2.7 + 0.3 * k, 1.0)), Vector((0, 0, 0.85)), 34
    if beat == 2: k = ease(bt / 2.6); return Vector((0.9 - 0.4 * k, -3.0, 0.45)), Vector((0, 0, 1.55)), 26
    if beat == 3: return Vector((DESK[0] - 0.35, -2.7 + 0.3 * ease(bt / 2.8), 1.65)), Vector((DESK[0] - 0.55, DESK[1] - 0.3, 1.3)), 28
    if beat == 4:
        a = math.radians(-35 + 50 * ease(bt / 2.3)); return Vector((3.4 * math.sin(a), -3.4 * math.cos(a), 1.3)), Vector((0, 0, 1.05)), 26
    if beat == 5: return Vector((-0.3, -3.4 + 0.4 * ease(bt / 2.9), 1.1)), Vector((0, 0, 0.95)), 30
    if beat == 6: k = ease(bt / 2.6); return Vector((2.2 - 0.6 * k, -4.4 + 0.4 * k, 2.5 - 0.3 * k)), Vector((0, -0.9, 0.55)), 30
    if beat == 7: return Vector((-0.1, -4.8 + 0.4 * ease(bt / 3.5), 1.6)), Vector((0.05, 0.4, 0.9)), 26
    if beat == 8: return Vector((0.45, -2.5 + 0.25 * ease(bt / 2), 1.3)), Vector((0.55, -0.3, 1.2)), 32
    if beat == 9: return Vector((-0.1, -5.2, 1.3)), Vector((-0.05, -0.5, 1.0)), 26
    k = ease(bt / 3.8); return Vector((0.2, -5.0 + 0.6 * k, 1.5)), Vector((0.0, 0.0, 1.0)), 26


frames = PLAN["frames"]
for fr in range(START, min(END, len(frames))):
    F = frames[fr]; t = F["t"]; beat = F["beat"]; bt = F["bt"]; env = F["env"]; k = F["k"]
    set_tex(kface, f'klod_face_{k["expr"]}_{k["m"]}_{k["b"]}')
    kx, ky, kz, kr = klod_pose(beat, bt, t)
    hop = 0.12 * abs(math.sin(bt * 9)) * math.exp(-bt * 2) if beat in (1, 10) else 0
    K_ROOT.location = (kx, ky, kz + hop + 0.015 * math.sin(t * 2.2)); K_ROOT.rotation_euler = (0, 0, math.radians(kr + 3 * math.sin(t * 1.3)))
    # Ruslan + chair / beanbag
    R_ROOT.location = HIDE; CHAIR.location = HIDE; BEAN.location = HIDE; MUG.location = HIDE; PH.location = HIDE
    for h in HIPS: h.rotation_euler = (0, 0, 0)
    for a in ARMS: a.rotation_euler = (0, 0, 0)
    if beat == 3:  # Ruslan types the request on his phone
        R_ROOT.location = (DESK[0] - 0.95, DESK[1] - 0.75, 0); R_ROOT.rotation_euler = (0, 0, math.radians(18))
        ARMS[1].rotation_euler = (math.radians(-75), 0, math.radians(-30)); ARMS[0].rotation_euler = (math.radians(-60), 0, math.radians(30))
        MUG.location = HIDE; PH.location = (0, 0, 0)
    if beat == 7:
        BEAN.location = (-0.85, 0.1, 0.22); R_ROOT.location = (-0.85, 0.05, 0.05); R_ROOT.rotation_euler = (0, 0, math.radians(25))
        for h in HIPS: h.rotation_euler = (math.radians(80), 0, 0)
        R_ROOT.location.z = -0.15; MUG.location = (0, 0, 0)
        sip = max(0, math.sin(bt * 1.8)); ARMS[1].rotation_euler = (math.radians(-60 - 55 * sip), 0, math.radians(-25 * sip))
    if beat == 10:
        R_ROOT.location = (-0.75, -0.1, 0); R_ROOT.rotation_euler = (0, 0, math.radians(15))
        ARMS[0].rotation_euler = (0, math.radians(-150 - 20 * math.sin(t * 9)), 0)
    rex = "happy" if beat != 3 else "smug"
    rm = 0
    set_tex(rface, f'ruslan_face_{rex}_{rm}_{1 if (t % 3.1) < 0.12 else 0}')
    scrm_name = "scr_render" if beat == 7 else "scr_claude"
    set_tex(scrm, scrm_name)
    # beat 0: coins rain and pile up
    for c, p, dl, sp in COINS:
        if beat <= 1:
            u = t - dl * 0.8
            if u < 0: c.location = HIDE; continue
            z = max(0.015 + (p.y + 1.6) * 0.0, 3.6 - 4.9 * u * u * 1.6)
            c.location = (p.x, p.y, z if z > 0.02 else 0.015 + 0.02 * ((hash(dl) % 3)))
            c.rotation_euler = (sp + u * 7 if z > 0.03 else 0, sp * 0.5 if z > 0.03 else 0, sp)
        else:
            c.location = HIDE
    # beat 2 + 10: hologram Claude core above a pad
    show_holo = beat in (2, 10)
    hc = Vector((kx, ky, 1.95)) if beat == 2 else Vector((0.45, 0.0, 2.05))
    sc_ = ease(bt / 0.35)
    for i, rg in enumerate(RINGS):
        rg.location = hc if show_holo else HIDE; rg.scale = (sc_,) * 3
        rg.rotation_euler = (t * (1.3 + 0.4 * i) + i, t * (0.8 - 0.3 * i), t * 0.5)
    CORE.location = hc if show_holo else HIDE; CORE.scale = (sc_,) * 3; CORE.rotation_euler = (0, t * 1.5, 0)
    # beat 4: orbiting screens + flying script pages
    for i, sobj in enumerate(SCR):
        if beat == 4:
            a = t * 0.9 + i * 2 * math.pi / len(SCR)
            sobj.location = (1.25 * math.cos(a), 1.25 * math.sin(a) * 0.8, 1.2 + 0.35 * math.sin(a * 2)); sobj.rotation_euler = (0, 0, a + math.pi / 2)
            sobj.scale = (ease(bt / 0.4),) * 3
        else:
            sobj.location = HIDE
    for i, pp in enumerate(PAPERS):
        if beat == 4:
            u = (bt * 0.6 + i / len(PAPERS)) % 1
            pp.location = (-1.6 + 3.2 * u, -0.9 + 0.3 * math.sin(i), 0.5 + 1.6 * math.sin(u * math.pi)); pp.rotation_euler = (u * 4 + i, u * 3, u * 2)
        else:
            pp.location = HIDE
    # beat 5: sound wave arc reacting to the voice
    for i, b in enumerate(BARS):
        if beat == 5:
            a = math.radians(-85 + 170 * i / (len(BARS) - 1))
            hgt = 0.15 + 1.1 * env * (0.5 + 0.5 * abs(math.sin(i * 1.7 + t * 11)))
            b.location = (1.35 * math.sin(a), 0.75 - 0.35 * math.cos(a), 0.95); b.scale = (1, 1, hgt); b.rotation_euler = (0, 0, a)
        else:
            b.location = HIDE
    # beat 6: blocks fly in and build a tiny kiosk world
    for b, pos, start, dl in BLOCKS:
        if beat == 6:
            kk = ease((bt - 0.2 - dl) / 0.35)
            tgt = Vector((0, -1.25, 0)) + pos
            b.location = start.lerp(tgt, kk) if kk > 0 else HIDE; b.rotation_euler = (3 * (1 - kk), 2 * (1 - kk), 0)
        else:
            b.location = HIDE
    # beat 8: phone with the finished reel
    PHONE.location = (0.55, -0.35, 1.2 + 0.03 * math.sin(t * 2)) if beat == 8 else HIDE
    PHONE.rotation_euler = (0, 0, math.radians(-8 * (1 - ease(bt / 0.4)))); PHONE.scale = (ease(bt / 0.3),) * 3
    # beat 9: balance scale
    SCALE.location = (-0.05, -0.8, 0) if beat == 9 else HIDE
    tilt = math.radians(-14 * ease((bt - 0.3) / 0.5)) if beat == 9 else 0
    tilt += math.radians(3 * math.sin(bt * 10) * math.exp(-max(0, bt - 0.8) * 3)) if beat == 9 and bt > 0.8 else 0
    BEAM.rotation_euler = (0, tilt, 0)
    for pv in PANS: pv.rotation_euler = (0, -tilt, 0)
    # end confetti
    for (cf, (v, ph)) in zip(CONF, CONFV):
        if beat == 10:
            u = (bt * 0.5 + ph) % 1.6
            cf.location = (v.x * 0.6, v.y * 0.4 - 0.5, 3.4 - 2.2 * u); cf.rotation_euler = (u * 6 + ph, u * 4, ph)
        else:
            cf.location = HIDE
    p, q, lens = shot(beat, bt, t)
    p = p + Vector((0.01 * math.sin(t * 0.9), 0, 0.008 * math.sin(t * 1.3)))
    C.location = p; look(C, q); C.data.lens = lens; C.data.dof.focus_distance = (q - p).length
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
