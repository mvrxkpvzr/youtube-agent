# Katalog přenositelných technik (TQ)

Každá technika je obecný postup, ne kopie konkrétního kanálu. Uvádí se jen s doložením z `observations.jsonl`
(nejméně dva kanály, pokud není řečeno jinak). „Doloženo“ = pozorování (fakt z videa), „Proč funguje“ = naše
interpretace. Odkaz s časem vrátí `python3 search.py --technique TQ-nn` nebo `python3 search.py O0148`.
Vlákno Znalosti tyto ID cituje jako [Praxe]. Stav k 2026-10-22: 26 videí, 15 kanálů + 1 srovnávací (Internet Historian).

Formát:

```
### TQ-nn Název
- Co: jedna věta.
- Doloženo: O0001 (kanál, čas), O0002 (...)
- Proč funguje (interpretace): ...
- Jak u nás (návrh pro pipeline): ...
- Riziko / kdy nepoužít: ...
```

## Příběh a struktura

### TQ-01 Známý konec, otázka „jak“
- Co: konec příběhu se řekne v prvních vteřinách a hlavní otázka se přesune z „co se stalo“ na „jak to bylo možné“.
- Doloženo: O0001 (ColdFusion, 0:00), O0002 (ColdFusion, 0:23), O0376 (Fascinating Horror, 0:11), O0358 (Fascinating Horror, 0:07), O0003 (ColdFusion, interpretace)
- Proč funguje (interpretace): u známé kauzy divák konec stejně zná; zvědavost drží mechanismus a lidé, ne překvapení.
- Jak u nás (návrh pro pipeline): v prvních 30 s říct výsledek Fyre (hosté na Exumě bez ubytování, trestní stíhání) a vyslovit otázku „jak se to mohlo stát“.
- Riziko / kdy nepoužít: u málo známého tématu, kde je překvapení hlavní hodnota.

### TQ-02 Datovaný studený začátek s návratem na konci
- Co: film začne konkrétním okamžikem s datem a časem (in medias res) a v závěru se k němu vrátí, teď už s kontextem.
- Doloženo: O0148 (Wendover, 1:01), O0161 (Wendover, 19:49), O0234 (Real Engineering, 0:04), O0358 (Fascinating Horror, 0:07), O0376 (Fascinating Horror, 0:11)
- Proč funguje (interpretace): přesný čas dává věrohodnost a napětí; návrat na konci uzavře oblouk a odmění pozornost.
- Jak u nás (návrh pro pipeline): otevřít ránem 27. 4. 2017 (příjezd prvních hostů) s ověřeným časem; stejnou scénu zopakovat v závěru.
- Riziko / kdy nepoužít: časy a data jen z primárních zdrojů; nevymýšlet hodiny, které nejsou doložené.

### TQ-03 Jednotné datové karty
- Co: přechody mezi obdobími nese stejně vypadající karta s datem (případně počitadlo dnů).
- Doloženo: O0363 (Fascinating Horror, 3:51), O0388 (Fascinating Horror, 0:13), O0320 (Barely Sociable, 35:54), O0205 (neo, 13:00), O0004 (ColdFusion, 1:20)
- Proč funguje (interpretace): divák se v časové ose neztratí a karta funguje jako nádech před dalším dějstvím.
- Jak u nás (návrh pro pipeline): vlastní šablona datové karty v naší paletě; odpočet „dní do festivalu“ v části příprav.
- Riziko / kdy nepoužít: nepřehánět počet karet; u krátkých úseků stačí titulek v rohu.

### TQ-04 Řetěz otázek mezi kapitolami
- Co: každá část končí výslovnou nezodpovězenou otázkou, kterou otevře další část.
- Doloženo: O0237 (Real Engineering, 3:23), O0030 (MagnatesMedia, 15:00), O0058 (MagnatesMedia, 10:16), O0346 (Nexpo, 2:36)
- Proč funguje (interpretace): drží retenci přes kapitolové předěly, kde diváci nejčastěji odcházejí.
- Jak u nás (návrh pro pipeline): ve scénáři ke každé kapitole pole „otevřená otázka na konci“; kontrola v review scénáře.
- Riziko / kdy nepoužít: falešné cliffhangery, které další část nezodpoví.

