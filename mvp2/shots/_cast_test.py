sc = reset(); night(); churchyard(seed=11, avoid=(0, 0, 2.6)); open_grave(at=(0.0, 0.0), rot_deg=75)
d = person("robber", "Fixing_Kneeling", at=(0.9, 0.9), facing_deg=215, phase=-60); hold(d, prop_shovel(), "hand_r", offset=(0, 0.12, 0), rot_deg=(90, 0, 0))
person("robber2", "Crouch_Idle_Loop", at=(1.9, 0.2), facing_deg=200)
w = person("watchman", "Idle_Torch_Loop", at=(-1.4, 2.2), facing_deg=160); prop_lantern(w)
person("anatomist", "Idle_Talking_Loop", at=(-2.2, -0.6), facing_deg=120)
person("corpse", "Death01", at=(0.3, -1.6), facing_deg=90, freeze_at=50)
key_cold((-3.6, -0.4, 4.3), (0.4, 0.5, 0.6), energy=2600, spot_deg=40, size=0.3); fill_cold((2.7, -3.7, 1.25), (0.1, -1.0, 0.05), 90)
CAM_START = (1.2, -4.8, 1.4); CAM_END = (0.9, -4.4, 1.2); CAM_AT = (0.3, 0.4, 0.7); LENS = 30
