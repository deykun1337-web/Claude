"""«Кабаново — деревня подписчиков»: low-poly valley, river, forest, campfire, Klod-boar, houses with subscriber nicks.
    blender -b -P klod3d/village3d.py -- <episode.json> <outdir> <start_frame> <end_frame> [preview]
episode.json: {"timing": "<timing.json>", "houses": [{"nick": "...", "slot": k}], "ghosts": N, "shots": "ep1"}
Houses come from reels/village/state.json via reels/village.py plan (real commenters' usernames only).
"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector, noise

HERE = "/home/user/Claude/klod3d"
argv = sys.argv[sys.argv.index("--") + 1:]
EP = json.load(open(argv[0])); OUT = argv[1]; PREVIEW = len(argv) > 4
FRAMES = [int(x) for x in argv[2].split(",")] if "," in argv[2] else list(range(int(argv[2]), int(argv[3])))
_src = open(os.path.join(HERE, "scene3d.py")).read().replace('PLAN = json.load(open(argv[0]))', 'PLAN = {}')
sys.argv = sys.argv[:sys.argv.index("--") + 1] + ["/dev/null", OUT, "0", "1"]
exec(_src[:_src.index("# ------------------------------------------------------------- characters")].replace('__file__', '"%s/scene3d.py"' % HERE))
exec(open(HERE + "/chars_smooth.py").read())
FPS = 30
sc.render.fps = FPS
sc.render.resolution_x, sc.render.resolution_y = (405, 720) if PREVIEW else (540, 960)
ee = sc.eevee; ee.taa_render_samples = 8 if PREVIEW else 10
ee.use_gtao = True; ee.gtao_distance = 1.2; ee.use_bloom = True; ee.bloom_intensity = 0.05; ee.bloom_threshold = 0.9
ee.use_soft_shadows = True; ee.shadow_cascade_size = "1024"; ee.use_motion_blur = False
sc.view_settings.exposure = 0.0
rng = random.Random(11)

# ---------------------------------------------------------------- world: Poly Haven sunset sky (light + colour)
w = sc.world or bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; nt = w.node_tree
env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(HERE + "/build/assets/kloppenheim_06_puresky.hdr")
bgn = nt.nodes["Background"]; nt.links.new(env.outputs[0], bgn.inputs[0]); bgn.inputs[1].default_value = 0.55
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.2; sun.color = (1.0, 0.78, 0.55); sun.angle = math.radians(3)
so = bpy.data.objects.new("sun", sun); bpy.context.collection.objects.link(so); so.rotation_euler = (math.radians(62), 0, math.radians(-38))


def flat_mat(name, col, rough=0.85, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    c = tuple((int(col[i:i + 2], 16) / 255) ** 2.2 for i in (1, 3, 5)) + (1,)
    b.inputs["Base Color"].default_value = c; b.inputs["Roughness"].default_value = rough
    if emit: b.inputs["Emission Color"].default_value = c; b.inputs["Emission Strength"].default_value = emit
    if alpha < 1: b.inputs["Alpha"].default_value = alpha; m.blend_method = "BLEND"; m.shadow_method = "NONE"
    return m


def mesh_obj(name, build, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), me=None):
    if me is None:
        me = bpy.data.meshes.new(name); bm = bmesh.new(); build(bm); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot; o.scale = scale
    return o


# ---------------------------------------------------------------- terrain with river (flat-shaded low-poly)
def river_x(y): return 7.0 + 5.0 * math.sin(y / 9.0) + 2.0 * math.sin(y / 3.7)


def height(x, y):
    d = math.hypot(x, y); h = 0.9 * noise.noise(Vector((x / 9, y / 9, 0.3))) + 0.25 * noise.noise(Vector((x / 3, y / 3, 1.7)))
    h += max(0, d - 18) * 0.12                                  # valley rises towards the edges
    h *= min(1, max(0.15, (d - 3) / 10))                         # flat clearing around the campfire
    r = abs(x - river_x(y)); h -= max(0, 1.6 - r) * 0.55         # river bed
    return h


def terrain(bm):
    bmesh.ops.create_grid(bm, x_segments=90, y_segments=90, size=45)
    for v in bm.verts: v.co.z = height(v.co.x, v.co.y)


grass = flat_mat("grass", "#6F8E3A", 0.95)
T = mesh_obj("terrain", terrain, grass)
for p in T.data.polygons: p.use_smooth = False
# per-face colour jitter for the low-poly look
ca = T.data.color_attributes.new("jit", "BYTE_COLOR", "CORNER")
for p in T.data.polygons:
    c = Vector(p.center); k = rng.uniform(-0.06, 0.06); dry = max(0, noise.noise(Vector((c.x / 14, c.y / 14, 5))) * 0.5)
    col = (0.30 + k + dry * 0.25, 0.42 + k + dry * 0.05, 0.12 + k * 0.5, 1)
    for li in p.loop_indices: ca.data[li].color = col
an = grass.node_tree.nodes.new("ShaderNodeVertexColor"); an.layer_name = "jit"
grass.node_tree.links.new(an.outputs[0], grass.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
water = flat_mat("water", "#3E95C2", 0.08)
water.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 0.6


def river(bm):
    prev = None
    for k in range(-46, 47):
        y = k * 1.0; x = river_x(y); a = bm.verts.new((x - 1.45, y, -0.18)); b = bm.verts.new((x + 1.45, y, -0.18))
        if prev: bm.faces.new((prev[0], prev[1], b, a))
        prev = (a, b)


mesh_obj("river", river, water)

# ---------------------------------------------------------------- forest (linked duplicates = fast)
fir_d = flat_mat("fir", "#2F5A2C", 0.9); leaf_cols = ["#5E8F36", "#7FA23A", "#C98A2E", "#B5651D", "#8DAA3F"]
leaf_m = [flat_mat(f"leaf{i}", c, 0.9) for i, c in enumerate(leaf_cols)]; trunk = flat_mat("trunk", "#5A3A22", 0.9)


def lcone(r, h, seg=6):
    return lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=0, depth=h)


def ico(r): return lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)


def lcyl(r, h, seg=5): return lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)


proto = {}


def proto_mesh(key, build, mat):
    if key not in proto:
        o = mesh_obj(key, build, mat, (0, 0, -100)); proto[key] = o.data
        for p in o.data.polygons: p.use_smooth = False
    return proto[key]


placed = 0
for k in range(2600):
    if placed > 520: break
    x, y = rng.uniform(-42, 42), rng.uniform(-42, 42); d = math.hypot(x, y)
    if d < 11.5 or abs(x - river_x(y)) < 2.6: continue
    if noise.noise(Vector((x / 11, y / 11, 9))) < -0.15 and d < 26: continue     # meadows
    z = height(x, y); s = rng.uniform(0.75, 1.35)
    if rng.random() < 0.55:
        mesh_obj("t", None, None, (x, y, z + 0.35 * s), scale=(s, s, s), me=proto_mesh("trunk", lcyl(0.13, 0.7), trunk))
        mesh_obj("f", None, None, (x, y, z + 1.6 * s), scale=(s, s, s), me=proto_mesh("fir1", lcone(0.95, 1.9), fir_d))
        mesh_obj("f", None, None, (x, y, z + 2.5 * s), scale=(s, s, s), me=proto_mesh("fir2", lcone(0.7, 1.5), fir_d))
    else:
        mi = rng.randrange(len(leaf_m))
        mesh_obj("t", None, None, (x, y, z + 0.45 * s), scale=(s, s, s), me=proto_mesh("trunk2", lcyl(0.12, 0.9), trunk))
        mesh_obj("l", None, None, (x, y, z + 1.45 * s), rot=(0, 0, rng.uniform(0, 6)), scale=(s, s, s * 0.9), me=proto_mesh(f"crown{mi}", ico(0.95), leaf_m[mi]))
    placed += 1
rockm = flat_mat("rock", "#8A8A84", 0.8)
for k in range(60):
    x, y = rng.uniform(-30, 30), rng.uniform(-30, 30)
    if math.hypot(x, y) < 5: continue
    s = rng.uniform(0.15, 0.4); mesh_obj("r", None, None, (x, y, height(x, y)), scale=(s, s * 1.2, s * 0.7), me=proto_mesh("rock", ico(1), rockm))

# ---------------------------------------------------------------- campfire, lean-to shelter, smoke, Klod
stone = flat_mat("stone", "#9A968E", 0.75); log = flat_mat("log", "#6B4226", 0.85)
for k in range(9):
    a = k / 9 * math.tau; mesh_obj("st", None, None, (0.75 * math.cos(a), 0.75 * math.sin(a), 0.08), scale=(0.2, 0.17, 0.13), me=proto_mesh("stone", ico(1), stone))
for k in range(4):
    a = k / 4 * math.tau + 0.4
    mesh_obj("lg", lcyl(0.07, 0.9, 6), log, (0.18 * math.cos(a), 0.18 * math.sin(a), 0.18), rot=(math.radians(62), 0, a + math.pi / 2))
fire_o = flat_mat("fire_o", "#FF5A12", 0.5, emit=5); fire_y = flat_mat("fire_y", "#FFB02E", 0.5, emit=7)
flames = [mesh_obj("fl", lcone(0.26, 0.75, 5), fire_o, (0, 0, 0.45)), mesh_obj("fl2", lcone(0.16, 0.5, 5), fire_y, (0.05, -0.08, 0.4)),
          mesh_obj("fl3", lcone(0.12, 0.45, 5), fire_o, (-0.12, 0.05, 0.36))]
fl_light = bpy.data.lights.new("fire", "POINT"); fl_light.color = (1.0, 0.55, 0.22); fl_light.shadow_soft_size = 0.3
fll = bpy.data.objects.new("fire", fl_light); bpy.context.collection.objects.link(fll); fll.location = (0, 0, 0.9)
for k in range(8):     # lean-to shelter: logs leaning on a ridge pole behind the fire
    y = 1.0 + (k - 3.5) * 0.3
    mesh_obj("sh", lcyl(0.075, 1.85, 6), log, (-1.95, y + 1.6, 0.72), rot=(0, math.radians(-35), 0))
mesh_obj("shb", lcyl(0.085, 2.9, 6), log, (-2.5, 2.6, 1.42), rot=(math.radians(90), 0, 0))
for yy in (1.35, 3.85): mesh_obj("shp", lcyl(0.07, 1.5, 6), log, (-2.5, yy, 0.72))
smoke_m = flat_mat("smoke", "#CFCBC2", 0.9, alpha=0.55)
puffs = [mesh_obj("p", ico(0.11), smoke_m, (0, 0, 1)) for _ in range(12)]
K = klod_smooth((-0.75, -1.25, 0), 21, 0.85)

# ---------------------------------------------------------------- houses: real subscribers or holographic ghosts
SLOTS = []
for k in range(60):
    a = k * 2.39996; r = 5.2 + 1.05 * math.sqrt(k) * 1.5
    x, y = r * math.cos(a), r * math.sin(a)
    if abs(x - river_x(y)) < 3.2: continue
    SLOTS.append((x, y, -a))
wallm = flat_mat("wall", "#E8C79A", 0.85); roofm = [flat_mat("roof0", "#B4532A", 0.8), flat_mat("roof1", "#C7652F", 0.8), flat_mat("roof2", "#8E3B22", 0.8)]
winm = flat_mat("win", "#FFC870", 0.4, emit=4); ghostm = flat_mat("ghost", "#9FE3FF", 0.3, emit=2.2, alpha=0.32)
plate_m = flat_mat("plate", "#1D1712", 0.6); txt_m = flat_mat("txt", "#FFFFFF", 0.5, emit=1.0)


def prism(bm):   # gable roof
    v = [bm.verts.new(p) for p in [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0), (0, -1, 0.75), (0, 1, 0.75)]]
    for f in [(0, 1, 4), (3, 5, 2), (0, 4, 5, 3), (1, 2, 5, 4), (0, 3, 2, 1)]: bm.faces.new([v[i] for i in f])


def label(text, loc, size=0.42):
    piv = bpy.data.objects.new("lbl", None); bpy.context.collection.objects.link(piv); piv.location = loc
    bpy.ops.object.text_add(location=(0, 0, 0)); t = bpy.context.object; t.data.body = text; t.data.size = size
    t.data.align_x = "CENTER"; t.data.align_y = "CENTER"; t.data.materials.append(txt_m); t.parent = piv; t.location = (0, 0, 0.01)
    t.data.font = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/Inter-Bold.otf")
    wdt = size * 0.62 * len(text) + 0.4
    pl = mesh_obj("pl", lambda bm: bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5), plate_m, (0, 0, 0), scale=(wdt, size * 1.7, 1)); pl.parent = piv
    return piv


houses, ghosts, labels = [], [], []
for i, hd in enumerate(EP.get("houses", [])):
    x, y, a = SLOTS[hd.get("slot", i)]; z = height(x, y)
    g = bpy.data.objects.new("house", None); bpy.context.collection.objects.link(g); g.location = (x, y, z); g.rotation_euler = (0, 0, a)
    for o in (mesh_obj("hw", lcyl(1, 1, 4), wallm, (0, 0, 0.6), rot=(0, 0, math.pi / 4), scale=(1.05, 1.05, 1.2)),
              mesh_obj("hr", prism, roofm[i % 3], (0, 0, 1.2), scale=(0.95, 0.95, 1.1)),
              mesh_obj("hwin", lambda bm: bmesh.ops.create_cube(bm, size=1), winm, (0, -0.75, 0.65), scale=(0.3, 0.02, 0.3))):
        o.parent = g
    houses.append(g); labels.append(label(hd["nick"], (x, y, z + 2.6)))
for j in range(EP.get("ghosts", 0)):
    x, y, a = SLOTS[len(houses) + j]; z = height(x, y)
    g = bpy.data.objects.new("ghost", None); bpy.context.collection.objects.link(g); g.location = (x, y, z); g.rotation_euler = (0, 0, a)
    for o in (mesh_obj("gw", lcyl(1, 1, 4), ghostm, (0, 0, 0.6), rot=(0, 0, math.pi / 4), scale=(1.05, 1.05, 1.2)),
              mesh_obj("gr", prism, ghostm, (0, 0, 1.2), scale=(0.95, 0.95, 1.1))):
        o.parent = g
    ghosts.append(g); labels.append(label("твой ник?", (x, y, z + 2.6)))

# ---------------------------------------------------------------- camera
c = bpy.data.cameras.new("cam"); c.sensor_fit = "VERTICAL"; c.sensor_height = 24; c.lens = 30; c.clip_end = 400
c.dof.use_dof = True; c.dof.aperture_fstop = 5.6
C = bpy.data.objects.new("cam", c); bpy.context.collection.objects.link(C); sc.camera = C
for lb in labels:
    con = lb.constraints.new("TRACK_TO"); con.target = C; con.track_axis = "TRACK_Z"; con.up_axis = "UP_Y"
TM = json.load(open(EP["timing"])); L = [s for s, d in TM["lines"]]


def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def lerp(a, b, k): return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


def shot(t):
    """returns camera position, target, lens for the episode-1 storyboard"""
    K1 = ((0, 0, 0.6), (1.4, -0.4, 0.6))
    if t < L[1] - 0.2:        # wide aerial orbit over the (future) village
        a = -1.0 + 0.11 * t; r = 30 - 0.6 * t
        return (r * math.cos(a), r * math.sin(a), 21 - 0.4 * t), (0, 0, 0), 30
    if t < L[2] - 0.2:        # closer pass over the house slots with nick plates
        k = ease((t - (L[1] - 0.2)) / (L[2] - L[1])); a = -0.45 + 0.25 * k
        p = lerp((17 * math.cos(-0.45), 17 * math.sin(-0.45), 12), (13 * math.cos(-0.2), 13 * math.sin(-0.2), 8), k)
        return p, (0, 0, 0.5), 32
    if t < L[3] - 0.3:        # descend to the campfire
        k = ease((t - (L[2] - 0.2)) / (L[3] - L[2] - 0.1))
        return lerp((13 * math.cos(-0.2), 13 * math.sin(-0.2), 8), (1.0, -5.8, 1.85), k), lerp((0, 0, 0.5), (-0.62, -0.85, 0.5), k), 32 + 8 * k
    if t < L[5] - 0.2:        # cozy: slow push on Klod and the fire
        k = (t - L[3]) / (L[5] - L[3]); return lerp((1.0, -5.8, 1.85), (0.75, -4.7, 1.5), k), (-0.62, -0.85, 0.5), 40
    k = ease((t - L[5]) / 3.5)   # final: rise to show the empty valley waiting for houses
    return lerp((0.75, -4.7, 1.5), (9, -12, 7.5), k), lerp((-0.62, -0.85, 0.5), (0, 0, 0.4), k), 40 - 8 * k


os.makedirs(OUT, exist_ok=True)
for f in FRAMES:
    t = f / FPS
    p, tg, lens = shot(t); C.location = p; c.lens = lens; look(C, Vector(tg)); c.dof.focus_distance = (Vector(p) - Vector(tg)).length
    # fire flicker + smoke puffs
    fk = 0.85 + 0.15 * math.sin(t * 17) * math.sin(t * 7.3 + 1)
    for i, fl in enumerate(flames): fl.scale = (1, 1, fk * (1 + 0.12 * math.sin(t * 11 + i)))
    fl_light.energy = 180 * fk
    for i, pf in enumerate(puffs):
        ph = ((t * 0.32 + i / len(puffs)) % 1.0)
        pf.location = (0.25 * math.sin(i * 2.1 + t) + ph * 0.7, 0.15 * math.cos(i), 1.0 + ph * 5.0); s = (0.5 + ph * 1.4) * min(1, (1 - ph) * 4); pf.scale = (s, s, s)
    # ghosts fade away when the camera reaches the fire ("а пока тут только костёр")
    ga = 0.32 * (1 - ease((t - (L[2] + 0.4)) / 1.2))
    ghostm.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = max(0.0, ga)
    for lb in labels[len(houses):]: lb.scale = (1, 1, 1) if ga > 0.02 else (0, 0, 0)
    for g in ghosts: g.scale = (1, 1, 1) if ga > 0.01 else (0, 0, 0)
    animate_smooth(K, t, face={"expr": "happy", "vis": 0, "b": 1 if (t % 3.7) < 0.12 else 0, "g": "c"}, gesture=0.2 * (0.5 + 0.5 * math.sin(t)))
    sc.render.filepath = f"{OUT}/{f:05d}.png"; bpy.ops.render.render(write_still=True)
