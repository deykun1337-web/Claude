"""Blender (run with: blender -b -P scene3d.py -- plan.json outdir start end).
Builds a blocky Minecraft-like 3D set + characters and renders the frames described in plan.json."""
import bpy, json, math, os, random, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
PLAN = json.load(open(argv[0])); OUTDIR = argv[1]; START = int(argv[2]); END = int(argv[3])
HERE = os.path.dirname(os.path.abspath(__file__)); TEX = os.path.join(HERE, "build", "tex")
os.makedirs(OUTDIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 720, 1280
sc.render.image_settings.file_format = "PNG"
ee = sc.eevee
ee.taa_render_samples = 12
ee.use_gtao = True; ee.gtao_distance = 0.6
ee.use_bloom = True; ee.bloom_intensity = 0.06; ee.bloom_threshold = 0.9
ee.use_soft_shadows = True; ee.shadow_cube_size = "1024"; ee.shadow_cascade_size = "2048"
ee.use_ssr = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.35

_imgs = {}


def img(name):
    if name not in _imgs:
        _imgs[name] = bpy.data.images.load(os.path.join(TEX, name + ".png"))
    return _imgs[name]


def mat_tex(name, tex, rough=0.65, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexImage"); n.image = img(tex); n.interpolation = "Closest"
    nt.links.new(n.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    if emit:
        nt.links.new(n.outputs["Color"], bsdf.inputs["Emission Color"]); bsdf.inputs["Emission Strength"].default_value = emit
    m["texnode"] = n.name
    return m


def mat_col(name, col, rough=0.6, emit=0.0, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    c = tuple(int(col[i:i + 2], 16) / 255 for i in (1, 3, 5))
    c = tuple(v ** 2.2 for v in c) + (1,)
    b.inputs["Base Color"].default_value = c; b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = c; b.inputs["Emission Strength"].default_value = emit
    return m


def set_tex(m, tex):
    m.node_tree.nodes[m["texnode"]].image = img(tex)


def box(name, w, d, h, loc, mats, parent=None):
    """Box with full 0..1 UVs on every face. mats: dict with keys front/back/left/right/top/bottom/other."""
    x0, x1, y0, y1, z0, z1 = -w / 2, w / 2, -d / 2, d / 2, -h / 2, h / 2
    faces = {"front": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
             "back": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
             "left": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
             "right": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
             "top": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
             "bottom": [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)]}
    verts = []; fidx = []; order = list(faces)
    for k in order:
        fidx.append([len(verts) + i for i in range(4)]); verts += faces[k]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], fidx); me.update()
    uv = me.uv_layers.new()
    for poly in me.polygons:
        for li, (u, v) in zip(poly.loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))):
            uv.data[li].uv = (u, v)
    slots = []
    for k in order:
        m = mats.get(k, mats.get("other"))
        if m not in slots: slots.append(m)
    for m in slots: me.materials.append(m)
    for poly, k in zip(me.polygons, order):
        poly.material_index = slots.index(mats.get(k, mats.get("other")))
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob.location = loc
    if parent: ob.parent = parent
    return ob


def empty(name, loc=(0, 0, 0), rot_z=0.0, parent=None):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e)
    e.location = loc; e.rotation_euler = (0, 0, math.radians(rot_z))
    if parent: e.parent = parent
    return e


def area(name, loc, target, power, col=(1, 1, 1), size=2.0):
    l = bpy.data.lights.new(name, "AREA"); l.energy = power; l.color = col; l.size = size
    o = bpy.data.objects.new(name, l); bpy.context.collection.objects.link(o); o.location = loc
    look(o, target); return o


def point(name, loc, power, col):
    l = bpy.data.lights.new(name, "POINT"); l.energy = power; l.color = col; l.shadow_soft_size = 0.3
    o = bpy.data.objects.new(name, l); bpy.context.collection.objects.link(o); o.location = loc; return o


