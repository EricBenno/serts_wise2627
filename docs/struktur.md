# Struktur und Stand

## Datenfluss

```
../Bad Lippspringe ──serts import-raw──> data/raw (+MANIFEST.sha256)
                                            │
config/base.yaml (+ scenarios/*.yaml) ──────┤
                                            ▼
                                  serts prepare (prepare.py)
          sources/netzberechnung ─> demand.py   ─┐
          sources/dwd            ─> weather.py  ─┼─> data/processed/<szenario>/zeitreihen_2022.csv
          PVGIS (fetch-pvgis)    ─> solar.py    ─┤                     kennzahlen.json, *.png
                                    heatpump.py ─┘
                                            │
                                            ▼  (ab M2)
          network.py + constraints.py ─> PyPSA/HiGHS ─> kpi.py, economics.py, plots.py
                                            │
                                            ▼
                     results/<zeit>_<szenario>/ (config.yaml, meta.json mit Git-Hash, netcdf, kpi.csv)
```

## Module (`src/serts/`)

| Modul | Aufgabe | Stand |
|---|---|---|
| `config.py` | YAML laden, Szenario mischen, prüfen; `get()` bricht bei `null` ab | fertig, getestet |
| `paths.py` | zentrale Pfade | fertig |
| `sources/netzberechnung.py` | Excel der NB lesen, Kennzahlen | fertig, getestet |
| `sources/dwd.py` | DWD-Stundenwerte, Lückenfüllung, Strahlungsklima | fertig, getestet |
| `sources/rawdata.py` | Rohdaten-Import + SHA-256 | fertig |
| `weather.py` | T_a 2022; PVGIS laden/lesen | T_a fertig; PVGIS ungetestet (kein Download erfolgt) |
| `demand.py` | Bedarf an heat_town (Gebäude, Netzverlust, Ankerkunde) | fertig, getestet |
| `heatpump.py` | Lorenz-COP, COP_luft, p_max_pu_luft | fertig, Prüfwerte getestet |
| `solar.py` | Kollektorkennlinie → P_hi/P_lo [kW/m²] | Formel getestet; Kennwerte offen |
| `prices.py` | Strompreis fest / Day-Ahead | fertig; Werte offen |
| `economics.py` | Annuität, LCOH, CO₂-Vermeidungskosten | fertig, getestet |
| `kpi.py` | Speicherbilanz (Solites-Definitionen), Solaranteil | Grundfunktionen getestet; Auswertung aus Netz fehlt |
| `network.py` | PyPSA-Netz bauen; Busse + Pool-Link-Tabelle | **Gerüst** (M2/M3) |
| `constraints.py` | extra_functionality (Volumensumme, Verluste, Fläche, WP-Kapazität) | **Gerüst** (M3) |
| `run.py` | Ergebnisordner mit Config + Git-Hash; Einzel/Raster | Ordner fertig; Läufe M5/M6 |
| `plots.py`, `prepare.py`, `annahmen.py`, `cli.py` | Darstellung, M1-Pipeline, Annahmentabelle, CLI | fertig |

## Meilensteine (BRF §5)

| | Inhalt | Stand |
|---|---|---|
| M0 | Repo, Config-Schema, Tests | ✅ `pytest` grün (37 Tests), `ruff` sauber |
| M1 | Zeitreihen | 🟡 Last, T_a, COP_luft fertig; **Kollektor wartet auf** `kollektor.eta0/a1/a2/neigung` + PVGIS; Strompreis offen |
| M2 | Mini-Netz 48 h ohne Speicher | ⬜ `network.build_network` |
| M3 | Pool-Speicher + Constraints, 8760 h | ⬜ `constraints.py` |
| M4 | Validierung Dronninglund | ⬜ Szenario + Referenz-CSV vorhanden; dänisches Wetter fehlt |
| M5–M9 | Basis, Raster, Varianten, Sensitivitäten, Bericht | ⬜ |

## Weiterarbeiten – nächste Schritte

1. Offene Werte mit Quelle setzen: `uv run serts offen` (aktuell u. a. Kollektorkennwerte, Neigung, Kosten,
   Strompreis, Zins, x_TL, x_HX). Danach `uv run serts annahmen`.
2. PVGIS laden (`uv run serts fetch-pvgis`), Jahressumme gegen DWD-Klima prüfen → M1 abschließen.
3. M2: `build_network` für 48 h ohne Speicher + Test „Energiebilanz < 0,1 %“.
4. M3: Pool-Stores + `constraints.py`, je Constraint ein Mini-Netz-Test mit Handrechnung.

## Konventionen

- Einheiten: MW, MWh, m³, °C; Kelvin nur in `heatpump.py`. Zeitindex tz-naiv, UTC, 8760 h.
- Keine Zahl im Code: alles über `cfg.get()`. Testwerte in Tests sind als solche kommentiert.
- Neuer Parameter → `base.yaml` mit einheit/status/quelle → `serts annahmen` → Commit.
- Notebooks nur zur Auswertung, Logik gehört nach `src/serts`.
- Ergebnisse nur über `run.new_run_dir()` speichern (Config-Kopie + Git-Hash).
