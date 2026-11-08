"""Aufbau des PyPSA-Netzes aus Config + Zeitreihen (BRF §3).

Busse (BRF §3.1):
    elec [MW], sol_hi / sol_lo [MW], V85 / V45 / V10 [m3], heat_plant [MW], heat_town [MW],
    hp_src [MW] (Quellwärme WP aus PTES), hp_heat [MW] (WP-Kondensator, Hilfsbus)

Konventionen:
- Kollektor: p_nom = A[m2] * 1e-3, p_max_pu = P_spez[kW/m2] (solar.py, docs E11)
- Pools: Store-Energie = Volumen [m3], e_nom = V, e_cyclic = True
- Pool-Links: efficiency = 1 (Volumen), Wärme über bus2 mit efficiency2 = ±dT * c
  (PyPSA: positiv = Abgabe an bus2, negativ = Entnahme)
- Wärmepumpe: zwei Links (Luft / PTES) auf den Hilfsbus hp_heat; der Link ``hp_out``
  (hp_heat -> heat_plant) trägt die thermische WP-Leistung P_WP (p_nom_extendable). Damit ist die
  gemeinsame Kapazität (BRF §3.4) automatisch erfüllt; p_max_pu je Quelle in constraints.py.
- Investitionen in Kollektor und PTES sind im Raster fest und gehen erst in die LCOH ein;
  WP und PtH werden mit annualisierten Kosten mitoptimiert (BRF §2).
- Strompreis im LP = Preis * preisdynamischer Faktor (economics.preisdynamik), damit Betrieb und
  Dimensionierung zur LCOH-Rechnung passen.
"""

from __future__ import annotations

import logging

import pandas as pd

from serts import economics
from serts.config import Config

log = logging.getLogger(__name__)

POOLS = ("V85", "V45", "V10")

# Pflichtparameter für einen Lauf (Abbruch, wenn null)
PFLICHT = [
    "kollektor.eta0",
    "kollektor.a1",
    "kollektor.a2",
    "kollektor.neigung",
    "netz.x_TL",
    "strom.preis_fest",
    "strom.emissionsfaktor",
    "waermepumpe.kosten_spez",
    "pth.kosten_spez",
    "oekonomie.zins",
    "oekonomie.betrachtungszeitraum",
]


def pool_links(cfg: Config) -> list[dict]:
    """Tabelle der Volumen-Links (BRF §3.2) inkl. Wärme-Effizienz auf bus2 [MWh/m3]."""
    c = cfg.get("ptes.c_wasser")
    t_hi, t_mid, t_lo = (cfg.get(f"ptes.T_{k}") for k in ("oben", "mitte", "unten"))
    links = [
        dict(
            name="laden_hi_aus45",
            bus0="V45",
            bus1="V85",
            bus2="sol_hi",
            efficiency2=-(t_hi - t_mid) * c,
        ),
        dict(
            name="laden_hi_aus10",
            bus0="V10",
            bus1="V85",
            bus2="sol_hi",
            efficiency2=-(t_hi - t_lo) * c,
        ),
        dict(
            name="laden_lo", bus0="V10", bus1="V45", bus2="sol_lo", efficiency2=-(t_mid - t_lo) * c
        ),
        dict(
            name="entladen_direkt",
            bus0="V85",
            bus1="V45",
            bus2="heat_plant",
            efficiency2=(t_hi - t_mid) * c,
        ),
        dict(
            name="wp_quelle_ptes",
            bus0="V45",
            bus1="V10",
            bus2="hp_src",
            efficiency2=(t_mid - t_lo) * c,
        ),
        dict(name="verlust_oben", bus0="V85", bus1="V45"),
        dict(name="verlust_mitte", bus0="V45", bus1="V10"),
    ]
    if cfg.get("pth.laden_ptes"):
        raise NotImplementedError("Variante PtH lädt PTES (BRF §3.5) noch nicht umgesetzt")
    return links


def annualisiert(cfg: Config, komponente: str, kosten_key: str) -> float:
    """Jährliche Kapitalkosten inkl. fixer O&M je Einheit [EUR/(Einheit*a)]."""
    return economics.kapitalkosten_jahr(
        invest=cfg.get(kosten_key),
        zins=cfg.get("oekonomie.zins"),
        lebensdauer=cfg.get(f"oekonomie.lebensdauer.{komponente}"),
        om_fix=cfg.get(f"oekonomie.om_fix.{komponente}"),
        foerderquote=cfg.get("oekonomie.foerderquote"),
    )


