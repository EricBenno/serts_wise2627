"""Mini-Netz 48 h mit synthetischen Zeitreihen: Bilanzen und die Zusatzbedingungen.

Synthetische Werte sind Testwerte, keine Modellannahmen. Laufen ohne Rohdaten.
"""

import numpy as np
import pandas as pd
import pytest

from serts import economics, kpi, network
from serts.run import loese

pytestmark = pytest.mark.solver


def synth_ts(stunden: int = 48) -> pd.DataFrame:
    idx = pd.date_range("2022-06-01", periods=stunden, freq="h")
    sonne = np.clip(np.sin(2 * np.pi * (idx.hour - 6) / 24), 0, None)
    return pd.DataFrame(
        {
            "T_a": np.where(idx.hour < 6, -10.0, 8.0),  # nachts unter T_min -> Luft-WP aus
            "last_gesamt": 0.5 + 0.2 * np.cos(2 * np.pi * idx.hour / 24),
            "last_netzverlust": 0.05,
            "COP_luft": 2.8,
            "p_max_pu_luft": np.where(idx.hour < 12, 0.8, 1.0),
            "P_solar": 0.6 * sonne,
            "strompreis": 300.0,
        },
        index=idx,
    )


@pytest.fixture(scope="module")
def ts():
    return synth_ts()


def _loese(cfg, ts, A=None, V=None):
    n = network.build_network(cfg, ts, A, V)
    network.optimize(n, cfg, ts)
    return n


@pytest.fixture(scope="module")
def netz_fest(cfg, ts):
    """Feste Größen, damit Solar und Speicher sicher genutzt werden."""
    return _loese(cfg, ts, A=3000.0, V=3000.0)


def test_energiebilanz_waermeknoten(cfg, ts, netz_fest):
    p0 = netz_fest.links_t.p0
    zu = p0["solar_direkt"] + p0["entladen_direkt"] + p0["wp_out"] + p0["pth"] * cfg.get("pth.eta")
    zu = zu + p0["vorwaermen"]
    np.testing.assert_allclose(zu.sum(), ts["last_gesamt"].sum(), rtol=1e-3)


def test_speicherbilanz_geschlossen(cfg, ts, netz_fest):
    p0 = netz_fest.links_t.p0
    e = netz_fest.stores_t.e
    zu = p0["laden_heiss"].sum() + p0["laden_kalt"].sum()
    ab = (
        p0["entladen_direkt"].sum()
        + p0["vorwaermen"].sum()
        + p0["hp_speicher"].sum() * (cfg.get("waermepumpe.COP_ptes") - 1)
    )
    # PyPSA: Verlust je Stunde = standing_loss * Inhalt der Vorstunde (zyklisch), je Speicherteil
    lam = netz_fest.meta["verlustrate"]
    assert lam == pytest.approx(network.verlustrate(cfg, 3000.0))
    verlust = sum((lam * e[n].shift(1, fill_value=e[n].iloc[-1])).sum() for n in e.columns)
    assert zu - ab - verlust == pytest.approx(0.0, abs=1e-3 * max(zu, 1.0))


def _mit_startinhalt(n, kern: float, ueb: float, kalt: float):
    """Startfüllstände (0..1) erzwingen, nicht zyklisch."""
    for name, anteil in (("ptes_heiss", kern), ("ptes_ueb", ueb), ("ptes_kalt", kalt)):
        n.stores.loc[name, "e_cyclic"] = False
        n.stores.loc[name, "e_initial"] = anteil * n.stores.at[name, "e_nom"]


def test_sommerzyklus_ohne_waermepumpe(cfg, ts):
    """Kalter Teil voll (Speicher unten auf Rücklauftemperatur): der heiße Teil lädt und entlädt ohne WP.

    Früher füllte ``laden`` heiß und kalt im festen Verhältnis -> bei vollem kalten Teil kein Nachladen (E39).
    """
    n = network.build_network(cfg, ts, A_m2=3000.0, V_m3=3000.0)
    _mit_startinhalt(n, kern=0.0, ueb=1.0, kalt=1.0)
    n.links.loc["hp_speicher", "p_nom"] = 0.0  # Speicher-WP aus
    network.optimize(n, cfg, ts)
    p0 = n.links_t.p0
    assert p0["laden_heiss"].sum() > 1.0
    assert p0["entladen_direkt"].sum() > 1.0


