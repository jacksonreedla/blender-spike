"""Post-production for the MVP explainer: narration -> timing -> per-shot frame plan
-> PNG sequences -> bed video + wind bed -> captions -> mix -> QC.

  python mvp/assemble.py narrate            # TTS every sentence (Kokoro 1.1x), write script.timed.json + render_plan.json
  python mvp/assemble.py render-cmds        # print the blender command per shot (run them under systemd-run + flock)
  python mvp/assemble.py post               # bed + captions + mux + qc  (needs mvp/renders/<shot>/f_0001.png ...)
  python mvp/assemble.py qc final/mvp.mp4

Run with /home/apollo/clipvault/.venv/bin/python. Reuses ClipVault's tts/narrate/
moviecaptions/longrender in place; writes only under ~/blender-spike/mvp/.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/apollo/clipvault")
from clipvault import config  # noqa: E402,F401  (must precede omni/clip_vod imports; loads ClipVault's own .env)
from clipvault import longrender as LR  # noqa: E402
from clipvault import moviecaptions, narrate, tts  # noqa: E402

MVP = Path("/home/apollo/blender-spike/mvp")
BLENDER = "/home/apollo/blender-spike/blender/blender"
FPS = 24
W, H = 1080, 1920
SAMPLES = 16
SPEED = 1.1               # Kokoro speed: ~170 wpm (tts-kokoro-calibration)
TAIL_S = 0.8              # video runs on after the last word
WIND_LUFS = -34           # synthesized brown-noise bed, well under the -16 narration
SR = 48000


def _run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:300])
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def load_script() -> dict:
    return json.loads((MVP / "script.json").read_text())


def frames_for(t0: float, t1: float) -> int:
    return max(1, round(t1 * FPS) - round(t0 * FPS))


def narrate_cmd() -> dict:
    """Synthesize every sentence at a flat 1.1x, measure, and lay out the timeline
    with narrate's gaps (0.35 s inside a beat, 0.8 s between beats, 1.2 s before a reveal)."""
    script = load_script()
    audio = MVP / "audio"
    shutil.rmtree(audio, ignore_errors=True)
    texts = [s["text"] for b in script["beats"] for s in b["sentences"]]
    lines = tts.synth_lines(texts, audio, speed=SPEED, speeds=[SPEED] * len(texts))
    script = narrate.apply_measured(script, [ln.duration_s for ln in lines])
    script["audio_dir"] = str(audio)
    script["narration_mode"] = "sentence"
    # one shot per beat: cut on the beat's first word; the last shot runs to runtime + tail
    t_end = round(script["runtime_s"] + TAIL_S, 3)
    shots, t = [], 0.0
    for i, b in enumerate(script["beats"]):
        t0 = 0.0 if i == 0 else b["start_s"]
        t1 = script["beats"][i + 1]["start_s"] if i + 1 < len(script["beats"]) else t_end
        shots.append({"id": b["shot"]["id"], "t0": round(t0, 3), "t1": round(t1, 3),
                      "frames": frames_for(t0, t1), "beat": i})
        t = t1
    plan = {"fps": FPS, "width": W, "height": H, "samples": SAMPLES, "runtime_s": script["runtime_s"],
            "video_s": t_end, "total_frames": sum(s["frames"] for s in shots), "shots": shots}
    (MVP / "script.timed.json").write_text(json.dumps(script, indent=1))
    (MVP / "render_plan.json").write_text(json.dumps(plan, indent=1))
    for ln in lines:
        print(f"  vo{ln.index:03d} {ln.duration_s:5.2f}s  {ln.text}")
    print(f"  runtime {script['runtime_s']:.2f}s, video {t_end:.2f}s, {plan['total_frames']} frames "
          f"(~{plan['total_frames'] * 2.1 / 60:.0f} min at 2.1 s/frame)")
    for s in shots:
        print(f"  {s['id']}: {s['t0']:6.2f} -> {s['t1']:6.2f}  {s['frames']:4d} frames")
    return plan


def render_cmds() -> list[list[str]]:
    plan = json.loads((MVP / "render_plan.json").read_text())
    cmds = []
    for s in plan["shots"]:
        out = MVP / "renders" / s["id"]
        cmds.append(["flock", "/home/apollo/blender-spike/out/.render.lock", BLENDER, "-b", "--python-exit-code", "1",
                     "-P", str(MVP / "runner.py"), "--", str(MVP / "shots" / f"{s['id']}.py"), "anim", str(out),
                     str(s["frames"]), str(plan["samples"]), str(plan["width"]), str(plan["height"])])
    return cmds


