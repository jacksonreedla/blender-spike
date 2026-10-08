# shot_05.py - one blank pauper's marker in a hard cold pool, a row of nameless
# slabs receding into fog, the monument and the churchyard gate only shapes.
import math

import bpy
from mathutils import Vector

sc = reset()

# Cold night. Fog near the clamp so the row loses contrast as it recedes and
# the far wall/gate survive only as outlines. a2 ran strength 0.45 and every
# surface in frame sat at the same value - the pool has to be the only bright
# thing, so the ambient goes down, not the key up.
world(color=(0.008, 0.013, 0.030), strength=0.26, fog=0.028, anisotropy=0.5)
# 120 m plane: at a 19.5 deg down-tilt the 80 m default's far edge was reaching
# the horizon band. Nothing may show an edge.
ground(size=120, texture="brown_mud_dry", scale=2.8, wet=0.30)


# --- shared materials -------------------------------------------------------
def _triplanar(mat, sat=1.0, val=1.0):
    """Re-map a library PBR set onto OBJECT coordinates with BOX projection.

    pbr_material() drives the texture from UVs, and a cube's UVs stretch each
    face to 0..1 - so a 0.17 m thick slab side got the same tile count as its
    0.70 m face. Object coords alone were worse: a flat 2D lookup of a vertical
    face smears the image into vertical stripes (the first a2 render looked
    like a row of barcodes). BOX projection samples each face along its own
    normal, which is the only correct way to put a ground texture on a cube.
    `sat`/`val` grade the albedo: the rock set is mossy green and a marker
    wants cold grey.
    """
    nt = mat.node_tree
    coord = next(n for n in nt.nodes if n.type == "TEX_COORD")
    mapn = next(n for n in nt.nodes if n.type == "MAPPING")
    nt.links.new(coord.outputs["Object"], mapn.inputs["Vector"])
    for n in nt.nodes:
        if n.type == "TEX_IMAGE":
            n.projection = "BOX"
            n.projection_blend = 0.3
    if sat != 1.0 or val != 1.0:
        bsdf = nt.nodes["Principled BSDF"]
        link = next((l for l in nt.links if l.to_socket == bsdf.inputs["Base Color"]), None)
        if link:
            hsv = nt.nodes.new("ShaderNodeHueSaturation")
            hsv.inputs["Saturation"].default_value = sat
            hsv.inputs["Value"].default_value = val
            src = link.from_socket
            nt.links.remove(link)
            nt.links.new(src, hsv.inputs["Color"])
            nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


STONE = _triplanar(pbr_material("GraveStone", "aerial_rocks_02", tiles=1.6, wet=0.10),
                   sat=0.22, val=0.72)
WALLST = _triplanar(pbr_material("WallStone", "cobblestone_03", tiles=2.2, wet=0.05),
                    sat=0.30, val=0.55)


def stone(size, at, rot_deg=0.0, tilt_deg=0.0, mat=None, bevel=0.010,
          taper=1.0, jitter=0.0, sink=0.02, seed=0):
    """A cut stone: real rock texture, bevelled edges, weathered top, settled
    into the ground at an angle. box() alone gives a flat-colour primitive,
    which is the single loudest placeholder tell in this spike."""
    o = box(size=size, at=at, rot_deg=rot_deg)
    # bake the non-uniform scale into the mesh so the bevel is metres, not axes
    for v in o.data.vertices:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    o.scale = (1.0, 1.0, 1.0)
    if taper != 1.0 or jitter:
        for i, v in enumerate(o.data.vertices):
            if v.co.z > 0:
                v.co.x *= taper
                v.co.y *= taper
                v.co.z += jitter * math.sin(seed * 2.3 + i * 1.7)
    o.rotation_euler = (math.radians(tilt_deg), 0.0, math.radians(rot_deg))
    o.data.materials.clear()
    o.data.materials.append(mat or STONE)
    b = o.modifiers.new("bev", "BEVEL")
    b.width, b.segments = bevel, 2
    b.limit_method, b.angle_limit = "ANGLE", math.radians(30)
    bpy.context.view_layer.update()
    zmin = min((o.matrix_world @ Vector(c[:])).z for c in o.bound_box)
    o.location.z += -sink - zmin           # settle it, never float it
    return o


# --- hero: the blank marker over a grave nobody paid for --------------------
# Attempt 1 used namaqualand_boulder_02: at 2.53 m it had to be turned nearly
# end-on to fit, and read as a natural boulder in a spotlight - the 1832 line
# had nothing to land on. A plain flat-faced 0.95 m slab, tipped 7 deg like a
# settled marker, is the object the sentence is about.
stone((0.70, 0.17, 0.95), (0.0, 0.0), rot_deg=9, tilt_deg=7,
      bevel=0.022, taper=0.94, jitter=0.020, seed=1)

