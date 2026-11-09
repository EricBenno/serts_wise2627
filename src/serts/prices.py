"""Strompreis-Zeitreihe (AP 6) in Komponenten.

Gesamtpreis(t) = Energie(t) + Netzentgelt (Arbeitspreis) + Abgaben   [EUR/MWh]

- Tarif ``fest``: ``strom.preis_fest`` ist der Gesamtpreis; Energie = Gesamt - Netzentgelt - Abgaben.
- Tarif ``day_ahead``: Energie(t) = Day-Ahead(t) + ``strom.vertriebsmarge``. CSV in
  ``data/raw/strompreise/day_ahead_<jahr>.csv`` mit Spalten ``zeit`` (UTC, Stundenbeginn) und ``preis``
  [EUR/MWh] (SMARD, Bundesnetzagentur, Quelle nennen; siehe docs/ausblick.md).

Nicht modelliert: Leistungspreis (EUR/kW und Jahr auf die höchste Netzbezugsleistung).
"""

from __future__ import annotations

import pandas as pd

from serts.config import Config
from serts.paths import DATA_RAW


def netz_und_abgaben(cfg: Config) -> tuple[float, float]:
    """Konstante Preisanteile [EUR/MWh]: (Netzentgelt, Abgaben)."""
    return float(cfg.get("strom.netzentgelt")), float(cfg.get("strom.abgaben"))


def strompreis(cfg: Config, index: pd.DatetimeIndex) -> pd.Series:
    netz, abgaben = netz_und_abgaben(cfg)
    tarif = cfg.get("strom.tarif")
    if tarif == "fest":
        gesamt = float(cfg.get("strom.preis_fest"))
        if gesamt < netz + abgaben:
            raise ValueError(
                f"strom.preis_fest ({gesamt}) kleiner als Netzentgelt + Abgaben ({netz + abgaben})"
            )
        return pd.Series(gesamt, index=index, name="strompreis")
    if tarif == "day_ahead":
        jahr = int(cfg.get("zeit.wetterjahr"))
        path = DATA_RAW / "strompreise" / f"day_ahead_{jahr}.csv"
        da = pd.read_csv(path, index_col="zeit", parse_dates=True)["preis"]
        da.index = pd.DatetimeIndex(da.index).tz_localize(None)
        da = da.reindex(index)
        if da.isna().any():
            raise ValueError(f"{path.name}: {int(da.isna().sum())} Stunden fehlen")
        return (da + float(cfg.get("strom.vertriebsmarge")) + netz + abgaben).rename("strompreis")
    raise ValueError(f"unbekannter Tarif '{tarif}'")
