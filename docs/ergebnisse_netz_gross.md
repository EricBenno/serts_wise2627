# Ergebnisse Netz groß (oben Stand 24.11.2026 nach E43/E44, darunter 21.11. nach E41, darunter 14.11. und 10.11.2026)

Netzfall `gross` (`config/netze/gross.yaml`, Aufruf `uv run serts run --netz gross`, Ergebnisse in `results/gross/`):
877 Gebäude, davon 54 % der Wärme in Nichtwohngebäuden (GMK/GKO), 42.782 MWh/a Gebäude + 5.440 MWh/a Netzverluste,
Spitze 15,5 MW (Stundensumme), Trasse 14.291 m, Freifläche 80.000 m². Alle anderen Annahmen wie Netz klein
(`docs/eingangsparameter.md` zeigt beide nebeneinander). Kollektor 276 €/m² Brutto (KWW, Klasse ≥ 15.000 m²
Apertur), Trasse 1.140/640 €/m (KWW, größere Rohre), Luft-WP nach KWW-Gütegrad, Speicher mit Kennlinie (E34–E36).

## Stand 24.11.2026 nach E43/E44 (Day-Ahead-Basis, Gas 12 ct, Zins 4 %, Kosten je Netz)

Annahmen wie Netz klein (`docs/ergebnisse.md`, Abschnitt 24.11.), aber Luft-WP 1.340 €/kW und PtH 180 €/kW (KWW,
größere Klassen). Ergebnisse: `results/gross/20261123-212251_base_opt`, `..._varianten` (20261123-212255),
`..._heatmap` (20261123-214212), `..._tornado` (20261124-010559).

**Basis:** 28.351 m² / 39.200 m³, WP 9,11 MW, PtH 15,5 MW, Solar 29 %, 4,8 Zyklen, LCOH 127,8 €/MWh,
**Wärmepreis inkl. Netz 189,2 €/MWh (Gas 207,3)**, mit BEW 164,1. Strom gewichtet 221 €/MWh, höchster Bezug 4,3 MW.
Varianten: ohne Speicher 222,0, nur WP + PtH 224,3, BEW-optimiert 164,0 €/MWh.

**Tornado** (Δ zum Wärmepreis inkl. Netz 189,2 €/MWh):

| Parameter | niedrig | hoch |
|---|---|---|
| fester Tarif 20 / 30 / 40 ct statt Day-Ahead | −9,4 | +27,0 / +63,2 |
| Preisjahr 2023 / 2022 | | +7,6 / +33,7 |
| Förderquote 40 % | −25,2 | |
| Ankerkunde 20 / 40 % | −13,7 / −22,9 | |
| Zins 2 / 6 % | −18,0 | +19,1 |
| Strompreis +2 %/a real | | +15,8 |
| WP-Gütegrad ×0,85 / ×1,15 | +14,6 | −10,9 |
| Vorlauf gleitend 60 / 70 °C | −14,1 / −7,0 | |
| Last ×0,8 / ×1,2 | +12,6 | −8,3 |
| Fläche unbegrenzt (130.000 m³ = Rasterende, Solar 58 %) | −12,1 | |
| Vorlauf fest 70 / 90 °C | −10,8 | +4,1 |
| Hausanschluss 5.000 / 15.000 € | −9,8 | +9,8 |
| Nebenkosten 0 / 20 % | −9,4 | +9,3 |
| Luft-WP 1.000 / 1.730 €/kW | −7,5 | +8,0 |
| Trasse Straße 730 / 1.560 €/m | −8,1 | +8,2 |
| PtH ohne Redundanz | −6,7 | |
| Leistungspreis 15,5 / 80 €/(kW·a) | −2,9 | +3,6 |

Übrige ≤ ±4 €/MWh. Gas-Referenz 6 / 8 / 10 / 14 ct/kWh: Abstand −54,1 / −30,7 / −7,3 / +39,4 €/MWh (Basis +16,0),
Gleichstand bei ≈ 11 ct/kWh. Lesart: Das große Netz bleibt unter Gas außer bei Gas ≤ 11 ct, Preisjahr 2022 oder
festem Tarif ≥ 30 ct.

