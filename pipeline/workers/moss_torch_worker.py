"""Run inside the MOSS PyTorch venv (Linux cloud, CPU). Usage: python moss_torch_worker.py <job.json>
Same job as moss_worker.py (MLX, Mac): {"model", "language", "ref_audio", "target_wpm", "max_stretch", "max_new_tokens", "items": [{"text", "out"}]}.
bf16 weights under CPU autocast: ~13 GB RAM peak, ~5x slower than real time on 4 cores. Every scene uses the same reference voice."""
import json, sys
import numpy as np, soundfile as sf, torch
from pedalboard import time_stretch
from transformers import AutoModel, AutoProcessor

job = json.load(open(sys.argv[1], encoding="utf-8"))
torch.set_num_threads(job.get("threads", 4)); torch.manual_seed(job.get("seed", 7))
dt = torch.bfloat16
proc = AutoProcessor.from_pretrained(job["model"], trust_remote_code=True)
proc.audio_tokenizer = proc.audio_tokenizer.to(dt)
model = AutoModel.from_pretrained(job["model"], trust_remote_code=True, attn_implementation="sdpa", dtype=dt).eval()
sr = proc.model_config.sampling_rate
for it in job["items"]:
    with torch.no_grad(), torch.autocast("cpu", dtype=dt):
        b = proc([[proc.build_user_message(text=it["text"], reference=[job["ref_audio"]], language=job.get("language", "Czech"))]], mode="generation")
        out = model.generate(input_ids=b["input_ids"], attention_mask=b["attention_mask"], max_new_tokens=job.get("max_new_tokens", 1500),
                             do_sample=True, audio_temperature=1.7, audio_top_p=0.8, audio_top_k=25, audio_repetition_penalty=1.0)
        a = [m for m in proc.decode(out) if m is not None][0].audio_codes_list[0].float().numpy()
    y = (a.mean(axis=0) if a.ndim == 2 else a).astype(np.float32)
    wpm = len(it["text"].split()) / (len(y) / sr) * 60
    k = min(max(job.get("target_wpm", wpm) / wpm, 1.0), job.get("max_stretch", 1.25))
    if k > 1.001: y = time_stretch(y[None, :], sr, stretch_factor=k, high_quality=True)[0]
    sf.write(it["out"], y, sr, subtype="PCM_24")
    print("ok", it["out"], f"wpm {wpm:.0f} -> {wpm * k:.0f} (x{k:.2f})", flush=True)
