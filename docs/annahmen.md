# Annahmentabelle

> Automatisch erzeugt aus `config/base.yaml` mit `serts annahmen`. Nicht von Hand ändern.

Status: belegt 39, vorgabe 53, annahme 45, offen 0


## standort

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `standort.name` | Bad Lippspringe | - | belegt | KWP-NRW Kommunenpaket 05774008 (Ordner Bad Lippspringe/KWP-NRW_...) |  |  |
| `standort.ags` | 05774008 | - | belegt | KWP-NRW Dateinamen |  |  |
| `standort.dwd_station_id` | 3028 | - | belegt | DWD CDC, Station 'Lippspringe, Bad' (Metadaten_Stationsname_03028.txt) |  |  |
| `standort.lat` | 51.7854 | deg | belegt | DWD Metadaten_Geographie_03028.txt (gültig ab 02.08.2006) |  |  |
| `standort.lon` | 8.8388 | deg | belegt | DWD Metadaten_Geographie_03028.txt |  |  |
| `standort.hoehe` | 157 | m | belegt | DWD Metadaten_Geographie_03028.txt |  |  |
| `standort.flaeche_verfuegbar` | 13000 | m2 | vorgabe | TEAM: ca. 13.000 m2 Grundstück am Erzeugerstandort, annähernd quadratisch | inf | Muss Kollektorfeld (inkl. Reihenabstand, Technik) UND PTES aufnehmen -> Flächencheck je Rasterpunkt. Sensitivität .inf = keine Flächenbegrenzung (Speicher dann nur durch ptes.segmente_m3 bis 35.000 m3 begrenzt). |

## zeit

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `zeit.wetterjahr` | 2022 | a | belegt | NB Blatt Lastprofil: Zeitstempel 2022-01-01 00:00 bis 2022-12-31 23:00 (8760 h) |  | TEAM: NB-Lastgang beruht auf Wetter Münster 2022; Modell nutzt DWD Bad Lippspringe 2022 (gleiches Jahr, Nachbarregion). |
| `zeit.zeitzone` | UTC | - | annahme | DWD-Stundenwerte sind UTC (Metadaten_Parameter). Zeitbasis des NB-Lastgangs nicht dokumentiert -> als UTC behandelt. |  | Fehler max. 1-2 h Phasenversatz, für Jahresbilanz irrelevant. |
| `zeit.stunden` | 8760 | h | vorgabe | BRF §2 |  |  |

## last

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `last.datei` | bad_lippspringe/results netzberechnung.xlsx | - | belegt | NB (relativ zu data/raw) |  |  |
| `last.Q_gebaeude` | 4525.1 | MWh/a | belegt | NB Lastprofil, Summe Spalte 'Summe aller Gebäudetypen' (Zusammenfassung: 4525,2; 159 Gebäude) |  | Kontrollwert; das Modell nutzt die Zeitreihe. Test prüft Übereinstimmung. |
| `last.Q_netzverlust` | 937.3 | MWh/a | belegt | NB Lastprofil, Spalte 'Verlust' (konstant 0,107 MW; Zusammenfassung 935,4), gerechnet bei 80/50 degC | 849.7 | 849,7 MWh/a = Variante extra Dämmung (Szenario netz_daemmung). |
| `last.netzverlust_variante` | standard | - | vorgabe | Basis = Standarddämmung; extra Dämmung als Variante | extra_daemmung |  |
| `last.P_max_kontrolle` | 1.592 | MW | belegt | NB Lastprofil, Max. 'Gesamtsumme' am 21.01.2022 07:00 |  |  |
| `last.skalierung` | 1 | - | vorgabe | unveränderter Lastgang; Sensitivität Lastprofil/-höhe über Szenario | 0.8, 1.2 |  |
| `last.ankerkunde_anteil` | 0 | - | vorgabe | BRF §3.5: Anteil 0/20/40 % von Q_a. Basis 0, da Gewerbe (GMK, GKO = 29 % von Q_gebaeude) im NB-Lastgang bereits enthalten | 0.2, 0.4 | Anteil bezogen auf Q_gebaeude, wird ZUSÄTZLICH zum NB-Lastgang addiert. |
| `last.ankerkunde_profil` | band | - | vorgabe | BRF §3.5 | werktag, saisonal |  |

