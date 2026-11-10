# Wie der Speicher im Modell funktioniert (zwei Teile) – und was drei Schichten kosten würden

## 1 Zwei Teile = zwei Temperaturbänder, nicht zwei Becken

Der Speicher ist ein Wasservolumen V. Gezählt wird Energie **bezogen auf 10 °C** (T_unten). Diese Energie wird in
zwei Bänder geteilt:

| Teil | Band | Anteil der Kapazität | wer kann ihn leeren? |
|---|---|---|---|
| **heiß** | Wärme zwischen 45 °C (Netz-Rücklauf) und 85 °C | 40 K / 75 K = **53 %** | `entladen_direkt` ins Netz |
| **kalt** | Wärme zwischen 10 °C und 45 °C | 35 K / 75 K = **47 %** | nur die Speicher-WP (Quelle) |

Man kann sich drei Wassertemperaturen vorstellen: oben 85 °C, in der Mitte 45 °C, unten 10 °C.

* **Laden (Solar):** 10-°C-Wasser wird auf 85 °C erwärmt → 1 MWh füllt 0,53 MWh heiß + 0,47 MWh kalt.
* **Direkt entladen:** 85-°C-Wasser geht ins Netz und kommt mit 45 °C zurück → nur der heiße Teil sinkt.
* **Speicher-WP:** kühlt 45-°C-Wasser auf 10 °C ab (COP 4,5) → nur der kalte Teil sinkt.
* **Umlagern:** ist die heiße Schicht zu dünn für das Netz, wird ihr Inhalt dem kalten Teil zugeschlagen
  (das Wasser vermischt sich und ist danach nur noch über die WP nutzbar).

Drei Bedingungen halten das physikalisch:

1. **Größenverhältnis:** kalt = 0,875 × heiß (beide Bänder gehören zu demselben Wasser).
2. **Schichtung (E36):** der kalte Teil ist relativ immer mindestens so voll wie der heiße – heißes Wasser enthält
   seinen 10–45-°C-Anteil immer mit.
3. **Kennlinie (E34):** direkt ins Netz nur, wenn die heiße Schicht dicker ist als die Übergangszone (30 % des
   Volumens). Das ist eine „erst-ab“-Schwelle, die ein lineares Programm nicht direkt kann. Deshalb rechnet das
   Modell **zweimal**: Lauf 1 ohne Schwelle; Lauf 2 erlaubt die Direktentladung nur in den Stunden, in denen sie in
   Lauf 1 bei dicker Schicht lief, und verlangt dort die dicke Schicht als Bedingung.

Die Optimierung (PyPSA/HiGHS) entscheidet für jede der 8.760 Stunden gleichzeitig, wie viel geladen, direkt
entladen, umgelagert und über die WP genutzt wird – mit perfekter Voraussicht über das ganze Jahr. Ziel sind die
geringsten Jahreskosten (Annuitäten + Strom). Die Temperaturen in den Grafiken werden aus den Füllständen
zurückgerechnet (Kennlinie), sie sind kein eigener Rechenwert.

## 2 Kann eine Schicht mit 70–75 °C einspeisen?

Bei **80 °C Vorlauf** nicht direkt: die Entnahme muss mindestens ≈ 85 °C haben (T_VL + 5 K). Wasser mit 70–75 °C
kann aber den **Rücklauf vorwärmen** (45 → ≈ 70 °C); den Rest bis 80 °C liefert dann die WP oder PtH. Außerdem
ist warmes Wasser eine bessere Quelle für die Speicher-WP (höherer COP). Beides fehlt im Zwei-Teile-Modell: Wärme
unter 85 °C ist dort nur über die WP mit festem COP 4,5 nutzbar – **das Modell ist hier eher konservativ**.

## 3 Was drei Schichten kosten würden

| Baustein | Aufwand |
|---|---|
| drittes Band „warm“ (z. B. 45–75 °C) mit Bus, Speicherteil, Größenverhältnis | klein |
| Laden je nach Kollektortemperatur in „warm“ oder „heiß“ (zwei Kollektor-Ausgänge mit eigener Effizienz) | mittel – neue Zeitreihe, mehr Annahmen |
| Vorwärmen: warm → Netz nur zusammen mit Nachheizung (WP/PtH ≥ 5/30 der Vorwärmleistung je Stunde) | klein (eine lineare Bedingung) |
| Speicher-WP aus „warm“ (COP ≈ 6) und aus „kalt“ (COP 4,5) | klein (ein Link) |
| Schichtung warm/heiß/kalt + Kennlinie je Band (zwei Läufe) | mittel |
| Tests, Doku, Notebook | mittel |

**Gesamt ≈ 1–2 Arbeitstage**, Rechenzeit ≈ +30–50 % (der Tornado dauert jetzt schon ≈ 3 h). Mehr Parameter
(Bandgrenze, Kollektorkennlinie je Temperatur), schwerer zu erklären.

**Nutzen abschätzen, bevor man baut:** Der Tornado zeigt die Obergrenze: ohne Kennlinie (ideale Schichtung) wird das
System 11 €/MWh günstiger. Drei Schichten holen davon einen Teil zurück. **Kleiner Zwischenschritt** mit dem
meisten Nutzen für wenig Aufwand: eine zweite Speicher-WP, die direkt aus dem heißen Teil schöpft (Quelle 45–85 °C,
COP ≈ 6) – ein Link, keine neue Schicht. Empfehlung: erst diesen Schritt, drei Schichten nur, wenn das Ergebnis
dann noch deutlich reagiert.
