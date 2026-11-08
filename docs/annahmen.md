# Annahmentabelle

> Automatisch erzeugt aus `config/base.yaml` mit `serts annahmen`. Nicht von Hand ändern.

Status: belegt 19, vorgabe 34, annahme 36, offen 1


## standort

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `standort.name` | Bad Lippspringe | - | belegt | KWP-NRW Kommunenpaket 05774008 (Ordner Bad Lippspringe/KWP-NRW_...) |  |  |
| `standort.ags` | 05774008 | - | belegt | KWP-NRW Dateinamen |  |  |
| `standort.dwd_station_id` | 3028 | - | belegt | DWD CDC, Station 'Lippspringe, Bad' (Metadaten_Stationsname_03028.txt) |  |  |
| `standort.lat` | 51.7854 | deg | belegt | DWD Metadaten_Geographie_03028.txt (gültig ab 02.08.2006) |  |  |
| `standort.lon` | 8.8388 | deg | belegt | DWD Metadaten_Geographie_03028.txt |  |  |
| `standort.hoehe` | 157 | m | belegt | DWD Metadaten_Geographie_03028.txt |  |  |
| `standort.flaeche_verfuegbar` | 13000 | m2 | vorgabe | TEAM: ca. 13.000 m2 Grundstück am Erzeugerstandort, annähernd quadratisch |  | Muss Kollektorfeld (inkl. Reihenabstand, Technik) UND PTES aufnehmen -> Flächencheck je Rasterpunkt. |

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
| `netz.T_RL` | 45 | degC | vorgabe | BRF §2 (TEAM: Rücklauf frei '80/x'); NB rechnet 50 degC | 40, 50 |  |
| `netz.T_VL_netzberechnung` | 80 | degC | belegt | NB Zusammenfassung, Spalte Vorlauftemp |  |  |
| `netz.T_RL_netzberechnung` | 50 | degC | belegt | NB Zusammenfassung, Spalte Ruecklauftemp |  |  |
| `netz.trassenlaenge` | 2432 | m | belegt | NB Zusammenfassung, Summe Trassenlänge (ohne Hausanschlüsse 3413 m) |  |  |

## ptes

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `ptes.c_wasser` | 0.001163 | MWh/(m3 K) | belegt | rho*cp Wasser ≈ 1000 kg/m3 * 4,187 kJ/(kg K) = 1,163 kWh/(m3 K); BRF §3.2 |  | Bei 45-85 degC rho*cp ≈ 1,14-1,15 kWh/(m3 K) (-1...-2 %); vernachlässigt. |
| `ptes.T_oben` | 85 | degC | vorgabe | BRF §3.1; Liner-Grenze (Xiang et al. 2022) | 90 | Direktentladung braucht T_oben >= T_VL + 5 K = 85 degC -> bei VL 80 genau an der Grenze. |
| `ptes.T_unten` | 10 | degC | vorgabe | BRF §3.1; DRL Tmin 9-12 degC |  |  |
| `ptes.verlustrate` | 4e-05 | 1/h | annahme | BRF §3.2 Startwert, abgeleitet aus DRL (Verluste / mittl. Inhalt ≈ 2.800 MWh) | 1.5e-05, 8e-05 | PTES hier ≈7x kleiner als DRL; Oberfläche/Volumen ~ V^(-1/3) -> Faktor ≈1,9 -> obere Sensitivität 8e-5 (docs E10). |
| `ptes.kosten_spez` | 105 | EUR/m3 | annahme | Kostenkurve aus DRL 60.000 m3 / 38,3 EUR/m3 (SIF, 2014) und Marstal 10.000 m3 / 67 EUR/m3 (DEA 2019): c ~ V^-0,31; bei ≈ 8.700 m3 -> 70 EUR/m3, x 1,5 Baupreissteigerung 2014->2025 ≈ 105 EUR/m3 | 70, 140 | Linear im LP (konstant je m3). Gilt für ≈ 5.000-12.000 m3; bei ganz anderer optimaler Größe neu ableiten (docs E20). |
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
| `kollektor.feldverluste` | 0.1 | - | annahme | BRF §3.3 Startwert | 0.05, 0.15 |  |
| `kollektor.neigung` | 35 | deg | annahme | TEAM: einfache Annahme; 35 deg = übliche Neigung großer Freiflächenfelder in DE/DK (Kompromiss Ertrag/Reihenabstand) | 25, 45 |  |
| `kollektor.azimut` | 180 | deg | annahme | Südausrichtung (pvlib-Konvention 180 = Süd), Standard bei Freifeldanlagen |  |  |
| `kollektor.flaechenfaktor` | 2.3 | m2 Grund / m2 Kollektor | belegt | BSW: 2- bis 2,3-fache Bruttokollektorfläche inkl. Reihenabstände und Heizzentrale (Berlin.de nennt ≈ 3) | 2, 3 |  |
| `kollektor.strahlung_skalierung` | 1 | - | vorgabe | Faktor auf die PVGIS-Strahlung 2022 (Sensitivität Solarressource) | 0.78 | 0,78 ≈ Normaljahr: DWD-Klima 03028 ≈ 960 kWh/m2 horizontal x 1,13 Neigungsgewinn ≈ 1.085 kWh/m2 vs. PVGIS 2022 1.394 kWh/m2 (datenbasis §2) |
| `kollektor.strahlungsquelle` | pvgis_sarah3 | - | annahme | DWD-Strahlung an Stn. 3028 endet 31.08.2011 -> 2022 fehlt. PVGIS-SARAH3 deckt 2005-2023 ab (JRC). |  |  |
| `kollektor.kosten_spez` | 450 | EUR/m2 | annahme | Bitterfeld-Wolfen (BBU 2024): Budget 2,25 Mio. EUR für 5.000 m2 -> 450 EUR/m2 (Planung 2020); DRL 2014: (5,856+0,321) Mio. EUR / 37.573 m2 = 164 EUR/m2 (sehr groß, DK) | 300, 550 | Feldgröße hier ≈ 2.000-5.000 m2 -> Bitterfeld-Größenordnung passender als DRL. |