**Heatmap:** ab ≈ 20.000 m³ Speicher flach (190–199 €/MWh); ohne Speicher 222–228.

## Stand 21.11.2026 nach E41 (Boosting, zwei WP, COP Jensen, Durchflussgrenze)

**Basis:** 29.240 m² / 33.780 m³, WP 8,65 MW Luft + 1,09 MW Speicher, PtH 15,5 MW (159 MWh/a), Solar 30 %,
3,9 Zyklen, LCOH 153,6 €/MWh, **Wärmepreis inkl. Netz 223,1 €/MWh** (vorher 221,6; Gas 236,2), mit BEW 194,5.
Varianten (`results/gross/20261121-161709_base_varianten`): ohne Speicher 249,0, nur WP + PtH 254,5, BEW-optimiert
194,4 €/MWh. Der volle Tornado wurde nicht neu gerechnet.

**Vorlauftemperatur** (`uv run serts tornado --netz gross --parameter netz.T_VL netz.T_VL_min`,
`results/gross/20261121-171545_base_sensitivitaet`):

| Vorlauf | inkl. Netz | Δ Basis | Vorteil ggü. Gas | Kollektor [m²] | Speicher [m³] | JAZ WP | Strom [MWh] | Boosting [MWh] | PtH [MWh] |
|---|---|---|---|---|---|---|---|---|---|
| fest 70 °C | 209,1 | −14,0 | 24,1 | 29.010 | 35.170 | 2,56 | 13.740 | 0 | 64 |
| fest 75 °C | 216,1 | −7,0 | 17,8 | 29.150 | 34.300 | 2,38 | 14.740 | 0 | 119 |
| **fest 80 °C (Basis)** | 223,1 | – | 11,7 | 29.240 | 33.780 | 2,23 | 15.730 | 0 | 159 |
| fest 85 °C | 225,5 | +2,4 | 9,5 | 29.240 | 33.810 | 2,18 | 16.100 | 210 | 200 |
| fest 90 °C | 228,0 | +4,9 | 7,3 | 29.230 | 33.840 | 2,14 | 16.460 | 415 | 248 |
| gleitend 80 → 70 °C | 214,0 | −9,1 | 19,7 | 28.980 | 35.400 | 2,44 | 14.450 | 0 | 104 |
| gleitend 80 → 60 °C | 205,2 | −17,9 | 27,6 | 28.330 | 39.330 | 2,69 | 13.230 | 0 | 0 |

Lesart wie Netz klein: Wirkung fast nur über COP/Strom, Boosting über 80 °C klein. Bei niedrigem Vorlauf wird der
Speicher etwas größer und das Kollektorfeld etwas kleiner (bessere Speicher-WP, weniger PtH). Netzverluste bleiben
bei 80/50 °C -> Vorteil niedriger Vorläufe eher unterschätzt.

## Stand 14.11.2026 nach E39 (neues Speichermodell)

Geändert wie Netz klein (`docs/ergebnisse.md`, E39). Heatmap und Tornado am 15.11. neu gerechnet (unten). **„Basislauf
im Vergleich alt“, die alte Variantentabelle und „Lesart“ zeigen den Stand vom 10.11.** Ergebnisordner
`results/gross/20261114-174233_base_opt` und `…-174238_base_varianten`.

