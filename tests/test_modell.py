"""Mini-Netz 48 h mit synthetischen Zeitreihen: Bilanzen und die zwei Zusatzbedingungen.

Synthetische Werte sind Testwerte, keine Modellannahmen. Laufen ohne Rohdaten.
"""

import numpy as np
import pandas as pd
import pytest

from serts import kpi, network
from serts.constraints import direktanteil_max

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
    network.optimize(n, cfg)
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
    e = netz_fest.stores_t.e["ptes"]
    zu = p0["laden"].sum()
    ab = p0["entladen_direkt"].sum() + p0["hp_speicher"].sum() * (
        cfg.get("waermepumpe.COP_ptes") - 1
    )
    # PyPSA: Verlust je Stunde = standing_loss * Inhalt der Vorstunde (zyklisch)
    verlust = (cfg.get("ptes.verlustrate") * e.shift(1, fill_value=e.iloc[-1])).sum()
    assert zu - ab - verlust == pytest.approx(0.0, abs=1e-3 * max(zu, 1.0))


def test_direktanteil_eingehalten(cfg, ts, netz_fest):
    p0 = netz_fest.links_t.p0
    direkt = p0["entladen_direkt"].sum()
    quelle = p0["hp_speicher"].sum() * (cfg.get("waermepumpe.COP_ptes") - 1)
    # absolut prüfen (Verhältnis ist bei fast leerem Speicher numerisch instabil)
    assert direkt <= direktanteil_max(cfg) * (direkt + quelle) + 1e-4


def test_luft_wp_aus_unter_tmin(cfg, ts, netz_fest):
    kalt = ts["T_a"] < cfg.get("waermepumpe.T_min_luft")
    assert (netz_fest.links_t.p0["hp_luft"][kalt] <= 1e-6).all()


def test_pth_redundanz(cfg, ts, netz_fest):
    P_th = netz_fest.links.at["pth", "p_nom_opt"] * cfg.get("pth.eta")
    assert P_th >= cfg.get("pth.redundanz") * ts["last_gesamt"].max() - 1e-6


def test_flaeche_begrenzt_optimierte_groessen(cfg, ts):
    n = _loese(cfg, ts)  # A und V optimiert
    k, _ = kpi.auswerten(n, cfg, ts)
    assert k["flaeche_m2"] <= cfg.get("standort.flaeche_verfuegbar") * (1 + 1e-6)


def test_ohne_speicher(cfg, ts):
    n = _loese(cfg, ts, A=1000.0, V=0.0)
    assert "ptes" not in n.stores.index
    k, _ = kpi.auswerten(n, cfg, ts)
    assert k["V_m3"] == 0.0


def test_mwh_je_m3_und_direktanteil(cfg):
    # 1,163e-3 * (85 - 10) = 0,0872 MWh/m3 -> 60.000 m3 ≈ 5.234 MWh (BRF §3.2)
    assert network.mwh_je_m3(cfg) * 60_000 == pytest.approx(5233.5, abs=1)
    assert direktanteil_max(cfg) == pytest.approx(40 / 75)
