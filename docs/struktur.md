# Struktur und Stand

Leitlinie: **so simpel wie möglich, so komplex wie nötig** (docs/entscheidungen.md E20).

## Das Modell auf einer Seite

```
                 ┌──────────── solar_direkt ─────────────┐
    Kollektor ──>│ solar                                 ▼
                 └── laden ──> [Speicher MWh] ──> entladen_direkt ──> waerme ──> Last
                                     │   (≤ 53 % der Entladung direkt)    ▲   ▲   (Gebäude
                                     └── Quellwärme ──┐                   │   │    + Netzverluste)
    Netzstrom ──> hp_luft ──────────────────────> wp ─┴─> wp_out ─────────┘   │
             └──> hp_speicher (holt Quellwärme aus dem Speicher) ─┘           │
             └──> pth (Mindestleistung = Spitzenlast) ────────────────────────┘
```

- PyPSA minimiert die Jahreskosten (Annuitäten + Strom) über 8760 h und legt dabei die Größen von
  Kollektorfeld, Speicher, Wärmepumpe und PtH fest.
- Speicherpreis in drei Größenstufen: je Stufe ein Lauf, die günstigste gewinnt (E24).
- Zwei Zusatzbedingungen (`constraints.py`): Fläche ≤ 13.000 m² und Direktanteil des Speichers ≤ 53 %.
  Die Speicher-WP darf nur Nov–Mär laufen (Parameter, E21).
- Alle Zahlen stehen in `config/base.yaml` (mit Quelle/Status); Varianten als kleine YAML-Dateien in
  `config/scenarios/`.

## Befehle

```bash
uv run serts run                         # Basis: Größen optimieren, 3 Preisstufen (≈ 2,5 min)
uv run serts run --V 0                   # Variante ohne Speicher
uv run serts run --A 4000 --V 6000       # feste Größen vorgeben
uv run serts run --szenario rl_50        # Szenario (Abweichungen zur Basis)
uv run serts run --stunden 168           # Schnelltest
uv run serts tornado                     # Sensitivitäten (41 Varianten, ≈ 20–25 min)
uv run serts prepare                     # nur Zeitreihen + Plots
uv run serts annahmen                    # docs/annahmen.md neu erzeugen
uv run pytest                            # 43 Tests
```

Ergebnis je Lauf in `results/<zeit>_<szenario>_<label>/`: `kpi.json` (alle Kennzahlen), `zeitreihen.csv`,
`monatsbilanz.png`, `network.nc`, `config.yaml` + `meta.json` (Git-Hash).

## Module (`src/serts/`)

| Modul | Aufgabe |
|---|---|
| `config.py` | YAML laden/prüfen; `cfg.get("a.b")` bricht ab, wenn der Wert fehlt |
| `sources/` | Leser: Netzberechnung (Excel), DWD, Rohdaten-Import |
| `demand.py`, `weather.py`, `solar.py`, `heatpump.py`, `prices.py` | Zeitreihen: Last, T_a, Strahlung, Kollektorleistung, COP, Strompreis |
| `prepare.py` | baut daraus eine Tabelle 8760 h |
| `network.py` | das PyPSA-Netz (Bild oben) |
| `constraints.py` | Fläche + Direktanteil |
| `kpi.py` | Kennzahlen: Bilanzen, Solar-/EE-Anteil, Speicher-η, LCOH, Wärmepreis inkl. Netz, CO₂, Gas-Referenz |
| `ergebnisplots.py` | Grafiken je Lauf: Jahresverlauf, Typwochen, Dauerlinie, Tag×Stunde, Jahresbilanz/Kosten |
| `tornado.py` | Sensitivitäten (Parameterliste `tornado.parameter`, Werte aus `sens`) |
| `economics.py` | VDI 2067-1 (Ersatz, Restwert, Preisdynamik), Netzkosten, Gas-Referenz |
| `run.py`, `cli.py`, `plots.py` | Lauf speichern, Kommandozeile, Abbildungen |

## Stand

| Thema | Stand |
|---|---|
| Daten Bad Lippspringe, Temperatur 2022, Strahlung Normaljahr (PVGIS-TMY) | ✅ |
| Modell + Optimierung der Größen | ✅ (Basis: LCOH ≈ 138 €/MWh, Wärmepreis inkl. Netz ≈ 219 vs. Gas-Fernwärme ≈ 252 €/MWh; Details `docs/ergebnisse.md`) |
| Tests (Bilanzen, Constraints, COP-Prüfwerte, Solites-Definitionen) | ✅ 43 |
| Validierung Dronninglund | ⏭ ausgelassen (Referenzwerte liegen in `data/reference/`) |
| Sensitivitäten (Tornado) | ✅ `serts tornado`, Ergebnisse in `docs/ergebnisse.md` |
| Varianten (PV für WP, Biomasse, Day-Ahead) / Bericht | ⬜ |

## Weiterarbeiten

1. Weitere Sensitivität: Parameter in `tornado.parameter` aufnehmen und `sens`-Werte setzen, dann `serts tornado`.
2. Keymark-Datenblatt HTHEATstore 35/10 → Kollektorkennwerte als `belegt`.
3. Gaspreis-Pfade für die Referenz (der Gaspreis entscheidet, ob das System günstiger als Gas ist).
4. Varianten: PV für die WP, Biomasse statt PtH, Day-Ahead-Strompreis.

## Konventionen

- Einheiten: MW, MWh, m³, °C, EUR (real, Preisbasis 2025, netto).
- Keine Zahl im Code – alles über `cfg.get()`. YAML-Zahlen ohne Kurzform wie `1e6` (wird Text; Validator meldet es).
- Neuer Parameter → `base.yaml` mit einheit/status/quelle → `serts annahmen` → Commit.
- Neue Komplexität nur, wenn sie eine Kernaussage ändert; Begründung in `docs/entscheidungen.md`.

## Notebook

`notebooks/01_modell_erklaert.ipynb` erklärt die Berechnung Schritt für Schritt (Zeitreihen → Netz →
Zusatzbedingungen → Optimieren → VDI-2067-Kosten → Gesamtlauf mit Grafiken). In VS Code öffnen und als Kernel
die `.venv` des Repos wählen; Laufzeit ≈ 2 min. Ausgaben vor dem Commit löschen.