## netz

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `netz.T_VL` | 80 | degC | vorgabe | TEAM: Netz bleibt bei 80 degC Vorlauf wie in der NB (ersetzt BRF-Wert 75 degC) | 75 |  |
| `netz.T_VL_min` | 80 | degC | vorgabe | Basis = konstanter Vorlauf (TEAM). Kleiner als T_VL -> gleitender Vorlauf: T_VL bei Tagesmittel <= gleit_T_kalt, linear fallend auf T_VL_min bei >= gleit_T_warm (Szenario vl_gleitend) | 70 | Wirkt nur auf den COP der Luft-WP (heatpump.py). Speicher (Direktentladung ab T_VL + 5 K) und Netzverluste rechnen weiter mit T_VL -> eher vorsichtig. |
| `netz.gleit_T_kalt` | -10 | degC | annahme | übliche Heizkurve Fernwärme: volle Vorlauftemperatur bei Auslegungs-Außentemperatur (Größenordnung -10 bis -12 °C) |  |  |
| `netz.gleit_T_warm` | 15 | degC | annahme | übliche Heizkurve: Mindest-Vorlauf ab Heizgrenze ≈ 15 °C (Sommer: Trinkwarmwasser) |  |  |
| `netz.T_RL` | 45 | degC | vorgabe | BRF §2 (TEAM: Rücklauf frei '80/x'); NB rechnet 50 degC | 40, 50 |  |
| `netz.T_VL_netzberechnung` | 80 | degC | belegt | NB Zusammenfassung, Spalte Vorlauftemp |  |  |
| `netz.T_RL_netzberechnung` | 50 | degC | belegt | NB Zusammenfassung, Spalte Ruecklauftemp |  |  |
| `netz.trassenlaenge` | 2432 | m | belegt | NB Zusammenfassung, Summe Trassenlänge (ohne Hausanschlüsse 3413 m) |  |  |
| `netz.hausanschluesse` | 159 | Stück | belegt | NB Zusammenfassung, Anzahl Hausanschlüsse (EFH 119, MFH 38, GHA 2); Hausanschlusslänge gesamt 3.413 m |  |  |
| `netz.netzkosten_einbeziehen` | True | - | vorgabe | TEAM 09.11.2026: Netzkosten in die LCOH einbeziehen (zusätzlich zur LCOH der Erzeugung ausgewiesen) |  |  |
| `netz.anteil_strasse` | 0.8 | - | vorgabe | TEAM: Großteil der Trasse unter Straßen, Rest 'grüne Wiese' – Verhältnis nachsteuerbar | 0.5, 1 |  |
| `netz.kosten_trasse_strasse` | 650 | EUR/m Trasse | belegt | KWW Tab. 36/37 (2026, netto): Tiefbau befestigtes Terrain (Mittel aus min./max.) + Rohrmaterial, gewichtet mit der Längenverteilung je Rohrdimension der Netzberechnung (PEX 20-100, KMR 100-250): 653 EUR/m, Spanne 366-940 (scripts/kww_trasse.py) | 370, 940 | Vorher 550 EUR/m (Manderfeld/Borderstep 2012 x 1,6). Größere Rohre sind teurer: Netz groß 1.140 EUR/m (config/netze/gross.yaml). docs/entscheidungen.md E32. |
| `netz.kosten_trasse_gruen` | 320 | EUR/m Trasse | belegt | KWW Tab. 36/37 (2026, netto): Tiefbau unbefestigtes Terrain (Mittel aus min./max.) + Rohrmaterial, gewichtet wie oben: 322 EUR/m, Spanne 241-403 (scripts/kww_trasse.py) | 240, 400 | Vorher 250 EUR/m (Manderfeld/Borderstep 2012 x 1,6). Netz groß 640 EUR/m. |
| `netz.kosten_hausanschluss` | 10000 | EUR/Stück | annahme | Hausanschlussleitung + Übergabestation EFH: 5.000-15.000 EUR (co2online via Finanztip; 42watt), Mitte 10.000 EUR | 5000, 15000 | Wird in der Praxis oft über Baukostenzuschüsse/Hausanschlusskosten von den Kunden getragen. |

