"""Blender: sets for the trend shorts («Муся, это ты?» / «Возьми телефон, детка»).
Bedroom at 3 a.m. + night swamp. Usage: blender -b -P trend3d.py -- plan.json outdir start end"""
import bpy, json, math, os, random, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "scene3d.py")).read()
exec(_src[:_src.index("# ------------------------------------------------------------- characters")])
sc.eevee.taa_render_samples = 16
sc.eevee.bloom_intensity = 0.09
sc.eevee.gtao_distance = 0.8


def cam(name, lens, fstop):
    c = bpy.data.cameras.new(name); c.lens = lens; c.sensor_fit = "VERTICAL"; c.sensor_height = 24
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, c); bpy.context.collection.objects.link(o); return o


world((0.012, 0.016, 0.035), 0.7)
# ================================================================ bedroom (around origin)
wall = mat_col("wall", "#25304A", 0.85); wall2 = mat_col("wall2", "#1F2840", 0.85)
box("backwall", 9, 0.2, 5, (0, 2.3, 2.5), {"other": wall})
box("leftwall", 0.2, 7, 5, (-3.6, 0, 2.5), {"other": wall2})
box("floor", 9, 7, 0.1, (0, 0, -0.05), {"other": mat_tex("floor", "floor_dark", 0.4)})
box("window", 1.6, 0.05, 1.5, (-0.4, 2.18, 2.4), {"front": mat_tex("night", "night", 0.9, emit=1.3), "other": wall})
frm = mat_col("frm", "#C9C2B0", 0.5)
for (w, h, x, z) in ((1.8, 0.08, -0.4, 3.19), (1.8, 0.08, -0.4, 1.61), (0.08, 1.6, -1.27, 2.4), (0.08, 1.6, 0.47, 2.4), (0.05, 1.5, -0.4, 2.4)):
    box("wf", w, 0.1, h, (x, 2.12, z), {"other": frm})
moonm = mat_col("moon", "#FFF4D0", 0.4, emit=6)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(-0.85, 2.14, 2.85)); bpy.context.object.data.materials.append(moonm)
wood = mat_col("wood", "#5A3A26", 0.5); dark = mat_col("dark", "#15171C", 0.4)
box("desk", 1.9, 0.8, 0.07, (2.2, 1.55, 0.78), {"other": wood})
for lx in (1.35, 3.05): box("dleg", 0.07, 0.7, 0.76, (lx, 1.55, 0.38), {"other": wood})
box("monitor", 0.95, 0.06, 0.58, (2.45, 1.82, 1.25), {"front": mat_tex("scr", "code", 0.9, emit=1.4), "other": dark})
box("bed", 1.3, 2.2, 0.38, (-2.7, 1.0, 0.19), {"other": wood})
box("mattress", 1.25, 2.1, 0.18, (-2.7, 1.0, 0.47), {"other": mat_col("sheet", "#E8E6E0", 0.8)})
blanket = box("blanket", 1.3, 1.5, 0.12, (-2.7, 0.35, 0.92), {"other": mat_col("blanket", "#3B5BA8", 0.8)})
box("pillow", 0.9, 0.4, 0.14, (-2.7, 1.85, 0.63), {"other": mat_col("pillow", "#F4F2EC", 0.8)})
box("nightstand", 0.5, 0.45, 0.55, (-1.75, 1.75, 0.27), {"other": wood})
phone_m = mat_tex("phonescr", "phone_call", 0.3, emit=0.0)
ns_phone = box("nsphone", 0.16, 0.3, 0.025, (-1.75, 1.7, 0.57), {"top": phone_m, "other": dark})
ns_glow = point("nsglow", (-1.75, 1.6, 0.8), 0, (0.4, 1.0, 0.6))
area("key", (1.5, -3.0, 4.2), (0, 0.5, 0.5), 300, (0.75, 0.82, 1.0), 3.0)
area("rim", (-1.0, 1.8, 3.5), (0, 0, 0.5), 180, (0.55, 0.65, 1.0), 2.5)
point("monglow", (2.4, 1.3, 1.2), 80, (0.6, 0.7, 1.0))
point("moonl", (-0.4, 1.7, 2.6), 60, (0.7, 0.8, 1.0))

