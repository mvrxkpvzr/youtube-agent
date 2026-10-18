"""Objective proxies for TTS samples. They do NOT replace human listening.
Usage: python metrics.py <voice_test_dir>  -> results/metrics.json + results/metrics.md
- intelligibility: WER/CER of Whisper large-v3-turbo transcript vs. source text
- term recall: share of names/terms Whisper recovered (proxy for pronunciation of names)
- tempo: words per minute; pauses: gaps >= 250 ms, longest gap; prosody: F0 spread in semitones
- stability: CER of first vs. second half of the transcript, clipping ratio"""
import json, re, sys, unicodedata
from pathlib import Path
import numpy as np, soundfile as sf, librosa, jiwer, mlx_whisper

root = Path(sys.argv[1]); out = root / "results"; out.mkdir(exist_ok=True)
TERMS = {"cs": ["Jawed Karim", "San Diegu", "Me at the zoo", "YouTube", "Chad Hurley", "Steve Chen", "Google", "1,65", "creator economy", "2005", "2006"],
         "de": ["Jawed Karim", "San Diego", "Me at the zoo", "YouTube", "Chad Hurley", "Steve Chen", "Google", "1,65", "Creator Economy", "2005", "2006"]}
MODEL = "mlx-community/whisper-large-v3-turbo"

def norm(s):
    s = unicodedata.normalize("NFC", s.lower())
    s = re.sub(r"[„“”\"'’–—\-.,:;!?()]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def numbers_variants(t):  # Whisper may write "dvacet" or "20", "1,65" or "1.65"
    return t.replace("1.65", "1,65")

rows = []
for wav in sorted((root / "samples" / "raw").glob("*.wav")):
    name, lang = wav.stem, wav.stem.rsplit("_", 1)[-1]
    ref = (root / "texts" / f"{lang}.txt").read_text(encoding="utf-8")
    y, sr = sf.read(wav, dtype="float32", always_2d=False)
    if y.ndim > 1: y = y.mean(axis=1)
    dur = len(y) / sr
    y16 = librosa.resample(y, orig_sr=sr, target_sr=16000)
    hyp = mlx_whisper.transcribe(y16, path_or_hf_repo=MODEL, language=lang, condition_on_previous_text=False)["text"]
    hyp_n, ref_n = norm(numbers_variants(hyp)), norm(ref)
    wer, cer = jiwer.wer(ref_n, hyp_n), jiwer.cer(ref_n, hyp_n)
    half = len(ref_n) // 2; hh = len(hyp_n) // 2
    cer_a, cer_b = jiwer.cer(ref_n[:half], hyp_n[:hh]), jiwer.cer(ref_n[half:], hyp_n[hh:])
    terms = TERMS[lang]; hit = [t for t in terms if norm(t) in hyp_n]
    # pauses: non-silent intervals at 35 dB below peak
    iv = librosa.effects.split(y16, top_db=35, frame_length=1024, hop_length=256) / 16000
    gaps = np.array([b0 - a1 for (a0, a1), (b0, b1) in zip(iv[:-1], iv[1:])])
    gaps = gaps[gaps >= 0.25]
    f0, vf, _ = librosa.pyin(y16, fmin=60, fmax=400, sr=16000, frame_length=1024)
    f0 = f0[~np.isnan(f0)]
    st = 12 * np.log2(f0 / np.median(f0)) if len(f0) else np.array([0.0])
    rows.append({
        "sample": name, "lang": lang, "duration_s": round(dur, 1),
        "wpm": round(len(ref.split()) / (dur / 60), 1),
        "wer": round(wer, 3), "cer": round(cer, 3), "cer_first_half": round(cer_a, 3), "cer_second_half": round(cer_b, 3),
        "terms_recovered": f"{len(hit)}/{len(terms)}", "terms_missed": [t for t in terms if t not in hit],
        "pauses_ge_250ms": int(len(gaps)), "pause_median_s": round(float(np.median(gaps)), 2) if len(gaps) else 0,
        "pause_max_s": round(float(gaps.max()), 2) if len(gaps) else 0,
        "f0_spread_semitones_p10_p90": round(float(np.percentile(st, 90) - np.percentile(st, 10)), 1),
        "clipping_ratio": round(float(np.mean(np.abs(y) > 0.999)), 5),
        "transcript": hyp.strip(),
    })
    print(name, rows[-1]["wer"], rows[-1]["terms_recovered"], flush=True)
(out / "metrics.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
cols = ["sample", "duration_s", "wpm", "wer", "cer", "cer_first_half", "cer_second_half", "terms_recovered", "pauses_ge_250ms", "pause_median_s", "pause_max_s", "f0_spread_semitones_p10_p90"]
md = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
(out / "metrics.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
