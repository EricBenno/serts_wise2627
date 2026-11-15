# Ergebnisse Netz klein (oben Stand 14.11.2026 nach E39, darunter Stand 10.11.2026)

Vorläufig: Kollektorkennwerte und mehrere Kosten sind Annahmen (`docs/annahmen.md`, Übersicht:
`docs/eingangsparameter.md`). Basis: Normaljahr (PVGIS-TMY), Lastgang/Temperatur 2022, Vorlauf 80 °C, **Zins real 5 %**,
10 % Nebenkosten, fester Strompreis 30 ct/kWh, VDI 2067-1 real, **Kosten für Kollektor, Speicher, Trasse und WP
(1.340 €/kW, unteres Ende) aus dem KWW Technikkatalog 2026** (E32, E38), **Luft-WP nach KWW-Gütegrad** (E35),
Speicher in drei Teilen mit Schichtung, Vorwärmen und größenabhängigen Verlusten, Leistungspreis Strom (E39;
vor dem 14.11.: Temperaturkennlinie E34/E36). Großes Netz:
**`docs/ergebnisse_netz_gross.md`**. Prüfung gegen die Leitfrage: **`docs/kernfragen.md`**. Speichermodell
erklärt: `docs/speichermodell.md`.

## Stand 14.11.2026 nach E39 (neues Speichermodell) – Testläufe, Netz klein

Geändert: Speicher in drei Teilen mit getrennten Ladelinks, Vorwärmen, größenabhängige Verluste/Übergangszone,
Leistungspreis Strom, Einfallswinkel am Kollektor (E39; Prüfung `docs/validierung_dronninglund.md`).
Heatmap, Strom-Vergleich und Tornado sind am 15.11. neu gerechnet (unten). **Nur „Basislauf alt“, „Was die
Änderungen vom 10.11. bewirkt haben“ und die alte Variantentabelle zeigen den Stand vor E39** (zum Vergleich).

| Kennzahl | alt (10.11.) | **Basis neu** | gleitender Vorlauf (`vl_gleitend`) | Day-Ahead 2024 (WP/PtH laden Speicher) |
|---|---|---|---|---|
| Kollektor / Speicher | 4.440 m² / 7.400 m³ | **4.670 m² / 6.000 m³** | 4.670 / 6.000 | 4.660 / 6.040 |
| Wärmepumpe | 0,93 MW | 0,95 MW | 0,95 MW | 0,93 MW |
| LCOH Erzeugung (Gas 164,9) | 159,9 | **150,0** | 143,3 | 130,6 |
| Wärmepreis inkl. Netz (Gas-Fernwärme 261,4) | 255,3 | **243,4** (−7 %) | 235,3 (−10 %) | 220,0 (−16 %) |
| mit BEW Modul 2, gleiche Auslegung | 221,1 | 209,3 | – | – |
| Solaranteil | 41 % | 40,5 % | 40,5 % | 41 % |
| Strombezug / höchste Leistung | 1.720 MWh / – | 1.520 MWh / 0,46 MW | 1.400 MWh / 0,44 MW | 1.520 MWh / 0,46 MW |
| PtH-Wärme | 140 MWh | 0 | 0 | 5 MWh |
| Speicher: Zyklen / Winteranteil / Wirkungsgrad | 2,3 / 46 % / 93 % | 3,2 / 37 % / 89 % | 3,2 / 37 % / 89 % | 4,1 / 42 % / – |
| Speicherentladung direkt mit 85 °C | 21 % | 71 % | 71 % | 76 % |

Ergebnisordner: `results/klein/20261114-172557_base_opt`, `…-170407_vl_gleitend_opt`,
`…-171910_strom_day_ahead_2024_opt`.

* **Woher die −10 €/MWh kommen:** Im Sommer (Juni–August) braucht das System jetzt keinen Strom mehr; der Speicher
  pendelt zwischen 45 und 85 °C. Vorher lief dafür die Speicher-WP (Mai–September 645 MWh). Die PtH-Spitzen im
  Februar entfallen. Gegenläufig: doppelte Speicherverluste (8·10⁻⁵ statt 4·10⁻⁵ 1/h), −3 % Kollektorertrag,
  Leistungspreis ≈ 7.100 €/a (≈ 1,3 €/MWh).
