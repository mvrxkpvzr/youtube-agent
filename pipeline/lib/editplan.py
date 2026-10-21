"""Edit plan: the interchange between the pipeline and an editor (render/editplan.<lang>.json, schemas/editplan.schema.json).
Clips are grouped by scene with scene-relative times, so one scene can be re-cut or replaced without touching the others;
`resolve` lays the scenes end to end into the absolute timeline the editor host (pipeline/artcraft) builds.
Who makes what: FFmpeg / fx3d / Blender render every shot (render.render_shots), mix.py the music + SFX bed (bed.wav),
the editor assembles shots, per-scene narration, the bed, transitions and optional burned-in titles, then exports."""
import json, re
from pathlib import Path
from .common import ffmpeg, load_shotlist, run, sha

TRANSITIONS = ("cut", "fade", "fadeblack")  # fade = crossfade (ffmpeg xfade "fade"), fadeblack = through black

def duration(path):
    r = run([ffmpeg(), "-hide_banner", "-i", str(path), "-f", "null", "-t", "0", "-"])
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr).groups()
    return round(int(h) * 3600 + int(m) * 60 + float(s), 3)

def srt_cues(path):
    def t(x): h, m, r = x.split(":"); s, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    out = []
    for blk in Path(path).read_text(encoding="utf-8").strip().split("\n\n"):
        lines = blk.split("\n"); a, b = lines[1].split(" --> "); out.append((t(a), t(b), "\n".join(lines[2:])))
    return out

class Media:
    def __init__(self, proj): self.proj, self.items, self.by_path = proj, {}, {}
    def add(self, path, kind, **extra):
        rel = str(Path(path).resolve().relative_to(self.proj))
        if rel not in self.by_path:
            mid = f"M{len(self.items) + 1:03d}"; self.by_path[rel] = mid
            self.items[mid] = {"path": rel, "kind": kind, "duration_s": None if kind == "image" else duration(path),
                               "sha256": sha(Path(path)), **extra}
        return self.by_path[rel]

def build(proj, lang, preview=True, burn_subtitles=False, codec="vp9"):
    """Render the shots, then write render/editplan.<lang>.json from them, the scene timings and the bed."""
    from . import render as R
    proj = Path(proj); sl = load_shotlist(proj, lang); d = proj / "audio" / lang
    shots, clips, total, X, transition = R.render_shots(proj, lang, preview, codec)
    if transition not in TRANSITIONS: transition = "fade"  # other xfade looks have no editor equivalent; closest is a crossfade
    tm = {t["id"]: t for t in json.loads((d / "timings.json").read_text())}
    voice = d / "narration.proc.wav" if (d / "narration.proc.wav").exists() else d / "narration.wav"
    media = Media(proj); scenes, t0 = [], 0.0
    for s, (clip, dur) in zip(shots, clips):
        if not scenes or scenes[-1]["id"] != s["scene"]:
            scenes.append({"id": s["scene"], "start_s": round(t0, 3), "video": [], "audio": [], "text": []})
        sc = scenes[-1]
        sc["video"].append({"media": media.add(clip, "video", made_by=f"render.{s['template']}" + (f"+{s['fx']}" if s["fx"] != "none" else "")),
                            "at_s": round(t0 - sc["start_s"], 3), "dur_s": round(dur, 3), "in_s": 0.0, "fit": "cover",
                            "template": s["template"]})
        t0 += dur
    for i, sc in enumerate(scenes):
        sc["dur_s"] = round((scenes[i + 1]["start_s"] if i + 1 < len(scenes) else total) - sc["start_s"], 3)
        t = tm[sc["id"]]; at = t["start"] - sc["start_s"]
        sc["audio"].append({"media": media.add(voice, "audio"), "role": "narration", "at_s": round(at, 3), "in_s": t["start"],
                            "dur_s": round(min(t["end"] - t["start"] + 0.05, sc["dur_s"] - at), 3), "gain_db": 0.0})
        del sc["start_s"]
    bed = []
    if (d / "bed.wav").exists():
        bed.append({"media": media.add(d / "bed.wav", "audio"), "role": "bed", "at_s": 0.0, "in_s": 0.0,
                    "dur_s": round(min(total, duration(d / "bed.wav")), 3), "gain_db": 0.0})
    srt = proj / "render" / f"subtitles.{lang}.srt"
    if burn_subtitles and srt.exists():
        starts = [0.0]
        for sc in scenes: starts.append(starts[-1] + sc["dur_s"])
        for a, b, txt in srt_cues(srt):
            k = max(i for i in range(len(scenes)) if starts[i] <= a + 0.05)  # a cue a few ms early belongs to the next scene
            scenes[k]["text"].append({"content": txt, "style": "subtitle", "at_s": round(a - starts[k], 3), "dur_s": round(b - a, 3)})
    plan = {"version": 1, "project": proj.name, "language": lang, "fps": sl["fps"], "resolution": sl.get("resolution", "1920x1080"),
            "duration_s": round(total, 3), "transition": {"type": transition, "dur_s": X}, "media": media.items,
            "scenes": scenes, "global_audio": bed,
            "inputs_sha256": {k: sha(proj / k) for k in (f"shotlist.{lang}.json", f"audio/{lang}/timings.json") if (proj / k).exists()},
            "export": {"engine": "artcraft", "format": "webm", "quality": "high" if not preview else "medium"}}
    edl = proj / "render" / f"edl.{lang}.json"
    if edl.exists():  # the EDL (pipeline/edl.py) describes the same shots; refuse a plan that disagrees with it
        rows = json.loads(edl.read_text(encoding="utf-8"))["shots"]
        if len(rows) != len(shots) or any(r["scene"] != s["scene"] for r, s in zip(rows, shots)):
            raise SystemExit(f"editplan: EDL {edl.name} má {len(rows)} záběrů, render {len(shots)} – přegeneruj EDL (edl.py)")
        plan["inputs_sha256"][f"render/edl.{lang}.json"] = sha(edl)
    out = proj / "render" / f"editplan.{lang}.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    return out, plan

