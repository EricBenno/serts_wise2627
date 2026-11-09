# Ergebnisse (Stand 09.11.2026)

Vorläufig: Kollektorkennwerte und mehrere Kosten sind Annahmen (`docs/annahmen.md`, `docs/unsicherheiten.md`).
Basis: Normaljahr (PVGIS-TMY), Lastgang/Temperatur 2022, Speicherpreis in drei Stufen (E24), Kosten nach
VDI 2067-1 real, Preisbasis 2025, Netzkosten im Wärmepreis beim Kunden (E25).

## Basislauf (`uv run serts run`) und Variante großer Speicher (`uv run serts run --V 12000`)

| Kennzahl                                                    | Basis (Kostenoptimum)   | Großer saisonaler Speicher |
| ----------------------------------------------------------- | ----------------------- | -------------------------- |
| Kollektor / Speicher                                        | ≈ 1.230 m² / ≈ 1.200 m³ | ≈ 3.680 m² / 12.000 m³     |
| Wärmepumpe / PtH (Reserve)                                  | 1,15 MW / 1,6 MW        | 0,83 MW / 1,6 MW           |
| LCOH Erzeugung (Gas-Referenz 165)                           | **≈ 138 €/MWh**         | ≈ 140 €/MWh                |
| Wärmepreis inkl. Netz, je MWh geliefert (Gas-Fernwärme 252) | **≈ 219 €/MWh**         | ≈ 222 €/MWh                |
| Solaranteil / Erneuerbaren-Anteil                           | ≈ 12 % / ≈ 85 %         | ≈ 33 % / ≈ 88 %            |
| CO₂ (Gas-Referenz ≈ 1.160 t/a)                              | ≈ 670 t/a               | ≈ 520 t/a                  |
| Flächenbedarf (verfügbar 13.000 m²)                         | ≈ 3.300 m²              | 13.000 m² (voll)           |

Die drei Speicher-Preisstufen liegen nur ≈ 2 €/MWh auseinander (137,9 / 138,3 / 140,0) – das Optimum ist
**flach**. Der große saisonale Speicher kostet ≈ 1,5 % mehr, spart aber ≈ 150 t CO₂/a
(≈ 15–20 €/t Vermeidungskosten gegenüber der Basis).

Grafiken je Lauf in `results/<lauf>/`: `1_jahresverlauf.png` (wer deckt wann die Last, Speicherinhalt),
`2_typwochen.png` (Stundenbetrieb in kalter Woche, April, Juli), `3_dauerlinie.png`, `4_betrieb_tag_stunde.png`
(Tag × Uhrzeit je Anlage), `5_jahresbilanz_kosten.png` (Mengen + Kostenaufteilung vs. Gas).

## Sensitivitäten (`uv run serts tornado`, 41 Varianten, Größen jeweils neu optimiert)

Wärmepreis inkl. Netz (Basis 219 €/MWh) und Vorteil gegenüber Gas-Fernwärme (Basis 27 €/MWh):

| Parameter (Variante)                                 | Wärmepreis inkl. Netz | Vorteil ggü. Gas                                   |
| ---------------------------------------------------- | --------------------- | -------------------------------------------------- |
| Gaspreis 8 / 16 ct/kWh                               | –                     | **−20 / +73**                                      |
| Strompreis 20 / 40 ct/kWh                            | 177 / 253             | +62 / **−1**                                       |
| CO₂-Preis 55 / 200 €/t                               | –                     | +17 / +48                                          |
| Förderung BEW 40 %                                   | 178                   | +46 (und Optimum mit großem Speicher, Solar 41 %)  |
| Gütegrad Luft-WP 0,45 / 0,6                          | 231 / 199             | +17 / +43                                          |
| Strompreis +2 %/a real                               | 238                   | +11                                                |
| Hausanschluss 5.000 / 15.000 €                       | 203 / 236             | unverändert (gleiches Netz)                        |
| Trasse Straße 400 / 800 €/m; Anteil Straße 50/100 %  | 215–228               | unverändert                                        |
| Kollektor-, Speicher-, Verlust-, COP-Parameter       | ± 1–9                 | ± 1–7                                              |

**Lesart:** Ob das System günstiger ist als Gas-Fernwärme, entscheiden vor allem **Gas- und Strompreis**
(und CO₂-Preis, Förderung). Kollektor- und Speicherparameter verschieben vor allem die *Größe* von
Kollektorfeld und Speicher (Solaranteil 4–41 %), kaum die Kosten. Netzkosten (≈ 50 €/MWh) sind ein großer
Block im Wärmepreis, aber für beide Varianten gleich.

**Kernaussage (vorläufig):** Wärmepumpe (Luft + Speicher) mit PtH-Reserve ist unter den Basisannahmen
günstiger als Gas-Fernwärme (≈ −13 %). Solarthermie + Erdbeckenspeicher sind gegenüber dem Minimalausbau
fast kostenneutral – mit Förderung (BEW) werden sie Teil des Optimums.
