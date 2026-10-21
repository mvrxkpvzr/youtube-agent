"""Pipeline CLI. Run with the Qwen venv python (has torch, mlx-whisper, librosa, Pillow, jsonschema).
  vid.py validate <project>
  vid.py voice <project> --lang cs [--engine piper_cs] [--force]
  vid.py check <project> --lang cs            # back-transcription
  vid.py audio <project> --lang cs            # join scenes -> narration.wav + timings
  vid.py subs <project> --lang cs             # .srt from approved text
  vid.py mix <project> --lang cs              # narration + music (music_cue) + SFX -> mix.wav
  vid.py render <project> --lang cs [--final]
  vid.py qa <project> --lang cs
  vid.py all <project> --lang cs              # voice→check→audio→subs→mix→render→qa, stops on errors
  vid.py sfxlib _                             # (re)build own synthesised SFX in pipeline/sfx/own
  vid.py status <project>                     # steps + stale steps
  vid.py craft <project> --lang cs            # craft_check.py: hook, beats, language, tempo, shots, music (knowledge/)
  vid.py visual <project> --lang cs           # visual_plan.py: visual sources manifest + per-scene plan (knowledge/12)
  vid.py edl <project> --lang cs              # edit decision list before an expensive render
  vid.py gates <project> --lang cs            # quality gates Q1–Q7; render --final needs Q1–Q5 (--override-gates "reason")"""
import argparse, json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import voice as V, asr_check as A, audio as AU, subtitles as S, render as R, qa as Q, mix as MX
from lib.common import stale_steps

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("project"); ap.add_argument("--lang", default="cs")
    ap.add_argument("--engine"); ap.add_argument("--force", action="store_true"); ap.add_argument("--final", action="store_true")
    ap.add_argument("--override-gates", metavar="REASON", help="render --final despite failing quality gates; the reason is recorded")
    a = ap.parse_args(); proj = Path(a.project).resolve(); t0 = time.time()
    def step(name, fn):
        t = time.time(); r = fn(); print(f"[{name}] {time.time()-t:.0f}s"); return r
    if a.cmd == "validate":
        sys.exit(subprocess.run([sys.executable, str(Path(__file__).parent / "validate.py"), str(proj)]).returncode)
    if a.cmd == "status":
        print(json.dumps(json.loads((proj / "state.json").read_text())["steps"], indent=1, ensure_ascii=False)[:4000]); print("stale:", stale_steps(proj)); return
    if a.cmd == "sfxlib":
        from lib.sfx import build_library
        anchors = build_library(); (Path(__file__).parent / "sfx" / "own" / "anchors.json").write_text(json.dumps(anchors, indent=1)); print(anchors); return
    if a.cmd in ("craft", "visual", "edl", "gates"):
        script = {"craft": "craft_check.py", "visual": "visual_plan.py", "edl": "edl.py", "gates": "gates.py"}[a.cmd]
        sys.exit(subprocess.run([sys.executable, str(Path(__file__).parent / script), str(proj), "--lang", a.lang]).returncode)
    cmds = ["voice", "check", "audio", "subs", "mix", "render", "qa"] if a.cmd == "all" else [a.cmd]
    for c in cmds:
        if c == "voice":
            regen, warns = step("voice", lambda: V.voice(proj, a.lang, a.engine, a.force))
            print(f"  regenerováno: {regen or 'nic (cache)'}"); [print("  WARN", w) for w in warns]
        elif c == "check":
            rep = step("check", lambda: A.check(proj, a.lang))
            errs = [(k, e) for k, v in rep.items() for e in v["errors"]]
            for k, v in rep.items(): print(f"  {k} WER {v['wer']:.0%}", *v["errors"], *v["warnings"])
            if errs and a.cmd == "all": sys.exit(f"STOP: zpětný přepis našel {len(errs)} chyb – oprav text/lexikon nebo přegeneruj scénu (--force)")
        elif c == "audio": step("audio", lambda: AU.assemble(proj, a.lang))
        elif c == "subs":
            out, w = step("subs", lambda: S.build(proj, a.lang)); print(" ", out.name, *w)
        elif c == "mix":
            if not (proj / f"shotlist.{a.lang}.json").exists() or "music" not in json.loads((proj / f"shotlist.{a.lang}.json").read_text()):
                print("[mix] přeskočeno – střihový plán nemá blok music"); continue
            out, used = step("mix", lambda: MX.mix(proj, a.lang)); print(f"  {out.name}: {len(used)} efektů", *[f"{t}s {n}" for t, n in used])
        elif c == "render":
            if a.final:
                import edl, gates
                edl.build(proj, a.lang)
                doc = gates.run(proj, a.lang, "Q5"); failed = [g for g, r in doc["quality"].items() if r["status"] == "fail"]
                if failed and not a.override_gates:
                    for g in failed: print(f"  {g} FAIL {doc['quality'][g]['name']}", *[f"\n    ✗ {f}" for f in doc["quality"][g]["fail"][:5]])
                    sys.exit(f"STOP: finální render vyžaduje brány Q1–Q5 (selhalo {', '.join(failed)}). Oprav fázi, nebo --override-gates \"důvod\".")
                if failed:
                    log = proj / "review" / "gate_overrides.md"; log.parent.mkdir(exist_ok=True)
                    with open(log, "a", encoding="utf-8") as f: f.write(f"- {time.strftime('%Y-%m-%d %H:%M')} render --final {a.lang} přes {', '.join(failed)}: {a.override_gates}\n")
                    print(f"  POZOR: brány {', '.join(failed)} přeskočeny, důvod zapsán do review/gate_overrides.md")
            out, n, tot = step("render", lambda: R.render(proj, a.lang, preview=not a.final)); print(f"  {out.name}: {n} záběrů, {tot:.1f} s")
        elif c == "qa":
            vid = proj / "render" / (f"final.{a.lang}.mp4" if a.final else f"preview.{a.lang}.mp4")
            rep, E, W = step("qa", lambda: Q.qa(proj, a.lang, vid)); print(f"  {rep.name}: {len(E)} ERROR, {len(W)} WARN"); [print("  ERROR", e) for e in E]
    print(f"celkem {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
