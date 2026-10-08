sc = reset(); night(fog=0.014, aniso=0.6); churchyard(seed=9, statue_at=None, avoid=(0, 0, 3.0))
top = gallows(at=(0.0, 0.0), rot_deg=0)
hanged((0.0, 0.0, top[2]), 0)
key_cold((-3.5, -3.0, 2.4), (0.0, 0.0, 1.6), energy=2200, spot_deg=32, size=0.2); fill_cold((3.0, -3.0, 1.5), (0, 0, 1.4), 60)
CAM_START = (1.6, -5.2, 0.5); CAM_END = (1.0, -4.3, 0.7); CAM_AT = (0.0, 0.0, 1.6); LENS = 28
