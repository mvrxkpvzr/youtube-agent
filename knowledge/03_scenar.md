# 03 Scénář: hook, stavba, věty pro ucho

**Kdy číst:** fáze 4 (scénář a střihový plán, brána G3).

## Stavba videa 8–12 min (dějství = pole `act` ve shotlistu)
| Dějství | Čas | Úkol |
|---|---|---|
| `hook` | 0–25 s | Kontrast nebo šokující číslo v 1. větě. Splnit slib z názvu. Otevřít hlavní otázku do 25 s. |
| `setup` | do ~1:30 | Kdo, kde, proč by nás to mělo zajímat. Jen to, co je potřeba k pochopení zvratu. |
| `rise` | | Eskalace: každých 20–40 s nová informace, která situaci zhorší („ale“) nebo posune („proto“). |
| `turn` | ~střed | Velký zvrat. Druhá otevřená otázka, která nese druhou půlku. |
| `consequence` | | Co to stálo: konkrétní lidé, čísla, soud. |
| `payoff` | posl. 1–2 min | Odpověď na otázku z hooku + vlastní pointa (názor kanálu). Callback na číslo/obraz z hooku. |
| `outro` | ≤ 20 s | Krátce. Otázka do komentářů nebo odkaz na další video. Žádné „nezapomeňte odebírat“. |

[Praxe, uniklý dokument MrBeast]: nejdůležitější je první minuta, pak minuty 1–3 a 3–6. Nejsilnější materiál
se nešetří na konec, rozloží se tak, aby každý úsek měl „wow“ moment.

## Hook (prvních 25 s) – povinné prvky
1. **1. věta = konkrétní obraz nebo číslo**, ne úvod. „Až dvanáct tisíc dolarů. Za jeden víkend.“ [U nás, Fyre]
2. **Kontrast** do 10 s (slib × realita).
3. **Otevřená otázka** do 25 s. [U nás] TOGI v1 měl první otázku v 55 s, v2 v 19 s.
4. **Proč zůstat:** náznak, že konec přinese něco, co divák nečeká („a to nejpodivnější přijde až potom“).
   Musí se to opravdu stát, jinak je to clickbait.
5. **Fakta do hooku vybírej podle neznalosti** [Praxe, cdeistopened/youtube-scriptwriting]: u každého kandidátního faktu
   odhadni, kolik diváků ho **nezná**. Do hooku patří ten, který zná málokdo a přitom je pochopitelný hned.
6. **Hlas, text na obrazovce a obraz v hooku říkají totéž** (jedna myšlenka, tři kanály), jinak se pozornost rozdělí.
7. **Zakázáno v hooku:** pozdrav, „v dnešním videu“, představení kanálu, logo intro, shrnutí obsahu, sponzor.
[Praxe] Cíl retence v 30. s ≥ 60–65 % (vidIQ). Ověř po publikaci v grafu „Úvod“.

## Pravidlo „ale / proto“ (Parker & Stone, South Park) [Praxe]
Mezi dvěma beaty nesmí jít říct „a pak“. Musí jít říct „ale“ (konflikt) nebo „proto“ (příčina → následek).
- Kontrola: přečti jen první věty scén za sebou. Když to je seznam událostí, přepiš na příčiny a překážky.
- `craft_check.py` měří poměr vět, které začínají „A / Pak / Potom“ vs. „Ale / Jenže / Proto / Takže“.

## Otevřené smyčky
- Hlavní smyčka: otázka z hooku, uzavřená v `payoff`.
- Malé smyčky: každá 1–2 min otevři menší otázku („proč by někdo posílal e-mail za bankéře?“) a uzavři ji
  o 30–90 s později. Nikdy nenech smyčku neuzavřenou.
- Smyčky označ ve shotlistu `"beats": ["rehook"]` u scény, která ji otevírá (kontrola mezer, viz `04`).

## Věty pro ucho (čeština, TTS)
- Průměr 8–14 slov na větu, ale **různé délky**: krátká úderná věta po dlouhé. Žádná věta nad 25 slov.
- Jedna myšlenka na větu. Podmět a sloveso brzy.
- Čísla zaokrouhli, kde přesnost nic nepřidá („skoro šest milionů“), přesné číslo jen jako pointu.
- Čísla a data vždy slovy v `narration_tts` (TTS je čte špatně) [U nás].
- Cizí jména: přepis výslovnosti v `lexicon.cs.json`, ověř `tools_lexicon_probe.py` [U nás].
- „Podle jeho slov / podle NBC“ u každého tvrzení se stavem `attributed` [U nás, validátor].
- Konkrétnost: ≥ 60 % vět obsahuje číslo, jméno nebo hmatatelný předmět [U nás, ai_smell Fyre 63 %].

## Hlas kanálu (osobnost vypravěče)
- Suchý, mírně ironický vypravěč, který fakta bere vážně a lidi v příběhu ne vždy. Komentuje, nemoralizuje.
- Názor vypravěče je jasně názor („podle mě“, „to je vlastně byznys model, jen bez byznysu“). Ve scénáři ho
  označ `⟨názor⟩`, aby šel oddělit od faktů ve fact sheetu.
- Mluví k jednomu divákovi („vy“ ne „vy všichni“), bez patosu.

## Zakázané fráze (AI pach, `craft_check.py` je hledá)
„pojďme se podívat“, „ponořme se“, „v dnešním videu“, „nezapomeňte“, „fascinující“, „neuvěřitelný příběh“,
„je důležité si uvědomit“, „stojí za zmínku“, „v neposlední řadě“, „na závěr lze říci“, „představte si svět“,
„cesta plná“, „nejen že…, ale také“, „zkrátka a dobře“, „v konečném důsledku“, „šokující pravda“, „odhalíme tajemství“,
„a to není všechno“, „svět, kde“, „hra se změnila“. Seznam je v `knowledge/craft_rules.json`, rozšiřuj ho.

## Kontrola před G3
- `craft_check.py` bez ERROR.
- Showrunner tabulka (háček, záhada, sázky, padouch, pointa) – každé ≥ 7/10, jinak přepiš slabé místo.
  Pozor: hodnotí stejný agent, který psal → napiš to ve zprávě („není nezávislé“).
- Přečti celý scénář nahlas tempem 150 slov/min (odhad délky) a škrtni 10 % slov. Vždy se něco najde.
