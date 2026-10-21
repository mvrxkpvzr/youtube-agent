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
# Blender 5.2.2 (same as on the Mac): tarball cached in the shared folder, unpacked locally (fast).
# Eevee needs EGL; Mesa renders it on the CPU.
BL=/home/user/blender; TB=blender-5.2.2-linux-x64.tar.xz; D="$ROOT/dist"; mkdir -p "$D"
if [ ! -x "$BL/blender" ]; then
  [ -s "$D/$TB" ] || { curl -fsSL -o "$D/$TB" "https://download.blender.org/release/Blender5.2/$TB" && curl -fsSL -o "$D/blender-5.2.2.sha256" "https://download.blender.org/release/Blender5.2/blender-5.2.2.sha256"; } || echo "WARN: Blender nejde stáhnout (je povolený download.blender.org?)"
  if [ -s "$D/$TB" ] && (cd "$D" && grep linux-x64 blender-5.2.2.sha256 | sha256sum -c - >/dev/null); then mkdir -p "$BL" && tar xJf "$D/$TB" -C "$BL" --strip-components=1; else echo "WARN: Blender neověřen, přeskočeno"; fi
fi
[ -e /usr/lib/x86_64-linux-gnu/libEGL.so.1 ] || { (apt-get update -qq && apt-get install -y -qq libegl1 libegl-mesa0 libgl1-mesa-dri libxkbcommon0 libsm6 libxi6 libxrender1 libxxf86vm1 libxfixes3) >/dev/null 2>&1 || echo "WARN: knihovny EGL pro Blender se nenainstalovaly"; }
[ -x "$BL/blender" ] && echo "blender ok: $("$BL/blender" -b --factory-startup --version 2>/dev/null | head -1)"
echo "Spouštění: $VENV/bin/python -I pipeline/vid.py ..."
