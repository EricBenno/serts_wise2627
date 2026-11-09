"""Sensitivitäten als Tornado (BRF §1 Pflicht 6, AP 12).

Vorgehen (bewusst einfach): Für jeden Parameter in ``tornado.parameter`` wird jeder Wert aus seinem
``sens``-Feld einzeln eingesetzt, alles andere bleibt auf Basis. Jeder Lauf optimiert die Größen neu –
der Tornado zeigt also, wie sich die LCOH des jeweils *kostenoptimalen* Systems verschiebt.

Parameter, die nur Kosten außerhalb der Optimierung betreffen (Verteilnetz, Gas-Referenz), werden ohne
neuen Solverlauf auf dem Basis-Ergebnis nachgerechnet (``NUR_NACHRECHNUNG``).
"""

from __future__ import annotations

import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from serts import kpi, plots
from serts.config import Config
from serts.prepare import build_zeitreihen
from serts.run import loese, new_run_dir

log = logging.getLogger(__name__)

KENNZAHLEN = [
    "lcoh",
    "gas_lcoh",
    "abstand_gas",
    "lcoh_inkl_netz",
    "gas_lcoh_inkl_netz",
    "solar_gesamt",
    "ee_anteil",
    "co2_t_a",
    "A_koll_m2",
    "V_m3",
    "P_WP_MW",
    "flaeche_m2",
    "speicher_wirkungsgrad",
]
NUR_NACHRECHNUNG = (
    "netz.anteil_strasse",
    "netz.kosten_",
    "netz.hausanschluesse",
    "gas_referenz.",
)


def varianten(cfg: Config) -> list[tuple[str, object]]:
    """(Parameter, Wert)-Paare aus tornado.parameter und deren sens-Werten."""
    out = []
    for pfad in cfg.get("tornado.parameter"):
        sens = cfg.node(pfad).get("sens") or []
        if not sens:
            log.warning("%s hat keine sens-Werte – übersprungen", pfad)
        out += [(pfad, w) for w in sens]
    return out


def _zeile(cfg: Config, pfad: str | None, wert, k: dict) -> dict:
    basis = None if pfad is None else cfg.get(pfad)
    return {
        "parameter": pfad or "basis",
        "wert": wert,
        "basiswert": basis,
        **{x: k.get(x) for x in KENNZAHLEN},
    }


def _lauf(cfg: Config, pfad: str, wert, threads: int | None) -> dict:
    logging.getLogger("linopy").setLevel(logging.WARNING)
    logging.getLogger("pypsa").setLevel(logging.WARNING)
    c = cfg.variante(pfad, wert)
    ts, _ = build_zeitreihen(c, vollstaendig=True)
    _, k, _ = loese(c, ts, threads=threads)
    return _zeile(cfg, pfad, wert, k)


def tornado(cfg: Config, jobs: int = 4) -> Path:
    """Alle Varianten rechnen -> tornado.csv + Tornado-Plots (LCOH, inkl. Netz, Abstand Gas, Solar)."""
    out = new_run_dir(cfg, "tornado")
    ts, _ = build_zeitreihen(cfg, vollstaendig=True)
    n_basis, k_basis, _ = loese(cfg, ts)
    zeilen = [_zeile(cfg, None, None, k_basis)]

    alle = varianten(cfg)
    nach = [(p, w) for p, w in alle if p.startswith(NUR_NACHRECHNUNG)]
    neu = [(p, w) for p, w in alle if not p.startswith(NUR_NACHRECHNUNG)]
    for p, w in nach:  # gleiche Anlage, nur andere Kosten
        k, _ = kpi.auswerten(n_basis, cfg.variante(p, w), ts)
        zeilen.append(_zeile(cfg, p, w, k))

    threads = 1 if jobs > 1 else None
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        futs = [pool.submit(_lauf, cfg, p, w, threads) for p, w in neu]
        for f in as_completed(futs):
            zeilen.append(f.result())
            log.info(
                "Tornado %d/%d: %s = %s",
                len(zeilen),
                len(alle) + 1,
                zeilen[-1]["parameter"],
                zeilen[-1]["wert"],
            )
    df = pd.DataFrame(zeilen)
    df.to_csv(out / "tornado.csv", index=False)
    plots.tornado(
        df, "lcoh", "LCOH Erzeugung [€/MWh]", out / "tornado_lcoh.png", referenz="gas_lcoh"
    )
    plots.tornado(
        df,
        "lcoh_inkl_netz",
        "Wärmepreis inkl. Netz [€/MWh geliefert]",
        out / "tornado_lcoh_inkl_netz.png",
        referenz="gas_lcoh_inkl_netz",
    )
    plots.tornado(
        df, "abstand_gas", "Vorteil ggü. Gas-Referenz [€/MWh]", out / "tornado_abstand_gas.png"
    )
    plots.tornado(df, "solar_gesamt", "Solaranteil [-]", out / "tornado_solaranteil.png")
    return out
