"""Visual research manifest + per-scene visual plan (knowledge/12): validate, cross-check, render a table.
Inputs:  visual_sources.jsonl (V001… every found item), visual_plan.<lang>.json (one entry per scene),
         shotlist.<lang>.json, assets.jsonl.
Output:  visual_plan.<lang>.md.  Usage: python3 visual_plan.py <project> [--lang cs]   (exit 1 on ERROR)"""
import argparse, json, sys
from pathlib import Path

SCHEMAS = Path(__file__).resolve().parent / "schemas"
OWN_ORIGINS = {"own", "generated"}
KEY_ACTS = {"hook", "turn", "payoff"}

def jsonl(p): return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []

def schema_errors(objs, name):
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return []
    v = Draft202012Validator(json.loads((SCHEMAS / name).read_text()))
    return [f"{o.get('id', '?')}: {e.message}" for o in objs for e in v.iter_errors(o)]

def check(proj, lang):
    proj = Path(proj); E, W, M = [], [], {}
    sl = json.loads((proj / f"shotlist.{lang}.json").read_text(encoding="utf-8"))
    vs = jsonl(proj / "visual_sources.jsonl"); V = {v["id"]: v for v in vs}
    assets = {a["id"]: a for a in jsonl(proj / "assets.jsonl")}
    pf = proj / f"visual_plan.{lang}.json"
    plan = json.loads(pf.read_text(encoding="utf-8")) if pf.exists() else None
    if not vs: E.append("chybí visual_sources.jsonl – vizuální rešerše není zapsaná (12 § 1)")
    if plan is None: E.append(f"chybí visual_plan.{lang}.json – povinný vizuální plán scén (12 § 7)")
    E += [f"visual_sources {e}" for e in schema_errors(vs, "visual_source.schema.json")]
    if plan: E += [f"visual_plan {e}" for e in schema_errors([plan], "visual_plan.schema.json")]
    by_asset = {v["asset_id"]: v for v in vs if v.get("asset_id")}

    # assets actually used in the shot list
    used_assets = {v["asset_id"]: sc["id"] for sc in sl["scenes"] for v in sc["visuals"] if v.get("asset_id")}
    used_v = {}
    for aid, scid in used_assets.items():
        a = assets.get(aid)
        if a and a.get("realistic_depiction_of_real_person"): E.append(f"{scid} {aid}: realistická AI podoba skutečné osoby (10)")
        if a and a.get("kind") in ("ai_image", "ai_video"): W.append(f"{scid} {aid}: AI obraz – existuje skutečný materiál místa/události? (12 § 2)")
        if aid in by_asset: used_v[by_asset[aid]["id"]] = scid
        elif a and a.get("origin") not in OWN_ORIGINS and a.get("kind") not in ("music", "sfx", "voice", "font"):
            E.append(f"{scid} {aid}: použitý cizí materiál bez záznamu ve visual_sources.jsonl (12 § 6)")
    for v in vs:
        if v.get("status") in ("used", "approved"): used_v.setdefault(v["id"], ",".join(v.get("proposed_scenes", [])) or "?")
    for vid, scid in used_v.items():
        v = V[vid]; cat = v.get("rights_category")
        if cat in ("E", "F"): E.append(f"{scid} {vid}: použitý materiál kategorie {cat} – nesmí do videa (12 § 3)")
        if cat == "D":
            miss = [k for k in ("function", "max_range") if not v.get(k)]
            if not (v.get("human_review") or {}).get("by"): miss.append("human_review")
            if miss: E.append(f"{scid} {vid}: kategorie D (zákonná výjimka) bez {', '.join(miss)} (12 § 3–4)")
        if not v.get("function"): W.append(f"{scid} {vid}: převzatý záběr bez dramaturgické funkce (12 § 4)")
    needs_human = [v["id"] for v in vs if v.get("status") == "needs_human"]
    if needs_human: W.append(f"čeká na lidské posouzení práv: {', '.join(needs_human)}")
    M["nalezené zdroje"] = f"{len(vs)} (použité {len(used_v)}, zamítnuté {sum(v.get('status') == 'rejected' for v in vs)}, k posouzení {len(needs_human)})"
    cats = {}
    for v in vs: cats[v.get("rights_category")] = cats.get(v.get("rights_category"), 0) + 1
    M["právní kategorie"] = ", ".join(f"{k}: {n}" for k, n in sorted(cats.items(), key=lambda x: str(x[0])))

    # per-scene plan
    rows = []
    P = {s["id"]: s for s in (plan or {}).get("scenes", [])}
    for vid_list in P.values():
        for vid in vid_list.get("sources", []):
            if vid not in V: E.append(f"{vid_list['id']}: neznámý zdroj {vid} ve vizuálním plánu")
    authentic = 0
    for sc in sl["scenes"]:
        p = P.get(sc["id"]); key = sc.get("act") in KEY_ACTS or bool(sc.get("claim_ids"))
        if plan is not None and not p: W.append(f"{sc['id']}: chybí ve vizuálním plánu"); continue
        if not p: continue
        srcs = [V[x] for x in p.get("sources", []) if x in V]
        auth = [v for v in srcs if (v.get("authenticity_rank") or 6) <= 5 and v.get("status") != "rejected"]
        authentic += bool(auth)
        if key and not auth and len(p.get("searches", [])) < 3:
            W.append(f"{sc['id']}: klíčová scéna bez autentického materiálu a s méně než 3 zapsanými postupy hledání (12 § 1)")
        if key and p.get("status") == "research": W.append(f"{sc['id']}: klíčová scéna je stále ve stavu research (12 § 7)")
        recon = any(v.get("kind") == "reconstruction" for v in srcs) or "rekonstr" in p.get("visual_type", "").lower()
        if recon and sc.get("claim_ids") and not p.get("reconstruction_label"):
            W.append(f"{sc['id']}: rekonstrukce skutečné události bez popisku v obraze (00, 12 § 5)")
        rows.append((sc, p, srcs))
    if P: M["scény s autentickým materiálem"] = f"{authentic}/{len(sl['scenes'])}"
    return E, W, M, rows

