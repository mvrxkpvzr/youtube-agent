# 05 Humor a autorský český hlas

**Kdy číst:** fáze 4, **při psaní** scénáře (humor není vrstva přidaná na konec, zadání Miry).

## Kde humor smí být
- Suchý český humor, ironie, přesné formulace. Deadpan komentář k absurdní situaci.
- Kontrast velkolepého slibu a banální reality (luxusní vila × stan; „gurmánské jídlo“ × toast se sýrem).
- Krátké úderné poznámky za faktem. Vtipné vizuální analogie. Opakující se motiv, který se vyplatí (callback).
- Komediální střih, pauza a zvukový kontrast (ticho po velkém slibu, „scratch“, zmrazený obraz).

## Kde humor nesmí být
- **Na obětech**, lidech v nouzi a podvedených. Satira míří na absurdní rozhodnutí, ega, selhávající systémy,
  marketingové iluze a doložené rozpory.
- **Nikdy vymyšlená citace ani událost** kvůli pointě. Vtip je vždy názor nebo přirovnání, ne fakt.
  Ve scénáři označ `⟨humor⟩` (a `⟨názor⟩`), ať je ve fact sheetu vidět, že to není tvrzení.
- Ne v každé větě. Vážná místa (škody, soud, zdraví) nech vážná; kontrast vážnost × humor posílí obojí.
- Citlivá témata (sebevražda, nemoc, nezletilí) bez humoru.

## Techniky (s příklady z pilotu Fyre)
| Technika | Jak | Příklad |
|---|---|---|
| Pravidlo tří | dvě položky nastaví vzorec, třetí ho rozbije | „Luxusní vily. Gurmánská kuchyně. Toast se sýrem.“ |
| Understatement | mimořádné podat jako drobnost | „Sakra. To je hrozně málo.“ → „Investoři by s ním v tu chvíli nejspíš souhlasili.“ |
| Přirovnání do každodennosti | velké číslo / absurditu převést na běžnou zkušenost | „Jako napsat si omluvenku a podepsat ji za mámu. Jen o tři miliony dražší.“ |
| Callback | motiv z první půlky se vrátí v pointě | číslo 57 443 $ z hooku → „Bude v testu.“ → návrat na konci |
| Ironické pojmenování | přesné slovo místo dlouhého vysvětlení | „podvodník s vytrvalostí“ |
| Vizuální gag | obraz komentuje text | razítko „NEEXISTUJE“, ukazatel „Lžiměr“, zmrazený obraz + „Ano, opravdu.“ |
| Deadpan pauza | věta, 0,5 s ticha, střih na důkaz | „Hlavní kapela odřekla.“ (ticho) → fotka prázdného pódia |

## Hustota a rozložení
- [Hypotéza] 1 humorný beat na 45–90 s; v hooku max 1 (napětí má přednost); v `consequence` méně.
- `craft_check.py` počítá scény s `"beats": ["humor"]` a hlásí, když jich je < 1 na 2 min nebo víc než 1 na 20 s.
- Při každé revizi scénáře najdi **aspoň 3 konkrétní příležitosti** ke zlepšení humoru (zapiš do `review/`).
  Když se nehodí, nevynucuj je a napiš proč.

## Test vtipu
1. Je to pravda, nebo zjevně názor/přirovnání? 2. Míří to na moc a absurditu, ne na oběť? 3. Funguje to nahlas
TTS hlasem (krátké, bez vnořených vět)? 4. Ví divák, na co se to vztahuje (obraz ve stejné chvíli)?
Když je jedna odpověď ne, přepiš nebo škrtni.

## Hlas a TTS
- Ironie u syntetického hlasu nefunguje intonací. Musí fungovat **slovy a střihem**: krátká věta, pauza, obraz.
- Pointa je poslední slovo věty. Ne „byl to toast, a to se sýrem“, ale „dostali toast. Se sýrem.“
