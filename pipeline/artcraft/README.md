# ArtCraft ve střihu (stav k 21. 10. 2026)

Agent stříhá a exportuje video v **editoru ArtCraftu** sám, bez obsluhy. Ověřený postup i výsledek testu jsou níže.

## Co ArtCraft nabízí a co z toho jde automatizovat (ověřeno ze zdrojového kódu)

ArtCraft je open source (MIT nebo Apache-2.0, github.com/storytold/artcraft). Web app.getartcraft.com je z cloudu
nedostupný (proxy ho blokuje), proto jsem vycházel ze zdrojového kódu.

| Funkce | Co to je | Automatizace |
|---|---|---|
| **Create Video** | AI generování videa z promptu (Seedance, Kling…), **spotřebovává kredity** | Existuje „Omni API“ (`api.storyteller.ai/v1/omni_api/generate/video`) s API klíčem, který musí na účtu zapnout podpora ArtCraftu. Pro střih ho nepoužíváme. |
| **Video editor** | časová osa, video/obrázky/zvuk/text, ořez, keyframy (průhlednost, měřítko, hlasitost), efekty, export MP4/WebM | V online aplikaci žádné API ani import projektu ze souboru. Editor je ale samostatná knihovna `@storyteller/ui-video-editor` s veřejným programovým rozhraním (`EditorCore`) a formátem projektu (`ProjectDocument v1`). Celý běží v prohlížeči (WebGPU + WebCodecs), export **nestojí kredity**. |

Agent proto používá **tutéž knihovnu editoru** v malé hostitelské stránce (`host/`) a ovládá ji přes Playwright
(`host/run_editor.mjs`). Žádné nezdokumentované API, žádné přihlašování, nic neopouští počítač
(Playwright blokuje všechny požadavky mimo místní stránku).

## Rozdělení práce

| Nástroj | Dělá |
|---|---|
| FFmpeg + `lib/graphics`, `lib/fx3d`, Blender | jednotlivé záběry (karty, fotky s pohybem, 3D, mapy) → `render/work_<lang>/shotNNN.webm` |
| MOSS/Piper, Whisper, `lib/subtitles` | hlas po scénách, kontrola, titulky .srt |
| `lib/mix` | hudba + SFX s ducháním pod hlasem → `audio/<lang>/bed.wav` (hlas zvlášť) |
| **ArtCraft editor** | sestaví střih: záběry v pořadí, prolínání, hlas po scénách, hudební podklad, volitelně titulky do obrazu; export |
| FFmpeg | master pro YouTube: H.264/AAC, hlasitost −14 LUFS dvěma průchody |
| `lib/verify_export` | ověří export proti plánu (viz níže), zvlášť surový export editoru i master |

## Střihový plán (meziformát)

`render/editplan.<lang>.json`, schéma `schemas/editplan.schema.json`, tvoří `lib/editplan.py`:

- `media`: zásobník médií `M001…` (cesta v projektu, druh, délka, sha256, čím vzniklo).
- `scenes`: scény `SC001…` v pořadí. Každá má vlastní délku a **vlastní** klipy `video`, `audio`, `text` s časy
  **relativně ke scéně** (`at_s`, `dur_s`, `in_s`, `fit`, `zoom_from/to`, `fade_in_s/fade_out_s`, `gain_db`, `role`).
  Scénu jde přestříhat nebo vyměnit, aniž by se sahalo na ostatní; další scény se jen posunou.
- `global_audio`: podklady přes celé video (hudba + SFX).
- `transition`: výchozí přechod mezi klipy `cut | fade | fadeblack` (klip ho může přepsat `transition_in`).
- `inputs_sha256`: z čeho plán vznikl (shot list, časy, EDL), aby šlo poznat zastaralý plán.

Klíčem je id scény jako v `shotlist.<lang>.json` a v EDL (`edl.py`); když EDL existuje, plán s ním musí souhlasit.
`editplan.resolve()` z plánu udělá absolutní časovou osu pro editor (`render/timeline.<lang>.json`):
`fade` = pozdější klip leží na druhé video stopě a prolne se přes konec předchozího (stejně jako FFmpeg xfade),
`fadeblack` = ztmavení a rozjasnění kolem střihu.

