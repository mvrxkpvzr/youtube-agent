# Protokol analýzy jednoho videa

Vstup: URL videa z `sample_plan.md`. Nástroj: Claude in Chrome (cloud ani počítač YouTube nepustí).

1. Otevřít `https://www.youtube.com/watch?v=<id>` a spustit `tools/extract_watch.js` (javascript_tool).
   Výstup: metadata (název, datum, délka), kapitoly z popisu, titulky s časy, odhad střihů ze storyboardu.
   Výstup se **neukládá do repa** (titulky jsou cizí text); zpracovává se jen do vlastních poznámek.
2. Prohlédnout storyboard (mřížka náhledů) a zařadit vizuální kategorie po úsecích:
   archival-video, archival-photo, document/screenshot, news-headline, map, chart/graph, motion-graphics-text,
   3d, original-animation/illustration, stock, talking-head, b-roll-original.
3. Přehrát v přehrávači minimálně: 0:00–1:30 (hook a slib), přechod do 2. aktu, hlavní odhalení, posledních 90 s.
   U těchto úseků ručně spočítat střihy a popsat hlas, hudbu, ambient, ticho, přechody (`source=player`, `confidence=high`).
4. Náhled: otevřít `https://i.ytimg.com/vi/<id>/maxresdefault.jpg`, popsat kompozici (počet prvků, tvář/objekt,
   text v náhledu, kontrast, vztah k názvu: opakuje / doplňuje / vytváří otázku).
5. Zapsat do `videos.jsonl` jeden řádek (pole níže) a do `observations.jsonl` časově ukotvené záznamy:
   každé z 10 témat zadání aspoň jedno pozorování; interpretace zvlášť.
6. Nově rozpoznanou obecnou techniku přidat do `techniques.md` (TQ-nn) s odkazy na pozorování, která ji dokládají
   (min. 2 kanály, jinak označit „jen 1 kanál“).
7. `python3 search.py --check` musí projít.

## Pole `videos.jsonl`
`id` (V-<slug>-NN), `channel`, `title`, `url`, `published` (YYYY-MM-DD), `runtime_s`, `selection_reason`,
`topic`, `narrative_question`, `hook` {`t_end`, `summary`, `promise`}, `structure` [{`t`, `beat`}], `revelations` [..],
`payoff`, `visual` {`cuts_est`, `cuts_per_min`, `method`, `categories` {kategorie: podíl 0–1}},
`archival_maps_graphics_3d` (text), `audio` {`voice`, `music`, `ambience`, `silence`, `transitions`},
`evidence` (jak jsou tvrzení doložena na obrazovce), `thumbnail` {`composition`, `title_relation`},
`works` [..], `improve` [..], `transfer` [..], `techniques` [TQ-nn], `analysed_via` [transcript|player|storyboard|thumbnail],
`confidence`, `analysed_at`.
