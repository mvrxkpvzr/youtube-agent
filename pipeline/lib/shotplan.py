"""Shot timing without rendering (stdlib only): scene times from audio/<lang>/timings.json, or estimated from word
count when there is no audio yet. Visual weights follow lib/render.plan (duration_s as relative weight)."""
import json, re
from pathlib import Path

def jsonl(p):
    p = Path(p)
    return {o["id"]: o for o in (json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip())} if p.exists() else {}

def words(text): return re.findall(r"\w+", text)

def scene_times(proj, lang, sl, wpm):
    """[(scene, start, end)] and whether the times are measured (True) or estimated (False)."""
    tf = Path(proj) / "audio" / lang / "timings.json"
    ids = [s["id"] for s in sl["scenes"]]
    if tf.exists():
        tm = {t["id"]: t for t in json.loads(tf.read_text())}
        if all(i in tm for i in ids):
            total = tm[ids[-1]]["end"] + 1.2; out = []
            for i, sc in enumerate(sl["scenes"]):
                start = 0.0 if i == 0 else tm[sc["id"]]["start"]
                end = tm[ids[i + 1]]["start"] if i + 1 < len(ids) else total
                out.append((sc, start, end, tm[sc["id"]]["start"], tm[sc["id"]]["end"]))
            return out, True
    gap = sl.get("pace", {}).get("scene_gap_s", 0.8); t = 0.5; out = []
    for sc in sl["scenes"]:
        d = len(words(sc.get("narration_tts") or sc["narration"])) / wpm * 60
        out.append((sc, t, t + d + gap, t, t + d)); t += d + gap
    return out, False

def shots(proj, lang, sl, wpm):
    times, measured = scene_times(proj, lang, sl, wpm); res = []
    for sc, start, end, vs, ve in times:
        weights = [v.get("duration_s", 1.0) for v in sc["visuals"]]; acc = start
        for v, w in zip(sc["visuals"], weights):
            d = (end - start) * w / sum(weights)
            res.append({"scene": sc["id"], "start": acc, "dur": d, "template": v["template"], "fx": v.get("fx", "none"),
                        "asset_id": v.get("asset_id"), "params": v.get("params", {})})
            acc += d
    return res, times, measured
