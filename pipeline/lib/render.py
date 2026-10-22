"""Shot list + timings -> PNG cards -> moving clips (slow push-in, 3D panel or own motion clip) -> xfade chain -> mux."""
import json, re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
from .common import cfg, ffmpeg, run, load_shotlist, update_state, sha
from .graphics import card, source_line, B, W as GW, H as GH
from . import fx3d

CHUNK = 24

def jsonl(p): return {o["id"]: o for o in (json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip())} if p.exists() else {}

def source_text(src, lang):
    if not src: return ""
    lab = "Zdroj" if lang == "cs" else "Quelle"
    date = src.get("published_at") or ""
    if date:
        y, m, d = (date.split("-") + ["", ""])[:3]
        date = f"{int(d)}. {int(m)}. {y}" if d else (f"{int(m)}/{y}" if m else y)
    pub = src.get(f"publisher_{lang}") or src["publisher"]
    return f"{lab}: {pub}" + (f", {date}" if date else "")

def plan(proj, lang):
    sl = load_shotlist(proj, lang); tm = {t["id"]: t for t in json.loads((proj / "audio" / lang / "timings.json").read_text())}
    sources, assets = jsonl(proj / "sources.jsonl"), jsonl(proj / "assets.jsonl")
    ids = [s["id"] for s in sl["scenes"]]; total = tm[ids[-1]]["end"] + 1.2
    shots = []
    for i, sc in enumerate(sl["scenes"]):
        start = 0.0 if i == 0 else tm[sc["id"]]["start"]
        end = tm[ids[i + 1]]["start"] if i + 1 < len(ids) else total
        weights = [v.get("duration_s", 1.0) for v in sc["visuals"]]; acc = start
        for v, w in zip(sc["visuals"], weights):
            d = (end - start) * w / sum(weights)
            asset = assets.get(v.get("asset_id") or "")
            shots.append({"scene": sc["id"], "template": v["template"], "params": v.get("params", {}), "dur": d, "fx": v.get("fx", "none"),
                          "source": source_text(sources.get(sc.get("on_screen_source") or ""), lang),
                          "photo": str(proj / asset["file"]) if asset else None})
            acc += d
    return shots, total

def master_audio(proj, lang, out):
    c = cfg(); ff = ffmpeg(); d = proj / "audio" / lang; nar = d / "narration.wav"
    tp = c['true_peak_dbtp'] - 0.5  # headroom: AAC encoding adds inter-sample peaks
    flt = f"loudnorm=I={c['loudness_target_lufs']}:TP={tp}:LRA=11:print_format=json"
    pre = c.get("voice_chain", "anull")  # narration polish before loudness normalisation
    mixed = d / "mix.wav"  # voice + music + SFX (vid.py mix); the voice chain is already applied inside it
    if mixed.exists() and mixed.stat().st_mtime >= nar.stat().st_mtime: nar, pre = mixed, "anull"
    r = run([ff, "-hide_banner", "-i", str(nar), "-af", pre + "," + flt, "-f", "null", "-"])
    js = r.stderr[r.stderr.rfind("{"): r.stderr.rfind("}") + 1]; m = json.loads(js)
    flt2 = (f"loudnorm=I={c['loudness_target_lufs']}:TP={tp}:LRA=11:measured_I={m['input_i']}:"
            f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=false")
    run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(nar), "-af", pre + "," + flt2 + ",aresample=48000", "-c:a", "pcm_s24le", str(out)])

def source_overlay(text, path):
    """Flat on-screen source line on a transparent layer (3D panels and motion clips keep the citation readable)."""
    img = Image.new("RGBA", (GW, GH), (0, 0, 0, 0)); source_line(ImageDraw.Draw(img), text)
    img.resize((B["w"], B["h"]), Image.LANCZOS).save(path); return path

def fit_clip(src, out, L, fps, overlay, enc, start=0.0):
    """Own motion clip -> exactly L seconds at 1920x1080: speed-fit within 0.5–1.3×, then trim / hold last frame."""
    ff = ffmpeg()
    info = subprocess.run([ff, "-hide_banner", "-i", str(src)], capture_output=True, text=True).stderr
    h, m, sec = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info).groups(); D = int(h) * 3600 + int(m) * 60 + float(sec) - start
    k = min(max(L / D, 0.5), 1.3)  # >1 slows down, <1 speeds up
    n = max(int(round(L * fps)), 2)
    vf = (f"[0:v]trim=start={start},setpts=(PTS-STARTPTS)*{k:.4f},fps={fps},scale={B['w']}:{B['h']}:force_original_aspect_ratio=increase,"
          f"crop={B['w']}:{B['h']},tpad=stop_mode=clone:stop_duration={L:.3f}[v]")
    inputs = ["-i", str(src)]
    if overlay: inputs += ["-i", str(overlay)]; vf += ";[v][1:v]overlay=0:0[v]"
    run([ff, "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", vf, "-map", "[v]", "-an",
         "-frames:v", str(n), "-pix_fmt", "yuv420p", *enc, str(out)])

