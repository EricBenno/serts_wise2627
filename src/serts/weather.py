"""Wetter-Zeitreihen (AP 1): Außentemperatur aus DWD 03028, Strahlung aus PVGIS.

Strahlungsquelle (``kollektor.strahlungsquelle``):
- ``pvgis_tmy``    Normaljahr (Typical Meteorological Year aus PVGIS-SARAH3, 2005-2023). PVGIS liefert
                   horizontale Werte (GHI, DNI, DHI) -> Umrechnung auf die Kollektorebene mit pvlib
                   (Perez-Modell, Albedo 0,2). Die 8760 Stunden werden der Reihe nach auf das Wetterjahr
                   gelegt (TMY-Monate stammen aus verschiedenen Jahren).
- ``pvgis_sarah3`` gemessenes Jahr ``zeit.wetterjahr`` (2022), von PVGIS direkt auf die Ebene gerechnet.

Die Außentemperatur kommt immer aus DWD 03028 im Wetterjahr (passt zum Lastgang 2022).
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
ALBEDO = 0.2  # pvlib-Standard für Wiese/Gras


def aussentemperatur(cfg: Config) -> pd.Series:
    jahr = int(cfg.get("zeit.wetterjahr"))
    t = dwd.lufttemperatur(TU_FILE, jahr)
    t.index = t.index.tz_localize(None).rename("zeit")
    return t


def pvgis_path(cfg: Config) -> Path:
    quelle = cfg.get("kollektor.strahlungsquelle")
    if quelle == "pvgis_tmy":
        return PVGIS_DIR / "pvgis_tmy_sarah3.csv"
    jahr = int(cfg.get("zeit.wetterjahr"))
    tilt, az = cfg.get("kollektor.neigung"), cfg.get("kollektor.azimut")
    return PVGIS_DIR / f"pvgis_sarah3_{jahr}_tilt{tilt:g}_az{az:g}.csv"


def fetch_pvgis(cfg: Config) -> Path:
    """Lädt die konfigurierte PVGIS-Strahlung nach data/raw/pvgis (Rohdatum, Netzzugang nötig)."""
    from pvlib.iotools import get_pvgis_hourly, get_pvgis_tmy

    lat, lon = cfg.get("standort.lat"), cfg.get("standort.lon")
    if cfg.get("kollektor.strahlungsquelle") == "pvgis_tmy":
        data = get_pvgis_tmy(lat, lon, usehorizon=True, map_variables=True)[0]
    else:
        jahr = int(cfg.get("zeit.wetterjahr"))
        data = get_pvgis_hourly(
            latitude=lat, longitude=lon, start=jahr, end=jahr, raddatabase="PVGIS-SARAH3",
            components=True, surface_tilt=cfg.get("kollektor.neigung"),
            surface_azimuth=cfg.get("kollektor.azimut"),  # pvlib-Konvention: 180 = Süd
            usehorizon=True, map_variables=True,
        )[0]
    out = pvgis_path(cfg)
    out.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(out)
    return out


def tmy_auf_ebene(cfg: Config, tmy: pd.DataFrame) -> pd.Series:
    """TMY (ghi, dni, dhi) -> Globalstrahlung auf der Kollektorebene [W/m2], Index = Wetterjahr."""
    import pvlib

    jahr = int(cfg.get("zeit.wetterjahr"))
    if len(tmy) != 8760:
        raise ValueError(f"TMY hat {len(tmy)} statt 8760 Stunden")
    zeit = pd.date_range(f"{jahr}-01-01", periods=8760, freq="h", tz="UTC")
    # Sonnenstand zur Stundenmitte (Annahme: Werte gelten für die folgende Stunde)
    mitte = zeit + pd.Timedelta(minutes=30)
    loc = pvlib.location.Location(cfg.get("standort.lat"), cfg.get("standort.lon"),
                                  altitude=cfg.get("standort.hoehe"))
    sp = loc.get_solarposition(mitte)
    irr = pvlib.irradiance.get_total_irradiance(
        surface_tilt=cfg.get("kollektor.neigung"),
        surface_azimuth=cfg.get("kollektor.azimut"),
        solar_zenith=sp["apparent_zenith"].to_numpy(),
        solar_azimuth=sp["azimuth"].to_numpy(),
        dni=tmy["dni"].to_numpy(), ghi=tmy["ghi"].to_numpy(), dhi=tmy["dhi"].to_numpy(),
        dni_extra=pvlib.irradiance.get_extra_radiation(mitte).to_numpy(),
        model="perez", albedo=ALBEDO,
    )
    poa = pd.Series(pd.Series(irr["poa_global"]).fillna(0.0).clip(lower=0).to_numpy(),
                    index=zeit.tz_localize(None).rename("zeit"))
    return poa


def strahlung_kollektorebene(cfg: Config) -> pd.DataFrame:
    """Globalstrahlung auf Kollektorebene ``G_poa`` [W/m2], stündlich, Index = Wetterjahr."""
    path = pvgis_path(cfg)
    if not path.exists():
        raise FileNotFoundError(f"{path} fehlt -> `serts fetch-pvgis` (Netzzugang nötig)")
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    if cfg.get("kollektor.strahlungsquelle") == "pvgis_tmy":
        return pd.DataFrame({"G_poa": tmy_auf_ebene(cfg, df)})
    poa = df[["poa_direct", "poa_sky_diffuse", "poa_ground_diffuse"]].sum(axis=1)
    out = pd.DataFrame({"G_poa": poa})
    # PVGIS-Zeitstempel liegen bei HH:10/HH:11 UTC -> auf Stundenbeginn legen
    out.index = pd.DatetimeIndex(out.index).tz_localize(None).floor("h").rename("zeit")
    return out
