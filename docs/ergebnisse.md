# Ergebnisse (Stand 09.11.2026, Commit siehe `results/*/meta.json`)

Vorläufig: Kollektorkennwerte und mehrere Kosten sind Annahmen (`docs/annahmen.md`). Wetterjahr 2022.

## Basislauf (`uv run serts run`)

| Kennzahl | Wert |
|---|---|
| Kollektorfläche / Speicher | ≈ 3.500 m² / ≈ 5.550 m³ (≈ 1,6 m³/m²) |
| Wärmepumpe / PtH (Reserve) | ≈ 1,0 MW / 1,6 MW |
| LCOH (Gas-Referenz) | ≈ 132 €/MWh (≈ 165 €/MWh) |
| Solaranteil / Erneuerbaren-Anteil | ≈ 37 % / ≈ 88 % |
| CO₂ System (Gas-Referenz) | ≈ 520 t/a (≈ 1.160 t/a) |
| Flächenbedarf | ≈ 10.200 von 13.000 m² (nicht bindend) |

## Sensitivitäten (`uv run serts tornado`, 23 Varianten, Größen jeweils neu optimiert)

Ergebnisordner: `results/<zeit>_base_tornado/` mit `tornado.csv`, `tornado_lcoh.png`, `tornado_solaranteil.png`.

1. **LCOH 102–156 €/MWh** über alle Varianten. Größter Hebel ist der **Strompreis** (20/40 ct → 102/156),
   danach WP-Gütegrad, Zins, Kollektor- und WP-Kosten. Speicherkosten und Verlustrate bewegen die LCOH nur
   um ±2–3 €/MWh, weil sich die optimale Größe anpasst.
2. **Solaranteil sehr empfindlich (12–46 %).** Solarwärme konkurriert eng mit der Luft-WP; kleine Änderungen
   kippen die optimale Feldgröße. Mit **normaler Einstrahlung** (Faktor 0,78 statt sonnigem 2022) schrumpft
   das Optimum auf ≈ 1.700 m² Kollektor / 1.900 m³ Speicher und **12 % Solaranteil**.
   → Für belastbare Aussagen ein Normaljahr (z. B. PVGIS-TMY) als Basis verwenden.
3. Alle Varianten bleiben unter der Gas-Referenz von 165 €/MWh. **Nicht** variiert ist dabei der Gaspreis
   selbst: Bei 8 ct/kWh läge die Gas-Referenz bei ≈ 118 €/MWh (dann wäre das System teurer), bei 16 ct/kWh
   bei ≈ 211 €/MWh.
4. Höherer Rücklauf (50 °C) verschlechtert LCOH (+4) und Solaranteil (−5 Prozentpunkte) – Rücklaufsenkung
   lohnt sich.

## Offene Punkte mit Ergebnisrelevanz

- Wetterjahr/Normaljahr (Punkt 2), Kollektorkennwerte (Keymark), Strompreis-Ansatz (fest vs. dynamisch/PV).
- Gaspreis-Pfad für die Referenz (Punkt 3).
