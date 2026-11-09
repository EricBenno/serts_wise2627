"""Zwei Zusatzbedingungen (linopy) – alles andere erledigt PyPSA selbst.

1. Fläche:  A_Koll * flaechenfaktor + V / volumen_je_grundflaeche <= flaeche_verfuegbar
            (nur wenn A oder V optimiert wird; bei festen Größen nur Check in kpi.py)
2. Temperatur-Regel des Speichers, vereinfacht über das Jahr:
            Σ Direktentladung <= f * (Σ Direktentladung + Σ Quellwärme an die WP)
            mit f = (T_oben - T_RL) / (T_oben - T_unten)  (≈ 53 %, SCH D3; DRL gemessen 52-63 %)
   Begründung: Nur der Anteil oberhalb des Rücklaufs kann ohne WP genutzt werden; der Rest
   (Rücklauf bis T_unten) ist nur als WP-Quelle nutzbar.
"""

from __future__ import annotations

from serts.config import Config
from serts.network import M2_JE_MW, mwh_je_m3


def _sel(var, name: str):
    """Eine Komponente auswählen und die Namens-Koordinate entfernen (linopy-v1-kompatibel)."""
    return var.sel(name=[name]).sum("name")


def direktanteil_max(cfg: Config) -> float:
    t_o, t_m, t_u = (cfg.get(k) for k in ("ptes.T_oben", "netz.T_RL", "ptes.T_unten"))
    return (t_o - t_m) / (t_o - t_u)


def extra_functionality(n, snapshots, *, cfg: Config) -> None:
    m = n.model
    hat_speicher = "ptes" in n.stores.index

    # 1 Fläche
    a_var = bool(n.generators.at["kollektor", "p_nom_extendable"])
    v_var = hat_speicher and bool(n.stores.at["ptes", "e_nom_extendable"])
    if a_var or v_var:
        kap = mwh_je_m3(cfg)
        a = (
            _sel(m["Generator-p_nom"], "kollektor")
            if a_var
            else n.generators.at["kollektor", "p_nom"]
        )
        lhs = a * M2_JE_MW * cfg.get("kollektor.flaechenfaktor")
        if hat_speicher:
            e = _sel(m["Store-e_nom"], "ptes") if v_var else n.stores.at["ptes", "e_nom"]
            lhs = lhs + e / kap / cfg.get("ptes.volumen_je_grundflaeche")
        m.add_constraints(lhs <= cfg.get("standort.flaeche_verfuegbar"), name="flaeche")

    # 2 Direktanteil der Speicherentladung
    if hat_speicher:
        p = m["Link-p"]
        f = direktanteil_max(cfg)
        cop = cfg.get("waermepumpe.COP_ptes")
        direkt = _sel(p, "entladen_direkt").sum()
        quelle = (cop - 1.0) * _sel(p, "hp_speicher").sum()
        m.add_constraints((1 - f) * direkt - f * quelle <= 0, name="speicher_direktanteil")
