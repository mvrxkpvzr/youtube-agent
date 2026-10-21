# Externí skilly a nástroje z GitHubu – evidence hodnocení

Stav k 21. 10. 2026. Každý kandidát byl naklonován (`git clone --depth 50`) do izolované složky mimo repozitář a jeho
kód byl **přečten před spuštěním**. Nic z kandidátů se neinstalovalo do `~/.claude/skills` a žádný instalační skript
(`install.sh`, `npx …`) se nespouštěl. GitHub API v tomto prostředí není dostupné, proto u repozitářů neuvádíme hvězdičky
a „poslední aktivitu“ bereme z historie gitu (datum posledního commitu).

Štítky důkazů: **test** = spuštěno a výsledek zaznamenán · **kód** = přečteno v kódu · **neznámé** = nešlo ověřit.

## Co bylo integrováno

| Co | Odkud | Licence | Kam | Ověřeno |
|---|---|---|---|---|
| Kontrola fotosenzitivního blikání (WCAG 2.2 SC 2.3.1 + EA IRIS) | konradre/video-production-skills `decoded_checks.py` @ `8a69b59` | MIT | `third_party/konradre-video-production-skills/`, adaptér `pipeline/lib/flashcheck.py`, řádky „blikání“ v `lib/qa.py` | test: selftest 36/36, `tests/test_flashcheck.py`, Fyre v1.3 celé video 12 516 snímků za 74 s → 0 záblesků |
| Přenositelná časová osa (OTIO + CMX 3600 EDL) | OpenTimelineIO 0.18.1 + otio-cmx3600-adapter 1.0.0 (PyPI) | Apache-2.0 | `pipeline/otio_export.py`, `setup/requirements.cloud.txt` | test: `tests/test_otio_export.py`; Fyre v1.3 (kopie) 119 záběrů, 66 značek scén, délka 500,60 s vs. video 500,64 s |
| Tabulka změn bpy API 4.x → 5.2 (jen znalost) | EL4CTEO/blender-skills `api-changes-5x.md` @ `71d031d` | MIT | `third_party/el4cteo-blender-skills/` | kód: náš `shots.py` v Blenderu 5.2.2 hlásí přesně varování, která tabulka uvádí (`use_nodes`) |

Kontrola blikání **nic neopravuje**: FAIL (víc než 3 záblesky za sekundu nebo trvalé 2–3 za sekundu) je ERROR v QA a
blokuje publikaci, WARN vyžaduje lidskou kontrolu. Když chybí `ffmpeg`/`ffprobe`, QA zapíše „kontrola blikání NEPROBĚHLA“
(nikdy ne tichý průchod). Úmyslné blikání lze vyjmout oknem `(od, do, důvod)` ve `flashcheck.check(..., accepted=...)`.

`otio_export.py` je místní záloha k ArtCraftu: časovou osu otevře DaVinci Resolve (zdarma), Kdenlive nebo Premiere.
Bere záběry z `render/edl.<lang>.json` (pipeline/edl.py z vlákna „Znalosti a schopnosti agenta“), jinak z `lib.render.plan`.
**Otevření v Resolve/Kdenlive jsme netestovali** (v cloudu není grafický střihový program); ověřeno je zpětné načtení `.otio`
i `.edl` knihovnou OpenTimelineIO a shoda délky s videem. Kontrola navíc hlásí, když je render zastaralý vůči plánu
(u Fyre v1.3 platí: `shotlist.cs.json` se změnil po posledním renderu).

## Skóre (0–5)

Rel = přínos pro dokumentární pipeline · Spol = spolehlivost a údržba · Komp = kompatibilita s naším agentem ·
Bezp = bezpečnost · 0 Kč = vhodnost pro nulový rozpočet · Snad = snadnost integrace.

