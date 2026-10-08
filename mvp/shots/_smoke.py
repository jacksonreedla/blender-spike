# smoke: the hand-built lamp scene (out/smoke_env2.png) in runner form
sc = reset()
world(color=(0.01, 0.012, 0.02), strength=0.5, fog=0.012)
ground(texture="cobblestone_03", scale=3.0, wet=0.8)
place("rock_face_01", at=(-3.5, 4.0), rot_deg=20)
place("rock_face_02", at=(3.5, 3.5), rot_deg=-30)
place("gothic_statue", at=(0, 1.5), rot_deg=180)
lamp(at=(2.2, 0.5), toward=(0, 1.5))
light("AREA", (-5, -4, 3), (0, 1.5, 1.0), 60, size=6, color=(0.6, 0.7, 1.0))
CAM_START = (0.4, -6.0, 1.6)
CAM_END = (0.4, -5.0, 1.6)
CAM_AT = (0, 1.5, 1.1)
LENS = 45
