# Kde jsme skončili (2026-10-21)

Hotovo: struktura knihovny, schéma pozorování, `search.py` (hledání + `--check`), extrakční skript pro Chrome,
protokol analýzy, kritéria výběru a první kandidáti (`sample_plan.md`). Formát odsouhlasen s vláknem
„Znalosti a schopnosti agenta“ (TQ-ID citují playbooky jako [Praxe]; rozpor s pravidlem playbooku → zpráva tomu vláknu).

Blokováno: YouTube je z cloudu i z počítače blokované (proxy 403); rozšíření Claude in Chrome hlásilo
„Could not verify this site's safety category“ i pro example.com a pak se odpojilo. Mira připojí Chrome zítra.

Další kroky:
1. Krok 0 v `sample_plan.md`: ověřit handle kanálů a vybrat 2–3 videa na kanál.
2. Ověřit, že `tools/extract_watch.js` na watch stránce vrací titulky a storyboard (fetch titulků může vyžadovat
   jiný postup; záložně otevřít panel „Přepis“ a číst DOM).
3. Analýza podle `protocol.md`, průběžně `search.py --check`.
4. `techniques.md` a `recommendation_fyre.md`; doporučení poslat vláknu „Struktura agenta a pilot Fyre Festival“ (v1.3).
