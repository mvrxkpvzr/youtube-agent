"""Blender 3D shots for the pipeline. Run headless:
  Blender -b --factory-startup -P pipeline/blender/shots.py -- <shot> <out_dir> <params.json>
Shots:
  number    – extruded, bevelled number + label, camera swing/dolly, DOF, reflective floor, floating dust
  timeline  – camera flies past image panels (story cards) with year labels and a glowing path
  question  – two extruded lines of text, camera orbit, moving light sweep
Renders PNG frames (Eevee) into <out_dir>/frames/####.png; encoding/post-FX is done by the pipeline."""
import bpy, json, math, os, random, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SHOT, OUT, PARAMS = argv[0], argv[1], json.load(open(argv[2], encoding="utf-8")) if len(argv) > 2 else {}
FPS = 25
ACCENT = (0.949, 0.694, 0.204)          # #F2B134
BG = (0.055, 0.078, 0.125)              # #0E1420
FONT = PARAMS.get("font")

def srgb_to_lin(c): return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def reset(frames):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try: sc.render.engine = eng; break
        except TypeError: pass
    sc.render.resolution_x, sc.render.resolution_y = PARAMS.get("w", 1920), PARAMS.get("h", 1080)
    sc.render.resolution_percentage = PARAMS.get("pct", 100)
    sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = frames
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = os.path.join(OUT, "frames", "")
    try: sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception: pass
    ee = getattr(sc, "eevee", None)
    if ee:
        for attr, val in (("taa_render_samples", PARAMS.get("samples", 48)), ("use_raytracing", True), ("use_shadows", True)):
            try: setattr(ee, attr, val)
            except Exception: pass
    try: sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
    except Exception: pass
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    bgn = w.node_tree.nodes["Background"]; bgn.inputs[0].default_value = (*srgb_to_lin(BG), 1); bgn.inputs[1].default_value = 1.0
    return sc

def mat(name, color, metallic=0.0, rough=0.4, emit=0.0, emit_color=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*srgb_to_lin(color), 1)
    p.inputs["Metallic"].default_value = metallic; p.inputs["Roughness"].default_value = rough
    if emit:
        for key in ("Emission Color", "Emission"):
            if key in p.inputs: p.inputs[key].default_value = (*srgb_to_lin(emit_color or color), 1); break
        p.inputs["Emission Strength"].default_value = emit
    return m

def image_mat(path, emit=0.9):
    m = bpy.data.materials.new(os.path.basename(path)); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(path)
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    for key in ("Emission Color", "Emission"):
        if key in p.inputs: nt.links.new(tex.outputs["Color"], p.inputs[key]); break
    p.inputs["Emission Strength"].default_value = emit; p.inputs["Roughness"].default_value = 0.35
    return m, tex.image

def text(body, size=1.0, extrude=0.12, bevel=0.018, material=None, loc=(0, 0, 0), align="CENTER"):
    cu = bpy.data.curves.new("T", "FONT"); cu.body = body; cu.size = size
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = 3
    cu.align_x = align; cu.align_y = "CENTER"; cu.space_character = PARAMS.get("tracking", 1.0)
    if FONT: cu.font = bpy.data.fonts.load(FONT)
    ob = bpy.data.objects.new("T", cu); bpy.context.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler = (math.radians(90), 0, 0)  # stand upright, facing -Y
    if material: ob.data.materials.append(material)
    return ob

def floor(z=-0.75):
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, z))
    f = bpy.context.object; f.data.materials.append(mat("floor", (0.03, 0.04, 0.06), metallic=0.6, rough=0.18)); return f

def backdrop(y=9.0, glow=(0.0, 1.2)):
    """Large navy wall behind the subject with a soft warm glow spot (gives the 'Bige' depth)."""
    m = bpy.data.materials.new("backdrop"); m.use_nodes = True; nt = m.node_tree
    out = nt.nodes["Material Output"]; nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission"); grad = nt.nodes.new("ShaderNodeTexGradient"); grad.gradient_type = "SPHERICAL"
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    sx, sy = 5.0, 8.0
    mp.inputs["Location"].default_value = (-0.5 * sx - glow[0] / 60 * sx, -0.47 * sy - glow[1] / 60 * sy, 0); mp.inputs["Scale"].default_value = (sx, sy, 1)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*srgb_to_lin((0.075, 0.11, 0.18)), 1); ramp.color_ramp.elements[1].color = (*srgb_to_lin((0.40, 0.27, 0.13)), 1)
    ramp.color_ramp.elements[0].position = 0.15; ramp.color_ramp.elements[1].position = 1.0; ramp.color_ramp.interpolation = "EASE"
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.0; nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, y, 4)); b = bpy.context.object
    b.rotation_euler = (math.radians(90), 0, 0); b.data.materials.append(m); return b

