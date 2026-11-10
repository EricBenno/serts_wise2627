# Zentrale Eingangsparameter

> Automatisch erzeugt aus `config/base.yaml` und `config/netze/*.yaml` mit `uv run serts uebersicht`.
> Nicht von Hand ändern: Zahlen in der YAML anpassen, Übersicht neu erzeugen. Alle Parameter mit Quellen: [annahmen.md](annahmen.md).

Szenario: **base**. "=" heißt: im großen Netz gleicher Wert wie im kleinen. Status: **B** belegt (Quelle/Messwert), **V** Vorgabe (Teamentscheidung), **A** Annahme (begründet, ohne Primärquelle). Kosten netto in EUR, real, Preisbasis 2025/26.

## 1 Netz und Standort

| Parameter | klein | groß | Einheit | St. | Quelle |
|---|---|---|---|---|---|
| Freifläche (Kollektor + Speicher) | 13.000 | 80.000 | m2 | V | klein: TEAM: ca. 13.000 m2 Grundstück am Erzeugerst …; groß: TEAM 10.11.2026: Freifläche für das große Ne … |
| Wärmebedarf Gebäude | 4.525 | 42.782 | MWh/a | B | klein: NB Lastprofil, Summe Spalte 'Summe aller Geb …; groß: GR Lastprofil, Summe 'Summe aller Gebäudetyp … |
| Netzverluste (Standarddämmung) | 937 | 5.440 | MWh/a | B | klein: NB Lastprofil, Spalte 'Verlust' …; groß: GR Lastprofil, Spalte 'Verlust' … |
| Spitzenlast inkl. Verluste (Stundenwert) | 1,592 | 15,5 | MW | B | klein: NB Lastprofil, Max. 'Gesamtsumme' am 21.01.2 …; groß: GR Lastprofil, Max. 'Gesamtsumme' am 21.01.2 … |
| Trassenlänge | 2.432 | 14.291 | m | B | klein: NB Zusammenfassung, Summe Trassenlänge …; groß: GR Zusammenfassung, Summe Trassenlänge … |
| Hausanschlüsse | 159 | 877 | Stück | B | klein: NB Zusammenfassung, Anzahl Hausanschlüsse …; groß: GR Zusammenfassung, Anzahl Hausanschlüsse … |
| Vorlauftemperatur | 80 | = | degC | V | TEAM: Netz bleibt bei 80 degC Vorlauf wie in der NB (ersetzt BRF-Wert 75 degC) |
| Rücklauftemperatur (Modell) | 45 | = | degC | V | BRF §2 (TEAM: Rücklauf frei '80/x'); NB rechnet 50 degC |
| Wetter-/Lastjahr (Temperatur DWD 03028) | 2022 | = | a | B | NB Blatt Lastprofil: Zeitstempel 2022-01-01 00:00 bis 2022-12-31 23:00 (8760 h) |

## 2 Energiepreise und Emissionen (netto, real)

