"""Craft check of a shot list against knowledge/ playbooks: hook, story beats, language (AI smell), tempo, shot
rhythm, visual mix, humor, music and SFX, title length. Writes craft_report.<lang>.md. Stdlib only.
Usage: python3 craft_check.py <project> [--lang cs] [--quiet]    (exit 1 on ERROR)
Times come from audio/<lang>/timings.json when present (measured), otherwise from a words-per-minute estimate."""
import argparse, json, re, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.shotplan import shots as plan_shots, words

RULES = Path(__file__).resolve().parents[1] / "knowledge" / "craft_rules.json"
SENT = re.compile(r"(?<=[.?!…])\s+")
NUM = re.compile(r"\d|\b(nul|jedn|dva|dvě|tři|čtyř|pět|šest|sedm|osm|devět|deset|náct|cet|set|sto|tisíc|milion|miliard|procent|polovin|čtvrt)", re.I)

def sentences(text): return [x.strip() for x in SENT.split(text) if x.strip()]

def concrete(s):
    w = s.split()
    return bool(NUM.search(s) or any(x[:1].isupper() for x in w[1:]) or "„" in s or "$" in s)

def fmt(t): return f"{int(t // 60)}:{int(t % 60):02d}"

def check(proj, lang, rules=None):
    R = rules or json.loads(RULES.read_text(encoding="utf-8"))
    proj = Path(proj); sl = json.loads((proj / f"shotlist.{lang}.json").read_text(encoding="utf-8"))
    E, W, M = [], [], {}
    shots, times, measured = plan_shots(proj, lang, sl, R["wpm_estimate"])
    total = times[-1][2]; M["délka"] = fmt(total); M["časy"] = "změřené z audia" if measured else "odhad z počtu slov"

    # --- tempo of speech
    n_words = sum(len(words(sc["narration"])) for sc in sl["scenes"])
    speech = sum(ve - vs for _, _, _, vs, ve in times)
    if measured:
        wpm = n_words / speech * 60; M["tempo řeči"] = f"{wpm:.0f} slov/min"
        if not R["wpm_min"] <= wpm <= R["wpm_max"]: W.append(f"tempo {wpm:.0f} slov/min mimo {R['wpm_min']}–{R['wpm_max']} (04)")

    # --- hook and story beats
    first_q = next((st for sc, st, *_ in times if "?" in sc["narration"] or "question" in sc.get("beats", [])), None)
    M["první otázka"] = fmt(first_q) if first_q is not None else "žádná"
    if first_q is None or first_q > R["hook_first_question_error_s"]:
        E.append(f"otevřená otázka chybí nebo přichází pozdě ({M['první otázka']}, cíl ≤ {R['hook_first_question_max_s']} s) (03)")
    elif first_q > R["hook_first_question_max_s"]: W.append(f"první otázka v {fmt(first_q)}, cíl ≤ {R['hook_first_question_max_s']} s (03)")
    acts = [sc.get("act") for sc in sl["scenes"]]
    if acts[0] not in (None, "hook"): W.append("video nezačíná dějstvím hook (03)")
    if "payoff" not in acts: W.append("chybí dějství payoff: odpověď na otázku z hooku (03)")
    beat_t = [st for sc, st, *_ in times if sc.get("beats") or "?" in sc["narration"] or sc.get("act") in ("turn", "payoff")]
    gaps = [(b - a, a) for a, b in zip([0.0] + beat_t, beat_t + [total])]
    worst = max(gaps); M["nejdelší úsek bez beatu"] = f"{worst[0]:.0f} s (od {fmt(worst[1])})"
    for g, a in gaps:
        if g > R["max_gap_without_beat_s"]: W.append(f"{g:.0f} s bez nové otázky, zvratu nebo vtipu od {fmt(a)} – označ beats nebo přidej (04)")
    if not any(sc.get("beats") for sc in sl["scenes"]): W.append("žádná scéna nemá pole beats – kontrola rytmu příběhu stojí jen na otaznících")
    humor = sum("humor" in sc.get("beats", []) for sc in sl["scenes"]); per_min = humor / (total / 60)
    M["humor"] = f"{humor} beatů ({per_min:.1f}/min)"
    if any(sc.get("beats") for sc in sl["scenes"]):
        if per_min < R["humor_min_per_min"]: W.append(f"málo humoru: {humor} beatů na {fmt(total)} (05)")
        if per_min > R["humor_max_per_min"]: W.append(f"humor v každé větě: {per_min:.1f}/min (05)")

    # --- language: AI smell
    text = " ".join(sc["narration"] for sc in sl["scenes"]); low = text.lower(); sents = sentences(text)
    banned = [b for b in R["banned_phrases"] if b in low]
    if banned: E.append(f"zakázané fráze: {', '.join(banned)} (03, 10)")
    over = {w: len(re.findall(rf"\b{w}\b", low)) for w in R["overused_words"]}
    over = {w: n for w, n in over.items() if n > R["overused_max"]}
    if over: W.append(f"nadužívaná slova: {over} (10)")
    lens = [len(words(s)) for s in sents]
    M["věty"] = f"{len(sents)}, průměr {statistics.mean(lens):.1f} slov, odchylka {statistics.pstdev(lens):.1f}, max {max(lens)}"
    long = [s[:60] for s, l in zip(sents, lens) if l > R["max_sentence_words"]]
    if long: W.append(f"{len(long)} vět nad {R['max_sentence_words']} slov, např. „{long[0]}…“ (03)")
    if statistics.pstdev(lens) < R["min_sentence_len_stdev"]: W.append("věty mají skoro stejnou délku – monotónní rytmus (10)")
    starters = {}
    for s in sents:
        w = words(s.lower())
        if w: starters[w[0]] = starters.get(w[0], 0) + 1
    top = max(starters.items(), key=lambda x: x[1])
    if top[1] / len(sents) > R["max_same_starter_share"]: W.append(f"{top[1]} vět začíná „{top[0]}“ ({top[1]/len(sents):.0%}) (10)")
    andthen = sum(starters.get(w, 0) for w in R["and_then_starters"]); buttherefore = sum(starters.get(w, 0) for w in R["but_therefore_starters"])
    M["a pak × ale/proto"] = f"{andthen} × {buttherefore}"
    if andthen > buttherefore: W.append(f"víc vět začíná „a/pak“ ({andthen}) než „ale/proto“ ({buttherefore}) – seznam událostí místo příběhu (03)")
    conc = sum(concrete(s) for s in sents) / len(sents); M["konkrétní věty"] = f"{conc:.0%}"
    if conc < R["min_concrete_share"]: W.append(f"konkrétních vět {conc:.0%} < {R['min_concrete_share']:.0%} (10)")
    for sc in sl["scenes"]:
        if re.search(r"\d", sc["narration"]) and not sc.get("narration_tts"): E.append(f"{sc['id']}: číslice bez narration_tts (08)")
    missing_purpose = [sc["id"] for sc in sl["scenes"] if not sc.get("purpose")]
    if missing_purpose and len(missing_purpose) < len(sl["scenes"]): W.append(f"scény bez purpose: {', '.join(missing_purpose[:8])} (00)")

    # --- shot rhythm and visual mix
    durs = [s["dur"] for s in shots]; avg = statistics.mean(durs)
    M["záběry"] = f"{len(shots)}, průměr {avg:.1f} s, max {max(durs):.1f} s"
    if not R["avg_shot_min_s"] <= avg <= R["avg_shot_max_s"]: W.append(f"průměrná délka záběru {avg:.1f} s mimo {R['avg_shot_min_s']}–{R['avg_shot_max_s']} s (04)")
    static = [s for s in shots if s["template"] in R["static_templates"] and s["fx"] == "none" and s["dur"] > R["max_static_shot_s"]]
    for s in static[:10]: W.append(f"{s['scene']} {fmt(s['start'])}: statická karta {s['template']} {s['dur']:.1f} s (06)")
    if len(static) > 10: W.append(f"… a dalších {len(static) - 10} statických karet nad {R['max_static_shot_s']} s")
    run, prev = 1, None
    for s in shots:
        run = run + 1 if s["template"] == prev else 1; prev = s["template"]
        if run == R["max_same_template_run"] + 1: W.append(f"{s['scene']} {fmt(s['start'])}: {run}× za sebou {s['template']} (06)")
    moving = [i for i, s in enumerate(shots) if s["template"] in R["motion_templates"] or s["fx"] == "panel3d"]
    holes = [(b - a, a) for a, b in zip([-1] + moving, moving + [len(shots)]) if b - a > R["motion_every_n_shots"] + 1]
    if holes: W.append(f"{len(holes)}× víc než {R['motion_every_n_shots']} záběry za sebou bez pohybu/3D, např. od {shots[holes[0][1] + 1]['scene']} (04)")
    real = sum(s["dur"] for s in shots if s["template"] in R["real_or_evidence_templates"]) / sum(durs)
    txt = sum(s["dur"] for s in shots if s["template"] in R["text_card_templates"]) / sum(durs)
    M["skutečný obraz a doklady"] = f"{real:.0%} času"; M["textové karty"] = f"{txt:.0%} času"
    if real < R["min_real_or_evidence_share"]: W.append(f"skutečný obraz a doklady jen {real:.0%} času (cíl ≥ {R['min_real_or_evidence_share']:.0%}) (06, 12)")
    if txt > R["max_text_card_share"]: W.append(f"textové karty {txt:.0%} času (max {R['max_text_card_share']:.0%}) – slideshow riziko (10)")
    for sc in sl["scenes"]:
        if sc.get("claim_ids") and not sc.get("on_screen_source") and not any(v.get("asset_id") for v in sc["visuals"]):
            W.append(f"{sc['id']}: tvrzení bez dokladu v obraze (on_screen_source) (06)")

    # --- music and SFX
    music = sl.get("music") or {}
    if not music: W.append("střihový plán nemá hudbu (09)")
    else:
        cues = music.get("cues", {}); used = [sc.get("music_cue") for sc in sl["scenes"] if sc.get("music_cue")]
        if used and not any(cues.get(c, {}).get("silence") for c in used): W.append("hudba bez jediného ticha – ticho je nástroj, ne chyba (09)")
    sfx = [(st, x) for sc, st, *_ in times for x in sc.get("sfx", [])]
    M["SFX"] = f"{len(sfx)} ({len(sfx) / (total / 10):.2f} na 10 s)"
    if len(sfx) / (total / 10) > R["max_sfx_per_10s"]: W.append(f"moc efektů: {len(sfx)} na {fmt(total)} (09)")
    synth = sum(x in R["synthetic_sfx"] for _, x in sfx)
    if synth: W.append(f"{synth} syntetických efektů (whoosh/hit/…) – preferuj skutečné nahrávky, syntetika jen výjimečně (09)")

    # --- packaging
    tt = proj / "publish" / lang / "titles_thumbnails.md"
    if tt.exists():
        section = ""
        for line in tt.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"): section = line.lower(); continue
            m = re.match(r"\s*\d\.\s+(.+?)(\s+←.*)?$", line)
            if m and ("náz" in section or "title" in section or "titel" in section):
                t = m[1].strip()
                if len(t) > R["title_max_chars"]: W.append(f"název má {len(t)} znaků (> {R['title_max_chars']}): „{t}“ (02)")
    return E, W, M

def report(proj, lang, E, W, M):
    out = Path(proj) / f"craft_report.{lang}.md"
    lines = [f"# Kontrola řemesla – {Path(proj).name} ({lang})", "", "Pravidla: `knowledge/` · prahy: `knowledge/craft_rules.json`", "",
             "## Měření", *[f"- {k}: {v}" for k, v in M.items()], "", f"## ERROR ({len(E)})", *[f"- {e}" for e in E], "",
             f"## WARN ({len(W)})", *[f"- {w}" for w in W], ""]
    out.write_text("\n".join(lines), encoding="utf-8"); return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--lang", default="cs"); ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(); E, W, M = check(a.project, a.lang); out = report(a.project, a.lang, E, W, M)
    if not a.quiet:
        for k, v in M.items(): print(f"  {k}: {v}")
        for e in E: print("ERROR", e)
        for w in W: print("WARN ", w)
    print(f"{out.name}: {len(E)} ERROR, {len(W)} WARN"); sys.exit(1 if E else 0)

if __name__ == "__main__":
    main()
