"""Mini-Netz 48 h mit synthetischen Zeitreihen (BRF §5 M2/M3, §10.4): Bilanzen und Constraints.

Synthetische Werte sind Testwerte, keine Modellannahmen. Laufen ohne Rohdaten.
"""

import numpy as np
import pandas as pd
import pytest

from serts import economics, flaeche, kpi, network

pytestmark = pytest.mark.solver


def synth_ts(stunden: int = 48) -> pd.DataFrame:
    idx = pd.date_range("2022-06-01", periods=stunden, freq="h")
    sonne = np.clip(np.sin(2 * np.pi * (idx.hour - 6) / 24), 0, None)
    return pd.DataFrame(
        {
            "T_a": np.where(idx.hour < 6, -1.0, 8.0),  # einige Froststunden
            "last_gesamt": 0.5 + 0.2 * np.cos(2 * np.pi * idx.hour / 24),
            "last_netzverlust": 0.05,
            "COP_luft": 2.8,
            "p_max_pu_luft": 1.0,
            "P_hi": 0.5 * sonne,
            "P_lo": 0.7 * sonne,
            "strompreis": 300.0,
        },
        index=idx,
    )


@pytest.fixture(scope="module")
def ts():
    return synth_ts()


def _loese(cfg, ts, A, V):
    n = network.build_network(cfg, ts, A, V)
    network.optimize(n, cfg, ts)
    return n


@pytest.fixture(scope="module")
def netz_mit_speicher(cfg, ts):
    return _loese(cfg, ts, A=2000.0, V=3000.0)


def test_m2_ohne_speicher_energiebilanz(cfg, ts):
    n = _loese(cfg, ts, A=2000.0, V=0.0)
    p0 = n.links_t.p0
    zufuhr_stadt = p0["transmission"] * (1 - cfg.get("netz.TL_verlust")) + p0["pth"] * cfg.get(
        "pth.eta"
    )
    np.testing.assert_allclose(zufuhr_stadt.sum(), ts["last_gesamt"].sum(), rtol=1e-3)
    # heat_plant: Solar direkt + WP = Transmission + Frostschutz
    frost = n.loads_t.p_set["frostschutz"].sum() if "frostschutz" in n.loads_t.p_set else 0.0
    zu = p0["solar_direkt"].sum() + p0["hp_out"].sum()
    np.testing.assert_allclose(zu, p0["transmission"].sum() + frost, rtol=1e-3)


def test_m3_volumensumme_und_verluste(cfg, ts, netz_mit_speicher):
    n = netz_mit_speicher
    e = n.stores_t.e
    np.testing.assert_allclose(
        e[["V85", "V45", "V10"]].sum(axis=1) * network.VOL, 3000.0, atol=1e-3
    )
    lam = cfg.get("ptes.verlustrate")
    np.testing.assert_allclose(n.links_t.p0["verlust_oben"], lam * e["V85"], atol=1e-6)
    np.testing.assert_allclose(n.links_t.p0["verlust_mitte"], lam * e["V45"], atol=1e-6)


def test_m3_speicherbilanz_geschlossen(cfg, ts, netz_mit_speicher):
    k, _ = kpi.auswerten(netz_mit_speicher, cfg, ts)
    assert abs(k["speicher_bilanzfehler_MWh"]) < 1e-3 * max(k["Q_laden_MWh"], 1.0)
    assert k["volumensumme_maxfehler_m3"] < 1e-3


def test_kollektorflaeche_gemeinsam(ts, netz_mit_speicher):
    n = netz_mit_speicher
    A = 2000.0 * 1e-3
    g = n.generators_t.p
    m = (ts["P_hi"] > 0) & (ts["P_lo"] > 0)
    belegt = g["sol_hi"][m] / (A * ts["P_hi"][m]) + g["sol_lo"][m] / (A * ts["P_lo"][m])
    assert (belegt <= 1 + 1e-6).all()


def test_wp_kapazitaet_je_quelle(cfg, ts, netz_mit_speicher):
    n = netz_mit_speicher
    P = n.links.at["hp_out", "p_nom_opt"]
    p0 = n.links_t.p0
    assert (ts["COP_luft"] * p0["hp_air"] <= ts["p_max_pu_luft"] * P + 1e-6).all()
    cop_p, pu_p = cfg.get("waermepumpe.COP_ptes"), cfg.get("waermepumpe.p_max_pu_ptes")
    assert (cop_p * p0["hp_ptes"] <= pu_p * P + 1e-6).all()


def test_pth_redundanz(cfg, ts, netz_mit_speicher):
    P = netz_mit_speicher.links.at["pth", "p_nom_opt"] * cfg.get("pth.eta")
    assert P >= cfg.get("pth.redundanz") * ts["last_gesamt"].max() - 1e-6


def test_preisdynamik():
    assert economics.preisdynamik(0.05, 20, 0.0) == pytest.approx(1.0)
    # r = i: b = T/(1+i) -> a*b = 0,080243 * 20 / 1,05 = 1,5284
    assert economics.preisdynamik(0.05, 20, 0.05) == pytest.approx(1.5284, abs=1e-3)
    assert economics.preisdynamik(0.05, 20, 0.02) > 1.0


def test_ptes_kosten_und_geometrie(cfg):
    # bei V_ref: c_ref * Preisindex
    inv = economics.ptes_invest(cfg, 60_000)
    assert inv == pytest.approx(38.3 * 1.5 * 60_000)
    assert economics.ptes_invest(cfg, 10_000) / 10_000 > inv / 60_000  # degressiv
    geo = flaeche.ptes_geometrie(cfg, 60_000)
    assert geo["ptes_a_oben_m"] == pytest.approx(90.0)
    assert geo["ptes_grundflaeche_m2"] == pytest.approx((90 + 10) ** 2)
