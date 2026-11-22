# Speichermodell gegen Dronninglund geprüft (14.11.2026)

Zwei Prüfungen: (1) Messdaten 2014 für die Struktur des Speichers, (2) Nachrechnung der Jahreswerte 2015–2017.

## 1 Messdaten 2014: Temperaturprofil im Speicher

Quelle: `../DronninglundData-main/data/Dronninglund_treated_data_and_flow_rates_2014.csv` (PitStorages/
DronninglundData, 32 Temperaturfühler alle 0,5 m, 10-Minuten-Werte; 2014 ist das Anfahrjahr, Start bei 14 °C).
Auswertung: Stundenmittel, Schichtvolumen aus dem Pyramidenstumpf (26 m unten, 90 m oben, 16 m tief), Wärme je
Schicht in die Modell-Teile sortiert mit den Temperaturen von Dronninglund (10 / 40 / 85 °C):
kalt = Wärme unter 40 °C, heißer Teil = Wärme über 40 °C, davon „Kern“ = Wasser ab 75 bzw. 80 °C, Rest = Übergangszone.

| Befund (Füllstände = Inhalt / Kapazität des Teils) | Wert | Folge fürs Modell |
|---|---|---|
| Kalter Teil relativ mindestens so voll wie der heiße Teil | in 100 % der Stunden | Schichtungsbedingung (E36) stimmt |
| Kalter Teil von Mai bis Oktober | durchgehend voll (unten 40–52 °C) | Sommerbetrieb pendelt nur im heißen Teil, ohne WP → getrennte Ladelinks (E39) |
| Wärme der Übergangszone, bezogen auf die Kapazität des heißen Teils (wenn ein Kern da ist) | Median 12 % (75 °C) bzw. 16 % (80 °C), P10–P90: 5–30 % | `ptes.uebergang_ref` = 0,15 (vorher 0,3, ungeprüft) |
| Übergangszone bei vollem Speicher (Aug/Sep) / beim Entladen (Nov) | 5–13 % / 27–33 % | ein fester Anteil ist eine Näherung; 0,15 liegt dazwischen |
| alte Schwelle „Kern erst ab 30 % Füllstand“ | nur in 34–55 % der Stunden erfüllt | zu streng |
| neue Bedingung „Kern relativ ≤ Übergangszone“ mit 0,15 | in 67–81 % der Stunden erfüllt | bei fast leerem Speicher zu großzügig, bei vollem zu streng |

## 2 Nachrechnung 2015–2017 (Szenario `validierung_dronninglund`)

```bash
uv run serts run --szenario validierung_dronninglund --A 37573 --V 60000
```

Kein Nachbau der Anlage: Wetter und Lastprofil von Bad Lippspringe, skaliert auf Wärme ans Netz ≈ 36.500 MWh/a
und Einstrahlung ≈ 1.060 kWh/m²; Rücklauf 40 °C; keine Luft-WP; Absorptions-WP als WP mit COP 1,7. Geprüft wird
nur der Speicher. Zielwerte: `data/reference/dronninglund_solites2019_jahr.csv` (Solites 2019).

| Kennzahl | Messung 2015–2017 | Modell, WP wie vorhanden (ohne Invest) | Modell, WP-Größe kostenoptimiert |
|---|---|---|---|
| Beladung [MWh] | 11.120–12.760 | 11.660 | 10.570 |
| Entladung [MWh] | 10.716–11.983 | 11.210 | 9.990 |
| WP-Quellwärme aus dem Speicher [MWh] | 4.019–5.398 | 4.330 | 1.800 |
| Direktanteil der Entladung | 52–63 % | **61 %** | 82 % |
| Verluste [MWh] | 388–1.275 | 454 | 578 |
| Speicherwirkungsgrad | 90–96 % | 96 % | 95 % |
| Zyklen | 1,9–2,2 | 2,1 | 1,9 |
| Solaranteil | 38–41 % | 39 % | 39 % |

Mit der vorhandenen WP (Spalte 2, WP-Kosten ≈ 0; seit E41 `waermepumpe.kosten_spez_speicher`) liegen alle Jahreswerte in der gemessenen
Spanne. Wird die WP-Größe im Modell nach Kosten gewählt, baut es eine viel kleinere WP als in Dronninglund
(dort 4,7 MW) und nutzt den kalten Teil weniger; das ist eine Folge der Kostenannahmen, kein Speicherfehler.

**Einschichtanteil** (`ptes.einschicht_anteil`): 0 / 0,15 / 0,3 ergeben 61 / 60 / 58 % Direktanteil. Der Wert 0
trifft die Messung schon, deshalb bleibt er 0 (Parameter für Sensitivität vorhanden).

**Grenzen des Vergleichs:** Monatsverlauf weicht ab (das Modell leert den Speicher schon im November/Dezember
ganz, gemessen sind im Dezember/Januar noch 500–1.300 MWh): perfekte Voraussicht und fremdes Wetter/Lastprofil.
In Dronninglund zählt alles, was nicht direkt ins Netz geht, als WP-Quellwärme; deshalb ist Vorwärmen im
Szenario aus.

**Seit E41 (21.11.2026):** Das Szenario setzt `waermepumpe.cop_ansatz_speicher: fest` (Absorptions-WP,
COP 1,7). Die Durchflussgrenze stammt aus denselben Messdaten (565 m³/h) und bindet in der Nachrechnung
per Konstruktion höchstens in den Spitzenstunden. Nicht neu gerechnet.
