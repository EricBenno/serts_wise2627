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
    q_out: float  # MWh Entladung (direkt + Vorwärmen + WP-Quellwärme)
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
    from serts.heatpump import cop_speicher

    cop_s = cop_speicher(cfg, ts["T_a"]).reindex(n.snapshots)
    r = pd.DataFrame(index=n.snapshots)
    r["last"] = ts["last_gesamt"]
    r["T_a"] = ts["T_a"]  # nur für Plots
    r["P_solar_spez"] = ts["P_solar"]  # kW/m2, nur für Plots
    r["kollektor"] = g["kollektor"]
    r["solar_direkt"] = p0["solar_direkt"]
    r["laden"] = p0.get("laden_heiss", leer) + p0.get(
        "laden_kalt", leer
    )  # Solarwärme in den Speicher
    r["laden_netz"] = p0.get(
        "laden_netz", leer
    )  # WP/PtH-Wärme in den Speicher (nur ptes.laden_aus_netz)
    r["entladen_direkt"] = p0.get("entladen_direkt", leer)
    r["vorwaermen"] = p0.get("vorwaermen", leer)  # Übergangszone wärmt den Rücklauf vor
    r["wp_strom_luft"] = p0["hp_luft"]
    r["wp_waerme_luft"] = p0["hp_luft"] * ts["COP_luft"]
    r["wp_strom_speicher"] = p0.get("hp_speicher", leer)
    r["wp_waerme_speicher"] = r["wp_strom_speicher"] * cop_s
    r["wp_quelle_speicher"] = r["wp_strom_speicher"] * (cop_s - 1.0)
    r["pth_waerme"] = p0["pth"] * cfg.get("pth.eta")
    r["strom_netz"] = g["netz_strom"]
    if "ptes_heiss" in n.stores.index:
        e, nom = n.stores_t.e, n.stores.e_nom_opt
        ueb = e["ptes_ueb"] if "ptes_ueb" in e else leer
        r["speicher_kern"], r["speicher_uebergang"] = e["ptes_heiss"], ueb
        r["speicher_heiss"], r["speicher_kalt"] = e["ptes_heiss"] + ueb, e["ptes_kalt"]
        r["speicherinhalt"] = r["speicher_heiss"] + r["speicher_kalt"]
        if float(nom["ptes_heiss"]) > 1e-6:
            from serts.network import temperaturen_speicher

            s_ueb = (
                (getattr(n, "meta", {}) or {}).get("uebergang_anteil", 0.0)
                if "ptes_ueb" in e
                else 0.0
            )
            fuell_ueb = (ueb / float(nom["ptes_ueb"])).clip(0, 1) if s_ueb > 0 else leer + 1.0
            r["T_speicher_oben"], r["T_speicher_mittel"] = temperaturen_speicher(
                cfg,
                (e["ptes_heiss"] / float(nom["ptes_heiss"])).clip(0, 1),
                fuell_ueb,
                (e["ptes_kalt"] / float(nom["ptes_kalt"])).clip(0, 1),
                s_ueb,
            )
    else:
        for c in (
            "speicher_kern",
            "speicher_uebergang",
            "speicher_heiss",
            "speicher_kalt",
            "speicherinhalt",
        ):
            r[c] = leer
    r["abregelung"] = (
        n.generators.at["kollektor", "p_nom_opt"] * ts["P_solar"].clip(0, 1) - r["kollektor"]
    ).clip(lower=0)
    # Lösungsrauschen des Innere-Punkte-Verfahrens (|x| < 1e-6 MW) auf 0 setzen
    fluss = r.columns.difference(["T_a", "P_solar_spez", "T_speicher_oben", "T_speicher_mittel"])
    r[fluss] = r[fluss].where(r[fluss].abs() > 1e-6, 0.0)
    r.attrs["T_direkt_noetig"] = cfg.get("netz.T_VL") + cfg.get("ptes.direkt_dT")
    return r


