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

### E23 Normaljahr (PVGIS-TMY) als Basis für die Strahlung
TEAM 09.11.2026. PVGIS-TMY (SARAH3, 2005–2023) liefert horizontale Werte; Umrechnung auf 35° Süd mit pvlib
(Perez, Albedo 0,2, Sonnenstand zur Stundenmitte). Die TMY-Stunden werden der Reihe nach auf 2022 gelegt;
Temperatur und Last bleiben 2022 (DWD bzw. Netzberechnung). Ergebnis: horizontal 1.090, Ebene 1.287 kWh/m²
(2022: 1.394). Die frühere Schätzung „Normaljahr ≈ Faktor 0,78“ (aus DWD 1992–2010, 960 kWh/m²) war zu
pessimistisch: Der TMY-Zeitraum 2005–2023 ist strahlungsreicher. Strahlungssensitivität jetzt ±10 %
(Spanne der Einzeljahre); Jahr 2022 als Szenario `wetter_2022`.

### E24 Speicherpreis in drei Preisstufen (ersetzt den linearen Preis aus E20) – **ersetzt durch E30 (Fehler: nicht monoton)**
Erdbeckenspeicher werden mit der Größe spezifisch billiger; ein LP kann das nicht direkt abbilden. Einfache
Lösung: drei Größenklassen mit je einem Preis aus der Kostenkurve (DRL/Marstal, × 1,5 Baupreise), konservativ
am **unteren Rand** jeder Stufe ausgewertet (sonst sitzt das Optimum am Stufenrand mit zu günstigem Preis):
< 5.000 m³: 165 €/m³ (bei 2.000 m³), 5.000–12.000 m³: 124 €/m³, 12.000–35.000 m³: 95 €/m³.
`run.loese` rechnet je Stufe einen Lauf (V innerhalb der Stufe) und nimmt den mit den geringsten Jahreskosten;
die Ausgabe zeigt alle drei Stufen. Laufzeit ≈ 2,5 min statt 30 s. Sensitivität über `ptes.kosten_faktor`
(0,7 / 1,3 auf alle Stufen).
Befund Basis: die drei Stufen liegen innerhalb ≈ 1 €/MWh (137,2–138,4) – das Kostenoptimum ist **flach**;
größere Speicher kosten kaum mehr, bringen aber mehr Solaranteil (siehe docs/ergebnisse.md).

### E25 LCOH nach VDI 2067 Blatt 1; Netzkosten
- **Annuitätenmethode nach VDI 2067-1** über den Betrachtungszeitraum T = 20 a: kapitalgebundene Kosten mit
  Ersatzbeschaffungen und linearem Restwert (vorher: Annuität über die Lebensdauer), betriebsgebundene Kosten
  als Anteil vom Invest, bedarfsgebundene Kosten (Strom, Gas, CO₂) mit preisdynamischem Barwertfaktor.
  Preisänderungen (Invest, Betrieb, Energie) als Parameter, Basis real 0 %/a.
- **Abweichungen von VDI 2067 (bewusst, im Bericht nennen):** Instandsetzung und Wartung zusammengefasst
  (`om_fix`); keine „sonstigen Kosten“ (Versicherung, Verwaltung) und kein Bedienpersonal; keine Erlöse;
  Förderung als Abzug vom Invest; Kostenstand real 2025 (keine Inflation, Zins als Realzins).
- **Verteilnetz:** Trasse 2.432 m × (Anteil Straße × 550 €/m + Rest × 250 €/m) + 159 Hausanschlüsse ×
  10.000 €. Lebensdauer 40 a (Trasse) / 25 a (Hausanschluss), O&M 1 % / 2 %. Das Netz geht nicht in die
  Optimierung ein (fix), sondern in den **Wärmepreis beim Kunden** (`lcoh_inkl_netz`, bezogen auf die
  gelieferte Wärme). Die Gas-Referenz (Gas-Fernwärme) trägt dasselbe Netz (ohne Förderung) → der Abstand
  System – Gas ändert sich nur durch die Förderung. `netz.anteil_strasse` steuert das Verhältnis Straße/Wiese.
- Tornado erweitert um Förderung (BEW 40 %), Strompreissteigerung, Kollektor η0/Feldverluste,
  PtH-Redundanz, Netzkosten, Gas- und CO₂-Preis. Reine Kostenparameter (Netz, Gas-Referenz) werden ohne
  neuen Solverlauf auf dem Basisergebnis nachgerechnet. Zusätzliche Kennzahl `abstand_gas`.

### E26 Grenzen der Speicher-Regel „Direktanteil ≤ 53 %“; Matplotlib-Backend
- Die Regel `Direktentladung ≤ (40/75) · (Direkt + Quellwärme der Speicher-WP)` ist eine **Jahresbilanz**. Sie
  stellt sicher, dass der Speicher über das Jahr nicht nur direkt entladen wird (die unteren 35 K müssen
  von der WP geholt werden, Quelle ≥ 35/40 · Direkt). Sie stellt **nicht** sicher, dass in einer einzelnen
  Stunde warmes Wasser (≥ 80 °C) vorhanden ist oder dass die WP erst nach der Direktentladung läuft. Ein
  Stundenmodell bräuchte Temperaturen/Schichten (das frühere 3-Pool-Modell, bewusst verworfen, E20).
