# Ergebnisse (Stand 09.11.2026)

Vorläufig: Kollektorkennwerte und mehrere Kosten sind Annahmen (`docs/annahmen.md`).
Basis: **Normaljahr** (PVGIS-TMY) für die Strahlung, Lastgang und Temperatur 2022.

## Basislauf (`uv run serts run`) und Jahr 2022 (`--szenario wetter_2022`)

| Kennzahl | Normaljahr (Basis) | Jahr 2022 |
|---|---|---|
| Strahlung Kollektorebene 35° | 1.287 kWh/m² | 1.394 kWh/m² |
| Kollektorfläche / Speicher | ≈ 2.070 m² / ≈ 3.320 m³ | ≈ 3.520 m² / ≈ 5.550 m³ |
| Wärmepumpe / PtH (Reserve) | ≈ 1,1 MW / 1,6 MW | ≈ 1,0 MW / 1,6 MW |
| LCOH (Gas-Referenz 165 €/MWh) | **≈ 136 €/MWh** | ≈ 132 €/MWh |
| Solaranteil / Erneuerbaren-Anteil | **≈ 19 %** / ≈ 86 % | ≈ 37 % / ≈ 88 % |
| CO₂ System (Gas-Referenz ≈ 1.160 t/a) | ≈ 620 t/a | ≈ 520 t/a |
| Flächenbedarf (verfügbar 13.000 m²) | ≈ 6.000 m² | ≈ 10.200 m² |

## Sensitivitäten (`uv run serts tornado`, Basis Normaljahr, Größen jeweils neu optimiert)

1. **LCOH 102–162 €/MWh.** Größter Hebel ist der **Strompreis** (20/40 ct → 102/162 €/MWh), dann der
   Gütegrad der Luft-WP, WP-Kosten, Zins und Kollektorkosten. Speicherkosten, Verlustrate und COP aus dem
   Speicher bewegen die LCOH nur um 1–2 €/MWh.
2. **Solaranteil 7–40 %, sehr empfindlich.** Das Kollektorfeld konkurriert eng mit der Luft-WP und steht
   wirtschaftlich auf der Kippe: ±10 % Strahlung → 13 % bzw. 31 % Solaranteil; günstigere Kollektoren
   (300 €/m²), Speicher (70 €/m³) oder Kapital (3 %) → 35–40 %. Ein billigerer Strompreis (20 ct) macht
   Solar fast überflüssig (7 %), ein teurerer (40 ct) attraktiv (40 %).
3. **Die Fläche (13.000 m²) bindet im Normaljahr nicht.** Erst bei günstigen Randbedingungen nähert sich das
   Optimum der Flächengrenze.
4. Alle Varianten bleiben unter der Gas-Referenz von 165 €/MWh. Der **Gaspreis selbst** ist nicht variiert:
   bei 8 ct/kWh läge die Gas-Referenz bei ≈ 118 €/MWh (System teurer), bei 16 ct/kWh bei ≈ 211 €/MWh.
5. Höherer Rücklauf (50 °C) kostet ≈ 4 €/MWh und ≈ 1,5 Prozentpunkte Solaranteil.

**Kernaussage (vorläufig):** Eine Luft-/Speicher-WP mit PtH-Reserve ist unter den Annahmen günstiger als Gas;
wie viel Solarthermie + Speicher sich lohnt, hängt stark an Strompreis, Kollektor-/Kapitalkosten und
Strahlung – das gehört als Bandbreite in den Bericht, nicht als Punktwert.

## Achtung: Speicherpreis bei kleinem Optimum

Der lineare Speicherpreis (105 €/m³) ist für ≈ 5.000–12.000 m³ abgeleitet. Das Normaljahr-Optimum liegt mit
≈ 3.300 m³ darunter; nach der Kostenkurve (Dronninglund/Marstal) kostet diese Größe eher ≈ 140 €/m³. Das
entspricht der Tornado-Variante `ptes.kosten_spez = 140`: LCOH ≈ 137 €/MWh, Solaranteil ≈ 14 %, ≈ 1.500 m²
Kollektor / ≈ 1.900 m³ Speicher. Kleine Erdbeckenspeicher sind spezifisch teuer – das Ergebnis spricht eher
für wenig Solarthermie/Speicher, solange Strom 30 ct/kWh kostet und die Luft-WP so gut ist wie angenommen.

## Offene Punkte mit Ergebnisrelevanz

- Kollektorkennwerte (Keymark), Kollektor- und WP-Kosten (DEA), Strompreis-Ansatz (fest vs. dynamisch/PV).
- Gaspreis-Pfad für die Referenz (Punkt 4).
