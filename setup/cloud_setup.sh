#!/usr/bin/env bash
# Prepares a fresh cloud session: Python env in /home/user/ytenv (local, fast) and the
# persistent folder for models, voices and Blender in the project's shared files.
# Free tools only. Nothing here buys or activates a paid service.
set -euo pipefail
VENV=${YT_VENV:-/home/user/ytenv}
ROOT=${YT_ENV_ROOT:-/mnt/project-files/youtube/env}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$ROOT/hf" "$ROOT/voices"
[ -x "$VENV/bin/python" ] || uv venv -q --python 3.12 "$VENV"
uv pip install -q --python "$VENV/bin/python" -r "$HERE/requirements.cloud.txt"
echo "env ok: $VENV ($("$VENV/bin/python" -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'))"
# Piper voices and Whisper come from huggingface.co, Blender from download.blender.org.
# Both hosts must be allowed in the cloud environment's network settings.
for v in cs_CZ-jirka-medium de_DE-thorsten-high; do
  [ -s "$ROOT/voices/$v.onnx" ] && continue
  lang=${v%%-*}; fam=${lang%%_*}; name=$(echo "$v" | cut -d- -f2); q=$(echo "$v" | cut -d- -f3)
  base="https://huggingface.co/rhasspy/piper-voices/resolve/main/$fam/$lang/$name/$q/$v"
  curl -fsSL -o "$ROOT/voices/$v.onnx" "$base.onnx" && curl -fsSL -o "$ROOT/voices/$v.onnx.json" "$base.onnx.json" \
    || { rm -f "$ROOT/voices/$v.onnx"; echo "WARN: hlas $v nejde stáhnout (je povolený huggingface.co?)"; }
done
echo "Spouštění: $VENV/bin/python -I pipeline/vid.py ..."
