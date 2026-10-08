# shot_03 - beat 2 "context", cut on "body".
# "A body belonged to no one, so taking it was not theft."
# Same plot as shot_02, nothing in the set moved; camera crosses to the LEFT and falls onto the corpse.
sc = reset()
night()                                                     # world 0.26 / fog 0.014 / aniso 0.6

# --- set: the dug plot, unchanged from shot_02 ------------------------------------------------
churchyard(seed=11, avoid=(0, 0, 2.6))                      # lamp far behind at (-2.4, 9.0), statue at (2.4, 7.9)
open_grave(at=(0.0, 0.0), rot_deg=75)                       # pit + spoil heap at (-0.97,0.26), slab at (-1.47,0.70)

# --- dressing: a lantern set down on the mud, and the POINT that is its actual light -----------
place("brass_diya_lantern", at=(-0.30, -2.55))              # foreground left, 0.7 m below the guard ray
light("POINT", (-0.30, -2.55, 0.42), (0.55, -1.45, 0.25), 34, size=0.05, color=(1.0, 0.70, 0.34))

# --- the body out of the ground, and the man going through its clothes -------------------------
# Death01 measured: the figure is only flat and still for clip frames 37-57 of 58, and it lies
# 2.2 m along its local +Y from the root. facing 85 lays it broadside across the lens, head to the
# grave; phase -24 puts clip frame 48 (flat, motionless) on the still frame.
person("corpse", "Death01", at=(1.15, -1.55), facing_deg=85, freeze_at=50)
person("robber", "Fixing_Kneeling", at=(0.45, -0.95), facing_deg=180, phase=-60)   # over the torso, hands working
person("robber2", "Crouch_Idle_Loop", at=(2.10, -0.15), facing_deg=200)             # his mate waiting clear of the pit

# --- light -------------------------------------------------------------------------------------
key_cold((-3.40, 0.20, 3.80), (0.30, -1.10, 0.30), energy=2000, spot_deg=36, size=0.20)
fill_cold((3.20, -3.40, 1.40), (0.00, -0.80, 0.30), 70)

# --- camera: left of the plot, dropping 0.86 m as it pushes in; 1.60 m of move at 0.94 m/s ------
# Pitched 23 deg down so the statue and the far rock mass sit in the top of frame, not black sky.
CAM_START = (-1.95, -6.60, 3.05)
CAM_END = (-0.90, -5.70, 2.19)
CAM_AT = (0.38, -1.22, 0.35)
LENS = 35
