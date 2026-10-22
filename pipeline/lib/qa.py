"""Technical + editorial QA -> qa_report.<lang>.md. ERROR blocks publication, WARN needs a human look."""
import json, re, subprocess, sys
from pathlib import Path
from .common import cfg, ffmpeg, PIPE

def probe(ff, f):
    r = subprocess.run([ff, "-hide_banner", "-i", str(f)], capture_output=True, text=True).stderr
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r); vid = re.search(r"Video: (\w+).*?, (\d+)x(\d+).*?([\d.]+) fps", r)
    aud = re.search(r"Audio: (\w+).*?, (\d+) Hz", r)
    d = int(dur[1]) * 3600 + int(dur[2]) * 60 + float(dur[3]) if dur else 0
    return {"duration": d, "vcodec": vid and vid[1], "w": vid and int(vid[2]), "h": vid and int(vid[3]), "fps": vid and float(vid[4]),
            "acodec": aud and aud[1], "ar": aud and int(aud[2])}

def loudness(ff, f):
    r = subprocess.run([ff, "-hide_banner", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    tail = r[r.rfind("Summary:"):]
    I = re.search(r"I:\s+(-?[\d.]+) LUFS", tail); TP = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return float(I[1]) if I else None, float(TP[1]) if TP else None

def detect(ff, f, flt, key):
    r = subprocess.run([ff, "-hide_banner", "-i", str(f), "-vf", flt, "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    return re.findall(key, r)

def srt_check(p):
    txt = p.read_text(encoding="utf-8").strip().split("\n\n"); issues = []
    def t(s): h, m, r = s.split(":"); sec, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
    prev_end = 0
    for blk in txt:
        lines = blk.split("\n"); a, b = lines[1].split(" --> "); s, e = t(a), t(b); body = lines[2:]
        if len(body) > 2: issues.append(f"#{lines[0]}: {len(body)} řádky")
        if any(len(x) > 42 for x in body): issues.append(f"#{lines[0]}: řádek > 42 znaků")
        if e - s < 0.9: issues.append(f"#{lines[0]}: kratší než 1 s")
        if s < prev_end - 0.01: issues.append(f"#{lines[0]}: překryv s předchozím")
        cps = len("".join(body)) / max(e - s, 0.01)
        if cps > 17: issues.append(f"#{lines[0]}: {cps:.0f} zn./s")
        prev_end = e
    return len(txt), issues

def qa(proj, lang, video):
    c = cfg(); ff = ffmpeg(); E, Wn, ok = [], [], []
    p = probe(ff, video)
    (ok if (p["w"], p["h"]) == (1920, 1080) else E).append(f"rozlišení {p['w']}x{p['h']}")
    (ok if p["fps"] and abs(p["fps"] - 25) < 0.01 else E).append(f"fps {p['fps']}")
    (ok if p["vcodec"] == "h264" and p["acodec"] == "aac" and p["ar"] == 48000 else E).append(f"kodeky {p['vcodec']}/{p['acodec']} {p['ar']} Hz")
    I, TP = loudness(ff, video)
    (ok if I is not None and abs(I - c["loudness_target_lufs"]) <= 1 else E).append(f"hlasitost {I} LUFS (cíl {c['loudness_target_lufs']} ±1)")
    (ok if TP is not None and TP <= c["true_peak_dbtp"] + 0.2 else E).append(f"true peak {TP} dBFS (max {c['true_peak_dbtp']})")
    blacks = detect(ff, video, "blackdetect=d=0.5:pix_th=0.05", r"black_start:([\d.]+)")
    (ok if not blacks else E).append(f"černé úseky ≥0,5 s: {len(blacks)}")
    freezes = detect(ff, video, "freezedetect=n=0.0005:d=8", r"freeze_start: ([\d.]+)")
    (ok if not freezes else Wn).append(f"statický obraz ≥8 s: {len(freezes)} (dlouhé karty bez pohybu působí jako slideshow)")
    srt = proj / "render" / f"subtitles.{lang}.srt"; n, iss = srt_check(srt)
    (ok if not iss else Wn).append(f"titulky: {n} titulků, problémy: {iss[:6] or 'žádné'}")
    asr = json.loads((proj / "audio" / lang / "asr_report.json").read_text())
    asr_err = [f"{k}: {e}" for k, v in asr.items() for e in v["errors"]]
    (ok if not asr_err else E).append(f"zpětný přepis: {asr_err or 'bez chyb'}")
    r = subprocess.run([sys.executable, str(PIPE / "validate.py"), str(proj)], capture_output=True, text=True)
    (ok if r.returncode == 0 else E).append("validátor projektu: " + r.stdout.strip().splitlines()[-1])
    Wn += [l for l in r.stdout.splitlines() if l.startswith("WARN")]
    metas = [json.loads(m.read_text()) for m in sorted((proj / "audio" / lang).glob("SC*.json")) if not m.name.endswith("words.json")]
    lic = {(m["engine"], m["license"], m["commercial"]) for m in metas}
    (ok if all(x[2] for x in lic) else E).append(f"licence hlasu: {sorted(lic)}")
    sl = json.loads((proj / f"shotlist.{lang}.json").read_text(encoding="utf-8"))
    ph = [f"{sc['id']} ({v['params'].get('ref','')})" for sc in sl["scenes"] for v in sc["visuals"] if v["template"] == "clip_placeholder"]
    if ph: Wn.append(f"čeká na vložení {len(ph)} klipů (práva + pípnutí): " + "; ".join(ph))
    # photosensitive flashes (WCAG 2.2 / EA IRIS), measuring code vendored from konradre/video-production-skills (MIT)
    from .flashcheck import check as flash_check
    fl = flash_check(video); (video.parent / f"{video.stem}.flash.json").write_text(json.dumps(fl, ensure_ascii=False, indent=1))
    if fl["status"] == "skipped": Wn.append(f"kontrola blikání NEPROBĚHLA: {fl['reason']}")
    for lvl, label, det in fl["rows"]:
        (E if lvl == "FAIL" else Wn if lvl == "WARN" else ok).append(f"blikání – {label}: {det}")
    Wn.append("RUČNĚ: poslech celé stopy, kontrola výslovnosti jmen, vizuální kontrola každé karty, kontrola citací na obrazovce")
    rep = proj / f"qa_report.{lang}.md"
    rep.write_text(f"# QA report – {proj.name} ({lang})\n\nVideo: `{video.relative_to(proj)}` · délka {p['duration']:.1f} s\n\n"
                   f"## ERROR ({len(E)})\n" + "".join(f"- {x}\n" for x in E) +
                   f"\n## WARN ({len(Wn)})\n" + "".join(f"- {x}\n" for x in Wn) +
                   f"\n## OK ({len(ok)})\n" + "".join(f"- {x}\n" for x in ok), encoding="utf-8")
    return rep, E, Wn
