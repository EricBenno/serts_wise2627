"""PyPSA-Netz – bewusst einfach gehalten (docs E20, E27).

                 ┌──────────── solar_direkt ─────────────┐
    Kollektor ──>│ solar                                 ▼
                 └── laden ──> [Speicher heiß | kalt] ──> entladen_direkt ──> waerme ──> Last
                                  │  (53 % | 47 %)  └── Quellwärme ──┐          ▲   ▲
    Netzstrom ──> hp_luft ───────────────────────────────> wp ───────┴> wp_out ─┘   │
             └──> hp_speicher (holt Quellwärme aus dem kalten Teil) ┘               │
             └──> pth ──────────────────────────────────────────────────────────────┘

- Ein Wärmeknoten ``waerme`` (Erzeugung liegt am Netz, TEAM). Last = Gebäude + Netzverluste.
- Speicher in zwei Teilen (Energie in MWh, bezogen auf T_unten):
    heiß  = Wärme zwischen T_oben und Netz-Rücklauf (40 K = 53 %)  -> kann direkt ins Netz
    kalt  = Wärme zwischen Rücklauf und T_unten (35 K = 47 %)      -> nur über die Wärmepumpe
  Beladen füllt beide Teile immer im Verhältnis 53 : 47 (Wasser wird von T_unten auf T_oben erwärmt).
  Verlust = verlustrate * Inhalt je Stunde und Teil. Größe: nur das Volumen wird optimiert, die Teile
  folgen dem festen Verhältnis (constraints.py).
- Größen werden mitoptimiert (linear): Kollektorfläche, Speicher, WP- und PtH-Leistung.
  Kollektor-p_nom in MW bei 1 kW/m2 -> A [m2] = p_nom * 1000.
- WP: zwei Quellen (Luft, Speicher) teilen sich die thermische Leistung ``wp_out``; die Luft-WP verliert
  bei Kälte Leistung (constraints.py).
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


def anteil_heiss(cfg: Config) -> float:
    """Anteil der Speicherenergie oberhalb des Netz-Rücklaufs: (T_oben - T_RL) / (T_oben - T_unten)."""
    t_o, t_r, t_u = (cfg.get(k) for k in ("ptes.T_oben", "netz.T_RL", "ptes.T_unten"))
    return (t_o - t_r) / (t_o - t_u)


def fuellstand_direkt(cfg: Config) -> float:
    """Mindestfüllstand (Energieinhalt / Kapazität) für Direktentladung ins Netz (Temperaturkennlinie).

    Die Oberschicht hat ab ``ptes.fuellstand_voll`` die Temperatur T_oben, darunter fällt sie linear bis
    T_unten. Direkt ins Netz geht es erst bei T_oben_min = T_VL + dT. 0 = Kennlinie aus.
    """
    s_voll = cfg.get("ptes.fuellstand_voll")
    if s_voll <= 0:
        return 0.0
    t_o, t_u = cfg.get("ptes.T_oben"), cfg.get("ptes.T_unten")
    t_noetig = cfg.get("netz.T_VL") + cfg.get("ptes.direkt_dT")
    return s_voll * min(1.0, max(0.0, (t_noetig - t_u) / (t_o - t_u)))


def temperaturen_speicher(cfg: Config, fuellstand: pd.Series) -> tuple[pd.Series, pd.Series]:
    """(Temperatur Oberschicht, mittlere Temperatur) in degC aus dem Füllstand 0..1 (Kennlinie)."""
    t_o, t_u = cfg.get("ptes.T_oben"), cfg.get("ptes.T_unten")
    s_voll = cfg.get("ptes.fuellstand_voll")
    mittel = t_u + fuellstand * (t_o - t_u)
    oben = (
        t_u + (t_o - t_u) * (fuellstand / s_voll).clip(upper=1.0)
        if s_voll > 0
        else mittel * 0 + t_o
    )
    return oben, mittel


def build_network(
    cfg: Config,
    ts: pd.DataFrame,
    A_m2: float | None = None,
    V_m3: float | None = None,
    segment: tuple[float, float, float, float] | None = None,
):
    """Netz bauen. A_m2 / V_m3 = None -> Größe wird optimiert, sonst fest vorgegeben.

    Bei optimiertem Speicher gibt ``segment`` = (V von, V bis, Grenzkosten EUR/m3, Fixkosten EUR) das
    Kostensegment vor (economics.ptes_segmente); das Volumen bleibt in diesem Bereich (siehe run.loese).

    ``ts`` braucht: last_gesamt [MW], T_a [degC], COP_luft, P_solar [kW/m2], strompreis [EUR/MWh].
    """
    import pypsa

    n = pypsa.Network()
    n.set_snapshots(ts.index)
    n.add("Carrier", ["strom", "waerme"])
    for bus, car in [
        ("elec", "strom"),
        ("solar", "waerme"),
        ("heiss", "waerme"),
        ("kalt", "waerme"),
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

    # Speicher in zwei Teilen heiß/kalt (Kosten je m3 -> je MWh heiß, da V = E_heiß / (f * kap))
    mit_speicher = V_m3 is None or V_m3 > 0
    if mit_speicher:
        kap = mwh_je_m3(cfg)
        f = anteil_heiss(cfg)
        if V_m3 is None:
            if segment is None:
                raise ValueError("Speicher optimieren braucht ein Kostensegment (segment=...)")
            v_von, v_bis, steigung, fix = segment
        else:
            v_von = v_bis = V_m3
            steigung, fix = economics.ptes_invest(cfg, V_m3) / V_m3, 0.0
        n.meta = {
            **dict(getattr(n, "meta", {}) or {}),
            "speicher_steigung": steigung,
            "speicher_fix": fix,
        }
        v_fix = V_m3 or 0.0
        verlust = cfg.get("ptes.verlustrate")
        for name, bus, anteil, kosten in (
            ("ptes_heiss", "heiss", f, annualisiert(cfg, "ptes", steigung) / (kap * f)),
            ("ptes_kalt", "kalt", 1.0 - f, 0.0),
        ):
            n.add(
                "Store",
                name,
                bus=bus,
                carrier="waerme",
                e_cyclic=True,
                standing_loss=verlust,
                e_nom=v_fix * kap * anteil,
                e_nom_extendable=V_m3 is None,
                e_nom_min=v_von * kap * anteil,
                e_nom_max=v_bis * kap * anteil,
                capital_cost=kosten,  # Kosten nur am heißen Teil; kalter Teil folgt per Constraint
            )
        # Laden: 1 MWh Solarwärme füllt heiß und kalt im Verhältnis f : (1-f).
        # Tie-Breaker: Laden minimal teurer als Direktnutzung (docs E16)
        n.add(
            "Link",
            "laden",
            bus0="solar",
            bus1="heiss",
            bus2="kalt",
            carrier="waerme",
            p_nom=1e3,
            efficiency=f,
            efficiency2=1.0 - f,
            marginal_cost=eps,
        )
        n.add("Link", "entladen_direkt", bus0="heiss", bus1="waerme", carrier="waerme", p_nom=1e3)
        if fuellstand_direkt(cfg) > 0:
            # Kühlt sich der Inhalt unter die Direkt-Grenze ab, ist die Wärme des heißen Bands nur noch über
            # die Wärmepumpe nutzbar: Umbuchung heiß -> kalt (verlustfrei, Energie bleibt im Speicher).
            n.add("Link", "umlagern", bus0="heiss", bus1="kalt", carrier="waerme", p_nom=1e3)

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
            bus2="kalt",
            carrier="strom",
            p_nom=1e3,
            efficiency=cop,
            efficiency2=-(cop - 1.0),
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
    # Links ohne dritten Anschluss: efficiency2 ist dort bedeutungslos (sonst NaN-Warnung)
    if "efficiency2" in n.links:
        n.links["efficiency2"] = n.links["efficiency2"].fillna(1.0)
    return n


def optimize(n, cfg: Config, ts: pd.DataFrame, threads: int | None = None):
    """Löst das LP (HiGHS) mit den Zusatzbedingungen aus constraints.py (``ts`` für die WP-Leistung).

    ``threads=1`` bei parallelen Läufen (sonst überbuchen mehrere HiGHS-Prozesse die Kerne).
    """
    from functools import partial

    from serts.constraints import extra_functionality

    status, cond = n.optimize(
        solver_name=cfg.get("solver.name"),
        extra_functionality=partial(extra_functionality, cfg=cfg, ts=ts),
        include_objective_constant=False,
        log_to_console=False,
        progress=False,
        **dict(cfg.get("solver.optionen")),
        **({"threads": threads} if threads else {}),
    )
    if status != "ok":
        raise RuntimeError(f"Optimierung fehlgeschlagen: {status} / {cond}")
    return status, cond
