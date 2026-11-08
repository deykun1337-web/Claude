"""Blender: «Чёрная пятница» — skeleton army at the mall doors at dawn (cinematic, fog, light shafts).
Usage: blender -b -P pyatnica3d.py -- plan.json outdir start end"""
import bpy, json, math, os, random, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "scene3d.py")).read()
exec(_src[:_src.index("# ------------------------------------------------------------- characters")])
ee = sc.eevee
ee.taa_render_samples = 16; ee.bloom_intensity = 0.12; ee.bloom_threshold = 0.8
ee.use_volumetric_lights = True; ee.volumetric_tile_size = "8"; ee.volumetric_samples = 32; ee.volumetric_end = 40
sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.7


def cam(name, lens, fstop):
    c = bpy.data.cameras.new(name); c.lens = lens; c.sensor_fit = "VERTICAL"; c.sensor_height = 24
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, c); bpy.context.collection.objects.link(o); return o


# world: dawn sky + volumetric fog
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes["Background"]; bg.inputs[0].default_value = (0.03, 0.045, 0.09, 1); bg.inputs[1].default_value = 0.8
vol = nt.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Density"].default_value = 0.012; vol.inputs["Color"].default_value = (0.75, 0.8, 0.9, 1)
nt.links.new(vol.outputs[0], nt.nodes["World Output"].inputs["Volume"])

FONT = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf")


