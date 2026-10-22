"""Flash check: the vendored self-test passes, a 6 Hz full-frame strobe FAILS, a calm fade passes, a missing file is skipped
(never a pass), an accepted window sets a deliberate strobe aside."""
import subprocess, sys, tempfile
from pathlib import Path
PIPE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(PIPE))
from lib import flashcheck as F

r = subprocess.run([sys.executable, "-I", str(F.VENDOR), "--selftest"], capture_output=True, text=True, cwd=tempfile.mkdtemp())
assert r.returncode == 0 and "SELFTEST PASS" in r.stdout, r.stdout[-2000:] + r.stderr[-2000:]

d = Path(tempfile.mkdtemp())
def mk(name, vf, dur=4):
    out = d / name
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=gray:s=640x360:r=25:d={dur}", "-vf", vf,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)], check=True)
    return out

strobe = mk("strobe.mp4", "geq=lum='if(lt(mod(N\\,4)\\,2)\\,20\\,230)':cb=128:cr=128")   # 6.25 Hz black/white
calm = mk("calm.mp4", "geq=lum='40+N':cb=128:cr=128")                                     # slow brightening ramp

s = F.check(strobe); assert s["status"] == "fail", s
assert any(l == "FAIL" and lab == "flash rate" for l, lab, _ in s["rows"]), s["rows"]
c = F.check(calm); assert c["status"] == "ok", c["rows"]
m = F.check(d / "missing.mp4"); assert m["status"] == "skipped" and not m["rows"], m
a = F.check(strobe, accepted=[(0, 4, "test: deliberate strobe")])
assert {lab: l for l, lab, _ in a["rows"]}["flash rate"] == "PASS", a["rows"]
print(f"ok: selftest, strobe={s['status']}, calm={c['status']}, missing={m['status']}, accepted window -> flash rate PASS")
