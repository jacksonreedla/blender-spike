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
    return cam


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


def ground(size=80.0, color=(0.03, 0.033, 0.04), rough=0.35):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    p = bpy.context.object
    p.data.materials.append(material("Ground", color, rough))
    return p


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
        v = nt.nodes.new("ShaderNodeVolumeScatter")
        v.inputs["Density"].default_value = fog
        v.inputs["Anisotropy"].default_value = anisotropy
        nt.links.new(v.outputs["Volume"], out.inputs["Volume"])
    return w


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# --- end preamble -------------------------------------------------------------

# --- generated ---
sc = reset()
world(color=(0.02,0.02,0.03), strength=0.4, fog=0.02, anisotropy=0.4)
ground(size=80, color=(0.05,0.05,0.06), rough=0.5)

# Museum hall: back wall and side walls
box(size=(14,0.6,6), at=(0,6), color=(0.08,0.08,0.09), rough=0.8)
box(size=(0.6,12,6), at=(-7,0), color=(0.07,0.07,0.08), rough=0.8)
box(size=(0.6,12,6), at=(7,0), color=(0.07,0.07,0.08), rough=0.8)

# Stone plinth for the bust
box(size=(0.9,0.9,1.1), at=(0,0), color=(0.18,0.17,0.16), rough=0.85)

# The marble bust on top of the plinth
root = place("marble_bust_01", at=(0,0))
root.location.z = 1.1

# Key spotlight from above
light("SPOT", location=(0.5,-1.5,4.5), at=(0,0,1.4), energy=2500, color=(1.0,0.95,0.85), spot_size=0.5)

# Dim fill from the side
light("AREA", location=(-2.5,2.0,2.0), at=(0,0,1.3), energy=80, size=2.0, color=(0.6,0.65,0.8))

# Camera framing the bust
camera(location=(0, -4.0, 1.6), at=(0,0,1.3), lens=50)

render("/home/apollo/blender-spike/out/shots_assets/shot_05.png")