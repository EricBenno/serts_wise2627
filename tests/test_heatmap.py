"""Heatmap: Flächencheck und Grafiken (ohne Solver, synthetische Werte)."""

import numpy as np
import pandas as pd

from serts.heatmap import FELDER, _bild, _bild_alle, passt


def test_passt_flaeche(cfg):
    # 13.000 m2: 5.000 m2 Kollektor (11.500 m2) + 4.000 m3 (1.509 m2) passt nicht, + 2.000 m3 passt
    assert passt(cfg, 5000, 2000)
    assert not passt(cfg, 5000, 4000)


def test_bilder_entstehen(tmp_path):
    A, V = np.meshgrid([1000.0, 2000.0], [0.0, 2000.0])
    df = pd.DataFrame({"A_m2": A.ravel(), "V_m3": V.ravel()})
    for spalte, *_ in FELDER:
        df[spalte] = np.linspace(1.0, 2.0, len(df))
    df.loc[3, "lcoh_inkl_netz"] = np.nan  # Punkt passt nicht auf die Fläche
    assert _bild(df, tmp_path / "a.png", 261.0).exists()
    assert _bild_alle(df, tmp_path / "b.png", "Test").exists()