* **Der Speicher ist jetzt deutlicher ein Mischspeicher** (3,2 Zyklen, 37 % der Entladung im Winter). Die Speicher-WP
  liefert nur noch ≈ 255 MWh/a (kalter Teil einmal im Winter geleert).
* **Optimum an der Segmentgrenze 6.000 m³:** Verlustrate und Übergangszone gelten je Kostensegment für dessen
  Untergrenze; das Segment 2.500–6.000 m³ rechnet deshalb mit den schlechteren Werten von 2.500 m³ (5.780 m³,
  LCOH 151,4). Das wahre Optimum liegt bei ≈ 6.000 m³; das Tal ist flach.
* **Gleitender Vorlauf** (nur COP der Luft-WP): −6,7 €/MWh. **Day-Ahead 2024:** −19 €/MWh gegenüber fest 30 ct;
  davon bringt das Laden des Speichers durch WP/PtH ≈ 3 €/MWh (bei fester Auslegung 133,5 → 130,6).
* Heatmap, Tornado und Strom-Vergleich: neu gerechnet am 15.11. (unten).

**Vergleichsvarianten neu** (`uv run serts varianten`, `results/klein/20261114-173001_base_varianten`):

| | Basis | ohne Speicher | nur WP + PtH | mit BEW Modul 2 (optimiert) | Gas-Fernwärme |
|---|---|---|---|---|---|
| Kollektor / Speicher | 4.670 m² / 6.000 m³ | 1.210 m² / – | – | 4.670 m² / 6.000 m³ | – |
| Wärmepumpe | 0,95 MW | 1,10 MW | 1,11 MW | 0,95 MW | – |
| Solaranteil / EE-Anteil | 40 % / 87 % | 9 % / 80 % | 0 % / 79 % | 40 % / 87 % | 0 |
| CO₂ [t/a] | 551 | 853 | 924 | 551 | 1.156 |
| LCOH Erzeugung [€/MWh] | 150,0 | 173,5 | 178,2 | 129,2 | 164,9 |
| Wärmepreis inkl. Netz [€/MWh] | **243,4** | 271,8 | 277,5 | **209,3** | **261,4** |
| dito mit BEW, gleiche Auslegung | 209,3 | 248,7 | 256,9 | 209,3 | – |

Solar + Speicher spart jetzt 34 €/MWh gegenüber reiner WP + PtH (vorher 18) und 28 €/MWh gegenüber Solar ohne
Speicher (vorher 12). Die Varianten ohne Speicher sind ≈ 5 €/MWh teurer als am 10.11. (Leistungspreis, geringerer
Kollektorertrag).

## Basislauf alt (Stand 10.11.2026, vor E39)


| Kennzahl | Wert |
|---|---|
| Kollektor / Speicher | **≈ 4.440 m² / ≈ 7.400 m³** (Fläche 13.000 von 13.000 m² – bindet knapp) |
| Wärmepumpe / PtH (Reserve) | 0,93 MW / 1,59 MW (PtH liefert ≈ 140 MWh/a, v. a. im Februar) |
| Arbeitszahl WP gesamt (Luft + Speicher) | 2,68 |
| Speicher | Wirkungsgrad 93 %, 2,3 Zyklen/a, 46 % der Entladung Nov–Mär, **gemischt** |
| Wärmeherkunft (5.462 MWh/a) | Luft-WP 2.740, Speicher-WP 1.480, Speicher direkt 320, Solar direkt ≈ 780, PtH 140 MWh |
| Solaranteil (direkt / Speicher direkt / WP-Quellwärme) | **41 %** (14 / 6 / 21 %) |
| LCOH Erzeugung (Gas-Referenz 165) | **≈ 160 €/MWh** |
| Wärmepreis beim Kunden inkl. Netz (Gas-Fernwärme 261) | **≈ 255 €/MWh** (−2 %) |
| davon Wärmenetz | Trasse ≈ 26 €/MWh, Hausanschlüsse + Übergabestationen ≈ 36 €/MWh |
| **mit BEW Modul 2** (40 %, gleiche Auslegung; Obergrenze) | LCOH ≈ 139, **inkl. Netz ≈ 221 €/MWh** (−15 % ggü. Gas), Zuschuss ≤ 2,1 Mio. € |
| EE-Anteil / CO₂ (Gas-Referenz 1.160 t/a) | 86 % / ≈ 625 t/a |

