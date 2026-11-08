# Entscheidungen und Abweichungen vom Briefing

Kurzformat: Kontext → Entscheidung → Folge. Neue Einträge unten anhängen, alte nicht löschen
(bei Revision: „ersetzt durch E…“). BRF = `../obsidian/AGENT_BRIEFING_SERTS.md`.

### E1 Repo-Struktur nach BRF §4, mit Ergänzungen (08.11.2026)
Struktur wie BRF §4. Ergänzt: `src/serts/sources/` (Leser je Rohdatenquelle), `prepare.py` (M1-Pipeline),
`annahmen.py` (Annahmentabelle aus YAML), `cli.py`, `data/reference/` (Validierungswerte), `docs/`.
Paketverwaltung mit **uv** + `pyproject.toml` (Lockfile `uv.lock` → reproduzierbare Umgebung), src-Layout,
pytest, ruff. Repo liegt im Unterordner `serts/`, damit Literatur, PyPSA-Quellcode, OpenPlan und GIS nicht
mitversioniert werden.

### E2 Lastgang der eigenen Netzberechnung statt demandlib (BRF §3.5)
Für Bad Lippspringe liegt ein stündlicher Lastgang 2022 je BDEW-Typ für 159 reale Gebäude vor. Er ist
projektspezifischer als ein synthetisches demandlib-Profil und wird **Basis**. demandlib bleibt für die
Sensitivität „Lastprofil“ (BRF §1, Pflicht 6). Gewerbe (GMK, GKO = 29 %) ist enthalten → Ankerkunde-Basis 0 %,
Varianten 20/40 % werden **zusätzlich** addiert.

### E3 Netztemperaturen: Modell 75/45 °C, Netzberechnung 80/50 °C
BRF §2 legt 75/45 °C fest (hat Vorrang). Die Netzverluste der NB gelten für 80/50 °C. Übernommen werden die
NB-Verluste unverändert (937 MWh/a, 17 %) → bei 75/45 °C leicht überschätzt (konservativ; grobe Abschätzung über
mittlere Übertemperatur gegen ≈ 10 °C Erdreich: (60−10)/(65−10) ≈ −9 %). Sensitivität: Szenario `rl_50`
(passt zur NB) und `netz_daemmung`. **Klären:** Netzberechnung mit 75/45 °C neu rechnen?

### E4 Wetterjahr 2022; Lücke in DWD-Temperatur gefüllt
Wetterjahr = Lastjahr 2022 (Zeitstempel der NB). DWD TU 2022 hat eine 68-h-Lücke (20.–23.05.) → Füllung
mit Tagesgang ±7 Tage, linear an Ränder angeschlossen (statt Abbruch oder linearer Interpolation über 3 Tage).
Lücken ≤ 6 h linear. Der Lastgang korreliert mit keinem DWD-Jahr deterministisch (datenbasis §3) → Wetterbasis
der NB beim Team erfragen.

### E5 COP-Prüfwerte brauchen eine Quell-Spreizung
BRF §3.4 nennt keine Spreizung der Quelle. Reproduzierbar sind die Prüfwerte nur mit
15 → 10 °C (η 0,6 → 3,78) und 50 → 40 °C (η 0,45 → 7,27). SCH D2 nutzt wieder andere Austrittstemperaturen
(z. B. PTES 50 °C ≈ 50 → 20 °C). `cop_lorenz` erhält deshalb Ein- **und** Austritt explizit; Tests dokumentieren
die angenommenen Spreizungen. Für das Pool-Modell gilt ohnehin `COP_ptes` = 4,5 konstant (BRF).

### E6 Strahlung 2022 aus PVGIS-SARAH3
DWD-Strahlung an 03028 endet 08/2011. Für 2022 wird PVGIS-SARAH3 (stündlich, direkt auf Kollektorebene,
mit Horizont) genutzt; Plausibilisierung gegen DWD-Klimamittel 03028 (Median ≈ 960 kWh/(m²a) horizontal).
Download braucht Netzzugang (`serts fetch-pvgis`), Kollektorneigung muss vorher gesetzt sein.