| Kandidát | Rel | Spol | Komp | Bezp | 0 Kč | Snad | Verdikt |
|---|---|---|---|---|---|---|---|
| konradre/video-production-skills – celá sada | 2 | 4 | 2 | 3 | 1 | 2 | ne: postavená na placených generátorech videa a hlasu |
| ↳ jen `decoded_checks.py` (blikání) | 4 | 4 | 5 | 5 | 5 | 5 | **integrováno** |
| kajisho5/video-production-agent | 2 | 3 | 1 | 3 | 5 | 1 | ne: vlastní orchestrátor, duplikuje `vid.py` |
| cdeistopened/skill-stack – youtube-scriptwriting | 2 | 2 | 4 | 5 | 5 | 4 | ne: obecné rady, překryv s playbooky |
| xnomad-dev/claude-skills – video-script-writer | 2 | 1 | 4 | 5 | 5 | 0 | ne: bez licence |
| laurentickner/youtube-scripting-skill | neznámé | – | – | – | – | – | nedostupné (neexistuje nebo soukromé) |
| EL4CTEO/blender-skills – celá sada | 2 | 2 | 3 | 4 | 5 | 3 | ne: zaměřeno na herní assety |
| ↳ jen `api-changes-5x.md` | 3 | 3 | 5 | 5 | 5 | 5 | **integrováno (znalost)** |
| vinhelysia/blender-mcp | 2 | 2 | 1 | 2 | 5 | 2 | ne: potřebuje Blender s GUI |
| oh-ashen-one/blender-agent-skills | 2 | 1 | 2 | 4 | 4 | 3 | ne: postupy převzaty jen jako poznámky |
| clonn/awesome-agent-video-skills | – | – | – | – | – | – | katalog, jen k vyhledávání |
| ella-wang-opus/awesome-video-skills | – | – | – | – | – | – | katalog bez licence, jen k vyhledávání |
| OpenTimelineIO + otio-cmx3600-adapter | 4 | 5 | 5 | 5 | 5 | 5 | **integrováno** (doplněno kvůli mezeře E) |

## Záznamy kandidátů

### 1. konradre/video-production-skills — https://github.com/konradre/video-production-skills
- **Co skutečně umí (kód):** 15 skillů pro reklamní spoty, krátké filmy a vysvětlující videa. Jádro je generování záběrů
  (Seedance, MiniMax) přes placené služby, hlas a efekty z ElevenLabs, hudba ze Suno přes AceDataCloud, finiš v DaVinci
  Resolve Studio + Dehancer Pro. Místní části: QC dodaného souboru (`qc_deliverable.py`, `decoded_checks.py`), EDL builder
  ve vlastním formátu, audio skripty.
- **Licence:** MIT (`LICENSE`), `NOTICE.md` uvádí MIT kostky z ComfyUI-Darkroom a spectral_film_lut (ty jsme nepřebírali).
- **Údržba:** poslední commit 11. 10. 2026, ≥ 50 commitů od 16. 9. 2026. README: „`skills/` se generuje z jiného zdroje“.
- **Závislosti:** Python ≥ 3.10, numpy, Pillow, scipy, PyYAML, OpenCV, ffmpeg; pro hlavní funkce placené účty a klíče
  (`KIE_API_KEY`, `FAL_KEY`, `ELEVENLABS_API_KEY`, `ACEDATACLOUD_API_TOKEN`, Higgsfield, monid, treg), GPU, Windows + Resolve Studio.
- **OS:** Linux/macOS, Windows jen přes WSL2.
- **Bezpečnost (kód):** `install.sh` linkuje skilly do `~/.claude/skills` (nespuštěno). Převzatý `decoded_checks.py`: jen
  `ffmpeg`/`ffprobe` jako seznam argumentů, žádná síť, žádné proměnné prostředí, zápis jen do dočasné složky v selftestu.
- **Rozpor s pravidly kanálu:** AI generované záběry a AI hudba (Mira zakázala AI hudbu a AI zvukové efekty).
- **Testy:** selftest 36/36 · stroboskop 6,25 Hz → FAIL · klidný přechod → OK · chybějící soubor → „skipped“ · Fyre v1.3 → 0 záblesků.

### 2. kajisho5/video-production-agent — https://github.com/kajisho5/video-production-agent
- **Co umí (README, kód):** japonský orchestrátor (CLI `video-agent`): analýza nahrávky, plán střihu tichých míst,
  normalizace hlasitosti, export, schvalování a `--resume`. Fáze 1 hotová, titulky/multicam jen návrh.
