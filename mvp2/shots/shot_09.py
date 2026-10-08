# shot_09 - beat 5, cut on "Watchmen": "Watchmen sat up in the churchyard for weeks, until the
# body was worthless." The vigil, not the theft: a watchman stands over the caged grave with a
# lantern at his raised hand, a second sits the night out on a chair in the near-right foreground,
# and a robber jogs away through the fog behind them and LEAVES frame before the cut.
# Coordinates are the planner's, solved against the real 35 mm portrait frustum.
sc = reset()
night(fog=0.018, aniso=0.40)

# --- set: churchyard with the cage mid-ground; no statue, the lamp is off frame left -----------
# avoid keeps the scattered headstones 2.6 m clear of the cage plot AND off the camera-aim line.
churchyard(seed=2, lamp_at=(-5.50, 9.50), statue_at=None, avoid=(0.4, 1.2, 2.6))
mortsafe(at=(0.40, 1.20), rot_deg=-15)

# --- dressing: the vigil's furniture. The chair is under the seated man; the diya burns at his
# feet as a warm floor source, and the standing watchman's raised hand gets its own POINT light
# (Idle_Torch_Loop carries no torch mesh and emits nothing). -----------------------------------
place("dining_chair_02", at=(0.75, -0.25), rot_deg=140)
place("brass_diya_lantern", at=(0.30, -0.75))
light("POINT", (0.30, -0.75, 0.45), (0.30, 0.40, 0.60), 55, size=0.05, color=(1.0, 0.68, 0.34))
light("POINT", (-0.60, 0.75, 1.80), (0.20, 1.10, 0.70), 80, size=0.06, color=(1.0, 0.66, 0.32))

# --- three figures: two keeping watch, one giving up and leaving ------------------------------
# The standing watchman is 0.69 m off the cage's short axis - outside the bars, not inside them.
_w = person("watchman", "Idle_Torch_Loop", at=(-0.60, 0.75), facing_deg=255)
prop_lantern(_w)
person("watchman", "Sitting_Idle_Loop", at=(0.75, -0.25), facing_deg=140)
# The jogger enters off the left edge, crosses dead centre at the still frame (f24) and is off
# the right edge by the cut: 2.4 m/s along facing 290 = 4.7 m over the 2 s shot.
person("robber", "Jog_Fwd_Loop", at=(-0.35, 2.60), facing_deg=290, travel=2.4)

# --- light: cold key raking in from frame right across the bars, cold fill from the camera side -
key_cold((3.60, 1.20, 3.40), (-0.60, 0.90, 1.20), energy=2400, spot_deg=40, size=0.25)
fill_cold((-3.20, -3.40, 1.50), (-0.40, 0.60, 1.00), 70)

# --- camera: 1.69 m lateral track left to right, dropping; aim just outside the near bars ------
CAM_START = (-2.55, -2.75, 1.50)
CAM_END = (-0.95, -3.25, 1.30)
CAM_AT = (0.10, 0.35, 0.95)
LENS = 35
