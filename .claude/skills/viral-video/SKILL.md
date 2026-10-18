---
name: viral-video
description: Produkce virálního, fakticky podloženého českého (později německého) YouTube videa o influencerovi nebo internetové osobnosti – od výběru úhlu přes ověřené momenty s časy, scénář s hookem, hlas, grafiku a sestavení v ArtCraftu až po QA a balíček ke schválení. Spusť jako "/viral-video <osobnost nebo téma>" (např. "/viral-video Shane Stoffer"). Použij vždy, když uživatel chce video o konkrétní osobnosti, youtuberovi, influencerovi nebo kauze.
---

# Agent „viral-video“

Cíl: **jedno opravdu dobré video**, ne hromadná výroba. Viralita přes silný příběh a nejlepší momenty, ale **nic nepodávat jako fakt bez dokladu**. Publikace jen po lidském schválení faktů a práv.

Pracovní složka: `projects/<YYYY-MM>_<slug>/`. Nástroje jsou v `pipeline/` (viz `pipeline/README.md`). Python prostředí je trvale v `~/youtube-agent-env` (`pipeline/config.json` → `env_root`, obnova viz `pipeline/README_SETUP.md`). Spouštěj `$PY -I pipeline/...`, kde `PY=~/youtube-agent-env/venv/qwen/bin/python`.

## Kroky (každý končí souborem; po chybě navaž od posledního hotového)

### 1. Úhel a potenciál (→ `brief.md`) – BRÁNA G1
- Kanál otevři v Claude in Chrome: `youtube.com/@<handle>/videos`, řazení **Oblíbené** a **Nejstarší**. Zapiš odběratele, počet videí, top 10 videí (název, zhlédnutí, datum, délka, ID). ID čti regexem z `href` (celé URL s `?v=` nástroj blokuje).
- Najdi 3 úhly. U každého uveď: proč by na to někdo klikl, důkaz zájmu (zhlédnutí, komentáře, nedávné zprávy), dostupnost zdrojů, právní riziko, prostor pro **vlastní** komentář.
- **Vždy čti popisy videí.** Hledej „skit / props / for entertainment“. U TOGIho to změnilo celý úhel: skeč vs. skutečnost.
- Ukaž uživateli 3 úhly a doporuč jeden. Bez jeho volby nepokračuj.

### 2. Momenty s ověřenými časy (→ `moments.md`, `sources/*.transcript.txt`)
- U každého klíčového videa: `Zobrazit přepis` → spusť `snippets/yt_transcript.js` (javascript_tool) → `get_page_text` (čte celý text; výstup javascript_tool se ořezává). Nad 49 000 znaků nastav `window.__OFFSET` a čti po částech.
- Do `sources/Sxxx.transcript.txt` ukládej **jen použité řádky s časem**. Celé přepisy neukládej (autorská práva).
- U každého momentu: URL, čas od–do, citace max. 25 slov, typ (překvapení / konflikt / odhalení / emoce), **skeč nebo realita**, vhodnost pro inzerenty.
- TikTok a Instagram: bez přihlášení. Na Instagramu odmítni volitelné cookies a metriky čti z `meta[property=og:description]`. Reuploady od clip účtů jsou jen signál zájmu, **nikdy zdroj**.
- **Nevymýšlej** časy ani citace. Co jsi neviděl v přepisu nebo na stránce, neexistuje.

### 3. Fakta (→ `sources.jsonl`, `claims.jsonl`, `factsheet.md`) – BRÁNA G2
- Snapshot zdroje: `$PY -I pipeline/snapshot.py <projekt> S101 <url> --grep slovo1,slovo2`. Když web blokuje (Fast Company, USA Today, Bloomberg, Social Blade), najdi jiný zdroj.
- Stavy: `verified` = 2 nezávislé zdroje tier A/B nebo primární zdroj. `attributed` = jen jeho slova nebo jeden zdroj, ve scénáři pak **„podle jeho slov“**. `rejected` = redakčně vyřazeno.
- Citlivé (`high`): drogy, zdraví, hazard, nezletilí, sebepoškozování.
- `$PY -I pipeline/validate.py <projekt>` musí mít 0 chyb. Pak `python3 pipeline/factsheet.py <projekt>` a předlož fact sheet uživateli.

