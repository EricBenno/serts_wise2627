"""PyPSA-Netz – bewusst einfach gehalten (docs E20).

                 ┌──────────── solar_direkt ─────────────┐
    Kollektor ──>│ solar                                 ▼
    (Generator)  └── laden ──> [Speicher (MWh)] ──> entladen_direkt ──> waerme ──> Last
                                     │                                  ▲   ▲
                                     └──(Quellwärme)──┐                 │   │
    Netzstrom ──> elec ──> hp_luft ──> wp ──> wp_out ──┼─────────────────┘   │
                     │ └──> hp_speicher ─┘ (bus2 = Speicher)                 │
                     └──> pth ───────────────────────────────────────────────┘

- Ein Wärmeknoten ``waerme`` (Erzeugung liegt am Netz, TEAM). Last = Gebäude + Netzverluste.
- Speicher: ein Store in MWh (Inhalt bezogen auf T_unten), Verlust = verlustrate * Inhalt je Stunde.
- Größen werden mitoptimiert (linear): Kollektorfläche, Speicher, WP- und PtH-Leistung.
  Kollektor-p_nom in MW bei 1 kW/m2 -> A [m2] = p_nom * 1000.
- WP: zwei Quellen (Luft, Speicher) teilen sich die thermische Leistung ``wp_out``.
"""

from __future__ import annotations

import pandas as pd

from serts import economics
from serts.config import Config

M2_JE_MW = 1000.0  # Kollektor: 1 MW p_nom = 1000 m2 (p_max_pu in kW/m2)


def annualisiert(cfg: Config, komponente: str, kosten: str | float) -> float:
    """Jährliche Kapitalkosten inkl. fixer O&M je Einheit [EUR/(Einheit*a)].

    ``kosten`` = Config-Schlüssel des spezifischen Invests oder direkt ein Wert.
    """
    invest = cfg.get(kosten) if isinstance(kosten, str) else kosten
    return economics.jahreskosten(cfg, komponente, invest)


def mwh_je_m3(cfg: Config) -> float:
    """Speicherkapazität je m3 Wasser: c * (T_oben - T_unten)."""
    return cfg.get("ptes.c_wasser") * (cfg.get("ptes.T_oben") - cfg.get("ptes.T_unten"))


