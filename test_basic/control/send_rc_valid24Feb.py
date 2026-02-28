"""
Example of how to use RC_CHANNEL_OVERRIDE messages to force input channels
in Ardupilot. These effectively replace the input channels (from joystick
or radio), NOT the output channels going to thrusters and servos.
"""

# Import mavutil
from pymavlink import mavutil
import time

# Create the connection
master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
# Wait a heartbeat before sending commands
master.wait_heartbeat()

# arm ArduSub autopilot and wait until confirmed
master.arducopter_arm()
master.motors_armed_wait()

# Create a function to send RC values
# More information about Joystick channels
# here: https://www.ardusub.com/operators-manual/rc-input-and-output.html#rc-inputs
def set_rc_channel_pwm(channel_id, pwm=1500):
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
    
def set_multi_rc_channel_pwm(channels_pwm):
    rc_channel_values = [65535 for _ in range(18)]
    for ch, pwm in channels_pwm.items():
        if ch < 1 or ch > 18:
            print(f"Channel {ch} does not exist.")
            continue
        rc_channel_values[ch - 1] = pwm
        master.mav.rc_channels_override_send(
            master.target_system,                # target_system
            master.target_component,             # target_component
            *rc_channel_values)                  # RC channel list, in microseconds.

# Send EVERY 0.05s (20Hz) for 10 seconds total
start_time = time.time()


while time.time() - start_time < 10:

    msg = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=False)

    # msg.pitch is in radians, format to degree
    if msg:
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
        print("Thrusters PWM:", pwms)

    # Set forward or backward
    # set_rc_channel_pwm(5, 1600) # 1900 forward, 1500 neutral, 1100 backward. or maybe im wrong.
 
    
    # 1 is pitch up (1900) or down (1100)
    # 2 is roll right (1900) or left (1100)
    # 3 is vertical up (1900) or down (1100)
    # 4 is yaw right (1900) or left (1100)
    # 5 is forward (1900) or backward (1100)
    # 6 is lateral right (1900) or left (1100)
    #set_rc_channel_pwm(1, 1500) 
    
    set_rc_channel_pwm(1, 1100)

    if time.time() - start_time > 5:
        set_multi_rc_channel_pwm({
            1: 1100, # pitch
            5: 1900, # thruster
        })

 

    