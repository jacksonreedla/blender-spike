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
scene.render.filepath = r"/home/apollo/blender-spike/out/shots/shot_03.png"
scene.eevee.taa_render_samples = 32
scene.eevee.use_shadows = True

# World: dusk gradient + volumetric haze
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputWorld")
bg = nt.nodes.new("ShaderNodeBackground")
grad = nt.nodes.new("ShaderNodeTexGradient")
grad.gradient_type = "LINEAR"
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.02, 0.03, 0.06, 1)
ramp.color_ramp.elements[1].position = 1.0
ramp.color_ramp.elements[1].color = (0.55, 0.28, 0.12, 1)
mapn = nt.nodes.new("ShaderNodeMapping")
mapn.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
texco = nt.nodes.new("ShaderNodeTexCoord")
nt.links.new(texco.outputs["Generated"], mapn.inputs["Vector"])
nt.links.new(mapn.outputs["Vector"], grad.inputs["Vector"])
nt.links.new(grad.outputs["Color"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0
nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
vol = nt.nodes.new("ShaderNodeVolumeScatter")
vol.inputs["Color"].default_value = (0.6, 0.4, 0.25, 1)
vol.inputs["Density"].default_value = 0.02
nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])

# Ground plane - cracked desert floor
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
ground = bpy.context.active_object
gmat = bpy.data.materials.new("Ground")
gmat.use_nodes = True
gn = gmat.node_tree
bsdf = gn.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.09, 0.06, 0.045, 1)
bsdf.inputs["Roughness"].default_value = 0.95
noise = gn.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 12.0
noise.inputs["Detail"].default_value = 8.0
bump = gn.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.6
gn.links.new(noise.outputs["Fac"], bump.inputs["Height"])
gn.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
ground.data.materials.append(gmat)

# Monolithic black stone slab
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 3.2))
slab = bpy.context.active_object
slab.scale = (1.1, 0.55, 3.2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
smat = bpy.data.materials.new("Stone")
smat.use_nodes = True
sn = smat.node_tree
sb = sn.nodes["Principled BSDF"]
sb.inputs["Base Color"].default_value = (0.012, 0.012, 0.014, 1)
sb.inputs["Roughness"].default_value = 0.55
sb.inputs["Metallic"].default_value = 0.0
snoise = sn.nodes.new("ShaderNodeTexNoise")
snoise.inputs["Scale"].default_value = 6.0
sbump = sn.nodes.new("ShaderNodeBump")
sbump.inputs["Strength"].default_value = 0.25
sn.links.new(snoise.outputs["Fac"], sbump.inputs["Height"])
sn.links.new(sbump.outputs["Normal"], sb.inputs["Normal"])
slab.data.materials.append(smat)

# Camera
cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (7.5, -9.0, 3.0)
scene.camera = cam
cam_data.lens = 50

def aim(obj, target_loc):
    t = bpy.data.objects.new("Aim_" + obj.name, None)
    t.location = target_loc
    bpy.context.collection.objects.link(t)
    c = obj.constraints.new("TRACK_TO")
    c.target = t
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

aim(cam, (0, 0, 3.0))

# Key light - warm dusk from behind/side
key_data = bpy.data.lights.new("Key", type="AREA")
key_data.energy = 2500
key_data.size = 4.0
key_data.color = (1.0, 0.55, 0.28)
key = bpy.data.objects.new("Key", key_data)
bpy.context.collection.objects.link(key)
key.location = (-6, 5, 7)
aim(key, (0, 0, 3.0))

# Rim light - cool from opposite side
rim_data = bpy.data.lights.new("Rim", type="AREA")
rim_data.energy = 1800
rim_data.size = 3.0
rim_data.color = (0.35, 0.5, 1.0)
rim = bpy.data.objects.new("Rim", rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (6, 6, 5)
aim(rim, (0, 0, 3.0))

# Fill - very low, front
fill_data = bpy.data.lights.new("Fill", type="AREA")
fill_data.energy = 300
fill_data.size = 6.0
fill_data.color = (0.5, 0.45, 0.4)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (2, -8, 4)
aim(fill, (0, 0, 2.5))

bpy.ops.render.render(write_still=True)