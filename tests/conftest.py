"""Tests's conftest file."""
import pytest
from colejorz import StationMaster


@pytest.fixture
def stationmaster():
    """Stationmaster fixture."""
    smstr = StationMaster()
    yield smstr
    smstr.exit()
