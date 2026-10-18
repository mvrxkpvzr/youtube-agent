# Průzkum GitHubu: hlas, hudba, zvukové efekty, Blender (18. 10. 2026)

Licence a aktivita ověřeny přes GitHub API a Hugging Face API (metadata repozitářů a karet modelů) 18. 10. 2026. „Ověřeno“ = z primárního zdroje; „netestováno“ = zatím jsme model nespustili.

## 1. Hlas (čeština, komerční použití)

| Projekt | Licence (kód / váhy) | Čeština | Mac M2 16 GB | Verdikt |
|---|---|---|---|---|
| **MOSS-TTS v1.5 / Local-Transformer v1.5** (OpenMOSS, ★4,2k) | Apache-2.0 / Apache-2.0 (HF tag) | **ano** (`cs` v kartě modelu) | ano: MLX 8bit 4,9 GB / 4bit přes `mlx-audio` (MIT, ★8k) | **hlavní kandidát – testuji** |
| **MOSS-VoiceGenerator** (1,7B) | Apache-2.0 | – (návrh hlasu z popisu) | pravděpodobně | **vlastní originální hlas kanálu** bez klonování skutečné osoby |
| Chatterbox Multilingual V3 (Resemble, ★27k) | MIT | **ne** (README: 23 jazyků bez češtiny; web Resemble tvrdí opak) | ano | nevhodné, navíc vodoznak |
| VoxCPM2 (OpenBMB, ★39k) | Apache-2.0 | neoficiálně, **WER 24 %** (jejich vlastní tabulka; ElevenLabs 2,1 %) | ano | nevhodné pro CZ |
| Pocket TTS (Kyutai, ★9,9k) | MIT | jen komunitní model, licence nejasná | ano (CPU) | později ověřit |
| Piper | archivováno → pokračuje jako `OHF-Voice/piper1-gpl` (GPL-3.0) | ano | ano | současný záložní hlas |
| XTTS-v2, F5-TTS, OmniVoice, Woosh | nekomerční váhy | – | – | **vyřazeno** |

## 2. Hudba a zvukové efekty

| Projekt | Licence | Co dělá | Mac | Verdikt |
|---|---|---|---|---|
| **ACE-Step 1.5** (★13,8k) | kód MIT, váhy MIT (HF tag) | generuje hudbu na míru (délka 10 s–10 min, žánr, nálada) | ano, backend MLX, < 4 GB VRAM; váhy cca 10 GB | **vlastní hudba přesně na délku a dějství** – vyzkoušet po uvolnění disku |
| **MOSS-SoundEffect v2.0** (1,3B DiT) | Apache-2.0 | efekty 48 kHz do 30 s z textu (EN/ZH) | nepotvrzeno (PyTorch); 11 GB | slibné pro whoosh/impact/ambience |
| Stable Audio Open + stable-audio-tools | kód MIT, váhy Stability Community License (komerčně do 1 mil. USD obratu) | efekty a krátké smyčky | ano | záloha |
| Sony Woosh | kód MIT, **váhy CC-BY-NC** | efekty | ne (CPU/CUDA) | **vyřazeno** |
| **pedalboard** (Spotify, ★6,4k) | GPL-3.0 (pro interní použití OK) | studiové efekty v Pythonu: EQ, kompresor, reverb, limiter | ano | **lepší mix a mastering** místo našich provizorních filtrů |
| **pyloudnorm** (★0,8k) | MIT | přesné měření LUFS (ITU BS.1770) | ano | **přesné hlasitosti stop** v mixu |
| matchering (★2,7k) | GPL-3.0 | mastering podle referenční nahrávky | ano | volitelně |

Poznámka k AI hudbě: ACE-Step sám upozorňuje na možnou „stylovou podobnost“ s existujícími díly. AI výstup nemusí být chráněný autorským právem, takže ho nemůžeme vymáhat jako „naše dílo“. Pro YouTube je ale podstatné, že ho nikdo nemá registrovaný v Content ID.

## 3. Blender a motion design