| Kennzahl | Netz groß alt (10.11.) | **Netz groß neu** | Netz klein neu |
|---|---|---|---|
| Kollektor / Speicher | 28.400 m² / 38.900 m³ | **29.800 m² / 30.300 m³** | 4.670 m² / 6.000 m³ |
| Fläche belegt / verfügbar | 80.000 / 80.000 m² | 80.000 / 80.000 m² (Grenze bindet) | 13.000 / 13.000 m² |
| Wärmepumpe / PtH | 9,1 / 15,5 MW (PtH 990 MWh/a) | 9,3 / 15,5 MW (PtH 280 MWh/a) | 0,95 / 1,59 MW (0) |
| Strombezug / höchste Leistung | 17.020 MWh/a / – | 15.630 MWh/a / 4,7 MW | 1.520 MWh/a / 0,46 MW |
| Speicher: Zyklen / Winteranteil / Charakter | 2,5 / 41 % / gemischt | 4,3 / 31 % / kurzzeit | 3,2 / 37 % / gemischt |
| Speicher: Verlustrate / Übergangszone / Wirkungsgrad | 4·10⁻⁵ / 30 % / – | 5·10⁻⁵ / 19 % / 95 % | 8,6·10⁻⁵ / 32 % / 89 % |
| LCOH Erzeugung (Gas-Referenz 165,3) | 158,8 | **152,3** | 150,0 |
| Wärmepreis inkl. Netz (Gas-Fernwärme 236,2) | 228,9 | **221,6** (−6 %) | 243,4 (Gas 261,4) |
| mit BEW Modul 2, gleiche Auslegung | 201 | 193,3, Zuschuss ≤ 16,7 Mio. € | 209,3 |
| Solaranteil / CO₂ (Gas-Referenz 10.200 t/a) | 30 % / 6.180 t/a | 31 % / 5.670 t/a | 40,5 % / 551 t/a |

**Kostensegmente** (LCOH, V, A): 0–2.500 m³ 160,8; 2.500–10.000 m³ 157,6; 10.000–30.000 m³ 153,0 (28.700 m³);
**30.000–70.000 m³ 152,3 (30.300 m³, 29.800 m²)**; 70.000–130.000 m³ 156,8 €/MWh.

| Varianten neu | Basis | ohne Speicher | nur WP + PtH | mit BEW Modul 2 (optimiert) | Gas-Fernwärme |
|---|---|---|---|---|---|
| Kollektor / Speicher | 29.800 m² / 30.300 m³ | 11.200 m² / – | – | 29.900 m² / 30.000 m³ | – |
| Solaranteil / EE-Anteil | 31 % / 85 % | 9 % / 80 % | 0 % / 79 % | 31 % / 85 % | 0 |
| CO₂ [t/a] | 5.670 | 7.640 | 8.250 | 5.620 | 10.200 |
| LCOH Erzeugung [€/MWh] | 152,3 | 176,6 | 181,5 | 135,8 | 165,3 |
| Wärmepreis inkl. Netz [€/MWh] | **221,6** | 249,0 | 254,5 | **193,0** | **236,2** |

* Der Speicher wird im großen Netz kleiner (30.300 statt 38.900 m³) und häufiger umgeschlagen (4,3 Zyklen): er
  arbeitet als Kurzzeitspeicher. Mehr Fläche geht an den Kollektor.
* Vorteil gegenüber Gas-Fernwärme 14,6 €/MWh (vorher 7,3); Solar + Speicher spart 33 €/MWh gegenüber reiner WP + PtH.

## Basislauf im Vergleich alt (Stand 10.11.2026, WP 1.340 €/kW, E38)

| Kennzahl | Netz groß | Netz klein |
|---|---|---|
| Kollektor / Speicher | **28.400 m² / 38.900 m³** | 4.440 m² / 7.400 m³ |
| Fläche belegt / verfügbar | **80.000 / 80.000 m² (Grenze bindet)** | 13.000 / 13.000 m² |
| Wärmepumpe / PtH | 9,1 MW / 15,5 MW (PtH liefert 990 MWh/a) | 0,93 / 1,59 MW (140 MWh/a) |
| Kollektorertrag | 15.140 MWh/a (533 kWh/m²) | 2.370 MWh/a |
| Strombezug / Arbeitszahl WP | 17.020 MWh/a / 2,46 | 1.720 MWh/a / 2,68 |
| Speicher: Zyklen / Winteranteil / Charakter | 2,5 / 41 % / gemischt | 2,3 / 46 % / gemischt |
| Spez. Speicherkosten (Kostenkurve KWW) | 75 €/m³ | 114 €/m³ |
| LCOH Erzeugung (Gas-Referenz) | **159 €/MWh** (165) | 160 €/MWh (165) |
| Wärmepreis inkl. Netz (Gas-Fernwärme) | **229 €/MWh** (236) | 255 €/MWh (261) |
| davon Trasse / Hausanschlüsse | 28,7 / 21,2 €/MWh | 25,9 / 36,4 €/MWh |
| **mit BEW Modul 2** (gleiche Auslegung, Obergrenze) | **201 €/MWh**, Zuschuss ≤ 16,6 Mio. € | 221 €/MWh, ≤ 2,1 Mio. € |
| Solaranteil / CO₂ (Gas-Referenz) | 30 % / 6.180 t/a (10.200) | 41 % / 625 t/a (1.160) |

