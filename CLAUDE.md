# Hinweise für Agenten

- Leitlinie des Teams: **so simpel wie möglich, so komplex wie nötig.** Das Modell muss für das Team
  verständlich und anpassbar bleiben. `../obsidian/AGENT_BRIEFING_SERTS.md` ist Orientierung, nicht Pflicht.
  Jede Abweichung/Vereinfachung in `docs/entscheidungen.md` anhängen.
- Stand, Modellbild und nächste Schritte: `docs/struktur.md`. Datenbasis: `docs/datenbasis_bad_lippspringe.md`.
- Umgebung: `uv sync`, Tests `uv run pytest`, CLI `uv run serts --help`. Windows/PowerShell.
- Keine Zahlen erfinden: Parameter nur in `config/base.yaml` mit `einheit`, `status`, `quelle`; unbekannt = `null` + `status: offen`.
  Nach Änderungen `uv run serts annahmen` (erzeugt `docs/annahmen.md`).
- Rohdaten in `data/raw` nie verändern. Jede neue Nebenbedingung bekommt einen Mini-Netz-Test.