**Kostensegmente** (LCOH, V, A): 0–1.000 m³ 162,3; 1.000–2.500 m³ 161,0; 2.500–6.000 m³ 160,0 (5.820 m³);
**6.000–12.000 m³ 159,9 (7.400 m³)**; 12.000–35.000 m³ 166,1 €/MWh – flaches Optimum (2.500–12.000 m³ innerhalb
0,1 €/MWh).

**Betrieb über das Jahr** (`1_jahresverlauf.png`): Der Speicher wird Juli–Oktober mit Solarwärme geladen (bis 85 °C),
im November/Dezember gehalten und im Januar zuerst direkt (Oberschicht ≈ 85 °C), danach über die Speicher-WP bis
10 °C entladen. Direktentladung gibt es nur bei dicker heißer Schicht (`kennlinie_rest_MWh` = 0).

~~Ohne Flächengrenze (Abschätzung aus der Heatmap, kein Lauf): höchstens 1–2 €/MWh niedriger.~~ Überholt: mit dem
neuen Speicher gerechnet sind es −18 €/MWh und ein Saisonspeicher (Tornado unten).

## Was die Änderungen vom 10.11. bewirkt haben (Netz klein)

| Stand | Kollektor / Speicher | LCOH | Wärmepreis inkl. Netz / Gas | Solar | Winteranteil |
|---|---|---|---|---|---|
| vorher (E31) | 2.540 m² / 1.640 m³ | 141,2 | 229 / 257 | 24 % | 28 % |
| + KWW-Kosten Kollektor, PTES, Trasse (E32) | 4.500 / 7.010 | 131,8 | 221 / 261 | 42 % | 47 % |
| + Kennlinie, Schichtung, Luft-WP nach KWW (E34–E36) | 3.680 / 4.560 | 152,9 | 247 / 261 | 35 % | 36 % |
| + WP 1.340 €/kW (E38) = **Basis** | 4.440 / 7.400 | 159,9 | 255 / 261 | 41 % | 46 % |

Der größte Sprung (+21 €/MWh) kommt von der realistischeren Luft-WP (Arbeitszahl 2,65 → 2,22, E35). Teurere WP
machen Solar und Speicher wieder attraktiver (mehr Fläche, mehr Speicher), der Vorteil gegenüber Gas schrumpft aber
auf ≈ 6 €/MWh.

## Vergleichsvarianten alt (Stand 10.11.2026, vor E39; neu: oben)

| | Basis | ohne Speicher | nur WP + PtH | mit BEW Modul 2 (optimiert) | Gas-Fernwärme |
|---|---|---|---|---|---|
| Kollektor / Speicher | 4.440 m² / 7.400 m³ | 1.250 m² / – | – | 4.440 m² / 7.420 m³ | – |
| Solaranteil / EE-Anteil | 41 % / 86 % | 9 % / 80 % | 0 % / 79 % | 41 % / 86 % | 0 |
| CO₂ [t/a] | 625 | 850 | 924 | 611 | 1.160 |
| LCOH Erzeugung [€/MWh] | 159,9 | 169,3 | 174,4 | 138,6 | 164,9 |
| Wärmepreis inkl. Netz [€/MWh] | **255,3** | 266,8 | 272,9 | **220,7** | **261,4** |
| dito mit BEW, gleiche Auslegung | 221,1 | 243,6 | 252,3 | 220,7 | – |

* **Solar + Speicher lohnt sich**: gegenüber reiner WP + PtH −18 €/MWh, gegenüber Solar ohne Speicher −12 €/MWh;
  nur Solar + Speicher ist überhaupt günstiger als Gas-Fernwärme.
