# Was man noch betrachten könnte – Vorschläge

Sortiert nach Nutzen für die Aussage und Aufwand (Aufwand: ● klein, ●● mittel, ●●● groß). Stand 09.11.2026.

## A Kernaussage absichern (empfohlen)

| Vorschlag | Warum | Aufwand |
|---|---|---|
| **Förderung genauer** (Wirtschaftlichkeitslücke statt pauschal 40 %, Modul 4 als Gutschrift, PtH/Hausanschluss klären) | BEW verschiebt das Optimum zu mehr Solar/Speicher | ●● |
| **Strompreisstruktur** (Arbeits-/Leistungspreis, reduzierte Netzentgelte, Day-Ahead-Zeitreihe) | größter Hebel überhaupt (±40 €/MWh) | ●● |
| **Validierung Dronninglund** (M4 bisher ausgelassen) | belegt Speicher-/Solarlogik gegen Messwerte (Referenzwerte liegen in `data/reference/`) | ●●● |

## B Technische Varianten

| Variante | Idee | Erwartung / Hinweis | Aufwand |
|---|---|---|---|
| **PV für die Wärmepumpe** (Briefing 5c) | PV-Feld auf der Fläche, WP nutzt Eigenstrom | Grobe Rechnung (PVGIS-Normaljahr, 85 % PR): 1 MWp ≈ 1.100 MWh/a, deckt **zeitgleich nur ≈ 17 %** des WP-/PtH-Stroms (≈ 1.850 MWh/a), 2 MWp ≈ 23 %. Winter: **nur 25 %** des PV-Jahresertrags fällt in Okt–Mär, aber **78 %** des Strombedarfs. PV hilft bilanziell, ersetzt aber den Speicher/Kollektor nicht; Flächenkonkurrenz (13.000 m²). Mit Batterie/dynamischem Tarif deutlich besser. | ●● |
| **WP/PtH lädt den Speicher** (Sommer-Wärme für den Winter, Briefing-Variante) | COP Sommer ≈ 3,2 statt Winter ≈ 2,3 | bei festem Preis ≈ 2–3 €/m³·a Ersparnis gegenüber ≈ 10–11 €/m³·a Speicherkosten → rechnet sich nicht; mit Day-Ahead-Preisen prüfen (E29) | ●● |
| **Biomassekessel statt PtH** (Spitze/Reserve) | Preis 10 ct/kWh liegt vor | BEW-förderfähig mit Auflagen; PtH fällt weg | ● |
| **Erdwärme/Abwärme als Quelle** | KWP-NRW-Daten für Bad Lippspringe liegen vor (oberflächennahe/mitteltiefe Geothermie, Solarthermie-Freiflächen) | stabile Quelle im Winter, könnte Luft-WP und Speicher entlasten | ●●● |
| **Teillast/Mindestlast der Luft-WP** | Frostleistung ist jetzt abgebildet (80 % bei -7 °C, E27); Teillastverluste/Taktung fehlen | Modell bei Teillast noch optimistisch; Herstellerdaten nötig | ●● |
| **Ankerkunde** | Industrie-/Gewerbelast ergänzen | im Tornado bereits (+20/40 %) – sinkende Wärmepreise | ● |

## C Methodik

- **Realistischere Speicherkosten** (stetige Kostenfunktion statt drei Stufen, z. B. durch iteratives Lineares
  Programm) und Fläche mit V^(1/3)-Geometrie (`docs/ptes_obergrenze.md`).
- **Monte-Carlo-Sensitivität** statt Einzelvariation: zeigt Wahrscheinlichkeit „System billiger als Gas“.
- **Mehrere Wetterjahre** (kalt/warm, strahlungsarm) nacheinander statt Normaljahr; Klimawandel-Trend.
- **Nichtlineare Speicherphysik** (Temperaturschichten) nur, wenn die Zwei-Teile-Näherung des Speichers (E27) als zu grob kritisiert wird.
- **Stündlicher CO₂-Faktor** des Strommix statt Jahresmittel (relevant für Day-Ahead-Betrieb der WP).
- **Versorgungssicherheit** qualitativ: PtH-Reserve, Ausfall der Luft-WP bei Frost, Anteil Spitzenlast.

## D Stromzeitreihe: woher und wie?

Börsenpreise (Day-Ahead) sind **keine Endkundenpreise**. Üblicher Weg: Preis(t) = Day-Ahead(t) + Vertriebsmarge +
Netzentgelt (Arbeitspreis) + Abgaben/Steuern; dazu ein **Leistungspreis** auf die höchste Bezugsleistung.
Das Modell hat dafür bereits den Tarif `day_ahead` (`prices.py`, Parameter `strom.vertriebsmarge` offen).

| Baustein | Quelle |
|---|---|
| Day-Ahead-Stundenpreise (Deutschland) | [SMARD](https://www.smard.de/en/downloadcenter/download-market-data) (Bundesnetzagentur, Quelle nennen), alternativ Energy-Charts-API (Fraunhofer ISE) – Download als `data/raw/strompreise/day_ahead_<jahr>.csv` mit Spalten `zeit`, `preis` |
| Netzentgelt Arbeits-/Leistungspreis | Preisblatt des örtlichen Netzbetreibers (Lastgangkunden: Jahresleistungspreissystem, getrennt nach Benutzungsdauer ≤/> 2.500 h) |
| Abgaben (Stromsteuer 2,05 ct, KWKG, §19, Offshore, Konzessionsabgabe) | netztransparenz.de und Versorger-Preisblätter 2026; Werte uneinheitlich, Entlastungen für WP (§22 EnFG; §14a EnWG gilt vermutlich nur für Niederspannung, nicht für eine ≈ 1 MW-Anlage) prüfen |
| Vergleichswerte Gesamtpreis | BDEW-Strompreisanalyse (Industrie 2025 ≈ 16–18 ct/kWh, Gewerbe höher): die 30 ct/kWh liegen am oberen Ende |

**Wichtige Folgen:** (1) Der Wetter-/Preisjahr-Bezug muss passen: Day-Ahead 2022 war ein Krisenjahr (hohe
Preise); ein ruhigeres Jahr oder ein Mittel ist realistischer. (2) Mit Leistungspreis wird die **PtH-Reserve
(1,6 MW)** teuer, auch wenn sie kaum läuft – das spricht für Gas-/Biomasse-Reserve oder eine kleinere Reserve.
(3) Der Preis-Hebel im Tornado (20 ct → Wärmepreis 186, 40 ct → 261 €/MWh; bei 20 ct entfällt Solar ganz) zeigt, dass diese Eingabe wichtiger ist
als jede Anlagenannahme.
