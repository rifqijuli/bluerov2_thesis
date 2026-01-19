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
import logging

log = logging.getLogger("Main Control")
log.info("Main Control started")

import runner as runner
from control import attitude_control, depth_control, pid_control

def main_control():
    specs = spec.load_specs()
    def pixelToDegree(value,flag):
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
            log.info("Control State: BUSY")

            # arm ArduSub autopilot and wait until confirmed
            master.arducopter_arm()
            master.motors_armed_wait()

            # set depth hold
            depth_control.set_depth_hold(master)

            # Set PID Constant Kp, Ki, Kd, and target
            yaw_pid = pid_control.PIDController(1.0,0.0,0.0,0.0)
            yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
            timePrev = time.time()

            # Temporary, focus on yaw
            roll_angle = pitch_angle = 0

            while abs(yawErrorPixel) > abs(spec.get_tolerance_pixels(specs)):
                log.info("Yaw Error Pixel: {}".format(yawErrorPixel))
                
                # Get Time
                timeNow = time.time()
                dt = timeNow - timePrev
                timePrev = timeNow

                # Get Target Yaw Correction
                yawErrorDegree = pixelToDegree(yawErrorPixel, "yaw")
                currentYaw = attitude_control.get_current_yaw(master)

                #targetYaw must be in degree from 0 to 360
                targetYaw = ((-1 * yaw_pid.compute(yawErrorDegree, dt)) + currentYaw) % 360

                # Correct Yaw
                attitude_control.set_target_attitude(roll_angle, pitch_angle, targetYaw, master, boot_time)

                # Might introduce race condition.
                # set Main state to free so that new difference value can be set
                runner.program_state.set_state_to_free()

                time.sleep(0.5) # wait for half a second. The best is if wait until the new value has been set.
                yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
                # End of while loop for yaw correction
            
            runner.program_state.set_state_to_free()
            # Set PID Constant Kp, Ki, Kd, and target
            '''
            height_pid = pid_control.PIDController(1.0,0.0,0.0,0.0)
            heightErrorPixel = runner.verticalHeadingDifference.get_value("pixel")
            timePrev = time.time()
            
            while abs(heightErrorPixel) > abs(spec.get_tolerance_pixels(specs)):

                # Get Time
                timeNow = time.time()
                dt = timeNow - timePrev
                timePrev = timeNow

                # Get Target Height Correction
                currentHeight = attitude_control.get_current_depth(master)
                
                targetHeight = currentHeight + height_pid.compute(heightErrorPixel, dt)

                # set a depth target
                depth_control.set_target_depth(targetHeight)  # target depth of 0.5m below the water surface

                # set Main state to free so that new difference value can be set
                runner.program_state.set_state_to_free()

                time.sleep(0.5) # wait for half a second. The best is if wait until the new value has been set.
                heightErrorPixel = runner.verticalHeadingDifference.get_value()
                # End of while loop for height correction
            '''
            # If Yaw already correct
            # runner.program_state.set_state_to_free()



            # clean up (disarm) at the end --> if disarmed, depth hold will also released and rov will just sink
            # master.arducopter_disarm()
            # master.motors_disarmed_wait()