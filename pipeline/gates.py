"""Quality gates Q1–Q7 (module 4.0 § G), checked from the project files, not from promises.
  Q1 research supported · Q2 story and script · Q3 storyboard/visual plan · Q4 voice, pronunciation, subtitles, timings
  Q5 low-cost full-length preview reviewed (+ fresh EDL) · Q6 final passed technical/editorial/factual/audio/rights checks
  Q7 publication assets + source/licence manifest
Human approvals G1–G5 (gates.json) are reported next to them; they are Mira's, never set by this script.
Usage: python3 gates.py <project> [--lang cs] [--upto Q5]   -> quality_gates.<lang>.json; exit 1 if a checked gate fails.
vid.py render --final runs this with --upto Q5 and refuses to render when a gate fails."""
import argparse, json, re, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import craft_check, visual_plan, edl

ORDER = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
NAMES = {"Q1": "rešerše je dostatečně podložená", "Q2": "příběh a scénář mají jasný hlavní argument",
         "Q3": "storyboard má proveditelné vizuální řešení každé důležité scény", "Q4": "hlas, výslovnost, titulky a časování zkontrolované",
         "Q5": "levný celovečerní náhled prohlédnutý před drahým renderem", "Q6": "finál prošel technickou, redakční, faktickou, zvukovou a právní kontrolou",
         "Q7": "publikační podklady a manifest zdrojů a licencí jsou připravené"}

def mtime(p): return p.stat().st_mtime if p.exists() else 0
def jsonl(p): return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []

def q1(proj, lang):
    F, W = [], []
    r = subprocess.run([sys.executable, str(Path(__file__).parent / "validate.py"), str(proj)], capture_output=True, text=True)
    if r.returncode != 0: F.append("validate.py: " + (r.stdout.strip().splitlines() or ["chyba"])[-1])
    claims = jsonl(proj / "claims.jsonl")
    if not claims: F.append("claims.jsonl je prázdný – chybí databáze tvrzení")
    used = {c for sl in proj.glob("shotlist.*.json") for sc in json.loads(sl.read_text(encoding="utf-8"))["scenes"] for c in sc.get("claim_ids", [])}
    noloc = [c["id"] for c in claims if c["id"] in used and not any(e.get("locator") for e in c["evidence"])]
    if noloc: F.append(f"použitá tvrzení bez citace/strany/času ve zdroji: {', '.join(noloc[:10])}")
    brief = proj / "brief.md"
    if not brief.exists(): W.append("chybí brief.md (téma a úhel)")
    elif not re.search(r"skóre|score", brief.read_text(encoding="utf-8"), re.I): W.append("brief.md nemá skóre tématu 0–10 (knowledge/01)")
    return F, W

def q2(proj, lang):
    E, W, M = craft_check.check(proj, lang); craft_check.report(proj, lang, E, W, M)
    return [f"craft_check: {e}" for e in E], ([f"craft_check: {len(W)} WARN (craft_report.{lang}.md)"] if W else [])

def q3(proj, lang):
    E, W, M, rows = visual_plan.check(proj, lang); visual_plan.report(proj, lang, E, W, M, rows)
    F = [f"visual_plan: {e}" for e in E] + [f"visual_plan: {w}" for w in W if "stále ve stavu research" in w]
    return F, ([f"visual_plan: {len(W)} WARN (visual_plan.{lang}.md)"] if W else [])

def q4(proj, lang):
    F, W = [], []; a = proj / "audio" / lang; tm = a / "timings.json"
    if not tm.exists(): return ["chybí audio/<lang>/timings.json – hlas nebyl spojen (vid.py audio)"], W
    rep = a / "asr_report.json"
    if not rep.exists(): F.append("chybí zpětný přepis (vid.py check)")
    else:
        errs = [f"{k}: {e}" for k, v in json.loads(rep.read_text(encoding="utf-8")).items() for e in v.get("errors", [])]
        if errs: F.append(f"zpětný přepis: {len(errs)} chyb, např. {errs[0]}")
        if mtime(rep) < max([mtime(p) for p in a.glob("SC*.wav")] or [0]): F.append("zpětný přepis je starší než hlas – spusť vid.py check")
    srt = proj / "render" / f"subtitles.{lang}.srt"
    if not srt.exists(): F.append("chybí titulky (vid.py subs)")
    elif mtime(srt) < mtime(tm): F.append("titulky jsou starší než časování – spusť vid.py subs")
    if not (proj / f"lexicon.{lang}.json").exists(): W.append(f"projekt nemá lexicon.{lang}.json – výslovnost jmen neověřená")
    return F, W

def q5(proj, lang):
    F, W = [], []
    if not edl.fresh(proj, lang): F.append("střihový list (EDL) chybí nebo neodpovídá shotlistu/časování – spusť vid.py edl")
    prev = proj / "render" / f"preview.{lang}.mp4"; note = proj / "review" / f"preview_{lang}.md"
    inputs = max(mtime(proj / f"shotlist.{lang}.json"), mtime(proj / "audio" / lang / "timings.json"))
    if not prev.exists(): F.append("chybí levný náhled celého videa (vid.py render bez --final)")
    elif mtime(prev) < inputs: F.append("náhled je starší než shotlist/časování – vyrenderuj nový")
    elif mtime(note) < mtime(prev): F.append(f"náhled nikdo neprohlédl: chybí review/preview_{lang}.md novější než náhled (zápis nálezů z kontaktního listu)")
    return F, W

