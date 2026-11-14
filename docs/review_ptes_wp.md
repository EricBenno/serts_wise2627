# Review Modellierung – Schwerpunkt PTES + Wärmepumpe (14.11.2026)

**Stand 14.11.2026 abends:** umgesetzt sind 1.1, 1.2, 1.3, 1.5, 2.1 (Szenario `vl_gleitend`), 2.3, 2.4 und 2.5
(E39 in `entscheidungen.md`, Prüfung in `validierung_dronninglund.md`). Offen: 2.2 und die Punkte in Abschnitt 3.
Der Text unten beschreibt den Stand **vor** der Umsetzung. Grundlage: `network.py`, `constraints.py`, `heatpump.py`, `solar.py`, `base.yaml`,
Basislauf `results/klein/20261110-230658_base_opt` und ein Diagnose-Experiment (unten).

## Kurzfassung

Die Zwei-Teile-Idee (heiß/kalt) ist gut und sollte bleiben. Zwei Details der Umsetzung drücken den Speicher aber
künstlich in die Rolle „Quelle für die WP“ und kosten ≈ 11–14 €/MWh, also mehr als der ganze Vorteil gegenüber
Gas (5 €/MWh). Beide lassen sich ohne zusätzliche Rechenzeit beheben. Die Kernaussage „knapp günstiger als Gas“
hängt damit zurzeit stärker an der Speicherformulierung als an den meisten Tornado-Parametern.

## 1 PTES + WP

### 1.1 Festes Beladeverhältnis 53 : 47 erzwingt WP-Betrieb im Sommer (größtes Problem)

`laden` füllt immer heiß **und** kalt. Der kalte Teil hat aber nur einen Ausgang: die Speicher-WP. Ist er voll
(Speicher unten 45 °C), kann der heiße Teil nicht nachgeladen werden, bis die WP unten Platz schafft. Real pendelt
ein PTES im Sommer zwischen ≈ 45 und 85 °C, ganz ohne WP.

Im Basislauf sichtbar: Mai–September liefert die Speicher-WP 645 MWh, die Direktentladung 66 MWh, im Juni und Juli
0 MWh. Stromverbrauch im Sommer 151 MWh, obwohl Solarwärme übrig ist. Direktanteil der Speicherentladung über das
Jahr 21 % (Dronninglund gemessen 52–63 %).

**Lösung:** `laden` durch zwei Links ersetzen: `laden_kalt` (10 → 45 °C) und `laden_heiss` (45 → 85 °C). Die
vorhandene Schichtungsbedingung (E36: kalter Teil relativ ≥ heißer Teil) sorgt schon dafür, dass nur Wasser auf
85 °C gebracht wird, das 45 °C hat. Ein Link mehr, keine neue Bedingung, eher leichter zu erklären.

### 1.2 Kennlinie über zwei Läufe ist eine Heuristik und sperrt zu viel

Lauf 2 erlaubt Direktentladung nur in Stunden, die Lauf 1 (ohne Kennlinie) zufällig gewählt hat: 3.679 → 1.398
Stunden. Folgen im Basislauf: 1.402 Stunden, in denen die Luft-WP läuft (912 MWh), obwohl die heiße Schicht dick
genug ist; 141 MWh PtH im Februar, die in allen anderen Varianten verschwinden. Das Ergebnis ist zulässig, aber
kein Optimum, und es kostet den zweiten Lauf.

**Lösung (ein Lauf):** Den heißen Teil in **Kern** (70 %) und **Übergangszone** (30 %) teilen, als dritten Store
mit derselben Art Bedingung wie E36: Kern relativ ≤ Übergangszone ≤ kalt. Direkt ins Netz geht nur der Kern, die
Übergangszone über `umlagern` → WP. Das ist die engste lineare Form der Schwelle „erst ab 30 %“ (ihre konvexe
Hülle). Sie ist bei fast leerem Speicher etwas zu großzügig: eine dünne heiße Schicht darf sofort wieder raus.
Für Tag-Nacht-Zyklen ist das eher realistischer als die Schwelle, weil die Übergangszone erst über Wochen wächst.

### 1.3 Wärme über Rücklauftemperatur geht nur über die WP (COP 4,5)

Wasser mit 60–70 °C wird im Modell zu „kalt“ umgebucht und dann mit Strom von 10 °C aus hochgepumpt. Real wärmt es
den Rücklauf vor, WP oder PtH heizen nach. **Lösung:** Link `vorwaermen` (Übergangszone → Netz) mit einer
Bedingung je Stunde: Vorwärmleistung ≤ 0,75 × (WP + PtH), d. h. 45 → 60 °C aus dem Speicher, 60 → 80 °C Nachheizung.
Optional; baut auf 1.2 auf.

### 1.4 Diagnose-Experiment (feste Auslegung 4.437 m² / 7.404 m³, WP und PtH optimiert)

| Variante | LP-Läufe / Zeit | Strom [MWh] | davon Mai–Sep | direkt | über Speicher-WP | PtH | Kosten ggü. heute |
|---|---|---|---|---|---|---|---|
| heute (Kennlinie, 2 Läufe) | 2 / 44 s | 1.723 | 153 | 311 | 1.496 | 141 | – |
| nur 1.1 (Laden getrennt) | 2 / 40 s | 1.679 | 113 | 642 | 1.173 | 149 | −2,6 €/MWh |
| 1.1 + 1.2 | 1 / 39 s | 1.503 | 40 | 1.459 | 425 | 0 | −11,3 €/MWh |
| 1.1 + 1.2 + 1.3 | 1 / 49 s | 1.490 | 45 | 1.196 (+345 vorgewärmt) | 322 | 0 | −13,9 €/MWh |
| zum Vergleich: heute ohne Kennlinie | 1 / 16 s | 1.570 | 103 | 851 | 939 | 0 | −9,0 €/MWh |