def area_light(loc, rot, energy, color=(1, 1, 1), size=4):
    l = bpy.data.lights.new("A", "AREA"); l.energy = energy; l.color = color; l.size = size
    o = bpy.data.objects.new("A", l); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = tuple(math.radians(a) for a in rot); return o

def dust(n=140, spread=(14, 18, 6), seed=3):
    random.seed(seed); m = mat("dust", (1, 0.9, 0.7), emit=6.0)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.012); base = bpy.context.object; base.data.materials.append(m)
    for i in range(n):
        o = base.copy(); bpy.context.collection.objects.link(o)
        o.location = (random.uniform(-spread[0], spread[0]), random.uniform(-4, spread[1]), random.uniform(-0.5, spread[2]))
        s = random.uniform(0.5, 2.2); o.scale = (s, s, s)
    base.hide_render = True

def camera(focus_obj=None, fstop=2.0, lens=40):
    c = bpy.data.cameras.new("C"); c.lens = lens
    o = bpy.data.objects.new("C", c); bpy.context.collection.objects.link(o); bpy.context.scene.camera = o
    if focus_obj is not None:
        c.dof.use_dof = True; c.dof.focus_object = focus_obj; c.dof.aperture_fstop = fstop
    return o

def look_at(cam, target):
    d = Vector(target) - cam.location; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def key_path(cam, keys, target_fn):
    """keys: list of (frame, (x,y,z)); camera rotation re-aimed at target each key; Bezier easing."""
    for f, pos in keys:
        cam.location = pos; look_at(cam, target_fn(f))
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)

def shot_number():
    frames = int(PARAMS.get("dur", 4.0) * FPS); reset(frames)
    gold = mat("gold", ACCENT, metallic=1.0, rough=0.22, emit=0.35)
    num = text(PARAMS.get("value", "1,34 MIL."), size=1.45, extrude=0.26, bevel=0.035, material=gold, loc=(0, 0, 0.45))
    text(PARAMS.get("label", "ODBĚRATELŮ"), size=0.42, extrude=0.04, bevel=0.006, material=mat("w", (0.96, 0.94, 0.9), emit=1.6), loc=(0, 0, -0.62))
    floor(); dust(); backdrop()
    area_light((-4, -4, 5), (50, 0, -40), 900, (1, 0.85, 0.7), 5)
    area_light((5, -2, 2), (70, 0, 60), 500, (0.55, 0.7, 1), 3)
    rim = area_light((0, 4, 3), (-60, 0, 180), 1200, (1, 0.8, 0.5), 6)
    cam = camera(num, fstop=2.4, lens=35)
    key_path(cam, [(1, (-4.6, -6.0, 0.3)), (frames, (0.4, -7.4, 0.7))], lambda f: (0, 0, 0.1))
    for o in (cam,):
        for fc in (o.animation_data.action.fcurves if o.animation_data and hasattr(o.animation_data.action, "fcurves") else []):
            for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"
    return frames

