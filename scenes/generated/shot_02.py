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
scene.render.filepath = r"/home/apollo/blender-spike/out/shots/shot_02.png"
scene.eevee.taa_render_samples = 32
scene.eevee.use_shadows = True

# World: dark, with a faint cool ambient
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
wnt.nodes.clear()
wout = wnt.nodes.new("ShaderNodeOutputWorld")
wbg = wnt.nodes.new("ShaderNodeBackground")
wbg.inputs["Color"].default_value = (0.02, 0.025, 0.035, 1.0)
wbg.inputs["Strength"].default_value = 0.4
wnt.links.new(wbg.outputs["Background"], wout.inputs["Surface"])

# Volumetric atmosphere
vol = wnt.nodes.new("ShaderNodeVolumeScatter")
vol.inputs["Color"].default_value = (0.7, 0.75, 0.85, 1.0)
vol.inputs["Density"].default_value = 0.02
wnt.links.new(vol.outputs["Volume"], wout.inputs["Volume"])

# Concrete room: large box, normals inward via solidify-like scale
room_mat = bpy.data.materials.new("Concrete")
room_mat.use_nodes = True
rbsdf = room_mat.node_tree.nodes["Principled BSDF"]
rbsdf.inputs["Base Color"].default_value = (0.16, 0.16, 0.17, 1.0)
rbsdf.inputs["Roughness"].default_value = 0.95
if "Specular IOR Level" in rbsdf.inputs:
    rbsdf.inputs["Specular IOR Level"].default_value = 0.15

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
room = bpy.context.active_object
room.name = "Room"
room.scale = (12, 12, 6)
room.location = (0, 0, 6)
room.data.materials.append(room_mat)
# flip normals so we see inside
sol = room.modifiers.new("Solidify", "SOLIDIFY")
sol.thickness = 0.2
sol.offset = 1

# Floor plane (slightly darker)
floor_mat = bpy.data.materials.new("Floor")
floor_mat.use_nodes = True
fbsdf = floor_mat.node_tree.nodes["Principled BSDF"]
fbsdf.inputs["Base Color"].default_value = (0.12, 0.12, 0.13, 1.0)
fbsdf.inputs["Roughness"].default_value = 0.9
bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, 0))
floor = bpy.context.active_object
floor.data.materials.append(floor_mat)

# Wooden chair material
wood_mat = bpy.data.materials.new("Wood")
wood_mat.use_nodes = True
wbsdf = wood_mat.node_tree.nodes["Principled BSDF"]
wbsdf.inputs["Base Color"].default_value = (0.28, 0.14, 0.06, 1.0)
wbsdf.inputs["Roughness"].default_value = 0.6

chair_parts = []
# seat
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.45))
seat = bpy.context.active_object
seat.scale = (0.22, 0.22, 0.025)
seat.data.materials.append(wood_mat)
chair_parts.append(seat)
# legs
for x, y in [(-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.22))
    leg = bpy.context.active_object
    leg.scale = (0.02, 0.02, 0.22)
    leg.data.materials.append(wood_mat)
    chair_parts.append(leg)
# backrest posts
for x in (-0.18, 0.18):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.18, 0.72))
    post = bpy.context.active_object
    post.scale = (0.02, 0.02, 0.27)
    post.data.materials.append(wood_mat)
    chair_parts.append(post)
# backrest slats
for z in (0.62, 0.78, 0.94):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.18, z))
    slat = bpy.context.active_object
    slat.scale = (0.18, 0.015, 0.02)
    slat.data.materials.append(wood_mat)
    chair_parts.append(slat)

# join chair
bpy.ops.object.select_all(action='DESELECT')
for p in chair_parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = chair_parts[0]
bpy.ops.object.join()
chair = bpy.context.active_object
chair.name = "Chair"

# Hanging bulb (emissive sphere) + cord
bulb_mat = bpy.data.materials.new("Bulb")
bulb_mat.use_nodes = True
bnt = bulb_mat.node_tree
bnt.nodes.clear()
bout = bnt.nodes.new("ShaderNodeOutputMaterial")
bem = bnt.nodes.new("ShaderNodeEmission")
bem.inputs["Color"].default_value = (1.0, 0.85, 0.6, 1.0)
bem.inputs["Strength"].default_value = 40.0
bnt.links.new(bem.outputs["Emission"], bout.inputs["Surface"])

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0, 0, 2.6))
bulb = bpy.context.active_object
bulb.data.materials.append(bulb_mat)

cord_mat = bpy.data.materials.new("Cord")
cord_mat.use_nodes = True
cbsdf = cord_mat.node_tree.nodes["Principled BSDF"]
cbsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=3.4, location=(0, 0, 4.3))
cord = bpy.context.active_object
cord.data.materials.append(cord_mat)

# Key light: point light at bulb position
key_data = bpy.data.lights.new("Key", type='POINT')
key_data.energy = 900.0
key_data.color = (1.0, 0.82, 0.55)
key_data.shadow_soft_size = 0.15
key = bpy.data.objects.new("Key", key_data)
key.location = (0, 0, 2.6)
bpy.context.collection.objects.link(key)

# Rim light from behind, cool
rim_data = bpy.data.lights.new("Rim", type='SPOT')
rim_data.energy = 800.0
rim_data.color = (0.6, 0.75, 1.0)
rim_data.spot_size = math.radians(60)
rim_data.spot_blend = 0.5
rim = bpy.data.objects.new("Rim", rim_data)
rim.location = (2.5, 2.5, 3.0)
bpy.context.collection.objects.link(rim)
aim = bpy.data.objects.new("Aim", None)
aim.location = (0, 0, 0.5)
bpy.context.collection.objects.link(aim)
con = rim.constraints.new("TRACK_TO")
con.target = aim

# Camera
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 50
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (2.2, -3.2, 1.6)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam_aim = bpy.data.objects.new("CamAim", None)
cam_aim.location = (0, 0, 0.7)
bpy.context.collection.objects.link(cam_aim)
ccon = cam.constraints.new("TRACK_TO")
ccon.target = cam_aim

bpy.ops.render.render(write_still=True)