"""Run: python pipeline/tests/test_validate.py  (uses tests/fixtures/example_project)"""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; EX = Path(__file__).resolve().parent / "fixtures" / "example_project"; V = ROOT / "pipeline" / "validate.py"
def run(p): r = subprocess.run([sys.executable, str(V), str(p)], capture_output=True, text=True); return r.returncode, r.stdout
code, out = run(EX); assert code == 0, out; print("ok: example passes")
with tempfile.TemporaryDirectory() as d:
    t = Path(d) / "p"; shutil.copytree(EX, t)
    c = [json.loads(l) for l in (t / "claims.jsonl").read_text().splitlines()]
    c[0]["status"] = "unverified"; c[2]["evidence"] = [{"source_id": "S002", "supports": "supports"}]
    (t / "claims.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in c))
    a = {"id": "A001", "kind": "voice", "origin": "generated", "file": "audio/cs/SC001.wav", "license": "CC0", "risk": "low", "status": "candidate"}
    a2 = dict(a, id="A002", kind="ai_image", origin="quotation_third_party", realistic_depiction_of_real_person=True, quotation_purpose=None)
    (t / "assets.jsonl").write_text(json.dumps(a) + "\n" + json.dumps(a2))
    s = json.loads((t / "shotlist.cs.json").read_text()); s["scenes"][4]["visuals"][0]["asset_id"] = "A999"
    (t / "shotlist.cs.json").write_text(json.dumps(s, ensure_ascii=False))
    code, out = run(t); assert code == 1
    for needle in ["only tier C/D", "realistic AI depiction", "quotation without stated purpose", "uses unverified claim C001", "unknown asset A999"]:
        assert needle in out, (needle, out)
    print("ok: broken project rejected with all 5 expected errors")
