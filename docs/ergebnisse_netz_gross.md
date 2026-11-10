# Ergebnisse Netz groß (Stand 10.11.2026, nach E32–E37)

Netzfall `gross` (`config/netze/gross.yaml`, Aufruf `uv run serts run --netz gross`, Ergebnisse in `results/gross/`):
877 Gebäude, davon 54 % der Wärme in Nichtwohngebäuden (GMK/GKO), 42.782 MWh/a Gebäude + 5.440 MWh/a Netzverluste,
Spitze 15,5 MW (Stundensumme), Trasse 14.291 m, Freifläche 80.000 m². Alle anderen Annahmen wie Netz klein
(`docs/eingangsparameter.md` zeigt beide nebeneinander). Kollektor 276 €/m² Brutto (KWW, Klasse ≥ 15.000 m²
Apertur), Trasse 1.140/640 €/m (KWW, größere Rohre), Luft-WP nach KWW-Gütegrad, Speicher mit Kennlinie (E34–E36).

## Basislauf im Vergleich

| Kennzahl | Netz groß | Netz klein |
|---|---|---|
| Kollektor / Speicher | **28.760 m² / 36.730 m³** | 3.680 m² / 4.560 m³ |
| Fläche belegt / verfügbar | **80.000 / 80.000 m² (Grenze bindet)** | 10.200 / 13.000 m² |
| Wärmepumpe / PtH | 9,4 MW / 15,5 MW (PtH liefert 730 MWh/a) | 1,03 / 1,59 MW (77 MWh/a) |
| Kollektorertrag | 15.330 MWh/a (533 kWh/m²) | 1.960 MWh/a |
| Strombezug / Arbeitszahl WP | 16.820 MWh/a / 2,45 | 1.820 MWh/a / 2,53 |
| Speicher: Zyklen / Winteranteil / Charakter | 2,7 / 38 % / gemischt | 2,9 / 36 % / gemischt |
| Spez. Speicherkosten (Kostenkurve KWW) | 76 €/m³ | 128 €/m³ |
| LCOH Erzeugung (Gas-Referenz) | **151 €/MWh** (165) | 153 €/MWh (165) |
| Wärmepreis inkl. Netz (Gas-Fernwärme) | **220 €/MWh** (236) | 247 €/MWh (261) |
| davon Trasse / Hausanschlüsse | 28,7 / 21,2 €/MWh | 25,9 / 36,4 €/MWh |
| **mit BEW Modul 2** (gleiche Auslegung, Obergrenze) | **194 €/MWh**, Zuschuss ≤ 15,4 Mio. € | 218 €/MWh, ≤ 1,8 Mio. € |
| Solaranteil / CO₂ (Gas-Referenz) | 31 % / 6.100 t/a (10.200) | 35 % / 660 t/a (1.160) |

**Kostensegmente des Speichers** (LCOH, V, A): 0–2.500 m³ 156,7; 2.500–10.000 m³ 155,5; 10.000–30.000 m³ 151,6;
**30.000–70.000 m³ 150,8 (36.730 m³, 28.760 m²)**; 70.000–130.000 m³ 154,7 €/MWh (70.000 m³, nur 23.300 m² Kollektor).

## Vergleichsvarianten (`uv run serts varianten --netz gross`)

| | Basis | ohne Speicher | nur WP + PtH | mit BEW Modul 2 (optimiert) | Gas-Fernwärme |
|---|---|---|---|---|---|
| Kollektor / Speicher | 28.760 m² / 36.730 m³ | 11.570 m² / – | – | 28.800 m² / 36.460 m³ | – |
| Solaranteil / EE-Anteil | 31 % / 84 % | 9 % / 80 % | 0 % / 79 % | 31 % / 84 % | 0 |
| CO₂ [t/a] | 6.100 | 7.530 | 8.170 | 6.050 | 10.200 |
| LCOH Erzeugung [€/MWh] | 150,8 | 163,7 | 168,9 | 136,6 | 165,3 |
| Wärmepreis inkl. Netz [€/MWh] | **219,9** | 234,5 | 240,3 | **193,9** | **236,2** |

## Lesart

* **Die Fläche begrenzt das System**, nicht die Kosten: Kollektor (2,3 m² Grund je m²) und Speicher (2,65 m³ je m²)
  teilen sich die 8 ha vollständig; mit BEW ändert sich die Auslegung deshalb kaum. Mehr Fläche würde den
  Solaranteil vermutlich erhöhen (nicht gerechnet).
* **Skaleneffekte**: Speicher je m³ 40 % billiger, Hausanschlüsse verteilen sich auf mehr Wärme (49 statt 28 MWh/a je
  Anschluss); die Trasse ist je m teurer (größere Rohre) und je MWh etwa gleich teuer.
* **Wärmepreis beim Kunden** ≈ 220 €/MWh, ≈ 7 % unter Gas-Fernwärme (236); mit BEW ≈ 194 €/MWh (−18 %).
* **PtH** liefert 730 MWh/a (Februar, Kältespitzen bei voll ausgelasteter WP); die 15,5-MW-Reserve (Stundensumme
  aller Gebäude) kostet ≈ 4 €/MWh. Mit Gleichzeitigkeitsfaktor (11,5 MW laut Netzberechnung) wäre sie ≈ 26 % kleiner.
* **Speicher** bleibt ein Mischtyp (2,7 Zyklen, 38 % Winteranteil). Er wird im Januar direkt, im Februar/März über
  die Speicher-WP entleert.

## Szenario `kww_komplett_gross` (auch WP, PtH, Gaskessel, Netz-Lebensdauer aus dem KWW)

Ergebnis noch Stand vor E34–E36 (Luft-WP nach Lorenz, erste Kennlinie): +9 €/MWh gegenüber der damaligen Basis.
Neu rechnen mit `uv run serts run --netz gross --szenario kww_komplett_gross`.

## Offen / nicht gerechnet

- Sensitivitäten (Tornado) für das große Netz: `uv run serts tornado --netz gross` (≈ 1–2 h, nicht gelaufen).
- Mehr Fläche, andere Aufteilung der Fläche, Ankerkunde: Szenario mit `standort.flaeche_verfuegbar`.
- Hausanschlüsse: pauschal 10.000 € wie im kleinen Netz; bei 54 % Nichtwohngebäuden eher oberes Ende (E32).
