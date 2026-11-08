"""Wirtschaftlichkeit (AP 9): Annuitätenmethode nach VDI 2067-1, LCOH, CO2-Vermeidungskosten.

Kapitalkosten: Annuität über die technische Lebensdauer (äquivalente Jahreskosten; bei Lebensdauer
> Betrachtungszeitraum entspricht das einer Restwertgutschrift).
Energiekosten mit Preisänderung r (VDI 2067-1, preisdynamischer Barwertfaktor):
    b(r, i, T) = (1 - ((1+r)/(1+i))^T) / (i - r),   Faktor auf Jahr-1-Kosten = a(i, T) * b
Bei r = 0 ist der Faktor genau 1 (reale Rechnung mit konstanten Preisen, TEAM-Vorgabe).
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


def kapitalkosten_jahr(
    invest: float, zins: float, lebensdauer: float, om_fix: float, foerderquote: float = 0.0
) -> float:
    """Annuität + fixe O&M (Anteil vom Invest, ohne Förderabzug) [EUR/a]."""
    return annuitaet(invest, zins, lebensdauer, foerderquote) + invest * om_fix


def preisdynamik(zins: float, jahre: float, r: float) -> float:
    """Mittelwertfaktor a*b: jährlich konstante Ersatzkosten je EUR Kosten im ersten Jahr."""
    if abs(zins - r) < 1e-12:
        b = jahre / (1.0 + zins)
    else:
        b = (1.0 - ((1.0 + r) / (1.0 + zins)) ** jahre) / (zins - r)
    return annuitaetenfaktor(zins, jahre) * b


def ptes_invest(cfg: Config, V_m3: float) -> float:
    """Invest PTES [EUR]: c(V) = c_ref * (V/V_ref)^b * Preisindex (degressiv, docs E13)."""
    if V_m3 <= 0:
        return 0.0
    c = (
        cfg.get("ptes.kosten_ref")
        * (V_m3 / cfg.get("ptes.V_ref")) ** cfg.get("ptes.kosten_exponent")
        * cfg.get("ptes.preisindex")
    )
    return c * V_m3


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


def gas_referenz(cfg: Config, Q_MWh_a: float, P_max_MW: float) -> dict:
    """Referenz: Gaskessel deckt die gesamte Einspeisung (AP 7 Einfach)."""
    zins = cfg.get("oekonomie.zins")
    T = cfg.get("oekonomie.betrachtungszeitraum")
    P = P_max_MW * cfg.get("gas_referenz.auslegung")
    capex_a = kapitalkosten_jahr(
        P * cfg.get("gas_referenz.kosten_spez"),
        zins,
        cfg.get("oekonomie.lebensdauer.gaskessel"),
        cfg.get("oekonomie.om_fix.gaskessel"),
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
