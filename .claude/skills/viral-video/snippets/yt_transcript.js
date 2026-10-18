// Run in the YouTube watch page (Claude in Chrome javascript_tool) AFTER clicking "Zobrazit přepis".
// Cleans the transcript panel into "m:ss<TAB>text" lines and puts it into a hidden <main id="__trdump">,
// so get_page_text can read the whole thing (javascript_tool output is truncated, get_page_text is not).
// For texts > 50 000 chars, set window.__OFFSET and re-run the last line to dump the next part.
const segs = [...document.querySelectorAll('ytd-transcript-segment-renderer, transcript-segment-view-model')]
  .map(s => s.textContent.replace(/\s+/g, ' ').trim());
const clean = s => {
  const ts = (s.match(/^(\d+:\d{2}(?::\d{2})?)/) || [])[1];
  const t = s.replace(/^[\d:]+[^​]*?(sekund[a-y]*|sekunda|minut[a-y]*|hodin[a-y]*)​*/, '');
  const parts = t.split(/[​\s]{3,}/).map(x => x.replace(/[​]/g, '').trim()).filter(Boolean);
  return ts + '\t' + [...new Set(parts)].join(' ');
};
window.__S = segs.map(clean);
let pre = document.getElementById('__trdump');
if (!pre) { pre = document.createElement('main'); pre.id = '__trdump'; document.body.prepend(pre); }
pre.style.cssText = 'position:absolute;left:-99999px;top:0;white-space:pre';
pre.textContent = window.__S.join('\n').slice(window.__OFFSET || 0, (window.__OFFSET || 0) + 49000);
({ segments: segs.length, total_chars: window.__S.join('\n').length, offset: window.__OFFSET || 0 });