### 4. Scénář a střihový plán (→ `shotlist.cs.json`)
- **Hook do 8 s**: kontrast (tehdy × dnes), šok, rozpor. **Otevřená otázka do 25 s.** Každých 20–30 s nová informace nebo zvrat. Payoff odpovídá na otázku z hooku. Na konci háček na další díl.
- Tempo: cíl **150–170 slov/min**, záběry **2–3 s** (karta → číslo → klip → citace). Jedna myšlenka na záběr.
- Čísla a data vždy slovy v `narration_tts`, protože TTS je čte špatně.
- Anglické citace: originál na kartě + český překlad (`translation`). Anglické názvy ve voice-overu překládej, Piper je nevysloví.
- Šablony: `kinetic` (velká věta se zvýrazněným slovem), `number_callout`, `quote_card`, `source_card` (doklad: popis, titulek), `timeline`, `photo_kenburns` (`fit: contain` pro screenshoty), `clip_placeholder` (místo pro schválený klip: `ref` = zdroj a čas, `sub` = český titulek).
- 3 varianty názvu a 3 koncepty thumbnailu (bez falešného slibu) do `publish/cs/`.

### 5. Hlas, kontrola, titulky, render
```
$PY -I pipeline/vid.py voice   <projekt> --lang cs --engine piper_cs_fast
$PY -I pipeline/vid.py check   <projekt> --lang cs   # vynechaný text / chybná čísla = STOP
$PY -I pipeline/vid.py audio   <projekt> --lang cs
$PY -I pipeline/vid.py subs    <projekt> --lang cs
$PY -I pipeline/vid.py render  <projekt> --lang cs
$PY -I pipeline/vid.py qa      <projekt> --lang cs
```
- Výslovnost jmen: `pipeline/tools_lexicon_probe.py` se skutečnou větou ze scény (výsledek závisí na kontextu). Výsledek zapiš do `projects/<p>/lexicon.cs.json`.
- Vizuální kontrola: kontaktní list (`ffmpeg … fps=1/6,tile=5x5`) prohlédni sám. Hledej přetékání textu, překryvy, nečitelné karty a soukromé prvky ve screenshotech (vždy ořezat sidebar a avatar uživatele).

### 6. Klipy a pípání (po BRÁNĚ G4 – práva)
- Právní rámec: `pravni_ramec_klipy.md`. **„Dost vlastního obsahu“ není zákonné pravidlo.** V ČR a DE platí jen citace (§ 31 AZ / § 51 UrhG), zpravodajská licence (§ 34) a parodie nebo pastiš (§ 38g / § 51a). Každý klip projde checklistem z kap. 4, jinak se nepoužije.
- YouTube videa **nestahuj** (porušuje podmínky YouTube). Klipy získej legálně: svolení autora (nejlepší cesta – napsat jeho týmu) nebo licence. Do té doby zůstávají `clip_placeholder`.
- Schválený klip: `$PY -I pipeline/bleep.py klip.mp4 klip_bleep.mp4 --lang en --report bleep.json` (seznam slov je v `pipeline/bleep_words.txt`, doplň názvy drog a kasin podle tématu).
- **Hazard a drogy ve videu nech, jsou jádro příběhu. Jen je vypípni.** Vždy ale:
  - **vyřaď** vtipy a výroky o sebevraždě nebo sebepoškozování (pípnutí kontext nemění, zásady YouTube),
  - **rozmaž** názvy kasin, odkazy a promo kódy (YouTube zakazuje navádět na neschválené hazardní weby),
  - nepřebírej zdravotní informace o nezletilých.