# ================================================================ swamp (x ~ 30)
SX = 30.0
box("water", 14, 14, 0.1, (SX, 2, -0.05), {"other": mat_tex("water", "swamp_water", 0.05)})
for (x, y, w, d) in ((SX - 3, 3, 3, 2), (SX + 3.5, 4, 3, 3), (SX - 1, 7, 6, 2)):
    box("mud", w, d, 0.2, (x, y, 0.05), {"other": mat_tex("mud", "swamp_mud", 0.8)})
rr = random.Random(5); reed = mat_tex("reed", "reed", 0.7); lily = mat_tex("lily", "lily", 0.6)
for k in range(40):
    x = SX + rr.uniform(-5, 5); y = rr.uniform(1.5, 8)
    if abs(x - SX) < 1.0 and y < 3: continue
    h = rr.uniform(0.6, 1.6); box("reed", 0.06, 0.06, h, (x, y, h / 2), {"other": reed})
for k in range(14):
    box("lily", 0.35, 0.35, 0.02, (SX + rr.uniform(-3, 3), rr.uniform(-0.5, 4), 0.01), {"other": lily})
fogm = bpy.data.materials.new("fog"); fogm.use_nodes = True; fogm.blend_method = "BLEND"
fb = fogm.node_tree.nodes["Principled BSDF"]; fb.inputs["Base Color"].default_value = (0.6, 0.7, 0.8, 1); fb.inputs["Alpha"].default_value = 0.12
for k in range(5): box("fog", 14, 0.02, 1.2, (SX, 2.5 + k * 1.2, 0.5), {"other": fogm})
smoon = mat_col("smoon", "#EAF0FF", 0.4, emit=8)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(SX - 2.5, 14, 6)); bpy.context.object.data.materials.append(smoon)
area("skey", (SX - 2, -2.5, 4), (SX, 1, 0.5), 260, (0.55, 0.7, 1.0), 4.0)
area("srim", (SX + 1, 5, 3), (SX, 1, 0.5), 300, (0.4, 1.0, 0.6), 3.0)

# ================================================================ Руслан
r_root = empty("ruslan", (-2.1, 0.55, 0), 20)
r_face = mat_tex("rface", "ruslan_face_neutral_0_0", 0.55)
r_side = mat_tex("rside", "ruslan_side"); r_cap = mat_tex("rcap", "ruslan_cap", 0.4)
p_front = mat_tex("pfront", "puffer_front", 0.22); p_side = mat_tex("pside", "puffer_side", 0.22)
r_legs = mat_tex("rlegs", "ruslan_legs"); r_arm = mat_tex("rarm", "ruslan_arm", 0.22)
for sx in (-0.125, 0.125): box("leg", 0.25, 0.25, 0.75, (sx, 0, 0.375), {"other": r_legs}, r_root)
box("body", 0.56, 0.32, 0.78, (0, 0, 1.13), {"front": p_front, "other": p_side}, r_root)
box("hood", 0.5, 0.18, 0.16, (0, 0.12, 1.55), {"other": p_side}, r_root)
arms = []
for sx in (-0.41, 0.41):
    piv = empty("shoulder", (sx, 0, 1.48), 0, r_root)
    box("arm", 0.26, 0.28, 0.76, (0, 0, -0.36), {"bottom": mat_col("hand", "#E8BFA2"), "other": r_arm}, piv)
    arms.append(piv)
r_phone = box("rphone", 0.05, 0.16, 0.3, (-0.285, -0.02, 1.76), {"left": mat_tex("rps", "phone_call", 0.3, emit=2.0), "other": dark}, r_root)
box("head", 0.5, 0.5, 0.5, (0, 0, 1.78), {"front": r_face, "top": r_cap, "other": r_side}, r_root)
box("cap", 0.53, 0.53, 0.1, (0, 0, 2.05), {"other": r_cap}, r_root)
box("brim", 0.5, 0.24, 0.035, (0, -0.35, 1.985), {"other": r_cap}, r_root)