def q6(proj, lang):
    F, W = [], []
    fin = proj / "render" / f"final.{lang}.mp4"; qa = proj / f"qa_report.{lang}.md"
    if not fin.exists(): return ["chybí finální video (vid.py render --final)"], W
    if mtime(qa) < mtime(fin): F.append("QA report chybí nebo je starší než finál – spusť vid.py qa --final")
    else:
        m = re.search(r"## ERROR \((\d+)\)", qa.read_text(encoding="utf-8"))
        if m and int(m[1]): F.append(f"qa_report: {m[1]} ERROR")
    for name, (f, w) in (("Q2", q2(proj, lang)), ("Q3", q3(proj, lang))):
        F += f
    if not list((proj / "review").glob("scorecard_v*.md")): F.append("chybí hodnocení verze 0–10 (review/scorecard_v<verze>.md, knowledge/00)")
    assets = {a["id"]: a for a in jsonl(proj / "assets.jsonl")}
    sl = json.loads((proj / f"shotlist.{lang}.json").read_text(encoding="utf-8"))
    music = [c.get("asset") for c in (sl.get("music") or {}).get("cues", {}).values() if c.get("asset")]
    for aid in music:
        a = assets.get(aid)
        if not a: F.append(f"hudba {aid}: není v assets.jsonl")
        elif a.get("status") != "cleared" or a.get("ai_generated"): F.append(f"hudba {aid}: není cleared nebo je AI (knowledge/09)")
        elif not a.get("attribution") and "CC-BY" in a.get("license", ""): F.append(f"hudba {aid}: CC BY bez znění atribuce")
    if not list((proj / "review").glob("hudba_*.md")): W.append("chybí kontrola hudby před exportem (review/hudba_v<verze>.md, knowledge/09 § 8)")
    return F, W

def q7(proj, lang):
    F, W = [], []; pub = proj / "publish" / lang
    tt = pub / "titles_thumbnails.md"
    if not tt.exists(): F.append("chybí publish/<lang>/titles_thumbnails.md")
    else:
        sec, n = "", {"t": 0, "n": 0}
        for line in tt.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"): sec = line.lower(); continue
            if re.match(r"\s*([0-9]|[A-C])[.)]\s+\S", line):
                if "náz" in sec or "title" in sec: n["t"] += 1
                elif "náhled" in sec or "thumb" in sec: n["n"] += 1
        if n["t"] < 3 or n["n"] < 3: F.append(f"potřeba ≥ 3 názvy a ≥ 3 koncepty náhledu (mám {n['t']} a {n['n']})")
    desc = pub / "description.txt"
    if not desc.exists(): F.append("chybí publish/<lang>/description.txt (popis + kapitoly)")
    else:
        stamps = re.findall(r"^\s*(\d{1,2}:\d{2}(?::\d{2})?)\s", desc.read_text(encoding="utf-8"), re.M)
        secs = [sum(int(x) * 60 ** i for i, x in enumerate(reversed(s.split(":")))) for s in stamps]
        if not secs or secs[0] != 0 or len(secs) < 3 or any(b - a < 10 for a, b in zip(secs, secs[1:])):
            F.append("kapitoly: první 0:00, aspoň 3, vzestupně, každá ≥ 10 s (knowledge/11)")
    cred = pub / "credits.txt"
    if not cred.exists(): F.append("chybí publish/<lang>/credits.txt")
    else:
        text = cred.read_text(encoding="utf-8")
        sl = json.loads((proj / f"shotlist.{lang}.json").read_text(encoding="utf-8"))
        used = {v.get("asset_id") for sc in sl["scenes"] for v in sc["visuals"]} | {c.get("asset") for c in (sl.get("music") or {}).get("cues", {}).values()}
        for a in jsonl(proj / "assets.jsonl"):
            if a["id"] in used and "BY" in a.get("license", "") and a.get("author") and a["author"].split()[-1] not in text:
                F.append(f"{a['id']}: licence {a['license']} vyžaduje atribuci, autor {a['author']} chybí v credits.txt")
    if not (proj / f"visual_plan.{lang}.md").exists(): F.append("chybí manifest zdrojů a licencí (visual_plan.<lang>.md)")
    return F, W

CHECKS = {"Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5, "Q6": q6, "Q7": q7}

def run(proj, lang, upto="Q7"):
    proj = Path(proj); res = {}
    for g in ORDER[: ORDER.index(upto) + 1]:
        F, W = CHECKS[g](proj, lang); res[g] = {"name": NAMES[g], "status": "fail" if F else "pass", "fail": F, "warn": W}
    human = json.loads((proj / "gates.json").read_text()) if (proj / "gates.json").exists() else {}
    doc = {"checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "language": lang, "quality": res,
           "human": {k: v.get("status") for k, v in human.items()}}
    (proj / f"quality_gates.{lang}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return doc

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--lang", default="cs"); ap.add_argument("--upto", default="Q7", choices=ORDER)
    a = ap.parse_args(); doc = run(a.project, a.lang, a.upto)
    for g, r in doc["quality"].items():
        print(f"{g} {'PASS' if r['status'] == 'pass' else 'FAIL'}  {r['name']}")
        for f in r["fail"]: print("   ✗", f)
        for w in r["warn"]: print("   !", w)
    print("lidské brány:", doc["human"] or "žádné zapsané")
    sys.exit(1 if any(r["status"] == "fail" for r in doc["quality"].values()) else 0)

if __name__ == "__main__":
    main()