- Matplotlib: `use("Agg")` steht nicht mehr in den Modulen (zeigte im Notebook keine Grafiken), sondern nur in
  `cli.main` und `tests/conftest.py`.

### E27 Speicher in zwei Teilen (heiß/kalt); Luft-WP-Leistung bei Kälte (ersetzt E21 und E26, Teile von E20)
**Anlass:** TEAM-Rückfrage 09.11.2026: Warum die Monatsbeschränkung der Speicher-WP?
**Befund:** Die Monatsregel (E21) war ein Pflaster für die Jahresregel „Direktentladung ≤ 53 %“ (E20): Diese
Bilanz erlaubte es, im Sommer „Quellwärme“ zu verbuchen, um im Winter mehr direkt zu entladen. Die Folge war
ein Verhalten, das **kurzfristige Speichernutzung blockierte** (direkte Sommerentladung verlangte
Quellwärme im Winter) und damit Solar und Speicher im Basislauf unterschätzte.
**Lösung (einfacher und physikalisch konsistent):** Der Speicher besteht aus zwei Energie-Speichern.
*Heiß* = Wärme zwischen 85 °C und dem Netz-Rücklauf (40 K, f = 53 %), *kalt* = Rücklauf bis 10 °C (35 K,
47 %). Beladen füllt beide immer im Verhältnis f : (1−f), direkt ins Netz geht nur der heiße Teil, die
Speicher-WP holt ihre Quellwärme nur aus dem kalten Teil. Eine Nebenbedingung koppelt die Größen
(kalt = (1−f)/f · heiß). Dadurch gilt die Aufteilung **in jeder Stunde**, die Jahresregel und die
Monatsbeschränkung entfallen, und die Speicher-WP darf ganzjährig laufen.
**Luft-WP bei Kälte:** Die thermische Leistung sinkt linear von 100 % (ab −1 °C) auf 80 % bei −7 °C
(`luft_leistung_voll_ab`, `luft_leistung_bei_tmin`); vorher war sie temperaturunabhängig (E20 hatte das
vereinfacht). Über −1 °C bleibt sie konstant 100 % (konservativ). Die PtH-Reserve deckt Spitzen unabhängig davon.
**Nicht umgesetzt:** WP lädt den Speicher (E29 Begründung), Mischung/Zwischentemperaturen.

### E28 Strompreis in Komponenten, Nebenkosten, Förderfähigkeit je Komponente
- **Strompreis:** Gesamt 30 ct/kWh (TEAM) = Energie + Netzentgelt (Arbeitspreis) + Abgaben. Aufteilung nach
  BDEW-Komponenten (Jan 2026, Kategorie nicht geklärt): Netzentgelt 93 €/MWh, Abgaben 57 €/MWh (Stromsteuer,
  Konzessionsabgabe, KWKG, §19), Energie = Rest (150 €/MWh). Ausgewiesen als `kosten_a_strom_energie/_netzentgelt/
  _abgaben`. Für Tarif `day_ahead`: Preis(t) = Day-Ahead(t) + Marge + Netzentgelt + Abgaben (Marge offen).
  Nicht modelliert: Leistungspreis (EUR/kW·a auf die höchste Bezugsleistung).
- **Wärmenetz** getrennt ausgewiesen: `netzkosten_spez_trasse`, `netzkosten_spez_hausanschluss` (EUR/MWh geliefert).
- **Nebenkosten 10 %** (TEAM) auf alle Investitionen (auch Gaskessel und Netz): `oekonomie.nebenkosten`.
- **Zins bleibt real** (TEAM); Preisänderungsfaktoren bleiben als Variante bestehen (Basis 0 %/a). Vorlauf bleibt 80 °C.
- **Förderfähigkeit je Komponente** (`oekonomie.foerderfaehig`): Kollektor, PTES, WP, Trasse ja; PtH und
  Hausanschluss konservativ nein (laut gelesenem BEW-Text nicht ausdrücklich genannt); Gaskessel nein.

### E29 WP lädt den Speicher: bewusst nicht umgesetzt
Idee (TEAM): im Sommer mit der Luft-WP (COP ≈ 3,3) den Speicher laden, im Winter direkt entladen statt Luft-WP
(COP ≈ 2,1–2,5). Handrechnung: je MWh gelieferter Wärme spart das ≈ 0,08–0,12 MWh Strom (Sommer-COP ≈ 3,2 und ≈ 13 %
Speicherverlust bei ≈ 3.500 h Haltedauer gegen Winter-COP ≈ 2,3) ≈ 25–35 €/MWh, das sind ≈ 2–3 €/m³ und Jahr gegenüber Speicherkosten von ≈ 10–11 €/m³ und Jahr (124 €/m³, 25 a, 5 %, O&M). Bei festem
Strompreis rechnet sich das nicht; mit dynamischem Preis (Day-Ahead + Aufschläge) kann es sich ändern.
Zusätzlicher Aufwand: Solaranteil müsste anders bilanziert werden (WP-Wärme im Speicher ist nicht solar).
→ Als Variante für den Day-Ahead-Fall vormerken (`docs/ausblick.md`).

