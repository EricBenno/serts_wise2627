"""Flächenbedarf Kollektorfeld + PTES gegen die verfügbare Grundstücksfläche (TEAM: ≈ 13.000 m2).

PTES-Geometrie: geometrisch ähnlich zu Dronninglund (Pyramidenstumpf 90/26 m, 16 m tief),
skaliert mit s = (V / V_ref)^(1/3); Grundfläche = (a_oben*s + 2*Randstreifen)^2.
Kollektorfeld: A_Koll * Flächenfaktor (BSW: 2-2,3, inkl. Reihenabstand und Technik).
"""

from __future__ import annotations

from serts.config import Config


def ptes_geometrie(cfg: Config, V_m3: float) -> dict:
    ref = cfg.get("ptes.geometrie_ref")
    if V_m3 <= 0:
        return {"ptes_a_oben_m": 0.0, "ptes_tiefe_m": 0.0, "ptes_grundflaeche_m2": 0.0}
    s = (V_m3 / ref["V"]) ** (1.0 / 3.0)
    a = ref["a_oben"] * s
    rand = cfg.get("ptes.randstreifen")
    return {
        "ptes_a_oben_m": a,
        "ptes_tiefe_m": ref["tiefe"] * s,
        "ptes_grundflaeche_m2": (a + 2 * rand) ** 2,
    }


def flaechenbedarf(cfg: Config, A_koll_m2: float, V_m3: float) -> dict:
    geo = ptes_geometrie(cfg, V_m3)
    koll = A_koll_m2 * cfg.get("kollektor.flaechenfaktor")
    gesamt = koll + geo["ptes_grundflaeche_m2"]
    verf = cfg.get("standort.flaeche_verfuegbar")
    return {
        **geo,
        "kollektor_grundflaeche_m2": koll,
        "flaeche_gesamt_m2": gesamt,
        "flaeche_verfuegbar_m2": verf,
        "flaeche_ok": bool(gesamt <= verf),
    }
