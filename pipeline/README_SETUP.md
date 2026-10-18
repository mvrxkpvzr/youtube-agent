# Prostředí pipeline

Vše leží v `~/youtube-agent-env` (mimo projekt, protože cesta „youtube agent“ obsahuje mezeru a virtuální prostředí s mezerou v cestě nefungují spolehlivě). `pipeline/config.json → env_root` na tuto složku ukazuje.

| Složka | Obsah |
|---|---|
| `venv/piper` | Python 3.11, Piper TTS (CS/DE), `requirements.piper.txt` |
| `venv/qwen` | Python 3.12, Qwen3-TTS, mlx-whisper, librosa, imageio-ffmpeg, Pillow, OpenCV – **hlavní prostředí pipeline** (`$PY`) |
| `voices/` | Piper hlasy `cs_CZ-jirka-medium`, `de_DE-thorsten-high` |
| `hf/` | modely Hugging Face: Qwen3-TTS-12Hz-0.6B-CustomVoice, whisper-large-v3-turbo |
| `python/` | interprety Pythonu spravované přes uv |
| `tools/uvpkg/bin/uv` | správce balíčků uv |

Blender 5.2.2 je v `/Applications/Blender.app`.

## Spuštění
```
PY=~/youtube-agent-env/venv/qwen/bin/python
$PY -I pipeline/vid.py ...
$PY -I pipeline/tests/test_validate.py
```

## Obnova od nuly
```
R=~/youtube-agent-env; UV=$R/tools/uvpkg/bin/uv; export UV_PYTHON_INSTALL_DIR=$R/python
$UV python install 3.11.17 3.12.15
$UV venv --python 3.11.17 $R/venv/piper && $UV pip install --python $R/venv/piper/bin/python -r $R/requirements.piper.txt
$UV venv --python 3.12.15 $R/venv/qwen  && $UV pip install --python $R/venv/qwen/bin/python  -r $R/requirements.qwen.txt
```
Modely se stáhnou samy při prvním použití do `$R/hf`. Piper hlasy jsou na huggingface.co/rhasspy/piper-voices.

Nezkopírováno (nekomerční nebo jen referenční): Chatterbox, OmniVoice, Qwen3-TTS 1.7B.

## Cloud (Linux, claude.ai project)
Agent běží v cloudovém kontejneru, ne na Macu. `pipeline/config.json → platform.linux` přepíše cesty a nástroje:

| Co | Mac | Cloud |
|---|---|---|
| Python | `~/youtube-agent-env/venv/qwen` | `/home/user/ytenv` (vytvoří `setup/cloud_setup.sh` na začátku každé session) |
| modely, hlasy, Blender | `~/youtube-agent-env` | `/mnt/project-files/youtube/env` (sdílené soubory projektu, přežijí konec session) |
| zpětný přepis | mlx-whisper | faster-whisper na CPU (`lib/asr.py`) |
| český hlas | MOSS přes MLX | zatím Piper; MOSS na CPU není ověřený |
| Blender | `/Applications/Blender.app` | linuxový Blender v `{env_root}/blender/` |

Projekty leží v `/mnt/project-files/youtube/projects/`. Stahování z huggingface.co a download.blender.org musí povolit síťové nastavení cloudového prostředí.
```
bash setup/cloud_setup.sh
PY=/home/user/ytenv/bin/python
$PY -I pipeline/vid.py status /mnt/project-files/youtube/projects/<projekt>
```
