# shot_06 - beat 3, cut on "hangman": the gallows, the only lawful supply.
sc = reset(); night(fog=0.014, aniso=0.6); churchyard(seed=9, statue_at=None, avoid=(0, 0, 3.0))
top = gallows(at=(0.0, 0.0), rot_deg=0)
hanged((0.0, 0.0, top[2]), 0)
person("watchman", "Idle_Loop", at=(-1.9, -1.2), facing_deg=40)   # a watching official
key_cold((-3.5, -3.0, 2.4), (0.0, 0.0, 1.8), energy=2200, spot_deg=32, size=0.2); fill_cold((3.0, -3.0, 1.5), (0, 0, 1.4), 60)
CAM_START = (1.9, -5.4, 0.4); CAM_END = (1.1, -4.2, 0.9); CAM_AT = (0.0, 0.0, 2.0); LENS = 28