## ptes

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `ptes.c_wasser` | 0.001163 | MWh/(m3 K) | belegt | rho*cp Wasser ≈ 1000 kg/m3 * 4,187 kJ/(kg K) = 1,163 kWh/(m3 K); BRF §3.2 |  | Bei 45-85 degC rho*cp ≈ 1,14-1,15 kWh/(m3 K) (-1...-2 %); vernachlässigt. |
| `ptes.T_oben` | 85 | degC | vorgabe | BRF §3.1; Liner-Grenze (Xiang et al. 2022) | 90 | Direktentladung braucht T_oben >= T_VL + 5 K = 85 degC -> bei VL 80 genau an der Grenze. |
| `ptes.T_unten` | 10 | degC | vorgabe | BRF §3.1; DRL Tmin 9-12 degC |  |  |
| `ptes.verlustrate` | 4e-05 | 1/h | annahme | BRF §3.2 Startwert, abgeleitet aus DRL (Verluste / mittl. Inhalt ≈ 2.800 MWh) | 1.5e-05, 8e-05 | Gilt bei ptes.V_ref (60.000 m3 = DRL). Für andere Größen x (V/V_ref)^groessen_exponent: z. B. 7.400 m3 -> 8e-5, 1.750 m3 -> 1,3e-4 (docs E39). |
| `ptes.groessen_exponent` | -0.3333 | - | annahme | Geometrie: Oberfläche/Volumen ~ V^(-1/3) (Verluste) und Tiefe ~ V^(1/3) (Dicke der Übergangszone bleibt in Metern gleich) bei ähnlicher Form; eigene Abschätzung (docs E10, E39) | 0 | Wirkt auf ptes.verlustrate und ptes.uebergang_ref. 0 = größenunabhängig (altes Verhalten). Bei optimiertem Volumen gilt die Untergrenze des Kostensegments (erstes Segment: Mitte). |
| `ptes.uebergang_ref` | 0.15 | - | belegt | Messdaten Dronninglund 2014 (PitStorages/DronninglundData, 32 Temperaturfühler, eigene Auswertung docs/validierung_dronninglund.md): Wärme des heißen Bands (über 40 °C), die in Wasser unter 75-80 °C steckt = Median 12-16 % der Kapazität des heißen Teils (P10-P90: 5-30 %) | 0, 0.1, 0.25 | Anteil der Übergangszone am heißen Teil bei ptes.V_ref. Größenabhängig (groessen_exponent): 7.400 m3 -> 0,30. Direkt ins Netz geht nur der Kern darüber. 0 = ideale Schichtung. Ersetzt ptes.schicht_min (docs E39). |
| `ptes.uebergang_max` | 0.8 | - | annahme | Obergrenze für sehr kleine/flache Speicher (unter ≈ 400 m3), damit ein Kern übrig bleibt; rechnerische Grenze |  |  |
| `ptes.einschicht_anteil` | 0 | - | annahme | Anteil der heiß geladenen Wärme, der sich beim Einschichten mit der Übergangszone mischt. Kalibriergröße gegen den Direktanteil der Speicherentladung in Dronninglund (docs/validierung_dronninglund.md) | 0.1, 0.2 |  |
| `ptes.vorwaermen` | True | - | vorgabe | Wasser der Übergangszone (≈ 65 °C) wärmt den Rücklauf auf ≈ 60 °C vor, WP/PtH heizen in derselben Stunde auf Vorlauf nach (übliche Betriebsweise). false = Übergangszone nur über die Speicher-WP nutzbar (docs E39) | False |  |
| `ptes.laden_aus_netz` | False | - | vorgabe | false = der Speicher nimmt nur Solarwärme auf (docs E29). true = WP und PtH dürfen den heißen Teil laden; sinnvoll nur bei zeitvariablem Strompreis (Szenarien strom_day_ahead_*) | True |  |
| `ptes.direkt_dT` | 5 | K | vorgabe | BRF §3.1: Direktentladung braucht T_oben >= T_VL + 5 K (Wärmeübertrager/Übergabe) |  |  |
| `ptes.kosten_ref` | 67.77 | EUR/m3 | belegt | KWW Tab. 52 (Erdbeckenspeicher): Kostenkurve Invest = 1093,6 * V^0,7472 (2026, netto) bei V_ref = 60.000 m3 -> 67,8 EUR/m3; Stützwerte 20.000 m3 90, 50.000 m3 70, 100.000 m3 60, 200.000 m3 50 EUR/m3 |  | Frühere Basis (SIF/DRL 2014: 38,3 EUR/m3 bei 60.000 m3 x Index 1,5 = 57,5) liegt bei 60.000 m3 ≈ 15 % niedriger; bei 1.600 m3 praktisch gleich (175 vs. 168 EUR/m3). docs/entscheidungen.md E32. |
| `ptes.V_ref` | 60000 | m3 | belegt | Bezugsgröße der Kostenkurve (innerhalb der KWW-Stützwerte 20.000-200.000 m3) |  |  |
| `ptes.kosten_exponent` | -0.2528 | - | belegt | KWW Tab. 52: Invest ~ V^0,7472 -> spezifisch ~ V^-0,2528 | -0.2, -0.4 | Gültigkeit laut KWW 20.000-200.000 m3; darunter (Basisfall klein: 1.000-6.000 m3) extrapoliert -> unsicher, Sensitivität ptes.kosten_faktor. Marstal 10.000 m3 real ≈ 67 EUR/m3 (2014). |
| `ptes.preisindex` | 1 | - | vorgabe | KWW-Kosten gelten bereits für 2026 (netto, real) -> kein Index nötig (Preisbasis 2025/26 ≈ gleich) | 1.3 | Bei Rückgriff auf Preise älterer Projekte (DRL 2014) Index ≈ 1,5 einsetzen. |
| `ptes.segmente_m3` | [0, 1000, 2500, 6000, 12000, 35000] | m3 | vorgabe | Stützstellen der stückweise linearen Kostenfunktion C(V) = V * c(V) (stetig, konkav); je Segment ein LP-Lauf mit Grenzkosten und Fixkostenanteil (docs E30) |  | Obergrenze 35.000 m3 ≈ ganze Fläche. Mehr Stützstellen = genauer, aber ein Lauf mehr je Stelle. |
| `ptes.kosten_faktor` | 1 | - | vorgabe | Faktor auf die gesamte Speicherkostenkurve (Sensitivität Speicherkosten) | 0.7, 1.3 |  |
| `ptes.volumen_je_grundflaeche` | 2.65 | m3/m2 | annahme | DRL-Geometrie (Pyramidenstumpf 90/26 m, 16 m tief) ähnlich skaliert auf 8.700 m3: Oberkante 47 m, Tiefe 8 m; + 5 m Randstreifen -> 3.280 m2 Grund -> 8.700/3.280 | 2, 4 |  |

