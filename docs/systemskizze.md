# Systemskizze – so wie das Modell rechnet

Diese Skizze entspricht 1:1 `src/serts/network.py` (Komponenten, Wirkungsgrade) und `src/serts/constraints.py`
(Zusatzbedingungen), Stand nach E27. Rechtecke = Komponenten (PyPSA-Links/Generatoren), Stadien/Kreise = Knoten
(Busse), Zylinder = Speicher. **✱ = Größe wird vom Solver optimiert.** Die Optimierung läuft über alle 8760 Stunden
gemeinsam (perfekte Voraussicht).

```mermaid
flowchart LR
    NS["Netzstrom<br/>30 ct/kWh, unbegrenzt<br/>(Generator netz_strom)"]
    KOL["Kollektorfeld ✱<br/>Leistung je m² = P_solar(t)<br/>Normaljahr, 67,5 °C, Abregelung möglich<br/>(Generator kollektor)"]

    ELEC(["Knoten Strom"])
    SOLAR(["Knoten Solar"])
    SPH[("Speicher HEISS ✱<br/>53 % der Energie: 85 °C bis Rücklauf<br/>Verlust 4·10⁻⁵ je Stunde<br/>Jahresende = Jahresanfang")]
    SPK[("Speicher KALT<br/>47 % der Energie: Rücklauf bis 10 °C<br/>Verlust 4·10⁻⁵ je Stunde<br/>wächst mit dem heißen Teil")]
    WPB(["Knoten WP-Wärme"])
    W(["Knoten Wärme<br/>Erzeugerstandort am Netz"])
    LAST["Last<br/>Gebäude + Netzverluste<br/>5.462 MWh/a, Spitze 1,59 MW"]

    SOLD["solar_direkt<br/>η = 1"]
    LAD["laden<br/>1 MWh Solar = 0,53 heiß + 0,47 kalt<br/>0,1 EUR/MWh Hilfskosten"]
    ENT["entladen_direkt<br/>heiß → Netz, η = 1"]
    HPL["hp_luft<br/>COP(T_a) 2,1 bis 3,3<br/>nur wenn T_a ≥ -7 °C"]
    HPS["hp_speicher<br/>COP 4,5, ganzjährig"]
    WPO["wp_out ✱<br/>gemeinsame WP-Leistung<br/>(Luft + Speicher)"]
    PTH["pth ✱<br/>η = 0,99<br/>Leistung ≥ Spitzenlast (n-1)"]

    NS --> ELEC
    KOL --> SOLAR
    SOLAR --> SOLD --> W
    SOLAR --> LAD
    LAD --> SPH
    LAD --> SPK
    SPH --> ENT --> W
    ELEC --> HPL --> WPB
    ELEC --> HPS --> WPB
    SPK -. "Quellwärme: 3,5 MWh je MWh Strom" .-> HPS
    WPB --> WPO --> W
    ELEC --> PTH --> W
    W --> LAST

    C1["Nebenbedingung 1: Fläche<br/>2,3 · A + V / 2,65 ≤ 13.000 m²"]
    C2["Nebenbedingung 2: Größe Speicher<br/>kalt = 0,875 × heiß<br/>(gilt in jeder Stunde)"]
    C3["Nebenbedingung 3: Luft-WP bei Kälte<br/>Wärmeleistung ≤ 100 % bis 80 % von P_WP<br/>(ab -1 bis -7 °C)"]
    C1 -.- KOL
    C1 -.- SPH
    C2 -.- SPH
    C2 -.- SPK
    C3 -.- HPL
    C3 -.- WPO

    NETZ["Verteilnetz - nicht optimiert<br/>Trasse 2.432 m + 159 Hausanschlüsse<br/>nur Kosten: Wärmepreis beim Kunden"]
    LAST -.- NETZ

    classDef bus fill:#eef3fb,stroke:#4e79a7,color:#000
    classDef quelle fill:#fff4d6,stroke:#c89b00,color:#000
    classDef speicher fill:#fde3c8,stroke:#d9730d,color:#000
    classDef link fill:#ffffff,stroke:#888,color:#000
    classDef regel fill:#f3e8f7,stroke:#8e44ad,color:#000
    classDef last fill:#e1f2e1,stroke:#3b8a3b,color:#000
    class ELEC,SOLAR,WPB,W bus
    class NS,KOL quelle
    class SPH,SPK speicher
    class SOLD,LAD,ENT,HPL,HPS,WPO,PTH link
    class C1,C2,C3,NETZ regel
    class LAST last
```

## Was die Skizze (nicht) enthält

- **Zeitlich variabel je Stunde:** Last, Außentemperatur → COP und Leistungsfaktor der Luft-WP, Kollektorleistung,
  (fester) Strompreis.
- **Fest je Lauf:** alle Wirkungsgrade, Preise, T_oben/Rücklauf/T_unten, Verlustrate, Fläche.
- **Optimiert (✱):** Kollektorfläche, Speichervolumen (innerhalb des gewählten Kostensegments), WP-Leistung,
  PtH-Leistung (mindestens Spitzenlast). Alle Verbindungen (Links) sind ansonsten nicht in der Leistung begrenzt.
- **Speicher:** Beladen füllt immer beide Teile im Verhältnis 53 : 47 (Wasser von 10 auf 85 °C). Direkt ins Netz
  geht nur der heiße Teil, die Wärmepumpe holt ihre Quellwärme aus dem kalten Teil. Das ersetzt die frühere
  Jahresregel („Direktanteil ≤ 53 %“) und die Monatsbeschränkung (E27).
- **Nicht im Modell:** Wärmeübertrager-Grenzen, Transmissionsleitung, Mischung/Zwischentemperaturen im Speicher,
  WP lädt den Speicher (rechnet sich bei festem Strompreis nicht, siehe `docs/ausblick.md`), Teillast der WP,
  Frostschutz des Kollektorfelds, Stagnation, Netzhydraulik, Leistungspreis für Strom.
- **Kostenseite (nicht in der Skizze):** Jahreskosten nach VDI 2067 je Komponente (inkl. 10 % Nebenkosten) + Strom
  (getrennt in Energie, Netzentgelt, Abgaben); Verteilnetz und Gas-Referenz werden in `kpi.py`/`economics.py`
  zugerechnet (`docs/entscheidungen.md` E25, E28).