### E30 Stetige Speicher-Kostenkurve statt Preisstufen (ersetzt E24)
**Fehler in E24:** Der Stufenpreis galt für das *gesamte* Volumen. Dadurch waren die Gesamtkosten an den
Stufengrenzen nicht monoton: 12.000 m³ zu 95 €/m³ (1,14 Mio. €) waren billiger als 11.000 m³ zu 124 €/m³
(1,36 Mio. €). Der Solver nutzte das aus – viele frühere Ergebnisse lagen exakt bei 5.000 oder 12.000 m³
(z. B. der „flache Optimum“-Befund und das Raster vom 09.11.2026). Meine Antwort „kein Fehler“ auf die Frage
„warum steigt die LCOH, wenn der Speicher billiger wird“ war daher unvollständig.
**Lösung:** Die Investition ist eine stetige, konkave Funktion C(V) = V · c_ref · (V/V_ref)^b · Preisindex
(c_ref = 38,3 €/m³ bei 60.000 m³, b = −0,31, Index 1,5; Kontrolle: Marstal 10.000 m³ = 67 €/m³, Vojens
210.000 m³ = 24 €/m³ in 2014er Preisen). Im LP wird sie je Segment durch eine Sehne ersetzt
(`ptes.segmente_m3` = 0, 1.000, 2.500, 6.000, 12.000, 35.000 m³): Grenzkosten je m³ + Fixkosten je Segment;
je Segment ein Lauf, der günstigste gewinnt. Die Sehne unterschätzt die Kosten zwischen den Stützstellen um
höchstens ≈ 4–6 % (bei V > 1.000 m³). Die Fixkosten stecken in `kosten_a_speicher`.
**Folgen:** Das Basisergebnis ändert sich kaum (V ≈ 1.600 m³, vorher 1.140), aber die Segmentvergleiche
(„flaches Optimum bei 5.000/12.000 m³“) und die Rasterläufe davor sind **nicht mehr gültig** und wurden neu
gerechnet (docs/saisonaler_speicher.md).

### E31 Strom als Zeitreihe (Option) und Kennzahlen zum Speichercharakter
- Tarif `day_ahead` mit Day-Ahead-Stundenpreisen DE-LU (Bundesnetzagentur | SMARD.de, CC BY 4.0, Download über die
  Energy-Charts-API, `serts fetch-strompreise 2022 2023 2024`): Preis(t) = Day-Ahead(t) + Vertriebsmarge 25 €/MWh
  + Netzentgelt 93 + Abgaben 57 €/MWh. Marge nach Preisblättern leistungsgemessener Gewerbekunden (2,5–7 ct/kWh
  inkl. Ausgleichsenergie; untere Spanne gewählt). Preisjahr 2024 (ruhig; 2022 = Krise 235, 2023 = 95 €/MWh Mittel);
  Preis- und Wetterjahr müssen nicht übereinstimmen. Szenarien: `strom_day_ahead_2024`, `_2022`, `_normiert`
  (gleicher Jahresmittelwert wie der feste Tarif). Leistungspreis weiterhin nicht modelliert.
- Neue Kennzahlen: `speicher_winteranteil` (Anteil der Speicherentladung Nov–Mär), `speicher_charakter`
  (saisonal: < 2 Zyklen und ≥ 60 % Winteranteil; kurzzeit: ≥ 4 Zyklen; sonst gemischt), `strompreis_mittel`
  und `strompreis_gewichtet` (tatsächlich bezahlter Mittelwert nach Strommenge).

### E32 KWW Technikkatalog als einheitliche deutsche Kostenquelle (10.11.2026)
Quelle: KWW Technikkatalog Wärmeplanung v1.1 (08-2026), Preise 2026 real, **netto**, `data/raw/kww/`.
**Übernommen** (Basisfall): 
- *Kollektor* (Tab. 21, Flachkollektor Freifläche): 330 €/m² Apertur bei 5.000 m² (Netz klein), 300 €/m² bei
  15.000 m² (Netz groß), × 0,92 = **304 bzw. 276 €/m² Brutto** (unser Kollektorfeld ist die Bruttofläche; vorher
  450 €/m² nach Bitterfeld-Wolfen). Lebensdauer 25 a und O&M 1 % unverändert, jetzt belegt. Der **Ertrag** (450 kWh/m²)
  wird *nicht* übernommen (eigene Rechnung mit PVGIS; die KWW-Anmerkung CG sagt selbst, er sei nicht pauschal gültig).
  Die Größenklasse ist eine Festlegung je Netz (die Kostenkurve des Kollektors bleibt linear); nach dem Lauf
  prüfen, ob das gewählte Feld zur Klasse passt (Tabelle in `docs/ergebnisse_netz_gross.md`).
