# Datenbasis Bad Lippspringe

Stand 08.11.2026. Alle Zahlen reproduzierbar mit `uv run serts prepare` (→ `data/processed/base/kennzahlen.json`)
bzw. `uv run serts check-strahlung`. Quelle NB = `data/raw/bad_lippspringe/results netzberechnung.xlsx`.

## 1 Wärmebedarf und Netz (eigene Netzberechnung)

| Größe | Wert | Herleitung |
|---|---|---|
| Gebäude am Netz | 159 (EFH 83, MFH 41, GMK 28, GKO 7, GHA 0) | NB Zusammenfassung |
| Wärmebedarf Gebäude Q_gebaeude | **4.525 MWh/a** | Σ Lastprofil „Summe aller Gebäudetypen“ |
| davon Wohnen (EFH + MFH) | 70,8 % (32,2 + 38,6) | Σ je Typ / Q_gebaeude |
| davon Gewerbe (GMK + GKO) | 29,2 % (27,6 + 1,6) | dto. |
| Netzverluste | **937 MWh/a** (konstant 0,107 MW) | Σ Spalte „Verlust“ |
| Netzverluste extra Dämmung | 850 MWh/a (0,097 MW) | Σ Spalte „Verlust bei extra Dämmung“ |
| Verlustanteil an Einspeisung | 17,2 % (extra Dämmung 15,8 %) | 937 / 5.460 |
| Einspeisung ins Netz | **5.460 MWh/a** | Σ „Gesamtsumme“ (Modell: 5.462 durch Rundung je Spalte) |
| Spitzenlast stündlich | **1,59 MW** am 21.01.2022 07:00 | max „Gesamtsumme“ |
| Minimallast | 0,155 MW (Sommer) | min „Gesamtsumme“ |
| Volllaststunden | 3.430 h | 5.460 / 1,592 – passt zu SCH A2 (≈ 3.300 h, 2.800–3.800) |
| Gleichzeitigkeitsfaktor | 0,52; P_max inkl. GLF 1,43 MW | NB Zusammenfassung |
| Trassenlänge / Hausanschlüsse | 2.432 m / 3.413 m | NB Zusammenfassung |
| Wärmeliniendichte | 1,86 MWh/(m·a) (Trasse), 0,77 inkl. HA | 4.525 / 2.432 bzw. / 5.845 |
| Netztemperaturen in der NB | **80 / 50 °C** | NB Zusammenfassung (Modell: 75/45, siehe E3) |
| Rohrsystem | PEX 20–100 (Trasse 2,4 km), KMR nicht genutzt | NB Zusammenfassung |

Gebäudestatistik (NB Blatt Statistik, Median je Typ): spez. Raumwärme 85–112 kWh/(m²a), Warmwasser
10–22 kWh/(m²a), häufigste Baualtersklasse EFH 1960, MFH 1970 → Raumwärme + Warmwasser sind im Lastgang enthalten.

**Größenvergleich Dronninglund:** DRL ≈ 36–37 GWh/a ans Netz, 12 MW Spitze → Bad Lippspringe ist ≈ **6,7× kleiner**.
Mit dem Raster (BRF §5, Bezug 5.462 MWh/a) ergeben sich A_Koll ≈ 2.200–8.200 m² und V bis ≈ 20.500 m³
(Startpunkt A = 5.460 m², V ≈ 8.700 m³). Folge: deutlich kleineres PTES → höhere spezifische Verluste
und höhere spezifische Kosten als DRL (siehe `ptes.verlustrate`, `ptes.kosten_spez`).

## 2 Wetter (DWD Station 03028 „Lippspringe, Bad“, 157 m, 51,7854 N / 8,8388 E)

