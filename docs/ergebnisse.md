# Ergebnisse Netz klein (Stand 10.11.2026 nachts, nach E32–E38)

Vorläufig: Kollektorkennwerte und mehrere Kosten sind Annahmen (`docs/annahmen.md`, Übersicht:
`docs/eingangsparameter.md`). Basis: Normaljahr (PVGIS-TMY), Lastgang/Temperatur 2022, Vorlauf 80 °C, **Zins real 5 %**,
10 % Nebenkosten, fester Strompreis 30 ct/kWh, VDI 2067-1 real, **Kosten für Kollektor, Speicher, Trasse und WP
(1.340 €/kW, unteres Ende) aus dem KWW Technikkatalog 2026** (E32, E38), **Luft-WP nach KWW-Gütegrad** (E35),
Speicher mit **Temperaturkennlinie** und konsistenter Schichtung (E34, E36). Großes Netz:
**`docs/ergebnisse_netz_gross.md`**. Prüfung gegen die Leitfrage: **`docs/kernfragen.md`**. Speichermodell
erklärt: `docs/speichermodell.md`.

## Basislauf (`uv run serts run`)

| Kennzahl | Wert |
|---|---|
| Kollektor / Speicher | **≈ 4.440 m² / ≈ 7.400 m³** (Fläche 13.000 von 13.000 m² – bindet knapp) |
| Wärmepumpe / PtH (Reserve) | 0,93 MW / 1,59 MW (PtH liefert ≈ 140 MWh/a, v. a. im Februar) |
| Arbeitszahl WP gesamt (Luft + Speicher) | 2,68 |
| Speicher | Wirkungsgrad 93 %, 2,3 Zyklen/a, 46 % der Entladung Nov–Mär, **gemischt** |
| Wärmeherkunft (5.462 MWh/a) | Luft-WP 2.740, Speicher-WP 1.480, Speicher direkt 320, Solar direkt ≈ 780, PtH 140 MWh |
| Solaranteil (direkt / Speicher direkt / WP-Quellwärme) | **41 %** (14 / 6 / 21 %) |
| LCOH Erzeugung (Gas-Referenz 165) | **≈ 160 €/MWh** |
| Wärmepreis beim Kunden inkl. Netz (Gas-Fernwärme 261) | **≈ 255 €/MWh** (−2 %) |
| davon Wärmenetz | Trasse ≈ 26 €/MWh, Hausanschlüsse + Übergabestationen ≈ 36 €/MWh |
| **mit BEW Modul 2** (40 %, gleiche Auslegung; Obergrenze) | LCOH ≈ 139, **inkl. Netz ≈ 221 €/MWh** (−15 % ggü. Gas), Zuschuss ≤ 2,1 Mio. € |
| EE-Anteil / CO₂ (Gas-Referenz 1.160 t/a) | 86 % / ≈ 625 t/a |

**Kostensegmente** (LCOH, V, A): 0–1.000 m³ 162,3; 1.000–2.500 m³ 161,0; 2.500–6.000 m³ 160,0 (5.820 m³);
**6.000–12.000 m³ 159,9 (7.400 m³)**; 12.000–35.000 m³ 166,1 €/MWh – flaches Optimum (2.500–12.000 m³ innerhalb
0,1 €/MWh).

**Betrieb über das Jahr** (`1_jahresverlauf.png`): Der Speicher wird Juli–Oktober mit Solarwärme geladen (bis 85 °C),
im November/Dezember gehalten und im Januar zuerst direkt (Oberschicht ≈ 85 °C), danach über die Speicher-WP bis
10 °C entladen. Direktentladung gibt es nur bei dicker heißer Schicht (`kennlinie_rest_MWh` = 0).

**Ohne Flächengrenze (Abschätzung aus der Heatmap, kein Lauf):** Die 13.000 m² binden, kosten aber wenig. Bei 4.000 m²
bringen +1.000 m² Kollektor nur noch 3–5 €/MWh weniger, Tendenz fallend. Geschätztes Optimum ohne Grenze ≈ 5.000 m² /
8.000–10.000 m³, Wärmepreis **höchstens 1–2 €/MWh** niedriger, Solaranteil ≈ 45 %. Obergrenze, denn Fläche kostet im
Modell nichts (keine Pacht/kein Kauf).

## Was die Änderungen vom 10.11. bewirkt haben (Netz klein)

| Stand | Kollektor / Speicher | LCOH | Wärmepreis inkl. Netz / Gas | Solar | Winteranteil |
|---|---|---|---|---|---|
| vorher (E31) | 2.540 m² / 1.640 m³ | 141,2 | 229 / 257 | 24 % | 28 % |
| + KWW-Kosten Kollektor, PTES, Trasse (E32) | 4.500 / 7.010 | 131,8 | 221 / 261 | 42 % | 47 % |
| + Kennlinie, Schichtung, Luft-WP nach KWW (E34–E36) | 3.680 / 4.560 | 152,9 | 247 / 261 | 35 % | 36 % |
| + WP 1.340 €/kW (E38) = **Basis** | 4.440 / 7.400 | 159,9 | 255 / 261 | 41 % | 46 % |

