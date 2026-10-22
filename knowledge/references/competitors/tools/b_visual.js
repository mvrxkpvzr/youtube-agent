// Step B on a loaded watch page (run after a_text.js). Starts a background job; poll window.__B.status.
// 1) contact sheets: 40 frames across the whole video + 30 frames of the first 90 s (seek + canvas, nothing saved);
// 2) cut estimate in 3 windows played muted at 4x: histogram difference between frames 0.2 s apart (video time);
// 3) loudness per 0.25 s in the same windows via WebAudio (routed to a zero-gain node, nothing audible).
window.__B = { status: 'running' };
(async () => {
  const B = window.__B, v = document.querySelector('video'), D = v.duration;
  const fmt = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  v.pause(); v.muted = true;
  const seek = t => new Promise(r => { const f = () => { v.removeEventListener('seeked', f); setTimeout(r, 120); }; v.addEventListener('seeked', f); v.currentTime = t; });
  const sheet = async (times, cols, label) => {
    const W = 200, H = 112, rows = Math.ceil(times.length / cols);
    const c = document.createElement('canvas'); c.width = W * cols; c.height = (H + 14) * rows; const x = c.getContext('2d');
    x.fillStyle = '#000'; x.fillRect(0, 0, c.width, c.height); x.font = '12px sans-serif';
    for (let i = 0; i < times.length; i++) { await seek(times[i]); const cx = (i % cols) * W, cy = Math.floor(i / cols) * (H + 14); x.drawImage(v, cx, cy + 14, W - 2, H - 2); x.fillStyle = '#ff0'; x.fillText(fmt(times[i]), cx + 2, cy + 11); }
    c.title = label; return c;
  };
  try {
    B.status = 'sheets';
    const whole = await sheet(Array.from({ length: 40 }, (_, i) => Math.min(D - 1, 5 + i * (D - 10) / 39)), 8, 'whole');
    const hook = await sheet(Array.from({ length: 30 }, (_, i) => 1 + i * 3), 10, 'hook 0-90s');
    let ov = document.getElementById('__vis'); if (ov) ov.remove();
    ov = document.createElement('div'); ov.id = '__vis';
    ov.style.cssText = 'position:fixed;inset:0;z-index:99999;background:#111;overflow:auto;padding:4px';
    const th = new Image(); th.src = `https://i.ytimg.com/vi/${new URLSearchParams(location.search).get('v')}/maxresdefault.jpg`; th.style.cssText = 'width:480px;display:block;margin-bottom:4px';
    [whole, hook].forEach(c => { c.style.cssText = 'width:100%;display:block;margin-bottom:4px'; });
    ov.append(th, whole, hook); document.body.appendChild(ov); ov.style.display = 'none';
    // audio graph (best effort)
    let an = null;
    try { const ac = new AudioContext(); const src = ac.createMediaElementSource(v); an = ac.createAnalyser(); an.fftSize = 2048; const g = ac.createGain(); g.gain.value = 0; src.connect(an); an.connect(g); g.connect(ac.destination); await ac.resume(); B.audio_ctx = ac.state; v.muted = false; v.volume = 1; } catch (e) { B.audio_ctx = 'ERR ' + e; }
    const buf = an ? new Float32Array(an.fftSize) : null;
    const wins = [[0, 120], [D / 2 - 60, D / 2 + 60], [Math.max(0, D - 150), Math.max(0, D - 30)]];
    const c = new OffscreenCanvas(64, 36), x = c.getContext('2d', { willReadFrequently: true });
    B.windows = [];
    for (const [a, b] of wins) {
      B.status = `window ${fmt(a)}-${fmt(b)}`;
      await seek(a); v.playbackRate = 4; await v.play();
      let prev = null, lastCut = -9, cuts = [], dark = 0, n = 0, rms = [];
      while (v.currentTime < b && !v.paused && !v.ended) {
        x.drawImage(v, 0, 0, 64, 36); const d = x.getImageData(0, 0, 64, 36).data; const h = new Float32Array(48); let lum = 0;
        for (let p = 0; p < d.length; p += 4) { h[d[p] >> 4]++; h[16 + (d[p + 1] >> 4)]++; h[32 + (d[p + 2] >> 4)]++; lum += d[p] + d[p + 1] + d[p + 2]; }
        const N = d.length / 4; n++; if (lum / N / 765 < 0.05) dark++;
        if (prev) { let s = 0; for (let k = 0; k < 48; k++) s += Math.abs(h[k] - prev[k]) / N; s /= 3; const t = v.currentTime; if (s > 0.5 && t - lastCut > 0.6) { cuts.push(+t.toFixed(1)); lastCut = t; } }
        prev = h;
        if (an) { an.getFloatTimeDomainData(buf); let q = 0; for (const s of buf) q += s * s; rms.push(10 * Math.log10(q / buf.length + 1e-10)); }
        await new Promise(r => setTimeout(r, 50));
      }
      v.pause();
      const span = Math.max(1, Math.min(b, v.currentTime) - a);
      const st = rms.length ? { db_med: +rms.slice().sort((p, q) => p - q)[rms.length >> 1].toFixed(1), quiet_pct: Math.round(100 * rms.filter(r => r < -45).length / rms.length), db_p90: +rms.slice().sort((p, q) => p - q)[Math.floor(rms.length * 0.9)].toFixed(1) } : null;
      B.windows.push({ win: `${fmt(a)}-${fmt(b)}`, cuts: cuts.length, cuts_per_min: +(cuts.length / span * 60).toFixed(1), avg_shot_s: +(span / (cuts.length + 1)).toFixed(1), dark_pct: Math.round(100 * dark / Math.max(1, n)), cut_times: cuts.map(fmt).join(' '), audio: st });
    }
    v.playbackRate = 1; v.muted = true; v.currentTime = 0; v.pause();
    B.status = 'done';
  } catch (e) { B.status = 'ERR ' + e; }
})();
'started'
