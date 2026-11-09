"""SMOOTH stylized 3D heroes (next level after the blocky/vinyl ones). exec() after the scene3d.py header (+ quality.py).

    R = ruslan_smooth((x, y, 0), rot_deg)   # pink DEYKUN cap, white tee + gold chain, jeans, sneakers
    K = klod_smooth((x, y, 0), rot_deg)     # ALWAYS a boar: salmon body, snout, tusks, ears, mane, Claude sparkle
    animate_smooth(C, t, face={"expr","vis","b","g"}, gesture=0..1, talk=bool, walk=0..1, hop=0..1, point=0..1)
Face rig: eyeballs with iris/pupil/glint that look l/c/r, eyelids for blink & moods, brows tilt per expression,
mouth = dark pocket scaled per viseme (0 closed … 4 lips pressed) with teeth & tongue. Subdivision-smooth bodies,
skin subsurface, fabric sheen, glossy eyes.
"""
import math, bmesh, bpy
from mathutils import Vector


def _mat(name, col, rough=0.5, sss=0.0, sheen=0.0, metal=0.0, coat=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    c = tuple((int(col[i:i + 2], 16) / 255) ** 2.2 for i in (1, 3, 5)) + (1,)
    b.inputs["Base Color"].default_value = c; b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    b.inputs["Subsurface Weight"].default_value = sss; b.inputs["Subsurface Radius"].default_value = (0.5, 0.2, 0.1)
    b.inputs["Sheen Weight"].default_value = sheen; b.inputs["Coat Weight"].default_value = coat
    if emit: b.inputs["Emission Color"].default_value = c; b.inputs["Emission Strength"].default_value = emit
    return m


def _obj(name, mesh_fn, mat, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, subd=2):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); mesh_fn(bm); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    o.location = loc; o.scale = scale; o.rotation_euler = rot
    if parent: o.parent = parent
    if name in BOXY:   # straight parts: rounded bevel keeps the volume (subdivision would melt them into blobs)
        bv = o.modifiers.new("bev", "BEVEL"); bv.width = BOXY[name]; bv.segments = 5; bv.limit_method = "NONE"
        bv.affect = "EDGES"; bv.use_clamp_overlap = True
        if hasattr(me, "use_auto_smooth"): me.use_auto_smooth = True; me.auto_smooth_angle = 1.0
    elif subd:
        m = o.modifiers.new("sub", "SUBSURF"); m.levels = subd; m.render_levels = subd
    return o


BOXY = {"leg": 0.04, "shoe": 0.4, "body": 0.45, "sleeve": 0.035, "forearm": 0.025, "neck": 0.02, "sideburn": 0.3, "brimm": 0.008,
        "kl": 0.03, "hoof": 0.015, "snout": 0.04, "mane": 0.01, "earm": 0.02, "tusk": 0.01, "ray": 0.4, "browm": 0.4, "teeth": 0.4, "medal": 0.004}


def sphere(r=1.0, seg=24):
    return lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)


def cube(s=1.0):
    return lambda bm: bmesh.ops.create_cube(bm, size=2 * s)   # scale = half-extent


def cyl(r=1.0, h=1.0, seg=16, r2=None):
    return lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)


def _empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc
    if parent: e.parent = parent
    return e


def _eye_rig(parent, x, y, z, r, iris_col, white, black, glint, lid_mat):
    rig = []
    for sx in (-1, 1):
        piv = _empty("eye", (sx * x, y, z), parent)
        _obj("white", sphere(r, 24), white, parent=piv, subd=1)
        look = _empty("look", (0, 0, 0), piv)
        _obj("iris", sphere(r * 0.55, 16), iris_col, (0, -r * 0.62, 0), (1, 0.35, 1), parent=look, subd=1)
        _obj("pupil", sphere(r * 0.3, 12), black, (0, -r * 0.8, 0), (1, 0.3, 1), parent=look, subd=1)
        _obj("glint", sphere(r * 0.12, 8), glint, (r * 0.18, -r * 0.92, r * 0.22), parent=look, subd=0)
        lid = _empty("lid", (0, 0, 0), piv)
        _obj("lidm", sphere(r * 1.1, 24), lid_mat, (0, -r * 0.05, 0), (1, 1, 0.6), parent=lid, subd=1)
        rig.append((piv, look, lid, r))
    return rig


def _brows(parent, x, y, z, w, col):
    out = []
    for sx in (-1, 1):
        p = _empty("brow", (sx * x, y, z), parent)
        _obj("browm", cube(1), col, (0, 0, 0), (w, 0.016, 0.014), parent=p, subd=2); out.append(p)
    return out


