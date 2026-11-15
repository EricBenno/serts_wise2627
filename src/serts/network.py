"""PyPSA-Netz – bewusst einfach gehalten (docs E20, E27, E39).

    Kollektor ──> solar ──┬── solar_direkt ─────────────────────────────────────────────> waerme ──> Last
                          ├── laden_heiss ─> [ heiß (Kern)   85 °C ] ── entladen_direkt ──>   ▲
                          │                  [ Übergangszone       ] ── vorwaermen ───────>   │ (+ Nachheizen)
                          └── laden_kalt ──> [ kalt        10-45 °C] ── Quellwärme ─┐         │
    Netzstrom ──> hp_luft ──────────────────────────────> wp ── wp_out ─────────────┴────────>┤
             └──> hp_speicher (holt Quellwärme aus dem kalten Teil) ┘                         │
             └──> pth ────────────────────────────────────────────────────────────────────────┘

- Ein Wärmeknoten ``waerme`` (Erzeugung liegt am Netz, TEAM). Last = Gebäude + Netzverluste.
- Speicher = ein Wasservolumen, Energie in MWh bezogen auf T_unten, in drei Teilen:
    kalt      = Wärme zwischen T_unten und Netz-Rücklauf (47 %)   -> nur über die Wärmepumpe
    heiß      = Wärme zwischen Rücklauf und T_oben (53 %), davon
      Kern          (heißes Wasser oben)                           -> direkt ins Netz
      Übergangszone (Mischwasser zwischen heiß und kalt)           -> Rücklauf vorwärmen oder über die WP
  Laden: ``laden_kalt`` erwärmt Wasser von T_unten auf Rücklauf, ``laden_heiss`` von Rücklauf auf T_oben.
  Schichtung (constraints.py): Kern relativ <= Übergangszone relativ <= kalt relativ. Damit braucht jede
  heiße Schicht ihre Übergangszone und ihr 10-45-°C-Wasser darunter; ein Lauf, keine Schwelle.
  ``abbau`` (Kern -> Übergangszone) und ``umlagern`` (Übergangszone -> kalt) sind Mischen ohne Energieverlust.
  Verlust = Verlustrate * Inhalt je Stunde und Teil. Verlustrate und Anteil der Übergangszone hängen von der
  Speichergröße ab (kleine Speicher: mehr Oberfläche je m3, weniger Tiefe).
- Größen werden mitoptimiert (linear): Kollektorfläche, Speicher, WP-, PtH- und Netzanschlussleistung.
  Kollektor-p_nom in MW bei 1 kW/m2 -> A [m2] = p_nom * 1000.
- WP: zwei Quellen (Luft, Speicher) teilen sich die thermische Leistung ``wp_out``; die Luft-WP verliert
  bei Kälte Leistung (constraints.py).
- Strom: Arbeitspreis am Generator ``netz_strom``, Leistungspreis als Kosten der Leistung ``netzanschluss``.
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


def groessenfaktor(cfg: Config, V_m3: float) -> float:
    """(V / V_ref)^Exponent: kleine Speicher haben je m3 mehr Oberfläche und weniger Tiefe (Exponent -1/3)."""
    if V_m3 <= 0:
        return 1.0
    return (V_m3 / cfg.get("ptes.V_ref")) ** cfg.get("ptes.groessen_exponent")


def verlustrate(cfg: Config, V_m3: float) -> float:
    """Verlustrate [1/h] bei Volumen V: Wert bei V_ref (Dronninglund) * Größenfaktor."""
    return cfg.get("ptes.verlustrate") * groessenfaktor(cfg, V_m3)


def anteil_uebergang(cfg: Config, V_m3: float) -> float:
    """Anteil der Übergangszone am heißen Teil (0..uebergang_max); 0 = ideale Schichtung.

    ``ptes.uebergang_ref`` ist der Anteil bei V_ref (Dronninglund 2014, Messdaten). Die Zone ist eine Dicke
    in Metern, kein Anteil -> bei flacheren (kleineren) Speichern größer (Größenfaktor). Braucht das Netz
    weniger als T_oben (T_VL + dT < T_oben), zählt nur der Teil der Zone unter dieser Temperatur.
    """
    s = cfg.get("ptes.uebergang_ref")
    if s <= 0:
        return 0.0
    t_o, t_r = cfg.get("ptes.T_oben"), cfg.get("netz.T_RL")
    t_noetig = cfg.get("netz.T_VL") + cfg.get("ptes.direkt_dT")
    temperatur = min(1.0, max(0.0, (t_noetig - t_r) / (t_o - t_r)))
    return min(cfg.get("ptes.uebergang_max"), s * groessenfaktor(cfg, V_m3) * temperatur)


def vorwaerm_verhaeltnis(cfg: Config) -> float:
    """Vorwärmleistung je MW Nachheizung (WP/PtH), 0 = Vorwärmen aus.

    Wasser der Übergangszone (Mittel zwischen Rücklauf und T_oben) wärmt den Rücklauf bis auf
    T_mittel - dT vor; den Rest bis zum Vorlauf muss WP oder PtH in derselben Stunde liefern.
    Basis: 65 °C - 5 K = 60 °C -> 15 K Vorwärmen, 20 K Nachheizen -> 0,75.
    """
    if not cfg.get("ptes.vorwaermen"):
        return 0.0
    t_o, t_r, t_vl = cfg.get("ptes.T_oben"), cfg.get("netz.T_RL"), cfg.get("netz.T_VL")
    t_vor = min(t_vl, (t_o + t_r) / 2.0 - cfg.get("ptes.direkt_dT"))
    if t_vor <= t_r:
        return 0.0
    return (t_vor - t_r) / (t_vl - t_vor) if t_vl > t_vor else 1e3


def temperaturen_speicher(cfg: Config, s_kern, s_ueb, s_kalt, anteil_ueb: float):
    """(Temperatur oben, mittlere Temperatur) in degC aus den Füllständen 0..1 der drei Teile (nur Anzeige).

    Mittel = Energieinhalt / Wasser. Oben: T_oben, solange der Kern heißes Wasser enthält; sonst die
    Mischtemperatur aus kaltem Teil und Übergangszone (beide voll = T_oben, beide leer = T_unten).
    """
    t_o, t_r, t_u = (cfg.get(k) for k in ("ptes.T_oben", "netz.T_RL", "ptes.T_unten"))
    heiss = (1.0 - anteil_ueb) * s_kern + anteil_ueb * s_ueb
    mittel = t_u + (t_r - t_u) * s_kalt + (t_o - t_r) * heiss
    ohne_kern = t_u + (t_r - t_u) * s_kalt + (t_o - t_r) * s_ueb
    return ohne_kern.where(s_kern < 1e-3, t_o), mittel


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
    Verlustrate und Übergangszone gelten dann für die Untergrenze des Segments (vorsichtig).

    ``ts`` braucht: last_gesamt [MW], T_a [degC], COP_luft, P_solar [kW/m2], strompreis [EUR/MWh].
    """
    import pypsa

    n = pypsa.Network()
    n.set_snapshots(ts.index)
    n.add("Carrier", ["strom", "waerme"])
    for bus, car in [
        ("netz", "strom"),
        ("elec", "strom"),
        ("solar", "waerme"),
        ("wp", "waerme"),
        ("waerme", "waerme"),
    ]:
        n.add("Bus", bus, carrier=car)

    zins, T = cfg.get("oekonomie.zins"), cfg.get("oekonomie.betrachtungszeitraum")
    f_strom = economics.preisdynamik(zins, T, cfg.get("oekonomie.preisaenderung.strom"))
    eps = cfg.get("solver.tie_breaker")

    # Strom: Arbeitspreis je MWh; Leistungspreis je kW höchster Bezug (= gebaute Anschlussleistung)
    n.add(
        "Generator",
        "netz_strom",
        bus="netz",
        carrier="strom",
        p_nom=1e3,
        marginal_cost=ts["strompreis"] * f_strom,
    )
    n.add(
        "Link",
        "netzanschluss",
        bus0="netz",
        bus1="elec",
        carrier="strom",
        p_nom_extendable=True,
        capital_cost=cfg.get("strom.leistungspreis") * 1000.0 * f_strom,
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

    # Speicher in drei Teilen: heiß (Kern), Übergangszone, kalt
    mit_speicher = V_m3 is None or V_m3 > 0
    if mit_speicher:
        kap = mwh_je_m3(cfg)
        f = anteil_heiss(cfg)
        if V_m3 is None:
            if segment is None:
                raise ValueError("Speicher optimieren braucht ein Kostensegment (segment=...)")
            v_von, v_bis, steigung, fix = segment
            # vorsichtig: Werte des kleinsten Volumens im Segment (erstes Segment: Mitte)
            v_bezug = v_von if v_von > 0 else v_bis / 2.0
        else:
            v_von = v_bis = v_bezug = V_m3
            steigung, fix = economics.ptes_invest(cfg, V_m3) / V_m3, 0.0
        s = anteil_uebergang(cfg, v_bezug)
        verlust = verlustrate(cfg, v_bezug)
        n.meta = {
            **dict(getattr(n, "meta", {}) or {}),
            "speicher_steigung": steigung,
            "speicher_fix": fix,
            "uebergang_anteil": s,
            "verlustrate": verlust,
        }
        v_fix = V_m3 or 0.0
        # Kosten nur am Kern (V = E_Kern / (f * (1 - s) * kap)); die anderen Teile folgen per Constraint
        kosten_kern = annualisiert(cfg, "ptes", steigung) / (kap * f * (1.0 - s))
        teile = [
            ("ptes_heiss", "heiss", f * (1.0 - s), kosten_kern),
            ("ptes_kalt", "kalt", 1.0 - f, 0.0),
        ]
        if s > 0:
            teile.append(("ptes_ueb", "ueb", f * s, 0.0))
        for name, bus, anteil, kosten in teile:
            n.add("Bus", bus, carrier="waerme")
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
                capital_cost=kosten,
            )
        # Laden: kalt = Wasser von T_unten auf Rücklauf, heiß = von Rücklauf auf T_oben. Beim Einschichten
        # vermischt sich ein fester Anteil mit der Übergangszone (einschicht_anteil).
        # Tie-Breaker: Laden minimal teurer als Direktnutzung (docs E16)
        m = cfg.get("ptes.einschicht_anteil") if s > 0 else 0.0
        heiss_ziel = {"bus1": "heiss", "efficiency": 1.0 - m}
        if m > 0:
            heiss_ziel.update(bus2="ueb", efficiency2=m)
        lade_quellen = [("laden_heiss", "solar", eps)]
        if cfg.get("ptes.laden_aus_netz"):
            # WP/PtH dürfen den Speicher laden (für zeitvariable Strompreise, docs E29/E39).
            # Doppelter Tie-Breaker: Solarwärme nimmt den direkten Weg (laden_heiss), nicht den über das Netz.
            lade_quellen.append(("laden_netz", "waerme", 2 * eps))
        for name, quelle, kosten in lade_quellen:
            n.add(
                "Link",
                name,
                bus0=quelle,
                carrier="waerme",
                p_nom=1e3,
                marginal_cost=kosten,
                **heiss_ziel,
            )
        n.add(
            "Link",
            "laden_kalt",
            bus0="solar",
            bus1="kalt",
            carrier="waerme",
            p_nom=1e3,
            marginal_cost=eps,
        )
        n.add("Link", "entladen_direkt", bus0="heiss", bus1="waerme", carrier="waerme", p_nom=1e3)
        if s > 0:
            # Mischen ohne Energieverlust: heißes Wasser wird Mischwasser, Mischwasser kühlt unter Rücklauf
            n.add("Link", "abbau", bus0="heiss", bus1="ueb", carrier="waerme", p_nom=1e3)
            n.add("Link", "umlagern", bus0="ueb", bus1="kalt", carrier="waerme", p_nom=1e3)
            if vorwaerm_verhaeltnis(cfg) > 0:
                n.add("Link", "vorwaermen", bus0="ueb", bus1="waerme", carrier="waerme", p_nom=1e3)

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