- *PTES* (Tab. 52): Kostenkurve **Invest = 1093,6 · V^0,7472** (Stützwerte 90/70/60/50 €/m³ bei 20.000/50.000/
  100.000/200.000 m³). Das entspricht in unserer Form c(V) = c_ref · (V/V_ref)^b mit c_ref = 67,8 €/m³ bei
  60.000 m³ und b = −0,2528; **Preisindex 1,0** (die 1,5 galten für die 2014er DRL-Preise). Bei 1.600 m³ praktisch
  gleich wie vorher (168 statt 175 €/m³), bei 60.000 m³ ≈ 18 % höher (68 statt 57 €/m³). **Achtung:** das KWW gilt für
  20.000–200.000 m³; für das kleine Netz (1.000–6.000 m³) wird die Kurve extrapoliert (Sensitivität
  `ptes.kosten_faktor`).
  **Lebensdauer 30 a** (vorher 25; KWW: „mittlere Lebensdauer, Abdeckung muss deutlich früher erneuert werden“,
  Unsicherheit ±40 %). Bei 20 a Betrachtungszeitraum wirkt der Restwert (VDI 2067); Sens. 20/40 a. O&M 0,5 %
  (KWW: 0,4–0,75 %). Das KWW nennt für TTES (Behälter) 40 a und 500–650 €/m³ – hier nicht relevant.
- *Trasse* (Tab. 36/37): €/m aus Tiefbau (Mittel min./max.) + Rohrmaterial, gewichtet mit der Rohrdimensions-
  verteilung der Netzberechnung (`scripts/kww_trasse.py`): **klein 653 €/m Straße / 322 €/m Grün** (vorher 550/250),
  **groß 1.143 / 644 €/m**: das große Netz braucht Rohre bis DN 250 (KMR) und ist je m fast doppelt so teuer.
  Anteil Straße weiter 80 % (Teamvorgabe).
**Nicht im Basisfall** (Szenarien `kww_komplett`, `kww_komplett_gross`): Luft-WP 1.730 €/kW (1 MW) bis 1.340 €/kW
(10 MW) gegenüber 1.000 €/kW (Frederikssund, DK) im Basisfall, 28 a Lebensdauer, O&M 3 %; PtH 340 €/kW (2 MW) bzw.
160 €/kW (Elektrodenkessel, 15 MW); Gaskessel; Netz-Lebensdauer 30 a (KWW) statt 40 a. Grund: Die WP-Kosten
verändern das Ergebnis stark und das KWW enthält keine Sole-/Speicher-WP; das Team soll bewusst entscheiden.
**Hausanschluss** bleibt bei 10.000 € je Anschluss (inkl. Übergabestation): KWW Hausstation 5.000–9.600 € (10–60 kW)
+ Hausanschlussleitung 12 m (3.000–6.500 € je nach Terrain) = 8.000–16.000 € – passt. Im großen Netz mit 54 %
Nichtwohngebäuden eher oberes Ende (Sensitivität `netz.kosten_hausanschluss`).
**Alle Erträge, Wirkungsgrade und Speicherverluste des KWW werden nicht übernommen.**

### E33 Netzfälle klein/groß, getrennte Ausgaben, zentrale Parameterübersicht (10.11.2026)
- **Netzfall** = `config/netze/<netz>.yaml` (nur Abweichungen von `base.yaml`): `klein` (Basis, ohne Datei) und
  `gross` (877 Gebäude, Last/Verluste/Spitze aus `results_gross.xlsx`, Trasse 14.291 m, 877 Anschlüsse, Fläche
  80.000 m², Kollektorkosten, Trassenkosten, Speicher-Stützstellen bis 130.000 m³). Aufruf `--netz gross`; Szenarien
  lassen sich mit `+` kombinieren (`--szenario kww_komplett_gross+strom_day_ahead_2024`). Das ist die einfachste
  Lösung, die beide Netze ohne Codeverzweigung abbildet: kein Modellcode kennt „klein“ oder „groß“.
- **Ausgaben getrennt:** `results/<netz>/<zeit>_<szenario>_<label>/` und `data/processed/<netz>/<szenario>/`
  (bestehende Läufe nach `results/klein/` verschoben); `config.yaml`/`meta.json` enthalten das Netz.
- **Spitzenlast:** wie beim kleinen Netz die Stundensumme (15,5 MW); die Zusammenfassung nennt 11,47 MW „inkl.
  Gleichzeitigkeitsfaktor“ (0,4537). Für PtH-Reserve und Gaskessel wäre das knapp 26 % weniger Leistung – bewusst
  konservativ gelassen (Sensitivität `pth.redundanz`).
- **Zentrale Übersicht** `docs/eingangsparameter.md` (`uv run serts uebersicht`): aus der Config erzeugt, beide Netze
  nebeneinander mit Status und Kurzquelle, gruppiert in Netz, Energiepreise, Wirtschaftlichkeit, Investitionen/
  Lebensdauern, Technik, plus PTES-Kostenkurve. Vollständige Liste weiterhin `docs/annahmen.md`.

