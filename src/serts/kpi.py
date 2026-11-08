"""Kennzahlen (Outputs C im Schema) und Regel-Checks (BRF §7).

Speicherdefinitionen wie Solites 2019 (BRF §6):
    eta     = (Q_out + dQ) / Q_in
    Verlust = Q_in - Q_out - dQ
    Zyklen  = Q_out / Kapazität,  Kapazität = V * c * (T_max - T_min)
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from serts.config import Config


@dataclass(frozen=True)
class Speicherbilanz:
    q_in: float  # MWh Beladung
    q_out: float  # MWh Entladung (inkl. WP-Quellwärme)
    dq: float  # MWh Inhaltsänderung Ende - Anfang (zyklisch: 0)

    @property
    def verluste(self) -> float:
        return self.q_in - self.q_out - self.dq

    @property
    def wirkungsgrad(self) -> float:
        return (self.q_out + self.dq) / self.q_in

    @property
    def verlustanteil(self) -> float:
        return self.verluste / self.q_in


def kapazitaet_MWh(volumen_m3: float, c: float, t_max: float, t_min: float) -> float:
    return volumen_m3 * c * (t_max - t_min)


def zyklen(q_out: float, kapazitaet: float) -> float:
    return q_out / kapazitaet


def solaranteil(direkt: float, ptes_direkt: float, wp_quelle_ptes: float, bedarf: float) -> dict:
    """Solaranteil getrennt (AP 0 Mittel). WP-Strom zählt NICHT als Solar (SCH D5)."""
    return {
        "solar_direkt": direkt / bedarf,
        "solar_ptes_direkt": ptes_direkt / bedarf,
        "solar_wp_quelle": wp_quelle_ptes / bedarf,
        "solar_gesamt": (direkt + ptes_direkt + wp_quelle_ptes) / bedarf,
    }


# ---------------------------------------------------------------------------------------
# Auswertung eines gelösten Netzes
# ---------------------------------------------------------------------------------------


def _link_waerme(n, name: str, eff_attr: str = "efficiency2") -> pd.Series:
    """Wärmestrom eines Links an bus1/bus2 [MW] = p0 * |efficiency|."""
    if name not in n.links.index:
        return pd.Series(0.0, index=n.snapshots)
    eff = n.links.at[name, eff_attr]
    return n.links_t.p0[name] * abs(eff)


def zeitreihen_ergebnis(n, cfg: Config, ts: pd.DataFrame) -> pd.DataFrame:
    """Stündliche Ergebnisgrößen [MW bzw. m3] für Bilanzen und Plots."""
    c = cfg.get("ptes.c_wasser")
    t_hi, t_mid, t_lo = (cfg.get(f"ptes.T_{k}") for k in ("oben", "mitte", "unten"))
    g = n.generators_t.p
    p0 = n.links_t.p0
    A = n.meta["A_koll_m2"] * 1e-3
    r = pd.DataFrame(index=n.snapshots)
    r["last"] = (
        n.loads_t.p_set["last"] if "last" in n.loads_t.p_set else n.loads.at["last", "p_set"]
    )
    r["sol_hi"] = g["sol_hi"]
    r["sol_lo"] = g["sol_lo"] if "sol_lo" in g else 0.0
    r["solar_direkt"] = p0["solar_direkt"]
    r["laden"] = sum(_link_waerme(n, k) for k in ("laden_hi_aus45", "laden_hi_aus10", "laden_lo"))
    r["entladen_direkt"] = _link_waerme(n, "entladen_direkt")
    r["wp_quelle_ptes"] = _link_waerme(n, "wp_quelle_ptes")
    r["speicherverlust"] = (
        (p0["verlust_oben"] * (t_hi - t_mid) * c + p0["verlust_mitte"] * (t_mid - t_lo) * c)
        if "verlust_oben" in p0
        else 0.0
    )
    r["wp_strom_luft"] = p0["hp_air"]
    r["wp_waerme_luft"] = p0["hp_air"] * ts["COP_luft"]
    r["wp_strom_ptes"] = p0["hp_ptes"] if "hp_ptes" in p0 else 0.0
    r["wp_waerme_ptes"] = r["wp_strom_ptes"] * cfg.get("waermepumpe.COP_ptes")
    r["pth_strom"] = p0["pth"]
    r["pth_waerme"] = p0["pth"] * cfg.get("pth.eta")
    r["strom_netz"] = g["netz_strom"]
    r["transmission"] = p0["transmission"]
    if "V85" in n.stores.index:
        e = n.stores_t.e
        r["V85"], r["V45"], r["V10"] = e["V85"], e["V45"], e["V10"]
        r["speicherinhalt"] = e["V85"] * (t_hi - t_lo) * c + e["V45"] * (t_mid - t_lo) * c
    # ungenutzte Kollektorfläche (Abregelung), bewertet auf Hochtemperatur-Niveau
    P_hi, P_lo = ts["P_hi"].clip(0, 1), ts["P_lo"].clip(0, 1)
    genutzt = (
        (r["sol_hi"] / (A * P_hi)).where(P_hi > 0, 0.0)
        + (r["sol_lo"] / (A * P_lo)).where(P_lo > 0, 0.0)
        if A > 0
        else 0.0
    )
    r["abregelung"] = ((1.0 - genutzt).clip(lower=0) * A * P_hi) if A > 0 else 0.0
    return r


def auswerten(n, cfg: Config, ts: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """KPI-Dictionary (Jahreswerte, bei kürzeren Läufen hochskaliert) + Ergebnis-Zeitreihen."""
    from serts import economics, flaeche

    r = zeitreihen_ergebnis(n, cfg, ts)
    A_m2, V = n.meta["A_koll_m2"], n.meta["V_m3"]
    skal = 8760.0 / len(n.snapshots)
    S = {k: float(v) * skal for k, v in r.sum().items()}
    Q = S["last"]
    k: dict = {"A_koll_m2": A_m2, "V_m3": V, "stunden": len(n.snapshots), "skalierung": skal}

    # --- Energiebilanzen -----------------------------------------------------------
    k.update(
        {
            f"Q_{x}_MWh": S[x]
            for x in (
                "last",
                "sol_hi",
                "sol_lo",
                "solar_direkt",
                "laden",
                "entladen_direkt",
                "wp_quelle_ptes",
                "speicherverlust",
                "wp_waerme_luft",
                "wp_waerme_ptes",
                "pth_waerme",
                "abregelung",
            )
        }
    )
    k["E_strom_MWh"] = S["strom_netz"]
    k["E_wp_MWh"] = S["wp_strom_luft"] + S["wp_strom_ptes"]
    k["solarertrag_spez_kWh_m2"] = (S["sol_hi"] + S["sol_lo"]) / A_m2 * 1e3 if A_m2 else 0.0

    # Speicher (Solites-Definitionen)
    if V > 0:
        dq = float(r["speicherinhalt"].iloc[-1] - r["speicherinhalt"].iloc[0])
        sb = Speicherbilanz(
            q_in=S["laden"], q_out=S["entladen_direkt"] + S["wp_quelle_ptes"], dq=dq
        )
        kap = kapazitaet_MWh(
            V, cfg.get("ptes.c_wasser"), cfg.get("ptes.T_oben"), cfg.get("ptes.T_unten")
        )
        k.update(
            {
                "speicher_wirkungsgrad": sb.wirkungsgrad if sb.q_in > 0 else float("nan"),
                "speicher_verlustanteil": sb.verlustanteil if sb.q_in > 0 else float("nan"),
                "speicher_bilanzfehler_MWh": sb.verluste - S["speicherverlust"],
                "speicher_kapazitaet_MWh": kap,
                "speicher_zyklen": zyklen(sb.q_out, kap),
                "volumensumme_maxfehler_m3": float(
                    (r[["V85", "V45", "V10"]].sum(axis=1) - V).abs().max()
                ),
            }
        )

    # Solaranteil getrennt (WP-Strom zählt nicht als Solar)
    k.update(solaranteil(S["solar_direkt"], S["entladen_direkt"], S["wp_quelle_ptes"], Q))
    # EE-Anteil: 1 - nicht-erneuerbarer Strom / Wärme (1 MWh Strom ≈ 1 MWh Wärme, docs E14)
    k["ee_anteil"] = 1.0 - k["E_strom_MWh"] * (1.0 - cfg.get("strom.ee_anteil")) / Q
    k["jaz_wp"] = (
        (S["wp_waerme_luft"] + S["wp_waerme_ptes"]) / k["E_wp_MWh"]
        if k["E_wp_MWh"]
        else float("nan")
    )

    # Leistungen und Caps
    k["P_WP_MW"] = float(n.links.at["hp_out", "p_nom_opt"])
    k["P_PtH_MW"] = float(n.links.at["pth", "p_nom_opt"])
    k["h_transmission_am_cap"] = int(
        (r["transmission"] >= 0.999 * n.links.at["transmission", "p_nom"]).sum()
    )
    k["h_wp_am_cap"] = (
        int((n.links_t.p0["hp_out"] >= 0.999 * k["P_WP_MW"] - 1e-6).sum())
        if k["P_WP_MW"] > 1e-6
        else 0
    )
    k["h_abregelung"] = int((r["abregelung"] > 1e-4).sum())
    # Regel-Check BRF §7: Luft-WP läuft, obwohl PTES-Mittelpool Volumen hat und Luft < 25 degC
    if V > 0:
        k["h_luft_trotz_ptes"] = int(
            ((r["wp_strom_luft"] > 1e-4) & (r["V45"] > 0.01 * V) & (ts["T_a"] < 25)).sum()
        )

    # --- Kosten -------------------------------------------------------------------
    zins = cfg.get("oekonomie.zins")
    from serts.network import annualisiert

    capex = {
        "kollektor": A_m2 * annualisiert(cfg, "kollektor", "kollektor.kosten_spez"),
        "ptes": economics.kapitalkosten_jahr(
            economics.ptes_invest(cfg, V),
            zins,
            cfg.get("oekonomie.lebensdauer.ptes"),
            cfg.get("oekonomie.om_fix.ptes"),
            cfg.get("oekonomie.foerderquote"),
        ),
        "waermepumpe": k["P_WP_MW"] * annualisiert(cfg, "waermepumpe", "waermepumpe.kosten_spez"),
        "pth": k["P_PtH_MW"] * annualisiert(cfg, "pth", "pth.kosten_spez"),
    }
    mc = n.get_switchable_as_dense("Generator", "marginal_cost")["netz_strom"]
    strom_kosten = float((r["strom_netz"] * mc).sum()) * skal  # enthält Preisdynamik-Faktor
    k.update({f"capex_a_{x}": v for x, v in capex.items()})
    k["invest_ptes_EUR"] = economics.ptes_invest(cfg, V)
    k["invest_kollektor_EUR"] = A_m2 * cfg.get("kollektor.kosten_spez")
    k["stromkosten_a"] = strom_kosten
    k["kosten_a_gesamt"] = sum(capex.values()) + strom_kosten
    # LCOH bezogen auf Netzeinspeisung (Systemgrenze Erzeugung) und auf gelieferte Wärme
    k["lcoh"] = economics.lcoh(sum(capex.values()), strom_kosten, Q)
    Q_geliefert = Q - _netzverlust(ts) * skal
    k["lcoh_geliefert"] = economics.lcoh(sum(capex.values()), strom_kosten, Q_geliefert)
    k["co2_t_a"] = k["E_strom_MWh"] * cfg.get("strom.emissionsfaktor")

    ref = economics.gas_referenz(cfg, Q, float(ts["last_gesamt"].max()))
    k.update(ref)
    k["co2_vermeidungskosten"] = economics.co2_vermeidungskosten(
        k["lcoh"], ref["gas_lcoh"], k["co2_t_a"] / Q, ref["gas_co2_t_a"] / Q
    )
    k.update(flaeche.flaechenbedarf(cfg, A_m2, V))
    return k, r


def _netzverlust(ts: pd.DataFrame) -> float:
    return float(ts["last_netzverlust"].sum()) if "last_netzverlust" in ts else 0.0
