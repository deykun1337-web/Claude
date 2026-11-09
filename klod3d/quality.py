"""PRO quality preset for every Blender scene. exec() it AFTER the scene3d.py header (needs `sc`, `bpy`).

    exec(open(os.path.join(HERE, "quality.py")).read())
    pro_lights(target=(0, 0, 1.2))        # optional: adds a soft top light + bounce if the scene is too flat

What it changes vs the old 720p/12-sample render:
  · native 810×1440 (sharper than 720 upscaled; upscale to 1080×1920 only in ffmpeg)
  · 20 TAA samples, motion blur (shutter 0.5), soft shadows 2048 cube / 4096 cascade, contact shadows on all lights
  · GTAO with bent normals, SSR (+refraction), subtle volumetrics for light shafts, bloom tuned for neon
  · AgX with "Medium High Contrast" look, slight exposure lift, film-like
Render time ≈ 2× the old preset → use for the 2 daily hero reels.
"""
import bpy

sc.render.resolution_x, sc.render.resolution_y = 810, 1440
ee = sc.eevee
ee.taa_render_samples = 20
ee.use_motion_blur = True; ee.motion_blur_shutter = 0.5; ee.motion_blur_steps = 1
ee.use_soft_shadows = True; ee.shadow_cube_size = "2048"; ee.shadow_cascade_size = "4096"; ee.use_shadow_high_bitdepth = True
ee.use_gtao = True; ee.gtao_distance = 0.4; ee.gtao_factor = 1.15; ee.use_gtao_bent_normals = True
ee.use_ssr = True; ee.use_ssr_refraction = True; ee.ssr_quality = 0.6; ee.ssr_thickness = 0.3
ee.use_bloom = True; ee.bloom_threshold = 0.85; ee.bloom_intensity = max(ee.bloom_intensity, 0.06); ee.bloom_radius = 6.5
ee.use_volumetric_lights = True; ee.volumetric_samples = max(getattr(ee, "volumetric_samples", 16), 32); ee.volumetric_tile_size = "8"
sc.view_settings.view_transform = "AgX"
try:
    sc.view_settings.look = "AgX - Punchy"
except TypeError:
    sc.view_settings.look = "AgX - Punchy"
sc.render.film_transparent = False
sc.render.filter_size = 1.2


def _contact_shadows():
    for L in bpy.data.lights:
        if hasattr(L, "use_contact_shadow"):
            L.use_contact_shadow = True; L.contact_shadow_distance = 0.15; L.contact_shadow_thickness = 0.02


def pro_lights(target=(0, 0, 1.2), warm=(1.0, 0.86, 0.72), cool=(0.62, 0.72, 1.0)):
    """Soft overhead key + floor bounce: removes the flat 'game' look on blocky characters."""
    from mathutils import Vector
    t = Vector(target)
    top = bpy.data.lights.new("pro_top", "AREA"); top.energy = 110; top.size = 4; top.color = warm
    o = bpy.data.objects.new("pro_top", top); bpy.context.collection.objects.link(o); o.location = t + Vector((0.5, -1.0, 4.0))
    o.rotation_euler = (t - o.location).to_track_quat("-Z", "Y").to_euler()
    b = bpy.data.lights.new("pro_bounce", "AREA"); b.energy = 35; b.size = 3; b.color = cool
    o2 = bpy.data.objects.new("pro_bounce", b); bpy.context.collection.objects.link(o2); o2.location = t + Vector((0, -1.5, -1.0))
    o2.rotation_euler = (t - o2.location).to_track_quat("-Z", "Y").to_euler()
    _contact_shadows()


_contact_shadows()
