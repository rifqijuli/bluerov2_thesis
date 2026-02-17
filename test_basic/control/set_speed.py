"""
Continuous MANUAL_CONTROL - sends 20Hz to prevent timeout
"""
import time
from pymavlink import mavutil

master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
master.wait_heartbeat()

master.arducopter_arm()
master.motors_armed_wait()
print("ARMED - sending continuous forward...")

# Send EVERY 0.05s (20Hz) for 10 seconds total
start_time = time.time()
while time.time() - start_time < 10:
    master.mav.manual_control_send(
        master.target_system,
        1000,  # Forward MAX
        0,     # No strafe
        500,   # Neutral vertical
        0,     # No yaw
        0      # No buttons
    )
    time.sleep(0.05)  # 20Hz rate

print("Stopping...")
# Send neutral to stop cleanly
for i in range(20):  # 1 second neutral
    master.mav.manual_control_send(master.target_system, 0,0,500,0,0)
    time.sleep(0.05)

master.arducopter_disarm()
master.motors_disarmed_wait()