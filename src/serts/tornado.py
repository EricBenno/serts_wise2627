"""Sensitivitäten als Tornado (BRF §1 Pflicht 6, AP 12).

Vorgehen (bewusst einfach): Für jeden Parameter in ``tornado.parameter`` wird jeder Wert aus seinem
``sens``-Feld einzeln eingesetzt, alles andere bleibt auf Basis. Jeder Lauf optimiert die Größen neu –
der Tornado zeigt also, wie sich die LCOH des jeweils *kostenoptimalen* Systems verschiebt.
"""

from __future__ import annotations

import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from serts import plots
from serts.config import Config
from serts.prepare import build_zeitreihen
from serts.run import loese, new_run_dir

log = logging.getLogger(__name__)

KENNZAHLEN = [
    "lcoh",
    "gas_lcoh",
    "solar_gesamt",
    "ee_anteil",
    "co2_t_a",
    "A_koll_m2",
    "V_m3",
    "P_WP_MW",
    "flaeche_m2",
    "speicher_wirkungsgrad",
]


def varianten(cfg: Config) -> list[tuple[str, object]]:
    """(Parameter, Wert)-Paare aus tornado.parameter und deren sens-Werten."""
    out = []
    for pfad in cfg.get("tornado.parameter"):
        sens = cfg.node(pfad).get("sens") or []
        if not sens:
            log.warning("%s hat keine sens-Werte – übersprungen", pfad)
        out += [(pfad, w) for w in sens]
    return out


def _lauf(cfg: Config, pfad: str | None, wert, threads: int | None) -> dict:
    logging.getLogger("linopy").setLevel(logging.WARNING)
    logging.getLogger("pypsa").setLevel(logging.WARNING)
    c = cfg if pfad is None else cfg.variante(pfad, wert)
    ts, _ = build_zeitreihen(c, vollstaendig=True)
    _, k, _ = loese(c, ts, threads=threads)
    basis = None if pfad is None else cfg.get(pfad)
    return {
        "parameter": pfad or "basis",
        "wert": wert,
        "basiswert": basis,
        **{x: k.get(x) for x in KENNZAHLEN},
    }


def tornado(cfg: Config, jobs: int = 3) -> Path:
    """Alle Varianten rechnen -> tornado.csv + tornado_lcoh.png + tornado_solaranteil.png."""
    out = new_run_dir(cfg, "tornado")
    laeufe = [(None, None), *varianten(cfg)]
    threads = 1 if jobs > 1 else None
    zeilen = []
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        futs = [pool.submit(_lauf, cfg, p, w, threads) for p, w in laeufe]
        for f in as_completed(futs):
            zeilen.append(f.result())
            log.info(
                "Tornado %d/%d: %s = %s",
                len(zeilen),
                len(laeufe),
                zeilen[-1]["parameter"],
                zeilen[-1]["wert"],
            )
    df = pd.DataFrame(zeilen)
    df.to_csv(out / "tornado.csv", index=False)
    plots.tornado(df, "lcoh", "LCOH [€/MWh]", out / "tornado_lcoh.png")
    plots.tornado(df, "solar_gesamt", "Solaranteil [-]", out / "tornado_solaranteil.png")
    return out
