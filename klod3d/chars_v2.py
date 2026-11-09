"""Blender character kit v2 (exec after the scene3d.py header). Hi-res expressive faces from tex_v2.py.

    R = ruslan_v2((x, y, 0), rot_deg)    # pink DEYKUN cap, friendly face, white tee + gold chain, jeans, 3D nose
    K = klod_v2((x, y, 0), rot_deg)      # salmon blocky boar with Claude sparkle
    animate(R, t, face={"expr":..,"vis":..,"b":..,"g":..}, gesture=0..1, talk=bool, nod=0..1, walk=0..1)
    animate(K, t, face=..., gesture=..., talk=..., hop=0..1)
Faces: v2r_<expr>_<vis>_<b>_<g> / v2k_<...>; arms and head move on stressed words (gesture), idle breathing always.
"""
import math, random
from mathutils import Vector


def ruslan_v2(loc, rot):
    root = empty("ruslan", loc, rot)
    face = mat_tex("rface2", "v2r_neutral_0_0_c", 0.55)
    rside = mat_tex("rside", "r2_side"); rback = mat_tex("rback", "r2_back"); rcap = mat_tex("rcap", "r2_cap", 0.5)
    tee = mat_tex("tee", "r2_tee"); teeside = mat_tex("teeside", "r2_tee_side"); rarm = mat_tex("rarm", "r2_arm"); jeans = mat_tex("jeans", "r2_jeans")
    skin = mat_col("skin", "#EBC3A5", 0.55); shoe = mat_col("shoe", "#F4F4F4", 0.5)
    legs = []
    for sx in (-0.125, 0.125):
        hip = empty("hip", (sx, 0, 0.75), 0, root)
        box("leg", 0.25, 0.25, 0.75, (0, 0, -0.375), {"other": jeans}, hip)
        box("shoe", 0.27, 0.34, 0.1, (0, -0.04, -0.7), {"other": shoe}, hip); legs.append(hip)
    torso = empty("torso", (0, 0, 0.75), 0, root)
    box("rbody", 0.52, 0.28, 0.76, (0, 0, 0.38), {"front": tee, "other": teeside}, torso)
    head = empty("head", (0, 0, 0.76), 0, torso)
    box("rhead", 0.5, 0.5, 0.5, (0, 0, 0.25), {"front": face, "back": rback, "top": rcap, "other": rside}, head)
    box("nose", 0.08, 0.07, 0.1, (0, -0.28, 0.2), {"other": skin}, head)
    pinkc = mat_col("pinkc", "#F0569A", 0.45)
    box("capb", 0.54, 0.54, 0.12, (0, 0, 0.53), {"top": rcap, "other": pinkc}, head)
    box("brim", 0.5, 0.26, 0.04, (0, -0.36, 0.48), {"other": mat_col("brim", "#E04A8C", 0.5)}, head)
    bpy.ops.object.text_add(location=(0, -0.276, 0.535), rotation=(math.radians(90), 0, 0))
    lg = bpy.context.object; lg.data.body = "DEYKUN"; lg.data.size = 0.075; lg.data.align_x = "CENTER"; lg.data.align_y = "CENTER"
    lg.data.extrude = 0.004; lg.data.font = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf")
    lg.data.materials.append(mat_col("logo", "#FFFFFF", 0.5)); lg.parent = head
    arms = []
    for sx in (-0.39, 0.39):
        sh = empty("shoulder", (sx, 0, 0.72), 0, torso)
        box("arm", 0.24, 0.26, 0.74, (0, 0, -0.35), {"other": rarm}, sh); arms.append(sh)
    return {"kind": "r", "root": root, "torso": torso, "head": head, "arms": arms, "legs": legs, "face": face, "rot": rot, "z0": loc[2]}


def klod_v2(loc, rot, scale=1.0):
    root = empty("klod", loc, rot)
    face = mat_tex("kface2", "v2k_neutral_0_0_c", 0.6)
    kside = mat_tex("kside", "klod_side"); ktop = mat_tex("ktop", "klod_top"); kdark = mat_tex("kdark", "klod_dark")
    ksnout = mat_tex("ksnout", "klod_snout", 0.5); tusk = mat_col("tusk", "#FFF6E6", 0.3)
    body = empty("kbodyp", (0, 0, 0.3), 0, root)
    legs = []
    for lx in (-0.36, 0.36):
        for ly in (-0.22, 0.22):
            lp = empty("kleg", (lx, ly, 0.3), 0, root); box("kl", 0.17, 0.17, 0.3, (0, 0, -0.15), {"other": kdark}, lp); legs.append(lp)
    box("kbody", 1.0, 0.75, 0.75, (0, 0, 0.375), {"front": face, "top": ktop, "other": kside}, body)
    box("snout", 0.38, 0.15, 0.19, (0, -0.445, 0.26), {"other": ksnout}, body)
    for tx in (-0.25, 0.25): box("tusk", 0.05, 0.05, 0.14, (tx, -0.4, 0.25), {"other": tusk}, body)
    ears = []
    for ex in (-0.39, 0.39):
        ep = empty("ear", (ex, -0.22, 0.75), 0, body); box("e", 0.17, 0.1, 0.17, (0, 0, 0.08), {"other": kdark}, ep); ears.append(ep)
    rr = random.Random(4)
    for k in range(7): box("mane", 0.07, 0.07, rr.uniform(0.06, 0.13), (-0.2 + k * 0.065, -0.05 + rr.uniform(-0.1, 0.1), 0.78), {"other": kdark}, body)
    root.scale = (scale,) * 3
    return {"kind": "k", "root": root, "body": body, "legs": legs, "ears": ears, "face": face, "rot": rot, "z0": loc[2]}


