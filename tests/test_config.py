import pytest

from serts.config import (
    ConfigError,
    OffenerParameter,
    deep_merge,
    load_config,
    validate,
)
from serts.paths import SCENARIO_DIR


def test_base_ist_gueltig(cfg):
    assert validate(cfg.tree) == []


def test_offener_parameter_bricht_ab(cfg):
    assert "strom.vertriebsmarge" in cfg.offene()
    with pytest.raises(OffenerParameter):
        cfg.get("strom.vertriebsmarge")
    with pytest.raises(OffenerParameter, match="strom.vertriebsmarge"):
        cfg.require(["netz.T_VL", "strom.vertriebsmarge"])


def test_get_liefert_wert(cfg):
    assert cfg.get("netz.T_VL") == 80
    assert cfg.get("ptes.c_wasser") == pytest.approx(1.163e-3)


@pytest.mark.parametrize("szenario", sorted(p.stem for p in SCENARIO_DIR.glob("*.yaml")))
def test_alle_szenarien_laden(szenario):
    load_config(szenario)


def test_szenario_ueberschreibt_skalar():
    c = load_config("rl_40")
    assert c.get("netz.T_RL") == 40
    assert c.get("netz.T_VL") == 80  # unverändert


def test_unbekannter_schluessel_im_szenario():
    base = {"netz": {"T_VL": {"wert": 75, "einheit": "degC", "status": "vorgabe", "quelle": "x"}}}
    with pytest.raises(ConfigError, match="unbekannten Schlüssel"):
        deep_merge(base, {"netz": {"T_VLL": 70}})


def test_validierung_findet_fehler():
    tree = {
        "a": {"wert": None, "einheit": "-", "status": "annahme", "quelle": "x"},
        "b": {"wert": 1, "einheit": "-", "status": "belegt", "quelle": ""},
        "c": {"wert": 1, "einheit": "-", "status": "geraten", "quelle": "x"},
    }
    errs = validate(tree)
    assert len(errs) == 3