## kollektor

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `kollektor.typ` | flachkollektor | - | vorgabe | SCH A3 (wie DRL) |  |  |
| `kollektor.modell` | Großflächen-Flachkollektor mit Konvektionsfolie, Typ Arcon-Sunmark HTHEATstore 35/10 (wie DRL) | - | annahme | SIF Kap. 2: DRL nutzt Arcon 35/10 HEATstore mit Folie; Solar-Keymark-Zertifikat SP SC0843-14 |  | Keymark-Datenblatt war am 09.11.2026 nicht abrufbar (solarkeymark.nl Verbindung abgelehnt) -> eta0/a1/a2 unten sind Annahmen in der BRF-Bandbreite. |
| `kollektor.eta0` | 0.8 | - | annahme | Mitte der BRF-Bandbreite 0,75-0,82 für große Flachkollektoren; Bezug Bruttofläche | 0.75, 0.82 | Durch Keymark SP SC0843-14 ersetzen. Plausibilisierung: spez. Ertrag vs. BSW 430-500 kWh/(m2 a). |
| `kollektor.a1` | 2.4 | W/(m2 K) | annahme | BRF-Bandbreite 2-2,5 W/(m2 K), oberes Drittel (konservativ) |  |  |
| `kollektor.a2` | 0.012 | W/(m2 K2) | annahme | BRF-Bandbreite 0,01-0,016 W/(m2 K2) |  |  |
| `kollektor.T_m` | 67.5 | degC | vorgabe | BRF §3.3: mittlere Kollektortemperatur 50 -> 85 degC; ein Niveau für Direktnutzung und Speicherladen (docs E20) |  |  |
| `kollektor.iam_b0` | 0.1 | - | annahme | Einfallswinkel-Korrektur der Direktstrahlung nach ASHRAE: K = 1 - b0 * (1/cos(Winkel) - 1); b0 ≈ 0,1 ist der übliche Wert für einfach verglaste Flachkollektoren (K ≈ 0,94 bei 50°). Durch Keymark-Wert K(50°) ersetzen | 0, 0.15 | 0 = keine Korrektur (altes Verhalten). Diffusstrahlung bleibt unkorrigiert (einfach gehalten). |
| `kollektor.feldverluste` | 0.1 | - | annahme | BRF §3.3 Startwert | 0.05, 0.15 |  |
| `kollektor.neigung` | 35 | deg | annahme | TEAM: einfache Annahme; 35 deg = übliche Neigung großer Freiflächenfelder in DE/DK (Kompromiss Ertrag/Reihenabstand) | 25, 45 |  |
| `kollektor.azimut` | 180 | deg | annahme | Südausrichtung (pvlib-Konvention 180 = Süd), Standard bei Freifeldanlagen |  |  |
| `kollektor.flaechenfaktor` | 2.3 | m2 Grund / m2 Kollektor | belegt | BSW: 2- bis 2,3-fache Bruttokollektorfläche inkl. Reihenabstände und Heizzentrale (Berlin.de nennt ≈ 3) | 2, 3 |  |
| `kollektor.strahlung_skalierung` | 1 | - | vorgabe | Faktor auf die Strahlung (Sensitivität Solarressource) | 0.9, 1.1 | ±10 % ≈ Spanne strahlungsarmer/-reicher Jahre: DWD 03028 1992-2010 meist 850-1.056 kWh/m2 um den Median ≈ 960 (datenbasis §2). Jahr 2022: Szenario wetter_2022. |
| `kollektor.strahlungsquelle` | pvgis_tmy | - | vorgabe | TEAM 09.11.2026: Normaljahr als Basis. PVGIS-TMY (SARAH3, 2005-2023), auf 35 deg Süd umgerechnet (pvlib Perez). DWD-Strahlung 03028 endet 2011. | pvgis_sarah3 | pvgis_sarah3 = gemessenes, strahlungsreiches Jahr 2022 (Szenario wetter_2022). |
| `kollektor.kosten_spez` | 304 | EUR/m2 Brutto | belegt | KWW Tab. 21 (Flachkollektor Freifläche, 2026, netto): 330 EUR/m2 Apertur bei 5.000 m2 (Spanne 390 bei 500 m2 bis 300 bei 15.000 m2, Unsicherheit ±20 %) x 0,92 (Apertur/Brutto) = 304 EUR/m2 Brutto | 240, 380 | Größenklasse hier 5.000 m2 Apertur (Netz klein); Netz groß: config/netze/gross.yaml (15.000 m2 Apertur). Vorher 450 EUR/m2 (Bitterfeld-Wolfen, Planung 2020; DRL 164 EUR/m2 DK). Erträge aus dem KWW (450 kWh/m2) werden NICHT übernommen (eigene Rechnung, PVGIS). docs/entscheidungen.md E32. |

