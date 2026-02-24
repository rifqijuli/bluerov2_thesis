import time
from pymavlink import mavutil

master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
master.wait_heartbeat()
print("HB from system (sys %u comp %u)" % (master.target_system, master.target_component))

# Set MANUAL mode
mode_id = master.mode_mapping()['MANUAL']
master.mav.set_mode_send(
    master.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    mode_id
)
time.sleep(1)

# Arm (target autopilot comp=1)
master.mav.command_long_send(
    master.target_system,
    1,  # autopilot comp ID
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1, 0, 0, 0, 0, 0, 0
)

print("Waiting for arm...")
master.motors_armed_wait()
print("ARMED!")

# Forward for 10s (z axis for ArduSub)
start_time = time.time()
while time.time() - start_time < 10:
    master.mav.manual_control_send(
        master.target_system,
        0,   # x (pitch)
        0,   # y (roll) 
        500, # z (forward!)
        0,   # r (yaw)
        0
    )
    time.sleep(0.05)

# Stop
for _ in range(20):
    master.mav.manual_control_send(master.target_system, 0, 0, 0, 0, 0)
    time.sleep(0.05)

# Disarm (also comp=1)
master.mav.command_long_send(
    master.target_system,
    1,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    0, 0, 0, 0, 0, 0, 0
)
master.motors_disarmed_wait()
print("Disarmed")