| Parameter | klein | groß | Einheit | St. | Quelle |
|---|---|---|---|---|---|
| Strom: Tarif (fest oder day_ahead) | fest | = | - | V | BRF §3.5 / TEAM: Basis fester Tarif … |
| Strom gesamt (fester Tarif) | 30 | = | ct/kWh | V | TEAM: 30 ct/kWh (inkl. Netzentgelte/Abgaben, netto) |
|   davon Netzentgelt (Arbeitspreis) | 9,3 | = | ct/kWh | A | Aufteilung der 30 ct nach BDEW-Komponenten (Jan 2026, Netzentgelt ≈ 9,3 ct/kWh … |
|   davon Steuern/Abgaben/Umlagen | 5,7 | = | ct/kWh | A | Stromsteuer 2,05 + Konzessionsabgabe 1,67 + KWKG-Umlage 0,45 + §19-Aufschlag 1,56 ct/kWh … |
| Day-Ahead-Tarif: Vertriebsmarge | 2,5 | = | ct/kWh | A | Spot-Tarife leistungsgemessener Gewerbekunden: Aufschlag auf den Spotpreis inkl. Vertrieb und … |
| Day-Ahead-Tarif: Preisjahr | 2024 | = | a | A | Day-Ahead-Stundenpreise DE-LU, Bundesnetzagentur / SMARD.de … |
| Strom: CO2-Faktor | 363 | = | g/kWh | B | UBA: CO2-Emissionen pro kWh Strom 2024 = 363 g/kWh (Themenseite; UBA-FAQ nennt 353 g) |
| Erdgas (Brennwert Hs, ohne CO2-Preis) | 12 | = | ct/kWh | V | TEAM: ca. 12 ct/kWh … |
| CO2-Preis (ETS) | 100 | = | EUR/t | V | TEAM: ETS ca. 100 EUR/t |
| Erdgas: CO2-Faktor (Hi) | 201 | = | g/kWh | V | UBA: Erdgas ≈ 55,8 t/TJ (Hi) = 0,201 t/MWh; TEAM bestätigt |
| Biomasse (Option, nicht im Basisfall) | 10 | = | ct/kWh | V | TEAM: 10 ct/kWh, real konstant |

## 3 Wirtschaftlichkeit (VDI 2067-1)

| Parameter | klein | groß | Einheit | St. | Quelle |
|---|---|---|---|---|---|
| Kalkulationszins (real) | 5 | = | % | V | TEAM 09.11.2026: Zins bleibt REAL (5 %), damit alle Preise real konstant … |
| Betrachtungszeitraum | 20 | = | a | V | TEAM |
| Preisbasis | 2025 | = | a | V | TEAM: 2025/26 |
| Planungs-/Nebenkosten auf alle Investitionen | 10 | = | % | V | TEAM 09.11.2026: ca. 10 % Planungs-/Nebenkosten auf alle Investitionen … |
| Förderquote in der Optimierung (Basis ohne) | 0 | = | % | V | AP 10 Einfach: Basis ohne Förderung; Variante pauschaler Investitionszuschuss |
| BEW Modul 2: Ausweis je Lauf (Obergrenze) | 40 | = | % | B | BEW Richtlinie 7.1.2: Modul 2 bis zu 40 % der förderfähigen Ausgaben (docs/foerderung_bew.md) |
| Preisänderung Strom (real) | 0 | = | %/a | V | TEAM: real gleichbleibende Preise (reale Rechnung); Variante +2 %/a |
| Preisänderung Gas (real) | 0 | = | %/a | V | TEAM: real gleichbleibend; Variante +2 %/a |
| Preisänderung CO2 (real) | 0 | = | %/a | V | TEAM: real gleichbleibend |

## 4 Investitionen und Lebensdauern (netto; Quelle: KWW Technikkatalog 2026, wo vermerkt)

| Parameter | klein | groß | Einheit | St. | Quelle |
|---|---|---|---|---|---|
| Kollektorfeld (Brutto-Fläche) | 304 | 276 | EUR/m2 Brutto | B | klein: KWW Tab. 21 …; groß: KWW Tab. 21 … |
|   Lebensdauer | 25 | = | a | B | KWW Tab. 21: 25 a (Freifläche, professionelle Wartung; Bezug VDI 2067-1) |
| PTES bei 60.000 m3 (Kostenkurve, siehe unten) | 67,77 | = | EUR/m3 | B | KWW Tab. 52 (Erdbeckenspeicher): Kostenkurve Invest = 1093,6 * V^0,7472 … |
|   Größenexponent spez. Kosten | -0,2528 | = | - | B | KWW Tab. 52: Invest ~ V^0,7472 -> spezifisch ~ V^-0,2528 |
|   Lebensdauer | 30 | = | a | B | KWW Tab. 52: 30 a (mittlere Lebensdauer, Unsicherheit ±40 %) … |
| Wärmepumpe (Luft + Speicher) | 1.000 | = | EUR/kW_th | A | Frederikssund 2022: ≈ 6,4 Mio. DKK/MW Luft-WP ≈ 0,86 Mio. EUR/MW (SCH) … |
|   Lebensdauer | 20 | = | a | A | Größenordnung DEA/VDI 2067-1 (18-25 a) |
| Power-to-Heat (Reserve) | 100 | = | EUR/kW_th | A | Frederikssund 2022: ≈ 0,5 Mio. DKK/MW ≈ 0,07 Mio. EUR/MW (SCH) … |
|   Lebensdauer | 20 | = | a | A | Größenordnung DEA (20 a) |
| Gaskessel (nur Gas-Referenz) | 100 | = | EUR/kW_th | A | Gaskessel Fernwärme ≈ 0,05-0,1 Mio. EUR/MW (DEA-Größenordnung); kleine Leistung -> oberer Wert |
|   Lebensdauer | 20 | = | a | A | Größenordnung VDI 2067-1 (18-20 a) |
| Trasse unter Straße | 650 | 1.140 | EUR/m Trasse | B | klein: KWW Tab. 36/37 …; groß: KWW Tab. 36/37 … |
| Trasse Grünfläche | 320 | 640 | EUR/m Trasse | B | klein: KWW Tab. 36/37 …; groß: KWW Tab. 36/37 … |
|   Anteil Straße an der Trasse | 80 | = | % | V | TEAM: Großteil der Trasse unter Straßen, Rest 'grüne Wiese' – Verhältnis nachsteuerbar |
|   Lebensdauer Trasse | 40 | = | a | A | KMR/PEX-Fernwärmeleitungen: Größenordnung 40 a (DEA District heating distribution; VDI 2067-1) |
| Hausanschluss inkl. Übergabestation | 10.000 | = | EUR/Stück | A | Hausanschlussleitung + Übergabestation EFH: 5.000-15.000 EUR (co2online via Finanztip … |
|   Lebensdauer | 25 | = | a | A | Übergabestation dominiert die Kosten: Größenordnung 20-30 a |

## 5 Technik (Wirkungsgrade, Temperaturen, Verluste)

| Parameter | klein | groß | Einheit | St. | Quelle |
|---|---|---|---|---|---|
| Kollektor: Konversionsfaktor eta0 | 0,8 | = | - | A | Mitte der BRF-Bandbreite 0,75-0,82 für große Flachkollektoren; Bezug Bruttofläche |
| Kollektor: Neigung (Süd) | 35 | = | deg | A | TEAM: einfache Annahme … |
| Grundfläche je Kollektor-Bruttofläche | 2,3 | = | m2 Grund / m2 Kollektor | B | BSW: 2- bis 2,3-fache Bruttokollektorfläche inkl. Reihenabstände und Heizzentrale … |
| Kollektor: Feld-/Rohrverluste | 10 | = | % | A | BRF §3.3 Startwert |
| PTES: max. Temperatur | 85 | = | degC | V | BRF §3.1; Liner-Grenze (Xiang et al. 2022) |
| PTES: min. Temperatur | 10 | = | degC | V | BRF §3.1; DRL Tmin 9-12 degC |
| PTES: Wärmeverlust (Speicherinhalt) | 4e-05 | = | 1/h | A | BRF §3.2 Startwert, abgeleitet aus DRL (Verluste / mittl. Inhalt ≈ 2.800 MWh) |
| PTES: Übergangszone (Direktentladung erst darüber) | 30 | = | % Vol. | A | Temperaturkennlinie (Abschätzung): Übergangszone … |
| PTES: Volumen je Grundfläche | 2,65 | = | m3/m2 | A | DRL-Geometrie … |
| Luft-WP: COP-Ansatz (KWW: Gütegrad x Carnot auf Vorlauf) | kww | = | - | V | KWW Tab. 24/25: COP = Gütegrad x T_VL / (T_VL - T_a) mit Gütegrad 46 % (70 °C) bzw. 44 % … |
| Luft-WP: Faktor auf KWW-Gütegrad (45 % bei 80 °C) | 1 | = | - | V | Faktor auf den KWW-Gütegrad (Sensitivität; KWW-Unsicherheit der JAZ ±30 %) |
| Speicher-WP: COP | 4,5 | = | - | A | BRF §3.4: Schrittmittel 45->10 degC ≈ 4,9, konservativ 4,5; Marstal NH3 Jahresmittel 5-5,5 |
| Luft-WP: Leistung bei -7 °C (Anteil) | 0,8 | = | - | A | BRF §3.4: linear auf 80 % der Leistung bei T_min_luft (-7 degC) … |
| PtH: Wirkungsgrad | 0,99 | = | - | V | BRF §2 |
| PtH: Reserve (x Spitzenlast) | 1 | = | x P_max | A | SCH A6: x_PtH >= P_max (n-1-Redundanz, Versorgungssicherheit) … |
| Gaskessel: Wirkungsgrad (Hi) | 0,95 | = | - | A | BRF §3.5 (x); Brennwertkessel bezogen auf Hi |

## 6 Abgeleitet: spezifische PTES-Kosten (Kostenkurve des Modells)

Kosten je m3 Wasseräquivalent (Preisindex und `ptes.kosten_faktor` eingerechnet). Die Kurve folgt dem KWW-Fit Invest = 1093,6 x V^0,7472; Stützwerte des KWW: 20.000 m3 = 90 EUR/m3, 50.000 m3 = 70 EUR/m3, 100.000 m3 = 60 EUR/m3, 200.000 m3 = 50 EUR/m3. Unter 20.000 m3 ist die Kurve **extrapoliert** (KWW-Gültigkeit 20.000-200.000 m3).

| Volumen [m3] | 2.000 | 10.000 | 20.000 | 60.000 | 100.000 |
|---|---|---|---|---|---|
| Kosten [EUR/m3] | 160 | 107 | 89 | 68 | 60 |

Nicht übernommen aus dem KWW: Kollektor- und Speichererträge/-verluste (eigene Rechnung mit PVGIS-Normaljahr und Speichermodell). Solar-O&M (1 % des Invests, KWW) und weitere Instandhaltungssätze stehen in `oekonomie.om_fix.*` ([annahmen.md](annahmen.md)).
