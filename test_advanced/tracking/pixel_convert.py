from torch import log

from misc import specLoader as spec
specs = spec.load_specs()

def pixel_to_pwm(value, flag, pwm_threshold):
    imgWidth, imgHeight = spec.get_vision_resolution(specs)
    range_pwm = pwm_threshold.max_pwm - pwm_threshold.min_pwm

    match flag:
        case "yaw":
            convertedValue = value * ((range_pwm/8)/(imgWidth/2))
        case "pitch":
            convertedValue = value * ((range_pwm/4)/(imgHeight/2))
        case "forward":
            convertedValue = value * ((range_pwm/6)/(imgHeight/2))

    pwm = convertedValue
    return pwm

def distance_to_pwm(value, flag, pwm_threshold, distance_threshold):
    range_distance = distance_threshold.max_distance - distance_threshold.min_distance
    range_pwm = pwm_threshold.max_pwm - pwm_threshold.min_pwm

    match flag:
        case "ping_sonar":
            convertedValue = value * ((range_pwm/4)/(range_distance))

    pwm = convertedValue
    return pwm

def filled_area_to_pwm(value, pwm_threshold):
    range_pwm = pwm_threshold.max_pwm - pwm_threshold.min_pwm

    convertedValue = (1 - value) * (range_pwm/4)

    pwm = convertedValue
    return pwm

def pixel_filled(width, height):
    imgWidth, imgHeight = spec.get_vision_resolution(specs)

    resolution_area = imgWidth * imgHeight
    filled_area = width * height
    print(f"Filled area: {filled_area} pixels, Resolution area: {resolution_area} pixels")
    approx_filled_area = filled_area / resolution_area
    print(f"Filled area: {filled_area} pixels, Resolution area: {resolution_area} pixels, Approximate filled area: {approx_filled_area * 100} % of the frame")
    return approx_filled_area