"""Render a Blender 3D shot and finish it like the rest of the channel (bloom, grain, CA, vignette).
Usage: python blender_render.py <shot> <out.mp4> '<params json>' [--preview]
  shot: number | timeline | question | sandwich | tents | tickets   (see pipeline/blender/shots.py)
  --preview renders at 50 % resolution with fewer samples (fast check)."""
import json, subprocess, sys, tempfile, time
from pathlib import Path
import numpy as np, cv2
sys.path.insert(0, str(Path(__file__).parent))
from lib import fx3d
from lib.common import cfg

PIPE = Path(__file__).parent

def bloom(img, thr=200, sigma=18, amount=0.55):
    f = img.astype(np.float32)
    bright = np.clip(f - thr, 0, None) * (255 / (255 - thr))
    return np.clip(f + amount * cv2.GaussianBlur(bright, (0, 0), sigma) + 0.35 * amount * cv2.GaussianBlur(bright, (0, 0), sigma * 4), 0, 255).astype(np.uint8)

def main():
    shot, out, params = sys.argv[1], Path(sys.argv[2]).resolve(), json.loads(sys.argv[3])
    preview = "--preview" in sys.argv
    params.setdefault("font", str(PIPE / "brand" / "fonts" / "ArchivoBlack-Regular.ttf"))
    if preview: params.update(pct=50, samples=12)
    else: params.setdefault("samples", 32)
    work = Path(tempfile.mkdtemp(prefix=f"bl_{shot}_")); (work / "p.json").write_text(json.dumps(params, ensure_ascii=False))
    t0 = time.time()
    r = subprocess.run([cfg()["blender"], "-b", "--factory-startup", "-P", str(PIPE / "blender" / "shots.py"), "--", shot, str(work), str(work / "p.json")],
                       capture_output=True, text=True)
    if "RENDERED" not in r.stdout:
        sys.exit("Blender failed:\n" + (r.stdout[-3000:] + r.stderr[-3000:]))
    t_render = time.time() - t0
    frames = sorted((work / "frames").glob("*.png"))
    p = fx3d.writer(str(out))
    for i, fp in enumerate(frames):
        im = cv2.imread(str(fp))
        if im.shape[1] != fx3d.W: im = cv2.resize(im, (fx3d.W, fx3d.H), interpolation=cv2.INTER_CUBIC)
        im = bloom(im)
        p.stdin.write(fx3d.finish(im, i / max(len(frames) - 1, 1), grain=0.03, ca=2.0, vignette=0.5, seed=7).tobytes())
    p.stdin.close(); p.wait()
    print(json.dumps({"shot": shot, "out": str(out), "frames": len(frames), "blender_s": round(t_render, 1),
                      "total_s": round(time.time() - t0, 1), "frames_dir": str(work / "frames")}))

if __name__ == "__main__":
    main()
