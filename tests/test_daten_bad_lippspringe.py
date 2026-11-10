"""Plausibilität der Rohdaten Bad Lippspringe (Kontrollwerte aus config/base.yaml)."""

import pytest

from serts import demand
from serts.sources import dwd, netzberechnung


@pytest.fixture(scope="module")
def last(netzberechnung_xlsx):
    return netzberechnung.read_lastgang(netzberechnung_xlsx)


def test_lastgang_form(last):
    assert len(last) == 8760
    assert str(last.index[0]) == "2022-01-01 00:00:00"
    assert (last >= 0).all().all()


def test_lastgang_kontrollwerte(last, cfg):
    kz = netzberechnung.kennzahlen(last)
    assert kz["Q_gebaeude_MWh"] == pytest.approx(cfg.get("last.Q_gebaeude"), abs=1)
    assert kz["Q_verlust_MWh"] == pytest.approx(cfg.get("last.Q_netzverlust"), abs=1)
    assert kz["P_max_MW"] == pytest.approx(cfg.get("last.P_max_kontrolle"), abs=1e-3)


@pytest.mark.parametrize("netz", ["klein", "gross"])
def test_lastgang_kontrollwerte_je_netz(netz):
    """Jedes Netz: Kontrollwerte der Config passen zur eigenen Lastgang-Datei (data/raw)."""
    from serts.config import load_config
    from serts.paths import DATA_RAW

    c = load_config(netz=netz)
    datei = DATA_RAW / c.get("last.datei")
    if not datei.exists():
        pytest.skip(f"Rohdatei fehlt ({datei.name}) -> `uv run serts import-raw`")
    kz = netzberechnung.kennzahlen(netzberechnung.read_lastgang(datei))
    assert kz["Q_gebaeude_MWh"] == pytest.approx(c.get("last.Q_gebaeude"), abs=1)
    assert kz["Q_verlust_MWh"] == pytest.approx(c.get("last.Q_netzverlust"), abs=1)
    assert kz["P_max_MW"] == pytest.approx(c.get("last.P_max_kontrolle"), abs=1e-3)


def test_summenspalten_konsistent(last):
    typen = last[netzberechnung.TYPEN].sum(axis=1)
    assert (typen - last["gebaeude"]).abs().max() < 0.005  # Rundung auf 3 Nachkommastellen
    assert (last["gebaeude"] + last["verlust"] - last["gesamt"]).abs().max() < 0.005


def test_waermebedarf_ankerkunde(cfg, last):
    from serts.config import load_config

    basis = demand.waermebedarf(cfg, last)
    assert basis["ankerkunde"].sum() == 0
    mit = demand.waermebedarf(load_config("ankerkunde_20"), last)
    assert mit["ankerkunde"].sum() == pytest.approx(0.2 * basis["gebaeude"].sum())


def test_dwd_temperatur_2022(dwd_tu, last):
    t = dwd.lufttemperatur(dwd_tu, 2022)
    assert len(t) == 8760
    assert 8.0 < t.mean() < 13.0  # Jahresmittel NRW-Tiefland
    t.index = t.index.tz_localize(None)
    r = t.resample("D").mean().corr(last["gebaeude"].resample("D").mean())
    assert r < -0.8, f"Last folgt Temperatur 2022 kaum (r={r:.2f}) -> Wetterjahr prüfen"