### TQ-05 Pojmenovaný bod zlomu
- Co: vypravěč výslovně řekne „tady se to láme“ (od klamání investorů k ohrožení lidí, od plánu ke lži).
- Doloženo: O0006 (ColdFusion, 4:25), O0029 (MagnatesMedia, 9:50), O0138 (Wendover, 13:10), O0179 (neo, 12:43)
- Proč funguje (interpretace): divák ví, kde v oblouku je, a zlom dostane váhu.
- Jak u nás (návrh pro pipeline): u Fyre dva zlomy: kdy plán přestal být splnitelný a kdy pokračoval prodej s vědomím, že nebude splněn (podle soudních dokumentů).
- Riziko / kdy nepoužít: zlom musí být doložený, ne dramaturgicky domyšlený.

### TQ-06 Řetěz stop a příčinná rekapitulace
- Co: vyšetřování vede přes pojmenované stopy a končí jedním odstavcem s celou příčinnou řadou.
- Doloženo: O0238 (Real Engineering, 4:27), O0245 (Real Engineering, 12:56), O0330 (Barely Sociable, 1:35), O0400 (Half as Interesting, 4:42), O0088 (Company Man, 6:00)
- Proč funguje (interpretace): divák si pocitově „vyřeší“ případ sám a závěrečná rekapitulace upevní pochopení.
- Jak u nás (návrh pro pipeline): stopy = dokumenty (žaloba SEC, obžaloba SDNY, e-maily citované v nich); na konci 30–45 s rekapitulace příčin.
- Riziko / kdy nepoužít: zjednodušení na jedinou příčinu, pokud zdroje ukazují více.

### TQ-07 Komplikace, která vyloučí snadnou odpověď
- Co: před závěrem se ukáže fakt, který nejjednodušší vysvětlení vyvrací.
- Doloženo: O0242 (Real Engineering, 7:21), O0399 (Half as Interesting, 4:11), O0275 (PolyMatter, 12:33)
- Proč funguje (interpretace): zvyšuje důvěryhodnost a prodlužuje napětí.
- Jak u nás (návrh pro pipeline): u Fyre ověřit populární tvrzení („jen počasí“, „jen influenceři“) proti dokumentům a jedno vyvrátit nebo zpřesnit.
- Riziko / kdy nepoužít: jen když komplikace skutečně existuje ve zdrojích.

### TQ-08 Postup podvodu jako očíslované kroky nebo plány
- Co: mechanismus se rozloží na pojmenované kroky („krok 1, 2, 3“, „plán A, B, C“) s počitadlem na obrazovce.
- Doloženo: O0116 (Fern, 7:20), O0102 (Fern, 6:49), O0056 (MagnatesMedia, 7:00), O0203 (neo, 9:19), O0086 (Company Man, 3:48), O0274 (PolyMatter, 9:12)
- Proč funguje (interpretace): složitý podvod je srozumitelný a divák vidí, kde v procesu je.
- Jak u nás (návrh pro pipeline): Fyre jako kroky: slib (kampaň) → prodej → financování (investoři, půjčky) → improvizace (plány B, C) → zhroucení.
- Riziko / kdy nepoužít: kroky nesmí znít jako návod k podvodu; popisovat, ne radit.

### TQ-09 Jeden mechanismus jako motor celé kauzy
- Co: celá bublina se vysvětlí jedním jednoduchým mechanismem, ideálně nejprve na smyšleném zjednodušeném modelu.
- Doloženo: O0430 (Business Casual, 4:35), O0271 (PolyMatter, 2:14), O0088 (Company Man, 6:00)
- Proč funguje (interpretace): divák si odnese jeden pochopený princip místo deseti čísel.
- Jak u nás (návrh pro pipeline): u Fyre mechanismus „peníze z nových prodejů a půjček kryjí staré sliby“ na jednoduchém schématu toků peněz.
- Riziko / kdy nepoužít: mechanismus musí být podložen dokumenty, jinak jen „ASSUMPTION“.

