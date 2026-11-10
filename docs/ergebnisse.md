# Ergebnisse Netz klein (Stand 10.11.2026, nach E32–E37)

Vorläufig: Kollektorkennwerte und mehrere Kosten sind Annahmen (`docs/annahmen.md`, Übersicht:
`docs/eingangsparameter.md`). Basis: Normaljahr (PVGIS-TMY), Lastgang/Temperatur 2022, Vorlauf 80 °C, **Zins real 5 %**,
10 % Nebenkosten, fester Strompreis 30 ct/kWh, VDI 2067-1 real, **Kosten für Kollektor, Speicher und Trasse aus dem
KWW Technikkatalog 2026** (E32), **Luft-WP nach KWW-Gütegrad** (E35), Speicher mit **Temperaturkennlinie** und
konsistenter Schichtung (E34, E36). Großes Netz: **`docs/ergebnisse_netz_gross.md`**. Prüfung der Auslegung gegen die
Leitfrage: **`docs/kernfragen.md`**.

## Basislauf (`uv run serts run`)

| Kennzahl | Wert |
|---|---|
| Kollektor / Speicher | **≈ 3.680 m² / ≈ 4.560 m³** (Fläche 10.200 von 13.000 m²) |
| Wärmepumpe / PtH (Reserve) | 1,03 MW / 1,59 MW (PtH liefert ≈ 77 MWh/a, v. a. im Februar) |
| Arbeitszahl WP gesamt (Luft + Speicher) | 2,53 |
| Speicher | Wirkungsgrad 94 %, 2,9 Zyklen/a, 36 % der Entladung Nov–Mär, **gemischt** |
| Wärmeherkunft (5.462 MWh/a) | Luft-WP 3.230, Speicher-WP 1.190, Speicher direkt 235, Solar direkt ≈ 720, PtH 77 MWh |
| Solaranteil (direkt / Speicher direkt / WP-Quellwärme) | **35 %** (13 / 4 / 17 %) |
| LCOH Erzeugung (Gas-Referenz 165) | **≈ 153 €/MWh** |
| Wärmepreis beim Kunden inkl. Netz (Gas-Fernwärme 261) | **≈ 247 €/MWh** (−6 %) |
| davon Wärmenetz | Trasse ≈ 26 €/MWh, Hausanschlüsse + Übergabestationen ≈ 36 €/MWh |
| **mit BEW Modul 2** (40 %, gleiche Auslegung; Obergrenze) | LCOH ≈ 136, **inkl. Netz ≈ 218 €/MWh** (−17 % ggü. Gas), Zuschuss ≤ 1,8 Mio. € |
| EE-Anteil / CO₂ (Gas-Referenz 1.160 t/a) | 85 % / ≈ 660 t/a |

**Kostensegmente** (LCOH, V, A): 0–1.000 m³ 154,4; 1.000–2.500 m³ 153,2; **2.500–6.000 m³ 152,9 (4.560 m³)**;
6.000–12.000 m³ 153,0 (7.410 m³, 41 % Solar); 12.000–35.000 m³ 159,4 €/MWh – das Optimum ist flach (2.500–12.000 m³
innerhalb 0,1 €/MWh).

**Betrieb über das Jahr** (`1_jahresverlauf.png`): Der Speicher wird Juli–Oktober mit Solarwärme geladen (bis 85 °C),
im November/Dezember gehalten und im Januar zuerst direkt (Oberschicht noch ≈ 83–85 °C), danach im Februar/März
über die Speicher-WP bis 10 °C entladen; März–Juni ist er praktisch leer. Direktentladung gibt es nur bei dicker
heißer Schicht (`kennlinie_rest_MWh` = 0). Die Speicher-WP läuft auch im Sommer: dort nutzt sie den kalten Teil
(10–45 °C), der beim Laden zwangsläufig mitgefüllt wird.

## Was die Änderungen vom 10.11. bewirkt haben (Netz klein)

| Stand | Kollektor / Speicher | LCOH | Wärmepreis inkl. Netz / Gas | Solar | Winteranteil |
|---|---|---|---|---|---|
| vorher (E31) | 2.540 m² / 1.640 m³ | 141,2 | 229 / 257 | 24 % | 28 % |
| + KWW-Kosten Kollektor, PTES, Trasse (E32) | 4.500 / 7.010 | 131,8 | 221 / 261 | 42 % | 47 % |
| + Kennlinie, Schichtung, Luft-WP nach KWW (E34–E36) = **Basis** | 3.680 / 4.560 | 152,9 | 247 / 261 | 35 % | 36 % |
| Varianten (`serts varianten`) | siehe unten | | | | |

Der größte Sprung (+21 €/MWh) kommt von der realistischeren Luft-WP (Arbeitszahl 2,65 → 2,22, E35); die Kennlinie
macht den Speicher kleiner, weil nur die heiße Schicht direkt nutzbar ist.

## Vergleichsvarianten (`uv run serts varianten`, Briefing Pflicht 5)

| | Basis | ohne Speicher | nur WP + PtH | mit BEW Modul 2 (optimiert) | Gas-Fernwärme |
|---|---|---|---|---|---|
| Kollektor / Speicher | 3.680 m² / 4.560 m³ | 1.240 m² / – | – | 4.440 m² / 7.420 m³ | – |
| Solaranteil / EE-Anteil | 35 % / 85 % | 9 % / 81 % | 0 % / 79 % | 41 % / 86 % | 0 |
| CO₂ [t/a] | 660 | 840 | 920 | 600 | 1.160 |
| LCOH Erzeugung [€/MWh] | 152,9 | 161,3 | 166,3 | 133,3 | 164,9 |
| Wärmepreis inkl. Netz [€/MWh] | **246,9** | 257,0 | 263,1 | **214,3** | **261,4** |
| dito mit BEW, gleiche Auslegung | 217,8 | 236,4 | 245,1 | 214,3 | – |

