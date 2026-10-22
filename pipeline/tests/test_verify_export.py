"""Run: python pipeline/tests/test_verify_export.py  (FFmpeg only: a synthetic "export" checked against its timeline,
then three broken timelines that verify_export must reject: swapped clips, moved narration, wrong length)"""
import copy, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import ffmpeg, run
from lib import verify_export as VX

ff = ffmpeg()
with tempfile.TemporaryDirectory() as d:
    d = Path(d); (d / "render").mkdir()
    a, b, n, x = d / "a.webm", d / "b.webm", d / "n.wav", d / "export.webm"
    run([ff, "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=640x360:r=25:d=2", "-c:v", "libvpx-vp9", "-deadline", "realtime", str(a)])
    run([ff, "-v", "error", "-f", "lavfi", "-i", "mandelbrot=s=640x360:r=25", "-t", "2", "-c:v", "libvpx-vp9", "-deadline", "realtime", str(b)])
    run([ff, "-v", "error", "-f", "lavfi", "-i", "anoisesrc=d=1.5:c=pink:r=48000:a=0.3", "-af", "volume='0.3+0.7*mod(floor(t*7),2)':eval=frame", str(n)])
    run([ff, "-v", "error", "-i", str(a), "-i", str(b), "-i", str(n), "-filter_complex",
         "[0:v][1:v]concat=n=2:v=1[v];[2:a]adelay=1000:all=1,apad=whole_dur=4[a]", "-map", "[v]", "-map", "[a]",
         "-c:v", "libvpx-vp9", "-deadline", "realtime", "-c:a", "libopus", "-t", "4", str(x)])
    tl = {"fps": 25, "width": 640, "height": 360, "duration_s": 4.0,
          "media": [{"id": "M1", "path": str(a), "kind": "video"}, {"id": "M2", "path": str(b), "kind": "video"},
                    {"id": "M3", "path": str(n), "kind": "audio"}],
          "video": [{"media": "M1", "start_s": 0, "dur_s": 2, "scene": "SC001"}, {"media": "M2", "start_s": 2, "dur_s": 2, "scene": "SC002"}],
          "audio": [{"media": "M3", "start_s": 1.0, "dur_s": 1.5, "in_s": 0, "role": "narration", "scene": "SC001"}], "text": []}
    _, E, _ = VX.verify(d, "cs", tl, x, engine="t"); assert not E, E; print("ok: matching export passes")
    sw = copy.deepcopy(tl); sw["video"][0]["media"], sw["video"][1]["media"] = "M2", "M1"
    _, E, _ = VX.verify(d, "cs", sw, x, engine="t"); assert sum("neodpovídá zdroji" in e for e in E) == 2, E
    mv = copy.deepcopy(tl); mv["audio"][0]["start_s"] = 1.3
    _, E, _ = VX.verify(d, "cs", mv, x, engine="t"); assert any("hlas" in e for e in E), E
    ln = copy.deepcopy(tl); ln["duration_s"] = 5.0
    _, E, _ = VX.verify(d, "cs", ln, x, engine="t"); assert any(e.startswith("délka") for e in E), E
    _, E, _ = VX.verify(d, "cs", tl, d / "missing.webm", engine="t"); assert E and "neexistuje" in E[0], E
    print("ok: swapped clips, moved narration, wrong length and a missing file are rejected")