## Postup (ověřený)

```
bash pipeline/artcraft/setup.sh                       # jednou za session: ArtCraft (pevný commit), npm ci, build (~1 min)
$PY -I pipeline/vid.py subs    projects/<p> --lang cs
$PY -I pipeline/vid.py mix     projects/<p> --lang cs  # bed.wav
$PY -I pipeline/vid.py artcraft projects/<p> --lang cs [--burn-subs] [--final]
#   = render.render_shots → editplan → timeline → editor (import, střih, export) → verify → master → verify
$PY -I pipeline/vid.py qa      projects/<p> --lang cs  # běžné QA na preview/final mp4
```

Výstupy v `render/`: `editplan`, `timeline`, `artcraft.<lang>.webm` (export editoru), `artcraft.<lang>.editor.json`
(časová osa načtená zpět z editoru + projekt ve formátu ArtCraftu `ProjectDocument`), `preview|final.<lang>.mp4`,
`verify_artcraft.<lang>.md|json`, `verify_artcraft_master.<lang>.md|json`.

### Co ověření kontroluje (ERROR = export neodpovídá plánu, pipeline se zastaví)

1. soubor existuje, rozlišení, fps, video i zvuková stopa, délka ±2 snímky;
2. **přehratelnost**: celý soubor se dekóduje bez jediné chyby;
3. časová osa načtená zpět z editoru má stejné prvky a časy jako plán, stejné texty;
4. **obraz**: u každého klipu snímek uprostřed klipu proti snímku ze zdroje (korelace ≥ 0,8) a zároveň se musí
   podobat svému klipu víc než kterémukoli jinému (chytá prohozené pořadí);
5. **hlas**: každá scéna se najde v exportu křížovou korelací se zdrojem a posun je ≤ 40 ms;
6. žádný černý úsek ≥ 0,5 s.

## Ověřeno na testovacím projektu (21. 10. 2026)

Prvních 7 scén pilotu Fyre (37 s), čistá instalace `setup.sh` a pak `vid.py artcraft --burn-subs` v cloudu:
editor importoval 18 médií, položil 16 záběrů (prolínání přes dvě stopy), 8 zvukových klipů (7× hlas po scénách
+ hudební podklad) a 15 titulků, exportoval VP9/Opus 1080p25 za 898 s. Ověření surového exportu i mp4 masteru: **PASS**
(obraz 16/16 klipů se shodou ≥ 0,996, hlas 7/7 scén, korelace ≥ 0,96, posun 14 ms stálý – zpoždění kodéru Opus).
`vid.py qa` na masteru: −14,0 LUFS, true peak −1,5 dBFS, h264/aac, bez černých úseků.
Kontrola, že ověření není bezzubé: plán s prohozenými klipy, posunutým hlasem o 0,2 s a špatnou délkou ověření
odmítne (`tests/test_verify_export.py` totéž na syntetickém videu). Výstupy testu:
`/mnt/project-files/youtube/projects/artcraft-test_fyre7/render/`.

## Omezení (změřeno)

- **Rychlost v cloudu**: bez GPU kreslí WebGPU SwiftShader na CPU, asi 0,6 s na snímek 1080p (5 s videa ≈ 90 s).
  Celé 8minutové video zabere v cloudu několik hodin; preview je proto vhodné pouštět po částech nebo přes noc.
  Na Macu s Chromem (`PW_CHANNEL=chrome`) běží na GPU.
- Open-source Chromium neumí H.264: v cloudu proto záběry i export používají VP9/Opus (WebM) a mp4 dělá až master.
- Headless Chromium neumí přečíst WebGPU plátno (export vyjde černý). Proto běží „s oknem“ ve virtuálním displeji Xvfb.
- Editor nemá přechody jako hotové efekty; prolínání je skládáno z průhlednosti dvou stop (výsledek je stejný).
- Online aplikace app.getartcraft.com na účtu uživatele zatím ověřená není (nešel připojit Chrome). Projekt z ní
  nelze načíst ani do ní nahrát souborem; v ní jde jen ručně dolaďovat.

Původní cesta (`vid.py render`, čisté FFmpeg) zůstává jako záloha, když editor není k dispozici.
