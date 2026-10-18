"""Bleep words in a clip (audio or video) using Whisper word timestamps.
Usage: python bleep.py <in.(wav|mp4|mp3)> <out> --lang en [--words f*ck,sh*t,...] [--list bleep_words.txt] [--report r.json]
- Matches words case-insensitively; a list entry ending with * matches a prefix (e.g. 'fuck*').
- Replaces each matched word (+40 ms padding) with a 1 kHz tone at -16 dBFS; video stream is copied untouched.
- Writes a JSON report of what was bleeped (time, word) for the human review gate."""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, soundfile as sf
sys.path.insert(0, str(Path(__file__).parent))
from lib.common import cfg, ffmpeg

DEFAULT = Path(__file__).parent / "bleep_words.txt"

def load_words(args):
    words = []
    for src in ([args.list] if args.list else []) + ([str(DEFAULT)] if not args.words and not args.list else []):
        words += [w.strip().lower() for w in Path(src).read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")]
    if args.words: words += [w.strip().lower() for w in args.words.split(",") if w.strip()]
    return words

def match(token, words):
    t = re.sub(r"[^\w*']", "", token.lower())
    return any((w.endswith("*") and t.startswith(w[:-1])) or t == w for w in words)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--lang", default="en")
    ap.add_argument("--words"); ap.add_argument("--list"); ap.add_argument("--report")
    a = ap.parse_args(); ff = ffmpeg(); words = load_words(a)
    tmp = Path(tempfile.mkdtemp()); wav = tmp / "a.wav"
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", a.inp, "-vn", "-ac", "1", "-ar", "48000", str(wav)], check=True)
    y, sr = sf.read(wav, dtype="float32")
    import librosa
    from lib.asr import transcribe
    res = transcribe(librosa.resample(y, orig_sr=sr, target_sr=16000), a.lang, cfg()["asr_model"])
    hits = []
    for seg in res["segments"]:
        for w in seg.get("words", []):
            if match(w["word"], words):
                s, e = max(0, int((w["start"] - 0.04) * sr)), min(len(y), int((w["end"] + 0.04) * sr))
                t = np.arange(e - s) / sr; y[s:e] = 0.158 * np.sin(2 * np.pi * 1000 * t)  # -16 dBFS
                hits.append({"word": w["word"].strip(), "start": round(w["start"], 2), "end": round(w["end"], 2)})
    sf.write(tmp / "b.wav", y, sr)
    is_video = Path(a.inp).suffix.lower() in (".mp4", ".mov", ".mkv", ".webm")
    cmd = [ff, "-y", "-loglevel", "error"] + (["-i", a.inp] if is_video else []) + ["-i", str(tmp / "b.wav")]
    cmd += (["-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k"] if is_video else [])
    subprocess.run(cmd + [a.out], check=True)
    rep = {"input": a.inp, "output": a.out, "bleeped": hits, "transcript": res["text"].strip()}
    if a.report: Path(a.report).write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps({"bleeped": hits}, ensure_ascii=False))

if __name__ == "__main__":
    main()
