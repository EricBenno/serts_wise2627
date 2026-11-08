"""Läufe: Ergebnisordner mit Config-Kopie + Git-Hash (BRF §10.5); Einzel-, Raster-, Szenario-Lauf."""

from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path

from serts.config import Config
from serts.paths import RESULTS, ROOT


def git_info() -> dict[str, str | bool]:
    def _git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()

    try:
        return {"hash": _git("rev-parse", "HEAD"), "dirty": bool(_git("status", "--porcelain"))}
    except (OSError, subprocess.CalledProcessError):
        return {"hash": "unbekannt", "dirty": True}


def new_run_dir(cfg: Config, label: str = "", root: Path = RESULTS) -> Path:
    """results/<YYYYmmdd-HHMMSS>_<szenario>[_<label>]/ mit config.yaml und meta.json."""
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    name = "_".join(filter(None, [stamp, cfg.name, label]))
    out = root / name
    out.mkdir(parents=True, exist_ok=False)
    cfg.dump(out / "config.yaml")
    meta = {"szenario": cfg.name, "label": label, "zeit": stamp, "git": git_info()}
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), "utf-8")
    return out


def run_single(cfg: Config, A_koll_m2: float, V_m3: float) -> Path:
    """TODO M5: Zeitreihen laden, build_network, optimize(highs), kpi, netcdf + kpi.csv speichern."""
    raise NotImplementedError("M5: Einzellauf noch nicht umgesetzt")


def run_raster(cfg: Config) -> Path:
    """TODO M6: Schleife über raster.A_spez x raster.V_pro_A (Bezug raster.bezug)."""
    raise NotImplementedError("M6: Rasterlauf noch nicht umgesetzt")
