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
        for attr, val in (("taa_render_samples", PARAMS.get("samples", 48)), ("use_raytracing", PARAMS.get("raytracing", True)), ("use_shadows", True)):
            try: setattr(ee, attr, val)
            except Exception: pass
    try: sc.render.use_motion_blur = PARAMS.get("motion_blur", True); sc.render.motion_blur_shutter = 0.4
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

# ---------- helpers for prop shots ----------
def noise_mat(name, c1, c2, scale=8.0, rough=0.6, bump=0.15, sss=0.0):
    """Principled BSDF with colour mixed by noise (crumb, sand, fabric) and a matching bump."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = 8
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = (*srgb_to_lin(c1), 1); r.color_ramp.elements[1].color = (*srgb_to_lin(c2), 1)
    nt.links.new(n.outputs["Fac"], r.inputs["Fac"]); nt.links.new(r.outputs["Color"], p.inputs["Base Color"])
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = bump
    nt.links.new(n.outputs["Fac"], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    if sss and "Subsurface Weight" in p.inputs: p.inputs["Subsurface Weight"].default_value = sss
    return m

def box(size, loc, material, bevel=0.0, segs=3, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object
    o.scale = size; o.rotation_euler = tuple(math.radians(a) for a in rot)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        m = o.modifiers.new("bv", "BEVEL"); m.width = bevel; m.segments = segs; m.limit_method = "NONE"
    o.data.materials.append(material)
    for f in o.data.polygons: f.use_smooth = True
    return o

def ease_all(*objs):
    for o in objs:
        ad = o.animation_data
        if not ad or not ad.action: continue
        for fc in getattr(ad.action, "fcurves", []):
            for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"

def sun(rot, energy, color, angle=2.0):
    l = bpy.data.lights.new("S", "SUN"); l.energy = energy; l.color = color; l.angle = math.radians(angle)
    o = bpy.data.objects.new("S", l); bpy.context.collection.objects.link(o); o.rotation_euler = tuple(math.radians(a) for a in rot); return o

def sky(top, horizon):
    w = bpy.context.scene.world; nt = w.node_tree; bgn = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); r = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(tc.outputs["Window"], sep.inputs[0]); nt.links.new(sep.outputs["Y"], r.inputs["Fac"])   # screen-space: fine for level cameras
    r.color_ramp.elements[0].position = 0.45; r.color_ramp.elements[0].color = (*srgb_to_lin(horizon), 1)
    r.color_ramp.elements[1].position = 1.0; r.color_ramp.elements[1].color = (*srgb_to_lin(top), 1); r.color_ramp.interpolation = "EASE"
    nt.links.new(r.outputs["Color"], bgn.inputs["Color"]); bgn.inputs["Strength"].default_value = 1.0

# ---------- Fyre pilot shots ----------
def shot_sandwich():
    """White polystyrene clamshell, two toast slices, cheese slice, a little lettuce; slow push-in, shallow DOF."""
    frames = int(PARAMS.get("dur", 9.3) * FPS); reset(frames)
    foam = noise_mat("foam", (0.72, 0.72, 0.70), (0.80, 0.80, 0.78), scale=90, rough=0.75, bump=0.05)
    tray = box((3.2, 2.4, 0.5), (0, 0, 0.25), foam, bevel=0.12)
    cut = box((2.9, 2.1, 0.5), (0, 0, 0.56), foam)                       # hollow out the tray (wall 0.15, floor 0.06)
    bo = tray.modifiers.new("hollow", "BOOLEAN"); bo.object = cut; bo.operation = "DIFFERENCE"; cut.hide_render = True; cut.hide_viewport = True
    tray.modifiers.move(tray.modifiers.find("hollow"), 0)
    lid = box((3.2, 2.4, 0.42), (0, -1.2, 0.21), foam, bevel=0.12)       # built closed on top of the tray, relative to the hinge
    lcut = box((2.9, 2.1, 0.42), (0, -1.2, 0.06), foam)
    bl = lid.modifiers.new("hollow", "BOOLEAN"); bl.object = lcut; bl.operation = "DIFFERENCE"; lcut.hide_render = True; lcut.hide_viewport = True
    lid.modifiers.move(lid.modifiers.find("hollow"), 0)
    hinge = bpy.data.objects.new("hinge", None); bpy.context.collection.objects.link(hinge); hinge.location = (0, 1.2, 0.5)
    lid.parent = hinge; lcut.parent = hinge; hinge.rotation_euler = (math.radians(-100), 0, 0)   # opened, leaning back 10°
    toast = noise_mat("toast", (0.80, 0.62, 0.38), (0.95, 0.86, 0.66), scale=28, rough=0.85, bump=0.35)
    b1 = box((1.15, 1.2, 0.16), (-0.66, -0.05, 0.40), toast, bevel=0.14, segs=4, rot=(0, 0, 6))
    b2 = box((1.15, 1.2, 0.16), (0.62, 0.0, 0.40), toast, bevel=0.14, segs=4, rot=(0, 0, -4))
    cheese = mat("cheese", (0.98, 0.70, 0.18), rough=0.35)
    if "Subsurface Weight" in cheese.node_tree.nodes["Principled BSDF"].inputs:
        cheese.node_tree.nodes["Principled BSDF"].inputs["Subsurface Weight"].default_value = 0.4
    ch = box((1.05, 1.05, 0.025), (0.62, 0.0, 0.50), cheese, bevel=0.01, rot=(0, 0, 38))
    leaf = noise_mat("leaf", (0.30, 0.55, 0.16), (0.62, 0.82, 0.36), scale=12, rough=0.45, bump=0.4)
    random.seed(5)
    for i in range(9):
        bpy.ops.mesh.primitive_plane_add(size=0.34, location=(-1.0 + random.uniform(-0.2, 0.2), -0.72 + random.uniform(-0.12, 0.12), 0.36 + i * 0.03))
        lf = bpy.context.object; lf.rotation_euler = (math.radians(random.uniform(-55, 55)), math.radians(random.uniform(-55, 55)), random.uniform(0, 6.28))
        sub = lf.modifiers.new("s", "SUBSURF"); sub.levels = 4; sub.render_levels = 4; sub.subdivision_type = "SIMPLE"
        tex = bpy.data.textures.new(f"crinkle{i}", "CLOUDS"); tex.noise_scale = 0.09
        d = lf.modifiers.new("d", "DISPLACE"); d.texture = tex; d.strength = 0.14
        lf.modifiers.new("sm", "SUBSURF").render_levels = 1
        lf.data.materials.append(leaf)
    table = noise_mat("table", (0.10, 0.08, 0.07), (0.20, 0.15, 0.11), scale=3, rough=0.5, bump=0.05)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0)); bpy.context.object.data.materials.append(table)
    backdrop(y=10, glow=(0, 0.8))
    area_light((-3.5, -3.0, 4.5), (40, 0, -45), 420, (1.0, 0.88, 0.72), 3)   # warm key
    area_light((4.0, -1.5, 2.5), (65, 0, 65), 260, (0.6, 0.72, 1.0), 4)     # cool fill
    area_light((0, 4.5, 3.5), (-55, 0, 180), 600, (1.0, 0.8, 0.55), 5)      # rim
    tgt = bpy.data.objects.new("tgt", None); bpy.context.collection.objects.link(tgt); tgt.location = (0.1, 0.0, 0.45)
    cam = camera(tgt, fstop=1.6, lens=50)
    tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    cam.location = (-1.8, -7.2, 4.4); cam.keyframe_insert("location", frame=1)
    cam.location = (-0.5, -4.6, 2.9); cam.keyframe_insert("location", frame=frames)
    ease_all(cam)
    return frames

def shot_tents():
    """Beach at dusk, a row of white relief tents (some unfinished frames), slow dolly along the row, dust."""
    frames = int(PARAMS.get("dur", 8.0) * FPS); reset(frames)
    sky((0.06, 0.09, 0.19), (0.80, 0.50, 0.38))
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0)); sand = bpy.context.object
    sand.data.materials.append(noise_mat("sand", (0.62, 0.56, 0.50), (0.80, 0.74, 0.66), scale=60, rough=0.9, bump=0.3))
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 260, -0.05)); sea = bpy.context.object
    sea.data.materials.append(noise_mat("sea", (0.03, 0.07, 0.13), (0.06, 0.13, 0.22), scale=2, rough=0.35, bump=0.2))
    sea.location = (0, 230, 0.02)
    fabric = noise_mat("fabric", (0.86, 0.86, 0.84), (0.97, 0.97, 0.95), scale=40, rough=0.8, bump=0.1, sss=0.2)
    pole = mat("pole", (0.6, 0.6, 0.62), metallic=0.8, rough=0.35)
    random.seed(11)
    for i in range(12):
        x = -14 + i * 3.4; y = 6 + random.uniform(-0.3, 0.3); unfinished = i in (3, 7, 8)
        if unfinished:
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=1.1, location=(x + dx * 1.2, y + dy * 1.2, 0.55))
                bpy.context.object.data.materials.append(pole)
            bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.72, depth=1.35, location=(x, y, 1.77), rotation=(0, 0, math.radians(45)))
            cn = bpy.context.object; w = cn.modifiers.new("w", "WIREFRAME"); w.thickness = 0.05; cn.data.materials.append(pole)
            if i == 7:   # loose fabric lying on the sand
                bpy.ops.mesh.primitive_plane_add(size=2.6, location=(x + 0.4, y - 1.8, 0.03)); fb = bpy.context.object
                fb.rotation_euler = (0, 0, 0.5); d = fb.modifiers.new("s", "SUBSURF"); d.levels = 3; d.render_levels = 3
                dd = fb.modifiers.new("d", "DISPLACE"); t = bpy.data.textures.new("folds", "CLOUDS"); t.noise_scale = 0.4; dd.texture = t; dd.strength = 0.18
                fb.data.materials.append(fabric)
            continue
        box((2.4, 2.4, 1.1), (x, y, 0.55), fabric, bevel=0.05)
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.72, depth=1.35, location=(x, y, 1.77), rotation=(0, 0, math.radians(45)))
        rf = bpy.context.object; rf.data.materials.append(fabric); bv = rf.modifiers.new("bv", "BEVEL"); bv.width = 0.06; bv.segments = 3
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y - 1.215, 0.5))   # door: dark triangle opening
        dr = bpy.context.object; dr.rotation_euler = (math.radians(90), 0, 0); dr.scale = (0.5, 0.9, 1)
        bm_v = dr.data.vertices; bm_v[2].co.x = 0; bm_v[3].co.x = 0.001   # pinch the top edge into a peak
        dr.data.materials.append(mat(f"door{i}", (0.08, 0.08, 0.09), rough=0.9))
    sun((82, 0, -60), 1.3, (1.0, 0.66, 0.45), 3)
    area_light((0, -8, 6), (50, 0, 0), 1400, (0.55, 0.65, 1.0), 14)
    dust(70, (20, 14, 3), seed=9)
    tgt = bpy.data.objects.new("tgt", None); bpy.context.collection.objects.link(tgt)
    cam = camera(tgt, fstop=2.8, lens=35)
    tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    for f, cp, tp in ((1, (-12, -4.5, 1.5), (-8, 6, 1.1)), (frames, (8, -4.0, 1.7), (12, 6, 1.1))):
        cam.location = cp; tgt.location = tp
        cam.keyframe_insert("location", frame=f); tgt.keyframe_insert("location", frame=f)
    ease_all(cam, tgt)
    return frames

def shot_tickets():
    """Three golden tickets tumble down into view; at ~70 % a red stamp slams on: NEEXISTUJÍ."""
    frames = int(PARAMS.get("dur", 8.0) * FPS); reset(frames)
    gold = mat("gold", ACCENT, metallic=1.0, rough=0.25, emit=0.25)
    ink = mat("ink", (0.10, 0.08, 0.05), rough=0.6)
    labels = PARAMS.get("labels", ["MET GALA", "GRAMMY", "SUPER BOWL"])
    rest = [(-2.9, 0.4, 0.6, 8), (0.1, -0.2, -0.15, -6), (3.0, 0.5, 0.75, 5)]
    random.seed(4); objs = []
    for i, (lab, (x, y, z, rz)) in enumerate(zip(labels, rest)):
        t = box((2.5, 0.025, 1.15), (0, 0, 0), gold, bevel=0.012)
        txt = text(lab, size=0.3, extrude=0.008, bevel=0.0, material=ink, loc=(0, -0.025, 0.08)); txt.parent = t
        txt2 = text("VSTUPENKA", size=0.13, extrude=0.004, bevel=0.0, material=ink, loc=(-0.2, -0.025, -0.33)); txt2.parent = t
        for k in range(9):   # perforated stub line
            dot = box((0.025, 0.01, 0.07), (0.92, -0.016, -0.48 + k * 0.12), ink); dot.parent = t
        txt.location.x = -0.2
        start = 1 + i * 8; land = start + int(2.2 * FPS)
        t.location = (x + random.uniform(-1, 1), y, 6.5 + i); t.rotation_euler = (math.radians(random.uniform(-150, 150)), math.radians(random.uniform(-80, 80)), math.radians(random.uniform(-90, 90)))
        t.keyframe_insert("location", frame=start); t.keyframe_insert("rotation_euler", frame=start)
        t.location = (x, y, z); t.rotation_euler = (math.radians(4), 0, math.radians(rz))
        t.keyframe_insert("location", frame=land); t.keyframe_insert("rotation_euler", frame=land)
        t.location = (x, y, z - 0.08); t.rotation_euler = (math.radians(4), math.radians(2), math.radians(rz + 1.5))
        t.keyframe_insert("location", frame=frames); t.keyframe_insert("rotation_euler", frame=frames)
        objs.append(t)
    red = mat("stamp", (0.82, 0.06, 0.05), rough=0.6, emit=0.45)
    stamp = text(PARAMS.get("stamp", "NEEXISTUJÍ"), size=0.95, extrude=0.03, bevel=0.0, material=red, loc=(0, -1.6, 0.3))
    frame_cu = bpy.data.curves.new("sf", "CURVE"); frame_cu.dimensions = "2D"; frame_cu.bevel_depth = 0.05
    sp = frame_cu.splines.new("POLY"); sp.points.add(3); sp.use_cyclic_u = True
    for pt, (px, py) in zip(sp.points, ((-3.6, -0.75), (3.6, -0.75), (3.6, 0.75), (-3.6, 0.75))): pt.co = (px, py, 0, 1)
    fo = bpy.data.objects.new("sf", frame_cu); bpy.context.collection.objects.link(fo); fo.data.materials.append(red); fo.parent = stamp
    stamp.rotation_euler = (math.radians(90), math.radians(-8), 0)
    hit = int(frames * 0.68)
    stamp.scale = (0, 0, 0); stamp.keyframe_insert("scale", frame=hit - 4)
    stamp.scale = (1.7, 1.7, 1.7); stamp.keyframe_insert("scale", frame=hit - 3)
    stamp.scale = (1.0, 1.0, 1.0); stamp.keyframe_insert("scale", frame=hit)
    stamp.scale = (1.03, 1.03, 1.03); stamp.keyframe_insert("scale", frame=frames)
    floor(-1.2); backdrop(glow=(0, 0.6)); dust()
    area_light((-4, -5, 5), (50, 0, -35), 1000, (1, 0.88, 0.7), 5)
    area_light((5, -3, 2), (70, 0, 60), 450, (0.55, 0.7, 1), 3)
    area_light((0, 4, 4), (-60, 0, 180), 1100, (1, 0.8, 0.5), 6)
    tgt = bpy.data.objects.new("tgt", None); bpy.context.collection.objects.link(tgt); tgt.location = (0, 0, 0.35)
    cam = camera(tgt, fstop=3.2, lens=35)
    tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    cam.location = (-1.0, -10.5, 1.6); cam.keyframe_insert("location", frame=1)
    cam.location = (0.6, -9.2, 1.0); cam.keyframe_insert("location", frame=frames)
    ease_all(cam)
    return frames

def shot_counter():
    """'6 LET' first, then the amount counts up to its final value (text changes per frame via a handler)."""
    frames = int(PARAMS.get("dur", 8.9) * FPS); reset(frames)
    first, first_label = PARAMS.get("first", "6 LET"), PARAMS.get("first_label", "VĚZENÍ")
    final, label = PARAMS.get("value", 26191306), PARAMS.get("label", "NAŘÍZENO VRÁTIT")
    switch, done = int(PARAMS.get("switch", 3.2) * FPS), int(PARAMS.get("done", 7.0) * FPS)
    gold = mat("gold", ACCENT, metallic=1.0, rough=0.22, emit=0.35); white = mat("w", (0.96, 0.94, 0.9), emit=1.6)
    num = text(first, size=1.3, extrude=0.26, bevel=0.035, material=gold, loc=(0, 0, 0.45))
    lab = text(first_label, size=0.42, extrude=0.04, bevel=0.006, material=white, loc=(0, 0, -0.62))
    def fmt(v): return f"{int(v):,}".replace(",", " ") + " $"
    def upd(scene, *_):
        f = scene.frame_current
        if f < switch: num.data.body, lab.data.body, sc = first, first_label, 1.3
        else:
            u = min(1.0, (f - switch) / max(done - switch, 1)); u = 1 - (1 - u) ** 3
            num.data.body, lab.data.body, sc = fmt(round(final * u)), label, 0.95
        num.data.size = sc
    bpy.app.handlers.frame_change_pre.append(upd)
    floor(); dust(); backdrop()
    area_light((-4, -4, 5), (50, 0, -40), 900, (1, 0.85, 0.7), 5)
    area_light((5, -2, 2), (70, 0, 60), 500, (0.55, 0.7, 1), 3)
    area_light((0, 4, 3), (-60, 0, 180), 1200, (1, 0.8, 0.5), 6)
    cam = camera(num, fstop=2.8, lens=35)
    key_path(cam, [(1, (-3.2, -8.2, 0.4)), (switch, (-1.2, -8.6, 0.5)), (frames, (1.4, -9.6, 0.7))], lambda f: (0, 0, 0.1))
    ease_all(cam)
    return frames

def shot_capacity():
    """A small stage and a fenced area; 250 yellow dots fill it, then 1 550 grey dots spill around it. Labels 250 / 1 800."""
    frames = int(PARAMS.get("dur", 9.6) * FPS); reset(frames)
    inside, total = PARAMS.get("inside", 250), PARAMS.get("total", 1800)
    t_in, t_out = int(PARAMS.get("t_in", 0.6) * FPS), int(PARAMS.get("t_out", 4.6) * FPS)
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
    bpy.context.object.data.materials.append(noise_mat("ground", (0.05, 0.07, 0.11), (0.08, 0.10, 0.15), scale=6, rough=0.7, bump=0.05))
    glow = mat("fence", ACCENT, emit=6.0)
    fw, fd = 5.0, 3.2                                                    # fenced area (inside dots), stage at the back
    cu = bpy.data.curves.new("fence", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.03
    sp = cu.splines.new("POLY"); sp.points.add(3); sp.use_cyclic_u = True
    for pt, (x, y) in zip(sp.points, ((-fw / 2, -fd / 2), (fw / 2, -fd / 2), (fw / 2, fd / 2), (-fw / 2, fd / 2))): pt.co = (x, y, 0.03, 1)
    fo = bpy.data.objects.new("fence", cu); bpy.context.collection.objects.link(fo); fo.data.materials.append(glow)
    stage = box((2.6, 0.9, 0.35), (0, fd / 2 + 0.6, 0.175), mat("stage", (0.12, 0.14, 0.2), metallic=0.3, rough=0.4), bevel=0.03)
    box((2.6, 0.06, 1.4), (0, fd / 2 + 1.05, 1.05), mat("screen", (0.2, 0.25, 0.35), emit=0.6))
    yel = mat("dot_in", ACCENT, emit=1.6); grey = mat("dot_out", (0.55, 0.58, 0.64), rough=0.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, segments=10, ring_count=6, location=(0, 0, -5)); base = bpy.context.object
    random.seed(8)
    nx = 25; ny = max(1, inside // nx)
    pts_in = [(-fw / 2 + 0.2 + (fw - 0.4) * (i + 0.5) / nx + random.uniform(-0.03, 0.03), -fd / 2 + 0.2 + (fd - 0.4) * (j + 0.5) / ny + random.uniform(-0.03, 0.03))
              for j in range(ny) for i in range(nx)][:inside]
    pts_out = []
    while len(pts_out) < total - inside:
        x, y = random.uniform(-14, 14), random.uniform(-6.5, 9)
        if -fw / 2 - 0.25 < x < fw / 2 + 0.25 and -fd / 2 - 0.25 < y < fd / 2 + 1.6: continue
        if abs(x) + max(0, -y) * 0.3 < 16: pts_out.append((x, y))
    def drop(o, x, y, f0):
        o.location = (x, y, 4.0); o.keyframe_insert("location", frame=max(1, f0))
        o.location = (x, y, 0.065); o.keyframe_insert("location", frame=max(2, f0 + 10))
    for k, (x, y) in enumerate(pts_in):
        o = base.copy(); bpy.context.collection.objects.link(o)
        o.active_material = yel; drop(o, x, y, t_in + int(k / len(pts_in) * 2.4 * FPS))
    pts_out.sort(key=lambda p: math.hypot(p[0], p[1]))
    for k, (x, y) in enumerate(pts_out):
        o = base.copy(); bpy.context.collection.objects.link(o); o.active_material = grey
        drop(o, x, y, t_out + int(k / len(pts_out) * 3.0 * FPS))
    base.hide_render = True
    white = mat("w", (0.96, 0.94, 0.9), emit=1.6); gold = mat("g", ACCENT, metallic=0.8, rough=0.25, emit=1.0)
    l1 = text(PARAMS.get("label_in", "250"), size=0.9, extrude=0.08, bevel=0.01, material=gold, loc=(0, -0.2, 1.4))
    l2 = text(PARAMS.get("label_total", "1 800"), size=1.2, extrude=0.1, bevel=0.012, material=white, loc=(0, 3.2, 3.2))
    for o, f0 in ((l1, t_in + int(2.4 * FPS)), (l2, t_out + int(2.6 * FPS))):
        o.scale = (0, 0, 0); o.keyframe_insert("scale", frame=f0); o.scale = (1, 1, 1); o.keyframe_insert("scale", frame=f0 + 8)
    l1.rotation_euler = (math.radians(70), 0, 0); l2.rotation_euler = (math.radians(70), 0, 0)
    area_light((0, -6, 8), (40, 0, 0), 1600, (1, 0.92, 0.82), 10)
    area_light((0, 8, 5), (-50, 0, 180), 800, (0.55, 0.65, 1.0), 8)
    tgt = bpy.data.objects.new("tgt", None); bpy.context.collection.objects.link(tgt)
    cam = camera(tgt, fstop=5.6, lens=30)
    tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    for f, cp, tp in ((1, (0, -7.5, 6.0), (0, 0.4, 0.3)), (t_out, (0, -8.5, 7.0), (0, 0.6, 0.3)), (frames, (0, -15.0, 11.5), (0, 1.0, 0.5))):
        cam.location = cp; tgt.location = tp
        cam.keyframe_insert("location", frame=f); tgt.keyframe_insert("location", frame=f)
    ease_all(cam, tgt)
    return frames

def shot_villa_tent():
    """A beach villa breaks apart in ~3 s and leaves an empty white relief tent; room on the right for a number."""
    frames = int(PARAMS.get("dur", 3.9) * FPS); reset(frames)
    sky((0.06, 0.09, 0.19), (0.80, 0.50, 0.38))
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
    bpy.context.object.data.materials.append(noise_mat("sand", (0.62, 0.56, 0.50), (0.80, 0.74, 0.66), scale=60, rough=0.9, bump=0.3))
    wall = mat("wall", (0.93, 0.90, 0.84), rough=0.5); glass = mat("glass", (0.35, 0.55, 0.7), metallic=0.2, rough=0.05, emit=0.4, emit_color=(1, 0.8, 0.5))
    wood = mat("wood", (0.42, 0.28, 0.18), rough=0.6); pool = mat("pool", (0.1, 0.55, 0.75), rough=0.05, emit=0.6)
    parts = [box((5.0, 3.2, 1.4), (-1.5, 2.0, 0.7), wall, bevel=0.04), box((3.6, 2.6, 1.2), (-2.0, 2.2, 2.0), wall, bevel=0.04),
             box((5.4, 3.6, 0.12), (-1.5, 2.0, 1.46), wood), box((4.0, 3.0, 0.12), (-2.0, 2.2, 2.66), wood),
             box((4.2, 0.05, 0.9), (-1.5, 0.38, 0.75), glass), box((3.0, 0.05, 0.8), (-2.0, 0.88, 2.0), glass),
             box((3.0, 1.6, 0.06), (1.6, 0.2, 0.03), pool)]
    t0, t1 = int(0.6 * FPS), int(PARAMS.get("collapse", 3.0) * FPS)
    random.seed(3)
    for o in parts:
        o.keyframe_insert("location", frame=t0); o.keyframe_insert("rotation_euler", frame=t0); o.keyframe_insert("scale", frame=t0)
        o.location = (o.location.x + random.uniform(-2, 2), o.location.y + random.uniform(1, 4), o.location.z + random.uniform(1.5, 4))
        o.rotation_euler = (random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5))
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("location", frame=t1); o.keyframe_insert("rotation_euler", frame=t1); o.keyframe_insert("scale", frame=t1)
    fabric = noise_mat("fabric", (0.86, 0.86, 0.84), (0.97, 0.97, 0.95), scale=40, rough=0.8, bump=0.1, sss=0.2)
    tent = bpy.data.objects.new("tent", None); bpy.context.collection.objects.link(tent); tent.location = (-1.6, 2.0, 0)
    tb = box((2.4, 2.4, 1.1), (0, 0, 0.55), fabric, bevel=0.05); tb.parent = tent
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.72, depth=1.35, location=(0, 0, 1.77), rotation=(0, 0, math.radians(45)))
    rf = bpy.context.object; rf.data.materials.append(fabric); rf.parent = tent
    tent.scale = (0.001, 0.001, 0.001); tent.keyframe_insert("scale", frame=int(t1 * 0.75))
    tent.scale = (1.15, 1.15, 0.9); tent.keyframe_insert("scale", frame=t1 + 3)
    tent.scale = (1, 1, 1); tent.keyframe_insert("scale", frame=t1 + 8)
    sun((80, 0, -60), 1.4, (1.0, 0.66, 0.45), 3)
    area_light((0, -8, 6), (50, 0, 0), 1400, (0.55, 0.65, 1.0), 14)
    dust(70, (14, 10, 3), seed=4)
    cam = camera(None, lens=35); tgt = bpy.data.objects.new("tgt", None); bpy.context.collection.objects.link(tgt); tgt.location = (0.6, 2.0, 1.1)
    tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    cam.location = (-2.0, -9.0, 2.2); cam.keyframe_insert("location", frame=1)
    cam.location = (-0.6, -8.0, 1.8); cam.keyframe_insert("location", frame=frames)
    ease_all(cam)
    return frames

frames = {"number": shot_number, "timeline": shot_timeline, "question": shot_question,
          "sandwich": shot_sandwich, "tents": shot_tents, "tickets": shot_tickets,
          "counter": shot_counter, "capacity": shot_capacity, "villa_tent": shot_villa_tent}[SHOT]()
os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)
if PARAMS.get("still_frame"):  # quick look at one frame
    sc = bpy.context.scene; sc.frame_set(min(PARAMS["still_frame"], frames)); sc.render.filepath = os.path.join(OUT, "frames", "still.png")
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print(f"RENDERED {SHOT} {frames} frames -> {OUT}")
