"""
Example of how to set target depth in depth hold mode with pymavlink
"""

import datetime
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
from tracking import pixel_convert
from log.pid_logger import PIDLogger

log = logging.getLogger("Main Control")
log.info("Main Control started")

rc_channel_values = [65535] * 18  # Shared PWM array

import main_state as runner
from control import attitude_control, depth_control, pid_control, thruster_control
from control.pwm_threshold import pwm_threshold

def main_control(rc_pwm, is_program_state_busy, ping_distance, is_target_close, is_target_detected, is_crane_view):
    class control_model():
        is_depth = True # Set to True if yaw and depth, rather than attitude

    pid_logger = PIDLogger(f"pid_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    yaw_threshold = pwm_threshold(max_pwm=1700, min_pwm=1300)
    pitch_threshold = pwm_threshold(max_pwm=1700, min_pwm=1300)
    forward_threshold = pwm_threshold(max_pwm=1800, min_pwm=1200)

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
    yaw_pid = pid_control.PIDController(0.0,0.0,0.0,0.0)
    pitch_pid = pid_control.PIDController(0.0,0.0,0.0,0.0)
    forward_pid = pid_control.PIDController(0.0,0.0,0.0,0.0)
    log.info("Control process initialized, entering main loop.")
    while True:
        time_to_log = time.time()
        #if runner.program_state.get_busy_state() == True:
        if is_program_state_busy.value == 1:
            log.info("Control State: BUSY")

            # Set PID Constant Kp, Ki, Kd, and target
            match is_target_close.value:
                case 1:
                    # Target is close, 
                    yaw_pid.Kp, yaw_pid.Ki, yaw_pid.Kd = 3.0, 0.0, 0.0
                    pitch_pid.Kp, pitch_pid.Ki, pitch_pid.Kd = 3.0, 0.0, 0.0
                    forward_pid.Kp, forward_pid.Ki, forward_pid.Kd = 2.0, 0.0, 0.0
                    '''
                    yaw_pid.Kp, yaw_pid.Ki, yaw_pid.Kd = 0.2, 0.1, 0.05
                    pitch_pid.Kp, pitch_pid.Ki, pitch_pid.Kd = 0.1, 0.1, 0.05
                    forward_pid.Kp, forward_pid.Ki, forward_pid.Kd = 0.5, 0.02, 0.01
                    '''
                case 0:
                    # Target is not close
                    yaw_pid.Kp, yaw_pid.Ki, yaw_pid.Kd = 3.0, 0.0, 0.0
                    pitch_pid.Kp, pitch_pid.Ki, pitch_pid.Kd = 3.0, 0.0, 0.0
                    forward_pid.Kp, forward_pid.Ki, forward_pid.Kd = 2.0, 0.0, 0.0
                    '''
                    yaw_pid.Kp, yaw_pid.Ki, yaw_pid.Kd = 1.0, 0.5, 0.01
                    pitch_pid.Kp, pitch_pid.Ki, pitch_pid.Kd = 1.0, 0.5, 0.01
                    forward_pid.Kp, forward_pid.Ki, forward_pid.Kd = 1.0, 0.0, 0.0
                    '''

            yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
            timePrev = time.time()

            pitch_error_pixel = runner.verticalHeadingDifference.get_value("pixel")

            log.info("Yaw Error Pixel: {}".format(yawErrorPixel))
            log.info("Pitch Error Pixel: {}".format(pitch_error_pixel))
            
            # Get Time
            timeNow = time.time()
            dt_percycle = timeNow - timePrev
            dt = timeNow - timeStart
            timePrev = timeNow

            log.info("Time Delta: {}".format(dt_percycle))

            # Get Target Yaw and Pitch Correction
            yaw_error_pwm = pixel_convert.pixel_to_pwm(yawErrorPixel, "yaw", yaw_threshold)
            pitch_error_pwm = pixel_convert.pixel_to_pwm(pitch_error_pixel, "pitch", pitch_threshold)
            match is_crane_view.value:
                case 1:
                    # In crane view
                    distance_error_pixel = runner.verticalHeadingDifference.get_closeness_value("pixel")
                    distance_error_pwm = pixel_convert.pixel_to_pwm(int(distance_error_pixel), "forward", forward_threshold)
                case 0:
                    # Not in crane view, normal operation
                    distance_error_pwm = distance_to_pwm(ping_distance.value, "ping_sonar")
            
            target_yaw = yaw_pid.compute(abs(yaw_error_pwm), dt_percycle)
            target_pitch = pitch_pid.compute(abs(pitch_error_pwm), dt_percycle)
            target_speed = forward_pid.compute(abs(distance_error_pwm), dt_percycle)

            if (yaw_error_pwm < 0):
                target_yaw = -target_yaw

            if (pitch_error_pwm < 0):
                target_pitch = -target_pitch
            
            yaw_pwm_values = yaw_threshold.check_pwm(int(1500 - target_yaw))
            pitch_pwm_values = pitch_threshold.check_pwm(int(1500 + target_pitch))
            forward_pwm_values = forward_threshold.check_pwm(int(1500 - target_speed))

            pid_logger.log(
                timestamp = time_to_log,
                processing_time = time_to_log - time.time(),
                pixel_error_x = yawErrorPixel,
                pixel_error_y = pitch_error_pixel,
                sonar_distance = ping_distance.value,
                yaw_out = target_yaw,
                pitch_out = target_pitch,
                forward_out = target_speed,
                pwm_yaw = yaw_pwm_values,
                pwm_pitch = pitch_pwm_values,
                pwm_forward = forward_pwm_values,
                yaw_kp = yaw_pid.Kp,
                yaw_ki = yaw_pid.Ki,
                yaw_kd = yaw_pid.Kd,
                pitch_kp = pitch_pid.Kp,
                pitch_ki = pitch_pid.Ki,
                pitch_kd = pitch_pid.Kd,
                forward_kp = forward_pid.Kp,
                forward_ki = forward_pid.Ki,
                forward_kd = forward_pid.Kd
            )

            if (is_target_detected.value == 0):
                log.info("Target is not detected. Stopping all movement. (satu)")
                rc_pwm[2] = 1500 # Set neutral vertical
                rc_pwm[3] = 1500 # Set neutral horizontal
                rc_pwm[4] = 1500 # Set neutral forward
                is_forward = False
            else:
                log.info("Target is detected. Adjusting movement.")
                rc_pwm[3] = yaw_pwm_values # Update shared PWM array for yaw control
                log.info("Yaw Correction to: %s", int(1500 - target_yaw))

                rc_pwm[2] = pitch_pwm_values # Update shared PWM array for pitch control
                log.info("Pitch Correction to: %s", int(1500 + target_pitch))
                
                match is_crane_view.value:
                    case 1:
                        if abs(yawErrorPixel) < abs(spec.get_tolerance_pixels(specs)):
                            log.info("Target is within tolerance attitude in crane view.")
                            log.info("In crane view, using forward PID based on closeness value.")
                            rc_pwm[4] = forward_pwm_values # Set forward based on closeness value
                            log.info("Forward Correction to: %s", int(1500 - target_speed))
                            is_forward = True
                        else:
                            log.info("Target is outside of tolerance attitude in crane view.")
                            rc_pwm[4] = 1500 # Set neutral forward
                            is_forward = False
                    case 0:
                        log.info("Not in crane view, using forward PID based on sonar distance.")
                        if abs(yawErrorPixel) < abs(spec.get_tolerance_pixels(specs)) and abs(pitch_error_pixel) < abs(spec.get_tolerance_pixels(specs)):
                            log.info("Target is within tolerance attitude.")
                            log.info(f"Distance from object: {ping_distance.value} m")
                            if ping_distance.value > min_distance: # If distance is greater than minimum distance, move forward
                                log.info("Target is far. Moving forward.")
                                rc_pwm[4] = forward_pwm_values # Set forward
                            elif ping_distance.value <= min_distance: # If distance is less than or equal to minimum distance, stop
                                log.info("Target is close enough. Stopping forward movement.")
                                rc_pwm[4] = 1500 # Set neutral
                            is_forward = True
                        else:
                            if is_forward == True:
                                log.info("Target is outside of tolerance attitude.")
                                rc_pwm[4] = 1500 # Set neutral forward
                                is_forward = False
                
            is_program_state_busy.value = 0 # Set to Free
            
            yawErrorPixel = runner.horizontalHeadingDifference.get_value("pixel")
            pitch_error_pixel= runner.verticalHeadingDifference.get_value("pixel")
        else:
            if (is_target_detected.value == 2):
                rc_pwm[2] = 1500 # Set neutral vertical
                rc_pwm[3] = 1500 # Set neutral horizontal
                rc_pwm[4] = 1500 # Set neutral forward
                is_forward = False