# Annahmentabelle

> Automatisch erzeugt aus `config/base.yaml` mit `serts annahmen`. Nicht von Hand ändern.

Status: belegt 15, vorgabe 23, annahme 17, offen 23


## standort

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `standort.name` | Bad Lippspringe | - | belegt | KWP-NRW Kommunenpaket 05774008 (Ordner Bad Lippspringe/KWP-NRW_...) |  |  |
| `standort.ags` | 05774008 | - | belegt | KWP-NRW Dateinamen |  |  |
| `standort.dwd_station_id` | 3028 | - | belegt | DWD CDC, Station 'Lippspringe, Bad' (Metadaten_Stationsname_03028.txt) |  |  |
| `standort.lat` | 51.7854 | deg | belegt | DWD Metadaten_Geographie_03028.txt (gültig ab 02.08.2006) |  |  |
| `standort.lon` | 8.8388 | deg | belegt | DWD Metadaten_Geographie_03028.txt |  |  |
| `standort.hoehe` | 157 | m | belegt | DWD Metadaten_Geographie_03028.txt |  |  |

## zeit

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `zeit.wetterjahr` | 2022 | a | belegt | NB Blatt Lastprofil: Zeitstempel 2022-01-01 00:00 bis 2022-12-31 23:00 (8760 h) |  | Wetter (DWD TU) und Last müssen dasselbe Jahr nutzen; anderes Jahr nur mit neuer Last. |
| `zeit.zeitzone` | UTC | - | annahme | DWD-Stundenwerte sind UTC (Metadaten_Parameter). Zeitbasis des NB-Lastgangs nicht dokumentiert -> als UTC behandelt. |  | Mit Team klären (Tool der Netzberechnung). Fehler max. 1-2 h Phasenversatz, für Jahresbilanz irrelevant. |
| `zeit.stunden` | 8760 | h | vorgabe | BRF §2 |  |  |

## last

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `last.datei` | bad_lippspringe/results netzberechnung.xlsx | - | belegt | NB (relativ zu data/raw) |  |  |
| `last.Q_gebaeude` | 4525.1 | MWh/a | belegt | NB Lastprofil, Summe Spalte 'Summe aller Gebäudetypen' (Zusammenfassung: 4525,2; 159 Gebäude) |  | Kontrollwert; das Modell nutzt die Zeitreihe. Test prüft Übereinstimmung. |
| `last.Q_netzverlust` | 937.3 | MWh/a | belegt | NB Lastprofil, Spalte 'Verlust' (konstant 0,107 MW; Zusammenfassung 935,4), gerechnet bei 80/50 degC | 849.7 | 849,7 MWh/a = Variante extra Dämmung (Szenario daemmung.yaml). Bei 75/45 degC wären die Verluste etwas geringer -> konservativ. |
| `last.netzverlust_variante` | standard | - | vorgabe | Basis = Standarddämmung; extra Dämmung als Variante | extra_daemmung |  |
| `last.P_max_kontrolle` | 1.592 | MW | belegt | NB Lastprofil, Max. 'Gesamtsumme' am 21.01.2022 07:00 |  |  |
| `last.skalierung` | 1 | - | vorgabe | unveränderter Lastgang; Sensitivität Lastprofil/-höhe über Szenario | 0.8, 1.2 |  |
| `last.ankerkunde_anteil` | 0 | - | vorgabe | BRF §3.5: Anteil 0/20/40 % von Q_a. Basis 0, da Gewerbe (GMK, GKO = 29 % von Q_gebaeude) im NB-Lastgang bereits enthalten | 0.2, 0.4 | Anteil bezogen auf Q_gebaeude, wird ZUSÄTZLICH zum NB-Lastgang addiert. |
| `last.ankerkunde_profil` | band | - | vorgabe | BRF §3.5 | werktag, saisonal |  |

## netz

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `netz.T_VL` | 75 | degC | vorgabe | BRF §2 (konstant) | 70, 80 |  |
| `netz.T_RL` | 45 | degC | vorgabe | BRF §2 | 40, 50 |  |
| `netz.T_VL_netzberechnung` | 80 | degC | belegt | NB Zusammenfassung, Spalte Vorlauftemp |  | Abweichung zu T_VL=75! Netzverluste in NB gelten für 80/50. Siehe docs/entscheidungen.md E3. |
| `netz.T_RL_netzberechnung` | 50 | degC | belegt | NB Zusammenfassung, Spalte Ruecklauftemp |  |  |
| `netz.trassenlaenge` | 2432 | m | belegt | NB Zusammenfassung, Summe Trassenlänge (ohne Hausanschlüsse 3413 m) |  |  |
| `netz.x_TL` | **offen** | MW | offen |  |  | Netzanschluss/Transmission Erzeugerstandort -> Stadt. Erzeugerstandort in Bad Lippspringe noch nicht festgelegt. |
| `netz.TL_verlust` | 0.015 | - | annahme | BRF §3.5 Startwert; DRL Transmission ≈1,4 % (558 MWh/a Auslegung) |  | Länge der Transmission in Bad Lippspringe offen; bei kurzer Leitung eher kleiner. |

