"""Strompreis-Zeitreihe (AP 6).

Basis: fester Tarif (``strom.preis_fest``). Variante ``day_ahead``: CSV in
``data/raw/strompreise/day_ahead_<jahr>.csv`` mit Spalten ``zeit`` (UTC, Stundenbeginn) und
``preis`` [EUR/MWh] (z. B. SMARD/ENTSO-E, Quelle im Manifest dokumentieren) + ``strom.aufschlag_day_ahead``.
"""

from __future__ import annotations

import pandas as pd

from serts.config import Config
from serts.paths import DATA_RAW


def strompreis(cfg: Config, index: pd.DatetimeIndex) -> pd.Series:
    tarif = cfg.get("strom.tarif")
    if tarif == "fest":
        return pd.Series(float(cfg.get("strom.preis_fest")), index=index, name="strompreis")
    if tarif == "day_ahead":
        jahr = int(cfg.get("zeit.wetterjahr"))
        path = DATA_RAW / "strompreise" / f"day_ahead_{jahr}.csv"
        da = pd.read_csv(path, index_col="zeit", parse_dates=True)["preis"]
        da.index = pd.DatetimeIndex(da.index).tz_localize(None)
        da = da.reindex(index)
        if da.isna().any():
            raise ValueError(f"{path.name}: {int(da.isna().sum())} Stunden fehlen")
        return (da + float(cfg.get("strom.aufschlag_day_ahead"))).rename("strompreis")
    raise ValueError(f"unbekannter Tarif '{tarif}'")