**Kostensegmente des Speichers** (LCOH, V, A): 0–2.500 m³ 164,8; 2.500–10.000 m³ 163,5; 10.000–30.000 m³ 159,6;
**30.000–70.000 m³ 158,8 (38.900 m³, 28.400 m²)**; 70.000–130.000 m³ 161,8 €/MWh (70.000 m³, nur 23.300 m² Kollektor).

## Vergleichsvarianten alt (Stand 10.11.2026; neu: oben)

| | Basis | ohne Speicher | nur WP + PtH | mit BEW Modul 2 (optimiert) | Gas-Fernwärme |
|---|---|---|---|---|---|
| Kollektor / Speicher | 28.400 m² / 38.900 m³ | 11.600 m² / – | – | 28.750 m² / 36.780 m³ | – |
| Solaranteil / EE-Anteil | 30 % / 84 % | 9 % / 80 % | 0 % / 79 % | 31 % / 84 % | 0 |
| CO₂ [t/a] | 6.180 | 7.600 | 8.250 | 6.100 | 10.200 |
| LCOH Erzeugung [€/MWh] | 158,8 | 172,0 | 177,3 | 142,1 | 165,3 |
| Wärmepreis inkl. Netz [€/MWh] | **228,9** | 243,8 | 249,8 | **200,1** | **236,2** |

## Heatmaps Kollektorfläche × Speichervolumen (Stand 22.11.2026 nach E41)

`results/gross/20261122-164427_base_heatmap`, Bild `docs/img/heatmap_gross.png`, `heatmap_alle.png` (neun Kennzahlen). Wärmepreis inkl. Netz [€/MWh], WP und PtH je Punkt optimiert, „–“ = passt nicht auf die Fläche:

| V [m³] \ A [m²] | 5.000 | 10.000 | 15.000 | 20.000 | 25.000 | 30.000 |
|---|---|---|---|---|---|---|
| 50.000 | 249 | 242 | 236 | 231 | 226 | – |
| 35.000 | 248 | 241 | 236 | 231 | 226 | – |
| 20.000 | 247 | 242 | 237 | 232 | 229 | 227 |
| 10.000 | 248 | 243 | 239 | 237 | 237 | 237 |
| 5.000 | 261 | 245 | 243 | 243 | 244 | 245 |
| 0 | 250 | 249 | 249 | 251 | 252 | 254 |

Bester Rasterpunkt 25.000 m² / 50.000 m³ mit 226,0 €/MWh (35.000 m³: 226,5); freies Optimum 29.200 m² / 33.800 m³ mit 223,1. Ab ≈ 20.000 m³ ist das Feld flach (±3 €/MWh); große Kollektorflächen lohnen nur mit Speicher.

## Heatmaps alt (`uv run serts heatmap --netz gross`, Stand 15.11.2026 nach E39, ≈ 12 min)

`results/gross/20261115-152947_base_heatmap`, `heatmap_alle.png` (neun Kennzahlen). Wärmepreis inkl. Netz [€/MWh],
Gas-Fernwärme 236; Basis-Optimum 29.800 m² / 30.300 m³ = 221,6:

| V \ A [m²] | 5.000 | 10.000 | 15.000 | 20.000 | 25.000 | 30.000 |
|---|---|---|---|---|---|---|
| 0 m³ | 250 | 249 | 249 | 251 | 252 | 254 |
| 5.000 m³ | 247 | 242 | 237 | 233 | 231 | 230 |
| 10.000 m³ | 246 | 241 | 236 | 232 | 229 | 228 |
| 20.000 m³ | 246 | 240 | 235 | 231 | 226 | **224** |
| 35.000 m³ | 247 | 240 | 235 | 230 | 225 | – |
| 50.000 m³ | 248 | 240 | 235 | 230 | 225 | – |

