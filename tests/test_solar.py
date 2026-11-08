import numpy as np
import pytest

from serts.solar import spez_leistung, wirkungsgrad

# Testwerte, KEINE Modellannahmen (Kollektorkennwerte sind in base.yaml offen)
P = dict(eta0=0.8, a1=2.0, a2=0.01)


def test_wirkungsgrad_handrechnung():
    # G = 800, dT = 50: 0,8 - 2*50/800 - 0,01*2500/800 = 0,8 - 0,125 - 0,03125 = 0,64375
    assert float(wirkungsgrad(800, 70, 20, **P)) == pytest.approx(0.64375)


def test_wirkungsgrad_null_bei_nacht_und_negativ():
    eta = wirkungsgrad(np.array([0.0, 50.0]), 70, 0, **P)
    np.testing.assert_array_equal(eta, [0.0, 0.0])


def test_spez_leistung_einheit_kw_m2():
    p = float(spez_leistung(800, 70, 20, **P, feldverluste=0.1))
    assert p == pytest.approx(0.64375 * 800 * 0.9 / 1000)
    assert p < 1.0  # p_max_pu-Konvention
