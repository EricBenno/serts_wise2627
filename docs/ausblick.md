# Was man noch betrachten könnte – Vorschläge

Sortiert nach Nutzen für die Aussage und Aufwand (Aufwand: ● klein, ●● mittel, ●●● groß). Stand 09.11.2026.

## A Kernaussage absichern (empfohlen)

| Vorschlag | Warum | Aufwand |
|---|---|---|
| **Zins real/nominal klären** und alle Preispfade konsistent setzen (r = 2 % für Strom, Gas, CO₂, Betrieb, falls nominal) | beeinflusst Strom-/Gas-Verhältnis und damit den Vorsprung gegenüber Gas | ● |
| **Förderung je Komponente** (Quote, ggf. Wirtschaftlichkeitslücke) + Modul 4 als Gutschrift | BEW verschiebt das Optimum zum großen Speicher (Solar 41 %) | ●● |
| **Strompreisstruktur** (Arbeits-/Leistungspreis, reduzierte Netzentgelte, Day-Ahead-Zeitreihe) | größter Hebel überhaupt (±40 €/MWh) | ●● |
| **Nebenkosten** (Planung 10–20 %, Stromanschluss, Technikgebäude, Grundstück) | Kosten ↑, bisher fehlend (`docs/unsicherheiten.md`) | ● |
| **Validierung Dronninglund** (M4 bisher ausgelassen) | belegt Speicher-/Solarlogik gegen Messwerte (Referenzwerte liegen in `data/reference/`) | ●●● |

## B Technische Varianten

| Variante | Idee | Erwartung / Hinweis | Aufwand |
|---|---|---|---|
| **PV für die Wärmepumpe** (Briefing 5c) | PV-Feld auf der Fläche, WP nutzt Eigenstrom | Grobe Rechnung (PVGIS-Normaljahr, 85 % PR): 1 MWp ≈ 1.100 MWh/a, deckt **zeitgleich nur ≈ 17 %** des WP-/PtH-Stroms (≈ 1.850 MWh/a), 2 MWp ≈ 23 %. Winter: **nur 25 %** des PV-Jahresertrags fällt in Okt–Mär, aber **78 %** des Strombedarfs. PV hilft bilanziell, ersetzt aber den Speicher/Kollektor nicht; Flächenkonkurrenz (13.000 m²). Mit Batterie/dynamischem Tarif deutlich besser. | ●● |
| **Vorlauftemperatur senken** (z. B. 70 °C, gleitend) | höherer COP, mehr Kollektorertrag, kleinere Netzverluste | Netz ist auf 80/50 °C ausgelegt; Tornado deckt T_RL ab, VL noch nicht | ● |
| **PtH lädt den Speicher** bei billigem Strom (Briefing-Variante) | nutzt Preisschwankungen | nur mit Day-Ahead-Preis sinnvoll | ●● |
| **Biomassekessel statt PtH** (Spitze/Reserve) | Preis 10 ct/kWh liegt vor | BEW-förderfähig mit Auflagen; PtH fällt weg | ● |
| **Erdwärme/Abwärme als Quelle** | KWP-NRW-Daten für Bad Lippspringe liegen vor (oberflächennahe/mitteltiefe Geothermie, Solarthermie-Freiflächen) | stabile Quelle im Winter, könnte Luft-WP und Speicher entlasten | ●●● |
| **Teillast/Frostverhalten der Luft-WP** | Leistung sinkt bei Kälte | Modell ist hier optimistisch (WP-Leistung konstant) | ●● |
| **Ankerkunde** | Industrie-/Gewerbelast ergänzen | im Tornado bereits (+20/40 %) – sinkende Wärmepreise | ● |

## C Methodik

- **Realistischere Speicherkosten** (stetige Kostenfunktion statt drei Stufen, z. B. durch iteratives Lineares
  Programm) und Fläche mit V^(1/3)-Geometrie (`docs/ptes_obergrenze.md`).
- **Monte-Carlo-Sensitivität** statt Einzelvariation: zeigt Wahrscheinlichkeit „System billiger als Gas“.
- **Mehrere Wetterjahre** (kalt/warm, strahlungsarm) nacheinander statt Normaljahr; Klimawandel-Trend.
- **Nichtlineare Speicherphysik** (Temperaturschichten) nur, wenn die 53-%-Regel (E26) als zu grob kritisiert wird.
- **Stündlicher CO₂-Faktor** des Strommix statt Jahresmittel (relevant für Day-Ahead-Betrieb der WP).
- **Versorgungssicherheit** qualitativ: PtH-Reserve, Ausfall der Luft-WP bei Frost, Anteil Spitzenlast.
