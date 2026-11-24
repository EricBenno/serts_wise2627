"""Import der Rohdaten aus dem Team-Ordner nach data/raw (unverändert, mit SHA-256-Manifest).

Nur Dateien, die das Modell braucht. GIS-Daten (gpkg, KWP-Shapes) werden bewusst nicht
importiert (Auftrag: übergehen).
"""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from serts.paths import DATA_RAW


@dataclass(frozen=True)
class RawFile:
    src: str  # relativ zum Team-Ordner "Bad Lippspringe"
    dst: str  # relativ zu data/raw
    beschreibung: str
    pflicht: bool = True  # False = nur Dokumentation, Modell läuft ohne


RAW_FILES: list[RawFile] = [
    RawFile(
        "results netzberechnung.xlsx",
        "bad_lippspringe/results netzberechnung.xlsx",
        "Eigene Netzberechnung (Netz klein): Lastgang 2022 (8760 h), Netzverluste, Gebäudestatistik",
    ),
    RawFile(
        "results_gross.xlsx",
        "bad_lippspringe/results_gross.xlsx",
        "Eigene Netzberechnung (Netz groß, 877 Gebäude): Lastgang 2022 (8760 h), Netzverluste, Statistik",
    ),
    RawFile(
        "../AP 0 und Annahmen/KWW-Technikkatalog-Waermeplanung_08-2026_Version_1.1.xlsx",
        "kww/KWW-Technikkatalog-Waermeplanung_08-2026_Version_1.1.xlsx",
        "KWW Technikkatalog Wärmeplanung v1.1: Kosten/Lebensdauern (2026, netto, real); Erträge werden nicht übernommen",
    ),
    RawFile(
        "stundenwerte_TU_03028_19710401_20251231_hist/produkt_tu_stunde_19710401_20251231_03028.txt",
        "dwd/tu_03028/produkt_tu_stunde_19710401_20251231_03028.txt",
        "DWD Lufttemperatur/Feuchte stündlich, UTC",
    ),
    RawFile(
        "stundenwerte_TU_03028_19710401_20251231_hist/Metadaten_Parameter_tu_stunde_03028.txt",
        "dwd/tu_03028/Metadaten_Parameter_tu_stunde_03028.txt",
        "DWD Metadaten TU",
    ),
    RawFile(
        "stundenwerte_TU_03028_19710401_20251231_hist/Metadaten_Geographie_03028.txt",
        "dwd/tu_03028/Metadaten_Geographie_03028.txt",
        "DWD Stationskoordinaten",
    ),
    RawFile(
        "stundenwerte_ST_03028_row/produkt_st_stunde_19820101_20110831_03028.txt",
        "dwd/st_03028/produkt_st_stunde_19820101_20110831_03028.txt",
        "DWD Global-/Diffusstrahlung stündlich 1982-2011 (nur Klimavergleich)",
    ),
    RawFile(
        "stundenwerte_ST_03028_row/Metadaten_Parameter_st_stunde_03028.txt",
        "dwd/st_03028/Metadaten_Parameter_st_stunde_03028.txt",
        "DWD Metadaten ST",
    ),
    RawFile(
        "stundenwerte_EB_03028_19810101_20251231_hist/produkt_eb_stunde_19810101_20251231_03028.txt",
        "dwd/eb_03028/produkt_eb_stunde_19810101_20251231_03028.txt",
        "DWD Erdbodentemperatur 2-100 cm (optional: Netz-/PTES-Umgebung)",
    ),
]


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


def import_raw(source: Path, target: Path = DATA_RAW, overwrite: bool = False) -> list[str]:
    """Kopiert RAW_FILES und schreibt data/raw/MANIFEST.sha256. Gibt Logzeilen zurück."""
    lines: list[str] = []
    manifest: list[str] = []
    for rf in RAW_FILES:
        src = source / rf.src
        dst = target / rf.dst
        if not src.exists():
            if dst.exists():  # z. B. aus dem Git-Repository mitgeliefert (Netzberechnung, KWW)
                lines.append(f"vorhanden {rf.dst} (Quelle fehlt, Datei aus dem Repo)")
                manifest.append(f"{sha256(dst)}  {rf.dst}")
                continue
            if not rf.pflicht:
                lines.append(f"fehlt    {rf.dst} (optional, nur Dokumentation)")
                continue
            raise FileNotFoundError(f"Rohdatei fehlt: {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not overwrite:
            if sha256(dst) != sha256(src):
                raise RuntimeError(f"{dst} weicht von Quelle ab (overwrite=True zum Ersetzen)")
            lines.append(f"ok       {rf.dst}")
        else:
            shutil.copy2(src, dst)
            lines.append(f"kopiert  {rf.dst}")
        manifest.append(f"{sha256(dst)}  {rf.dst}")
    (target / "MANIFEST.sha256").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    return lines


def verify_raw(target: Path = DATA_RAW) -> list[str]:
    """Prüft data/raw gegen MANIFEST.sha256; gibt Liste der Abweichungen zurück."""
    mf = target / "MANIFEST.sha256"
    if not mf.exists():
        return ["MANIFEST.sha256 fehlt -> `serts import-raw` ausführen"]
    problems = []
    for line in mf.read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        p = target / rel
        if not p.exists():
            problems.append(f"fehlt: {rel}")
        elif sha256(p) != digest:
            problems.append(f"Prüfsumme weicht ab: {rel}")
    return problems
