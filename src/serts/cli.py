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
    from serts.run import run

    out = run(load_config(a.szenario), A_m2=a.A, V_m3=a.V, stunden=a.stunden)
    k = json.loads((out / "kpi.json").read_text("utf-8"))
    zeilen = [
        ("Kollektorfläche [m2]", "A_koll_m2", "{:,.0f}"),
        ("Speichervolumen [m3]", "V_m3", "{:,.0f}"),
        ("Wärmepumpe [MW]", "P_WP_MW", "{:.2f}"),
        ("PtH [MW]", "P_PtH_MW", "{:.2f}"),
        ("LCOH [EUR/MWh]", "lcoh", "{:.1f}"),
        ("LCOH Gas-Referenz [EUR/MWh]", "gas_lcoh", "{:.1f}"),
        ("Solaranteil", "solar_gesamt", "{:.1%}"),
        ("Erneuerbaren-Anteil", "ee_anteil", "{:.1%}"),
        ("CO2 System [t/a]", "co2_t_a", "{:,.0f}"),
        ("Speicher-Wirkungsgrad", "speicher_wirkungsgrad", "{:.1%}"),
        ("Flächenbedarf [m2]", "flaeche_m2", "{:,.0f}"),
    ]
    for text, key, fmt in zeilen:
        if key in k:
            print(f"{text:30s} {fmt.format(k[key])}")
    print(f"{'Gas-Referenz CO2 [t/a]':30s} {k['gas_co2_t_a']:,.0f}")
    print(f"\nErgebnis: {out}")


def _cmd_tornado(a):
    import pandas as pd

    from serts.tornado import tornado

    out = tornado(load_config(a.szenario), jobs=a.jobs)
    df = pd.read_csv(out / "tornado.csv").sort_values(["parameter", "wert"])
    cols = ["parameter", "wert", "lcoh", "solar_gesamt", "A_koll_m2", "V_m3", "P_WP_MW"]
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

    p = sub.add_parser("run", help="Lauf: Größen optimieren (oder mit --A/--V festlegen)")
    p.add_argument("--szenario", default=None)
    p.add_argument("--A", type=float, default=None, help="Kollektorfläche fest [m2]")
    p.add_argument("--V", type=float, default=None, help="Speichervolumen fest [m3] (0 = ohne)")
    p.add_argument("--stunden", type=int, default=None, help="nur die ersten N Stunden (Test)")
    p.set_defaults(func=_cmd_run)

    p = sub.add_parser("tornado", help="Sensitivitäten (tornado.parameter x sens-Werte)")
    p.add_argument("--szenario", default=None)
    p.add_argument("--jobs", type=int, default=3, help="parallele Läufe (je 1 Thread)")
    p.set_defaults(func=_cmd_tornado)

    sub.add_parser("annahmen", help="docs/annahmen.md erzeugen").set_defaults(func=_cmd_annahmen)
    sub.add_parser(
        "check-strahlung", help="DWD-Strahlung 03028 1991-2010 (Klimavergleich für PVGIS)"
    ).set_defaults(func=_cmd_check_strahlung)

    a = ap.parse_args(argv)
    return int(a.func(a) or 0)


if __name__ == "__main__":
    sys.exit(main())
