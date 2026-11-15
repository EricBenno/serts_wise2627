# Ergebnisse Netz groß (oben Stand 14.11.2026 nach E39, darunter Stand 10.11.2026)

Netzfall `gross` (`config/netze/gross.yaml`, Aufruf `uv run serts run --netz gross`, Ergebnisse in `results/gross/`):
877 Gebäude, davon 54 % der Wärme in Nichtwohngebäuden (GMK/GKO), 42.782 MWh/a Gebäude + 5.440 MWh/a Netzverluste,
Spitze 15,5 MW (Stundensumme), Trasse 14.291 m, Freifläche 80.000 m². Alle anderen Annahmen wie Netz klein
(`docs/eingangsparameter.md` zeigt beide nebeneinander). Kollektor 276 €/m² Brutto (KWW, Klasse ≥ 15.000 m²
Apertur), Trasse 1.140/640 €/m (KWW, größere Rohre), Luft-WP nach KWW-Gütegrad, Speicher mit Kennlinie (E34–E36).

## Stand 14.11.2026 nach E39 (neues Speichermodell)

Geändert wie Netz klein (`docs/ergebnisse.md`, E39). **Die Abschnitte ab „Basislauf im Vergleich alt“ (Heatmap,
weitere Tabellen) sind noch mit dem alten Speicher gerechnet.** Ergebnisordner
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

## Vergleichsvarianten (`uv run serts varianten --netz gross`)

| | Basis | ohne Speicher | nur WP + PtH | mit BEW Modul 2 (optimiert) | Gas-Fernwärme |
|---|---|---|---|---|---|
| Kollektor / Speicher | 28.400 m² / 38.900 m³ | 11.600 m² / – | – | 28.750 m² / 36.780 m³ | – |
| Solaranteil / EE-Anteil | 30 % / 84 % | 9 % / 80 % | 0 % / 79 % | 31 % / 84 % | 0 |
| CO₂ [t/a] | 6.180 | 7.600 | 8.250 | 6.100 | 10.200 |
| LCOH Erzeugung [€/MWh] | 158,8 | 172,0 | 177,3 | 142,1 | 165,3 |
| Wärmepreis inkl. Netz [€/MWh] | **228,9** | 243,8 | 249,8 | **200,1** | **236,2** |

## Heatmaps (`uv run serts heatmap --netz gross`, ≈ 40 min)

`heatmap_alle.png` im Ergebnisordner (neun Kennzahlen). Wärmepreis inkl. Netz [€/MWh], Gas-Fernwärme 236:

| V \ A [m²] | 5.000 | 10.000 | 15.000 | 20.000 | 25.000 | 30.000 |
|---|---|---|---|---|---|---|
| 0 m³ | 246 | 244 | 244 | 245 | 247 | 249 |
| 5.000 m³ | 244 | 240 | 237 | 235 | 235 | 235 |
| 10.000 m³ | 244 | 240 | 237 | 234 | 234 | 235 |
| 20.000 m³ | 245 | 240 | 237 | 234 | 232 | 232 |
| 35.000 m³ | 247 | 241 | 237 | 233 | 231 | – |
| 50.000 m³ | 250 | 242 | 238 | 233 | **230** | – |

* Erst ab ≈ 20.000 m² Kollektor ist das System günstiger als Gas-Fernwärme; das Optimum liegt am Flächenrand
  (25.000–30.000 m², 20.000–50.000 m³) – **mehr Fläche würde helfen**.
* Saisonaler Betrieb (≤ 1 Zyklus, > 90 % Winteranteil) nur bei großem Speicher mit wenig Kollektor (5.000–10.000 m²
  mit ≥ 20.000 m³, 15.000 m² mit ≥ 35.000 m³) – dort teurer als Gas. Am günstigsten Rasterpunkt (25.000 m²,
  35.000–50.000 m³): 1,6–2,3 Zyklen, 44–62 % Winteranteil – auf dem Weg zum Saisonspeicher.
* Ohne Speicher hilft mehr Kollektor nicht (244–249 €/MWh, PtH ≈ 1.900 MWh/a).

**Ohne Flächengrenze (Abschätzung aus der Heatmap, kein Lauf):** Bei 25.000 m² wird es mit mehr Speicher noch
billiger (232 → 230 €/MWh von 20.000 auf 50.000 m³), +5.000 m² Kollektor bringen −5, dann −3 €/MWh. Geschätztes
Optimum ≈ 35.000–40.000 m² / 60.000–90.000 m³ (≈ 12–14 ha statt 8 ha), Wärmepreis ≈ 225–227 €/MWh (**−2 bis
−4 €/MWh**), Solaranteil ≈ 35–40 %, Speicher deutlich saisonaler (< 1,5 Zyklen, > 60 % Winteranteil). Obergrenze,
denn Fläche kostet im Modell nichts; schon eine geringe Pacht zehrt den Vorteil auf.

## Lesart

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

- Sensitivitäten (Tornado) für das große Netz: `uv run serts tornado --netz gross` (≈ 1–2 h, nicht gelaufen).
- Mehr Fläche, andere Aufteilung der Fläche, Ankerkunde: Szenario mit `standort.flaeche_verfuegbar`.
- Hausanschlüsse: pauschal 10.000 € wie im kleinen Netz; bei 54 % Nichtwohngebäuden eher oberes Ende (E32).
