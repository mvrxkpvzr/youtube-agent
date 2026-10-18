"""Render claims.jsonl + sources.jsonl into factsheet.md for the human fact-check gate (G2).
Usage: python factsheet.py <project>"""
import json, sys
from pathlib import Path
proj = Path(sys.argv[1])
rd = lambda p: [json.loads(l) for l in (proj / p).read_text(encoding="utf-8").splitlines() if l.strip()]
S = {s["id"]: s for s in rd("sources.jsonl")}; C = rd("claims.jsonl")
LBL = {"verified": "✅ ověřeno", "attributed": "🟡 tvrzení zdroje – ve scénáři „podle …“", "disputed": "⚠️ sporné",
       "unverified": "⛔ neověřeno – nepoužít", "rejected": "⛔ vyřazeno redakčně"}
out = [f"# Fact sheet – {proj.name}", "", f"{len(C)} tvrzení, {len(S)} zdrojů. Stav: **čeká na schválení (brána G2)**.", "",
       "| Stav | Počet |", "|---|---|"] + [f"| {LBL[k]} | {sum(c['status'] == k for c in C)} |" for k in LBL] + ["", "## Tvrzení", ""]
for c in C:
    out.append(f"### {c['id']} · {LBL[c['status']]} · citlivost: {c['sensitivity']}" + (f" · datum události: {c['event_date']}" if c.get("event_date") else ""))
    out.append(c["text_cs"]); out.append("")
    for e in c["evidence"]:
        s = S[e["source_id"]]
        out.append(f"- {e['source_id']} ({s['tier']}) [{s['publisher']}]({s['url']}), {s.get('published_at') or 'bez data'}: „{e.get('locator','')}“")
    if c.get("conflicts"): out.append(f"- **Pozn.:** {c['conflicts']}")
    out.append("")
out += ["## Zdroje", "", "| ID | Tier | Médium | Datum | Titulek | Poznámka |", "|---|---|---|---|---|---|"]
out += [f"| {s['id']} | {s['tier']} | {s['publisher']} | {s.get('published_at') or ''} | [{s['title'][:70]}]({s['url']}) | {s.get('notes','')} |" for s in S.values()]
(proj / "factsheet.md").write_text("\n".join(out) + "\n", encoding="utf-8"); print(proj / "factsheet.md")