* **Mehr Kollektor lohnt sich bis zum Flächenrand**, solange Speicher dabei ist (je +5.000 m² ≈ −2 bis −5 €/MWh);
  günstiger als Gas ab ≈ 15.000 m². Gegenüber dem 10.11. ist das Feld mit Speicher 3–8 €/MWh günstiger, ohne
  Speicher ≈ 5 €/MWh teurer (Leistungspreis, Einfallswinkel).
* **Volumen**: ab 20.000 m³ flach (bei 25.000 m²: 226 → 225 €/MWh bis 50.000 m³).
* **Charakter**: bei 25.000 m² / 35.000 m³ 3,4 Zyklen, 36 % Winteranteil (Mischspeicher). Saisonal (< 1 Zyklus,
  > 70 % Winter) nur mit wenig Kollektor (5.000–10.000 m² mit ≥ 20.000 m³) – dort teurer als Gas.

## Sensitivitäten (`uv run serts tornado --netz gross`, 60 Varianten, Stand 22.11.2026 nach E41/E42)

`results/gross/20261122-135246_base_tornado` (≈ 1,6 h). Wärmepreis inkl. Netz (Basis 223,1 €/MWh) und Vorteil
gegenüber Gas-Fernwärme (Basis **+11,7 €/MWh**, LCOH Erzeugung):

| Parameter (Variante) | Wärmepreis inkl. Netz | Vorteil ggü. Gas | Kollektor / Speicher |
|---|---|---|---|
| Gaspreis 8 / 16 ct/kWh | – | **−35 / +58** | – |
| Strompreis 20 / 40 ct/kWh | 186 / 260 | **+45 / −21** | 29.100 / 34.600; 29.300 / 33.100 |
| CO₂-Preis 55 / 200 €/t | – | +2 / +33 | – |
| **keine Flächenbegrenzung** | **200** | **+33** | **57.700 m² / 130.000 m³** (Segmentgrenze), Solar 58 % |
| Förderung BEW 40 % | 194 | +28 | gleich |
| **Vorlauf gleitend 80 → 60 / 80 → 70 °C** (neu) | **205 / 214** | **+28 / +20** | 28.300 / 39.300; 29.000 / 35.400 |
| **Vorlauf fest 70 / 90 °C** (neu) | **209 / 228** | **+24 / +7** | 29.000 / 35.200; gleich |
| Gütegrad Luft-WP × 0,85 / × 1,15 | 242 / 209 | **−5,2 / +24** | gleich |
| Strompreis +2 %/a real | 243 | **−5,9** | gleich |
| Leistungspreis 0 / 163,73 €/kW·a | 221 / 239 | +13 / **−2,0** | 28.900 / 35.900 bei 163,73 |
| Zins 3 / 7 %; WP-Kosten Luft 1,0 / 1,73 Mio. €/MW | 205 / 243; 215 / 232 | +19 / +4 | gleich |
| Nebenkosten 0 / 20 %; Kollektor 220 / 350 €/m² | 213–233 | +7 … +16 | gleich |
| Strahlung − / + 10 %; Last × 0,8 / × 1,2; Ankerkunde + 20 / 40 % | 201–234 | +6 … +17 | 28.500 / 38.400 bei +10 % Strahlung |
| PtH-Reserve 0; η₀; Feldverluste; Speicherverluste; Speicherkosten ±30 % | 219–227 | +8 … +15 | 29.000–29.600 / 31.800–35.300 |
| **Speicher-Obertemperatur 80 / 90 °C** (neu) | 224 / 222 | +10 / +13 | 28.700 / 36.900; 29.600 / 31.700 |
| Vorwärmen aus; Rücklauf; b₀; Größenabhängigkeit; Kosten Speicher-WP; Jensen-Wirkungsgrad | 222–224 | ±1,2 | gleich |
| **Durchflussgrenze aus** (neu) | 223,1 | +0,2 | 29.800 / 30.400 |
| Hausanschluss, Trasse, Anteil Straße | 212–234 | unverändert | gleiches Netz |