### E34 Temperaturkennlinie des Speichers: Direktentladung nur bei dicker heißer Schicht (10.11.2026)
**Anlass (TEAM):** Der Speicher speiste auch im Januar/Februar direkt ins Netz ein, obwohl seine Temperatur weit unter
dem Vorlauf lag; die Speicher-WP lief im Winter kaum, der Speicher wurde nie richtig entladen. In Dronninglund hat die
Oberschicht im Dezember nur noch ≈ 50 °C.
**Erste Fassung (verworfen):** Kennlinie über den Füllstand des *ganzen* Speichers, im LP als
p_direkt · 0,1 h ≤ E(t) − s_min · E_nom. Zwei Fehler: (1) der kalte Teil (Wasser 10–45 °C) zählte mit und hielt als
„Ballast“ den Füllstand hoch – der kalte Teil blieb im Winter voll, die Speicher-WP lief nicht; (2) weil p ≥ 0 ist,
erzwingt die Ungleichung E(t) ≥ s_min · E_nom in **jeder** Stunde – der Speicher konnte nie unter ≈ 40 % entladen
werden.
**Jetzt:** Heißes Wasser liegt oben, darunter eine Übergangszone (Thermokline). Direkt ins Netz (T_VL + 5 K) geht es
nur, wenn die **heiße Schicht** dicker ist als diese Zone: Inhalt des heißen Teils zu Beginn der Stunde ≥
`ptes.schicht_min` (0,3) × Kapazität des heißen Teils. 0,3 ≈ 5 m Übergangszone bei 16 m Tiefe (Dronninglund,
Simulationsstudie; Annahme, Tornado 0/0,15/0,5). Eine solche Schwelle („erst ab …“) ist im LP nicht linear
(braucht Binärvariablen). Gelöst mit **zwei Läufen** in `network.optimize`: (1) ohne Kennlinie rechnen; (2)
Direktentladung nur in den Stunden erlauben, in denen sie in Lauf 1 bei dicker heißer Schicht stattfand, und in
genau diesen Stunden die dicke Schicht als lineare Bedingung verlangen (E_heiß(t−1) ≥ 0,3 · E_heiß,nom, auch bei
optimiertem Volumen linear). Ergebnis ist immer physikalisch gültig, aber leicht konservativ (Stunden, die erst in
Lauf 2 sinnvoll wären, bleiben gesperrt). Ein iteratives Sperren (bis 8 Durchgänge) wurde getestet und verworfen:
es konvergierte nicht (Rest ≈ 100 MWh Direktentladung bei dünner Schicht). Kontrollwert `kennlinie_rest_MWh` in
`kpi.json`. Unter der Schwelle bleibt die Wärme über die Speicher-WP nutzbar (Link `umlagern` heiß → kalt).
**Temperaturen (Kennlinie, nur Anzeige):** Mittel = T_unten + 35 K · s_kalt + 40 K · s_heiß; oben = T_unten +
35 K · min(1, s_kalt/0,3) + 40 K · min(1, s_heiß/0,3). Plausibilität Dronninglund-Dezember (kalt 25 %, heiß 5 %) →
oben ≈ 46 °C. In `zeitreihen.csv` (`T_speicher_oben`, `T_speicher_mittel`) und im Jahresverlauf (eigenes Feld; die
Außentemperatur ist dort entfallen, sie wurde mit der Speichertemperatur verwechselt).
**Maximaltemperatur:** im Modell 85 °C (`ptes.T_oben`, Liner-Grenze, Vorgabe). Werte über 85 °C gibt es nicht; in der
alten Grafik lag die Speicherinhalts-Fläche (MWh) über der Temperaturachse und sah wie > 90 °C aus.

### E35 Luft-WP: COP nach KWW-Ansatz statt Lorenz (10.11.2026)
**Anlass (TEAM):** Die Luft-WP wirkte zu effizient. **Prüfung:** Der Briefing-Ansatz (Lorenz mit logarithmischen
Mitteltemperaturen 45 → 80 °C, Gütegrad 0,5) ergab für 2022 eine Arbeitszahl von **2,65** (bei 7 °C Quelle: COP 2,66).
Das KWW (Tab. 24/25) rechnet COP = Gütegrad · T_VL / (T_VL − T_Quelle) mit 46 % (70 °C) bzw. 44 % (95 °C) und kommt
so auf JAZ 2,5 bzw. 1,8 bei 7 °C Heizperiodenmittel. Für 80 °C (linear 45,2 %) → **COP 2,19 bei 7 °C**, Arbeitszahl
2022 **2,22** (−16 %). Das Referenzjahr ist nicht die Ursache: Heizperiode 2022 (Okt–Apr) 6,4 °C gegen 5,5 °C im Mittel
1992–2021 (DWD 03028) → nur ≈ 1 % günstiger.
**Umsetzung:** `waermepumpe.cop_ansatz_luft = kww` (Basis), `lorenz` als Vergleich; `guetegrad_faktor` (1,0; Tornado
0,85/1,15). Im KWW-Ansatz kein zusätzlicher Abtauabschlag (Annahme: im Gütegrad enthalten). Die Speicher-WP bleibt
bei COP 4,5 (Marstal gemessen 5–5,5; KWW Sole/Wasser 50 K: JAZ 3,9) – damit ist sie im Winter rund doppelt so
effizient wie die Luft-WP (≈ 1,9–2,2), was ihre Nutzung im Winter erklärt.

### E36 Speicherschichtung konsistent: kalter Teil relativ ≥ heißer Teil (10.11.2026)
Im Zwei-Teile-Modell konnte die Speicher-WP den kalten Teil leeren, während der heiße Teil noch voll war – physikalisch
unmöglich, weil heißes Wasser seinen Anteil 10–45 °C immer mit enthält. Die Kennlinie zeigte dann z. B. 50 °C oben
bei erlaubter Direktentladung. Neue lineare Bedingung in jeder Stunde: E_kalt(t) ≥ (1−f)/f · E_heiß(t) (gleicher
relativer Füllstand oder mehr im kalten Teil). Die WP kann Wärme aus dem heißen Teil weiterhin nutzen – erst über
`umlagern` (das Wasser kühlt dabei unter 45 °C ab). Mini-Netz-Test `test_schichtung_konsistent`.