## waermepumpe

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `waermepumpe.approach` | 3 | K | vorgabe | BRF §3.4 (je Seite 3 K) |  |  |
| `waermepumpe.cop_ansatz_luft` | kww | - | vorgabe | KWW Tab. 24/25: COP = Gütegrad x T_VL / (T_VL - T_a) mit Gütegrad 46 % (70 °C) bzw. 44 % (95 °C), JAZ 2,5 bzw. 1,8 bei 7 °C Heizperiodenmittel; für 80 °C linear 45,2 % -> COP 2,19 bei 7 °C. Ersetzt den Lorenz-Ansatz des Briefings (der war ≈ 20 % optimistischer: Arbeitszahl 2022 2,65 statt 2,22). | lorenz | lorenz = Briefing-Ansatz (eta_G_luft, Abtauabschlag, logarithmische Mitteltemperaturen). Heizperiode 2022 (Okt-Apr) 6,4 °C, Mittel 1992-2021 5,5 °C (DWD 03028) -> Wetterjahr nur ≈ 1 % günstiger. docs/entscheidungen.md E35. |
| `waermepumpe.guetegrad_faktor` | 1 | - | vorgabe | Faktor auf den KWW-Gütegrad (Sensitivität; KWW-Unsicherheit der JAZ ±30 %) | 0.85, 1.15 |  |
| `waermepumpe.eta_G_luft` | 0.5 | - | annahme | BRF §3.4: Rückrechnung GEA Swaffham (Luft, 55->75 degC, COP 2,5-3,5) |  | Nur für cop_ansatz_luft = lorenz. |
| `waermepumpe.luft_spreizung` | 5 | K | vorgabe | BRF §3.4: Quelle T_a -> T_a - 5 K |  |  |
| `waermepumpe.abtau_abschlag` | 0.05 | - | annahme | BRF §3.4 (x) | 0, 0.1 |  |
| `waermepumpe.abtau_grenze` | 5 | degC | annahme | BRF §3.4: Abschlag für T_a < 5 degC |  |  |
| `waermepumpe.T_min_luft` | -7 | degC | annahme | BRF §3.4: ökonomische Grenze; Referenzen nur bis ≈ -5 degC (SCH D7) | -15, 0 |  |
| `waermepumpe.luft_leistung_voll_ab` | -1 | degC | annahme | BRF §3.4: DRL Luft-WP 6 MW bei -1 degC (EHPA Award); darüber konstant volle Leistung (konservativ) |  |  |
| `waermepumpe.luft_leistung_bei_tmin` | 0.8 | - | annahme | BRF §3.4: linear auf 80 % der Leistung bei T_min_luft (-7 degC); Rest Annahme, keine Referenz unter -5 degC | 0.6, 1 | Thermische Leistung der Luft-WP relativ zur gebauten WP-Leistung (docs E27); 1,0 = altes Verhalten (Leistung unabhängig von der Temperatur). |
| `waermepumpe.COP_ptes` | 4.5 | - | annahme | BRF §3.4: Schrittmittel 45->10 degC ≈ 4,9, konservativ 4,5; Marstal NH3 Jahresmittel 5-5,5 | 3.5, 5.5 | Bei VL 80 statt 75 degC eher etwas niedriger (≈ -5 %) -> in Sensitivität abgedeckt. |
| `waermepumpe.kosten_spez` | 1340000 | EUR/MW_th | vorgabe | TEAM 10.11.2026: unteres Ende des KWW Technikkatalogs (Tab. 24, Kompressions-WP Luft, zweistufig, 70 °C, 2026, netto): 1.340 EUR/kW_th (10 MW); Spanne 1.970 (0,3 MW) / 1.730 (1 MW) / 1.600 (2 MW) / 1.440 (5 MW), Unsicherheit ±30 % | 1000000, 1730000 | Für das kleine Netz (≈ 1 MW) optimistisch (KWW-Größenklasse 1.730 EUR/kW, Szenario kww_komplett). Vorher 1,0 Mio. EUR/MW (Frederikssund 2022, DK). Lebensdauer/O&M weiter 20 a / 2,5 % (KWW: 28 a / 3 %). Gilt für Luft- und Speicher-WP (gemeinsame Leistung wp_out). |

## pth

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `pth.eta` | 0.99 | - | vorgabe | BRF §2 |  |  |
| `pth.redundanz` | 1 | x P_max | annahme | SCH A6: x_PtH >= P_max (n-1-Redundanz, Versorgungssicherheit); p_nom_min der PtH (elektrisch: /eta) | 0 | 0 = PtH nur so groß, wie das LP sie braucht (Variante SCH A6: x_PtH = P_max - x_WP). |
| `pth.kosten_spez` | 100000 | EUR/MW_th | annahme | Frederikssund 2022: ≈ 0,5 Mio. DKK/MW ≈ 0,07 Mio. EUR/MW (SCH); kleine Leistung -> 0,1 Mio. EUR/MW | 70000, 150000 |  |

## biomasse

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `biomasse.eta` | 0.875 | - | annahme | BRF §3.5 / SCH A6: 0,85-0,90 (Mittelwert) | 0.85, 0.9 |  |
| `biomasse.brennstoffkosten` | 100 | EUR/MWh | vorgabe | TEAM: 10 ct/kWh, real konstant |  |  |

## gas_referenz

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `gas_referenz.eta` | 0.95 | - | annahme | BRF §3.5 (x); Brennwertkessel bezogen auf Hi |  |  |
| `gas_referenz.emissionsfaktor` | 0.201 | t/MWh_Hi | vorgabe | UBA: Erdgas ≈ 55,8 t/TJ (Hi) = 0,201 t/MWh; TEAM bestätigt |  |  |
| `gas_referenz.hs_hi` | 1.11 | - | belegt | Verhältnis Brennwert/Heizwert Erdgas H ≈ 1,11 (DVGW G 685 Größenordnung) |  |  |
| `gas_referenz.gaspreis` | 120 | EUR/MWh_Hs | vorgabe | TEAM: ca. 12 ct/kWh; interpretiert als Bezugspreis netto OHNE CO2-Bepreisung (CO2 separat über co2_preis) | 80, 160 |  |
| `gas_referenz.co2_preis` | 100 | EUR/t | vorgabe | TEAM: ETS ca. 100 EUR/t | 55, 200 |  |
| `gas_referenz.kosten_spez` | 100000 | EUR/MW_th | annahme | Gaskessel Fernwärme ≈ 0,05-0,1 Mio. EUR/MW (DEA-Größenordnung); kleine Leistung -> oberer Wert |  |  |
| `gas_referenz.auslegung` | 1.1 | x P_max | annahme | Kesselleistung = 1,1 x Spitzenlast (Reserve) |  |  |

