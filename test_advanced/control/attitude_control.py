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

def get_current_depth(master):
    # Blocks up to 1 s waiting for latest HUD data
    msg = master.recv_match(type='VFR_HUD', blocking=True, timeout=1)
    if not msg:
        return None

    # In ArduSub: msg.alt is depth (m, positive down)
    depth_m = msg.alt
    return depth_m
