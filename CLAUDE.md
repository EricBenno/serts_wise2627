# Hinweise für Agenten

- Maßgeblich: `../obsidian/AGENT_BRIEFING_SERTS.md` (Vorrang), dann `../obsidian/Waermenetz_PTES_Modellschema_v3.md`.
  Abweichungen davon stehen in `docs/entscheidungen.md` – dort neue Einträge anhängen.
- Stand und nächste Schritte: `docs/struktur.md`. Datenbasis: `docs/datenbasis_bad_lippspringe.md`.
- Umgebung: `uv sync`, Tests `uv run pytest`, CLI `uv run serts --help`. Windows/PowerShell.
- Keine Zahlen erfinden: Parameter nur in `config/base.yaml` mit `einheit`, `status`, `quelle`; unbekannt = `null` + `status: offen`.
  Nach Änderungen `uv run serts annahmen` (erzeugt `docs/annahmen.md`).
- Rohdaten in `data/raw` nie verändern. Jede neue Constraint bekommt einen Mini-Netz-Test mit Handrechnung.
