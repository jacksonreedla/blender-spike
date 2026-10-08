# shot_02 - beat 1 (hook), cut on "England".
# "Stealing a corpse in Georgian England was barely a crime."
# A man kneels at the lip of a half dug grave with his hands in the earth while a second sneaks in
# past the camera. Camera side: right, 1.12 m push-in dropping toward the pit lip.
sc = reset()
night()                                                   # world 0.26, fog 0.014, aniso 0.6
churchyard(seed=11, avoid=(0, 0, 2.6))                    # lamp burns far behind at (-2.4, 9.0)
open_grave(at=(0.0, 0.0), rot_deg=75)                     # spoil heap (-0.97,+0.26), slab (-1.47,+0.70)

# The kneeler: facing 215 with phase=-60 on the 125-frame clip puts his hands over the hole
# (lifted verbatim from the rendered still mvp2/stills/char_test2.png). Pit radius 1.41 > 1.15,
# so he kneels 0.12 m outside the dug edge and does not float over the depression.
_d = person("robber", "Fixing_Kneeling", at=(0.9, 0.9), facing_deg=215, phase=-60)
hold(_d, prop_shovel(), "hand_r", offset=(0, 0.12, 0), rot_deg=(90, 0, 0))
# was rendered (a1) and put his body across ndc x -0.81..-0.21 at the cut, exactly over the grave
# (the pit projects to -0.81..-0.05), so the hole the line is about was erased, and his head
# clipped the left edge. Mirrored: he enters at ndc +1.05 on frame 1, is at +0.78 and 40% of frame
# height at the cut, still crossing toward the pit and past the lens. Pit radius 4.2 at every
# frame, and 1.2 m clear of the guard ray at frame 1, where check_sightline() runs.
person("robber2", "Crouch_Fwd_Loop", at=(2.05, -1.20), facing_deg=120, travel=0.6)

# DEVIATION 2 - the key is raked low from the NORTH-WEST instead of high from the west. At the
# planned 42 deg elevation the spot poured straight into the grave: a1 rendered the pit interior
# as bright as the mud around it, so no hole read at all. From (-4.00,2.60,1.70) the beam runs
# south-east at 17 deg, so the only inner wall the camera can see (the north end's, which faces
# south) is turned away from the light and goes black, the north lip crest catches the rake, and
# the churned earth and spoil heap throw long shadows toward the lens. Energy is up because a
# grazing beam delivers ~0.43x the irradiance of the old steep one.
key_cold((-4.00, 2.60, 1.70), (0.40, 0.20, 0.20), energy=4200, spot_deg=44, size=0.30)
fill_cold((2.80, -3.60, 1.35), (0.90, -1.40, 0.50), 80)

# DEVIATION 3 - the whole camera path is 0.45 m higher, aim 0.18 m lower, same 1.12 m move.
# Measured: the grave's own near lip hides its interior below ~31 deg of depression, and the
# planned 1.15 m eye had 7.6 deg, so a1 showed a lit crack. At 1.60 m and -15.4 deg the far wall
# AND floor clear the lip: a dark slot 13% of frame height at ndc x -0.34. It also lifts the lamp
# head to ndc y +0.75 and the rock face to +0.73, filling the top of frame that a1 left dead.
CAM_START = (1.72, -4.55, 1.80)
CAM_END = (1.05, -3.75, 1.40)
CAM_AT = (0.42, 0.40, 0.32)
LENS = 32
