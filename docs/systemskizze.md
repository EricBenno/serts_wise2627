# Systemskizze – so wie das Modell rechnet

Diese Skizze entspricht 1:1 `src/serts/network.py` (Komponenten, Wirkungsgrade) und `src/serts/constraints.py`
(Zusatzbedingungen). Rechtecke = Komponenten (PyPSA-Links/Generatoren), Stadien/Kreise = Knoten (Busse).
**✱ = Größe wird vom Solver optimiert.** Die Optimierung läuft über alle 8760 Stunden gemeinsam (perfekte Voraussicht).

```mermaid
flowchart LR
    NS["Netzstrom<br/>30 ct/kWh, unbegrenzt<br/>(Generator netz_strom)"]
    KOL["Kollektorfeld ✱<br/>Leistung je m² = P_solar(t)<br/>Normaljahr, 67,5 °C, Abregelung möglich<br/>(Generator kollektor)"]

    ELEC(["Knoten Strom"])
    SOLAR(["Knoten Solar"])
    SPEI[("PTES-Speicher ✱<br/>Energie in MWh (bez. auf 10 °C)<br/>Verlust 4·10⁻⁵ je Stunde<br/>Jahresende = Jahresanfang")]
    WPB(["Knoten WP-Wärme"])
    W(["Knoten Wärme<br/>Erzeugerstandort am Netz"])
    LAST["Last<br/>Gebäude + Netzverluste<br/>5.462 MWh/a, Spitze 1,59 MW"]

    SOLD["solar_direkt<br/>η = 1"]
    LAD["laden<br/>η = 1<br/>0,1 EUR/MWh Hilfskosten"]
    ENT["entladen_direkt<br/>η = 1"]
    HPL["hp_luft<br/>COP(T_a) 2,1 bis 3,3<br/>nur wenn T_a ≥ -7 °C"]
    HPS["hp_speicher<br/>COP 4,5<br/>nur Nov bis Mär"]
    WPO["wp_out ✱<br/>gemeinsame WP-Leistung<br/>(Luft + Speicher)"]
    PTH["pth ✱<br/>η = 0,99<br/>Leistung ≥ Spitzenlast (n-1)"]

    NS --> ELEC
    KOL --> SOLAR
    SOLAR --> SOLD --> W
    SOLAR --> LAD --> SPEI
    SPEI --> ENT --> W
    ELEC --> HPL --> WPB
    ELEC --> HPS --> WPB
    SPEI -. "Quellwärme: 3,5 MWh je MWh Strom" .-> HPS
    WPB --> WPO --> W
    ELEC --> PTH --> W
    W --> LAST

    C1["Nebenbedingung 1: Fläche<br/>2,3 · A + V / 2,65 ≤ 13.000 m²"]
    C2["Nebenbedingung 2: Speicher (Jahressumme)<br/>Direktentladung ≤ 40/35 · Quellwärme der Speicher-WP<br/>(≈ Direktanteil ≤ 53 %)"]
    C1 -.- KOL
    C1 -.- SPEI
    C2 -.- ENT
    C2 -.- HPS

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
    class SPEI speicher
    class SOLD,LAD,ENT,HPL,HPS,WPO,PTH link
    class C1,C2,NETZ regel
    class LAST last
```

## Was die Skizze (nicht) enthält

- **Zeitlich variabel je Stunde:** Last, Außentemperatur → COP Luft, Kollektorleistung, (fester) Strompreis.
- **Fest je Lauf:** alle Wirkungsgrade, Preise, T_oben/Rücklauf/T_unten, Verlustrate, Fläche.
- **Optimiert (✱):** Kollektorfläche, Speichervolumen (innerhalb der gewählten Preisstufe), WP-Leistung,
  PtH-Leistung (mindestens Spitzenlast). Alle Verbindungen (Links) sind ansonsten nicht in der Leistung begrenzt.
- **Nicht im Modell:** Wärmeübertrager-Grenzen, Transmissionsleitung, Speichertemperaturen/Schichtung,
  Teillast der WP, Frostschutz des Kollektorfelds, Stagnation, Netzhydraulik.
- **Kostenseite (nicht in der Skizze):** Jahreskosten nach VDI 2067 je Komponente + Strom; Verteilnetz und
  Gas-Referenz werden in `kpi.py`/`economics.py` zugerechnet (siehe `docs/entscheidungen.md` E25).
