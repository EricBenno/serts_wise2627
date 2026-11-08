"""M1: Eingangszeitreihen (8760 h) erzeugen -> data/processed/.

Was offen ist (z. B. Kollektorkennwerte, Strahlung), wird übersprungen und gemeldet –
nicht mit Defaults gefüllt.
"""

from __future__ import annotations

import json
import logging

import pandas as pd

from serts import demand, heatpump, plots, solar, weather
from serts.config import Config, OffenerParameter
from serts.paths import DATA_PROCESSED
from serts.sources import netzberechnung

log = logging.getLogger(__name__)


def prepare(cfg: Config) -> dict:
    jahr = int(cfg.get("zeit.wetterjahr"))
    out_dir = DATA_PROCESSED / cfg.name
    out_dir.mkdir(parents=True, exist_ok=True)
    hinweise: list[str] = []

    roh = demand.lastgang_roh(cfg)
    last = demand.waermebedarf(cfg, roh)
    T_a = weather.aussentemperatur(cfg)
    if not last.index.equals(T_a.index):
        raise ValueError("Zeitachsen Lastgang und DWD-Temperatur passen nicht zusammen")

    ts = pd.DataFrame(index=last.index)
    ts["T_a"] = T_a
    ts[[f"last_{c}" for c in last.columns]] = last.to_numpy()
    ts["COP_luft"] = heatpump.cop_luft(cfg, T_a)
    ts["p_max_pu_luft"] = heatpump.p_max_pu_luft(cfg, T_a)

    try:
        strahlung = weather.strahlung_kollektorebene(cfg)
        ts["G_poa"] = strahlung["G_poa"].reindex(ts.index)
        ts[["P_hi", "P_lo"]] = solar.kollektor_zeitreihen(cfg, ts["G_poa"], T_a).to_numpy()
    except (OffenerParameter, FileNotFoundError) as exc:
        hinweise.append(f"Kollektor-Zeitreihen übersprungen: {exc}")

    ts.to_csv(out_dir / f"zeitreihen_{jahr}.csv", float_format="%.6g")

    kz = netzberechnung.kennzahlen(roh)
    kz.update(
        {
            "Q_modell_gesamt_MWh": float(last["gesamt"].sum()),
            "T_a_mittel_degC": float(T_a.mean()),
            "T_a_min_degC": float(T_a.min()),
            "korrelation_tagesmittel_T_last": float(
                T_a.resample("D").mean().corr(last["gebaeude"].resample("D").mean())
            ),
            "COP_luft_jahresmittel_lastgewichtet": float(
                (ts["COP_luft"] * last["gesamt"]).sum() / last["gesamt"].sum()
            ),
            "stunden_unter_T_min_luft": int((T_a < cfg.get("waermepumpe.T_min_luft")).sum()),
            "hinweise": hinweise,
        }
    )
    (out_dir / "kennzahlen.json").write_text(json.dumps(kz, indent=2, ensure_ascii=False), "utf-8")

    plots.lastgang(last, out_dir / "lastgang.png")
    plots.last_ueber_temperatur(last["gebaeude"], T_a, out_dir / "last_ueber_temperatur.png")
    plots.cop_kurve(T_a, ts["COP_luft"], out_dir / "cop_luft.png")
    return kz