def _mouth(parent, loc, w, dark, teeth, tongue):
    m = _empty("mouth", loc, parent)
    _obj("pocket", sphere(1, 20), dark, (0, 0, 0), (w, 0.04, 0.05), parent=m, subd=1)
    t1 = _obj("teeth", cube(1), teeth, (0, -0.015, 0.03), (w * 0.35, 0.005, 0.008), parent=m, subd=1)
    t2 = _obj("tongue", sphere(1, 12), tongue, (0, -0.01, -0.02), (w * 0.5, 0.02, 0.02), parent=m, subd=1)
    return m


GL = {}


def _shared():
    if GL: return GL
    GL.update(white=_mat("eyew", "#F8F6F2", 0.08, coat=0.6), black=_mat("eyek", "#0D0D0F", 0.05, coat=0.8), glint=_mat("glint", "#FFFFFF", 0.1, emit=6),
              dark=_mat("mouthd", "#4A0F18", 0.4), teeth=_mat("teeth", "#FBF7EE", 0.25, coat=0.3), tongue=_mat("tongue", "#E86A7A", 0.35, sss=0.2),
              gold=_mat("gold2", "#F2B53A", 0.2, metal=0.9))
    return GL


def ruslan_smooth(loc, rot):
    g = _shared()
    skin = _mat("rskin", "#EBC3A5", 0.48, sss=0.15); tee = _mat("rtee", "#F4F1EC", 0.8, sheen=0.4); jeans = _mat("rjeans", "#3C5A8C", 0.85, sheen=0.3)
    capm = _mat("rcap", "#F0569A", 0.6, sheen=0.5); brim = _mat("rbrim", "#D9408A", 0.6, sheen=0.4); shoe = _mat("rshoe", "#F7F7F7", 0.4, coat=0.2)
    hair = _mat("rhair", "#4A3224", 0.7, sheen=0.5); brow = _mat("rbrow", "#3A2418", 0.7)
    root = _empty("ruslan", loc); root.rotation_euler = (0, 0, math.radians(rot))
    legs = []
    for sx in (-0.12, 0.12):
        hip = _empty("hip", (sx, 0, 0.82), root)
        _obj("leg", cyl(0.105, 0.78, 16, 0.095), jeans, (0, 0, -0.39), parent=hip)
        _obj("shoe", cube(1), shoe, (0, -0.05, -0.765), (0.11, 0.17, 0.055), parent=hip); legs.append(hip)
    torso = _empty("torso", (0, 0, 0.82), root)
    _obj("body", cube(1), tee, (0, 0, 0.36), (0.27, 0.16, 0.36), parent=torso)
    for k in range(15):
        a = -1.2 + k * (2.4 / 14)
        _obj("link", sphere(0.018, 8), g["gold"], (0.13 * math.sin(a), -0.17 - 0.01 * math.cos(a), 0.66 - 0.1 * (1 - math.cos(a))), parent=torso, subd=0)
    _obj("medal", cyl(0.035, 0.012, 16), g["gold"], (0, -0.18, 0.55), rot=(math.radians(90), 0, 0), parent=torso, subd=1)
    arms = []
    for sx in (-1, 1):
        sh = _empty("shoulder", (sx * 0.3, 0, 0.66), torso)
        _obj("sleeve", cyl(0.085, 0.24, 16), tee, (0, 0, -0.1), parent=sh)
        _obj("forearm", cyl(0.06, 0.3, 16, 0.055), skin, (0, 0, -0.36), parent=sh)
        _obj("hand", sphere(0.07, 16), skin, (0, 0, -0.54), (1, 0.8, 1.1), parent=sh); arms.append(sh)
    head = _empty("head", (0, 0, 0.74), torso)
    _obj("neck", cyl(0.07, 0.12, 12), skin, (0, 0, 0.0), parent=head)
    _obj("skull", sphere(0.25, 32), skin, (0, 0, 0.27), (1, 0.95, 1.08), parent=head)
    for sx in (-1, 1):
        _obj("ear", sphere(0.06, 12), skin, (sx * 0.245, 0.0, 0.27), (0.5, 0.9, 1.2), parent=head)
        _obj("sideburn", cube(1), hair, (sx * 0.225, -0.02, 0.36), (0.015, 0.045, 0.035), parent=head)
    _obj("nose", sphere(0.045, 12), skin, (0, -0.25, 0.25), (0.9, 0.9, 1.1), parent=head)
    _obj("cap", sphere(0.27, 32), capm, (0, 0.01, 0.36), (1.0, 1.0, 0.72), parent=head)
    _obj("brimm", cyl(0.2, 0.02, 32), brim, (0, -0.25, 0.39), (1.0, 1.15, 1), rot=(math.radians(-8), 0, 0), parent=head)
    bpy.ops.object.text_add(location=(0, -0.255, 0.48), rotation=(math.radians(80), 0, 0))
    lg = bpy.context.object; lg.data.body = "DEYKUN"; lg.data.size = 0.06; lg.data.align_x = "CENTER"; lg.data.align_y = "CENTER"; lg.data.extrude = 0.004
    lg.data.font = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"); lg.data.materials.append(_mat("logo2", "#FFFFFF", 0.5)); lg.parent = head
    for sx in (-1, 1): _obj("blush", sphere(0.035, 12), _mat("blush", "#F29A9A", 0.6), (sx * 0.15, -0.205, 0.22), (1, 0.3, 0.6), parent=head, subd=0)
    eyes = _eye_rig(head, 0.085, -0.2, 0.3, 0.045, _mat("riris", "#5B3A22", 0.15, coat=0.5), g["white"], g["black"], g["glint"], skin)
    brs = _brows(head, 0.085, -0.235, 0.375, 0.055, brow)
    mouth = _mouth(head, (0, -0.235, 0.17), 0.06, g["dark"], g["teeth"], g["tongue"])
    return {"kind": "rs", "root": root, "torso": torso, "head": head, "arms": arms, "legs": legs, "eyes": eyes, "brows": brs, "mouth": mouth, "z0": loc[2], "rot": rot}