def check(plan):
    """Plan consistency (beyond the JSON schema): references, in-points inside the media, clips inside their scene."""
    import jsonschema
    schema = json.loads((Path(__file__).resolve().parents[1] / "schemas" / "editplan.schema.json").read_text())
    errs = [f"schema: {'/'.join(map(str, e.path))}: {e.message}" for e in jsonschema.Draft202012Validator(schema).iter_errors(plan)]
    for sc in plan["scenes"]:
        for kind in ("video", "audio", "text"):
            for c in sc.get(kind, []):
                tag = f"{sc['id']} {kind} {c.get('media', c.get('content', ''))[:20]}"
                if c["dur_s"] <= 0: errs.append(f"{tag}: délka {c['dur_s']}")
                end_ok = kind == "text" or c["at_s"] + c["dur_s"] <= sc["dur_s"] + 1e-3  # a subtitle may run into the next scene
                if c["at_s"] < -0.05 or not end_ok: errs.append(f"{tag}: mimo scénu ({c['at_s']}+{c['dur_s']} > {sc['dur_s']})")
                if kind == "text": continue
                m = plan["media"].get(c["media"])
                if not m: errs.append(f"{tag}: neznámé médium"); continue
                if m["duration_s"] is not None and c.get("in_s", 0) + c["dur_s"] > m["duration_s"] + 0.05:
                    errs.append(f"{tag}: {c.get('in_s', 0)}+{c['dur_s']} s přesahuje médium ({m['duration_s']} s)")
    total = sum(sc["dur_s"] for sc in plan["scenes"])
    if abs(total - plan["duration_s"]) > 0.05: errs.append(f"součet scén {total:.3f} s ≠ duration_s {plan['duration_s']}")
    return errs

def resolve(plan, proj):
    """Absolute timeline for the editor host. Transitions become editor operations:
    fade = the later clip lies on the other video track and fades in over the earlier clip's tail (exactly ffmpeg xfade);
    fadeblack = out to black and in from black around the cut; cut = nothing."""
    proj = Path(proj); w, h = map(int, plan["resolution"].split("x")); tr = plan.get("transition", {"type": "cut", "dur_s": 0})
    video, audio, text, t0 = [], [], [], 0.0
    for sc in plan["scenes"]:
        for c in sc["video"]: video.append({**c, "scene": sc["id"], "start_s": t0 + c["at_s"]})
        for c in sc["audio"]: audio.append({**c, "scene": sc["id"], "start_s": t0 + c["at_s"]})
        for c in sc.get("text", []): text.append({**c, "scene": sc["id"], "start_s": t0 + c["at_s"]})
        t0 += sc["dur_s"]
    audio += [{**c, "scene": None, "start_s": c["at_s"]} for c in plan.get("global_audio", [])]
    video.sort(key=lambda c: c["start_s"])
    for k, c in enumerate(video):
        t = c.get("transition_in", tr) if k else {"type": "cut", "dur_s": 0}
        typ, X = t["type"], t.get("dur_s", 0)
        prev = video[k - 1] if k else None
        if typ == "fade" and prev and X > 0:
            prev["tail_s"] = X; c["fade_in_s"] = X
        elif typ == "fadeblack" and prev and X > 0:
            prev["fade_out_s"] = X / 2; c["fade_in_s"] = X / 2
    layer = 0
    for k, c in enumerate(video):  # crossfaded clips alternate between the two video tracks
        if k and video[k - 1].get("tail_s"): layer = 1 - layer
        c["layer"] = layer
    out = []
    for c in video:
        o = {"media": c["media"], "start_s": round(c["start_s"], 4), "dur_s": round(c["dur_s"] + c.get("tail_s", 0), 4),
             "in_s": c.get("in_s", 0.0), "fit": c.get("fit", "cover"), "layer": c["layer"], "scene": c["scene"]}
        for k in ("fade_in_s", "fade_out_s", "zoom_from", "zoom_to"):
            if c.get(k): o[k] = c[k]
        out.append(o)
    aud = [{"media": c["media"], "start_s": round(c["start_s"], 4), "dur_s": c["dur_s"], "in_s": c.get("in_s", 0.0),
            "gain_db": c.get("gain_db", 0.0), "role": c.get("role", ""), "scene": c["scene"],
            **({k: c[k] for k in ("fade_in_s", "fade_out_s") if c.get(k)})} for c in audio]
    txt = [{"content": c["content"], "start_s": round(c["start_s"], 4), "dur_s": c["dur_s"], "style": c.get("style", "subtitle"),
            "scene": c["scene"], **({k: c[k] for k in ("fade_in_s", "fade_out_s") if c.get(k)})} for c in text]
    ex = plan.get("export", {})
    return {"fps": plan["fps"], "width": w, "height": h, "duration_s": plan["duration_s"], "background": plan.get("background", "#000000"),
            "format": ex.get("format", "webm"), "quality": ex.get("quality", "high"),
            "filename": f"{plan['project']}.{plan['language']}.{ex.get('format', 'webm')}",
            "media": [{"id": k, "path": str(proj / m["path"]), "kind": m["kind"]} for k, m in plan["media"].items()],
            "video": out, "audio": aud, "text": txt}
