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
# Czech numbers spelled out for TTS vs Whisper digits (Fyre Festival false alarms)
for ref, hyp in [("vrátit dvacet šest milionů sto devadesát jedna tisíc tři sta šest dolarů", "vrátit 26 191 306 dolarů"),
                 ("Konečná cena: dvě stě čtyřicet pět tisíc tři sta dolarů.", "Konečná cena – 245 300 dolarů."),
                 ("Jedenáctého října dva tisíce osmnáct dostane šest let.", "11. října 2018 dostane 6 let."),
                 ("ukazoval dva a půl tisíce rezervací, zhruba jedno procento", "ukazoval 2,5 tisíce rezervací, zhruba 1%"),
                 ("Pátek dvacátého osmého dubna dva tisíce sedmnáct.", "Pátek 28. dubna 2017."),
                 ("třicátého prvního května", "31. května")]:
    r = compare(ref, hyp); assert r["errors"] == [] and r["wer"] == 0, (ref, r)
r = compare("vrátit dvacet šest milionů dolarů", "vrátit 25 milionů dolarů")
assert any("26000000" in e for e in r["errors"]), r
print("ok: 11 compare cases pass")