Der größte Sprung (+21 €/MWh) kommt von der realistischeren Luft-WP (Arbeitszahl 2,65 → 2,22, E35). Teurere WP
machen Solar und Speicher wieder attraktiver (mehr Fläche, mehr Speicher), der Vorteil gegenüber Gas schrumpft aber
auf ≈ 6 €/MWh.

## Vergleichsvarianten (`uv run serts varianten`, Briefing Pflicht 5)

| | Basis | ohne Speicher | nur WP + PtH | mit BEW Modul 2 (optimiert) | Gas-Fernwärme |
|---|---|---|---|---|---|
| Kollektor / Speicher | 4.440 m² / 7.400 m³ | 1.250 m² / – | – | 4.440 m² / 7.420 m³ | – |
| Solaranteil / EE-Anteil | 41 % / 86 % | 9 % / 80 % | 0 % / 79 % | 41 % / 86 % | 0 |
| CO₂ [t/a] | 625 | 850 | 924 | 611 | 1.160 |
| LCOH Erzeugung [€/MWh] | 159,9 | 169,3 | 174,4 | 138,6 | 164,9 |
| Wärmepreis inkl. Netz [€/MWh] | **255,3** | 266,8 | 272,9 | **220,7** | **261,4** |
| dito mit BEW, gleiche Auslegung | 221,1 | 243,6 | 252,3 | 220,7 | – |

* **Solar + Speicher lohnt sich**: gegenüber reiner WP + PtH −18 €/MWh, gegenüber Solar ohne Speicher −12 €/MWh;
  nur Solar + Speicher ist überhaupt günstiger als Gas-Fernwärme.
* **Mit BEW** ändert sich die Auslegung kaum (die Fläche bindet schon), der Wärmepreis sinkt um ≈ 35 €/MWh.
  40 % ist die Obergrenze; die BAFA begrenzt auf die Wirtschaftlichkeitslücke (E37).

## Heatmaps Kollektorfläche × Speichervolumen (`uv run serts heatmap`, ≈ 25 min)

`heatmap_alle.png` im Ergebnisordner zeigt neun Kennzahlen (Wärmepreis, mit BEW, Vorteil ggü. Gas, Solaranteil, CO₂,
Speicherzyklen, Winteranteil, WP-Leistung, PtH-Wärme). Wärmepreis inkl. Netz [€/MWh], Gas-Fernwärme 261:

| V \ A [m²] | 1.000 | 2.000 | 3.000 | 4.000 | 5.000 |
|---|---|---|---|---|---|
| 0 m³ | 267 | 268 | 272 | 276 | 282 |
| 1.000 m³ | 266 | 260 | 258 | 259 | 262 |
| 2.000 m³ | 267 | 261 | 257 | 259 | 261 |
| 4.000 m³ | 270 | 262 | 258 | 256 | – |
| 5.500 m³ | 273 | 264 | 259 | **256** | – |
| 7.000 m³ | 276 | 267 | 260 | 256 | – |
| 10.000 m³ | 283 | 272 | 264 | 259 | – |

* **Flaches Tal**: 3.000–4.000 m² mit 1.000–7.000 m³ liegen innerhalb ≈ 4 €/MWh; günstiger als Gas nur rechts der
  Diagonale (genug Kollektor je m³ Speicher).
* **Wann wird der Speicher saisonal?** Bei großem Speicher und wenig Kollektor: ≤ 1 Zyklus und > 95 % Winteranteil
  (z. B. 1.000–2.000 m² mit 5.500–10.000 m³) – aber genau dort ist das System am teuersten (bis +21 €/MWh über Gas).
  Im kostengünstigen Bereich ist der Speicher ein Mischspeicher (2–3 Zyklen, 35–50 % Winteranteil).
* Ohne Speicher wird mehr Kollektor teurer (der Sommerüberschuss bleibt ungenutzt); PtH-Wärme sinkt mit Speicher.

## Strom: fest gegen Day-Ahead (Szenarien `strom_day_ahead_*`, Stand E38: WP 1.340 €/kW)

Preis(t) = Day-Ahead(t) + Marge 25 + Netzentgelt 93 + Abgaben 57 €/MWh; Preisjahr unabhängig vom Wetterjahr 2022.

| | fest 30 ct | Day-Ahead 2024 | Day-Ahead 2024 normiert (Ø wie fest) | Day-Ahead 2022 (Krise) |
|---|---|---|---|---|
| Strompreis Ø / gewichtet bezahlt [€/MWh] | 300 / 300 | 254 / 252 | 300 / 294 | 410 / 345 |
| Kollektor / Speicher | 4.440 m² / 7.400 m³ | 3.630 / 4.270 | 4.440 / 7.400 | 4.460 / 7.260 |
| Speicher-Zyklen / Winteranteil | 2,3 / 46 % | 3,3 / 35 % | 2,4 / 46 % | 2,6 / 46 % |
| Solaranteil | 41 % | 34 % | 41 % | 42 % |
| Strombezug [MWh/a] | 1.720 | 1.850 | 1.710 | 1.690 |
| LCOH Erzeugung / Wärmepreis inkl. Netz [€/MWh] | 160 / 255 | **144 / 237** | 159 / 254 | 176 / **274** |
| Gas-Fernwärme inkl. Netz / mit BEW | 261 / 221 | 261 / 205 | 261 / 219 | 261 / 239 |

