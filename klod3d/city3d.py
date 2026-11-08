"""Blender: «Я в Москве» chase — blocky Moscow / Piter / Кабаново / home sets with selfie shots.
Usage: blender -b -P city3d.py -- plan.json outdir start end"""
import bpy, json, math, os, random, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "scene3d.py")).read()
exec(_src[:_src.index("# ------------------------------------------------------------- characters")])
sc.eevee.taa_render_samples = 16
sc.eevee.bloom_intensity = 0.1


def cam(name, lens, fstop):
    c = bpy.data.cameras.new(name); c.lens = lens; c.sensor_fit = "VERTICAL"; c.sensor_height = 24
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, c); bpy.context.collection.objects.link(o); return o


world((0.03, 0.04, 0.09), 0.9)
rr = random.Random(2)
red = mat_col("kred", "#9A2A22", 0.8); red2 = mat_col("kred2", "#7A1E18", 0.8)
stone = mat_col("stone", "#55524E", 0.7); gold = mat_col("gold", "#E8B740", 0.25, metal=0.9)
lampm = mat_col("lampm", "#FFE2A0", 0.4, emit=10); starm = mat_col("starm", "#FF2A2A", 0.3, emit=12)
LOC = {"moscow": 0.0, "piter": 40.0, "village": 80.0, "home": 120.0}

# ---------------- Moscow: Kremlin wall + Spasskaya tower
X = LOC["moscow"]
box("ground_m", 30, 30, 0.1, (X, 6, -0.05), {"other": stone})
for k in range(-6, 7):
    box("wall", 2.0, 1.0, 4.0, (X + k * 2, 9, 2.0), {"other": red})
    for m in (-0.5, 0.5): box("merlon", 0.55, 1.0, 0.7, (X + k * 2 + m, 9, 4.35), {"other": red2})
box("tower", 3.0, 3.0, 8.0, (X + 1.5, 8.6, 4.0), {"other": red})
box("tower2", 2.2, 2.2, 3.0, (X + 1.5, 8.6, 9.5), {"other": red2})
box("spire", 1.2, 1.2, 3.0, (X + 1.5, 8.6, 12.5), {"other": mat_col("green", "#2E5A3A", 0.6)})
box("star", 0.9, 0.3, 0.9, (X + 1.5, 8.4, 14.5), {"other": starm})
box("clock", 1.6, 0.1, 1.6, (X + 1.5, 7.05, 7.0), {"other": mat_col("clockf", "#F4EAD0", 0.4, emit=1.5)})
for k in range(-3, 4):
    box("lamp", 0.12, 0.12, 2.6, (X + k * 3.2, 4.5, 1.3), {"other": mat_col("pole", "#222", 0.5)})
    box("lampb", 0.35, 0.35, 0.35, (X + k * 3.2, 4.5, 2.7), {"other": lampm})
area("m_key", (X - 1.5, -3.0, 3.6), (X, 1, 1.4), 420, (1.0, 0.85, 0.7), 3.0)
area("m_rim", (X + 2, 5, 4), (X, 0, 1.5), 500, (1.0, 0.4, 0.3), 4.0)

# ---------------- Piter: embankment, Neva, golden spire, raised bridge
X = LOC["piter"]
box("emb", 30, 4, 0.6, (X, 0, -0.3), {"other": mat_col("granite", "#6E6460", 0.6)})
box("neva", 40, 30, 0.1, (X, 17, -0.8), {"other": mat_col("neva", "#1C2E4A", 0.08)})
box("rail", 30, 0.1, 0.9, (X, 1.9, 0.45), {"other": mat_col("railm", "#222", 0.4)})
box("fortress", 10, 3, 2.5, (X - 4, 22, 0.5), {"other": mat_col("fort", "#C9A880", 0.7)})
box("cath", 2, 2, 4, (X - 4, 22, 2.5), {"other": mat_col("cath", "#E8D8B0", 0.6)})
box("pspire", 0.4, 0.4, 7, (X - 4, 22, 8), {"other": gold})
for side in (-1, 1):
    b = box("bridge", 6, 2.4, 0.4, (X + 6 + side * 3, 12, 0.2), {"other": mat_col("brm", "#3A3F48", 0.5)})
    b.rotation_euler = (0, math.radians(-side * 50), 0); b.location.z = 2.3
