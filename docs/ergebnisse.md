# Ergebnisse (Stand 09.11.2026, nach E27–E31)

Vorläufig: Kollektorkennwerte und mehrere Kosten sind Annahmen (`docs/annahmen.md`, `docs/unsicherheiten.md`).
Basis: Normaljahr (PVGIS-TMY), Lastgang/Temperatur 2022, Vorlauf 80 °C, **Zins real 5 %**, 10 % Nebenkosten,
Speicher in zwei Teilen (heiß/kalt, E27) mit **stetiger, mit der Größe degressiver Kostenkurve** (E30),
fester Strompreis 30 ct/kWh, Kosten nach VDI 2067-1 real, Preisbasis 2025, Netzkosten im Wärmepreis (E25).

## Basislauf (`uv run serts run`)

| Kennzahl | Wert |
|---|---|
| Kollektor / Speicher | ≈ 2.540 m² / ≈ 1.640 m³ (≈ 140 MWh) |
| Speichercharakter | **Kurzzeitspeicher**: ≈ 5 Zyklen/a, nur 28 % der Entladung im Winter (Nov–Mär) |
| Wärmepumpe / PtH (Reserve) | 1,12 MW / 1,59 MW (PtH liefert nur ≈ 16 MWh/a) |
| LCOH Erzeugung (Gas-Referenz 165) | **≈ 141 €/MWh** |
| Wärmepreis beim Kunden inkl. Netz (Gas-Fernwärme 257) | **≈ 229 €/MWh** |
| davon Wärmenetz | Trasse ≈ 22 €/MWh, Hausanschlüsse ≈ 36 €/MWh |
| Solaranteil / Erneuerbaren-Anteil | ≈ 24 % / ≈ 86 % |
| CO₂ (Gas-Referenz ≈ 1.160 t/a) | ≈ 600 t/a |
| Flächenbedarf (verfügbar 13.000 m²) | ≈ 6.500 m² |

**Flaches Optimum:** je Kostensegment der Speicherkurve (LCOH, V): 0–1.000 m³ 141,5; 1.000–2.500 m³ **141,2**
(1.640 m³); 2.500–6.000 m³ 141,4 (2.580 m³); 6.000–12.000 m³ 142,5 (6.000 m³); 12.000–35.000 m³ 145,7 €/MWh.
Zwischen 1.000 und 6.000 m³ liegen die Kosten innerhalb von ≈ 1 €/MWh; ein Saisonspeicher von 12.000 m³ ist
≈ 4,5 €/MWh teurer. *(Frühere Befunde „Optimum bei 5.000/12.000 m³“ waren ein Artefakt der Preisstufen, E30.)*

Warum der Speicher kein Saisonspeicher ist und was sich ändern müsste: **docs/saisonaler_speicher.md**.

## Strom: fest gegen Day-Ahead (zwei Läufe, Szenarien `strom_day_ahead_*`)

Preis(t) = Day-Ahead(t) + Marge 25 + Netzentgelt 93 + Abgaben 57 €/MWh; Preisjahr unabhängig vom Wetterjahr 2022.

| | fest 30 ct | Day-Ahead 2024 | Day-Ahead 2024 normiert (Ø wie fest) | Day-Ahead 2022 (Krise) |
|---|---|---|---|---|
| Strompreis Ø / gewichtet bezahlt [€/MWh] | 300 / 300 | 254 / 253 | 300 / 293 | 410 / 341 |
| Kollektor / Speicher | 2.540 m² / 1.640 m³ | 1.240 / 420 | 2.950 / 3.730 | 4.460 / 7.290 |
| Speicher-Zyklen | 5,0 | 12,5 | 3,6 | 2,7 |
| Solaranteil | 24 % | 12 % | 28 % | 42 % |
| Strombezug [MWh/a] | 1.645 | 1.927 | 1.594 | 1.367 |
| LCOH Erzeugung / inkl. Netz [€/MWh] | 141 / 229 | **127 / 211** | 142 / 229 | 157 / 247 |

* **Preisniveau** bestimmt das System: bei billigem Strom (2024) schrumpft Solar; bei teurem (2022) wächst es und der
  Speicher wird größer.
* **Zeitliche Struktur** allein (normiert) senkt den bezahlten Preis nur um 2 % (293 statt 300), die LCOH bleibt
  gleich (141,5): Das Modell kann Preisspitzen kaum ausnutzen, weil der Speicher nur Solarwärme speichert (WP lädt den
  Speicher nicht, E29). Im Krisenjahr 2022 mit starken Preisschwankungen zahlt das flexible System 17 % unter dem Mittel.
* Nicht modelliert: Leistungspreis; Korrelation Preis↔Wetter (Preis- und Wetterjahr verschieden).

## Sensitivitäten (`uv run serts tornado`, 45 Varianten, Größen jeweils neu optimiert)

Wärmepreis inkl. Netz (Basis 229 €/MWh) und Vorteil gegenüber Gas-Fernwärme (Basis +24 €/MWh):

| Parameter (Variante) | Wärmepreis inkl. Netz | Vorteil ggü. Gas |
|---|---|---|
| Gaspreis 8 / 16 ct/kWh | – | **−23 / +70** |
| Strompreis 20 / 40 ct/kWh | 186 / 261 | +59 / **−3** (dann Solar 42 %, 7.170 m³) |
| CO₂-Preis 55 / 200 €/t | – | +14 / +45 |
| Förderung BEW 40 % (nur förderfähige Teile) | 196 | **+45** (Optimum: 4.480 m², 7.170 m³, Solar 42 %) |
| Gütegrad Luft-WP 0,45 / 0,6 | 239 / 210 | +15 / +39 |
| Zins 3 / 7 % (real) | 207 / 248 | +32 / +17 |
| Nebenkosten 0 / 20 % | 218 / 239 | +28 / +20 |
| WP-Kosten 0,7 / 1,4 Mio. €/MW | 220 / 240 | +31 / +15 |
| Strompreis +2 %/a real | 247 | +9 |
| Kollektor 300 / 550 €/m² | 217 / 232 | +33 / +21 |
| Speicherkosten × 0,7 / × 1,3 | 226 / 230 | +26 / +23 |
| Hausanschluss 5.000 / 15.000 € | 211 / 247 | unverändert (gleiches Netz) |
| Trasse Straße 400 / 800 €/m; Anteil Straße 50/100 % | 223–238 | unverändert |
| Luft-WP-Leistung bei −7 °C: 60 / 100 % | 229 / 229 | 24 / 24 |

**Lesart:** Ob das System günstiger ist als Gas-Fernwärme, entscheiden **Gas- und Strompreis** (CO₂-Preis,
Förderung, Zins). Die Größe von Kollektorfeld und Speicher springt mit den Kosten (Solaranteil 10–42 %; Speicher
90–7.300 m³), ohne dass die Kosten stark reagieren. Der Wärmepreis beim Kunden wird zu ≈ 25 % vom Wärmenetz
bestimmt (≈ 58 €/MWh, vor allem Hausanschlüsse).

**Kernaussage (vorläufig):** Wärmepumpe (Luft + Speicher) mit PtH-Reserve ist unter den Basisannahmen günstiger als
Gas-Fernwärme (≈ −11 %). Ein kleiner Speicher (≈ 1.600 m³) mit ≈ 2.500 m² Kollektor ist kostenoptimal; ein saisonaler
Großspeicher lohnt sich erst mit deutlich billigeren Speichern (≈ halbe Kosten), mehr Fläche oder BEW-Förderung.
