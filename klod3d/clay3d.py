"""Blender: «Уровни редкости кабанов» — claymation (plasticine) stop-motion look.
Rarity tower: four pedestals climbing up (Rare -> Super rare -> Epic -> Mythic), characters drop in with squash.
Usage: blender -b -P clay3d.py -- plan.json outdir start end   (renders even frames only: animation on twos)"""
import bpy, json, math, os, random, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "scene3d.py")).read()
exec(_src[:_src.index("# ------------------------------------------------------------- characters")])
ee = sc.eevee
ee.taa_render_samples = 14; ee.bloom_intensity = 0.08; ee.bloom_threshold = 0.85; ee.bloom_radius = 5.5
ee.use_gtao = True; ee.gtao_distance = 0.35; ee.gtao_factor = 1.3
ee.use_volumetric_lights = True; ee.volumetric_tile_size = "8"; ee.volumetric_samples = 12; ee.volumetric_end = 25
sc.view_settings.look = "AgX - Base Contrast"; sc.view_settings.exposure = -0.2
F_ = PLAN; S, E, DROP, BANNER = F_["S"], F_["E"], F_["drop"], F_["banner"]
random.seed(4)


def rgb(h):
    return tuple((int(h[i:i + 2], 16) / 255) ** 2.2 for i in (1, 3, 5)) + (1,)


