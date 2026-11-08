"""Blender: «Майкл из Техаса» in blocky 3D. Usage: blender -b -P michael3d.py -- plan.json outdir start end
Writes projected boxes (carpet / mom / head) to outdir/boxes_<start>.json for the 2D HUD."""
import bpy, json, math, os, sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "scene3d.py")).read()
exec(_src[:_src.index("# ------------------------------------------------------------- characters")])
sc.eevee.taa_render_samples = 16
sc.eevee.bloom_intensity = 0.08
sc.eevee.gtao_distance = 0.8


def cam(name, lens, fstop):
    c = bpy.data.cameras.new(name); c.lens = lens; c.sensor_fit = "VERTICAL"; c.sensor_height = 24
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, c); bpy.context.collection.objects.link(o); return o


# ---------------------------------------------------------------- room
world((0.02, 0.03, 0.03), 0.6)
wall = mat_col("wall", "#2A3B38", 0.85); wall2 = mat_col("wall2", "#223230", 0.85)
box("backwall", 10, 0.2, 5, (0, 2.0, 2.5), {"other": wall})
box("leftwall", 0.2, 7, 5, (-3.6, 0, 2.5), {"other": wall2})
box("floor", 10, 7, 0.1, (0, 0, -0.05), {"other": mat_tex("floor", "floor_wood", 0.35)})
carpet = box("carpet", 2.2, 0.06, 3.0, (-0.55, 1.88, 1.95), {"front": mat_tex("carpet", "carpet", 0.9), "other": mat_col("cfr", "#C9A04A")})
flag = box("flag", 2.3, 0.04, 1.6, (-0.55, 1.82, 2.4), {"front": mat_tex("flag", "usflag", 0.8), "other": mat_col("flb", "#B22234")})
box("sign66", 0.7, 0.05, 1.05, (1.55, 1.88, 2.6), {"front": mat_tex("s66", "sign66", 0.6), "other": mat_col("s66b", "#1A2422")})
wood = mat_col("wood", "#5A3A26", 0.45); dark = mat_col("dark", "#15171C", 0.4)
box("desk", 1.8, 0.8, 0.07, (2.25, 0.9, 0.8), {"other": wood})
for lx in (1.42, 3.08): box("dleg", 0.07, 0.7, 0.78, (lx, 0.9, 0.39), {"other": wood})
lap = box("laptop", 0.7, 0.05, 0.45, (2.75, 1.12, 1.07), {"front": mat_tex("lapscr", "laptop_red", 0.5, emit=3.0), "other": dark})
box("lapbase", 0.7, 0.45, 0.03, (2.75, 0.92, 0.85), {"other": dark})
box("door", 1.1, 0.06, 2.2, (-2.35, 1.86, 1.1), {"other": mat_col("door", "#5A3E2A", 0.6)})
door_open = box("doorhole", 1.0, 0.04, 2.1, (-2.35, 1.82, 1.05), {"other": mat_col("doorhole", "#FFE2A8", 0.6, emit=2.5)})
lampm = mat_col("lampm", "#FFE7B0", 0.4, emit=10)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0.2, 0.2, 4.2)); bpy.context.object.data.materials.append(lampm)

key = area("key", (-1.2, -3.6, 3.6), (0, 0.4, 1.4), 520, (1.0, 0.86, 0.66), 3.0)
fill = area("fill", (3.5, -2.5, 2.2), (0, 0.4, 1.2), 140, (0.5, 0.75, 0.8), 2.5)
rim = area("rim", (1.0, 2.6, 3.2), (-0.5, 0, 1.4), 300, (1.0, 0.5, 0.35), 2.0)
lapl = point("lapglow", (2.6, 0.7, 1.15), 60, (1.0, 0.25, 0.2))
redl = area("alarm", (0.0, -3.0, 3.0), (0, 0.5, 1.4), 0, (1.0, 0.08, 0.05), 4.0)
doorl = point("doorlight", (-2.35, 1.75, 2.4), 0, (1.0, 0.85, 0.6))