def render_shots(proj, lang, preview=True, codec="h264"):
    """Every shot as its own clip (shot length + one transition overlap), in work_<lang>/shotNNN.mp4 (codec="vp9": .webm,
    which open-source Chromium can decode; the headless ArtCraft editor in the cloud has no H.264).
    Returns shots, [(clip, shot length)], total, transition length and type. Also the input of an editor (lib/editplan)."""
    ff = ffmpeg(); fps = B["fps"]; pace = load_shotlist(proj, lang).get("pace", {})
    X = pace.get("xfade_s", B["xfade_s"]); transition = pace.get("transition", B.get("transition", "fadeblack"))
    enc = ["-c:v", "libx264", "-preset", "veryfast" if preview else "slow", "-crf", "20" if preview else "16"]
    ext = ".mp4"
    if codec == "vp9":
        enc = ["-c:v", "libvpx-vp9", "-deadline", "realtime", "-cpu-used", "8", "-row-mt", "1", "-b:v", "0", "-crf", "24" if preview else "18"]; ext = ".webm"
    work = proj / "render" / f"work_{lang}"; work.mkdir(parents=True, exist_ok=True)
    shots, total = plan(proj, lang); clips = []
    for i, s in enumerate(shots):
        L = s["dur"] + (X if i < len(shots) - 1 else 0); n = max(int(round(L * fps)), 2)
        out = work / f"shot{i:03}{ext}"
        ov = source_overlay(s["source"], work / f"shot{i:03}.src.png") if s["source"] else None
        if s["template"] == "motion":  # own pre-rendered 3D/motion clip (Blender, fx3d), path relative to the project
            fit_clip(proj / s["params"]["file"], out, L, fps, ov, enc, start=s["params"].get("start_s", 0.0))
            clips.append((out, s["dur"])); continue
        png = work / f"shot{i:03}.png"
        if s["fx"] == "panel3d":  # tilted 3D panel; cached by card content + length (fx3d is slow)
            card(s["template"], s["params"], "", seed=i, photo=s["photo"]).save(png)
            raw = work / f"p3d_{sha(png)[:10]}_{n}.mp4"
            if not raw.exists():
                st, en = ((12, -20, -3, 0.95), (5, -6, -1, 1.1)) if i % 2 else ((10, 22, 3, 0.95), (4, 7, 1, 1.1))
                fx3d.panel3d(str(png), str(raw), dur=n / fps, start=st, end=en, seed=i)
            fit_clip(raw, out, L, fps, ov, enc); clips.append((out, s["dur"])); continue
        card(s["template"], s["params"], s["source"], seed=i, photo=s["photo"]).save(png)
        z = f"min(1+({B['zoom_end']}-1)*on/{n},{B['zoom_end']})"
        vf = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={B['w']}x{B['h']}:fps={fps},"
              f"format=yuv420p")
        run([ff, "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-framerate", str(fps), "-i", str(png), "-vf", vf,
             "-frames:v", str(n), *enc, str(out)])
        clips.append((out, s["dur"]))
    return shots, clips, total, X, transition

def render(proj, lang, preview=True):
    ff = ffmpeg(); fps = B["fps"]
    shots, clips, total, X, transition = render_shots(proj, lang, preview)
    work = proj / "render" / f"work_{lang}"
    # xfade chain; long videos are pre-joined in chunks (one ffmpeg with 100+ inputs ran out of 15 GB RAM)
    def chain(cs):
        inputs, parts, last, off = [], [], "[0:v]", 0.0
        for c, _ in cs: inputs += ["-i", str(c)]
        for k in range(1, len(cs)):
            off += cs[k - 1][1]; lab = f"[v{k}]"
            parts.append(f"{last}[{k}:v]xfade=transition={transition}:duration={X}:offset={off:.3f}{lab}"); last = lab
        return inputs, parts, last
    while len(clips) > CHUNK:
        joined = []
        for j in range(0, len(clips), CHUNK):
            cs = clips[j:j + CHUNK]
            if len(cs) == 1: joined.append(cs[0]); continue
            out = work / f"chunk{len(clips)}_{j:03d}.mp4"; inputs, parts, last = chain(cs)
            run([ff, "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", ";".join(parts), "-map", last,
                 "-c:v", "libx264", "-preset", "ultrafast", "-crf", "10", "-pix_fmt", "yuv420p", "-r", str(fps), str(out)])
            joined.append((out, sum(d for _, d in cs)))  # same offsets as the flat chain: chunk length = sum of its shot durations
        clips = joined
    inputs, parts, last = chain(clips)
    audio = work / "master.wav"; master_audio(proj, lang, audio)
    final = proj / "render" / (f"preview.{lang}.mp4" if preview else f"final.{lang}.mp4")
    fc = (";".join(parts) if parts else "[0:v]null[v0]") + f";[{len(clips)}:a]apad[a]"
    run([ff, "-y", "-hide_banner", "-loglevel", "error", *inputs, "-i", str(audio), "-filter_complex", fc,
         "-map", last if parts else "[v0]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast" if preview else "slow",
         "-crf", "20" if preview else "16", "-maxrate", "12M", "-bufsize", "24M", "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
         "-movflags", "+faststart", "-t", f"{total:.3f}", str(final)])
    for f in work.glob("chunk*.mp4"): f.unlink()   # several GB of intermediates; shots stay for inspection
    update_state(proj, f"render_{lang}", "done", inputs=[proj / f"shotlist.{lang}.json", proj / "audio" / lang / "narration.wav"],
                 outputs=[final], shots=len(shots))
    return final, len(shots), total
