sc = reset(); night(); churchyard(seed=11, avoid=(0, 0, 2.6)); open_grave(at=(0.0, 0.0), rot_deg=75)
character("Fixing_Kneeling", at=(0.9, 0.9), facing_deg=215, phase=-60)   # kneeling at the pit lip, working
character("Idle_Torch_Loop", at=(-2.2, 3.4), facing_deg=150)             # a watcher with a lantern behind
character("Crouch_Fwd_Loop", at=(-1.6, -1.2), facing_deg=90)             # a second man sneaking in from the left
key_cold((-3.6, -0.4, 4.3), (0.4, 0.5, 0.6), energy=2600, spot_deg=40, size=0.3); fill_cold((2.7, -3.7, 1.25), (0.1, -1.0, 0.05), 60)
CAM_START = (1.6, -4.6, 1.3); CAM_END = (0.9, -4.4, 1.2); CAM_AT = (0.5, 0.4, 0.55); LENS = 32