# ---------------------------------------------------------------- Руслан (with shoulder pivots)
r_root = empty("ruslan", (-0.35, 0.2, 0), 8)
r_face = mat_tex("rface", "ruslan_face_neutral_0_0", 0.55)
r_side = mat_tex("rside", "ruslan_side"); r_cap = mat_tex("rcap", "ruslan_cap", 0.4)
p_front = mat_tex("pfront", "puffer_front", 0.22); p_side = mat_tex("pside", "puffer_side", 0.22)
r_legs = mat_tex("rlegs", "ruslan_legs"); r_arm = mat_tex("rarm", "ruslan_arm", 0.22); hatm = mat_tex("hat", "hat", 0.6)
for sx in (-0.125, 0.125): box("leg", 0.25, 0.25, 0.75, (sx, 0, 0.375), {"other": r_legs}, r_root)
box("body", 0.56, 0.32, 0.78, (0, 0, 1.13), {"front": p_front, "other": p_side}, r_root)
box("hood", 0.5, 0.18, 0.16, (0, 0.12, 1.55), {"other": p_side}, r_root)
arms = []
for sx in (-0.41, 0.41):
    piv = empty("shoulder", (sx, 0, 1.48), 0, r_root)
    box("arm", 0.26, 0.28, 0.76, (0, 0, -0.36), {"bottom": mat_col("hand", "#E8BFA2"), "other": r_arm}, piv)
    arms.append(piv)
box("head", 0.5, 0.5, 0.5, (0, 0, 1.78), {"front": r_face, "top": r_cap, "other": r_side}, r_root)
cap = [box("cap", 0.53, 0.53, 0.1, (0, 0, 2.05), {"other": r_cap}, r_root), box("brim", 0.5, 0.24, 0.035, (0, -0.35, 1.985), {"other": r_cap}, r_root)]
hat = [box("hatcrown", 0.5, 0.5, 0.26, (0, 0, 2.15), {"front": hatm, "other": hatm}, r_root),
       box("hatbrim", 0.95, 0.95, 0.04, (0, 0, 2.03), {"other": mat_col("hatb", "#6B4423", 0.6)}, r_root)]

# ---------------------------------------------------------------- mom (in the doorway)
m_root = empty("mom", (-2.3, 1.35, 0), 12)
m_face = mat_tex("mface", "mom_face_1_0_0", 0.55); m_hair = mat_tex("mhair", "mom_hair", 0.7)
blouse = mat_tex("blouse", "mom_blouse", 0.6); skirt = mat_tex("skirt", "mom_skirt", 0.7)
for sx in (-0.125, 0.125): box("mleg", 0.24, 0.24, 0.7, (sx, 0, 0.35), {"other": mat_col("mlegc", "#E8CBB0")}, m_root)
box("mskirt", 0.56, 0.3, 0.32, (0, 0, 0.78), {"other": skirt}, m_root)
box("mbody", 0.52, 0.28, 0.6, (0, 0, 1.24), {"front": blouse, "other": blouse}, m_root)
box("mhead", 0.5, 0.5, 0.5, (0, 0, 1.79), {"front": m_face, "other": m_hair}, m_root)
for (w, d, h, x, y, z) in ((0.62, 0.62, 0.22, 0, 0.02, 2.1), (0.12, 0.5, 0.42, -0.3, 0.02, 1.86), (0.12, 0.5, 0.42, 0.3, 0.02, 1.86)):
    box("curls", w, d, h, (x, y, z), {"other": m_hair}, m_root)
m_arm = empty("mshoulder", (0.38, 0, 1.5), 0, m_root)
box("marm", 0.22, 0.24, 0.6, (0, 0, -0.28), {"other": blouse}, m_arm)
box("ladle", 0.05, 0.05, 0.7, (0, -0.05, -0.75), {"other": mat_col("steel", "#B8BCC4", 0.25, metal=0.8)}, m_arm)
box("ladlecup", 0.2, 0.2, 0.12, (0, -0.05, -1.12), {"other": mat_col("steel2", "#B8BCC4", 0.25, metal=0.8)}, m_arm)
for sx in (-0.38,): box("marm2", 0.22, 0.24, 0.6, (sx, 0, 1.2), {"other": blouse}, m_root)

# ---------------------------------------------------------------- Клод on the desk
k_root = empty("klod", (2.0, 0.85, 0.84), -18)
kface = mat_tex("kface", "klod_face_neutral_0_0", 0.6)
kside = mat_tex("kside", "klod_side"); ktop = mat_tex("ktop", "klod_top"); kdark = mat_tex("kdark", "klod_dark")
ksnout = mat_tex("ksnout", "klod_snout", 0.5); tusk = mat_col("tusk", "#FFF6E6", 0.3)
KS = 0.55
for lx in (-0.36, 0.36):
    for ly in (-0.22, 0.22): box("kleg", 0.17 * KS, 0.17 * KS, 0.3 * KS, (lx * KS, ly * KS, 0.15 * KS), {"other": kdark}, k_root)
