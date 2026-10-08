# mvp2 state (2026-09-16 ~00:xx UTC) — resume point after compaction

GOAL: v2 of "The Graves That Wore Iron" per operator feedback: PS1 aesthetic, body model, faster lo-fi voice,
more happening on screen. Operator liked v1's look; voice speed 1.3x chosen by default (samples sent, no reply yet).

DONE: script.json (73 words, 6 beats, 12 word-cut shots), narration at 1.3x + lo-fi -> audio/lofi, script.timed.json,
render_plan.json (586 frames, 24.4 s), render_all.sh (MVP_PS1=1, flock), sets.py (gate_set, churchyard, open_grave,
fresh_grave, mortsafe, character() with 43 CC0 Quaternius clips), ps1.py pass, runner still-frame 24, AUTHOR_CONTRACT.md.
Author agents wrote shots 02-11 (a1 stills for 02-10 exist, UNJUDGED: subagent session cap hit, resets 23:30 UTC).
Shots 01 and 12 have NO file yet; shot_11 has a file but no still.

NEXT (in order): 1) view stills/shot_0[2-8]_a1.png (scale=540:960:flags=neighbor), fix by hand if needed;
2) write shots/shot_01 and shot_12 by hand from script.json staging_notes (contract: sets + character helpers);
3) render: systemd-run --user --unit=mvp2-render --collect --working-directory=/home/apollo/blender-spike
   /bin/sh -c "exec ./mvp2/render_all.sh > mvp2/logs/render.log 2>&1"  (~0.7 s/frame -> ~7 min); Monitor for RENDER_DONE;
4) /home/apollo/clipvault/.venv/bin/python mvp2/assemble.py post  -> final/graves-that-wore-iron.mp4, QC;
5) SendUserFile (<30 MiB; make a -delivery.mp4 at crf 24 if needed); 6) update mvp2/README (copy mvp/README shape),
   project.json slice, PROJECT-3D.md, memory note blender-mvp-pipeline.
Known: Death01 clip is 58 f with a flat window at 37-57 only -> a corpse "re-falls" in long shots (use phase=-24 and
accept, or pin with travel=0 + a short shot). character() grounds feet at z=0 and does not follow terrain.
