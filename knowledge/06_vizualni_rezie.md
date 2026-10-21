# 06 Vizuální režie (storyboard, typy záběrů, mapy)

**Kdy číst:** fáze 4 (shotlist) spolu s `12_vizualni_reserse_a_prava.md` (co hledat dřív, než něco vyrobíš).

## Pořadí volby obrazu pro každou scénu
1. Autentický materiál (viz `12`, pořadí 1–5) s jasnou funkcí.
2. Doklad v obraze: výřez dokumentu/článku (`source_card`), citace (`quote_card`), číslo se zdrojem (`number_callout`).
3. Mapa nebo časová osa, když jde o místo, přesun nebo pořadí událostí.
4. Vlastní 3D, když vysvětluje něco, co fotka neukáže (`07_blender_3d.md`).
5. Kinetická typografie (`kinetic`) jen na pointu nebo přechod, ne jako výplň.

## Gramatika záběrů (šablony pipeline)
| Šablona | Na co | Max délka | Poznámka |
|---|---|---|---|
| `photo_kenburns` | skutečná fotka místa/osoby | 4 s | pohyb k detailu, který vypravěč zmiňuje; `fit: contain` u screenshotů |
| `clip` | autentický klip s právy | podle účelu (`max_range`) | zastavení + anotace u klíčového detailu |
| `source_card` | doklad (článek, spis) | 3 s | zvýrazni přesně citovanou frázi; `fx: panel3d` |
| `quote_card` | citace osoby | 3 s + čtení | originál + překlad |
| `number_callout` | klíčové číslo | 2,5 s | zdroj v řádku „Zdroj:“ |
| `map` / `motion` (mapa) | místo, přesun | 4 s | viz mapy níže |
| `timeline` | pořadí událostí | 4 s | max 5 položek na obrazovce |
| `motion` (3D) | vlastní 3D vysvětlení | 4 s | `render/fx/*.mp4` |
| `kinetic` | pointa, otázka | 1,5 s | 1 zvýrazněné slovo |
| `title_card` | předěl kapitol | 2 s | max 3× za video |

## Pravidla
- **Jedna myšlenka na záběr.** Obraz ukazuje to, o čem hlas mluví **ve stejnou chvíli** (střih na slovo).
- **Neopakuj totéž v hlase, titulku i obraze** (zadání Miry). Obraz má přidat: detail, důkaz, srovnání.
- Variabilita: stejná šablona max 2× za sebou (`craft_check.py`). Typy obrazu se střídají.
- Podíl: [Cíl kanálu] ≥ 50 % záběrů skutečný obraz nebo doklad (fotky, klipy, dokumenty, mapy); kinetic + title ≤ 25 %.
- Vizuální kontrast slib × realita je hlavní nástroj dokumentu o selhání: split screen, stejná kompozice, tvrdý střih.
- Čitelnost: text ≥ 48 px při 1080p, na obrazovce ≥ 0,4 s na slovo. Nic důležitého do spodních 15 % (titulky, UI).
- Soukromé prvky na screenshotech (avatar, sidebar, e-maily) vždy ořízni nebo rozmaž.
- Jednotná identita: paleta `brand.json`, písmo, zrno, viněta. Cizí materiál barevně sjednoť jen tak, aby se
  neměnil význam (žádné „vylepšování“ důkazu).

## Mapy (zadání Miry § 9)
- Mapa odpovídá na otázku: odkud kam? kde je klíčové místo? co se změnilo v čase? čeho si má divák všimnout?
- Geograficky správně; data Natural Earth (`/mnt/project-files/youtube/env/geo/`, public domain) – atribuce v `credits.txt`
  není nutná, ale zapiš zdroj do `assets.jsonl`.
- Max 3 popisky naráz. Kamera jen tam, kde pohyb pomáhá pochopení (přesun Norman's Cay → Great Exuma). Žádné
  dekorativní trasy a zoomy.
- Měřítko nebo známý orientační bod (Miami) pro české publikum.

## Storyboard (část vizuálního plánu)
Pro každou scénu: `purpose` (proč existuje) · co je v obraze · střih (na které slovo) · grafický zásah · zvuk.
Kontrola: přečti jen sloupec „co je v obraze“ – dává smysl i bez zvuku? Má každá klíčová scéna skutečný doklad?
