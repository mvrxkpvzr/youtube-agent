# Doporučení pro pilot Fyre Festival: techniky k otestování

Stav 2026-10-22. Podklad: 26 videí z 15 kanálů a jedno srovnávací video o Fyre (Internet Historian), 462 záznamů
v `observations.jsonl`, katalog `techniques.md` (TQ-01 až TQ-29). Vše jsou obecné postupy; žádný záběr, text, hudba,
grafika ani identita kanálu se nepřebírá. Fakta o Fyre se ověřují nezávisle z primárních zdrojů.

## Postavení videa
Fyre už na YouTube existuje hlavně jako komedie (srovnávací video, 2017, končí před soudem: O0458). Prostor, který
zbývá: **vážné, doložené, české video, které dovypráví i to, co bylo po roce 2017**. Proto preferujeme techniky
důvěry a důkazu (TQ-13 až TQ-16) před rychlým humorem.

## Co testovat (pořadí podle očekávaného přínosu)

| # | Technika | Kde ve videu | Proč | Doklad |
|---|---|---|---|---|
| 1 | Známý konec, otázka „jak“ (TQ-01) + datovaný studený začátek s návratem (TQ-02) | 0:00–0:45 a závěr | Konec všichni znají; drží to „jak se to mohlo stát“. Přesné datum a čas dodají váhu, návrat v závěru uzavře oblouk. | O0001, O0002, O0148, O0161, O0234, O0376 |
| 2 | Slib vs. realita (TQ-18) | háček a první zlom | Nejsilnější kontrast kauzy, srozumitelný beze slov. U nás vlastní typografická montáž slibů se zdrojem a datem. | O0444, O0446, O0019 |
| 3 | Dokumenty aktérů jako exponáty (TQ-13) + jednotné karty citací (TQ-14) | celý střed | Faceless formát ukáže lidi a důkazy bez cizích záběrů; vypravěč nemusí soudit. | O0219, O0221, O0177, O0292, O0366, O0047 |
| 4 | Postup jako očíslované kroky (TQ-08) + jeden mechanismus peněz (TQ-09) | střed | Slib → prodej → financování → improvizace → pád. Jedno jednoduché schéma toků peněz. | O0116, O0102, O0203, O0430, O0271 |
| 5 | Vyrobený sociální důkaz (TQ-17) | kapitola o kampani | Jádro kauzy a pro diváka nejpoužitelnější poučení. Generický „feed“ bez skutečných účtů. | O0313, O0314, O0453 |
| 6 | Mapa Exumy a areálu před dnem D (TQ-19) | před příjezdem hostů | Chaos dne pak dává prostorový smysl. Vlastní mapa z otevřených dat. | O0361, O0289, O0290 |
| 7 | Odpočet dnů a datové karty (TQ-03) | přípravy | Ukáže, jak málo času zbývalo; přirozeně se pojí se srovnáním s běžným festivalem (TQ-10). | O0205, O0363, O0378 |
| 8 | Rozpor čísel a kontrola mýtů (TQ-16) + vyslovená nejistota (TQ-15) | jeden krátký segment | Fyre je plný přehnaných čísel; jejich oprava je obsah a buduje důvěru. | O0207, O0275, O0455, O0334, O0105 |
| 9 | Co se ztratí: místní lidé a firmy (TQ-11) | před pádem a v závěru | Méně omletá linka; dopad na Exumu. | O0155, O0257 |
| 10 | Závěr: teze + „co bylo potom“ (TQ-12) | posledních 2–3 min | Naše hlavní odlišení: soud, další podvod, propuštění, pokračování (vše s datem a zdrojem). | O0106, O0107, O0163, O0422 |

Obraz a zvuk (vše vlastní výroba):
- **Paleta**: 2–3 vlastní barvy pro všechny zdroje (TQ-21; O0023, O0280, O0352), ne červeno-černá, která je obsazená.
- **Grafy** s jednoslovným českým titulkem (TQ-22; O0414, O0418).
- **Rekonstruované obrazovky** (TQ-23; O0317) a 2–3 jednoduché 3D modely (stan, letadlo, hromada peněz proti známému objektu; TQ-20; O0197, O0201).
- **Tempo**: háček 15–25 změn obrazu za minutu, střed 6–12 (TQ-27; O0005, O0113, O0409, O0264). Měřit stejným nástrojem.
- **Hudba** nízko podle `knowledge/09` (15–20 dB pod hlasem; náš orientační údaj −24 dB je relativní měření v prohlížeči, ne cíl mixu) (TQ-26; O0423, O0165, O0012); 2–4 tiché pauzy 3–8 s na zlomových místech (TQ-24; O0301, O0166); ruchy místo hudby v noci ve stanech (TQ-25; O0344).

## Návrh A/B testu (jen tam, kde to jde levně)
- **Háček A**: datovaný studený začátek (příjezd hostů) → **Háček B**: montáž slibů a tvrdý střih na realitu. Měřit
  udržení po 30 s a 60 s.
- **Náhled**: typografický náhled bez obličeje s jedním doloženým číslem vs. ilustrace stanů bez textu. Číslo v náhledu
  a názvu musí zaznít ve videu se zdrojem (O0373, O0110 ukazují opak).
- **Role diváka** (TQ-28; O0083, O0392, O0342): „jsi host, který přistál na Exumě“ jen jako zřetelně označená
  rekonstrukce podle doložených výpovědí. Testovat až ve druhé verzi.

## Co nedělat (TQ-29)
- Žádné cizí záběry, zpravodajské klipy, záběry hostů, filmové scény ani hlas (O0024, O0062, O0410, O0425, O0460).
  To se týká i dokumentů Netflix a Hulu o Fyre.
- Žádná čísla v názvu nebo náhledu, která video nedoloží (O0373, O0110).
- Žádné fámy o místních (O0449), žádné hodnotící nálepky o lidech mimo citace (O0227).
- Rekonstrukce vždy označit (O0184); žádné anachronické ilustrační záběry (O0386).
- Nekopírovat identitu žádného kanálu (paleta, typ písma karet, struktura úvodu jako celek).

## Tvrzení ze srovnávacího videa: jen stopy, ne fakta
Následující tvrzení se objevila v srovnávacím videu a **nesmí se použít bez ověření** z primárních zdrojů
(obžaloba a rozsudek SDNY, žaloba a dohoda SEC, dobové zpravodajství s datem):
1. Počty hostů a vstupenek (řádově tisíce prodaných vs. stovky přítomných).
2. Ceny vstupenek a balíčků a tvrzení, že žádný balíček za 250 000 USD nebyl prokazatelně prodán (O0455).
3. Délka příprav („dva týdny“ apod.).
4. Že ostrov z kampaně nebyl místem konání a souvislost s Norman's Cay a Escobarem (O0446).
5. Vysvětlení zakladatele, že přípravy zničila bouře (O0452).
6. Fámy o přepadeních a psech (O0449): nepoužívat vůbec, pokud je nedoloží seriózní zdroj.

## Jak to navazuje na pipeline
- Scénář: u každé kapitoly pole „otevřená otázka na konci“ (TQ-04), značky [jisté]/[pravděpodobné]/[nejasné] (TQ-15)
  a [PAUZA] (TQ-24).
- Review: kontrolní seznam TQ-29 jako povinný krok před vydáním.
- Měření hotového střihu: `tools/run_watch.js` na náhledu (střihy za minutu, hudební podložka) a porovnání s tabulkou výše.
