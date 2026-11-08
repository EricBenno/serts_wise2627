# SERTS – Solares Wärmenetz mit Erdbeckenspeicher, Wärmepumpe und PtH

Fallstudie **Bad Lippspringe** (AGS 05774008). Leitfrage, feste Entscheidungen und Modellarchitektur:
`../obsidian/AGENT_BRIEFING_SERTS.md` (hat Vorrang), Inputs/Schema: `../obsidian/Waermenetz_PTES_Modellschema_v3.md`,
Umfang: `../obsidian/Arbeitspakete_Saisonspeicher_Annahmen.md`.

## Schnellstart

```bash
uv sync                      # Python 3.12 + Abhängigkeiten in .venv
uv run serts import-raw      # Rohdaten aus ../Bad Lippspringe nach data/raw kopieren (+ SHA-256 prüfen)
uv run serts prepare         # Zeitreihen 8760 h -> data/processed/
uv run serts offen           # Liste der offenen Parameter (x-Werte)
uv run serts annahmen        # docs/annahmen.md aus config/base.yaml erzeugen
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

Details und Stand der Meilensteine: [docs/struktur.md](docs/struktur.md).
