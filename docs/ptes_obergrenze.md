# Wie groß kann das PTES werden? (Fläche 13.000 m², Normaljahr)

Rechnung mit `config/base.yaml`: Fläche 13.000 m², Kollektor-Grundfläche 2,3 m² je m² Kollektor (BSW),
Speicher-Grundfläche aus Dronninglund-Geometrie (Pyramidenstumpf, 5 m Randstreifen), Speicherkapazität
0,0872 MWh/m³ (75 K). Reproduzierbar mit dem Code in der Sitzung vom 09.11.2026.

## Obergrenzen

| Betrachtung | Ergebnis |
|---|---|
| Nur Speicher, kein Kollektor (rechnerisch, sinnlos) | Modell (feste 2,65 m³ je m² Grund): **≈ 34.500 m³**; Geometrie ähnlich Dronninglund: ≈ 90.000 m³ bei 18 m Tiefe (DRL: 16 m) |
| Nur Kollektoren, kein Speicher | **≈ 5.650 m²** → ≈ 3.000 MWh/a Solarwärme (≈ 55 % des Bedarfs, aber zur falschen Jahreszeit) |
| Kollektor 4.000 m² + Speicher | Speicher max. **≈ 11.300 m³** (Geometrie) bzw. 10.100 m³ (Modell) |
| Kollektor 3.000 m² + Speicher | max. ≈ 26.000 m³ (Geometrie) bzw. 16.200 m³ (Modell) |
| Sinnvolles Verhältnis V/A = 1,6 / 2,5 / 3,3 m³ je m² (DRL / Bracht / Basis 12.000 m³) | A ≈ 4.380 / 4.090 / 3.880 m², **V ≈ 7.000 / 10.200 / 12.800 m³** |

**Praktische Obergrenze: ≈ 10.000–13.000 m³** mit 3.900–4.400 m² Kollektor. Darüber hinaus fehlt dem Speicher
die Solarwärme zum Füllen: 3.900 m² liefern ≈ 2.100 MWh/a, ein 13.000-m³-Speicher fasst ≈ 1.130 MWh – das sind
schon ≈ 2 Zyklen pro Jahr. Ein größerer Speicher wäre nur mit mehr Kollektorfläche (die dann fehlt) oder einer
anderen Wärmequelle (z. B. Abwärme, PV-WP im Sommer) sinnvoll.

## Hinweis zum Modell

Das Modell nutzt eine **konstante** Speicher-Grundfläche von 2,65 m³ je m² (abgeleitet bei ≈ 8.700 m³).
Bei größeren Becken ist das Verhältnis besser (V^(1/3)): 3,1 m³/m² bei 12.000 m³, 4,5 m³/m² bei 30.000 m³.
Für den Lauf mit 12.000 m³ rechnet das Modell daher ≈ 600 m² Grundfläche zu viel für den Speicher; das Optimum
läge mit der Geometrie-Skalierung bei ≈ 3.950 statt 3.680 m² Kollektor. Der Effekt ist klein (≈ 7 %); bei Bedarf
lässt sich `ptes.volumen_je_grundflaeche` auf ≈ 3,0 setzen (Szenario) oder die Fläche größenabhängig machen.

## Weitere Grenzen, die das Modell nicht kennt

Grundwasserstand, Bodenbeschaffenheit, maximale Beckentiefe, Liner-/Deckelkosten bei sehr großen Becken,
Verfügbarkeit von Abraumflächen und Genehmigung (Wasserrecht). Die Fläche ist daher eine **obere** Schranke.
