"""MOSS-TTS-Local-Transformer-v1.5 (MLX 8bit, Apache-2.0) – Czech test on TOGI scenes.
Run with ~/youtube-agent-env/venv/mlxaudio/bin/python. Scene 1 is generated from a style instruction only
(an original voice, no cloning of a real person); later scenes use scene 1 as the voice reference."""
import json, sys, time
from pathlib import Path
from mlx_audio.tts import load
from mlx_audio.audio_io import write as audio_write

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
SCENES = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
STYLE = ("Klidný, sebejistý mužský vypravěč dokumentu, hlubší hlas, zřetelná výslovnost, "
         "svižné tempo, napětí v hlase, bez přehrávání.")
t0 = time.time(); model = load("mlx-community/MOSS-TTS-Local-Transformer-v1.5-8bit", lazy=True)
log = {"load_s": round(time.time() - t0, 1), "items": []}
ref = None
for i, (sid, text) in enumerate(SCENES):
    t = time.time()
    kw = dict(text=text, language="Czech", max_tokens=1200)
    if ref: kw.update(ref_audio=str(ref[0]), ref_text=ref[1])
    else: kw.update(instruction=STYLE)
    res = next(model.generate(**kw))
    out = OUT / f"moss_{sid}.wav"; audio_write(str(out), res.audio, res.sample_rate)
    dur = res.audio.shape[0] / res.sample_rate
    log["items"].append({"id": sid, "gen_s": round(time.time() - t, 1), "audio_s": round(dur, 2), "ref": bool(ref)})
    print(log["items"][-1], flush=True)
    if ref is None: ref = (out, text)
(OUT / "moss_log.json").write_text(json.dumps(log, indent=1))
