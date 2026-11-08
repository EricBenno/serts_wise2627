"""Kommandozeile: ``uv run serts <befehl>``."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from serts.config import load_config
from serts.paths import DATA_RAW, DEFAULT_RAW_SOURCE, DOCS


def _cmd_import_raw(a):
    from serts.sources.rawdata import import_raw

    for line in import_raw(Path(a.src), overwrite=a.overwrite):
        print(line)


def _cmd_verify_raw(a):
    from serts.sources.rawdata import verify_raw

    problems = verify_raw()
    print("\n".join(problems) if problems else "data/raw ok")
    return 1 if problems else 0


def _cmd_prepare(a):
    from serts.prepare import prepare

    kz = prepare(load_config(a.szenario))
    print(json.dumps(kz, indent=2, ensure_ascii=False))


def _cmd_offen(a):
    cfg = load_config(a.szenario)
    for path in cfg.offene():
        p = cfg.node(path)
        print(f"{path:40s} [{p.get('einheit', '')}]  {p.get('hinweis', '')}")


def _cmd_annahmen(a):
    from serts.annahmen import annahmen_markdown

    out = DOCS / "annahmen.md"
    out.write_text(annahmen_markdown(load_config()), encoding="utf-8")
    print(f"geschrieben: {out}")


def _cmd_check_strahlung(a):
    from serts.sources.dwd import strahlung_klima

    df = strahlung_klima(DATA_RAW / "dwd/st_03028/produkt_st_stunde_19820101_20110831_03028.txt")
    print(df.round(1).to_string())
    ok = df[df["n_fehlend"] <= 48]
    print(
        f"\nJahre mit <= 48 h Lücken: {len(ok)}; G_hor Median = {ok['G_hor_kWh_m2'].median():.0f}, "
        f"Mittel = {ok['G_hor_kWh_m2'].mean():.0f} kWh/m2a (Diffus erst ab 2010 gemessen)"
    )


def _cmd_fetch_pvgis(a):
    from serts.weather import fetch_pvgis

    print(f"gespeichert: {fetch_pvgis(load_config(a.szenario))}")


def _cmd_run(a):
    from serts.run import run_single

    out = run_single(load_config(a.szenario), a.A_spez, a.V_pro_A, stunden=a.stunden)
    k = json.loads((out / "kpi.json").read_text("utf-8"))
    keys = [
        "A_koll_m2",
        "V_m3",
        "lcoh",
        "gas_lcoh",
        "solar_gesamt",
        "ee_anteil",
        "P_WP_MW",
        "P_PtH_MW",
        "speicher_wirkungsgrad",
        "flaeche_gesamt_m2",
        "flaeche_ok",
    ]
    for key in keys:
        if key in k:
            print(f"{key:24s} {k[key]}")
    print(f"\nErgebnis: {out}")


def _cmd_raster(a):
    import pandas as pd

    from serts.run import run_raster

    out = run_raster(load_config(a.szenario), stunden=a.stunden, jobs=a.jobs)
    df = pd.read_csv(out / "raster.csv")
    cols = [
        "A_spez",
        "V_pro_A",
        "A_koll_m2",
        "V_m3",
        "lcoh",
        "solar_gesamt",
        "ee_anteil",
        "flaeche_ok",
    ]
    print(df[cols].round(3).to_string(index=False))
    print(f"\nErgebnis: {out}")


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(prog="serts")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("import-raw", help="Rohdaten aus Team-Ordner nach data/raw kopieren")
    p.add_argument("--src", default=str(DEFAULT_RAW_SOURCE))
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=_cmd_import_raw)

    sub.add_parser("verify-raw", help="data/raw gegen MANIFEST prüfen").set_defaults(
        func=_cmd_verify_raw
    )

    for name, func, hlp in [
        ("prepare", _cmd_prepare, "Zeitreihen 8760 h + Kennzahlen + Plots nach data/processed"),
        ("offen", _cmd_offen, "offene Parameter (x-Werte) auflisten"),
        ("fetch-pvgis", _cmd_fetch_pvgis, "PVGIS-SARAH3-Strahlung laden (Netzzugang)"),
    ]:
        p = sub.add_parser(name, help=hlp)
        p.add_argument("--szenario", default=None)
        p.set_defaults(func=func)

    p = sub.add_parser("run", help="Einzellauf (M5) für eine Rastergröße")
    p.add_argument("--szenario", default=None)
    p.add_argument("--A-spez", type=float, default=0.6, help="m2 je MWh/a Einspeisung")
    p.add_argument("--V-pro-A", type=float, default=1.6, help="m3 je m2 Kollektor")
    p.add_argument("--stunden", type=int, default=None, help="nur die ersten N Stunden (Test)")
    p.set_defaults(func=_cmd_run)

    p = sub.add_parser("raster", help="Rasterlauf (M6): Heatmap LCOH + Pareto")
    p.add_argument("--szenario", default=None)
    p.add_argument("--stunden", type=int, default=None, help="nur die ersten N Stunden (Test)")
    p.add_argument("--jobs", type=int, default=4, help="parallele Prozesse (je ≈ 1 GB RAM)")
    p.set_defaults(func=_cmd_raster)

    sub.add_parser("annahmen", help="docs/annahmen.md erzeugen").set_defaults(func=_cmd_annahmen)
    sub.add_parser(
        "check-strahlung", help="DWD-Strahlung 03028 1991-2010 (Klimavergleich für PVGIS)"
    ).set_defaults(func=_cmd_check_strahlung)

    a = ap.parse_args(argv)
    return int(a.func(a) or 0)


if __name__ == "__main__":
    sys.exit(main())
