import pandas as pd
import pytest

from serts import plots
from serts.tornado import varianten


def test_variante_aendert_nur_kopie(cfg):
    c2 = cfg.variante("ptes.kosten_faktor", 1.3)
    assert c2.get("ptes.kosten_faktor") == 1.3
    assert cfg.get("ptes.kosten_faktor") == 1.0


def test_variante_nur_fuer_parameter(cfg):
    with pytest.raises(KeyError):
        cfg.variante("ptes", 1)


def test_varianten_aus_sens(cfg):
    v = varianten(cfg)
    assert ("ptes.kosten_faktor", 0.7) in v and ("ptes.kosten_faktor", 1.3) in v
    assert ("kollektor.strahlung_skalierung", 0.9) in v
    for pfad in cfg.get("tornado.parameter"):
        cfg.node(pfad)  # existiert


def test_tornado_plot(tmp_path):
    df = pd.DataFrame(
        [
            {
                "parameter": "basis",
                "wert": None,
                "basiswert": None,
                "lcoh": 130.0,
                "gas_lcoh": 165.0,
            },
            {"parameter": "a", "wert": 1, "basiswert": 2, "lcoh": 120.0, "gas_lcoh": 165.0},
            {"parameter": "a", "wert": 3, "basiswert": 2, "lcoh": 140.0, "gas_lcoh": 165.0},
            {"parameter": "b", "wert": 0.5, "basiswert": 1, "lcoh": 135.0, "gas_lcoh": 165.0},
        ]
    )
    out = plots.tornado(df, "lcoh", "LCOH", tmp_path / "t.png")
    assert out.exists()


def test_varianten_nur_ausgewaehlte_parameter(cfg):
    v = varianten(cfg, nur=["netz.T_VL", "netz.T_VL_min"])
    assert v == [("netz.T_VL", w) for w in cfg.node("netz.T_VL")["sens"]] + [
        ("netz.T_VL_min", w) for w in cfg.node("netz.T_VL_min")["sens"]
    ]