### E37 BEW Modul 2 in jedem Lauf ausgewiesen, Vergleichsvarianten (10.11.2026)
- **Ausweis:** Jeder Lauf rechnet für dieselbe (ungefördert optimierte) Auslegung zusätzlich die Kosten mit 40 %
  Investitionszuschuss auf die förderfähigen Teile (Kollektor, PTES, WP, Trasse; nicht PtH/Hausanschluss) inkl.
  Nebenkosten: `lcoh_bew`, `lcoh_inkl_netz_bew`, `zuschuss_bew_EUR` (Kommandozeile, `kpi.json`, Kostengrafik).
  `oekonomie.bew_ausweis_quote` = 0,4. **Obergrenze:** der tatsächliche Zuschuss ist auf die
  Wirtschaftlichkeitslücke begrenzt (BAFA-Berechnung, nicht modelliert) – ist das System schon ohne Förderung
  günstiger als die fossile Referenz, kann die Lücke kleiner sein. Modul 4 (Betriebskostenförderung) nicht enthalten.
- **Mit Förderung optimiert:** Szenario `bew_modul2` (Förderquote 0,4 wirkt auf die Auslegung).
- **Vergleichsvarianten** (Briefing §1 Pflicht 5): `uv run serts varianten [--netz gross]` rechnet Basis, ohne Speicher,
  nur WP + PtH und mit BEW (optimiert), jeweils mit Gas-Fernwärme als Referenz → `varianten.md/.csv` und
  `pareto.png` (EE-Anteil gegen Wärmepreis). PV für die WP (5c) ist nicht modelliert (Abschätzung in `ausblick.md`).

### E38 WP-Kosten: unteres Ende des KWW, Heatmap, Weitergabe (10.11.2026)
- **WP-Kosten** (Team): 1.340 €/kW_th = unteres Ende des KWW (Tab. 24, 10-MW-Klasse) für Luft- und Speicher-WP,
  statt 1.000 €/kW (Frederikssund, DK). Für das kleine Netz (≈ 1 MW, KWW-Klasse 1.730 €/kW) optimistisch;
  Lebensdauer/O&M bleiben 20 a / 2,5 % (KWW 28 a / 3 %). Tornado-Spanne 1,0 / 1,73 Mio. €/MW.
  **Tornado und Varianten in `docs/ergebnisse*.md` sind noch mit 1.000 €/kW gerechnet**; Strom-Vergleich und Heatmap
  vom 10.11. abends bereits mit 1.340 €/kW.
- **Heatmap** (Briefing Pflicht 6): `uv run serts heatmap [--netz gross]` rechnet 5 × 5 feste Größen (Raster in
  `heatmap.*`, je Netz), WP und PtH je Punkt optimiert, Punkte über der Fläche entfallen; ≈ 50 s je Punkt.
- **Weitergabe** (README): `.venv` nie mitgeben (absolute Pfade), `.python-version` = 3.12, `uv.lock` legt alle
  Paketversionen fest; PVGIS- und Strompreisdateien jetzt im Git (klein), DWD weiter per `import-raw`; `import-raw`
  übernimmt Dateien aus dem Repo, wenn die Quelle fehlt, und überspringt die (optionale) Netzkarte. Die CLI gibt UTF-8
  aus (Windows-Konsole). Speichermodell für Einsteiger: `docs/speichermodell.md`.

### E39 Speicher in drei Teilen, ein Lauf; Größenabhängigkeit; Leistungspreis, Einfallswinkel, gleitender Vorlauf (14.11.2026)
**Anlass:** Review `docs/review_ptes_wp.md` (TEAM-Auftrag). Der Speicher war im Modell fast nur WP-Quelle
(Direktanteil der Entladung 21 %, Dronninglund 52–63 %; Mai–September 645 MWh über die Speicher-WP).
**Speicher (ersetzt E34, ändert E27/E36):**
- *Laden getrennt:* `laden_kalt` (10 → 45 °C) und `laden_heiss` (45 → 85 °C) statt eines Links mit festem
  Verhältnis 53 : 47. Vorher konnte bei vollem kalten Teil nicht nachgeladen werden, bis die WP unten Platz schuf.
- *Übergangszone als eigener Teil* statt Schwelle mit zwei Läufen: heißer Teil = Kern + Übergangszone;
  Schichtung Füllstand Kern ≤ Übergangszone ≤ kalt (linear, ein Lauf). Direkt ins Netz geht nur der Kern.
  Das ist die engste lineare Form der alten Schwelle; bei fast leerem Speicher etwas großzügiger.
- *Vorwärmen:* die Übergangszone darf den Rücklauf vorwärmen (45 → 60 °C), wenn WP/PtH in derselben Stunde
  nachheizen (≤ 0,75 MW je MW Nachheizung; aus den Temperaturen abgeleitet, kein neuer Zahlenwert). `ptes.vorwaermen`.