### TQ-10 Srovnání s úspěšným protějškem
- Co: kauza se poměří s podobným projektem, který se povedl, nebo s dřívějšími případy.
- Doloženo: O0378 (Fascinating Horror, 0:43), O0413 (Modern MBA, 2:06), O0180 (neo, 15:05)
- Proč funguje (interpretace): kontrast ukáže, co přesně chybělo (čas, infrastruktura), bez moralizování.
- Jak u nás (návrh pro pipeline): kolik měsíců a jaké zázemí potřebuje běžný festival dané velikosti vs. Fyre (zdroj: oborové údaje, ne odhad).
- Riziko / kdy nepoužít: srovnávat jen doložená čísla.

### TQ-11 Co se ztratí: krátký portrét před pádem
- Co: před krizí krátký montážní odstavec ukáže svět, o který se přijde (místo, lidé, sliby).
- Doloženo: O0155 (Wendover, 6:00), O0257 (PolyMatter, 1:36), O0367 (Fascinating Horror, 9:25)
- Proč funguje (interpretace): pád bolí, jen když divák viděl, co bylo v sázce.
- Jak u nás (návrh pro pipeline): u Fyre portrét Exumy a místních lidí a firem, které na akci pracovaly (dopad na ně je silná a méně omletá linka).
- Riziko / kdy nepoužít: neidealizovat; žádné klišé o „ráji“ bez faktů.

### TQ-12 Ukončení tezí a stavem „co bylo potom“
- Co: závěr přinese obecnou tezi a seznam dalšího osudu všech aktérů, včetně nevyřešeného.
- Doloženo: O0014 (ColdFusion, 21:10), O0106 (Fern, 16:00), O0107 (Fern, 18:06), O0163 (Wendover, 21:44), O0422 (Modern MBA, 29:03), O0385 (Fascinating Horror, 9:23)
- Proč funguje (interpretace): divák odchází s myšlenkou, ne jen s příběhem; „co bylo potom“ je přesně to, co starší videa nemají.
- Jak u nás (návrh pro pipeline): Fyre po roce 2017: rozsudek, další podvod z vazby, propuštění, „Fyre 2“ (vše ověřit ze zdrojů s datem).
- Riziko / kdy nepoužít: teze nesmí být kázání; jedna věta, opřená o fakta z videa.

## Důkazy a poctivost

### TQ-13 Vlastní slova a dokumenty aktérů jako exponáty
- Co: hlavním důkazem jsou dokumenty, příspěvky a výroky samotných aktérů, ukázané jako exponát (papír, zvýrazňovač).
- Doloženo: O0219 (Real Engineering, 3:16), O0221 (Real Engineering, 3:16), O0177 (neo, 11:19), O0018 (ColdFusion, 19:10), O0019 (MagnatesMedia, 0:00), O0452 (Internet Historian, 5:30)
- Proč funguje (interpretace): divák vidí důkaz sám; vypravěč nemusí hodnotit.
- Jak u nás (návrh pro pipeline): vlastní grafika „dokument na stole“ s krátkou citací (do 15 slov) ze soudních spisů a veřejných prohlášení; zdroj vždy na obrazovce.
- Riziko / kdy nepoužít: nepřebírat cizí záznamy ani hlas; citace krátké, s uvedením zdroje.

### TQ-14 Jednotné karty svědectví a citací
- Co: citace a svědectví mají jednu stálou podobu (karta s textem, jménem, zdrojem), často místo videa.
- Doloženo: O0292 (LEMMiNO, 7:30), O0366 (Fascinating Horror, 7:50), O0151 (Wendover, 1:26), O0047 (ColdFusion, 15:40)
- Proč funguje (interpretace): faceless kanál tak ukáže lidi bez cizích záběrů a citace působí jako důkaz.
- Jak u nás (návrh pro pipeline): šablona karty svědectví v naší paletě; text přečte náš hlas s označením „citace“.
- Riziko / kdy nepoužít: neupravovat citace; neuvádět jména soukromých osob bez veřejného zdroje.

