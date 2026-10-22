#!/usr/bin/env python3
"""Search and validate the competitor reference library.

  python3 search.py "cold open"                    # full-text over videos, observations, techniques
  python3 search.py --category hook --kind observation
  python3 search.py --channel fern --technique TQ-03
  python3 search.py --check                        # validate ids, references, timestamps, confidence
"""
import argparse, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA = HERE.parents[2] / "pipeline" / "schemas" / "reference_observation.schema.json"


def load_jsonl(p):
    rows = []
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                sys.exit(f"{p.name}:{n}: invalid JSON: {e}")
    return rows


def load_techniques():
    out = {}
    for block in re.split(r"^### ", (HERE / "techniques.md").read_text(encoding="utf-8"), flags=re.M)[1:]:
        m = re.match(r"(TQ-\d{2})\s+(.+)", block)
        if m:
            out[m.group(1)] = {"id": m.group(1), "name": m.group(2).strip(), "body": block}
    return out


def fmt_t(t):
    return "--:--" if t is None else f"{int(t)//60}:{int(t)%60:02d}"


def check(videos, obs, tq):
    errs = []
    schema = json.loads(SCHEMA.read_text())
    allowed = set(schema["properties"])
    cats = set(schema["properties"]["category"]["enum"])
    vids = {v["id"]: v for v in videos}
    if len(vids) != len(videos):
        errs.append("duplicate video ids")
    for v in videos:
        for k in ("id", "channel", "title", "url", "published", "runtime_s", "topic", "narrative_question", "analysed_via", "confidence"):
            if v.get(k) in (None, ""):
                errs.append(f"{v.get('id')}: missing {k}")
        if not str(v.get("url", "")).startswith("https://www.youtube.com/watch?v="):
            errs.append(f"{v['id']}: url must be a youtube watch url")
        for t in v.get("techniques", []):
            if t not in tq:
                errs.append(f"{v['id']}: unknown technique {t}")
    seen = set()
    for o in obs:
        oid = o.get("id")
        if oid in seen:
            errs.append(f"{oid}: duplicate")
        seen.add(oid)
        for k in schema["required"]:
            if k not in o:
                errs.append(f"{oid}: missing {k}")
        for k in o:
            if k not in allowed:
                errs.append(f"{oid}: unknown field {k}")
        if o.get("video") not in vids:
            errs.append(f"{oid}: unknown video {o.get('video')}")
        else:
            rt = vids[o["video"]]["runtime_s"]
            for k in ("t_start", "t_end"):
                if o.get(k) is not None and o[k] > rt + 1:
                    errs.append(f"{oid}: {k} beyond runtime")
        if o.get("t_start") is not None and o.get("t_end") is not None and o["t_end"] < o["t_start"]:
            errs.append(f"{oid}: t_end < t_start")
        if o.get("category") not in cats:
            errs.append(f"{oid}: bad category")
        if o.get("kind") not in ("observation", "interpretation"):
            errs.append(f"{oid}: bad kind")
        if o.get("confidence") not in ("high", "medium", "low"):
            errs.append(f"{oid}: bad confidence")
        if o.get("quote") and len(o["quote"].split()) > 15:
            errs.append(f"{oid}: quote longer than 15 words")
        for t in o.get("techniques", []):
            if t not in tq:
                errs.append(f"{oid}: unknown technique {t}")
    oids = {o.get("id") for o in obs}
    for t in tq.values():
        for ref in sorted(set(re.findall(r"\bO\d{4}\b", t["body"]))):
            if ref not in oids:
                errs.append(f"{t['id']}: cites unknown observation {ref}")
    per_video = {}
    for o in obs:
        per_video.setdefault(o.get("video"), set()).add(o.get("kind"))
    for vid in vids:
        if per_video.get(vid) != {"observation", "interpretation"}:
            errs.append(f"{vid}: needs at least one observation and one interpretation")
    channels = {v["channel"] for v in videos}
    print(f"{len(channels)} channels, {len(videos)} videos, {len(obs)} observations, {len(tq)} techniques")
    for e in errs:
        print("ERROR", e)
    return 1 if errs else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--channel")
    ap.add_argument("--category")
    ap.add_argument("--kind", choices=["observation", "interpretation"])
    ap.add_argument("--technique")
    ap.add_argument("--confidence", choices=["high", "medium", "low"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    videos = load_jsonl(HERE / "videos.jsonl")
    obs = load_jsonl(HERE / "observations.jsonl")
    tq = load_techniques()
    if a.check:
        sys.exit(check(videos, obs, tq))
    vids = {v["id"]: v for v in videos}
    q = a.query.lower()
    if a.technique and a.technique in tq and not (a.channel or a.category or q):
        print(tq[a.technique]["body"].strip(), "\n")
    for o in obs:
        v = vids.get(o["video"], {})
        hay = " ".join([o["text"], o.get("quote") or "", v.get("title", ""), v.get("channel", "")]).lower()
        if q and q not in hay:
            continue
        if a.channel and a.channel.lower() not in v.get("channel", "").lower():
            continue
        if a.category and o["category"] != a.category:
            continue
        if a.kind and o["kind"] != a.kind:
            continue
        if a.confidence and o["confidence"] != a.confidence:
            continue
        if a.technique and a.technique not in o.get("techniques", []):
            continue
        t = int(o["t_start"]) if o.get("t_start") is not None else None
        link = v.get("url", "") + (f"&t={t}s" if t is not None else "")
        print(f"[{o['id']}] {v.get('channel')} · {v.get('title')} @{fmt_t(o.get('t_start'))}  ({o['category']}, {o['kind']}, {o['confidence']})")
        print(f"   {o['text']}")
        print(f"   {link}")


if __name__ == "__main__":
    main()
