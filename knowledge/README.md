# Znalostní vrstva agenta (knowledge/)

Tahle složka je „řemeslo“ kanálu: co dělá dobré YouTube video, jak to poznat a jak to měřit.
Agent `viral-video` ji čte **před každou fází** a jeho výstupy se proti ní kontrolují skriptem
`pipeline/craft_check.py`. Pravidla nejsou dogma: každé má štítek důkazu a cíle se upravují podle
skutečných čísel z YouTube Studia (`11_po_publikaci.md`).

## Štítky důkazu (používej je i ve svých výstupech)
| Štítek | Význam |
|---|---|
| **[U nás]** | změřeno na našich videích (TOGI, Fyre). Nejsilnější důkaz pro tento kanál. |
| **[YouTube]** | oficiální nápověda nebo pravidla YouTube. Závazné. |
| **[Praxe]** | shoda praktiků a nástrojů (vidIQ, retenční editoři, uniklý dokument MrBeast). Rozumné výchozí nastavení, ne zákon. |
| **[Hypotéza]** | náš odhad. Ověřit A/B testem nebo analytikou, pak přepsat na [U nás]. |

## Závazné moduly od Miry (21. 10. 2026) – mají přednost před ostatními playbooky
- `00_role.md` – role kreativního ředitele, pravidla práce, dvě role kontroly, skóre 0–10, nulový rozpočet, předání.
- `12_vizualni_reserse_a_prava.md` – nejdřív autentický materiál, právní kategorie A–F, manifest zdrojů, vizuální plán.
- `09_hudba_a_zvuk.md` – jen hudba od lidských skladatelů, skutečné ruchy, licence každé stopy, kontrola před exportem.
- Modul 4.0 (studio a neustálé zlepšování) je rozepsaný do `01` (skóre tématu), `04`, `06`, `11` (postmortem) a do bran Q1–Q7.

## Mapa: fáze → co číst → co kontroluje stroj
| Fáze agenta (SKILL.md) | Číst | Strojová kontrola |
|---|---|---|
| 1 Téma a úhel (G1) | `00`, `01`, `02` | brána Q1 hledá skóre tématu v `brief.md` |
| 2–3 Fakta (G2) + vizuální rešerše | `01`, `12` | `validate.py` → **Q1**; `visual_sources.jsonl` založit hned |
| 4 Scénář a střihový plán (G3) | `03`, `04`, `05`, `06` | `craft_check.py` → **Q2** |
| 4b Vizuální plán a storyboard | `06`, `07`, `12` | `visual_plan.py` → **Q3** |
| 5 Hlas, titulky, časování | `08` | `vid.py check`, `vid.py subs` → **Q4** |
| 5b Střihový list + levný náhled | `04`, `08`, `09` | `edl.py`, `review/preview_<lang>.md` → **Q5** |
| 5c Finální render (G4 práva) | `07`, `09`, `10` | `vid.py render --final` **odmítne běžet bez Q1–Q5**; `vid.py qa` → **Q6** |
| 8 Balíček (G5) | `02`, `10`, `11` | **Q7**: 3 názvy + 3 náhledy, popis s kapitolami, credits, manifest |
| Po publikaci | `11` | `postmortem.md`, `lessons.md` |

**Dvě sady bran:** G1–G5 schvaluje Mira (`gates.json`, nikdy je nenastavuje skript). Q1–Q7 jsou strojové brány kvality
(`python3 pipeline/gates.py <projekt> --lang cs` → `quality_gates.<lang>.json`). Když brána selže, oprav příslušnou fázi,
neschovávej vadu. Výjimka jen `vid.py render --final --override-gates "důvod"` – důvod se zapíše do `review/gate_overrides.md`
a musí být ve zprávě Mirovi.

`references/` = případové studie konkurenčních kanálů (techniky `TQ-xxx`, vlastní vlákno). Playbooky na ně odkazují jako [Praxe].
`lessons.md` = co jsme se naučili na konkrétních videích. Čti ho na začátku **každého** projektu.
`zdroje.md` = odkud pravidla pochází (výzkum 21. 10. 2026).

## Jak agent pracuje s touto vrstvou
1. Na začátku projektu přečti `lessons.md` a playbook fáze, kterou děláš. Ne všechny najednou.
2. Každé rozhodnutí, které se odchyluje od playbooku, zapiš do `projects/<p>/decisions.md` s důvodem.
3. Po každé fázi spusť `python3 pipeline/gates.py projects/<p> --lang cs --upto Qn` (nebo jednotlivě `craft_check.py`,
   `visual_plan.py`, `edl.py`). FAIL/ERROR = oprav, než ukážeš Mirovi. WARN = oprav, nebo napiš, proč ne.
4. Co se na projektu ukáže jako nové (chyba, trik, číslo z analytiky), připiš do `lessons.md` (datum, projekt, důkaz).
5. Pravidla v playboocích měň jen na základě [U nás] důkazu a změnu zapiš do `lessons.md`.

## Šest zásad kanálu (shrnutí všeho níže)
1. **Balíček dřív než video.** Název + náhled musí být lákavé dřív, než se napíše první věta. Slib z náhledu se splní do 30 s.
2. **Každá věta je buď informace, nebo napětí.** Žádná vata, žádné „a pak“. Spojky „ale“ a „proto“.
3. **Oko se nesmí nudit, ale střih má význam.** Obraz se mění, když přidá informaci (orientačně každé 2–4 s), pohyb aspoň
   v každém 3. záběru, statická karta nad 3,5 s jen se záměrem.
4. **Fakta na obrazovce, názor v hlase.** Každé tvrzení má doklad v obraze. Humor jen jako názor a ironie, nikdy jako vymyšlený fakt.
5. **Nejdřív skutečný svět, pak rekonstrukce; lidská hudba.** Autentický materiál s posouzenými právy (`12`), hudba od lidí (`09`).
6. **Nesmí to působit jako AI.** Konkrétní detaily, vlastní úhel a názor, různá délka vět, ruční řemeslo v obraze. Masově vyráběné šablonové video YouTube nemonetizuje.