for k in range(8): box("blight", 0.2, 0.2, 0.2, (X + 3 + k * 0.8, 12, 2.5 + (k % 4) * 0.6), {"other": lampm})
area("p_key", (X - 1.5, -3.0, 3.4), (X, 1, 1.4), 380, (0.8, 0.88, 1.0), 3.0)
area("p_rim", (X + 2, 6, 4), (X, 0, 1.5), 420, (0.4, 0.6, 1.0), 4.0)

# ---------------- Кабаново: hut, fence, sunflowers
X = LOC["village"]
box("grass", 30, 30, 0.1, (X, 6, -0.05), {"other": mat_col("grass", "#3E6A2E", 0.9)})
logm = mat_col("log", "#6B4A2E", 0.8)
box("hut", 5, 4, 3, (X + 0.5, 8, 1.5), {"other": logm})
for k in range(6): box("logline", 5.02, 4.02, 0.08, (X + 0.5, 8, 0.3 + k * 0.5), {"other": mat_col("logd", "#4A3220", 0.8)})
roof = box("roof", 5.6, 4.6, 0.3, (X + 0.5, 8, 3.4), {"other": mat_col("roofm", "#5A5F66", 0.6)})
win = box("hutwin", 1.2, 0.05, 1.0, (X - 0.6, 5.97, 1.7), {"other": mat_col("hwin", "#FFC860", 0.4, emit=4)})
for k in range(-6, 7): box("fence", 0.12, 0.12, 1.2, (X + k * 0.6, 3.5, 0.6), {"other": mat_col("fencem", "#8A6A40", 0.8)})
box("rail1", 8, 0.08, 0.1, (X, 3.5, 0.9), {"other": mat_col("fencem2", "#8A6A40", 0.8)})
for k in range(5):
    sx = X + 2.5 + k * 0.7
    box("stem", 0.06, 0.06, 1.6, (sx, 3.0, 0.8), {"other": mat_col("stemm", "#3E7A2E", 0.8)})
    box("sun", 0.4, 0.08, 0.4, (sx, 2.95, 1.7), {"other": mat_col("sunm", "#F2C230", 0.6)})
area("v_key", (X - 1.5, -3.0, 3.4), (X, 1, 1.4), 380, (1.0, 0.8, 0.6), 3.0)
area("v_rim", (X + 2, 5, 4), (X, 0, 1.5), 300, (1.0, 0.7, 0.4), 4.0)

# ---------------- home: carpet wall + desk
X = LOC["home"]
box("hwall", 10, 0.2, 5, (X, 2.0, 2.5), {"other": mat_col("hwallm", "#2A3B38", 0.85)})
box("hfloor", 10, 7, 0.1, (X, 0, -0.05), {"other": mat_tex("hfloort", "floor_wood", 0.35)})
box("hcarpet", 2.2, 0.06, 3.0, (X - 0.4, 1.88, 1.95), {"front": mat_tex("hcarp", "carpet", 0.9), "other": mat_col("hcf", "#C9A04A")})
box("hdesk", 1.8, 0.8, 0.07, (X + 1.6, 0.9, 0.8), {"other": mat_col("hdeskm", "#5A3A26", 0.45)})
area("h_key", (X - 1.5, -3.0, 3.4), (X, 0.4, 1.4), 420, (1.0, 0.86, 0.66), 3.0)

