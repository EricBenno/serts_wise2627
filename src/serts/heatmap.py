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
WERTE = [
    "lcoh",
    "lcoh_inkl_netz",
    "lcoh_inkl_netz_bew",
    "gas_lcoh_inkl_netz",
    "solar_gesamt",
    "ee_anteil",
    "co2_t_a",
    "P_WP_MW",
    "Q_pth_waerme_MWh",
    "jaz_wp",
    "speicher_zyklen",
    "speicher_winteranteil",
    "speicher_wirkungsgrad",
]

# Grafik "heatmap_alle.png": (Spalte, Titel, Farbskala, Format)
FELDER = [
    ("lcoh_inkl_netz", "Wärmepreis inkl. Netz [€/MWh]", "viridis_r", "{:.0f}"),
    ("lcoh_inkl_netz_bew", "dito mit BEW Modul 2 (max. 40 %) [€/MWh]", "viridis_r", "{:.0f}"),
    ("vorteil_gas", "Vorteil ggü. Gas-Fernwärme [€/MWh]", "RdYlGn", "{:+.0f}"),
    ("solar_gesamt", "Solaranteil [-]", "YlOrRd", "{:.0%}"),
    ("co2_t_a", "CO₂ [t/a]", "Greys", "{:,.0f}"),
    ("speicher_zyklen", "Speicherzyklen [1/a]", "PuBu", "{:.1f}"),
    ("speicher_winteranteil", "Speicherentladung Nov–Mär [-]", "PuBu", "{:.0%}"),
    ("P_WP_MW", "WP-Leistung [MW]", "Blues", "{:.2f}"),
    ("Q_pth_waerme_MWh", "PtH-Wärme [MWh/a]", "Reds", "{:,.0f}"),
]


def passt(cfg: Config, A: float, V: float) -> bool:
    f = A * cfg.get("kollektor.flaechenfaktor") + V / cfg.get("ptes.volumen_je_grundflaeche")
    return f <= cfg.get("standort.flaeche_verfuegbar")


def _punkt(cfg: Config, A: float, V: float, threads) -> dict:
    logging.getLogger("linopy").setLevel(logging.WARNING)
    logging.getLogger("pypsa").setLevel(logging.WARNING)
    ts, _ = build_zeitreihen(cfg, vollstaendig=True)
    _, k, _ = loese(cfg, ts, A_m2=A, V_m3=V, threads=threads)
    return {"A_m2": A, "V_m3": V, **{w: k.get(w) for w in WERTE}}


def _feld(ax, fig, df: pd.DataFrame, spalte: str, titel: str, cmap: str, fmt: str) -> None:
    mat = df.pivot(index="V_m3", columns="A_m2", values=spalte).sort_index()
    werte = mat.to_numpy(dtype=float)
    kw = {}
    if spalte == "vorteil_gas" and np.isfinite(werte).any():
        g = float(np.nanmax(np.abs(werte)))
        kw = {"vmin": -g, "vmax": g}  # 0 = gleich teuer wie Gas, in der Mitte der Farbskala
    im = ax.imshow(werte, origin="lower", aspect="auto", cmap=cmap, **kw)
    ax.set_xticks(range(len(mat.columns)), [f"{a / 1000:g}" for a in mat.columns])
    ax.set_yticks(range(len(mat.index)), [f"{v / 1000:g}" for v in mat.index])
    ax.set(xlabel="Kollektorfläche [1.000 m²]", ylabel="Speicher [1.000 m³]", title=titel)
    ax.title.set_fontsize(10)
    for (i, j), v in np.ndenumerate(werte):
        if v == v:
            ax.text(
                j,
                i,
                fmt.format(v).replace(",", "."),
                ha="center",
                va="center",
                fontsize=7,
                color="k",
                path_effects=[patheffects.withStroke(linewidth=2.5, foreground="w")],
            )
    fig.colorbar(im, ax=ax)
    if spalte.startswith("lcoh") and np.isfinite(werte).any():
        i, j = np.unravel_index(np.nanargmin(werte), werte.shape)
        ax.scatter(j, i, s=250, facecolors="none", edgecolors="red", linewidths=2)


def _bild(df: pd.DataFrame, out: Path, gas: float | None) -> Path:
    """Kurzfassung: Wärmepreis und Solaranteil."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    _feld(
        axes[0], fig, df, "lcoh_inkl_netz", "Wärmepreis inkl. Netz [€/MWh]", "viridis_r", "{:.0f}"
    )
    _feld(axes[1], fig, df, "solar_gesamt", "Solaranteil [-]", "YlOrRd", "{:.0%}")
    if gas is not None:
        fig.suptitle(
            f"Raster mit festen Größen (WP, PtH je Punkt optimiert); Gas-Fernwärme {gas:.0f} €/MWh"
        )
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _bild_alle(df: pd.DataFrame, out: Path, titel: str) -> Path:
    """Alle Kennzahlen aus FELDER in einem 3 x 3-Raster."""
    fig, axes = plt.subplots(3, 3, figsize=(17, 13))
    for ax, (spalte, t, cmap, fmt) in zip(axes.flat, FELDER, strict=True):
        if spalte in df and df[spalte].notna().any():
            _feld(ax, fig, df, spalte, t, cmap, fmt)
        else:
            ax.set_axis_off()
    fig.suptitle(titel)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
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
    if "gas_lcoh_inkl_netz" in df:
        df["vorteil_gas"] = df["gas_lcoh_inkl_netz"] - df["lcoh_inkl_netz"]
        df.to_csv(out / "heatmap.csv", index=False)
    _bild(df, out / "heatmap.png", gas)
    _bild_alle(
        df,
        out / "heatmap_alle.png",
        f"Netz {cfg.netz}: Raster mit festen Größen (WP, PtH je Punkt optimiert)"
        + (f"; Gas-Fernwärme {gas:.0f} €/MWh" if gas is not None else ""),
    )
    return out
