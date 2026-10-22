// Step A on a loaded watch page: metadata, chapters, most-replayed peaks, transcript (via the page's own transcript panel).
// Result is put in window.__A and shown in an overlay <article> so get_page_text can read it (it is not saved anywhere).
(async () => {
  const v = document.querySelector('video'); if (v) { v.muted = true; v.pause(); }
  const pr = document.querySelector('#movie_player').getPlayerResponse();
  const vd = pr.videoDetails, mf = pr.microformat?.playerMicroformatRenderer || {};
  const fmt = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  const meta = { id: vd.videoId, title: vd.title, channel: vd.author, runtime_s: +vd.lengthSeconds, published: (mf.publishDate || '').slice(0, 10), views: +vd.viewCount };
  // most replayed
  let heat = [];
  const walk = o => { if (!o || typeof o !== 'object') return; if (o.markerType === 'MARKER_TYPE_HEATMAP' && o.markers) { heat = o.markers; return; } for (const k in o) walk(o[k]); };
  walk(window.ytInitialData);
  const peaks = heat.map(m => [+m.startMillis / 1000, +m.intensityScoreNormalized]).filter((m, i, a) => i > 0 && i < a.length - 1 && m[1] >= a[i - 1][1] && m[1] >= a[i + 1][1] && m[1] > 0.35).sort((a, b) => b[1] - a[1]).slice(0, 6);
  const early = heat.slice(0, 5).map(m => (+m.intensityScoreNormalized).toFixed(2));
  // transcript
  const btn = document.querySelector('ytd-video-description-transcript-section-renderer button');
  let segs = [...document.querySelectorAll('transcript-segment-view-model, ytd-transcript-segment-renderer')];
  if (btn && !segs.length) btn.click();
  for (let i = 0; i < 20 && !segs.length; i++) { await new Promise(r => setTimeout(r, 700)); segs = [...document.querySelectorAll('transcript-segment-view-model, ytd-transcript-segment-renderer')]; }
  const toS = t => t.split(':').reduce((a, b) => a * 60 + +b, 0);
  const lines = segs.map(e => { const ts = e.querySelector('[class*="Timestamp"], .segment-timestamp')?.textContent.trim(); if (!ts || !/^\d+:\d+/.test(ts)) return null; const tx = [...e.querySelectorAll('span, .segment-text')].map(x => x.textContent).join(' ').replace(/\s+/g, ' ').trim() || e.textContent.replace(ts, '').trim(); return [toS(ts), tx.replace(/^\d+:\d+\s*/, '')]; }).filter((l, i, a) => l && a.findIndex(m => m && m[0] === l[0] && m[1] === l[1]) === i);
  const chapters = [...document.querySelectorAll('[class*="SectionHeader"], ytd-transcript-section-header-renderer')].map(e => e.textContent.trim()).filter(Boolean);
  // merge into ~20 s blocks; mark narration gaps >= 3 s
  const blocks = []; let cur = null, gaps = [];
  lines.forEach(([t, tx], i) => { if (i) { const pt = lines[i - 1][0]; const est = pt + lines[i - 1][1].split(' ').length / 2.6; if (t - est >= 3) gaps.push([Math.round(est), Math.round(t - est)]); } if (!cur || t - cur.t >= 20) { cur = { t, tx: [] }; blocks.push(cur); } cur.tx.push(tx); });
  const words = lines.reduce((a, l) => a + l[1].split(' ').length, 0);
  window.__A = { meta, peaks, early, chapters, n_lines: lines.length, words, wpm: Math.round(words / (meta.runtime_s / 60)), gaps };
  const head = `${meta.title} | ${meta.channel} | ${meta.published} | ${fmt(meta.runtime_s)} | views ${meta.views}\nwords ${words}, wpm ${window.__A.wpm}, lines ${lines.length}\nchapters: ${chapters.join(' / ')}\nmost-replayed peaks: ${peaks.map(p => fmt(p[0]) + '=' + p[1].toFixed(2)).join(', ')}; first 5 buckets: ${early.join(' ')}\nnarration gaps>=3s: ${gaps.map(g => fmt(g[0]) + '(' + g[1] + 's)').join(', ')}\n---\n`;
  const body = blocks.map(b => `[${fmt(b.t)}] ${b.tx.join(' ')}`).join('\n');
  let art = document.getElementById('__ov'); if (!art) { art = document.createElement('article'); art.id = '__ov'; document.body.appendChild(art); }
  art.textContent = head + body;
  return head.length + body.length;
})()
