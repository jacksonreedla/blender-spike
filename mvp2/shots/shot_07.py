# shot_07 - beat 3, cut on "men": "Anatomy schools paid cash, the hangman sent too few, so men
# went digging at night." Three men working two graves at once - the line is the NUMBER of them,
# so they are stacked in depth (2.6 / 3.6 / 4.0 m) down a 28 mm portrait frustum that is only
# +-19.9 deg wide. Camera dives in over the nearest man.
sc = reset()
night(fog=0.013)

# --- set: the churchyard plot, an opened grave and a still-mounded fresh one -------------------
# The spoil heap (-1.24,1.44) and the dragged slab (-1.17,2.11) come out of open_grave itself at
# rot 20; fresh_grave puts its rough head stone at (1.50,2.90). Nothing extra to place.
churchyard(seed=5, lamp_at=(2.80, 8.40), statue_at=(-2.60, 7.40), avoid=(-0.9, 0.5, 2.8))
open_grave(at=(-0.90, 0.50), rot_deg=20)
fresh_grave(at=(1.50, 1.60))

# --- three men, spread in depth ----------------------------------------------------------------
# Fixing_Kneeling is 125 f; phase=-60 has him already down and working at frame 1.
_d = person("robber", "Fixing_Kneeling", at=(-0.45, -0.25), facing_deg=30, phase=-60)
hold(_d, prop_shovel(), "hand_r", offset=(0, 0.12, 0), rot_deg=(90, 0, 0))
person("robber2", "Fixing_Kneeling", at=(0.75, 0.35), facing_deg=330, travel=0.12)        # shoving at the new mound
# The planner crossed him left-to-right at facing 300; measured on render a1 his screen span
# (-0.75..+0.17) sat on top of the kneeler (-0.91..-0.25) and the two near men read as ONE black
# mass. Mirrored: he now crosses right-to-left across the foreground and still lands at frame
# centre on the cut (0.24,-1.36 at f34, 1.34 m off the lens), clear of the kneeler and stacked
# BELOW the pusher, who is 1.7 m deeper and sits in the upper half.
person("robber", "Crouch_Fwd_Loop", at=(0.95, -0.95), facing_deg=120, travel=0.6)  # a shade off black so his edge cuts the pusher behind him
# (a1 at 0.10 the camera-side fill made him a pale grey mass that owned the frame; 0.075 keeps the
#  separating edge and puts him back among the other two as a dark body.)

# --- light: hard key from frame-left across the workings, cold fill from the camera side -------
key_cold((-4.20, 1.00, 4.00), (0.20, 0.60, 0.30), energy=3000, spot_deg=46, size=0.30)
fill_cold((3.40, -3.60, 1.60), (0.00, 0.00, 0.40), 80)

# --- camera: front and high, 1.18 m dive-in over the nearest man --------------------------------
CAM_START = (0.05, -3.60, 2.05)
CAM_END = (0.35, -2.70, 1.35)
CAM_AT = (0.15, 0.35, 0.35)
LENS = 28