def text3d(body, loc, size, mat, extrude=0.06, rot=(math.radians(90), 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o = bpy.context.object; o.data.body = body; o.data.font = FONT; o.data.size = size; o.data.extrude = extrude
    o.data.bevel_depth = 0.01; o.data.align_x = "CENTER"; o.data.materials.append(mat); return o


# ================================================================ outside: parking lot + mall
box("asphalt", 40, 40, 0.1, (0, 6, -0.05), {"other": mat_tex("asph", "asphalt", 0.6)})
mallw = mat_tex("mallw", "mall_wall", 0.7)
box("mall", 26, 3, 9, (0, 13.5, 4.5), {"other": mallw})
glass = mat_tex("glass", "mall_glass", 0.3, emit=3.0)
box("doorlight", 5.2, 0.05, 3.4, (0, 11.98, 1.7), {"other": glass})
doorm = mat_col("doorm", "#9AB0C8", 0.1, metal=0.3)
doors = [box("door", 2.5, 0.08, 3.2, (x, 11.9, 1.6), {"other": doorm}) for x in (-1.27, 1.27)]
red = mat_col("signred", "#FF2A2A", 0.3, emit=14)
text3d("−70%", (0, 11.85, 4.6), 2.3, red, 0.15)
text3d("ЧЁРНАЯ ПЯТНИЦА", (0, 11.85, 7.2), 0.9, mat_col("signw", "#FFFFFF", 0.3, emit=6), 0.08)
pole = mat_col("pole", "#202226", 0.5); lampm = mat_col("lampm", "#FFD9A0", 0.4, emit=12)
for x in (-9, 9):
    for y in (2, 8):
        box("pole", 0.15, 0.15, 5, (x, y, 2.5), {"other": pole}); box("lamp", 0.6, 0.3, 0.2, (x, y, 5.05), {"other": lampm})
area("doorbeam", (0, 11.6, 2.4), (0, 2, 1.0), 700, (1.0, 0.85, 0.6), 4.0)
area("signglow", (0, 11.2, 5), (0, 4, 1), 350, (1.0, 0.2, 0.15), 3.0)
area("moonfill", (-8, -6, 8), (0, 6, 0), 300, (0.45, 0.6, 1.0), 6.0)
sun = bpy.data.lights.new("dawn", "SUN"); sun.energy = 0.6; sun.color = (1.0, 0.55, 0.3)
so = bpy.data.objects.new("dawn", sun); bpy.context.collection.objects.link(so); so.rotation_euler = (math.radians(70), 0, math.radians(200))

# ================================================================ inside: empty store (x ~ 40)
IX = 40.0
box("ifloor", 14, 16, 0.1, (IX, 2, -0.05), {"other": mat_col("ifl", "#C9CED6", 0.25)})
box("iback", 14, 0.2, 5, (IX, 8, 2.5), {"other": mat_col("iwall", "#E8ECF0", 0.7)})
shelf = mat_tex("shelf", "shelf", 0.4)
for k, x in enumerate((-4.5, -1.5, 1.5, 4.5)):
    box("shelf", 1.0, 5.0, 2.2, (IX + x, 3.5, 1.1), {"other": shelf})
fl = mat_col("fluo", "#F2F8FF", 0.3, emit=9)
for x in (-3, 0, 3):
    box("fluo", 0.25, 4.0, 0.06, (IX + x, 3, 4.6), {"other": fl})
area("ifill", (IX, 0, 4.5), (IX, 3, 0), 900, (0.9, 0.95, 1.0), 8.0)
text3d("РАСПРОДАНО ОНЛАЙН В 00:01", (IX, 7.85, 3.4), 0.42, mat_col("soldout", "#FF3B30", 0.3, emit=6), 0.03)
box("lastsock", 0.18, 0.06, 0.28, (IX + 1.5, 1.0, 1.55), {"other": mat_col("sock", "#E8B740", 0.6)})

# ================================================================ skeleton warriors
bone = mat_tex("bone", "bone", 0.6); skull = mat_tex("skull", "skull_face", 0.5); ribs = mat_tex("ribs", "ribs", 0.6)
shieldm = mat_tex("shield", "shield", 0.5); steel = mat_col("steel", "#C9CED6", 0.2, metal=0.9)
SK = []
rr = random.Random(7)


def skeleton(name, loc, rotz):
    root = empty(name, loc, rotz)
    for sx in (-0.12, 0.12): box("sleg", 0.09, 0.09, 0.8, (sx, 0, 0.4), {"other": bone}, root)
    box("pelvis", 0.34, 0.14, 0.12, (0, 0, 0.86), {"other": bone}, root)
    box("spine", 0.07, 0.07, 0.4, (0, 0.02, 1.05), {"other": bone}, root)
    box("ribcage", 0.44, 0.24, 0.42, (0, 0, 1.32), {"front": ribs, "back": ribs, "other": bone}, root)
    box("skull", 0.36, 0.36, 0.36, (0, 0, 1.74), {"front": skull, "other": bone}, root)
    la = empty(name + "la", (-0.28, 0, 1.48), 0, root); la.rotation_euler = (math.radians(-70), 0, math.radians(-15))
    box("larm", 0.07, 0.07, 0.6, (0, 0, -0.3), {"other": bone}, la)
    box("shield", 0.6, 0.05, 0.7, (0.05, -0.12, -0.5), {"front": shieldm, "back": shieldm, "other": bone}, la).rotation_euler = (math.radians(70), 0, 0)
    ra = empty(name + "ra", (0.28, 0, 1.48), 0, root)
    box("rarm", 0.07, 0.07, 0.6, (0, 0, -0.3), {"other": bone}, ra)
    box("blade", 0.05, 0.02, 0.8, (0, -0.02, -0.95), {"other": steel}, ra)
    box("hilt", 0.2, 0.04, 0.04, (0, -0.02, -0.55), {"other": steel}, ra)
    return root, ra


for row in range(4):
    for col in range(-3, 3):
        x = col * 1.15 + 0.55 + (0.3 if row % 2 else 0) + rr.uniform(-0.15, 0.15)
        y = 6.2 - row * 1.25 + rr.uniform(-0.15, 0.15)
        if abs(x) < 1.6 and row == 0: continue  # leave room for the heroes
        SK.append(skeleton(f"sk{row}{col}", (x, y, 0), 180 + rr.uniform(-12, 12)) + (rr.uniform(0, 6.28), y))
SOLO = SK[0]

# ================================================================ heroes (viking Руслан + Клод)
def ruslan(loc, rotz):
    root = empty("ruslan", loc, rotz)
    face = mat_tex("rface", "ruslan_face_hat_neutral_0_0", 0.55)
    side = mat_tex("rside", "ruslan_side"); pf = mat_tex("pfront", "puffer_front", 0.22); ps = mat_tex("pside", "puffer_side", 0.22)
    legs = mat_tex("rlegs", "ruslan_legs"); arm = mat_tex("rarm", "ruslan_arm", 0.22); helm = mat_tex("helm", "helmet", 0.3); horn = mat_tex("horn", "horn", 0.5)
    for sx in (-0.125, 0.125): box("leg", 0.25, 0.25, 0.75, (sx, 0, 0.375), {"other": legs}, root)
    box("body", 0.56, 0.32, 0.78, (0, 0, 1.13), {"front": pf, "other": ps}, root)
    for sx in (-0.41, 0.41): box("arm", 0.26, 0.28, 0.76, (sx, 0, 1.12), {"bottom": mat_col("hand", "#E8BFA2"), "other": arm}, root)
    box("head", 0.5, 0.5, 0.5, (0, 0, 1.78), {"front": face, "other": side}, root)
    box("helmet", 0.56, 0.56, 0.2, (0, 0, 2.08), {"other": helm}, root)
    for sx in (-1, 1):
        h = box("horn", 0.1, 0.1, 0.38, (sx * 0.33, 0, 2.25), {"other": horn}, root); h.rotation_euler = (0, math.radians(-sx * 35), 0)
    box("rshield", 0.65, 0.06, 0.75, (-0.58, -0.12, 1.1), {"front": shieldm, "other": bone}, root)
    return root, face


R_ROOT, R_FACE = ruslan((-0.85, 7.9, 0), 180)
K_ROOT = empty("klod", (0.9, 7.9, 0), 180)
KS = 1.05
kface = mat_tex("kface", "klod_face_neutral_0_0", 0.6)
kside = mat_tex("kside", "klod_side"); ktop = mat_tex("ktop", "klod_top"); kdark = mat_tex("kdark", "klod_dark")
ksnout = mat_tex("ksnout", "klod_snout", 0.5); tusk = mat_col("tusk", "#FFF6E6", 0.3)
for lx in (-0.36, 0.36):
    for ly in (-0.22, 0.22): box("kleg", 0.17 * KS, 0.17 * KS, 0.3 * KS, (lx * KS, ly * KS, 0.15 * KS), {"other": kdark}, K_ROOT)
box("kbody", 1.0 * KS, 0.75 * KS, 0.75 * KS, (0, 0, 0.675 * KS), {"front": kface, "top": ktop, "other": kside}, K_ROOT)
box("snout", 0.38 * KS, 0.15 * KS, 0.19 * KS, (0, -0.445 * KS, 0.56 * KS), {"other": ksnout}, K_ROOT)
for tx in (-0.25, 0.25): box("tusk", 0.05 * KS, 0.05 * KS, 0.14 * KS, (tx * KS, -0.4 * KS, 0.55 * KS), {"other": tusk}, K_ROOT)
box("khelm", 0.85 * KS, 0.62 * KS, 0.16 * KS, (0, 0, 1.13 * KS), {"other": mat_tex("helm2", "helmet", 0.3)}, K_ROOT)
for sx in (-1, 1):
    h = box("khorn", 0.09, 0.09, 0.4, (sx * 0.5 * KS, 0, 1.3 * KS), {"other": mat_tex("horn2", "horn", 0.5)}, K_ROOT); h.rotation_euler = (0, math.radians(-sx * 30), 0)
box("kshield", 0.7, 0.06, 0.7, (0.75 * KS, -0.1, 0.55 * KS), {"front": shieldm, "other": bone}, K_ROOT).rotation_euler = (0, 0, math.radians(-25))

CAMS = {
    "crane": cam("c_crane", 22, 6.0), "r_close": cam("c_r", 38, 2.0), "k_close": cam("c_k", 36, 2.0),
    "charge": cam("c_ch", 22, 6.0), "in_wide": cam("c_iw", 22, 5.0), "in_r": cam("c_ir", 38, 2.0), "in_k": cam("c_ik", 36, 2.0),
    "end": cam("c_end", 30, 3.5),
}


def place(name, pos, tgt, fstop_focus=None):
    o = CAMS[name]; o.location = Vector(pos); look(o, Vector(tgt)); o.data.dof.focus_distance = (Vector(fstop_focus or tgt) - Vector(pos)).length; sc.camera = o


for fr in range(START, min(END, len(PLAN["frames"]))):
    F = PLAN["frames"][fr]; t = F["t"]; shot = F["shot"]; p = F["push"]; sw = F["sway"]
    r, k = F["r"], F["k"]
    set_tex(R_FACE, f'ruslan_face_hat_{r["expr"]}_{r["m"]}_{r["b"]}')
    set_tex(kface, f'klod_face_{k["expr"]}_{k["m"]}_{k["b"]}')
    inside = F["scene"] == "in"
    ch = F["charge"]
    # doors slide open
    for d, sgn in zip(doors, (-1, 1)): d.location.x = sgn * (1.27 + 2.4 * F["doors"])
    # skeleton army: bang shields, charge forward
    for root, ra, ph, y0 in SK:
        hit = max(0.0, math.sin(t * 2 * math.pi * 1.5 + ph)) ** 6 * F["bang"]
        if F.get("solo") and root is not SOLO[0]: hit = 0
        if F.get("solo") and root is SOLO[0]: hit = max(0.0, math.sin(t * 2 * math.pi * 0.8)) ** 6
        ra.rotation_euler = (math.radians(-100 + 35 * hit), 0, math.radians(-10 - 40 * hit))
        root.location.y = y0 + 4.5 * ch + 0.05 * math.sin(t * 6 + ph) * (ch > 0)
        root.location.z = 0.08 * abs(math.sin(t * 9 + ph)) * (1 if ch > 0 else 0)
    if inside:
        R_ROOT.location = (IX - 0.7, 0.2, 0); R_ROOT.rotation_euler = (0, 0, 0)
        K_ROOT.location = (IX + 0.7, 0.2, 0); K_ROOT.rotation_euler = (0, 0, 0)
    else:
        R_ROOT.location = (-0.85, 7.9 + 4.0 * ch, 0); R_ROOT.rotation_euler = (0, 0, math.radians(180))
        K_ROOT.location = (0.9, 7.9 + 4.0 * ch, 0); K_ROOT.rotation_euler = (0, 0, math.radians(180))
    sx, sz = sw
    if shot == "crane":
        z = 8.5 - 5.5 * p; place("crane", (0 + sx, 11.2, z), (0, 3.0, 1.0 + 0.3 * p))
    elif shot == "r_close":
        place("r_close", (-0.5 + sx, 10.7 - 0.2 * p, 2.0 + sz), (-0.85, 7.9, 1.65))
    elif shot == "k_close":
        place("k_close", (0.55 + sx, 11.1 - 0.2 * p, 1.55 + sz), (0.9, 7.9, 0.85))
    elif shot == "charge":
        place("charge", (0.4 + sx, -1.5 + 2.5 * p, 1.4 + sz), (0, 12, 2.0), (0, 7, 1.5))
    elif shot == "in_wide":
        place("in_wide", (IX + sx, -4.0 + 0.6 * p, 2.3), (IX, 4, 1.4), (IX, 0.2, 1.4))
    elif shot == "in_r":
        place("in_r", (IX - 0.45 + sx, -2.3 + 0.2 * p, 1.95 + sz), (IX - 0.7, 0.2, 1.65))
    elif shot == "in_k":
        place("in_k", (IX + 0.5 + sx, -2.4 + 0.2 * p, 1.35 + sz), (IX + 0.7, 0.2, 0.85))
    else:
        sxk, syk = SOLO[0].location.x, SOLO[0].location.y
        place("end", (sxk - 1.3 + sx, syk + 2.6, 1.6), (sxk, syk, 1.25))
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
