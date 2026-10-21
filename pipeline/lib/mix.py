"""Narration + music bed (from scene music_cue, ducked under speech) + SFX (scene sfx + whoosh on motion shots) -> mix.wav.
Levels are set in LUFS (pyloudnorm, ITU-R BS.1770): voice, every music track and every SFX are normalised first, so the
gains in shotlist["music"] are true loudness offsets relative to the voice. Processing uses pedalboard (Spotify, GPL-3.0).
Music cues live in shotlist["music"]["cues"]: {cue: {"asset": "A101", "at": seconds_into_track} | {"silence": true}}.
A scene with music_cue null keeps the current bed; after a silence the previous track resumes as if it had kept playing."""
import json, subprocess
import numpy as np, soundfile as sf, librosa, pyloudnorm
from pedalboard import Pedalboard, HighpassFilter, PeakFilter, HighShelfFilter, Compressor, Reverb
from .common import cfg, load_shotlist, update_state, PIPE
from .render import plan, jsonl

SR = 48000

def db(x): return 10 ** (x / 20)

def load(path):
    y, _ = librosa.load(str(path), sr=SR, mono=True); return y.astype(np.float32)

METER = pyloudnorm.Meter(SR)
VOICE_LUFS = -16.0  # narration is normalised here; music/SFX gains are LU relative to it

def lufs(y):
    return METER.integrated_loudness(np.pad(y, (0, max(0, int(0.5 * SR) - len(y)))).astype(np.float64))

def to_lufs(y, target):
    L = lufs(y); return y if not np.isfinite(L) else (y * db(target - L)).astype(np.float32)

def fx(board, y):
    return board(y[None, :].astype(np.float32), SR)[0]

VOICE_CHAIN = Pedalboard([HighpassFilter(75), PeakFilter(300, -2.0, 1.0), Compressor(-22, 3.0, 4, 120),
                          PeakFilter(3500, 2.0, 0.9), HighShelfFilter(9000, -1.5)])
MUSIC_EQ = Pedalboard([HighpassFilter(35), PeakFilter(2500, -3.5, 0.8)])  # carve space for the voice
SFX_GLUE = Pedalboard([Reverb(room_size=0.25, wet_level=0.12, dry_level=1.0, width=0.8)])
# no pedalboard Limiter here: JUCE's limiter adds make-up gain (= -threshold) and shifts the whole balance;
# true peaks are handled by the two-pass loudnorm (TP -1.5) in render.master_audio

def to_lufs_capped(y, target, peak_db=-3.0):
    """Short transients read low in integrated LUFS – also cap the sample peak."""
    y = to_lufs(y, target); pk = np.abs(y).max()
    return y if pk <= db(peak_db) else (y * db(peak_db) / pk).astype(np.float32)

def rms_db(y):
    return 20 * np.log10(np.sqrt(np.mean(y.astype(np.float64) ** 2)) + 1e-9)

def smooth(env, attack_s, release_s, hop_s):
    out = np.zeros_like(env); a, r = np.exp(-hop_s / attack_s), np.exp(-hop_s / release_s); v = 0.0
    for i, x in enumerate(env):
        c = a if x > v else r; v = c * v + (1 - c) * x; out[i] = v
    return out

def scene_starts(proj, lang):
    shots, total = plan(proj, lang); starts, t = {}, 0.0
    for s in shots:
        starts.setdefault(s["scene"], t); s["t0"] = t; t += s["dur"]
    return shots, starts, total

