# Referenční knihovna: dokumentární kanály (konkurenční studie)

Případové studie 15 dokumentárních YouTube kanálů pro výrobu faceless dokumentů (pilot: Fyre Festival).
Knihovna slouží agentovi i člověku: hledá se v ní technika, ne kopírovaný obsah.

## Soubory
| Soubor | Co obsahuje |
|---|---|
| `channels.json` | 15 kanálů + 1 srovnávací (`comparator`), slug, ověřený handle, proč je studujeme |
| `sample_plan.md` | kritéria výběru a seznam 26 analyzovaných videí |
| `protocol.md` | jak analyzovat jedno video (10 bodů zadání), co je pozorování a co interpretace |
| `videos.jsonl` | jeden řádek = jedno analyzované video (metadata + souhrn 10 bodů) |
| `observations.jsonl` | jeden řádek = jedno časově ukotvené pozorování nebo interpretace, schéma `pipeline/schemas/reference_observation.schema.json` |
| `techniques.md` | katalog obecných, přenositelných technik `TQ-nn`; playbooky v `knowledge/` je citují jako [Praxe] |
| `recommendation_fyre.md` | doporučení pro pilot Fyre Festival (co testovat a proč) |
| `search.py` | vyhledávání a kontrola (`--check`) |
| `tools/run_watch.js` | skript pro Claude in Chrome: metadata, přepis s časy, kontaktní listy, odhad střihů a hladiny zvuku (postup v `protocol.md`) |
| `STATUS.md` | aktuální stav a otevřené body |

## Pravidla
- **Pozorování vs. interpretace.** `kind=observation` je jen to, co je v přepisu, přehrávači, náhledu nebo metadatech.
  `kind=interpretation` je náš výklad, proč to funguje. Nikdy je nemíchat v jednom záznamu.
- **Jistota.** `high` = viděno/slyšeno přímo na daném čase; `medium` = odvozeno z přepisu nebo kontaktních listů bez
  přehrání; `low` = odhad (např. hudba popsaná jen z přepisu, náhled ze zmenšeniny).
- **Žádné cizí dílo.** Neukládáme záběry, zvuk, hudbu, grafiku ani celé scénáře. Citace max. 15 slov, jen jako kotva času.
  Nekopírujeme rozpoznatelnou identitu kanálu (logo, typografii, barevný systém, znělku, frázi pořadu).
- **Fakta z videí nejsou zdroje.** Cokoli faktického, co převezmeme do scénáře, ověřujeme z primárních zdrojů
  (`sources.jsonl` projektu), nikdy z cizího videa.
- **Měření.** Střihy za minutu a hladina hudby jsou orientační měření v prohlížeči (meze v `protocol.md`);
  slouží ke srovnání mezi kanály a s naším střihem, ne jako přesná čísla.

## Hledání
```
python3 knowledge/references/competitors/search.py "cold open"
python3 knowledge/references/competitors/search.py --category hook --kind observation
python3 knowledge/references/competitors/search.py --technique TQ-03
python3 knowledge/references/competitors/search.py --check
```
