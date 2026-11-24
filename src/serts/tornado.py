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
from serts.run import loese, new_run_dir, niedrige_prioritaet

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
    "P_WP_luft_MW",
    "P_WP_speicher_MW",
    "jaz_wp",
    "cop_speicher_mittel",
    "E_strom_MWh",
    "Q_boost_MWh",
    "Q_pth_waerme_MWh",
    "flaeche_m2",
    "speicher_wirkungsgrad",
    "speicher_zyklen",
    "speicher_direktanteil",
]
NUR_NACHRECHNUNG = (
    "netz.anteil_strasse",
    "netz.kosten_",
    "netz.hausanschluesse",
    "gas_referenz.",
)


def varianten(cfg: Config, nur: list[str] | None = None) -> list[tuple[str, object]]:
    """(Parameter, Wert)-Paare aus tornado.parameter (oder ``nur``) und deren sens-Werten."""
    out = []
    for pfad in nur or cfg.get("tornado.parameter"):
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


def _lauf(cfg: Config, pfad: str, wert, threads: int | None, start: int | None) -> dict:
    logging.getLogger("linopy").setLevel(logging.WARNING)
    logging.getLogger("pypsa").setLevel(logging.WARNING)
    c = cfg.variante(pfad, wert)
    if (
        pfad == "strom.preis_fest"
    ):  # wirkt nur beim festen Tarif: Variante = fester Tarif statt Day-Ahead (E43)
        c = c.variante("strom.tarif", "fest")
    ts, _ = build_zeitreihen(c, vollstaendig=True)
    _, k, _ = loese(c, ts, threads=threads, start_segment=start)
    return _zeile(cfg, pfad, wert, k)


def tornado(cfg: Config, jobs: int = 6, nur: list[str] | None = None) -> Path:
    """Alle Varianten rechnen -> tornado.csv + Tornado-Plots (LCOH, inkl. Netz, Abstand Gas, Solar).

    ``nur``: nur diese Parameter (z. B. ["netz.T_VL"]) statt der ganzen Liste ``tornado.parameter``.
    """
    out = new_run_dir(cfg, "tornado" if not nur else "sensitivitaet")
    ts, _ = build_zeitreihen(cfg, vollstaendig=True)
    n_basis, k_basis, _ = loese(cfg, ts, jobs=jobs)  # alle Segmente, parallel
    start = k_basis.get("segment_index")  # Varianten: nur Nachbarsegmente (docs E42)
    zeilen = [_zeile(cfg, None, None, k_basis)]

    alle = varianten(cfg, nur)
    nach = [(p, w) for p, w in alle if p.startswith(NUR_NACHRECHNUNG)]
    neu = [(p, w) for p, w in alle if not p.startswith(NUR_NACHRECHNUNG)]
    for p, w in nach:  # gleiche Anlage, nur andere Kosten
        k, _ = kpi.auswerten(n_basis, cfg.variante(p, w), ts)
        zeilen.append(_zeile(cfg, p, w, k))

    threads = 1 if jobs > 1 else None
    with ProcessPoolExecutor(max_workers=jobs, initializer=niedrige_prioritaet) as pool:
        futs = [pool.submit(_lauf, cfg, p, w, threads, start) for p, w in neu]
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
        df, "lcoh", "LCOH generation [€/MWh]", out / "tornado_lcoh.png", referenz="gas_lcoh"
    )
    plots.tornado(
        df,
        "lcoh_inkl_netz",
        "Heat price incl. network [€/MWh delivered]",
        out / "tornado_lcoh_inkl_netz.png",
        referenz="gas_lcoh_inkl_netz",
    )
    plots.tornado(
        df, "abstand_gas", "Advantage over gas reference [€/MWh]", out / "tornado_abstand_gas.png"
    )
    plots.tornado(df, "solar_gesamt", "Solar share [-]", out / "tornado_solaranteil.png")
    return out
