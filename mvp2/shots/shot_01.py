# shot_01 - hook, cut on "Stealing": a crouched man scuttles across the wet cobbles in front of the locked gate.
sc = reset()
night(world_strength=0.22, fog=0.011, aniso=0.75, color=(0.004, 0.006, 0.012))
gate_set()
person("robber", "Crouch_Fwd_Loop", at=(-0.55, -0.8), facing_deg=270, travel=0.6)
CAM_START = (0.55, -3.05, 0.42); CAM_END = (0.30, -2.10, 0.86); CAM_AT = (0.00, 0.05, 1.70); LENS = 28
