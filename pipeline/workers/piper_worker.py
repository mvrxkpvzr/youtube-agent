"""Run inside the Piper venv. Usage: python piper_worker.py <job.json>
job = {"model": ".onnx", "espeak_data_dir": "...", "items": [{"text": "...", "out": "x.wav"}]}"""
import json, sys, wave
from piper import PiperVoice, SynthesisConfig
job = json.load(open(sys.argv[1], encoding="utf-8"))
voice = PiperVoice.load(job["model"], espeak_data_dir=job["espeak_data_dir"])
for it in job["items"]:
    with wave.open(it["out"], "wb") as wf:
        voice.synthesize_wav(it["text"], wf, syn_config=SynthesisConfig(length_scale=job.get("length_scale")))
    print("ok", it["out"], flush=True)
