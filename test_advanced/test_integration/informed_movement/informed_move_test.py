import pytest
import numpy as np
import time
import sys

from pymavlink import mavutil
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tracking.yolo_track import coordinate
from control.pid_control import PIDController
from main_rc_command import send_rc_command
from control.pwm_threshold import pwm_threshold
from tracking import pixel_convert

frame = np.zeros((720, 1280, 3), dtype=np.uint8)

# ArduSub channel mapping
CH_PITCH    = 0 # 0 is pitch up (1900) or down (1100)
CH_ROLL     = 1 # 1 is roll right (1900) or left (1100)
CH_THROTTLE = 2 # 2 is vertical up (1900) or down (1100)
CH_YAW      = 3 # 3 is yaw right (1900) or left (1100)
CH_FORWARD  = 4 # 4 is forward (1900) or backward (1100)
CH_LATERAL  = 5 # 5 is lateral right (1900) or left (1100)

PWM_NEUTRAL = 1500
RC_CHANNELS = 18

yaw_threshold = pwm_threshold(max_pwm=1800, min_pwm=1200)

@pytest.fixture(scope="module")
def master():
    m = mavutil.mavlink_connection('udpin:0.0.0.0:14550')

    heartbeat = m.wait_heartbeat(timeout=5)  # wait max 5 seconds
    if heartbeat is None:
        pytest.skip("BlueROV2 not connected — skipping RC command tests")
    
    m.arducopter_arm()
    m.motors_armed_wait()

    DEPTH_HOLD = 'ALT_HOLD'
    DEPTH_HOLD_MODE = m.mode_mapping()[DEPTH_HOLD]
    while not m.wait_heartbeat().custom_mode == DEPTH_HOLD_MODE:
        m.set_mode(DEPTH_HOLD)

    return m

def send_and_receive(master, channel, pwm):
    rc_pwm = [PWM_NEUTRAL] * RC_CHANNELS
    rc_pwm[channel] = pwm

    # Flush stale messages first
    while master.recv_match(type='SERVO_OUTPUT_RAW', blocking=False):
        pass

    # Keep sending + wait for fresh response
    timeout = time.time() + 3.0
    while time.time() < timeout:
        send_rc_command(master, rc_pwm)   # ← send every iteration
        time.sleep(0.05)                  # 20Hz, same as real implementation
        msg = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=False)
        if msg:
            return msg
    return None


# ── Connection ────────────────────────────────────────────────────────────────
def test_heartbeat_received(master):
    assert master.target_system != 0

def test_motors_armed(master):
    assert master.motors_armed


# ── Yaw ───────────────────────────────────────────────────────────────────────
def test_coordinate_to_pid_yaw_right(master):
    coord = coordinate(x_coord=320, y_coord=360, frame=frame)
    result = coord.difference_to_frame()

    assert result.x == pytest.approx(-320.0)
    assert result.y == pytest.approx(0.0)

    yaw_result = pixel_convert.pixel_to_pwm(result.x,"yaw",yaw_threshold)
    assert yaw_result == pytest.approx(-37.5)

    pid_yaw = PIDController(Kp=4.0, Ki=0, Kd=0, setpoint=0)
    output_yaw = pid_yaw.compute(process_variable=yaw_result, dt=0.1)

    assert isinstance(output_yaw, float)
    assert output_yaw == pytest.approx(150.0)  # Kp=4.0, error=-37.5 → output=150.0

    msg = send_and_receive(master, CH_YAW, yaw_threshold.check_pwm(PWM_NEUTRAL - output_yaw))
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo2_raw > PWM_NEUTRAL  # T2 follows
    assert msg.servo4_raw > PWM_NEUTRAL  # T4 follows
    assert msg.servo1_raw < PWM_NEUTRAL  # T1 opposes
    assert msg.servo3_raw < PWM_NEUTRAL  # T3 opposes

def test_coordinate_to_pid_yaw_left(master):
    coord = coordinate(x_coord=960, y_coord=360, frame=frame)
    result = coord.difference_to_frame()

    assert result.x == pytest.approx(320.0)
    assert result.y == pytest.approx(0.0)

    yaw_result = pixel_convert.pixel_to_pwm(result.x,"yaw",yaw_threshold)
    assert yaw_result == pytest.approx(37.5)

    pid_yaw = PIDController(Kp=4.0, Ki=0, Kd=0, setpoint=0)
    output_yaw = pid_yaw.compute(process_variable=yaw_result, dt=0.1)

    assert isinstance(output_yaw, float)
    assert output_yaw == pytest.approx(-150.0) # Kp=4.0, error=37.5 → output=-150.0

    msg = send_and_receive(master, CH_YAW, yaw_threshold.check_pwm(PWM_NEUTRAL - output_yaw))
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo2_raw < PWM_NEUTRAL  # T2 follows
    assert msg.servo4_raw < PWM_NEUTRAL  # T4 follows
    assert msg.servo1_raw > PWM_NEUTRAL  # T1 opposes
    assert msg.servo3_raw > PWM_NEUTRAL  # T3 opposes

if __name__ == "__main__":
    pytest.main()
