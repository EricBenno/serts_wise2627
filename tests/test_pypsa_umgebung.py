"""Rauchtest: PyPSA + HiGHS lösen ein Mini-Netz (Abnahme M0 Umgebung)."""

import pandas as pd
import pytest


@pytest.mark.solver
def test_pypsa_highs_mini_netz():
    import pypsa

    n = pypsa.Network()
    n.set_snapshots(pd.RangeIndex(3))
    n.add("Bus", "heat")
    n.add("Load", "last", bus="heat", p_set=[1.0, 2.0, 1.5])
    n.add("Generator", "billig", bus="heat", p_nom=1.5, marginal_cost=10)
    n.add("Generator", "teuer", bus="heat", p_nom=5, marginal_cost=100)
    status, _ = n.optimize(solver_name="highs")
    assert status == "ok"
    # Handrechnung: billig 1,0+1,5+1,5 = 4,0 MWh, teuer 0,5 MWh -> 40 + 50 = 90
    assert n.objective == pytest.approx(90.0)
