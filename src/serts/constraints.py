"""Zusatz-Constraints über ``extra_functionality`` (linopy), BRF §3.2-3.4. Stand: Gerüst.

Jede Constraint bekommt einen Test mit Mini-Netz und Handrechnung (BRF §10.4).

1. Volumensumme:      e_V85(t) + e_V45(t) + e_V10(t) = V                    für alle t
2. Verluste:          p_verlust_oben(t)  = lambda * e_V85(t)
                      p_verlust_mitte(t) = lambda * e_V45(t)
3. Kollektorfläche:   p_hi(t)*P_lo(t) + p_lo(t)*P_hi(t) <= A*P_hi(t)*P_lo(t)  (nur wo P_hi, P_lo > 0;
                      sonst p_hi = 0 bzw. p_lo = 0 über p_max_pu)
4. WP-Kapazität:      p_hp_air(t) + p_hp_ptes(t) <= P_WP  (bei p_nom_extendable gegen Investvariable)

Hinweis zu 3: p_hi/p_lo sind Generator-Dispatch in MW; A in denselben Einheiten wie p_nom
(A[m2]*1e-3 MW), P_* = p_max_pu.
"""

from __future__ import annotations


def extra_functionality(n, snapshots, *, V_m3: float, verlustrate: float) -> None:
    """Wird an ``n.optimize(extra_functionality=...)`` übergeben (per functools.partial)."""
    raise NotImplementedError("M3: Constraints noch nicht umgesetzt")
