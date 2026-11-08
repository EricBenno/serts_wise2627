"""M1: Eingangszeitreihen (8760 h) erzeugen -> data/processed/.

Was offen ist (z. B. Strahlung ohne PVGIS-Datei), wird bei ``prepare`` übersprungen und gemeldet –
nicht mit Defaults gefüllt. ``build_zeitreihen(..., vollstaendig=True)`` bricht dagegen ab.
"""

from __future__ import annotations

import json
import logging

import pandas as pd

from serts import demand, heatpump, plots, prices, solar, weather
from serts.config import Config, OffenerParameter
from serts.paths import DATA_PROCESSED
from serts.sources import netzberechnung

log = logging.getLogger(__name__)


def build_zeitreihen(cfg: Config, vollstaendig: bool = True) -> tuple[pd.DataFrame, list[str]]:
    """Alle Modell-Zeitreihen in einem DataFrame (Index: Stunden 2022, tz-naiv UTC)."""
    hinweise: list[str] = []
    roh = demand.lastgang_roh(cfg)
    last = demand.waermebedarf(cfg, roh)
    T_a = weather.aussentemperatur(cfg)
    if not last.index.equals(T_a.index):
        raise ValueError("Zeitachsen Lastgang und DWD-Temperatur passen nicht zusammen")

    ts = pd.DataFrame(index=last.index)
    ts["T_a"] = T_a
    for c in last.columns:
        ts[f"last_{c}"] = last[c]
    ts["COP_luft"] = heatpump.cop_luft(cfg, T_a)
    ts["p_max_pu_luft"] = heatpump.p_max_pu_luft(cfg, T_a)
    try:
        strahlung = weather.strahlung_kollektorebene(cfg)
        ts["G_poa"] = strahlung["G_poa"].reindex(ts.index)
        koll = solar.kollektor_zeitreihen(cfg, ts["G_poa"], T_a)
        ts["P_hi"], ts["P_lo"] = koll["P_hi"], koll["P_lo"]
    except (OffenerParameter, FileNotFoundError) as exc:
        if vollstaendig:
            raise
        hinweise.append(f"Kollektor-Zeitreihen übersprungen: {exc}")
    try:
        ts["strompreis"] = prices.strompreis(cfg, ts.index)
    except OffenerParameter as exc:
        if vollstaendig:
            raise
        hinweise.append(f"Strompreis übersprungen: {exc}")
    return ts, hinweise


def prepare(cfg: Config) -> dict:
    jahr = int(cfg.get("zeit.wetterjahr"))
    out_dir = DATA_PROCESSED / cfg.name
    out_dir.mkdir(parents=True, exist_ok=True)
    ts, hinweise = build_zeitreihen(cfg, vollstaendig=False)
    ts.to_csv(out_dir / f"zeitreihen_{jahr}.csv", float_format="%.6g")

    roh = demand.lastgang_roh(cfg)
    kz = netzberechnung.kennzahlen(roh)
    T_a = ts["T_a"]
    kz.update(
        {
            "Q_modell_gesamt_MWh": float(ts["last_gesamt"].sum()),
            "T_a_mittel_degC": float(T_a.mean()),
            "T_a_min_degC": float(T_a.min()),
            "korrelation_tagesmittel_T_last": float(
                T_a.resample("D").mean().corr(ts["last_gebaeude"].resample("D").mean())
            ),
            "COP_luft_jahresmittel_lastgewichtet": float(
                (ts["COP_luft"] * ts["last_gesamt"]).sum() / ts["last_gesamt"].sum()
            ),
            "stunden_unter_T_min_luft": int((T_a < cfg.get("waermepumpe.T_min_luft")).sum()),
        }
    )
    if "P_hi" in ts:
        kz.update(
            {
                "G_poa_kWh_m2": float(ts["G_poa"].sum() / 1000),
                "P_hi_kWh_m2": float(ts["P_hi"].sum()),
                "P_lo_kWh_m2": float(ts["P_lo"].sum()),
            }
        )
    kz["hinweise"] = hinweise
    (out_dir / "kennzahlen.json").write_text(json.dumps(kz, indent=2, ensure_ascii=False), "utf-8")

    last = ts[["last_gebaeude", "last_netzverlust", "last_ankerkunde", "last_gesamt"]]
    last.columns = [c.removeprefix("last_") for c in last.columns]
    plots.lastgang(last, out_dir / "lastgang.png")
    plots.last_ueber_temperatur(last["gebaeude"], T_a, out_dir / "last_ueber_temperatur.png")
    plots.cop_kurve(T_a, ts["COP_luft"], out_dir / "cop_luft.png")
    return kz