- *Übergangszone 0,15 bei 60.000 m³* (`ptes.uebergang_ref`, vorher `schicht_min` 0,3 ungeprüft) aus den Messdaten
  Dronninglund 2014; *Einschichtanteil* 0 (`ptes.einschicht_anteil`): die Nachrechnung 2015–2017 trifft damit alle
  Jahreswerte, Direktanteil 61 % (`docs/validierung_dronninglund.md`).
- *Größenabhängig* (`ptes.groessen_exponent` = −1/3): Verlustrate und Übergangszone × (V/60.000)^(−1/3); bei
  optimiertem Volumen für die Untergrenze des Kostensegments (vorsichtig; erstes Segment: Mitte; Sprünge an den
  Segmentgrenzen in Kauf genommen). Bei
  7.400 m³: Verlust 8·10⁻⁵ 1/h (vorher 4·10⁻⁵), Übergangszone 0,30.
**Rechenzeit:** ein LP je Kostensegment statt zwei (≈ 50 s je Lauf, vorher 2 × ≈ 22 s) – unverändert.
**Weitere Punkte:**
- *Leistungspreis* (`strom.leistungspreis` 15,50 €/kW·a, Westfalen Weser Netz 2025, Mittelspannung < 2.500 h/a):
  im Netz als Kosten der Anschlussleistung (Link `netzanschluss`), keine eigene Bedingung. Netzentgelt-Arbeitspreis
  aus demselben Preisblatt: 79,9 statt 93 €/MWh (fester Tarif bleibt 300 €/MWh, Day-Ahead wird 13 €/MWh günstiger).
- *Einfallswinkel* (`kollektor.iam_b0` 0,1, ASHRAE, nur Direktstrahlung): Ertrag −3 % (533 → 517 kWh/m² bei 67,5 °C).
- *Gleitender Vorlauf* als Szenario `vl_gleitend` (`netz.T_VL_min` 70): 80 °C bei ≤ −10 °C, 70 °C ab 15 °C
  (24-h-Mittel). Wirkt nur auf den COP der Luft-WP (lastgewichtet 2,25 → 2,49). Basis bleibt 80 °C (Teamvorgabe).
- *WP/PtH laden den Speicher* (`ptes.laden_aus_netz`, Link `laden_netz` Wärmeknoten → Kern): Basis aus (E29 gilt
  weiter für den festen Tarif), in den Szenarien `strom_day_ahead_*` an. Solaranteil zählt Speicherwärme dann nur
  anteilig als solar.
**Nicht umgesetzt:** Laden des kalten Teils bei niedriger Kollektortemperatur (höherer Ertrag; braucht eine zweite
Zeitreihe und eine Flächenbedingung je Stunde).
**Folge:** Alle Ergebnisse vor dem 14.11.2026 (Heatmap, Varianten, Tornado, Netz groß) sind mit dem alten Speicher
gerechnet und müssen neu laufen; `kpi.json` enthält statt `kennlinie_*` jetzt `uebergang_anteil`,
`verlustrate_1_h`, `speicher_direktanteil`, `P_netzanschluss_MW`, `kosten_a_strom_leistung`.

## E40 Tornado-Variante „keine Flächenbegrenzung" (15.11.2026)

`standort.flaeche_verfuegbar` hat `sens: [.inf]`; bei `.inf` entfällt die Flächenbedingung (constraints.py, Test
`test_ohne_flaechenbegrenzung`). Das Volumen bleibt durch das letzte Kostensegment auf 35.000 m³ begrenzt. Fläche
kostet im Modell nichts (keine Pacht, kein Kauf), die Variante ist also eine Obergrenze für den Nutzen von mehr
Fläche. Heatmap-Raster Volumen auf das neue Optimum gelegt (5.500/7.000 → 6.000/8.000 m³).
**Ergebnis (15.11., Netz klein):** ohne Grenze 11.400 m² / 33.400 m³, Saisonspeicher (1,45 Zyklen, 70 % Winter),
Solaranteil 92 %, Wärmepreis 226 statt 243 €/MWh, Flächenbedarf ≈ 38.900 m² (`docs/ergebnisse.md`, Tornado).
**Netz groß (15.11.):** ohne Grenze kein inneres Optimum – das Volumen läuft an die letzte Stützstelle (130.000 m³,
nachgerechnet bis 200.000 m³ = Gültigkeitsgrenze KWW: 72.900 m², 73 % solar, 186 statt 222 €/MWh, 24 ha).
`ptes.segmente_m3` Netz groß bleibt bei 130.000 m³ (Basis bindet die Fläche ohnehin).

## E41 Boosting, zwei Wärmepumpen, COP nach Jensen, Durchflussgrenze (21.11.2026)

Anlass: Vergleich mit Schauß et al. 2026 (`docs/vergleich_schauss2026.md`).
- *Direktentladung/Boosting:* Ist der Kern kälter als Vorlauf + 5 K (`ptes.T_oben` < 85 °C oder gleitender Vorlauf
  darüber), braucht jede MWh Direktentladung α(t) = (T_VL(t) + 5 − T_oben)/(T_oben − T_RL) MWh Nachheizen durch
  WP/PtH in derselben Stunde (Paper Gl. 4a). Zusammen mit dem Vorwärmen in einer Bedingung (constraints.py Nr. 5).
  Basis 85 °C: α = 0, Ergebnis unverändert. Vorher ging der Kern bei T_oben < 85 °C unphysikalisch direkt ins Netz.
  `ptes.T_oben` (80/90 °C) jetzt im Tornado.
