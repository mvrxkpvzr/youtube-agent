"""Whisper back-end: mlx-whisper on Apple Silicon, faster-whisper (CPU, int8) elsewhere.
Both return the mlx-whisper shape: {"text", "segments": [{"words": [{"word", "start", "end"}]}]}."""
import sys

def transcribe(audio16k, lang, model):
    """audio16k: mono float32 numpy array at 16 kHz."""
    if sys.platform == "darwin":
        import mlx_whisper
        return mlx_whisper.transcribe(audio16k, path_or_hf_repo=model, language=lang, word_timestamps=True,
                                      condition_on_previous_text=False)
    from faster_whisper import WhisperModel
    m = _models.get(model) or _models.setdefault(model, WhisperModel(model, device="cpu", compute_type="int8"))
    segs, _ = m.transcribe(audio16k, language=lang, word_timestamps=True, condition_on_previous_text=False, beam_size=5)
    segments = [{"text": s.text, "words": [{"word": w.word, "start": w.start, "end": w.end} for w in (s.words or [])]} for s in segs]
    return {"text": "".join(s["text"] for s in segments), "segments": segments}

_models = {}
