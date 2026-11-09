"""Wirtschaftlichkeit (AP 9): Annuitätenmethode nach VDI 2067 Blatt 1, LCOH, CO2-Vermeidungskosten.

Alle Kosten werden als Annuität über den Betrachtungszeitraum T (oekonomie.betrachtungszeitraum)
ausgedrückt, Zinsfaktor q = 1 + i, Annuitätsfaktor a = (q - 1) / (1 - q^-T).

Kapitalgebundene Kosten (VDI 2067-1, Gl. für A_N,K):
    A_N,K = (A0 + A1 + ... + An - R_W) * a
    Ersatzbeschaffung k im Jahr k*T_N:  A_k = A0 * r^(k*T_N) / q^(k*T_N),  n = ceil(T/T_N) - 1
    Restwert (linear):                  R_W = A0 * r^(n*T_N) * ((n+1)*T_N - T) / T_N / q^T
Betriebsgebundene Kosten: A0 * f_om * (a * b_B)   (Instandsetzung + Wartung, VDI: f_Inst + f_W+Insp)
Bedarfsgebundene Kosten (Energie): Kosten im 1. Jahr * (a * b_V) mit dem preisdynamischen Barwertfaktor
    b(r, i, T) = (1 - ((1+r)/(1+i))^T) / (i - r)
Bei realer Rechnung ohne Preisänderung (r = 0, TEAM-Vorgabe) ist a * b = 1.
Förderung (Investitionszuschuss) mindert A0 in den kapitalgebundenen Kosten.
Nicht enthalten (VDI-Kostengruppe "sonstige Kosten", Bedienpersonal): siehe docs/entscheidungen.md E25.
"""

from __future__ import annotations

from serts.config import Config


def annuitaetenfaktor(zins: float, jahre: float) -> float:
    """Capital Recovery Factor: i(1+i)^n / ((1+i)^n - 1); bei i = 0 -> 1/n."""
    if jahre <= 0:
        raise ValueError("Lebensdauer muss > 0 sein")
    if zins == 0:
        return 1.0 / jahre
    q = (1.0 + zins) ** jahre
    return zins * q / (q - 1.0)


def annuitaet(invest: float, zins: float, jahre: float, foerderquote: float = 0.0) -> float:
    return invest * (1.0 - foerderquote) * annuitaetenfaktor(zins, jahre)


def kapitalfaktor_vdi(zins: float, T: float, T_N: float, r: float = 0.0) -> float:
    """VDI 2067-1: (A0 + Ersatz - Restwert) * a, bezogen auf A0 = 1 [1/a]."""
    import math

    q, rr = 1.0 + zins, 1.0 + r
    n = max(math.ceil(T / T_N) - 1, 0)
    barwert = 1.0 + sum((rr / q) ** (k * T_N) for k in range(1, n + 1))
    restwert = rr ** (n * T_N) * ((n + 1) * T_N - T) / T_N / q**T
    return (barwert - restwert) * annuitaetenfaktor(zins, T)


def kapitalkosten_jahr(
    invest: float,
    zins: float,
    lebensdauer: float,
    om_fix: float,
    foerderquote: float = 0.0,
    T: float | None = None,
    r_invest: float = 0.0,
    r_betrieb: float = 0.0,
) -> float:
    """Kapital- + betriebsgebundene Kosten nach VDI 2067-1 [EUR/a].

    Ohne T (Betrachtungszeitraum) wird T = lebensdauer gesetzt (einfache Annuität).
    """
    T = lebensdauer if T is None else T
    kapital = invest * (1.0 - foerderquote) * kapitalfaktor_vdi(zins, T, lebensdauer, r_invest)
    betrieb = invest * om_fix * preisdynamik(zins, T, r_betrieb)
    return kapital + betrieb


def jahreskosten(
    cfg: Config, komponente: str, invest: float, gefoerdert: bool | None = None
) -> float:
    """VDI-2067-Jahreskosten einer Komponente aus oekonomie.* (Lebensdauer, O&M, Förderung, T).

    ``invest`` ohne Nebenkosten; ``oekonomie.nebenkosten`` (Planung etc.) wird aufgeschlagen.
    Förderquote gilt nur, wenn ``oekonomie.foerderfaehig.<komponente>`` (oder ``gefoerdert``) true ist.
    """
    if gefoerdert is None:
        gefoerdert = bool(cfg.get(f"oekonomie.foerderfaehig.{komponente}"))
    return kapitalkosten_jahr(
        invest=invest * (1.0 + cfg.get("oekonomie.nebenkosten")),
        zins=cfg.get("oekonomie.zins"),
        lebensdauer=cfg.get(f"oekonomie.lebensdauer.{komponente}"),
        om_fix=cfg.get(f"oekonomie.om_fix.{komponente}"),
        foerderquote=cfg.get("oekonomie.foerderquote") if gefoerdert else 0.0,
        T=cfg.get("oekonomie.betrachtungszeitraum"),
        r_invest=cfg.get("oekonomie.preisaenderung.invest"),
        r_betrieb=cfg.get("oekonomie.preisaenderung.betrieb"),
    )


def preisdynamik(zins: float, jahre: float, r: float) -> float:
    """Mittelwertfaktor a*b: jährlich konstante Ersatzkosten je EUR Kosten im ersten Jahr."""
    if abs(zins - r) < 1e-12:
        b = jahre / (1.0 + zins)
    else:
        b = (1.0 - ((1.0 + r) / (1.0 + zins)) ** jahre) / (zins - r)
    return annuitaetenfaktor(zins, jahre) * b


