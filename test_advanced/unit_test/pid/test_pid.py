import pytest
import sys
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from control.pid_control import PIDController

# --- Proportional only ---
def test_proportional_only():
    pid = PIDController(Kp=1.0, Ki=0, Kd=0, setpoint=10)
    output = pid.compute(process_variable=0, dt=1.0)
    # error = 10 - 0 = 10, P = 1.0 * 10 = 10
    assert output == pytest.approx(10.0)

# --- Integral accumulates over time ---
def test_integral_accumulates():
    pid = PIDController(Kp=0, Ki=1.0, Kd=0, setpoint=10)
    pid.compute(process_variable=0, dt=1.0)  # integral = 10
    output = pid.compute(process_variable=0, dt=1.0)  # integral = 20
    assert output == pytest.approx(20.0)

# --- Derivative on changing error ---
def test_derivative_on_error_change():
    pid = PIDController(Kp=0, Ki=0, Kd=1.0, setpoint=10)
    pid.compute(process_variable=0, dt=1.0)   # prev_error = 10
    output = pid.compute(process_variable=5, dt=1.0)
    # error = 5, derivative = (5 - 10) / 1.0 = -5
    assert output == pytest.approx(-5.0)

# --- Zero error → zero output ---
def test_zero_error():
    pid = PIDController(Kp=1.0, Ki=1.0, Kd=1.0, setpoint=5)
    output = pid.compute(process_variable=5, dt=1.0)
    assert output == pytest.approx(0.0)

# --- Combined P+I+D ---
def test_combined_output():
    pid = PIDController(Kp=1.0, Ki=1.0, Kd=1.0, setpoint=10)
    output = pid.compute(process_variable=0, dt=1.0)
    # error=10, P=10, I=10*1=10, D=(10-0)/1=10 → 30
    assert output == pytest.approx(30.0)

if __name__ == "__main__":
    pytest.main()