### TQ-15 Vyslovená nejistota a jistota
- Co: vypravěč řekne, co se neví, odhadne pravděpodobnost a uvede alternativní vysvětlení.
- Doloženo: O0334 (Barely Sociable, 13:10), O0298 (LEMMiNO, 94:00), O0434 (Business Casual, 8:01), O0105 (Fern, 7:29), O0054 (MagnatesMedia, 0:59)
- Proč funguje (interpretace): buduje důvěru a odliší seriózní kanál od senzace.
- Jak u nás (návrh pro pipeline): ve scénáři značky [jisté]/[pravděpodobné]/[nejasné] a odpovídající formulace v textu.
- Riziko / kdy nepoužít: nezahltit video výhradami; jen tam, kde nejistota mění význam.

### TQ-16 Rozpor čísel a kontrola mýtů
- Co: oficiální a nezávislé číslo zazní vedle sebe se zdrojem, rozšířené tvrzení se ověří.
- Doloženo: O0207 (neo, 18:52), O0275 (PolyMatter, 12:33), O0455 (Internet Historian, 8:20), O0172 (neo, 4:13)
- Proč funguje (interpretace): Fyre je obklopený přehnanými čísly; jejich oprava je sama o sobě obsah.
- Jak u nás (návrh pro pipeline): segment „co se o Fyre říká vs. co říkají dokumenty“ (ceny vstupenek, počty hostů, výše škod).
- Riziko / kdy nepoužít: neopravovat jiné tvůrce jménem; opravovat tvrzení, ne lidi.

### TQ-17 Vyrobený sociální důkaz jako téma
- Co: video ukáže, jak byl zájem a důvěra uměle vyroben (placené příspěvky, nové účty, recenze).
- Doloženo: O0313 (Barely Sociable, 3:13), O0314 (Barely Sociable, 8:17), O0453 (Internet Historian, 6:42)
- Proč funguje (interpretace): u Fyre je to jádro kauzy (oranžový čtverec, influenceři) a divák pozná mechanismus i ve svém feedu.
- Jak u nás (návrh pro pipeline): vlastní animace „feedu“ s generickými účty (žádné skutečné profily ani loga), čísla dosahu ze zdrojů.
- Riziko / kdy nepoužít: neukazovat skutečné účty soukromých lidí; neobviňovat konkrétní influencery nad rámec zdrojů.

### TQ-18 Slib vs. realita
- Co: rychlá montáž slibů z kampaně a pak tvrdý střih na skutečnost.
- Doloženo: O0444 (Internet Historian, 1:02), O0446 (Internet Historian, 1:33), O0019 (MagnatesMedia, 0:00), O0376 (Fascinating Horror, 0:11)
- Proč funguje (interpretace): kontrast je u Fyre přirozený vrchol a dá se říct bez komentáře.
- Jak u nás (návrh pro pipeline): sliby jako vlastní typografická montáž (text slibu, zdroj, datum), realita jako vlastní ilustrace nebo licencovaný materiál; žádné převzaté záběry.
- Riziko / kdy nepoužít: srovnávací kanál (Internet Historian) to dělá komicky; u nás vážně a s doklady.

## Obraz

### TQ-19 Mapa a plán místa před dnem D
- Co: před vyprávěním dne se vysvětlí prostor (mapa, model, šipky toků) a pak se k němu opakovaně vrací.
- Doloženo: O0361 (Fascinating Horror, 1:56), O0289 (LEMMiNO, 0:00), O0290 (LEMMiNO, 5:00), O0141 (Wendover, 0:00)
- Proč funguje (interpretace): divák pak chaos chápe prostorově (kde byly stany, letiště, kde lidé čekali).
- Jak u nás (návrh pro pipeline): vlastní mapa Exumy a areálu z veřejných geodat (OpenStreetMap, s licencí), bílý model areálu.
- Riziko / kdy nepoužít: rozložení areálu jen z ověřených zdrojů; jinak označit jako přibližné.