def ptes_kosten_je_m3(cfg: Config, V_m3: float) -> float:
    """Durchschnittlicher Speicherpreis [EUR/m3] bei Volumen V: c_ref * (V/V_ref)^b * Preisindex * Faktor."""
    return (
        cfg.get("ptes.kosten_ref")
        * (V_m3 / cfg.get("ptes.V_ref")) ** cfg.get("ptes.kosten_exponent")
        * cfg.get("ptes.preisindex")
        * cfg.get("ptes.kosten_faktor")
    )


def ptes_invest(cfg: Config, V_m3: float) -> float:
    """Investition PTES [EUR] = V * c(V): stetig, mit der Größe abnehmender Stückpreis (Skaleneffekt)."""
    return V_m3 * ptes_kosten_je_m3(cfg, V_m3) if V_m3 > 0 else 0.0


def ptes_segmente(cfg: Config) -> list[tuple[float, float, float, float]]:
    """Stückweise lineare Näherung von C(V): (V von, V bis, Grenzkosten EUR/m3, Fixkosten EUR).

    Je Segment gilt C(V) = Fix + Grenzkosten * V (Sehne durch die Stützstellen); die Kostenfunktion ist
    damit stetig und monoton, Fixkosten und Grenzkosten sind im LP je Segment konstant.
    """
    pts = list(cfg.get("ptes.segmente_m3"))
    out = []
    for v0, v1 in zip(pts[:-1], pts[1:], strict=True):
        c0, c1 = ptes_invest(cfg, v0), ptes_invest(cfg, v1)
        steigung = (c1 - c0) / (v1 - v0)
        out.append((float(v0), float(v1), steigung, c0 - steigung * v0))
    return out


def lcoh(annuitaeten_capex: float, opex_jahr: float, waerme_MWh: float) -> float:
    """Wärmegestehungskosten [EUR/MWh]. Bezug (erzeugt vs. geliefert) im Aufruf festlegen."""
    if waerme_MWh <= 0:
        raise ValueError("Wärmemenge muss > 0 sein")
    return (annuitaeten_capex + opex_jahr) / waerme_MWh


def co2_vermeidungskosten(
    lcoh_sys: float, lcoh_ref: float, co2_sys_t_MWh: float, co2_ref_t_MWh: float
) -> float:
    """EUR/t CO2 gegenüber Referenz (beide spezifisch je MWh Wärme)."""
    d_co2 = co2_ref_t_MWh - co2_sys_t_MWh
    if d_co2 <= 0:
        return float("nan")
    return (lcoh_sys - lcoh_ref) / d_co2


def netzkosten(cfg: Config) -> dict:
    """Verteilnetz: Trasse (Straße / grüne Wiese) + Hausanschlüsse -> Invest und Jahreskosten.

    Gleiche Investition für System und Gas-Referenz (Gas-Fernwärme mit demselben Netz); die Förderung
    gilt nur für das System und nur für förderfähige Teile (oekonomie.foerderfaehig).
    """
    L = cfg.get("netz.trassenlaenge")
    s = cfg.get("netz.anteil_strasse")
    trasse = L * (
        s * cfg.get("netz.kosten_trasse_strasse") + (1 - s) * cfg.get("netz.kosten_trasse_gruen")
    )
    ha = cfg.get("netz.hausanschluesse") * cfg.get("netz.kosten_hausanschluss")
    k_trasse = jahreskosten(cfg, "netz", trasse)
    k_ha = jahreskosten(cfg, "hausanschluss", ha)
    return {
        "netz_invest_trasse_EUR": trasse,
        "netz_invest_hausanschluss_EUR": ha,
        "kosten_a_netz_trasse": k_trasse,
        "kosten_a_netz_hausanschluss": k_ha,
        "kosten_a_netz_system": k_trasse + k_ha,
        "kosten_a_netz_gasref": jahreskosten(cfg, "netz", trasse, gefoerdert=False)
        + jahreskosten(cfg, "hausanschluss", ha, gefoerdert=False),
    }


def gas_referenz(cfg: Config, Q_MWh_a: float, P_max_MW: float) -> dict:
    """Referenz: Gaskessel deckt die gesamte Einspeisung (AP 7 Einfach)."""
    zins = cfg.get("oekonomie.zins")
    T = cfg.get("oekonomie.betrachtungszeitraum")
    P = P_max_MW * cfg.get("gas_referenz.auslegung")
    capex_a = jahreskosten(
        cfg, "gaskessel", P * cfg.get("gas_referenz.kosten_spez"), gefoerdert=False
    )
    brennstoff_hi = Q_MWh_a / cfg.get("gas_referenz.eta")
    gas_kosten = (
        brennstoff_hi
        * cfg.get("gas_referenz.hs_hi")
        * cfg.get("gas_referenz.gaspreis")
        * preisdynamik(zins, T, cfg.get("oekonomie.preisaenderung.gas"))
    )
    co2_t = brennstoff_hi * cfg.get("gas_referenz.emissionsfaktor")
    co2_kosten = (
        co2_t
        * cfg.get("gas_referenz.co2_preis")
        * preisdynamik(zins, T, cfg.get("oekonomie.preisaenderung.co2"))
    )
    return {
        "gas_P_kessel_MW": P,
        "gas_capex_a": capex_a,
        "gas_brennstoffkosten_a": gas_kosten,
        "gas_co2_kosten_a": co2_kosten,
        "gas_co2_t_a": co2_t,
        "gas_lcoh": lcoh(capex_a, gas_kosten + co2_kosten, Q_MWh_a),
    }
