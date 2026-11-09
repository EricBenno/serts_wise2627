"""Kennzahlen aus einem gelösten Netz.

Speicherdefinitionen wie Solites 2019 (BRF §6):
    eta     = (Q_out + dQ) / Q_in,   Verlust = Q_in - Q_out - dQ,   Zyklen = Q_out / Kapazität
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from serts.config import Config


@dataclass(frozen=True)
class Speicherbilanz:
    q_in: float  # MWh Beladung
    q_out: float  # MWh Entladung (direkt + WP-Quellwärme)
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


def solaranteil(direkt: float, ptes_direkt: float, wp_quelle_ptes: float, bedarf: float) -> dict:
    """Solaranteil getrennt (AP 0 Mittel). WP-Strom zählt NICHT als Solar (SCH D5)."""
    return {
        "solar_direkt": direkt / bedarf,
        "solar_ptes_direkt": ptes_direkt / bedarf,
        "solar_wp_quelle": wp_quelle_ptes / bedarf,
        "solar_gesamt": (direkt + ptes_direkt + wp_quelle_ptes) / bedarf,
    }


def zeitreihen_ergebnis(n, cfg: Config, ts: pd.DataFrame) -> pd.DataFrame:
    """Stündliche Wärme-/Stromflüsse [MW] und Speicherinhalt [MWh]."""
    g, p0 = n.generators_t.p, n.links_t.p0
    leer = pd.Series(0.0, index=n.snapshots)
    cop_s = cfg.get("waermepumpe.COP_ptes")
    r = pd.DataFrame(index=n.snapshots)
    r["last"] = ts["last_gesamt"]
    r["kollektor"] = g["kollektor"]
    r["solar_direkt"] = p0["solar_direkt"]
    r["laden"] = p0.get("laden", leer)
    r["entladen_direkt"] = p0.get("entladen_direkt", leer)
    r["wp_strom_luft"] = p0["hp_luft"]
    r["wp_waerme_luft"] = p0["hp_luft"] * ts["COP_luft"]
    r["wp_strom_speicher"] = p0.get("hp_speicher", leer)
    r["wp_waerme_speicher"] = r["wp_strom_speicher"] * cop_s
    r["wp_quelle_speicher"] = r["wp_strom_speicher"] * (cop_s - 1.0)
    r["pth_waerme"] = p0["pth"] * cfg.get("pth.eta")
    r["strom_netz"] = g["netz_strom"]
    r["speicherinhalt"] = n.stores_t.e["ptes"] if "ptes" in n.stores.index else leer
    r["abregelung"] = (
        n.generators.at["kollektor", "p_nom_opt"] * ts["P_solar"].clip(0, 1) - r["kollektor"]
    ).clip(lower=0)
    return r


def auswerten(n, cfg: Config, ts: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """KPI (Jahreswerte; kürzere Läufe werden auf 8760 h hochskaliert) + Zeitreihen."""
    from serts import economics
    from serts.network import M2_JE_MW, annualisiert, mwh_je_m3

    r = zeitreihen_ergebnis(n, cfg, ts)
    skal = 8760.0 / len(n.snapshots)
    S = {k: float(v) * skal for k, v in r.drop(columns="speicherinhalt").sum().items()}
    Q = S["last"]

    # Größen
    A = float(n.generators.at["kollektor", "p_nom_opt"]) * M2_JE_MW
    E = float(n.stores.at["ptes", "e_nom_opt"]) if "ptes" in n.stores.index else 0.0
    V = E / mwh_je_m3(cfg)
    speicher_preis = float((getattr(n, "meta", {}) or {}).get("speicher_preis", 0.0))
    k: dict = {
        "A_koll_m2": A,
        "V_m3": V,
        "E_speicher_MWh": E,
        "speicher_preis_EUR_m3": speicher_preis,
        "P_WP_MW": float(n.links.at["wp_out", "p_nom_opt"]),
        "P_PtH_MW": float(n.links.at["pth", "p_nom_opt"]) * cfg.get("pth.eta"),
        "stunden": len(n.snapshots),
    }
    k.update(
        {
            f"Q_{x}_MWh": S[x]
            for x in (
                "last",
                "kollektor",
                "solar_direkt",
                "laden",
                "entladen_direkt",
                "wp_quelle_speicher",
                "wp_waerme_luft",
                "wp_waerme_speicher",
                "pth_waerme",
                "abregelung",
            )
        }
    )
    k["E_strom_MWh"] = S["strom_netz"]
    k["solarertrag_spez_kWh_m2"] = S["kollektor"] / A * 1e3 if A > 0 else 0.0
    wp_strom = S["wp_strom_luft"] + S["wp_strom_speicher"]
    k["jaz_wp"] = (
        (S["wp_waerme_luft"] + S["wp_waerme_speicher"]) / wp_strom if wp_strom else float("nan")
    )

    # Speicher
    if E > 0 and S["laden"] > 0:
        dq = float(r["speicherinhalt"].iloc[-1] - r["speicherinhalt"].iloc[0])
        sb = Speicherbilanz(S["laden"], S["entladen_direkt"] + S["wp_quelle_speicher"], dq)
        k.update(
            {
                "speicher_wirkungsgrad": sb.wirkungsgrad,
                "speicher_verluste_MWh": sb.verluste,
                "speicher_zyklen": sb.q_out / E,
                "speicher_direktanteil": (
                    S["entladen_direkt"] / sb.q_out if sb.q_out > 1e-3 else float("nan")
                ),
            }
        )

    # Anteile
    k.update(solaranteil(S["solar_direkt"], S["entladen_direkt"], S["wp_quelle_speicher"], Q))
    k["ee_anteil"] = 1.0 - S["strom_netz"] * (1.0 - cfg.get("strom.ee_anteil")) / Q

    # Kosten (Jahreswerte, real)
    capex = {
        "kollektor": A * annualisiert(cfg, "kollektor", "kollektor.kosten_spez"),
        "speicher": V * annualisiert(cfg, "ptes", speicher_preis) if V > 0 else 0.0,
        "waermepumpe": k["P_WP_MW"] * annualisiert(cfg, "waermepumpe", "waermepumpe.kosten_spez"),
        "pth": k["P_PtH_MW"] * annualisiert(cfg, "pth", "pth.kosten_spez"),
    }
    mc = n.get_switchable_as_dense("Generator", "marginal_cost")["netz_strom"]
    strom = float((r["strom_netz"] * mc).sum()) * skal
    k.update({f"kosten_a_{x}": v for x, v in capex.items()})
    k["kosten_a_strom"] = strom
    k["kosten_a_gesamt"] = sum(capex.values()) + strom
    k["invest_EUR"] = (
        A * cfg.get("kollektor.kosten_spez")
        + V * speicher_preis
        + k["P_WP_MW"] * cfg.get("waermepumpe.kosten_spez")
        + k["P_PtH_MW"] * cfg.get("pth.kosten_spez")
    )
    k["lcoh"] = economics.lcoh(sum(capex.values()), strom, Q)
    Q_geliefert = Q - float(ts["last_netzverlust"].sum()) * skal if "last_netzverlust" in ts else Q
    k["lcoh_geliefert"] = economics.lcoh(sum(capex.values()), strom, Q_geliefert)
    k["co2_t_a"] = S["strom_netz"] * cfg.get("strom.emissionsfaktor")

    ref = economics.gas_referenz(cfg, Q, float(ts["last_gesamt"].max()))
    k.update(ref)
    k["co2_vermeidungskosten"] = economics.co2_vermeidungskosten(
        k["lcoh"], ref["gas_lcoh"], k["co2_t_a"] / Q, ref["gas_co2_t_a"] / Q
    )

    # Fläche (Check)
    flaeche = A * cfg.get("kollektor.flaechenfaktor") + V / cfg.get("ptes.volumen_je_grundflaeche")
    k["flaeche_m2"] = flaeche
    k["flaeche_ok"] = bool(flaeche <= cfg.get("standort.flaeche_verfuegbar") * (1 + 1e-6))
    return k, r