def music_bed(proj, sl, starts, total, n):
    m = sl.get("music", {}); cues = m.get("cues", {}); assets = jsonl(proj / "assets.jsonl")
    xf = m.get("crossfade_s", 0.6); bed = np.zeros(n, np.float32); cache = {}
    events, sc_list = [], sl["scenes"]
    for k, sc in enumerate(sc_list):
        cue = cues.get(sc.get("music_cue") or "")
        if cue: events.append((starts[sc["id"]], cue))
        if cue and cue.get("silence") and k + 1 < len(sc_list) and not cues.get(sc_list[k + 1].get("music_cue") or ""):
            events.append((starts[sc_list[k + 1]["id"]], {"resume": True}))  # a silence lasts one scene only
    events.sort(key=lambda e: e[0]); cur = None; cur_gain = 1.0  # (asset, track_time_at_t0, t0)
    for i, (t, cue) in enumerate(events):
        t_end = events[i + 1][0] if i + 1 < len(events) else total
        if cue.get("silence"):
            continue  # bed stays empty; `cur` keeps running in the background
        if cue.get("resume") and cur:
            asset, at = cur[0], cur[1] + (t - cur[2])
        else:
            asset, at = cue["asset"], cue.get("at", 0.0)
        cur = (asset, at, t)
        g = db(cue.get("gain_db", 0.0)) if not cue.get("resume") else cur_gain
        cur_gain = g
        if asset not in cache:
            cache[asset] = to_lufs(fx(MUSIC_EQ, load(proj / assets[asset]["file"])), VOICE_LUFS)  # every track at voice loudness
        y = cache[asset]; a, b = int(t * SR), min(int(t_end * SR) + int(xf * SR), n)
        seg = y[int(at * SR): int(at * SR) + (b - a)]
        if len(seg) < b - a: seg = np.pad(seg, (0, b - a - len(seg)))
        fade = np.ones(b - a, np.float32); k = min(int(xf * SR), (b - a) // 2)
        fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.minimum(fade[-k:], np.linspace(1, 0, k))
        if i + 1 >= len(events): fade[-int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR))  # final fade-out
        # events that silence the bed or end the video: cut on the cue instead of overlapping into it
        nxt_silent = i + 1 < len(events) and events[i + 1][1].get("silence")
        if nxt_silent: fade[int(t_end * SR) - a:] = 0; fade[max(int(t_end * SR) - a - int(0.08 * SR), 0): int(t_end * SR) - a] *= np.linspace(1, 0, min(int(0.08 * SR), int(t_end * SR) - a))
        bed[a:b] += seg * fade * g
    return bed

def place_sfx(shots, sl, starts, n, anchors):
    lane = np.zeros(n, np.float32); used = []
    gains = sl.get("music", {}).get("sfx_gain_db", {})
    def put(name, t, gain_db):
        y = to_lufs_capped(load(PIPE / "sfx" / "own" / f"{name}.wav"), VOICE_LUFS); s = int((t - anchors.get(name, 0.0)) * SR)
        if s < 0: y, s = y[-s:], 0
        e = min(s + len(y), n); lane[s:e] += y[: e - s] * db(gain_db); used.append((round(t, 2), name))
    for sc in sl["scenes"]:
        for name in sc.get("sfx", []):
            put(name, starts[sc["id"]], gains.get(name, -6))
    for s in shots:  # motion/3D shots get a soft whoosh into the cut
        if gains.get("auto_whoosh", -14) <= -60: break   # turned off (e.g. -120 = no synthetic effects)
        if s["template"] == "motion" and s["t0"] > 0.5 and not any(abs(u[0] - s["t0"]) < 0.3 for u in used):
            put("whoosh", s["t0"], gains.get("auto_whoosh", -14))
    return lane, sorted(used)

def mix(proj, lang):
    c = cfg(); sl = load_shotlist(proj, lang); m = sl.get("music", {}); d = proj / "audio" / lang
    anchors = json.loads((PIPE / "sfx" / "own" / "anchors.json").read_text())
    # narration through the voice chain, then to VOICE_LUFS (the chain must not touch music/SFX)
    nar_p = d / "narration.proc.wav"
    voice = to_lufs(fx(VOICE_CHAIN, load(d / "narration.wav")), VOICE_LUFS); sf.write(nar_p, voice, SR, subtype="PCM_24")
    shots, starts, total = scene_starts(proj, lang)
    n = max(len(voice), int((total + 0.5) * SR)); voice = np.pad(voice, (0, n - len(voice)))
    # speech activity -> ducking envelope (50 ms frames)
    hop = int(0.05 * SR); frames = len(voice) // hop
    act = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2)) for i in range(frames)])
    vdb = 20 * np.log10(act + 1e-9); speech = (vdb > np.percentile(vdb[vdb > -80], 30) - 6).astype(np.float32)
    duck = smooth(speech, 0.06, 0.45, 0.05); duck = np.repeat(duck, hop); duck = np.pad(duck, (0, n - len(duck)), constant_values=duck[-1])
    under, gaps = m.get("level_under_voice_db", -18), m.get("level_in_gaps_db", -11)
    bed = music_bed(proj, sl, starts, total, n)
    bed_gain = db(gaps) + (db(under) - db(gaps)) * duck  # LU below the voice
    lane, used = place_sfx(shots, sl, starts, n, anchors)
    out = voice + bed * bed_gain + fx(SFX_GLUE, lane)[:n]
    out = (out / max(1.0, np.abs(out).max() / 0.98)).astype(np.float32)
    path = d / "mix.wav"; sf.write(path, out.astype(np.float32), SR, subtype="PCM_24")
    update_state(proj, f"mix_{lang}", "done", inputs=[proj / f"shotlist.{lang}.json", d / "narration.wav"], outputs=[path],
                 sfx=[f"{t}s {nme}" for t, nme in used])
    return path, used
