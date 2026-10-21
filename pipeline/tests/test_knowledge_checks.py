"""Tests for craft_check.py, visual_plan.py, edl.py and gates.py on a temp copy of the example project (stdlib + jsonschema)."""
import json, os, shutil, sys, tempfile, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent))
import craft_check, visual_plan, edl, gates

def fresh_copy():
    d = Path(tempfile.mkdtemp(prefix="kn_")) / "p"; shutil.copytree(HERE / "fixtures" / "example_project", d); return d
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def save(p, o): p.write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")
def wjsonl(p, rows): p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
n = 0
def ok(cond, msg):
    global n; assert cond, msg; n += 1

# --- craft_check
P = fresh_copy(); sl = P / "shotlist.cs.json"
E, W, M = craft_check.check(P, "cs")
ok(M["časy"] == "změřené z audia", M)
base_errors = list(E)
d = load(sl); d["scenes"][3]["narration"] += " Pojďme se podívat, co bylo dál."; save(sl, d)
E, W, M = craft_check.check(P, "cs"); ok(any("zakázané fráze" in e for e in E), E)
d = load(sl); d["scenes"][4]["narration"] = "Za 3 dny přišlo 5 lidí."; d["scenes"][4].pop("narration_tts", None); save(sl, d)
E, W, M = craft_check.check(P, "cs"); ok(any("SC005: číslice bez narration_tts" in e for e in E), E)
d = load(sl)
for sc in d["scenes"]: sc["narration"] = sc["narration"].replace("?", "."); sc.pop("beats", None)
save(sl, d); E, W, M = craft_check.check(P, "cs"); ok(any("otevřená otázka" in e for e in E), E)
d["scenes"][1]["beats"] = ["question"]; save(sl, d); E, W, M = craft_check.check(P, "cs")
ok(not any("otevřená otázka" in e for e in E), "beats question counts as the open question")
shutil.rmtree(P / "audio"); E, W, M = craft_check.check(P, "cs"); ok(M["časy"] == "odhad z počtu slov", M)

# --- visual_plan
P = fresh_copy(); sl = load(P / "shotlist.cs.json")
E, W, M, rows = visual_plan.check(P, "cs"); ok(any("visual_sources.jsonl" in e for e in E) and any("visual_plan.cs.json" in e for e in E), E)
sl["scenes"][0]["visuals"][0]["asset_id"] = "A201"; save(P / "shotlist.cs.json", sl)
asset = {"id": "A201", "kind": "photo", "origin": "cc", "file": "assets/photos/x.jpg", "license": "CC-BY-2.0", "author": "Jan Novák", "risk": "low", "status": "cleared"}
wjsonl(P / "assets.jsonl", [asset])
V1 = {"id": "V001", "kind": "photo", "title": "Foto z místa", "original_url": "https://commons.wikimedia.org/x", "accessed_at": "2026-10-21",
      "found_via": "commons: místo 2005", "authenticity_rank": 4, "rights_category": "B", "rights_basis": "CC BY 2.0", "status": "used",
      "proposed_scenes": ["SC001"], "function": "shows_event", "asset_id": "A201"}
wjsonl(P / "visual_sources.jsonl", [V1])
plan = {"scenes": [{"id": s["id"], "purpose": "test", "visual_type": "foto", "sources": ["V001"] if s["id"] == "SC001" else [], "status": "verified",
                    "searches": ["a", "b", "c"]} for s in sl["scenes"]]}
save(P / "visual_plan.cs.json", plan)
E, W, M, rows = visual_plan.check(P, "cs"); ok(E == [], E)
V1b = dict(V1, rights_category="E"); wjsonl(P / "visual_sources.jsonl", [V1b])
E, W, M, rows = visual_plan.check(P, "cs"); ok(any("kategorie E" in e for e in E), E)
V1c = dict(V1, rights_category="D", max_range=None); wjsonl(P / "visual_sources.jsonl", [V1c])
E, W, M, rows = visual_plan.check(P, "cs"); ok(any("kategorie D" in e and "human_review" in e and "max_range" in e for e in E), E)
V1d = dict(V1c, max_range="0:01–0:04", human_review={"by": "Mira", "at": "2026-10-21", "decision": "citace § 31"}); wjsonl(P / "visual_sources.jsonl", [V1d])
E, W, M, rows = visual_plan.check(P, "cs"); ok(E == [], E)
wjsonl(P / "visual_sources.jsonl", [dict(V1, asset_id=None, status="candidate")])
E, W, M, rows = visual_plan.check(P, "cs"); ok(any("A201: použitý cizí materiál bez záznamu" in e for e in E), E)
plan["scenes"][0]["status"] = "research"; plan["scenes"][0]["sources"] = []; plan["scenes"][0]["searches"] = []; save(P / "visual_plan.cs.json", plan)
wjsonl(P / "visual_sources.jsonl", [V1])
E, W, M, rows = visual_plan.check(P, "cs"); ok(any("SC001: klíčová scéna bez autentického" in w for w in W) and any("research" in w for w in W), W)
out = visual_plan.report(P, "cs", E, W, M, rows); ok("| SC001 |" in out.read_text(encoding="utf-8"), "table row")

# --- edl
P = fresh_copy(); out, doc = edl.build(P, "cs")
ok(doc["times"] == "measured" and doc["shots"][0]["scene"] == "SC001" and (P / "render" / "edl.cs.csv").exists(), doc["shots"][0])
ok(abs(sum(s["dur_s"] for s in doc["shots"]) - doc["duration_s"]) < 0.1, "shots cover the whole video")
ok(edl.fresh(P, "cs"), "fresh after build")
d = load(P / "shotlist.cs.json"); d["scenes"][0]["narration"] += " Změna."; save(P / "shotlist.cs.json", d); ok(not edl.fresh(P, "cs"), "stale after edit")

# --- gates
P = fresh_copy(); (P / "render").mkdir(exist_ok=True)
F, _ = gates.q5(P, "cs"); ok(any("EDL" in f for f in F) and any("náhled" in f for f in F), F)
edl.build(P, "cs"); prev = P / "render" / "preview.cs.mp4"; prev.write_bytes(b"x")
F, _ = gates.q5(P, "cs"); ok(any("nikdo neprohlédl" in f for f in F), F)
time.sleep(0.05); (P / "review").mkdir(exist_ok=True); (P / "review" / "preview_cs.md").write_text("prohlédnuto", encoding="utf-8")
F, _ = gates.q5(P, "cs"); ok(F == [], F)
pub = P / "publish" / "cs"; pub.mkdir(parents=True)
(pub / "titles_thumbnails.md").write_text("# Názvy\n1. A\n2. B\n3. C\n# Náhledy\nA. x\nB. y\nC. z\n", encoding="utf-8")
(pub / "description.txt").write_text("Popis\n\n0:00 Začátek\n0:05 Druhá\n1:00 Třetí\n", encoding="utf-8")
(pub / "credits.txt").write_text("nic", encoding="utf-8")
F, _ = gates.q7(P, "cs"); ok(any("kapitoly" in f for f in F), F)
(pub / "description.txt").write_text("Popis\n\n0:00 Začátek\n0:15 Druhá\n1:00 Třetí\n", encoding="utf-8")
F, _ = gates.q7(P, "cs"); ok(not any("kapitoly" in f for f in F) and not any("názvy" in f for f in F), F)
doc = gates.run(P, "cs", "Q2"); ok(set(doc["quality"]) == {"Q1", "Q2"} and (P / "quality_gates.cs.json").exists(), doc)
print(f"ok: {n} knowledge-check cases pass")
