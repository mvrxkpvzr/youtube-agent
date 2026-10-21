"""SRT from the APPROVED text (never from the ASR transcript); ASR word times only position the cues."""
import difflib, json, re
from .asr_check import norm_words, raw_words
from .csnum import collapse
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

def fill_gaps(times, dur):
    """Unmatched tokens (ASR merged or misheard words) get times interpolated between matched neighbours,
    so a cue never relies on one stray match far away. Times are scene-relative; scene spans 0..dur."""
    n = len(times); known = [i for i, t in enumerate(times) if t]
    if not known: return [(dur * i / max(n, 1), dur * (i + 1) / max(n, 1)) for i in range(n)]
    out = list(times)
    for i in range(n):
        if out[i]: continue
        prv = max((k for k in known if k < i), default=None); nxt = min((k for k in known if k > i), default=None)
        a = times[prv][1] if prv is not None else 0.0; b = times[nxt][0] if nxt is not None else dur
        lo = prv if prv is not None else -1; hi = nxt if nxt is not None else n
        if b < a: b = a
        f0, f1 = (i - lo - 1) / (hi - lo - 1), (i - lo) / (hi - lo - 1)
        out[i] = (a + (b - a) * f0, a + (b - a) * f1)
    return out

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
        # ASR tokens with times; numbers merged across words ("26" "191" "306" -> one token spanning all three)
        raw = [(t, (w["start"] - off, w["end"] - off)) for w in asr for t in raw_words(w["w"])]
        aw, at = collapse([t for t, _ in raw], [x for _, x in raw], merge=lambda a, b: (a[0], b[1]))
        parts = chunks(sc["narration"]); ref_tokens, owner = [], []
        for ci, p in enumerate(parts):
            toks = norm_words(p); ref_tokens += toks; owner += [ci] * len(toks)
        times = [None] * len(ref_tokens)
        sm = difflib.SequenceMatcher(a=ref_tokens, b=aw, autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n): times[a + k] = at[b + k]
        times = fill_gaps(times, t1 - t0)
        for ci, p in enumerate(parts):
            idx = [i for i, o in enumerate(owner) if o == ci]
            if idx: s, e = t0 + times[idx[0]][0], t0 + times[idx[-1]][1]
            else: s = e = t0
            cues.append([s, max(e, s), wrap(p)])
    for i in range(1, len(cues)):  # never start before the previous cue (ASR can mis-order merged/garbled words)
        if cues[i][0] < cues[i - 1][0] + 0.05: cues[i][0] = cues[i - 1][0] + 0.05; cues[i][1] = max(cues[i][1], cues[i][0])
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