**Lesart (neu):**
* Wie im kleinen Netz: Gas- und Strompreis, Fläche, Förderung, **Vorlauf** und WP-Gütegrad entscheiden. Der Vorteil
  gegenüber Gas kippt bei 15 % schlechterem Gütegrad, +2 %/a realem Strompreisanstieg oder hohem Leistungspreis.
* **Gleitender Vorlauf bis 60 °C: −18 €/MWh**, der Speicher wächst dabei auf 39.300 m³ (bessere Speicher-WP).
* E41-Details (Obertemperatur, Durchflussgrenze, Speicher-WP) verschieben die Auslegung etwas, den Preis ≤ 1,4 €/MWh.
* Ohne Flächengrenze wieder am größten Kostensegment (130.000 m³); Nachrechnung bis 200.000 m³ siehe unten (15.11.).

## Sensitivitäten alt (`uv run serts tornado --netz gross`, 50 Varianten, Stand 15.11.2026 nach E39)

`results/gross/20261115-154127_base_tornado` (≈ 2,4 h). Wärmepreis inkl. Netz (Basis 221,6 €/MWh) und Vorteil
gegenüber Gas-Fernwärme (Basis **+13,0 €/MWh**, LCOH Erzeugung):

| Parameter (Variante) | Wärmepreis inkl. Netz | Vorteil ggü. Gas | Kollektor / Speicher |
|---|---|---|---|
| Gaspreis 8 / 16 ct/kWh | – | **−34 / +60** | – |
| Strompreis 20 / 40 ct/kWh | 185 / 258 | **+46 / −19** | gleich |
| **keine Flächenbegrenzung** (80.000 m² → unbegrenzt) | **198** | **+34** | **57.900 m² / 130.000 m³** (Segmentgrenze!), Solar 58 % |
| Förderung BEW 40 % | 193 | +29 | gleich |
| CO₂-Preis 55 / 200 €/t | – | +3 / +34 | – |
| Gütegrad Luft-WP × 0,85 / × 1,15 | 240 / 208 | **−3,7 / +25** | gleich |
| Zins 3 / 7 % (real) | 203 / 241 | +20 / +5 | gleich |
| Strompreis +2 %/a real | 241 | **−4,4** | gleich |
| Leistungspreis 0 / 163,73 €/kW·a (≥ 2.500 h) | 220 / 237 | +15 / **−0,7** | 29.200 / 34.200 |
| WP-Kosten 1,0 / 1,73 Mio. €/MW | 213 / 231 | +21 / +4 | gleich |
| Nebenkosten 0 / 20 % | 212 / 232 | +18 / +8 | gleich |
| Ankerkunde + 20 / 40 % | 208 / 199 | +14 / +15 | 32.500 / 13.800; 32.800 / 12.000 |
| Last × 0,8 / × 1,2 | 233 / 214 | +18 / +9 | 28.900 / 35.600; gleich |
| Strahlung − / + 10 % | 228 / 216 | +7 / +18 | gleich; 28.500 / 38.100 |
| Kollektor 220 / 350 €/m² | 218 / 226 | +16 / +9 | gleich |
| Hausanschluss 5.000 / 15.000 €; Trasse 730 / 1.560 €/m; Anteil Straße 50 / 100 % | 211–232 | unverändert | gleiches Netz |
| η₀, Feldverluste, Speicherverluste, PtH-Reserve, Speicherkosten ±30 % | 218–226 | +9 … +16 | 29.300–29.900 / 30.000–33.400 |
| Vorwärmen, Größenabhängigkeit, Übergangszone, COP Speicher-WP, Rücklauf, Einfallswinkel | 220–223 | ±1 | gleich |

**Lesart:**
* Wie im kleinen Netz entscheiden **Gas- und Strompreis**, dann **WP-Gütegrad**, Zins und Förderung. Im großen Netz
  kippt der Vorteil schon bei 15 % schlechterem Gütegrad, +2 %/a realem Strompreisanstieg oder dem hohen
  Leistungspreis (≥ 2.500 Benutzungsstunden).
