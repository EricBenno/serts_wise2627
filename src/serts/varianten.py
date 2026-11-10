"""Vergleichsvarianten zur Leitfrage (BRF §1 Pflicht 5) für ein Netz.

Je Variante ein Lauf (Größen jeweils kostenoptimal, soweit nicht vorgegeben):
  Basis               Kollektor + PTES + WP + PtH optimiert, ohne Förderung
  ohne Speicher       Kollektor + WP + PtH (V = 0)
  nur WP + PtH        kein Kollektor, kein Speicher
  mit BEW Modul 2     wie Basis, aber mit 40 % Investitionszuschuss optimiert (Obergrenze)
Gas-Referenz (Gaskessel + gleiches Netz) steht in jeder Zeile als Vergleich. PV für die WP (Pflicht 5c) ist
nicht modelliert (Abschätzung in docs/ausblick.md).

Ausgabe: results/<netz>/<zeit>_<szenario>_varianten/ mit varianten.csv, varianten.md, pareto.png.
"""

from __future__ import annotations

import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from serts.config import Config
from serts.prepare import build_zeitreihen
from serts.run import loese, new_run_dir

log = logging.getLogger(__name__)

SPALTEN = {
    "A_koll_m2": ("Kollektor [m²]", "{:,.0f}"),
    "V_m3": ("Speicher [m³]", "{:,.0f}"),
    "P_WP_MW": ("WP [MW]", "{:.2f}"),
    "P_PtH_MW": ("PtH [MW]", "{:.2f}"),
    "solar_gesamt": ("Solaranteil", "{:.0%}"),
    "ee_anteil": ("EE-Anteil", "{:.0%}"),
    "co2_t_a": ("CO₂ [t/a]", "{:,.0f}"),
    "speicher_zyklen": ("Speicherzyklen [1/a]", "{:.1f}"),
    "speicher_winteranteil": ("Speicherentladung Nov-Mär", "{:.0%}"),
    "lcoh": ("LCOH Erzeugung [€/MWh]", "{:.1f}"),
    "lcoh_inkl_netz": ("Wärmepreis inkl. Netz [€/MWh]", "{:.1f}"),
    "lcoh_inkl_netz_bew": ("  dito mit BEW (gleiche Auslegung)", "{:.1f}"),
    "gas_lcoh_inkl_netz": ("Gas-Fernwärme inkl. Netz [€/MWh]", "{:.1f}"),
    "zuschuss_bew_EUR": ("BEW-Zuschuss max. [Mio. €]", "{:.2f}"),
}


def faelle(cfg: Config) -> dict[str, tuple[Config, float | None, float | None]]:
    q = cfg.get("oekonomie.bew_ausweis_quote")
    return {
        "Basis": (cfg, None, None),
        "ohne Speicher": (cfg, None, 0.0),
        "nur WP + PtH": (cfg, 0.0, 0.0),
        "mit BEW Modul 2": (cfg.variante("oekonomie.foerderquote", q), None, None),
    }


def _lauf(name: str, c: Config, A, V, threads) -> tuple[str, dict]:
    logging.getLogger("linopy").setLevel(logging.WARNING)
    logging.getLogger("pypsa").setLevel(logging.WARNING)
    ts, _ = build_zeitreihen(c, vollstaendig=True)
    _, k, _ = loese(c, ts, A_m2=A, V_m3=V, threads=threads)
    if name == "mit BEW Modul 2":  # Förderung wirkt hier schon in der Optimierung
        k["lcoh_inkl_netz_bew"] = k.get("lcoh_inkl_netz")
    return name, k


def _markdown(df: pd.DataFrame, cfg: Config) -> str:
    zeilen = [
        f"# Varianten Netz {cfg.netz} (Szenario {cfg.name})",
        "",
        "Größen kostenoptimal je Variante; BEW = Obergrenze 40 % auf förderfähige Teile "
        "(Wirtschaftlichkeitslücke nicht geprüft).",
        "",
        "| Kennzahl | " + " | ".join(df.columns) + " |",
        "|---|" + "---|" * len(df.columns),
    ]
    for key, (label, fmt) in SPALTEN.items():
        if key not in df.index:
            continue
        werte = []
        for v in df.loc[key]:
            if v is None or v != v:
                werte.append("–")
            else:
                werte.append(fmt.format(v / 1e6 if key == "zuschuss_bew_EUR" else v))
        zeilen.append(f"| {label} | " + " | ".join(werte) + " |")
    return "\n".join(zeilen) + "\n"


def _pareto(df: pd.DataFrame, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 5))
    for name in df.columns:
        x, y = df.at["ee_anteil", name], df.at["lcoh_inkl_netz", name]
        ax.scatter(x, y, s=60)
        ax.annotate(name, (x, y), textcoords="offset points", xytext=(6, 4), fontsize=9)
    gas = float(df.loc["gas_lcoh_inkl_netz"].iloc[0])
    ax.scatter(0.0, gas, marker="s", color="k")
    ax.annotate("Gas-Fernwärme", (0.0, gas), textcoords="offset points", xytext=(6, 4), fontsize=9)
    ax.set(
        xlabel="Erneuerbaren-Anteil [-]",
        ylabel="Wärmepreis inkl. Netz [€/MWh geliefert]",
        title="Kosten gegen Erneuerbaren-Anteil (Varianten)",
    )
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def varianten(cfg: Config, jobs: int = 2) -> Path:
    out = new_run_dir(cfg, "varianten")
    f = faelle(cfg)
    threads = 1 if jobs > 1 else None
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        futs = [pool.submit(_lauf, name, c, A, V, threads) for name, (c, A, V) in f.items()]
        ergebnisse = dict(fu.result() for fu in futs)
    df = pd.DataFrame({name: ergebnisse[name] for name in f}).loc[
        [k for k in SPALTEN if k in pd.DataFrame(ergebnisse).index]
    ]
    df.to_csv(out / "varianten.csv")
    (out / "varianten.md").write_text(_markdown(df, cfg), encoding="utf-8")
    _pareto(df, out / "pareto.png")
    return out