## strom

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `strom.tarif` | fest | - | vorgabe | BRF §3.5 / TEAM: Basis fester Tarif; Option day_ahead (Zeitreihe) über Szenarien strom_day_ahead_*.yaml | day_ahead |  |
| `strom.preis_fest` | 300 | EUR/MWh | vorgabe | TEAM: 30 ct/kWh (inkl. Netzentgelte/Abgaben, netto) | 200, 400 | Gesamtpreis beim festen Tarif; Beschaffung+Vertrieb = Gesamt - Netzentgelt - Abgaben. Bandbreite ±1/3 als Annahme. BDEW-Strompreisanalyse nennt für Industrie 2025 ≈ 16-18 ct/kWh (ohne Gewerbeaufschläge) -> 30 ct ist eher hoch, 20 ct plausibel (docs/ausblick.md). |
| `strom.netzentgelt` | 79.9 | EUR/MWh | belegt | Westfalen Weser Netz, Preisblatt Netznutzung Strom gültig ab 01.01.2025 (Stand 19.12.2024), lastganggemessene Kunden, Mittelspannung, Benutzungsdauer < 2.500 h/a: Arbeitspreis 7,99 ct/kWh | 60, 110 | Arbeitspreis. Vorher 93 EUR/MWh (BDEW-Durchschnitt). Benutzungsdauer hier ≈ 1.000-1.500 h/a (Strombezug / höchste Leistung). Ab 2.500 h/a gälte 163,73 EUR/kW und 2,06 ct/kWh. Preisblatt 2026 war am 14.11.2026 nur vorläufig veröffentlicht. |
| `strom.leistungspreis` | 15.5 | EUR/(kW a) | belegt | Westfalen Weser Netz, Preisblatt Netznutzung Strom ab 01.01.2025, Mittelspannung, < 2.500 h/a: Leistungspreis 15,50 EUR/kWa (auf die höchste Bezugsleistung des Jahres) | 0, 163.73 | Im Modell: Kosten der Anschlussleistung (Link netzanschluss) = höchster Strombezug einer Stunde. Zusätzlich zu strom.preis_fest. 163,73 EUR/kWa gehört zur Preisregelung ab 2.500 h/a (dann Arbeitspreis 2,06 ct/kWh) und ist als alleinige Variante nur ein Grenzfall. |
| `strom.abgaben` | 57 | EUR/MWh | annahme | Stromsteuer 2,05 + Konzessionsabgabe 1,67 + KWKG-Umlage 0,45 + §19-Aufschlag 1,56 ct/kWh (BDEW/Versorger-Preisblätter 2026, uneinheitlich); Offshore-Umlage 0,94 ct nicht enthalten; evtl. Entlastungen für WP (§22 EnFG) ungeprüft | 40, 70 |  |
| `strom.vertriebsmarge` | 25 | EUR/MWh | annahme | Spot-Tarife leistungsgemessener Gewerbekunden: Aufschlag auf den Spotpreis inkl. Vertrieb und Ausgleichsenergie z. B. 2,50 ct/kWh (Stadtwerke Radolfzell, RLM Niederspannung), 5,80 ct/kWh (Mainova, RLM ab 100.000 kWh/a, Ersatzversorgung), 7,1 ct/kWh (Bad Belzig); Spanne 2,5-7 ct -> untere Spanne 2,5 ct angesetzt | 10, 60 | Nur für tarif day_ahead: Energie(t) = Day-Ahead(t) + Marge. Bei Großabnehmern (>1 GWh/a, Mittelspannung) verhandelbar und oft niedriger. |
| `strom.preisjahr` | 2024 | a | annahme | Day-Ahead-Stundenpreise DE-LU, Bundesnetzagentur / SMARD.de (CC BY 4.0) über Energy-Charts-API. Jahresmittel: 2022 = 235 (Krise), 2023 = 95, 2024 = 78,5 EUR/MWh. 2024 als ruhiges, aktuelles Jahr | 2023, 2022 | Preisjahr ist unabhängig vom Wetterjahr 2022 (Stunde i -> Stunde i); Zusammenhang kalt <-> teuer nur statistisch. Daten laden: serts fetch-strompreise. |
| `strom.day_ahead_normieren` | False | - | vorgabe | true = Day-Ahead-Profil auf den Energieanteil des festen Tarifs normiert (gleicher Jahresmittelwert) -> isoliert den Effekt der zeitlichen Preisstruktur |  |  |
| `strom.emissionsfaktor` | 0.363 | t/MWh | belegt | UBA: CO2-Emissionen pro kWh Strom 2024 = 363 g/kWh (Themenseite; UBA-FAQ nennt 353 g) | 0.2 |  |
| `strom.ee_anteil` | 0.544 | - | belegt | AGEE-Stat/UBA: Anteil EE am Bruttostromverbrauch 2024 = 54,4 % |  |  |

