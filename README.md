# SERTS – Solares Wärmenetz mit Erdbeckenspeicher, Wärmepumpe und PtH

Fallstudie **Bad Lippspringe** (AGS 05774008). Ein einfaches, nachvollziehbares PyPSA-Modell: Kollektorfeld,
Erdbeckenspeicher, Wärmepumpe (Luft/Speicher) und PtH versorgen das Netz; die Größen werden kostenoptimal
bestimmt. Leitlinie: so simpel wie möglich, so komplex wie nötig. Hintergrund: `../obsidian/` (Briefing,
Modellschema, Arbeitspakete); Abweichungen davon in [docs/entscheidungen.md](docs/entscheidungen.md).

## Key Findings (Stand 15.11.2026, vorläufig)

| | Netz klein (13.000 m²) | Netz groß (80.000 m²) |
|---|---|---|
| Kostenoptimum Kollektor / Speicher | 4.670 m² / 6.000 m³ | 29.800 m² / 30.300 m³ |
| Wärmepreis inkl. Netz (Gas-Fernwärme) | **243 €/MWh** (261) | **222 €/MWh** (236) |
| mit BEW Modul 2 (Obergrenze) | 209 €/MWh | 193 €/MWh |
| Solaranteil / Speicher | 40 % / Mischspeicher (3,2 Zyklen) | 31 % / Kurzzeit (4,3 Zyklen) |

- **Solar + Speicher lohnt sich:** ≈ 34 €/MWh günstiger als reine Wärmepumpe + PtH und ≈ 7 % unter Gas-Fernwärme.
- **Der Vorsprung ist knapp:** Gas- und Strompreis, Effizienz der Luft-WP und Zins entscheiden. Bei einem 15 % schlechteren
  WP-Gütegrad ist der Vorteil gegenüber Gas weg.
- **Die Fläche ist der Engpass:** Ohne Flächengrenze wird ein **Saisonspeicher** die günstigste Lösung.
  - klein: 33.400 m³, 92 % Solar, −18 €/MWh, braucht ≈ 3,9 ha
  - groß: ≥ 200.000 m³, 73 % Solar, −35 €/MWh, braucht ≈ 24 ha

  Obergrenze, weil Fläche im Modell nichts kostet.
- **Day-Ahead-Strom:** WP/PtH laden den Speicher in billigen Stunden. 2024er Preise ergeben 220 €/MWh; selbst mit dem
  Krisenjahr 2022 bleibt das System unter Gas.

| Wer deckt wann die Last? (Netz klein) | Sensitivitäten Wärmepreis (Netz klein) |
|---|---|
| ![Jahresverlauf](docs/img/jahresverlauf_klein.png) | ![Tornado](docs/img/tornado_klein.png) |
| **Heatmap Netz klein** (Kreis = bester Rasterpunkt) | **Heatmap Netz groß** |
| ![Heatmap klein](docs/img/heatmap_klein.png) | ![Heatmap groß](docs/img/heatmap_gross.png) |

Details: [docs/ergebnisse.md](docs/ergebnisse.md), [docs/ergebnisse_netz_gross.md](docs/ergebnisse_netz_gross.md).

## Schnellstart

```bash
uv sync                      # Python 3.12 + Abhängigkeiten in .venv
uv run serts import-raw      # Rohdaten aus ../Bad Lippspringe nach data/raw kopieren (+ SHA-256 prüfen)
uv run serts prepare         # Zeitreihen 8760 h -> data/processed/
uv run serts offen           # Liste der offenen Parameter (x-Werte)
uv run serts annahmen        # docs/annahmen.md aus config/base.yaml erzeugen
uv run serts fetch-pvgis     # Strahlung 2022 (einmalig, Netzzugang)
uv run serts run             # Lauf: Größen optimieren, Kennzahlen ausgeben (≈ 4 min)
uv run serts run --V 0       # Variante ohne Speicher (weitere Optionen: --A, --szenario, --stunden)
uv run serts run --netz gross  # größeres Netz (877 Gebäude, 8 ha); Ergebnisse getrennt in results/gross/
uv run serts uebersicht      # docs/eingangsparameter.md: zentrale Übersicht der Eingangsparameter
uv run serts varianten       # Vergleich Basis / ohne Speicher / nur WP+PtH / mit BEW (+ Gas), ≈ 10 min
uv run serts heatmap         # Raster Kollektorfläche x Speichervolumen (≈ 12 min)
uv run serts tornado         # Sensitivitäten (≈ 2,5 h), Ergebnisse: docs/ergebnisse.md
uv run pytest                # Tests
```

## Struktur

