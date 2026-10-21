# 12 Vizuální rešerše, autentické záběry a práva (PRIORITNÍ MODUL, závazný)

Zdroj: zadání Miry „Prioritní modul: internetové archivy, autentické záběry a dokumentární střih“ (21. 10. 2026).
**Kdy:** fáze 3 (spolu s faktickou rešerší) a znovu před renderem. Výstupy: `visual_sources.jsonl`,
`visual_plan.<lang>.json` → `visual_plan.<lang>.md` (`pipeline/visual_plan.py`), `assets.jsonl`.

## Hlavní princip
Jsi dokumentarista, ne generátor syntetických obrázků. Nejdřív hledáš skutečné události, původní materiály, archivní
záznamy, dobové fotky, rozhovory a veřejná vyjádření. Vlastní rekonstrukci (Blender, mapa, grafika) děláš teprve, když
skutečný materiál není, nedá se bezpečně použít, nebo příběh nevysvětlí. Veřejná dostupnost **není** licence.

## 1. Povinná vizuální rešerše (samostatná, vedle faktické)
Hledej: originální promo videa a reklamy · dobové TV reportáže · rozhovory s účastníky, organizátory, novináři, svědky ·
tiskové konference a veřejná vyjádření · původní příspěvky na sociálních sítích · archivní fotky z místa · zákulisí a
přípravy · dokumenty, prezentace, reklamní materiály · soudní spisy, časové osy, mapy, finanční podklady ·
materiál, který ukazuje rozdíl slib × skutečnost · záznamy vhodné pro kritiku, komentář, recenzi.
- Jazyky: čeština, angličtina a další, pokud přinesou zdroje (u Fyre: španělština pro Mexiko, Exuma = bahamská média).
- Kanály: vyhledávače, YouTube, Internet Archive / Wayback Machine, Wikimedia Commons, oficiální weby, soudy (PACER
  výtahy v médiích, justice.gov), zpravodajská média, sociální sítě, vládní archivy (US federální díla = často PD).
- Úspěch měř kvalitou, autenticitou, relevancí a rozmanitostí, ne počtem otevřených stránek.
- Když nestačí první hledání: jiná klíčová slova, původní autor, datum, alternativní kopie, původní publikace.
  Nespokoj se s první fotkou. U důležité scény ověř nedostatek **aspoň 3 různými postupy** a zapiš je (`searches` ve `visual_plan`).
- Nedostupné vyhledávání (blokovaný web, chybí prohlížeč): zjisti proč, zkus jiný nástroj, zapiš omezení.
  **Netvrď, že rešerše proběhla, když neproběhla.**

## 2. Pořadí autenticity (pole `authenticity_rank`)
1 původní záběr události / původní dokument · 2 dobový materiál přímého účastníka nebo původního vydavatele ·
3 důvěryhodná reportáž či rozhovor · 4 relevantní archivní foto nebo dokument · 5 licencovaný materiál z veřejného
archivu · 6 vlastní rekonstrukce (Blender, mapa, animace, grafika).
Pořadí není absolutní: dobře licencovaný archiv může být lepší než nekvalitní nebo zavádějící autentický záznam.
U důležitých událostí preferuj autentický materiál. **Žádné generické AI záběry** hotelu, pláže, letadla, davu,
když existují skutečné záběry místa nebo události. Když autentický materiál existuje, ale nejde použít, zapiš důvod.

## 3. Právní kategorie (pole `rights_category`) – nezaměňovat
| Kat. | Význam | Smí do videa? |
|---|---|---|
| **A** | výslovné povolení nebo získaná licence (doklad v `assets/licenses/`) | ano |
| **B** | licence povolující zamýšlené použití vč. komerčního (CC BY, CC BY-SA, CC0 …) při splnění podmínek | ano, s atribucí |
| **C** | volné dílo / bez majetkových práv, status **ověřen** (např. dílo federální vlády USA, uplynulá ochrana) | ano |
| **D** | konkrétní použití může spadat pod zákonnou výjimku (citace pro kritiku, recenzi, komentář; zpravodajská licence; parodie) | jen s vyplněným účelem, rozsahem a **lidským posouzením** |
| **E** | nejasný právní stav nebo významné riziko | **ne** – alternativa + `needs_human` |
| **F** | nelze použít za podmínek projektu | **ne** |

Právní rámec pro české a evropské publikum: český autorský zákon (zákonná citace § 31 AZ, zpravodajská licence § 34 AZ,
parodie / pastiš § 38g AZ), směrnice EU; pro DE § 51 / § 51a UrhG. Americký **fair use** jen jako doplňkový rámec tam,
kde se skutečně uplatní, ne jako univerzální oprávnění. Podrobnosti a checklist klipů: `pravni_ramec_klipy.md` (pokud
v projektu chybí, nejde použít kategorii D bez lidského posouzení).
- Neexistuje bezpečný počet sekund, procento ani počet fotek.
- Komentář, uvedení autora, vzdělávací účel ani nápis „fair use“ samy nic nelegalizují.
- Posuzuj: účel, vztah ke komentáři, nezbytný rozsah, význam převzaté části, kontext, licenční podmínky, rizika.
- Kritika konkrétní reklamy, tvrzení nebo mediální prezentace → zvaž použití **právě v nezbytném rozsahu**.
- Jen dekorace bez vztahu k výkladu → hledej licencovanou alternativu.
- **Nikdy:** odstranění loga, ořez, zrcadlení, změna rychlosti, filtry nebo barvy jako „odstranění“ práv.
  Žádné triky proti Content ID ani jiným ochranám.
