"""Speicherkennzahlen gegen Solites 2019 (Dronninglund) und Annuitätenrechnung."""

from pathlib import Path

import pandas as pd
import pytest

from serts.economics import annuitaetenfaktor, co2_vermeidungskosten, lcoh
from serts.kpi import Speicherbilanz, kapazitaet_MWh, solaranteil
from serts.paths import DATA_REFERENCE


@pytest.fixture(scope="module")
def drl() -> pd.DataFrame:
    return pd.read_csv(
        Path(DATA_REFERENCE) / "dronninglund_solites2019_jahr.csv",
        comment="#",
        index_col="kennzahl",
    )


@pytest.mark.parametrize("jahr", ["2015", "2016", "2017"])
def test_speicherdefinitionen_reproduzieren_solites(drl, jahr):
    b = Speicherbilanz(
        q_in=drl.loc["beladung_ptes", jahr],
        q_out=drl.loc["entladung_ptes", jahr],
        dq=drl.loc["dq_speicher", jahr],
    )
    assert b.wirkungsgrad * 100 == pytest.approx(drl.loc["speicherwirkungsgrad", jahr], abs=0.6)
    assert b.verluste == pytest.approx(drl.loc["verluste_ptes", jahr], abs=2)


def test_kapazitaet_dronninglund():
    # BRF §3.2: 60.000 m3 * 75 K * c = 5.234 MWh (gemessen 5.200-5.500)
    assert kapazitaet_MWh(60_000, 1.163e-3, 85, 10) == pytest.approx(5233.5, abs=1)


def test_solaranteil_summe():
    s = solaranteil(10, 20, 5, 100)
    assert s["solar_gesamt"] == pytest.approx(0.35)


def test_annuitaetenfaktor():
    assert annuitaetenfaktor(0.0, 20) == pytest.approx(0.05)
    # 5 %, 20 a: 0,080243 (Tabellenwert)
    assert annuitaetenfaktor(0.05, 20) == pytest.approx(0.080243, abs=1e-6)


def test_lcoh_und_vermeidungskosten():
    assert lcoh(100_000, 50_000, 5_000) == pytest.approx(30.0)
    assert co2_vermeidungskosten(120, 100, 0.05, 0.25) == pytest.approx(100.0)