## waermepumpe

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `waermepumpe.approach` | 3 | K | vorgabe | BRF §3.4 (je Seite 3 K) |  |  |
| `waermepumpe.eta_G_luft` | 0.5 | - | annahme | BRF §3.4: Rückrechnung GEA Swaffham (Luft, 55->75 degC, COP 2,5-3,5) | 0.45, 0.6 |  |
| `waermepumpe.luft_spreizung` | 5 | K | vorgabe | BRF §3.4: Quelle T_a -> T_a - 5 K |  |  |
| `waermepumpe.abtau_abschlag` | 0.05 | - | annahme | BRF §3.4 (x) | 0, 0.1 |  |
| `waermepumpe.abtau_grenze` | 5 | degC | annahme | BRF §3.4: Abschlag für T_a < 5 degC |  |  |
| `waermepumpe.T_min_luft` | -7 | degC | annahme | BRF §3.4: ökonomische Grenze; Referenzen nur bis ≈ -5 degC (SCH D7) | -15, 0 |  |
| `waermepumpe.speicher_monate` | [11, 12, 1, 2, 3] | Monat | annahme | SIF Kap. 2.1: Speicher-WP in DRL lief ab ≈ November bis Januar/Februar; März als Puffer für späte Kälte |  | Nur in diesen Monaten darf die WP den Speicher als Quelle nutzen (verhindert Sommer-Artefakt der Jahresregel, docs E21). |
| `waermepumpe.COP_ptes` | 4.5 | - | annahme | BRF §3.4: Schrittmittel 45->10 degC ≈ 4,9, konservativ 4,5; Marstal NH3 Jahresmittel 5-5,5 | 3.5, 5.5 | Bei VL 80 statt 75 degC eher etwas niedriger (≈ -5 %) -> in Sensitivität abgedeckt. |
| `waermepumpe.kosten_spez` | 1000000 | EUR/MW_th | annahme | Frederikssund 2022: ≈ 6,4 Mio. DKK/MW Luft-WP ≈ 0,86 Mio. EUR/MW (SCH); kleine Leistung (1-2 MW) + NH3 + Luftkühler -> 1,0 Mio. EUR/MW | 700000, 1400000 | DEA Technology Data (District heating, 2025) nachtragen. |

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
| `strom.tarif` | fest | - | vorgabe | BRF §3.5 / TEAM: zunächst fester Tarif; später Zeitreihe oder PV-Anteil | day_ahead |  |
| `strom.preis_fest` | 300 | EUR/MWh | vorgabe | TEAM: 30 ct/kWh (inkl. Netzentgelte/Abgaben, netto) | 200, 400 | Bandbreite ±1/3 als Annahme für die Sensitivität |
| `strom.aufschlag_day_ahead` | **offen** | EUR/MWh | offen |  |  | erst für Day-Ahead-Variante nötig |
| `strom.emissionsfaktor` | 0.363 | t/MWh | belegt | UBA: CO2-Emissionen pro kWh Strom 2024 = 363 g/kWh (Themenseite; UBA-FAQ nennt 353 g) | 0.2 |  |
| `strom.ee_anteil` | 0.544 | - | belegt | AGEE-Stat/UBA: Anteil EE am Bruttostromverbrauch 2024 = 54,4 % |  |  |

