# Wie der Speicher im Modell funktioniert (drei Teile)

Stand 14.11.2026 (E39). Geprüft gegen Dronninglund: `docs/validierung_dronninglund.md`.

## 1 Drei Teile = drei Sorten Wärme in demselben Wasser

Der Speicher ist ein Wasservolumen V. Gezählt wird Energie **bezogen auf 10 °C** (T_unten). Diese Energie wird in
drei Teile sortiert (Zahlen für 80/45 °C Netz und ≈ 7.400 m³):

| Teil | was ist das? | Anteil der Kapazität | wie kommt die Wärme heraus? |
|---|---|---|---|
| **heißer Kern** | Wärme über 45 °C in richtig heißem Wasser (85 °C, oben) | 53 % × 70 % = 37 % | `entladen_direkt` ins Netz |
| **Übergangszone** | Wärme über 45 °C im Mischwasser zwischen heiß und kalt (≈ 65 °C) | 53 % × 30 % = 16 % | `vorwaermen` (Rücklauf auf ≈ 60 °C, WP/PtH heizen nach) oder `umlagern` → WP |
| **kalt** | Wärme zwischen 10 °C und 45 °C (Rücklauf) | 47 % | nur die Speicher-WP (Quelle, COP 4,5) |

* **Laden kalt** (`laden_kalt`): Wasser wird von 10 °C auf 45 °C erwärmt.
* **Laden heiß** (`laden_heiss`): Wasser mit 45 °C wird auf 85 °C erwärmt. Ist der kalte Teil voll (Speicher unten
  auf Rücklauftemperatur, im Sommer normal), wird nur noch heiß geladen und entladen: der Speicher pendelt zwischen
  45 und 85 °C, ganz ohne Wärmepumpe.
* **Direkt entladen:** 85-°C-Wasser geht ins Netz und kommt mit 45 °C zurück → nur der Kern sinkt.
* **Vorwärmen:** Mischwasser hebt den Rücklauf von 45 auf ≈ 60 °C; die restlichen 20 K liefert in derselben Stunde
  die WP oder PtH (je MW Nachheizung höchstens 0,75 MW Vorwärmen).
* **Speicher-WP:** kühlt 45-°C-Wasser auf 10 °C ab → nur der kalte Teil sinkt.
* **Mischen** (`abbau` Kern → Übergangszone, `umlagern` Übergangszone → kalt): heißes Wasser wird zu Mischwasser,
  Mischwasser kühlt unter 45 °C. Keine Energie geht verloren, aber sie wird weniger wert.

Zwei Bedingungen halten das physikalisch (`constraints.py`):

1. **Größenverhältnis:** die drei Teile gehören zu demselben Wasser und wachsen gemeinsam.
2. **Schichtung:** Füllstand Kern ≤ Füllstand Übergangszone ≤ Füllstand kalt (jeweils Inhalt / Kapazität), in jeder
   Stunde. Heißes Wasser liegt immer auf seiner Übergangszone, und jedes Wasser über 45 °C enthält seinen
   10–45-°C-Anteil. Folge: von einem vollen heißen Teil gehen höchstens 70 % direkt ins Netz, der Rest ist Mischwasser.

Die Optimierung (PyPSA/HiGHS) entscheidet für jede der 8.760 Stunden gleichzeitig, wie viel geladen, direkt
entladen, vorgewärmt und über die WP genutzt wird – mit perfekter Voraussicht über das ganze Jahr, in **einem**
Lauf. Die Temperaturen in den Grafiken werden aus den Füllständen zurückgerechnet, sie sind kein eigener Rechenwert.

## 2 Kleine Speicher sind schlechter

Zwei Größen hängen von der Speichergröße ab (`ptes.groessen_exponent` = −1/3, Bezug Dronninglund 60.000 m³):

| Volumen | Verlust je Stunde (vom Inhalt) | Übergangszone (Anteil am heißen Teil) |
|---|---|---|
| 60.000 m³ | 4,0 · 10⁻⁵ | 15 % (Messdaten Dronninglund 2014) |
| 23.500 m³ | 5,5 · 10⁻⁵ | 21 % |
| 7.400 m³ | 8,0 · 10⁻⁵ | 30 % |
| 1.750 m³ | 13 · 10⁻⁵ | 49 % |

Grund: kleine Speicher haben je m³ mehr Oberfläche (Verluste) und sind flacher; die Übergangszone ist aber eine
Dicke in Metern. Wird das Volumen optimiert, gilt je Kostensegment der Wert der Untergrenze (vorsichtig; im ersten Segment die Mitte).

## 3 Was das Modell nicht kann

* Heißes Wasser bleibt 85 °C; Verluste verringern die Menge, nicht die Temperatur. Da das Netz 85 °C braucht
  (80 °C + 5 K), gibt es keine Reserve – die Direktentladung ist eher optimistisch.
* Die Übergangszone ist ein fester Anteil. In Dronninglund ist sie bei vollem Speicher kleiner (5–13 %) und beim
  Entladen größer (bis 33 %).
* Bei fast leerem Speicher darf eine dünne heiße Schicht sofort wieder direkt entladen werden. Für Tag-Nacht-Zyklen
  passt das, für lange Standzeiten ist es zu großzügig.
* Der Kollektor liefert immer bei 67,5 °C mittlerer Temperatur, auch wenn er nur den kalten Teil lädt (dort wäre
  der Ertrag höher).

## 4 Vorher (bis 10.11.2026) und warum geändert

Vorher: zwei Teile, Laden immer im Verhältnis 53 : 47, Direktentladung erst ab 30 % Füllstand des heißen Teils,
gelöst mit zwei Läufen. Probleme (`docs/review_ptes_wp.md`): Im Sommer musste die Speicher-WP laufen, damit
nachgeladen werden konnte (Mai–September 645 MWh über die WP, 66 MWh direkt); die Zwei-Lauf-Lösung sperrte mehr
Stunden als nötig; Wasser mit 60–70 °C ging nur über die WP. Direktanteil der Speicherentladung 21 %, in
Dronninglund gemessen 52–63 %.
