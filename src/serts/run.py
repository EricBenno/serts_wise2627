"""Läufe: Ergebnisordner mit Config-Kopie + Git-Hash (BRF §10.5); Einzel- und Rasterlauf."""

from __future__ import annotations

import datetime as dt
import json
import logging
import subprocess
from pathlib import Path

import pandas as pd

from serts import kpi, network, plots
from serts.config import Config
from serts.paths import RESULTS, ROOT
from serts.prepare import build_zeitreihen

log = logging.getLogger(__name__)


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


def bezugsmenge(cfg: Config, ts: pd.DataFrame) -> float:
    """Rasterbezug [MWh/a] (raster.bezug = einspeisung -> Jahressumme last_gesamt)."""
    if cfg.get("raster.bezug") != "einspeisung":
        raise ValueError("nur raster.bezug = einspeisung umgesetzt")
    return float(ts["last_gesamt"].sum()) * 8760.0 / len(ts)


def loese(cfg: Config, ts: pd.DataFrame, A_m2: float, V_m3: float, threads: int | None = None):
    n = network.build_network(cfg, ts, A_m2, V_m3)
    network.optimize(n, cfg, ts, threads=threads)
    k, r = kpi.auswerten(n, cfg, ts)
    return n, k, r


def _ts(cfg: Config, stunden: int | None) -> tuple[pd.DataFrame, float]:
    """Zeitreihen (ggf. gekürzt für Tests) + Rasterbezug aus dem vollen Jahr."""
    ts, _ = build_zeitreihen(cfg, vollstaendig=True)
    Q = bezugsmenge(cfg, ts)
    return (ts.iloc[:stunden] if stunden else ts), Q


def run_single(cfg: Config, A_spez: float, V_pro_A: float, stunden: int | None = None) -> Path:
    """Einzellauf (M5): speichert config, meta, kpi.json, zeitreihen.csv, network.nc, Plots."""
    ts, Q = _ts(cfg, stunden)
    A = A_spez * Q
    V = V_pro_A * A
    n, k, r = loese(cfg, ts, A, V)
    out = new_run_dir(cfg, f"A{A_spez:g}_V{V_pro_A:g}" + (f"_{stunden}h" if stunden else ""))
    k.update({"A_spez": A_spez, "V_pro_A": V_pro_A})
    (out / "kpi.json").write_text(
        json.dumps(k, indent=2, ensure_ascii=False, default=float), "utf-8"
    )
    r.to_csv(out / "zeitreihen.csv", float_format="%.5g")
    n.export_to_netcdf(out / "network.nc")
    plots.monatsbilanz(r, out / "monatsbilanz.png")
    return out


def _rasterpunkt(
    cfg: Config, ts: pd.DataFrame, Q: float, a: float, v: float, threads: int | None
) -> dict:
    """Ein Rasterpunkt (top-level, damit er in einem Worker-Prozess laufen kann)."""
    logging.getLogger("linopy").setLevel(logging.WARNING)
    logging.getLogger("pypsa").setLevel(logging.WARNING)
    _, k, _ = loese(cfg, ts, a * Q, v * a * Q, threads=threads)
    k.update({"A_spez": a, "V_pro_A": v})
    return k


def run_raster(cfg: Config, stunden: int | None = None, jobs: int = 1) -> Path:
    """Rasterlauf (M6): A_spez x V_pro_A -> raster.csv, Heatmap LCOH, Pareto EE-Anteil vs. LCOH."""
    from concurrent.futures import ProcessPoolExecutor, as_completed

    ts, Q = _ts(cfg, stunden)
    out = new_run_dir(cfg, "raster" + (f"_{stunden}h" if stunden else ""))
    punkte = [(a, v) for a in cfg.get("raster.A_spez") for v in cfg.get("raster.V_pro_A")]
    zeilen = []
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        futs = {
            pool.submit(_rasterpunkt, cfg, ts, Q, a, v, 1 if jobs > 1 else None): (a, v)
            for a, v in punkte
        }
        for f in as_completed(futs):
            a, v = futs[f]
            zeilen.append(f.result())
            log.info("Raster %d/%d fertig: A_spez=%s V/A=%s", len(zeilen), len(punkte), a, v)
            pd.DataFrame(zeilen).to_csv(out / "raster.csv", index=False)  # Zwischenstand
    df = pd.DataFrame(zeilen).sort_values(["A_spez", "V_pro_A"])
    df.to_csv(out / "raster.csv", index=False)
    plots.heatmap_lcoh(df, out / "heatmap_lcoh.png")
    plots.pareto(df, out / "pareto_ee_lcoh.png")
    return out
