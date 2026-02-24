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

def set_rc_channel_pwm(master, channel_id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        channel_id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if channel_id < 1 or channel_id > 18:
        print("Channel does not exist.")
        return

    # Mavlink 2 supports up to 18 channels:
    # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
    rc_channel_values = [65535 for _ in range(18)]
    rc_channel_values[channel_id - 1] = pwm
    master.mav.rc_channels_override_send(
        master.target_system,                # target_system
        master.target_component,             # target_component
        *rc_channel_values)                  # RC channel list, in microseconds.
