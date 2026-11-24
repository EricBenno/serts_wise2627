"""Laufzeit-Benchmark und Laufzeitausweis (kurzer Zeitraum)."""

import pandas as pd

from serts.bench import bench, zusammenfassung
from serts.run import plattform


def test_plattform_felder():
    p = plattform()
    assert {"system", "cpu", "threads", "python", "highs", "pypsa"} <= set(p)
    assert p["threads"] > 0


def test_bench_haengt_zeilen_an(cfg, tmp_path):
    datei = tmp_path / "bench.csv"
    df = bench(cfg, modus="fest", wiederholungen=1, stunden=48, datei=datei)
    bench(cfg, modus="fest", wiederholungen=1, stunden=48, datei=datei)
    gespeichert = pd.read_csv(datei)
    assert len(df) == 1 and len(gespeichert) == 2  # angehängt, Kopfzeile nur einmal
    z = df.iloc[0]
    assert z["gesamt_s"] >= z["aufbau_s"] + z["modell_s"] + z["highs_s"] > 0
    assert gespeichert["lcoh_inkl_netz"].nunique() == 1  # gleiche Rechnung, gleiches Ergebnis
    assert "Wärmepreis" in zusammenfassung(df)


def test_segmente_parallel_gleich_wie_nacheinander(cfg):
    """Parallel gelöste Segmente liefern dieselben Größen, Kennzahlen und Zeitreihen (kein Datenverlust)."""
    import numpy as np

    from serts.prepare import build_zeitreihen
    from serts.run import loese

    kurz = build_zeitreihen(cfg, vollstaendig=True)[0].iloc[:48]
    _, k1, r1 = loese(cfg, kurz, jobs=1)
    n2, k2, r2 = loese(cfg, kurz, jobs=3)
    zahlen = [s for s, v in k1.items() if isinstance(v, (int, float)) and s != "laufzeit"]
    for s in zahlen:
        assert k2[s] == k1[s] or np.isclose(k2[s], k1[s], rtol=1e-9, atol=1e-9, equal_nan=True), s
    assert k1["segmente_vergleich"] == k2["segmente_vergleich"]
    assert list(r1.columns) == list(r2.columns)
    np.testing.assert_allclose(
        r1.to_numpy(float), r2.to_numpy(float), rtol=1e-9, atol=1e-9, equal_nan=True
    )
    assert n2.generators.shape[0] > 0  # Netz kommt vollständig zurück (für network.nc)