## ptes

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `ptes.c_wasser` | 0.001163 | MWh/(m3 K) | belegt | rho*cp Wasser ≈ 1000 kg/m3 * 4,187 kJ/(kg K) = 1,163 kWh/(m3 K); BRF §3.2 |  | Bei 45-85 degC rho*cp ≈ 1,14-1,15 kWh/(m3 K) (-1...-2 %); vernachlässigt. |
| `ptes.T_oben` | 85 | degC | vorgabe | BRF §3.1; Liner-Grenze (Xiang et al. 2022) | 80, 90 |  |
| `ptes.T_mitte` | 45 | degC | vorgabe | = Netz-Rücklauf (BRF §3.1) |  |  |
| `ptes.T_unten` | 10 | degC | vorgabe | BRF §3.1; DRL Tmin 9-12 degC |  |  |
| `ptes.verlustrate` | 4e-05 | 1/h | annahme | BRF §3.2 Startwert, abgeleitet aus DRL (Verluste / mittl. Inhalt ≈ 2.800 MWh) | 1.5e-05, 8e-05 | Bad Lippspringe-PTES ist ≈7x kleiner als DRL (V≈8.700 vs. 60.000 m3). Oberfläche/Volumen ~ V^(-1/3) -> Faktor ≈1,9 -> obere Sensitivität 8e-5 (eigene Abschätzung). |
| `ptes.x_HX_lad` | **offen** | MW | offen |  |  |  |
| `ptes.x_HX_ent` | **offen** | MW | offen |  |  |  |
| `ptes.kosten_spez` | **offen** | EUR/m3 | offen |  |  | DEA Technology Catalogue (Energy Storage, Brief LTES 02/2025), PlanEnergi 2025. DK 2014/15: 24-48 EUR/m3 nur für große PTES; < 10.000 m3 deutlich teurer -> degressive Kurve nötig. |

## kollektor

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `kollektor.typ` | flachkollektor | - | vorgabe | SCH A3 (wie DRL) |  |  |
| `kollektor.eta0` | **offen** | - | offen |  |  | Solar-Keymark-Datenblatt eines großen Flachkollektors (typ. 0,75-0,82 lt. BRF, nicht ungeprüft übernehmen) |
| `kollektor.a1` | **offen** | W/(m2 K) | offen |  |  | typ. 2-2,5 (BRF) |
| `kollektor.a2` | **offen** | W/(m2 K2) | offen |  |  | typ. 0,01-0,016 (BRF) |
| `kollektor.T_m_hoch` | 67.5 | degC | vorgabe | BRF §3.3 (Rücklauf 50 -> 85 degC) |  |  |
| `kollektor.T_m_tief` | 30 | degC | vorgabe | BRF §3.3 (10 -> 50 degC) |  |  |
| `kollektor.feldverluste` | 0.1 | - | annahme | BRF §3.3 Startwert | 0.05, 0.15 |  |
| `kollektor.neigung` | **offen** | deg | offen |  |  | Freiflächenanlagen DE/DK meist 30-45 deg; mit Team/Literatur festlegen (KWP-NRW Freiflächen-Solarthermie-Doku prüfen) |
| `kollektor.azimut` | 180 | deg | annahme | Südausrichtung (pvlib-Konvention 180 = Süd), Standard bei Freifeldanlagen |  |  |
| `kollektor.frostschutz_anteil` | 0.01 | - | annahme | BRF §3.3 Startwert (1 % des Kollektorertrags, verteilt auf Stunden mit T_a < 0) |  |  |
| `kollektor.strahlungsquelle` | pvgis_sarah3 | - | annahme | DWD-Strahlung an Stn. 3028 endet 31.08.2011 (Ordner stundenwerte_ST_03028_row) -> 2022 fehlt. PVGIS-SARAH3 deckt 2005-2023 ab (JRC). |  | Vor Nutzung: Jahressumme PVGIS gegen DWD-Klimamittel 1991-2010 an Stn. 3028 plausibilisieren (serts check-strahlung). |

