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
