"""Run inside the Qwen venv. Usage: python qwen_worker.py <job.json>
job = {"model": "...", "speaker": "ryan", "language": "German", "instruct": null, "dtype": "bfloat16", "items": [...]}"""
import json, sys, numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel
job = json.load(open(sys.argv[1], encoding="utf-8"))
dev = "mps" if torch.backends.mps.is_available() else "cpu"
m = Qwen3TTSModel.from_pretrained(job["model"], device_map=dev, dtype=getattr(torch, job.get("dtype", "bfloat16")))
for it in job["items"]:
    wavs, sr = m.generate_custom_voice(text=it["text"], language=job["language"], speaker=job["speaker"], instruct=job.get("instruct"))
    sf.write(it["out"], np.asarray(wavs[0], dtype=np.float32), sr)
    print("ok", it["out"], flush=True)
