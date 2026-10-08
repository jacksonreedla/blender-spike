# shot_04.py - an iron mortsafe padlocked shut over a half-sunk grave slab, a cold beam
# raking through the bars so their shadows stripe the slab and run down the mud to the lens.
import random

# Camera first: the rain and the dressing below are solved against this axis, so the frame
# math (32 mm -> horizontal half-width 0.3164*depth, half-height 0.5625*depth) must exist
# before them. Every dressed item below was checked against it; four had to move.
CAM_START = (1.85, -4.60, 0.62)     # knee height, 3/4 on to the cage from front-right
CAM_END   = (1.55, -4.10, 1.48)     # rises 0.86 m and pushes 0.58 m: 1.04 m of travel
CAM_AT    = (0.15, -0.35, 0.55)     # a point just INSIDE the near bars (sightline guard)
LENS      = 32                      # the cage is 2.4 m wide in projection; 35 mm crops it

_cm = [(a + b) / 2 for a, b in zip(CAM_START, CAM_END)]
_d = (CAM_AT[0] - _cm[0], CAM_AT[1] - _cm[1])
_dl = math.hypot(*_d)
DX, DY = _d[0] / _dl, _d[1] / _dl          # view direction, ground plan
PX, PY = DY, -DX                           # frame-right in the ground plan
CX, CY = _cm[0], _cm[1]


def at_frame(depth, lat):
    """world (x, y) `depth` m along the view axis and `lat` m to frame-right."""
    return (CX + depth * DX + lat * PX, CY + depth * DY + lat * PY)


sc = reset()
# Cold, thin, near-isotropic: a1's sepia was the warm lamp lighting dense forward-scattering
# fog. The lamp is now a small distant accent and the only strong source is the cold key.
world(color=(0.014, 0.018, 0.030), strength=0.42, fog=0.016, anisotropy=0.25)
ground(size=200, texture="brown_mud_dry", scale=2.2, wet=0.62)   # 200 m: no plane edge at the horizon

IRON = material("Iron", (0.048, 0.048, 0.055), rough=0.34, metal=1.0)
LOCK = material("Lock", (0.21, 0.20, 0.18), rough=0.26, metal=1.0)
STONE = pbr_material("Stone", "aerial_rocks_02", tiles=1.4, wet=0.30)
for _n in STONE.node_tree.nodes:
    if _n.type == "TEX_IMAGE":
        _n.projection, _n.projection_blend = "BOX", 0.3
STONE.node_tree.links.new(next(n for n in STONE.node_tree.nodes if n.type == "TEX_COORD").outputs["Object"], next(n for n in STONE.node_tree.nodes if n.type == "MAPPING").inputs["Vector"])
WALLM = pbr_material("WallStone", "cobblestone_03", tiles=4.0, wet=0.2)
RAINM = material("Rain", (0.50, 0.56, 0.68), rough=0.08)
DARKM = material("FarStone", (0.030, 0.032, 0.038), rough=0.95)


def skin(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


def ibar(p1, p2, r=0.019, mat=None):
    """One iron bar between two points. box() can never leave the ground, so the top grid,
    the rails and the round bars the judges asked for are cylinders."""
    a, b = Vector(p1), Vector(p2)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=d.length, location=(a + b) / 2)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    o.data.materials.append(mat or IRON)
    return o


# --- the mortsafe: 2.2 x 1.0 m footprint, barred on all four sides, top grid, three rails,
# --- padlock on the near face. a1 built one edge-on row of posts: a picket fence.
CROT = -15.0                                     # 3/4 to camera: near long side AND the right end read
_cc, _ss = math.cos(math.radians(CROT)), math.sin(math.radians(CROT))


def W(u, v, z=0.0):
    return (_cc * u - _ss * v, _ss * u + _cc * v, z)


HU, HV, TOP = 1.10, 0.50, 1.00

# the grave itself: a flat stone half sunk in the mud, under the cage, seen through the bars
slab = box(size=(2.00, 0.90, 0.16), at=W(0, 0)[:2], rot_deg=CROT + 3,
           color=(0.16, 0.155, 0.147), rough=0.9)
slab.location.z = 0.02                           # top at 0.10, bottom at -0.06: sunk, not a plinth
skin(slab, STONE)

for i in range(19):                              # 19 uprights a side, 0.122 m apart, sunk 8 cm
    u = -HU + i * (2 * HU / 18)
    for v in (-HV, HV):
        ibar(W(u, v, -0.08), W(u, v, 1.02), 0.031 if i in (0, 18) else 0.019)
for u in (-HU, HU):                              # the end returns - what a1 was missing
    for j in range(1, 8):
        ibar(W(u, -HV + j * 0.125, -0.08), W(u, -HV + j * 0.125, 1.02), 0.019)
for z in (0.10, 0.58, TOP):                      # bottom / mid band / top rail, all four sides
    for v in (-HV, HV):
        ibar(W(-HU, v, z), W(HU, v, z), 0.021)
    for u in (-HU, HU):
        ibar(W(u, -HV, z), W(u, HV, z), 0.021)
for v in (-0.375, -0.125, 0.125, 0.375):         # top grid: a closed iron box, not a fence
    ibar(W(-HU, v, TOP), W(HU, v, TOP), 0.017)
for k in range(1, 8):
    ibar(W(-HU + k * 0.275, -HV, TOP), W(-HU + k * 0.275, HV, TOP), 0.017)

