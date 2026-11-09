# Ergebnisse (Stand 09.11.2026, nach E27/E28)

Vorläufig: Kollektorkennwerte und mehrere Kosten sind Annahmen (`docs/annahmen.md`, `docs/unsicherheiten.md`).
Basis: Normaljahr (PVGIS-TMY), Lastgang/Temperatur 2022, Vorlauf 80 °C, **Zins real 5 %**, 10 % Nebenkosten,
Speicher in zwei Teilen (heiß/kalt, E27), Speicherpreis in drei Stufen (E24), Kosten nach VDI 2067-1 real,
Preisbasis 2025, Netzkosten im Wärmepreis beim Kunden (E25).

## Basislauf (`uv run serts run`)

| Kennzahl | Wert |
|---|---|
| Kollektor / Speicher | ≈ 2.400 m² / ≈ 1.140 m³ (≈ 100 MWh, kurzzeitig/„Tagesbis Wochenspeicher“, ≈ 6–7 Zyklen/a) |
| Wärmepumpe / PtH (Reserve) | 1,13 MW / 1,59 MW (PtH liefert nur ≈ 16 MWh/a) |
| LCOH Erzeugung (Gas-Referenz 165) | **≈ 141 €/MWh** |
| Wärmepreis beim Kunden inkl. Netz (Gas-Fernwärme 257) | **≈ 228 €/MWh** |
| davon Wärmenetz | Trasse ≈ 22 €/MWh, Hausanschlüsse ≈ 36 €/MWh |
| Strom (≈ 1.680 MWh/a) | Energie ≈ 252, Netzentgelt ≈ 156, Abgaben ≈ 96 T€/a |
| Solaranteil / Erneuerbaren-Anteil | ≈ 23 % / ≈ 86 % |
| CO₂ (Gas-Referenz ≈ 1.160 t/a) | ≈ 610 t/a |
| Flächenbedarf (verfügbar 13.000 m²) | ≈ 6.000 m² |

Preisstufen (je Stufe ein Lauf): < 5.000 m³ **140,8** (2.400 m², Solar 23 %), 5.000–12.000 m³ 142,2 (3.400 m²,
Solar 32 %), > 12.000 m³ 145,8 €/MWh (3.700 m², Solar 33 %). Der saisonale Großspeicher ist jetzt
**≈ 5 €/MWh teurer** als der kleine Speicher (vorher ≈ 2).

## Was hat sich gegenüber dem vorigen Stand verändert – und warum

| | vorher | jetzt |
|---|---|---|
| Kollektor / Speicher | 1.230 m² / 1.213 m³ | 2.410 m² / 1.140 m³ |
| Solaranteil | 12 % | 23 % |
| LCOH Erzeugung / inkl. Netz | 137,9 / 219,4 | 140,8 / 228,1 |

Haupttreiber: **Die Speichermodellierung (E27).** Die frühere Jahresregel mit Monatsbeschränkung verlangte, dass
jede direkte Sommerentladung durch Quellwärme im Winter „ausgeglichen“ wird – das blockierte die kurzfristige
Speichernutzung. Mit dem heiß/kalt-Modell wird der kleine Speicher als Puffer über Tage bis Wochen nutzbar, damit
lohnt sich mehr Kollektorfläche. Gegenläufig wirken die **10 % Nebenkosten** (+≈ 4–5 €/MWh, Tornado: 0 % → 136,2) und das **Förder-Flag**
(Basis ohne Förderung, keine Wirkung). Die temperaturabhängige Luft-WP-Leistung (80 % bei −7 °C) ändert kaum etwas
(Tornado: 140,8 ↔ 140,7), weil die PtH-Reserve die Spitze ohnehin abdeckt.

Grafiken je Lauf in `results/<lauf>/`: `1_jahresverlauf.png`, `2_typwochen.png`, `3_dauerlinie.png`,
`4_betrieb_tag_stunde.png`, `5_jahresbilanz_kosten.png` (Strom und Wärmenetz in Komponenten getrennt).

## Sensitivitäten (`uv run serts tornado`, 45 Varianten, Größen jeweils neu optimiert)

Wärmepreis inkl. Netz (Basis 228 €/MWh) und Vorteil gegenüber Gas-Fernwärme (Basis +24 €/MWh):

| Parameter (Variante) | Wärmepreis inkl. Netz | Vorteil ggü. Gas |
|---|---|---|
| Gaspreis 8 / 16 ct/kWh | – | **−23 / +71** |
| Strompreis 20 / 40 ct/kWh | 186 / 262 | +59 / **−4** (dann Solar 37 %) |
| CO₂-Preis 55 / 200 €/t | – | +15 / +45 |
| Förderung BEW 40 % (nur förderfähige Teile) | 197 | **+44** (Optimum: 4.500 m², 7.000 m³, Solar 42 %) |
| Gütegrad Luft-WP 0,45 / 0,6 | 239 / 209 | +15 / +40 |
| Zins 3 / 7 % (real) | 208 / 247 | +32 / +18 |
| Nebenkosten 0 / 20 % | 217 / 239 | +28 / +20 |
| WP-Kosten 0,7 / 1,4 Mio. €/MW | 219 / 240 | +32 / +15 |
| Strompreis +2 %/a real | 247 | +9 |
| Kollektor 300 / 550 €/m² | 218 / 232 | +33 / +21 |
| Hausanschluss 5.000 / 15.000 € | 210 / 246 | unverändert (gleiches Netz) |
| Trasse Straße 400 / 800 €/m; Anteil Straße 50/100 % | 223–237 | unverändert |
| Luft-WP-Leistung bei −7 °C: 60 / 100 % | 228 / 228 | 24 / 24 |

**Lesart:** Ob das System günstiger ist als Gas-Fernwärme, entscheiden **Gas- und Strompreis** (CO₂-Preis,
Förderung, Zins). Die Größe von Kollektorfeld und Speicher springt mit den Kosten (Solaranteil 10–42 %), ohne
dass die Kosten stark reagieren. Der Wärmepreis beim Kunden wird zu ≈ 25 % vom Wärmenetz bestimmt (≈ 58 €/MWh,
vor allem Hausanschlüsse).

**Kernaussage (vorläufig):** Wärmepumpe (Luft + Speicher) mit PtH-Reserve ist unter den Basisannahmen günstiger als
Gas-Fernwärme (≈ −11 %). Ein kleiner Speicher mit ≈ 2.400 m² Kollektor ist kostenoptimal; ein saisonaler
Großspeicher lohnt sich nur mit BEW-Förderung.