def build_network(
    cfg: Config,
    ts: pd.DataFrame,
    A_m2: float | None = None,
    V_m3: float | None = None,
    stufe: tuple[float, float, float] | None = None,
):
    """Netz bauen. A_m2 / V_m3 = None -> Größe wird optimiert, sonst fest vorgegeben.

    Bei optimiertem Speicher gibt ``stufe`` = (V von, V bis, EUR/m3) die Preisstufe vor
    (ptes.preisstufen); das Volumen bleibt in diesem Bereich (siehe run.loese).

    ``ts`` braucht: last_gesamt [MW], T_a [degC], COP_luft, P_solar [kW/m2], strompreis [EUR/MWh].
    """
    import pypsa

    n = pypsa.Network()
    n.set_snapshots(ts.index)
    n.add("Carrier", ["strom", "waerme"])
    for bus, car in [
        ("elec", "strom"),
        ("solar", "waerme"),
        ("speicher", "waerme"),
        ("wp", "waerme"),
        ("waerme", "waerme"),
    ]:
        n.add("Bus", bus, carrier=car)

    zins, T = cfg.get("oekonomie.zins"), cfg.get("oekonomie.betrachtungszeitraum")
    f_strom = economics.preisdynamik(zins, T, cfg.get("oekonomie.preisaenderung.strom"))
    eps = cfg.get("solver.tie_breaker")

    # Strom
    n.add(
        "Generator",
        "netz_strom",
        bus="elec",
        carrier="strom",
        p_nom=1e3,
        marginal_cost=ts["strompreis"] * f_strom,
    )

    # Kollektorfeld (Kosten je m2 -> je MW p_nom)
    n.add(
        "Generator",
        "kollektor",
        bus="solar",
        carrier="waerme",
        p_max_pu=ts["P_solar"].clip(0, 1),
        p_nom=(A_m2 or 0.0) / M2_JE_MW,
        p_nom_extendable=A_m2 is None,
        capital_cost=annualisiert(cfg, "kollektor", "kollektor.kosten_spez") * M2_JE_MW,
    )
    n.add("Link", "solar_direkt", bus0="solar", bus1="waerme", carrier="waerme", p_nom=1e3)

    # Speicher (Kosten je m3 -> je MWh Kapazität)
    mit_speicher = V_m3 is None or V_m3 > 0
    if mit_speicher:
        kap = mwh_je_m3(cfg)
        if V_m3 is None:
            if stufe is None:
                raise ValueError("Speicher optimieren braucht eine Preisstufe (stufe=...)")
            v_von, v_bis, preis = stufe
            preis *= cfg.get("ptes.kosten_faktor")
        else:
            v_von = v_bis = V_m3
            preis = economics.speicherpreis(cfg, V_m3)
        n.meta = {**dict(getattr(n, "meta", {}) or {}), "speicher_preis": preis}
        n.add(
            "Store",
            "ptes",
            bus="speicher",
            carrier="waerme",
            e_cyclic=True,
            standing_loss=cfg.get("ptes.verlustrate"),
            e_nom=(V_m3 or 0.0) * kap,
            e_nom_extendable=V_m3 is None,
            e_nom_min=v_von * kap,
            e_nom_max=v_bis * kap,
            capital_cost=annualisiert(cfg, "ptes", preis) / kap,
        )
        # Tie-Breaker: Laden minimal teurer als Direktnutzung (docs E16)
        n.add(
            "Link",
            "laden",
            bus0="solar",
            bus1="speicher",
            carrier="waerme",
            p_nom=1e3,
            marginal_cost=eps,
        )
        n.add(
            "Link", "entladen_direkt", bus0="speicher", bus1="waerme", carrier="waerme", p_nom=1e3
        )

    # Wärmepumpe: Luft (COP je Stunde, aus unter T_min) und Speicher (COP konstant)
    luft_aus = ts["T_a"] < cfg.get("waermepumpe.T_min_luft")
    n.add(
        "Link",
        "hp_luft",
        bus0="elec",
        bus1="wp",
        carrier="strom",
        p_nom=1e3,
        efficiency=ts["COP_luft"],
        p_max_pu=(~luft_aus).astype(float),
    )
    if mit_speicher:
        cop = cfg.get("waermepumpe.COP_ptes")
        n.add(
            "Link",
            "hp_speicher",
            bus0="elec",
            bus1="wp",
            bus2="speicher",
            carrier="strom",
            p_nom=1e3,
            efficiency=cop,
            efficiency2=-(cop - 1.0),
            # nur in der Heizperiode als Quelle (waermepumpe.speicher_monate, docs E21)
            p_max_pu=ts.index.month.isin(cfg.get("waermepumpe.speicher_monate")).astype(float),
        )
    n.add(
        "Link",
        "wp_out",
        bus0="wp",
        bus1="waerme",
        carrier="waerme",
        p_nom_extendable=True,
        capital_cost=annualisiert(cfg, "waermepumpe", "waermepumpe.kosten_spez"),
    )

    # PtH mit Mindestleistung (Redundanz) und Last
    eta = cfg.get("pth.eta")
    n.add(
        "Link",
        "pth",
        bus0="elec",
        bus1="waerme",
        carrier="strom",
        efficiency=eta,
        p_nom_extendable=True,
        p_nom_min=cfg.get("pth.redundanz") * float(ts["last_gesamt"].max()) / eta,
        capital_cost=annualisiert(cfg, "pth", "pth.kosten_spez") * eta,
    )
    n.add("Load", "last", bus="waerme", carrier="waerme", p_set=ts["last_gesamt"])
    return n


def optimize(n, cfg: Config, threads: int | None = None):
    """Löst das LP (HiGHS) mit den zwei Zusatzbedingungen aus constraints.py.

    ``threads=1`` bei parallelen Läufen (sonst überbuchen mehrere HiGHS-Prozesse die Kerne).
    """
    from functools import partial

    from serts.constraints import extra_functionality

    status, cond = n.optimize(
        solver_name=cfg.get("solver.name"),
        extra_functionality=partial(extra_functionality, cfg=cfg),
        include_objective_constant=False,
        log_to_console=False,
        **dict(cfg.get("solver.optionen")),
        **({"threads": threads} if threads else {}),
    )
    if status != "ok":
        raise RuntimeError(f"Optimierung fehlgeschlagen: {status} / {cond}")
    return status, cond
