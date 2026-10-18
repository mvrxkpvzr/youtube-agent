"""Chatterbox Multilingual, default built-in voice (no cloning), per paragraph + 0.6 s pauses.
Usage: python gen_chatterbox.py <lang> <text.txt> <out.wav> [t3_model]"""
import sys, time, inspect, torch, numpy as np, soundfile as sf
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
lang, text_path, out = sys.argv[1:4]
t3 = sys.argv[4] if len(sys.argv) > 4 else None
dev = "mps" if torch.backends.mps.is_available() else "cpu"
kw = {"t3_model": t3} if t3 and "t3_model" in inspect.signature(ChatterboxMultilingualTTS.from_pretrained).parameters else {}
m = ChatterboxMultilingualTTS.from_pretrained(device=dev, **kw)
paras = [p.strip() for p in open(text_path, encoding="utf-8").read().split("\n\n") if p.strip()]
t0, chunks = time.time(), []
for p in paras:
    w = m.generate(p, language_id=lang).squeeze().cpu().numpy().astype(np.float32)
    chunks += [w, np.zeros(int(0.6 * m.sr), dtype=np.float32)]
sf.write(out, np.concatenate(chunks), m.sr)
print(f"{out}: {time.time()-t0:.0f}s on {dev} {kw}")
