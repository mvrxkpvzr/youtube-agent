"""Build the blind listening test: loudness-normalised anonymous copies + HTML form.
Usage: python build_blind_test.py <voice_test_dir> <ffmpeg_path>
Writes blind/<code>.m4a, results/KEY_neposilat_posluchacum.json, listening_test.html"""
import json, random, subprocess, sys, string
from pathlib import Path
root, ffmpeg = Path(sys.argv[1]), sys.argv[2]
raw, blind = root / "samples" / "raw", root / "blind"
blind.mkdir(exist_ok=True)
rng = random.Random(20261018)
samples = sorted(raw.glob("*.wav"))
codes = rng.sample([a + b for a in "KMPRTV" for b in "23456789"], len(samples))
key, items = {}, {"cs": [], "de": []}
for wav, code in zip(samples, codes):
    lang = wav.stem.rsplit("_", 1)[-1]
    out = blind / f"{code}.m4a"
    # same loudness for every sample so volume does not bias ratings (EBU R128, -16 LUFS)
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "44100", "-ac", "1", "-c:a", "aac", "-b:a", "128k", str(out)], check=True)
    key[code] = wav.name; items[lang].append(code)
for l in items: rng.shuffle(items[l])
(root / "results" / "KEY_neposilat_posluchacum.json").write_text(json.dumps(key, indent=2, ensure_ascii=False))
texts = {l: (root / "texts" / f"{l}.txt").read_text(encoding="utf-8") for l in ("cs", "de")}
html = (Path(__file__).parent / "listening_test_template.html").read_text(encoding="utf-8")
html = html.replace("__ITEMS__", json.dumps(items)).replace("__TEXTS__", json.dumps(texts, ensure_ascii=False))
(root / "listening_test.html").write_text(html, encoding="utf-8")
print(json.dumps(items), "->", root / "listening_test.html")