# ================================================================ Клод ×2 (desk / swamp tiger)
def make_klod(name, loc, rot, ks, tiger=False):
    root = empty(name, loc, rot)
    pre = "klod_tiger" if tiger else "klod"
    face = mat_tex(name + "face", f"{pre}_face_neutral_0_0", 0.6)
    side = mat_tex(name + "side", "klod_tiger_side" if tiger else "klod_side"); top = mat_tex(name + "top", "klod_tiger_top" if tiger else "klod_top")
    kd = mat_tex(name + "dark", "klod_dark"); sn = mat_tex(name + "snout", "klod_snout", 0.5); tu = mat_col(name + "tusk", "#FFF6E6", 0.3)
    front_legs = []
    for lx in (-0.36, 0.36):
        piv = empty(name + "fl", (lx * ks, -0.22 * ks, 0.3 * ks), 0, root)
        box("kleg", 0.17 * ks, 0.17 * ks, 0.3 * ks, (0, 0, -0.15 * ks), {"other": kd}, piv); front_legs.append(piv)
        box("kleg", 0.17 * ks, 0.17 * ks, 0.3 * ks, (lx * ks, 0.22 * ks, 0.15 * ks), {"other": kd}, root)
    box("kbody", 1.0 * ks, 0.75 * ks, 0.75 * ks, (0, 0, 0.675 * ks), {"front": face, "top": top, "other": side}, root)
    box("snout", 0.38 * ks, 0.15 * ks, 0.19 * ks, (0, -0.445 * ks, 0.56 * ks), {"other": sn}, root)
    for tx in (-0.25, 0.25): box("tusk", 0.05 * ks, 0.05 * ks, 0.14 * ks, (tx * ks, -0.4 * ks, 0.55 * ks), {"other": tu}, root)
    for ex in (-0.39, 0.39): box("ear", 0.17 * ks, 0.1 * ks, 0.17 * ks, (ex * ks, -0.22 * ks, 1.13 * ks), {"other": kd}, root)
    for k in range(6): box("mane", 0.05 * ks * 2, 0.05 * ks * 2, 0.06 * ks * 2, ((-0.15 + k * 0.06) * ks * 2, 0, 1.05 * ks + 0.03 * ks * 2), {"other": kd}, root)
    phone = box(name + "phone", 0.2 * ks, 0.05 * ks, 0.36 * ks, (-0.62 * ks, -0.3 * ks, 0.9 * ks), {"front": mat_tex(name + "ps", "phone_call", 0.3, emit=2.5), "other": dark}, root)
    phone.rotation_euler = (0, math.radians(12), 0)
    return root, face, front_legs, phone, pre


K_DESK = make_klod("kdesk", (1.75, 1.45, 0.82), -12, 0.55)
K_SWAMP = make_klod("kswamp", (SX, 0.6, -0.12), 0, 1.0, tiger=True)
K_CORNER = make_klod("kcorner", (0.95, 1.85, 0.0), 180, 0.8)
shades = [box("shade", 0.26, 0.04, 0.14, (sx * 0.8, -0.32 * 0.8 * 0 - 0.31, 0.62), {"other": mat_col("shadem", "#0A0A0C", 0.15, metal=0.6)}, K_CORNER[0]) for sx in (-0.17, 0.17)]
shades.append(box("shadebar", 0.6, 0.04, 0.05, (0, -0.31, 0.68), {"other": mat_col("shadem2", "#0A0A0C", 0.15)}, K_CORNER[0]))
R_OBI = Vector((-0.35, 0.25, 0))

