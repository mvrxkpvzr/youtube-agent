"""Czech number words -> digits, so the approved text (numbers spelled out for TTS) and Whisper's
transcript (digits) compare word for word: "padesát sedm tisíc čtyři sta čtyřicet tři" == "57 443" -> "57443".
Works on a token list; each token may carry a payload (e.g. ASR word times) that merged tokens combine."""
import re

_U = {1: "jeden jedna jedno jednoho jednomu jedné jednom jedním", 2: "dva dvě dvou dvěma", 3: "tři tří třem třemi",
      4: "čtyři čtyř čtyřem čtyřech čtyřmi", 5: "pět pěti", 6: "šest šesti", 7: "sedm sedmi", 8: "osm osmi",
      9: "devět devíti", 0: "nula"}
_T = {10: "deset", 11: "jedenáct", 12: "dvanáct", 13: "třináct", 14: "čtrnáct", 15: "patnáct", 16: "šestnáct",
      17: "sedmnáct", 18: "osmnáct", 19: "devatenáct"}
_D = {20: "dvacet", 30: "třicet", 40: "čtyřicet", 50: "padesát", 60: "šedesát", 70: "sedmdesát", 80: "osmdesát",
      90: "devadesát"}
_ORD = {1: "prv", 2: "druh", 3: "třet", 4: "čtvrt", 5: "pát", 6: "šest", 7: "sedm", 8: "osm", 9: "devát", 10: "desát",
        11: "jedenáct", 12: "dvanáct", 13: "třináct", 14: "čtrnáct", 15: "patnáct", 16: "šestnáct", 17: "sedmnáct",
        18: "osmnáct", 19: "devatenáct", 20: "dvacát", 30: "třicát"}
_ORD_SUF = r"(?:ý|ého|ému|ém|ým|á|é|ou|í|ího|ímu|ím)"
_COMP = r"(jedn|dva|tři|čtyři|pět|šest|sedm|osm|devět)a"   # třiadvacet, třiadvacátého

WORDS = {}
for v, s in _U.items():
    for w in s.split(): WORDS[w] = ("unit", v)
for v, w in list(_T.items()) + list(_D.items()):
    WORDS[w] = ("unit" if v < 20 else "ten", v); WORDS[w + "i"] = WORDS[w]
for w in "sto sta stě set stech stům sty".split(): WORDS[w] = ("hund", 100)
for w in "tisíc tisíce tisících tisícům tisíci".split(): WORDS[w] = ("mult", 1000)
for w in "milion miliony milionů milionech milionu milionům".split(): WORDS[w] = ("mult", 10**6)
for w in "miliarda miliardy miliard miliardách miliardu".split(): WORDS[w] = ("mult", 10**9)
_UNIT_OF = {"jedn": 1, "dva": 2, "tři": 3, "čtyři": 4, "pět": 5, "šest": 6, "sedm": 7, "osm": 8, "devět": 9}
_TEN_OF = {v: w for w, (k, v) in WORDS.items() if k == "ten"}

def word_value(w):
    """('unit'|'ten'|'hund'|'mult'|'num', value) or None."""
    if w in WORDS: return WORDS[w]
    if re.fullmatch(r"\d+", w): return ("num", int(w))
    if re.fullmatch(r"\d+\.\d+", w): return ("num", float(w))
    m = re.fullmatch(_COMP + r"(dvacet|třicet|čtyřicet|padesát|šedesát|sedmdesát|osmdesát|devadesát)i?", w)
    if m: return ("unit", _UNIT_OF[m[1]] + WORDS[m[2]][1])
    m = re.fullmatch(_COMP + r"(dvacát|třicát)" + _ORD_SUF, w)
    if m: return ("ord", _UNIT_OF[m[1]] + {"dvacát": 20, "třicát": 30}[m[2]])
    if re.fullmatch(r"prvn(?:í|ího|ímu|ím|ími|ích)", w): return ("ord", 1)
    for v, stem in _ORD.items():
        if re.fullmatch(stem + _ORD_SUF, w): return ("ord", v)
    return None

def collapse(tokens, payloads=None, merge=lambda a, b: a):
    """Merge runs of number tokens into one digit token. Returns (tokens, payloads)."""
    payloads = payloads if payloads is not None else [None] * len(tokens)
    # 1) digit groups written with spaces: "26 191 306" -> "26191306"
    toks, pays, grouped = [], [], []
    for t, p in zip(tokens, payloads):
        if toks and re.fullmatch(r"\d{3}", t) and (grouped[-1] or re.fullmatch(r"\d{1,3}", toks[-1])):
            toks[-1] += t; pays[-1] = merge(pays[-1], p); grouped[-1] = True; continue
        toks.append(t); pays.append(p); grouped.append(False)
    # 2) number words
    out, outp = [], []
    total = cur = 0; last = None; last_val = 0; start = None; p_acc = None

    def flush():
        nonlocal total, cur, last, start, p_acc, last_val
        if start is not None:
            v = round(total + cur, 6); out.append(str(int(v)) if v == int(v) else str(v)); outp.append(p_acc)
        total = cur = 0; last = None; start = None; p_acc = None; last_val = 0

    i = -1; last_ord = None
    while i + 1 < len(toks):
        i += 1; t, p = toks[i], pays[i]
        if start is not None and last in ("unit", "ten") and t == "a" and toks[i + 1:i + 2] == ["půl"]:
            cur += 0.5; p_acc = merge(p_acc, pays[i + 1]); i += 1; last = "half"; continue  # "dva a půl tisíce"
        wv = word_value(t)
        if wv is None:
            flush(); out.append(t); outp.append(p); last_ord = None; continue
        kind, v = wv
        if kind == "ord":
            flush()
            if out and last_ord and last_ord % 10 == 0 and last_ord >= 20 and v < 10:   # "dvacátého osmého" -> 28
                out[-1] = str(last_ord + v); outp[-1] = merge(outp[-1], p); last_ord = None; continue
            out.append(str(v)); outp.append(p); last_ord = v; continue
        last_ord = None
        if kind == "num":
            flush(); start = i; p_acc = p; cur = v; last = "unit"; last_val = v; continue
        ok = start is not None
        if kind == "unit" and ok and last not in ("ten", "hund", "mult"): flush(); ok = False
        if kind == "ten" and ok and last not in ("hund", "mult"): flush(); ok = False
        if kind == "hund" and ok and last == "hund": flush(); ok = False
        if kind == "mult" and ok and last == "mult": flush(); ok = False
        if kind != "mult" and last == "half": flush(); ok = False
        if not ok: start = i; p_acc = p
        else: p_acc = merge(p_acc, p)
        if kind in ("unit", "ten"): cur += v; last_val = v
        elif kind == "hund":
            if last == "unit" and start != i: cur = cur - last_val + last_val * 100
            else: cur += 100
        else:
            total += (cur or 1) * v; cur = 0
        last = kind
    flush()
    return out, outp
