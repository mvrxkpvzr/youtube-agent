"""Try respelling variants for one term with a TTS engine and keep the one Whisper hears as the target.
Usage: python tools_lexicon_probe.py <engine> <lang> "<target term>" "<carrier sentence with {}>" <variant1> <variant2> ...
This only ranks by intelligibility to Whisper – a human still has to approve the final pick."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lib.common import cfg, PIPE
from lib.asr_check import transcribe, norm_words
import difflib
engine, lang, target, carrier, *variants = sys.argv[1:]
c = cfg(); e = c["engines"][engine]; tmp = Path(tempfile.mkdtemp())
items = [{"text": carrier.format(v), "out": str(tmp / f"v{i}.wav")} for i, v in enumerate(variants)]
job = tmp / "job.json"; job.write_text(json.dumps(dict(e["job"], items=items), ensure_ascii=False))
subprocess.run([e["python"], "-I", str(PIPE / e["worker"]), str(job)], check=True, capture_output=True, env=dict(os.environ, **e.get("env", {})))
tw = " ".join(norm_words(target)); res = []
for v, it in zip(variants, items):
    hyp = transcribe(it["out"], lang, c["asr_model"])["text"]; hw = " ".join(norm_words(hyp))
    score = max(difflib.SequenceMatcher(a=tw, b=hw[i:i + len(tw)]).ratio() for i in range(max(1, len(hw) - len(tw) + 1)))
    res.append((round(score, 2), v, hyp.strip()))
for r in sorted(res, reverse=True): print(r)
