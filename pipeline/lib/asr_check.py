"""Back-transcription check: catches dropped sentences, wrong numbers and garbled words.
Reference = the approved narration (display text, may contain digits); Whisper usually writes digits too."""
import difflib, json, re, unicodedata
from pathlib import Path
from .common import cfg, load_shotlist, update_state
from .csnum import collapse

_PROC = re.compile(r"procent(?:o|a|u|em|ech|ům)?")

def raw_words(s):
    """Lower-cased word tokens; numbers not yet merged (see norm_words)."""
    s = unicodedata.normalize("NFC", s.lower()).replace("“", " ").replace("„", " ").replace("%", " procent")
    s = re.sub(r"(\d),(\d)", r"\1.\2", s)            # 1,65 -> 1.65 (both sides)
    s = re.sub(r"(?<=\d)\.(?!\d)", " ", s)            # ordinal dot "23." -> "23"
    s = re.sub(r"[^\w\s.]|(?<!\d)\.|\.(?!\d)", " ", s)
    return ["procent" if _PROC.fullmatch(w) else w for w in s.split()]

def norm_words(s):
    """raw_words with spelled-out Czech numbers and digit groups merged ("dvacet šest milionů…" == "26 191 306")."""
    return collapse(raw_words(s))[0]

def numbers(words): return [w for w in words if re.fullmatch(r"\d+(\.\d+)?", w)]

def compare(reference, hypothesis, min_dropped=4):
    """Pure function (unit-tested). Returns dict with errors/warnings and alignment stats."""
    r, h = norm_words(reference), norm_words(hypothesis)
    sm = difflib.SequenceMatcher(a=r, b=h, autojunk=False)
    errors, warnings, dropped = [], [], []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op in ("delete", "replace") and (a1 - a0) - (b1 - b0 if op == "replace" else 0) >= min_dropped:
            dropped.append(" ".join(r[a0:a1]))
    for d in dropped: errors.append(f"vynechaný text: „{d}“")
    missing_nums = [n for n in numbers(r) if n not in numbers(h)]
    extra_nums = [n for n in numbers(h) if n not in numbers(r)]
    if missing_nums: errors.append(f"čísla nenalezena v přepisu: {missing_nums} (přepis má {extra_nums or 'nic navíc'})")
    import jiwer
    wer = jiwer.wer(" ".join(r), " ".join(h)) if r else 0.0
    if wer > 0.15: warnings.append(f"WER {wer:.0%} – poslechni celou scénu")
    return {"wer": round(wer, 3), "errors": errors, "warnings": warnings}

def transcribe(wav, lang, model):
    import librosa
    from .asr import transcribe as whisper
    y, _ = librosa.load(str(wav), sr=16000, mono=True)   # array input: no system ffmpeg needed
    return whisper(y, lang, model)

def check(proj, lang):
    c = cfg(); sl = load_shotlist(proj, lang); report = {}
    for sc in sl["scenes"]:
        wav = proj / "audio" / lang / f"{sc['id']}.wav"
        res = transcribe(wav, lang, c["asr_model"])
        words = [{"w": w["word"].strip(), "start": w["start"], "end": w["end"]} for seg in res["segments"] for w in seg.get("words", [])]
        (wav.with_suffix(".words.json")).write_text(json.dumps(words, ensure_ascii=False))
        report[sc["id"]] = dict(compare(sc["narration"], res["text"]), transcript=res["text"].strip())
    out = proj / "audio" / lang / "asr_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    n_err = sum(len(v["errors"]) for v in report.values())
    update_state(proj, f"asr_check_{lang}", "done" if n_err == 0 else "failed",
                 inputs=[proj / f"shotlist.{lang}.json"] + sorted((proj / "audio" / lang).glob("SC*.wav")), outputs=[out], errors=n_err)
    return report
