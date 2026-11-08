"""Kennzahlen (Outputs C im Schema) und Regel-Checks (BRF §7).

Speicherdefinitionen wie Solites 2019 (BRF §6):
    eta     = (Q_out + dQ) / Q_in
    Verlust = Q_in - Q_out - dQ
    Zyklen  = Q_out / Kapazität,  Kapazität = V * c * (T_max - T_min)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Speicherbilanz:
    q_in: float  # MWh Beladung
    q_out: float  # MWh Entladung (inkl. WP-Quellwärme)
    dq: float  # MWh Inhaltsänderung Ende - Anfang (zyklisch: 0)

    @property
    def verluste(self) -> float:
        return self.q_in - self.q_out - self.dq

    @property
    def wirkungsgrad(self) -> float:
        return (self.q_out + self.dq) / self.q_in

    @property
    def verlustanteil(self) -> float:
        return self.verluste / self.q_in


def kapazitaet_MWh(volumen_m3: float, c: float, t_max: float, t_min: float) -> float:
    return volumen_m3 * c * (t_max - t_min)


def zyklen(q_out: float, kapazitaet: float) -> float:
    return q_out / kapazitaet


def solaranteil(direkt: float, ptes_direkt: float, wp_quelle_ptes: float, bedarf: float) -> dict:
    """Solaranteil getrennt (AP 0 Mittel). WP-Strom zählt NICHT als Solar (SCH D5)."""
    return {
        "solar_direkt": direkt / bedarf,
        "solar_ptes_direkt": ptes_direkt / bedarf,
        "solar_wp_quelle": wp_quelle_ptes / bedarf,
        "solar_gesamt": (direkt + ptes_direkt + wp_quelle_ptes) / bedarf,
    }


# TODO M3/M5: Funktionen, die die Größen aus einem gelösten pypsa.Network ziehen
# (Links 'laden_*', 'entladen_direkt', 'hp_ptes' bus2, Abregelung sol_hi/sol_lo, Caps) und
# die Regel-Checks aus BRF §7 ausgeben.
