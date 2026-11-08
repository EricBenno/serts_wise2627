"""Zentrale Pfade. Alle Pfade relativ zur Repo-Wurzel, keine absoluten Pfade im Code."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
SCENARIO_DIR = CONFIG_DIR / "scenarios"
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_REFERENCE = ROOT / "data" / "reference"
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"

# Ordner mit den Originaldaten des Teams (Geschwister-Ordner der Repo-Wurzel)
DEFAULT_RAW_SOURCE = ROOT.parent / "Bad Lippspringe"
