"""Kollektorfeld (AP 2, BRF §3.3).

Kennlinie (EN ISO 9806, quasi-stationär, ohne Einfallswinkelkorrektur):
    eta = eta0 - a1 * (T_m - T_a) / G - a2 * (T_m - T_a)^2 / G,  eta >= 0

Ausgabe als spezifische Leistung in kW/m2. Im PyPSA-Netz gilt dann
    p_nom = A_Koll[m2] * 1e-3  (MW bei 1 kW/m2)   und   p_max_pu = P_spez[kW/m2]  (<= 1).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from serts.config import Config


def wirkungsgrad(G, T_m, T_a, eta0: float, a1: float, a2: float):
    """Kollektorwirkungsgrad [-]; 0 bei G <= 0 und bei negativer Kennlinie."""
    G = np.asarray(G, dtype=float)
    dT = np.asarray(T_m, dtype=float) - np.asarray(T_a, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        eta = eta0 - a1 * dT / G - a2 * dT**2 / G
    eta = np.where(G > 0, eta, 0.0)
    return np.clip(eta, 0.0, None)


def spez_leistung(G, T_m, T_a, eta0, a1, a2, feldverluste: float):
    """Nutzbare Leistung je m2 Bruttofläche [kW/m2] nach Feld-/Rohrverlusten."""
    eta = wirkungsgrad(G, T_m, T_a, eta0, a1, a2)
    return eta * np.asarray(G, dtype=float) * (1.0 - feldverluste) / 1000.0


def kollektor_zeitreihen(cfg: Config, G_poa: pd.Series, T_a: pd.Series) -> pd.DataFrame:
    """``P_hi`` (T_m hoch) und ``P_lo`` (T_m tief) in kW/m2."""
    kw = dict(
        eta0=cfg.get("kollektor.eta0"),
        a1=cfg.get("kollektor.a1"),
        a2=cfg.get("kollektor.a2"),
        feldverluste=cfg.get("kollektor.feldverluste"),
    )
    G = G_poa.reindex(T_a.index)
    if G.isna().any():
        raise ValueError("Strahlung und Temperatur haben unterschiedliche Zeitachsen")
    return pd.DataFrame(
        {
            "P_hi": spez_leistung(G, cfg.get("kollektor.T_m_hoch"), T_a, **kw),
            "P_lo": spez_leistung(G, cfg.get("kollektor.T_m_tief"), T_a, **kw),
        },
        index=T_a.index,
    )


def frostschutz_last(cfg: Config, T_a: pd.Series, solarertrag_MWh: float) -> pd.Series:
    """Frostschutzbedarf [MW]: Anteil des Jahresertrags (Feld gesamt), gleich auf Froststunden verteilt."""
    frost = (T_a < 0).astype(float)
    n = frost.sum()
    if n == 0:
        return frost * 0.0
    return frost * cfg.get("kollektor.frostschutz_anteil") * solarertrag_MWh / n
