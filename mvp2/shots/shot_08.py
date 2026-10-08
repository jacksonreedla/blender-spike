# shot_08 - beat 4, cut on "In": "In Scotland, families locked iron cages over graves."
# Villagers heave a mortsafe down over a grave while a lantern is held over the work; the camera
# arcs in and down off the right shoulder and lands its aim on the shut padlock at (-0.085,-0.547).
# Every coordinate below is the planner's, solved against the real 32 mm portrait frustum.
sc = reset()
night(fog=0.016, aniso=0.25, color=(0.014, 0.018, 0.030), world_strength=0.42)
mud_ground(scale=2.2, wet=0.62, value=1.0)

# --- set: the churchyard, the cage on its slab, a fresh mound kept OFF the cage ---------------
# mortsafe and fresh_grave sit apart on purpose - a cage dropped on a mound intersects its slab.
churchyard(seed=2, lamp_at=(-5.50, 9.50), lamp_toward=(-3.50, 5.00), statue_at=None, avoid=(0, 0, 2.6))
mortsafe(at=(0.00, 0.00), rot_deg=-15)
fresh_grave(at=(2.20, 1.50))

# --- dressing: the held lantern. Idle_Torch_Loop carries no torch mesh and emits nothing, so the
# warm source is a real POINT light at hand height beside the prop. -----------------------------
place("brass_diya_lantern", at=(-1.85, 1.55))
light("POINT", (-1.85, 1.55, 1.75), (-0.20, 0.60, 0.70), 70, size=0.06, color=(1.0, 0.66, 0.32))

# --- three villagers: one shoving the cage home, one holding the light, one calling the work ---
# Push_Loop faces 270 = drives +X into the cage end; 0.15 m/s = 0.34 m over the shot, closing on
# the bars without entering them (root 1.44 m out along the cage axis, cage half-length 1.10).
person("robber", "Fixing_Kneeling", at=(-1.45, 0.15), facing_deg=270, travel=0)
_w = person("watchman", "Idle_Torch_Loop", at=(-1.35, 1.95), facing_deg=160)
prop_lantern(_w)
person("robber2", "Idle_Talking_Loop", at=(-0.25, 2.35), facing_deg=215)

# --- light: a hard low key raking along the bars, cold fill from the camera side ---------------
# Deviation (render 2 proved it): the planner's key at (-4.90,2.74,1.60) sat INSIDE this wider
# frustum - a bare white glare blob in fog across the left third. Slid 1.5 m further out along
# the same rake line so the source is off the left edge, energy up for the extra 0.8 m throw.
key_cold((-6.30, 1.30, 2.10), (0.75, -2.10, 0.02), energy=6200, spot_deg=50, size=0.03)
fill_cold((3.90, -3.00, 2.10), (0.40, -0.10, 0.55), 140)

# --- camera: 2.06 m arc in and down, the only aim pan in the film, landing on the padlock ------
# Deviation (render 1 proved it): the planner's arc sat at cage height, so the cage read as a
# flat fence edge-on, two of the three men fell outside the 35 deg horizontal frustum and the
# upper-left third was bare fog. Backed the arc off 0.7 m and raised it ~0.7 m: the top grid now
# reads as a cage seen down onto, all three men clear the frame edges, and the aim still ends on
# the padlock at (-0.085,-0.547) - where mortsafe() actually builds it.
CAM_START = (3.05, -3.95, 2.45)
CAM_END = (1.75, -2.70, 1.45)
CAM_AT = (-0.80, 2.15, 1.70)          # head height between the two standing men, under the lantern
CAM_AT_END = (-0.085, -0.547, 0.55)   # ... and walks down onto the shut padlock
LENS = 32
