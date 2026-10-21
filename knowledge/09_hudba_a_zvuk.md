# 09 Hudba a zvuk (PRIORITNÍ MODUL, závazný)

Zdroj: zadání Miry „Prioritní modul: profesionální hudba od lidských skladatelů“ (21. 10. 2026) + měření v pipeline.
**Kdy:** fáze 4 (hudební dramaturgie ve shotlistu, blok `music`), fáze 5 (mix), před exportem (kontrola níže).
Strojově: `craft_check.py` (hudba a SFX), `vid.py qa` (LUFS, true peak).

## 1. Základní pravidlo
- Jen **skutečná, kvalitně produkovaná hudba od lidských skladatelů a hudebníků**. Instrumentální, filmová, autentické nahrávky.
- **Žádná AI hudba.** Žádné AI generované zvuky. (Ruší dřívější návrh ACE-Step a MOSS-SoundEffect v
  `pruzkum_github_hlas_hudba_blender.md`.)
- Žádné umělé efekty a laciné generické podklady jako automatická náhrada sound designu. Syntetizované efekty
  z `pipeline/lib/sfx.py` (whoosh, hit, impact, riser) jsou **nouzové**: jen když není vhodná skutečná nahrávka,
  střídmě a nikdy na každou animaci. `craft_check.py` je hlásí.
- Soundtrack má znít jako kvalitní dokument, ne jako podkres automaticky vytvořeného videa.

## 2. Zdroje (pořadí hledání)
| # | Zdroj | Poznámka k licenci |
|---|---|---|
| 0 | vlastní licencovaná knihovna uživatele | prohledat první, pokud existuje |
| 1 | **YouTube Audio Library** (studio.youtube.com) | první volba pro YouTube; stahuje **Mira** (vyžaduje přihlášení). Zapiš typ licence (bez atribuce / s atribucí). |
| 2 | **Incompetech** (Kevin MacLeod) | CC BY 4.0, atribuce povinná v popisu; monetizace povolena (snímek FAQ v `assets/licenses/`). ISRC do `assets.jsonl` pro spor v Content ID. |
| 3 | **Mixkit** | Mixkit licence – ověř u konkrétní skladby a ulož snímek licence. |
| 4 | **Pixabay Music** | archivuj licenční údaje a stránku skladby; někteří autoři registrují Content ID → zapiš, kdo je autor a postup při nároku. Ne jako automatická volba. |
| 5 | **Uppbeat** | jen bezplatný tarif a jeho limity (počet stažení / měsíc); atribuce dle podmínek; žádné placené kredity. |
| 6 | **Freesound** | **jen** jednotlivé autentické ruchy, atmosféry, terénní nahrávky. Licence se liší po souborech (CC0, CC BY, CC BY-NC = **nepoužít** při monetizaci). |
Neomezuj se na jednu knihovnu, když nenajdeš vhodnou skladbu.

## 3. Hudební dramaturgie (podle příběhu, ne dostupnosti)
Ve shotlistu mapuj `music.cues` na dějství. Pro dokument o selhání:
| Úsek (`act`) | Funkce hudby |
|---|---|
| cold open (`hook`) | výrazný, atmosférický začátek, který vyvolá otázku |
| budování očekávání (`setup`) | elegantní, optimistická nebo ambiciózní |
| první varovné signály (`rise`) | jemné napětí, minimalistické pulzy, temnější harmonie |
| odhalení problému (`turn`) | postupná gradace, výrazné přechody, promyšlené **ticho** |
| finanční a organizační chaos | rytmické, nervózní nebo strohé motivy, ne automatické komediální efekty |
| ironické momenty | suchý, decentní kontrast, nepřebíjí vyprávění |
| vyvrcholení | nejsilnější vhodná skladba nebo práce s tichem |
| následky a závěr (`consequence`, `payoff`) | emocionálně přesný, civilní, zapamatovatelný motiv |
**Ne pod každou scénou.** Ticho a autentický ruch mají často větší účinek. `craft_check.py` hlásí, když hudba hraje
> 90 % délky bez jediného `silence` cue.

## 4. Výběr a technika
- Kandidátní skladby **poslechni** (u nás: změř a prohlédni spektrogram/obálku, poslech dělá člověk) – ne podle názvu a tagů.
- Kritéria: tempo (BPM vs. tempo střihu), dynamika, harmonie, instrumentace, emoční funkce, čistota nahrávky,
  delší úseky, vhodný začátek a konec, případně samostatné stopy.
- Hudbu upravuj podle střihu, ne naopak: nástup na střih nebo slovo, konec frázi, ne uprostřed taktu.
- Pod voiceoverem výrazně ztiš a automatizuj (ducking): hudba **15–20 dB pod hlasem** [Praxe; u nás `level_under_voice_db` −21,
  v mezerách −13]. Řeč musí zůstat srozumitelná na mobilu.
- Přechody: střih, prolínačka, změna hlasitosti, přirozený dozvuk. Ne mechanicky.
- Žádné nadměrné whooshe, bass dropy a údery na každé animaci. [Hypotéza] max 1 akcent na 10 s, a jen na skutečný beat.
- Master: −14 LUFS integrovaně, true peak ≤ −1 dBTP [Praxe; YouTube hlasitější zeslabí]. Kontrola `vid.py qa`.

## 5. Autentické zvuky místo umělých efektů
Když scéna potřebuje zvuk: skutečné nahrávky (vítr, moře, dav, déšť, kroky, stroje, letiště, ruch). Jen s licencí
odpovídající použití. U rekonstrukce historické události **nikdy nevydávej ilustrační zvuk za dobový záznam** – žádné
falešné důkazy; když by divák mohl být zmaten, označ „rekonstrukce“ / „ilustrační zvuk“.

## 6. Licence a ochrana kanálu
„No copyright“ ≠ bez autorských práv. Každá skladba i ruch musí mít ověřené oprávnění pro video **a monetizaci**.
Do `assets.jsonl` (kind `music` / `sfx`) zapiš: název a autor · původní URL · datum stažení · typ licence a podmínky
(`usage_limits`) · přesné znění atribuce (`attribution`) · uložený důkaz licence (`assets/licenses/…`) · známé omezení
Content ID a postup při nároku (ISRC, kontakt na autora, licence). Nejasná licence = nepoužít.
Nikdy neobcházej Content ID. Atribuce sama právo nedává.

## 7. Rozpočet
Neplať za hudbu, předplatné ani kredity. Limit, paywall nebo nejasná licence → zastav jen tento krok, napiš
překážku, pokračuj ve zbytku. Když nic legálního nesedí: další zdroj, nebo střih postavený na ruchu a tichu.

## 8. Kontrola před exportem (zapiš do `review/hudba_v<verze>.md`)
- [ ] hudba podporuje dramaturgii, nezní genericky (každý cue má funkci z tabulky § 3)
- [ ] nezahlcuje hlas (měření hudba vs. hlas po sekundách: −16 až −20 dB pod řečí; poslech na telefonu)
- [ ] přechody nejsou mechanické
- [ ] žádná neověřená skladba ani zvuk; žádná AI hudba / AI zvuk
- [ ] atribuce připravené v `publish/<lang>/credits.txt`, licenční důkazy uložené
- [ ] syntetické SFX jen výjimečně a s důvodem
