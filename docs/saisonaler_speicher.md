# Warum lohnt sich der Saisonspeicher in Dänemark – und im Modell für Bad Lippspringe nicht?

Stand 09.11.2026. Modell: Basislauf mit stetiger Speicherkostenkurve (E30). Zahlen aus Rechnungen mit dem
Modell (Raster 24 Läufe, 12 Szenarien) und aus Recherchen (Quellen unten).

## 1 Befund im Modell

Der Basislauf wählt ein **Kurzzeit-/Wochenspeicher**: ≈ 1.600 m³ (≈ 140 MWh), **≈ 5 Zyklen pro Jahr**, nur 28 % der Entladung im Winter (Nov–Mär), Solaranteil ≈ 24 %. Ein Saisonspeicher hätte < 2 Zyklen und ≥ 60 % Winteranteil (Kennzahl `speicher_charakter` in `serts run`). Dronninglund: ≈ 2 Zyklen, ≈ 40 % Solaranteil.

## 2 Warum es sich in Dänemark lohnt (recherchiert)

| Faktor | Dänemark | Quelle / Bemerkung |
|---|---|---|
| **Größe und Skaleneffekt** | Speicherkosten fallen mit der Größe: Ottrupgård 1.500 m³ ≈ 150 €/m³, Marstal 10.000 m³ ≈ 67, Dronninglund 60.000 m³ ≈ 38, Marstal 75.000 m³ ≈ 36, Vojens 210.000 m³ ≈ **24 €/m³** (2014/15) | [Solar Thermal World, 2019](https://solarthermalworld.org/news/seasonal-pit-heat-storage-cost-benchmark-30-eurm3/) |
| **Günstige Kollektorfelder** | Dronninglund: 5,86 Mio. € für 37.573 m² ≈ **164 €/m²** (2014); große Felder > 10.000 m² „bis 200 €/m²“ inkl. Montage | lokale Dronninglund-Studie (Sifnaios et al. 2023, Tab. 1); [Solar Thermal World](https://solarthermalworld.org/?p=22896) (Websuche-Zusammenfassung) |
| **Solarwärmepreis** | **31–56 €/MWh** (3.000 m² mit Tank, 3 % Zins: 46–56 laut PlanEnergi/Solites; große Felder ab 31; neuere Anlagen ≈ 40) | [Solar Thermal World, 2014](https://solarthermalworld.org/news/germanydenmark-solar-district-heating-prices-between-37-and-88-eurmwh/): Spanne 37–88 €/MWh je nach Zins (3–8 %) und Förderung (0–40 %); 31 und ≈ 40 aus Websuche-Zusammenfassungen |
| **Finanzierung** | kommunale Versorger mit ≈ **3 %** Zins; in Deutschland wird für Stadtwerke 8 % als üblich genannt | Solites/Arcon in der Quelle von 2014; Kreditprogramm selbst nicht belegt |
| **Heizpreisregulierung** | Fernwärme ist per Gesetz Non-Profit, Preis = tatsächliche Kosten (Wärmeversorgungsgesetz 1979); Preisdeckel richtet sich nach den Kosten einer Einzel-Luft-WP | Zusammenfassungen (Taiwan-Präsentation, [The Local DK 2024](https://www.thelocal.dk/20240701/denmark-to-introduce-limit-on-district-heating-prices)) |
| **Gassteuer** | Vojens „rein kommerziell, nur indirekt subventioniert über die Energiesteuer auf Gas“ | **nur eine Quelle** (Projektbeschreibung [Solmax](https://www.solmax.com/global/en/case-studies/worlds-largest-pit-thermal-storage-in-vojens)), Höhe nicht belegt |
| **Anlagengröße** | Vojens: 71.000 m² Kollektor + 203.000 m³, 45 % Solaranteil; mit Saisonspeicher > 50 %, mit herkömmlichen Speichern ≤ 25 % | Websuche-Zusammenfassungen ([State of Green](https://stateofgreen.com/en/solutions/world-largest-thermal-pit-storage-in-vojens/), Solar Thermal World; Seite selbst nicht lesbar); Fisch et al.: 50–70 % mit Saisonspeicher gegen 10–20 % mit Kurzzeitspeichern |
| **Strom-Kopplung** | Saisonspeicher als billige Nutzung von Windüberschuss, Kombination mit Wärmepumpen | [Solar Thermal World, 2019](https://solarthermalworld.org/news/seasonal-pit-heat-storage-cost-benchmark-30-eurm3/) |

Nicht gefunden: eine belegte Mindestgröße für wirtschaftliche Saisonspeicher (nur: Saisonspeicher ab ≈ 1.500 MWh/a
Wärmebedarf nach Hahne; Verhältnis Speicher/Kollektor 2–3 m³/m², unklar belegt).

## 3 Warum das Modell anders entscheidet – einfache Kostenrechnung

Kosten je MWh, im Modell (5 % real, 10 % Nebenkosten, Kollektor 25 a, Speicher 25 a) gegen dänisch-nahe Werte
(DRL 2014; „2025“ = ×1,5 wie beim Speicher; 3 % Zins, ohne Nebenkosten):

| | Bad Lippspringe (Modell) | Dänemark (DRL-nah) |
|---|---|---|
| Kollektorwärme (Kosten je MWh Kollektorertrag) | 450 €/m², 533 kWh/m²a → **78 €/MWh** | 164 €/m², 430 kWh/m²a → **27**; mit 2025er Preisen 40 €/MWh |
| Speicher je MWh Durchsatz bei 1 / 2 Zyklen | 124 €/m³ (5.000 m³) → **95–124** bzw. 62 €/MWh | 38 €/m³, 2 Zyklen → **14**; mit 2025er Preisen 21 €/MWh |
| Saisonale Solarwärme gesamt (≈ Kollektor + Speicher, ohne Verluste) | **≈ 170–200 €/MWh** | **≈ 40–60 €/MWh** |
| Alternative im Winter | Luft-WP bei 30 ct/kWh: 300 / COP 2,3 = **130 €/MWh** (Sommer: 94, Speicher-WP: 67) | Gas/Biomasse/WP im kostenbasierten Fernwärmepreis |

Im Modell ist Saisonwärme also **teurer als die Alternative** (Luft-WP, 130 €/MWh), im dänischen Fall
**deutlich billiger**. Der Kurzzeitspeicher (≈ 5 Zyklen, ≈ 170 €/m³) kostet nur ≈ 30 €/MWh Durchsatz und lohnt sich
daher: Er verschiebt Solarwärme von mittags auf abends/Wochen und spart Sommer-WP-Strom.

**Strukturelle Gründe im Modell (Bad Lippspringe statt Dänemark):**
1. **Maßstab:** 5,5 GWh/a statt 37–50 GWh/a; PTES ≈ 5.000–10.000 m³ statt 60.000–200.000 m³ → Speicherkosten
   ≈ 95–170 €/m³ statt 24–38 €/m³ (Skaleneffekt, Exponent −0,31).
2. **Fläche:** Nur 13.000 m². Dronninglund braucht ≈ 10 ha (Kollektoren ×2,3 + Becken). Hier: Kollektorfeld ≤ 4.500 m² bei 8.000–10.000 m³ Speicher – das Feld ist zu klein, um einen großen Speicher zu füllen.
3. **Kostenniveau:** Kollektor 450 €/m² (kleines Feld, Planungsbudget 2020) statt 164–250 €/m².
4. **Zins und Nebenkosten:** 5 % real + 10 % Nebenkosten gegen 3 % Kommunalkredit.
5. **Alternative:** Eine Luft-WP (COP 2,3–3,3) mit 30 ct/kWh ist kein billiger Referenzfall für Solarwärme – die dänische Alternative sind kostenbasierte Fernwärmepreise (inkl. Steuer auf Gas).
6. **Modellannahmen, die Saisonspeicher benachteiligen:** konstante Verlustrate 4·10⁻⁵ 1/h (ohne Skaleneffekt der Oberfläche), Speicher-WP mit konstantem COP 4,5, kein Wärmeübertrager-/Mischungseffekt; **begünstigen**: perfekte Voraussicht.

## 4 Welche Parameter müssten sich ändern? (Rechnungen mit dem Modell)

Kennzeichnung: **saisonal** = < 2 Zyklen und ≥ 60 % Entladung im Winter. Raster Speicherkosten-Faktor
(0,35 / 0,5 / 0,7 / 1,0 × der Kostenkurve) × Kollektorkosten (450 / 350 / 250 €/m²) × Fläche (13.000 / 30.000 m²):

| Speicherkosten (Faktor) | Kollektor €/m² | Fläche | Kollektor / Speicher | Zyklen  | Winteranteil | Solar | LCOH  | Charakter     |
| ----------------------- | -------------- | ------ | -------------------- | ------- | ------------ | ----- | ----- | ------------- |
| 1,0 (Basis)             | 450            | 13.000 | 2.540 m² / 1.640 m³  | 5,0     | 28 %         | 24 %  | 141,2 | Kurzzeit      |
| 1,0                     | 350            | 13.000 | 4.490 / 7.080        | 2,6     | 47 %         | 42 %  | 135,4 | gemischt      |
| 1,0                     | 350            | 30.000 | 6.790 / 16.510       | **1,8** | **61 %**     | 62 %  | 134,9 | **saisonal**  |
| 1,0                     | 250            | 30.000 | 8.800 / 25.880       | **1,5** | **69 %**     | 79 %  | 121,5 | **saisonal**  |
| 0,7                     | 450            | 13.000 | 4.230 / 8.290        | 2,0     | 57 %         | 39 %  | 139,0 | fast saisonal |
| 0,5                     | 450            | 13.000 | 4.070 / 9.670        | **1,7** | **68 %**     | 37 %  | 136,1 | **saisonal**  |
| 0,35                    | 450            | 13.000 | 3.920 / 10.540       | **1,5** | **75 %**     | 36 %  | 133,7 | **saisonal**  |
| 0,35                    | 250            | 13.000 | 4.360 / 7.860        | 2,3     | 53 %         | 41 %  | 119,6 | gemischt      |
| 0,35                    | 250            | 30.000 | 8.770 / 26.080       | **1,5** | **70 %**     | 78 %  | 101,9 | **saisonal**  |

**Einzelne Hebel** (alles andere Basis, Fläche 13.000 m²; Szenarien-Sweep):

| Änderung | Speicher | Zyklen | Winteranteil | Wirkung |
|---|---|---|---|---|
| Kollektor 250 €/m² (DRL inflationsber.) | 7.000 m³ | 2,7 | 46 % | **gemischt** (mehr Solar, größerer Speicher) |
| Speicherkosten × 0,35 (≈ 35 €/m³ bei 10.000 m³) | 10.500 m³ | 1,5 | 75 % | **saisonal** |
| Zins 3 % | 7.300 m³ | 2,5 | 48 % | gemischt |
| BEW 40 % | 7.200 m³ | 2,6 | 47 % | gemischt |
| Strom 40 ct/kWh | 7.200 m³ | 2,6 | 47 % | gemischt (Solar lohnt, aber noch kein Saisonspeicher) |
| Kollektor 250 + Speicher × 0,35 | 7.900 m³ | 2,3 | 53 % | gemischt – das Feld ist auf 13.000 m² zu klein |
| … + Fläche 40.000 m² | 32.500 m³ | 1,4 | 71 % | **saisonal, Solaranteil 90 %**, LCOH 98 €/MWh |
| Dänemark-Maßstab (Last × 7 = 38 GWh, Fläche 150.000 m², Kollektor 250, Kostenkurve bis 300.000 m³) | 128.000 m³ (A = 44.000 m²) | 1,6 | 69 % | **saisonal, Solaranteil 66 %** (Dronninglund 40 %, Vojens 45 %) |

### Antwort auf „Welche Parameter müssten sich ändern?“

Ein Saisonspeicher entsteht, wenn **Saisonwärme billiger wird als Winterstrom für die Wärmepumpe** (≈ 130 €/MWh)
**und** genug Fläche da ist, das Feld und den Speicher zu bauen. Am wirksamsten (in dieser Reihenfolge):

1. **Speicherkosten ≈ halbieren bis dritteln** (Faktor 0,35–0,5 ≙ ≈ 35–50 €/m³ bei 10.000 m³ statt ≈ 100 €/m³;
   das liegt auf dem Niveau von Dronninglund/Marstal 36–38 €/m³ in 2014er Preisen). Mit 13.000 m² genügt das
   bereits für einen saisonalen Speicher von ≈ 10.000 m³.
2. **Mehr Fläche und billigere Kollektoren:** ab ≈ 30.000 m² Grundstück genügt ein Kollektorpreis von ≈ 350 €/m²
   (statt 450) – dann ist der Speicher mit ≈ 16.500 m³ saisonal. Ab ≈ 250 €/m² steigt der Solaranteil auf ≈ 80 %.
3. **Maßstab:** ein größeres Netz (z. B. Quartier + Nachbarorte, ≥ 20–40 GWh/a) senkt die Speicherkosten durch
   den Skaleneffekt; so rechnet Dänemark.
4. **Zins/Förderung (3 % bzw. 40 % BEW):** verschieben das Optimum zu mehr Solar, aber **allein nicht** zum
   Saisonspeicher; erst in Kombination mit (1) oder (2).
5. **Strompreis hoch** (40 ct) hat nur eine schwache Wirkung auf die Saisonalität (2,6 Zyklen); er macht Solar
   attraktiv, aber der Speicher bleibt ein Kurz-/Mittelfristspeicher.

**Was sich nicht ändern lässt:** das Klima (Heizlast im Winter, Strahlung im Sommer) – das ist der Grund, warum
überhaupt saisonale Speicherung gebraucht wird; die Konsequenz ist nur, dass die Kostenschwelle erreicht werden muss.

## 5 Grenzen dieser Aussage

Die Schwellen hängen an Annahmen: Speicherkostenkurve (Exponent −0,31, Preisindex 1,5), Kollektorertrag
(533 kWh/m²a, TMY 35° Süd), Verlustrate (4·10⁻⁵ 1/h), Strompreis fest 30 ct, perfekte Voraussicht. Die Dänemark-Zahlen
stammen aus Quellen von 2014/2019; die dänische Gassteuer und das Kreditprogramm sind nicht belegt.
