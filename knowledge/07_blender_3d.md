# 07 Blender jako vypravěčský nástroj (a efektivní CPU render)

**Kdy číst:** před návrhem každé 3D scény. Technika pipeline: SKILL.md § „3D a 2,5D vizuály“, `pipeline/blender/shots.py`.

## 3D jen s vypravěčským účelem (zadání Miry § 7)
Před návrhem odpověz (zapiš do `render/fx/<záběr>.brief.md` nebo do vizuálního plánu):
1. Jakou informaci nebo emoci scéna přidává?
2. Proč je 3D lepší než fotka, mapa nebo jednoduchá grafika? (Je k dispozici autentický materiál? → `12` má přednost.)
3. Jak dlouho musí trvat? (typicky 2–4 s; renderuj jen to)
4. Které prvky jsou pro pochopení nezbytné? (vše ostatní pryč)
5. Jak snížit polygony, světla, vzorky a počet snímků bez viditelné ztráty?
Když 3D nepřidává dost, použij levnější řešení.

Dobré použití: rekonstrukce místa a prostoru (stylizovaná, označená), animované mapy a přesuny, časová osa v prostoru,
rozpad objektu / plánu / systému, metafory finančních toků a chaosu, izometrické scény, exploded view a řezy, kamera
procházející prostředím, procedurální davy a opakující se struktury (instancování), typografie ve 3D.
Špatné použití: 3D text jen „protože to jde“, dekorace bez informace, realistická podoba skutečné osoby (zakázáno).

Změny API Blenderu 5.x (před psaním `shots.py`): `third_party/el4cteo-blender-skills/api-changes-5x.md` (po sloučení PR #2).

## Vizuální identita 3D (jednotná napříč videem)
- Stylizace, ne fotorealismus: rekonstrukce nesmí působit jako autentický záznam. Kde hrozí záměna, popisek „rekonstrukce“.
- Světlo: tmavě modrá stěna, teplá záře za objektem, lesklá podlaha, AgX, akcent `#F2B134` [U nás, TOGI/Fyre].
- Text: Archivo Black (Anton rozbíjí háčky ve 3D) [U nás]; emise textu ≤ 2, jinak se rozpije [U nás].
- Kamera: Empty + `TRACK_TO`, ostření na cíl; poslední klíčový snímek nesmí ležet za posledním objektem [U nás, bug v1].
- Post: bloom, zrno, CA, viněta dělá `blender_render.py` – nepřidávej je v Blenderu znovu.

## Efektivní render v cloudu (CPU, hodiny) – zadání Miry § 8
Postup, nikdy nepřeskakuj:
1. kontrola scény a závislostí (fonty, textury, cesty) → 2. **testovací snímek** (1 still) → 3. `--preview`
(50 %, 12 vzorků) → 4. kontrola kamery, materiálů, světel, kompozice na 3 snímcích (začátek, střed, konec) →
5. krátký testovací úsek → 6. **odhad času a místa**: (s/snímek × počet snímků), volné místo `df` → 7. finální render.
Preferuj:
- **EEVEE** (pipeline ho používá; v cloudu přes Mesa EGL, softwarově), Cycles jen kde přínos (odrazy, GI) odůvodní cenu.
  [Praxe, Blender manuál] Cycles: adaptivní sampling (noise threshold 0,01–0,1), denoiser (OpenImageDenoise), méně odrazů.
- Nízké vzorky + denoising; instancování opakovaných objektů (davy, stany, lístky); jednoduchá geometrie a materiály.
- Renderovat jen potřebné snímky (délka záběru × fps + 0,5 s rezerva); 25 fps; nižší rozlišení a upscale při kompozici,
  když to nejde poznat [U nás, pipeline to dělá].
- Opětovné využití existujících renderů z `render/fx/` (stejný záběr do více videí, jiný text = jen textová vrstva).
- **Přerušitelné dávky:** `resume_dir` v `blender_render.py` pokračuje od posledního snímku [U nás]. Logy a parametry
  (`<záběr>.params.json`) vedle výstupu.
- Opravuj a přerenderuj jen postiženou část (rozsah snímků), ne celou scénu.
- Render farma jen když je skutečně zdarma. Hrozí-li překročení limitu (čas session, disk), zastav **před** spuštěním a napiš.
- Mac s GPU (Mira) je rychlejší cesta pro náročné scény – nabídni, nevynucuj.

## Kontrola hotového 3D záběru
- [ ] 3 snímky prohlédnuté: nic neořezané, text čitelný, háčky správně, žádný prázdný konec
- [ ] záběr odpovídá faktům (čísla, názvy, geografie) ze `claims.jsonl`
- [ ] délka sedí na scénu (render přizpůsobí 0,5–1,3×, víc ne)
- [ ] `params.json` uložen, záběr zapsán v `assets.jsonl` (kind `animation`, origin `own`)
