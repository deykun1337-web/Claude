"""Blender: «Агенты» bedroom scene. Usage: blender -b -P agents3d.py -- plan.json outdir start end
Reuses the helpers from scene3d.py and writes label screen positions to outdir/labels_<start>.json."""
import bpy, json, math, os, sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "scene3d.py")).read()
exec(_src[:_src.index("# ------------------------------------------------------------- characters")])
sc.eevee.taa_render_samples = 12


def cam(name, lens, fstop):
    c = bpy.data.cameras.new(name); c.lens = lens; c.sensor_fit = "VERTICAL"; c.sensor_height = 24
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, c); bpy.context.collection.objects.link(o); return o

# ---------------------------------------------------------------- room
world((0.02, 0.025, 0.05), 0.7)
wall = mat_col("wall", "#2A3550", 0.85); wall2 = mat_col("wall2", "#232C44", 0.85)
box("backwall", 9, 0.2, 5, (0, 2.3, 2.5), {"other": wall})
box("leftwall", 0.2, 7, 5, (-3.6, 0, 2.5), {"other": wall2})
box("floor", 9, 7, 0.1, (0, 0, -0.05), {"other": mat_tex("floor", "floor_dark", 0.4)})
box("window", 1.6, 0.05, 1.5, (-0.4, 2.18, 2.4), {"front": mat_tex("night", "night", 0.9, emit=1.4), "other": wall})
frm = mat_col("frm", "#C9C2B0", 0.5)
for (w, h, x, z) in ((1.8, 0.08, -0.4, 3.19), (1.8, 0.08, -0.4, 1.61), (0.08, 1.6, -1.27, 2.4), (0.08, 1.6, 0.47, 2.4), (0.05, 1.5, -0.4, 2.4)):
    box("wf", w, 0.1, h, (x, 2.12, z), {"other": frm})
moon = mat_col("moon", "#FFF4D0", 0.4, emit=6)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(-0.85, 2.14, 2.85)); bpy.context.object.data.materials.append(moon)
# desk + monitor
wood = mat_col("wood", "#5A3A26", 0.5); dark = mat_col("dark", "#15171C", 0.4)
box("desk", 1.9, 0.8, 0.07, (2.2, 1.55, 0.78), {"other": wood})
for lx in (1.35, 3.05): box("dleg", 0.07, 0.7, 0.76, (lx, 1.55, 0.38), {"other": wood})
box("monitor", 0.95, 0.06, 0.58, (2.45, 1.82, 1.25), {"front": mat_tex("scr", "code", 0.9, emit=1.6), "other": dark})
box("stand", 0.08, 0.08, 0.25, (2.45, 1.85, 0.93), {"other": dark})
# bed
box("bed", 1.3, 2.2, 0.38, (-2.7, 1.0, 0.19), {"other": wood})
box("mattress", 1.25, 2.1, 0.18, (-2.7, 1.0, 0.47), {"other": mat_col("sheet", "#E8E6E0", 0.8)})
blanket = box("blanket", 1.3, 1.5, 0.12, (-2.7, 0.35, 0.6), {"other": mat_col("blanket", "#3B5BA8", 0.8)})
box("pillow", 0.9, 0.4, 0.14, (-2.7, 1.85, 0.63), {"other": mat_col("pillow", "#F4F2EC", 0.8)})
# door with exit sign
box("door", 0.06, 1.0, 2.1, (-3.48, -0.4, 1.05), {"other": mat_col("door", "#6B4A30", 0.6)})
box("exit", 0.04, 0.42, 0.16, (-3.45, -0.4, 2.35), {"other": mat_col("exitg", "#2EE87A", 0.4, emit=8)})
area("key", (1.5, -3.0, 4.2), (0, 0.5, 0.5), 520, (1.0, 0.92, 0.85), 3.0)
area("rim", (-1.0, 1.8, 3.5), (0, 0, 0.5), 260, (0.55, 0.65, 1.0), 2.5)
point("monglow", (2.4, 1.3, 1.2), 70, (0.6, 0.7, 1.0))
point("lamp", (-0.4, 1.6, 2.5), 60, (1.0, 0.85, 0.6))

