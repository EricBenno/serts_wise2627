# Modellgrenzen (mit Verzerrungsrichtung) – Baustein für den Bericht (M9)

Aus BRF §8, ergänzt um Bad-Lippspringe-spezifische Punkte (★).

| Grenze | Wirkung |
|---|---|
| Ideale Schichtung, feste Pool-Niveaus 85/45/10 °C | Speichernutzung eher überschätzt |
| Perfekte Voraussicht (LP über 8760 h) | Betrieb und Solaranteil eher überschätzt, Kosten unterschätzt |
| Verluste ∝ Inhalt, kein Erdreich | Anfahrjahre unterschätzt, Spätjahre leicht überschätzt |
| Feste Kollektor-Betriebstemperaturen | Ertrag ± je nach Speichertemperatur |
| Kollektorkennlinie ohne Einfallswinkelkorrektur (IAM) | Ertrag leicht überschätzt (morgens/abends, Winter) |
| Konstanter COP aus PTES | Herbst unterschätzt, Frühjahr überschätzt; Jahresmittel ok |
| Standardlastprofile / BDEW-Typen | Spitzen geglättet → PtH-Leistung eher unterschätzt |
| Linearisierte Investkosten, Raster | Optimum nur auf Rastergenauigkeit |
| ★ Netzverluste aus NB bei 80/50 °C, Modell 75/45 °C | Netzverluste leicht überschätzt (≈ −9 % bei 75/45, grob) |
| ★ Lastgang nicht aus DWD-Wetter 2022 abgeleitet | Gleichzeitigkeit Kälte ↔ Spitzenlast ↔ niedriger COP_air nur statistisch abgebildet |
| ★ Kleines PTES (≈ 8.700 m³ statt 60.000 m³) | Verlustrate aus DRL eher zu niedrig → Sensitivität bis 8·10⁻⁵ 1/h |
| ★ Strahlung aus Satellit (PVGIS) statt Bodenmessung | Abweichung typ. wenige % im Jahr; stündlich größer |
| ★ Wetterjahr 2022 strahlungsreich (PVGIS 1.394 kWh/m² auf 35°) | Solarertrag und Solaranteil überschätzt ggü. Normaljahr (grob +20–30 %) |
| ★ Kollektorkennwerte angenommen (Keymark nicht abrufbar) | Ertrag ± ca. 5–10 % |
| ★ Niedertemperatur-Laden (10 → 50 °C, T_m 30 °C) ohne Zirkelbezug zur Speichertemperatur | spez. Ertrag eher überschätzt (Modell ≈ 700 kWh/(m²a) inkl. Niveau „tief“) |
| ★ WÜT-Leistungen nicht begrenzt (E12) | Lade-/Entladespitzen eher überschätzt (gering) |
| ★ Flächenbedarf nur geprüft, nicht begrenzt (E17) | Rasterpunkte mit `flaeche_ok = False` sind am Standort nicht baubar |
