#!/usr/bin/env bash
# Headless ArtCraft video editor for the pipeline: ArtCraft's open-source editor library (MIT OR Apache-2.0,
# github.com/storytold/artcraft, pinned commit below) mounted in a small host page and driven by Playwright.
# No ArtCraft account, no API key, no credits: media, editing and export stay inside the local browser.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=${ARTCRAFT_SRC:-/home/user/artcraft-src}
COMMIT=40e04793b504147de97ba1f0659d3975167524e5   # 2026-10-20; update only after re-running the test project
LIB=frontend/libs/components/video-editor
if [ "$(git -C "$SRC" rev-parse HEAD 2>/dev/null)" != "$COMMIT" ]; then
  rm -rf "$SRC"; git init -q "$SRC"; git -C "$SRC" remote add origin https://github.com/storytold/artcraft.git
  git -C "$SRC" sparse-checkout set --no-cone "/$LIB/" /frontend/tsconfig.base.json /LICENSE-MIT /LICENSE-APACHE /NOTICE
  git -C "$SRC" fetch -q --depth 1 --filter=blob:none origin "$COMMIT" && git -C "$SRC" checkout -q FETCH_HEAD
fi
cd "$HERE/host"
[ -d node_modules ] || npm ci --no-audit --no-fund --ignore-scripts
# the library's own imports resolve from its monorepo root: point that at the host's pinned dependencies
ln -sfn "$HERE/host/node_modules" "$SRC/frontend/node_modules"
ARTCRAFT_EDITOR_SRC="$SRC/$LIB" npx vite build --logLevel warn
command -v xvfb-run >/dev/null || [ "$(uname)" = Darwin ] || echo "WARN: chybí xvfb-run (apt-get install xvfb)"
echo "artcraft editor ok: $HERE/host/dist (ArtCraft $COMMIT)"
