"""
Example of how to set target depth in depth hold mode with pymavlink
"""

import time
import math
# Import mavutil
from pymavlink import mavutil
# Imports for attitude
from pymavlink.quaternion import QuaternionBase
from misc import specLoader as spec
from misc import stateLoader as stateLoad

import runner as runner
from control import attitude_control, depth_control, pid_control

def main_control():

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

    # Create the connection
    master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
    boot_time = time.time()
    # Wait a heartbeat before sending commands
    master.wait_heartbeat()

    while True:
        if runner.program_state.get_busy_state() == True:

            # arm ArduSub autopilot and wait until confirmed
            master.arducopter_arm()
            master.motors_armed_wait()

            # set depth hold
            depth_control.set_depth_hold(master)

            # Set PID Constant Kp, Ki, Kd, and target
            yaw_pid = pid_control.PIDController(1.0,0.0,0.0,0.0)
            yawErrorPixel = runner.horizontalHeadingDifference.get_value()
            timePrev = time.time()

            # Temporary, focus on yaw
            roll_angle = pitch_angle = 0

            while abs(yawErrorPixel) >= 50:

                # Get Time
                timeNow = time.time()
                dt = timeNow - timePrev
                timePrev = timeNow

                # Get Target Yaw Correction
                yawErrorDegree = pixelToDegree(yawErrorPixel, "yaw")
                currentYaw = attitude_control.get_current_yaw(master)
                targetYaw = yaw_pid.compute(yawErrorDegree, dt) + currentYaw

                # Correct Yaw
                attitude_control.set_target_attitude(roll_angle, pitch_angle, targetYaw)

                # Might introduce race condition.
                runner.program_state.set_state_to_free()
                time.sleep(0.5) # wait for half a second. The best is if wait until the new value has been set.
                yawErrorPixel = runner.horizontalHeadingDifference.get_value()

            # If Yaw already correct
            runner.program_state.set_state_to_free()

            # set a depth target
            depth_control.set_target_depth(-0.5)  # target depth of 0.5m below the water surface

            # clean up (disarm) at the end --> if disarmed, depth hold will also released and rov will just sink
            # master.arducopter_disarm()
            # master.motors_disarmed_wait()