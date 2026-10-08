# shot_10 - beat 5, cut on "until": "Watchmen sat up in the churchyard for weeks, until the body
# was worthless." The watch rises off the chair he sat the night out on, the cage left behind him
# in the fog, while the camera cranes up and back - the only widening move in the film.
# Set, dressing, staging and camera are the planner's, solved against the real 32 mm frustum.
sc = reset()
night(fog=0.018)

# --- set: shot_09's churchyard, unchanged, with the cage now mid-ground -------------------------
# Same seed, same lamp, no statue: the place has to be continuous with the shot before it.
churchyard(seed=2, lamp_at=(-5.50, 9.50), statue_at=None, avoid=(0.4, 1.2, 2.6))
mortsafe(at=(0.40, 1.20), rot_deg=-15)

# --- dressing: the chair he sat the night out on, and the lantern burnt low ---------------------
# Render a1 put the chair at the planner's (0.75,-0.25) = the man's own root, and a rising body
# wears a 0.43 x 0.58 x 0.97 m chair: the seat and back came out through his chest. It is moved
# 0.38 m along his backward vector, so it is the chair he is LEAVING - which is the beat - and
# turned to match him. Same chair, same spot to within a step, at 320 px.
place("dining_chair_02", at=(0.44, -0.03), rot_deg=235)
place("brass_diya_lantern", at=(0.30, -0.75))
light("POINT", (0.30, -0.75, 0.45), (0.30, 0.40, 0.60), 30, size=0.05, color=(1.0, 0.68, 0.34))

# --- the watch standing up, and the second watchman still on his feet ---------------------------
# Sitting_Exit is only 24.8 f long (measured on the rig), so at the still frame 24 an unphased
# clip is already finished and reads as a man simply standing. phase=+8 puts frame 24 at clip
# local 16 - half risen, weight still forward off the seat - so the ACTION reads in one frame.
# facing 205 aimed him within 3 deg of the lens: a1 made him a flat, featureless frontal mass.
# 235 is the three-quarter the contract asks for and turns him out of frame, away from the cage.
person("watchman", "Sitting_Exit", at=(0.75, -0.25), facing_deg=235, phase=8)
_w = person("watchman", "Idle_Torch_Loop", at=(-1.05, 1.85), facing_deg=150)
prop_lantern(_w)
# hand height, dimmer than shot_09's 80 W because this is the same night, later and burning down.
light("POINT", (-1.05, 1.85, 1.80), (-0.40, 1.10, 0.80), 45, size=0.06, color=(1.0, 0.66, 0.32))

# --- light: key flattened and pushed colder than shot_09 so the churchyard reads emptier --------
key_cold((-4.40, 3.20, 3.60), (0.40, 1.20, 0.50), energy=1900, spot_deg=52, size=0.40)
# Fill raised 60 -> 110: the key rakes the cage from behind-left, so at 60 W the whole
# camera-facing side of the rising man was unmodelled black in a1. Still the weakest fill in the
# film, and still cold - the flattening the planner asked for survives.
fill_cold((3.00, -3.80, 2.00), (0.30, 0.90, 0.50), 110)

# a1's upper third was bare fog above the far rock. A rock mass 6 m out behind the cage, off the
# guard ray and outside the key cone, puts a shape in the top right.
place("rock_face_02", at=(1.35, 3.30), rot_deg=-60)

# --- camera: 1.74 m crane up and back off the chair -------------------------------------------
# The planner's CAM_AT_END (0.55,0.35,0.95) aborted the render: at the end pose the ray reaches
# the man's chest 3.5 m out and the aim sits 0.68 m past it, just over check_sightline()'s 0.6 m
# tolerance - the exact failure the staging note predicted for aiming past him at the cage. The
# drift is cut to 0.18 m, still toward the cage, and the widening is carried by the crane.
CAM_START = (1.35, -2.35, 0.85)
CAM_END = (2.25, -3.35, 1.95)
CAM_AT = (0.70, -0.20, 0.90)
CAM_AT_END = (0.58, -0.10, 0.98)
LENS = 32
