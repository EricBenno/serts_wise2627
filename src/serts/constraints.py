"""Sechs Zusatzbedingungen (linopy) – alles andere erledigt PyPSA selbst.

f = Anteil des heißen Teils (T_oben - T_RL) / (T_oben - T_unten) ≈ 53 %, s = Anteil der Übergangszone am
heißen Teil (network.anteil_uebergang), Kern = heißer Teil ohne Übergangszone.

1. Fläche:   A_Koll * flaechenfaktor + V / volumen_je_grundflaeche <= flaeche_verfuegbar
             (V = E_Kern / (f * (1 - s) * kap); nur wenn A oder V optimiert wird, sonst Check in kpi.py;
             flaeche_verfuegbar = .inf schaltet die Bedingung ab)
2. Speichergröße: die drei Teile gehören zu demselben Wasser und wachsen im festen Verhältnis
             E_Übergang = s / (1 - s) * E_Kern,  E_kalt = (1 - f) / (f * (1 - s)) * E_Kern
             (nur wenn das Volumen optimiert wird)
3. WP bei Kälte: COP_luft(t) * p_hp_luft(t) <= p_max_pu_luft(t) * P_WP_luft
             (thermische Leistung der Luft-WP sinkt bei Kälte; Speicher-WP nicht betroffen)
4. Schichtung, in jeder Stunde (Füllstand = Inhalt / Kapazität des Teils):
             Füllstand Kern <= Füllstand Übergangszone <= Füllstand kalt
             Heißes Wasser liegt immer auf seiner Übergangszone und enthält seinen 10-45-°C-Anteil. Direkt ins
             Netz geht nur der Kern; die Übergangszone wärmt vor oder wird über die WP genutzt. Das ersetzt die
             frühere Schwelle mit zwei Läufen (docs E34 -> E39).
5. Nachheizen (WP oder PtH in derselben Stunde):
             p_vorwaermen(t) / k + alpha(t) * p_entladen_direkt(t) <= p_wp_luft(t) + p_wp_speicher(t) + eta * p_pth(t)
             (k = network.vorwaerm_verhaeltnis: Mischwasser hebt den Rücklauf nur auf ≈ 60 °C;
              alpha = network.boost_verhaeltnis: Kern kälter als Vorlauf + dT -> Boosting, Basis 0; docs E41)
6. Durchfluss (Diffusoren, je Richtung und Stunde): sum(Wärme_i / (c * Spreizung_i)) <= austauschrate * V
             (Spreizung: heiß 45->85 = 40 K, kalt 10->45 = 35 K, Vorwärmen 20 K, WP-Quelle 6 K je Durchgang;
              Rate aus Dronninglund 2014; .inf = aus)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from serts import heatpump
from serts.config import Config
from serts.network import (
    M2_JE_MW,
    anteil_heiss,
    boost_verhaeltnis,
    mwh_je_m3,
    vorwaerm_verhaeltnis,
)


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
    if (a_var or v_var) and np.isfinite(cfg.get("standort.flaeche_verfuegbar")):
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
    wp_variabel = bool(n.links.at["wp_luft_out", "p_nom_extendable"])
    p_wp = (
        _sel(m["Link-p_nom"], "wp_luft_out") if wp_variabel else n.links.at["wp_luft_out", "p_nom"]
    )
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

    # 5 Nachheizen: Vorwärmen und Direktentladung unter Vorlauftemperatur (Boosting) brauchen WP/PtH
    p = m["Link-p"]
    boost = boost_verhaeltnis(cfg, ts["T_a"]) if hat_speicher else None
    mit_boost = boost is not None and float(boost.max()) > 0
    if "vorwaermen" in n.links.index or mit_boost:
        bedarf = 0
        if "vorwaermen" in n.links.index:
            bedarf = _sel(p, "vorwaermen") * (1.0 / vorwaerm_verhaeltnis(cfg))
        if mit_boost:
            bedarf = bedarf + _zeitreihe(boost, ts.index) * _sel(p, "entladen_direkt")
        wp = [x for x in ("wp_luft_out", "wp_speicher_out") if x in n.links.index]
        nachheizen = sum(_sel(p, x) for x in wp) + cfg.get("pth.eta") * _sel(p, "pth")
        m.add_constraints(bedarf - nachheizen <= 0, name="nachheizen")

    # 6 Volumenstrom durch die Diffusoren (je Richtung): sum(Wärme / (c * Spreizung)) <= Rate * V
    rate = cfg.get("ptes.austauschrate")
    if hat_speicher and np.isfinite(rate):
        c = cfg.get("ptes.c_wasser")
        t_o, t_r, t_u = (cfg.get(k) for k in ("ptes.T_oben", "netz.T_RL", "ptes.T_unten"))
        e_kern = (
            _sel(m["Store-e_nom"], "ptes_heiss") if v_var else n.stores.at["ptes_heiss", "e_nom"]
        )
        grenze = rate * e_kern / (mwh_je_m3(cfg) * f * (1.0 - s))  # m3/h
        heiss, kalt, zone = c * (t_o - t_r), c * (t_r - t_u), c * (t_o - t_r) / 2.0

        def strom(teile):
            return sum(_sel(p, x) * (1.0 / dt) for x, dt in teile if x in n.links.index)

        m.add_constraints(
            strom([("laden_heiss", heiss), ("laden_netz", heiss), ("laden_kalt", kalt)]) - grenze
            <= 0,
            name="durchfluss_laden",
        )
        # Speicher-WP: Quellwärme (COP - 1) * Strom, Wasser kühlt je Durchgang um quell_abkuehlung (6 K)
        quelle = 0
        if "hp_speicher" in n.links.index:
            cop = heatpump.cop_speicher(cfg, ts["T_a"])
            dt_q = c * cfg.get("waermepumpe.quell_abkuehlung")
            quelle = _zeitreihe(cop - 1.0, ts.index) * _sel(p, "hp_speicher") * (1.0 / dt_q)
        m.add_constraints(
            strom([("entladen_direkt", heiss), ("vorwaermen", zone)]) + quelle - grenze <= 0,
            name="durchfluss_entladen",
        )
