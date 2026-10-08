# --- preamble: prepended verbatim to every LLM-generated shot script ----------
# Every helper here exists because the first spike measured the model getting
# that exact thing wrong: objects floating (origin is not the base), lights
# aimed by guessed eulers into the void, cameras framing nothing, and geometry
# assembled from parts that do not touch. The model calls these; it does not
# re-derive them.
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

_MANIFEST = json.loads(Path("/home/apollo/blender-spike/assets/models/manifest.json").read_text())
_TEXTURES = json.loads(Path("/home/apollo/blender-spike/assets/textures/manifest.json").read_text())
_SIGHTLINE_TARGET = None


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.image_settings.file_format = "PNG"
    sc.eevee.taa_render_samples = 32
    sc.eevee.use_shadows = True
    return sc


def _link(obj):
    bpy.context.collection.objects.link(obj)
    return obj


def place(name, at=(0.0, 0.0), rot_deg=0.0, scale=1.0):
    """Import a library model so that its BASE rests on the ground at (x, y).

    Returns the parent empty. The manifest's measured base_z is subtracted, so
    a model whose origin is at its centre still lands with its feet on z=0.
    """
    m = _MANIFEST[name]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=m["path"])
    new = [o for o in bpy.data.objects if o not in before]
    root = _link(bpy.data.objects.new(f"{name}_root", None))
    for o in new:
        if o.parent is None:
            o.parent = root
    cx, cy = m["centre_xy"]
    root.location = (-cx * scale, -cy * scale, -m["base_z"] * scale)
    root.rotation_euler = (0, 0, math.radians(rot_deg))
    root.scale = (scale, scale, scale)
    # shift the whole group so its measured centre sits at `at`
    root.location.x += at[0]
    root.location.y += at[1]
    return root


def aim(obj, at):
    """Point a light or camera at a world position. Never guess eulers."""
    t = _link(bpy.data.objects.new(f"{obj.name}_aim", None))
    t.location = at
    c = obj.constraints.new("TRACK_TO")
    c.target = t
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    return t


def camera(location, at, lens=50):
    cd = bpy.data.cameras.new("Cam")
    cd.lens = lens
    cam = _link(bpy.data.objects.new("Cam", cd))
    cam.location = location
    aim(cam, at)
    bpy.context.scene.camera = cam
    global _SIGHTLINE_TARGET
    _SIGHTLINE_TARGET = Vector(at)
    return cam


def check_sightline():
    """Refuse to render a frame whose subject is hidden behind something.

    The first asset run produced a frame that was half solid black: the model
    built a wall between the camera and the chair. A wall in front of the lens
    is invisible in the script and obvious in the render, so it is checked here,
    where the geometry is final, and turned into an error the model can act on.
    """
    sc = bpy.context.scene
    cam = sc.camera
    if cam is None or _SIGHTLINE_TARGET is None:
        return
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    origin = cam.matrix_world.translation
    to_target = _SIGHTLINE_TARGET - origin
    dist = to_target.length
    hit, loc, _n, _i, obj, _m = sc.ray_cast(dg, origin, to_target.normalized(), distance=dist)
    if hit and (loc - _SIGHTLINE_TARGET).length > 0.6 and (loc - origin).length < 0.85 * dist:
        raise RuntimeError(
            f"SIGHTLINE BLOCKED: '{obj.name}' sits {(loc - origin).length:.1f} m in front of the "
            f"camera, between it and the subject {dist:.1f} m away. Move the camera, or move/"
            f"remove '{obj.name}'. Nothing may stand between camera and subject.")


def light(kind, location, at, energy, size=1.0, color=(1, 1, 1), spot_size=1.0):
    """kind: 'SPOT' | 'AREA' | 'POINT' | 'SUN'. Aimed at `at`."""
    ld = bpy.data.lights.new(kind.lower(), type=kind)
    ld.energy = energy
    ld.color = color
    if kind == "AREA":
        ld.size = size
    if kind == "SPOT":
        ld.spot_size = spot_size
        ld.spot_blend = 0.4
        ld.shadow_soft_size = size
    if kind == "POINT":
        ld.shadow_soft_size = size
    lo = _link(bpy.data.objects.new(kind.lower(), ld))
    lo.location = location
    aim(lo, at)
    return lo


