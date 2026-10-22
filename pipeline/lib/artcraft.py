"""Cut and export in ArtCraft's video editor (headless host in pipeline/artcraft), then master for YouTube and verify.
  shots (render.render_shots) + narration + bed -> editplan -> editor timeline -> editor export (.webm VP9/Opus)
  -> verify against the plan -> preview/final.<lang>.mp4 (H.264/AAC, two-pass loudnorm) -> verify again.
The editor runs on this machine only: no ArtCraft account, API key or credits are involved."""
import json, os, shutil, subprocess, sys
from pathlib import Path
from .common import PIPE, cfg, ffmpeg, run, update_state
from . import editplan as EP, verify_export as VX

HOST = PIPE / "artcraft" / "host"

def available():
    """None when the editor can run here, otherwise what is missing."""
    if not (HOST / "dist" / "index.html").exists(): return "editor není sestavený: bash pipeline/artcraft/setup.sh"
    if not shutil.which("node"): return "chybí node"
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY") and not shutil.which("xvfb-run"): return "chybí xvfb-run"
    return None

def master(raw, out, preview):
    """Editor export -> YouTube master: H.264 + AAC 48 kHz, loudness to the pipeline target in two passes."""
    c = cfg(); ff = ffmpeg(); tp = c["true_peak_dbtp"] - 0.5
    flt = f"loudnorm=I={c['loudness_target_lufs']}:TP={tp}:LRA=11:print_format=json"
    r = run([ff, "-hide_banner", "-i", str(raw), "-vn", "-af", flt, "-f", "null", "-"])
    m = json.loads(r.stderr[r.stderr.rfind("{"): r.stderr.rfind("}") + 1])
    flt2 = (f"loudnorm=I={c['loudness_target_lufs']}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=false,aresample=48000")
    run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw), "-af", flt2, "-c:v", "libx264", "-preset",
         "veryfast" if preview else "slow", "-crf", "20" if preview else "16", "-maxrate", "12M", "-bufsize", "24M", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(out)])
    return out

def assemble(proj, lang, preview=True, burn_subtitles=False):
    proj = Path(proj); missing = available()
    if missing: raise SystemExit(f"[artcraft] {missing}")
    plan_path, plan = EP.build(proj, lang, preview, burn_subtitles)
    errs = EP.check(plan)
    if errs: raise SystemExit("[artcraft] střihový plán je nekonzistentní:\n  " + "\n  ".join(errs))
    tl = EP.resolve(plan, proj); r = proj / "render"
    tl_path = r / f"timeline.{lang}.json"; tl_path.write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    raw = r / f"artcraft.{lang}.webm"; raw.unlink(missing_ok=True)
    cmd = ["node", str(HOST / "run_editor.mjs"), str(tl_path), str(raw)]
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"): cmd = ["xvfb-run", "-a", *cmd]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0: raise SystemExit(f"[artcraft] editor selhal:\n{p.stderr[-3000:]}")
    report = json.loads((r / f"artcraft.{lang}.editor.json").read_text())
    rep, E, W = VX.verify(proj, lang, tl, raw, report, engine="artcraft")
    if E: raise SystemExit(f"[artcraft] export neodpovídá plánu ({len(E)} chyb), viz {rep}:\n  " + "\n  ".join(E[:10]))
    final = r / (f"preview.{lang}.mp4" if preview else f"final.{lang}.mp4")
    master(raw, final, preview)
    rep2, E2, _ = VX.verify(proj, lang, tl, final, report, engine="artcraft_master")
    if E2: raise SystemExit(f"[artcraft] master neodpovídá plánu, viz {rep2}:\n  " + "\n  ".join(E2[:10]))
    update_state(proj, f"render_{lang}", "done", inputs=[plan_path, proj / f"shotlist.{lang}.json"], outputs=[raw, final],
                 engine="artcraft", editor_wall_s=report.get("wall_s"), verify=[str(rep.relative_to(proj)), str(rep2.relative_to(proj))])
    return final, rep, rep2, report
