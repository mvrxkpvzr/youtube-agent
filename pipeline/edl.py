"""Edit decision list (EDL) before any expensive render (module 4.0 § E): every shot with its time, scene, template,
asset file, on-screen source, music cue and SFX. Portable: JSON for tools, CSV for any editor or a human.
Usage: python3 edl.py <project> [--lang cs]  ->  render/edl.<lang>.json + render/edl.<lang>.csv"""
import argparse, csv, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.shotplan import shots as plan_shots, jsonl

def inputs_hash(proj, lang):
    h = hashlib.sha256()
    for rel in (f"shotlist.{lang}.json", f"audio/{lang}/timings.json", "assets.jsonl"):
        p = Path(proj) / rel
        h.update(rel.encode() + (p.read_bytes() if p.exists() else b"-"))
    return h.hexdigest()

def build(proj, lang, wpm=153.6):
    proj = Path(proj); sl = json.loads((proj / f"shotlist.{lang}.json").read_text(encoding="utf-8"))
    assets = jsonl(proj / "assets.jsonl"); shots, times, measured = plan_shots(proj, lang, sl, wpm)
    scenes = {sc["id"]: sc for sc, *_ in times}
    rows, first = [], set()
    for i, s in enumerate(shots, 1):
        sc = scenes[s["scene"]]; a = assets.get(s["asset_id"] or "") or {}
        p = s["params"]; file = a.get("file") or p.get("file") or ""
        head = s["scene"] not in first; first.add(s["scene"])
        rows.append({"shot": i, "scene": s["scene"], "act": sc.get("act") or "", "start_s": round(s["start"], 2),
                     "end_s": round(s["start"] + s["dur"], 2), "dur_s": round(s["dur"], 2), "template": s["template"], "fx": s["fx"],
                     "asset_id": s["asset_id"] or "", "file": file, "license": a.get("license", ""),
                     "on_screen_source": sc.get("on_screen_source") or "",
                     "text": p.get("text") or p.get("value") or p.get("quote") or p.get("title") or "",
                     "narration": sc["narration"] if head else "", "music_cue": (sc.get("music_cue") or "") if head else "",
                     "sfx": " ".join(sc.get("sfx", [])) if head else "", "audio": f"audio/{lang}/{s['scene']}.wav" if head else ""})
    doc = {"project": proj.name, "language": lang, "times": "measured" if measured else "estimated",
           "inputs_sha256": inputs_hash(proj, lang), "duration_s": round(times[-1][2], 2), "shots": rows}
    out = proj / "render"; out.mkdir(exist_ok=True)
    (out / f"edl.{lang}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(out / f"edl.{lang}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return out / f"edl.{lang}.json", doc

def fresh(proj, lang):
    p = Path(proj) / "render" / f"edl.{lang}.json"
    return p.exists() and json.loads(p.read_text(encoding="utf-8")).get("inputs_sha256") == inputs_hash(proj, lang)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--lang", default="cs")
    a = ap.parse_args(); out, doc = build(a.project, a.lang)
    print(f"{out.name}: {len(doc['shots'])} záběrů, {doc['duration_s']:.1f} s, časy {doc['times']}")

if __name__ == "__main__":
    main()