def clay(name, col, rough=0.5, bump=0.35, sheen=0.25, metal=0.0, emit=0.0):
    """Plasticine: soft roughness, a bit of subsurface, fingerprint dents + fine noise bump in object space."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(col); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Subsurface Weight"].default_value = 0.08; b.inputs["Subsurface Radius"].default_value = (0.05, 0.03, 0.02)
    b.inputs["Sheen Weight"].default_value = sheen
    if emit: b.inputs["Emission Color"].default_value = rgb(col); b.inputs["Emission Strength"].default_value = emit
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature = "SMOOTH_F1"; vo.inputs["Scale"].default_value = 9
    no = nt.nodes.new("ShaderNodeTexNoise"); no.inputs["Scale"].default_value = 60; no.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"]); nt.links.new(tc.outputs["Object"], no.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MULTIPLY_ADD"; mx.inputs[1].default_value = 0.35
    nt.links.new(no.outputs["Fac"], mx.inputs[0]); nt.links.new(vo.outputs["Distance"], mx.inputs[2])
    bu = nt.nodes.new("ShaderNodeBump"); bu.inputs["Strength"].default_value = bump; bu.inputs["Distance"].default_value = 0.02
    nt.links.new(mx.outputs[0], bu.inputs["Height"]); nt.links.new(bu.outputs["Normal"], b.inputs["Normal"])
    return m


def glow(name, col, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(col); b.inputs["Emission Color"].default_value = rgb(col)
    b.inputs["Emission Strength"].default_value = strength; return m


def link(o, parent=None):
    bpy.context.collection.objects.link(o)
    if parent: o.parent = parent
    return o


def blob(name, mat, els, parent=None, res=0.045):
    """Metaball family = soft merged clay forms. els: (type, (x,y,z), radius, (sx,sy,sz))."""
    mb = bpy.data.metaballs.new(name); mb.resolution = res * 1.6; mb.render_resolution = res; mb.threshold = 0.25
    for typ, co, r, sz in els:
        e = mb.elements.new(); e.type = typ; e.co = co; e.radius = r
        if typ in ("ELLIPSOID", "CAPSULE", "CUBE"):
            e.size_x, e.size_y, e.size_z = sz
    o = bpy.data.objects.new(name, mb); o.data.materials.append(mat); return link(o, parent)


def ball(name, mat, loc, r, scale=(1, 1, 1), parent=None, seg=32):
    me = bpy.data.meshes.new(name)
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me); o.location = loc; o.scale = scale; return link(o, parent)


def cyl(name, mat, loc, r, h, parent=None, seg=48, r2=None):
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me); o.location = loc; link(o, parent)
    bv = o.modifiers.new("bev", "BEVEL"); bv.width = min(0.04, h * 0.3); bv.segments = 4
    for p in me.polygons: p.use_smooth = True
    me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(40)
    return o


def torus(name, mat, loc, R, r, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=64, minor_segments=16, location=loc)
    o = bpy.context.object; o.data.materials.append(mat); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o


def blk(name, mat, loc, dims, parent=None, bev=0.03):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.name = name
    o.scale = (dims[0] / 2, dims[1] / 2, dims[2] / 2); o.data.materials.append(mat)
    m = o.modifiers.new("bev", "BEVEL"); m.width = bev; m.segments = 4; bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o


FONT = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf")


def text3d(body, loc, size, mat, parent=None, extrude=0.03):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, 0))
    o = bpy.context.object; o.data.body = body; o.data.font = FONT; o.data.size = size; o.data.extrude = extrude
    o.data.bevel_depth = 0.008; o.data.align_x = "CENTER"; o.data.align_y = "CENTER"; o.data.materials.append(mat)
    if parent: o.parent = parent
    return o


# ================================================================ set: velvet night stage + rarity tower
RCOL = ["#3BA0FF", "#B45CFF", "#FFB21F", "#FF3B5C"]
PED = [(-0.55, 0.0, 0.0), (0.6, 1.8, 0.95), (-0.5, 3.6, 1.9), (0.05, 5.6, 2.95)]
floor = clay("floor", "#2A2340", 0.7, 0.5)
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 8, 0)); bpy.context.object.data.materials.append(floor)
# cyclorama: back wall curving into the floor
import bmesh
me = bpy.data.meshes.new("cyc"); bm = bmesh.new(); prof = []
for k in range(13):
    a = math.radians(90 * k / 12); prof.append((12 + 4 * math.sin(a), 4 - 4 * math.cos(a)))
prof += [(16, 4 + 2.5 * k) for k in range(1, 7)]
rows = []
for x in (-20, 20):
    rows.append([bm.verts.new((x, y, z)) for y, z in prof])
for k in range(len(prof) - 1):
    bm.faces.new((rows[0][k], rows[1][k], rows[1][k + 1], rows[0][k + 1]))
bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = True
wall = clay("wall", "#231B3D", 0.8, 0.6)
link(bpy.data.objects.new("cyc", me)).data.materials.append(wall)
# clay stars + fairy-light bokeh on the backdrop
starm = glow("starm", "#FFE7A8", 6.0)
for k in range(70):
    x = random.uniform(-9, 9); z = random.uniform(2.0, 15); y = 15.4 if z > 4 else 12 + 4 * math.sin(math.acos(max(-1, min(1, (4 - z) / 4))))
    ball("star", starm, (x, min(y, 15.6), z), random.uniform(0.03, 0.09))
# clay clouds on the floor around the tower
cloudm = clay("cloud", "#4B3F70", 0.75, 0.6)
for k in range(9):
    cx, cy = random.choice((-1, 1)) * random.uniform(1.6, 3.4), random.uniform(-0.5, 7.5)
    blob(f"cloud{k}", cloudm, [("BALL", (random.uniform(-0.5, 0.5), random.uniform(-0.3, 0.3), 0.1), random.uniform(0.45, 0.7), (1, 1, 1)) for _ in range(4)]).location = (cx, cy, 0)

PEDS = []; RINGS = []; RLIGHT = []; BEAM = []
pedm = clay("ped", "#ECE3D2", 0.55, 0.4)
for i, (x, y, z) in enumerate(PED):
    h = z + 0.35
    cyl(f"ped{i}", pedm, (x, y, h / 2), 0.78, h)
    cyl(f"pedtop{i}", clay(f"ptop{i}", RCOL[i], 0.45, 0.4), (x, y, h + 0.04), 0.7, 0.08)
    ring = torus(f"ring{i}", glow(f"ringm{i}", RCOL[i], 0.0), (x, y, h + 0.03), 0.74, 0.035); RINGS.append(ring)
    # rarity plate on the front of the column
    plate = text3d(["RARE", "SUPER RARE", "EPIC", "MYTHIC"][i], (x, y - 0.8, max(0.25, h - 0.28)), 0.17 if i == 1 else 0.22, clay(f"txt{i}", RCOL[i], 0.4, 0.2))
    # rim + top spot in rarity colour (switched on at the reveal)
    L = bpy.data.lights.new(f"spot{i}", "SPOT"); L.energy = 0; L.color = rgb(RCOL[i])[:3]; L.spot_size = math.radians(38); L.spot_blend = 0.6
    L.shadow_soft_size = 0.3
    lo = link(bpy.data.objects.new(f"spot{i}", L)); lo.location = (x, y + 0.4, h + 4.2); look(lo, Vector((x, y, h)))
    P = bpy.data.lights.new(f"rim{i}", "POINT"); P.energy = 0; P.color = rgb(RCOL[i])[:3]; P.shadow_soft_size = 0.5
    po = link(bpy.data.objects.new(f"rim{i}", P)); po.location = (x + 0.3, y + 1.0, h + 1.2)
    RLIGHT.append((L, P)); PEDS.append((x, y, h))

# key + fill (warm key, cool fill: classic stop-motion studio)
key = area("key", (-3.5, -4.5, 6.0), (0, 2.5, 1.5), 900, (1.0, 0.86, 0.72), 3.0)
fill = area("fill", (4.5, -3.0, 3.0), (0, 2.5, 1.5), 250, (0.6, 0.7, 1.0), 4.0)
back = area("back", (0, 12, 6), (0, 3, 1.5), 400, (0.8, 0.5, 1.0), 5.0)
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.015, 0.04, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
vol = w.node_tree.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Density"].default_value = 0.006
w.node_tree.links.new(vol.outputs[0], w.node_tree.nodes["World Output"].inputs["Volume"])

# ================================================================ characters (all face -Y)
white = clay("white", "#FBF6EC", 0.35, 0.2); black = clay("black", "#141218", 0.12, 0.05, sheen=0.0)
mouthm = clay("mouth", "#3A0E14", 0.4, 0.1); tongue = clay("tongue", "#E8607A", 0.4, 0.2)
CHARS = []


def eyes(root, x, y, z, r=0.085, pupil=0.045, lidm=None):
    E_ = []
    for sx in (-1, 1):
        ey = empty(f"eye{sx}", (sx * x, y, z), parent=root)
        ball("sclera", white, (0, 0, 0), r, parent=ey)
        ball("pupil", black, (0, -r * 0.72, 0), pupil, (1, 0.6, 1), parent=ey)
        ball("glint", glow("glint", "#FFFFFF", 4.0), (r * 0.25, -r * 0.98, r * 0.3), r * 0.15, parent=ey)
        E_.append(ey)
    return E_


def boar(prefix, col, snoutcol, scale=1.0, buff=False):
    root = empty(prefix, (0, 0, -20))
    body = clay(prefix + "b", col, 0.5, 0.45)
    els = [("ELLIPSOID", (0, 0.15, 0.62), 0.62, (0.95, 1.25, 0.85)),
           ("BALL", (0, -0.42, 0.78), 0.5, (1, 1, 1)),
           ("ELLIPSOID", (-0.25, -0.45, 1.1), 0.24, (0.6, 0.4, 1.1)), ("ELLIPSOID", (0.25, -0.45, 1.1), 0.24, (0.6, 0.4, 1.1)),
           ("ELLIPSOID", (0, 0.25, 0.95), 0.3, (0.4, 1.4, 0.5))]
    for lx in (-0.3, 0.3):
        for ly in (-0.3, 0.55): els.append(("ELLIPSOID", (lx, ly, 0.2), 0.22, (0.8, 0.8, 1.3)))
    if buff:
        els += [("BALL", (-0.42, -0.25, 0.75), 0.38, (1, 1, 1)), ("BALL", (0.42, -0.25, 0.75), 0.38, (1, 1, 1)),
                ("ELLIPSOID", (0, -0.4, 0.55), 0.45, (1.2, 0.9, 0.8))]
    blob(prefix + "body", body, els, root)
    sn = blob(prefix + "snout", clay(prefix + "s", snoutcol, 0.45, 0.35), [("ELLIPSOID", (0, -0.86, 0.66), 0.26, (1.0, 0.55, 0.8))], root)
    for sx in (-1, 1): ball("nostril", black, (sx * 0.07, -0.97, 0.68), 0.028, (1, 0.6, 1.3), parent=root)
    mouth = ball("mouth", mouthm, (0, -0.74, 0.5), 0.11, (1.0, 0.5, 0.25), parent=root)
    for sx in (-1, 1):
        t = blob(prefix + f"tusk{sx}", white, [("CAPSULE", (0, 0, 0), 0.05, (0.0, 0.0, 0.07))], root)
        t.location = (sx * 0.19, -0.78, 0.52); t.rotation_euler = (0, math.radians(sx * 25), 0)
    E_ = eyes(root, 0.17, -0.68, 0.98)
    root.scale = (scale,) * 3
    return root, mouth, E_


# --- RARE: plain forest boar with an acorn
R0, M0, E0 = boar("rare", "#8A5A3B", "#C98B6B")
acorn = empty("acorn", (0.0, -0.9, 0.46), parent=R0)
ball("nut", clay("nut", "#B9772E", 0.45, 0.4), (0, 0, 0), 0.09, (1, 1, 1.25), parent=acorn)
ball("cap", clay("acap", "#5A3A1E", 0.8, 0.8), (0, 0, 0.08), 0.085, (1.05, 1.05, 0.6), parent=acorn)
# --- SUPER RARE: gym boar (bulky, red sweatband, dumbbell in teeth)
R1, M1, E1 = boar("buff", "#5E4A44", "#B07F74", 1.08, buff=True)
torus("band", clay("band", "#E8343F", 0.6, 0.6), (0, -0.42, 1.0), 0.29, 0.065, parent=R1)
db = empty("dumbbell", (0, -0.86, 0.5), parent=R1)
blk("bar", clay("steel", "#9AA3AE", 0.25, 0.1, metal=0.6), (0, 0, 0), (0.9, 0.06, 0.06), parent=db, bev=0.02)
for sx in (-1, 1): cyl("plate", clay("plate", "#1E1E24", 0.4, 0.3), (sx * 0.4, 0, 0), 0.17, 0.09, parent=db).rotation_euler = (0, math.radians(90), 0)
# --- EPIC: Klod — Claude boar (terracotta, white starburst, glowing laptop)
R2, M2, E2 = boar("klod", "#D97757", "#F0A68A")
for k in range(8):
    a = k * math.pi / 4
    ray = blk(f"ray{k}", white, (0.06 * math.sin(a), -0.64, 1.055 + 0.06 * math.cos(a)), (0.035, 0.03, 0.09), parent=R2, bev=0.014)
    ray.rotation_euler = (math.radians(-15), a, 0)
ball("core", white, (0, -0.65, 1.055), 0.038, parent=R2)
lap = empty("laptop", (0.55, -0.85, 0.0), 35, parent=R2)
blk("lbase", clay("lap", "#3B3F47", 0.35, 0.2, metal=0.3), (0, 0, 0.02), (0.62, 0.42, 0.04), parent=lap, bev=0.015)
scr = empty("scr", (0, 0.2, 0.04), parent=lap); scr.rotation_euler = (math.radians(-12), 0, 0)
blk("lid", clay("lap2", "#3B3F47", 0.35, 0.2, metal=0.3), (0, 0, 0.2), (0.62, 0.03, 0.4), parent=scr, bev=0.015)
screenm = glow("screen", "#FFD7B8", 2.2); blk("screen", screenm, (0, -0.02, 0.2), (0.56, 0.01, 0.34), parent=scr, bev=0.004)
for k in range(5):
    blk("code", glow(f"code{k}", ["#D97757", "#3B3F47", "#7A5CFF", "#3B3F47", "#D97757"][k], 1.5),
        (-0.2 + random.uniform(0, 0.1) + 0.0, -0.03, 0.32 - k * 0.055), (random.uniform(0.15, 0.32), 0.005, 0.025), parent=scr, bev=0.002)
# --- MYTHIC: Ruslan ДЕЙКУН Кабанович in clay (black cap, cheek tattoos, grey hoodie) + crown, red cape, gold chain
R3 = empty("ruslan", (0, 0, -20))
skin = clay("skin", "#E8BFA2", 0.5, 0.3); hood = clay("hood", "#F2F0EC", 0.7, 0.6); pants = clay("pants", "#3C5A8C", 0.7, 0.6)  # v2: white tee, jeans
gold = clay("gold", "#F2B53A", 0.22, 0.15, metal=0.85); cape = clay("cape", "#B3122E", 0.6, 0.5, sheen=0.6)
blob("rlegs", pants, [("ELLIPSOID", (-0.16, 0, 0.5), 0.23, (0.7, 0.7, 2.1)), ("ELLIPSOID", (0.16, 0, 0.5), 0.23, (0.7, 0.7, 2.1))], R3)
for sx in (-1, 1):
    blk("stripe", white, (sx * 0.265, -0.02, 0.45), (0.02, 0.05, 0.5), parent=R3, bev=0.008)
    blob(f"shoe{sx}", white, [("ELLIPSOID", (sx * 0.17, -0.08, 0.09), 0.2, (0.9, 1.4, 0.55))], R3)
blob("rbody", hood, [("ELLIPSOID", (0, 0, 1.1), 0.58, (1.0, 0.75, 1.0)), ("ELLIPSOID", (-0.48, -0.02, 1.0), 0.22, (0.6, 0.6, 1.5)),
                     ("ELLIPSOID", (0.48, -0.02, 1.0), 0.22, (0.6, 0.6, 1.5)), ("ELLIPSOID", (0, 0.05, 1.42), 0.3, (1.3, 0.8, 0.5))], R3)
for sx in (-1, 1): ball("hand", skin, (sx * 0.49, -0.06, 0.72), 0.1, parent=R3)
blob("rhead", skin, [("BALL", (0, -0.02, 1.8), 0.5, (1, 1, 1)), ("BALL", (-0.37, 0.0, 1.78), 0.14, (1, 1, 1)), ("BALL", (0.37, 0.0, 1.78), 0.14, (1, 1, 1))], R3)
capm = clay("capm", "#F0569A", 0.55, 0.5)  # v2: pink DEYKUN cap
blob("rcap", capm, [("ELLIPSOID", (0, 0.03, 2.0), 0.56, (1.0, 1.0, 0.62))], R3)
blob("rbrim", capm, [("ELLIPSOID", (0, -0.4, 1.99), 0.34, (0.9, 0.8, 0.14))], R3)
blk("capprint", white, (0, -0.37, 2.1), (0.22, 0.02, 0.045), parent=R3, bev=0.01)

E3 = eyes(R3, 0.14, -0.33, 1.8, 0.07, 0.04)
for sx in (-1, 1):
    blob(f"lid{sx}", clay("lid", "#C99A80", 0.5, 0.3), [("ELLIPSOID", (sx * 0.14, -0.34, 1.85), 0.12, (1.0, 0.8, 0.45))], R3)
    blk(f"brow{sx}", clay("brow", "#3A2A20", 0.7, 0.4), (sx * 0.14, -0.33, 1.92), (0.14, 0.04, 0.035), parent=R3, bev=0.012)
    for k in range(3):
        ball("blush", clay("blush", "#F2A9A0", 0.6, 0.2), (sx * 0.22, -0.28, 1.68), 0.035 if k == 0 else 0.001, parent=R3)  # v2: no tattoos, blush
blk("stache", clay("stache", "#8E6A55", 0.7, 0.6), (0, -0.335, 1.64), (0.18, 0.04, 0.03), parent=R3, bev=0.012)
ball("nose", skin, (0, -0.37, 1.72), 0.065, parent=R3)
M3 = ball("rmouth", mouthm, (0, -0.31, 1.57), 0.08, (1.0, 0.5, 0.2), parent=R3)
# crown + chain + cape
crown = empty("crown", (0, 0.02, 2.27), parent=R3)
cyl("crownb", gold, (0, 0, 0), 0.3, 0.14, parent=crown, seg=40)
for k in range(5):
    a = k * 2 * math.pi / 5
    c = cyl("spike", gold, (0.26 * math.sin(a), 0.26 * math.cos(a), 0.14), 0.06, 0.16, parent=crown, seg=12, r2=0.0)
    ball("gem", glow("gem", ["#FF2E4D", "#3BA0FF", "#3DDC84", "#FFB21F", "#B45CFF"][k], 3.0), (0.3 * math.sin(a), 0.3 * math.cos(a) - 0.0, 0.0), 0.035, parent=crown)
for k in range(11):
    a = math.radians(-70 + 14 * k)
    ball("chain", gold, (0.28 * math.sin(a), -0.3 - 0.05 * math.cos(a), 1.5 - 0.22 * math.cos(a)), 0.04, parent=R3)
ball("medal", gold, (0, -0.33, 1.22), 0.09, (1, 0.4, 1), parent=R3)
blob("cape", cape, [("ELLIPSOID", (0, 0.42, 1.0), 0.6, (1.1, 0.25, 1.35)), ("ELLIPSOID", (0, 0.3, 1.5), 0.45, (1.2, 0.3, 0.3))], R3)
R3.scale = (0.92,) * 3

CH = [(R0, M0, E0), (R1, M1, E1), (R2, M2, E2), (R3, M3, E3)]

# --- the booster pack («КАБАН ПАК») floating over pedestal 0
PACK = empty("pack", (PED[0][0], PED[0][1], 1.2))
foil = bpy.data.materials.new("foil"); foil.use_nodes = True
nt = foil.node_tree; b = nt.nodes["Principled BSDF"]; b.inputs["Metallic"].default_value = 0.9; b.inputs["Roughness"].default_value = 0.22
ramp = nt.nodes.new("ShaderNodeValToRGB"); lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.6
nt.links.new(lw.outputs["Facing"], ramp.inputs["Fac"])
cr = ramp.color_ramp; cr.elements[0].color = rgb("#7A5CFF"); cr.elements[1].color = rgb("#FF6FB0")
e2 = cr.elements.new(0.5); e2.color = rgb("#3BE0FF")
nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
blk("packbody", foil, (0, 0, 0), (0.85, 0.16, 1.2), parent=PACK, bev=0.05)
for z in (0.62, -0.62): blk("crimp", foil, (0, 0, z), (0.88, 0.06, 0.08), parent=PACK, bev=0.01)
text3d("КАБАН", (0, -0.1, 0.18), 0.2, clay("ptx", "#FFFFFF", 0.4, 0.1), PACK)
text3d("ПАК", (0, -0.1, -0.05), 0.24, clay("ptx2", "#FFD23F", 0.4, 0.1), PACK)
ball("packpig", clay("pp", "#F0A68A", 0.5, 0.3), (0, -0.1, -0.35), 0.13, (1, 0.4, 0.8), parent=PACK)

# confetti blobs per pedestal
CONF = []
for i in range(4):
    cols = [RCOL[i], "#FFFFFF", "#FFD23F"] if i < 3 else ["#FF3B5C", "#FFB21F", "#3BA0FF", "#3DDC84", "#B45CFF", "#FFFFFF"]
    mats = [clay(f"cf{i}{k}", c, 0.4, 0.3, emit=0.6) for k, c in enumerate(cols)]
    lst = []
    for k in range(26 if i < 3 else 44):
        o = ball("conf", mats[k % len(mats)], (0, 0, -30), random.uniform(0.035, 0.07), (1, 1, random.uniform(0.35, 0.7)), seg=12)
        a = random.uniform(0, 2 * math.pi); sp = random.uniform(1.2, 2.6)
        lst.append((o, Vector((math.cos(a) * sp * 0.8, math.sin(a) * sp * 0.5 - 0.6, random.uniform(2.2, 4.2))), random.uniform(0, 6)))
    CONF.append(lst)

CAM = bpy.data.cameras.new("cam"); CAM.lens = 40; CAM.sensor_fit = "VERTICAL"; CAM.sensor_height = 24
CAM.dof.use_dof = True; CAM.dof.aperture_fstop = 1.8
CO = link(bpy.data.objects.new("cam", CAM)); sc.camera = CO


def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def shot_for(i):
    """Camera (pos, target, lens) framing pedestal i, slightly from below for a hero look."""
    x, y, h = PEDS[i]
    hz = 0.75 if i < 3 else 1.05
    if i == 3: return Vector((x - 0.9, y - 4.3, h + 0.55)), Vector((x, y, h + 1.3)), 34
    return Vector((x - 0.95 * (1 if i % 2 == 0 else -1), y - 4.3, h + 0.95)), Vector((x, y, h + 0.82)), 36


WIDE = (Vector((0.4, -7.6, 2.7)), Vector((0.0, 2.8, 2.6)), 27)
INTRO = (Vector((PED[0][0] - 0.5, -4.6, 1.3)), Vector((PED[0][0], 0, 1.45)), 40)


def camera_at(t):
    # sequence of anchors (time, framing); transitions are quick whip-pans with an ease
    seq = [(0.0, INTRO), (DROP[0] - 0.05, shot_for(0)), (DROP[1] - 0.4, shot_for(1)), (DROP[2] - 0.4, shot_for(2)),
           (BANNER[3] - 0.35, shot_for(3)), (S[6] - 0.35, WIDE)]
    for k in range(len(seq) - 1, -1, -1):
        if t >= seq[k][0]: break
    t0, (p1, q1, l1) = seq[k]
    if k == 0:
        p0, q0, l0 = p1, q1, l1; a = 1
    else:
        p0, q0, l0 = seq[k - 1][1]; a = ease((t - t0) / (0.3 if k < 5 else 0.6))
    p = p0.lerp(p1, a); q = q0.lerp(q1, a); lens = l0 + (l1 - l0) * a
    # slow push-in during the hold
    hold = t - t0; push = min(1, hold / 3.0)
    d = (q - p); p = p + d * 0.08 * push
    return p, q, lens


def squash(t, t0):
    """Drop from the sky, land with a clay squash, wobble back."""
    u = t - t0
    if u < 0: return None
    if u < 0.2: return (3.0 * (1 - u / 0.2) ** 2, 0.85, 1.25)  # falling, stretched
    v = u - 0.2
    sq = 0.32 * math.exp(-v * 7) * math.cos(v * 26)
    return (0.0, 1 + sq * 0.6, 1 - sq)


frames = PLAN["frames"]
for fr in range(START, min(END, len(frames))):
    if fr % 2: continue  # animated on twos; compose duplicates odd frames
    F = frames[fr]; t = F["t"]; hold = int(round(t * 12))
    rnd = random.Random(hold)
    # characters
    for i, (root, mouth, eyes_) in enumerate(CH):
        x, y, h = PEDS[i]
        s = squash(t, DROP[i])
        if s is None:
            root.location = (0, 0, -20); continue
        dz, sxy, szz = s[0], s[1], s[2]
        base_s = 1.08 if i == 1 else (0.92 if i == 3 else 1.0)
        root.location = (x, y, h + 0.08 + dz)
        root.scale = (base_s * sxy, base_s * sxy, base_s * szz)
        root.rotation_euler = (0, 0, math.radians([-18, 16, -14, -10][i] + 3 * math.sin(t * 1.3 + i)))
        if i == 3 and t > DROP[3] + 0.4:
            root.rotation_euler = (0, 0, math.radians(-10 + 4 * math.sin(t * 1.6)))
        m = F["mouth"][i]
        mouth.scale = (1.0, 0.5, 0.18 + 0.9 * m)
        blink = F["blink"][i]
        for e in eyes_: e.scale = (1, 1, 0.12 if blink else 1)
    # props
    acorn.location.z = 0.42 + 0.02 * math.sin(t * 9) if F["mouth"][0] < 0.1 else 0.42 + 0.05 * F["mouth"][0]
    db.rotation_euler = (0, math.radians(6 * math.sin(t * 5)), 0)
    screenm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0 + 0.4 * rnd.random()
    # pack: shake harder towards the burst, then vanish
    if t < DROP[0] - 0.05:
        k = min(1, t / (DROP[0] - 0.1)); amp = 0.01 + 0.07 * k ** 2
        PACK.location = (PED[0][0] + rnd.uniform(-amp, amp), PED[0][1], 1.25 + 0.05 * math.sin(t * 3) + rnd.uniform(-amp, amp))
        PACK.rotation_euler = (0, math.radians(rnd.uniform(-4, 4) * k * 2), math.radians(-12 + rnd.uniform(-3, 3) * k))
        PACK.scale = (1 + 0.08 * k,) * 3
    else:
        PACK.location = (0, 0, -30)
    # confetti bursts
    for i, lst in enumerate(CONF):
        x, y, h = PEDS[i]; t0 = DROP[i] + 0.2 if i else DROP[0] - 0.05
        u = t - t0
        for o, v, sp in lst:
            if u < 0 or u > 2.2: o.location = (0, 0, -30); continue
            o.location = (x + v.x * u, y + v.y * u, h + 0.6 + v.z * u - 4.9 * u * u)
            if o.location.z < h + 0.1 and abs(o.location.x - x) < 0.75 and abs(o.location.y - y) < 0.75: o.location.z = h + 0.1
            elif o.location.z < 0.05: o.location.z = 0.05
            o.rotation_euler = (sp + u * 5, sp * 2 + u * 3, 0)
    # rarity lights (flash at reveal, then steady) + ring glow
    for i, (L, P) in enumerate(RLIGHT):
        on = t >= BANNER[i] - 0.1
        fl = math.exp(-max(0, t - (DROP[i] + 0.2)) * 3) if t >= DROP[i] + 0.2 else 0
        pre = 0
        if i == 3 and BANNER[3] - 0.1 <= t < DROP[3] + 0.2:  # mythic: pulsing build-up
            pre = 0.5 + 0.5 * math.sin((t - BANNER[3]) * 14 * (1 + (t - BANNER[3]) / 1.5))
        L.energy = (600 if on else 0) * (1 + 2.5 * fl) + 400 * pre
        P.energy = (60 if on else 0) * (1 + 4 * fl) * (1.3 if i == 3 else 1)
        RINGS[i].active_material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = (6 if on else 0) * (1 + 3 * fl) + 8 * pre
    # stop-motion flicker
    key.data.energy = 900 * (1 + rnd.uniform(-0.03, 0.03))
    # camera (+ tiny per-hold jitter like a hand-animated rig)
    p, q, lens = camera_at(t)
    p = p + Vector((rnd.uniform(-1, 1), 0, rnd.uniform(-1, 1))) * 0.004
    CO.location = p; look(CO, q); CAM.lens = lens
    CAM.dof.focus_distance = (q - p).length
    CAM.dof.aperture_fstop = 3.2 if t >= S[6] - 0.35 else 1.8
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
