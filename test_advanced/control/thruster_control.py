import time
from pymavlink import mavutil

def set_thruster_control(master, forward, strafe, vertical, yaw):
    master.mav.manual_control_send(
        master.target_system,
        forward,  # Forward (-1000-1000, 0 is neutral (no forward/backward))
        strafe,   # Strafe (-1000-1000, 0 is neutral)
        vertical, # Vertical (0 -1000, 500 is neutral)
        yaw,      # Yaw (-1000-1000, 0 is neutral)
        0         # No buttons
    )

def set_manual(master):
    # set the desired operating mode
    MANUAL = 'MANUAL'
    MANUAL_MODE = master.mode_mapping()[MANUAL]
    while not master.wait_heartbeat().custom_mode == MANUAL_MODE:
        master.set_mode(MANUAL)