# ---------------------------------------------------------------- Руслан
r_root = empty("ruslan", (-2.1, 0.55, 0), 20)
r_face = mat_tex("rface", "ruslan_face_neutral_0_0", 0.55)
r_side = mat_tex("rside", "ruslan_side"); r_cap = mat_tex("rcap", "ruslan_cap", 0.4)
p_front = mat_tex("pfront", "puffer_front", 0.25); p_side = mat_tex("pside", "puffer_side", 0.25)
r_legs = mat_tex("rlegs", "ruslan_legs"); r_arm = mat_tex("rarm", "ruslan_arm", 0.25)
for sx in (-0.125, 0.125): box("leg", 0.25, 0.25, 0.75, (sx, 0, 0.375), {"other": r_legs}, r_root)
box("body", 0.56, 0.32, 0.78, (0, 0, 1.13), {"front": p_front, "other": p_side}, r_root)
box("hood", 0.5, 0.18, 0.16, (0, 0.12, 1.55), {"other": p_side}, r_root)
for sx in (-0.4, 0.4): box("arm", 0.26, 0.28, 0.76, (sx, 0, 1.12), {"bottom": mat_col("hand", "#E8BFA2"), "other": r_arm}, r_root)
box("head", 0.5, 0.5, 0.5, (0, 0, 1.78), {"front": r_face, "top": r_cap, "other": r_side}, r_root)
box("cap", 0.53, 0.53, 0.1, (0, 0, 2.05), {"other": r_cap}, r_root)
box("brim", 0.5, 0.24, 0.035, (0, -0.35, 1.985), {"other": r_cap}, r_root)

# ---------------------------------------------------------------- Клод (main agent, on the desk)
k_root = empty("klod", (1.75, 1.45, 0.82), -12)
kface = mat_tex("kface", "klod_face_neutral_0_0", 0.6)
kside = mat_tex("kside", "klod_side"); ktop = mat_tex("ktop", "klod_top"); kdark = mat_tex("kdark", "klod_dark")
ksnout = mat_tex("ksnout", "klod_snout", 0.5); tusk = mat_col("tusk", "#FFF6E6", 0.3)
KS = 0.5
for lx in (-0.36, 0.36):
    for ly in (-0.22, 0.22): box("kleg", 0.17 * KS, 0.17 * KS, 0.3 * KS, (lx * KS, ly * KS, 0.15 * KS), {"other": kdark}, k_root)
box("kbody", 1.0 * KS, 0.75 * KS, 0.75 * KS, (0, 0, 0.675 * KS), {"front": kface, "top": ktop, "other": kside}, k_root)
box("snout", 0.38 * KS, 0.15 * KS, 0.19 * KS, (0, -0.445 * KS, 0.56 * KS), {"other": ksnout}, k_root)
for tx in (-0.25, 0.25): box("tusk", 0.05 * KS, 0.05 * KS, 0.14 * KS, (tx * KS, -0.4 * KS, 0.55 * KS), {"other": tusk}, k_root)
for ex in (-0.39, 0.39): box("ear", 0.17 * KS, 0.1 * KS, 0.17 * KS, (ex * KS, -0.22 * KS, 1.13 * KS), {"other": kdark}, k_root)
kcap = [box("kcap", 0.62 * KS, 0.6 * KS, 0.14 * KS, (0, 0, 1.12 * KS), {"other": r_cap}, k_root),
        box("kbrim", 0.6 * KS, 0.3 * KS, 0.04 * KS, (0, -0.42 * KS, 1.06 * KS), {"other": r_cap}, k_root)]

# ---------------------------------------------------------------- agents (created lazily)
AG = {}


def agent(aid, col):
    if aid in AG: return AG[aid]
    root = empty("ag_" + aid)
    face = mat_tex("af_" + aid, f"agent_{col}", 0.55); side = mat_tex("as_" + aid, f"agent_{col}_side", 0.55)
    for lx in (-0.14, 0.14):
        for ly in (-0.1, 0.1): box("al", 0.08, 0.08, 0.12, (lx, ly, 0.06), {"other": side}, root)
    box("ab", 0.44, 0.36, 0.33, (0, 0, 0.285), {"front": face, "other": side}, root)
    AG[aid] = (root, face, col)
    return AG[aid]