def look(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def world(col, strength):
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = col + (1,); bg.inputs[1].default_value = strength


# ------------------------------------------------------------- characters
HUMAN = PLAN["human"]
GX, KX = -0.85, 0.85
H_ROT, K_ROT = -18, 14

h_root = empty("human", (GX, 0, 0), H_ROT)
face_m = mat_tex("hface", f"{HUMAN}_face_neutral_0_0", 0.55)
if HUMAN == "girl":
    hair = mat_tex("hair", "girl_hair", 0.5); shirt = mat_tex("shirt", "girl_shirt"); sleeve = mat_tex("sleeve", "girl_sleeve")
    skin = mat_tex("skin", "girl_skin"); legs = mat_tex("legs", "girl_legs"); hand = mat_tex("hand", "girl_hand")
    for sx in (-0.125, 0.125): box("leg", 0.25, 0.25, 0.75, (sx, 0, 0.375), {"other": legs}, h_root)
    box("body", 0.5, 0.25, 0.75, (0, 0, 1.125), {"front": shirt, "other": sleeve}, h_root)
    head = box("head", 0.5, 0.5, 0.5, (0, 0, 1.75), {"front": face_m, "other": hair}, h_root)
    box("hair_back", 0.56, 0.1, 0.95, (0, 0.27, 1.5), {"other": hair}, h_root)
    for sx in (-0.275, 0.275): box("hair_side", 0.06, 0.42, 0.7, (sx, 0.02, 1.62), {"other": hair}, h_root)
    arms = []
    for sx in (-0.37, 0.37):
        piv = empty("shoulder", (sx, 0, 1.47), 0, h_root)
        box("sleeve", 0.24, 0.24, 0.36, (0, 0, -0.16), {"other": sleeve}, piv)
        box("arm", 0.22, 0.22, 0.4, (0, 0, -0.52), {"bottom": hand, "other": skin}, piv)
        arms.append(piv)
else:
    side = mat_tex("side", "guy_side"); cap = mat_tex("cap", "guy_cap"); shirt = mat_tex("shirt", "guy_shirt")
    arm_m = mat_tex("arm", "guy_arm"); legs = mat_tex("legs", "guy_legs")
    for sx in (-0.125, 0.125): box("leg", 0.25, 0.25, 0.75, (sx, 0, 0.375), {"other": legs}, h_root)
    box("body", 0.5, 0.25, 0.75, (0, 0, 1.125), {"other": shirt}, h_root)
    head = box("head", 0.5, 0.5, 0.5, (0, 0, 1.75), {"front": face_m, "top": cap, "other": side}, h_root)
    box("cap", 0.53, 0.53, 0.1, (0, 0, 2.02), {"other": cap}, h_root)
    box("brim", 0.5, 0.24, 0.035, (0, -0.35, 1.955), {"other": cap}, h_root)
    arms = []
    for sx in (-0.37, 0.37):
        piv = empty("shoulder", (sx, 0, 1.47), 0, h_root)
        box("arm", 0.24, 0.24, 0.74, (0, 0, -0.35), {"other": arm_m}, piv)
        arms.append(piv)

k_root = empty("klod", (KX, 0, 0), K_ROT)
kface = mat_tex("kface", "klod_face_neutral_0_0", 0.6)
kside = mat_tex("kside", "klod_side"); ktop = mat_tex("ktop", "klod_top"); kdark = mat_tex("kdark", "klod_dark")
ksnout = mat_tex("ksnout", "klod_snout", 0.5); tusk = mat_col("tusk", "#FFF6E6", 0.3)
for lx in (-0.36, 0.36):
    for ly in (-0.22, 0.22): box("kleg", 0.17, 0.17, 0.3, (lx, ly, 0.15), {"other": kdark}, k_root)
box("kbody", 1.0, 0.75, 0.75, (0, 0, 0.675), {"front": kface, "top": ktop, "other": kside}, k_root)
box("snout", 0.38, 0.15, 0.19, (0, -0.445, 0.56), {"other": ksnout}, k_root)
for tx in (-0.25, 0.25):
    box("tusk", 0.05, 0.05, 0.12, (tx, -0.4, 0.535), {"other": tusk}, k_root)
    box("tusk_tip", 0.05, 0.05, 0.05, (tx + (0.02 if tx < 0 else -0.02), -0.4, 0.62), {"other": tusk}, k_root)
for ex in (-0.39, 0.39): box("ear", 0.17, 0.1, 0.17, (ex, -0.22, 1.13), {"other": kdark}, k_root)
rr = random.Random(4)
for k in range(7):
    box("mane", 0.07, 0.07, rr.uniform(0.06, 0.13), (-0.2 + k * 0.065, -0.05 + rr.uniform(-0.1, 0.1), 1.08), {"other": kdark}, k_root)

# ------------------------------------------------------------- sets
if PLAN["set"] == "salon":
    world((0.05, 0.02, 0.07), 0.6)
    wall = mat_col("wall", "#4A2468", 0.8)
    box("wall", 12, 0.2, 6, (0, 3.6, 3), {"other": wall})
    box("floor", 12, 8, 0.1, (0, 0, -0.05), {"other": mat_tex("floor", "floor_wood", 0.35)})
    city = mat_tex("city", "city", 0.9, emit=1.6)
    box("window", 2.4, 0.05, 2.6, (-2.0, 3.48, 2.35), {"front": city, "other": wall})
    frame = mat_col("frame", "#F4EAF7", 0.5)
    for (w, h, x, z) in ((2.6, 0.1, -2.0, 3.7), (2.6, 0.1, -2.0, 1.0), (0.1, 2.8, -3.25, 2.35), (0.1, 2.8, -0.75, 2.35), (0.06, 2.6, -2.0, 2.35), (2.4, 0.06, -2.0, 2.35)):
        box("frame", w, 0.12, h, (x, 3.42, z), {"other": frame})
    bulb = mat_col("bulb", "#FFD58A", 0.4, emit=12)
    for k in range(16):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(-3.3 + k * 0.17, 3.38, 3.85 - 0.08 * math.sin(k * 0.6)))
        bpy.context.object.data.materials.append(bulb)
    neon = mat_col("neon", "#FF4FB8", 0.4, emit=9)
    bpy.ops.object.text_add(location=(0.15, 3.47, 3.0), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object; t.data.body = "nails & tea"; t.data.size = 0.42; t.data.extrude = 0.02; t.data.materials.append(neon)
    bpy.ops.mesh.primitive_torus_add(location=(-0.2, 3.46, 3.12), rotation=(math.radians(90), 0, 0), major_radius=0.17, minor_radius=0.02)
    bpy.context.object.data.materials.append(neon)
    shelf = mat_col("shelf", "#F7EEF9", 0.4, emit=0.4)
    cols = ["#FF4F8B", "#C2185B", "#F06292", "#BA68C8", "#FF8A65", "#E91E63", "#F8BBD0", "#7E57C2", "#FFD54F"]
    bmats = [mat_col(f"pol{i}", c, 0.15) for i, c in enumerate(cols)]; capm = mat_col("capm", "#2A1A22", 0.3)
    rr = random.Random(9)
    for r in range(6):
        z = 0.9 + r * 0.5
        box("shelf", 3.6, 0.35, 0.04, (2.4, 3.3, z), {"other": shelf})
        for k in range(22):
            x = 0.75 + k * 0.155
            box("bottle", 0.09, 0.09, 0.15, (x, 3.3, z + 0.095), {"other": rr.choice(bmats)})
            box("bcap", 0.05, 0.05, 0.07, (x, 3.3, z + 0.205), {"other": capm})
    # manicure table near the girl
    tbl = mat_col("tbl", "#F4E9F7", 0.35)
    box("table", 1.3, 0.6, 0.06, (-1.6, 0.9, 0.8), {"other": tbl})
    for lx in (-2.15, -1.05): box("tleg", 0.06, 0.5, 0.78, (lx, 0.9, 0.39), {"other": tbl})
    box("uvlamp", 0.35, 0.25, 0.14, (-1.7, 0.85, 0.9), {"other": mat_col("uv", "#FFFFFF", 0.3)})
    box("uvglow", 0.28, 0.02, 0.06, (-1.7, 0.72, 0.87), {"other": mat_col("uvg", "#B388FF", 0.3, emit=8)})
    area("key", (-1.5, -3.2, 3.4), (0, 0, 1.2), 380, (1.0, 0.86, 0.92), 2.5)
    area("fill", (3.0, -2.5, 2.0), (0, 0, 1.0), 120, (0.8, 0.7, 1.0), 2.0)
    area("rim", (0.5, 2.6, 3.2), (0, 0, 1.2), 420, (1.0, 0.45, 0.85), 2.0)
    point("winglow", (-2.0, 2.8, 2.4), 80, (1.0, 0.8, 0.5))
else:
    world((0.01, 0.012, 0.03), 0.6)
    wall = mat_col("wall", "#0A0D1E", 0.8)
    box("wall", 14, 0.2, 7, (0, 4.2, 3.5), {"other": wall})
    box("floor", 14, 9, 0.1, (0, 0, -0.05), {"other": mat_tex("floor", "floor_blue", 0.25)})
    code = mat_tex("code", "code", 0.9, emit=1.4)
    rr = random.Random(2)
    for k in range(9):
        x = -5 + k * 1.25 + rr.uniform(-0.3, 0.3); y = 3.0 + rr.uniform(-0.6, 1.0); z = rr.uniform(1.0, 3.6)
        p = box("codepanel", rr.uniform(1.4, 2.2), 0.02, rr.uniform(0.8, 1.4), (x, y, z), {"front": code, "other": wall})
        p.rotation_euler = (0, 0, math.radians(rr.uniform(-20, 20)))
    red = mat_col("red", "#FF2A2A", 0.4, emit=10)
    for k in range(14):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(rr.uniform(-4, 4), rr.uniform(2.2, 4.0), rr.uniform(0.6, 3.8)))
        bpy.context.object.data.materials.append(red)
    desk = mat_col("desk", "#1A2040", 0.4)
    box("desk", 1.6, 0.7, 0.06, (-2.2, 1.2, 0.78), {"other": desk})
    box("monitor", 0.9, 0.05, 0.55, (-2.2, 1.35, 1.15), {"front": mat_tex("scr", "code", 0.9, emit=2.0), "other": desk})
    area("key", (-1.2, -3.2, 3.2), (0, 0, 1.2), 520, (0.9, 0.92, 1.0), 2.5)
    area("fill", (3.0, -2.2, 1.8), (0, 0, 1.0), 160, (0.6, 0.7, 1.0), 2.0)
    area("rim", (0.0, 2.8, 3.0), (0, 0, 1.2), 650, (0.35, 0.45, 1.0), 2.5)
    point("mon", (-2.2, 0.9, 1.2), 60, (0.5, 0.6, 1.0))

