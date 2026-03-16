"""
Continuous MANUAL_CONTROL - sends 20Hz to prevent timeout
"""
import math
import time
from pymavlink import mavutil

master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
master.wait_heartbeat()

master.arducopter_arm()
master.motors_armed_wait()
print("ARMED - sending continuous forward...")

# Send EVERY 0.05s (20Hz) for 10 seconds total

start_time = time.time()
while time.time() - start_time < 3:
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

    master.mav.manual_control_send(
        master.target_system,
        500,  # Forward  -1000, Neutral 0, Backward +1000. 
        0,     # No strafe -1000, Neutral 0, Backward +1000
        500,   # Neutral vertical 0, neutral 500, full up 1000
        0,     # No yaw -1000, Neutral 0, Backward +1000
        0      # No buttons -1000, Neutral 0, Backward +1000
    )
    # The problem with this, is that it goes forward, but the attitude is maintained, so even if we set the vertical to go below, its heading down but the attitude is still looking forward.
    # time.sleep(0.05)  # 20Hz rate
    # TIME SLEEP RUINS IN REAAL TIME. So we will just send it as fast as possible.

print("Stopping...")
# Send neutral to stop cleanly
for i in range(20):  # 1 second neutral
    master.mav.manual_control_send(master.target_system, 0,0,500,0,0)
    time.sleep(0.05)

#master.arducopter_disarm()
#master.motors_disarmed_wait()