"""Run: python pipeline/tests/test_editplan.py  (no editor needed: plan checks, transition mapping, audio offset detection)"""
import copy, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import editplan as E
from lib import verify_export as VX

H = "0" * 64
PLAN = {"version": 1, "project": "t", "language": "cs", "fps": 25, "resolution": "1920x1080", "duration_s": 6.0,
        "transition": {"type": "fade", "dur_s": 0.2},
        "media": {"M001": {"path": "a.webm", "kind": "video", "duration_s": 2.2, "sha256": H},
                  "M002": {"path": "b.webm", "kind": "video", "duration_s": 2.2, "sha256": H},
                  "M003": {"path": "c.webm", "kind": "video", "duration_s": 2.0, "sha256": H},
                  "M004": {"path": "n.wav", "kind": "audio", "duration_s": 10.0, "sha256": H}},
        "scenes": [{"id": "SC001", "dur_s": 4.0, "video": [{"media": "M001", "at_s": 0, "dur_s": 2.0}, {"media": "M002", "at_s": 2.0, "dur_s": 2.0}],
                    "audio": [{"media": "M004", "at_s": 0.5, "in_s": 0.5, "dur_s": 3.0, "role": "narration"}]},
                   {"id": "SC002", "dur_s": 2.0, "video": [{"media": "M003", "at_s": 0, "dur_s": 2.0}],
                    "audio": [{"media": "M004", "at_s": 0.2, "in_s": 4.2, "dur_s": 1.5, "role": "narration"}],
                    "text": [{"content": "Ahoj", "at_s": 0.5, "dur_s": 1.0}]}]}

assert E.check(PLAN) == [], E.check(PLAN); print("ok: valid plan passes")
bad = copy.deepcopy(PLAN)
bad["scenes"][0]["video"][1]["dur_s"] = 2.5            # runs past its scene
bad["scenes"][1]["audio"][0]["in_s"] = 9.0             # past the end of the narration file
bad["scenes"][1]["video"][0]["media"] = "M999"
bad["duration_s"] = 7.0
errs = E.check(bad)
for needle in ["mimo scénu", "přesahuje médium", "neznámé médium", "součet scén"]:
    assert any(needle in e for e in errs), (needle, errs)
bad2 = copy.deepcopy(PLAN); bad2["scenes"][0]["id"] = "S1"; bad2["transition"]["type"] = "wipe"
assert sum("schema" in e for e in E.check(bad2)) == 2, E.check(bad2)
print("ok: broken plans rejected with the expected errors")

tl = E.resolve(PLAN, "/p")
v = tl["video"]
assert [c["start_s"] for c in v] == [0.0, 2.0, 4.0]
assert [c["dur_s"] for c in v] == [2.2, 2.2, 2.0], v           # crossfade: earlier clip keeps playing under the later one
assert [c["layer"] for c in v] == [0, 1, 0] and v[1]["fade_in_s"] == 0.2 and "fade_in_s" not in v[0]
assert [a["start_s"] for a in tl["audio"]] == [0.5, 4.2] and tl["text"][0]["start_s"] == 4.5
fb = copy.deepcopy(PLAN); fb["transition"] = {"type": "fadeblack", "dur_s": 0.4}
v = E.resolve(fb, "/p")["video"]
assert [c["layer"] for c in v] == [0, 0, 0] and v[0]["fade_out_s"] == 0.2 and v[1]["fade_in_s"] == 0.2 and v[1]["dur_s"] == 2.0
cut = copy.deepcopy(PLAN); cut["transition"] = {"type": "cut", "dur_s": 0}
assert all("fade_in_s" not in c and c["layer"] == 0 for c in E.resolve(cut, "/p")["video"])
print("ok: transitions map to editor operations (fade, fadeblack, cut)")

rng = np.random.default_rng(1); sr = VX.SR
voice = rng.standard_normal(sr * 2).astype(np.float32) * np.repeat(rng.random(40), sr // 20).astype(np.float32)
for shift in (0.0, 0.03, -0.12):
    got = np.zeros(int(sr * 2.5), np.float32); k = int((0.25 + shift) * sr)
    got[k:k + len(voice)] += voice; got += 0.3 * rng.standard_normal(len(got)).astype(np.float32)  # plus a music-like bed
    peak, lag = VX.xcorr(voice, got)
    assert peak > 0.6 and abs(lag - shift) < 0.002, (shift, peak, lag)
peak, _ = VX.xcorr(voice, rng.standard_normal(int(sr * 2.5)).astype(np.float32))
assert peak < 0.2, peak
print("ok: narration offset found to 2 ms under a bed; absent narration rejected")