## oekonomie

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `oekonomie.zins` | 0.05 | - | vorgabe | TEAM 09.11.2026: Zins bleibt REAL (5 %), damit alle Preise real konstant (Preisänderung 0 %/a); Preisänderungsfaktoren nur für Varianten | 0.03, 0.07 |  |
| `oekonomie.betrachtungszeitraum` | 20 | a | vorgabe | TEAM |  |  |
| `oekonomie.preisbasisjahr` | 2025 | a | vorgabe | TEAM: 2025/26 |  |  |
| `oekonomie.nebenkosten` | 0.1 | - | vorgabe | TEAM 09.11.2026: ca. 10 % Planungs-/Nebenkosten auf alle Investitionen (Kollektor, PTES, WP, PtH, Netz, Hausanschluss, Gaskessel) | 0, 0.2 | Wirkt auf Annuität und O&M. Planung (HOAI LPh 5-8) ist teilweise BEW-förderfähig; Modell wendet die Förderquote auf Invest inkl. Nebenkosten an. |
| `oekonomie.foerderfaehig.kollektor` | True | - | belegt | BEW Richtlinie 4.2 Nr. 1: Solarthermie (docs/foerderung_bew.md) |  |  |
| `oekonomie.foerderfaehig.ptes` | True | - | belegt | BEW Richtlinie 4.2: Wärmespeicher, saisonale Großspeicher genannt (docs/foerderung_bew.md) |  |  |
| `oekonomie.foerderfaehig.waermepumpe` | True | - | belegt | BEW Richtlinie 4.2 Nr. 2: Wärmepumpen (docs/foerderung_bew.md) |  |  |
| `oekonomie.foerderfaehig.pth` | False | - | annahme | Elektrodenkessel im gelesenen BEW-Text nicht aufgeführt -> konservativ nicht förderfähig; klären |  |  |
| `oekonomie.foerderfaehig.netz` | True | - | belegt | BEW Richtlinie 4.2: Rohrleitungssystem inkl. Verlegung und Dämmung |  |  |
| `oekonomie.foerderfaehig.hausanschluss` | False | - | annahme | Hausanschlussleitungen im gelesenen BEW-Text nicht ausdrücklich genannt -> konservativ nicht förderfähig; klären |  |  |
| `oekonomie.foerderfaehig.gaskessel` | False | - | belegt | BEW: fossile Wärmeerzeuger nicht förderfähig (Gas-Referenz) |  |  |
| `oekonomie.foerderquote` | 0 | - | vorgabe | AP 10 Einfach: Basis ohne Förderung; Variante pauschaler Investitionszuschuss | 0.4 | Variante 0,4 = BEW Modul 2 (BAFA, bis zu 40 % der förderfähigen Ausgaben). Gilt nur für Komponenten mit oekonomie.foerderfaehig = true (Kollektor, PTES, WP, Trasse); nicht für PtH, Hausanschluss (ungeklärt) und die Gas-Referenz. Wirkt auf die Optimierung (Szenario bew_modul2). |
| `oekonomie.bew_ausweis_quote` | 0.4 | - | belegt | BEW Richtlinie 7.1.2: Modul 2 bis zu 40 % der förderfähigen Ausgaben (docs/foerderung_bew.md) |  | Jeder Lauf weist zusätzlich die Kosten MIT BEW Modul 2 für dieselbe Auslegung aus (Kennzahlen *_bew). Obergrenze: der tatsächliche Zuschuss ist auf die Wirtschaftlichkeitslücke begrenzt (BAFA-Berechnung, hier nicht modelliert). 0 = kein Ausweis. |
| `oekonomie.preisaenderung.invest` | 0 | 1/a | vorgabe | TEAM: reale Rechnung, Ersatzinvestitionen ohne reale Preisänderung (VDI 2067: r_K) |  |  |
| `oekonomie.preisaenderung.betrieb` | 0 | 1/a | vorgabe | TEAM: reale Rechnung (VDI 2067: r_IN für Instandhaltung) |  |  |
| `oekonomie.preisaenderung.strom` | 0 | 1/a | vorgabe | TEAM: real gleichbleibende Preise (reale Rechnung); Variante +2 %/a | 0.02 |  |
| `oekonomie.preisaenderung.gas` | 0 | 1/a | vorgabe | TEAM: real gleichbleibend; Variante +2 %/a | 0.02 |  |
| `oekonomie.preisaenderung.co2` | 0 | 1/a | vorgabe | TEAM: real gleichbleibend | 0.05 |  |
| `oekonomie.preisaenderung.biomasse` | 0 | 1/a | vorgabe | TEAM: real gleichbleibend |  |  |
| `oekonomie.lebensdauer.ptes` | 30 | a | belegt | KWW Tab. 52: 30 a (mittlere Lebensdauer, Unsicherheit ±40 %); Anmerkung GX: die Abdeckung muss i. d. R. deutlich früher erneuert werden | 20, 40 | Vorher 25 a (Liner, DEA 20-40 a). Der Betrachtungszeitraum ist 20 a -> Restwert nach VDI 2067 wirkt (E32). |
| `oekonomie.lebensdauer.kollektor` | 25 | a | belegt | KWW Tab. 21: 25 a (Freifläche, professionelle Wartung; Bezug VDI 2067-1) |  |  |
| `oekonomie.lebensdauer.waermepumpe` | 20 | a | annahme | Größenordnung DEA/VDI 2067-1 (18-25 a) |  |  |
| `oekonomie.lebensdauer.pth` | 20 | a | annahme | Größenordnung DEA (20 a) |  |  |
| `oekonomie.lebensdauer.gaskessel` | 20 | a | annahme | Größenordnung VDI 2067-1 (18-20 a) |  |  |
| `oekonomie.lebensdauer.netz` | 40 | a | annahme | KMR/PEX-Fernwärmeleitungen: Größenordnung 40 a (DEA District heating distribution; VDI 2067-1) |  |  |
| `oekonomie.lebensdauer.hausanschluss` | 25 | a | annahme | Übergabestation dominiert die Kosten: Größenordnung 20-30 a |  |  |
| `oekonomie.om_fix.ptes` | 0.005 | 1/a vom Invest | belegt | KWW Tab. 52: fix 7.500-100.000 EUR/a (≈ 5 EUR/MWh Speicherkapazität) = 0,4-0,75 % des Invests je nach Größe; Mitte 0,5 % |  |  |
| `oekonomie.om_fix.kollektor` | 0.01 | 1/a vom Invest | belegt | KWW Tab. 21: 1 % des Invests (in Anlehnung an VDI 2067-1) |  |  |
| `oekonomie.om_fix.waermepumpe` | 0.025 | 1/a vom Invest | annahme | Größenordnung VDI 2067-1 (Wärmepumpen 2,5 %/a) |  |  |
| `oekonomie.om_fix.pth` | 0.02 | 1/a vom Invest | annahme | Größenordnung VDI 2067-1 |  |  |
| `oekonomie.om_fix.gaskessel` | 0.02 | 1/a vom Invest | annahme | Größenordnung VDI 2067-1 |  |  |
| `oekonomie.om_fix.netz` | 0.01 | 1/a vom Invest | annahme | Größenordnung VDI 2067-1 (Rohrleitungen ≈ 1 %/a) |  |  |
| `oekonomie.om_fix.hausanschluss` | 0.02 | 1/a vom Invest | annahme | Übergabestation, Größenordnung VDI 2067-1 |  |  |