# ------------------------------------------------------------- cameras
def cam(name, lens, fstop):
    c = bpy.data.cameras.new(name); c.lens = lens; c.sensor_fit = "VERTICAL"; c.sensor_height = 24
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, c); bpy.context.collection.objects.link(o); return o


h_head = Vector((GX, 0, 1.75)); k_face = Vector((KX, -0.38, 0.62))
# camera bases: (position, target, focus target)
def h_dir(rot):  # direction the human faces (towards -Y rotated)
    a = math.radians(rot); return Vector((math.sin(-a) * -1, -math.cos(a), 0))


CAMS = {
    "girl": (cam("c_h", 36, 1.8), h_head + Vector((0.55, -2.25, -0.02)), h_head + Vector((0.0, 0, -0.06))),
    "nik": (cam("c_k", 36, 2.0), k_face + Vector((-0.55, -2.35, 0.35)), k_face + Vector((0.0, 0.1, 0.05))),
    "wide": (cam("c_w", 28, 4.0), Vector((0.0, -6.2, 1.55)), Vector((0, 0.5, 1.0))),
}


def place_cam(shot, push, sway):
    o, pos, tgt = CAMS[shot]
    d = (tgt - pos)
    p = pos + d * (0.10 * push) + Vector((sway[0], 0, sway[1]))
    o.location = p; look(o, tgt + Vector((sway[0] * 0.5, 0, 0)))
    o.data.dof.focus_distance = (tgt - p).length
    sc.camera = o


# ------------------------------------------------------------- render loop
for fr in range(START, min(END, len(PLAN["frames"]))):
    F = PLAN["frames"][fr]
    h = F["h"]; k = F["k"]
    set_tex(face_m, f'{HUMAN}_face_{h["expr"]}_{h["m"]}_{h["b"]}')
    set_tex(kface, f'klod_face_{k["expr"]}_{k["m"]}_{k["b"]}')
    if HUMAN == "girl":
        arms[1].rotation_euler = (math.radians(-150 * h.get("arm", 0)), 0, math.radians(-15 * h.get("arm", 0)))
    h_root.location.z = F.get("hop", 0.0)
    k_root.location.z = k.get("hop", 0.0)
    h_root.rotation_euler.z = math.radians(H_ROT + h.get("turn", 0)); k_root.rotation_euler.z = math.radians(K_ROT + k.get("turn", 0))
    place_cam(F["shot"], F["push"], F["sway"])
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
