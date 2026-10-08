import bpy
import math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = r"/home/apollo/blender-spike/out/shots/shot_05.png"
scene.eevee.taa_render_samples = 32
scene.eevee.use_shadows = True

# World with dark background and volumetric scatter
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
bg.inputs[0].default_value = (0.005, 0.006, 0.010, 1.0)
bg.inputs[1].default_value = 0.15
vol = nt.nodes.new("ShaderNodeVolumeScatter")
vol.inputs["Color"].default_value = (0.55, 0.60, 0.75, 1.0)
vol.inputs["Density"].default_value = 0.018
nt.links.new(vol.outputs["Volume"], nt.nodes["World Output"].inputs["Volume"])

# Regolith ground plane
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Regolith"
mat_g = bpy.data.materials.new("RegolithMat")
mat_g.use_nodes = True
bsdf = mat_g.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.10, 0.10, 0.11, 1.0)
bsdf.inputs["Roughness"].default_value = 0.95
if "Specular IOR Level" in bsdf.inputs:
    bsdf.inputs["Specular IOR Level"].default_value = 0.1
ground.data.materials.append(mat_g)

# Helmet: UV sphere with a visor cutout suggestion (dark glass sphere in front)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, segments=48, ring_count=32, location=(0, 0, 0.16))
helmet = bpy.context.active_object
helmet.name = "Helmet"
mat_h = bpy.data.materials.new("HelmetMat")
mat_h.use_nodes = True
hb = mat_h.node_tree.nodes["Principled BSDF"]
hb.inputs["Base Color"].default_value = (0.75, 0.76, 0.78, 1.0)
hb.inputs["Roughness"].default_value = 0.35
hb.inputs["Metallic"].default_value = 0.6
helmet.data.materials.append(mat_h)

# Visor: dark reflective sphere slightly forward
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.115, segments=48, ring_count=32, location=(0, -0.075, 0.17))
visor = bpy.context.active_object
visor.name = "Visor"
mat_v = bpy.data.materials.new("VisorMat")
mat_v.use_nodes = True
vb = mat_v.node_tree.nodes["Principled BSDF"]
vb.inputs["Base Color"].default_value = (0.01, 0.012, 0.02, 1.0)
vb.inputs["Roughness"].default_value = 0.08
vb.inputs["Metallic"].default_value = 1.0
visor.data.materials.append(mat_v)

# Camera
cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (0.9, -1.6, 0.55)
scene.camera = cam
cam_data.lens = 65

# Aim empty at helmet
aim = bpy.data.objects.new("Aim", None)
aim.location = (0, 0, 0.18)
bpy.context.collection.objects.link(aim)
tc = cam.constraints.new("TRACK_TO")
tc.target = aim
tc.track_axis = 'TRACK_NEGATIVE_Z'
tc.up_axis = 'UP_Y'

# Key light: warm-ish spot from upper left
key_data = bpy.data.lights.new("Key", 'SPOT')
key_data.energy = 1800
key_data.spot_size = math.radians(45)
key_data.spot_blend = 0.4
key = bpy.data.objects.new("Key", key_data)
key.location = (-1.6, -1.4, 2.2)
bpy.context.collection.objects.link(key)
kc = key.constraints.new("TRACK_TO")
kc.target = aim
kc.track_axis = 'TRACK_NEGATIVE_Z'
kc.up_axis = 'UP_Y'

# Rim light: cool from behind right
rim_data = bpy.data.lights.new("Rim", 'AREA')
rim_data.energy = 900
rim_data.size = 1.2
rim = bpy.data.objects.new("Rim", rim_data)
rim.location = (1.8, 1.6, 1.4)
bpy.context.collection.objects.link(rim)
rc = rim.constraints.new("TRACK_TO")
rc.target = aim
rc.track_axis = 'TRACK_NEGATIVE_Z'
rc.up_axis = 'UP_Y'

# Fill: very dim cool from front
fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 120
fill_data.size = 2.0
fill = bpy.data.objects.new("Fill", fill_data)
fill.location = (0.5, -2.5, 0.8)
bpy.context.collection.objects.link(fill)
fc = fill.constraints.new("TRACK_TO")
fc.target = aim
fc.track_axis = 'TRACK_NEGATIVE_Z'
fc.up_axis = 'UP_Y'

# Color management: filmic-ish, slightly cool
scene.view_settings.look = 'AgX - Medium High Contrast'

bpy.ops.render.render(write_still=True)