Kosten = Strom + WP/PtH-Annuität je MWh Einspeisung, Auslegung nicht neu optimiert (Untergrenze des Effekts).
Skript: nicht im Repo (Scratch), bei Bedarf als Test nachbauen.

**Einordnung:** 1.1 + 1.2 ist vermutlich zu optimistisch: Direktanteil ≈ 80 % statt 52–63 % in Dronninglund. Die
Wahrheit liegt zwischen Zeile 2 und 3. Stellschraube zum Kalibrieren: beim Laden einen festen Anteil (z. B.
10–15 %) in die Übergangszone statt in den Kern buchen (Einschichtverlust, nur eine Effizienz am Link), oder den
Anteil 0,3 anpassen. Dafür das vorhandene Szenario `validierung_dronninglund` um den Direktanteil ergänzen.

### 1.5 Parameter, die für kleine Speicher nicht passen

* **Verlustrate größenunabhängig**, obwohl V von 1.000 bis 35.000 m³ optimiert wird. Das bevorzugt kleine
  Speicher. 93 % Wirkungsgrad bei 7.400 m³ ist optimistisch. **Lösung:** je Kostensegment (ohnehin eigener Lauf)
  `verlustrate · (V_mitte / 60.000)^(−1/3)` setzen; bei festem V exakt. Null Rechenaufwand.
* **Übergangszone 0,3** stammt aus 5 m bei 16 m Tiefe. Die Dicke ist eine Länge, kein Anteil: bei ≈ 8 m Tiefe wären
  es ≈ 0,6. Ebenfalls je Segment aus der Tiefe ableiten. Die 5 m selbst sind laut Config ungeprüft.
* **T_oben = T_VL + 5 K = 85 °C**, also null Reserve. Im Bandmodell bleibt heißes Wasser immer 85 °C (Verluste
  kosten Menge, nicht Temperatur). Real fällt die Oberschicht nach Tagen darunter. Abhilfe: 1.3 (Vorwärmen), oder
  T_oben 90 °C, oder gleitender Vorlauf (2.1).

## 2 Weit von der Realität, aber leicht zu beheben

1. **Vorlauf ganzjährig 80 °C.** Üblich ist gleitend (z. B. 80 °C bei −10 °C, 70 °C ab ≈ 10 °C). `cop_kww` nimmt
   schon Zeitreihen; das ist reine Vorverarbeitung. Wirkt auf die Luft-WP-Arbeitszahl, und deren Gütegrad ±15 %
   entscheidet laut Tornado über den Gasvergleich. Ist Teamvorgabe, daher als Szenario.
2. **Kollektor nur bei T_m 67,5 °C.** Mit getrennten Ladelinks (1.1) kann das Feld den kalten Teil bei T_m ≈ 30 °C
   laden; bei 400 W/m² und 5 °C ist der Wirkungsgrad dann ≈ 0,65 statt ≈ 0,31. Braucht eine zweite Zeitreihe und
   eine Flächenbedingung je Stunde (+8.760 Zeilen). Mittlerer Aufwand, erst nach 1.1–1.2.
3. **Kein Einfallswinkel-Korrekturfaktor.** Reine Vorverarbeitung mit pvlib, kostet nichts, senkt den Ertrag
   morgens/abends um einige Prozent.
4. **Kein Leistungspreis Strom**, obwohl PtH = Spitzenlast gebaut wird. Eine Variable „höchster Bezug“ plus eine
   Bedingung je Stunde. Würde auch die PtH-Spitzen im Februar richtig bepreisen.
5. **Day-Ahead-Aussage „Preisstruktur bringt ≈ 1 €/MWh“** ist eine Folge davon, dass die WP den Speicher nicht
   laden darf (E29), kein Befund. Nach 1.1 ist das ein Link (WP → heiß); nur für die Day-Ahead-Szenarien einschalten.

## 3 Struktur und Rechenzeit

* Eine Auslegung = 5 Segmente × 2 Läufe = 10 LPs. Mit 1.2 sind es 5. Im Tornado reichen das Basis-Segment und
  seine Nachbarn (Optimum ist flach), das spart weitere ≈ 40 %.
* Luft- und Speicher-WP teilen sich eine Leistung zum Luft-WP-Preis: vertretbar, im Bericht nennen.
* Perfekte Voraussicht (Speicher bleibt im November voll, Luft-WP liefert 539 von 595 MWh) ist eine echte
  Modellgrenze und steht schon in `modellgrenzen.md`.
* `ergebnisse.md` ist uneinheitlich: Kernaussage nennt noch ≈ 4.600 m³ / 3 Zyklen (Basis: 7.400 m³ / 2,3), Tornado
  noch mit WP 1.000 €/kW.

## 4 Empfohlene Reihenfolge

1. 1.1 und 1.2 zusammen (ersetzt `laden`, `umlagern`-Logik und den zweiten Lauf; je ein Mini-Netz-Test).
2. 1.5 Verlustrate und Übergangszone je Segment.
3. Gegen Dronninglund kalibrieren (Direktanteil), dann Basis, Varianten und Tornado neu rechnen.
4. Optional: 1.3, 2.1, 2.3, 2.4. Erst danach über 2.2 entscheiden.
