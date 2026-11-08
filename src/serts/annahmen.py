"""Erzeugt docs/annahmen.md aus config/base.yaml (Single Source of Truth = YAML)."""

from __future__ import annotations

from collections import Counter

from serts.config import Config


def _fmt(v) -> str:
    if v is None:
        return "**offen**"
    if isinstance(v, float):
        return f"{v:g}"
    return str(v).replace("|", "/")


def annahmen_markdown(cfg: Config) -> str:
    params = cfg.params()
    count = Counter(p["status"] for _, p in params)
    lines = [
        "# Annahmentabelle",
        "",
        "> Automatisch erzeugt aus `config/base.yaml` mit `serts annahmen`. Nicht von Hand ändern.",
        "",
        "Status: "
        + ", ".join(f"{k} {count.get(k, 0)}" for k in ("belegt", "vorgabe", "annahme", "offen")),
        "",
    ]
    section = None
    for path, p in params:
        top = path.split(".")[0]
        if top != section:
            section = top
            lines += [
                "",
                f"## {top}",
                "",
                "| Parameter | Wert | Einheit | Status | Quelle / Begründung | Sensitivität | Hinweis |",
                "|---|---|---|---|---|---|---|",
            ]
        sens = ", ".join(_fmt(s) for s in p.get("sens", []) or [])
        lines.append(
            f"| `{path}` | {_fmt(p.get('wert'))} | {_fmt(p.get('einheit'))} | {p['status']} | "
            f"{_fmt(p.get('quelle') or '')} | {sens} | {_fmt(p.get('hinweis') or '')} |"
        )
    return "\n".join(lines) + "\n"