def test_speicherteile_wachsen_im_festen_verhaeltnis(cfg, ts):
    n = network.build_network(
        cfg, ts, None, None, segment=(0.0, 5000.0, 150.0, 0.0)
    )  # A und V optimiert
    network.optimize(n, cfg, ts)
    h = n.stores.at["ptes_heiss", "e_nom_opt"]
    f = network.anteil_heiss(cfg)
    s = n.meta["uebergang_anteil"]
    assert s == pytest.approx(network.anteil_uebergang(cfg, 2500.0))  # Segmentmitte
    assert n.stores.at["ptes_kalt", "e_nom_opt"] == pytest.approx(
        (1 - f) / (f * (1 - s)) * h, abs=1e-6
    )
    assert n.stores.at["ptes_ueb", "e_nom_opt"] == pytest.approx(s / (1 - s) * h, abs=1e-6)


def test_uebergangszone_und_verlust_haengen_von_der_groesse_ab(cfg):
    # bei V_ref (Dronninglund, 60.000 m3) die Config-Werte
    assert network.anteil_uebergang(cfg, 60_000) == pytest.approx(cfg.get("ptes.uebergang_ref"))
    assert network.verlustrate(cfg, 60_000) == pytest.approx(cfg.get("ptes.verlustrate"))
    # 8-mal kleiner -> halbe Tiefe, doppelte Oberfläche je m3 -> beides doppelt
    assert network.anteil_uebergang(cfg, 7_500) == pytest.approx(2 * 0.15, rel=1e-3)
    assert network.verlustrate(cfg, 7_500) == pytest.approx(2 * 4.0e-5, rel=1e-3)
    # sehr kleine Speicher: Obergrenze; Exponent 0 = größenunabhängig
    assert network.anteil_uebergang(cfg, 100) == pytest.approx(cfg.get("ptes.uebergang_max"))
    c0 = cfg.variante("ptes.groessen_exponent", 0.0)
    assert network.anteil_uebergang(c0, 1_000) == pytest.approx(0.15)
    assert network.verlustrate(c0, 1_000) == pytest.approx(4.0e-5)
    # kälteres Netz (VL 60): Direktentladung ab 65 °C -> nur die halbe Zone (45-65 von 45-85 °C) zählt
    assert network.anteil_uebergang(cfg.variante("netz.T_VL", 60), 60_000) == pytest.approx(0.075)


def test_speichertemperaturen_anzeige(cfg):
    # Füllstände (Kern, Übergangszone, kalt) -> Temperatur oben / Mittel; Anteil Übergangszone 0,3
    kern = pd.Series([0.0, 0.0, 0.0, 0.5, 1.0])
    ueb = pd.Series([0.0, 0.0, 0.5, 1.0, 1.0])
    kalt = pd.Series([0.0, 1.0, 1.0, 1.0, 1.0])
    oben, mittel = network.temperaturen_speicher(cfg, kern, ueb, kalt, 0.3)
    # leer 10 °C; nur kalter Teil voll -> 45 °C; halbe Übergangszone -> 65 °C; mit Kern immer 85 °C
    np.testing.assert_allclose(oben, [10.0, 45.0, 65.0, 85.0, 85.0])
    np.testing.assert_allclose(mittel, [10.0, 45.0, 45 + 40 * 0.15, 45 + 40 * 0.65, 85.0])


def test_schichtung_kern_uebergang_kalt(cfg, ts, netz_fest):
    """Füllstand Kern <= Übergangszone <= kalt in jeder Stunde (heißes Wasser liegt auf seiner Zone)."""
    e = netz_fest.stores_t.e
    E = netz_fest.stores.e_nom
    s = {n: e[n] / E[n] for n in ("ptes_heiss", "ptes_ueb", "ptes_kalt")}
    assert (s["ptes_ueb"] >= s["ptes_heiss"] - 1e-6).all()
    assert (s["ptes_kalt"] >= s["ptes_ueb"] - 1e-6).all()
    assert netz_fest.links_t.p0["entladen_direkt"].sum() > 0  # sonst prüft der Test nichts


def test_ohne_kern_keine_direktentladung(cfg, ts):
    """Kalter Teil voll, Übergangszone halb voll, kein Kern: nichts geht direkt ins Netz (kein Ballast)."""
    n = network.build_network(cfg, ts, A_m2=0.0, V_m3=3000.0)
    _mit_startinhalt(n, kern=0.0, ueb=0.5, kalt=1.0)
    network.optimize(n, cfg, ts)
    p0 = n.links_t.p0
    assert p0["entladen_direkt"].sum() <= 1e-6
    # die Wärme ist trotzdem nutzbar: Vorwärmen oder Speicher-WP
    assert p0["vorwaermen"].sum() + p0["hp_speicher"].sum() > 0


