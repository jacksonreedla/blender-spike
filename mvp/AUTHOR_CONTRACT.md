# Shot author contract (MVP explainer)

You write ONE file, `mvp/shots/shot_NN.py`, a plain Python script that builds a Blender
scene with the helpers below and defines the camera as DATA. `mvp/runner.py` prepends the
helpers, executes your file, places the camera, checks the sightline at the start, middle and
end of the move, and renders. Nothing else. Render it yourself as a still and LOOK at it
before you hand it in.

## Render (always from ~/blender-spike, always under the flock; ~6-10 s)
```
cd /home/apollo/blender-spike && flock out/.render.lock ./blender/blender -b --python-exit-code 1 \
  -P mvp/runner.py -- mvp/shots/shot_NN.py still mvp/stills/shot_NN_aK.png 2>&1 | grep -E "MVP_RESULT|Error|Traceback|SIGHTLINE|WARNING"
```
`MVP_RESULT` on stdout = it rendered. A `SIGHTLINE BLOCKED` line names the object on the
camera-subject ray: move it. Then `Read` the PNG and describe what you see, honestly.

## The file
```python
# shot_03.py - <one line: what the viewer sees>
sc = reset()                                   # EEVEE Next, 1080x1920, 32 samples (do not change)
world(color=(0.01, 0.012, 0.02), strength=0.5, fog=0.012)
ground(texture="cobblestone_03", scale=3.0, wet=0.8)
place("gothic_statue", at=(0, 1.5), rot_deg=180)
place("rock_face_01", at=(-3.5, 4.0), rot_deg=20)
light("SPOT", (2.5, -2.0, 4.0), (0, 1.5, 1.0), 2500, size=0.3, color=(1.0, 0.9, 0.8), spot_size=0.7)
light("AREA", (-5, -4, 3), (0, 1.5, 1.0), 60, size=6, color=(0.6, 0.7, 1.0))
CAM_START = (0.4, -6.0, 1.6)                   # metres; the move is SLOW: 0.3-1.5 m total
CAM_END   = (0.4, -5.0, 1.6)
CAM_AT    = (0, 1.5, 1.1)                      # aim point (mid-height of the subject)
LENS      = 45                                 # mm; 35-50 for wides, 50-85 for details
# CAM_AT_END = (...)                           # optional: pan the aim point across the move
```
Do NOT call `camera()` or `render()` yourself; do not set resolution/samples/fps; do not
import bpy for things the helpers do. You MAY use `bpy` for what they cannot: `obj.location.z = h`
to elevate a placed model (there is no `z=`), `obj.scale`, an emissive sphere for a visible bulb,
keyframes on a light's `energy` for a flicker (frames 1..N are the shot; N is unknown to you, so
keyframe by `sc.frame_current`-independent means: use a driver or skip it).

## Helpers (units: metres, degrees for rot_deg, watts, mm; spot_size in RADIANS)
- `reset()` -> scene. `world(color, strength, hdri=None, fog=0.015, anisotropy=0.4)`: `hdri="/home/apollo/blender-spike/assets/studio.hdr"` is a moonless night sky; fog > 0.03 is clamped; strength 0.3-1.0 (below 0.3 fog has nothing to scatter).
- `ground(size=80, color=..., rough=0.35, texture=None, scale=6.0, wet=0.0)`: ALWAYS pass a texture (`cobblestone_03 | brown_mud_dry | coast_sand_03 | aerial_rocks_02 | asphalt_03 | anti_slip_concrete`); `scale` = metres per tile (2-4 for cobbles/mud near camera; 8 made concrete look like stickers); `wet` 0.6-0.9 for reflections.
- `place(name, at=(x, y), rot_deg=0, scale=1.0)` -> root empty, base on the ground, centred on `at`. Models (size x,y,z m): barrel_03 .63x.64x.93 · boulder_01 1.27x1.83x1.0 · namaqualand_boulder_02 2.53x1.23x.88 · moon_rock_01 .21x.11x.08 · rock_face_01 4.95x3.83x3.56 · rock_face_02 2.71x2.13x2.47 · coastal_cliff_01 92x11x10 (background only) · dead_tree_trunk 3.05x.28x.29 (lies flat) · dining_chair_02 .43x.58x.97 · gothic_statue 1.48x1.56x1.74 (crowned, chained, on its own base) · marble_bust_01 .27x.30x.52 · large_iron_gate 2.95x.10x2.93 · street_lamp_01 .70x.39x3.87 · brass_diya_lantern .12x.12x.38.
- `lamp(at=(x, y), toward=(x, y), energy=1600, color=(1.0, .8, .55), rot_deg=0)`: street lamp WITH its bulb correctly offset out of the housing (a light inside the head = black frame).
- `light(kind, location, at, energy, size=1.0, color=(1,1,1), spot_size=1.0)`: kind SPOT|AREA|POINT|SUN, aimed at `at`. Key: SPOT 1500-4000 W at 3-6 m or POINT 300-1200 W at 2-4 m; fill AREA 40-150 W from the other side; size = softness. SUN energy is W/m2 (0.5-3).
- `box(size=(sx, sy, sz), at=(x, y), color, rough, rot_deg)`: rests on the ground; a "slab in the air" needs `.location.z` set after. `material(name, color, rough, metal, emit)` for emissive bulbs.

## What the judges reject (all measured on real frames)
- "Product shot / lightbox / asset preview": a lone object on a flat plane. Give every frame an environment beside and behind the subject, a textured ground, fog with a visible light cone, and deep shadow.
- Dead space: the top 45-60% of a 9:16 frame empty or solid black. Fill it: rock faces, a wall box, the lamp head, fog glow, the gate.
- A visible plane edge / hard horizon seam. Enlarge the ground, put geometry or fog at the horizon.
- No contact shadow ("pasted on"). Keep world strength low and one hard key so objects sit.
- Subject too small (< 15% frame height) or too big; the camera at eye level dead-centre. Prefer knee-to-chest height, subject on a third, 3-7 m back.
- Under-exposed "moody" = unreadable. Dark and moody means a LIT subject with deep shadow around it.
- Anything on the camera-subject line (the runner refuses to render it).
- The wrong model for the noun (a diya is not a lantern; the chair is upholstered; the statue is a crowned monument).

## Hand-in
Report: the file path, the still path (final attempt), what the still shows in two sentences, and
any deviation from the shot spec with the reason.
