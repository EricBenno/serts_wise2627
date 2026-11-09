"""Strompreis-Zeitreihe (AP 6) in Komponenten.

Gesamtpreis(t) = Energie(t) + Netzentgelt (Arbeitspreis) + Abgaben   [EUR/MWh]

- Tarif ``fest``: ``strom.preis_fest`` ist der Gesamtpreis; Energie = Gesamt - Netzentgelt - Abgaben.
- Tarif ``day_ahead``: Energie(t) = Day-Ahead(t) + ``strom.vertriebsmarge``. Day-Ahead-Stundenpreise
  (DE-LU) des Jahres ``strom.preisjahr`` aus ``data/raw/strompreise/day_ahead_<jahr>.csv`` (Spalten ``zeit``
  = Stundenbeginn UTC, ``preis`` EUR/MWh; Quelle Bundesnetzagentur | SMARD.de, CC BY 4.0, geladen über die
  Energy-Charts-API, siehe ``fetch_day_ahead``). Schaltjahr: 29.02. wird verworfen -> 8760 Stunden.
  Das Preisjahr ist vom Wetterjahr unabhängig (Stunde i des Preisjahres -> Stunde i des Modelljahres).
- ``strom.day_ahead_normieren`` = true: das Day-Ahead-Profil wird so skaliert, dass der Jahresmittelwert der
  Energiekomponente dem festen Tarif entspricht -> vergleicht nur die zeitliche Struktur, nicht das Preisniveau.

Nicht modelliert: Leistungspreis (EUR/kW und Jahr auf die höchste Netzbezugsleistung).
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from serts.config import Config
from serts.paths import DATA_RAW

ENERGY_CHARTS_URL = "https://api.energy-charts.info/price"


def pfad_day_ahead(jahr: int) -> Path:
    return DATA_RAW / "strompreise" / f"day_ahead_{jahr}.csv"


def fetch_day_ahead(jahr: int, versuche: int = 4) -> Path:
    """Lädt die Day-Ahead-Stundenpreise DE-LU eines Jahres (Netzzugang nötig) und speichert sie als CSV."""
    import requests

    params = {"bzn": "DE-LU", "start": f"{jahr}-01-01", "end": f"{jahr}-12-31"}
    for i in range(versuche):
        r = requests.get(
            ENERGY_CHARTS_URL,
            params=params,
            timeout=60,
            headers={"User-Agent": "SERTS-student-project"},
        )
        if r.status_code != 429:  # Rate-Limit der API -> warten und erneut versuchen
            break
        time.sleep(20 * (i + 1))
    r.raise_for_status()
    d = r.json()
    df = pd.DataFrame({"zeit": pd.to_datetime(d["unix_seconds"], unit="s"), "preis": d["price"]})
    ziel = pfad_day_ahead(jahr)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ziel, index=False)
    return ziel


def reihe_aus_csv(path: Path) -> pd.Series:
    """Day-Ahead-Reihe als 8760 Werte (29.02. verworfen), Index 0..8759."""
    df = pd.read_csv(path, parse_dates=["zeit"])
    df = df[~((df["zeit"].dt.month == 2) & (df["zeit"].dt.day == 29))]
    werte = df["preis"].to_numpy()
    if len(werte) < 8760:
        raise ValueError(f"{path.name}: nur {len(werte)} Stunden (erwartet >= 8760)")
    return pd.Series(werte[:8760], name="day_ahead")


def netz_und_abgaben(cfg: Config) -> tuple[float, float]:
    """Konstante Preisanteile [EUR/MWh]: (Netzentgelt, Abgaben)."""
    return float(cfg.get("strom.netzentgelt")), float(cfg.get("strom.abgaben"))


def strompreis(cfg: Config, index: pd.DatetimeIndex) -> pd.Series:
    netz, abgaben = netz_und_abgaben(cfg)
    gesamt = float(cfg.get("strom.preis_fest"))
    tarif = cfg.get("strom.tarif")
    if gesamt < netz + abgaben:
        raise ValueError(
            f"strom.preis_fest ({gesamt}) kleiner als Netzentgelt + Abgaben ({netz + abgaben})"
        )
    if tarif == "fest":
        return pd.Series(gesamt, index=index, name="strompreis")
    if tarif == "day_ahead":
        jahr = int(cfg.get("strom.preisjahr"))
        da = reihe_aus_csv(pfad_day_ahead(jahr))
        if len(da) != len(index):
            raise ValueError(f"Day-Ahead hat {len(da)} Stunden, Modell {len(index)}")
        energie = da.to_numpy() + float(cfg.get("strom.vertriebsmarge"))
        if cfg.get("strom.day_ahead_normieren"):
            ziel = gesamt - netz - abgaben  # Energieanteil des festen Tarifs
            energie = energie * (ziel / energie.mean())
        return pd.Series(energie + netz + abgaben, index=index, name="strompreis")
    raise ValueError(f"unbekannter Tarif '{tarif}'")
