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

    sub.add_parser("annahmen", help="docs/annahmen.md erzeugen").set_defaults(func=_cmd_annahmen)
    sub.add_parser(
        "check-strahlung", help="DWD-Strahlung 03028 1991-2010 (Klimavergleich für PVGIS)"
    ).set_defaults(func=_cmd_check_strahlung)

    a = ap.parse_args(argv)
    return int(a.func(a) or 0)


if __name__ == "__main__":
    sys.exit(main())
