import numpy as np
import pandas as pd

from serts.sources.dwd import fuelle_tagesgang


def test_tagesgang_fuellung_rekonstruiert_sinus():
    idx = pd.date_range("2022-05-01", periods=24 * 30, freq="h", tz="UTC")
    wahr = pd.Series(
        15 + 5 * np.sin(2 * np.pi * idx.hour / 24) + np.arange(len(idx)) * 0.01, index=idx
    )
    mit_luecke = wahr.copy()
    mit_luecke.iloc[300:368] = np.nan  # 68 h wie 2022
    gefuellt = fuelle_tagesgang(mit_luecke)
    assert not gefuellt.isna().any()
    assert (gefuellt - wahr).abs().max() < 0.5
    pd.testing.assert_series_equal(gefuellt.iloc[:300], wahr.iloc[:300])
