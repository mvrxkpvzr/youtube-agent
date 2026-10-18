"""Text preparation for TTS: lexicon respelling + checks that make TTS errors unlikely.
Rule (from the voice test): digits are never sent to TTS. The script must provide
`narration_tts` with numbers written as words, otherwise `voice` refuses to run."""
import json, re
from pathlib import Path

PIPE = Path(__file__).resolve().parents[1]

def load_lexicon(lang, project=None):
    lex = {}
    for p in [PIPE / f"lexicon.{lang}.json", (Path(project) / f"lexicon.{lang}.json") if project else None]:
        if p and p.exists():
            lex.update(json.loads(p.read_text(encoding="utf-8")))
    return lex

def apply_lexicon(text, lex):
    for k in sorted(lex, key=len, reverse=True):
        text = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", lex[k], text)
    return text

ALLOW_CS = {"web", "webu", "webem", "weby", "webové", "wifi"}
FOREIGN_CS = re.compile(r"\b\w*(?:w|q|x|th|ea|ck)\w*\b", re.I)

def check(text, lang, lex):
    """Return (errors, warnings) for a TTS input string (before lexicon)."""
    errors, warnings = [], []
    for m in re.finditer(r"\d[\d.,:/]*", text):
        errors.append(f"číslice '{m.group()}' – napiš slovy v narration_tts")
    for m in re.finditer(r"\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽÄÖÜ]{2,}\b", text):
        if m.group() not in lex:
            warnings.append(f"zkratka '{m.group()}' není v lexikonu")
    if lang == "cs":
        known = {w.lower() for k in lex for w in re.findall(r"\w+", k)} | ALLOW_CS
        for m in FOREIGN_CS.finditer(text):
            if m.group().lower() not in known:
                warnings.append(f"možné cizí slovo '{m.group()}' není v lexikonu")
    return errors, sorted(set(warnings))

def prepare(scene, lang, lex):
    src = scene.get("narration_tts") or scene["narration"]
    errors, warnings = check(src, lang, lex)
    return apply_lexicon(src, lex), errors, warnings
