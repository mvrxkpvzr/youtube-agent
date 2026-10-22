"""Photosensitive flash check of a rendered video (WCAG 2.2 SC 2.3.1 + EA IRIS's extended failure).
The measuring code is vendored unmodified from konradre/video-production-skills (MIT):
third_party/konradre-video-production-skills/decoded_checks.py (see PROVENANCE.md there).
  check(video) -> {"status": ok|fail|warn|skipped, "rows": [(level, label, detail)], ...}
  python -I pipeline/lib/flashcheck.py <video.mp4> [--json out.json]
FAIL rows (over 3 flashes in any second, sustained 2–3 a second) block publication; WARN rows need a human look.
Needs ffmpeg + ffprobe on PATH and numpy. When they are missing the check is reported as skipped, never as a pass."""
import importlib.util, json, shutil, sys, time
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[2] / "third_party" / "konradre-video-production-skills" / "decoded_checks.py"

def _vendor():
    sp = importlib.util.spec_from_file_location("decoded_checks", VENDOR)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

def check(video, accepted=()):
    """accepted: [(from_s, to_s, why)] deliberate flashes set aside from the whole-frame rows (still printed as INFO)."""
    video = Path(video)
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing: return {"status": "skipped", "reason": f"chybí {', '.join(missing)} v PATH", "rows": []}
    if not VENDOR.exists(): return {"status": "skipped", "reason": f"chybí {VENDOR}", "rows": []}
    if not video.exists(): return {"status": "skipped", "reason": f"video neexistuje: {video}", "rows": []}
    dc = _vendor(); t0 = time.time()
    frames, fps, (W, H) = dc.flash_frames(str(video))
    if not W: return {"status": "skipped", "reason": "ffprobe nenašel video stopu", "rows": []}
    res = dc.flash_read(frames, fps, W, H)
    if res["n"] < 3: return {"status": "skipped", "reason": f"dekódováno jen {res['n']} snímků", "rows": []}
    rows = dc.flash_rows(res, list(accepted))
    levels = {r[0] for r in rows}
    status = "fail" if "FAIL" in levels else "warn" if "WARN" in levels else "ok"
    return {"status": status, "rows": rows, "frames": res["n"], "fps": fps, "size": [W, H],
            "flash_frames": {k: res[k]["frame"] for k in ("general", "red")}, "seconds": round(time.time() - t0, 1),
            "tool": "konradre/video-production-skills decoded_checks.py (MIT)"}

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"): print(__doc__); return 0
    r = check(sys.argv[1])
    for lvl, label, det in r["rows"]: print(f"{lvl:4} {label}: {det}")
    print(f"STATUS {r['status']}" + (f" ({r['reason']})" if r.get("reason") else f" · {r['frames']} snímků za {r['seconds']} s"))
    if "--json" in sys.argv: Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(r, ensure_ascii=False, indent=1))
    return {"ok": 0, "warn": 0, "fail": 1, "skipped": 2}[r["status"]]

if __name__ == "__main__":
    sys.exit(main())
