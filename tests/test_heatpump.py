"""COP-Prüfwerte aus BRF §3.4 und SCH D2 (Abweichung > 10 % deutet auf Fehler °C/K/Mittelung)."""

import numpy as np
import pandas as pd
import pytest

from serts.heatpump import cop_lorenz, cop_luft, p_max_pu_luft, tlog


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


def test_cop_luft_mit_abtau(cfg):
    T = pd.Series([-5.0, 4.9, 5.0, 10.0])
    cop = cop_luft(cfg, T)
    ref = cop_lorenz(cfg.get("netz.T_RL"), cfg.get("netz.T_VL"), T, T - 5, eta_g=0.5, approach=3)
    np.testing.assert_allclose(cop.to_numpy(), ref * np.array([0.95, 0.95, 1.0, 1.0]))


def test_p_max_pu_luft(cfg):
    T = pd.Series([-20.0, -7.0, -4.0, -1.0, 10.0])
    pu = p_max_pu_luft(cfg, T).to_numpy()
    # 1,0 ab -1 degC, linear auf 0,8 bei -7 degC, darunter konstant 0,8 (Luft-WP dort ohnehin aus)
    np.testing.assert_allclose(pu, [0.8, 0.8, 0.9, 1.0, 1.0])
