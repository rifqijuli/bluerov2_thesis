import pytest
import numpy as np

import sys
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tracking import pixel_convert
from control.pwm_threshold import pwm_threshold

threshold = pwm_threshold(max_pwm=1600, min_pwm=1400)

def test_below_threshold():
    check = threshold.check_pwm(1300)
    assert check == 1400

def test_above_threshold():
    check = threshold.check_pwm(1700)
    assert check == 1600

def test_within_threshold():
    check = threshold.check_pwm(1500)
    assert check == 1500
