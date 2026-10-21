"""Export the cut of a rendered video as a portable timeline (OpenTimelineIO + CMX 3600 EDL) for Kdenlive, DaVinci
Resolve or Premiere: the local fallback when ArtCraft cannot do an edit, and a record of what the render actually cut.
  python -I pipeline/otio_export.py <project> --lang cs [--video render/final.cs.mp4]
Shots come from render/edl.<lang>.json when it exists (pipeline/edl.py), otherwise from lib.render.plan (shot list +
timings; shot k starts at the sum of the earlier shot lengths, exactly as the xfade chain places it).
  V1  each shot: its own clip render/work_<lang>/shotNNN.mp4 when the render kept it, else that shot's span of the video
  V2  (disabled) the original asset of photo and motion shots, so an editor can swap a shot back to its source
  A1  the video's mastered sound, whole length
  markers: one per scene (id + narration); every clip carries scene, template, asset, licence and on-screen text
Writes render/timeline.<lang>.otio, render/timeline.<lang>.edl and render/timeline.<lang>.check.json, then reads the
.otio back and checks it against the video (length within one frame, every referenced file present). Exit 1 if not."""
import argparse, json, subprocess, sys
from pathlib import Path
import opentimelineio as otio
sys.path.insert(0, str(Path(__file__).resolve().parent))

def probe_duration(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)

def shots_from_edl(edl):
    d = json.loads(edl.read_text(encoding="utf-8"))
    return [{"scene": s.get("scene"), "template": s.get("template"), "dur": float(s["dur_s"]), "asset_file": s.get("file"),
             "asset_id": s.get("asset_id"), "license": s.get("license"), "text": s.get("text"), "narration": s.get("narration"),
             "source": s.get("on_screen_source")} for s in d["shots"]], "edl"

def shots_from_plan(proj, lang):
    from lib.render import plan
    shots, _ = plan(proj, lang); out = []
    for s in shots:
        p = s["params"]; f = s["photo"] or (str(proj / p["file"]) if s["template"] == "motion" and p.get("file") else None)
        out.append({"scene": s["scene"], "template": s["template"], "dur": s["dur"], "asset_file": f, "asset_id": None,
                    "license": p.get("credit"), "text": p.get("text") or p.get("value") or p.get("quote"), "narration": None,
                    "source": s["source"]})
    return out, "plan"

def rt(sec, fps): return otio.opentime.RationalTime(round(sec * fps), fps)
def tr(start, dur, fps): return otio.opentime.TimeRange(rt(start, fps), rt(dur, fps))

def build(proj, lang, video):
    fps = 25.0; vdur = probe_duration(video)
    edl = proj / "render" / f"edl.{lang}.json"
    shots, origin = shots_from_edl(edl) if edl.exists() else shots_from_plan(proj, lang)
    sl = json.loads((proj / f"shotlist.{lang}.json").read_text(encoding="utf-8"))
    fps = float(sl.get("fps", fps)); narration = {sc["id"]: sc.get("narration", "") for sc in sl["scenes"]}
    tl = otio.schema.Timeline(name=f"{proj.name} ({lang})"); tl.global_start_time = rt(0, fps)
    tl.metadata["youtube_agent"] = {"project": proj.name, "lang": lang, "video": str(video), "shots_from": origin}
    v1 = otio.schema.Track(name="V1 render", kind=otio.schema.TrackKind.Video)
    v2 = otio.schema.Track(name="V2 originals (off)", kind=otio.schema.TrackKind.Video); v2.enabled = False
    a1 = otio.schema.Track(name="A1 master", kind=otio.schema.TrackKind.Audio)
    vref = lambda: otio.schema.ExternalReference(target_url=str(video), available_range=tr(0, vdur, fps))
    work = proj / "render" / f"work_{lang}"; pos = 0.0; last_scene = None; v2_gap = 0.0
    for i, s in enumerate(shots):
        own = work / f"shot{i:03}.mp4"
        f0, f1 = round(pos * fps), round((pos + s["dur"]) * fps)   # cumulative frame boundaries: no rounding drift over 100+ shots
        dur = (f1 - f0) / fps
        if own.exists(): ref, src = otio.schema.ExternalReference(target_url=str(own)), tr(0, dur, fps)
        else: ref, src = vref(), tr(f0 / fps, dur, fps)
        name = f"{s['scene']} #{i:03} {s['template']}"
        meta = {k: s[k] for k in ("scene", "template", "asset_id", "asset_file", "license", "text", "source") if s.get(k)}
        clip = otio.schema.Clip(name=name, media_reference=ref, source_range=src, metadata={"youtube_agent": meta})
        if s["scene"] != last_scene:
            m = otio.schema.Marker(name=s["scene"], marked_range=tr(0, 0, fps), metadata={"narration": s.get("narration") or narration.get(s["scene"], "")})
            clip.markers.append(m); last_scene = s["scene"]
        v1.append(clip)
        f = s.get("asset_file")
        if f and Path(f).exists():
            if v2_gap: v2.append(otio.schema.Gap(source_range=tr(0, v2_gap, fps))); v2_gap = 0.0
            v2.append(otio.schema.Clip(name=f"{name} (originál)", media_reference=otio.schema.ExternalReference(target_url=str(Path(f).resolve())),
                                       source_range=tr(0, dur, fps), metadata={"youtube_agent": meta}))
        else: v2_gap += dur
        pos += s["dur"]
    a1.append(otio.schema.Clip(name="master", media_reference=vref(), source_range=tr(0, vdur, fps)))
    tl.tracks.extend([v1, v2, a1])
    return tl, shots, origin, vdur, fps