def polish(C, bevel=0.018, segments=3):
    """Max quality pass for blocky heroes: rounded bevelled edges that catch light, smooth-shaded bevels,
    skin subsurface, cloth/fur sheen. Call once after ruslan_v2()/klod_v2()."""
    import bpy
    root = C["root"]; seen = set()
    for o in [root] + list(root.children_recursive):
        if o.type != "MESH" or o.name in seen: continue
        seen.add(o.name)
        dims = min(o.dimensions) if o.dimensions else 0.1
        m = o.modifiers.new("bev", "BEVEL"); m.width = min(bevel, dims * 0.18); m.segments = segments; m.limit_method = "ANGLE"
        m.harden_normals = True
        for poly in o.data.polygons: poly.use_smooth = True
        if hasattr(o.data, "use_auto_smooth"): o.data.use_auto_smooth = True; o.data.auto_smooth_angle = 0.6
        for slot in o.material_slots:
            mat = slot.material
            if not mat or not mat.use_nodes or mat.get("polished"): continue
            b = mat.node_tree.nodes.get("Principled BSDF")
            if not b: continue
            n = mat.name.lower()
            if any(k in n for k in ("face", "skin", "hand", "nose")):
                b.inputs["Subsurface Weight"].default_value = 0.12; b.inputs["Subsurface Radius"].default_value = (0.4, 0.15, 0.08)
                b.inputs["Roughness"].default_value = 0.5
            elif any(k in n for k in ("tee", "jeans", "arm", "cap", "pink", "brim")):
                b.inputs["Sheen Weight"].default_value = 0.35; b.inputs["Roughness"].default_value = 0.75
            elif any(k in n for k in ("kside", "ktop", "kdark", "kface")):
                b.inputs["Sheen Weight"].default_value = 0.45; b.inputs["Sheen Roughness"].default_value = 0.4; b.inputs["Roughness"].default_value = 0.7
            elif "tusk" in n or "shoe" in n or "logo" in n:
                b.inputs["Roughness"].default_value = 0.3; b.inputs["Coat Weight"].default_value = 0.3
            mat["polished"] = True


def animate(C, t, face=None, gesture=0.0, talk=False, nod=0.0, walk=0.0, hop=0.0, point=0.0):
    f = face or {}
    pre = "v2r" if C["kind"] == "r" else "v2k"
    set_tex(C["face"], f'{pre}_{f.get("expr", "neutral")}_{f.get("vis", 0)}_{f.get("b", 0)}_{f.get("g", "c")}')
    breath = 0.012 * math.sin(t * 2.1)
    if C["kind"] == "r":
        C["torso"].scale = (1, 1, 1 + breath)
        C["head"].rotation_euler = (math.radians(4 * nod * math.sin(t * 9) + (3 if talk else 0) * math.sin(t * 6.5)), 0,
                                    math.radians(6 * math.sin(t * 0.9) + 8 * gesture * math.sin(t * 3)))
        sw = math.sin(t * 9) * 0.6 * walk
        C["legs"][0].rotation_euler = (sw, 0, 0); C["legs"][1].rotation_euler = (-sw, 0, 0)
        # right hand: emphatic raise on stressed words; left: point at partner
        C["arms"][1].rotation_euler = (math.radians(-sw * 50 - 65 * gesture - 6 * math.sin(t * 1.7)), 0, math.radians(-12 * gesture))
        C["arms"][0].rotation_euler = (math.radians(sw * 50 - 80 * point - 4 * math.sin(t * 1.5 + 1)), 0, math.radians(10 * point))
        C["root"].location.z = C["z0"] + 0.05 * abs(math.sin(t * 9)) * walk + 0.15 * hop
    else:
        C["body"].scale = (1 + 0.03 * gesture, 1, 1 + breath + 0.04 * gesture)
        C["body"].rotation_euler = (math.radians(3 * gesture), 0, math.radians(3 * math.sin(t * 1.3) + (2 if talk else 0) * math.sin(t * 8)))
        for k, e in enumerate(C["ears"]): e.rotation_euler = (math.radians(12 * gesture + 4 * math.sin(t * 3 + k)), 0, 0)
        C["root"].location.z = C["z0"] + 0.25 * hop * abs(math.sin(t * 10)) + (0.02 * abs(math.sin(t * 9)) if talk else 0)
