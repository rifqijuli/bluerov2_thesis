"""
Example of how to set target depth in depth hold mode with pymavlink
"""

import time
import math
# Import mavutil
from pymavlink import mavutil
# Imports for attitude
from pymavlink.quaternion import QuaternionBase

def set_target_attitude(roll, pitch, yaw, master, boot_time):
    """ Sets the target attitude while in depth-hold mode.

    'roll', 'pitch', and 'yaw' are angles in degrees.

    """
    master.mav.set_attitude_target_send(
        int(1e3 * (time.time() - boot_time)), # ms since boot
        master.target_system, master.target_component,
        # allow throttle to be controlled by depth_hold mode
        mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_THROTTLE_IGNORE,
        # -> attitude quaternion (w, x, y, z | zero-rotation is 1, 0, 0, 0)
        QuaternionBase([math.radians(angle) for angle in (roll, pitch, yaw)]),
        0, 0, 0, 0 # roll rate, pitch rate, yaw rate, thrust
    )

def get_current_yaw(master):
    msg = master.recv_match(type='ATTITUDE', blocking=True, timeout=1)
    if not msg:
        return None
    
    # msg.yaw is in radians, format to degree
    yaw_rad = msg.yaw
    yaw_deg = math.degrees(yaw_rad)
    return yaw_deg

def get_current_pitch(master):
    msg = master.recv_match(type='ATTITUDE', blocking=True, timeout=1)
    if not msg:
        return None
    
    # msg.pitch is in radians, format to degree
    pitch_rad = msg.pitch
    pitch_deg = math.degrees(pitch_rad)
    return pitch_deg

def get_current_depth(master):
    # Blocks up to 1 s waiting for latest HUD data
    msg = master.recv_match(type='VFR_HUD', blocking=True, timeout=1)
    if not msg:
        return None

    # In ArduSub: msg.alt is depth (m, positive down)
    depth_m = msg.alt
    return depth_m

def get_current_pwm(master):
    msg = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=True)
    if not msg:
        return None
    
    servo_dict = msg.to_dict()
    pwms = [
        servo_dict.get('servo1_raw', 0),
        servo_dict.get('servo2_raw', 0), 
        servo_dict.get('servo3_raw', 0),
        servo_dict.get('servo4_raw', 0),
        servo_dict.get('servo5_raw', 0),
        servo_dict.get('servo6_raw', 0),
        servo_dict.get('servo7_raw', 0),
        servo_dict.get('servo8_raw', 0)
    ]
    return pwms

def set_multi_rc_channel_pwm(master, channels_pwm):
    rc_channel_values = [65535 for _ in range(18)]
    for ch, pwm in channels_pwm.items():
        if ch < 1 or ch > 18:
            print(f"Channel {ch} does not exist.")
            continue
        rc_channel_values[ch - 1] = pwm
        master.mav.rc_channels_override_send(
            master.target_system,               
            master.target_component,             
            *rc_channel_values)                  