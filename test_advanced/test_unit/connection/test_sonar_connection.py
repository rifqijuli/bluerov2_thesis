import pytest
import sys
from brping import Ping1D

import sys
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from main_sonar import get_sonar_distance

@pytest.fixture(scope="module")
def myPing():
    ping = Ping1D()
    ping.connect_udp("192.168.2.2", 9090)
    if ping.initialize() is False:
        pytest.skip("Sonar not reachable — is it connected?")
    return ping

def test_sonar_returns_value(myPing):
    distance = get_sonar_distance(myPing)
    assert distance is not None, "Failed to get distance from sonar"