### E7 Zusätzlicher Status `vorgabe`
BRF §4 kennt `belegt|annahme|offen`. Ergänzt um `vorgabe` für Teamentscheidungen aus BRF §2 (z. B. 75/45 °C,
η_PtH), damit diese nicht als „unbelegte Annahme“ erscheinen, aber auch nicht als „belegt“.

### E8 Rohdaten: unverändert, außerhalb von Git, mit Prüfsummen
`serts import-raw` kopiert nur benötigte Dateien aus `../Bad Lippspringe` nach `data/raw/` und schreibt
`MANIFEST.sha256`. Öffentliche DWD-Daten (≈ 60 MB) nicht im Git; die NB-Excel (0,5 MB, nicht anders
beschaffbar) schon. Generierte Daten (`data/processed`, `results`) nie im Git.

### E9 Rasterbezug = Einspeisung inkl. Netzverluste
BRF §5 gibt A in m² je MWh/a „Bedarf“; DRL-Bezug (≈ 1,0 m²/(MWh/a)) ist „Wärme ans Netz“. Daher Bezug
5.462 MWh/a (Gebäude + Netzverluste), nicht 4.525.

### E10 Verlustrate PTES: obere Sensitivität 8·10⁻⁵ 1/h
Das PTES in Bad Lippspringe ist ≈ 7× kleiner als DRL. Verluste skalieren mit der Oberfläche (∝ V^(2/3)), der
Inhalt mit V → spezifisch ∝ V^(−1/3) → Faktor (60.000/8.700)^(1/3) ≈ 1,9. Startwert bleibt 4·10⁻⁵ (BRF),
Sensitivität bis 8·10⁻⁵. Eigene Abschätzung, Literaturbeleg (Xiang 2022) nachziehen.

### E11 Kollektor im Netz: p_nom = A·10⁻³ MW, p_max_pu = kW/m²
Damit p_max_pu ≤ 1 bleibt (max. ≈ 0,7 kW/m²) und A direkt in m² aus dem Raster kommt.

---
*Ab hier: Team-Rückmeldung 09.11.2026 und Umsetzung M2–M6.*

### E3 (revidiert) Netztemperatur 80/45 °C
TEAM: Netz bleibt bei 80 °C Vorlauf (wie NB), Rücklauf frei → Basis 80/45 °C, Sensitivität 40/50 °C.
Die NB-Netzverluste (80/50 °C) passen damit; E3-Abschlag entfällt weitgehend. Folge: Direktentladung
braucht T_oben ≥ 85 °C = T_max → Pool-Modell unverändert, aber kein Puffer mehr nach oben.

### E12 Wärmeübertrager-Caps (x_HX) nicht modelliert
Lade-Links: Wärme ist durch die Kollektorleistung (≤ 0,66 kW/m²) begrenzt, eine WÜT-Auslegung auf
Kollektorspitze (SCH A3) bindet also nie. Entlade-Links: durch Last und WP-Leistung begrenzt. Pool-Links
erhalten deshalb p_nom = V m³/h (praktisch unbegrenzt). x_TL = 10 MW (Erzeugung am Netz, TEAM), Check
„Stunden am Cap“ = 0. Kosten der WÜT stecken pauschal in den spezifischen Kosten.

### E13 Kostenansätze (Preisbasis 2025, netto, real)
- **PTES** degressiv: c(V) = 38,3 €/m³ · (V/60.000)^−0,31 · 1,5. Stützstellen DRL 38,3 €/m³ (SIF) und
  Marstal 10.000 m³ 67 €/m³ (DEA 2019); Kontrolle Vojens 200.000 m³: 26 vs. 24 €/m³ real. Faktor 1,5 =
  grobe Baupreissteigerung 2014→2025. Ergebnis z. B. 8.700 m³ ≈ 105 €/m³.
- **Kollektorfeld** 450 €/m² (Bitterfeld-Wolfen, Planung 2020, 5.000 m²); DRL 2014 (164 €/m², 37.500 m²)
  nicht übertragbar (Größe, Land, Jahr).
