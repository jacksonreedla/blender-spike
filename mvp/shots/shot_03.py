# shot_03.py - low at the foot of a fresh grave: a heaped mound of turned earth with a rough
# uncarved stone standing at its head, cold hard light from the right rimming the stone,
# older graves and a lamp halo lost in fog behind; the camera pushes in along the ground.
sc = reset()
world(color=(0.006, 0.009, 0.020), strength=0.26, fog=0.018, anisotropy=0.6)
g = ground(size=200, texture="brown_mud_dry", scale=2.4, wet=0.35)
shade(g.data.materials[0], 0.30, 0.65)

# --- the fresh grave: a mound of dug earth, darker and wetter than the ground -------------------
m = mound((0.0, 0.55), size=(0.66, 1.15, 0.30), rot_deg=4, tiles=0.9, wet=0.25)
shade(m.data.materials[0], 0.24, 0.8)
m.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.85
# clods that fell off the spade
for at, r, sc_ in (((0.72, -0.35), 20, 1.6), ((-0.66, 0.15), -50, 1.3), ((0.58, 1.05), 65, 1.2), ((-0.55, -0.85), 15, 1.1)):
    place("moon_rock_01", at=at, rot_deg=r, scale=sc_)
# the rough uncarved stone at its head
head = place("rock_face_02", at=(0.0, 1.85), rot_deg=0, scale=0.30)

# --- the churchyard behind, in fog ------------------------------------------------------------
for at, r, size, t in (((-1.75, 3.6), 14, (0.58, 0.14, 0.86), 6), ((1.65, 3.9), -9, (0.54, 0.13, 0.78), -5),
                       ((-2.6, 5.4), 22, (0.62, 0.15, 0.92), 4), ((2.5, 5.6), -18, (0.50, 0.13, 0.70), 7),
                       ((0.6, 6.4), 5, (0.56, 0.14, 0.84), -4), ((-1.2, 7.6), -12, (0.60, 0.14, 0.90), 5)):
    shade(headstone(at, rot_deg=r, size=size, tilt_deg=t).data.materials[0], 0.40, 0.5)
shade(tbox((1.7, 0.85, 0.6), (-2.9, 3.2), texture="aerial_rocks_02", tiles=1.4, rot_deg=10, name="Tomb").data.materials[0], 0.4, 0.5)
# no wall: a flat band across the mid-frame read as a hay bale. Rock masses in fog instead.
place("rock_face_02", at=(4.6, 9.5), rot_deg=-40)
place("namaqualand_boulder_02", at=(-3.4, 8.2), rot_deg=25)
place("gothic_statue", at=(2.4, 7.9), rot_deg=160)
place("rock_face_01", at=(-4.2, 10.5), rot_deg=30)
place("dead_tree_trunk", at=(2.9, 4.6), rot_deg=80)
lamp(at=(-2.4, 9.0), toward=(0.0, 5.0), energy=700, color=(1.0, 0.64, 0.32))

# --- light: one hard cold key from the RIGHT, grazing, so the mound and the stone throw shadows left
light("SPOT", (4.0, 0.6, 2.2), (0.0, 0.9, 0.30), 2400, size=0.12, color=(0.62, 0.76, 1.0), spot_size=math.radians(30))
# soft cold fill from camera-left, low, so the shadow side of the mound is earth not void
light("AREA", (-3.6, -2.6, 1.6), (0.0, 0.6, 0.3), 90, size=3.0, color=(0.58, 0.70, 1.0))
# a little warm bounce from the lamp direction onto the stones behind
light("AREA", (-1.5, 6.5, 3.0), (0.0, 5.0, 0.8), 120, size=4.0, color=(1.0, 0.75, 0.5))

CAM_START = (0.30, -3.60, 0.52)
CAM_END   = (0.18, -2.70, 0.46)
CAM_AT    = (0.0, 0.60, 0.28)     # the mound itself: the sightline guard lands on it
LENS      = 35