box("kbody", 1.0 * KS, 0.75 * KS, 0.75 * KS, (0, 0, 0.675 * KS), {"front": kface, "top": ktop, "other": kside}, k_root)
box("snout", 0.38 * KS, 0.15 * KS, 0.19 * KS, (0, -0.445 * KS, 0.56 * KS), {"other": ksnout}, k_root)
for tx in (-0.25, 0.25): box("tusk", 0.05 * KS, 0.05 * KS, 0.14 * KS, (tx * KS, -0.4 * KS, 0.55 * KS), {"other": tusk}, k_root)
for ex in (-0.39, 0.39): box("ear", 0.17 * KS, 0.1 * KS, 0.17 * KS, (ex * KS, -0.22 * KS, 1.13 * KS), {"other": kdark}, k_root)

CAMS = {
    "medium": (cam("c_med", 30, 3.2), Vector((0.1, -4.2, 1.75)), Vector((-0.25, 0.4, 1.45))),
    "r_close": (cam("c_r", 40, 1.6), Vector((-0.05, -1.95, 1.72)), Vector((-0.35, 0.2, 1.68))),
    "k_close": (cam("c_k", 40, 2.0), Vector((1.75, -0.65, 1.35)), Vector((2.0, 0.85, 1.12))),
    "m_close": (cam("c_m", 40, 1.8), Vector((-2.0, -0.85, 1.75)), Vector((-2.3, 1.35, 1.7))),
    "mom_wide": (cam("c_mw", 22, 3.5), Vector((-0.7, -4.4, 1.85)), Vector((-1.15, 0.7, 1.3))),
    "plate": (cam("c_p", 26, 0.9), Vector((0.2, -4.8, 1.8)), Vector((0, 0.5, 1.4))),
}


def proj(o, pts):
    vs = [world_to_camera_view(sc, o, Vector(p)) for p in pts]
    xs = [v.x for v in vs]; ys = [1 - v.y for v in vs]
    return [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)]


out_boxes = {}
for fr in range(START, min(END, len(PLAN["frames"]))):
    F = PLAN["frames"][fr]; shot = F["shot"]
    if shot == "ui":
        print("SKIP", fr, flush=True); continue
    r, k, m = F["r"], F["k"], F["m"]
    set_tex(r_face, f'ruslan_face_{r["expr"]}_{r["m"]}_{r["b"]}')
    set_tex(kface, f'klod_face_{k["expr"]}_{k["m"]}_{k["b"]}')
    set_tex(m_face, f'mom_face_1_{m["m"]}_{m["b"]}')
    for o in cap: o.hide_render = r["hat"]
    for o in hat: o.hide_render = not r["hat"]
    a = r["arms"]
    arms[0].rotation_euler = (0, math.radians(-150 * a), 0); arms[1].rotation_euler = (0, math.radians(150 * a), 0)
    r_root.rotation_euler.z = math.radians(8 + r.get("turn", 0))
    r_root.location.z = r.get("hop", 0)
    flag.hide_render = F["flag"] <= 0.01
    flag.scale = (1, 1, max(0.01, F["flag"])); flag.location.z = 2.4 + (1 - F["flag"]) * 0.8
    vis_m = m["vis"]
    for ob in [m_root] + list(m_root.children_recursive): ob.hide_render = not vis_m
    m_arm.rotation_euler = (math.radians(-60 - 25 * math.sin(F["t"] * 9)), 0, 0)
    door_open.hide_render = not vis_m; doorl.data.energy = 45 if vis_m else 0
    redl.data.energy = 900 if F["red"] else 0
    key.data.energy = 220 if F["red"] else 520
    o, pos, tgt = CAMS[shot]
    d = tgt - pos; p = pos + d * (0.08 * F["push"]) + Vector((F["sway"][0], 0, F["sway"][1]))
    o.location = p; look(o, tgt + Vector((F.get("turn_cam", 0), 0, 0))); o.data.dof.focus_distance = (tgt - p).length; sc.camera = o
    bpy.context.view_layer.update()
    cx, cy = carpet.location.x, carpet.location.z
    out_boxes[fr] = {"carpet": proj(o, [(cx - 1.1, 1.85, cy - 1.5), (cx + 1.1, 1.85, cy + 1.5)]),
                     "mom": proj(o, [(-2.62, 1.35, 0.0), (-1.98, 1.35, 2.25)]),
                     "head": proj(o, [(r_root.location.x - 0.3, 0.0, 1.5), (r_root.location.x + 0.3, 0.0, 2.1)])}
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
json.dump(out_boxes, open(os.path.join(OUTDIR, f"boxes_{START}.json"), "w"))
