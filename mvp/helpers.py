# --- MVP helpers, exec'd by mvp/runner.py after scenes/preamble.py ---------------
# Textured primitives so no untextured "card" is ever in frame, and the grave
# dressing the library lacks: half-buried earth mounds, rough headstones, iron bars.

def skin(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


def tbox(size, at, texture="anti_slip_concrete", tiles=2.0, rot_deg=0.0, tilt_deg=0.0, z=0.0, wet=0.0, name="TBox"):
    """box() with a PBR texture instead of a flat colour. tilt_deg leans it about its own x axis."""
    o = box(size=size, at=at, rot_deg=rot_deg)
    mat = pbr_material(f"{name}_{texture}_{tiles}_{wet}_{len(bpy.data.materials)}", texture, tiles=tiles, wet=wet)
    nt = mat.node_tree
    coord = next(n for n in nt.nodes if n.type == "TEX_COORD")
    mapn = next(n for n in nt.nodes if n.type == "MAPPING")
    nt.links.new(coord.outputs["Object"], mapn.inputs["Vector"])   # box projection: a cube's UVs stretch each face
    for n in nt.nodes:
        if n.type == "TEX_IMAGE":
            n.projection, n.projection_blend = "BOX", 0.3
    skin(o, mat)
    o.rotation_euler = (math.radians(tilt_deg), 0.0, math.radians(rot_deg))
    o.location.z += z
    return o


def headstone(at, rot_deg=0.0, size=(0.6, 0.14, 0.9), tilt_deg=5.0, texture="aerial_rocks_02", tiles=1.5):
    """A rough stone slab standing on end, sunk 5 cm so a lean cannot float a corner."""
    return tbox(size, at, texture=texture, tiles=tiles, rot_deg=rot_deg, tilt_deg=tilt_deg, z=-0.05, name="Headstone")


def mound(at, size=(1.1, 0.5, 0.26), rot_deg=0.0, texture="brown_mud_dry", tiles=1.2, wet=0.3):
    """A fresh grave: a half-buried ellipsoid of earth (sphere centre on the ground)."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=48, ring_count=24, location=(at[0], at[1], 0.0))
    o = bpy.context.object
    o.scale = size
    o.rotation_euler = (0, 0, math.radians(rot_deg))
    bpy.ops.object.shade_smooth()
    return skin(o, pbr_material(f"Mound_{texture}", texture, tiles=tiles, wet=wet))


IRON = None


def iron():
    global IRON
    if IRON is None:
        IRON = material("Iron", (0.05, 0.05, 0.058), rough=0.38, metal=1.0)
    return IRON


def ibar(p1, p2, r=0.019, mat=None):
    """One iron bar (cylinder) between two world points."""
    a, b = Vector(p1), Vector(p2)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=d.length, location=(a + b) / 2)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    o.data.materials.append(mat or iron())
    return o


def ground_object(root):
    """Shift a placed model's root so the lowest point of its meshes sits on z=0
    (use after rotating a model about x/y, which invalidates the manifest's base_z)."""
    bpy.context.view_layer.update()
    lo = None
    for o in root.children_recursive:
        if o.type == "MESH":
            for c in o.bound_box:
                z = (o.matrix_world @ Vector(c)).z
                lo = z if lo is None else min(lo, z)
    if lo is not None:
        root.location.z -= lo
    return root


def shade(mat, value=1.0, sat=1.0):
    """Darken / desaturate a library texture's base colour (brown_mud_dry is a bright dry tan)."""
    nt = mat.node_tree
    b = nt.nodes["Principled BSDF"]
    link = next((l for l in nt.links if l.to_socket is b.inputs["Base Color"]), None)
    if link is None:
        return mat
    hs = nt.nodes.new("ShaderNodeHueSaturation")
    hs.inputs["Saturation"].default_value = sat
    hs.inputs["Value"].default_value = value
    src = link.from_socket
    nt.links.remove(link)
    nt.links.new(src, hs.inputs["Color"])
    nt.links.new(hs.outputs["Color"], b.inputs["Base Color"])
    return mat
