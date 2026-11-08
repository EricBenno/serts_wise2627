import pytest

from serts.config import load_config
from serts.paths import DATA_RAW


@pytest.fixture(scope="session")
def cfg():
    return load_config()


def _need(rel: str):
    p = DATA_RAW / rel
    if not p.exists():
        pytest.skip(f"Rohdatei fehlt ({rel}) -> `uv run serts import-raw`")
    return p


@pytest.fixture(scope="session")
def netzberechnung_xlsx():
    return _need("bad_lippspringe/results netzberechnung.xlsx")


@pytest.fixture(scope="session")
def dwd_tu():
    return _need("dwd/tu_03028/produkt_tu_stunde_19710401_20251231_03028.txt")
