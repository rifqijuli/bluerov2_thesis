"""
Example of how to set target depth in depth hold mode with pymavlink
"""

import time
import math
# Import mavutil
from pymavlink import mavutil
# Imports for attitude
from pymavlink.quaternion import QuaternionBase
from specs import loader as spec

import runner as runner
from control import attitude_control, depth_control, pid_control

def pixelToDegree(value,flag):
    specs = spec.load_specs("specification.yaml")
    
    horizontalFOV, verticalFOV = spec.get_camera_fov(specs)
    imgWidth, imgHeight = spec.get_vision_resolution(specs)

    match flag:
        case "yaw":
            convertedValue = value / (imgWidth/horizontalFOV)
        case "pitch":
            convertedValue = value / (imgHeight/verticalFOV)

    return convertedValue

def main_control():

    # Create the connection
    master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
    boot_time = time.time()
    # Wait a heartbeat before sending commands
    master.wait_heartbeat()

    # arm ArduSub autopilot and wait until confirmed
    master.arducopter_arm()
    master.motors_armed_wait()

    # set depth hold
    depth_control.set_depth_hold(master)

    yawErrorPixel = runner.horizontalHeadingDifference.get_value()
    yawErrorDegree = pixelToDegree(yawErrorPixel, "yaw")
    pid = pid_control.PIDController(10,0,0,0)
    pid.compute(yawErrorDegree, 0)

    # go for a spin
    # (set target yaw from 0 to 500 degrees in steps of 10, one update per second)
    roll_angle = pitch_angle = 0
    for yaw_angle in range(0, 500, 10):
        attitude_control.set_target_attitude(roll_angle, pitch_angle, yaw_angle)
        time.sleep(1) # wait for a second

    # spin the other way with 3x larger steps
    for yaw_angle in range(500, 0, -30):
        attitude_control.set_target_attitude(roll_angle, pitch_angle, yaw_angle)
        time.sleep(1)
    

    # set a depth target
    depth_control.set_target_depth(-0.5)  # target depth of 0.5m below the water surface

    # clean up (disarm) at the end
    master.arducopter_disarm()
    master.motors_disarmed_wait()