- **WP** 1,0 Mio. €/MW_th, **PtH** 0,1 Mio. €/MW_th (Frederikssund 2022 + Kleinanlagen-Aufschlag),
  **Gaskessel** 0,1 Mio. €/MW. DEA-Technology-Data-Werte waren online nicht direkt abrufbar → Annahmen
  mit Sensitivitätsbereich in `base.yaml`.
- Kapitalkosten = Annuität über die technische Lebensdauer + fixe O&M (% vom Invest).

### E14 Kennzahlen-Definitionen
- **LCOH** = (Σ Kapitalkosten/a + Stromkosten/a) / Netzeinspeisung (inkl. Netzverluste; Systemgrenze
  Erzeugung). Zusätzlich `lcoh_geliefert` bezogen auf Wärme an Gebäude.
- **Preisänderung** über den preisdynamischen Faktor a·b nach VDI 2067-1; bei 0 %/a (TEAM: real konstant)
  genau 1. Variante +2 %/a über `oekonomie.preisaenderung.*`. Der Faktor wirkt auch im LP (Strompreis).
- **EE-Anteil** = 1 − Netzstrom · (1 − EE-Anteil Strommix) / Einspeisung (1 MWh Strom ≈ 1 MWh Wärme
  bei PtH; bei WP konservativ, weil Umweltwärme voll als EE zählt).
- **Gas-Referenz:** Gaspreis 12 ct/kWh_Hs als Preis **ohne** CO₂-Bepreisung gelesen, CO₂ (100 €/t) separat.
- **CO₂-Vermeidungskosten** negativ = System ist günstiger als Gas.

### E15 PtH-Redundanz
SCH A6: PtH ≥ Spitzenlast (n−1). Umgesetzt als `p_nom_min` der PtH (`pth.redundanz` = 1,0; Variante 0).
Ohne diese Grenze baut das LP bei perfekter Voraussicht keine PtH (WP + Speicher decken die Spitze).

### E16 Tie-Breaker für Speicherladen
Laden und Entladen in derselben Stunde ist im Pool-Modell verlustfrei → LP-Lösung nicht eindeutig
(Solar „durch den Speicher“ statt direkt). Lade-Links kosten 0,1 €/MWh (numerische Hilfsgröße, nicht in
der LCOH). Damit ist die Aufteilung Solar direkt / über PTES aussagekräftig.

### E17 Flächencheck statt Flächen-Constraint
TEAM: ≈ 13.000 m² Grundstück. Bedarf = A_Koll · 2,3 (BSW, inkl. Reihenabstand/Technik) + PTES-Grundfläche
(geometrisch ähnlich DRL, + 5 m Rand). Wird je Rasterpunkt ausgewiesen (`flaeche_ok`), nicht als
Nebenbedingung – so bleibt sichtbar, wie viel teurer/besser größere Anlagen wären.

### E18 Kollektorkennwerte als Annahme
Typ wie DRL (Arcon-Sunmark HTHEATstore 35/10, Keymark SP SC0843-14). Das Datenblatt war am 09.11.2026 nicht
abrufbar (solarkeymark.nl: Verbindung abgelehnt). η0 = 0,80, a1 = 2,4, a2 = 0,012 (BRF-Bandbreite).
Plausibilisierung: Hochtemperatur-Ertrag 587 kWh/(m²a) bei PVGIS 2022 (1.394 kWh/m² Ebene); auf ein
Normaljahr skaliert (DWD-Klima ≈ 960 kWh/m² horizontal, Ebene ≈ 1.085 mit angenommenem Neigungsgewinn 1,13) ≈ 460 kWh/(m²a) → im BSW-Bereich
430–500. **Nachtragen**, sobald das Keymark-Datenblatt vorliegt.

### E19 LP-Skalierung und Solver
Pool-Volumen werden im LP in 1.000 m³ geführt (`network.VOL`), damit Volumen- und Leistungsvariablen in
ähnlicher Größenordnung liegen. HiGHS mit Interior-Point ohne Crossover (`solver.optionen`). Benchmark
8760 h, 1 Thread: Simplex 262 s → IPM 56 s bei identischem Optimum. Im Raster läuft je Prozess 1 Thread
(`--jobs 4` auf 4 Kernen).

