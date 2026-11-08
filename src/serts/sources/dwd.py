"""DWD-CDC-Stundenwerte (Station 03028 Bad Lippspringe).

Formate (Metadaten_Parameter_*.txt):
- TU: ``MESS_DATUM`` = YYYYMMDDHH in UTC, ``TT_TU`` Lufttemperatur [degC], ``RF_TU`` rel. Feuchte [%]
- ST: ``MESS_DATUM`` = YYYYMMDDHH:MM (UTC), ``FG_LBERG``/``FD_LBERG`` Stundensumme Global-/
  Diffusstrahlung [J/cm2], nur 01.01.1982-31.08.2011 -> für 2022 nicht nutzbar, nur Klimavergleich.
Fehlwerte: -999.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

J_CM2_TO_KWH_M2 = 1e4 / 3.6e6  # 1 J/cm2 = 1e4 J/m2 = 1/360 kWh/m2
J_CM2_H_TO_W_M2 = 1e4 / 3600.0  # Stundensumme J/cm2 -> mittlere Leistung W/m2


def read_dwd_product(path: Path, fmt: str = "%Y%m%d%H") -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=";",
        skipinitialspace=True,
        na_values=[-999, "-999"],
        dtype={"MESS_DATUM": str},
    )
    df.columns = [c.strip() for c in df.columns]
    df = df.drop(columns=[c for c in ("eor",) if c in df.columns])
    idx = pd.to_datetime(df.pop("MESS_DATUM").str.strip(), format=fmt, utc=True)
    df.index = pd.DatetimeIndex(idx, name="zeit_utc")
    return df


def _luecken(s: pd.Series) -> list[tuple[pd.Timestamp, int]]:
    """Zusammenhängende NaN-Blöcke als (Start, Länge in h)."""
    na = s.isna()
    block = (na != na.shift()).cumsum()
    return [(g.index[0], len(g)) for _, g in s[na].groupby(block[na])]


def fuelle_tagesgang(s: pd.Series, fenster_tage: int = 7) -> pd.Series:
    """Füllt Lücken mit dem mittleren Tagesgang (gleiche Stunde, +-fenster_tage) und
    verschiebt ihn linear so, dass er an beiden Lückenrändern an die Messwerte anschließt."""
    out = s.copy()
    for start, n in _luecken(s):
        idx = pd.date_range(start, periods=n, freq="h", tz=s.index.tz)
        umfeld = s[
            start - pd.Timedelta(days=fenster_tage) : idx[-1] + pd.Timedelta(days=fenster_tage)
        ]
        gang = umfeld.groupby(umfeld.index.hour).mean()
        fill = pd.Series(gang.reindex(idx.hour).to_numpy(), index=idx)
        vor, nach = s.get(start - pd.Timedelta(hours=1)), s.get(idx[-1] + pd.Timedelta(hours=1))
        h_vor = gang.get((start - pd.Timedelta(hours=1)).hour)
        h_nach = gang.get((idx[-1] + pd.Timedelta(hours=1)).hour)
        off0 = (vor - h_vor) if pd.notna(vor) else 0.0
        off1 = (nach - h_nach) if pd.notna(nach) else off0
        fill += np.linspace(off0, off1, n + 2)[1:-1]
        out.loc[idx] = fill
    return out


def lufttemperatur(path: Path, jahr: int, max_luecke_linear_h: int = 6) -> pd.Series:
    """Lufttemperatur [degC] eines Jahres (UTC, lückenlos).

    Lücken <= max_luecke_linear_h: linear interpoliert; längere Lücken: Tagesgang-Füllung
    (fuelle_tagesgang). 2022 betrifft das 20.05. 16 UTC - 23.05. 11 UTC (68 h), docs E4.
    """
    df = read_dwd_product(path)
    full = pd.date_range(f"{jahr}-01-01 00:00", f"{jahr}-12-31 23:00", freq="h", tz="UTC")
    t = df["TT_TU"].reindex(full)
    for start, n in _luecken(t):
        log.warning("TU %s: Lücke ab %s, %d h", jahr, start, n)
    t = t.interpolate(limit=max_luecke_linear_h, limit_area="inside")
    if t.isna().any():
        t = fuelle_tagesgang(t)
    t.name = "T_a"
    return t


def strahlung_klima(path: Path, von: int = 1991, bis: int = 2010) -> pd.DataFrame:
    """Jahressummen Global-/Diffusstrahlung [kWh/m2] aus DWD ST (nur vollständige Jahre)."""
    df = read_dwd_product(path, fmt="%Y%m%d%H:%M")
    df = df.loc[str(von) : str(bis), ["FG_LBERG", "FD_LBERG"]]
    jahre = df.groupby(df.index.year)
    out = jahre.sum(min_count=1) * J_CM2_TO_KWH_M2
    out["n_fehlend"] = jahre["FG_LBERG"].apply(lambda s: int(s.isna().sum()))
    out.columns = ["G_hor_kWh_m2", "D_hor_kWh_m2", "n_fehlend"]
    return out
