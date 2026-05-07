# Import mavutil
import time

from pymavlink import mavutil


import logging
import threading

from control import attitude_control, depth_control, pid_control, thruster_control

log = logging.getLogger("Main RC Command")
log.info("Main RC Command started")

def send_rc_command(master, rc_pwm):
    master.mav.rc_channels_override_send(
        master.target_system,                # target_system
        master.target_component,             # target_component
        *rc_pwm)                  # RC channel list, in microseconds.

def main_rc_command(rc_pwm, is_program_state_busy, ping_distance, is_target_close):
    master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
    master.wait_heartbeat()

    # arm ArduSub autopilot and wait until confirmed
    master.arducopter_arm()
    master.motors_armed_wait()

    # set depth hold
    #NEXT: APA COBA INI DIMATIIN DULU YA? KAN DEPTH CONTROLNYA BIKIN ERROR KEMARIN.
    depth_control.set_depth_hold(master)

    while True:
        send_rc_command(master, rc_pwm)

        time.sleep(0.02)  # Send every 0.02s (50Hz)

        msg = master.recv_match()
        if not msg:
            continue
        if msg.get_type() == 'SERVO_OUTPUT_RAW':

            log.info("Camera angle: %s" % msg.servo10_raw) 

            # Straight camera = 1245
            # Downward camera = 1900
            # Upward camera = 1100
            # desired downward = 1612
