# SERTS – Solares Wärmenetz mit Erdbeckenspeicher, Wärmepumpe und PtH

Fallstudie **Bad Lippspringe** (AGS 05774008). Ein einfaches, nachvollziehbares PyPSA-Modell: Kollektorfeld,
Erdbeckenspeicher, Wärmepumpe (Luft/Speicher) und PtH versorgen das Netz; die Größen werden kostenoptimal
bestimmt. Leitlinie: so simpel wie möglich, so komplex wie nötig. Hintergrund: `../obsidian/` (Briefing,
Modellschema, Arbeitspakete); Abweichungen davon in [docs/entscheidungen.md](docs/entscheidungen.md).

## Schnellstart

```bash
uv sync                      # Python 3.12 + Abhängigkeiten in .venv
uv run serts import-raw      # Rohdaten aus ../Bad Lippspringe nach data/raw kopieren (+ SHA-256 prüfen)
uv run serts prepare         # Zeitreihen 8760 h -> data/processed/
uv run serts offen           # Liste der offenen Parameter (x-Werte)
uv run serts annahmen        # docs/annahmen.md aus config/base.yaml erzeugen
uv run serts fetch-pvgis     # Strahlung 2022 (einmalig, Netzzugang)
uv run serts run             # Lauf: Größen optimieren, Kennzahlen ausgeben (≈ 2,5 min)
uv run serts run --V 0       # Variante ohne Speicher (weitere Optionen: --A, --szenario, --stunden)
uv run serts tornado         # Sensitivitäten (≈ 20–25 min), Ergebnisse: docs/ergebnisse.md
uv run pytest                # Tests
```

## Struktur

```
config/base.yaml            alle Parameter: wert, einheit, status (belegt|vorgabe|annahme|offen), quelle
config/scenarios/*.yaml     nur Abweichungen zur Basis
data/raw/                   Rohdaten unverändert (nicht im Git, siehe data/raw/MANIFEST.md)
data/processed/             erzeugte Zeitreihen (nicht im Git, reproduzierbar per `serts prepare`)
data/reference/             Referenzwerte Dronninglund (Solites 2019) für Validierung
docs/                       Datenbasis, Entscheidungen, Annahmen (generiert), Modellgrenzen
src/serts/                  Paket (siehe docs/struktur.md)
tests/                      pytest
results/<lauf-id>/          Laufergebnisse inkl. Config-Kopie + Git-Hash (nicht im Git)
notebooks/                  nur Auswertung, keine Logik
```

Details und Stand: [docs/struktur.md](docs/struktur.md). Ergebnisse: [docs/ergebnisse.md](docs/ergebnisse.md),
offene Kostenpunkte: [docs/unsicherheiten.md](docs/unsicherheiten.md).
Wie die Berechnung funktioniert: [notebooks/01_modell_erklaert.ipynb](notebooks/01_modell_erklaert.ipynb).
