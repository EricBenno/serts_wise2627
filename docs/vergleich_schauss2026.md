# Comparison: Schauß et al. 2026 ("Mind the temperature gap") vs. SERTS model (21.11.2026)

Paper: Schauß, Schledorn, Kähler, Schumacher, Ammon, Brown: *Mind the temperature gap: Pit thermal energy storage in
sector-coupled energy systems with high-temperature district heating*. Advances in Applied Energy 24 (2026) 100315,
doi:10.1016/j.adapen.2026.100315 (+ supplementary information). PDF: `../AP 0 und Annahmen/other papers/`.
Model state compared: after E39/E40 (`docs/speichermodell.md`, `docs/systemskizze.md`).

## 1 In one sentence

Same tool family (PyPSA, linear, perfect foresight) and the same core message, namely that **PTES must be modelled
temperature-aware**. The scales are opposite: the paper covers 40 German DH systems inside a national energy
system, with no solar thermal and supply temperatures ≥ 90 °C. SERTS covers one 80/45 °C network with solar thermal
as the main heat source. SERTS models the storage **in more detail** (three layers, stratification, validated
against Dronninglund). The paper models **boosting and the heat-pump COP more systematically**.

## 2 Scope

| | Paper (PyPSA-DE) | SERTS |
|---|---|---|
| System | Germany + neighbours, 40 largest DH systems, sector-coupled, brownfield CHP | one DH network (Bad Lippspringe, small/large), greenfield generation |
| Time | 2045, weather 2019, **3-hourly** | weather year 2022/TMY, **hourly** |
| Electricity price | endogenous (nodal shadow price) | exogenous: fixed 30 ct/kWh or day-ahead time series |
| Heat sources | air/river/sea/geothermal/electrolysis HP, resistive heater, CHP, boilers, waste | **solar thermal**, air HP, storage HP, PtH |
| Storage | PTES + TTES | PTES only |
| Network temperatures | forward 90–124 °C, return 46–60 °C (three scenarios) | 80/45 °C (sliding forward 70–80 °C as scenario) |

The paper explicitly leaves out solar thermal (limitations section). Its PTES is charged by power-to-heat and CHP
surplus heat, whereas in SERTS it is charged mainly by the collector field.

## 3 PTES

| Aspect | Paper | SERTS | Assessment |
|---|---|---|---|
| Energy capacity | one store, (T_top − T_bottom)·c·ρ·V, T_bottom = return temperature or 10 °C (Eq. 2a) | three stores: core 85 °C, transition zone 45–85 °C, cold part 10–45 °C, in fixed ratios | **overlap**: both make capacity depend on the temperature spread; SERTS splits it by usability |
| Stratification | **none** (named as limitation) | fill level core ≤ zone ≤ cold, every hour; transition zone 15 % at 60,000 m³, checked against Dronninglund 2014 | SERTS more detailed |
| Top temperature | fixed 90 °C (sensitivity, resistive boosting: savings 213 / 330 / 463 M€/a at 85 / 90 / 95 °C) | fixed 85 °C (liner limit), `sens: [90]` exists but **not in the tornado** | gap → add `ptes.T_oben` to tornado |
| Standing losses | constant 0.19 %/d = 7.8·10⁻⁵ 1/h | 4·10⁻⁵ 1/h at 60,000 m³ × (V/60,000)^(−1/3) → 8.6·10⁻⁵ at 6,000 m³, 5.0·10⁻⁵ at 30,300 m³ | **good agreement** for small net; SERTS adds size dependence |
| Charge/discharge power | limited by energy-to-power ratio μ^e2p · V (Eq. 2d) | storage links unlimited (`p_nom = 1000 MW`); in practice limited by collector, load and PtH | gap, small effect (see §6) |
| Investment cost | 63 €/m³ flat (Danish Energy Agency) | KWW curve, degressive: ≈ 120 €/m³ at 6,000 m³, ≈ 75 €/m³ at 30,000 m³ | SERTS more conservative and size-dependent |
| Land use | 25,000 m² per 70,000 m³ = **2.8 m³/m²**; eligible land from OSM, Natura 2000, groundwater | `volumen_je_grundflaeche` **2.65 m³/m²**; shared area limit with collector field | **good agreement** |
| Cycles | 3–24 a⁻¹ depending on configuration; Høje-Taastrup 6.5–8.2 a⁻¹ | 3.2 (small) / 4.3 (large); seasonal 1.4–1.7 only without area limit | consistent: both find short/mixed operation |

## 4 Heat pumps and boosting