### TQ-20 Čistý 3D „laboratorní“ prostor a měřítko
- Co: věci a čísla se ukazují v neutrálním 3D prostoru jako jednoduché modely; velké číslo se převede na fyzický objem.
- Doloženo: O0201 (neo, 6:28), O0197 (neo, 1:02), O0290 (LEMMiNO, 5:00), O0097 (Fern, 0:00)
- Proč funguje (interpretace): faceless kanál nepotřebuje záběry lidí; jednoduchý model je levný a jasný.
- Jak u nás (návrh pro pipeline): 3D modely stanu, letadla, kontejneru; ztráty investorů jako hromada bankovek proti známému objektu.
- Riziko / kdy nepoužít: výrobně náročné; omezit na 2–3 klíčová místa.

### TQ-21 Omezená paleta pro všechny zdroje
- Co: všechny obrazové zdroje (grafy, ilustrace, archiv) jsou sjednocené do 2–3 barev.
- Doloženo: O0023 (MagnatesMedia, 0:00), O0280 (PolyMatter, 2:14), O0352 (Nexpo, 0:00)
- Proč funguje (interpretace): smíšený materiál působí jako jeden film a kanál je rozpoznatelný.
- Jak u nás (návrh pro pipeline): vlastní paleta (ne červeno-černá, ta je obsazená); definovat v design tokenech pipeline.
- Riziko / kdy nepoužít: nekopírovat paletu konkrétního kanálu.

### TQ-22 Grafy s jednoslovným titulkem
- Co: každý graf má jeden údaj a jedno až dvě slova jako titulek.
- Doloženo: O0414 (Modern MBA, 3:07), O0418 (Modern MBA, 11:05), O0071 (Company Man, 2:46)
- Proč funguje (interpretace): graf se přečte za vteřinu i bez komentáře.
- Jak u nás (návrh pro pipeline): grafy tržeb vstupenek, dluhů, škod; titulek česky, jedno slovo.
- Riziko / kdy nepoužít: zjednodušující titulek nesmí zkreslit data.

### TQ-23 Vrstva obrazovkových materiálů
- Co: velká část obrazu jsou rekonstruované obrazovky (stránky, zprávy, dokumenty) pomalu posouvané.
- Doloženo: O0317 (Barely Sociable, 1:40), O0221 (Real Engineering, 3:16), O0097 (Fern, 0:00)
- Proč funguje (interpretace): internetová kauza se odehrává na obrazovkách; je to levné a autentické.
- Jak u nás (návrh pro pipeline): vlastní rekonstrukce rozhraní (generické, bez log), texty jen z doložených zdrojů.
- Riziko / kdy nepoužít: snímky obrazovky cizích lidí; napodobení skutečných značek.

## Zvuk a tempo

### TQ-24 Tiché pauzy bez vypravěče
- Co: na klíčových místech vypravěč na několik vteřin až desítek vteřin zmlkne a běží jen obraz a hudba či zvuk.
- Doloženo: O0301 (LEMMiNO, 0:00), O0166 (Wendover, 0:00), O0371 (Fascinating Horror, 0:00), O0108 (Fern, 0:00)
- Proč funguje (interpretace): dá divákovi čas pochopit závažnost; kontrast s jinak hustým textem.
- Jak u nás (návrh pro pipeline): 2–4 pauzy 3–8 s ve scénáři označené [PAUZA]; střih je respektuje.
- Riziko / kdy nepoužít: dlouhé pauzy v prvních 60 s, kde se rozhoduje o odchodu.

### TQ-25 Ruchy místo hudby ve scéně
- Co: rekonstruovaná scéna stojí na ruchu (vlny, kroky, vítr) místo hudby.
- Doloženo: O0344 (Nexpo, 0:47), O0189 (neo, 0:00)
- Proč funguje (interpretace): zvuk vtáhne do místa bez záběrů; hudba je tišší a o to účinnější.
- Jak u nás (návrh pro pipeline): příjezd na Exumu, noc ve stanech: vlastní nebo licencované ruchy (CC0).
- Riziko / kdy nepoužít: doloženo hlavně jedním kanálem (Nexpo), proto testovat.

