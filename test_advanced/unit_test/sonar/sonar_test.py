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

def test_sonar_is_a_number(myPing):
    distance = get_sonar_distance(myPing)
    assert isinstance(distance, float)

def test_sonar_is_positive(myPing):
    distance = get_sonar_distance(myPing)
    assert distance > 0, "Distance should be positive"

def test_sonar_is_in_meters(myPing):
    distance = get_sonar_distance(myPing)
    assert distance < 100, "Distance looks wrong — expected meters not mm"

def test_sonar_confidence_is_valid(myPing):
    data = myPing.get_distance()
    assert 0 <= data["confidence"] <= 100, "Confidence should be 0-100%"
    
if __name__ == "__main__":
    pytest.main()