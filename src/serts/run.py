"""Läufe: Ergebnisordner mit Config-Kopie + Git-Hash (BRF §10.5)."""

from __future__ import annotations

import datetime as dt
import json
import os
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

from serts import economics, ergebnisplots, kpi, network, plots
from serts.config import Config
from serts.paths import RESULTS, ROOT
from serts.prepare import build_zeitreihen


def git_info() -> dict[str, str | bool]:
    def _git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()

    try:
        return {"hash": _git("rev-parse", "HEAD"), "dirty": bool(_git("status", "--porcelain"))}
    except (OSError, subprocess.CalledProcessError):
        return {"hash": "unbekannt", "dirty": True}


def new_run_dir(cfg: Config, label: str = "", root: Path = RESULTS) -> Path:
    """results/<netz>/<YYYYmmdd-HHMMSS>_<szenario>[_<label>]/ mit config.yaml und meta.json."""
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    name = "_".join(filter(None, [stamp, cfg.name, label]))
    out = root / cfg.netz / name
    out.mkdir(parents=True, exist_ok=False)
    cfg.dump(out / "config.yaml")
    meta = {
        "netz": cfg.netz,
        "szenario": cfg.name,
        "label": label,
        "zeit": stamp,
        "git": git_info(),
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), "utf-8")
    return out


def plattform() -> dict[str, str | int]:
    """Rechner und Softwarestand für Laufzeitvergleiche (meta.json, benchmarks/bench.csv)."""
    from importlib.metadata import version

    cpu = platform.processor()
    try:
        if os.name == "nt":
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
            ) as key:
                cpu = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        else:
            for zeile in Path("/proc/cpuinfo").read_text().splitlines():
                if zeile.startswith("model name"):
                    cpu = zeile.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    system = platform.system()
    if system == "Linux" and "microsoft" in platform.release().lower():
        system = "Linux (WSL)"
    return {
        "system": system,
        "os": platform.platform(),
        "cpu": cpu,
        "threads": os.cpu_count() or 0,
        "python": sys.version.split()[0],
        "highs": version("highspy"),
        "pypsa": version("pypsa"),
        "linopy": version("linopy"),
    }


def meta_ergaenzen(out: Path, **felder) -> None:
    """Felder in out/meta.json ergänzen (z. B. Laufzeit nach dem Lösen)."""
    pfad = out / "meta.json"
    meta = json.loads(pfad.read_text("utf-8"))
    meta.update(felder)
    pfad.write_text(json.dumps(meta, indent=2, ensure_ascii=False), "utf-8")


def _highs_zeit(n) -> float:
    """Reine Rechenzeit von HiGHS [s] (0, falls nicht verfügbar)."""
    try:
        return float(n.model.solver_model.getRunTime())
    except Exception:  # noqa: BLE001 - nur Laufzeitausweis
        return 0.0


def _rechne(cfg: Config, ts: pd.DataFrame, A_m2, V_m3, threads, segment=None):
    """Bauen, lösen, auswerten; Laufzeit je Schritt in k["laufzeit"] (Sekunden)."""
    t0 = time.perf_counter()
    n = network.build_network(cfg, ts, A_m2, V_m3, **({"segment": segment} if segment else {}))
    t1 = time.perf_counter()
    network.optimize(n, cfg, ts, threads=threads)
    t2 = time.perf_counter()
    highs = _highs_zeit(n)
    k, r = kpi.auswerten(n, cfg, ts)
    t3 = time.perf_counter()
    k["laufzeit"] = {
        "aufbau_s": t1 - t0,
        "modell_s": max(t2 - t1 - highs, 0.0),
        "highs_s": highs,
        "auswertung_s": t3 - t2,
    }
    return n, k, r


def niedrige_prioritaet() -> None:
    """Rechenprozess auf niedrige Priorität setzen, damit der Rechner bedienbar bleibt.

    Windows: BELOW_NORMAL (Kindprozesse erben das), sonst nice +10. Fehler werden ignoriert.
    """
    try:
        if os.name == "nt":
            import ctypes

            k32 = ctypes.windll.kernel32
            k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)  # BELOW_NORMAL_PRIORITY_CLASS
        else:
            os.nice(10)
    except Exception:  # noqa: BLE001 - Priorität ist nur Komfort
        pass


def _segment(cfg: Config, ts: pd.DataFrame, A_m2, i: int, threads: int | None):
    """Ein Kostensegment lösen -> (i, n, k, r) oder (i, None, Text, None) wenn unzulässig."""
    seg = economics.ptes_segmente(cfg)[i]
    try:
        n, k, r = _rechne(cfg, ts, A_m2, None, threads, segment=seg)
    except RuntimeError:  # z. B. Mindestvolumen passt nicht auf die Fläche
        return i, None, f"{seg[0]:.0f}-{seg[1]:.0f} m3: unzulässig", None
    if hasattr(n, "_model"):  # linopy-Modell nicht mitschicken (Prozessgrenze, Speicher)
        n._model = None
    return i, n, k, r


