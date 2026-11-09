import bpy, json, math, os, random, sys
from mathutils import Vector
HERE = "/home/user/Claude/klod3d"; SP = "/tmp/claude-0/-home-user-Claude/8ebf3e2a-b18f-5ba9-ac9d-30501f6704c5/scratchpad"
sys.argv = sys.argv[:sys.argv.index("--") + 1] + ["/dev/null", SP + "/avatar", "0", "1"]
_src = open(os.path.join(HERE, "scene3d.py")).read().replace('PLAN = json.load(open(argv[0]))', 'PLAN = {}')
exec(_src[:_src.index("# ------------------------------------------------------------- characters")].replace('__file__', '"%s/scene3d.py"' % HERE))
exec(open(os.path.join(HERE, "chars_v2.py")).read())
sc.render.resolution_x = sc.render.resolution_y = 1080; sc.eevee.taa_render_samples = 48; sc.eevee.bloom_intensity = 0.08
world((0.9, 0.3, 0.55), 0.0)
# pink gradient backdrop
bg = bpy.data.materials.new("bg"); bg.use_nodes = True; nt = bg.node_tree; b = nt.nodes["Principled BSDF"]
ramp = nt.nodes.new("ShaderNodeValToRGB"); tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], ramp.inputs[0])
ramp.color_ramp.elements[0].color = (0.45, 0.02, 0.35, 1); ramp.color_ramp.elements[1].color = (1.0, 0.18, 0.45, 1)
nt.links.new(ramp.outputs[0], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 1.6; b.inputs["Base Color"].default_value = (0, 0, 0, 1)
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 2.0, 1.4), rotation=(math.radians(90), 0, 0)); bpy.context.object.data.materials.append(bg)
area("key", (-2.2, -3.2, 3.2), (0, 0, 1.3), 650, (1, 0.92, 0.9), 3); area("fill", (2.5, -2.5, 1.5), (0, 0, 1.2), 220, (0.85, 0.85, 1), 3)
area("rim", (0, 1.4, 3.0), (0, 0, 1.4), 500, (1, 0.8, 0.95), 2)
import sys as _s
R = ruslan_v2((-0.42, 0, 0), 14); K = klod_v2((0.5, -0.25, 0.62), -16, 0.95)
animate(R, 0.4, face={"expr": "happy", "vis": 2, "g": "c"}, gesture=0.0)
R["arms"][1].rotation_euler = (math.radians(-35), math.radians(-55), math.radians(-20))    # hand out to the side (wave)
animate(K, 0.4, face={"expr": "smug", "vis": 0, "g": "l"})
c = bpy.data.cameras.new("c"); c.sensor_fit = "VERTICAL"; c.sensor_height = 24; c.lens = 40; c.dof.use_dof = True; c.dof.aperture_fstop = 4
C = bpy.data.objects.new("c", c); bpy.context.collection.objects.link(C); sc.camera = C
tgt = Vector((0.04, 0, 1.55)); C.location = tgt + Vector((0.1, -3.6, 0.2)); look(C, tgt); c.dof.focus_distance = 3.6
os.makedirs(OUTDIR, exist_ok=True)
# variant 2: Klod alone, close
R["root"].location = (0, 0, -50); K["z0"] = 0.0; K["root"].rotation_euler = (0, 0, math.radians(-8))
animate(K, 0.4, face={"expr": "happy", "vis": 0, "g": "c"})
tgt = Vector((0.5, -0.6, 0.72)); C.location = tgt + Vector((0.2, -3.0, 0.2)); look(C, tgt); c.dof.focus_distance = 3.3
sc.render.filepath = OUTDIR + "/klod.png"; bpy.ops.render.render(write_still=True)
