"""Wirtschaftlichkeit (AP 9): Annuitätenmethode, LCOH, CO2-Vermeidungskosten."""

from __future__ import annotations


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
        raise ValueError("System spart kein CO2 gegenüber der Referenz")
    return (lcoh_sys - lcoh_ref) / d_co2
