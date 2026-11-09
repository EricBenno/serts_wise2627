# Rohdaten (unverändert)

Werden mit `uv run serts import-raw` aus dem Team-Ordner `../Bad Lippspringe` kopiert;
`MANIFEST.sha256` hält die Prüfsummen fest (`uv run serts verify-raw`). Liste der Dateien:
`src/serts/sources/rawdata.py` (`RAW_FILES`).

| Ordner | Inhalt | Herkunft | Im Git? |
|---|---|---|---|
| `bad_lippspringe/` | `results netzberechnung.xlsx`: Lastgang 2022 (8760 h, MW) je BDEW-Typ, Netzverluste, Gebäudestatistik | eigene Netzberechnung des Teams | ja (0,5 MB, nicht anders reproduzierbar) |
| `dwd/tu_03028/` | Lufttemperatur/Feuchte stündlich 1971–2025, UTC | DWD CDC `observations_germany/climate/hourly/air_temperature` | nein (öffentlich, 23 MB) |
| `dwd/st_03028/` | Global-/Diffusstrahlung stündlich 1982–08/2011 | DWD CDC `.../hourly/solar` | nein |
| `dwd/eb_03028/` | Erdbodentemperatur 2–100 cm | DWD CDC `.../hourly/soil_temperature` | nein |
| `pvgis/` | Strahlung auf Kollektorebene 2022 (PVGIS-SARAH3) | JRC PVGIS-API, `uv run serts fetch-pvgis` | nein |
| `strompreise/` | `day_ahead_<jahr>.csv` (Spalten `zeit` = Stundenbeginn UTC, `preis` EUR/MWh), DE-LU | Bundesnetzagentur \| SMARD.de (CC BY 4.0) über Energy-Charts-API, `uv run serts fetch-strompreise 2022 2023 2024` | nein |

Nicht importiert (bewusst): GIS-Daten (`*.gpkg`, KWP-NRW-Shapes, QGIS-Projekt), DWD-Sonnenscheindauer (SD).
DWD-Nutzungsbedingungen: Datenlizenz Deutschland – Namensnennung 2.0, Quelle „Deutscher Wetterdienst“ angeben.
