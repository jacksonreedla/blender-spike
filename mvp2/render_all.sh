#!/bin/bash
# v2 PS1 render, all shots, flock-serialised; run under systemd-run --user
set -u
cd /home/apollo/blender-spike
echo "RENDER_START $(date -u +%FT%TZ)"
export MVP_PS1=1 MVP_SETS=1
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_01.py anim /home/apollo/blender-spike/mvp2/renders/shot_01 38 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_02.py anim /home/apollo/blender-spike/mvp2/renders/shot_02 49 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_03.py anim /home/apollo/blender-spike/mvp2/renders/shot_03 36 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_04.py anim /home/apollo/blender-spike/mvp2/renders/shot_04 39 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_05.py anim /home/apollo/blender-spike/mvp2/renders/shot_05 36 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_06.py anim /home/apollo/blender-spike/mvp2/renders/shot_06 33 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_07.py anim /home/apollo/blender-spike/mvp2/renders/shot_07 42 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_08.py anim /home/apollo/blender-spike/mvp2/renders/shot_08 90 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_09.py anim /home/apollo/blender-spike/mvp2/renders/shot_09 54 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_10.py anim /home/apollo/blender-spike/mvp2/renders/shot_10 43 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_11.py anim /home/apollo/blender-spike/mvp2/renders/shot_11 51 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
flock out/.render.lock ./blender/blender -b --python-exit-code 1 -P mvp/runner.py -- /home/apollo/blender-spike/mvp2/shots/shot_12.py anim /home/apollo/blender-spike/mvp2/renders/shot_12 75 2>&1 | grep -E 'MVP_RESULT|Error|Traceback|SIGHTLINE' | tail -2
echo "RENDER_DONE $(date -u +%FT%TZ)"
