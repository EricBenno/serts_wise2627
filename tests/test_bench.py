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