- **Licence:** `pyproject.toml` uvádí MIT, **soubor LICENSE chybí**.
- **Údržba:** 5.–11. 9. 2026, 56 commitů. **Závislosti:** jsonschema + 4 další repozitáře autora (ffmpeg-skill přes `npx`).
- **Proč ne:** zavádí nový rámec agenta a duplikuje náš `vid.py` (state.json, cache, QA). Instalace přes `npx` = neprověřený kód.

### 3. cdeistopened/skill-stack → `.claude/skills/youtube-scriptwriting`
- **Co umí:** pouze text (prompt): workflow v kontrolních bodech, „realita musí překonat očekávání“, skóre šoku 1–100,
  9 typů hooků, 7 struktur. Cílí na tutoriály a listicly, ne dokument.
- **Licence:** MIT, ale copyright „Wayne Sutton 2025“ v repozitáři jiného autora (původ nejasný). Skill má jediný commit (26. 1. 2026).
- **Proč ne:** překryv s playbooky scénáře a retence (`knowledge/` z vlákna „Znalosti a schopnosti agenta“). Užitečné nápady
  (skóre šoku faktů, kontrola „vizuál = slovo = text v hooku“) předány tomu vláknu jako podnět.

### 4. xnomad-dev/claude-skills → `video-script-writer`
- **Co umí:** prompt na scénáře talking-head/short-form s [B-ROLL] značkami. **Licence: žádná** → autorská práva vyhrazena,
  nelze převzít. Poslední commit 8. 4. 2026.

### 5. laurentickner/youtube-scripting-skill
- `git clone` vyžaduje přihlášení → repozitář neexistuje nebo je soukromý. Nic dalšího nelze ověřit.

### 6. EL4CTEO/blender-skills — https://github.com/EL4CTEO/blender-skills
- **Co umí:** 22 skillů pro Blender 5.2+ (modelování, rigging, PBR, export do herních enginů, rendering, počasí, QA assetů),
  skripty volané `blender -b … -P`. README tvrdí 50 testů v Blenderu (**nespouštěli jsme je**).
- **Licence:** MIT. **Údržba:** 6 commitů 14.–16. 10. 2026 (velmi mladé). **Kompatibilita:** Blender 5.2 ✔ (máme 5.2.2).
- **Bezpečnost:** skripty pracují jen s bpy a soubory; `install/install.sh` nespuštěn.
- **Převzato:** jen tabulka změn API. Užitečné poznámky z `blender-rendering` (neintegrované, k úvaze pro vlákno pilotu):
  renderovat snímky a kódovat zvlášť (máme), `render.use_persistent_data` pro animace, EEVEE vyžaduje GPU kontext i v
  pozadí → v cloudu bez GPU je Cycles na CPU nebo Workbench často rychlejší cesta (neměřeno).

### 7. vinhelysia/blender-mcp — https://github.com/vinhelysia/blender-mcp
- **Co umí:** MCP server (1 049 řádků Pythonu), 26 nástrojů, mluví s oficiálním rozšířením Blender Lab MCP na TCP 9876.
- **Licence:** MIT (přidána 12. 7. 2026). **Požadavky:** Blender 5.1+ **s GUI** a zapnutým rozšířením, balíček `mcp`.
- **Proč ne:** náš Blender běží v cloudu bez GUI; nástroj spouští libovolný Python v Blenderu přes lokální socket. Vhodné
  nanejvýš na Macu pro ladění scén, ne do automatické výroby.

### 8. oh-ashen-one/blender-agent-skills
- **Co umí:** 5 znalostních skillů z „postmortemů“ (izolované MCP relace, stavba scény po etapách s checkpointy, vizuální
  brána podle konceptu, voxely, rigy). Licence MIT, 1 commit (15. 9. 2026).
- **Převzaté poznámky (bez kódu):** ≥ 3 náhledy v nízkém rozlišení před finálním renderem, `validation.json` s polem
  `known_limits`, finální render v samostatném procesu na pozadí.

