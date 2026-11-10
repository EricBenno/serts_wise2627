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

> **Der folgende Abschnitt Strom ist Stand vor E32–E37** (alte Kosten, Luft-WP nach Lorenz, ohne Kennlinie); die Aussagen zur Wirkung des Preisniveaus gelten qualitativ weiter, die Zahlen nicht.

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

## Sensitivitäten (`uv run serts tornado`, 48 Varianten, Stand E37, Größen jeweils neu optimiert)

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
