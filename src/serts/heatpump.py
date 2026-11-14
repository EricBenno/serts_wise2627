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


def cop_kww(t_senke_c, t_quelle_c, guetegrad):
    """KWW-Technikkatalog (Tab. 24/25): COP = Gütegrad * T_Senke / (T_Senke - T_Quelle), Senke = Vorlauf."""
    t_s = np.asarray(t_senke_c, dtype=float) + K0
    t_q = np.asarray(t_quelle_c, dtype=float) + K0
    return guetegrad * t_s / (t_s - t_q)


def vorlauf(cfg: Config, T_a: pd.Series) -> pd.Series:
    """Vorlauftemperatur je Stunde [degC]. Basis: konstant ``netz.T_VL``.

    Gleitend, wenn ``netz.T_VL_min`` < T_VL: T_VL bei Tagesmittel der Außentemperatur <= ``gleit_T_kalt``,
    linear fallend auf T_VL_min bei >= ``gleit_T_warm`` (Mittel der letzten 24 h, das Netz ist träge).
    """
    t_vl, t_min = cfg.get("netz.T_VL"), cfg.get("netz.T_VL_min")
    if t_min >= t_vl:
        return pd.Series(float(t_vl), index=T_a.index, name="T_VL")
    tag = T_a.rolling(24, min_periods=1).mean()
    werte = np.interp(
        tag, [cfg.get("netz.gleit_T_kalt"), cfg.get("netz.gleit_T_warm")], [t_vl, t_min]
    )
    return pd.Series(werte, index=T_a.index, name="T_VL")


def guetegrad_kww(cfg: Config, t_vl=None):
    """Gütegrad der Luft-WP nach KWW, linear zwischen 70 °C (46 %) und 95 °C (44 %) Vorlauf interpoliert."""
    t_vl = cfg.get("netz.T_VL") if t_vl is None else t_vl
    g = np.interp(t_vl, [70.0, 95.0], [0.46, 0.44]) * cfg.get("waermepumpe.guetegrad_faktor")
    return float(g) if np.ndim(g) == 0 else g


def cop_luft(cfg: Config, T_a: pd.Series) -> pd.Series:
    """COP Luftquelle je Stunde.

    ``waermepumpe.cop_ansatz_luft``:
      kww    (Basis) Carnot auf den Vorlauf x Gütegrad nach KWW (JAZ-Bezug, Abtauen im Gütegrad enthalten)
      lorenz (Briefing) Lorenz mit Mitteltemperaturen, eta_G_luft, plus Abtauabschlag
    """
    T_vl = vorlauf(cfg, T_a).to_numpy()  # konstant oder gleitend (netz.T_VL_min)
    if cfg.get("waermepumpe.cop_ansatz_luft") == "kww":
        cop = cop_kww(T_vl, T_a, guetegrad_kww(cfg, T_vl))
        return pd.Series(cop, index=T_a.index, name="COP_luft")
    T_rl = cfg.get("netz.T_RL")
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


def p_max_pu_luft(cfg: Config, T_a: pd.Series) -> pd.Series:
    """Thermische Leistung der Luft-WP relativ zur gebauten Leistung P_WP [-].

    1,0 ab ``luft_leistung_voll_ab``, linear fallend auf ``luft_leistung_bei_tmin`` bei ``T_min_luft``.
    (Oberhalb bleibt 1,0 - konservativ; unterhalb T_min läuft die Luft-WP ohnehin nicht, siehe network.py.)
    """
    t_voll = cfg.get("waermepumpe.luft_leistung_voll_ab")
    t_min = cfg.get("waermepumpe.T_min_luft")
    pu_min = cfg.get("waermepumpe.luft_leistung_bei_tmin")
    pu = np.interp(np.asarray(T_a, dtype=float), [t_min, t_voll], [pu_min, 1.0])
    return pd.Series(pu, index=T_a.index, name="p_max_pu_luft")