def shot_timeline():
    cards = PARAMS["cards"]; per = PARAMS.get("per_card", 2.0)
    frames = int(per * len(cards) * FPS + FPS); reset(frames)
    floor(-1.6); dust(220, (10, 6 * len(cards) + 10, 6)); backdrop(y=7.0 * len(cards) + 6, glow=(0, 1.0))
    glow = mat("glow", ACCENT, emit=9.0)
    pts = []
    for i, c in enumerate(cards):
        x = -2.6 if i % 2 == 0 else 2.6; y = i * 7.0
        m, img = image_mat(c["image"]); aspect = img.size[0] / img.size[1]
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 0.4))
        pl = bpy.context.object; pl.scale = (2.3 * aspect, 2.3, 1)
        pl.rotation_euler = (math.radians(90), 0, math.radians(-14 if x < 0 else 14)); pl.data.materials.append(m)
        text(c["label"], size=0.42, extrude=0.08, bevel=0.01, material=mat(f"hl{i}", ACCENT, metallic=0.8, rough=0.25, emit=0.9) if i == PARAMS.get("highlight", -1) else mat(f"y{i}", (0.96, 0.94, 0.9), emit=1.5),
             loc=(x, y, 0.4 + 1.15 + 0.45))
        pts.append((x * 0.35, y, -1.55))
    # glowing path on the floor
    cu = bpy.data.curves.new("path", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.035
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
    po = bpy.data.objects.new("path", cu); bpy.context.collection.objects.link(po); po.data.materials.append(glow)
    area_light((0, -6, 6), (55, 0, 0), 1500, (1, 0.9, 0.8), 8)
    # Camera aims at a moving target (card centre incl. its label) and stops far enough away that the whole
    # card + label fits the frame with margin (lens 32: half-height ≈ 0.32·d, card+label spans z −0.75..2.25 → d ≥ 4.8;
    # 6+ keeps the source line at the card's bottom edge clear of the frame).
    # Each card: travel 45 % of `per`, then a slow drift-in hold; the last card holds until the final frame.
    tgt = bpy.data.objects.new("tgt", None); bpy.context.collection.objects.link(tgt)
    cam = camera(None, lens=32)
    tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt; cam.data.dof.aperture_fstop = 2.4
    fr = lambda t: max(1, min(frames, 1 + round(t * FPS)))
    def key(t, cpos, tpos):
        f = fr(t); cam.location = cpos; tgt.location = tpos
        cam.keyframe_insert("location", frame=f); tgt.keyframe_insert("location", frame=f)
    key(0, (0, -11.0, 1.6), (0, 3.0, 0.7))                       # wide establishing view
    total = frames / FPS
    for i in range(len(cards)):
        x, y = (-2.6 if i % 2 == 0 else 2.6), i * 7.0
        centre = (x, y, 0.65)
        last = i == len(cards) - 1
        s, e = i * per + 0.45 * per, (total if last else (i + 1) * per)
        d0, d1 = (6.5, 5.9) if last else (6.5, 6.1)
        key(s, (x * 0.45, y - d0, 0.95), centre)
        key(e, (x * 0.45, y - d1, 0.9), centre)
    for o in (cam, tgt):
        for fc in o.animation_data.action.fcurves if hasattr(o.animation_data.action, "fcurves") else []:
            for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"
    return frames

def shot_question():
    frames = int(PARAMS.get("dur", 4.0) * FPS); reset(frames)
    white = mat("w", (0.96, 0.94, 0.9), metallic=0.3, rough=0.3, emit=0.6)
    gold = mat("g", ACCENT, metallic=1.0, rough=0.2, emit=0.6)
    a = text(PARAMS.get("line1", "SKEČ,"), size=0.95, extrude=0.2, bevel=0.025, material=white, loc=(0, 0, 0.9))
    text(PARAMS.get("line2", "NEBO ZPOVĚĎ?"), size=0.95, extrude=0.2, bevel=0.025, material=gold, loc=(0, 0, -0.45))
    floor(-1.4); dust(); backdrop(glow=(0, 0.6))
    sweep = area_light((-6, -3, 2), (80, 0, -60), 1800, (1, 0.9, 0.75), 2)
    sweep.keyframe_insert("location", frame=1); sweep.location = (6, -3, 2); sweep.keyframe_insert("location", frame=frames)
    area_light((0, 5, 4), (-55, 0, 180), 900, (0.5, 0.65, 1), 6)
    cam = camera(a, fstop=2.0, lens=38)
    key_path(cam, [(1, (4.5, -7.5, -0.6)), (frames, (-2.2, -8.6, 0.6))], lambda f: (0, 0, 0.15))
    return frames

frames = {"number": shot_number, "timeline": shot_timeline, "question": shot_question}[SHOT]()
os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)
bpy.ops.render.render(animation=True)
print(f"RENDERED {SHOT} {frames} frames -> {OUT}")
