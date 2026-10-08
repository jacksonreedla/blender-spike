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
scene.render.filepath = r"/home/apollo/blender-spike/out/shots/shot_01.png"

scene.eevee.taa_render_samples = 32
scene.eevee.use_shadows = True

# World: dark cave ambience with a hint of cool light
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
bg = wnt.nodes["Background"]
bg.inputs["Color"].default_value = (0.02, 0.025, 0.035, 1.0)
bg.inputs["Strength"].default_value = 0.15

# Volumetric atmosphere
vol = wnt.nodes.new("ShaderNodeVolumeScatter")
vol.inputs["Color"].default_value = (0.7, 0.75, 0.85, 1.0)
vol.inputs["Density"].default_value = 0.02
wnt.links.new(vol.outputs["Volume"], wnt.nodes["World Output"].inputs["Volume"])

# --- Cave geometry: a large dark tunnel mouth ---
# Floor
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "CaveFloor"

# Cave walls: two large planes angled inward
for side, x in (("L", -6), ("R", 6)):
    bpy.ops.mesh.primitive_plane_add(size=40, location=(x, 0, 10))
    wall = bpy.context.active_object
    wall.name = "Wall_" + side
    wall.rotation_euler = (math.radians(90), 0, math.radians(90 if side == "L" else -90))
    wall.scale = (1.0, 1.0, 1.0)

# Ceiling
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 20))
ceil = bpy.context.active_object
ceil.name = "Ceiling"

# Back wall with a bright opening (the cave mouth) - use a plane with emission
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 12, 10))
back = bpy.context.active_object
back.name = "BackWall"
back.rotation_euler = (math.radians(90), 0, 0)

# Cave rock material
rock_mat = bpy.data.materials.new("Rock")
rock_mat.use_nodes = True
rn = rock_mat.node_tree.nodes
bsdf = rn.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.04, 0.04, 0.045, 1.0)
bsdf.inputs["Roughness"].default_value = 0.95
for obj in (floor, ceil, back):
    obj.data.materials.append(rock_mat)
for obj in bpy.data.objects:
    if obj.name.startswith("Wall_"):
        obj.data.materials.append(rock_mat)

# Bright opening: emissive plane at the cave mouth
bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 11.5, 6))
opening = bpy.context.active_object
opening.name = "Opening"
opening.rotation_euler = (math.radians(90), 0, 0)
emit_mat = bpy.data.materials.new("OpeningLight")
emit_mat.use_nodes = True
en = emit_mat.node_tree.nodes
for n in list(en):
    en.remove(n)
out = en.new("ShaderNodeOutputMaterial")
em = en.new("ShaderNodeEmission")
em.inputs["Color"].default_value = (1.0, 0.95, 0.85, 1.0)
em.inputs["Strength"].default_value = 12.0
emit_mat.node_tree.links.new(em.outputs["Emission"], out.inputs["Surface"])
opening.data.materials.append(emit_mat)

# --- Lone figure silhouette ---
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=1.8, location=(0, 6, 0.9))
body = bpy.context.active_object
body.name = "Figure"
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(0, 6, 2.0))
head = bpy.context.active_object
head.name = "Head"

fig_mat = bpy.data.materials.new("Figure")
fig_mat.use_nodes = True
fn = fig_mat.node_tree.nodes
fb = fn.get("Principled BSDF")
fb.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1.0)
fb.inputs["Roughness"].default_value = 0.9
body.data.materials.append(fig_mat)
head.data.materials.append(fig_mat)

# --- Lights ---
# Key light from behind (the cave mouth) - strong backlight
bpy.ops.object.light_add(type="AREA", location=(0, 10, 6))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 3000
key.data.size = 8
key.data.color = (1.0, 0.95, 0.85)
key.rotation_euler = (math.radians(90), 0, 0)

# Rim light from the side to catch the figure
bpy.ops.object.light_add(type="AREA", location=(-4, 4, 3))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 800
rim.data.size = 3
rim.data.color = (0.6, 0.7, 1.0)

# Aim rim at figure
empty = bpy.data.objects.new("Aim", None)
empty.location = (0, 6, 1.2)
bpy.context.collection.objects.link(empty)
con = rim.constraints.new("TRACK_TO")
con.target = empty

# --- Camera ---
bpy.ops.object.camera_add(location=(0, -6, 2.5))
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 35
scene.camera = cam

# Aim camera at figure
cam_empty = bpy.data.objects.new("CamAim", None)
cam_empty.location = (0, 6, 1.5)
bpy.context.collection.objects.link(cam_empty)
cam_con = cam.constraints.new("TRACK_TO")
cam_con.target = cam_empty

bpy.ops.render.render(write_still=True)