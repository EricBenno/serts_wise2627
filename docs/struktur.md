# Struktur und Stand

Leitlinie: **so simpel wie möglich, so komplex wie nötig** (docs/entscheidungen.md E20).

## Das Modell auf einer Seite

Als Mermaid-Diagramm (exakt wie gerechnet): [docs/systemskizze.md](systemskizze.md). Weiterführend:
[PTES-Obergrenze](ptes_obergrenze.md), [BEW-Förderung](foerderung_bew.md), [Ausblick](ausblick.md).

```
                 ┌──────────── solar_direkt ─────────────┐
    Kollektor ──>│ solar                                 ▼
                 └── laden ──> [Speicher heiß | kalt] ──> entladen_direkt ──> waerme ──> Last
                                  (53 % | 47 %)  └── Quellwärme ──┐              ▲   ▲
    Netzstrom ──> hp_luft ─────────────────────────────────> wp ──┴> wp_out ─────┘   │
             └──> hp_speicher (holt Quellwärme aus dem kalten Teil) ┘                 │
             └──> pth (Mindestleistung = Spitzenlast) ──────────────────────────────┘
```

- PyPSA minimiert die Jahreskosten (Annuitäten + Strom) über 8760 h und legt dabei die Größen von
  Kollektorfeld, Speicher, Wärmepumpe und PtH fest.
- **Speicher in zwei Teilen** (heiß: direkt nutzbar, kalt: nur über die WP), Beladen im festen Verhältnis 53 : 47 (E27).
- Speicherkosten als stetige, mit der Größe degressive Kurve (stückweise linear): je Kostensegment ein Lauf, das günstigste gewinnt (E30).
- Drei Zusatzbedingungen (`constraints.py`): Fläche ≤ 13.000 m², Speicherteile im festen Größenverhältnis,
  Luft-WP-Leistung sinkt bei Kälte.
- Kosten nach VDI 2067-1 inkl. 10 % Nebenkosten; Strom in Energie/Netzentgelt/Abgaben getrennt; Wärmenetz
  (Trasse, Hausanschlüsse) getrennt ausgewiesen (E25, E28).
- Alle Zahlen stehen in `config/base.yaml` (mit Quelle/Status); Varianten als kleine YAML-Dateien in
  `config/scenarios/`.

## Befehle

```bash
uv run serts run                         # Basis: Größen optimieren, 5 Kostensegmente (≈ 2 min)
uv run serts run --V 0                   # Variante ohne Speicher
uv run serts run --A 4000 --V 6000       # feste Größen vorgeben
uv run serts run --szenario rl_50        # Szenario (Abweichungen zur Basis); kombinierbar: --szenario a+b
uv run serts run --netz gross            # größeres Netz (config/netze/gross.yaml), Ausgabe in results/gross/
uv run serts uebersicht                  # docs/eingangsparameter.md (Netz klein + groß) neu erzeugen
uv run serts run --stunden 168           # Schnelltest
uv run serts tornado                     # Sensitivitäten (≈ 45 Varianten, ≈ 20–25 min)
uv run serts prepare                     # nur Zeitreihen + Plots
uv run serts annahmen                    # docs/annahmen.md neu erzeugen
uv run serts fetch-strompreise 2022 2023 2024   # Day-Ahead-Preise laden (einmalig, Netzzugang)
uv run serts run --szenario strom_day_ahead_2024  # Strom als Zeitreihe statt fester Tarif
uv run pytest                            # 71 Tests
```

Ergebnis je Lauf in `results/<netz>/<zeit>_<szenario>_<label>/` (Netz `klein` = Basis, `gross` = größeres Netz;
Zeitreihen in `data/processed/<netz>/<szenario>/`): `kpi.json` (alle Kennzahlen), `zeitreihen.csv`,
`monatsbilanz.png`, `network.nc`, `config.yaml` + `meta.json` (Git-Hash).

## Module (`src/serts/`)

| Modul | Aufgabe |
|---|---|
| `config.py` | YAML laden/prüfen (Basis → Netzfall → Szenario); `cfg.get("a.b")` bricht ab, wenn der Wert fehlt |
| `uebersicht.py` | zentrale Parameterübersicht → `docs/eingangsparameter.md` |
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
| Modell + Optimierung der Größen | ✅ (Basis: Kurzzeitspeicher ≈ 1.640 m³ + 2.540 m² Kollektor, LCOH ≈ 141 €/MWh, Wärmepreis inkl. Netz ≈ 229 vs. Gas-Fernwärme ≈ 257 €/MWh; Details docs/ergebnisse.md) |
| Tests (Bilanzen, Constraints, COP-Prüfwerte, Solites-Definitionen) | ✅ 43 |
| Validierung Dronninglund | ⏭ ausgelassen (Referenzwerte liegen in `data/reference/`) |
| Sensitivitäten (Tornado) | ✅ `serts tornado`, Ergebnisse in `docs/ergebnisse.md` |
| Varianten (PV für WP, Biomasse, Day-Ahead) / Bericht | ⬜ |

## Weiterführend

- Warum kein Saisonspeicher? [docs/saisonaler_speicher.md](saisonaler_speicher.md)
- Strom als Zeitreihe: Szenarien strom_day_ahead_*, Ergebnisse in [docs/ergebnisse.md](ergebnisse.md)

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
