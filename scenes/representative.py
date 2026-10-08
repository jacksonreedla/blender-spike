"""Gate 2: the shot we would actually ship, benchmarked honestly.

Not a stress test and not a toy - this is the style the plan says is reachable:
a large dark space, volumetric light, a lone silhouetted figure, a slow dolly.
Volumetrics and soft shadows are what actually cost time in EEVEE, so a
benchmark without them would flatter the box and mislead the decision.

The HDRI is optional on purpose: gate 2 must not be blocked on gate 3, and a
procedural sky costs about the same to render as an image-based one.

    blender -b -P scenes/representative.py -- <frames> <outdir>
"""
import os
import sys
import time

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
FRAMES = int(argv[0]) if argv else 5
OUTDIR = argv[1] if len(argv) > 1 else "/home/apollo/blender-spike/out/rep"
HDRI = os.environ.get("SPIKE_HDRI", "")
W, H = 1080, 1920
SAMPLES = 32


def world():
    w = bpy.data.worlds.new("W")
    w.use_nodes = True
    bpy.context.scene.world = w
    nt = w.node_tree
    out = nt.nodes["World Output"]
    bg = nt.nodes["Background"]
    if HDRI and os.path.exists(HDRI):
        env = nt.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(HDRI)
        nt.links.new(env.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = 0.6
    else:
        grad = nt.nodes.new("ShaderNodeTexGradient")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.01, 0.012, 0.02, 1)
        ramp.color_ramp.elements[1].color = (0.05, 0.06, 0.09, 1)
        tex = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tex.outputs["Generated"], grad.inputs["Vector"])
        nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def fog():
    """A world volume: the single most expensive thing in this style, and the
    thing that makes a bare scene read as cinematic."""
    w = bpy.context.scene.world
    nt = w.node_tree
    vol = nt.nodes.new("ShaderNodeVolumeScatter")
    vol.inputs["Density"].default_value = 0.018
    vol.inputs["Anisotropy"].default_value = 0.4
    nt.links.new(vol.outputs["Volume"], nt.nodes["World Output"].inputs["Volume"])


def figure():
    """A stand-in for a rigged character: correct silhouette scale and mass, so
    the shadow and volumetric cost are honest. Gate 3 swaps in a real Mixamo rig."""
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=1.75, location=(0.6, 1.5, 0.875))
    body = bpy.context.object
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(0.6, 1.5, 1.88))
    mat = bpy.data.materials.new("Dark")
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.02, 0.02, 0.025, 1)
    b.inputs["Roughness"].default_value = 0.8
    for o in (body, bpy.context.object):
        o.data.materials.append(mat)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.image_settings.file_format = "PNG"
    scene.eevee.taa_render_samples = SAMPLES
    scene.eevee.use_shadows = True
    if hasattr(scene.eevee, "use_raytracing"):
        scene.eevee.use_raytracing = True

    world()
    fog()

    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
    floor = bpy.context.object
    fm = bpy.data.materials.new("Floor")
    fm.use_nodes = True
    fb = fm.node_tree.nodes["Principled BSDF"]
    fb.inputs["Base Color"].default_value = (0.03, 0.033, 0.04, 1)
    fb.inputs["Roughness"].default_value = 0.25
    floor.data.materials.append(fm)

    figure()

    # one hard key behind the figure: the shaft of light this style lives on.
    # A spot points down its own -Z, so it is AIMED with a Track To constraint
    # rather than by guessing an euler - guessing produced a black frame that
    # still cost full render time, which is the worst kind of bug to benchmark.
    target = bpy.data.objects.new("Aim", None)
    target.location = (0.6, 1.5, 1.0)
    bpy.context.collection.objects.link(target)

    ld = bpy.data.lights.new("Key", type="SPOT")
    ld.energy = 15000
    ld.spot_size = 1.1
    ld.spot_blend = 0.35
    ld.shadow_soft_size = 0.25
    key = bpy.data.objects.new("Key", ld)
    key.location = (0.6, 8.5, 6.5)
    bpy.context.collection.objects.link(key)
    con = key.constraints.new("TRACK_TO")
    con.target = target

    # a dim fill so the figure reads as a silhouette rather than a hole
    fd = bpy.data.lights.new("Fill", type="AREA")
    fd.energy = 60
    fd.size = 10
    fill = bpy.data.objects.new("Fill", fd)
    fill.location = (-6, -5, 4)
    bpy.context.collection.objects.link(fill)
    fcon = fill.constraints.new("TRACK_TO")
    fcon.target = target

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("Cam", cam_data)
    cam.location = (0, -7.5, 1.7)
    cam.rotation_euler = (1.52, 0, 0)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam

    # slow dolly - the camera move is part of the cost (motion changes what the
    # volume integrator sees each frame)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0, -6.0, 1.9)
    cam.keyframe_insert("location", frame=90)

    scene.frame_start, scene.frame_end = 1, FRAMES
    scene.render.filepath = OUTDIR + "/f_"


build()
t0 = time.time()
bpy.ops.render.render(animation=True)
el = time.time() - t0
print(f"SPIKE_RESULT engine=EEVEE scene=representative frames={FRAMES} "
      f"total={el:.2f}s per_frame={el / max(FRAMES, 1):.2f}s samples={SAMPLES} res={W}x{H}")