* **Fläche ist auch hier der größte Auslegungshebel**: siehe unten. Speicherparameter wirken ≤ 2 €/MWh.

**Ohne Flächengrenze:** Im Tornado landet das Volumen genau auf der Obergrenze der Kostensegmente (130.000 m³).
Nachgerechnet mit Stützstellen bis 200.000 m³ (Gültigkeitsgrenze der KWW-Kostenkurve), ebenfalls am Rand:

| Größtes Segment bis | Kollektor / Speicher | Solaranteil | Zyklen / Winteranteil | Wärmepreis inkl. Netz | Fläche |
|---|---|---|---|---|---|
| Basis (Fläche 80.000 m²) | 29.800 m² / 30.300 m³ | 31 % | 4,3 / 31 % | 221,6 | 8 ha |
| 130.000 m³ | 57.900 m² / 130.000 m³ | 58 % | – | 197,9 | 18 ha |
| 200.000 m³ | 72.900 m² / 200.000 m³ | 73 % | 1,7 / 66 % (saisonal) | **186,2** (mit BEW 147,6) | 24 ha |

Jedes größere Segment ist ≈ 10 €/MWh günstiger (LCOH 152 → 143 → 131 → 121 €/MWh); ein Optimum innerhalb des
gültigen Kostenbereichs gibt es nicht. Im großen Netz begrenzt also allein die Fläche (und die Gültigkeit der
Kostenkurve) Saisonspeicher und Solaranteil. CO₂ sinkt auf 2.510 t/a (Basis 5.670). Fläche kostet im Modell
nichts; Wärmeverluste und Kosten der Zuleitung zu einer weiter entfernten Fläche fehlen ebenfalls.

## Basis-Abschätzung ohne Flächengrenze vom 10.11. (überholt)

~~Geschätzt −2 bis −4 €/MWh bei 35.000–40.000 m² / 60.000–90.000 m³.~~ Gerechnet: siehe Tornado oben.

## Lesart (Stand 10.11.)

* **Die Fläche begrenzt das System**, nicht die Kosten: Kollektor (2,3 m² Grund je m²) und Speicher (2,65 m³ je m²)
  teilen sich die 8 ha vollständig; mit BEW ändert sich die Auslegung deshalb kaum.
* **Skaleneffekte**: Speicher je m³ ≈ 35 % billiger, Hausanschlüsse verteilen sich auf mehr Wärme (49 statt 28 MWh/a je
  Anschluss); die Trasse ist je m teurer (größere Rohre) und je MWh etwa gleich teuer.
* **Wärmepreis beim Kunden** ≈ 229 €/MWh, ≈ 3 % unter Gas-Fernwärme (236); mit BEW ≈ 201 €/MWh (−15 %).
* **PtH** liefert ≈ 990 MWh/a (Kältespitzen bei voll ausgelasteter WP); die 15,5-MW-Reserve (Stundensumme aller
  Gebäude) kostet ≈ 4 €/MWh. Mit Gleichzeitigkeitsfaktor (11,5 MW laut Netzberechnung) wäre sie ≈ 26 % kleiner.

## Szenario `kww_komplett_gross` (auch WP, PtH, Gaskessel, Netz-Lebensdauer aus dem KWW)

Ergebnis noch Stand vor E34–E36 (Luft-WP nach Lorenz, erste Kennlinie): +9 €/MWh gegenüber der damaligen Basis.
Neu rechnen mit `uv run serts run --netz gross --szenario kww_komplett_gross`.

## Offen / nicht gerechnet

- Day-Ahead-Szenarien und `vl_gleitend` für das große Netz (nur Netz klein gerechnet).
- Flächenkosten (Pacht/Kauf) fehlen; ohne sie ist die Variante „keine Flächenbegrenzung“ eine Obergrenze.
- Hausanschlüsse: pauschal 10.000 € wie im kleinen Netz; bei 54 % Nichtwohngebäuden eher oberes Ende (E32).
