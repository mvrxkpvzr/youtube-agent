// Run in the context of a loaded https://www.youtube.com/watch?v=... page (Claude in Chrome javascript_tool).
// Reads only public metadata, captions and storyboard thumbnails for analysis; nothing is downloaded or republished.
// Returns {meta, chapters, transcript:[{t,text}], storyboard:{level, interval_s, frames, cuts_est, cut_times}}.
(async () => {
  const pr = window.ytInitialPlayerResponse;
  const vd = pr.videoDetails, mf = pr.microformat?.playerMicroformatRenderer || {};
  const meta = {
    video_id: vd.videoId, title: vd.title, channel: vd.author, runtime_s: +vd.lengthSeconds,
    published: mf.publishDate || mf.uploadDate || null, views: +vd.viewCount,
    description: (vd.shortDescription || '').slice(0, 4000),
  };
  // Chapters from the description ("0:00 Intro" lines).
  const chapters = [];
  for (const line of meta.description.split('\n')) {
    const m = line.match(/^\s*\(?((?:\d+:)?\d{1,2}:\d{2})\)?\s*[-–—]?\s*(.+)$/);
    if (m) chapters.push({ t: m[1].split(':').reduce((a, b) => a * 60 + +b, 0), title: m[2].trim() });
  }
  // Captions: prefer manual English, else auto English.
  let transcript = [], caption_kind = null;
  const tracks = pr.captions?.playerCaptionsTracklistRenderer?.captionTracks || [];
  const tr = tracks.find(t => t.languageCode?.startsWith('en') && t.kind !== 'asr') || tracks.find(t => t.languageCode?.startsWith('en')) || tracks[0];
  if (tr) {
    caption_kind = tr.kind === 'asr' ? 'auto' : 'manual';
    try {
      const j = await (await fetch(tr.baseUrl + '&fmt=json3')).json();
      transcript = (j.events || []).filter(e => e.segs).map(e => ({ t: +(e.tStartMs / 1000).toFixed(1), text: e.segs.map(s => s.utf8).join('').replace(/\n/g, ' ').trim() })).filter(x => x.text);
    } catch (e) { transcript = [{ t: 0, text: 'CAPTION_FETCH_FAILED ' + e }]; }
  }
  // Storyboard: estimate hard cuts from frame-to-frame difference of the public thumbnail sprites.
  let storyboard = null;
  const spec = pr.storyboards?.playerStoryboardSpecRenderer?.spec;
  if (spec) {
    const parts = spec.split('|'), base = parts[0];
    const L = parts.length - 2; // highest level
    const [w, h, count, cols, rows, intervalMs, name, sigh] = parts[L + 1].split('#');
    const per = cols * rows, sheets = Math.ceil(count / per);
    const frames = [];
    for (let s = 0; s < sheets; s++) {
      let url = base.replace('$L', L).replace('$N', name.replace('$M', s)) + '&sigh=' + sigh;
      try {
        const blob = await (await fetch(url)).blob();
        const bmp = await createImageBitmap(blob);
        const c = new OffscreenCanvas(bmp.width, bmp.height), x = c.getContext('2d');
        x.drawImage(bmp, 0, 0);
        for (let i = 0; i < per && frames.length < count; i++) {
          const fx = (i % cols) * w, fy = Math.floor(i / cols) * h;
          const d = x.getImageData(fx, fy, +w, +h).data;
          const hist = new Array(48).fill(0); let lum = 0;
          for (let p = 0; p < d.length; p += 16) { hist[d[p] >> 4]++; hist[16 + (d[p + 1] >> 4)]++; hist[32 + (d[p + 2] >> 4)]++; lum += d[p] + d[p + 1] + d[p + 2]; }
          const n = d.length / 16;
          frames.push({ hist: hist.map(v => v / n), lum: lum / n / 765 });
        }
      } catch (e) { storyboard = { error: String(e), url }; break; }
    }
    if (!storyboard) {
      const iv = +intervalMs / 1000 || (meta.runtime_s / count);
      const diffs = frames.slice(1).map((f, i) => f.hist.reduce((a, v, k) => a + Math.abs(v - frames[i].hist[k]), 0) / 3);
      const cut_times = diffs.map((d, i) => d > 0.45 ? +((i + 1) * iv).toFixed(1) : null).filter(v => v !== null);
      const dark = frames.map((f, i) => f.lum < 0.06 ? +(i * iv).toFixed(1) : null).filter(v => v !== null);
      storyboard = { level: L, interval_s: +iv.toFixed(2), frames: frames.length, cuts_est: cut_times.length, cut_times, dark_frames: dark };
    }
  }
  return { meta, chapters, caption_kind, transcript, storyboard };
})()
