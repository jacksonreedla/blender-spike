"""Run one MVP shot script as a judged still or a rendered animation.

  blender -b -P mvp/runner.py -- <shot.py> still <out.png> [samples]
  blender -b -P mvp/runner.py -- <shot.py> anim <outdir> <frames> [samples] [width height]

A shot script uses the preamble helpers (reset/world/ground/place/light/box/...)
and defines the camera as data, never by calling camera() itself:

    CAM_START = (x, y, z)      # metres, frame 1
    CAM_END   = (x, y, z)      # metres, last frame (slow move: 0.3-1.5 m)
    CAM_AT    = (x, y, z)      # what the camera looks at, both frames
    LENS      = 45             # mm, optional (default 45)
    CAM_AT_END = (x, y, z)     # optional: pan the aim point too

A still renders the MIDPOINT of the move (representative frame) after checking
the sightline at start, mid and end. Nothing else about the scene changes
between still and anim, so a judged still is what the video will show.
Always run from ~/blender-spike (relative texture paths) under the render flock.
"""
import os
import sys
import time

import bpy

HERE = "/home/apollo/blender-spike"
os.chdir(HERE)
argv = sys.argv[sys.argv.index("--") + 1:]
shot_path, mode = argv[0], argv[1]

ns = {}
exec(compile(open(f"{HERE}/scenes/preamble.py").read(), "preamble.py", "exec"), ns)
exec(compile(open(f"{HERE}/mvp/helpers.py").read(), "helpers.py", "exec"), ns)
ns["SHOT_FRAMES"] = int(argv[3]) if mode == "anim" else 48
if os.environ.get("MVP_SETS") == "1":
    exec(compile(open(f"{HERE}/mvp2/sets.py").read(), "sets.py", "exec"), ns)
    exec(compile(open(f"{HERE}/mvp2/cast.py").read(), "cast.py", "exec"), ns)
exec(compile(open(shot_path).read(), shot_path, "exec"), ns)
if os.environ.get("MVP_PS1") == "1":
    ns["os"] = os
    exec(compile(open(f"{HERE}/mvp2/ps1.py").read(), "ps1.py", "exec"), ns)
    ns["ps1_pass"](bpy.context.scene)

for k in ("CAM_START", "CAM_END", "CAM_AT"):
    if k not in ns:
        raise SystemExit(f"shot script must define {k}")
start, end, at = tuple(ns["CAM_START"]), tuple(ns["CAM_END"]), tuple(ns["CAM_AT"])
at_end = tuple(ns.get("CAM_AT_END") or at)
lens = float(ns.get("LENS", 45))
sc = bpy.context.scene
sc.render.fps, sc.render.fps_base = 24, 1.0

cam = ns["camera"](start, at, lens)
target = cam.constraints[0].target
check = ns["check_sightline"]


def _set(t, loc, aim):
    cam.location = loc
    target.location = aim
    ns["_SIGHTLINE_TARGET"] = ns["Vector"](aim)
    bpy.context.view_layer.update()


mid = tuple((a + b) / 2 for a, b in zip(start, end))
mid_at = tuple((a + b) / 2 for a, b in zip(at, at_end))
for label, loc, aim in (("start", start, at), ("mid", mid, mid_at), ("end", end, at_end)):
    _set(0, loc, aim)
    try:
        check()
    except RuntimeError as e:
        raise SystemExit(f"{label}: {e}")

if mode == "still":
    out = argv[2]
    if len(argv) > 3:
        sc.eevee.taa_render_samples = int(argv[3])
    _set(0, mid, mid_at)
    sc.frame_set(int(os.environ.get("MVP_STILL_FRAME", "24")))   # mid-clip, so character actions read
    sc.render.filepath = out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"MVP_RESULT mode=still out={out} seconds={time.time() - t0:.1f} "
          f"res={sc.render.resolution_x}x{sc.render.resolution_y} samples={sc.eevee.taa_render_samples}")
elif mode == "anim":
    outdir, frames = argv[2], int(argv[3])
    if len(argv) > 4:
        sc.eevee.taa_render_samples = int(argv[4])
    if len(argv) > 6:
        sc.render.resolution_x, sc.render.resolution_y = int(argv[5]), int(argv[6])
    os.makedirs(outdir, exist_ok=True)
    _set(0, start, at)
    cam.keyframe_insert("location", frame=1)
    target.keyframe_insert("location", frame=1)
    _set(0, end, at_end)
    cam.keyframe_insert("location", frame=frames)
    target.keyframe_insert("location", frame=frames)
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.filepath = outdir.rstrip("/") + "/f_"
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    dt = time.time() - t0
    print(f"MVP_RESULT mode=anim outdir={outdir} frames={frames} seconds={dt:.1f} per_frame={dt / frames:.2f} "
          f"res={sc.render.resolution_x}x{sc.render.resolution_y} samples={sc.eevee.taa_render_samples}")
else:
    raise SystemExit(f"unknown mode {mode}")