# --- the row of nameless slabs receding right, into the fog -----------------
# spread wider in x than a straight row needs: from this camera the row
# converges hard, and at the first spacing the six stones piled into one mass
for i, (x, y, h, w, rz, tz) in enumerate([
        (1.25, 2.5, 0.54, 0.64, -7, 4),
        (2.00, 4.1, 0.48, 0.58, 5, -3),
        (2.80, 5.9, 0.56, 0.66, -3, 6),
        (3.70, 7.8, 0.46, 0.56, 9, -5),
        (4.70, 9.8, 0.50, 0.60, -6, 3),
        (5.80, 12.0, 0.42, 0.52, 4, -4)]):
    stone((w, 0.13, h), (x, y), rot_deg=rz, tilt_deg=tz,
          taper=0.95, jitter=0.014, seed=10 + i)

# two more on the left so the churchyard continues past both sides of frame
stone((0.56, 0.13, 0.44), (-0.95, 2.7), rot_deg=14, tilt_deg=-6, taper=0.95,
      jitter=0.012, seed=20)
stone((0.60, 0.13, 0.50), (-1.10, 4.6), rot_deg=-9, tilt_deg=5, taper=0.95,
      jitter=0.012, seed=21)

# --- foreground: a broken stump of a marker at the edge of the pool ---------
# Attempt 1's near box was an untextured black wedge in the corner. This one is
# stone, sits in the spot's falloff so its top face catches a rim, and crosses
# only the left edge.
# (foreground stump removed: outside the pool it was a black block)

# --- the paid-for monument, now only a silhouette against the lamp glow -----
place("gothic_statue", at=(-0.60, 7.2), rot_deg=150)

# --- churchyard wall, broken-topped, with the gateway standing in it --------
# Attempt 1's wall was a flat grey band with a razor-straight top across the
# whole frame. Built here from segments of different heights so the top edge is
# ragged, textured as masonry, and interrupted by the gate opening.
for x, h in [(-3.45, 1.20), (-2.55, 1.42), (-1.65, 1.08), (-0.75, 1.34),
             (0.15, 1.16), (5.25, 1.38), (6.15, 1.10), (7.05, 1.30),
             (7.95, 1.14), (8.85, 1.36), (9.75, 1.22)]:
    stone((1.22, 0.45, h), (x, 15.2 + 0.05 * math.sin(x * 2.1)),
          rot_deg=1.5 * math.sin(x * 1.3), mat=WALLST, bevel=0.02,
          jitter=0.05, seed=int(40 + x))
# gate piers: the only wall pieces that break the horizon line
stone((0.52, 0.52, 1.92), (0.88, 15.2), mat=WALLST, bevel=0.03, jitter=0.04, seed=60)
stone((0.52, 0.52, 1.88), (4.58, 15.2), mat=WALLST, bevel=0.03, jitter=0.04, seed=61)

# --- the gate from the hook, 18 m back, arch only above the wall ------------
place("large_iron_gate", at=(2.73, 14.9), rot_deg=6)

# --- the far practical: warm sodium, deliberately the only warm thing -------
lamp(at=(-0.50, 13.5), toward=(0.20, 8.0), energy=520, color=(1.0, 0.64, 0.34))

# --- one hard COLD pool, on the marker and the ground around it -------------
# a1's key was nominally cold at (0.66,0.78,1.0) and rendered sepia: AgX
# desaturates highlights, so a key has to be pushed much further than it looks.
key = light("SPOT", (-2.45, -2.00, 3.10), (0.02, 0.10, 0.55), 3400, size=0.13,
            color=(0.34, 0.54, 1.00), spot_size=math.radians(26))
key.data.spot_blend = 0.62          # the 0.4 default drew a hard arc on the floor
# cold rake down the row - a SPOT, not an area: the 280 W area lit the whole
# floor and there was no pool left to see. Aimed SHORT, so the near markers
# catch an edge and the far ones fall to shapes in the fog.
rake = light("SPOT", (5.60, 0.20, 3.20), (2.60, 4.50, 0.30), 900, size=0.8,
             color=(0.46, 0.64, 1.00), spot_size=math.radians(44))
rake.data.spot_blend = 0.75
# barely-there cold fill from camera-left so shadow sides are not pure black
light("AREA", (-3.60, -4.60, 2.40), (0.00, 0.60, 0.70), 45, size=6.0,
      color=(0.55, 0.72, 1.00))

# Descent: 1.32 m of travel, starting 1.2 m higher and tilted 26 deg down so
# the row reads as a row, ending low and close on the marker.
CAM_START = (-0.66, -3.55, 2.35)
CAM_END   = (-0.44, -3.05, 1.15)
CAM_AT    = (0.20, 0.00, 0.55)
LENS      = 32
