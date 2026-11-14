"""Fünf Zusatzbedingungen (linopy) – alles andere erledigt PyPSA selbst.

f = Anteil des heißen Teils (T_oben - T_RL) / (T_oben - T_unten) ≈ 53 %, s = Anteil der Übergangszone am
heißen Teil (network.anteil_uebergang), Kern = heißer Teil ohne Übergangszone.

1. Fläche:   A_Koll * flaechenfaktor + V / volumen_je_grundflaeche <= flaeche_verfuegbar
             (V = E_Kern / (f * (1 - s) * kap); nur wenn A oder V optimiert wird, sonst Check in kpi.py)
2. Speichergröße: die drei Teile gehören zu demselben Wasser und wachsen im festen Verhältnis
             E_Übergang = s / (1 - s) * E_Kern,  E_kalt = (1 - f) / (f * (1 - s)) * E_Kern
             (nur wenn das Volumen optimiert wird)
3. WP bei Kälte: COP_luft(t) * p_hp_luft(t) <= p_max_pu_luft(t) * P_WP
             (thermische Leistung der Luft-WP sinkt bei Kälte; Speicher-WP nicht betroffen)
4. Schichtung, in jeder Stunde (Füllstand = Inhalt / Kapazität des Teils):
             Füllstand Kern <= Füllstand Übergangszone <= Füllstand kalt
             Heißes Wasser liegt immer auf seiner Übergangszone und enthält seinen 10-45-°C-Anteil. Direkt ins
             Netz geht nur der Kern; die Übergangszone wärmt vor oder wird über die WP genutzt. Das ersetzt die
             frühere Schwelle mit zwei Läufen (docs E34 -> E39).
5. Vorwärmen braucht Nachheizen: p_vorwaermen(t) <= k * (p_wp_out(t) + eta * p_pth(t))
             (k = network.vorwaerm_verhaeltnis: Mischwasser hebt den Rücklauf nur auf ≈ 60 °C)
"""

from __future__ import annotations

import pandas as pd

from serts.config import Config
from serts.network import M2_JE_MW, anteil_heiss, mwh_je_m3, vorwaerm_verhaeltnis


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
    hat_ueb = "ptes_ueb" in n.stores.index
    f = anteil_heiss(cfg)
    s = float((getattr(n, "meta", {}) or {}).get("uebergang_anteil", 0.0)) if hat_ueb else 0.0

    # 1 Fläche
    a_var = bool(n.generators.at["kollektor", "p_nom_extendable"])
    v_var = hat_speicher and bool(n.stores.at["ptes_heiss", "e_nom_extendable"])
    if a_var or v_var:
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
            volumen = e / (mwh_je_m3(cfg) * f * (1.0 - s))
            lhs = lhs + volumen / cfg.get("ptes.volumen_je_grundflaeche")
        m.add_constraints(lhs <= cfg.get("standort.flaeche_verfuegbar"), name="flaeche")

    # 2 feste Aufteilung der Speichergröße
    if v_var:
        e_h = _sel(m["Store-e_nom"], "ptes_heiss")
        e_k = _sel(m["Store-e_nom"], "ptes_kalt")
        m.add_constraints(e_k - (1.0 - f) / (f * (1.0 - s)) * e_h == 0, name="speicher_verhaeltnis")
        if hat_ueb:
            e_u = _sel(m["Store-e_nom"], "ptes_ueb")
            m.add_constraints(e_u - s / (1.0 - s) * e_h == 0, name="speicher_verhaeltnis_ueb")

    # 3 Luft-WP: Leistung sinkt bei Kälte
    wp_variabel = bool(n.links.at["wp_out", "p_nom_extendable"])
    p_wp = _sel(m["Link-p_nom"], "wp_out") if wp_variabel else n.links.at["wp_out", "p_nom"]
    cop = _zeitreihe(ts["COP_luft"], ts.index)
    pu = _zeitreihe(ts["p_max_pu_luft"], ts.index)
    m.add_constraints(cop * _sel(m["Link-p"], "hp_luft") - pu * p_wp <= 0, name="wp_luft_leistung")

    # 4 Schichtung: Kern <= Übergangszone <= kalt (relative Füllstände; Kapazitäten im festen Verhältnis)
    if hat_speicher:
        e_h = _sel(m["Store-e"], "ptes_heiss")
        e_k = _sel(m["Store-e"], "ptes_kalt")
        if hat_ueb:
            e_u = _sel(m["Store-e"], "ptes_ueb")
            m.add_constraints(e_u - s / (1.0 - s) * e_h >= 0, name="schichtung_kern")
            m.add_constraints(e_k - (1.0 - f) / (f * s) * e_u >= 0, name="schichtung_kalt")
        else:
            m.add_constraints(e_k - (1.0 - f) / f * e_h >= 0, name="schichtung_kalt")

    # 5 Vorwärmen nur zusammen mit Nachheizen (WP oder PtH)
    if "vorwaermen" in n.links.index:
        p = m["Link-p"]
        nachheizen = _sel(p, "wp_out") + cfg.get("pth.eta") * _sel(p, "pth")
        m.add_constraints(
            _sel(p, "vorwaermen") - vorwaerm_verhaeltnis(cfg) * nachheizen <= 0, name="nachheizen"
        )
