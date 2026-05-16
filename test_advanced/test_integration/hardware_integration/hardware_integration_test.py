# tests/unit/test_camera.py
import pytest
import time
import sys
from pathlib import Path
from brping import Ping1D

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from camera.rov_camera import Video 
from main_sonar import get_sonar_distance
from pymavlink import mavutil
from main_rc_command import send_rc_command
from control import gripper

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

# ── Connection ────────────────────────────────────────────────────────────────
def test_heartbeat_received(master):
    assert master.target_system != 0

def test_motors_armed(master):
    assert master.motors_armed

# ── Gripper ───────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def gripper_init(master):
    return gripper.Gripper(master, 3, set_default=False)  # don't send on init

@pytest.fixture(scope="module")
def video():
    """Start real video stream once for all tests."""
    try:
        v = Video(port=5601)
    except Exception:
        pytest.skip("No frame received — is ROV connected?")

    timeout = 10
    start = time.time()
    while not v.frame_available():
        if time.time() - start > timeout:
            pytest.skip("No frame received — is ROV connected?")
        time.sleep(0.03)
    return v

@pytest.fixture(scope="module")
def myPing():
    ping = Ping1D()
    ping.connect_udp("192.168.2.2", 9090)
    if ping.initialize() is False:
        pytest.skip("Sonar not reachable — is it connected?")
    return ping
    

def test_frame_is_available(video, myPing, master, gripper_init):
    assert video.frame_available()

    distance = get_sonar_distance(myPing)
    assert distance > 0, "Distance should be positive"

    gripper_init.open()
    time.sleep(0.5)
    while master.recv_match(type='SERVO_OUTPUT_RAW', blocking=False):
        pass  # flush stale
    msg = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=True, timeout=3)
    assert msg is not None
    assert msg.servo11_raw == 1600

    gripper_init.close()
    time.sleep(0.5)
    while master.recv_match(type='SERVO_OUTPUT_RAW', blocking=False):
        pass  # flush stale
    msg = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=True, timeout=3)
    assert msg is not None
    assert msg.servo11_raw == 1100


if __name__ == "__main__":
    pytest.main([__file__])
