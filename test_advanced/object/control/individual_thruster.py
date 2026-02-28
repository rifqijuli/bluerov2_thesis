"""
Continuous MANUAL_CONTROL - sends 20Hz to prevent timeout
"""
import math
import time
from pymavlink import mavutil

def set_servo_pwm(servo_n, microseconds):
    """ Sets AUX 'servo_n' output PWM pulse-width.

    Uses https://mavlink.io/en/messages/common.html#MAV_CMD_DO_SET_SERVO

    'servo_n' is the AUX port to set (assumes port is configured as a servo).
        Valid values are 1-3 in a normal BlueROV2 setup, but can go up to 8
        depending on Pixhawk type and firmware.
    'microseconds' is the PWM pulse-width to set the output to. Commonly
        between 1100 and 1900 microseconds.

    """
    # master.set_servo(servo_n+8, microseconds) or:
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0,            # first transmission of this command
        servo_n + 8,  # servo instance, offset by 8 MAIN outputs
        microseconds, # PWM pulse-width
        0,0,0,0,0     # unused parameters
    )

master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
master.wait_heartbeat()

master.arducopter_arm()
master.motors_armed_wait()
print("ARMED - sending continuous forward...")

# Send EVERY 0.05s (20Hz) for 10 seconds total
start_time = time.time()
while time.time() - start_time < 2:
    msg = master.recv_match(type='ATTITUDE', blocking=True, timeout=1)
    
    # msg.pitch is in radians, format to degree
    pitch_rad = msg.pitch
    pitch_deg = math.degrees(pitch_rad)
    print(f"Current pitch: {pitch_deg:.2f} degrees")

    set_servo_pwm(2, 1100)  # Example: set servo_1 to mid-point (1500us) (malah semua thruster gerak)
    time.sleep(0.05)  # 20Hz rate

print("Stopping...")
# Send neutral to stop cleanly
for i in range(20):  # 1 second neutral
    master.mav.manual_control_send(master.target_system, 0,0,500,0,0)
    time.sleep(0.05)

master.arducopter_disarm()
master.motors_disarmed_wait()