### TQ-26 Tichá hudební podložka
- Co: hudba běží téměř stále, ale hluboko pod hlasem.
- Doloženo: O0423 (Modern MBA, −26 až −29 dB), O0165 (Wendover, −27 až −30 dB), O0076 (Company Man, −23,5 dB), O0012 (ColdFusion, −19,5 dB), O0438 (Business Casual, −17 až −18 dB)
- Proč funguje (interpretace): vážné vyšetřovací kanály drží hudbu níž; hlasitější podložka působí jako „business entertainment“.
- Jak u nás (návrh pro pipeline): držet podložku na tiché straně podle `knowledge/09`; hotový střih změřit stejnou metodou a porovnat se vzorkem (orientačně kolem −24 dB), u svědectví níž.
- Riziko / kdy nepoužít: −24 dB je relativní měření celkové hladiny v prohlížeči (ne LUFS, ne odstup od hlasu) a nelze ho srovnávat s cílem playbooku. Pro mix platí `knowledge/09` (hudba 15–20 dB pod hlasem; pipeline `level_under_voice_db` −21, v mezerách −13); toto číslo slouží jen ke srovnání kanálů mezi sebou.

### TQ-27 Rychlý háček, klidnější střed
- Co: první 1–2 minuty mají výrazně víc střihů než zbytek videa.
- Doloženo: O0113 (Fern, 36,5/min), O0409 (Modern MBA, 32,5/min), O0005 (ColdFusion, 25,5/min), O0459 (Internet Historian, 23/min), O0264 (PolyMatter, 11,5→4/min); protiklad O0303 (LEMMiNO, ~1/min), O0248 (Real Engineering, rovnoměrně 14,5/min)
- Proč funguje (interpretace): háček musí rychle ukázat šíři; střed pak potřebuje prostor na vysvětlení.
- Jak u nás (návrh pro pipeline): háček 15–25 změn/min, střed 6–12/min; měřit nástrojem `tools/run_watch.js` na našem střihu.
- Riziko / kdy nepoužít: rychlost bez obsahu; měření podhodnocuje plynulé 3D pohyby.

## Nepřenášet (etika)

### TQ-28 Hraní rolí a druhá osoba v úvodu — jen označeně
- Co: vypravěč staví diváka do role („jsi investor v roce 2004“, „probouzíš se“).
- Doloženo: O0083 (Company Man, 0:42), O0392 (Half as Interesting, 0:10), O0342 (Nexpo, 0:47)
- Proč funguje (interpretace): okamžitě vtáhne; u Fyre by „jsi host, který přistál na Exumě“ fungovalo silně.
- Jak u nás (návrh pro pipeline): testovat jen jako zřetelně označenou rekonstrukci podle doložených výpovědí.
- Riziko / kdy nepoužít: neoznačená dramatizace (O0184, neo) a smyšlené detaily; u tragédií nevhodné.

### TQ-29 Co nepřebírat
- Co: soupis praktik, které se ve vzorku objevily a které nepoužíváme.
- Doloženo: O0024 a O0062 (MagnatesMedia, záběry z filmů bez označení), O0425 (Business Casual, filmová postava), O0410 (Modern MBA, cizí klipy), O0460 (Internet Historian, cizí zpravodajské a hostovské záběry), O0373 (Fascinating Horror, číslo v názvu neodpovídá videu), O0110 (Fern, částka v názvu není ve videu), O0449 (Internet Historian, nepodložené fámy o místních), O0227 (Real Engineering, hodnotící nálepky), O0184 (neo, neoznačená rekonstrukce), O0386 (Fascinating Horror, anachronické stockové záběry)
- Proč funguje (interpretace): tyto praktiky zvyšují riziko nároků na autorská práva, ztráty důvěry a pomluvy.
- Jak u nás (návrh pro pipeline): kontrolní seznam v review: každé číslo v názvu a náhledu je ve videu se zdrojem; žádné cizí záběry; rekonstrukce označena; hodnocení jen citací.
- Riziko / kdy nepoužít: platí vždy.
