"""VDI 2067-1: Ersatzbeschaffung und Restwert im Betrachtungszeitraum (Handrechnung)."""

import pytest

from serts.economics import (
    annuitaetenfaktor,
    jahreskosten,
    kapitalfaktor_vdi,
    kapitalkosten_jahr,
    netzkosten,
)
from serts.prices import strompreis

A20 = annuitaetenfaktor(0.05, 20)  # 0,080243


def test_lebensdauer_gleich_zeitraum():
    assert kapitalfaktor_vdi(0.05, 20, 20) == pytest.approx(A20)


def test_restwert_bei_laengerer_lebensdauer():
    # T_N = 25 > T = 20: kein Ersatz, Restwert 5/25 = 0,2, abgezinst 1/1,05^20 = 0,37689
    assert kapitalfaktor_vdi(0.05, 20, 25) == pytest.approx((1 - 0.2 * 0.37689) * A20, rel=1e-4)


def test_ersatz_ohne_restwert():
    # T_N = 10: Ersatz im Jahr 10 (1/1,05^10 = 0,61391), Restwert 0
    assert kapitalfaktor_vdi(0.05, 20, 10) == pytest.approx((1 + 0.61391) * A20, rel=1e-4)


def test_ersatz_mit_restwert():
    # T_N = 15: Ersatz im Jahr 15 (0,48102), Restwert (2*15-20)/15 = 2/3, abgezinst 0,37689
    erwartet = (1 + 0.48102 - 2 / 3 * 0.37689) * A20
    assert kapitalfaktor_vdi(0.05, 20, 15) == pytest.approx(erwartet, rel=1e-4)


def test_betriebskosten_und_foerderung():
    k = kapitalkosten_jahr(1000.0, 0.05, 20, om_fix=0.02, foerderquote=0.4, T=20)
    assert k == pytest.approx(1000 * 0.6 * A20 + 20.0)


def test_netzkosten(cfg):
    nk = netzkosten(cfg)
    s = cfg.get("netz.anteil_strasse")
    soll = cfg.get("netz.trassenlaenge") * (
        s * cfg.get("netz.kosten_trasse_strasse") + (1 - s) * cfg.get("netz.kosten_trasse_gruen")
    )
    assert nk["netz_invest_trasse_EUR"] == pytest.approx(soll)
    assert nk["kosten_a_netz_system"] > 0


def test_nebenkosten_schlagen_auf_jahreskosten_auf(cfg):
    ohne = jahreskosten(cfg.variante("oekonomie.nebenkosten", 0.0), "waermepumpe", 1000.0)
    mit = jahreskosten(cfg, "waermepumpe", 1000.0)
    assert mit == pytest.approx(ohne * 1.10)


def test_foerderung_nur_fuer_foerderfaehige_komponenten(cfg):
    gef = cfg.variante("oekonomie.foerderquote", 0.4)
    # WP förderfähig -> billiger; PtH (Annahme: nicht förderfähig) -> unverändert
    assert jahreskosten(gef, "waermepumpe", 1000.0) < jahreskosten(cfg, "waermepumpe", 1000.0)
    assert jahreskosten(gef, "pth", 1000.0) == pytest.approx(jahreskosten(cfg, "pth", 1000.0))


def test_netzkosten_getrennt(cfg):
    nk = netzkosten(cfg)
    assert nk["kosten_a_netz_system"] == pytest.approx(
        nk["kosten_a_netz_trasse"] + nk["kosten_a_netz_hausanschluss"]
    )


def test_strompreis_komponenten(cfg):
    import pandas as pd

    idx = pd.date_range("2022-01-01", periods=3, freq="h")
    p = strompreis(cfg.variante("strom.tarif", "fest"), idx)
    assert (p == cfg.get("strom.preis_fest")).all()
    assert cfg.get("strom.netzentgelt") + cfg.get("strom.abgaben") < cfg.get("strom.preis_fest")
