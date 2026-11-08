# Struktur und Stand

## Datenfluss

```
../Bad Lippspringe ──serts import-raw──> data/raw (+MANIFEST.sha256)
PVGIS-API ─────────serts fetch-pvgis──> data/raw/pvgis
                                            │
config/base.yaml (+ scenarios/*.yaml) ──────┤
                                            ▼
                prepare.build_zeitreihen (8760 h): Last, T_a, COP_luft, p_max_pu_luft,
                G_poa, P_hi, P_lo [kW/m²], Strompreis   (serts prepare -> data/processed + Plots)
                                            │
                                            ▼
          network.build_network(A, V) + constraints.extra_functionality ─> PyPSA/HiGHS
                                            │
                                            ▼
          kpi.auswerten: Bilanzen, Speicher-η, Solaranteil getrennt, EE-Anteil, Caps, Regel-Checks,
                         LCOH (economics), Gas-Referenz, CO₂, Flächencheck (flaeche)
                                            │
                                            ▼
          results/<zeit>_<szenario>_<label>/  config.yaml, meta.json (Git-Hash),
              Einzellauf: kpi.json, zeitreihen.csv, network.nc, monatsbilanz.png
              Raster:     raster.csv, heatmap_lcoh.png, pareto_ee_lcoh.png
```

## Befehle

```bash
uv run serts run --A-spez 0.6 --V-pro-A 1.6          # Einzellauf, ≈ 1–1,5 min
uv run serts run --A-spez 0.6 --V-pro-A 1.6 --stunden 168   # Schnelltest 1 Woche
uv run serts raster --jobs 4                         # 24 Rasterpunkte, ≈ 6–8 min
uv run serts raster --szenario rl_50 --jobs 4        # Raster für ein Szenario
uv run pytest                                        # 45 Tests
```

## Module (`src/serts/`)

| Modul | Aufgabe | Stand |
|---|---|---|
| `config.py` | YAML laden, Szenario mischen, prüfen; `get()` bricht bei `null` ab | fertig |
| `sources/` | NB-Excel, DWD (Lückenfüllung, Strahlungsklima), Rohdaten-Import | fertig |
| `weather.py` | T_a 2022, PVGIS laden/lesen | fertig |
| `demand.py`, `heatpump.py`, `solar.py`, `prices.py` | Last, COP, Kollektor, Strompreis (fest) | fertig; Day-Ahead offen |
| `network.py` | PyPSA-Netz (Pools, Kollektor hi/lo, WP Luft/PTES, PtH, Transmission) | fertig |
| `constraints.py` | Volumensumme, Verluste, gemeinsame Kollektorfläche, WP-Leistung je Quelle | fertig, getestet |
| `kpi.py` | Auswertung gelöster Netze inkl. Regel-Checks BRF §7 | fertig (Basis) |
| `economics.py` | Annuität + O&M, Preisdynamik (VDI 2067), PTES-Kostenkurve, Gas-Referenz | fertig |
| `flaeche.py` | Flächenbedarf Kollektor + PTES vs. 13.000 m² | fertig |
| `run.py`, `cli.py`, `plots.py` | Einzel-/Rasterlauf (parallel), Plots | fertig |

## Meilensteine (BRF §5)

| | Inhalt | Stand |
|---|---|---|
| M0 | Repo, Config, Tests | ✅ |
| M1 | Zeitreihen | ✅ (Kollektorkennwerte = Annahme, E18) |
| M2 | Mini-Netz 48 h ohne Speicher | ✅ Test Energiebilanz < 0,1 % |
| M3 | Pool-Speicher + Constraints | ✅ Tests Volumensumme, Verluste, Fläche, WP-Caps, Speicherbilanz |
| M4 | Validierung Dronninglund | ⏭ übersprungen (braucht dänisches Wetter + Last; Szenario/Referenz liegen bereit) |
| M5 | Basisszenario | ✅ `serts run` (KPI, Monatsbilanz) |
| M6 | Raster, LCOH, CO₂ | ✅ `serts raster` (Heatmap, Pareto) – vereinfacht, s. u. |
| M7–M9 | Varianten, Tornado, Bericht | ⬜ |

**Vereinfachungen (bewusst):** keine Wärmeübertrager-Caps (E12), Fläche nur als Check (E17), PtH-Laden des
PTES und Biomasse-Variante nicht implementiert, Gas-Referenz als Formel statt LP, M4 ausgelassen.

## Weiterarbeiten – sinnvolle nächste Schritte

1. Keymark-Datenblatt HTHEATstore 35/10 besorgen → `kollektor.eta0/a1/a2` als `belegt`.
2. DEA Technology Data (Storage 2025, District Heating) für PTES-, WP-, PtH-Kosten nachziehen.
3. Strahlungsarmes bzw. Normaljahr (z. B. PVGIS-TMY) als Sensitivität „Solarressource“.
4. M7: Varianten als Szenarien (ohne Speicher = V/A 0 ist schon im Raster; PV für WP; Biomasse).
5. M8: Tornado – Schleife über `sens`-Werte in `base.yaml` (Struktur dafür ist vorhanden).

## Konventionen

- Einheiten: MW, MWh, m³, °C, EUR (real, Preisbasis 2025, netto); Kelvin nur in `heatpump.py`.
- Keine Zahl im Code: alles über `cfg.get()`. YAML-Zahlen ohne Exponent-Kurzform (1e6 wird Text!) –
  der Validator meldet das.
- Neuer Parameter → `base.yaml` mit einheit/status/quelle → `serts annahmen` → Commit.
- Ergebnisse nur über `run.new_run_dir()` (Config-Kopie + Git-Hash).