### 7. Sestavení v ArtCraftu (app.getartcraft.com → Edit Video)
Ověřené chování (beta, 18. 10. 2026):
- Kredity jsou 0. Generování obrázků a videa stojí kredity, **editor a export ne**.
- Rozřež render na části po dějstvích (bez zvuku, CRF 24, < 10 MB) + hlas jako **MP3** (M4A editor odmítne). Nahrávej přes skrytý `input[type=file]`: `find` → `file_upload`, **po jednom souboru**.
- Tlačítko „+“ na assetu vkládá na **pozici hlavy**. Před každým dalším klipem klikni do prázdné časové osy a stiskni **End** (hlava na konec). Pro hlas **Home** a pak „+“. Psaný čas v poli editor někdy odmítne (zčervená). Kontroluj polohy klipů z DOM (left/width).
- Text: Text → „Default text“ → „+“. Obsah a velikost nastav **nativním setterem + událostí `input`** (psaní z klávesnice editor zachytí jako zkratky). Velikost 5 ≈ malý popisek. Pozice: Transform → Position Y −470 = horní okraj.
- Titulky (Captions) zatím nejsou („coming soon“), knihovna zvuků je prázdná, z efektů je jen Blur. Titulky dodej jako `.srt` na YouTube.
- Export: MP4 H.264, High. Vypni „Save to my media library“. Soubor přijde do `~/Downloads` → zkopíruj do `render/artcraft_export.cs.mp4` a pusť na něj QA.
- **Pozor:** ArtCraft při exportu mění zvuk (44,1 kHz a cca +3 dB, −11 LUFS). Pro finál použij master z pipeline nebo hlasitost po exportu zkontroluj.
- Média nahraná do ArtCraftu leží v jejich cloudu. Nenahrávej tam nic, co nesmí ven.

### 8. Balíček ke schválení – BRÁNA G5
Předlož: video, `factsheet.md`, `qa_report*.md`, seznam klipů čekajících na práva, názvy a thumbnaily, otevřené problémy a čas a náklady na krok. **Nepublikuj.** Publikaci provádí člověk.

## 3D a 2,5D vizuály (úroveň „Bige“)
Rozbor reference (Bige, „Nejšílenější Selhání Firem“, LMbHaHrHI9s): nakloněné 3D screenshoty s hloubkou ostrosti, výřezy objektů s parallaxem nad rozmazaným pozadím, rozpadající se loga, neonové linky a ikony, částice, zrno, chromatická aberace, silná barevná korekce, rychlé tempo (~170 slov/min) a moderátor na kameře.
- `pipeline/lib/fx3d.py`:
  - `panel3d(img, out, dur, start=(rx,ry,rz,zoom), end=...)` = screenshot nebo dokument v 3D prostoru s pohybem kamery, stínem, odleskem a DOF ✅ otestováno.
  - `parallax(fg_rgba, bg, out)` = výřez nad pozadím (výřez je potřeba připravit, např. rembg nebo ArtCraft BG Change za kredity) – netestováno.
- Pravidlo střihu: **min. každý 3. záběr pohyblivý 3D/2,5D**, žádná statická karta delší než 3 s. Klíčová čísla a otázky z hooku vždy jako 3D záběr z Blenderu.
- **Skutečné 3D – Blender 5.2.2 LTS** (`/Applications/Blender.app`, nainstalováno 18. 10. 2026, SHA-256 ověřen):
  ```
  $PY -I pipeline/blender_render.py number   out.mp4 '{"value":"1,34 MIL.","label":"ODBĚRATELŮ","dur":4}' [--preview]
  $PY -I pipeline/blender_render.py question out.mp4 '{"line1":"SKEČ,","line2":"NEBO ZPOVĚĎ?","dur":3.5}'
  $PY -I pipeline/blender_render.py timeline out.mp4 '{"per_card":1.8,"highlight":2,"cards":[{"image":"card.png","label":"2024"}, ...]}'
  ```
  - Vždy nejdřív `--preview` (50 % rozlišení, 12 vzorků, cca 30 s na 2 s záběru). Prohlédni 3 snímky, oprav, teprve pak finální render.
  - Font pro 3D text: **Archivo Black** (OFL). **Anton v Blenderu rozbíjí háčky** (Č, Ě, Ď), proto ho nepoužívat pro češtinu ve 3D.
  - Vzhled: tmavě modrá stěna s teplou září za objektem, lesklá podlaha s odrazem, prach, zlatý kov, AgX. Post-processing (bloom, zrno, CA, viněta) dělá `blender_render.py`.
  - Silně svítící materiál na textu se rozpije do skvrny – pro čitelný text emise ≤ 2.
  - Scény jsou v `pipeline/blender/shots.py`; nový typ záběru = nová funkce `shot_<name>()`.
  - Kamera: miř přes cíl (Empty + `TRACK_TO`) a ostři na stejný cíl. Vzdálenost volej tak, aby se celý objekt i se štítkem vešel do obrazu (lens 32: poloviční výška obrazu ≈ 0,32 × vzdálenost). Poslední klíčový snímek **nesmí ležet za posledním objektem**, jinak konec záběru ukáže prázdnou scénu (chyba v1 časové osy). Parametry renderu ukládej vedle videa jako `<záběr>.params.json`.

