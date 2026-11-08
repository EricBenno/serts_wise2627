"""Aufbau des PyPSA-Netzes aus Config + Zeitreihen (BRF §3). Stand: Gerüst für M2/M3.

Busse (BRF §3.1):
    elec [MW], sol_hi / sol_lo [MW], V85 / V45 / V10 [m3], heat_plant [MW], heat_town [MW],
    hp_src [MW] (Quellwärme WP aus PTES), heat_pth_st [MW] (PtH -> Speicher, Variante)

Konventionen:
- Kollektor: p_nom = A[m2] * 1e-3, p_max_pu = P_spez[kW/m2] (solar.py)
- Pools: Store-Energie = Volumen [m3], e_nom = V, e_cyclic = True
- Pool-Links: efficiency = 1 (Volumen), Wärme über bus2 mit efficiency2 = ±dT * c
  (Vorzeichen: negativ = Entnahme vom Wärmebus, positiv = Abgabe)
"""

from __future__ import annotations

import pandas as pd

from serts.config import Config

BUSSE: dict[str, str] = {
    "elec": "MW",
    "sol_hi": "MW",
    "sol_lo": "MW",
    "V85": "m3",
    "V45": "m3",
    "V10": "m3",
    "heat_plant": "MW",
    "heat_town": "MW",
    "hp_src": "MW",
    "heat_pth_st": "MW",
}

# Pflichtparameter für einen Lauf (Abbruch, wenn null) – bei neuen Komponenten ergänzen
PFLICHT = [
    "kollektor.eta0",
    "kollektor.a1",
    "kollektor.a2",
    "kollektor.neigung",
    "ptes.x_HX_lad",
    "ptes.x_HX_ent",
    "netz.x_TL",
    "strom.preis_fest",
    "strom.emissionsfaktor",
]


def pool_links(cfg: Config) -> list[dict]:
    """Tabelle der Volumen-Links (BRF §3.2) inkl. Wärme-Effizienz auf bus2 [MWh/m3]."""
    c = cfg.get("ptes.c_wasser")
    t_hi, t_mid, t_lo = (cfg.get(f"ptes.T_{k}") for k in ("oben", "mitte", "unten"))
    return [
        dict(
            name="laden_hi_aus45",
            bus0="V45",
            bus1="V85",
            bus2="sol_hi",
            efficiency2=-(t_hi - t_mid) * c,
        ),
        dict(
            name="laden_hi_aus10",
            bus0="V10",
            bus1="V85",
            bus2="sol_hi",
            efficiency2=-(t_hi - t_lo) * c,
        ),
        dict(
            name="laden_lo", bus0="V10", bus1="V45", bus2="sol_lo", efficiency2=-(t_mid - t_lo) * c
        ),
        dict(
            name="pth_laden",
            bus0="V45",
            bus1="V85",
            bus2="heat_pth_st",
            efficiency2=-(t_hi - t_mid) * c,
        ),
        dict(
            name="entladen_direkt",
            bus0="V85",
            bus1="V45",
            bus2="heat_plant",
            efficiency2=(t_hi - t_mid) * c,
        ),
        dict(
            name="wp_quelle_ptes",
            bus0="V45",
            bus1="V10",
            bus2="hp_src",
            efficiency2=(t_mid - t_lo) * c,
        ),
        dict(name="verlust_oben", bus0="V85", bus1="V45"),
        dict(name="verlust_mitte", bus0="V45", bus1="V10"),
    ]


def build_network(cfg: Config, ts: pd.DataFrame, A_koll_m2: float, V_m3: float):
    """Baut das Netz für feste Größen (A, V) aus dem Raster.

    TODO M2 (48 h, ohne Speicher): elec_grid-Generator (marginal_cost = Strompreis),
      sol_hi/sol_lo-Generatoren, Link sol_hi->heat_plant, hp_air/hp_ptes-Multilinks,
      PtH-Link elec->heat_town, Transmission heat_plant->heat_town, Last an heat_town.
    TODO M3: Pool-Stores V85/V45/V10 + pool_links(); Constraints aus constraints.py.
    Abnahme: siehe docs/struktur.md (Energiebilanz < 0,1 %, Volumensumme = V je Stunde).
    """
    cfg.require(PFLICHT)
    raise NotImplementedError("M2/M3: build_network noch nicht umgesetzt")
