"""Unit tests for the back-transcription comparison (cases taken from the real voice test)."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.asr_check import compare
ref = "Doch schon im Herbst 2006 kaufte Google YouTube. Für 1,65 Milliarden Dollar. Warum so viel?"
# Chatterbox case: sentence dropped
r = compare(ref, "Doch schon im Herbst 2006 kaufte Google YouTube. Warum so viel?")
assert any("vynechaný" in e for e in r["errors"]), r
assert any("1.65" in e for e in r["errors"]), r
# Qwen 1.7B case: wrong number
r = compare(ref, "Doch schon im Herbst 2006 kaufte Google YouTube für 1,5 Milliarden Dollar. Warum so viel?")
assert any("1.65" in e for e in r["errors"]) and not any("vynechaný" in e for e in r["errors"]), r
# correct reading, different punctuation/case -> no errors
r = compare(ref, "doch schon im herbst 2006 kaufte google youtube für 1,65 milliarden dollar warum so viel")
assert r["errors"] == [], r
# Czech ordinal date written by Whisper as digits
r = compare("Třiadvacátého dubna 2005 se objevilo video.", "23. dubna 2005 se objevilo video.")
assert not any("vynechaný" in e for e in r["errors"]), r
print("ok: 4 compare cases pass")
