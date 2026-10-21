# Pipeline `vid` – stav k 18. 10. 2026

Deterministický řetězec od schváleného shot listu k hotovému videu. Žádní agenti, jen Python + FFmpeg.
Spouští se Pythonem z prostředí Qwen. Cesty k prostředím jsou v `config.json` a leží v dočasné složce session.

```
PY=~/youtube-agent-env/venv/qwen/bin/python   # viz README_SETUP.md
$PY -I pipeline/vid.py validate projects/<projekt>
$PY -I pipeline/vid.py all projects/<projekt> --lang cs     # voice → check → audio → subs → render → qa
$PY -I pipeline/vid.py status projects/<projekt>           # kroky + zastaralé kroky (změněné vstupy)
python3 pipeline/factsheet.py projects/<projekt>          # fact sheet pro bránu G2
$PY -I pipeline/snapshot.py projects/<projekt> S020 <url> --grep slovo1,slovo2
$PY -I pipeline/tools_lexicon_probe.py piper_cs cs "<termín>" "<věta s {}>" variantaA variantaB
```

| Modul | Co dělá | Ověřeno |
|---|---|---|
| `lib/textprep.py` | lexikon výslovnosti (`lexicon.<lang>.json`), **zákaz číslic v TTS textu** (vyžaduje `narration_tts`), upozornění na zkratky a cizí slova | ✅ na testovacím projektu |
| `lib/voice.py` + `workers/` | TTS po scénách. Cache podle hashe textu a enginu, takže se přegenerují jen změněné scény. Licence enginu se zapisuje k audiu | ✅ Piper CS 10 scén / 5 s; Qwen DE 10 scén / 311 s |
| `lib/asr_check.py` | zpětný přepis (Whisper), detekce vynechaného textu (≥ 4 slova) a chybných čísel | ✅ 4 unit testy z reálných chyb + běh na CS/DE |
| `lib/audio.py` | spojení scén, mezery 0,8 s, `timings.json` | ✅ |
| `lib/subtitles.py` | .srt ze **schváleného textu** (ne z přepisu), časování podle slov z Whisperu, max 2×42 znaků | ✅ (DE má 6 titulků nad 17 zn./s → WARN) |
| `lib/graphics.py` | šablony: title, number, quote, source card (s překladem citace), timeline, photo, generic + řádek „Zdroj: …“ | ✅ vizuálně zkontrolováno |
| `lib/render.py` | pomalý zoom na kartách, prolínání přes tmu, úprava hlasu (HP, kompresor, limiter), dvouprůchodová normalizace na −14 LUFS | ✅ |
| `lib/qa.py` | rozlišení, fps, kodeky, LUFS, true peak, černé úseky, statický obraz, titulky, zpětný přepis, validátor, licence hlasu | ✅ (zachytil 3 skutečné chyby, viz výsledky) |
| `lib/editplan.py` | střihový plán `render/editplan.<lang>.json` (scény s vlastními klipy, zvukem, titulky, přechody; schéma `schemas/editplan.schema.json`) a jeho převod na časovou osu editoru | ✅ `tests/test_editplan.py` + testovací projekt |
| `lib/artcraft.py` + `artcraft/` | střih a export v **editoru ArtCraftu** bez obsluhy (`vid.py artcraft`), master do mp4, viz `artcraft/README.md` | ✅ testovací projekt fyre7 |
| `lib/verify_export.py` | ověří export proti plánu: přehratelnost, délka, časová osa editoru, obraz klip po klipu, hlas po scénách, černé úseky | ✅ |
| `validate.py` | schémata a křížové vazby tvrzení, zdrojů a assetů | ✅ 5/5 negativních testů |

| `craft_check.py` | řemeslo podle `knowledge/`: hook a první otázka, mezery bez beatu, AI fráze, rytmus vět, „a pak × ale/proto“, tempo, délky záběrů, mix obrazu, humor, hudba a SFX, délka názvu → `craft_report.<lang>.md` | ✅ testy + kopie pilotu Fyre |
| `visual_plan.py` | manifest vizuálních zdrojů (`visual_sources.jsonl`, práva A–F) + vizuální plán scén → `visual_plan.<lang>.md` | ✅ testy |
| `edl.py` | střihový list před drahým renderem → `render/edl.<lang>.json` + `.csv` (přenositelný do editoru) | ✅ testy + Fyre |
| `gates.py` | brány kvality Q1–Q7 → `quality_gates.<lang>.json`; `vid.py render --final` i `vid.py artcraft --final` vyžadují Q1–Q5 | ✅ testy |

Testy: `pipeline/tests/test_validate.py`, `pipeline/tests/test_asr_compare.py`, `pipeline/tests/test_knowledge_checks.py` (jen stdlib + jsonschema), `pipeline/tests/test_editplan.py`, `pipeline/tests/test_verify_export.py`.

**Zatím chybí:** hudba a SFX (není licencovaná knihovna), export XML do Premiere (OpenTimelineIO), fotografie a klipy (šablona `photo_kenburns` existuje, ale je netestovaná), Remotion (zatím není potřeba).
