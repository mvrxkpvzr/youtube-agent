# EL4CTEO/blender-skills – vendored reference

| | |
|---|---|
| Source | https://github.com/EL4CTEO/blender-skills |
| Commit | `71d031dab8bc6729504d11a78cbe91945401045f` (release 1.1.0, 2026-10-16) |
| File | `skills/blender-core/references/api-changes-5x.md` → `api-changes-5x.md` (**unmodified**, SHA-256 `ccf0b52a1d9fd836eb689abcec6a878b0ac57fb32ac600476b5070b9c8d22307`) |
| License | MIT, Copyright (c) 2026 EL4CTEO – `LICENSE` copied unmodified |
| Vendored | 2026-10-21 |
| Kind | knowledge only (no code is executed) |

Why: the table lists bpy changes 4.x → 5.2 that old tutorials and model memory get wrong. Our Blender 5.2.2 run of
`pipeline/blender/shots.py` prints exactly the warnings it predicts (`Material.use_nodes` / `World.use_nodes` deprecated,
to be removed in Blender 6.0). Read it before writing or changing a `shot_<name>()` in `pipeline/blender/shots.py`.

Not vendored: the 22 skills' scripts and `install/install.sh` (they install into `~/.claude/skills` and target game/asset
work: rigging, LODs, export). The upstream claims its scripts are "tested in a real Blender"; we did not run its tests.