* **Mit BEW** ändert sich die Auslegung kaum (die Fläche bindet schon), der Wärmepreis sinkt um ≈ 35 €/MWh.
  40 % ist die Obergrenze; die BAFA begrenzt auf die Wirtschaftlichkeitslücke (E37).

## Heatmaps Kollektorfläche × Speichervolumen (`uv run serts heatmap`, Stand 15.11.2026 nach E39, ≈ 12 min)

`results/klein/20261115-142814_base_heatmap`; `heatmap_alle.png` zeigt neun Kennzahlen (Wärmepreis, mit BEW,
Vorteil ggü. Gas, Solaranteil, CO₂, Speicherzyklen, Winteranteil, WP-Leistung, PtH-Wärme). Feste Größen, WP und PtH
je Punkt optimiert. Wärmepreis inkl. Netz [€/MWh], Gas-Fernwärme 261; Basis-Optimum 4.670 m² / 6.000 m³ = 243,4:

| V \ A [m²] | 1.000 | 2.000 | 3.000 | 4.000 | 5.000 |
|---|---|---|---|---|---|
| 0 m³ | 272 | 273 | 277 | 282 | 287 |
| 1.000 m³ | 268 | 259 | 253 | 251 | 252 |
| 2.000 m³ | 269 | 260 | 253 | 249 | 250 |
| 4.000 m³ | 272 | 262 | 254 | **247** | – |
| 6.000 m³ | 275 | 264 | 256 | 248 | – |
| 8.000 m³ | 278 | 267 | 258 | 250 | – |
| 10.000 m³ | 280 | 270 | 260 | 251 | – |

(– = passt nicht auf 13.000 m²)

* **Mehr Kollektor lohnt sich, solange Speicher dabei ist**: entlang jeder Speicherzeile fällt der Preis bis an die
  Flächengrenze. Ohne Speicher steigt er mit der Kollektorfläche (Sommerüberschuss bleibt ungenutzt).
* **Flaches Tal beim Volumen**: bei 4.000 m² liegen 2.000–10.000 m³ innerhalb ≈ 4 €/MWh. Gegenüber dem 10.11. ist
  das ganze Feld mit Speicher 5–10 €/MWh günstiger, ohne Speicher ≈ 5 €/MWh teurer (Leistungspreis, Einfallswinkel).
* **Charakter des Speichers** (Zyklen / Winteranteil): bei 4.000 m² und 6.000 m³ 2,9 / 39 %; saisonal (< 1 Zyklus,
  ≈ 65 % Winter) nur bei viel Speicher und wenig Kollektor (1.000–2.000 m² mit ≥ 6.000 m³) – dort ist es am teuersten.
  Auf 13.000 m² ist kein saisonaler Betrieb wirtschaftlich (siehe Tornado: erst ohne Flächengrenze).

## Strom: fest gegen Day-Ahead (Szenarien `strom_day_ahead_*`, Stand 15.11.2026 nach E39)

Preis(t) = Day-Ahead(t) + Marge 25 + Netzentgelt 79,9 + Abgaben 57 €/MWh, dazu Leistungspreis 15,50 €/kW·a;
Preisjahr unabhängig vom Wetterjahr 2022. In den Day-Ahead-Szenarien dürfen WP/PtH den Speicher laden (E39).

| | fest 30 ct | Day-Ahead 2024 | Day-Ahead 2024 normiert (Ø wie fest) | Day-Ahead 2022 (Krise) |
|---|---|---|---|---|
| Strompreis Ø / gewichtet bezahlt [€/MWh] | 300 / 300 | 240 / 232 | 300 / 281 | 397 / 303 |
| Kollektor / Speicher | 4.670 m² / 6.000 m³ | 4.660 / 6.040 | 4.640 / 6.160 | 4.670 / 6.000 |
| Speicher-Zyklen / Winteranteil | 3,2 / 37 % | 4,1 / 42 % | 4,2 / 44 % | 4,7 / 48 % |
| Speicher aus WP/PtH geladen [MWh/a] | 0 | 480 | 570 | 770 |
| Solaranteil | 40,5 % | 41 % | 41 % | 42 % |
| Strombezug [MWh/a] / höchste Leistung [MW] | 1.520 / 0,46 | 1.520 / 0,46 | 1.520 / 0,48 | 1.520 / 0,52 |
| LCOH Erzeugung / Wärmepreis inkl. Netz [€/MWh] | 150,0 / 243,4 | **130,6 / 220,0** | 145,5 / 238,0 | 153,7 / **247,9** |
| mit BEW, gleiche Auslegung (Gas-Fernwärme 261) | 209,3 | 186,1 | 203,7 | 212,8 |

