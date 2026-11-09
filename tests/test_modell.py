"""Mini-Netz 48 h mit synthetischen Zeitreihen: Bilanzen und die zwei Zusatzbedingungen.

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
    np.testing.assert_allclose(zu.sum(), ts["last_gesamt"].sum(), rtol=1e-3)


def test_speicherbilanz_geschlossen(cfg, ts, netz_fest):
    p0 = netz_fest.links_t.p0
    e = netz_fest.stores_t.e
    zu = p0["laden"].sum()
    ab = p0["entladen_direkt"].sum() + p0["hp_speicher"].sum() * (
        cfg.get("waermepumpe.COP_ptes") - 1
    )
    # PyPSA: Verlust je Stunde = standing_loss * Inhalt der Vorstunde (zyklisch), je Speicherteil
    lam = cfg.get("ptes.verlustrate")
    verlust = sum(
        (lam * e[n].shift(1, fill_value=e[n].iloc[-1])).sum() for n in ("ptes_heiss", "ptes_kalt")
    )
    assert zu - ab - verlust == pytest.approx(0.0, abs=1e-3 * max(zu, 1.0))


def test_laden_fuellt_heiss_und_kalt_im_festen_verhaeltnis(cfg, ts, netz_fest):
    f = network.anteil_heiss(cfg)
    p0 = netz_fest.links_t.p0
    # 1 MWh Solarwärme -> f in den heißen, (1-f) in den kalten Teil (Link-Ausgänge)
    assert netz_fest.links.at["laden", "efficiency"] == pytest.approx(f)
    assert netz_fest.links.at["laden", "efficiency2"] == pytest.approx(1.0 - f)
    assert p0["laden"].sum() > 0  # der Test prüft nur sinnvoll, wenn geladen wird


def test_speicherteile_wachsen_im_festen_verhaeltnis(cfg, ts):
    n = network.build_network(
        cfg, ts, None, None, segment=(0.0, 5000.0, 150.0, 0.0)
    )  # A und V optimiert
    network.optimize(n, cfg, ts)
    h = n.stores.at["ptes_heiss", "e_nom_opt"]
    kalt = n.stores.at["ptes_kalt", "e_nom_opt"]
    f = network.anteil_heiss(cfg)
    assert kalt == pytest.approx((1 - f) / f * h, abs=1e-6)


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
    # bei V_ref: c_ref * Preisindex (38,3 * 1,5)
    assert economics.ptes_kosten_je_m3(cfg, 60_000) == pytest.approx(38.3 * 1.5)


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
