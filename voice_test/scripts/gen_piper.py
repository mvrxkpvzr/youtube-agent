"""Generate Piper samples. Usage: python gen_piper.py <model.onnx> <text.txt> <out.wav> <espeak_data_dir>"""
import sys, wave, time
from piper import PiperVoice
model, text, out, esd = sys.argv[1:5]
voice = PiperVoice.load(model, espeak_data_dir=esd)
t = time.time()
with wave.open(out, "wb") as wf:
    voice.synthesize_wav(open(text, encoding="utf-8").read(), wf)
print(f"{out}: {time.time()-t:.1f}s")