- Nejasné → nepřikrášluj nejistotu, navrhni alternativu, `status: needs_human`, pokračuj na dalších scénách.
- YouTube videa nestahuj (podmínky YouTube). Analyzuj v přehrávači / přes přepis, klip získej od autora nebo z licence.

## 4. Dramaturgická funkce převzatého záběru (pole `function`, povinné)
`proves_claim` dokládá tvrzení · `original_promise` ukazuje původní slib/prohlášení · `contradiction` odhaluje rozpor
prezentace × realita · `testimony` přímé svědectví · `shows_event` divák vidí skutečnou událost · `context` dobový
kontext · `object_of_critique` předmět kritiky/analýzy · `irreplaceable_detail` výraz, reakce nebo detail, který
generická ilustrace nenahradí. Náhodné pozadí pod voiceoverem **není** funkce.
U každého navrženého klipu zapiš do `visual_sources.jsonl`: co divák uvidí (`what_it_shows`), co dokládá
(`evidentiary_value`, ID tvrzení), scény (`proposed_scenes`), zásah (`edit_notes`: zastavení, zvýraznění, popisek,
anotace), nezbytný rozsah (`max_range`), právní režim (`rights_category` + `rights_basis`), alternativu (`alternative`).
Co k záběru říká vypravěč, stojí ve `visual_plan.<lang>.json` (`voiceover`).
Dokument není kompilace cizích videí: těžiště je naše vyprávění, výzkum, komentář, analýza a střih.

## 5. Hlubší analýza obrazu
Kde je to technicky a právně možné, projdi materiál po snímcích nebo reprezentativních náhledech (kontaktní list
`ffmpeg … fps=1,tile=6x4` z legálně získané kopie nebo snímky z přehrávače). Hledej: detaily, které běžný divák
přehlédne · rozdíly reklama × skutečnost · texty, symboly, předměty, prostorové vztahy · změny v čase · důkazy pro mapu
nebo časovou osu · rozpory mezi zdroji · moment, který nejlépe ukazuje myšlenku scény. Zapiš do `edit_notes` / `what_it_shows`.
- Klíčový záběr ověř: kontext, datum, původ. Nepřisuzuj mu víc důkazní hodnoty, než má.
- Nestříhej nesouvisející záběry tak, aby vznikl falešný dojem kdy, kde nebo proč se něco stalo.
  Záběr jiného místa/času = popisek („ilustrační“, „Exuma, 2019“).

## 6. Získání a evidence
- Preferuj oficiální stažení, press kity, veřejné archivy, licenční knihovny, zdroje, které daný přístup výslovně
  povolují. Respektuj podmínky webů, soukromí, přihlášení a ochrany; nic neobcházej.
- Stačí-li analýza v přehrávači bez lokální kopie, nedělej kopii.
- Každý **použitý** soubor: původní URL, autor/vydavatel, název, datum, použitý časový rozsah, datum získání, licence
  nebo právní důvod, požadovaná atribuce → `assets.jsonl` (záznam ve `visual_sources.jsonl` nese `asset_id`).
- Stálé identifikátory: kandidát `V001…` (každý nalezený, i nepoužitý), použitý soubor `A001…`. Odvozené pracovní soubory nesou ID zdroje
  v názvu i v metadatech (`render/fx/A214_crop.mp4`). Žádná databáze jen podle názvů souborů.

## 7. Povinný vizuální plán (`python3 pipeline/visual_plan.py <projekt> --lang cs`)
Tabulka všech scén: ID · vypravěčský účel (`purpose`) · text voiceoveru · požadovaný typ vizuálu · nalezené autentické
materiály · ověřené odkazy · licence / předběžný právní režim · navržený rozsah · plánovaný střih a grafické zásahy ·
alternativa · stav (rešerše / ověření / produkce). Skript hlásí:
- **ERROR**: scéna používá materiál kat. E/F; kat. D bez účelu, rozsahu nebo lidského posouzení; použitý asset bez
  záznamu původu; realistická AI podoba skutečné osoby.
- **WARN**: klíčová scéna (hook, turn, payoff, scéna s tvrzením) bez jediného autentického kandidáta nebo bez zápisu
  rešerše; scéna bez `purpose`; vlastní rekonstrukce reálné události bez označení; podíl autentického materiálu nízký.
Důležitá scéna bez vhodného obrazu **není hotová**: pokračuj v rešerši nebo navrhni originální řešení.

## 8. Výchozí chování
Nevynechávej internetovou rešerši, protože je pomalejší než generování obrázku. Nevol automaticky nejbezpečnější
variantu, která výrazně sníží kvalitu: hledej řešení s maximem autenticity a vypravěčské hodnoty v mezích práv a
prostředků. Nejistý zdroj neblokuje projekt: hledej dál, ostatní scény pokračují.

## Cíl
Každý dokument má dost konkrétních, relevantních a ověřených vizuálních důkazů, aby nepůsobil jako generická prezentace
se syntetickými obrázky. Ne co nejvíc cizích materiálů, ale ty správné, s ukázaným významem, v novém originálním celku.