def lamp(at=(2.0, 0.0), toward=(0.0, 1.5), energy=1600, color=(1.0, 0.8, 0.55), rot_deg=0.0):
    """A street lamp WITH its light, correctly placed.

    A point light put at the lamp head sits inside the lamp's own mesh and the
    housing shadows it - the frame goes black while the script looks right.
    The bulb here is offset 0.5 m out of the head toward the subject and 0.7 m
    down, where the real lamp's light actually leaves the housing.
    """
    root = place("street_lamp_01", at=at, rot_deg=rot_deg)
    dx, dy = toward[0] - at[0], toward[1] - at[1]
    n = math.hypot(dx, dy) or 1.0
    bulb = (at[0] + 0.5 * dx / n, at[1] + 0.5 * dy / n, 3.15)
    light("POINT", bulb, (toward[0], toward[1], 1.0), energy, size=0.3, color=color)
    return root


def ground(size=80.0, color=(0.03, 0.033, 0.04), rough=0.35, texture=None, scale=6.0, wet=0.0):
    """Floor at z=0. `texture` names a library PBR set and replaces the flat
    colour with real cobbles / cracked mud / sand / rock. `scale` = how many
    metres one texture tile covers (bigger = coarser). `wet` 0..1 lowers
    roughness so lights reflect off the floor, which is the "wet street" look."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    p = bpy.context.object
    if texture and texture in _TEXTURES:
        p.data.materials.append(pbr_material(f"Ground_{texture}", texture, size / scale, wet))
    else:
        p.data.materials.append(material("Ground", color, rough))
    return p


def pbr_material(name, texture, tiles=10.0, wet=0.0):
    """Principled material from a library texture set (diffuse / roughness / normal)."""
    t = _TEXTURES[texture]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapn = nt.nodes.new("ShaderNodeMapping")
    mapn.inputs["Scale"].default_value = (tiles, tiles, tiles)
    nt.links.new(coord.outputs["UV"], mapn.inputs["Vector"])

    def img(path, colorspace):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = colorspace
        nt.links.new(mapn.outputs["Vector"], n.inputs["Vector"])
        return n

    if t.get("diff"):
        nt.links.new(img(t["diff"], "sRGB").outputs["Color"], b.inputs["Base Color"])
    if t.get("rough"):
        r = img(t["rough"], "Non-Color")
        if wet:
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            mul.inputs[1].default_value = max(0.05, 1.0 - 0.8 * wet)
            nt.links.new(r.outputs["Color"], mul.inputs[0])
            nt.links.new(mul.outputs["Value"], b.inputs["Roughness"])
        else:
            nt.links.new(r.outputs["Color"], b.inputs["Roughness"])
    else:
        b.inputs["Roughness"].default_value = max(0.1, 0.75 - 0.6 * wet)
    if t.get("nor"):
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = 1.0
        nt.links.new(img(t["nor"], "Non-Color").outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def material(name, color, rough=0.6, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


def box(size, at, color=(0.2, 0.2, 0.22), rough=0.7, rot_deg=0.0):
    """Environment geometry only (walls, pillars, slabs). Rests on the ground."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(at[0], at[1], size[2] / 2))
    o = bpy.context.object
    o.scale = size
    o.rotation_euler = (0, 0, math.radians(rot_deg))
    o.data.materials.append(material("Box", color, rough))
    return o


def world(color=(0.01, 0.012, 0.02), strength=1.0, hdri=None, fog=0.015, anisotropy=0.4):
    """Dark sky by default; optional HDRI; volumetric fog on by default."""
    w = bpy.data.worlds.new("W")
    w.use_nodes = True
    bpy.context.scene.world = w
    nt = w.node_tree
    bg = nt.nodes["Background"]
    out = nt.nodes["World Output"]
    if hdri:
        env = nt.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(hdri)
        nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    else:
        bg.inputs["Color"].default_value = (*color, 1)
    bg.inputs["Strength"].default_value = strength
    if fog:
        if fog > 0.03:
            # 0.055 over a 9 m sightline rendered as a near-black frame. Fog
            # is exponential in distance; past this it swallows the subject.
            print(f"WARNING fog={fog} clamped to 0.03 (0.005-0.012 for >6 m sightlines)")
            fog = 0.03
        v = nt.nodes.new("ShaderNodeVolumeScatter")
        v.inputs["Density"].default_value = fog
        v.inputs["Anisotropy"].default_value = anisotropy
        nt.links.new(v.outputs["Volume"], out.inputs["Volume"])
    return w


