"""Drei Zusatzbedingungen (linopy) – alles andere erledigt PyPSA selbst.

1. Fläche:   A_Koll * flaechenfaktor + V / volumen_je_grundflaeche <= flaeche_verfuegbar
             (V = E_heiß / (f * kap); nur wenn A oder V optimiert wird, sonst Check in kpi.py)
2. Speicher: E_kalt = (1 - f) / f * E_heiß     (die beiden Speicherteile wachsen im festen Verhältnis,
             f = (T_oben - T_RL) / (T_oben - T_unten) ≈ 53 %; nur wenn das Volumen optimiert wird)
3. WP bei Kälte: COP_luft(t) * p_hp_luft(t) <= p_max_pu_luft(t) * P_WP
             (thermische Leistung der Luft-WP sinkt bei Kälte; Speicher-WP nicht betroffen)

Die frühere Jahresregel „Direktanteil <= 53 %“ und die Monatsbeschränkung der Speicher-WP entfallen:
das feste Verhältnis heiß : kalt gilt jetzt in jeder Stunde (docs E27).
"""

from __future__ import annotations

import pandas as pd

from serts.config import Config
from serts.network import M2_JE_MW, anteil_heiss, mwh_je_m3


def _sel(var, name: str):
    """Eine Komponente auswählen und die Namens-Koordinate entfernen (linopy-v1-kompatibel)."""
    return var.sel(name=[name]).sum("name")


def _zeitreihe(werte, index):
    return pd.Series(
        pd.Series(werte).to_numpy(), index=pd.Index(index, name="snapshot")
    ).to_xarray()


def extra_functionality(n, snapshots, *, cfg: Config, ts: pd.DataFrame) -> None:
    m = n.model
    hat_speicher = "ptes_heiss" in n.stores.index
    f = anteil_heiss(cfg)

    # 1 Fläche
    a_var = bool(n.generators.at["kollektor", "p_nom_extendable"])
    v_var = hat_speicher and bool(n.stores.at["ptes_heiss", "e_nom_extendable"])
    if a_var or v_var:
        kap = mwh_je_m3(cfg)
        a = (
            _sel(m["Generator-p_nom"], "kollektor")
            if a_var
            else n.generators.at["kollektor", "p_nom"]
        )
        lhs = a * M2_JE_MW * cfg.get("kollektor.flaechenfaktor")
        if hat_speicher:
            e = (
                _sel(m["Store-e_nom"], "ptes_heiss")
                if v_var
                else n.stores.at["ptes_heiss", "e_nom"]
            )
            lhs = lhs + e / (kap * f) / cfg.get("ptes.volumen_je_grundflaeche")
        m.add_constraints(lhs <= cfg.get("standort.flaeche_verfuegbar"), name="flaeche")

    # 2 feste Aufteilung heiß : kalt
    if v_var:
        e_h = _sel(m["Store-e_nom"], "ptes_heiss")
        e_k = _sel(m["Store-e_nom"], "ptes_kalt")
        m.add_constraints(e_k - (1.0 - f) / f * e_h == 0, name="speicher_verhaeltnis")

    # 3 Luft-WP: Leistung sinkt bei Kälte
    wp_variabel = bool(n.links.at["wp_out", "p_nom_extendable"])
    p_wp = _sel(m["Link-p_nom"], "wp_out") if wp_variabel else n.links.at["wp_out", "p_nom"]
    cop = _zeitreihe(ts["COP_luft"], ts.index)
    pu = _zeitreihe(ts["p_max_pu_luft"], ts.index)
    m.add_constraints(cop * _sel(m["Link-p"], "hp_luft") - pu * p_wp <= 0, name="wp_luft_leistung")
