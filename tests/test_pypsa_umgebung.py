"""Rauchtest: PyPSA + HiGHS lösen ein Mini-Netz (Abnahme M0 Umgebung)."""

import pandas as pd
import pytest

from serts.network import pool_links


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


def test_pool_links_vorzeichen(cfg):
    links = {d["name"]: d for d in pool_links(cfg)}
    c = 1.163e-3
    assert links["laden_hi_aus10"]["efficiency2"] == pytest.approx(-75 * c)
    assert links["entladen_direkt"]["efficiency2"] == pytest.approx(40 * c)
    assert links["wp_quelle_ptes"]["efficiency2"] == pytest.approx(35 * c)
