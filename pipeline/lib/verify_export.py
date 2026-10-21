"""Does an editor export match its edit plan? Checks the file itself (exists, decodes end to end, size, fps, streams,
duration), the editor's own read-back of its timeline, every visual clip (the export frame in the middle of the clip
against a frame made straight from the clip's source, and that it matches its own clip better than any other clip),
every narration clip (audio cross-correlation with the source at the planned offset) and long black gaps.
Writes render/verify_<engine>.<lang>.json + .md. ERROR = the export does not match the plan."""
import json, re, subprocess
from pathlib import Path
import numpy as np
from .common import ffmpeg
from .qa import probe

SW, SH, SR = 160, 90, 16000

def frame(src, t, fit="cover", zoom=1.0, image=False):
    ff = ffmpeg()
    vf = (f"scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH}" if fit == "cover" else
          f"scale={SW}:{SH}:force_original_aspect_ratio=decrease,pad={SW}:{SH}:(ow-iw)/2:(oh-ih)/2")
    if zoom != 1.0: vf = f"scale=iw*{zoom:.4f}:ih*{zoom:.4f},crop=iw/{zoom:.4f}:ih/{zoom:.4f}," + vf
    inp = ["-loop", "1", "-i", str(src)] if image else ["-ss", f"{max(t, 0):.3f}", "-i", str(src)]
    r = subprocess.run([ff, "-v", "error", *inp, "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                       capture_output=True)
    a = np.frombuffer(r.stdout, np.uint8)
    return a.reshape(SH, SW).astype(np.float32) if a.size == SW * SH else None

def audio(src, start, dur):
    r = subprocess.run([ffmpeg(), "-v", "error", "-ss", f"{max(start, 0):.3f}", "-t", f"{dur:.3f}", "-i", str(src),
                        "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.float32)

def corr(a, b):
    a, b = a - a.mean(), b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else (1.0 if np.allclose(a, b) else 0.0)

def xcorr(ref, got, max_lag_s=0.25):
    """Peak normalised cross-correlation of the source segment inside a window of the export, and its lag in seconds."""
    n = len(ref); L = int(max_lag_s * SR)
    if n < SR // 4 or len(got) < n: return 0.0, None
    size = 1 << int(np.ceil(np.log2(len(got) + n)))
    c = np.fft.irfft(np.fft.rfft(got, size) * np.conj(np.fft.rfft(ref, size)), size)[: len(got) - n + 1]
    e = np.sqrt(np.convolve(got ** 2, np.ones(n), "valid")) * np.sqrt((ref ** 2).sum()) + 1e-9
    nc = c / e; k = int(np.argmax(nc[: 2 * L + 1])) if len(nc) > 2 * L else int(np.argmax(nc))
    return float(nc[k]), (k - L) / SR

def verify(proj, lang, timeline, export, editor_report=None, engine="artcraft"):
    proj, export = Path(proj), Path(export); E, W, ok = [], [], []
    tl = timeline; fps = tl["fps"]; media = {m["id"]: m for m in tl["media"]}
    res = {"export": str(export), "engine": engine, "clips": [], "audio": []}
    if not export.exists() or export.stat().st_size == 0:
        E.append(f"export {export.name} neexistuje nebo je prázdný"); return finish(proj, lang, engine, res, E, W, ok)
    p = probe(ffmpeg(), export); res["probe"] = p
    (ok if (p["w"], p["h"]) == (tl["width"], tl["height"]) else E).append(f"rozlišení {p['w']}x{p['h']} (plán {tl['width']}x{tl['height']})")
    (ok if p["fps"] and abs(p["fps"] - fps) < 0.01 else E).append(f"fps {p['fps']} (plán {fps})")
    (ok if p["vcodec"] and p["acodec"] else E).append(f"stopy: video {p['vcodec']}, zvuk {p['acodec']}")
    tol = max(2 / fps, 0.1)
    (ok if abs(p["duration"] - tl["duration_s"]) <= tol else E).append(f"délka {p['duration']:.3f} s (plán {tl['duration_s']:.3f} ±{tol:.2f})")
    dec = subprocess.run([ffmpeg(), "-v", "error", "-i", str(export), "-f", "null", "-"], capture_output=True, text=True)
    errs = [l for l in dec.stderr.splitlines() if l.strip()]
    (ok if dec.returncode == 0 and not errs else E).append(f"přehrání celého souboru (dekódování): {len(errs)} chyb" + (f" – {errs[0][:120]}" if errs else ""))
    # the editor's own timeline read-back against the plan
    if editor_report:
        rb = [e for tr in editor_report.get("readback", []) for e in tr["elements"]]
        got = {k: sorted(round(e["start_s"], 2) for e in rb if (e["type"] in ("video", "image")) == (k == "video") and (e["type"] == "audio") == (k == "audio") and (e["type"] == "text") == (k == "text")) for k in ("video", "audio", "text")}
        for k in ("video", "audio", "text"):
            want = sorted(round(c["start_s"], 2) for c in tl[k])
            bad = len(want) != len(got[k]) or any(abs(a - b) > 1.5 / fps for a, b in zip(want, got[k]))
            (E if bad else ok).append(f"časová osa editoru, {k}: {len(got[k])} prvků (plán {len(want)})" + (" – časy nesedí" if bad and len(want) == len(got[k]) else ""))
        texts = sorted(e.get("content") or "" for e in rb if e["type"] == "text")
        if texts != sorted(c["content"] for c in tl["text"]): E.append("texty v editoru se liší od plánu")
    # every visual clip: export frame in the middle of the clip's clean part vs. the source
    refs, outs = [], []
    for c in tl["video"]:
        a = c["start_s"] + c.get("fade_in_s", 0); b = c["start_s"] + c["dur_s"] - max(c.get("fade_out_s", 0), 0.2)
        t = (a + b) / 2 if b > a else c["start_s"] + c["dur_s"] / 2; local = t - c["start_s"]
        m = media[c["media"]]; z0, z1 = c.get("zoom_from", 1.0), c.get("zoom_to", c.get("zoom_from", 1.0))
        z = z0 + (z1 - z0) * local / c["dur_s"]
        refs.append(frame(m["path"], c.get("in_s", 0) + local, c.get("fit", "cover"), z, image=m["kind"] == "image"))
        outs.append((t, frame(export, t)))
    rows = int(SH * 0.72)  # burned-in subtitles sit in the lower part of the frame
    for i, (c, ref, (t, got)) in enumerate(zip(tl["video"], refs, outs)):
        if ref is None or got is None:
            E.append(f"{c['scene']} klip {c['media']} v {t:.2f} s: snímek nejde přečíst"); continue
        own = corr(ref[:rows], got[:rows]); others = [corr(r[:rows], got[:rows]) for j, r in enumerate(refs) if j != i and r is not None]
        best_other = max(others, default=0.0)
        row = {"scene": c["scene"], "media": c["media"], "t": round(t, 3), "match": round(own, 3), "best_other": round(best_other, 3)}
        res["clips"].append(row)
        if own < 0.8: E.append(f"{c['scene']} {c['media']} v {t:.2f} s: obraz neodpovídá zdroji (shoda {own:.2f})")
        elif best_other > own + 0.02: E.append(f"{c['scene']} {c['media']} v {t:.2f} s: víc se podobá jinému klipu ({best_other:.2f} > {own:.2f}) – pořadí?")
    if res["clips"] and all(r["match"] >= 0.8 for r in res["clips"]):
        ok.append(f"obraz: {len(res['clips'])} klipů na svém místě (nejnižší shoda {min(r['match'] for r in res['clips']):.2f})")
    # narration: the source segment must sit in the export at its planned time
    for c in tl["audio"]:
        if c.get("role") != "narration": continue
        m = media[c["media"]]; dur = min(c["dur_s"], 6.0)
        ref = audio(m["path"], c.get("in_s", 0), dur); got = audio(export, c["start_s"] - 0.25, dur + 0.5)
        peak, lag = xcorr(ref, got)
        row = {"scene": c["scene"], "start_s": c["start_s"], "corr": round(peak, 3), "lag_s": lag}
        res["audio"].append(row)
        if peak < 0.5 or lag is None or abs(lag) > 0.04:
            E.append(f"{c['scene']} hlas v {c['start_s']:.2f} s: nenalezen na svém místě (korelace {peak:.2f}, posun {lag})")
    if res["audio"] and all(r["corr"] >= 0.5 and r["lag_s"] is not None and abs(r["lag_s"]) <= 0.04 for r in res["audio"]):
        ok.append(f"hlas: {len(res['audio'])} scén na svém místě (nejnižší korelace {min(r['corr'] for r in res['audio']):.2f}, "
                  f"největší posun {max(abs(r['lag_s']) for r in res['audio']) * 1000:.0f} ms)")
    bl = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(export), "-vf", "blackdetect=d=0.5:pix_th=0.05", "-an", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    blacks = re.findall(r"black_start:([\d.]+)", bl)
    (ok if not blacks else E).append(f"černé úseky ≥ 0,5 s: {len(blacks)}" + (f" (od {', '.join(blacks[:4])} s)" if blacks else ""))
    return finish(proj, lang, engine, res, E, W, ok)

def finish(proj, lang, engine, res, E, W, ok):
    res.update({"errors": E, "warnings": W, "ok": ok, "passed": not E})
    out = proj / "render" / f"verify_{engine}.{lang}.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    md = (f"# Ověření exportu – {engine} ({lang})\n\nSoubor: `{Path(res['export']).name}` · výsledek: **{'PASS' if not E else 'FAIL'}**\n\n"
          f"## ERROR ({len(E)})\n" + "".join(f"- {x}\n" for x in E) + f"\n## WARN ({len(W)})\n" + "".join(f"- {x}\n" for x in W) +
          f"\n## OK ({len(ok)})\n" + "".join(f"- {x}\n" for x in ok) +
          "\n## Klipy\n| scéna | médium | čas s | shoda | nejbližší jiný |\n|---|---|---|---|---|\n" +
          "".join(f"| {r['scene']} | {r['media']} | {r['t']} | {r['match']} | {r['best_other']} |\n" for r in res["clips"]) +
          "\n## Hlas\n| scéna | začátek s | korelace | posun ms |\n|---|---|---|---|\n" +
          "".join(f"| {r['scene']} | {r['start_s']:.2f} | {r['corr']} | {'' if r['lag_s'] is None else round(r['lag_s'] * 1000)} |\n" for r in res["audio"]))
    md_path = out.with_suffix(".md"); md_path.write_text(md, encoding="utf-8")
    return md_path, E, W