def klod_smooth(loc, rot, scale=1.0):
    g = _shared()
    body = _mat("kbody", "#E5684B", 0.62, sss=0.06, sheen=0.6); dark = _mat("kdark2", "#A9442E", 0.7, sheen=0.5)
    snout = _mat("ksnout2", "#F49A82", 0.45, sss=0.12); tusk = _mat("ktusk", "#FFF6E6", 0.25, coat=0.5); spark = _mat("kspark", "#FFF1E4", 0.3, emit=0.6)
    root = _empty("klod", loc); root.rotation_euler = (0, 0, math.radians(rot)); root.scale = (scale,) * 3
    legs = []
    for lx in (-0.3, 0.3):
        for ly in (-0.2, 0.25):
            lp = _empty("kleg", (lx, ly, 0.28), root); _obj("kl", cyl(0.075, 0.28, 12, 0.065), dark, (0, 0, -0.14), parent=lp)
            _obj("hoof", cyl(0.07, 0.05, 12), _mat("hoof", "#3A1A12", 0.4), (0, 0, -0.28), parent=lp); legs.append(lp)
    bod = _empty("kbodyp", (0, 0, 0.3), root)
    _obj("torso", sphere(0.42, 32), body, (0, 0.08, 0.28), (1.0, 1.25, 0.82), parent=bod)
    _obj("head", sphere(0.36, 32), body, (0, -0.32, 0.36), (1.05, 0.95, 0.95), parent=bod)
    for k in range(9):
        _obj("mane", cyl(0.035, 0.12, 8, 0.0), dark, (-0.16 + k * 0.04, -0.15 + abs(k - 4) * 0.01, 0.68), rot=(math.radians(-15), 0, math.radians((k - 4) * 6)), parent=bod, subd=1)
    ears = []
    for sx in (-1, 1):
        ep = _empty("ear", (sx * 0.24, -0.38, 0.62), bod)
        _obj("earm", cyl(0.08, 0.16, 12, 0.0), dark, (0, 0, 0.06), (1, 0.45, 1), rot=(0, math.radians(sx * 25), 0), parent=ep); ears.append(ep)
    _obj("snout", cyl(0.17, 0.12, 24), snout, (0, -0.66, 0.29), (1.0, 1.0, 0.72), rot=(math.radians(90), 0, 0), parent=bod)
    for sx in (-1, 1):
        _obj("nostril", sphere(0.028, 12), g["dark"], (sx * 0.06, -0.725, 0.3), (0.8, 0.4, 1.2), parent=bod, subd=0)
        _obj("tusk", cyl(0.028, 0.14, 10, 0.0), tusk, (sx * 0.17, -0.6, 0.2), rot=(math.radians(-20), math.radians(sx * 18), 0), parent=bod, subd=1)
    for k in range(8):
        a = k * math.pi / 4
        _obj("ray", cube(1), spark, (0.055 * math.sin(a), -0.62 + 0.0, 0.58 + 0.055 * math.cos(a)), (0.008, 0.006, 0.022), rot=(math.radians(-20), a, 0), parent=bod, subd=1)
    _obj("core", sphere(0.022, 10), spark, (0, -0.64, 0.58), parent=bod, subd=0)
    eyes = _eye_rig(bod, 0.14, -0.57, 0.46, 0.055, g["black"], g["white"], g["black"], g["glint"], body)
    brs = _brows(bod, 0.14, -0.6, 0.535, 0.06, _mat("kbrow", "#5A2418", 0.6))
    mouth = _mouth(bod, (0, -0.64, 0.15), 0.07, g["dark"], g["teeth"], g["tongue"])
    return {"kind": "ks", "root": root, "body": bod, "legs": legs, "ears": ears, "eyes": eyes, "brows": brs, "mouth": mouth, "z0": loc[2], "rot": rot}