def test_vorwaermen_braucht_nachheizen(cfg, ts):
    n = network.build_network(cfg, ts, A_m2=0.0, V_m3=3000.0)
    _mit_startinhalt(n, kern=0.0, ueb=1.0, kalt=1.0)
    network.optimize(n, cfg, ts)
    p0 = n.links_t.p0
    k = network.vorwaerm_verhaeltnis(cfg)
    assert k == pytest.approx(0.75)  # 45 -> 60 °C aus dem Speicher, 60 -> 80 °C Nachheizung
    assert p0["vorwaermen"].sum() > 1.0
    nachheizen = p0["wp_out"] + p0["pth"] * cfg.get("pth.eta")
    assert (p0["vorwaermen"] <= k * nachheizen + 1e-6).all()
    # abgeschaltet: kein Link
    aus = network.build_network(cfg.variante("ptes.vorwaermen", False), ts, A_m2=0.0, V_m3=3000.0)
    assert "vorwaermen" not in aus.links.index


def test_ideale_schichtung_ohne_uebergangszone(cfg, ts):
    c = cfg.variante("ptes.uebergang_ref", 0.0)
    n = network.build_network(c, ts, A_m2=3000.0, V_m3=3000.0)
    assert "ptes_ueb" not in n.stores.index
    assert not {"umlagern", "abbau", "vorwaermen"} & set(n.links.index)
    network.optimize(n, c, ts)
    e, E = n.stores_t.e, n.stores.e_nom
    assert (e["ptes_kalt"] / E["ptes_kalt"] >= e["ptes_heiss"] / E["ptes_heiss"] - 1e-6).all()


def test_einschichtanteil_geht_in_die_uebergangszone(cfg, ts):
    c = cfg.variante("ptes.einschicht_anteil", 0.2)
    n = network.build_network(c, ts, A_m2=1000.0, V_m3=3000.0)
    assert n.links.at["laden_heiss", "efficiency"] == pytest.approx(0.8)
    assert n.links.at["laden_heiss", "bus2"] == "ueb"
    assert n.links.at["laden_heiss", "efficiency2"] == pytest.approx(0.2)


def test_laden_aus_netz_nur_auf_wunsch(cfg, ts):
    assert "laden_netz" not in network.build_network(cfg, ts, 1000.0, 3000.0).links.index
    n = network.build_network(cfg.variante("ptes.laden_aus_netz", True), ts, 1000.0, 3000.0)
    assert n.links.at["laden_netz", "bus0"] == "waerme"  # WP und PtH speisen in den Wärmeknoten
    assert n.links.at["laden_netz", "bus1"] == "heiss"


def test_leistungspreis_auf_hoechsten_strombezug(cfg, ts):
    c = cfg.variante("strom.leistungspreis", 100.0)
    n, k, r = loese(c, ts, A_m2=2000.0, V_m3=2000.0)
    # gebaute Anschlussleistung = höchster Bezug; Kosten = EUR/kW * kW
    assert n.links.at["netzanschluss", "p_nom_opt"] == pytest.approx(
        r["strom_netz"].max(), abs=1e-4
    )
    assert k["kosten_a_strom_leistung"] == pytest.approx(r["strom_netz"].max() * 1000 * 100.0)
    assert k["kosten_a_strom"] > k["kosten_a_strom_leistung"] > 0
    # ohne Leistungspreis ist die Spitze mindestens so hoch
    _, k0, r0 = loese(cfg.variante("strom.leistungspreis", 0.0), ts, A_m2=2000.0, V_m3=2000.0)
    assert k0["kosten_a_strom_leistung"] == 0.0
    assert r0["strom_netz"].max() >= r["strom_netz"].max() - 1e-6


def test_bew_ausweis(cfg, ts):
    n, k, _ = loese(cfg, ts, A_m2=2000.0, V_m3=2000.0)
    assert k["lcoh_bew"] < k["lcoh"]
    assert k["lcoh_inkl_netz_bew"] < k["lcoh_inkl_netz"]
    # Zuschuss = 40 % x (1 + Nebenkosten) x förderfähige Invests (Kollektor, PTES, WP, Trasse)
    q, nk = 0.4, 1.0 + cfg.get("oekonomie.nebenkosten")
    soll = (
        q
        * nk
        * (
            2000.0 * cfg.get("kollektor.kosten_spez")
            + economics.ptes_invest(cfg, 2000.0)
            + k["P_WP_MW"] * cfg.get("waermepumpe.kosten_spez")
            + k["netz_invest_trasse_EUR"]
        )
    )
    assert k["zuschuss_bew_EUR"] == pytest.approx(soll, rel=1e-6)