def auswerten(n, cfg: Config, ts: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """KPI (Jahreswerte; kürzere Läufe werden auf 8760 h hochskaliert) + Zeitreihen."""
    from serts import economics, prices
    from serts.network import M2_JE_MW, annualisiert, anteil_heiss, mwh_je_m3

    meta = getattr(n, "meta", {}) or {}
    s_ueb = float(meta.get("uebergang_anteil", 0.0)) if "ptes_ueb" in n.stores.index else 0.0

    r = zeitreihen_ergebnis(n, cfg, ts)
    skal = 8760.0 / len(n.snapshots)
    S = {
        k: float(v) * skal
        for k, v in r.drop(
            columns=["speicherinhalt", "T_speicher_oben", "T_speicher_mittel"], errors="ignore"
        )
        .sum()
        .items()
    }
    Q = S["last"]

    # Größen
    A = float(n.generators.at["kollektor", "p_nom_opt"]) * M2_JE_MW
    # Speicher-Energie gesamt = Kern / (Anteil heiß * (1 - Anteil Übergangszone))
    E = (
        float(n.stores.at["ptes_heiss", "e_nom_opt"]) / (anteil_heiss(cfg) * (1.0 - s_ueb))
        if "ptes_heiss" in n.stores.index
        else 0.0
    )
    V = E / mwh_je_m3(cfg)
    invest_speicher = (
        float(meta.get("speicher_steigung", 0.0)) * V + float(meta.get("speicher_fix", 0.0))
        if V > 1e-6
        else 0.0
    )
    speicher_preis = invest_speicher / V if V > 1e-6 else 0.0
    k: dict = {
        "A_koll_m2": A,
        "V_m3": V,
        "E_speicher_MWh": E,
        "speicher_preis_EUR_m3": speicher_preis,
        "P_WP_luft_MW": float(n.links.at["wp_luft_out", "p_nom_opt"]),
        "P_WP_speicher_MW": (
            float(n.links.at["wp_speicher_out", "p_nom_opt"])
            if "wp_speicher_out" in n.links.index
            else 0.0
        ),
        "P_PtH_MW": float(n.links.at["pth", "p_nom_opt"]) * cfg.get("pth.eta"),
        "stunden": len(n.snapshots),
        "anteil_heiss": anteil_heiss(cfg),
        "uebergang_anteil": s_ueb,
        "verlustrate_1_h": float(meta.get("verlustrate", 0.0)),
        "P_netzanschluss_MW": float(r["strom_netz"].max()),
    }
    k["P_WP_MW"] = k["P_WP_luft_MW"] + k["P_WP_speicher_MW"]  # thermisch, beide Maschinen
    wp_invest = k["P_WP_luft_MW"] * cfg.get("waermepumpe.kosten_spez") + k[
        "P_WP_speicher_MW"
    ] * cfg.get("waermepumpe.kosten_spez_speicher")

    def wp_jahr(c):
        return k["P_WP_luft_MW"] * annualisiert(c, "waermepumpe", "waermepumpe.kosten_spez") + k[
            "P_WP_speicher_MW"
        ] * annualisiert(c, "waermepumpe", "waermepumpe.kosten_spez_speicher")

    k.update(
        {
            f"Q_{x}_MWh": S[x]
            for x in (
                "last",
                "kollektor",
                "solar_direkt",
                "laden",
                "laden_netz",
                "entladen_direkt",
                "vorwaermen",
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
    k["cop_speicher_mittel"] = (
        S["wp_waerme_speicher"] / S["wp_strom_speicher"]
        if S["wp_strom_speicher"] > 1e-9
        else float("nan")
    )
    # Boosting: Nachheizwärme für Direktentladung unter Vorlauftemperatur (docs E41)
    from serts.network import boost_verhaeltnis

    k["Q_boost_MWh"] = (
        float((boost_verhaeltnis(cfg, ts["T_a"]).reindex(n.snapshots) * r["entladen_direkt"]).sum())
        * skal
    )

    # Speicher
    q_in = S["laden"] + S["laden_netz"]
    q_out = S["entladen_direkt"] + S["vorwaermen"] + S["wp_quelle_speicher"]
    if E > 0 and q_in > 0:
        dq = float(r["speicherinhalt"].iloc[-1] - r["speicherinhalt"].iloc[0])
        sb = Speicherbilanz(q_in, q_out, dq)
        # Anteil der Entladung, der mit voller Temperatur direkt ins Netz geht (Dronninglund 2015-2017:
        # 52-63 %; dort zählt alles andere als WP-Quellwärme) und Anteil ganz ohne Speicher-WP
        k["speicher_direktanteil"] = S["entladen_direkt"] / q_out if q_out else 0.0
        k["speicher_anteil_ohne_wp"] = (
            (S["entladen_direkt"] + S["vorwaermen"]) / q_out if q_out else 0.0
        )
        k.update(
            {
                "speicher_wirkungsgrad": sb.wirkungsgrad,
                "speicher_verluste_MWh": sb.verluste,
                "speicher_zyklen": sb.q_out / E,
            }
        )

    # Speichercharakter: saisonal = wenige Zyklen und Entladung überwiegend im Winter (Nov-Mär)
    if E > 0:
        aus = r["entladen_direkt"] + r["vorwaermen"] + r["wp_quelle_speicher"]
        winter = aus[aus.index.month.isin([11, 12, 1, 2, 3])].sum()
        k["speicher_winteranteil"] = float(winter / aus.sum()) if aus.sum() > 1e-6 else float("nan")
        z = k.get("speicher_zyklen", float("nan"))
        if z == z and k["speicher_winteranteil"] == k["speicher_winteranteil"]:
            k["speicher_charakter"] = (
                "saisonal"
                if z < 2 and k["speicher_winteranteil"] >= 0.6
                else "kurzzeit"
                if z >= 4
                else "gemischt"
            )

    # Anteile
    # Speicherwärme zählt als solar, soweit der Speicher mit Solarwärme geladen wurde
    solar_im_speicher = S["laden"] / q_in if q_in > 0 else 1.0
    k.update(
        solaranteil(
            S["solar_direkt"],
            (S["entladen_direkt"] + S["vorwaermen"]) * solar_im_speicher,
            S["wp_quelle_speicher"] * solar_im_speicher,
            Q,
        )
    )
    k["ee_anteil"] = 1.0 - S["strom_netz"] * (1.0 - cfg.get("strom.ee_anteil")) / Q

    # Kosten (Jahreswerte, real)
    capex = {
        "kollektor": A * annualisiert(cfg, "kollektor", "kollektor.kosten_spez"),
        "speicher": annualisiert(cfg, "ptes", invest_speicher) if V > 0 else 0.0,
        "waermepumpe": wp_jahr(cfg),
        "pth": k["P_PtH_MW"] * annualisiert(cfg, "pth", "pth.kosten_spez"),
    }
    mc = n.get_switchable_as_dense("Generator", "marginal_cost")["netz_strom"]
    strom = float((r["strom_netz"] * mc).sum()) * skal
    k.update({f"kosten_a_{x}": v for x, v in capex.items()})
    # Leistungspreis auf den höchsten Strombezug (im LP: Kosten der Anschlussleistung)
    leistung = k["P_netzanschluss_MW"] * 1000.0 * cfg.get("strom.leistungspreis")
    leistung *= economics.preisdynamik(
        cfg.get("oekonomie.zins"),
        cfg.get("oekonomie.betrachtungszeitraum"),
        cfg.get("oekonomie.preisaenderung.strom"),
    )
    k["kosten_a_strom_leistung"] = leistung
    strom_arbeit = strom
    strom = strom_arbeit + leistung  # Stromkosten gesamt
    k["kosten_a_strom"] = strom
    # Strompreis-Komponenten getrennt (Netzentgelt Arbeitspreis, Abgaben, Rest = Energie)
    netz_e, abgaben = prices.netz_und_abgaben(cfg)
    f_strom = economics.preisdynamik(
        cfg.get("oekonomie.zins"),
        cfg.get("oekonomie.betrachtungszeitraum"),
        cfg.get("oekonomie.preisaenderung.strom"),
    )
    k["kosten_a_strom_netzentgelt"] = S["strom_netz"] * netz_e * f_strom
    k["kosten_a_strom_abgaben"] = S["strom_netz"] * abgaben * f_strom
    k["kosten_a_strom_energie"] = (
        strom_arbeit - k["kosten_a_strom_netzentgelt"] - k["kosten_a_strom_abgaben"]
    )
    k["strompreis_mittel_EUR_MWh"] = float(mc.mean()) / f_strom  # Jahresmittel (ungewichtet)
    k["strompreis_gewichtet_EUR_MWh"] = (  # tatsächlich bezahlt: nach Strommenge gewichtet
        strom_arbeit / S["strom_netz"] / f_strom if S["strom_netz"] > 1e-9 else float("nan")
    )
    k["kosten_a_gesamt"] = sum(capex.values()) + strom
    k["invest_EUR"] = (1.0 + cfg.get("oekonomie.nebenkosten")) * (
        A * cfg.get("kollektor.kosten_spez")
        + invest_speicher
        + wp_invest
        + k["P_PtH_MW"] * cfg.get("pth.kosten_spez")
    )  # inkl. Nebenkosten, ohne Verteilnetz
    k["lcoh"] = economics.lcoh(sum(capex.values()), strom, Q)
    Q_geliefert = Q - float(ts["last_netzverlust"].sum()) * skal if "last_netzverlust" in ts else Q
    k["lcoh_geliefert"] = economics.lcoh(sum(capex.values()), strom, Q_geliefert)
    k["Q_geliefert_MWh"] = Q_geliefert
    k["co2_t_a"] = S["strom_netz"] * cfg.get("strom.emissionsfaktor")

    ref = economics.gas_referenz(cfg, Q, float(ts["last_gesamt"].max()))
    k.update(ref)
    k["co2_vermeidungskosten"] = economics.co2_vermeidungskosten(
        k["lcoh"], ref["gas_lcoh"], k["co2_t_a"] / Q, ref["gas_co2_t_a"] / Q
    )
    k["abstand_gas"] = ref["gas_lcoh"] - k["lcoh"]  # > 0: System günstiger als Gas-Referenz

    # Verteilnetz (gleich für System und Gas-Fernwärme) -> Wärmepreis beim Kunden
    nk_bew = None
    q_bew = cfg.get("oekonomie.bew_ausweis_quote")
    if q_bew > 0 and cfg.get("oekonomie.foerderquote") == 0:
        # Gleiche Auslegung, Kosten MIT BEW Modul 2 (nur förderfähige Teile, Obergrenze 40 %)
        cb = cfg.variante("oekonomie.foerderquote", q_bew)
        capex_b = {
            "kollektor": A * annualisiert(cb, "kollektor", "kollektor.kosten_spez"),
            "speicher": annualisiert(cb, "ptes", invest_speicher) if V > 0 else 0.0,
            "waermepumpe": wp_jahr(cb),
            "pth": k["P_PtH_MW"] * annualisiert(cb, "pth", "pth.kosten_spez"),
        }
        k["lcoh_bew"] = economics.lcoh(sum(capex_b.values()), strom, Q)
        k["kosten_a_gesamt_bew"] = sum(capex_b.values()) + strom
        foerderbar = {
            "kollektor": A * cfg.get("kollektor.kosten_spez"),
            "ptes": invest_speicher,
            "waermepumpe": wp_invest,
            "pth": k["P_PtH_MW"] * cfg.get("pth.kosten_spez"),
        }
        if cfg.get("netz.netzkosten_einbeziehen"):
            nk_bew = economics.netzkosten(cb)
            foerderbar["netz"] = nk_bew["netz_invest_trasse_EUR"]
            foerderbar["hausanschluss"] = nk_bew["netz_invest_hausanschluss_EUR"]
        k["zuschuss_bew_EUR"] = sum(
            v * (1.0 + cfg.get("oekonomie.nebenkosten")) * q_bew
            for kompo, v in foerderbar.items()
            if cfg.get(f"oekonomie.foerderfaehig.{kompo}")
        )
        k["bew_quote"] = q_bew
    if cfg.get("netz.netzkosten_einbeziehen"):
        nk = economics.netzkosten(cfg)
        k.update(nk)
        k["netzkosten_spez_trasse"] = nk["kosten_a_netz_trasse"] / Q_geliefert
        k["netzkosten_spez_hausanschluss"] = nk["kosten_a_netz_hausanschluss"] / Q_geliefert
        k["netzkosten_spez"] = nk["kosten_a_netz_system"] / Q_geliefert  # EUR/MWh geliefert
        k["lcoh_inkl_netz"] = (k["kosten_a_gesamt"] + nk["kosten_a_netz_system"]) / Q_geliefert
        k["gas_lcoh_inkl_netz"] = (ref["gas_lcoh"] * Q + nk["kosten_a_netz_gasref"]) / Q_geliefert
        if nk_bew is not None:
            k["lcoh_inkl_netz_bew"] = (
                k["kosten_a_gesamt_bew"] + nk_bew["kosten_a_netz_system"]
            ) / Q_geliefert
            k["abstand_gas_inkl_netz_bew"] = k["gas_lcoh_inkl_netz"] - k["lcoh_inkl_netz_bew"]

    # Fläche (Check)
    flaeche = A * cfg.get("kollektor.flaechenfaktor") + V / cfg.get("ptes.volumen_je_grundflaeche")
    k["flaeche_m2"] = flaeche
    k["flaeche_ok"] = bool(flaeche <= cfg.get("standort.flaeche_verfuegbar") * (1 + 1e-6))
    return k, r
