# konradre/video-production-skills – vendored file

| | |
|---|---|
| Source | https://github.com/konradre/video-production-skills |
| Commit | `8a69b599e1439a284996b218d3502dbaff8ccd92` (2026-10-11) |
| File | `skills/video-finish-qc/scripts/decoded_checks.py` → `decoded_checks.py` (**unmodified**, SHA-256 `6c7e8b2008e9fb34a6b9f09313ad3b076db9395532918956a77646f39942a37d`) |
| License | MIT, Copyright (c) 2026 konradre – `LICENSE` copied unmodified |
| Vendored | 2026-10-21 |
| Used by | `pipeline/lib/flashcheck.py` → `pipeline/lib/qa.py` (rows „blikání – …“) |

## Security review (2026-10-21)
- Read in full before running. Imports: stdlib + numpy (+ Pillow only for PNG folders).
- Subprocesses: only `ffmpeg` / `ffprobe`, argument lists (no shell). Network: none. Environment variables, credentials: none.
- Filesystem: reads the video; writes only inside a `tempfile` directory during `--selftest`.
- The repository's `install.sh` (symlinks into `~/.claude/skills`) and every script that calls a paid service
  (fal.ai, Higgsfield, ElevenLabs, AceDataCloud …) were **not** vendored and **not** run.

## Tests run
- `decoded_checks.py --selftest` → `SELFTEST PASS (36/36)` (cloud: Python 3.12.3, numpy 2.5.4, ffmpeg 6.1.1).
- `pipeline/tests/test_flashcheck.py` (strobe FAILS, calm fade passes, missing file is skipped, accepted window).

## Updating
Copy the new file over this one, record the new commit and SHA-256 here, re-read the diff, rerun both tests.
