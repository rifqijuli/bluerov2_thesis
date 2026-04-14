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
from sonar import pingsonar
import logging
import threading

log = logging.getLogger("Main Control")
log.info("Main Control started")

rc_channel_values = [65535] * 18  # Shared PWM array

import main_state as runner
from control import attitude_control, depth_control, pid_control, thruster_control


def main_control(rc_pwm, is_program_state_busy, ping_distance):
    class control_model():
        is_depth = True # Set to True if yaw and depth, rather than attitude


    is_forward = False
    current_pitch_pwm = 1500
    max_pwm = 1900
    min_pwm = 1100

    max_distance = 5.5 # threshold for max distance considered to object
    min_distance = 0.5

    specs = spec.load_specs()

    def check_pwm(pwm):
        if pwm > max_pwm:
            return max_pwm
        elif pwm < min_pwm:
            return min_pwm
        else:
            return pwm

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
        range_pwm = max_pwm - min_pwm

        match flag:
            case "yaw":
                convertedValue = value * ((range_pwm/4)/(imgWidth/2))
            case "pitch":
                convertedValue = value * ((range_pwm/4)/(imgHeight/2))

        pwm = convertedValue
        return pwm

    def distance_to_pwm(value, flag):
        range_distance = max_distance - min_distance
        range_pwm = max_pwm - min_pwm

        match flag:
            case "ping_sonar":
                convertedValue = value * ((range_pwm/4)/(range_distance))

        pwm = convertedValue
        return pwm



    while True:
        #if runner.program_state.get_busy_state() == True:
        if is_program_state_busy.value == 1:
            log.info("Control State: BUSY")

            # Set PID Constant Kp, Ki, Kd, and target
            yaw_pid = pid_control.PIDController(1.0,0.5,0.0,0.0)
            yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
            timePrev = time.time()

            pitch_pid = pid_control.PIDController(1.0,0.5,0.0,0.0)
            pitch_error_pixel= runner.verticalHeadingDifference.get_value("pixel")

            forward_pid = pid_control.PIDController(1.0,0.5,0.0,0.0)

            # Temporary, focus on yaw
            roll_angle = pitch_angle = 0

            log.info("Yaw Error Pixel: {}".format(yawErrorPixel))
            log.info("Pitch Error Pixel: {}".format(pitch_error_pixel))
            
            # Get Time
            timeNow = time.time()
            dt = timeNow - timePrev
            timePrev = timeNow

            log.info("Time Delta: {}".format(dt))

            # Get Target Yaw Correction
            yawErrorDegree = pixelToDegree(yawErrorPixel, "yaw")
            yaw_error_pwm = pixel_to_pwm(yawErrorPixel, "yaw")
            #currentYaw = attitude_control.get_current_yaw(master)

            # Get Target Pitch Correction
            pitch_error_degree = pixelToDegree(pitch_error_pixel, "pitch")
            pitch_error_pwm = pixel_to_pwm(pitch_error_pixel, "pitch")
            #current_pitch = attitude_control.get_current_pitch(master)

            #targetYaw must be in degree from 0 to 360
            #targetYaw = ((-1 * yaw_pid.compute(yawErrorDegree, dt)) + currentYaw) % 360
            target_yaw = yaw_pid.compute(abs(yaw_error_pwm), dt)
            if (yaw_error_pwm < 0):
                target_yaw = -target_yaw

            #targetPitch must be in degree from -90 to 90
            #targetPitch = (pitch_pid.compute(pitch_error_degree, dt) + current_pitch) % 360
            target_pitch = pitch_pid.compute(abs(pitch_error_pwm), dt)
            if (pitch_error_pwm < 0):
                target_pitch = -target_pitch

            distance_error_pwm = distance_to_pwm(ping_distance.value, "ping_sonar")
            target_speed = forward_pid.compute(abs(distance_error_pwm), dt)

            # Correct attitude
            # attitude_control.set_target_attitude(roll_angle, targetPitch, targetYaw, master, boot_time)
            if is_forward is False:                
                log.info(f"Correction yaw pwm to : {int(1500 - target_yaw)}")
                rc_pwm[3] = check_pwm(int(1500 - target_yaw))  # Update shared PWM array for yaw control
                match control_model.is_depth:
                    case True:
                        #thruster_control.set_rc_channel_pwm(master, 3, check_pwm(int(1500 + target_pitch)))
                        rc_pwm[2] = check_pwm(int(1500 + target_pitch))
                    case False:
                        # Update current pitch so it does not reset to 1500, but rather increase or decrease based on the error and correction.
                        current_pitch_pwm = current_pitch_pwm + target_pitch
                        #thruster_control.set_rc_channel_pwm(master, 1, check_pwm(int(current_pitch_pwm)))
                        rc_pwm[0] = check_pwm(int(current_pitch_pwm))  
            else:
                rc_pwm[3] = check_pwm(int(1500))
                rc_pwm[2] = check_pwm(int(1500))
            #log.info(f"Updated RC PWM for Yaw: {rc_pwm[3]}")
            #thruster_control.set_rc_channel_pwm(master, 4, check_pwm(int(1500 - target_yaw))) 
            
            
            # attitude_control.set_multi_rc_channel_pwm(master, {1: int(1500 + targetPitch), 4: int(1500 - target_yaw)})

            # Might introduce race condition.
            # set Main state to free so that new difference value can be set
            #runner.program_state.set_state_to_free()
            is_program_state_busy.value = 0 # Set to Free
            
            #time.sleep(0.02) # Sleep for 20ms.
            yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
            pitch_error_pixel= runner.verticalHeadingDifference.get_value("pixel")

            #Current PWM for debugging
            #get_current_pwm = attitude_control.get_current_pwm(master)
            #log.info("Current PWM: %s", get_current_pwm)
            log.info("Yaw PWM Correction: %s", yaw_error_pwm)

            
            if abs(yawErrorPixel) < abs(spec.get_tolerance_pixels(specs)) and abs(pitch_error_pixel) < abs(spec.get_tolerance_pixels(specs)):
                log.info("Target is within tolerance attitude.")
                try:
                    log.info(f"Distance from object: {ping_distance} cm")
                    if ping_distance.value > 0.5: # If distance is greater than 0.5 meter, move forward
                        log.info(f"Setting forward speed with PWM correction: {int(1500 - target_speed)}")
                        #rc_pwm[4] = check_pwm(int(1500 - target_speed)) # Set forward
                        is_forward = True
                    elif ping_distance.value <= 0.5: # If distance is less than or equal to 0.5 meter, stop
                        rc_pwm[4] = check_pwm(int(1500)) # Set neutral
                
                except Exception as e:
                    log.error(f"Error getting distance from sonar: {e}")
                    object_distance = None

                #thruster_control.set_rc_channel_pwm(master, 5, 1800) # 1100 forward, 1500 neutral, 1900 backward. or maybe im wrong
                #rc_pwm[4] = check_pwm(int(1600)) # Set forward

                is_forward = True
            else:
                if is_forward is True:

                    #thruster_control.set_rc_channel_pwm(master, 5, 1500) # 1100 forward, 1500 neutral, 1900 backward. or maybe im wrong
                    rc_pwm[4] = check_pwm(int(1500))

                    #time.sleep(0.01) # 
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