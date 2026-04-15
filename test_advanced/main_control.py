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


def main_control(rc_pwm, is_program_state_busy, ping_distance, is_target_close):
    class control_model():
        is_depth = True # Set to True if yaw and depth, rather than attitude


    is_forward = False
    current_pitch_pwm = 1500
    max_pwm = 1900
    min_pwm = 1100

    max_distance = 5.7 # threshold for max distance considered to object
    min_distance = 0.7

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
                convertedValue = value * ((range_pwm/8)/(imgWidth/2))
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

    timeStart = time.time()
    while True:
        #if runner.program_state.get_busy_state() == True:
        if is_program_state_busy.value == 1:
            log.info("Control State: BUSY")

            # Set PID Constant Kp, Ki, Kd, and target
            yaw_pid = pid_control.PIDController(1.5,1.0,0.00000001,0.0)
            yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
            timePrev = time.time()

            pitch_pid = pid_control.PIDController(1.5,0.0,0.00000005,0.00)
            pitch_error_pixel= runner.verticalHeadingDifference.get_value("pixel")

            forward_pid = pid_control.PIDController(1.0,0.0,0,0.00)

            log.info("Yaw Error Pixel: {}".format(yawErrorPixel))
            log.info("Pitch Error Pixel: {}".format(pitch_error_pixel))
            
            # Get Time
            timeNow = time.time()
            dt_percycle = timeNow - timePrev
            dt = timeNow - timeStart
            timePrev = timeNow

            log.info("Time Delta: {}".format(dt_percycle))

            # Get Target Yaw and Pitch Correction
            yaw_error_pwm = pixel_to_pwm(yawErrorPixel, "yaw")
            pitch_error_pwm = pixel_to_pwm(pitch_error_pixel, "pitch")
            distance_error_pwm = distance_to_pwm(ping_distance.value, "ping_sonar")

            #targetYaw must be in degree from 0 to 360
            target_yaw = yaw_pid.compute(abs(yaw_error_pwm), dt_percycle)
            if (yaw_error_pwm < 0):
                target_yaw = -target_yaw

            target_pitch = pitch_pid.compute(abs(pitch_error_pwm), dt_percycle)
            if (pitch_error_pwm < 0):
                target_pitch = -target_pitch
            
            target_speed = forward_pid.compute(abs(distance_error_pwm), dt_percycle)

            rc_pwm[3] = check_pwm(int(1500 - target_yaw))  # Update shared PWM array for yaw control
            log.info("Yaw Correction to: %s", int(1500 - target_yaw))

            rc_pwm[2] = check_pwm(int(1500 + target_pitch))
            log.info("Pitch Correction to: %s", int(1500 + target_pitch))
            # Pitch if needed
            # current_pitch_pwm = current_pitch_pwm + target_pitch
            # rc_pwm[0] = check_pwm(int(current_pitch_pwm))

            
            if abs(yawErrorPixel) < abs(spec.get_tolerance_pixels(specs)) and abs(pitch_error_pixel) < abs(spec.get_tolerance_pixels(specs)):
                log.info("Target is within tolerance attitude.")
                log.info(f"Distance from object: {ping_distance.value} cm")
                if ping_distance.value > min_distance: # If distance is greater than minimum distance, move forward
                    rc_pwm[4] = check_pwm(int(1500 - target_speed)) # Set forward
                elif ping_distance.value <= min_distance: # If distance is less than or equal to minimum distance, stop
                    log.info("Target is close enough. Stopping forward movement.")
                    rc_pwm[4] = check_pwm(int(1500)) # Set neutral
                    
                is_forward = True
            else:
                if is_forward == True:
                    log.info("Target is outside of tolerance attitude.")
                    rc_pwm[4] = check_pwm(int(1500))
                    is_forward = False
                
            is_program_state_busy.value = 0 # Set to Free
            
            yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
            pitch_error_pixel= runner.verticalHeadingDifference.get_value("pixel")