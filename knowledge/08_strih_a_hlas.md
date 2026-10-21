# 08 Střih, hlas a titulky

**Kdy číst:** fáze 5 (hlas, titulky, render) a při kontrole renderu.

## Střih (zadání Miry § 10)
- Střih reaguje na **význam, rytmus a pozornost**. Automatické střídání obrázků po pevném intervalu není střih.
- Každý střih má funkci (i „oddech“). Hledej: vizuální pointy, **match cut** (stejný tvar/kompozice: vila → stan),
  grafické přechody, rytmické montáže (série 4–6 rychlých záběrů na výčet), záměrné pauzy.
- Střih na slovo: obraz se mění na podstatném jméně, které ukazuje (slovní časy z Whisperu v `SCxxx.words.json`).
- J-cut / L-cut: zvuk další scény začne o 0,2–0,5 s dřív, nebo ruch dozní pod další scénou. Plynulost bez prolínaček.
- Prolínačky střídmě; tvrdý střih je výchozí. `xfade_s` 0,15 [U nás].
- Komediální střih: věta → 0,3–0,6 s pauza → tvrdý střih na důkaz.
- Kontrola: kontaktní list (`ffmpeg … fps=1/5,tile=6x5`) a projetí 2× rychlostí; viz `04`.

## Hlas (TTS)
- Engine podle projektu: `moss_cs` (přirozenější, pomalý), Piper **Jirka** `cs_CZ-jirka-medium` (rychlý, robotičtější;
  zadání Miry: využívej české hlasy Piper, zejména Jirku, pokud odpovídá stylu). Volbu zapiš do `decisions.md`.
- Monotónní řeč: **nejdřív uprav text, rytmus a segmentaci** (kratší věty, pointa na konci, rozdělení scén, pauzy),
  ne hudbou. [U nás] Piper `length_scale` 0,64 ≈ 152 slov/min; zrychlení zvyšuje WER – sleduj `vid.py check`.
- Před syntézou: jazyková kontrola a vyslovitelnost – čísla slovy (`narration_tts`), cizí jména v `lexicon.cs.json`
  ověřená `tools_lexicon_probe.py` ve skutečné větě, zkratky rozepsat, anglické termíny přeložit nebo přepsat foneticky.
  Význam se nesmí změnit.
- Pauzy a důrazy jen v rozsahu, který engine skutečně podporuje (Piper: interpunkce a dělení vět; ne SSML).
- `vid.py check` (zpětný přepis): vynechaný text nebo chybné číslo = STOP, přegeneruj scénu.
- Hlas nesmí klonovat skutečnou osobu.

## Titulky
- Ze **schváleného textu**, časované podle slov (pipeline). Max 2 × 42 znaků, ≤ 17 zn./s (WARN nad), min. 1 s.
- Titulky na YouTube jako `.srt` (ne vypálené), aby šly vypnout a přeložit.
- Rychlejší řeč → víc WARN o rychlosti; řeš zkrácením textu, ne zpomalením titulků mimo řeč.

## Technická kontrola renderu (`vid.py qa`)
1080p25, H.264 + AAC 48 kHz, −14 LUFS ±1, TP ≤ −1 dBTP, žádné černé úseky a zamrzlý obraz mimo záměr, délka = audio ± 0,1 s,
titulky v synchronu, licence hlasu zapsaná. ERROR blokuje G5.