_lx, _ly, _lz = W(0.06, -0.55)                   # padlock, clamped over the mid rail, near face
bpy.ops.mesh.primitive_cube_add(size=1, location=(_lx, _ly, 0.55))
_lock = bpy.context.object
_lock.scale = (0.13, 0.07, 0.17)
_lock.rotation_euler = (0, 0, math.radians(CROT))
_lock.data.materials.append(LOCK)
bpy.ops.mesh.primitive_torus_add(major_radius=0.052, minor_radius=0.013, major_segments=20,
                                 minor_segments=8, location=(_lx, _ly, 0.65),
                                 rotation=(math.radians(90), 0, math.radians(CROT)))
bpy.context.object.data.materials.append(LOCK)

# --- the kirkyard around it ---------------------------------------------------
s2 = box(size=(1.85, 0.85, 0.15), at=(-1.80, 1.75), rot_deg=14,
         color=(0.16, 0.155, 0.148), rough=0.9)  # the uncaged grave beside: the comparison
s2.location.z = 0.03
skin(s2, STONE)


def headstone(at, rot, size, tilt=6.0):
    o = box(size=size, at=at, rot_deg=rot, color=(0.15, 0.147, 0.14), rough=0.85)
    o.rotation_euler = (math.radians(tilt), 0, math.radians(rot))
    o.location.z -= 0.05                         # sunk: a tilt about its own centre cannot float it
    return skin(o, STONE)


headstone((-1.30, 2.45), 22, (0.62, 0.14, 0.92), tilt=7)
headstone((-3.10, 4.10), -12, (0.55, 0.13, 0.80), tilt=-5)
headstone((-0.35, 4.70), 8, (0.58, 0.13, 0.86), tilt=4)
headstone(at_frame(8.0, 1.75), 40, (0.60, 0.14, 0.88), tilt=6)
headstone(at_frame(11.0, 2.45), -25, (0.52, 0.12, 0.74), tilt=-4)

place("rock_face_01", at=at_frame(10.5, 2.55), rot_deg=18)          # a rock mass breaks the wall line

for sz, at, rot in (((7.0, 0.45, 1.35), (-5.60, 8.10), 4),       # kirkyard wall in two segments,
                    ((7.0, 0.45, 1.12), (1.00, 7.50), -7)):      # stepped so the top line is not one seam
    skin(box(size=sz, at=at, rot_deg=rot, color=(0.09, 0.088, 0.085), rough=0.95), WALLM)

tower = box(size=(3.0, 3.0, 7.0), at=(-10.2, 18.0), rot_deg=12, color=(0.03, 0.032, 0.038), rough=0.95)
skin(tower, DARKM)                                               # the kirk itself, a fogged silhouette
spire = box(size=(1.7, 1.7, 2.6), at=(-10.2, 18.0), rot_deg=12, color=(0.03, 0.032, 0.038), rough=0.95)
spire.location.z = 8.3
skin(spire, DARKM)
win = box(size=(0.34, 0.20, 0.55), at=(-10.0, 16.45), rot_deg=12, color=(1.0, 0.66, 0.34), rough=0.6)
win.location.z = 4.2                                             # one lit window: somebody is watching
skin(win, material("Win", (1.0, 0.66, 0.34), rough=0.6, emit=3.5))

for dep, lat, sz, rot in ((28.0, 4.6, (9.0, 4.0, 4.2), 12),      # fogged skyline closing the right
                          (33.0, 7.6, (10.0, 4.0, 5.6), -8)):    # half, so the sky is not half the frame
    skin(box(size=sz, at=at_frame(dep, lat), rot_deg=rot, color=(0.03, 0.032, 0.038), rough=0.95), DARKM)

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(-13.8, 21.8, 9.4), segments=24, ring_count=12)
bpy.context.object.data.materials.append(material("Moon", (0.86, 0.91, 1.0), rough=1.0, emit=6.0))

lamp(at=(-5.50, 9.50), toward=(-3.50, 5.00), energy=600, color=(1.0, 0.60, 0.28))  # dim, distant, behind the wall

# (rain rods removed: they read as scratches on the frame)

# --- light --------------------------------------------------------------------
# Key: COLD, hard and LOW (12 deg elevation) from behind-left, aimed past the cage at the mud
# 2 m in front of it, so the beam rakes between the uprights and throws 4.7 m bar shadows over
# the slab and on down the mud into the bottom of frame. size=0.03 keeps them hard at that
# throw. The apex sits just OUTSIDE the left frame edge - in a1 the cone mouth was in shot as
# a white fog wedge - and the warm gas lamp, which was a1's key, is now a background accent.
light("SPOT", (-4.90, 2.74, 1.60), (0.75, -2.10, 0.02), 4800, size=0.03,
      color=(0.70, 0.80, 1.0), spot_size=math.radians(50))
# Fill: cold, camera-right and high, so the near bars carry a specular edge against the fog
# instead of reading as flat black pickets. About 7 percent of key.
light("AREA", (3.90, -3.00, 2.10), (0.40, -0.10, 0.55), 140, size=3.0, color=(0.66, 0.76, 1.0))
# Sky bounce: very soft, high front-left, 5 percent of key at the cage - it exists to keep the
# wall, the headstones and the tomb house off pure black without touching the mud's contrast.
light("AREA", (-6.00, -2.00, 7.00), (-2.00, 6.00, 1.00), 420, size=7.0, color=(0.62, 0.72, 1.0))
