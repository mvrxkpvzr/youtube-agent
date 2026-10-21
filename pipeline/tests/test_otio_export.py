"""otio_export: on a copy of the example project with a stand-in video of the planned length the timeline reads back,
matches the video and carries one marker per scene; a video one second short is caught (exit 1); an edl.<lang>.json from
pipeline/edl.py is preferred over the plan."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
import opentimelineio as otio
PIPE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(PIPE))
from lib.render import plan

proj = Path(tempfile.mkdtemp()) / "example"; shutil.copytree(PIPE / "tests" / "fixtures" / "example_project", proj)
(proj / "state.json").unlink(missing_ok=True); (proj / "render").mkdir(exist_ok=True)
shots, total = plan(proj, "cs"); fps = json.loads((proj / "shotlist.cs.json").read_text())["fps"] if "fps" in json.loads((proj / "shotlist.cs.json").read_text()) else 25
def video(name, dur):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s=320x180:r={fps}:d={dur:.3f}", "-f", "lavfi", "-i",
                    f"sine=d={dur:.3f}", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(proj / "render" / name)], check=True)
def run(*extra): return subprocess.run([sys.executable, "-I", str(PIPE / "otio_export.py"), str(proj), "--lang", "cs", *extra], capture_output=True, text=True)

video("final.cs.mp4", total)
r = run(); assert r.returncode == 0, r.stdout + r.stderr
chk = json.loads(r.stdout.strip().splitlines()[-1]); assert chk["shots_from"] == "plan" and chk["v1_clips"] == len(shots), chk
tl = otio.adapters.read_from_file(str(proj / "render" / "timeline.cs.otio"))
scenes = {s["scene"] for s in shots}; assert chk["markers"] == len(scenes), (chk, scenes)
assert [t.kind for t in tl.tracks] == ["Video", "Video", "Audio"] and not tl.tracks[1].enabled
assert (proj / "render" / "timeline.cs.edl").read_text().count(" V     C ") == len(shots)

video("short.cs.mp4", total - 1)
r = run("--video", "render/short.cs.mp4"); assert r.returncode == 1 and "V1 trvá" in r.stdout, r.stdout + r.stderr

edl = {"project": "example", "language": "cs", "times": "measured", "shots": [
    {"shot": i, "scene": s["scene"], "start_s": 0, "end_s": 0, "dur_s": s["dur"], "template": s["template"], "file": None, "text": "x"}
    for i, s in enumerate(shots)]}
(proj / "render" / "edl.cs.json").write_text(json.dumps(edl))
r = run(); assert r.returncode == 0 and json.loads(r.stdout.strip().splitlines()[-1])["shots_from"] == "edl", r.stdout + r.stderr
print(f"ok: {len(shots)} shots / {len(scenes)} scene markers, CMX EDL written, short video caught, edl.json preferred")