def verify(path, video, vdur, fps):
    tl = otio.adapters.read_from_file(str(path)); v1 = tl.video_tracks()[0]; problems = []
    d = v1.duration().to_seconds()
    if abs(d - vdur) > 1.0 / fps + 1e-6: problems.append(f"V1 trvá {d:.3f} s, video {vdur:.3f} s")
    missing = sorted({c.media_reference.target_url for c in tl.find_clips() if not Path(c.media_reference.target_url).exists()})
    if missing: problems.append(f"chybí soubory: {missing[:5]}")
    return {"v1_seconds": round(d, 3), "video_seconds": round(vdur, 3), "v1_clips": len(list(v1.find_clips())),
            "v2_clips": len(list(tl.video_tracks()[1].find_clips())), "markers": sum(len(c.markers) for c in v1.find_clips()),
            "problems": problems}

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project"); ap.add_argument("--lang", default="cs"); ap.add_argument("--video")
    a = ap.parse_args(); proj = Path(a.project).resolve()
    video = proj / (a.video or f"render/final.{a.lang}.mp4")
    if not video.exists() and not a.video: video = proj / "render" / f"preview.{a.lang}.mp4"
    if not video.exists(): sys.exit(f"STOP: video neexistuje: {video} (nejdřív vid.py render)")
    tl, shots, origin, vdur, fps = build(proj, a.lang, video)
    out = proj / "render" / f"timeline.{a.lang}.otio"; otio.adapters.write_to_file(tl, str(out))
    edl_out = out.with_suffix(".edl"); cmx = None
    try:
        t1 = otio.schema.Timeline(name=tl.name); t1.tracks.append(tl.video_tracks()[0].deepcopy())
        otio.adapters.write_to_file(t1, str(edl_out), adapter_name="cmx_3600")
    except Exception as e:  # adapter not installed or a clip it cannot express: the .otio stays the record
        cmx = f"CMX EDL nevznikl: {type(e).__name__}: {e}"
    chk = verify(out, video, vdur, fps)
    from lib.common import stale_steps
    if (proj / "state.json").exists() and f"render_{a.lang}" in stale_steps(proj):
        chk["problems"].append(f"render_{a.lang} je zastaralý: střihový plán nebo zvuk se změnil po renderu, časová osa odpovídá novému plánu")
    chk.update(shots_from=origin, shots=len(shots), otio=str(out.relative_to(proj)),
                                                    edl=str(edl_out.relative_to(proj)) if edl_out.exists() and not cmx else None, edl_error=cmx)
    out.with_suffix(".check.json").write_text(json.dumps(chk, ensure_ascii=False, indent=1))
    print(json.dumps(chk, ensure_ascii=False))
    sys.exit(1 if chk["problems"] else 0)

if __name__ == "__main__":
    main()
