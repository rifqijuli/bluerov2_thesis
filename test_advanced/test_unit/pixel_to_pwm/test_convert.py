import pytest
import numpy as np

import sys
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tracking import pixel_convert
from control.pwm_threshold import pwm_threshold

threshold_low = pwm_threshold(max_pwm=1600, min_pwm=1400)

threshold_high = pwm_threshold(max_pwm=1900, min_pwm=1100)

def test_yaw_low_edge_positive():
    yaw_result = pixel_convert.pixel_to_pwm(640,"yaw",threshold_low)
    assert yaw_result == pytest.approx(25.0)

def test_yaw_low_edge_negative():
    yaw_result = pixel_convert.pixel_to_pwm(-640,"yaw",threshold_low)
    assert yaw_result == pytest.approx(-25.0)

def test_yaw_high_edge_positive():
    yaw_result = pixel_convert.pixel_to_pwm(640,"yaw",threshold_high)
    assert yaw_result == pytest.approx(100.0)

def test_yaw_high_edge_negative():
    yaw_result = pixel_convert.pixel_to_pwm(-640,"yaw",threshold_high)
    assert yaw_result == pytest.approx(-100.0)

def test_pitch_high_edge_positive():
    pitch_result = pixel_convert.pixel_to_pwm(360,"pitch",threshold_high)
    assert pitch_result == pytest.approx(200.0)

def test_pitch_high_edge_negative():
    pitch_result = pixel_convert.pixel_to_pwm(-360,"pitch",threshold_high)
    assert pitch_result == pytest.approx(-200.0)

def test_pitch_low_edge_positive():
    pitch_result = pixel_convert.pixel_to_pwm(360,"pitch",threshold_low)
    assert pitch_result == pytest.approx(50.0)

def test_pitch_low_edge_negative():
    pitch_result = pixel_convert.pixel_to_pwm(-360,"pitch",threshold_low)
    assert pitch_result == pytest.approx(-50.0)

def test_yaw_center():
    assert pixel_convert.pixel_to_pwm(0, "yaw", threshold_low) == pytest.approx(0.0)

def test_pitch_center():
    assert pixel_convert.pixel_to_pwm(0, "pitch", threshold_low) == pytest.approx(0.0)

if __name__ == "__main__":
    pytest.main()
