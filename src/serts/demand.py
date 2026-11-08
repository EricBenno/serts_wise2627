"""Wärmebedarf (AP 3): Lastgang der eigenen Netzberechnung Bad Lippspringe.

Abweichung vom BRF (§3.5 nennt demandlib): Es liegt ein projektspezifischer Lastgang je
Gebäudetyp vor (159 Gebäude, 2022). Dieser ist die Basis; demandlib bleibt Werkzeug für die
Sensitivität "Lastprofil" (siehe docs/entscheidungen.md E2).

Netzverluste liegen innerhalb der Systemgrenze (AP 0 Mittel) und werden als eigene Spalte
mitgeführt (konstante 0,107 MW aus der Netzberechnung).
"""

from __future__ import annotations

import pandas as pd

from serts.config import Config
from serts.paths import DATA_RAW
from serts.sources import netzberechnung


def lastgang_roh(cfg: Config) -> pd.DataFrame:
    return netzberechnung.read_lastgang(DATA_RAW / cfg.get("last.datei"))


def ankerkunden_profil(index: pd.DatetimeIndex, art: str, referenz: pd.Series) -> pd.Series:
    """Normiertes Profil (Summe = 1)."""
    if art == "band":
        p = pd.Series(1.0, index=index)
    elif art == "werktag":
        p = pd.Series(((index.dayofweek < 5) & (index.hour >= 6) & (index.hour < 22)), index=index)
        p = p.astype(float)
    elif art == "saisonal":
        p = referenz.astype(float).copy()
    else:
        raise ValueError(f"unbekanntes Ankerkunden-Profil '{art}'")
    return p / p.sum()


def waermebedarf(cfg: Config, roh: pd.DataFrame | None = None) -> pd.DataFrame:
    """Bedarf am Knoten heat_town [MW]: gebaeude, netzverlust, ankerkunde, gesamt."""
    roh = lastgang_roh(cfg) if roh is None else roh
    s = float(cfg.get("last.skalierung"))
    variante = cfg.get("last.netzverlust_variante")
    verlust_col = {"standard": "verlust", "extra_daemmung": "verlust_daemmung"}[variante]

    gebaeude = roh["gebaeude"] * s
    anteil = float(cfg.get("last.ankerkunde_anteil"))
    profil = ankerkunden_profil(roh.index, cfg.get("last.ankerkunde_profil"), gebaeude)
    anker = profil * anteil * gebaeude.sum()

    df = pd.DataFrame({"gebaeude": gebaeude, "netzverlust": roh[verlust_col], "ankerkunde": anker})
    df["gesamt"] = df.sum(axis=1)
    return df
