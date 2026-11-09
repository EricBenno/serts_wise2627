"""Läufe: Ergebnisordner mit Config-Kopie + Git-Hash (BRF §10.5)."""

from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path

import pandas as pd

from serts import kpi, network, plots
from serts.config import Config
from serts.paths import RESULTS, ROOT
from serts.prepare import build_zeitreihen


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


def loese(
    cfg: Config,
    ts: pd.DataFrame,
    A_m2: float | None = None,
    V_m3: float | None = None,
    threads: int | None = None,
):
    """Netz bauen, optimieren, auswerten. A/V = None -> Größe wird optimiert.

    Speicher optimiert: ein Lauf je Preisstufe (ptes.preisstufen), V bleibt in der Stufe;
    der Lauf mit den geringsten Jahreskosten gewinnt (docs E24).
    """
    if V_m3 is not None:
        n = network.build_network(cfg, ts, A_m2, V_m3)
        network.optimize(n, cfg, threads=threads)
        k, r = kpi.auswerten(n, cfg, ts)
        return n, k, r

    beste, stufen = None, []
    for stufe in cfg.get("ptes.preisstufen"):
        n = network.build_network(cfg, ts, A_m2, None, stufe=tuple(stufe))
        try:
            network.optimize(n, cfg, threads=threads)
        except RuntimeError:  # z. B. Mindestvolumen passt nicht auf die Fläche
            stufen.append(f"{stufe[0]}-{stufe[1]} m3: unzulässig")
            continue
        k, r = kpi.auswerten(n, cfg, ts)
        stufen.append(f"{stufe[0]}-{stufe[1]} m3: LCOH {k['lcoh']:.1f}, V {k['V_m3']:.0f}")
        if beste is None or k["kosten_a_gesamt"] < beste[1]["kosten_a_gesamt"]:
            beste = (n, k, r)
    if beste is None:
        raise RuntimeError("keine Preisstufe lösbar: " + "; ".join(stufen))
    n, k, r = beste
    k["preisstufen_vergleich"] = stufen
    return n, k, r


def run(
    cfg: Config,
    A_m2: float | None = None,
    V_m3: float | None = None,
    stunden: int | None = None,
) -> Path:
    """Ein Lauf: speichert config, meta, kpi.json, zeitreihen.csv, network.nc, monatsbilanz.png."""
    ts, _ = build_zeitreihen(cfg, vollstaendig=True)
    if stunden:
        ts = ts.iloc[:stunden]
    n, k, r = loese(cfg, ts, A_m2, V_m3)
    teile = [f"A{A_m2:g}" if A_m2 is not None else "", f"V{V_m3:g}" if V_m3 is not None else ""]
    label = "_".join(filter(None, teile)) or "opt"
    out = new_run_dir(cfg, label + (f"_{stunden}h" if stunden else ""))
    (out / "kpi.json").write_text(
        json.dumps(k, indent=2, ensure_ascii=False, default=float), "utf-8"
    )
    r.to_csv(out / "zeitreihen.csv", float_format="%.5g")
    n.export_to_netcdf(out / "network.nc")
    plots.monatsbilanz(r, out / "monatsbilanz.png")
    return out