* **Solar + Speicher lohnt sich**: gegenüber reiner WP + PtH −16 €/MWh, gegenüber Solar ohne Speicher −10 €/MWh.
* **Mit BEW Modul 2** wird optimal mehr gebaut (7.400 m³, 41 % Solar), Wärmepreis ≈ 214 €/MWh (−18 % ggü. Gas).
  40 % ist die Obergrenze; die BAFA begrenzt auf die Wirtschaftlichkeitslücke (E37).
* `pareto.png` im Ergebnisordner zeigt EE-Anteil gegen Wärmepreis.

> **Die folgenden Abschnitte (Strom, Sensitivitäten) sind Stand vor E32–E37** (alte Kosten, Luft-WP nach Lorenz, ohne Kennlinie) – Tornado wird neu gerechnet und hier ersetzt.

## Strom: fest gegen Day-Ahead (zwei Läufe, Szenarien `strom_day_ahead_*`)

Preis(t) = Day-Ahead(t) + Marge 25 + Netzentgelt 93 + Abgaben 57 €/MWh; Preisjahr unabhängig vom Wetterjahr 2022.

| | fest 30 ct | Day-Ahead 2024 | Day-Ahead 2024 normiert (Ø wie fest) | Day-Ahead 2022 (Krise) |
|---|---|---|---|---|
| Strompreis Ø / gewichtet bezahlt [€/MWh] | 300 / 300 | 254 / 253 | 300 / 293 | 410 / 341 |
| Kollektor / Speicher | 2.540 m² / 1.640 m³ | 1.240 / 420 | 2.950 / 3.730 | 4.460 / 7.290 |
| Speicher-Zyklen | 5,0 | 12,5 | 3,6 | 2,7 |
| Solaranteil | 24 % | 12 % | 28 % | 42 % |
| Strombezug [MWh/a] | 1.645 | 1.927 | 1.594 | 1.367 |
| LCOH Erzeugung / inkl. Netz [€/MWh] | 141 / 229 | **127 / 211** | 142 / 229 | 157 / 247 |

* **Preisniveau** bestimmt das System: bei billigem Strom (2024) schrumpft Solar; bei teurem (2022) wächst es und der
  Speicher wird größer.
* **Zeitliche Struktur** allein (normiert) senkt den bezahlten Preis nur um 2 % (293 statt 300), die LCOH bleibt
  gleich (141,5): Das Modell kann Preisspitzen kaum ausnutzen, weil der Speicher nur Solarwärme speichert (WP lädt den
  Speicher nicht, E29). Im Krisenjahr 2022 mit starken Preisschwankungen zahlt das flexible System 17 % unter dem Mittel.
* Nicht modelliert: Leistungspreis; Korrelation Preis↔Wetter (Preis- und Wetterjahr verschieden).

## Sensitivitäten (`uv run serts tornado`, 45 Varianten, Größen jeweils neu optimiert)

Wärmepreis inkl. Netz (Basis 229 €/MWh) und Vorteil gegenüber Gas-Fernwärme (Basis +24 €/MWh):

| Parameter (Variante) | Wärmepreis inkl. Netz | Vorteil ggü. Gas |
|---|---|---|
| Gaspreis 8 / 16 ct/kWh | – | **−23 / +70** |
| Strompreis 20 / 40 ct/kWh | 186 / 261 | +59 / **−3** (dann Solar 42 %, 7.170 m³) |
| CO₂-Preis 55 / 200 €/t | – | +14 / +45 |
| Förderung BEW 40 % (nur förderfähige Teile) | 196 | **+45** (Optimum: 4.480 m², 7.170 m³, Solar 42 %) |
| Gütegrad Luft-WP 0,45 / 0,6 | 239 / 210 | +15 / +39 |
| Zins 3 / 7 % (real) | 207 / 248 | +32 / +17 |
| Nebenkosten 0 / 20 % | 218 / 239 | +28 / +20 |
| WP-Kosten 0,7 / 1,4 Mio. €/MW | 220 / 240 | +31 / +15 |
| Strompreis +2 %/a real | 247 | +9 |
| Kollektor 300 / 550 €/m² | 217 / 232 | +33 / +21 |
| Speicherkosten × 0,7 / × 1,3 | 226 / 230 | +26 / +23 |
| Hausanschluss 5.000 / 15.000 € | 211 / 247 | unverändert (gleiches Netz) |
| Trasse Straße 400 / 800 €/m; Anteil Straße 50/100 % | 223–238 | unverändert |
| Luft-WP-Leistung bei −7 °C: 60 / 100 % | 229 / 229 | 24 / 24 |

**Lesart:** Ob das System günstiger ist als Gas-Fernwärme, entscheiden **Gas- und Strompreis** (CO₂-Preis,
Förderung, Zins). Die Größe von Kollektorfeld und Speicher springt mit den Kosten (Solaranteil 10–42 %; Speicher
90–7.300 m³), ohne dass die Kosten stark reagieren. Der Wärmepreis beim Kunden wird zu ≈ 25 % vom Wärmenetz
bestimmt (≈ 58 €/MWh, vor allem Hausanschlüsse).

**Kernaussage (vorläufig):** Wärmepumpe (Luft + Speicher) mit PtH-Reserve ist unter den Basisannahmen günstiger als
Gas-Fernwärme (≈ −11 %). Ein kleiner Speicher (≈ 1.600 m³) mit ≈ 2.500 m² Kollektor ist kostenoptimal; ein saisonaler
Großspeicher lohnt sich erst mit deutlich billigeren Speichern (≈ halbe Kosten), mehr Fläche oder BEW-Förderung.
