# Modellgrenzen (mit Verzerrungsrichtung) – Baustein für den Bericht

| Grenze | Wirkung |
|---|---|
| Speicher in drei Teilen (Kern/Übergangszone/kalt) statt Temperaturschichten; Übergangszone als fester Anteil (E39) | bei fast leerem Speicher zu großzügig (dünne heiße Schicht sofort direkt nutzbar), bei vollem zu streng; Jahreswerte von Dronninglund werden getroffen (`validierung_dronninglund.md`) |
| Heißes Wasser bleibt 85 °C (Verluste kosten Menge, nicht Temperatur); T_oben = Vorlauf + 5 K ohne Reserve | Direktentladung eher überschätzt |
| Speicherverlust ∝ Inhalt, kein Erdreich | Anfahrjahre unterschätzt, Spätjahre leicht überschätzt |
| Verlustrate und Übergangszone aus DRL (60.000 m³), mit V^(−1/3) auf kleine Speicher umgerechnet; je Kostensegment der Wert der Untergrenze | innerhalb eines Segments leicht zu pessimistisch, Sprünge an den Segmentgrenzen; für < 20.000 m³ ohne Messwerte |
| Perfekte Voraussicht (LP über 8760 h) | Betrieb und Solaranteil eher überschätzt, Kosten unterschätzt |
| Kollektor bei fester mittlerer Temperatur (67,5 °C), auch beim Laden des kalten Teils; Einfallswinkel nur für Direktstrahlung | Ertrag beim Laden des kalten Teils unterschätzt |
| Kollektorkennwerte angenommen (Keymark nicht abrufbar) | Ertrag ± 5–10 % |
| Strahlung Normaljahr (TMY), Temperatur/Last 2022 – Stunden nicht gleichzeitig gemessen | Zusammenspiel sonnig ↔ kalt nur statistisch; Jahresbilanz ok |
| TMY aus Satellitendaten 2005–2023 | ggü. älteren Bodenmessungen (DWD 1992–2010) ≈ 13 % mehr Strahlung → Solar eher optimistisch |
| Konstanter COP aus dem Speicher (4,5) | Herbst unterschätzt, Frühjahr überschätzt; Jahresmittel ok |
| Luft-WP-Leistung: 100 % ab -1 °C, linear 80 % bei -7 °C (Annahme), darüber konstant; keine Teillast-/Mindestlastgrenzen | Leistung bei Kälte evtl. überschätzt (real ggf. stärker fallend); Teillastverluste fehlen |
| Lastgang aus Standardprofilen (NB, Wetter Münster 2022) | Spitzen geglättet; Kopplung Kälte ↔ Last nur statistisch |
| Speicherkosten als stückweise lineare Sehne einer konkaven Kostenkurve (E30) | Kosten zwischen den Stützstellen um ≤ 4–6 % unterschätzt (V > 1.000 m³) |
| Netzverluste aus NB (80/50 °C), Modell 80/45 °C | vernachlässigbar |
| Nebenkosten pauschal 10 % auf alle Investitionen | Spanne real 5–20 %; wirkt auf alle Varianten ähnlich |
| Strom: Leistungspreis auf die höchste Stunde (real höchste Viertelstunde), Preisregelung < 2.500 h/a fest gewählt | Leistungskosten leicht unterschätzt |
| Vorlauf konstant 80 °C (Teamvorgabe); gleitend nur als Szenario und nur für den COP der Luft-WP | Luft-WP im Basisfall eher pessimistisch (Arbeitszahl ≈ −10 %) |
