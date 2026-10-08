# shot_04 - beat 2, cut on "taking": "A body belonged to no one, so taking it was not theft."
# Third angle on the same plot as shots 02/03. The lift, backlit: every light is behind the
# lifter and the camera rises from ankle to hip height as he takes the weight.
sc = reset()
night()

# --- set: the same churchyard plot, the same open grave ---------------------------------------
churchyard(seed=11, avoid=(0, 0, 2.6))
open_grave(at=(0.0, 0.0), rot_deg=75)

# --- characters: the lifter over the corpse ----------------------------------------------------
# PickUp_Table is 20 f; phase=-10 has him mid-lift from frame 1, so the action is underway on the cut.
person("robber", "Fixing_Kneeling", at=(0.25, -1.35), facing_deg=175, phase=-10)
# Death01 is 58 f; phase=-45 puts the body down before frame 1. Lying at 157 deg (planned 100) it
# runs from his feet toward the lens instead of off the left edge - at this lens the frame is only
# ~1.3 m wide at the body, and the planned angle put its head and shoulders outside it. Cloth lifted
# off the lifter's near-black so the corpse is a separate shape at 320 px.
person("corpse", "Death01", at=(0.40, -1.75), facing_deg=157, freeze_at=50)
# character() cycles every clip so it loops, which stands a corpse back UP 13 frames in (measured:
# 0.29 m tall at frame 12, 1.53 m at frame 24). Dropping the cycle modifiers on Death01 only holds
# its last keyframe instead: the body stays down for the whole shot.
for _fc in bpy.data.actions["Death01"].fcurves:
    for _m in list(_fc.modifiers):
        _fc.modifiers.remove(_m)

# --- light: all of it BEHIND him. The silhouette is the shot. ----------------------------------
key_cold((-2.20, 3.60, 2.80), (0.20, -1.00, 1.10), energy=2800, spot_deg=34, size=0.18)
fill_cold((2.60, -3.80, 1.50), (0.20, -1.20, 0.90), 40)

# --- camera: front, ankle height rising to hip height, tightest lens in the film ---------------
# Pulled back from the planned y=-4.15/-3.35: at 2.5 m this 40 mm frames only 1.3 m of width and the
# first render was one unreadable dark mass. At ~4.6 m the lifter is ~43% of frame height, the body
# is inside the frame, and the aim at 0.88 keeps the fog band above his head thin.
CAM_START = (0.52, -6.20, 0.40)
CAM_END = (0.26, -5.40, 0.96)
CAM_AT = (0.25, -1.25, 0.88)
LENS = 40