def esc(x): return str(x or "").replace("|", "/").replace("\n", " ")

def report(proj, lang, E, W, M, rows):
    out = Path(proj) / f"visual_plan.{lang}.md"
    L = [f"# Vizuální plán – {Path(proj).name} ({lang})", "", "Pravidla: `knowledge/12_vizualni_reserse_a_prava.md`", "",
         "## Souhrn", *[f"- {k}: {v}" for k, v in M.items()], "", f"## ERROR ({len(E)})", *[f"- {e}" for e in E], "",
         f"## WARN ({len(W)})", *[f"- {w}" for w in W], "", "## Scény", "",
         "| Scéna | Účel | Voiceover | Typ vizuálu | Autentické materiály | Odkazy | Práva | Rozsah | Střih a grafika | Alternativa | Stav |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for sc, p, srcs in rows:
        mats = "; ".join(f"{v['id']} {esc(v.get('title'))[:40]} (r{v.get('authenticity_rank', '?')})" for v in srcs)
        links = " ".join(f"[{v['id']}]({v['original_url']})" for v in srcs)
        rights = esc(p.get("rights")) or "; ".join(f"{v['id']}:{v.get('rights_category')}" for v in srcs)
        rng = "; ".join(f"{v['id']} {esc(v.get('max_range'))}" for v in srcs if v.get("max_range"))
        edit = esc(" · ".join(x for x in (p.get("planned_edit"), p.get("graphics"), p.get("reconstruction_label")) if x))
        L.append(f"| {sc['id']} | {esc(p.get('purpose'))} | {esc(p.get('voiceover') or sc['narration'])[:120]} | {esc(p.get('visual_type'))} | "
                 f"{mats} | {links} | {rights} | {rng} | {edit} | {esc(p.get('alternative'))} | {p.get('status')} |")
    out.write_text("\n".join(L) + "\n", encoding="utf-8"); return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--lang", default="cs"); ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(); E, W, M, rows = check(a.project, a.lang); out = report(a.project, a.lang, E, W, M, rows)
    if not a.quiet:
        for k, v in M.items(): print(f"  {k}: {v}")
        for e in E: print("ERROR", e)
        for w in W: print("WARN ", w)
    print(f"{out.name}: {len(E)} ERROR, {len(W)} WARN"); sys.exit(1 if E else 0)

if __name__ == "__main__":
    main()
