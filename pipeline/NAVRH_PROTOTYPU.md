# Návrh minimálního end-to-end prototypu (CZ první)

Stav: **návrh**. Implementováno a otestováno je zatím jen to, co je níže označeno ✅.

## 1. Cíl prototypu
Z **již schváleného** projektu (scénář s ID tvrzení, vyčištěné assety) vyrobit kompletní video **bez ruční práce na časové ose**:
voice-over → časování → titulky → grafika → hudba → finální MP4 + .srt + XML pro Premiere + QA report.

Rešerše, fact-check a scénář jsou v prototypu **vstupy**, ne kroky, které se automatizují. Ty přijdou v další etapě.

## 2. Struktura projektu (jedna složka = jedno video)

```
projects/<YYYY-MM>_<slug>/
  state.json              # stav kroků, hashe vstupů, schválení, minuty lidské práce, náklady
  brief.md                # G1: téma, úhel, publikum, risk score
  sources.jsonl           # S001…  zdroj + tier A–D + cesta ke snapshotu
  sources/                # S001.html / .pdf / .txt (snapshot), S001.meta.json
  claims.jsonl            # C001…  atomická tvrzení → evidence (source_id + citace/čas) + status
  script.cs.md            # master scénář; každá věta s fakty končí značkou [C003]
  script.de.md            # lokalizace se stejnými značkami
  lexicon.cs.json         # výslovnost: "Jawed Karim" → "Džaved Karím" (přepis pro TTS)
  shotlist.cs.json        # SC001…  text, claim_ids, vizuály (šablona + asset_id), zdroj na obrazovce
  assets.jsonl            # A001…  původ, licence, atribuce, riziko, status (cleared/…)
  assets/{photo,clip,graphic,music,sfx}/
  audio/cs/SC001.wav …    # hlas po scénách (opakovatelné jednotlivě)
  audio/cs/narration.wav  # spojená stopa + timings.json (začátek/konec scén, slova)
  render/preview.mp4, render/final.mp4, render/subtitles.cs.srt, render/timeline.xml
  qa_report.md            # automatické kontroly + checklist lidských bran
  publish/cs/{title.txt,description.txt,thumbnail_*.png}
  logs/<step>-<timestamp>.log
```

**Proč takto:**
- *Navázání po chybě:* každý krok zapisuje jen do svých výstupů. `state.json` ukládá hash vstupů. Při změně scénáře se zneplatní jen hlas, titulky a render, ne rešerše.
- *Opakování jednotlivých kroků:* hlas se generuje **po scénách**, takže oprava jedné věty znamená přegenerovat jeden soubor.
- *Dohledatelnost:* věta ve videu → `SC012` → `C031` → `S007` → snapshot a citace či časová značka.
- ✅ Schémata JSON jsou v `pipeline/schemas/`. ✅ Validátor `pipeline/validate.py` kontroluje schémata i křížové vazby a blokuje neověřená tvrzení, chybějící účel citace a realistické AI zobrazení skutečné osoby. Ukázka je v `projects/_example_test_text/`.

## 3. Kroky prototypu (CLI, deterministické)

| Krok | Příkaz | Vstup → výstup | Nástroj | Ověření |
|---|---|---|---|---|
| P0 | `vid validate` | projekt → seznam chyb | `validate.py` ✅ | 0 chyb = lze pokračovat |
| P1 | `vid voice` | shotlist + lexicon → `audio/cs/SCxxx.wav` | adaptér TTS (piper / později API) | Whisper zpětný přepis, CER < práh, kontrola termínů |
| P2 | `vid assemble-audio` | SC wav → `narration.wav` + `timings.json` | Python + FFmpeg | pauzy 0,35 s mezi větami, 0,8 s mezi scénami |
| P3 | `vid subtitles` | narration + text → `.srt` | Whisper slovní časy, zarovnané na **schválený text** (ne na přepis) | ≤ 42 znaků/řádek, ≤ 2 řádky, ≤ 17 zn./s, min. 1 s |
| P4 | `vid graphics` | shotlist → PNG/MOV vrstvy | **fáze 1: Pillow + FFmpeg**, fáze 2: Remotion | náhled v kontaktním listu |
| P5 | `vid render` | vrstvy + audio → `preview.mp4` | FFmpeg (Ken Burns `zoompan`, `xfade`, overlay) | ffprobe: 1080p25, délka = audio ± 0,1 s |
| P6 | `vid mix` | hlas + hudba + SFX → finální audio | FFmpeg `sidechaincompress` (ducking), `loudnorm` | −14 LUFS ±1, TP ≤ −1 dBTP |
| P7 | `vid export` | → `final.mp4`, `.srt`, `timeline.xml` | FFmpeg + OpenTimelineIO (FCP XML) | otevře se v Premiere |
| P8 | `vid qa` | vše → `qa_report.md` | `blackdetect`, `freezedetect`, LUFS, validátor | report bez ERROR |

**Šablony vizuálů v1** (pokrývají dokumentární styl bez cizích klipů): `title_card`, `number_callout`, `quote_card` (citace se zdrojem), `source_card` (screenshot titulku článku + logo médium/datum), `timeline`, `map`, `photo_kenburns` (jen *cleared* fotky), `chart`. Jednotná paleta, font a pohyb určí vizuální identitu kanálu.

**Rozhodnutí FFmpeg vs. Remotion:** první průchod jen FFmpeg + Pillow. Je bez Node závislostí, nejrychleji ověří celý řetězec a stačí na statické karty s pohybem kamery. Remotion (zdarma pro jednotlivce a firmy do 3 zaměstnanců) přidáme ve chvíli, kdy budou potřeba animované časové osy, mapy a kinetická typografie. Pokud to nebude potřeba, nepřidáme ho.

**Premiere jako finální krok:** automat vyrobí hotové video. Pro „lidské dočištění“ exportuje i XML časovou osu, takže střihač upravuje scény místo skládání od nuly.

## 4. Co se automatizovat (zatím) nedá spolehlivě
- výběr *nejlepšího* záběru a rytmu střihu (vyžaduje vkus a kontext),
- posouzení, zda je cizí klip legitimní citací,
- finální poslech hlasu (TTS občas chybuje v přízvuku nebo frázování, což metriky nezachytí),
- německá jazyková korektura (viz níže).

## 5. Automatizace německé kontroly – jak to změříme
Pilot: rodilý korektor opraví DE scénář a poslechne DE hlas. **Předtím** stejný text projde automatickou kontrolou (LLM korektura podle kontrolního seznamu + zpětný přepis hlasu Whisperem + kontrola jmen podle lexikonu).
Pak porovnáme nálezy:
- **recall** = podíl korektorových nálezů, které našel i automat,
- **precision** = podíl automatických nálezů, které korektor uznal.

Pravidlo [HYPOTÉZA, ověřit na 3–5 videích]: pokud automat dosáhne recall ≥ 90 % u věcných a gramatických chyb, korektor přejde z plného čtení na **rychlou kontrolu označených míst a poslech** (odhad 30–45 min místo 2–3 h). Stylistika a přirozenost hooku zůstanou u člověka.