| Aspect | Paper | SERTS | Assessment |
|---|---|---|---|
| Discharge when supply temperature > top temperature | **boosting**: per unit of discharge α = (T_fwd − T_top)/(T_top − T_ret) of extra heat from a resistive heater or heat pump (Eq. 4) | not needed in base case: T_VL 80 °C < T_oben 85 °C, core goes directly to the network | in the paper's terms SERTS is a "no-boost" system; its main penalty does not apply to us |
| Water below supply temperature | in "HP boosting" the booster HP uses PTES water below the return temperature as source | **`vorwaermen`**: transition zone pre-heats return, only together with HP/PtH reheating (≤ 0.75 × (HP + PtH)); same structure as α·q_discharge ≤ q_boost | **overlap in method** (fixed ratio set a priori, linear) |
| Cooling the bottom | "HP Boosting (10 °C)" cools the bottom to 10 °C and enlarges capacity; **only this variant beats resistive boosting** | storage HP (`hp_speicher`) uses the cold part 45 → 10 °C as source | **paper confirms the SERTS design**: an HP on the storage pays mainly because it enlarges usable capacity |
| COP method | Jensen et al. (2018): ammonia, isentropic efficiency 80 %, 6 K source ΔT; sink/source inlet/outlet temperatures; time-varying; PTES-HP COP 3–6 | air HP: KWW quality grade × Carnot (0.452·T_VL/(T_VL − T_a)); storage HP: constant 4.5 | different method, similar values; both keep the storage-source temperature fixed |
| Forward temperature curve | piecewise linear: maximum at T_a ≤ 0 °C, minimum at ≥ 10 °C, floor 90 °C; affects all COPs and boosting | `vl_gleitend`: 80 °C at ≤ −10 °C, 70 °C at ≥ 15 °C (24 h mean), only affects the air HP COP | similar approach; scenario only in SERTS |
| HP cost | air 906 €/kW_th, PTES HP 598 €/kW_th (separate units) | one shared HP 1,340 €/kW (`wp_out`, air + storage) | SERTS more expensive and does not distinguish |
| Charging by power-to-heat | main value source: resistive heaters charge in cheap hours (50 % of charging in ≈ 3 % of time steps) | only in day-ahead scenarios (`laden_netz`): 480–770 MWh/a, worth ≈ 3 €/MWh (2024 prices) | consistent; smaller in SERTS because solar already fills the store |

## 5 System sketch

The paper's Fig. 2 is a **hydraulic/temperature diagram**. The charging path runs at T_fwd into the top, the return
goes to the bottom, and the discharge leaves from the top through the booster to the load. The HP variant also shows
the source flow at T_bottom. The SERTS sketch (`docs/systemskizze.md`) is a **component/bus diagram**: it shows exactly
what the LP contains (links, stores, constraints), but the temperature logic only appears in the labels.

| | Paper Fig. 2 | SERTS Systemskizze |
|---|---|---|
| Purpose | explain temperature levels and flow paths | 1:1 image of the PyPSA network + constraints |
| Storage | one tank with gradient T_top → T_bottom | three stores (core / zone / cold) + mixing links |
| Booster/HP | in the discharge path between storage and load | `hp_speicher` with cold part as source; `vorwaermen` as pre-heater |
| Optimised sizes, costs, constraints | not shown | shown (✱, C1–C5) |

Suggestion: put a second, small hydraulic view in the style of Fig. 2 next to the existing sketch. It would show
the network at 80/45 °C, the collector charging 45→85 °C (top) and 10→45 °C (bottom), the direct discharge from the
top, pre-heating from the zone, and the HP using the cold part as source. That makes "why no boosting at 80 °C" and
"why the storage HP adds capacity" visible at a glance and directly comparable to the paper. The LP does not change.

## 6 What SERTS could take from the paper (cheap, ranked)

**Status 21.11.2026 (E41):** points 1–4 are implemented. Top temperature is in the tornado (80/90 °C), and
below 85 °C direct discharge needs boosting. Air and storage heat pumps are separate units (storage HP 1,100 €/kW,
KWW Tab. 26/27). The storage-HP COP follows Jensen et al. as in the paper: 3.91 instead of 4.5, and the
implementation reproduces the paper's Fig. S7 within ±0.02. Charge/discharge is limited by the Dronninglund
diffuser flow (0.0094 per hour × V). See `docs/entscheidungen.md` E41.

1. **Add `ptes.T_oben` to the tornado** (sens 90 already exists; add 80). The paper shows top temperature as a
   first-order driver. In SERTS, 85 °C is exactly T_VL + 5 K (`hinweis` of `ptes.T_oben`), so a lower top temperature
   should hit direct discharge hard (check what the model does below 85 °C before running). Cost: 2 extra tornado
   runs.
2. **Boosting when the forward temperature exceeds T_oben**: generalise the `vorwaermen` constraint so that
   `entladen_direkt` needs α(t)·(HP + PtH) whenever T_VL(t) > T_oben (Eq. 4a, α precomputed per hour). Only relevant
   if a scenario raises the forward temperature above 85 °C (e.g. an existing high-temperature network). Not needed
   for the base case; document as "not needed because 80 < 85 °C".
3. **Sensitivity: cheaper storage HP**. The paper prices PTES heat pumps ≈ 34 % below air heat pumps. In SERTS
   both share one capacity. Either a sensitivity on `waermepumpe.kosten_spez`, or later two separate HP
   capacities (one more variable).
4. **Energy-to-power limit on charge/discharge** (Eq. 2d). Effect is small in SERTS: solar charging is limited by
   the collector, discharge by the load, grid charging by the PtH capacity. Only worth adding with a sourced e2p
   value (Danish Energy Agency technology data; not looked up, no number invented).
5. **Citations for the report**: the paper supports our loss rate (0.19 %/d ≈ 8.6·10⁻⁵ 1/h at 6,000 m³), the land
   factor (2.8 vs 2.65 m³/m²), and the main methodological argument of E34–E39: temperature-agnostic PTES
   overstates savings by up to 4×.

## 7 Where SERTS goes beyond the paper (useful for positioning)

- Stratification with a validated transition zone; separate charging bands; size-dependent losses.
- Solar thermal as the main charging source and the land competition between collector field and PTES (the paper
  limits land per storage only).
- Hourly resolution and a single-site cost curve (KWW) instead of one flat €/m³.

The paper in turn goes beyond SERTS in system scope (endogenous prices, CHP, TTES, many heat sources), its COP method,
and its explicit boosting configurations.