| Projekt | Licence | Přínos | Verdikt |
|---|---|---|---|
| **mcp-for-blender** (dříve blender-mcp, ★31,5k) | MIT | Claude ovládá běžící Blender, nástroj `look` renderuje pohledy pro kontrolu, import assetů z Poly Haven | **ano** – rychlejší ladění scén; jen lokálně, vypnout telemetrii, nepoužívat placené generátory (Hyper3D, Meshy, Tripo) |
| **Poly Haven** | CC0 (HDRI, textury, modely) | realistické osvětlení a odrazy (zlatý text, lesklá podlaha) | **ano** – HDRI jsou největší rychlé zlepšení vzhledu |
| Cycles + OpenImageDenoise | součást Blenderu | fyzikálně správné odrazy a světlo místo Eevee | ano pro finální rendery (pomalejší) |
| Commotion | GPL-3.0 | posunuté animace mnoha objektů (efektory) | volitelně |
| Coldtype / ST2 | ověřit | typografie v Blenderu | volitelně |
| **Remotion** (★65k) | vlastní licence: **zdarma pro jednotlivce a firmy do 3 zaměstnanců, i komerčně** (změna ohlášena pro v5.0) | animované 2D karty, kinetická typografie, grafy v Reactu | **ano** – nahradí statické karty z Pillow, což je teď největší vizuální slabina |
| Motion Canvas (★19k) / Revideo (★4,1k) | MIT | totéž, čistě open source (TypeScript) | alternativa k Remotion |
| Manim (★42k) | MIT | animace čísel, grafů a schémat | volitelně |
| TRELLIS / TripoSR | MIT | obrázek → 3D model | TRELLIS vyžaduje CUDA (na Macu ne). Výstupy nepoužívat na skutečné osoby. |
| Hunyuan3D, HunyuanVideo-Foley (Tencent) | Tencent Hunyuan Community License – podle mé znalosti vylučuje území EU (dnes jsem to znovu neověřoval) | – | **vyřazeno**, dokud se neověří (ČR je v EU) |

## 4. Omezení prostředí
- Volné místo na disku: cca 21 GB → 16 GB po stažení MOSS. ACE-Step (10 GB) a MOSS-SoundEffect (11 GB) se už nevejdou. **Externí SSD je teď skutečná překážka.**
- 16 GB RAM: modely 4B v 8bit jsou na hraně, větší modely nespouštět souběžně.

## 5. Test MOSS-TTS v češtině (18. 10. 2026, M2 16 GB)
Model `mlx-community/MOSS-TTS-Local-Transformer-v1.5-8bit` přes `mlx-audio` 0.5.9. První scéna je vygenerovaná jen podle popisu stylu (originální hlas, bez klonování skutečné osoby), další scény mají první jako hlasovou referenci.

| Scéna | MOSS WER | Piper WER | MOSS slov/min | Piper slov/min |
|---|---|---|---|---|
| SC001 | 6 % | 18 % | 145 | 172 |
| SC005 („TOGI“) | **0 %** | 33 % („to dí“) | 153 | 170 |
| SC012 | 0 % | 15 % | 141 | 157 |
| SC017 | 4 % | 4 % | 123 | 157 |
| **průměr** | **2,5 %** | 17,5 % | 141 | 164 |

- Rychlost: asi 14× pomalejší než reálný čas (12 s řeči ≈ 3 min). Celé video (110 s) ≈ 25 min, přijatelné pro dávkovou výrobu.
- Tempo je pomalejší než cíl, řešení: instrukce „rychlé tempo“ nebo `atempo` 1,1×. Zatím netestováno.
- **Lidský poslech neproběhl:** ukázky `voice_test/samples/ukazka_moss_4sceny.mp3` a `ukazka_piper_4sceny.mp3`.
- Disk: model 4,9 GB, prostředí `venv/mlxaudio`.

## 6. Doporučený postup (priorita)
1. **Hlas → MOSS-TTS** (po tvém poslechu): engine `moss_cs` v pipeline, jeden pevný referenční hlas kanálu (nejlépe navržený přes MOSS-VoiceGenerator), zrychlení na 150–160 slov/min, kontrola zpětným přepisem zůstává.
2. **Mix → pyloudnorm + pedalboard:** přesné LUFS stop, EQ a komprese hlasu, reverb a limiter na efektech, sidechain ducking místo provizoria.
3. **2D karty → Remotion** (zdarma pro jednotlivce): animovaná kinetická typografie místo statických karet. Největší vizuální zlepšení.
4. **Blender → Poly Haven HDRI (CC0) + Cycles pro finál + mcp-for-blender** pro iterace s náhledy.
5. **Hudba na míru → ACE-Step 1.5** a **efekty → MOSS-SoundEffect v2**: až po uvolnění disku (externí SSD), dohromady cca 21 GB.
