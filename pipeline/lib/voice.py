"""Per-scene TTS with caching: a scene is regenerated only if its prepared text or engine changed."""
import json, os, subprocess, tempfile
from pathlib import Path
from .common import cfg, sha, load_shotlist, update_state, PIPE
from .textprep import load_lexicon, prepare

def voice(proj, lang, engine=None, force=False):
    c = cfg(); sl = load_shotlist(proj, lang); lex = load_lexicon(lang, proj)
    engine = engine or sl.get("pace", {}).get("tts_engine") or c["default_engine"][lang]; e = c["engines"][engine]
    if e.get("lexicon_file"):  # engine-specific respellings (Piper hacks like "jůtůb" confuse MOSS); missing file = none
        pl = proj / e["lexicon_file"].format(lang=lang); lex = json.loads(pl.read_text(encoding="utf-8")) if pl.exists() else {}
    outdir = proj / "audio" / lang; outdir.mkdir(parents=True, exist_ok=True)
    items, problems, warns = [], [], []
    for sc in sl["scenes"]:
        text, errs, w = prepare(sc, lang, lex)
        problems += [f"{sc['id']}: {x}" for x in errs]; warns += [f"{sc['id']}: {x}" for x in w]
        wav, meta = outdir / f"{sc['id']}.wav", outdir / f"{sc['id']}.json"
        key = sha(engine + "\n" + json.dumps(e["job"], sort_keys=True) + "\n" + text)  # engine settings (e.g. speed) invalidate too
        if not force and wav.exists() and meta.exists() and json.loads(meta.read_text()).get("key") == key:
            continue
        items.append({"id": sc["id"], "text": text, "out": str(wav), "key": key})
    if problems:
        raise SystemExit("TTS zastaveno – nejdřív oprav text:\n  " + "\n  ".join(problems))
    if items:
        job = dict(e["job"], items=[{"text": i["text"], "out": i["out"]} for i in items])
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(job, f, ensure_ascii=False)
        env = dict(os.environ, **e.get("env", {}))
        r = subprocess.run([e["python"], "-I", str(PIPE / e["worker"]), f.name], capture_output=True, text=True, env=env)
        if r.returncode != 0:
            raise RuntimeError(f"TTS worker failed:\n{r.stderr[-3000:]}")
        for i in items:
            (outdir / f"{i['id']}.json").write_text(json.dumps({"key": i["key"], "engine": engine, "license": e["license"],
                                                                 "commercial": e["commercial"], "tts_text": i["text"]}, ensure_ascii=False, indent=1))
    update_state(proj, f"voice_{lang}", "done", inputs=[proj / f"shotlist.{lang}.json"],
                 outputs=sorted(outdir.glob("SC*.wav")), engine=engine, regenerated=[i["id"] for i in items])
    return [i["id"] for i in items], warns