* **Preisniveau** entscheidet: mit Day-Ahead 2024 (Ø 25 ct) ist das System 24 €/MWh günstiger als Gas-Fernwärme,
  im Krisenjahr 2022 (Ø 41 ct) 13 €/MWh teurer.
* **Zeitliche Struktur** allein (normiert) senkt den bezahlten Preis um 2 % und den Wärmepreis um ≈ 1 €/MWh: der
  Speicher nimmt nur Solarwärme auf (die WP lädt ihn nicht, E29), Preisspitzen werden kaum ausgenutzt.
* Die Auslegung reagiert kaum auf die Preisstruktur (Kollektor/Speicher fast gleich), nur auf das Preisniveau.
* Nicht modelliert: Leistungspreis; Korrelation Preis ↔ Wetter (Preis- und Wetterjahr verschieden).

## Sensitivitäten (`uv run serts tornado`, 48 Varianten, **Stand E37: WP noch 1.000 €/kW**, Größen jeweils neu optimiert)

Wärmepreis inkl. Netz (Basis 247 €/MWh) und Vorteil gegenüber Gas-Fernwärme (Basis **+14,5 €/MWh**):

| Parameter (Variante) | Wärmepreis inkl. Netz | Vorteil ggü. Gas |
|---|---|---|
| Gaspreis 8 / 16 ct/kWh | – | **−42 / +71** |
| Strompreis 20 / 40 ct/kWh | 203 / 284 | **+59 / −23** |
| Gütegrad Luft-WP × 0,85 / × 1,15 | 262 / 233 | **−0,4 / +29** |
| Förderung BEW 40 % (mit Förderung optimiert) | 214 | **+47** (4.440 m², 7.420 m³, Solar 41 %) |
| CO₂-Preis 55 / 200 €/t | – | +3 / +40 |
| Zins 3 / 7 % (real) | 224 / 268 | +26 / +6 |
| Strompreis +2 %/a real | 267 | −5 |
| WP-Kosten 0,7 / 1,4 Mio. €/MW | 239 / 257 | +23 / +5 |
| Nebenkosten 0 / 20 % | 235 / 258 | +21 / +9 |
| Kollektor 240 / 380 €/m² | 241 / 252 | +20 / +10 |
| Übergangszone (Kennlinie) 0 / 0,15 / 0,5 | 236 / 245 / 248 | +25 / +17 / +13 |
| Speicherkosten × 0,7 / × 1,3 | 242 / 249 | +19 / +12 |
| COP Speicher-WP 3,5 / 5,5 | 250 / 244 | +11 / +18 |
| Strahlung − / + 10 % | 251 / 243 | +11 / +19 |
| Ankerkunde + 20 / 40 % | 226 / 211 | +19 / +23 |
| Last × 0,8 / × 1,2 | 269 / 232 | +16 / +14 |
| PtH-Reserve 0 (statt Spitzenlast) | 244 | +17 |
| Hausanschluss 5.000 / 15.000 € | 229 / 265 | unverändert (gleiches Netz) |
| Trasse Straße 370 / 940 €/m; Anteil Straße 50 / 100 % | 237–257 | unverändert |
| Rücklauf 40 / 50 °C; Luft-WP-Leistung bei −7 °C 60 / 100 % | 246–248 | ±1 |

**Lesart:** Ob das System günstiger ist als Gas-Fernwärme, entscheiden **Gas- und Strompreis**, danach die
**Effizienz der Luft-WP** (bei 15 % schlechterem Gütegrad ist der Vorteil weg), Förderung, CO₂-Preis und Zins.
Die Größen von Kollektorfeld und Speicher springen mit den Kosten (Speicher 540–8.840 m³, Solaranteil 20–40 %),
ohne dass der Wärmepreis stark reagiert (flaches Optimum). Ohne Kennlinie (ideale Schichtung) wäre der Speicher
größer (7.000 m³) und das System 11 €/MWh günstiger – die Kennlinie ist also ergebnisrelevant.

**Kernaussage (vorläufig, Netz klein):** Luft-WP + Speicher-WP mit Solarthermie, PTES und PtH-Reserve ist unter den
Basisannahmen ≈ 6 % günstiger als Gas-Fernwärme, mit BEW Modul 2 (Obergrenze) ≈ 18 %. Der Vorteil ist knapp und hängt
vor allem an Energiepreisen und WP-Effizienz. Der kostenoptimale Speicher ist ein Mischspeicher (≈ 4.600 m³,
≈ 3 Zyklen), kein Saisonspeicher. Netz groß: `docs/ergebnisse_netz_gross.md`, Prüfung: `docs/kernfragen.md`.