## oekonomie

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `oekonomie.zins` | 0.05 | - | vorgabe | TEAM: 5 %; als realer Kalkulationszins verwendet (Preise real konstant) | 0.03, 0.07 |  |
| `oekonomie.betrachtungszeitraum` | 20 | a | vorgabe | TEAM |  |  |
| `oekonomie.preisbasisjahr` | 2025 | a | vorgabe | TEAM: 2025/26 |  |  |
| `oekonomie.foerderquote` | 0 | - | vorgabe | AP 10 Einfach: Basis ohne Förderung; Variante pauschaler Investitionszuschuss |  |  |
| `oekonomie.preisaenderung.strom` | 0 | 1/a | vorgabe | TEAM: real gleichbleibende Preise (reale Rechnung); Variante +2 %/a | 0.02 |  |
| `oekonomie.preisaenderung.gas` | 0 | 1/a | vorgabe | TEAM: real gleichbleibend; Variante +2 %/a | 0.02 |  |
| `oekonomie.preisaenderung.co2` | 0 | 1/a | vorgabe | TEAM: real gleichbleibend | 0.05 |  |
| `oekonomie.preisaenderung.biomasse` | 0 | 1/a | vorgabe | TEAM: real gleichbleibend |  |  |
| `oekonomie.lebensdauer.ptes` | 25 | a | annahme | Liner-Lebensdauer; Größenordnung DEA Technology Data Energy Storage (20-40 a) |  |  |
| `oekonomie.lebensdauer.kollektor` | 25 | a | annahme | Größenordnung DEA/VDI 2067-1 (20-30 a) |  |  |
| `oekonomie.lebensdauer.waermepumpe` | 20 | a | annahme | Größenordnung DEA/VDI 2067-1 (18-25 a) |  |  |
| `oekonomie.lebensdauer.pth` | 20 | a | annahme | Größenordnung DEA (20 a) |  |  |
| `oekonomie.lebensdauer.gaskessel` | 20 | a | annahme | Größenordnung VDI 2067-1 (18-20 a) |  |  |
| `oekonomie.om_fix.ptes` | 0.005 | 1/a vom Invest | annahme | geringe Wartung (Pumpen/Deckel), Größenordnung VDI 2067-1 |  |  |
| `oekonomie.om_fix.kollektor` | 0.01 | 1/a vom Invest | annahme | Größenordnung VDI 2067-1 (Solaranlagen 1-1,5 %/a) |  |  |
| `oekonomie.om_fix.waermepumpe` | 0.025 | 1/a vom Invest | annahme | Größenordnung VDI 2067-1 (Wärmepumpen 2,5 %/a) |  |  |
| `oekonomie.om_fix.pth` | 0.02 | 1/a vom Invest | annahme | Größenordnung VDI 2067-1 |  |  |
| `oekonomie.om_fix.gaskessel` | 0.02 | 1/a vom Invest | annahme | Größenordnung VDI 2067-1 |  |  |

## solver

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `solver.name` | highs | - | vorgabe | BRF §2 |  |  |
| `solver.optionen` | {'solver': 'ipm', 'run_crossover': 'off'} | - | vorgabe | Benchmark 09.11.2026 (A_spez 0,4, V/A 1,0, 8760 h, 1 Thread): Simplex 262 s, IPM ohne Crossover 56 s, identisches Optimum |  |  |
| `solver.tie_breaker` | 0.1 | EUR/MWh | vorgabe | numerische Hilfsgröße (keine Kosten): Speicherladen minimal teurer als Direktnutzung; << Strompreis, LCOH-Einfluss < 0,01 EUR/MWh |  |  |

## tornado

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `tornado.parameter` | ['ptes.kosten_spez', 'kollektor.strahlung_skalierung', 'strom.preis_fest', 'last.skalierung', 'last.ankerkunde_anteil', 'ptes.verlustrate', 'waermepumpe.COP_ptes', 'waermepumpe.eta_G_luft', 'netz.T_RL', 'kollektor.kosten_spez', 'waermepumpe.kosten_spez', 'oekonomie.zins'] | - | vorgabe | BRF §1 Pflicht 6 (Speicherkosten, Solarressource, Strompreis, Lastprofil) + ergebnisrelevante Annahmen; Werte je Parameter aus 'sens' |  |  |
