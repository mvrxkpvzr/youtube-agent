# 04 Retence a tempo

**Kdy číst:** fáze 4 (scénář, střihový plán) a po renderu. Strojově: `craft_check.py`.

## Co YouTube měří a proč na tom záleží
- **CTR** (klik z náhledu), **AVD** (průměrná doba sledování), **AVP** (průměrné procento zhlédnutí). [Praxe, MrBeast]
- Vestavěný A/B test náhledů vybírá podle podílu času sledování [YouTube] → klik bez udržení nevyhrává.
- Retenční graf v Studiu: „Úvod“ = % diváků v 30. s. Cíl [Praxe, vidIQ]: ≥ 60 %, dobré háčky > 65 %.

## Kritická místa videa
| Místo | Riziko | Opatření |
|---|---|---|
| 0–30 s | největší odchod | hook podle `03`, žádné intro, slib z názvu splněný |
| 25–35 s | druhá vlna odchodu [Praxe, AIR Media-Tech] | první velký „pattern interrupt“: nový typ obrazu + zvuk + nová informace |
| 1:00–3:00 | divák se rozhoduje, jestli zůstane | eskalace, první malá otevřená smyčka uzavřená, nová otevřená |
| 3:00–6:00 | [Praxe, MrBeast] druhý nejdůležitější úsek | nejzajímavější a nejjednodušší materiál, ne vata |
| střed | únava | velký zvrat (`turn`), změna hudby, nový vizuální svět (mapa, 3D) |
| posl. 60 s | odchod při „shrnutí“ | žádné shrnutí; payoff = nová informace + pointa; outro ≤ 20 s |

## Stav příběhu se mění každých ~20–45 s (zadání Miry)
Každých 20–45 s musí přibýt aspoň jedno: nová informace, nová otázka, vizuální událost, změna perspektivy, důležitý vtip.
Není to rigidní limit, ale `craft_check.py` hlásí úsek > 45 s bez „beatu“ (otázka, zvrat, humor, re-hook) jako WARN.
Beaty označ ve shotlistu `"beats": ["rehook" | "twist" | "humor" | "question" | "reveal" | "payoff" | "breather"]`.
Umělé cliffhangery zakázány: napětí musí vycházet z obsahu.

## Tempo řeči a obrazu
| Metrika | Cíl | Důkaz |
|---|---|---|
| tempo hlasu | 145–170 slov/min | [U nás] TOGI v1 104 slov/min = nuda; v2 152 |
| průměrná délka záběru | 2–3,5 s | [U nás] v1 11,3 s; v2 2,5 s |
| statická karta | ≤ 3 s | pravidlo kanálu |
| pohyb (3D/2,5D/klip/mapa) | aspoň každý 3. záběr | pravidlo kanálu |
| první otevřená otázka | ≤ 25 s | [U nás] |
| mezera bez beatu | ≤ 45 s | zadání Miry |

Pozor [Praxe]: přestříhání škodí. B-roll zvyšuje retenci jen když **přímo ilustruje** řečené (kontrolovaný test
Opus Clip: +3–7 %, generický b-roll nic nebo pokles). Rychlý střih bez obsahu = AI pach. Ne „každé 2 s něco“, ale
„každé 2 s něco, co nese informaci“. Klidné místo (`breather`) po silném momentu je dovolené a potřebné.

Modul 4.0 § D: obraz se mění, když to **přidává význam**, ne podle pevného pravidla sekund na záběr. Prahy v tabulce
jsou proto jen WARN v `craft_check.py`: signál k zamyšlení, ne povinnost. Drž kontinuitu geografie, dat, měřítka,
světla, typografie a perspektivy.

## Rytmus scén
- Střídej délky: 3 rychlé záběry → 1 delší (fotka, která má co ukázat) → rychlá série.
- Důležité číslo nebo citace: obraz drží tak dlouho, aby se dal přečíst (≥ 0,4 s na slovo textu, min. 1,2 s).
- Pauza před pointou (0,3–0,6 s ticha nebo jen hudba) zvyšuje účinek. Pauza po pointě dá divákovi čas se zasmát.

## Po renderu
1. `craft_check.py` s časováním (`audio/<lang>/timings.json`) – skutečné tempo a délky záběrů.
2. Kontaktní list po 5 s a projet video 2× rychleji: kde se nic neděje 10 s, tam divák odejde.
3. Po publikaci: retenční graf → propady > 5 bodů během 10 s zapiš do `lessons.md` s časem a scénou.