def build_network(cfg: Config, ts: pd.DataFrame, A_koll_m2: float, V_m3: float):
    """Baut das Netz für feste Größen (A [m2], V [m3]).

    ``ts`` braucht die Spalten last_gesamt [MW], COP_luft, p_max_pu_luft, P_hi, P_lo [kW/m2],
    strompreis [EUR/MWh], T_a [degC] (siehe prepare.build_zeitreihen).
    """
    import pypsa

    cfg.require(PFLICHT)
    n = pypsa.Network()
    n.set_snapshots(ts.index)
    n.meta = {"A_koll_m2": float(A_koll_m2), "V_m3": float(V_m3), "szenario": cfg.name}
    mit_speicher = V_m3 > 0
    p_koll = A_koll_m2 * 1e-3  # MW bei 1 kW/m2

    carriers = ["strom", "solar", "wasser", "waerme"]
    n.add("Carrier", carriers)
    busse = {
        "elec": "strom",
        "sol_hi": "solar",
        "sol_lo": "solar",
        "heat_plant": "waerme",
        "heat_town": "waerme",
        "hp_src": "waerme",
        "hp_heat": "waerme",
    }
    if mit_speicher:
        busse.update({p: "wasser" for p in POOLS})
    for bus, car in busse.items():
        n.add("Bus", bus, carrier=car, unit="m3" if car == "wasser" else "MW")

    # --- Strom ------------------------------------------------------------------
    f_strom = economics.preisdynamik(
        cfg.get("oekonomie.zins"),
        cfg.get("oekonomie.betrachtungszeitraum"),
        cfg.get("oekonomie.preisaenderung.strom"),
    )
    n.add(
        "Generator",
        "netz_strom",
        bus="elec",
        carrier="strom",
        p_nom=1e3,
        marginal_cost=ts["strompreis"] * f_strom,
    )

    # --- Kollektorfeld ------------------------------------------------------------
    n.add(
        "Generator",
        "sol_hi",
        bus="sol_hi",
        carrier="solar",
        p_nom=p_koll,
        p_max_pu=ts["P_hi"].clip(0, 1),
    )
    n.add(
        "Link",
        "solar_direkt",
        bus0="sol_hi",
        bus1="heat_plant",
        carrier="waerme",
        p_nom=max(p_koll, 1e-6),
    )
    if mit_speicher:
        n.add(
            "Generator",
            "sol_lo",
            bus="sol_lo",
            carrier="solar",
            p_nom=p_koll,
            p_max_pu=ts["P_lo"].clip(0, 1),
        )

    # Frostschutz: Anteil des potenziellen Hochtemperatur-Ertrags auf Froststunden verteilt
    frost = (ts["T_a"] < 0).astype(float)
    pot = float((ts["P_hi"] * p_koll).sum())
    if frost.sum() > 0 and pot > 0:
        n.add(
            "Load",
            "frostschutz",
            bus="heat_plant",
            carrier="waerme",
            p_set=frost * cfg.get("kollektor.frostschutz_anteil") * pot / frost.sum(),
        )

    # --- PTES-Pools -----------------------------------------------------------------
    if mit_speicher:
        for pool in POOLS:
            n.add("Store", pool, bus=pool, carrier="wasser", e_nom=V_m3, e_cyclic=True)
        eps = cfg.get("solver.tie_breaker")
        for d in pool_links(cfg):
            name = d.pop("name")
            # Tie-Breaker: Laden kostet eps je MWh Wärme -> Solar direkt hat Vorrang vor
            # "gleichzeitig laden und entladen" (sonst gleichwertige, nicht eindeutige Lösung)
            mc = eps * abs(d["efficiency2"]) if name.startswith("laden") else 0.0
            # p_nom = V je Stunde: Lade-/Entladeleistung praktisch nicht begrenzt (docs E12)
            n.add("Link", name, carrier="wasser", p_nom=V_m3, marginal_cost=mc, **d)

    # --- Wärmepumpe -------------------------------------------------------------------
    n.add(
        "Link",
        "hp_air",
        bus0="elec",
        bus1="hp_heat",
        carrier="strom",
        efficiency=ts["COP_luft"],
        p_nom=1e3,
    )
    if mit_speicher:
        cop_p = cfg.get("waermepumpe.COP_ptes")
        n.add(
            "Link",
            "hp_ptes",
            bus0="elec",
            bus1="hp_heat",
            bus2="hp_src",
            carrier="strom",
            efficiency=cop_p,
            efficiency2=-(cop_p - 1.0),
            p_nom=1e3,
        )
    n.add(
        "Link",
        "hp_out",
        bus0="hp_heat",
        bus1="heat_plant",
        carrier="waerme",
        p_nom_extendable=True,
        capital_cost=annualisiert(cfg, "waermepumpe", "waermepumpe.kosten_spez"),
    )

    # --- Netzanschluss, PtH, Last -------------------------------------------------------
    n.add(
        "Link",
        "transmission",
        bus0="heat_plant",
        bus1="heat_town",
        carrier="waerme",
        p_nom=cfg.get("netz.x_TL"),
        efficiency=1.0 - cfg.get("netz.TL_verlust"),
    )
    n.add(
        "Link",
        "pth",
        bus0="elec",
        bus1="heat_town",
        carrier="strom",
        efficiency=cfg.get("pth.eta"),
        p_nom_extendable=True,
        p_nom_min=cfg.get("pth.redundanz") * float(ts["last_gesamt"].max()) / cfg.get("pth.eta"),
        capital_cost=annualisiert(cfg, "pth", "pth.kosten_spez"),
    )
    n.add("Load", "last", bus="heat_town", carrier="waerme", p_set=ts["last_gesamt"])
    return n


def optimize(n, cfg: Config, ts: pd.DataFrame):
    """Löst das LP mit HiGHS und den Zusatz-Constraints. Gibt (status, condition) zurück."""
    from functools import partial

    from serts.constraints import extra_functionality

    ef = partial(extra_functionality, cfg=cfg, ts=ts)
    status, cond = n.optimize(
        solver_name=cfg.get("solver.name"),
        extra_functionality=ef,
        include_objective_constant=False,
        log_to_console=False,
    )
    if status != "ok":
        raise RuntimeError(f"Optimierung fehlgeschlagen: {status} / {cond}")
    return status, cond
