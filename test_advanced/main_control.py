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


import main_state as runner
from control import attitude_control, depth_control, pid_control, thruster_control

def main_control():
    is_forward = False

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
    
    def pixel_to_pwm(value, flag):
        imgWidth, imgHeight = spec.get_vision_resolution(specs)
        max_pwm = 1900
        min_pwm = 1100
        range_pwm = max_pwm - min_pwm

        match flag:
            case "yaw":
                convertedValue = value * ((range_pwm/8)/(imgWidth/2))
            case "pitch":
                convertedValue = value * ((range_pwm/8)/(imgHeight/2))

        pwm = convertedValue
        return pwm

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

    while True:
        if runner.program_state.get_busy_state() == True:
            log.info("Control State: BUSY")

            # Set PID Constant Kp, Ki, Kd, and target
            yaw_pid = pid_control.PIDController(1.0,0.0,0.0,0.0)
            yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
            timePrev = time.time()

            pitch_pid = pid_control.PIDController(1.0,0.0,0.0,0.0)
            pitch_error_pixel= runner.verticalHeadingDifference.get_value("pixel")

            # Temporary, focus on yaw
            roll_angle = pitch_angle = 0

            log.info("Yaw Error Pixel: {}".format(yawErrorPixel))
            log.info("Pitch Error Pixel: {}".format(pitch_error_pixel))
            
            # Get Time
            timeNow = time.time()
            dt = timeNow - timePrev
            timePrev = timeNow

            # Get Target Yaw Correction
            yawErrorDegree = pixelToDegree(yawErrorPixel, "yaw")
            yaw_error_pwm = pixel_to_pwm(yawErrorPixel, "yaw")
            currentYaw = attitude_control.get_current_yaw(master)

            # Get Target Pitch Correction
            pitch_error_degree = pixelToDegree(pitch_error_pixel, "pitch")
            current_pitch = attitude_control.get_current_pitch(master)

            #targetYaw must be in degree from 0 to 360
            targetYaw = ((-1 * yaw_pid.compute(yawErrorDegree, dt)) + currentYaw) % 360
            target_yaw = yaw_pid.compute(abs(yaw_error_pwm), dt)
            if (yaw_error_pwm < 0):
                target_yaw = -target_yaw

            #targetPitch must be in degree from -90 to 90
            targetPitch = (pitch_pid.compute(pitch_error_degree, dt) + current_pitch) % 360

            # Correct attitude
            # attitude_control.set_target_attitude(roll_angle, targetPitch, targetYaw, master, boot_time)
            thruster_control.set_rc_channel_pwm(master, 4, int(1500 - target_yaw)) 

            # Might introduce race condition.
            # set Main state to free so that new difference value can be set
            runner.program_state.set_state_to_free()
            
            time.sleep(0.5) # wait for half a second. The best is if wait until the new value has been set.
            yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
            pitch_error_pixel= runner.verticalHeadingDifference.get_value("pixel")

            #Current PWM for debugging
            get_current_pwm = attitude_control.get_current_pwm(master)
            log.info("Current PWM: %s", get_current_pwm)
            log.info("Yaw PWM Correction: %s", yaw_error_pwm)

            if abs(yawErrorPixel) < abs(spec.get_tolerance_pixels(specs)) and abs(pitch_error_pixel) < abs(spec.get_tolerance_pixels(specs)):
                log.info("Target is within tolerance attitude.")
                thruster_control.set_rc_channel_pwm(master, 5, 1600) # 1100 forward, 1500 neutral, 1900 backward. or maybe im wrong
                #thruster_control.set_thruster_control(master, 500, 0, 500, 0) # Send neutral to stop cleanly
                is_forward = True
            else:
                if is_forward is True:
                    #thruster_control.set_thruster_control(master, 0, 0, 500, 0) # Send neutral to stop cleanly
                    thruster_control.set_rc_channel_pwm(master, 5, 1500) # 1100 forward, 1500 neutral, 1900 backward. or maybe im wrong
                    time.sleep(0.5) # wait for half a second to make sure the rov stop before correcting the attitude again. The best is if wait until the new value has been set.
                    # This is.. not optimal. its recursive. But it works for now.
                    # Will implement something better in the future, maybe with state machine or something.
                    # main_control()
                    is_forward = False
                    #break
                #thruster_control.set_thruster_control(master, 0, 0, 500, 0) # Send neutral to stop cleanly
            
                
            # set depth hold
            # runner.program_state.set_state_to_free()

            # If Yaw already correct
            # runner.program_state.set_state_to_free()



            # clean up (disarm) at the end --> if disarmed, depth hold will also released and rov will just sink
            # master.arducopter_disarm()
            # master.motors_disarmed_wait()

        depth_control.set_depth_hold(master)
