#!/usr/bin/env python3
# thruster_listener.py
from pymavlink import mavutil
import time

MAV_PORT = "udp:0.0.0.0:14550"
conn = mavutil.mavlink_connection(MAV_PORT)
print("Waiting for heartbeat...")
conn.wait_heartbeat()
print("Listening for thruster outputs... (Ctrl-C to stop)")

try:
    while True:
        msg = conn.recv_match(blocking=True, timeout=2)
        if not msg:
            continue
        t = msg.get_type()
        if t == "SERVO_OUTPUT_RAW":
            vals = [getattr(msg, f"servo{i}_raw", None) for i in range(1,9)]
            print(f"[{time.time():.2f}] SERVO_OUTPUT_RAW:", vals)
        elif t == "ACTUATOR_OUTPUT_STATUS":
            vals = list(msg.actuator) if hasattr(msg, "actuator") else []
            print(f"[{time.time():.2f}] ACTUATOR_OUTPUT_STATUS:", vals)
        elif t == "RC_CHANNELS":
            vals = [getattr(msg, f"chan{i}", None) for i in range(1,10)]
            print(f"[{time.time():.2f}] RC_CHANNELS:", vals)
        elif t == "RAW_IMU" or t == "ATTITUDE":
            # optional: show attitude occasionally
            pass
except KeyboardInterrupt:
    print("Stopped.")