"""Integration test: synthesise a Czech sentence with a swear word, bleep it, check a 1 kHz tone sits where the word was."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, soundfile as sf
PIPE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(PIPE))
from lib.common import cfg
e = cfg()["engines"]["piper_cs"]; d = Path(tempfile.mkdtemp())
job = d / "job.json"; job.write_text(json.dumps(dict(e["job"], items=[{"text": "To je ale do prdele dobrý nápad, řekl.", "out": str(d / "in.wav")}]), ensure_ascii=False))
subprocess.run([e["python"], "-I", str(PIPE / e["worker"]), str(job)], check=True, capture_output=True)
r = subprocess.run([sys.executable, str(PIPE / "bleep.py"), str(d / "in.wav"), str(d / "out.wav"), "--lang", "cs"], capture_output=True, text=True, env=dict(os.environ))
hits = json.loads(r.stdout.strip().splitlines()[-1])["bleeped"]; assert hits, r.stdout + r.stderr
y, sr = sf.read(d / "out.wav", dtype="float32"); h = hits[0]
seg = y[int((h["start"] + 0.05) * sr): int((h["end"] - 0.02) * sr)]
spec = np.abs(np.fft.rfft(seg)); f = np.fft.rfftfreq(len(seg), 1 / sr)
assert abs(f[spec.argmax()] - 1000) < 20, f[spec.argmax()]
print(f"ok: bleeped {hits[0]['word']!r} at {h['start']}-{h['end']} s, dominant {f[spec.argmax()]:.0f} Hz")
