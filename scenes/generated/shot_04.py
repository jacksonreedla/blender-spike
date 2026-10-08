import bpy
import math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = "/home/apollo/blender-spike/out/shots/shot_04.png"
scene.eevee.taa_render_samples = 32
scene.eevee.use_shadows = True

# World: dark fog with volumetric scatter
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
bg.inputs[0].default_value = (0.02, 0.025, 0.035, 1.0)
bg.inputs[1].default_value = 0.15
vol = nt.nodes.new("ShaderNodeVolumeScatter")
vol.inputs["Color"].default_value = (0.35, 0.4, 0.5, 1.0)
vol.inputs["Density"].default_value = 0.022
nt.links.new(vol.outputs["Volume"], nt.nodes["World Output"].inputs["Volume"])

# Materials
mat_pillar = bpy.data.materials.new("Pillar")
mat_pillar.use_nodes = True
p = mat_pillar.node_tree.nodes["Principled BSDF"]
p.inputs["Base Color"].default_value = (0.09, 0.09, 0.1, 1.0)
p.inputs["Roughness"].default_value = 0.85

mat_floor = bpy.data.materials.new("Floor")
mat_floor.use_nodes = True
f = mat_floor.node_tree.nodes["Principled BSDF"]
f.inputs["Base Color"].default_value = (0.02, 0.02, 0.025, 1.0)
f.inputs["Roughness"].default_value = 0.08
f.inputs["Metallic"].default_value = 0.6

# Floor plane
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor.data.materials.append(mat_floor)

# Pillars receding down -Y
for i in range(9):
    y = -2.0 - i * 3.2
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(side * 2.6, y, 3.0))
        pil = bpy.context.active_object
        pil.scale = (0.55, 0.55, 6.0)
        pil.data.materials.append(mat_pillar)

# Camera
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 40
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (0.0, 3.5, 1.6)
bpy.context.collection.objects.link(cam)
scene.camera = cam

# Aim target down the corridor
aim = bpy.data.objects.new("Aim", None)
aim.location = (0.0, -14.0, 2.2)
bpy.context.collection.objects.link(aim)
ct = cam.constraints.new("TRACK_TO")
ct.target = aim
ct.track_axis = "TRACK_NEGATIVE_Z"
ct.up_axis = "UP_Y"

# Key light: warm spot from behind camera, low, raking the floor
key_data = bpy.data.lights.new("Key", type="SPOT")
key_data.energy = 1800
key_data.spot_size = math.radians(70)
key_data.spot_blend = 0.5
key_data.color = (1.0, 0.85, 0.65)
key = bpy.data.objects.new("Key", key_data)
key.location = (0.0, 4.5, 3.2)
bpy.context.collection.objects.link(key)
kt = key.constraints.new("TRACK_TO")
kt.target = aim
kt.track_axis = "TRACK_NEGATIVE_Z"
kt.up_axis = "UP_Y"

# Cool rim light deep in the corridor
rim_data = bpy.data.lights.new("Rim", type="SPOT")
rim_data.energy = 2500
rim_data.spot_size = math.radians(55)
rim_data.spot_blend = 0.6
rim_data.color = (0.55, 0.7, 1.0)
rim = bpy.data.objects.new("Rim", rim_data)
rim.location = (0.0, -22.0, 4.0)
bpy.context.collection.objects.link(rim)
rt = rim.constraints.new("TRACK_TO")
rt.target = aim
rt.track_axis = "TRACK_NEGATIVE_Z"
rt.up_axis = "UP_Y"

# Side fill to catch pillar edges
fill_data = bpy.data.lights.new("Fill", type="AREA")
fill_data.energy = 400
fill_data.size = 4.0
fill_data.color = (0.6, 0.75, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
fill.location = (5.0, -6.0, 3.5)
bpy.context.collection.objects.link(fill)
ft = fill.constraints.new("TRACK_TO")
ft.target = aim
ft.track_axis = "TRACK_NEGATIVE_Z"
ft.up_axis = "UP_Y"

bpy.ops.render.render(write_still=True)