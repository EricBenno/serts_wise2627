# BEW – was ist förderfähig? (Recherche 09.11.2026)

Quelle: Richtlinie „Bundesförderung für effiziente Wärmenetze (BEW)“ vom 1. August 2022 in der Fassung der
[Förderdatenbank des Bundes](https://www.foerderdatenbank.de/FDB/Content/DE/Foerderprogramm/Bund/BMWi/bundesfoerderung-effiziente-waermenetze.html)
(Abschnitte der Richtlinie in Klammern). Der Richtlinientext im
[Bundesanzeiger (BAnz AT 18.08.2022 B1)](https://www.bundesanzeiger.de/pub/publication/LqynJ78mbcSrTH7lL83/content/LqynJ78mbcSrTH7lL83/BAnz%20AT%2018.08.2022%20B1.pdf)
war maschinell nicht lesbar. Antrag/Info: [BAFA Wärmenetze](https://www.bafa.de/DE/Energie/Energieeffizienz/Waermenetze/waermenetze_node.html).
**Kennzeichnung:** ✔ = im Richtlinientext gelesen, ? = nicht gefunden/uneindeutig, ⚠ = aus Zusammenfassungen,
vor Verwendung prüfen. Ob die Richtlinie seitdem geändert wurde, ließ sich nicht klären – **vor einem Antrag die
aktuelle Fassung beim BAFA prüfen.**

## Modul 2 (Neubau und Ausbau von Wärmenetzen, Investition)

- **Fördersatz:** bis zu **40 %** der förderfähigen Ausgaben, höchstens 100 Mio. € je Antrag (7.1.2) ✔.
  (Andere Quellen nennen 50 % für Modul 1 – Machbarkeitsstudie.)
- **Voraussetzungen Neubau (4.2.1) ✔:** mindestens **75 %** erneuerbare Energien + Abwärme in der eingespeisten
  Wärme; mehr als 16 Gebäude oder 100 Wohneinheiten; Vorlauf höchstens 95 °C; höchstens 10 % Wärme aus
  fossilen Kesseln; Machbarkeitsstudie mit Mindestinhalt; Wirtschaftlichkeitslücken-Berechnung.
  → Bad Lippspringe: 159 Gebäude, 80 °C, ≈ 85–88 % EE-Anteil im Modell (Strommix zählt anteilig, siehe Hinweis unten).
- **Bewilligung:** 48 Monate (einmal um 24 Monate verlängerbar); Ermessensentscheidung ohne Rechtsanspruch ✔.

| Position im Modell | Förderfähig? |
|---|---|
| **Solarthermie** (Kollektorfeld) | ✔ (4.2 Nr. 1) |
| **Wärmepumpe** (Luft/Umweltwärme) | ✔ (4.2 Nr. 2) |
| **Wärmespeicher**, saisonale Großspeicher (PTES) | ✔ (Maßnahmen zur Netzoptimierung; saisonale Großwärmespeicher ausdrücklich genannt) |
| **Rohrleitungssystem** inkl. Verlegung und Dämmung (Trasse, Tiefbau) | ✔ |
| **Übergabestationen** im Eigentum des Netzbetreibers | ✔ |
| **Heizzentrale** bei Einbindung neuer förderfähiger Anlagen | ✔ |
| **Planung** | ✔ Leistungsphasen 5–8 (HOAI) in Modul 2; Phasen 2–4 gehören zu Modul 1 |
| **Hausanschlussleitungen** | ? nicht ausdrücklich genannt; ⚠ Gräben für Neukunden evtl. (7.2.3.10) |
| **PtH / Elektrodenkessel** (Spitzenlast/Reserve) | ? im gelesenen Text nicht aufgeführt → klären |
| **Stromnetzanschluss/Trafo**, **Grundstück** | ? nicht gefunden (⚠ Grundstückskauf gilt nicht als Vorhabenbeginn) |
| Biomassekessel | ✔ mit Auflagen (Anteilsgrenzen) |
| Fossile Wärmeerzeuger (Gas-Spitzenlast) | ✘ **nicht** förderfähig |

## Modul 4 (Betriebskostenförderung, 10 Jahre)

Gilt für **Solarthermie** und **strombetriebene Wärmepumpen** und nur für Anlagen, die zuvor über Modul 2/3
gefördert wurden (Höhe „nach Art der Anlage und Jahresarbeitszahl“ ✔). ⚠ Nach Zusammenfassungen/Merkblättern:
Solarthermie **1 ct/kWh_th** über 10 Jahre; Wärmepumpe bis 9,2 ct/kWh (Umwelt-/Abwärme) bzw. 3 ct/kWh_th bei
direktem EE-Strom, gedeckelt auf 90 % der nachgewiesenen Stromkosten, SCOP ≥ 2,5. Die WP-Formel konnte nicht
verifiziert werden. Größenordnung Solar im Modell: 650–1.960 MWh/a × 1 ct ≈ **7–20 T€/a** – klein gegen die
Gesamtkosten (≈ 1,2 Mio. €/a).

## Konsequenzen für das Modell

1. **40 % ist eine Obergrenze.** Der Zuschuss richtet sich nach der Wirtschaftlichkeitslücke; die tatsächliche
   Quote kann niedriger sein (`oekonomie.foerderquote`: Variante 0,4 im Tornado).
2. **Die 40 % gelten derzeit pauschal für alle Komponenten** (inkl. PtH und Hausanschlüsse). Genauer wäre eine
   Quote je Komponente: Kollektor, PTES, WP, Trasse 40 %; PtH und Hausanschlüsse offen (0–40 %). Betroffen sind
   PtH (≈ 0,16 Mio. € Invest) und vor allem die Hausanschlüsse (1,6 Mio. € Invest → bis ≈ 0,6 Mio. € Zuschuss
   weniger, wenn nicht förderfähig). Das wirkt auf den Wärmepreis inkl. Netz; bei Bedarf eigene Parameter anlegen.
3. **Planung** (≈ 10–20 % Nebenkosten, im Modell noch nicht enthalten) ist teilweise förderfähig.
4. **Gas-Referenz** bekommt keine BEW-Förderung (fossile Erzeugung nicht förderfähig) – im Modell richtig umgesetzt.
5. **EE-Anteil 75 %:** Die Richtlinie verlangt ≥ 75 % EE + Abwärme in der eingespeisten Wärme (✔). **Nicht
   geprüft** habe ich, wie der Strom der Wärmepumpe dabei angerechnet wird (Netzmix 2024: 54 % EE, Umweltwärme
   zählt als erneuerbar). Der Modellwert `ee_anteil` (≈ 85 %) ist eine eigene Definition und **kein**
   BEW-Nachweis. Vor einem Antrag klären (BAFA/Machbarkeitsstudie); ggf. mit Ökostrom oder PV-WP absichern
   (siehe `docs/ausblick.md`).