def render(path):
    check_sightline()
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# --- end preamble -------------------------------------------------------------

# --- generated ---
import math
sc = reset()
world(color=(0.02,0.025,0.035), strength=0.45, fog=0.02, anisotropy=0.5)

# Cave floor
ground(size=60, texture="aerial_rocks_02", scale=4.0, color=(0.35,0.33,0.30))

# --- Build the cave: rock faces stacked and rotated into walls and ceiling ---
# Back wall behind camera (so camera is enclosed)
place("rock_face_01", at=(-1.0, 6.5), rot_deg=180)
place("rock_face_02", at=(3.0, 6.0), rot_deg=200)
place("rock_face_01", at=(-5.0, 5.5), rot_deg=160)

# Left wall of the cave
place("rock_face_01", at=(-5.5, 2.0), rot_deg=90)
place("rock_face_02", at=(-5.0, -1.0), rot_deg=90)
place("rock_face_01", at=(-5.5, -4.0), rot_deg=90)

# Right wall of the cave
place("rock_face_01", at=(5.5, 2.0), rot_deg=-90)
place("rock_face_02", at=(5.0, -1.0), rot_deg=-90)
place("rock_face_01", at=(5.5, -4.0), rot_deg=-90)

# Ceiling rocks (stacked above, rotated to overhang)
place("rock_face_01", at=(-2.0, 3.0), rot_deg=0)
place("rock_face_02", at=(2.0, 3.5), rot_deg=0)
place("rock_face_01", at=(0.0, 5.0), rot_deg=0)

# Cave mouth framing rocks - left and right of the opening, NOT in front of subject
place("rock_face_01", at=(-4.5, -6.5), rot_deg=45)
place("rock_face_02", at=(-3.0, -7.0), rot_deg=30)
place("rock_face_01", at=(4.5, -6.5), rot_deg=-45)
place("rock_face_02", at=(3.0, -7.0), rot_deg=-30)

# Low boulders as ground dressing at the sides
place("namaqualand_boulder_02", at=(-3.5, -3.0))
place("namaqualand_boulder_02", at=(3.8, -2.5))
place("boulder_01", at=(-2.8, 1.5))
place("boulder_01", at=(3.2, 1.0))

# --- The lone figure: full-body gothic statue standing in the opening ---
place("gothic_statue", at=(0.0, -3.5))

# --- Light pouring in from BEHIND the figure (outside the cave mouth) ---
# Strong sun/area light outside the mouth, behind the figure
light("AREA", location=(0.0, -12.0, 5.0), at=(0.0, -3.5, 1.0), energy=6000, size=8.0, color=(1.0, 0.95, 0.85))
# Additional spot from outside for rim light
light("SPOT", location=(0.0, -10.0, 4.0), at=(0.0, -3.5, 1.2), energy=4000, spot_size=1.2, color=(1.0, 0.93, 0.80))

# Dim fill from inside the cave so the rock walls have some detail
light("AREA", location=(-3.0, 4.0, 3.0), at=(0.0, -1.0, 1.0), energy=120, size=4.0, color=(0.5, 0.55, 0.7))
light("AREA", location=(3.5, 3.0, 2.5), at=(0.0, -1.0, 1.0), energy=80, size=3.0, color=(0.5, 0.55, 0.7))

# --- Camera inside the cave, looking out toward the opening ---
camera(location=(0.0, 4.5, 1.6), at=(0.0, -3.5, 1.0), lens=35)

render("/home/apollo/blender-spike/out/shots_assets/shot_01_a2.png")