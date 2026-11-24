"""Laufzeit-Benchmark: Basisfall mehrmals rechnen, Laufzeit je Schritt in benchmarks/bench.csv.

Zwei Modi:
- ``fest``: eine Optimierung mit fester Kollektorfläche und festem Speichervolumen (misst Modell + Solver).
- ``voll``: Größen optimiert wie ``serts run`` (Segmentsuche, mehrere Optimierungen; mit ``jobs`` > 1 parallel,
  dann zählt auch der Start der Rechenprozesse mit).

Es wird nichts in results/ geschrieben. Der Wärmepreis steht als Kontrolle mit in der Tabelle: Er muss auf jeder
Plattform gleich sein. Vergleich Windows/Linux: docs/laufzeit.md (nur lokal, nicht in Git).
"""

from __future__ import annotations

import datetime as dt
import statistics
import time
from pathlib import Path

import pandas as pd

from serts.config import Config
from serts.paths import ROOT
from serts.prepare import build_zeitreihen
from serts.run import git_info, loese, plattform

BENCH_CSV = ROOT / "benchmarks" / "bench.csv"
SCHRITTE = ["zeitreihen_s", "aufbau_s", "modell_s", "highs_s", "auswertung_s", "gesamt_s"]


def bench(
    cfg: Config,
    modus: str = "fest",
    wiederholungen: int = 3,
    A_m2: float = 4000.0,
    V_m3: float = 6000.0,
    jobs: int = 1,
    stunden: int | None = None,
    datei: Path = BENCH_CSV,
) -> pd.DataFrame:
    """Benchmark rechnen, Zeilen an ``datei`` anhängen und zurückgeben."""
    if modus not in ("fest", "voll"):
        raise ValueError("modus muss 'fest' oder 'voll' sein")
    info = plattform()
    git = git_info()
    zeilen = []
    for nr in range(1, wiederholungen + 1):
        t0 = time.perf_counter()
        ts, _ = build_zeitreihen(cfg, vollstaendig=True)
        if stunden:
            ts = ts.iloc[:stunden]
        t1 = time.perf_counter()
        if modus == "fest":
            _, k, _ = loese(cfg, ts, A_m2, V_m3)
        else:
            _, k, _ = loese(cfg, ts, jobs=jobs)
        t2 = time.perf_counter()
        lz = k["laufzeit"]
        zeilen.append(
            {
                "datum": dt.datetime.now().isoformat(timespec="seconds"),
                **info,
                "git": git["hash"][:7] + ("+" if git["dirty"] else ""),
                "netz": cfg.netz,
                "modus": modus,
                "jobs": jobs if modus == "voll" else 1,
                "stunden": stunden or len(ts),
                "lauf": nr,
                "segmente": lz.get("segmente", 1),
                "zeitreihen_s": t1 - t0,
                "aufbau_s": lz["aufbau_s"],
                "modell_s": lz["modell_s"],
                "highs_s": lz["highs_s"],
                "auswertung_s": lz["auswertung_s"],
                "gesamt_s": t2 - t0,
                "lcoh_inkl_netz": k.get("lcoh_inkl_netz"),
            }
        )
    df = pd.DataFrame(zeilen)
    datei.parent.mkdir(parents=True, exist_ok=True)
    df.round(3).to_csv(datei, mode="a", header=not datei.exists(), index=False)
    return df


def zusammenfassung(df: pd.DataFrame) -> str:
    """Median je Schritt (der erste Lauf enthält Import und Dateicache und streut stärker)."""
    kopf = f"{df['system'].iloc[0]}, {df['cpu'].iloc[0]}, {df['modus'].iloc[0]}, {len(df)} Läufe"
    teile = [f"{s[:-2]:<12} {statistics.median(df[s]):7.1f} s" for s in SCHRITTE]
    return "\n".join([kopf, *teile, f"Wärmepreis   {df['lcoh_inkl_netz'].iloc[-1]:7.2f} €/MWh"])
