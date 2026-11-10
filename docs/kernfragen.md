# Passt die Systemauslegung zur Leitfrage? (Prüfung 10.11.2026)

**Leitfrage (Briefing §1):** Wie beeinflussen Kollektorfläche und Speichervolumen Solaranteil, Erneuerbaren-Anteil,
LCOH und CO₂ eines solarthermischen Wärmenetzes mit PTES, Großwärmepumpe und PtH-Spitzenlast – und wie robust ist
das Ergebnis gegenüber Speicherkosten, Solarressource, Strompreis und Lastprofil?

## 1 Pflicht-Ergebnisse: wo stehen sie?

| Pflicht (Briefing §1) | Stand | Wo |
|---|---|---|
| 1 Speicherverluste und -wirkungsgrad je Konfiguration | ✔ | `kpi.json`: `speicher_verluste_MWh`, `speicher_wirkungsgrad` (94 %) |
| 2 Solaranteil getrennt: direkt / PTES direkt / WP-Quellwärme | ✔ | `solar_direkt`, `solar_ptes_direkt`, `solar_wp_quelle` (klein 13/4/17 %) |
| 3 Kostenoptimale Größen (Kollektor, Speicher, WP) | ✔ (LP statt Raster) | je Lauf optimiert, Speicher über Kostensegmente (E30); Raster auf Teamwunsch entfallen |
| 4 LCOH und CO₂; Pareto EE-Anteil vs. LCOH | ✔ / teilweise | LCOH, Wärmepreis inkl. Netz, CO₂; Pareto aus den Varianten (`pareto.png`), keine Kurve über alle Größen |
| 5a ohne Speicher, 5b nur WP + PtH, 5d Gas-Referenz | ✔ | `serts varianten` (beide Netze) |
| 5c PV für die WP | ✘ | nur Abschätzung (`docs/ausblick.md`) |
| 6 Tornado: Speicherkosten, Solar, Strompreis, Last | ✔ (Netz klein) | `serts tornado`; Netz groß nicht gerechnet |
| 6 Heatmap LCOH über Fläche × Volumen | ✘ | möglich mit festen Größen (`--A`, `--V`), nicht umgesetzt |
| Förderung (TEAM) | ✔ | BEW Modul 2 in jedem Lauf ausgewiesen + Szenario `bew_modul2` (E37) |

## 2 Auslegung: was am 10.11. falsch oder zu optimistisch war und korrigiert ist

| Befund | Wirkung auf die Kernaussage | Korrektur |
|---|---|---|
| Direktentladung aus einem Speicher, dessen Temperatur weit unter dem Vorlauf lag | Speichernutzen überschätzt | Kennlinie: direkt nur bei dicker heißer Schicht (E34) |
| Speicher-WP lief im Winter nicht, Speicher wurde nie unter ≈ 40 % entladen | Speicher wirkte als „Sockel“, Winternutzen unterschätzt | Fehler der ersten Kennlinie (Mindestinhalt erzwungen) behoben; kalter Teil kann nicht mehr als Ballast dienen (E34, E36) |
| WP kühlte den kalten Teil, während der heiße voll war (unphysikalisch) | Kennlinie zeigte 50 °C bei Direktentladung | Schichtung konsistent (E36) |
| Luft-WP zu effizient (Lorenz, Gütegrad 0,5: Arbeitszahl 2,65) | Luft-WP-Referenz zu billig, Solar/Speicher zu unattraktiv | KWW-Ansatz (Arbeitszahl 2,22, E35); Wetterjahr 2022 nur ≈ 1 % günstiger als das Mittel |
| Kostenquellen uneinheitlich (Dänemark, Einzelprojekte) | Rangfolge der Varianten unsicher | KWW-Technikkatalog für Kollektor, PTES, Trasse (E32); WP/PtH als Szenario |
| Speicher max. „über 90 °C“ | – | Modell rechnet höchstens 85 °C (Liner-Grenze); Darstellung war missverständlich, jetzt eigenes Temperaturfeld |

## 3 Auslegung: was die Antwort noch verzerren kann (offen)

| Punkt | Richtung | Vorschlag |
|---|---|---|
| **Strompreis 30 ct/kWh fest**, kein Leistungspreis | größter Hebel überhaupt (Tornado vor E34: ±40 €/MWh); Leistungspreis würde die PtH-Reserve verteuern | Preisblatt des Netzbetreibers; Day-Ahead-Szenarien liegen vor |
| **PtH-Reserve = Spitzenlast als Stundensumme** (1,59 / 15,5 MW) | Kosten leicht überschätzt (Gleichzeitigkeit 0,45 laut Netzberechnung) | `pth.redundanz` oder P_max mit GLF |
| **WP-Kosten 1.000 €/kW** (DK) statt KWW 1.400–1.730 €/kW | System zu günstig (+9 bis +20 €/MWh mit KWW) | Teamentscheidung: `kww_komplett(_gross)` als Basis? |
| **Speicher-WP COP 4,5 konstant** | Herbst (warmer Speicher) unterschätzt, Frühjahr überschätzt | ok für Jahresmittel (Briefing §8) |
| **Kennlinie** (Übergangszone 30 %) ist abgeschätzt, nicht gemessen | Speichernutzen ±; Tornado 0/0,15/0,5 | Messdaten Dronninglund (DTU-Datensatz) |
| **Perfekte Voraussicht**, ein Wetterjahr | Betrieb/Solaranteil eher überschätzt | als Modellgrenze benennen |
| **Fläche Netz groß bindet** (80.000 m²) | Solaranteil durch Fläche begrenzt, nicht durch Kosten | Flächen-Variante rechnen |
| **BEW 40 % = Obergrenze**, Wirtschaftlichkeitslücke nicht geprüft; EE-Anteil ≥ 75 % (Modell 84–85 %) nur grob | Förderung eher überschätzt | BAFA-Berechnung im nächsten Schritt; Modul 4 ergänzen |
| **Hausanschlüsse pauschal 10.000 €** | im großen Netz (54 % Nichtwohngebäude) eher zu niedrig | Kosten nach Anschlussleistung (KWW Tab. 40) |

## 4 Antwort auf die Leitfrage (Stand jetzt, beide Netze)

* **Kollektor und Speicher senken Kosten und CO₂** gegenüber reiner WP + PtH (klein −16 €/MWh, groß −20 €/MWh;
  CO₂ −25 bis −28 %), ein Speicher lohnt sich gegenüber Solar ohne Speicher (−10 bzw. −15 €/MWh).
* Kostenoptimal: **Solaranteil 31–35 %**, Speicher ≈ 1,2 m³ je m² Kollektor (klein 4.560 m³ / 3.680 m², groß
  36.700 m³ / 28.800 m²), **Mischspeicher** (≈ 3 Zyklen, ein Drittel der Entladung im Winter), kein Saisonspeicher.
* **Gegen Gas-Fernwärme** liegt das System 6–7 % günstiger, mit BEW Modul 2 (Obergrenze) 17–18 %. Die Antwort hängt
  am stärksten vom **Strom- und Gaspreis** ab, danach von WP-Kosten und Förderung; die Speicherkosten selbst wirken
  schwach (flaches Optimum).
