#!/usr/bin/env python3
# pymav_test.py -- listens for a heartbeat and prints ATTITUDE/RAW_IMU messages
from pymavlink import mavutil
import time, sys

# Choose connection: try listening locally (ROV -> your machine) first
MASTER = "udp:0.0.0.0:14550"
# If that doesn't work, try explicit ROV/companion IP, e.g.:
# MASTER = "udp:192.168.2.2:14550"

print("Connecting to MAVLink on:", MASTER)
mav = mavutil.mavlink_connection(MASTER, autoreconnect=True, source_system=255)

print("Waiting for heartbeat (this may take a few seconds)...")
mav.wait_heartbeat(timeout=10)
print("Heartbeat from system %d component %d" % (mav.target_system, mav.target_component))


try:
    while True:
        msg = mav.recv_match(blocking=True, timeout=5)
        if not msg:
            # no message, continue listening
            continue
        t = msg.get_type()
        if t == "ATTITUDE":
            print("[ATT] time={:.2f} roll={:.3f} pitch={:.3f} yaw={:.3f}".format(
                time.time(), msg.roll, msg.pitch, msg.yaw))
        elif t == "RAW_IMU":
            print("[IMU] ax={:.3f} ay={:.3f} az={:.3f} gx={:.3f} gy={:.3f} gz={:.3f}".format(
                msg.xacc, msg.yacc, msg.zacc, msg.xgyro, msg.ygyro, msg.zgyro))
        elif t == "HEARTBEAT":
            print("[HEARTBEAT] mode=%s type=%s" % (msg.base_mode, msg.type))
        # add other message types as needed
except KeyboardInterrupt:
    print("Exiting")
    mav.close()
    sys.exit(0)