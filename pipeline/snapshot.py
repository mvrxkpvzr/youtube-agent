"""Save a source snapshot + plain text into a project and print the text (for quoting).
Usage: python snapshot.py <project> <source_id> <url> [--grep word1,word2]"""
import hashlib, html, json, re, subprocess, sys, time
from html.parser import HTMLParser
from pathlib import Path

class T(HTMLParser):
    def __init__(self): super().__init__(); self.out, self.skip = [], 0
    def handle_starttag(self, t, a):
        if t in ("script", "style", "noscript", "svg", "nav", "footer"): self.skip += 1
        if t in ("p", "br", "h1", "h2", "h3", "li", "div"): self.out.append("\n")
    def handle_endtag(self, t):
        if t in ("script", "style", "noscript", "svg", "nav", "footer") and self.skip: self.skip -= 1
    def handle_data(self, d):
        if not self.skip: self.out.append(d)

proj, sid, url = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
grep = sys.argv[sys.argv.index("--grep") + 1].split(",") if "--grep" in sys.argv else None
(proj / "sources").mkdir(parents=True, exist_ok=True)
raw = subprocess.run(["curl", "-sL", "--max-time", "40", "-A", "Mozilla/5.0 (Macintosh) research-snapshot", url], capture_output=True).stdout
(proj / "sources" / f"{sid}.html").write_bytes(raw)
p = T(); p.feed(raw.decode("utf-8", "replace")); text = re.sub(r"\n\s*\n+", "\n", html.unescape("".join(p.out)))
(proj / "sources" / f"{sid}.txt").write_text(text, encoding="utf-8")
meta = {"id": sid, "url": url, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
(proj / "sources" / f"{sid}.meta.json").write_text(json.dumps(meta, indent=1))
title = re.search(rb"<title[^>]*>(.*?)</title>", raw, re.S); print("TITLE:", html.unescape(title.group(1).decode("utf-8", "replace")).strip() if title else "?", "| bytes", len(raw))
for m in re.finditer(rb'"datePublished"\s*:\s*"([^"]+)"', raw): print("datePublished:", m.group(1).decode()); break
lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 40]
if grep: lines = [l for l in lines if any(g.lower() in l.lower() for g in grep)]
print("\n".join(lines[:60]))
