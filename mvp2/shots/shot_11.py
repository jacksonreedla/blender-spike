# shot_11 - beat 6, cut on "In": "In eighteen thirty two the law handed anatomists the unclaimed
# poor, and the trade died." The bookend to shot_01: same gate, same wet cobbles, same left-to-right
# crossing - but a man walking upright at 0.94 m/s instead of a crouch scuttling at 0.6, and the
# camera cranes BACK and UP off him onto the shut gate instead of pushing in. Set, dressing,
# staging and camera are the planner's, solved against the real 32 mm frustum.
sc = reset()

# --- dressing: the lawful world, so the fog is thinner than shot_01's 0.011 --------------------
night(world_strength=0.26, fog=0.008, aniso=0.60)

# --- set: gate_set() unchanged - its practical lamp at (-2.15,2.85) and its two spots do all the
# lighting, exactly as in shot_01. No extra key: the register change is the gait and the emptiness.
gate_set()

# Barrel moved left (shot_01 had it at frame right) so the right half of the cobbles is bare.

# --- the man: upright, unhurried, crossing left to right in front of the shut gate --------------
# facing 270 makes local +Y point +X, so Walk_Loop's 0.94 m/s carries him from (-0.95,-0.55) at
# frame 1 to (-0.05,-0.55) at the cut - centre frame, the gate behind him, feet on the cobbles.
person("robber", "Walk_Loop", at=(-0.95, -0.55), facing_deg=270, travel=0.94)

# --- camera: 1.88 m crane back and up, panning off him onto the iron --------------------------
# The aim STARTS on him (1.9 m out) so check_sightline() treats him as the subject and cannot
# abort on the figure filling the lens, then drifts to the gate plane (y=0.05, z=1.65) as the
# camera withdraws and he walks out of the widening frame. The barrel sits ~0.9 m off the ray.
CAM_START = (-0.55, -2.45, 0.90)
CAM_END = (-1.25, -3.95, 1.80)
CAM_AT = (-0.95, -0.55, 1.05)
CAM_AT_END = (0.00, 0.05, 1.65)
LENS = 32