## waermepumpe

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `waermepumpe.approach` | 3 | K | vorgabe | BRF §3.4 (je Seite 3 K) |  |  |
| `waermepumpe.eta_G_luft` | 0.5 | - | annahme | BRF §3.4: Rückrechnung GEA Swaffham (Luft, 55->75 degC, COP 2,5-3,5) | 0.45, 0.6 |  |
| `waermepumpe.luft_spreizung` | 5 | K | vorgabe | BRF §3.4: Quelle T_a -> T_a - 5 K |  |  |
| `waermepumpe.abtau_abschlag` | 0.05 | - | annahme | BRF §3.4 (x) | 0, 0.1 |  |
| `waermepumpe.abtau_grenze` | 5 | degC | annahme | BRF §3.4: Abschlag für T_a < 5 degC |  |  |
| `waermepumpe.T_min_luft` | -7 | degC | annahme | BRF §3.4: ökonomische Grenze; Referenzen nur bis ≈ -5 degC (SCH D7) | -15, 0 |  |
| `waermepumpe.p_max_pu_luft_knick` | [[-1, 1.0], [-7, 0.8]] | [degC, -] | annahme | BRF §3.4: 1 ab -1 degC (DRL 6 MW bei -1 degC), linear auf 0,8 bei -7 degC; Rest Annahme |  |  |
| `waermepumpe.COP_ptes` | 4.5 | - | annahme | BRF §3.4: Schrittmittel 45->10 degC ≈ 4,9, konservativ 4,5; Marstal NH3 Jahresmittel 5-5,5 | 3.5, 5.5 |  |
| `waermepumpe.p_max_pu_ptes` | 0.75 | - | annahme | BRF §3.4: Marstal, Leistung halbiert sich 50 -> 15 degC Quelle | 0.5, 1 |  |
| `waermepumpe.kosten_spez` | **offen** | EUR/MW_th | offen |  |  | DEA Technology Catalogue District Heating; Frederikssund 2022 ≈ 6,4 Mio. DKK/MW nur Orientierung |

## pth

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `pth.eta` | 0.99 | - | vorgabe | BRF §2 |  |  |
| `pth.laden_ptes` | False | - | vorgabe | BRF §3.5 (Variante, Standard aus) |  |  |
| `pth.kosten_spez` | **offen** | EUR/MW_th | offen |  |  | DEA; Frederikssund 2022 ≈ 0,5 Mio. DKK/MW nur Orientierung |

## biomasse

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `biomasse.eta` | 0.875 | - | annahme | BRF §3.5 / SCH A6: 0,85-0,90 (Mittelwert) | 0.85, 0.9 |  |
| `biomasse.brennstoffkosten` | **offen** | EUR/MWh | offen |  |  |  |

## gas_referenz

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `gas_referenz.eta` | 0.95 | - | annahme | BRF §3.5 (x) |  |  |
| `gas_referenz.emissionsfaktor` | 0.201 | t/MWh_Hi | annahme | UBA, CO2-Emissionsfaktoren für fossile Brennstoffe: Erdgas ≈ 55,8 t/TJ (Hi) = 0,201 t/MWh |  | Wert ohne Primärdokument im Repo übernommen -> UBA-Tabelle (aktuelle Ausgabe) prüfen, dann status: belegt. Bezug Hi; Gaspreise meist auf Hs (Hs/Hi ≈ 1,11). |
| `gas_referenz.gaspreis` | **offen** | EUR/MWh_Hs | offen |  |  |  |
| `gas_referenz.co2_preis` | **offen** | EUR/t | offen |  |  | 3 Pfade ab ETS2 (AP 7 Mittel) |

## strom

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `strom.tarif` | fest | - | vorgabe | BRF §3.5: Basis fester Tarif, Variante Day-Ahead + Aufschlag | day_ahead |  |
| `strom.preis_fest` | **offen** | EUR/MWh | offen |  |  |  |
| `strom.aufschlag_day_ahead` | **offen** | EUR/MWh | offen |  |  |  |
| `strom.emissionsfaktor` | **offen** | t/MWh | offen |  |  | UBA Strommix-Jahresmittel, Bezugsjahr angeben |

## oekonomie

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `oekonomie.zins` | **offen** | - | offen |  |  |  |
| `oekonomie.betrachtungszeitraum` | **offen** | a | offen |  |  |  |
| `oekonomie.preisbasisjahr` | **offen** | a | offen |  |  |  |
| `oekonomie.foerderquote` | 0 | - | vorgabe | AP 10 Einfach: Basis ohne Förderung; Variante pauschaler Investitionszuschuss |  |  |
| `oekonomie.lebensdauer.ptes` | **offen** | a | offen |  |  |  |
| `oekonomie.lebensdauer.kollektor` | **offen** | a | offen |  |  |  |
| `oekonomie.lebensdauer.waermepumpe` | **offen** | a | offen |  |  |  |
| `oekonomie.lebensdauer.pth` | **offen** | a | offen |  |  |  |

## raster

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `raster.bezug` | einspeisung | - | vorgabe | BRF §5: m2 je MWh/a Bedarf; DRL-Bezug ist 'Wärme ans Netz' (inkl. Netzverluste) -> hier Q_gebaeude + Q_netzverlust = 5.462 MWh/a |  |  |
| `raster.A_spez` | [0.4, 0.6, 0.8, 1.0, 1.2, 1.5] | m2/(MWh/a) | vorgabe | BRF §5 Raster-Vorschlag (DRL ≈ 1,0) |  |  |
| `raster.V_pro_A` | [0.0, 1.0, 1.6, 2.5] | m3/m2 | vorgabe | BRF §5 (DRL ≈ 1,6; Bracht ≈ 2,3) |  |  |

## solver

| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |
|---|---|---|---|---|---|---|
| `solver.name` | highs | - | vorgabe | BRF §2 |  |  |
