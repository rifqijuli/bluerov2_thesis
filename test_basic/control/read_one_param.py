"""
Example of how to filter for specific mavlink messages coming from the
autopilot using pymavlink.

Can also filter within recv_match command - see "Read all parameters" example
"""
# Import mavutil
from pymavlink import mavutil

# Create the connection
# From topside computer
master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')

while True:
    msg = master.recv_match()
    if not msg:
        continue
    if msg.get_type() == 'AHRS2':
        print("\n\n*****Got message: %s*****" % msg.get_type())
        print("Message: %s" % msg)
        print("\nAs dictionary: %s" % msg.to_dict())
        # Armed = MAV_STATE_STANDBY (4), Disarmed = MAV_STATE_ACTIVE (3)
        print("\nROV Altitude: %s" % msg.altitude)
        depth_m = -msg.altitude
        print(f"Depth: {depth_m:.2f} m")

## NEED TO BE TESTED ON THE WATER, BECUASE IT READS FROM BAR30
# Valid! BAR30 from bluerov is msg.get_type() == 'AHRS2' --> msg.altitude is the depth in m, with negative sign (e.g. -1.5 for 1.5m depth)