# Was fehlt noch? Kostenrelevante Parameter und Annahmen mit Abweichungsrisiko

Stand 09.11.2026. Richtung: ↑ = Modell unterschätzt die Kosten / ↓ = überschätzt. „Tornado“ = in
`tornado.parameter` enthalten.

## 1 Kostenpositionen, die im Modell fehlen

| Position | Größenordnung (grob) | Wirkung | Vorschlag |
|---|---|---|---|
| Planung, Genehmigung, Bauherrenleistungen | **10 % pauschal im Modell enthalten (E28)**; Spanne real 5–20 % | – | Tornado `oekonomie.nebenkosten` |
| Stromnetzanschluss (Mittelspannung, Trafo) für ≈ 2–3 MW elektrisch | mehrere 100 T€ | ↑ | einmaliger Posten in `pth`/`waermepumpe` oder eigener Parameter |
| Grundstück (Kauf/Pacht 13.000 m²) | standortabhängig | ↑ (v. a. bei großem Kollektorfeld) | €/m² Fläche × Flächenbedarf |
| Heizzentrale/Gebäude, Hydraulik, Leittechnik | DRL: 3,2 Mio. € „Technique building“ (SIF Tab. 1) | ↑ | Zuschlag oder eigener Posten |
| VDI 2067 „sonstige Kosten“ (Versicherung, Verwaltung), Bedienpersonal | typ. 1–2 %/a vom Invest | ↑ | `om_fix` erhöhen oder eigener Satz |
| Betriebskostenförderung BEW Modul 4 (WP, Solarthermie) | Solar ≤ 1 ct/kWh_th; WP abhängig vom Strompreis | ↓ | als Gutschrift je MWh, 10 Jahre |

## 2 Annahmen mit großem Hebel, die (noch) nicht oder nur grob variiert sind

| Annahme | Stand im Modell | Risiko | Tornado |
|---|---|---|---|
| **Strompreisstruktur** | fester Mischpreis 30 ct/kWh | Größter Hebel überhaupt. Real: Arbeitspreis + Leistungspreis, ggf. reduzierte Netzentgelte (§ 14a, atypische Netznutzung), Day-Ahead-Optimierung, PV-Eigenstrom → kann deutlich günstiger *oder* teurer sein | Höhe ja, Struktur nein |
| Gaspreis- und CO₂-Pfad (Referenz) | 12 ct/kWh, 100 €/t, real konstant | entscheidet, ob das System günstiger als Gas ist | ja (Höhe) |
| Förderung BEW | Basis 0 % | 40 % Invest-Zuschuss senkt LCOH spürbar | ja (40 %) |
| Lebensdauern, O&M-Sätze | VDI/DEA-Größenordnung | ±10–20 % auf Kapitalkosten | nein |
| Hausanschlusskosten: wer zahlt? | 10.000 €/Stück im Wärmepreis | oft per Baukostenzuschuss vom Kunden → Wärmepreis ↓ | Höhe ja |
| Netz 80/45 °C, Netzverluste 17 % | aus NB | Rücklauf ja; Verluste nur als Variante „extra Dämmung“ | Rücklauf ja |

## 3 Technische Annahmen, bei denen das Modell eher zu optimistisch ist

| Annahme | Warum optimistisch | Wirkung |
|---|---|---|
| Speicher als ein Energiespeicher + Jahresregel 53 % | keine Mischung/Schichtungsverluste, Temperaturen immer passend | Speichernutzen ↑ |
| Verlustrate aus Dronninglund (60.000 m³) | kleine Becken haben relativ mehr Oberfläche | Verluste ↓ (Tornado bis 8·10⁻⁵) |
| Perfekte Voraussicht | Betrieb kennt Wetter und Last des ganzen Jahres | Betriebskosten ↓, Solaranteil ↑ |
| Luft-WP ohne Teillast-/Mindestlastgrenzen, Leistung temperaturunabhängig | reale Großanlagen verlieren bei Frost Leistung, takten in Teillast | Kosten ↓, WP-Anteil ↑ |
| Kollektorkennwerte angenommen (Keymark nicht abrufbar), ohne Einfallswinkelkorrektur | | Ertrag ↑ (wenige %) |
| TMY aus Satellitendaten 2005–2023 | ≈ 13 % mehr Strahlung als DWD-Bodenmessung 1992–2010 | Solar ↑ |
| Standardlastprofile | geglättete Spitzen | PtH-/WP-Leistung ↓ |

## 4 Was ist bei Bad Lippspringe robust?

- Wärmepumpe (Luft + Speicher) mit PtH-Reserve ist in fast allen Varianten günstiger als die Gas-Referenz.
- Größe von Kollektorfeld und Speicher ist kostenseitig fast egal (flaches Optimum, Preisstufen ±2 €/MWh)
  → Solaranteil und Speichergröße als Bandbreite berichten; Entscheidung über CO₂/Förderung/Fläche.
- Netzkosten (≈ 50 €/MWh geliefert) sind ein großer Block im Wärmepreis, aber gleich für System und
  Gas-Fernwärme.