def bed() -> tuple[Path, Path]:
    """Per-shot PNG sequences -> h264 (no B-frames, explicit durations) -> bed.mp4; brown-noise wind -> bed.wav."""
    plan = json.loads((MVP / "render_plan.json").read_text())
    work = MVP / "work"
    work.mkdir(exist_ok=True)
    parts, durs = [], []
    for s in plan["shots"]:
        d = MVP / "renders" / s["id"]
        have = sorted(d.glob("f_*.png"))
        if len(have) < s["frames"]:
            raise SystemExit(f"{s['id']}: {len(have)} of {s['frames']} frames rendered")
        v = work / f"{s['id']}.mp4"
        _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-framerate", FPS, "-start_number", 1,
              "-i", d / "f_%04d.png", "-frames:v", s["frames"],
              "-vf", f"scale={W}:{H}:flags=lanczos,format=yuv420p", *LR.ENCODE, *LR.MP4_TIMING, "-an", v])
        parts.append(v)
        durs.append(s["frames"] / FPS)
    lst = work / "list_v.txt"
    lst.write_text(LR.concat_list(parts, durs))
    bed_v = work / "bed.mp4"
    _run(LR.concat_cmd(lst, bed_v))
    bed_a = work / "bed.wav"
    _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
          "-i", f"anoisesrc=c=brown:r={SR}:a=0.6:s=7", "-t", f"{plan['video_s'] + 1:.3f}",
          "-af", f"lowpass=f=260,highpass=f=40,tremolo=f=0.11:d=0.35,loudnorm=I={WIND_LUFS}:TP=-6:LRA=7,aformat=channel_layouts=stereo",
          "-c:a", "pcm_s16le", "-ar", SR, "-ac", 2, bed_a])
    return bed_v, bed_a


def captions() -> Path:
    script = json.loads((MVP / "script.timed.json").read_text())
    out = MVP / "captions" / "captions.ass"
    out.parent.mkdir(exist_ok=True)
    moviecaptions.write_ass(script, out, style="pop")
    return out


def mux(bed_v: Path, bed_a: Path, ass: Path) -> Path:
    script = json.loads((MVP / "script.timed.json").read_text())
    vo = [(Path(script["audio_dir"]) / s["audio"], int(round(s["start_s"] * 1000)))
          for b in script["beats"] for s in b["sentences"]]
    out = MVP / "final" / f"{script.get('slug', 'mvp')}.mp4"
    out.parent.mkdir(exist_ok=True)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", bed_v, "-i", bed_a]
    for p, _ in vo:
        cmd += ["-i", p]
    graph = f"[0:v]ass={ass}[v];" + LR.mix_graph([d for _, d in vo]).replace(
        "aresample=48000[out]", "aresample=48000,aformat=channel_layouts=stereo[out]")
    cmd += ["-filter_complex", graph, "-map", "[v]", "-map", "[out]", *LR.ENCODE, "-c:a", "aac", "-b:a", "192k",
            *LR.MP4_TIMING, "-movflags", "+faststart", out]
    _run(cmd)
    return out


def qc(mp4: Path) -> dict:
    probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(mp4)],
                                      capture_output=True, text=True, check=True).stdout)
    v = next(s for s in probe["streams"] if s["codec_type"] == "video")
    a = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)
    frames = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                                 "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(mp4)],
                                capture_output=True, text=True, check=True).stdout.strip() or 0)
    loud = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    il = [ln for ln in loud.splitlines() if "I:" in ln and "LUFS" in ln]
    plan = json.loads((MVP / "render_plan.json").read_text()) if (MVP / "render_plan.json").exists() else {}
    rep = {"file": str(mp4), "size_mb": round(mp4.stat().st_size / 1e6, 1), "width": v["width"], "height": v["height"],
           "fps": v["r_frame_rate"], "duration_s": round(float(probe["format"]["duration"]), 3), "frames": frames,
           "audio": bool(a), "audio_channels": a and a.get("channels"), "integrated_lufs": il[-1].strip() if il else None,
           "expected_frames": plan.get("total_frames"), "expected_s": plan.get("video_s")}
    rep["ok"] = (rep["width"], rep["height"]) == (W, H) and rep["audio"] and rep["audio_channels"] == 2 and \
        (rep["expected_frames"] is None or abs(frames - rep["expected_frames"]) <= 1)
    print(json.dumps(rep, indent=1))
    return rep


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "narrate":
        narrate_cmd()
    elif cmd == "render-cmds":
        for c in render_cmds():
            print(" ".join(c))
    elif cmd == "post":
        bv, ba = bed()
        out = mux(bv, ba, captions())
        return 0 if qc(out)["ok"] else 2
    elif cmd == "qc":
        return 0 if qc(Path(sys.argv[2]))["ok"] else 2
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