def test_luft_wp_leistung_sinkt_bei_kaelte(cfg, ts, netz_fest):
    P = netz_fest.links.at["wp_out", "p_nom_opt"]
    p0 = netz_fest.links_t.p0
    assert (ts["COP_luft"] * p0["hp_luft"] <= ts["p_max_pu_luft"] * P + 1e-6).all()


def test_luft_wp_leistung_auch_bei_fester_wp(cfg, ts):
    n = network.build_network(cfg, ts, A_m2=2000.0, V_m3=2000.0)
    n.links.loc["wp_out", ["p_nom", "p_nom_extendable"]] = [0.6, False]
    n.links.loc["pth", ["p_nom", "p_nom_extendable"]] = [1.6, False]
    network.optimize(n, cfg, ts)
    wp_waerme = ts["COP_luft"] * n.links_t.p0["hp_luft"]
    assert (wp_waerme <= ts["p_max_pu_luft"] * 0.6 + 1e-6).all()


def test_luft_wp_aus_unter_tmin(cfg, ts, netz_fest):
    kalt = ts["T_a"] < cfg.get("waermepumpe.T_min_luft")
    assert (netz_fest.links_t.p0["hp_luft"][kalt] <= 1e-6).all()


def test_pth_redundanz(cfg, ts, netz_fest):
    P_th = netz_fest.links.at["pth", "p_nom_opt"] * cfg.get("pth.eta")
    assert P_th >= cfg.get("pth.redundanz") * ts["last_gesamt"].max() - 1e-6


def test_flaeche_begrenzt_optimierte_groessen(cfg, ts):
    _, k, _ = loese(cfg, ts)  # A und V optimiert, je Kostensegment ein Lauf
    assert k["flaeche_m2"] <= cfg.get("standort.flaeche_verfuegbar") * (1 + 1e-6)
    assert len(k["segmente_vergleich"]) == len(cfg.get("ptes.segmente_m3")) - 1
    # Kosten des gewählten Volumens liegen auf der (Sehnen-)Kostenkurve des Segments
    if k["V_m3"] > 1.0:  # im 48-h-Test kann der Speicher unrentabel (V ≈ 0) sein
        assert k["speicher_preis_EUR_m3"] * k["V_m3"] == pytest.approx(
            economics.ptes_invest(cfg, k["V_m3"]), rel=0.06
        )


def test_speicherkosten_stetig_monoton_und_degressiv(cfg):
    vs = [500, 2500, 5000, 5001, 11999, 12000, 12001, 35000]
    invest = [economics.ptes_invest(cfg, v) for v in vs]
    assert invest == sorted(invest)  # mehr Volumen kostet nie weniger (kein Sprung nach unten)
    je_m3 = [economics.ptes_kosten_je_m3(cfg, v) for v in vs]
    assert je_m3 == sorted(je_m3, reverse=True)  # Skaleneffekt: je m3 immer günstiger
    # bei V_ref: c_ref * Preisindex (KWW Tab. 52: 1093,6 * V^0,7472 / V = 67,8 EUR/m3)
    assert economics.ptes_kosten_je_m3(cfg, 60_000) == pytest.approx(67.77 * 1.0)


def test_speicherkosten_passen_zu_kww_stuetzwerten(cfg):
    # KWW Tab. 52 (2026): 20.000 m3 = 90, 50.000 = 70, 100.000 = 60, 200.000 m3 = 50 EUR/m3
    kww = {20_000: 90, 50_000: 70, 100_000: 60, 200_000: 50}
    for v, soll in kww.items():
        assert economics.ptes_kosten_je_m3(cfg, v) == pytest.approx(soll, rel=0.05)


def test_segmente_sind_stetig(cfg):
    seg = economics.ptes_segmente(cfg)
    for (_, v1, s1, f1), (v0b, _, s2, f2) in zip(seg[:-1], seg[1:], strict=True):
        assert v1 == v0b
        assert s1 * v1 + f1 == pytest.approx(s2 * v0b + f2)  # gleiche Kosten an der Segmentgrenze
        assert s1 > s2  # Grenzkosten sinken (konkav)


def test_ohne_speicher(cfg, ts):
    n = _loese(cfg, ts, A=1000.0, V=0.0)
    assert "ptes_heiss" not in n.stores.index
    k, _ = kpi.auswerten(n, cfg, ts)
    assert k["V_m3"] == 0.0


def test_mwh_je_m3_und_anteil_heiss(cfg):
    # 1,163e-3 * (85 - 10) = 0,0872 MWh/m3 -> 60.000 m3 ≈ 5.234 MWh (BRF §3.2)
    assert network.mwh_je_m3(cfg) * 60_000 == pytest.approx(5233.5, abs=1)
    assert network.anteil_heiss(cfg) == pytest.approx(40 / 75)
