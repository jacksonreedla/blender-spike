"""Fast lo-fi narration test: Kokoro at several speeds -> wpm, then the PS1 voice chain."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "/home/apollo/clipvault")
from clipvault import config  # noqa
from clipvault import tts
TEXT = "In Georgian England, stealing a corpse from a grave was barely a crime. A body belonged to no one, so taking it was not theft."
OUT = Path("/home/apollo/blender-spike/mvp2/audio/voicetest"); OUT.mkdir(parents=True, exist_ok=True)
words = len(TEXT.split())
for sp in (1.1, 1.3, 1.4, 1.5):
    d = tts.synth_one(TEXT, OUT / f"v_{sp}.wav", speed=sp)
    print(f"speed {sp}: {d:5.2f}s -> {words / d * 60:5.0f} wpm")
