"""Trassenkosten je m aus dem KWW Technikkatalog, gewichtet mit der Rohrdimensionsverteilung der Netzberechnung.

Aufruf:  uv run python scripts/kww_trasse.py

Methode (nur Rechnung auf Rohdaten, keine eigenen Preise):
- Länge je Rohrdimension aus Blatt "Zusammenfassung" der Netzberechnung (PEX 20-100, KMR 100-300).
- PEX -> KWW Tab. 37 (polymere Mediumrohre, dn 20-160), KMR -> KWW Tab. 36 (Kunststoffmantelrohr DN 20-200);
  nächstgelegene KWW-Dimension (KMR 250/300 -> DN 200, unterschätzt leicht).
- Kosten je m = Tiefbau (Mittel aus min. und max.) + Materialkosten; getrennt für befestigtes Terrain (Straße)
  und unbefestigtes Terrain (Grün). min./max. dienen als Sensitivitätsspanne.
"""

from __future__ import annotations

import sys
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KWW = ROOT / "data/raw/kww/KWW-Technikkatalog-Waermeplanung_08-2026_Version_1.1.xlsx"
NETZE = {
    "klein": ROOT / "data/raw/bad_lippspringe/results netzberechnung.xlsx",
    "gross": ROOT / "data/raw/bad_lippspringe/results_gross.xlsx",
}


def kww_tabelle(wb, blatt: str) -> dict[str, dict[int, float]]:
    """Zeilen 'Hauptleitung - ...' der Tab. 36/37 -> {Zeilenname: {Dimension: EUR/m}}."""
    ws = wb[blatt]
    dims: list[int] = []
    out: dict[str, dict[int, float]] = {}
    for row in ws.iter_rows(min_row=1, max_row=20, values_only=True):
        if row[1] == "Rohrdurchmesser":
            dims = [int(x) for x in row[3:14] if x is not None]
        elif dims and isinstance(row[1], str) and row[1].startswith("Hauptleitung"):
            out[row[1]] = {
                d: float(v) for d, v in zip(dims, row[3:], strict=False) if v is not None
            }
    return out


def eur_je_m(
    tab: dict[str, dict[int, float]], dn: int, befestigt: bool
) -> tuple[float, float, float]:
    """(Mittel, min, max) EUR/m inkl. Material für die nächstgelegene KWW-Dimension."""

    def zeile(ende: str) -> dict[int, float]:
        return next(
            v
            for k, v in tab.items()
            if k.startswith("Hauptleitung - Tiefbau")
            and (("unbefestigt" in k) != befestigt)
            and k.endswith(ende)
        )

    mat = next(v for k, v in tab.items() if "Materialkosten" in k)
    mi, ma = zeile("min."), zeile("max.")
    d = min(mi, key=lambda x: abs(x - dn))
    return (mi[d] + ma[d]) / 2 + mat[d], mi[d] + mat[d], ma[d] + mat[d]


def trasse(netz: str) -> dict[str, list[int]]:
    wb = openpyxl.load_workbook(KWW, data_only=True)
    tabs = {"PEX": kww_tabelle(wb, "Tab 37"), "KMR": kww_tabelle(wb, "Tab 36")}
    z = pd.read_excel(NETZE[netz], sheet_name="Zusammenfassung")
    z = z[z.iloc[:, 3].astype(str).str.contains("PEX|KMR", na=False)]
    laenge, name = z.iloc[:, 6].astype(float), z.iloc[:, 3].astype(str)
    res: dict[str, list[int]] = {}
    for label, bef in (("strasse (befestigt)", True), ("gruen (unbefestigt)", False)):
        summe = [0.0, 0.0, 0.0]
        for nm, ell in zip(name, laenge, strict=True):
            typ, dn = nm.split()
            for i, c in enumerate(eur_je_m(tabs[typ], int(dn), bef)):
                summe[i] += c * ell
        res[label] = [round(s / laenge.sum()) for s in summe]
    res["trassenlaenge_m"] = [round(laenge.sum())]
    return res


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for n in NETZE:
        r = trasse(n)
        print(f"Netz {n}: Trasse {r['trassenlaenge_m'][0]} m  (EUR/m: Mittel, min, max)")
        for k in ("strasse (befestigt)", "gruen (unbefestigt)"):
            print(f"  {k:22s} {r[k][0]:5d}  {r[k][1]:5d}  {r[k][2]:5d}")