## solver

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `solver.name` | highs | - | vorgabe | BRF §2 |  |  |
| `solver.optionen` | {'solver': 'ipm', 'run_crossover': 'off'} | - | vorgabe | Benchmark 09.11.2026 (A_spez 0,4, V/A 1,0, 8760 h, 1 Thread): Simplex 262 s, IPM ohne Crossover 56 s, identisches Optimum |  |  |
| `solver.tie_breaker` | 0.1 | EUR/MWh | vorgabe | numerische Hilfsgröße (keine Kosten): Speicherladen minimal teurer als Direktnutzung; << Strompreis, LCOH-Einfluss < 0,01 EUR/MWh |  |  |

## heatmap

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `heatmap.A_m2` | [1000, 2000, 3000, 4000, 5000] | m2 | vorgabe | Raster Kollektorfläche für serts heatmap (BRF §1 Pflicht 6), um das Optimum ≈ 3.700 m2 (Netz klein) |  |  |
| `heatmap.V_m3` | [0, 1000, 2000, 4000, 6000, 8000, 10000] | m3 | vorgabe | Raster Speichervolumen für serts heatmap, um das Optimum ≈ 6.000 m3 (Netz klein, E39); Punkte über der Fläche entfallen |  |  |

## tornado

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `tornado.parameter` | ['ptes.kosten_faktor', 'standort.flaeche_verfuegbar', 'kollektor.strahlung_skalierung', 'strom.preis_fest', 'last.skalierung', 'last.ankerkunde_anteil', 'ptes.verlustrate', 'ptes.uebergang_ref', 'ptes.groessen_exponent', 'ptes.vorwaermen', 'strom.leistungspreis', 'kollektor.iam_b0', 'waermepumpe.COP_ptes', 'waermepumpe.guetegrad_faktor', 'netz.T_RL', 'kollektor.kosten_spez', 'waermepumpe.kosten_spez', 'oekonomie.zins', 'oekonomie.foerderquote', 'oekonomie.nebenkosten', 'waermepumpe.luft_leistung_bei_tmin', 'oekonomie.preisaenderung.strom', 'kollektor.eta0', 'kollektor.feldverluste', 'pth.redundanz', 'netz.anteil_strasse', 'netz.kosten_trasse_strasse', 'netz.kosten_hausanschluss', 'gas_referenz.gaspreis', 'gas_referenz.co2_preis'] | - | vorgabe | BRF §1 Pflicht 6 (Speicherkosten, Solarressource, Strompreis, Lastprofil) + ergebnisrelevante Annahmen; Werte je Parameter aus 'sens' |  |  |
