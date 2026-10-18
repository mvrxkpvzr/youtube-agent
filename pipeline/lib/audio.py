"""Join scene WAVs into narration.wav (mono 48 kHz) with fixed gaps; write timings.json."""
import json
import numpy as np, soundfile as sf, librosa
from .common import cfg, load_shotlist, update_state

SR = 48000

def assemble(proj, lang):
    c = cfg(); sl = load_shotlist(proj, lang); d = proj / "audio" / lang
    gap = np.zeros(int(sl.get("pace", {}).get("scene_gap_s", c["scene_gap_s"]) * SR), dtype=np.float32)
    parts, timings, t = [], [], 0.0
    lead = np.zeros(int(0.5 * SR), dtype=np.float32); parts.append(lead); t += 0.5
    for sc in sl["scenes"]:
        y, sr = sf.read(d / f"{sc['id']}.wav", dtype="float32", always_2d=False)
        if y.ndim > 1: y = y.mean(axis=1)
        if sr != SR: y = librosa.resample(y, orig_sr=sr, target_sr=SR)
        y, idx = librosa.effects.trim(y, top_db=45)
        timings.append({"id": sc["id"], "start": round(t, 3), "end": round(t + len(y) / SR, 3), "trim_offset": round(idx[0] / SR, 3)})
        parts += [y, gap]; t += len(y) / SR + len(gap) / SR
    out = d / "narration.wav"
    sf.write(out, np.concatenate(parts), SR, subtype="PCM_24")
    (d / "timings.json").write_text(json.dumps(timings, indent=1))
    update_state(proj, f"audio_{lang}", "done", inputs=sorted(d.glob("SC*.wav")), outputs=[out, d / "timings.json"])
    return timings
