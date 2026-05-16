# tests/unit/test_camera.py
import pytest
import time

from pymavlink import mavutil

import sys
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from main_rc_command import send_rc_command
from control import gripper

# ArduSub channel mapping
CH_PITCH    = 0 # 0 is pitch up (1900) or down (1100)
CH_ROLL     = 1 # 1 is roll right (1900) or left (1100)
CH_THROTTLE = 2 # 2 is vertical up (1900) or down (1100)
CH_YAW      = 3 # 3 is yaw right (1900) or left (1100)
CH_FORWARD  = 4 # 4 is forward (1900) or backward (1100)
CH_LATERAL  = 5 # 5 is lateral right (1900) or left (1100)

PWM_NEUTRAL = 1500
RC_CHANNELS = 18

@pytest.fixture(scope="module")
def master():
    m = mavutil.mavlink_connection('udpin:0.0.0.0:14550')

    heartbeat = m.wait_heartbeat(timeout=5)  # wait max 5 seconds
    if heartbeat is None:
        pytest.skip("BlueROV2 not connected — skipping RC gripper tests")
    
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

# ── Gripper ───────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def gripper_init(master):
    return gripper.Gripper(master, 3, set_default=False)  # don't send on init

def test_gripper_open(master, gripper_init):
    gripper_init.open()
    time.sleep(0.5)
    while master.recv_match(type='SERVO_OUTPUT_RAW', blocking=False):
        pass  # flush stale
    msg = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=True, timeout=3)
    assert msg is not None
    assert msg.servo11_raw == 1600

def test_gripper_close(master, gripper_init):
    gripper_init.close()
    time.sleep(0.5)
    while master.recv_match(type='SERVO_OUTPUT_RAW', blocking=False):
        pass  # flush stale
    msg = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=True, timeout=3)
    assert msg is not None
    assert msg.servo11_raw == 1100

if __name__ == "__main__":
    pytest.main([__file__])