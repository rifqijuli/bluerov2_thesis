"""
Example of how to use RC_CHANNEL_OVERRIDE messages to force input channels
in Ardupilot. These effectively replace the input channels (from joystick
or radio), NOT the output channels going to thrusters and servos.
"""

# Import mavutil
import logging

from pymavlink import mavutil
import time

log = logging.getLogger("Thruster Cleaner")
log.info("Main Cleaner started")

# Create a function to send RC values
# More information about Joystick channels
# here: https://www.ardusub.com/operators-manual/rc-input-and-output.html#rc-inputs
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

def main_cleaner():
    n=1
    # Create the connection
    master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
    # Wait a heartbeat before sending commands
    master.wait_heartbeat()

    # arm ArduSub autopilot and wait until confirmed
    master.arducopter_arm()
    master.motors_armed_wait()

    log.info(f"Cleaning thruster...")

    while n <= 6:
        
        start_time = time.time()
        while time.time() - start_time < 2:

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

            set_rc_channel_pwm(master, n, 1500)
        n+=1

    log.info(f"Done! Disarming...")
    # arm ArduSub autopilot and wait until confirmed
    master.arducopter_disarm()
    master.motors_disarmed_wait()