## Kvalita – co hlídat (z rozboru minulých verzí)
| Metrika | Špatně (v1) | Prototyp TOGI | TOGI v2 (18. 10.) | Cíl |
|---|---|---|---|---|
| průměrná délka záběru | 11,3 s | 4,7 s | 2,5 s | 2–3 s |
| tempo řeči | 104 slov/min | 114 | 152 | 150–170 |
| 1. otevřená otázka | 55 s | 26 s | 19 s | ≤ 25 s |
| skutečný obraz (klipy, fotky) | 0 % | 4 místa pro klip | 4 místa pro klip, 14/44 záběrů 3D | ≥ 50 % záběrů |
| hlas | robotický | robotický (Piper) | Piper zrychlený (WER 10 %) | přirozený (komerční TTS) |

### Tempo a 3D ve střihovém plánu (ověřeno na TOGI v2)
- `pace` v `shotlist.<lang>.json`: `scene_gap_s` 0,25, `xfade_s` 0,15, `transition` „fade“, `tts_engine` „piper_cs_viral“ (length_scale 0,64 ≈ 152 slov/min; 0,68 = 145).
- Vlastní 3D klip: `{"template":"motion","params":{"file":"render/fx/x.mp4","start_s":0}}` – render ho rychlostí přizpůsobí délce záběru (0,5–1,3×) a přidá řádek se zdrojem.
- Libovolná karta jako 3D panel: `"fx":"panel3d"` (cache ve `work_<lang>/p3d_*.mp4`).
- Po renderu vypiš délky záběrů (`lib.render.plan`) – statické karty > 3 s rozděl.
- Rychlejší řeč zvyšuje rychlost titulků (> 17 zn./s) – titulky na YouTube nahrávej jako .srt, ale hlídej varování.

### Hudba a zvukové efekty (ověřeno 18. 10. 2026)
- **Hudba:** Kevin MacLeod / incompetech, CC BY 4.0. Monetizace je povolená, atribuce povinná v popisu videa (incompetech FAQ, snímek v `assets/licenses/`). Katalog `~/youtube-agent-env/dl/pieces.json` (pole feel, bpm, isrc), MP3 na `incompetech.com/music/royalty-free/mp3-royaltyfree/<název>.mp3`. Každou skladbu zapiš do `assets.jsonl` s ISRC (pro spor v Content ID) a kredit do `publish/<lang>/credits.txt`.
- **Pixabay nepoužívat jako výchozí** (někteří autoři registrují skladby do Content ID). **YouTube Audio Library** je pro YouTube nejbezpečnější, ale stahování vyžaduje přihlášení uživatele, takže skladby musí stáhnout on sám.
- **Efekty:** vlastní syntéza `pipeline/lib/sfx.py` (`vid.py sfxlib _`): whoosh, hit, impact, riser, heartbeat, roulette_tick, typewriter (klávesy z Kenney Interface Sounds, CC0). Nepotřebují žádnou licenci.
- **Mix:** blok `music` ve `shotlist.<lang>.json`: `cues` {music_cue: `{asset, at, gain_db}` | `{silence}` (jen na jednu scénu) | `{resume}`}, `level_under_voice_db` −21, `level_in_gaps_db` −13, `sfx_gain_db`. `vid.py mix` → `audio/<lang>/mix.wav`, render ho použije automaticky. Mix ověř měřením „hudba+SFX vs. hlas po sekundách“ (cíl pod řečí cca −16 až −20 dB) a pak poslechem člověkem.
