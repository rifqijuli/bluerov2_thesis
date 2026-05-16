# tests/unit/test_camera.py
import pytest
import time

from pymavlink import mavutil

import sys
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from main_rc_command import send_rc_command

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
def test_yaw_right(master):
    msg = send_and_receive(master, CH_YAW, 1800)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo2_raw > PWM_NEUTRAL  # T2 follows
    assert msg.servo4_raw > PWM_NEUTRAL  # T4 follows
    assert msg.servo1_raw < PWM_NEUTRAL  # T1 opposes
    assert msg.servo3_raw < PWM_NEUTRAL  # T3 opposes

def test_yaw_left(master):
    msg = send_and_receive(master, CH_YAW, 1200)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo2_raw < PWM_NEUTRAL  # T2 follows
    assert msg.servo4_raw < PWM_NEUTRAL  # T4 follows
    assert msg.servo1_raw > PWM_NEUTRAL  # T1 opposes
    assert msg.servo3_raw > PWM_NEUTRAL  # T3 opposes


# ── Pitch ─────────────────────────────────────────────────────────────────────
def test_pitch_forward(master):
    msg = send_and_receive(master, CH_PITCH, 1800)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo5_raw > PWM_NEUTRAL  # T5 follows
    assert msg.servo8_raw > PWM_NEUTRAL  # T8 follows
    assert msg.servo6_raw < PWM_NEUTRAL  # T6 opposes
    assert msg.servo7_raw < PWM_NEUTRAL  # T7 opposes

def test_pitch_backward(master):
    msg = send_and_receive(master, CH_PITCH, 1200)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo5_raw < PWM_NEUTRAL  # T5 follows
    assert msg.servo8_raw < PWM_NEUTRAL  # T8 follows
    assert msg.servo6_raw > PWM_NEUTRAL  # T6 opposes
    assert msg.servo7_raw > PWM_NEUTRAL  # T7 opposes

# ── Throttle ──────────────────────────────────────────────────────────────────
def test_throttle_up(master):
    msg = send_and_receive(master, CH_THROTTLE, 1800)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo5_raw > PWM_NEUTRAL
    assert msg.servo6_raw < PWM_NEUTRAL
    assert msg.servo7_raw < PWM_NEUTRAL
    assert msg.servo8_raw > PWM_NEUTRAL

def test_throttle_down(master):
    msg = send_and_receive(master, CH_THROTTLE, 1200)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo5_raw < PWM_NEUTRAL
    assert msg.servo6_raw > PWM_NEUTRAL
    assert msg.servo7_raw > PWM_NEUTRAL
    assert msg.servo8_raw < PWM_NEUTRAL


# ── Forward / Backward ────────────────────────────────────────────────────────
def test_forward(master):
    msg = send_and_receive(master, CH_FORWARD, 1800)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo1_raw > PWM_NEUTRAL  # T1 follows
    assert msg.servo2_raw > PWM_NEUTRAL  # T2 follows
    assert msg.servo3_raw > PWM_NEUTRAL  # T3 follows
    assert msg.servo4_raw > PWM_NEUTRAL  # T4 follows

def test_backward(master):
    msg = send_and_receive(master, CH_FORWARD, 1200)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo1_raw < PWM_NEUTRAL
    assert msg.servo2_raw < PWM_NEUTRAL
    assert msg.servo3_raw < PWM_NEUTRAL
    assert msg.servo4_raw < PWM_NEUTRAL


# ── Lateral ───────────────────────────────────────────────────────────────────
def test_lateral_right(master):
    msg = send_and_receive(master, CH_LATERAL, 1800)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo2_raw > PWM_NEUTRAL  # T2 follows
    assert msg.servo3_raw > PWM_NEUTRAL  # T3 follows
    assert msg.servo1_raw < PWM_NEUTRAL  # T1 opposes
    assert msg.servo4_raw < PWM_NEUTRAL  # T4 opposes

def test_lateral_left(master):
    msg = send_and_receive(master, CH_LATERAL, 1200)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert msg.servo2_raw < PWM_NEUTRAL
    assert msg.servo3_raw < PWM_NEUTRAL
    assert msg.servo1_raw > PWM_NEUTRAL
    assert msg.servo4_raw > PWM_NEUTRAL


# ── All neutral ───────────────────────────────────────────────────────────────
def test_all_neutral(master):
    rc_pwm = [PWM_NEUTRAL] * RC_CHANNELS
    send_rc_command(master, rc_pwm)
    time.sleep(0.1)
    msg = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=False)
    assert msg is not None, "No SERVO_OUTPUT_RAW received"
    assert 1400 <= msg.servo1_raw <= 1600
    assert 1400 <= msg.servo2_raw <= 1600
    assert 1400 <= msg.servo3_raw <= 1600
    assert 1400 <= msg.servo4_raw <= 1600
    assert 1400 <= msg.servo5_raw <= 1600
    assert 1400 <= msg.servo6_raw <= 1600
    assert 1400 <= msg.servo7_raw <= 1600
    assert 1400 <= msg.servo8_raw <= 1600

if __name__ == "__main__":
    pytest.main([__file__])