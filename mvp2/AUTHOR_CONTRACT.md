# v2 shot author contract (PS1 explainer)

You write ONE file `mvp2/shots/shot_NN.py`. The runner prepends the preamble helpers, `mvp/helpers.py`
and `mvp2/sets.py`, executes your file, applies the PS1 pass (320x569, decimation, flat shading, 64 px
texels), places the camera from your CAM_* data, checks the sightline, renders. Render a still yourself,
LOOK at it, fix, hand in.

## Render (from ~/blender-spike, under the flock, ~2 s)
```
cd /home/apollo/blender-spike && MVP_PS1=1 MVP_SETS=1 flock out/.render.lock ./blender/blender -b --python-exit-code 1 \
  -P mvp/runner.py -- mvp2/shots/shot_NN.py still mvp2/stills/shot_NN_aK.png 2>&1 | grep -E "MVP_RESULT|Error|Traceback|SIGHTLINE"
```
The still is rendered at frame 24 (1 s in) so clips are mid-action. View it upscaled: `ffmpeg -y -i <png> -vf scale=540:960:flags=neighbor <out>`.

## The file (everything is a helper call; no bpy needed)
```python
sc = reset()
night(world_strength=0.26, fog=0.014, aniso=0.6)                 # dark world + fog (fog <= 0.03)
churchyard(seed=11, lamp_at=(-2.4, 9.0), statue_at=(2.4, 7.9), avoid=(0, 0, 2.6))   # or gate_set()
open_grave(at=(0.0, 0.0), rot_deg=75)                            # or fresh_grave(at) / mortsafe(at, rot_deg)
character("Fixing_Kneeling", at=(0.9, 0.9), facing_deg=215, phase=-60)   # returns the root empty
character("Crouch_Fwd_Loop", at=(-1.6, -1.2), facing_deg=90)             # locomotion clips cross the frame
key_cold((-3.6, -0.4, 4.3), (0.4, 0.5, 0.6), energy=2600, spot_deg=40, size=0.3)
fill_cold((2.7, -3.7, 1.25), (0.1, -1.0, 0.05), 60)
CAM_START = (1.6, -4.6, 1.3); CAM_END = (0.9, -4.4, 1.2); CAM_AT = (0.5, 0.4, 0.55); LENS = 32
```
- `character(clip, at, facing_deg, travel=None, phase=0, cloth=(r,g,b), scale=1.0)`: 1.8 m dark figure, feet on
  the ground. facing_deg 0 = away from a camera on -Y, 180 = toward it, 90 = frame-left... (it faces local +Y).
  Locomotion clips (Walk_Loop 0.94 m/s, Jog_Fwd_Loop 2.4, Sprint_Loop 4.5, Crouch_Fwd_Loop 0.6) really move
  across the shot along their facing; `travel=0` pins them. `phase=-N` starts the clip N frames in (use for
  Fixing_Kneeling 125 f, PickUp_Table 20 f, Death01 58 f, Sitting_Enter so the action is underway at frame 1).
  Clips: Idle_Loop Idle_Talking_Loop Idle_Torch_Loop Walk_Loop Walk_Formal_Loop Jog_Fwd_Loop Sprint_Loop
  Crouch_Fwd_Loop Crouch_Idle_Loop Fixing_Kneeling PickUp_Table Push_Loop Interact Sitting_Enter Sitting_Idle_Loop
  Sitting_Exit Punch_Jab Punch_Cross Roll Death01 Hit_Chest Hit_Head Jump_Start Jump_Loop Jump_Land.
- Sets: `gate_set()`, `churchyard(seed, lamp_at, lamp_toward, statue_at, wall_y, avoid)`, `open_grave(at, rot_deg)`,
  `fresh_grave(at, rot_deg)`, `mortsafe(at, rot_deg)`, `mud_ground()`, `cobble_ground()`, `headstones(n, seed, cx, cy)`.
  Lights: `key_cold(location, at, energy, spot_deg, size)`, `fill_cold(location, at, energy)`, `lamp(at, toward, energy, color)`,
  plus the base helpers `place(name, at, rot_deg, scale)`, `tbox(size, at, texture, tiles, rot_deg, tilt_deg, z)`, `box`, `light`, `world`.
- Camera: CAM_START/CAM_END in metres over the shot (2 s shots take 0.3-2 m of travel), CAM_AT = a point ON the
  subject (the guard raycasts to it), LENS mm. Optional CAM_AT_END for a pan.

## What reads on a phone at 320 px wide
- The action must read from posture at 15-40% frame height; frame the figure from knee height, three-quarter, not
  eye-level frontal. A character crossing a lit pool of light reads; a figure in fog does not.
- Fill the top of the frame (lamp head, rock mass, statue, gate arch); no empty black upper third.
- Something must MOVE: a clip that changes pose, a crossing, or a camera move with intent. Idle_Loop alone is dead.
- Keep the camera-subject line clear (the runner refuses to render a blocked one).

## Hand-in
Report: file path, final still path, what the still shows (two honest sentences), deviations from the plan and why.
