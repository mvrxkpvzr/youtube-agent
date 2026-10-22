# Protokol analýzy jednoho videa

Vstup: URL videa z `sample_plan.md`. Nástroj: Claude in Chrome v uživatelově prohlížeči (cloud YouTube nepustí).
Nic se nestahuje ani neukládá: titulky a snímky jsou jen v paměti stránky a do knihovny jdou vlastní poznámky.

1. Otevřít `https://www.youtube.com/watch?v=<id>` a počkat na načtení.
2. Celý soubor `tools/run_watch.js` vložit **jako text** do `javascript_tool` (stránka blokuje `eval` uložené kopie
   přes Trusted Types; obcházení této ochrany nezkoušet). Ve stejném `browser_batch` přečíst `get_page_text`.
   - Výstup A (hned): metadata, slova a tempo řeči (WPM), mezery ve vyprávění ≥3 s, přepis po 20s blocích v `#__ov`.
     U dlouhých videí zkrátit `#__ov` na hlavičku + bloky do 200 s, posledních ~200 s a každý k-tý blok (k = bloky/30).
   - Výstup B (na pozadí, `window.__B`): kontaktní listy (40 snímků celého videa + 30 snímků prvních 90 s), náhled,
     odhad střihů a hladiny zvuku ve 3 oknech (začátek, střed, konec).
3. Dotazovat `window.__B.status` po jednom volání (smyčka max. 14 × 2,5 s; `browser_batch` má limit 60 s celkem).
   Při `done` zobrazit `#__vis` a udělat snímek obrazovky (náhled + kontaktní listy), přečíst `window.__B.windows`.
4. Zapsat do `videos.jsonl` jeden řádek a do `observations.jsonl` časově ukotvené záznamy: každé z 10 témat zadání
   aspoň jedno pozorování; interpretace jako samostatné záznamy (`kind=interpretation`).
5. Obecnou techniku doložit v `techniques.md` (TQ-nn) odkazy na pozorování (min. 2 kanály, jinak to napsat).
6. `python3 search.py --check` musí projít (kontroluje i to, že TQ cituje existující O-id).

## Známé meze měření
- Střihy: rozdíl barevného histogramu mezi snímky při 4× rychlosti; plynulé 3D pohyby a posuny ve fotkách
  podhodnocuje. Je to orientační srovnání mezi kanály, ne přesný počet.
- Zvuk: medián RMS v dB z Web Audio při hlasitosti přehrávače; relativní srovnání, ne LUFS.
- Kapitoly z popisu skript nenačte; zapisují se ručně z přehrávače.
- Kanály jen s automatickými titulky (např. Barely Sociable) mají přepis bez velkých písmen a interpunkce.

## Pole `videos.jsonl`
`id` (V-<slug>-NN), `channel`, `title`, `url`, `published` (YYYY-MM-DD), `runtime_s`, `selection_reason`,
`topic`, `narrative_question`, `hook` {`t_end`, `summary`, `promise`}, `structure` [{`t`, `beat`}], `revelations` [..],
`payoff`, `visual` {`cuts_per_min`, `method`, `categories`}, `archival_maps_graphics_3d` (text),
`audio` {`voice`, `music`, `ambience`, `silence`, `transitions`}, `evidence`, `thumbnail` {`composition`, `title_relation`},
`works` [..], `improve` [..], `transfer` [..], `techniques` [TQ-nn], `analysed_via` [transcript|player|thumbnail],
`confidence`, `analysed_at`.
