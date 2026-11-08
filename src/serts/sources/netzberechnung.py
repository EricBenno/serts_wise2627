"""Eigene Netzberechnung Bad Lippspringe (``results netzberechnung.xlsx``).

Blätter:
- ``Zusammenfassung``: Gebäudeanzahl und Wärmebedarf je Lastprofiltyp, Rohrdimensionen,
  Trassen-/Hausanschlusslängen, Netzverluste, Netztemperaturen (80/50 degC), GLF.
- ``Lastprofil``: 8760 Stundenwerte 2022 in MW (= MWh/h) je Lastprofiltyp, Summe, Verlust.
- ``Statistik``: Median Nutzfläche und spez. Bedarf je Gebäudetyp (LANUV/ALKIS).

Lastprofiltypen sind BDEW-Kürzel (EFH/MFH Wohnen, GHA Handel, GMK Metall/Kfz,
GKO Gebietskörperschaften/Kreditinstitute) – vermutlich mit BDEW-SLP erzeugt (mit Team klären).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

LAST_SPALTEN = {
    "EFH": "efh",
    "MFH": "mfh",
    "GHA": "gha",
    "GMK": "gmk",
    "GKO": "gko",
    "Summe aller Gebäudetypen": "gebaeude",
    "Verlust": "verlust",
    "Verlust bei extra Dämmung": "verlust_daemmung",
    "Gesamtsumme": "gesamt",
    "Gesamtsumme (extra Dämmung)": "gesamt_daemmung",
}
TYPEN = ["efh", "mfh", "gha", "gmk", "gko"]


def read_lastgang(path: Path) -> pd.DataFrame:
    """Stündlicher Lastgang in MW, Index = Stundenbeginn (tz-naiv, siehe zeit.zeitzone)."""
    df = pd.read_excel(path, sheet_name="Lastprofil", index_col=0, engine="openpyxl")
    missing = set(LAST_SPALTEN) - set(df.columns)
    if missing:
        raise ValueError(f"{path.name}: Spalten fehlen im Blatt Lastprofil: {sorted(missing)}")
    df = df.rename(columns=LAST_SPALTEN)[list(LAST_SPALTEN.values())].astype(float)
    df.index = pd.DatetimeIndex(df.index, name="zeit")
    if len(df) != 8760 or not df.index.is_monotonic_increasing:
        raise ValueError(f"{path.name}: erwartet 8760 aufsteigende Stunden, gefunden {len(df)}")
    if (df.index.to_series().diff().dropna() != pd.Timedelta("1h")).any():
        raise ValueError(f"{path.name}: Zeitstempel nicht stündlich lückenlos")
    return df


def read_zusammenfassung(path: Path) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name="Zusammenfassung", engine="openpyxl")


def read_statistik(path: Path) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name="Statistik", engine="openpyxl", index_col=0)


def kennzahlen(last: pd.DataFrame) -> dict[str, float]:
    """Jahreskennzahlen des Lastgangs (MWh/a bei stündlichen MW-Werten)."""
    gesamt = last["gesamt"]
    return {
        "Q_gebaeude_MWh": float(last["gebaeude"].sum()),
        "Q_verlust_MWh": float(last["verlust"].sum()),
        "Q_verlust_daemmung_MWh": float(last["verlust_daemmung"].sum()),
        "Q_gesamt_MWh": float(gesamt.sum()),
        "P_max_MW": float(gesamt.max()),
        "P_min_MW": float(gesamt.min()),
        "zeit_P_max": str(gesamt.idxmax()),
        "vollaststunden_h": float(gesamt.sum() / gesamt.max()),
        "verlustanteil": float(last["verlust"].sum() / gesamt.sum()),
        **{f"anteil_{t}": float(last[t].sum() / last["gebaeude"].sum()) for t in TYPEN},
    }