def loese(
    cfg: Config,
    ts: pd.DataFrame,
    A_m2: float | None = None,
    V_m3: float | None = None,
    threads: int | None = None,
    start_segment: int | None = None,
    jobs: int = 1,
):
    """Netz bauen, optimieren, auswerten. A/V = None -> Größe wird optimiert.

    Speicher optimiert: ein Lauf je Kostensegment (economics.ptes_segmente), V bleibt im Segment;
    der Lauf mit den geringsten Jahreskosten gewinnt (docs E30).
    ``start_segment`` (Tornado, docs E42): nur dieses Segment und seine Nachbarn rechnen; liegt das
    Optimum am Rand der Auswahl, wird so lange ein Segment weiter außen ergänzt, bis es innen liegt
    oder am ersten/letzten Segment. ``jobs`` > 1: Segmente parallel (je 1 Thread).
    """
    if V_m3 is not None:
        t0 = time.perf_counter()
        n, k, r = _rechne(cfg, ts, A_m2, V_m3, threads)
        k["laufzeit"].update(segmente=1, loesen_s=time.perf_counter() - t0)
        return n, k, r

    t0 = time.perf_counter()

    anzahl = len(economics.ptes_segmente(cfg))
    if start_segment is None:
        offen = list(range(anzahl))
    else:
        offen = [
            i for i in (start_segment - 1, start_segment, start_segment + 1) if 0 <= i < anzahl
        ]
    ergebnisse: dict[int, tuple] = {}

    def rechnen(idx):
        if jobs > 1 and len(idx) > 1:
            with ProcessPoolExecutor(
                max_workers=min(jobs, len(idx)), initializer=niedrige_prioritaet
            ) as pool:
                return list(
                    pool.map(_segment, *zip(*[(cfg, ts, A_m2, i, 1) for i in idx], strict=True))
                )
        return [_segment(cfg, ts, A_m2, i, threads) for i in idx]

    while offen:
        for i, n, k, r in rechnen(offen):
            ergebnisse[i] = (n, k, r)
        gueltig = {i: e for i, e in ergebnisse.items() if e[0] is not None}
        if not gueltig:  # Auswahl ganz unzulässig (z. B. weniger Fläche) -> restliche Segmente
            offen = [j for j in range(anzahl) if j not in ergebnisse]
            continue
        beste_i = min(gueltig, key=lambda i: gueltig[i][1]["kosten_a_gesamt"])
        offen = [j for j in (beste_i - 1, beste_i + 1) if 0 <= j < anzahl and j not in ergebnisse]

    segmente = []
    for i in sorted(ergebnisse):
        n, k, _ = ergebnisse[i]
        if n is None:
            segmente.append(k)
        else:
            seg = economics.ptes_segmente(cfg)[i]
            segmente.append(
                f"{seg[0]:.0f}-{seg[1]:.0f} m3: LCOH {k['lcoh']:.1f}, V {k['V_m3']:.0f} m3, "
                f"A {k['A_koll_m2']:.0f} m2, Solar {k['solar_gesamt']:.0%}"
            )
    gueltig = {i: e for i, e in ergebnisse.items() if e[0] is not None}
    if not gueltig:
        raise RuntimeError("kein Kostensegment lösbar: " + "; ".join(segmente))
    beste_i = min(gueltig, key=lambda i: gueltig[i][1]["kosten_a_gesamt"])
    n, k, r = gueltig[beste_i]
    # Laufzeit über alle gelösten Segmente summiert; loesen_s = Wandzeit (inkl. Prozessstart, unzulässige)
    laufzeit = {
        s: sum(e[1]["laufzeit"][s] for e in gueltig.values())
        for s in ("aufbau_s", "modell_s", "highs_s", "auswertung_s")
    }
    k["laufzeit"] = {**laufzeit, "segmente": len(ergebnisse), "loesen_s": time.perf_counter() - t0}
    k["segmente_vergleich"] = segmente
    k["segment_index"] = beste_i
    return n, k, r


def run(
    cfg: Config,
    A_m2: float | None = None,
    V_m3: float | None = None,
    stunden: int | None = None,
) -> Path:
    """Ein Lauf: speichert config, meta, kpi.json, zeitreihen.csv, network.nc, monatsbilanz.png."""
    t0 = time.perf_counter()
    ts, _ = build_zeitreihen(cfg, vollstaendig=True)
    if stunden:
        ts = ts.iloc[:stunden]
    t1 = time.perf_counter()
    n, k, r = loese(cfg, ts, A_m2, V_m3, jobs=int(cfg.get("solver.jobs_segmente") or 1))
    teile = [f"A{A_m2:g}" if A_m2 is not None else "", f"V{V_m3:g}" if V_m3 is not None else ""]
    label = "_".join(filter(None, teile)) or "opt"
    out = new_run_dir(cfg, label + (f"_{stunden}h" if stunden else ""))
    (out / "kpi.json").write_text(
        json.dumps(k, indent=2, ensure_ascii=False, default=float), "utf-8"
    )
    r.to_csv(out / "zeitreihen.csv", float_format="%.5g")
    n.export_to_netcdf(out / "network.nc")
    plots.monatsbilanz(r, out / "monatsbilanz.png")
    ergebnisplots.alle(r, k, out)
    laufzeit = {"zeitreihen_s": t1 - t0, **k["laufzeit"]}
    laufzeit["speichern_s"] = time.perf_counter() - t1 - laufzeit["loesen_s"]
    laufzeit["gesamt_s"] = time.perf_counter() - t0
    meta_ergaenzen(
        out, laufzeit={s: round(v, 2) for s, v in laufzeit.items()}, plattform=plattform()
    )
    return out