CAMS = {
    "r_close": (cam("c_r", 38, 1.8), Vector((-1.75, -1.55, 1.75)), Vector((-2.1, 0.55, 1.72))),
    "bed": (cam("c_bed", 24, 3.2), Vector((-1.5, -1.7, 3.4)), Vector((-2.25, 1.25, 0.6))),
    "bed_close": (cam("c_bc", 38, 1.8), Vector((-2.7, 0.75, 2.6)), Vector((-2.7, 1.62, 0.78))),
    "k_desk": (cam("c_k", 32, 2.2), Vector((1.3, -1.05, 1.35)), Vector((1.7, 1.45, 1.08))),
    "swamp": (cam("c_s", 34, 2.2), Vector((SX - 0.4, -2.6, 1.15)), Vector((SX, 0.6, 0.55))),
    "swamp_wide": (cam("c_sw", 22, 4.5), Vector((SX + 0.5, -5.5, 2.3)), Vector((SX, 2.0, 0.4))),
    "plate": (cam("c_p", 26, 0.9), Vector((0.5, -4.6, 3.5)), Vector((0.2, 0.35, 0.3))),
    "corner_wide": (cam("c_cw", 24, 3.5), Vector((-0.9, -2.8, 2.1)), Vector((0.45, 1.4, 0.7))),
    "kc_close": (cam("c_kc", 34, 2.0), Vector((0.7, -0.45, 1.05)), Vector((0.95, 1.85, 0.55))),
    "r_obi": (cam("c_ro", 32, 1.8), Vector((0.95, 2.0, 1.85)), Vector((-0.35, 0.25, 1.62))),
}

for fr in range(START, min(END, len(PLAN["frames"]))):
    F = PLAN["frames"][fr]; shot = F["shot"]
    if shot == "ui":
        print("SKIP", fr, flush=True); continue
    t = F["t"]; r = F["r"]
    set_tex(r_face, f'ruslan_face_{r["expr"]}_{r["m"]}_{r["b"]}')
    pose = r["pose"]
    if "pos" in r:
        r_root.location = (r["pos"][0], r["pos"][1], 0); r_root.rotation_euler = (0, 0, math.radians(r.get("rotz", 0))); blanket.location.z = 0.6
    elif pose.startswith("lie"):
        r_root.location = (-2.7, -0.1, 0.72); r_root.rotation_euler = (math.radians(-90), 0, 0); blanket.location.z = 0.92
    else:
        r_root.location = (-2.1, 0.55, 0); r_root.rotation_euler = (0, 0, math.radians(20)); blanket.location.z = 0.6
    if pose in ("stand_phone", "lie_phone"):
        arms[0].rotation_euler = (math.radians(-135), 0, math.radians(-18)); r_phone.hide_render = False
    else:
        arms[0].rotation_euler = (0, 0, 0); r_phone.hide_render = True
    buzz = F.get("buzz", 0)
    ns_phone.location.x = -1.75 + (0.012 * math.sin(t * 90) if buzz else 0)
    set_tex(phone_m, "phone_call"); phone_m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 3.0 if buzz else 0.2
    ns_phone.hide_render = pose == "lie_phone" or pose == "stand_phone"
    ns_glow.data.energy = 40 if buzz else 0
    kc = F.get("kc")
    for ob in [K_CORNER[0]] + list(K_CORNER[0].children_recursive): ob.hide_render = kc is None
    for ob in shades: ob.hide_render = not (kc and kc.get("shades"))
    if kc:
        K_CORNER[0].rotation_euler = (0, 0, math.radians(kc["rot"]))
        set_tex(K_CORNER[1], f'klod_face_{kc["expr"]}_{kc["m"]}_{kc["b"]}'); K_CORNER[3].hide_render = True
    for ob in [K_DESK[0]] + list(K_DESK[0].children_recursive): ob.hide_render = bool(kc)
    for (root, face, legs, phone, pre), st in ((K_DESK, F["k"]), (K_SWAMP, F["kt"])):
        set_tex(face, f'{pre}_face_{st["expr"]}_{st["m"]}_{st["b"]}')
        pa = st.get("piano", 0)
        legs[0].rotation_euler = (math.radians(-55 * st.get("raise", 0) - 25 * pa * max(0, math.sin(t * 16))), 0, 0)
        legs[1].rotation_euler = (math.radians(-25 * pa * max(0, math.sin(t * 16 + 1.6))), 0, 0)
        phone.hide_render = st.get("phone", 0) < 0.5
        root.location.z = root.location.z * 0 + st.get("z0", 0) + 0.04 * st.get("bob", 0) * abs(math.sin(t * 8))
    o, pos, tgt = CAMS[shot]
    d = tgt - pos; p = pos + d * (0.08 * F["push"]) + Vector((F["sway"][0], 0, F["sway"][1]))
    o.location = p; look(o, tgt); o.data.dof.focus_distance = (tgt - p).length; sc.camera = o
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