# ---------------- Руслан (selfie pose) + Клод
r_root = empty("ruslan", (0, 0, 0), 0)
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
arms[1].rotation_euler = (math.radians(-80), 0, math.radians(-25))  # selfie arm toward camera
box("head", 0.5, 0.5, 0.5, (0, 0, 1.78), {"front": r_face, "top": r_cap, "other": r_side}, r_root)
box("cap", 0.53, 0.53, 0.1, (0, 0, 2.05), {"other": r_cap}, r_root)
box("brim", 0.5, 0.24, 0.035, (0, -0.35, 1.985), {"other": r_cap}, r_root)

k_root = empty("klod", (0, 0, 0), 0)
KS = 0.75
kface = mat_tex("kface", "klod_face_neutral_0_0", 0.6)
kside = mat_tex("kside", "klod_side"); ktop = mat_tex("ktop", "klod_top"); kdark = mat_tex("kdark", "klod_dark")
ksnout = mat_tex("ksnout", "klod_snout", 0.5); tusk = mat_col("tusk", "#FFF6E6", 0.3)
for lx in (-0.36, 0.36):
    for ly in (-0.22, 0.22): box("kleg", 0.17 * KS, 0.17 * KS, 0.3 * KS, (lx * KS, ly * KS, 0.15 * KS), {"other": kdark}, k_root)
box("kbody", 1.0 * KS, 0.75 * KS, 0.75 * KS, (0, 0, 0.675 * KS), {"front": kface, "top": ktop, "other": kside}, k_root)
box("snout", 0.38 * KS, 0.15 * KS, 0.19 * KS, (0, -0.445 * KS, 0.56 * KS), {"other": ksnout}, k_root)
for tx in (-0.25, 0.25): box("tusk", 0.05 * KS, 0.05 * KS, 0.14 * KS, (tx * KS, -0.4 * KS, 0.55 * KS), {"other": tusk}, k_root)
for ex in (-0.39, 0.39): box("ear", 0.17 * KS, 0.1 * KS, 0.17 * KS, (ex * KS, -0.22 * KS, 1.13 * KS), {"other": kdark}, k_root)
for k in range(6): box("mane", 0.06, 0.06, 0.08, ((-0.15 + k * 0.06) * KS * 1.3, 0, 1.05 * KS + 0.04), {"other": kdark}, k_root)

selfie = cam("c_selfie", 22, 3.0)

for fr in range(START, min(END, len(PLAN["frames"]))):
    F = PLAN["frames"][fr]
    if F["shot"] == "ui":
        print("SKIP", fr, flush=True); continue
    t = F["t"]; X = LOC[F["loc"]]
    r, k = F["r"], F["k"]
    set_tex(r_face, f'ruslan_face_{r["expr"]}_{r["m"]}_{r["b"]}')
    set_tex(kface, f'klod_face_{k["expr"]}_{k["m"]}_{k["b"]}')
    r_root.location = (X, 1.0, r.get("hop", 0)); r_root.rotation_euler = (0, 0, math.radians(r.get("turn", 0)))
    kp = k["pop"]  # 0..1 pop-in behind Руслан
    k_root.location = (X + 0.85, 2.0, -0.8 * (1 - kp) + 0.03 * abs(math.sin(t * 7)))
    k_root.scale = (max(0.01, kp),) * 3
    for ob in [k_root] + list(k_root.children_recursive): ob.hide_render = kp < 0.02
    if F["loc"] == "home":
        k_root.location = (X + 1.5, 0.95, 0.84); k_root.scale = (0.6,) * 3
    sh = F.get("shake", 0)
    pos = Vector((X - 0.15 + 0.03 * math.sin(t * 1.7) + sh * math.sin(t * 60), -0.65, 1.95 + 0.02 * math.sin(t * 2.1)))
    tgt = Vector((X + 0.25, 1.6, 1.55))
    selfie.location = pos; look(selfie, tgt); selfie.data.dof.focus_distance = (Vector((X, 1.0, 1.78)) - pos).length; sc.camera = selfie
    sc.render.filepath = os.path.join(OUTDIR, f"{fr:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", fr, flush=True)
