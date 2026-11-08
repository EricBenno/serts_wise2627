"""Zusatz-Constraints über ``extra_functionality`` (linopy), BRF §3.2-3.4.

1. Volumensumme:   e_V85(t) + e_V45(t) + e_V10(t) = V                     für alle t
2. Verluste:       p_verlust_oben(t)  = lambda * e_V85(t)
                   p_verlust_mitte(t) = lambda * e_V45(t)
3. Kollektorfläche p_hi(t)*P_lo(t) + p_lo(t)*P_hi(t) <= A' * P_hi(t)*P_lo(t)
                   (A' = A*1e-3 MW, nur Stunden mit P_hi, P_lo > 0; sonst greift p_max_pu)
4. WP je Quelle:   COP_luft(t) * p_hp_air(t)  <= p_max_pu_luft(t) * P_WP
                   COP_ptes    * p_hp_ptes(t) <= p_max_pu_ptes    * P_WP
                   (Summe <= P_WP über Link hp_out, siehe network.py)

Jede Constraint hat einen Test (tests/test_modell.py).
"""

from __future__ import annotations

import pandas as pd

from serts.config import Config
from serts.network import POOLS


def _sel(var, name: str):
    return var.sel(name=name)


def extra_functionality(n, snapshots, *, cfg: Config, ts: pd.DataFrame) -> None:
    m = n.model
    V = float(n.meta["V_m3"])
    A = float(n.meta["A_koll_m2"]) * 1e-3
    link_p = m["Link-p"]

    # 1 + 2: Pool-Speicher
    if V > 0:
        e = m["Store-e"]
        m.add_constraints(sum(_sel(e, p) for p in POOLS) == V, name="pool_volumensumme")
        lam = cfg.get("ptes.verlustrate")
        m.add_constraints(
            _sel(link_p, "verlust_oben") - lam * _sel(e, "V85") == 0, name="pool_verlust_oben"
        )
        m.add_constraints(
            _sel(link_p, "verlust_mitte") - lam * _sel(e, "V45") == 0, name="pool_verlust_mitte"
        )

        # 3: gemeinsame Kollektorfläche
        P_hi = ts["P_hi"].clip(0, 1)
        P_lo = ts["P_lo"].clip(0, 1)
        maske = (P_hi > 0) & (P_lo > 0)
        if maske.any():
            sn = ts.index[maske]
            gp = m["Generator-p"].sel(snapshot=sn)
            hi = pd.Series(P_hi[maske].to_numpy(), index=pd.Index(sn, name="snapshot")).to_xarray()
            lo = pd.Series(P_lo[maske].to_numpy(), index=pd.Index(sn, name="snapshot")).to_xarray()
            m.add_constraints(
                lo * _sel(gp, "sol_hi") + hi * _sel(gp, "sol_lo") <= A * hi * lo,
                name="kollektor_flaeche",
            )

    # 4: WP-Leistung je Quelle gegen die gemeinsame thermische Kapazität
    P_wp = m["Link-p_nom"].sel(name="hp_out")
    cop = pd.Series(
        ts["COP_luft"].to_numpy(), index=pd.Index(ts.index, name="snapshot")
    ).to_xarray()
    pu = pd.Series(
        ts["p_max_pu_luft"].to_numpy(), index=pd.Index(ts.index, name="snapshot")
    ).to_xarray()
    m.add_constraints(cop * _sel(link_p, "hp_air") - pu * P_wp <= 0, name="wp_luft_kapazitaet")
    if V > 0:
        cop_p = cfg.get("waermepumpe.COP_ptes")
        pu_p = cfg.get("waermepumpe.p_max_pu_ptes")
        m.add_constraints(
            cop_p * _sel(link_p, "hp_ptes") - pu_p * P_wp <= 0, name="wp_ptes_kapazitaet"
        )
