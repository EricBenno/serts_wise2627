"""Großwärmepumpe (AP 5, BRF §3.4).

COP nach Lorenz mit logarithmischen Mitteltemperaturen:
    T_k = Tlog(Senke ein, Senke aus) + approach
    T_e = Tlog(Quelle ein, Quelle aus) - approach
    COP = eta_G * T_k / (T_k - T_e)          (alle Temperaturen in K)

Prüfwerte (BRF §3.4, Senke 45 -> 75 degC, approach 3 K):
    Quelle 15 -> 10 degC, eta_G 0,60  -> COP ≈ 3,8
    Quelle 50 -> 40 degC, eta_G 0,45  -> COP ≈ 7,3
(Die Quell-Spreizung ist im BRF nicht genannt; die Prüfwerte werden nur mit 5 K bzw. 10 K
reproduziert -> docs/entscheidungen.md E5.)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from serts.config import Config

K0 = 273.15


def tlog(t_ein_c, t_aus_c):
    """Logarithmische Mitteltemperatur in K (Eingabe degC)."""
    a = np.asarray(t_ein_c, dtype=float) + K0
    b = np.asarray(t_aus_c, dtype=float) + K0
    with np.errstate(divide="ignore", invalid="ignore"):
        m = (a - b) / np.log(a / b)
    return np.where(np.isclose(a, b), (a + b) / 2.0, m)


def cop_lorenz(senke_ein, senke_aus, quelle_ein, quelle_aus, eta_g, approach=3.0):
    t_k = tlog(senke_ein, senke_aus) + approach
    t_e = tlog(quelle_ein, quelle_aus) - approach
    if np.any(t_k <= t_e):
        raise ValueError("Verdampfung >= Kondensation: Quelle zu warm für Lorenz-Ansatz")
    return eta_g * t_k / (t_k - t_e)


def cop_luft(cfg: Config, T_a: pd.Series) -> pd.Series:
    """COP Luftquelle je Stunde inkl. Abtauabschlag."""
    T_rl, T_vl = cfg.get("netz.T_RL"), cfg.get("netz.T_VL")
    dT = cfg.get("waermepumpe.luft_spreizung")
    cop = cop_lorenz(
        T_rl,
        T_vl,
        T_a,
        T_a - dT,
        eta_g=cfg.get("waermepumpe.eta_G_luft"),
        approach=cfg.get("waermepumpe.approach"),
    )
    abtau = np.where(
        T_a < cfg.get("waermepumpe.abtau_grenze"), 1.0 - cfg.get("waermepumpe.abtau_abschlag"), 1.0
    )
    return pd.Series(cop * abtau, index=T_a.index, name="COP_luft")
