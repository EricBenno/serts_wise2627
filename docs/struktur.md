# Struktur und Stand

Leitlinie: **so simpel wie möglich, so komplex wie nötig** (docs/entscheidungen.md E20).

## Das Modell auf einer Seite

Als Mermaid-Diagramm (exakt wie gerechnet): [docs/systemskizze.md](systemskizze.md). Weiterführend:
[PTES-Obergrenze](ptes_obergrenze.md), [BEW-Förderung](foerderung_bew.md), [Ausblick](ausblick.md).

```
    Kollektor ──> solar ──┬── solar_direkt ─────────────────────────────────────────────> waerme ──> Last
                          ├── laden_heiss ─> [ heiß (Kern)   85 °C ] ── entladen_direkt ──>   ▲
                          │                  [ Übergangszone       ] ── vorwaermen ───────>   │ (+ Nachheizen)
                          └── laden_kalt ──> [ kalt        10-45 °C] ── Quellwärme ─┐         │
    Netzstrom ──> hp_luft ──────────────────────────────> wp ── wp_out ─────────────┴────────>┤
             └──> hp_speicher (holt Quellwärme aus dem kalten Teil) ┘                         │
             └──> pth (Mindestleistung = Spitzenlast) ────────────────────────────────────────┘
```

- PyPSA minimiert die Jahreskosten (Annuitäten + Strom) über 8760 h und legt dabei die Größen von
  Kollektorfeld, Speicher, Wärmepumpe, PtH und Netzanschluss fest.
- **Speicher in drei Teilen** (E39, erklärt in `docs/speichermodell.md`): heißer Kern (direkt nutzbar),
  Übergangszone (Rücklauf vorwärmen oder über die WP), kalt (nur über die WP). Laden getrennt: `laden_kalt`
  (10 → 45 °C) und `laden_heiss` (45 → 85 °C). Geprüft gegen Dronninglund: `docs/validierung_dronninglund.md`.
- Verlustrate und Übergangszone hängen von der Speichergröße ab (kleine Speicher sind schlechter).
- Speicherkosten als stetige, mit der Größe degressive Kurve (stückweise linear): je Kostensegment ein Lauf, das günstigste gewinnt (E30).
- Zusatzbedingungen (`constraints.py`): Fläche (13.000 bzw. 80.000 m²), Speicherteile im festen Größenverhältnis,
  Luft-WP-Leistung sinkt bei Kälte, **Schichtung** (Füllstand Kern ≤ Übergangszone ≤ kalt), Vorwärmen nur mit
  Nachheizen. Ein Lauf je Kostensegment (die frühere Kennlinie mit zwei Läufen entfällt).
- Strom: Arbeitspreis + **Leistungspreis** auf den höchsten Bezug (Netzbetreiber-Preisblatt).
- Kollektor mit Einfallswinkel-Korrektur der Direktstrahlung; Vorlauf konstant 80 °C, gleitend als Szenario
  `vl_gleitend`.
- Luft-WP: COP nach KWW-Gütegrad (≈ 45 % von Carnot auf den Vorlauf, E35); Speicher-WP COP 4,5.
- BEW Modul 2 wird in jedem Lauf zusätzlich ausgewiesen (Obergrenze 40 %, E37).
- Kosten nach VDI 2067-1 inkl. 10 % Nebenkosten; Strom in Energie/Netzentgelt/Abgaben getrennt; Wärmenetz
  (Trasse, Hausanschlüsse) getrennt ausgewiesen (E25, E28).
- Alle Zahlen stehen in `config/base.yaml` (mit Quelle/Status); Varianten als kleine YAML-Dateien in
  `config/scenarios/`.

## Befehle

```bash
uv run serts run                         # Basis: Größen optimieren, 5 Kostensegmente (≈ 4 min)
uv run serts run --V 0                   # Variante ohne Speicher
uv run serts run --A 4000 --V 6000       # feste Größen vorgeben
uv run serts run --szenario rl_50        # Szenario (Abweichungen zur Basis); kombinierbar: --szenario a+b
uv run serts run --netz gross            # größeres Netz (config/netze/gross.yaml), Ausgabe in results/gross/
uv run serts uebersicht                  # docs/eingangsparameter.md (Netz klein + groß) neu erzeugen
uv run serts run --stunden 168           # Schnelltest
uv run serts varianten [--netz gross]    # Basis / ohne Speicher / nur WP+PtH / mit BEW (+ Gas-Referenz)
uv run serts tornado                     # Sensitivitäten (≈ 45 Varianten, ≈ 1 h)
uv run serts prepare                     # nur Zeitreihen + Plots
uv run serts annahmen                    # docs/annahmen.md neu erzeugen
uv run serts fetch-strompreise 2022 2023 2024   # Day-Ahead-Preise laden (einmalig, Netzzugang)
uv run serts run --szenario strom_day_ahead_2024  # Strom als Zeitreihe statt fester Tarif
uv run serts run --szenario vl_gleitend           # gleitender Vorlauf 80 -> 70 °C
uv run serts run --szenario validierung_dronninglund --A 37573 --V 60000   # Speichermodell prüfen
uv run pytest                            # 95 Tests
```

Ergebnis je Lauf in `results/<netz>/<zeit>_<szenario>_<label>/` (Netz `klein` = Basis, `gross` = größeres Netz;
Zeitreihen in `data/processed/<netz>/<szenario>/`): `kpi.json` (alle Kennzahlen), `zeitreihen.csv`,
`monatsbilanz.png`, `network.nc`, `config.yaml` + `meta.json` (Git-Hash).

## Module (`src/serts/`)

| Modul | Aufgabe |
|---|---|
| `config.py` | YAML laden/prüfen (Basis → Netzfall → Szenario); `cfg.get("a.b")` bricht ab, wenn der Wert fehlt |
| `uebersicht.py` | zentrale Parameterübersicht → `docs/eingangsparameter.md` |
| `varianten.py` | Vergleichsvarianten der Leitfrage (Briefing Pflicht 5) + Pareto-Grafik |
| `sources/` | Leser: Netzberechnung (Excel), DWD, Rohdaten-Import |
| `demand.py`, `weather.py`, `solar.py`, `heatpump.py`, `prices.py` | Zeitreihen: Last, T_a, Strahlung, Kollektorleistung, COP, Strompreis |
| `prepare.py` | baut daraus eine Tabelle 8760 h |
| `network.py` | das PyPSA-Netz (Bild oben) |
| `constraints.py` | Fläche, Speicherverhältnis, Luft-WP bei Kälte, Schichtung, Vorwärmen mit Nachheizen |
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