- *Zwei Wärmepumpen:* Luft-WP (`wp_luft_out`, KWW Tab. 24, 1.340 €/kW) und Speicher-WP (`wp_speicher_out`,
  Wasser/Wasser, KWW Tab. 26/27 auf 64 K Hub interpoliert: 1.100 €/kW) mit eigener Leistung statt einer gemeinsamen
  `wp_out`. `P_WP_MW` in kpi.json = Summe; neu `P_WP_luft_MW`, `P_WP_speicher_MW`.
- *COP Speicher-WP nach Jensen et al. 2018* (Ammoniak, Pinch 5 K, isentrop 0,8; Umsetzung PyPSA-Eur), Temperaturen
  wie Schauß et al.: Senke Rücklauf → Vorlauf, Quelle (T_RL + T_unten)/2 → 6 K kälter. Reproduziert Fig. S7 des
  Papers auf ±0,02. Basis 3,91 statt fest 4,5 (`waermepumpe.cop_ansatz_speicher`; `fest` für die Validierung
  Dronninglund). Luft-WP bleibt KWW (Jensen ohne Abtauen ≈ 30 % höher; Option `cop_ansatz_luft: jensen`).
- *Durchfluss* (`ptes.austauschrate` 0,0094 1/h): Volumenstrom je Richtung ≤ Rate × V, Wärme / (c × Spreizung je
  Temperaturband; WP-Quelle 6 K). Rate = höchster Stundenwert durch die Diffusoren in Dronninglund 2014 (565 m³/h bei
  60.000 m³). Gemessener Höchstwert, keine Auslegungsgrenze; `.inf` = aus.
**Wirkung Netz klein (Basis):** 4.670 m² / 6.000 m³ wie vorher; WP 0,84 MW Luft + 0,15 MW Speicher; Wärmepreis
244,5 statt 243,4 €/MWh inkl. Netz (LCOH 150,9). **Netz groß:** 29.240 m² / 33.780 m³, WP 8,65 + 1,09 MW, 223,1 statt 221,6 €/MWh.
Voller Tornado nicht neu gerechnet (Wirkung klein); stattdessen Vorlauf-Sensitivität 70–90 °C fest und gleitend bis
60/70 °C: −14 bis +5 €/MWh, fast nur über COP/Strom, Boosting über 80 °C ≤ 415 MWh/a (Tabellen in
`docs/ergebnisse.md`, `docs/ergebnisse_netz_gross.md`).

## E42 Rechenzeit Tornado (22.11.2026)

- *Tornado-Liste gekürzt:* `ptes.uebergang_ref`, `waermepumpe.luft_leistung_bei_tmin` und `ptes.groessen_exponent`
  fliegen raus (Tornado 15.11.: höchstens ±0,2 / +0,1 / −3,0 €/MWh klein, ±0,03 / +0,1 / −0,4 groß). Die Parameter
  bleiben in `config/base.yaml` mit ihren `sens`-Werten; einzeln weiter mit `serts tornado --parameter ...`.
- *Nur Nachbarsegmente:* Die Basis rechnet alle Kostensegmente des Speichers. Jede Tornado-Variante rechnet nur das
  Gewinnersegment der Basis und seine Nachbarn (`run.loese(start_segment=...)`). Liegt das Optimum am Rand dieser
  Auswahl, kommt so lange das nächste Segment dazu, bis es innen oder am ersten/letzten Segment liegt. Fehlt dadurch
  ein Optimum, dann nur, wenn die Kosten über die Segmente mehr als ein Tal haben (bisher nicht beobachtet).
- *Parallel und niedrige Priorität:* Die Basis rechnet ihre Segmente parallel; Tornado standardmäßig 6 statt 4
  parallele Läufe (8 Kerne, 32 GB). `run`, `tornado`, `varianten`, `heatmap` laufen mit niedriger Prozesspriorität
  (Windows BELOW_NORMAL), damit der Rechner bedienbar bleibt; ein freier Rechner wird trotzdem voll genutzt.
**Wirkung:** Vorlauf-Sensitivität Netz klein (7 Läufe) 14,5 statt 49 min, alle Ergebnisse identisch
(`results/klein/20261122-114029_base_sensitivitaet`).
**Nachtrag 22.11.2026:** `ptes.groessen_exponent` wieder im Tornado (Wirkung 15.11. −3,0 €/MWh klein, nicht
vernachlässigbar; die Auswahl hatte nur die Spanne zwischen sens-Werten verglichen, bei einem sens-Wert also 0).
Vorlauf jetzt fester Teil des Tornados: `netz.T_VL` 70/90 °C fest, `netz.T_VL_min` gleitend 80 → 60/70 °C
(75/85 °C nur noch einzeln, Ergebnisse 21.11.). Segmentsuche: sind Startsegment und Nachbarn alle unzulässig
(z. B. Variante mit weniger Fläche), rechnet sie die übrigen Segmente, statt abzubrechen.
