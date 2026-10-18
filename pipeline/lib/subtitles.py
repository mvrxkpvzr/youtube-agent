"""SRT from the APPROVED text (never from the ASR transcript); ASR word times only position the cues."""
import difflib, json, re
from .asr_check import norm_words
from .common import load_shotlist, update_state

MAX_LINE, MAX_LINES, MAX_CPS, MIN_DUR = 42, 2, 17, 1.0

def chunks(text):
    """Split into cues of <= 2 lines x 42 chars, preferring sentence and comma boundaries."""
    out = []
    for sent in re.split(r"(?<=[^\d\s][.!?…])\s+", text.strip()):  # no split after "23." (ordinal)
        words, cur = sent.split(), ""
        for w in words:
            cand = (cur + " " + w).strip()
            if len(cand) > MAX_LINE * MAX_LINES:
                out.append(cur); cur = w
            else:
                cur = cand
                if cur.endswith((",", "–", ":")) and len(cur) > MAX_LINE: out.append(cur); cur = ""
        if cur: out.append(cur)
    return out

def wrap(cue):
    if len(cue) <= MAX_LINE: return cue
    words, best = cue.split(), None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) <= MAX_LINE and len(b) <= MAX_LINE:
            score = abs(len(a) - len(b))
            if best is None or score < best[0]: best = (score, a + "\n" + b)
    return best[1] if best else cue

def ts(t):
    h, m = int(t // 3600), int(t % 3600 // 60); s = t % 60
    return f"{h:02}:{m:02}:{int(s):02},{int(round((s - int(s)) * 1000)):03}"

def build(proj, lang):
    sl = load_shotlist(proj, lang); d = proj / "audio" / lang
    timings = {t["id"]: t for t in json.loads((d / "timings.json").read_text())}
    cues, warnings = [], []
    for sc in sl["scenes"]:
        t0, t1 = timings[sc["id"]]["start"], timings[sc["id"]]["end"]; off = timings[sc["id"]].get("trim_offset", 0)
        wpath = d / f"{sc['id']}.words.json"
        asr = json.loads(wpath.read_text()) if wpath.exists() else []
        aw = [norm_words(w["w"])[0] if norm_words(w["w"]) else "" for w in asr]
        parts = chunks(sc["narration"]); ref_tokens, owner = [], []
        for ci, p in enumerate(parts):
            toks = norm_words(p); ref_tokens += toks; owner += [ci] * len(toks)
        times = [None] * len(ref_tokens)
        sm = difflib.SequenceMatcher(a=ref_tokens, b=aw, autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n): times[a + k] = (asr[b + k]["start"] - off, asr[b + k]["end"] - off)
        total_chars = sum(len(p) for p in parts) or 1; acc = 0
        for ci, p in enumerate(parts):
            idx = [i for i, o in enumerate(owner) if o == ci and times[i]]
            if idx:
                s, e = t0 + times[idx[0]][0], t0 + times[idx[-1]][1]
            else:  # proportional fallback
                s = t0 + (t1 - t0) * acc / total_chars; e = t0 + (t1 - t0) * (acc + len(p)) / total_chars
            acc += len(p); cues.append([s, e, wrap(p)])
    for i, c in enumerate(cues):  # make cues contiguous-ish and readable
        nxt = cues[i + 1][0] if i + 1 < len(cues) else c[1] + 1.5
        c[1] = max(c[1], min(c[0] + MIN_DUR, nxt - 0.05)); c[1] = min(c[1] + 0.25, nxt - 0.05)
        cps = len(c[2].replace("\n", "")) / max(c[1] - c[0], 0.01)
        if cps > MAX_CPS: warnings.append(f"titulek {i+1}: {cps:.0f} zn./s > {MAX_CPS}")
    out = proj / "render" / f"subtitles.{lang}.srt"; out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(f"{i+1}\n{ts(s)} --> {ts(e)}\n{t}\n" for i, (s, e, t) in enumerate(cues)), encoding="utf-8")
    update_state(proj, f"subtitles_{lang}", "done", inputs=[proj / f"shotlist.{lang}.json", d / "timings.json"], outputs=[out],
                 warnings=len(warnings))
    return out, warnings
