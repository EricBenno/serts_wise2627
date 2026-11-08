"""Laden, Zusammenführen und Prüfen der Konfiguration.

Regeln (BRF §4, §10):
- Jeder Parameter hat ``wert``, ``einheit``, ``status`` und ``quelle``.
- ``status: offen`` <=> ``wert: null``.
- ``Config.get()`` bricht mit :class:`OffenerParameter` ab, wenn der Wert ``null`` ist –
  es gibt keine stillen Defaults.
- Szenarien enthalten nur Abweichungen. Ein Szenario darf einen Parameter als Mapping
  (z. B. ``{wert: 40, quelle: ..., status: ...}``) oder als Skalar (nur ``wert``) überschreiben.
"""

from __future__ import annotations

import copy
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from serts.paths import CONFIG_DIR, SCENARIO_DIR

STATUS = ("belegt", "vorgabe", "annahme", "offen")
PARAM_KEYS = {"wert", "einheit", "status", "quelle", "sens", "hinweis"}


class ConfigError(ValueError):
    """Formal ungültige Konfiguration."""


class OffenerParameter(ConfigError):
    """Ein ergebnisrelevanter Parameter ist noch ``null`` (status: offen)."""


def is_param(node: Any) -> bool:
    return isinstance(node, dict) and "wert" in node


def iter_params(tree: dict, prefix: str = "") -> Iterator[tuple[str, dict]]:
    """Alle Parameter als (punkt.pfad, param-dict)."""
    for key, node in tree.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if is_param(node):
            yield path, node
        elif isinstance(node, dict):
            yield from iter_params(node, path)


def deep_merge(base: dict, override: dict, _path: str = "") -> dict:
    """Szenario ``override`` in ``base`` einmischen (gibt neue Struktur zurück)."""
    out = copy.deepcopy(base)
    for key, val in override.items():
        path = f"{_path}.{key}" if _path else str(key)
        if key not in out:
            if _path != "meta" and key != "meta":
                raise ConfigError(f"Szenario setzt unbekannten Schlüssel '{path}' (Tippfehler?)")
            out[key] = copy.deepcopy(val)
            continue
        target = out[key]
        if is_param(target):
            if isinstance(val, dict):
                unknown = set(val) - PARAM_KEYS
                if unknown:
                    raise ConfigError(f"{path}: unbekannte Felder {sorted(unknown)}")
                target.update(copy.deepcopy(val))
            else:
                target["wert"] = copy.deepcopy(val)
                target["hinweis"] = f"Szenario-Wert (Basis-Quelle: {target.get('quelle', '')})"
        elif isinstance(target, dict) and isinstance(val, dict):
            out[key] = deep_merge(target, val, path)
        else:
            out[key] = copy.deepcopy(val)
    return out


def validate(tree: dict) -> list[str]:
    """Formale Prüfung; gibt Liste von Fehlermeldungen zurück (leer = ok)."""
    errors: list[str] = []
    for path, p in iter_params(tree):
        unknown = set(p) - PARAM_KEYS
        if unknown:
            errors.append(f"{path}: unbekannte Felder {sorted(unknown)}")
        status = p.get("status")
        if status not in STATUS:
            errors.append(f"{path}: status '{status}' nicht in {STATUS}")
        if "einheit" not in p:
            errors.append(f"{path}: 'einheit' fehlt")
        if p.get("wert") is None and status != "offen":
            errors.append(f"{path}: wert ist null, status muss 'offen' sein")
        if status == "offen" and p.get("wert") is not None:
            errors.append(f"{path}: status 'offen', aber wert gesetzt -> status anpassen")
        if status != "offen" and not str(p.get("quelle") or "").strip():
            errors.append(f"{path}: quelle/Begründung fehlt (status {status})")
    return errors


@dataclass
class Config:
    tree: dict
    name: str = "base"
    sources: list[str] = field(default_factory=list)

    # -- Zugriff ---------------------------------------------------------------
    def node(self, dotted: str) -> Any:
        node: Any = self.tree
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                raise KeyError(f"Parameter '{dotted}' existiert nicht (bei '{part}')")
            node = node[part]
        return node

    def get(self, dotted: str) -> Any:
        """Wert eines Parameters. Bricht ab, wenn der Wert offen (null) ist."""
        node = self.node(dotted)
        if not is_param(node):
            return node
        if node["wert"] is None:
            hint = node.get("hinweis", "")
            raise OffenerParameter(
                f"Parameter '{dotted}' [{node.get('einheit', '')}] ist offen (null). "
                f"Bitte mit Quelle in config/base.yaml oder im Szenario setzen. {hint}".strip()
            )
        return node["wert"]

    def get_optional(self, dotted: str) -> Any:
        """Wie get(), liefert aber None statt Abbruch (nur für Berichte/Plots!)."""
        node = self.node(dotted)
        return node["wert"] if is_param(node) else node

    def require(self, keys: list[str]) -> None:
        """Alle Schlüssel prüfen und gesammelt abbrechen (vor einem Lauf aufrufen)."""
        missing = []
        for key in keys:
            node = self.node(key)
            if is_param(node) and node["wert"] is None:
                missing.append(key)
        if missing:
            raise OffenerParameter(
                "Lauf abgebrochen, offene ergebnisrelevante Parameter:\n  - "
                + "\n  - ".join(missing)
            )

    def params(self) -> list[tuple[str, dict]]:
        return list(iter_params(self.tree))

    def offene(self) -> list[str]:
        return [path for path, p in self.params() if p.get("wert") is None]

    def dump(self, path: Path) -> None:
        payload = {"_szenario": self.name, "_quellen": self.sources, **self.tree}
        path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), "utf-8")


def _read_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: Wurzel muss ein Mapping sein")
    return data


def resolve_scenario(scenario: str | Path) -> Path:
    p = Path(scenario)
    if p.suffix in {".yaml", ".yml"} and p.exists():
        return p
    candidate = SCENARIO_DIR / f"{scenario}.yaml"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Szenario '{scenario}' nicht gefunden (gesucht: {candidate})")


def load_config(
    scenario: str | Path | None = None, base: Path = CONFIG_DIR / "base.yaml"
) -> Config:
    tree = _read_yaml(base)
    sources = [str(base)]
    name = "base"
    if scenario is not None:
        spath = resolve_scenario(scenario)
        tree = deep_merge(tree, _read_yaml(spath))
        sources.append(str(spath))
        name = spath.stem
    errors = validate(tree)
    if errors:
        raise ConfigError("Ungültige Konfiguration:\n  - " + "\n  - ".join(errors))
    return Config(tree=tree, name=name, sources=sources)