---
*Ab hier: Vereinfachung nach Team-Rückmeldung 09.11.2026 – „so simpel wie möglich, so komplex wie nötig“.*

### E20 Einfaches Modell statt Pool-Modell und Raster (ersetzt E11, E12, E17, E19 und Teile von E13, E16)
Das Briefing ist Orientierung, nicht Pflicht. Ziel: Das Team soll das Modell verstehen und anpassen können.
- **Speicher:** ein PyPSA-Store in MWh (Inhalt bezogen auf 10 °C), Verlust = `verlustrate` × Inhalt je Stunde.
  Statt drei Temperatur-Pools eine einzige Jahresregel: Direktentladung ≤ 53 % der Entladung
  ((85−45)/(85−10), SCH D3; DRL gemessen 52–63 %), der Rest geht nur über die WP.
- **Kollektor:** ein Temperaturniveau (T_m 67,5 °C) für Direktnutzung und Laden; kein Niedertemperatur-Laden.
- **Größen werden mitoptimiert** (Kollektor, Speicher, WP, PtH) mit linearen Kosten; ein Lauf statt 24
  Rasterpunkten (≈ 30 s statt ≈ 25 min). Feste Größen bleiben möglich (`serts run --A … --V …`), z. B. für
  „ohne Speicher“ (`--V 0`) oder eine kleine Heatmap, falls gewünscht.
- **Fläche** ist jetzt eine Nebenbedingung: A · 2,3 + V / 2,65 m³/m² ≤ 13.000 m².
- **Speicherkosten** linear 105 €/m³ (aus der degressiven Kurve bei ≈ 8.700 m³ abgeleitet). Liegt das Optimum
  weit davon entfernt, Wert neu ableiten.
- **Weggefallen:** Transmission/x_TL (Erzeugung am Netz), WÜT-Caps, Leistungsabschläge der WP je Quelle
  (nur noch: Luft-WP aus unter −7 °C), Frostschutz (≈ 1 % Ertrag), LP-Skalierung, Raster, Heatmap/Pareto.
- **Bleibt:** Tie-Breaker auf dem Speicherladen (E16), PtH-Redundanz (E15), Preisdynamik (E14).

### E21 Speicher als WP-Quelle nur in der Heizperiode
Mit nur der Jahresregel (E20) nutzte das LP im Sommer die WP aus dem Speicher, um sich Direktentladung für den
Winter „freizuschalten“ – physikalisch unsinnig (oben im Speicher ist es im Sommer heiß). Ein Parameter
`waermepumpe.speicher_monate` (Basis Nov–Mär, nach DRL-Betrieb Nov–Feb) beschränkt die Speicher-WP auf die
Heizperiode. Ergebnis: Sommer Kurzzeitnutzung, Ladung Jun–Sep, Entladung Nov–Jan wie in Dronninglund.
Bleibende Eigenheit (perfekte Voraussicht): Der volle Speicher wird bis Nov/Dez gehalten, weil die Wärme dort
die Luft-WP mit schlechterem COP ersetzt.

### E22 Tornado und kleine Aufräumarbeiten
- `serts tornado`: Jeder Parameter aus `tornado.parameter` wird einzeln auf seine `sens`-Werte gesetzt, die
  Größen werden jeweils neu optimiert (zeigt die LCOH des jeweils kostenoptimalen Systems). 3 parallele
  Läufe à 1 Thread, ≈ 3 min für 24 Läufe.
- Solarressource als Faktor `kollektor.strahlung_skalierung` (Variante 0,78 ≈ Normaljahr statt 2022).
- Strompreis-Bandbreite 20–40 ct/kWh (Annahme ±1/3).
- `ptes.T_mitte` entfällt: die Grenze direkt/WP ist der Netz-Rücklauf `netz.T_RL` (ein Parameter weniger,
  Rücklauf-Sensitivität wirkt automatisch auf den Direktanteil).