`results/klein/20261114-171910_strom_day_ahead_2024_opt`, `…/20261115-151050_strom_day_ahead_normiert_opt`,
`…/20261115-151009_strom_day_ahead_2022_opt`.

* **Preisniveau** entscheidet weiter: Day-Ahead 2024 (Ø 24 ct) ist 41 €/MWh günstiger als Gas-Fernwärme; selbst
  das Krisenjahr 2022 (Ø 40 ct) bleibt jetzt 14 €/MWh darunter (am 10.11.: 13 €/MWh darüber).
* **Zeitliche Struktur wirkt jetzt**: normiert sinkt der bezahlte Strompreis um 6 % (vorher 2 %) und der Wärmepreis
  um 5 €/MWh (vorher 1). 2022 bezahlt das System nur 303 statt Ø 397 €/MWh. Grund: WP/PtH laden den Speicher in
  billigen Stunden (bis 770 MWh/a), der Speicher macht dafür mehr Zyklen.
* Die Auslegung bleibt bei ≈ 4.650 m² / 6.000 m³ (Fläche bindet), die Strommenge ist überall gleich.
* Nicht modelliert: Korrelation Preis ↔ Wetter (Preis- und Wetterjahr verschieden).

## Sensitivitäten (`uv run serts tornado`, 50 Varianten, Stand 15.11.2026 nach E39, Größen jeweils neu optimiert)

`results/klein/20261115-115003_base_tornado` (≈ 2,6 h mit 4 Läufen parallel). Wärmepreis inkl. Netz (Basis
243,4 €/MWh) und Vorteil gegenüber Gas-Fernwärme (Basis **+14,9 €/MWh**, LCOH Erzeugung):

| Parameter (Variante) | Wärmepreis inkl. Netz | Vorteil ggü. Gas | Kollektor / Speicher |
|---|---|---|---|
| Gaspreis 8 / 16 ct/kWh | – | **−32 / +62** | – |
| Strompreis 20 / 40 ct/kWh | 210 / 277 | **+43 / −13** | gleich |
| **keine Flächenbegrenzung** (13.000 m² → unbegrenzt) | **226** | **+30** | **11.420 m² / 33.440 m³**, Solar 92 % |
| Förderung BEW 40 % | 209 | +36 | gleich |
| CO₂-Preis 55 / 200 €/t | – | +5 / +36 | – |
| Gütegrad Luft-WP × 0,85 / × 1,15 | 261 / 231 | **+0,5 / +26** | gleich |
| Zins 3 / 7 % (real) | 220 / 268 | +25 / +5 | gleich |
| Strompreis +2 %/a real | 261 | −0,1 | gleich |
| Ankerkunde + 20 / 40 % | 224 / 210 | +18 / +20 | 5.040 / 3.710; 5.240 / 2.500 |
| Last × 0,8 / × 1,2 | 263 / 232 | +18 / +12 | 4.550 / 6.730; gleich |
| Leistungspreis 0 / 163,73 €/kW·a (≥ 2.500 h) | 242 / 258 | +16 / +3 | gleich |
| Nebenkosten 0 / 20 % | 231 / 256 | +21 / +9 | gleich |
| WP-Kosten 1,0 / 1,73 Mio. €/MW | 235 / 253 | +22 / +7 | gleich |
| Strahlung − / + 10 % | 252 / 237 | +8 / +20 | 4.940 / 4.340; 4.450 / 7.330 |
| Kollektor 240 / 380 €/m² | 237 / 251 | +20 / +9 | gleich |
| Speicherverluste 1,5 / 8 ·10⁻⁵ 1/h | 240 / 249 | +18 / +10 | 4.610 / 6.330; gleich |
| η₀ 0,75 / 0,82; Feldverluste 5 / 15 % | 249 / 242; 241 / 247 | +10 / +16; +17 / +12 | η₀ 0,75: 4.850 / 4.890 |
| Speicherkosten × 0,7 / × 1,3 | 239 / 247 | +18 / +12 | gleich |
| PtH-Reserve 0 | 240 | +18 | gleich |
| Vorwärmen aus | 246 | +12 | gleich |
| Größenabhängigkeit aus (Exponent 0) | 240 | +17 | 4.630 / 6.230 |
| Einfallswinkel b₀ 0 / 0,15; Rücklauf 40 / 50 °C | 242–245 | ±1,5 | – |
| Übergangszone 0 / 0,1 / 0,25; COP Speicher-WP 3,5 / 5,5 | 243–244 | ±0,6 | gleich |
| Hausanschluss 5.000 / 15.000 €; Trasse 370 / 940 €/m; Anteil Straße 50 / 100 % | 225–262 | unverändert | gleiches Netz |

