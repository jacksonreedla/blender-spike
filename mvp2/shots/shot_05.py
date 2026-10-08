# shot_05 - beat 3, cut on "Anatomy": the money changes hands over the dissecting slab.
sc = reset(); night(world_strength=0.16, fog=0.006, aniso=0.5); cobble_ground(scale=2.0, wet=0.35)
tbox((6.40, 0.30, 2.80), (0.00, 2.90), texture="cobblestone_03", tiles=3.0, name="WallBack")
tbox((0.30, 6.60, 2.80), (-3.00, 0.00), texture="cobblestone_03", tiles=3.0, name="WallL")
tbox((0.30, 6.60, 2.80), (3.00, 0.00), texture="cobblestone_03", tiles=3.0, name="WallR")
tbox((6.30, 3.60, 0.20), (0.00, 1.25), texture="cobblestone_03", tiles=3.0, z=2.80, name="Ceiling")
tbox((1.95, 0.85, 0.80), (0.30, 1.70), texture="aerial_rocks_02", tiles=1.4, name="Slab")
place("marble_bust_01", at=(-1.90, 2.35), scale=2.2); place("dining_chair_02", at=(1.85, 2.15), rot_deg=205)
coins((0.1, 1.45), n=14, z=0.80)
light("POINT", (0.30, 1.40, 2.35), (0.25, 1.20, 0.60), 380, size=0.25, color=(1.0, 0.82, 0.55))
fill_cold((0.20, -3.60, 2.00), (0.15, 1.00, 1.00), 45)
payer = person("anatomist", "Idle_Talking_Loop", at=(0.95, 0.95), facing_deg=90)   # anatomist in black, purse in hand
hold(payer, prop_purse(), "hand_r", offset=(0, 0.04, 0))
person("robber", "Idle_Talking_Loop", at=(-0.75, 0.95), facing_deg=270, phase=-20)   # resurrection man
person("corpse", "Death01", at=(0.3, 2.2), facing_deg=90, freeze_at=50)
CAM_START = (0.9, -2.7, 1.4); CAM_END = (0.1, -2.1, 1.2); CAM_AT = (0.1, 0.95, 0.95); LENS = 30
