"""Qwen3-TTS CustomVoice: per-paragraph synthesis, joined with 0.6 s pauses.
Usage: python gen_qwen.py <model_id> <speaker|list> <language> <text.txt> <out.wav> [instruct]"""
import sys, time, numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel
model_id, speaker, lang, text_path, out = sys.argv[1:6]
instruct = sys.argv[6] if len(sys.argv) > 6 else None
dev = "mps" if torch.backends.mps.is_available() else "cpu"
m = Qwen3TTSModel.from_pretrained(model_id, device_map=dev, dtype=getattr(torch, __import__("os").environ.get("QDTYPE","float32")))
if speaker == "list":
    print(m.get_supported_speakers(), m.get_supported_languages()); sys.exit()
paras = [p.strip() for p in open(text_path, encoding="utf-8").read().split("\n\n") if p.strip()]
t0, chunks, sr = time.time(), [], None
for p in paras:
    wavs, sr = m.generate_custom_voice(text=p, language=lang, speaker=speaker, instruct=instruct)
    chunks += [wavs[0], np.zeros(int(0.6 * sr), dtype=np.float32)]
sf.write(out, np.concatenate(chunks), sr)
print(f"{out}: {time.time()-t0:.0f}s on {dev}")