### 9–10. Katalogy
- **clonn/awesome-agent-video-skills** (MIT, 184 repozitářů, data z 10. 10. 2026): použito k hledání mezer. Jeho hlavní tip
  OpenMontage je **AGPL-3.0** → pro nás ne.
- **ella-wang-opus/awesome-video-skills** (bez licence, 17 položek, hlavně AI generování a Remotion): nic pro náš pipeline.

### 11. OpenTimelineIO (Academy Software Foundation) + otio-cmx3600-adapter
- **Proč:** mezera E – přenositelný střihový list. `pipeline/README.md` ji uváděl jako chybějící („export XML do Premiere“).
- **Licence:** obě Apache-2.0 (metadata balíčků z PyPI). Žádné běhové závislosti, žádná síť za běhu.
- **Testy:** viz výše; formát `.otio` čte DaVinci Resolve a Kdenlive (externí informace, netestováno).

## Mapa schopností (12 cílů) – co existuje a co tato práce přidala

| # | Cíl | Stav před | Tato práce |
|---|---|---|---|
| 1 | Rešerše a ověření zdrojů | `snapshot.py`, `claims/sources.jsonl`, `validate.py`, brána G2 | – (vlákno znalostí) |
| 2 | Scénář a retence | pravidla ve SKILL.md, playbooky (vlákno znalostí) | – nic lepšího s licencí nenalezeno |
| 3 | Střihový plán / EDL | `shotlist.<lang>.json`, `edl.py` (vlákno znalostí) | export do OTIO / CMX EDL |
| 4 | Archivní záběry | pravidla + manifest (vlákno znalostí) | – |
| 5 | Blender | `blender_render.py` (`--preview`, `resume_dir`) | reference API 5.x; test obnovy přerušeného renderu |
| 6 | Sestavení videa | `lib/render.py`, ArtCraft (ruční, beta) | časová osa pro Resolve/Kdenlive jako místní záloha |
| 7 | Hudba, zvuk, mix | `lib/mix.py`, `lib/sfx.py`, incompetech | – (AI hudba/SFX vyřazeny) |
| 8 | Titulky, čeština | `subtitles.py`, `asr_check.py`, lexikon | – |
| 9 | Náhled, název | 3 varianty v kroku 4 | – |
| 10 | Technické QA | `lib/qa.py` | **kontrola blikání** (nová kategorie chyb) |
| 11 | Obnova po chybě | `state.json`, cache TTS, `resume_dir` | ověřeno testem (viz zpráva) |
| 12 | Analytika po publikaci | postmortem (vlákno znalostí) | – (bez přístupu k YouTube Analytics nic nepředstíráme) |

## Test obnovy po chybě (21. 10. 2026, cloud, 4 CPU, Blender 5.2.2 EEVEE přes Mesa)
- Záběr `question` („FESTIVAL, / NEBO PODVOD?“), náhled 50 %, 12 vzorků, 30 snímků; ≈ 11 s na snímek.
- Blender násilně ukončen (`kill -9`) po 12 snímcích → `blender_render.py … resume_dir` dorenderoval snímky 13–30
  (192 s), snímky 1 a 12 zůstaly bajtově stejné (md5), výsledné video 30 snímků 1920×1080, snímky před a po přerušení
  navazují (kontaktní list prohlédnut), kontrola blikání OK.
- Omezení: `resume_dir` počítá hotové snímky podle počtu PNG; rozepsaný (poškozený) poslední PNG by nepoznal. Neměřeno, zda
  Blender píše PNG atomicky.

## Vrácení změn
Vše je na větvi `claude/project-thread-ld1qhi`. Odstranění: smazat `third_party/`, `docs/external-skills/`,
`pipeline/lib/flashcheck.py`, `pipeline/otio_export.py`, oba testy, vrátit blok „photosensitive flashes“ v `lib/qa.py` a
dva řádky v `setup/requirements.cloud.txt` – nebo `git revert` commitu. Projekty ani assety se neměnily.
