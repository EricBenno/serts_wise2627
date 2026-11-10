# Rohdaten (unverändert)

Werden mit `uv run serts import-raw` aus dem Team-Ordner `../Bad Lippspringe` kopiert;
`MANIFEST.sha256` hält die Prüfsummen fest (`uv run serts verify-raw`). Liste der Dateien:
`src/serts/sources/rawdata.py` (`RAW_FILES`).

| Ordner | Inhalt | Herkunft | Im Git? |
|---|---|---|---|
| `bad_lippspringe/` | `results netzberechnung.xlsx`: Lastgang 2022 (8760 h, MW) je BDEW-Typ, Netzverluste, Gebäudestatistik | eigene Netzberechnung des Teams (klein + `results_gross.xlsx`) | ja (je 0,6 MB, nicht anders reproduzierbar) |
| `dwd/tu_03028/` | Lufttemperatur/Feuchte stündlich 1971–2025, UTC | DWD CDC `observations_germany/climate/hourly/air_temperature` | ja (23 MB) |
| `dwd/st_03028/` | Global-/Diffusstrahlung stündlich 1982–08/2011 | DWD CDC `.../hourly/solar` | ja (21 MB) |
| `dwd/eb_03028/` | Erdbodentemperatur 2–100 cm | DWD CDC `.../hourly/soil_temperature` | ja (18 MB, im Modell derzeit nicht genutzt) |
| `pvgis/` | Strahlung auf Kollektorebene 2022 (PVGIS-SARAH3) | JRC PVGIS-API, `uv run serts fetch-pvgis` | ja (1,2 MB; Abruf 09.11.2026, PVGIS kann Datensätze aktualisieren) |
| `strompreise/` | `day_ahead_<jahr>.csv` (Spalten `zeit` = Stundenbeginn UTC, `preis` EUR/MWh), DE-LU | Bundesnetzagentur \| SMARD.de (CC BY 4.0) über Energy-Charts-API, `uv run serts fetch-strompreise 2022 2023 2024` | ja (0,7 MB; Quelle nennen) |

Nicht importiert (bewusst): GIS-Daten (`*.gpkg`, KWP-NRW-Shapes, QGIS-Projekt), DWD-Sonnenscheindauer (SD).
DWD-Nutzungsbedingungen: Datenlizenz Deutschland – Namensnennung 2.0, Quelle „Deutscher Wetterdienst“ angeben.
