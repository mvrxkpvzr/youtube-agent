"""Run inside the mlx-audio venv. Usage: python moss_worker.py <job.json>
job = {"model", "language", "ref_audio", "ref_text", "target_wpm", "max_stretch", "max_tokens", "items": [{"text", "out"}]}
Every scene is generated with the same reference voice (channel identity), then time-stretched (Rubber Band via
pedalboard, pitch kept) towards target_wpm, at most max_stretch× faster, never slower."""
import json, sys
import numpy as np, soundfile as sf
from pedalboard import time_stretch
from mlx_audio.tts import load

job = json.load(open(sys.argv[1], encoding="utf-8"))
model = load(job["model"], lazy=True)
for it in job["items"]:
    res = next(model.generate(text=it["text"], language=job.get("language", "Czech"), ref_audio=job["ref_audio"],
                              ref_text=job["ref_text"], max_tokens=job.get("max_tokens", 2400)))
    y = np.array(res.audio, dtype=np.float32); sr = res.sample_rate
    y = y.mean(axis=1) if y.ndim > 1 else y
    words = len(it["text"].split()); wpm = words / (len(y) / sr) * 60
    k = min(max(job.get("target_wpm", wpm) / wpm, 1.0), job.get("max_stretch", 1.25))
    if k > 1.001: y = time_stretch(y[None, :], sr, stretch_factor=k, high_quality=True)[0]
    sf.write(it["out"], y, sr, subtype="PCM_24")
    print("ok", it["out"], f"wpm {wpm:.0f} -> {wpm * k:.0f} (x{k:.2f})", flush=True)
