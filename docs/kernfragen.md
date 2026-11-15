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
| 5c PV für die WP | ✘ (zurückgestellt, TEAM) | nur Abschätzung (`docs/ausblick.md`) |
| 6 Tornado: Speicherkosten, Solar, Strompreis, Last (+ Fläche) | ✔ (Netz klein, Stand 15.11. nach E39) | `docs/ergebnisse.md`; Netz groß nicht gerechnet |
| 6 Heatmap LCOH über Fläche × Volumen | ✔ (klein 15.11. nach E39; groß noch altes Speichermodell) | `serts heatmap` (≈ 12/40 min), `docs/ergebnisse*.md` |
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
| (14.11.) Speicher fast nur WP-Quelle: festes Beladeverhältnis erzwang WP-Betrieb im Sommer, Kennlinie mit zwei Läufen sperrte zu viel | Speichernutzen unterschätzt (≈ 10 €/MWh), Direktanteil 21 % statt 52–63 % (Dronninglund) | Speicher in drei Teilen, ein Lauf, gegen Dronninglund geprüft (E39) |

## 3 Auslegung: was die Antwort noch verzerren kann (offen)

| Punkt | Richtung | Vorschlag |
|---|---|---|
| **Strompreis 30 ct/kWh fest** (Leistungspreis seit E39 enthalten, 15,50 €/kW·a) | größter Hebel überhaupt (Tornado: 20 ct → 210, 40 ct → 277 €/MWh) | Day-Ahead-Szenarien liegen vor; Höhe des Gesamtpreises klären |
| **PtH-Reserve = Spitzenlast als Stundensumme** (1,59 / 15,5 MW) | Kosten leicht überschätzt (Gleichzeitigkeit 0,45 laut Netzberechnung) | `pth.redundanz` oder P_max mit GLF |
| **WP-Kosten** jetzt 1.340 €/kW (unteres Ende KWW, E38); kleines Netz laut KWW eher 1.730 €/kW | Tornado 1,0 / 1,73 Mio. €/MW: 235 / 253 €/MWh (Vorteil ggü. Gas +22 / +7) | erledigt (15.11.) |
| **Speicher-WP COP 4,5 konstant** | Herbst (warmer Speicher) unterschätzt, Frühjahr überschätzt | ok für Jahresmittel (Briefing §8) |
| **Übergangszone** fester Anteil (15 % bei 60.000 m³, Messdaten Dronninglund), mit V^(−1/3) auf kleine Speicher umgerechnet; heißes Wasser kühlt im Modell nicht ab | Direktentladung eher optimistisch (71 % der Speicherentladung) | Tornado 0/0,1/0,25: < 1 €/MWh – unkritisch (15.11.) |
| **Perfekte Voraussicht**, ein Wetterjahr | Betrieb/Solaranteil eher überschätzt | als Modellgrenze benennen |
| **Fläche bindet in beiden Netzen** (13.000 / 80.000 m²) | Netz klein ohne Grenze: Saisonspeicher 33.400 m³, Solar 92 %, −18 €/MWh bei ≈ 39.000 m² (Tornado 15.11.); Fläche kostet im Modell nichts | Pacht/Kauf der Fläche als Kosten; Flächen-Variante Netz groß |
| **BEW 40 % = Obergrenze**, Wirtschaftlichkeitslücke nicht geprüft; EE-Anteil ≥ 75 % (Modell 84–85 %) nur grob | Förderung eher überschätzt | BAFA-Berechnung im nächsten Schritt; Modul 4 ergänzen |
| **Hausanschlüsse pauschal 10.000 €** | im großen Netz (54 % Nichtwohngebäude) eher zu niedrig | Kosten nach Anschlussleistung (KWW Tab. 40) |

## 4 Antwort auf die Leitfrage (Stand 10.11. nachts, WP 1.340 €/kW, beide Netze)

**Nachtrag 14.11. (E39, neues Speichermodell):** Basis und Varianten beider Netze neu gerechnet (`docs/ergebnisse.md`, `docs/ergebnisse_netz_gross.md`). Wärmepreis inkl. Netz: klein 243 (Gas 261), groß 222 (Gas 236) €/MWh; Solar + Speicher spart gegenüber reiner WP + PtH ≈ 33–34 €/MWh. Die Aussagen unten gelten in der Richtung weiter, die Zahlen sind vom 10.11.

**Nachtrag 15.11. (Tornado, Heatmap, Strom neu, Netz klein):** Das System bleibt im Krisenjahr 2022 jetzt günstiger
als Gas (248 statt 261 €/MWh), weil WP/PtH den Speicher in billigen Stunden laden. **Neu und wichtig:** Ohne
Flächengrenze wird ein Saisonspeicher (33.400 m³, 11.400 m² Kollektor, 92 % solar) die günstigste Lösung (226 €/MWh,
−18 €/MWh). Die Aussage „saisonal nur teurer“ gilt also nur für die verfügbaren 13.000 m².

* **Kollektor und Speicher senken Kosten und CO₂** gegenüber reiner WP + PtH (klein −18 €/MWh, groß −21 €/MWh;
  CO₂ −25 bis −32 %), ein Speicher lohnt sich gegenüber Solar ohne Speicher (−12 bzw. −15 €/MWh). Nur mit Solar und
  Speicher ist das System überhaupt günstiger als Gas-Fernwärme.
* Kostenoptimal: **Solaranteil 30–41 %**, Speicher ≈ 1,4–1,7 m³ je m² Kollektor (klein 7.400 m³ / 4.440 m², groß
  38.900 m³ / 28.400 m²); die **Fläche bindet** in beiden Netzen. **Mischspeicher** (≈ 2,3–2,5 Zyklen, 41–46 % der
  Entladung im Winter); saisonal wird er nur bei viel Speicher und wenig Kollektor – und dann teurer (Heatmaps).
* **Gegen Gas-Fernwärme** liegt das System nur 2–3 % günstiger, mit BEW Modul 2 (Obergrenze) ≈ 15 %. Die Antwort hängt
  am stärksten vom **Strom- und Gaspreis** ab (Day-Ahead 2024: −24 €/MWh ggü. Gas, Krise 2022: +13), danach von
  Effizienz der Luft-WP, Förderung, CO₂-Preis und Zins. Die Speicherkosten selbst wirken schwach (flaches Optimum).
