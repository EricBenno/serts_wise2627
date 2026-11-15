"""COP-Prüfwerte aus BRF §3.4 und SCH D2 (Abweichung > 10 % deutet auf Fehler °C/K/Mittelung)."""

import numpy as np
import pandas as pd
import pytest

from serts.heatpump import cop_kww, cop_lorenz, cop_luft, guetegrad_kww, p_max_pu_luft, tlog


def test_tlog_handrechnung():
    # (348,15 - 318,15) / ln(348,15/318,15) = 30 / 0,090111 = 332,92 K
    assert float(tlog(75, 45)) == pytest.approx(332.92, abs=0.01)
    assert float(tlog(20, 20)) == pytest.approx(293.15)


@pytest.mark.parametrize(
    "q_ein, q_aus, eta, soll",
    [
        (15, 10, 0.60, 3.8),  # BRF §3.4 Prüfwert 1 (Spreizung 5 K angenommen)
        (50, 40, 0.45, 7.3),  # BRF §3.4 Prüfwert 2 (Spreizung 10 K angenommen)
    ],
)
def test_pruefwerte_briefing(q_ein, q_aus, eta, soll):
    cop = float(cop_lorenz(45, 75, q_ein, q_aus, eta_g=eta, approach=3))
    assert cop == pytest.approx(soll, rel=0.02)


@pytest.mark.parametrize("t_luft, soll", [(-5, 2.3), (0, 2.5), (10, 2.9)])
def test_cop_luft_briefing(t_luft, soll):
    # BRF §3.4: Quelle T -> T-5 K, eta_G 0,5; Briefing-Werte gerundet -> Toleranz 5 %
    cop = float(cop_lorenz(45, 75, t_luft, t_luft - 5, eta_g=0.5, approach=3))
    assert cop == pytest.approx(soll, rel=0.05)


def test_cop_luft_kww(cfg):
    # KWW Tab. 24/25: JAZ 2,5 (70 °C, Gütegrad 46 %) und 1,8 (95 °C, 44 %) bei 7 °C Quelle
    assert float(cop_kww(70, 7, 0.46)) == pytest.approx(2.5, abs=0.01)
    assert float(cop_kww(95, 7, 0.44)) == pytest.approx(1.8, abs=0.05)
    # Basis: Vorlauf 80 °C -> Gütegrad 45,2 % -> COP 2,19 bei 7 °C
    assert guetegrad_kww(cfg) == pytest.approx(0.452)
    cop = cop_luft(cfg, pd.Series([7.0, -5.0]))
    np.testing.assert_allclose(cop, [2.187, 0.452 * 353.15 / 85], rtol=1e-3)


def test_cop_luft_lorenz_mit_abtau(cfg):
    c = cfg.variante("waermepumpe.cop_ansatz_luft", "lorenz")
    T = pd.Series([-5.0, 4.9, 5.0, 10.0])
    cop = cop_luft(c, T)
    ref = cop_lorenz(c.get("netz.T_RL"), c.get("netz.T_VL"), T, T - 5, eta_g=0.5, approach=3)
    np.testing.assert_allclose(cop.to_numpy(), ref * np.array([0.95, 0.95, 1.0, 1.0]))


def test_p_max_pu_luft(cfg):
    T = pd.Series([-20.0, -7.0, -4.0, -1.0, 10.0])
    pu = p_max_pu_luft(cfg, T).to_numpy()
    # 1,0 ab -1 degC, linear auf 0,8 bei -7 degC, darunter konstant 0,8 (Luft-WP dort ohnehin aus)
    np.testing.assert_allclose(pu, [0.8, 0.8, 0.9, 1.0, 1.0])


def test_vorlauf_konstant_und_gleitend(cfg):
    from serts.heatpump import vorlauf

    T_a = pd.Series([-15.0] * 48 + [2.5] * 48 + [20.0] * 48)
    # Basis: konstant netz.T_VL
    assert (vorlauf(cfg, T_a) == cfg.get("netz.T_VL")).all()
    # gleitend 80 -> 70 degC zwischen -10 und 15 degC (Mittel der letzten 24 h)
    c = cfg.variante("netz.T_VL_min", 70)
    vl = vorlauf(c, T_a)
    assert vl.iloc[47] == pytest.approx(80.0)
    assert vl.iloc[95] == pytest.approx(75.0)  # 2,5 degC = Mitte der Heizkurve
    assert vl.iloc[-1] == pytest.approx(70.0)
    # niedrigerer Vorlauf -> besserer COP, bei kaltem Wetter unverändert
    cop_fest, cop_gleit = cop_luft(cfg, T_a), cop_luft(c, T_a)
    assert cop_gleit.iloc[47] == pytest.approx(cop_fest.iloc[47])
    assert cop_gleit.iloc[-1] > cop_fest.iloc[-1] * 1.1
