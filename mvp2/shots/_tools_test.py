sc = reset(); night(); churchyard(seed=11, avoid=(0, 0, 2.6)); open_grave(at=(0.0, 0.0), rot_deg=75)
d = character("Fixing_Kneeling", at=(0.9, 0.9), facing_deg=215, phase=-60, cloth=(0.28, 0.2, 0.12))
hold(d, prop_shovel(), "hand_r", offset=(0, 0.1, -0.3), rot_deg=(20, 0, 0))
w = character("Idle_Torch_Loop", at=(-1.4, 2.2), facing_deg=160, cloth=(0.12, 0.14, 0.24))
prop_lantern(w)
key_cold((-3.6, -0.4, 4.3), (0.4, 0.5, 0.6), energy=2600, spot_deg=40, size=0.3); fill_cold((2.7, -3.7, 1.25), (0.1, -1.0, 0.05), 60)
CAM_START = (1.6, -4.6, 1.3); CAM_END = (0.9, -4.4, 1.2); CAM_AT = (0.5, 0.4, 0.55); LENS = 32
