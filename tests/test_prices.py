import numpy as np
import pandas as pd
import pytest

from serts import prices


def _csv(tmp_path, jahr: int):
    idx = pd.date_range(f"{jahr}-01-01", f"{jahr}-12-31 23:00", freq="h")
    df = pd.DataFrame({"zeit": idx, "preis": np.arange(len(idx), dtype=float)})
    p = tmp_path / f"day_ahead_{jahr}.csv"
    df.to_csv(p, index=False)
    return p, df


def test_reihe_aus_csv_schaltjahr_verwirft_29_februar(tmp_path):
    p, df = _csv(tmp_path, 2024)  # 8784 Stunden
    s = prices.reihe_aus_csv(p)
    assert len(s) == 8760
    # 29.02. (24 Stunden) fehlt: der Wert nach dem 28.02. 23:00 ist der vom 01.03. 00:00
    i = int(df.index[(df["zeit"] == "2024-03-01 00:00")][0])
    assert s.iloc[i - 24] == df["preis"].iloc[i]


def test_reihe_normales_jahr(tmp_path):
    p, df = _csv(tmp_path, 2023)
    s = prices.reihe_aus_csv(p)
    assert (s.to_numpy() == df["preis"].to_numpy()).all()


def test_strompreis_day_ahead_und_normierung(cfg, tmp_path, monkeypatch):
    p, df = _csv(tmp_path, 2023)
    monkeypatch.setattr(prices, "pfad_day_ahead", lambda jahr: p)
    idx = pd.date_range("2022-01-01", periods=8760, freq="h")
    c = cfg.variante("strom.tarif", "day_ahead").variante("strom.preisjahr", 2023)
    netz, abg = prices.netz_und_abgaben(c)
    marge = c.get("strom.vertriebsmarge")
    preis = prices.strompreis(c, idx)
    # absolut: Day-Ahead + Marge + Netzentgelt + Abgaben
    np.testing.assert_allclose(preis.to_numpy(), df["preis"].to_numpy() + marge + netz + abg)
    # normiert: gleicher Jahresmittelwert wie der feste Tarif, Profil bleibt proportional
    norm = prices.strompreis(c.variante("strom.day_ahead_normieren", True), idx)
    assert norm.mean() == pytest.approx(c.get("strom.preis_fest"))
    assert np.corrcoef(norm, preis)[0, 1] == pytest.approx(1.0)
