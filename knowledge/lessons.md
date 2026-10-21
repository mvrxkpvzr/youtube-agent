# Lekce z projektů (verzovaná znalostní báze)

Formát: `datum · projekt · zjištění · důkaz · co měníme (kde)`. Nejnovější nahoře. Čti na začátku každého projektu.
Změna pravidla v playbooku = zápis sem + zmínka Mirovi.

## v1 – 21. 10. 2026 (založení znalostní vrstvy)

### Fyre Festival (pilot, verze 1.2), měřeno `craft_check.py` 21. 10. 2026 na kopii projektu
- Tempo 162 slov/min, první otázka v 0:23, 55 % času skutečný obraz a doklady → splňuje cíle `04` a `06`.
- **Rytmus příběhu:** tři úseky 62–88 s bez nové otázky, zvratu nebo vtipu (od 0:23, 1:24, 4:16). Shotlist nemá pole `beats`,
  takže stroj vidí jen otazníky → v příštích projektech beaty značit (`03`, `04`).
- **„A pak“ místo „ale/proto“:** 16 vět začíná „A/Pak“, jen 7 „Ale/Jenže/Proto“ → pravidlo ale/proto v `03`.
- Konkrétních vět 55 % (cíl 60 %); ai_smell skript pilotu dřív naměřil 63 % s jinou heuristikou → sjednoceno v `craft_check.py`.
- **Textové karty 36 % času** (cíl ≤ 30 %), 31 statických karet nad 3,5 s, 8× tři stejné šablony za sebou → slideshow riziko (`10`).
- 32 syntetických efektů (whoosh/hit) → podle modulu hudby jen výjimečně, preferovat skutečné nahrávky (`09`).
- Název č. 3 má 79 znaků → na mobilu se ořízne (`02`).
- Zpětný přepis SC044 a SC050: čísla „2“ a „100“ nenalezena → brána Q4 to blokuje.
- Fotky z Wikimedia Commons fungovaly; vizuální rešerše ale nebyla zapsaná jako manifest → nový `visual_sources.jsonl`
  a `visual_plan.<lang>.json` (formát dohodnutý s pilotním vláknem).

### TOGI (18. 10. 2026), z SKILL.md
- Průměrná délka záběru v1 11,3 s → v2 2,5 s; tempo 104 → 152 slov/min; první otázka 55 s → 19 s.
- Anton rozbíjí háčky ve 3D, Archivo Black ne. Emise textu > 2 se rozpije. Poslední klíčový snímek kamery za posledním objektem = prázdný konec.
- Popis videa změnil celý úhel (skeč vs. realita) → vždy číst popisy.

### Rozhodnutí Miry, která mění dřívější návrhy
- 21. 10. 2026: **žádná AI hudba ani AI zvuky** → ACE-Step a MOSS-SoundEffect z `pruzkum_github_hlas_hudba_blender.md` se nepoužijí (`09`).
- 21. 10. 2026: nejdřív autentický materiál z internetu s právním posouzením A–F, vlastní 3D až potom (`12`).
- 21. 10. 2026: hlas – využívat Piper Jirka, pokud odpovídá stylu; monotónnost řešit textem a rytmem, ne hudbou (`08`).