**Lesart:**
* Ob das System günstiger ist als Gas-Fernwärme, entscheiden **Gas- und Strompreis**, danach die **Effizienz der
  Luft-WP** (bei 15 % schlechterem Gütegrad ist der Vorteil weg), Zins und Förderung.
* **Die Fläche ist die wichtigste Stellschraube der Auslegung.** Ohne Grenze baut das Modell 11.400 m² Kollektor und
  einen **Saisonspeicher** mit 33.400 m³ (1,45 Zyklen, 70 % der Entladung im Winter, Wirkungsgrad 83 %), Solaranteil
  92 %, Strombezug 375 statt 1.520 MWh/a, CO₂ 136 statt 551 t/a. Wärmepreis 226 €/MWh (−18 €/MWh), mit BEW 169.
  Dafür werden ≈ 38.900 m² gebraucht, dreimal so viel wie verfügbar; Fläche kostet im Modell nichts (Obergrenze des
  Nutzens). Die Abschätzung vom 10.11. („höchstens 1–2 €/MWh“) war damit falsch: Mit dem neuen Speichermodell
  rechnet sich der große Speicher, wenn genug Kollektor dazukommt. Die Kostensegmente steigen monoton bis zum
  größten (6.000 m³ 151,2 → 12.000 m³ 145,3 → 33.400 m³ 135,3 €/MWh LCOH).
* **Speicherparameter wirken wenig** (Übergangszone, COP Speicher-WP, Speicherkosten ±30 % je ≤ 4 €/MWh). Viele
  Varianten landen genau bei 4.670 m² / 6.000 m³: Fläche und Segmentgrenze (Speicherwerte gelten für die Untergrenze
  des Segments, E39) halten die Auslegung fest. Der Tornado unterschätzt daher, wie stark die Größen reagieren
  würden.
* Netzkosten (Hausanschluss, Trasse) verschieben den Wärmepreis um bis zu ±18 €/MWh, aber nicht den Vergleich mit
  Gas (gleiches Netz).

**Kernaussage (vorläufig, Netz klein):** Luft-WP + Speicher-WP mit Solarthermie, PTES und PtH-Reserve ist unter den
Basisannahmen ≈ 7 % günstiger als Gas-Fernwärme (243 statt 261 €/MWh), mit BEW Modul 2 (Obergrenze) ≈ 20 %. Der
Vorteil hängt vor allem an Energiepreisen und WP-Effizienz. Auf 13.000 m² ist der kostenoptimale Speicher ein
Mischspeicher (6.000 m³, ≈ 3 Zyklen). **Mit ≈ 39.000 m² Fläche wird ein Saisonspeicher (≈ 33.000 m³, 92 % solar)
die günstigste Lösung** – die Flächenfrage ist damit zentral für den Bericht. Netz groß:
`docs/ergebnisse_netz_gross.md`, Prüfung: `docs/kernfragen.md`.