BROW = {"angry": (14, -0.012), "sad": (-14, 0.0), "shock": (0, 0.02), "panic": (-8, 0.022), "think": (8, 0.01), "smug": (6, -0.004), "happy": (-4, 0.008)}
VIS = {0: (1.0, 0.25), 1: (1.15, 0.55), 2: (0.95, 1.25), 3: (0.6, 1.0), 4: (1.05, 0.12)}


def animate_smooth(C, t, face=None, gesture=0.0, talk=False, walk=0.0, hop=0.0, point=0.0, nod=0.0):
    f = face or {}; expr = f.get("expr", "neutral"); vis = f.get("vis", 0); blink = f.get("b", 0); gz = {"l": -1, "c": 0, "r": 1}[f.get("g", "c")]
    for piv, look, lid, r in C["eyes"]:
        look.rotation_euler = (0, 0, math.radians(-gz * 22))
        close = 1.0 if blink else {"smug": 0.45, "angry": 0.4, "sad": 0.35, "happy": 0.5}.get(expr, 0.0)
        lid.location = (0, 0, r * (0.25 + 0.95 * (1 - close)))   # lid slides from above the eye down over it
    tilt, lift = BROW.get(expr, (0, 0))
    for k, b in enumerate(C["brows"]):
        sx = -1 if k == 0 else 1
        b.rotation_euler = (0, math.radians(sx * tilt), 0)
    sx, sz = VIS.get(vis, VIS[0])
    if vis == 0 and expr in ("happy", "smug"): sx, sz = 1.2, 0.3
    if expr in ("shock", "panic") and vis == 0: sx, sz = 0.55, 0.8
    C["mouth"].scale = (sx, 1, sz)
    breath = 0.01 * math.sin(t * 2.1)
    if C["kind"] == "rs":
        C["torso"].scale = (1, 1, 1 + breath)
        C["head"].rotation_euler = (math.radians(4 * nod * math.sin(t * 9) + (3 if talk else 0) * math.sin(t * 6.5)), 0, math.radians(5 * math.sin(t * 0.9) + 7 * gesture * math.sin(t * 3)))
        sw = math.sin(t * 9) * 0.6 * walk
        C["legs"][0].rotation_euler = (sw, 0, 0); C["legs"][1].rotation_euler = (-sw, 0, 0)
        C["arms"][1].rotation_euler = (math.radians(-sw * 50 - 70 * gesture - 5 * math.sin(t * 1.7)), 0, math.radians(8 - 14 * gesture))
        C["arms"][0].rotation_euler = (math.radians(sw * 50 - 85 * point - 4 * math.sin(t * 1.5 + 1)), 0, math.radians(-8 + 10 * point))
        C["root"].location.z = C["z0"] + 0.04 * abs(math.sin(t * 9)) * walk + 0.15 * hop
    else:
        C["body"].scale = (1 + 0.02 * gesture, 1, 1 + breath + 0.03 * gesture)
        C["body"].rotation_euler = (math.radians(3 * gesture), 0, math.radians(3 * math.sin(t * 1.3) + (2 if talk else 0) * math.sin(t * 8)))
        for k, e in enumerate(C["ears"]): e.rotation_euler = (math.radians(14 * gesture + 5 * math.sin(t * 3 + k)), 0, 0)
        C["root"].location.z = C["z0"] + 0.25 * hop * abs(math.sin(t * 10)) + (0.015 * abs(math.sin(t * 9)) if talk else 0)
