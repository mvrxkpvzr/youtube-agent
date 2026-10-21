# 11 Publikační balíček a učení z analytiky

**Kdy číst:** fáze 8 (balíček G5) a 2–14 dní po publikaci.

## Publikační podklady (`publish/<lang>/`)
- `titles_thumbnails.md`: 3 názvy + 3 náhledy, doporučená dvojice, kde se slib splní (čas). Pravidla `02`.
- `description.txt`: 1–2 věty háček (prvních ~150 znaků je vidět nad „více“), pak kapitoly, pak zdroje, pak atribuce
  (`credits.txt`: hudba CC BY, fotky CC BY/BY-SA s autorem a licencí, mapová data).
- **Kapitoly** [YouTube]: první `00:00`, aspoň 3 časové značky vzestupně, každá kapitola ≥ 10 s. Názvy kapitol jako
  zvědavé popisky, ne „Úvod“. Generuj z `timings.json` a `act`.
- `.srt` titulky (cs), u DE verze vlastní.
- Štítek syntetického obsahu: zaškrtnout jen podle pravidel (`10`); rozhodnutí zapiš.
- Publikuje člověk (G5). Agent nic nenahrává.

## Po publikaci (Mira pošle nebo ukáže Studio; agent nic nepřihlašuje)
Zapiš do `lessons.md` po 48 h a po 14 dnech:
| Metrika | Kde | Co z ní plyne |
|---|---|---|
| CTR náhledu | Dosah | < 4 %: balíček (`02`), ne video |
| Úvod (% v 30. s) | Zapojení → retence | < 60 %: hook (`03`) |
| Propady v grafu | retenční graf | čas → scéna (`timings.json`) → příčina |
| AVD / AVP | Přehled | srovnání s předchozími videi kanálu |
| Vítěz A/B testu | Dosah | který slib funguje → pravidlo do `02` |
| Komentáře | | opravy faktů (hned řešit), nápady na další díl |
Prahy jsou [Hypotéza]; po 3–5 videích je nahraď mediánem kanálu.

## Co sbírat (modul 4.0 § H, jen se svolením Miry)
Zobrazení a CTR podle zdroje návštěvnosti · retence, hlavně prvních 30 s · výrazné propady, špičky a nejsledovanější
momenty · AVD a celkový čas sledování · noví × vracející se diváci · která videa přivádějí nové diváky · výsledky A/B testů.
Srovnávej videa podobného formátu a délky. Pozor na malé vzorky a rozdíly ve zdrojích návštěvnosti.

## Postmortem každého dílu (`projects/<p>/postmortem.md`)
1. Co fungovalo a co ne (s čísly a časy).
2. Která rozhodnutí ve scénáři nebo střihu k tomu **pravděpodobně** přispěla.
3. Jaký důkaz tuto interpretaci podporuje (a jak silný – korelace není kauzalita).
4. **Tři konkrétní změny** k otestování v příští produkci.
5. Které úspěšné prvky zachovat.
Jedno slabší video nemění strategii kanálu.

## Smyčka učení
1. Každé zjištění zapiš do `lessons.md`: datum · video · metrika/pozorování · důkaz · co měníme.
2. Když se zjištění opakuje na 2+ videích, přepiš pravidlo v playbooku a štítek na [U nás].
3. Nikdy neměň pravidla tiše: změnu playbooku zapiš do `lessons.md` a zmiň ji Mirovi.
