"""Own sound effects synthesised in numpy (no third-party rights: origin "own").
Each function returns mono float32 at SR. `build_library()` writes them to pipeline/sfx/own/*.wav.
Anchor = where in the effect the "moment" is (the mixer aligns that point to the cue time)."""
import numpy as np, soundfile as sf, librosa
from scipy.signal import fftconvolve
from .common import PIPE

SR = 48000
rng = np.random.default_rng(7)

def _env(n, attack, release_curve=3.0):
    a = max(int(attack * SR), 1); e = np.ones(n, np.float32)
    e[:a] = np.linspace(0, 1, a); e[a:] = np.exp(-release_curve * np.linspace(0, 1, n - a)); return e

def _band_sweep(dur, f0, f1, width=0.35, shape=None):
    """Noise through a moving gaussian band (STFT mask): the core of whooshes and risers."""
    n = int(dur * SR); x = rng.standard_normal(n).astype(np.float32)
    S = librosa.stft(x, n_fft=2048, hop_length=256); freqs = librosa.fft_frequencies(sr=SR, n_fft=2048)
    T = S.shape[1]; t = np.linspace(0, 1, T); fc = f0 * (f1 / f0) ** (shape(t) if shape else t)
    lf = np.log2(freqs[:, None] + 1); mask = np.exp(-((lf - np.log2(fc[None, :])) ** 2) / (2 * width ** 2))
    return librosa.istft(S * mask, hop_length=256, length=n).astype(np.float32)

def reverb(x, tail=1.2, mix=0.25):
    n = int(tail * SR); ir = rng.standard_normal(n).astype(np.float32) * np.exp(-6 * np.linspace(0, 1, n)) ** 1.5
    ir /= np.abs(ir).sum() ** 0.5 * 4
    wet = fftconvolve(x, ir).astype(np.float32); out = np.zeros(len(wet), np.float32)
    out[: len(x)] += x; out += mix * wet; return out

def norm(x, peak=0.9): return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)

def whoosh(dur=0.7):
    x = _band_sweep(dur, 250, 2600, 0.45, shape=lambda t: np.sin(np.pi * t * 0.9))
    n = len(x); t = np.linspace(0, 1, n); e = np.sin(np.pi * t) ** 2.2
    return norm(reverb(x * e, 0.6, 0.2), 0.7), dur * 0.5

def hit(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 48 + 90 * np.exp(-t * 28); body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5)
    click = rng.standard_normal(n) * np.exp(-t * 90) * 0.5
    x = body + librosa.effects.preemphasis(click.astype(np.float32), coef=-0.9) * 0.3
    return norm(reverb(x.astype(np.float32), 0.8, 0.18)), 0.0

def impact(dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 36 + 70 * np.exp(-t * 12); sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    crack = _band_sweep(dur, 3000, 400, 0.6) * np.exp(-t * 9) * 0.6
    x = sub + crack
    return norm(reverb(x.astype(np.float32), 2.0, 0.35)), 0.0

def riser(dur=2.4):
    x = _band_sweep(dur, 180, 7000, 0.5, shape=lambda t: t ** 1.6)
    n = len(x); t = np.linspace(0, 1, n)
    tone = np.sin(2 * np.pi * np.cumsum(70 * (6 ** t)) / SR) * 0.35
    y = (x / (np.abs(x).max() + 1e-9) + tone) * t ** 2.4
    return norm(y.astype(np.float32), 0.75), dur  # anchor at the end: it lands on the cue

def heartbeat(beats=2, bpm=62):
    period = 60 / bpm; n = int(beats * period * SR + 0.5 * SR); out = np.zeros(n, np.float32)
    for b in range(beats):
        for off, amp in ((0.0, 1.0), (0.26, 0.7)):
            s = int((b * period + off) * SR); m = int(0.18 * SR); t = np.arange(m) / SR
            out[s:s + m] += amp * np.sin(2 * np.pi * (52 + 30 * np.exp(-t * 40)) * t) * np.exp(-t * 22)
    return norm(out, 0.9), 0.0

def roulette_tick(dur=2.2):
    """Decelerating ball-on-frets ticks."""
    out = np.zeros(int(dur * SR) + SR // 4, np.float32); t, gap = 0.0, 0.035
    while t < dur:
        m = int(0.012 * SR); tt = np.arange(m) / SR
        click = (np.sin(2 * np.pi * 3200 * tt) + 0.5 * rng.standard_normal(m)) * np.exp(-tt * 600)
        s = int(t * SR); out[s:s + m] += click.astype(np.float32) * (0.6 + 0.4 * rng.random())
        t += gap; gap *= 1.09
    return norm(reverb(out, 0.4, 0.15), 0.6), 0.0

def typewriter(n_keys=9, kenney_dir=None):
    """Key clicks from Kenney Interface Sounds (CC0) if present, else synthesised clicks."""
    clicks = sorted((kenney_dir or (PIPE / "sfx" / "kenney")).glob("click_*.ogg"))
    out = np.zeros(int(n_keys * 0.14 * SR) + SR // 2, np.float32); t = 0.0
    for i in range(n_keys):
        if clicks: c, _ = librosa.load(clicks[i % len(clicks)], sr=SR, mono=True)
        else:
            m = int(0.02 * SR); tt = np.arange(m) / SR; c = rng.standard_normal(m) * np.exp(-tt * 300)
        s = int(t * SR); out[s:s + len(c)] += c[: len(out) - s] * (0.7 + 0.3 * rng.random())
        t += 0.08 + 0.07 * rng.random()
    return norm(out, 0.55), 0.0

LIB = {"whoosh": whoosh, "hit": hit, "impact": impact, "riser": riser, "heartbeat": heartbeat,
       "roulette_tick": roulette_tick, "typewriter": typewriter}

def build_library():
    d = PIPE / "sfx" / "own"; d.mkdir(parents=True, exist_ok=True); anchors = {}
    for name, fn in LIB.items():
        y, anchor = fn(); sf.write(d / f"{name}.wav", y, SR, subtype="PCM_24"); anchors[name] = round(anchor, 3)
    return anchors
