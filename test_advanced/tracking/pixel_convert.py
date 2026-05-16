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

def pixel_filled(width, height):
    imgWidth, imgHeight = spec.get_vision_resolution(specs)

    resolution_area = imgWidth * imgHeight
    filled_area = width * height

    return round(filled_area / resolution_area, 2)