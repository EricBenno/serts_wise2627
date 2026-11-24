"""Kommandozeile: ``uv run serts <befehl>``."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from serts.config import load_config
from serts.paths import DATA_RAW, DEFAULT_RAW_SOURCE, DOCS


def _cfg(a):
    """Konfiguration aus --netz und --szenario (Szenarien mit + kombinierbar)."""
    return load_config(a.szenario, netz=getattr(a, "netz", "klein"))


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

    kz = prepare(_cfg(a))
    print(json.dumps(kz, indent=2, ensure_ascii=False))


def _cmd_offen(a):
    cfg = _cfg(a)
    for path in cfg.offene():
        p = cfg.node(path)
        print(f"{path:40s} [{p.get('einheit', '')}]  {p.get('hinweis', '')}")


def _cmd_annahmen(a):
    from serts.annahmen import annahmen_markdown

    out = DOCS / "annahmen.md"
    out.write_text(annahmen_markdown(load_config()), encoding="utf-8")
    print(f"geschrieben: {out}")


def _cmd_uebersicht(a):
    from serts.uebersicht import uebersicht_markdown

    klein = load_config(a.szenario, netz="klein")
    gross = load_config(a.szenario, netz="gross")
    out = DOCS / "eingangsparameter.md"
    out.write_text(uebersicht_markdown(klein, gross), encoding="utf-8")
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

    print(f"gespeichert: {fetch_pvgis(_cfg(a))}")


def _cmd_fetch_strompreise(a):
    from serts.prices import fetch_day_ahead

    for jahr in a.jahre:
        print(f"gespeichert: {fetch_day_ahead(jahr)}")


def _cmd_bench(a):
    from serts.bench import BENCH_CSV, bench, zusammenfassung

    df = bench(
        _cfg(a),
        modus=a.modus,
        wiederholungen=a.wiederholungen,
        A_m2=a.A,
        V_m3=a.V,
        jobs=a.jobs,
        stunden=a.stunden,
    )
    print(zusammenfassung(df))
    print(f"angehängt: {BENCH_CSV}")


def _cmd_run(a):
    from serts.run import run

    out = run(_cfg(a), A_m2=a.A, V_m3=a.V, stunden=a.stunden)
    k = json.loads((out / "kpi.json").read_text("utf-8"))
    zeilen = [
        ("Kollektorfläche [m2]", "A_koll_m2", "{:,.0f}"),
        ("Speichervolumen [m3]", "V_m3", "{:,.0f}"),
        ("Wärmepumpe [MW]", "P_WP_MW", "{:.2f}"),
        ("PtH [MW]", "P_PtH_MW", "{:.2f}"),
        ("LCOH [EUR/MWh]", "lcoh", "{:.1f}"),
        ("LCOH Gas-Referenz [EUR/MWh]", "gas_lcoh", "{:.1f}"),
        ("Wärmepreis inkl. Netz [EUR/MWh]", "lcoh_inkl_netz", "{:.1f}"),
        ("  Gas-Fernwärme inkl. Netz", "gas_lcoh_inkl_netz", "{:.1f}"),
        ("  davon Wärmenetz Trasse [EUR/MWh]", "netzkosten_spez_trasse", "{:.1f}"),
        ("  davon Hausanschl. + Übergabest. [EUR/MWh]", "netzkosten_spez_hausanschluss", "{:.1f}"),
        ("Mit BEW Modul 2 (max. 40 %, gleiche Auslegung):", None, ""),
        ("  LCOH [EUR/MWh]", "lcoh_bew", "{:.1f}"),
        ("  Wärmepreis inkl. Netz [EUR/MWh]", "lcoh_inkl_netz_bew", "{:.1f}"),
        ("  Zuschuss [Mio. EUR]", "zuschuss_bew_EUR", "{:.2f}"),
        ("Solaranteil", "solar_gesamt", "{:.1%}"),
        ("Erneuerbaren-Anteil", "ee_anteil", "{:.1%}"),
        ("CO2 System [t/a]", "co2_t_a", "{:,.0f}"),
        ("Speicher-Wirkungsgrad", "speicher_wirkungsgrad", "{:.1%}"),
        ("Speicher Zyklen pro Jahr", "speicher_zyklen", "{:.1f}"),
        ("Speicher Entladung im Winter", "speicher_winteranteil", "{:.0%}"),
        ("Speicher Entladung direkt (85 °C)", "speicher_direktanteil", "{:.0%}"),
        ("Speicher-Charakter", "speicher_charakter", "{}"),
        ("Strompreis gewichtet [EUR/MWh]", "strompreis_gewichtet_EUR_MWh", "{:.0f}"),
        ("Strompreis Jahresmittel [EUR/MWh]", "strompreis_mittel_EUR_MWh", "{:.0f}"),
        ("Höchster Strombezug [MW]", "P_netzanschluss_MW", "{:.2f}"),
        ("  Leistungspreis [EUR/a]", "kosten_a_strom_leistung", "{:,.0f}"),
        ("Flächenbedarf [m2]", "flaeche_m2", "{:,.0f}"),
    ]
    for text, key, fmt in zeilen:
        if key is None:
            print(text)
        elif key in k:
            wert = k[key] / 1e6 if key == "zuschuss_bew_EUR" else k[key]
            print(f"{text:30s} {fmt.format(wert)}")
    print(f"{'Gas-Referenz CO2 [t/a]':30s} {k['gas_co2_t_a']:,.0f}")
    if "speicher_preis_EUR_m3" in k:
        print(f"{'Speicherpreis Durchschnitt [EUR/m3]':30s} {k['speicher_preis_EUR_m3']:.0f}")
    for zeile in k.get("segmente_vergleich", []):
        print(f"  Kostensegment {zeile}")
    print(f"\nErgebnis: {out}")


def _cmd_varianten(a):
    from serts.varianten import varianten

    out = varianten(_cfg(a), jobs=a.jobs)
    print((out / "varianten.md").read_text("utf-8"))
    print(f"Ergebnis: {out}")


def _cmd_heatmap(a):
    from serts.heatmap import heatmap

    out = heatmap(_cfg(a), jobs=a.jobs)
    print(f"Ergebnis: {out}")


def _cmd_tornado(a):
    import pandas as pd

    from serts.tornado import tornado

    out = tornado(_cfg(a), jobs=a.jobs, nur=a.parameter)
    df = pd.read_csv(out / "tornado.csv").sort_values(["parameter", "wert"])
    cols = ["parameter", "wert", "lcoh", "lcoh_inkl_netz", "abstand_gas", "solar_gesamt", "V_m3"]
    print(df[cols].round(3).to_string(index=False))
    print(f"\nErgebnis: {out}")


def main(argv: list[str] | None = None) -> int:
    import matplotlib

    # Windows-Konsole (cp1252) kann z. B. "CO₂" nicht ausgeben -> Ausgabe immer UTF-8
    for strom in (sys.stdout, sys.stderr):
        if hasattr(strom, "reconfigure"):
            strom.reconfigure(encoding="utf-8", errors="replace")
    matplotlib.use("Agg")  # Kommandozeile/Prozesse ohne Fenster
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
        p.add_argument("--netz", default="klein", help="Netzfall (config/netze/<netz>.yaml)")
        p.set_defaults(func=func)

    p = sub.add_parser("run", help="Lauf: Größen optimieren (oder mit --A/--V festlegen)")
    p.add_argument("--szenario", default=None)
    p.add_argument("--netz", default="klein", help="Netzfall (config/netze/<netz>.yaml)")
    p.add_argument("--A", type=float, default=None, help="Kollektorfläche fest [m2]")
    p.add_argument("--V", type=float, default=None, help="Speichervolumen fest [m3] (0 = ohne)")
    p.add_argument("--stunden", type=int, default=None, help="nur die ersten N Stunden (Test)")
    p.set_defaults(func=_cmd_run)

    p = sub.add_parser("bench", help="Laufzeit-Benchmark Basisfall -> benchmarks/bench.csv")
    p.add_argument("--szenario", default=None)
    p.add_argument("--netz", default="klein", help="Netzfall (config/netze/<netz>.yaml)")
    p.add_argument(
        "--modus",
        choices=["fest", "voll"],
        default="fest",
        help="fest = eine Optimierung mit festen Größen; voll = Größen optimiert wie run",
    )
    p.add_argument("--wiederholungen", type=int, default=3)
    p.add_argument("--A", type=float, default=4000.0, help="Kollektorfläche bei modus fest [m2]")
    p.add_argument("--V", type=float, default=6000.0, help="Speichervolumen bei modus fest [m3]")
    p.add_argument("--jobs", type=int, default=1, help="parallele Segmente bei modus voll")
    p.add_argument("--stunden", type=int, default=None, help="nur die ersten N Stunden (Test)")
    p.set_defaults(func=_cmd_bench)

    p = sub.add_parser("tornado", help="Sensitivitäten (tornado.parameter x sens-Werte)")
    p.add_argument("--szenario", default=None)
    p.add_argument("--netz", default="klein", help="Netzfall (config/netze/<netz>.yaml)")
    p.add_argument("--jobs", type=int, default=6, help="parallele Läufe (je 1 Thread)")
    p.add_argument(
        "--parameter",
        nargs="+",
        default=None,
        help="nur diese Parameter variieren (sens-Werte aus der Config), z. B. netz.T_VL",
    )
    p.set_defaults(func=_cmd_tornado)

    p = sub.add_parser(
        "varianten", help="Vergleich: Basis, ohne Speicher, nur WP+PtH, mit BEW (+ Gas-Referenz)"
    )
    p.add_argument("--szenario", default=None)
    p.add_argument("--netz", default="klein", help="Netzfall (config/netze/<netz>.yaml)")
    p.add_argument("--jobs", type=int, default=2, help="parallele Läufe")
    p.set_defaults(func=_cmd_varianten)

    p = sub.add_parser("heatmap", help="Wärmepreis über Kollektorfläche x Speichervolumen (Raster)")
    p.add_argument("--szenario", default=None)
    p.add_argument("--netz", default="klein", help="Netzfall (config/netze/<netz>.yaml)")
    p.add_argument("--jobs", type=int, default=3, help="parallele Läufe")
    p.set_defaults(func=_cmd_heatmap)

    p = sub.add_parser(
        "fetch-strompreise", help="Day-Ahead-Preise DE-LU laden (Energy-Charts/SMARD)"
    )
    p.add_argument("jahre", type=int, nargs="+", help="z. B. 2022 2023 2024")
    p.set_defaults(func=_cmd_fetch_strompreise)

    sub.add_parser("annahmen", help="docs/annahmen.md erzeugen").set_defaults(func=_cmd_annahmen)
    p = sub.add_parser(
        "uebersicht", help="docs/eingangsparameter.md: zentrale Übersicht (Netz klein + groß)"
    )
    p.add_argument("--szenario", default=None)
    p.set_defaults(func=_cmd_uebersicht)
    sub.add_parser(
        "check-strahlung", help="DWD-Strahlung 03028 1991-2010 (Klimavergleich für PVGIS)"
    ).set_defaults(func=_cmd_check_strahlung)

    a = ap.parse_args(argv)
    if a.cmd in ("run", "tornado", "varianten", "heatmap"):
        from serts.run import niedrige_prioritaet

        niedrige_prioritaet()  # Rechner bleibt bedienbar; Kindprozesse erben die Priorität
    return int(a.func(a) or 0)


if __name__ == "__main__":
    sys.exit(main())
