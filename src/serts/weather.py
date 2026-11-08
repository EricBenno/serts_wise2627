"""Wetter-Zeitreihen (AP 1): Außentemperatur aus DWD 03028, Strahlung aus PVGIS-SARAH3.

Zeitbasis im Modell: tz-naive Stunden in UTC (siehe config zeit.zeitzone).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from serts.config import Config
from serts.paths import DATA_RAW
from serts.sources import dwd

log = logging.getLogger(__name__)

TU_FILE = DATA_RAW / "dwd/tu_03028/produkt_tu_stunde_19710401_20251231_03028.txt"
ST_FILE = DATA_RAW / "dwd/st_03028/produkt_st_stunde_19820101_20110831_03028.txt"
PVGIS_DIR = DATA_RAW / "pvgis"


def aussentemperatur(cfg: Config) -> pd.Series:
    jahr = int(cfg.get("zeit.wetterjahr"))
    t = dwd.lufttemperatur(TU_FILE, jahr)
    t.index = t.index.tz_localize(None).rename("zeit")
    return t


def pvgis_path(cfg: Config) -> Path:
    jahr = int(cfg.get("zeit.wetterjahr"))
    tilt = cfg.get("kollektor.neigung")
    az = cfg.get("kollektor.azimut")
    return PVGIS_DIR / f"pvgis_sarah3_{jahr}_tilt{tilt:g}_az{az:g}.csv"


def fetch_pvgis(cfg: Config) -> Path:
    """Lädt PVGIS-Stundenwerte (Strahlung auf geneigte Fläche) und speichert sie in data/raw/pvgis.

    Braucht Netzzugang (JRC-API). Ergebnis ist Rohdatum -> wird nicht verändert.
    """
    from pvlib.iotools import get_pvgis_hourly

    jahr = int(cfg.get("zeit.wetterjahr"))
    res = get_pvgis_hourly(
        latitude=cfg.get("standort.lat"),
        longitude=cfg.get("standort.lon"),
        start=jahr,
        end=jahr,
        raddatabase="PVGIS-SARAH3",
        components=True,
        surface_tilt=cfg.get("kollektor.neigung"),
        surface_azimuth=cfg.get("kollektor.azimut"),  # pvlib-Konvention: 180 = Süd
        usehorizon=True,
        map_variables=True,
    )
    data = res[0]
    out = pvgis_path(cfg)
    out.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(out)
    return out


def strahlung_kollektorebene(cfg: Config) -> pd.DataFrame:
    """Globalstrahlung auf Kollektorebene ``G_poa`` [W/m2] + PVGIS-Lufttemperatur, stündlich."""
    path = pvgis_path(cfg)
    if not path.exists():
        raise FileNotFoundError(f"{path} fehlt -> `serts fetch-pvgis` (Netzzugang nötig)")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    poa = df[["poa_direct", "poa_sky_diffuse", "poa_ground_diffuse"]].sum(axis=1)
    out = pd.DataFrame({"G_poa": poa, "T_a_pvgis": df.get("temp_air")})
    # PVGIS-Zeitstempel liegen bei HH:10/HH:11 UTC -> auf Stundenbeginn legen
    out.index = pd.DatetimeIndex(out.index).tz_localize(None).floor("h").rename("zeit")
    return out
