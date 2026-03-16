# Import mavutil
from pymavlink import mavutil

def get_depth(master):
    msg = master.recv_match()
    if not msg:
        return None
    if msg.get_type() == 'AHRS2':
        depth_m = msg.altitude
        # msg.altitude is depth (negative value in m)
        return depth_m
