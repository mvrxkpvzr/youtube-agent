"""Validate a project folder: JSON schemas + cross-references + publication blockers.
Usage: python validate.py <project_dir>   (exit code 1 if errors)"""
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

SCHEMAS = Path(__file__).parent / "schemas"
def schema(name): return Draft202012Validator(json.loads((SCHEMAS / name).read_text()), format_checker=FormatChecker())
def jsonl(p): return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []

proj = Path(sys.argv[1]); errors, warnings = [], []
def check(objs, sch, label):
    v = schema(sch)
    for o in objs:
        for e in v.iter_errors(o): errors.append(f"{label} {o.get('id','?')}: {e.message}")

sources, claims, assets = jsonl(proj/"sources.jsonl"), jsonl(proj/"claims.jsonl"), jsonl(proj/"assets.jsonl")
check(sources, "source.schema.json", "source"); check(claims, "claim.schema.json", "claim"); check(assets, "asset.schema.json", "asset")
state = json.loads((proj/"state.json").read_text()); check([state], "state.schema.json", "state")
S, C, A = {s["id"]: s for s in sources}, {c["id"]: c for c in claims}, {a["id"]: a for a in assets}
for c in claims:
    for ev in c["evidence"]:
        if ev["source_id"] not in S: errors.append(f"claim {c['id']}: unknown source {ev['source_id']}")
    tiers = {S[e["source_id"]]["tier"] for e in c["evidence"] if e["source_id"] in S}
    if c["status"] == "verified" and tiers <= {"C", "D"}: errors.append(f"claim {c['id']}: 'verified' but only tier C/D evidence")
    if c["sensitivity"] == "high" and not c.get("reviewed_by"): warnings.append(f"claim {c['id']}: high sensitivity, no human review")
for a in assets:
    if a.get("realistic_depiction_of_real_person"): errors.append(f"asset {a['id']}: realistic AI depiction of a real person is blocked")
    if a["origin"] == "quotation_third_party" and not a.get("quotation_purpose"): errors.append(f"asset {a['id']}: quotation without stated purpose")
for sl in sorted(proj.glob("shotlist.*.json")):
    doc = json.loads(sl.read_text(encoding="utf-8")); check([doc], "shotlist.schema.json", sl.name)
    for sc in doc.get("scenes", []):
        for cid in sc.get("claim_ids", []):
            if cid not in C: errors.append(f"{sl.name} {sc['id']}: unknown claim {cid}")
            elif C[cid]["status"] in ("unverified", "rejected"): errors.append(f"{sl.name} {sc['id']}: uses {C[cid]['status']} claim {cid}")
            elif C[cid]["status"] == "disputed": warnings.append(f"{sl.name} {sc['id']}: disputed claim {cid} – blocks approval")
            elif C[cid]["status"] == "attributed": warnings.append(f"{sl.name} {sc['id']}: claim {cid} is attributed – narration must name the source")
        for v in sc["visuals"]:
            if v.get("asset_id") and v["asset_id"] not in A: errors.append(f"{sl.name} {sc['id']}: unknown asset {v['asset_id']}")
            elif v.get("asset_id") and A[v["asset_id"]]["status"] != "cleared": warnings.append(f"{sl.name} {sc['id']}: asset {v['asset_id']} not cleared")
        if sc.get("on_screen_source") and sc["on_screen_source"] not in S: errors.append(f"{sl.name} {sc['id']}: unknown on-screen source")
for w in warnings: print("WARN ", w)
for e in errors: print("ERROR", e)
print(f"{len(errors)} errors, {len(warnings)} warnings"); sys.exit(1 if errors else 0)
