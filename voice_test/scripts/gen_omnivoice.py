"""OmniVoice (weights CC-BY-NC – NON-COMMERCIAL REFERENCE ONLY), voice design, no cloning.
Usage: python gen_omnivoice.py <lang> <text.txt> <out.wav> <instruct>"""
import sys, time, inspect, numpy as np, soundfile as sf, torch
import omnivoice
lang, text_path, out, instruct = sys.argv[1:5]
cls = getattr(omnivoice, "OmniVoice")
dev = "mps" if torch.backends.mps.is_available() else "cpu"
sig = inspect.signature(cls.from_pretrained)
m = cls.from_pretrained("k2-fsa/OmniVoice", **({"device_map": dev} if "device_map" in sig.parameters else {}))
paras = [p.strip() for p in open(text_path, encoding="utf-8").read().split("\n\n") if p.strip()]
t0, chunks, sr = time.time(), [], getattr(m, "sampling_rate", 24000)
for p in paras:
    a = m.generate(text=p, language=lang, instruct=instruct)
    a = a[0] if isinstance(a, (list, tuple)) else a
    a = a.detach().cpu().numpy() if hasattr(a, "detach") else np.asarray(a)
    chunks += [a.squeeze().astype(np.float32), np.zeros(int(0.6 * sr), dtype=np.float32)]
sf.write(out, np.concatenate(chunks), sr)
print(f"{out}: {time.time()-t0:.0f}s on {dev}")
