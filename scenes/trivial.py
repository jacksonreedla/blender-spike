"""Gate 1: does EEVEE initialise headless on the Vega 11 iGPU at all?

Deliberately the smallest scene that still exercises a GPU rasteriser path:
one mesh, one light, one camera, a real material. If this cannot render, no
amount of scene work matters and the project is a cloud-render project.

    blender -b -P scenes/trivial.py -- out/trivial.png
"""
import sys
import time

import bpy

OUT = sys.argv[-1] if "--" in sys.argv else "/home/apollo/blender-spike/out/trivial.png"
W, H = 1080, 1920


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = OUT

    # floor + a single object
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.4, location=(0, 0, 1.4))
    bpy.ops.object.shade_smooth()
    obj = bpy.context.object
    mat = bpy.data.materials.new("Chalk")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.55, 0.57, 0.62, 1)
    bsdf.inputs["Roughness"].default_value = 0.45
    obj.data.materials.append(mat)

    light_data = bpy.data.lights.new("Key", type="AREA")
    light_data.energy = 900
    light_data.size = 6
    light = bpy.data.objects.new("Key", light_data)
    light.location = (5, -6, 8)
    light.rotation_euler = (0.7, 0.2, 0.7)
    bpy.context.collection.objects.link(light)

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 40
    cam = bpy.data.objects.new("Cam", cam_data)
    cam.location = (0, -9, 2.6)
    cam.rotation_euler = (1.40, 0, 0)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam


clear()
build()
t0 = time.time()
bpy.ops.render.render(write_still=True)
print(f"SPIKE_RESULT engine=EEVEE scene=trivial seconds={time.time() - t0:.2f} out={OUT}")
