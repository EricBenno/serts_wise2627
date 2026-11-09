# Ergebnisse (Stand 09.11.2026)

Vorläufig: Kollektorkennwerte und mehrere Kosten sind Annahmen (`docs/annahmen.md`).
Basis: **Normaljahr** (PVGIS-TMY) für die Strahlung, Lastgang und Temperatur 2022, Speicherpreis in drei
Preisstufen (E24).

## Basislauf (`uv run serts run`)

| Kennzahl | Wert |
|---|---|
| Kollektorfläche / Speicher | ≈ 2.650 m² / 5.000 m³ (Preisstufe 5.000–12.000 m³, 124 €/m³) |
| Wärmepumpe / PtH (Reserve) | ≈ 1,0 MW / 1,6 MW |
| LCOH (Gas-Referenz 165 €/MWh) | **≈ 137 €/MWh** |
| Solaranteil / Erneuerbaren-Anteil | **≈ 25 %** / ≈ 87 % |
| CO₂ System (Gas-Referenz ≈ 1.160 t/a) | ≈ 580 t/a |
| Flächenbedarf (verfügbar 13.000 m²) | ≈ 8.000 m² |

### Die drei Speichergrößen liegen fast gleichauf (flaches Optimum)

| Preisstufe | Ergebnis | LCOH |
|---|---|---|
| < 5.000 m³ (165 €/m³) | ≈ 1.400 m³ Speicher, kleines Kollektorfeld | 137,5 €/MWh |
| 5.000–12.000 m³ (124 €/m³) | 5.000 m³, ≈ 2.650 m², Solar ≈ 25 % | **137,2 €/MWh** |
| 12.000–35.000 m³ (95 €/m³) | 12.000 m³, Fläche voll ausgenutzt | 138,4 €/MWh |

→ Speichergröße und Solaranteil sind über einen weiten Bereich **fast kostenneutral** (±1 €/MWh). Ein großer
saisonaler Speicher kostet kaum mehr als ein kleiner, bringt aber deutlich mehr Solarwärme und weniger CO₂.
Die Wahl kann also nach anderen Kriterien fallen (CO₂, Unabhängigkeit vom Strompreis, Förderung).

## Sensitivitäten (`uv run serts tornado --jobs 4`, Größen jeweils neu optimiert)

1. **LCOH 103–164 €/MWh.** Größter Hebel ist der **Strompreis** (20/40 ct → 103/164 €/MWh), dann der Gütegrad
   der Luft-WP (121/146), WP-Kosten (131/145) und Zins (129/143). Speicher- und Kollektorparameter bewegen
   die LCOH nur um ≈ 1–7 €/MWh.
2. **Solaranteil springt zwischen ≈ 12 % und ≈ 33–41 %.** Wegen des flachen Optimums kippt das Modell je nach
   Annahme zwischen „kleiner Speicher“ und „großer saisonaler Speicher“. Für den Bericht deshalb den
   Solaranteil als Bandbreite angeben, nicht als Punktwert.
3. **Fläche:** bindet nur, wenn der große Speicher gewählt wird (12.000 m³ + ≈ 3.700 m² Kollektor).
4. Alle Varianten bleiben unter der Gas-Referenz von 165 €/MWh (Strom 40 ct knapp: 164). Der **Gaspreis
   selbst** ist nicht variiert: bei 8 ct/kWh läge die Gas-Referenz bei ≈ 118 €/MWh (System teurer), bei
   16 ct/kWh bei ≈ 211 €/MWh.

**Kernaussage (vorläufig):** Wärmepumpe (Luft + Speicher) mit PtH-Reserve ist unter den Annahmen günstiger als
Gas. Wie viel Solarthermie + Speicher dazukommt, ist kostenseitig nahezu egal – eine Abwägung zwischen gleich
teuren Varianten mit 12 % bzw. ≈ 35 % Solaranteil.

## Offene Punkte mit Ergebnisrelevanz

- Strompreis-Ansatz (fest vs. dynamisch/PV) – größter Hebel.
- Kollektorkennwerte (Keymark), Kollektor- und WP-Kosten (DEA).
- Gaspreis-Pfad für die Referenz (Punkt 4).
- Optional: Variante „Speichergröße vorgeben“ (`serts run --V 12000`) als Szenario für den Bericht.