```
config/base.yaml            alle Parameter: wert, einheit, status (belegt|vorgabe|annahme|offen), quelle
config/netze/gross.yaml     Netzfall "gross" (Lastgang, Trasse, Fläche); Netz "klein" = Basis
config/scenarios/*.yaml     nur Abweichungen zur Basis (kombinierbar: --szenario a+b)
data/raw/                   Rohdaten unverändert (im Git, Prüfsummen in data/raw/MANIFEST.sha256)
data/processed/<netz>/      erzeugte Zeitreihen je Netz (nicht im Git, reproduzierbar per `serts prepare`)
data/reference/             Referenzwerte Dronninglund (Solites 2019) für Validierung
docs/                       Datenbasis, Entscheidungen, Annahmen (generiert), Modellgrenzen
src/serts/                  Paket (siehe docs/struktur.md)
tests/                      pytest
results/<netz>/<lauf-id>/   Laufergebnisse je Netz (klein|gross) inkl. Config-Kopie + Git-Hash (nicht im Git)
notebooks/                  nur Auswertung, keine Logik
```

Passt das Modell zur Leitfrage? [docs/kernfragen.md](docs/kernfragen.md). Zentrale Übersicht aller wichtigen Eingangsparameter (Netz klein und groß nebeneinander): [docs/eingangsparameter.md](docs/eingangsparameter.md).
Details und Stand: [docs/struktur.md](docs/struktur.md). Ergebnisse: [docs/ergebnisse.md](docs/ergebnisse.md),
offene Kostenpunkte: [docs/unsicherheiten.md](docs/unsicherheiten.md), Systemskizze: [docs/systemskizze.md](docs/systemskizze.md),
BEW-Förderung: [docs/foerderung_bew.md](docs/foerderung_bew.md), Vorschläge: [docs/ausblick.md](docs/ausblick.md).
Speichermodell: [docs/speichermodell.md](docs/speichermodell.md), geprüft gegen Dronninglund: [docs/validierung_dronninglund.md](docs/validierung_dronninglund.md).
Wie die Berechnung funktioniert: [notebooks/01_modell_erklaert.ipynb](notebooks/01_modell_erklaert.ipynb).

## Projekt weitergeben / auf einem neuen Rechner einrichten

**Nie die `.venv` mitkopieren** (auch nicht im Zip): sie enthält absolute Pfade zum Python dieses Rechners und
funktioniert woanders nicht oder nur scheinbar. Der Jupyter-Kernel „Python 3 (.venv)“ ist keine Datei im Projekt,
sondern einfach diese Umgebung – er entsteht beim Empfänger neu durch `uv sync`.

Das Projekt liegt im **privaten GitHub-Repo [EricBenno/serts_wise2627](https://github.com/EricBenno/serts_wise2627)**.
Zugriff nur für eingeladene Personen: GitHub-Konto anlegen, vom Repo-Besitzer unter *Settings → Collaborators*
einladen lassen, Einladung annehmen.

Neu einrichten (Windows/macOS/Linux; einmalig [Git](https://git-scm.com) und [uv](https://docs.astral.sh/uv/) installieren):

```bash
git clone https://github.com/EricBenno/serts_wise2627.git serts   # beim ersten Mal öffnet sich der GitHub-Login im Browser
cd serts
uv sync                      # Python 3.12 + exakt die Paketversionen aus uv.lock in eine neue .venv
uv run serts verify-raw      # Prüfsummen der Rohdaten
uv run pytest                # alle Tests grün? dann rechnet das Modell wie hier
```

Zusammenarbeiten: vor dem Arbeiten `git pull`, nach dem Committen `git push`. Größere Änderungen auf einem eigenen
Branch (`git switch -c mein-thema`), dann auf GitHub als Pull Request in `main` zusammenführen.

Was im Repo liegt: Code, Config, Doku, alle Rohdaten (Netzberechnungen, DWD, PVGIS, Strompreise, KWW). Nicht im
Repo: `.venv`, `data/processed/` (per `serts prepare`), `results/` (aus `config.yaml` + Git-Hash in `meta.json`
reproduzierbar; die Grafiken oben liegen als Kopie in `docs/img/`). `import-raw` braucht man nur, wenn sich Dateien im
Team-Ordner ändern.

Ohne GitHub (z. B. Abgabe als Zip): `git archive --format=zip -o serts.zip HEAD` – nur versionierte Dateien.

Was schiefgehen kann: alte `.venv`/Kernel aus einer Kopie (löschen, `uv sync`); Notebook mit veraltetem
Kernel-Stand („Restart Kernel“); Windows-Konsole und Umlaute (die CLI gibt UTF-8 aus); Commits enthalten Name und
E-Mail des Autors (sichtbar für alle mit Zugriff).