| Datensatz | Zeitraum | Nutzung |
|---|---|---|
| TU Lufttemperatur, stündlich, UTC | 04/1971–12/2025 | **T_a 2022** für COP, Frostschutz, Kollektor |
| ST Global-/Diffusstrahlung | 01/1982–08/**2011** | nur Klimavergleich – **für 2022 keine Messung** |
| EB Erdbodentemperatur 2–100 cm | 1981–2025 | optional (Umgebung PTES/Netz) |
| SD Sonnenscheindauer | 1951–02/2025 | nicht verwendet |

Kennwerte 2022 (TU): Mittel **11,2 °C**, Minimum −10,7 °C, 60 h unter −7 °C (`waermepumpe.T_min_luft`).
Lastgewichteter Jahres-COP der Luft-WP (η_G 0,5, 45→80 °C, Abtau 5 %) = **2,70** (bei 45→75 °C: 2,79).

**PVGIS-SARAH3 2022** (35° Süd, mit Horizont): Einstrahlung Kollektorebene **1.394 kWh/m²** – deutlich über
dem DWD-Klimamittel (≈ 960 kWh/m² horizontal ≈ 1.085 auf 35° bei angenommenem Neigungsgewinn 1,13).
PVGIS-T_a korreliert mit DWD 03028 zu r = 0,98 (PVGIS im Mittel 1 K kälter). Kollektor-Potenzial (Annahme-Kennwerte):
P_hi 587 kWh/(m²a), P_lo 871 kWh/(m²a).
**Standort:** TEAM 09.11.2026 – Erzeugerstandort am Netz in Bad Lippspringe, ≈ 13.000 m², annähernd quadratisch.
Lastgang der NB beruht auf Wetter Münster 2022 (Abschnitt 3 damit erklärt).

**Datenlücke:** 20.05.2022 16 UTC – 23.05.2022 11 UTC (68 h) fehlen. Gefüllt mit Tagesgang ±7 Tage, linear an
die Ränder angeschlossen (`dwd.fuelle_tagesgang`, Test `test_dwd.py`). Lastarme Zeit → Einfluss vernachlässigbar.

**Strahlung:** DWD-Messung Globalstrahlung 03028 (Jahre mit ≤ 48 h Lücke, 1992–2010): Median **≈ 960 kWh/(m²a)**
horizontal (Spanne 850–1.056; 2006 = 718 vermutlich Messproblem). Diffusstrahlung erst ab 2010 vorhanden.
Für 2022 Strahlung aus **PVGIS-SARAH3** (Satellit, 2005–2023) direkt auf Kollektorebene → `serts fetch-pvgis`,
danach Jahressumme gegen diesen Klimawert halten (2022 gilt in DE als strahlungsreiches Jahr → prüfen, ggf.
Sensitivität „Solarressource“ mit strahlungsarmem Jahr).

## 3 Zusammenhang Last ↔ Wetter

Korrelation Tagesmittel T_a mit Tageslast (Gebäude): r = −0,86 (2022). Gegen andere Jahre 2012–2023 liegt r
ähnlich (−0,82 … −0,88; Spearman mit geometrisch gewichteter Temperatur −0,89 … −0,92, 2022 und 2017 am höchsten).
**Folgerung:** Der Lastgang ist nicht deterministisch aus der DWD-Temperatur 2022 dieser Station erzeugt
(sonst |r| ≈ 0,95+); Werte wirken stochastisch je Gebäude. Wetterbasis der Netzberechnung beim Team erfragen.
Für die Jahresbilanz unkritisch; für die stündliche Kopplung Kälte ↔ Spitzenlast ↔ COP_air ist sie nur statistisch.

## 4 Nicht genutzt (bewusst)

GIS-Daten (`*.gpkg`, KWP-NRW-Shapes inkl. Wärmebedarfsmodell, Solarthermie-Freiflächenpotenzial, Geothermie,
QGIS-Projekt). Die KWP-Kurzdokumentation Freiflächen-Solarthermie kann später Kollektorneigung und Flächenpotenzial
für Bad Lippspringe belegen.
