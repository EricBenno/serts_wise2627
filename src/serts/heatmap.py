"""Heatmap Wärmepreis über Kollektorfläche × Speichervolumen (BRF §1 Pflicht 6).

Jeder Rasterpunkt ist ein Lauf mit festen Größen A und V; WP und PtH werden je Punkt optimiert. Punkte, die nicht
auf die Fläche passen, bleiben leer. Raster: ``heatmap.A_m2`` und ``heatmap.V_m3`` (je Netz in config/netze/).

Ausgabe: results/<netz>/<zeit>_<szenario>_heatmap/ mit heatmap.csv und heatmap.png.
"""

from __future__ import annotations

import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import patheffects

from serts.config import Config
from serts.prepare import build_zeitreihen
from serts.run import loese, new_run_dir

log = logging.getLogger(__name__)
WERTE = ["lcoh", "lcoh_inkl_netz", "lcoh_inkl_netz_bew", "solar_gesamt", "co2_t_a", "P_WP_MW"]


def passt(cfg: Config, A: float, V: float) -> bool:
    f = A * cfg.get("kollektor.flaechenfaktor") + V / cfg.get("ptes.volumen_je_grundflaeche")
    return f <= cfg.get("standort.flaeche_verfuegbar")


def _punkt(cfg: Config, A: float, V: float, threads) -> dict:
    logging.getLogger("linopy").setLevel(logging.WARNING)
    logging.getLogger("pypsa").setLevel(logging.WARNING)
    ts, _ = build_zeitreihen(cfg, vollstaendig=True)
    _, k, _ = loese(cfg, ts, A_m2=A, V_m3=V, threads=threads)
    return {"A_m2": A, "V_m3": V, **{w: k.get(w) for w in WERTE}}


def _bild(df: pd.DataFrame, out: Path, gas: float | None) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, (spalte, titel, cmap) in zip(
        axes,
        [
            ("lcoh_inkl_netz", "Wärmepreis inkl. Netz [€/MWh]", "viridis_r"),
            ("solar_gesamt", "Solaranteil [-]", "YlOrRd"),
        ],
        strict=True,
    ):
        mat = df.pivot(index="V_m3", columns="A_m2", values=spalte).sort_index()
        im = ax.imshow(mat.to_numpy(dtype=float), origin="lower", aspect="auto", cmap=cmap)
        ax.set_xticks(range(len(mat.columns)), [f"{a:,.0f}".replace(",", ".") for a in mat.columns])
        ax.set_yticks(range(len(mat.index)), [f"{v:,.0f}".replace(",", ".") for v in mat.index])
        ax.set(xlabel="Kollektorfläche [m²]", ylabel="Speichervolumen [m³]", title=titel)
        for (i, j), v in np.ndenumerate(mat.to_numpy(dtype=float)):
            if v == v:
                ax.text(
                    j,
                    i,
                    f"{v:.0%}" if spalte == "solar_gesamt" else f"{v:.0f}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="k",
                    path_effects=[patheffects.withStroke(linewidth=2.5, foreground="w")],
                )
        fig.colorbar(im, ax=ax)
        if spalte == "lcoh_inkl_netz" and df[spalte].notna().any():
            best = df.loc[df[spalte].idxmin()]
            j = list(mat.columns).index(best["A_m2"])
            i = list(mat.index).index(best["V_m3"])
            ax.scatter(j, i, s=250, facecolors="none", edgecolors="red", linewidths=2)
    if gas is not None:
        fig.suptitle(
            f"Raster mit festen Größen (WP, PtH je Punkt optimiert); Gas-Fernwärme {gas:.0f} €/MWh"
        )
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def heatmap(cfg: Config, jobs: int = 3) -> Path:
    out = new_run_dir(cfg, "heatmap")
    punkte = [
        (float(A), float(V))
        for A in cfg.get("heatmap.A_m2")
        for V in cfg.get("heatmap.V_m3")
        if passt(cfg, A, V)
    ]
    threads = 1 if jobs > 1 else None
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        zeilen = list(
            pool.map(
                _punkt, [cfg] * len(punkte), *zip(*punkte, strict=True), [threads] * len(punkte)
            )
        )
    alle = pd.DataFrame(
        [(float(A), float(V)) for A in cfg.get("heatmap.A_m2") for V in cfg.get("heatmap.V_m3")],
        columns=["A_m2", "V_m3"],
    )
    df = alle.merge(pd.DataFrame(zeilen), on=["A_m2", "V_m3"], how="left")
    df.to_csv(out / "heatmap.csv", index=False)
    ts, _ = build_zeitreihen(cfg, vollstaendig=True)
    from serts import economics

    gas = None
    if cfg.get("netz.netzkosten_einbeziehen"):
        Q = float(ts["last_gesamt"].sum())
        ref = economics.gas_referenz(cfg, Q, float(ts["last_gesamt"].max()))
        nk = economics.netzkosten(cfg)
        Qg = Q - float(ts["last_netzverlust"].sum())
        gas = (ref["gas_lcoh"] * Q + nk["kosten_a_netz_gasref"]) / Qg
    _bild(df, out / "heatmap.png", gas)
    return out
