import hashlib, json, os, subprocess, sys, time
from pathlib import Path

PIPE = Path(__file__).resolve().parents[1]

def _overlay(base, over):
    for k, v in over.items():
        base[k] = _overlay(base.get(k, {}), v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return base

def cfg():
    """config.json, with config["platform"][sys.platform] laid over it (Mac = base, Linux cloud = overlay).
    Placeholders: {env_root} (models, voices, tools; YT_ENV_ROOT overrides), {venv} (Python env), {pipe} (this folder)."""
    c = json.loads((PIPE / "config.json").read_text())
    c = _overlay(c, c.pop("platform", {}).get(sys.platform, {}))
    root = os.environ.get("YT_ENV_ROOT") or c["env_root"]; venv = os.environ.get("YT_VENV") or c.get("venv", "")
    def sub(v):
        if isinstance(v, str): return v.replace("{env_root}", root).replace("{venv}", venv).replace("{pipe}", str(PIPE))
        if isinstance(v, dict): return {k: sub(x) for k, x in v.items()}
        return v
    # ASR (Whisper) and other in-process HF loads use the project's model cache
    os.environ.setdefault("HF_HOME", f"{root}/hf")
    return sub(c)

def sha(path_or_text):
    h = hashlib.sha256()
    if isinstance(path_or_text, Path): h.update(path_or_text.read_bytes())
    else: h.update(path_or_text.encode("utf-8"))
    return h.hexdigest()

def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(map(str, cmd))[:300]}\n{r.stderr[-2000:]}")
    return r

def load_shotlist(proj, lang):
    return json.loads((proj / f"shotlist.{lang}.json").read_text(encoding="utf-8"))

def update_state(proj, step, status, inputs=(), outputs=(), **extra):
    p = proj / "state.json"
    st = json.loads(p.read_text()) if p.exists() else {"project": proj.name, "created_at": time.strftime("%Y-%m-%d"), "steps": {}}
    st["steps"][step] = {"status": status,
                         "inputs_sha256": {str(Path(i).relative_to(proj)): sha(Path(i)) for i in inputs if Path(i).exists()},
                         "outputs": [str(Path(o).relative_to(proj)) for o in outputs],
                         "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **extra}
    p.write_text(json.dumps(st, indent=2, ensure_ascii=False))

def stale_steps(proj):
    """Steps whose recorded inputs changed since they ran."""
    st = json.loads((proj / "state.json").read_text())
    out = []
    for name, s in st["steps"].items():
        for rel, h in s.get("inputs_sha256", {}).items():
            f = proj / rel
            if not f.exists() or sha(f) != h:
                out.append(name); break
    return out