# ---------------------------------------------------------------- cameras
CAMS = {
    "room": (cam("c_room", 17, 6.0), Vector((0.1, -5.0, 4.3)), Vector((0.05, 0.4, 0.2))),
    "r_close": (cam("c_r", 38, 1.8), Vector((-1.75, -1.55, 1.75)), Vector((-2.1, 0.55, 1.72))),
    "k_close": (cam("c_k", 38, 2.0), Vector((1.45, -0.55, 1.3)), Vector((1.75, 1.45, 1.08))),
    "bed": (cam("c_bed", 30, 2.8), Vector((-2.55, -0.9, 3.3)), Vector((-2.7, 1.05, 0.8))),
    "email": (cam("c_e", 30, 4.0), Vector((2.45, 0.4, 1.3)), Vector((2.45, 1.8, 1.25))),
    "ui_installed": (cam("c_u", 30, 4.0), Vector((2.45, 0.4, 1.3)), Vector((2.45, 1.8, 1.25))),
}

labels_out = {}
for fr in range(START, min(END, len(PLAN["frames"]))):
    F = PLAN["frames"][fr]; shot = F["shot"]
    r = F["r"]; k = F["k"]
    ex = "sleep" if r["pose"] == "lie" else "neutral"
    set_tex(r_face, f'ruslan_face_{ex}_{r["m"]}_{r["b"]}')
    set_tex(kface, f'klod_face_{"smug" if k["cap"] else "neutral"}_{k["m"]}_{k["b"]}')
    for o in kcap: o.hide_render = not k["cap"]
    if r["pose"] == "lie":
        r_root.location = (-2.7, -0.1, 0.72); r_root.rotation_euler = (math.radians(-90), 0, 0); blanket.location.z = 0.92
    else:
        r_root.location = (-2.1, 0.55, 0); r_root.rotation_euler = (0, 0, math.radians(20)); blanket.location.z = 0.6
    seen = set()
    for a in F["agents"]:
        root, face, col = agent(a["id"], a["col"])
        seen.add(a["id"])
        root.hide_render = False
        for ch in root.children: ch.hide_render = False
        root.location = (a["x"], a["y"], a["z"]); root.scale = (a["s"] * 1.35,) * 3
        root.rotation_euler = (math.radians(a["rot"] * 0.0), math.radians(a["rot"] if a["sleep"] else 0), math.radians(0 if not a["sleep"] else 8))
        if a["id"].startswith("wthr") and a["rot"] and not a["sleep"]:
            root.rotation_euler = (0, 0, math.radians(a["rot"] - 90))
        set_tex(face, f'agent_{col}_sleep' if a["sleep"] else f'agent_{col}')
    for aid, (root, face, col) in AG.items():
        if aid not in seen:
            root.hide_render = True
            for ch in root.children: ch.hide_render = True
    o, pos, tgt = CAMS[shot if shot in CAMS else "room"]
    d = tgt - pos; p = pos + d * (0.08 * F["push"]) + Vector((F["sway"][0], 0, F["sway"][1]))
    o.location = p; look(o, tgt); o.data.dof.focus_distance = (tgt - p).length; sc.camera = o
    bpy.context.view_layer.update()
    labs = []
    if shot == "room":
        for a in F["agents"]:
            root = AG[a["id"]][0]
            v = world_to_camera_view(sc, o, root.matrix_world @ Vector((0, 0, 0.55)))
            labs.append({"id": a["id"], "lab": a["lab"], "x": round(v.x, 4), "y": round(1 - v.y, 4), "sleep": a["sleep"], "s": a["s"]})
        v = world_to_camera_view(sc, o, k_root.matrix_world @ Vector((0, 0, 0.7)))
        labs.append({"id": "klod", "lab": "главный агент", "x": round(v.x, 4), "y": round(1 - v.y, 4), "sleep": False, "s": 1})
    labels_out[fr] = labs
    if shot in ("email", "ui_installed"):  # 2D-only shots: skip 3D render
        print("SKIP", fr, flush=True); continue
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
json.dump(labels_out, open(os.path.join(OUTDIR, f"labels_{START}.json"), "w"))
